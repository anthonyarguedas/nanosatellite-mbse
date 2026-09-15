#!/usr/bin/env python3
"""Run and reconcile a corrective Springer Nature Link final-search subset."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
RUNNER_PATH = SCRIPT_PATH.with_name("run.py")
BACKEND_PATH = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "_springer_concurrent_cdp.py"
)
DEFAULT_CORRECTIVE_TIMEOUT_SECONDS = 180

PLAN_SCHEMA = "slr1-springer-nature-link-final-direct-corrective-plan/v1"
RUN_SCHEMA = "slr1-springer-nature-link-final-direct-corrective-run/v1"
RECONCILIATION_SCHEMA = "slr1-springer-nature-link-final-direct-run-reconciliation/v1"
CELL_DECLARATIONS_SCHEMA = "slr1-springer-nature-link-final-direct-reconciled-cell-declarations/v1"
ASSESSMENT_SCHEMA = "slr1-springer-nature-link-final-direct-reconciled-assessment/v1"


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("slr1_springer_final_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_runner()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    return runner.load(path)


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    runner.write_new(path, value)


def digest(path: Path) -> str:
    return runner.digest(path)


def relative(path: Path) -> str:
    return runner.relative(path)


def output_file(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return output_dir / str(event["output_filename"])


def regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def base_failure_events(
    base_plan: Mapping[str, Any], base_receipt: Mapping[str, Any]
) -> list[dict[str, Any]]:
    outcomes = {
        item.get("event_id"): item
        for item in base_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    failures: list[dict[str, Any]] = []
    for event in base_plan.get("events", []):
        if not isinstance(event, Mapping):
            raise ValueError("The superseded plan has a malformed event")
        outcome = outcomes.get(event.get("event_id"))
        if outcome is None:
            raise ValueError(f"The superseded receipt lacks {event.get('event_id')}")
        if outcome.get("success") is not True:
            failures.append(dict(event))
    return failures


def correction_event(
    base_event: Mapping[str, Any], sequence: int, timeout_seconds: int
) -> dict[str, Any]:
    event = copy.deepcopy(dict(base_event))
    base_event_id = str(base_event["event_id"])
    event["event_id"] = f"{base_event_id}-corrective-{sequence:03d}"
    event["correction_of_event_id"] = base_event_id
    event["correction_sequence"] = sequence
    event["timeout_seconds"] = timeout_seconds
    return event


def build_plan(
    base_plan_path: Path,
    base_receipt_path: Path,
    *,
    sequence: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    if sequence < 2:
        raise ValueError("Corrective sequence must be at least 2")
    if timeout_seconds < 60 or timeout_seconds > 600:
        raise ValueError("Corrective timeout must be between 60 and 600 seconds")
    base_plan = load(base_plan_path)
    base_receipt = load(base_receipt_path)
    # The superseded plan is frozen evidence. Its bindings were checked before
    # the initial source execution, so concurrent unrelated working-tree edits
    # must not invalidate that completed attempt.
    errors = runner.validate_plan(base_plan, verify_bindings=False)
    if errors:
        raise ValueError("The superseded Springer plan is invalid: " + ", ".join(errors))
    if (
        base_receipt.get("schema_version") != runner.RUN_SCHEMA
        or base_receipt.get("plan_sha256") != digest(base_plan_path)
        or base_receipt.get("success") is not False
        or base_receipt.get("all_source_cells_attempted") is not True
    ):
        raise ValueError("The superseded Springer receipt is not a completed failed run")
    failed = base_failure_events(base_plan, base_receipt)
    if not failed:
        raise ValueError("The superseded Springer run has no failed source cells")
    outcomes = {
        item.get("event_id"): item
        for item in base_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    prior_attempts = []
    for prior_sequence in range(2, sequence):
        prior_root = base_plan_path.parent / f"corrective-{prior_sequence:03d}"
        prior_plan = prior_root / "final-event-plan.json"
        prior_receipts = (
            prior_root / "run-receipt.json",
            prior_root / "interrupted-run-receipt.json",
        )
        prior_receipt = next((path for path in prior_receipts if regular(path)), None)
        if regular(prior_plan) and prior_receipt is not None:
            prior_value = load(prior_receipt)
            prior_attempts.append(
                {
                    "sequence": prior_sequence,
                    "plan": relative(prior_plan),
                    "plan_sha256": digest(prior_plan),
                    "receipt": relative(prior_receipt),
                    "receipt_sha256": digest(prior_receipt),
                    "status": prior_value.get("status"),
                    "success": prior_value.get("success"),
                    "selected_for_final_union": False,
                }
            )
    failure_evidence = []
    for event in failed:
        outcome = outcomes[event["event_id"]]
        source_cell = runner.source_cell_name(event["partition_id"], event["cell_id"])
        diagnostic = base_plan_path.parent / f"{source_cell}.NON_MERGEABLE_DIAGNOSTIC.json"
        failure_evidence.append(
            {
                "superseded_event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "exit_code": outcome.get("exit_code"),
                "diagnostic": relative(diagnostic) if regular(diagnostic) else None,
                "diagnostic_sha256": digest(diagnostic) if regular(diagnostic) else None,
            }
        )
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": base_plan["source"],
        "source_id": base_plan["source_id"],
        "review_namespace": base_plan["review_namespace"],
        "review_id": base_plan["review_id"],
        "event_kind": "final",
        "phase": base_plan["phase"],
        "strategy_reference": base_plan["strategy_reference"],
        "repository_head_at_predeclaration": base_plan[
            "repository_head_at_predeclaration"
        ],
        "source_union_expected_partitions": base_plan[
            "source_union_expected_partitions"
        ],
        "source_union_expected_sources": base_plan["source_union_expected_sources"],
        "cutoff": copy.deepcopy(base_plan["cutoff"]),
        "source_configuration": copy.deepcopy(base_plan["source_configuration"]),
        "translation": copy.deepcopy(base_plan["translation"]),
        "capture_contract": copy.deepcopy(base_plan["capture_contract"]),
        "execution_policy": {
            **copy.deepcopy(base_plan["execution_policy"]),
            "superseded_successful_cells_reused": True,
            "one_source_execution_per_failed_cell": True,
            "retry_policy": "one corrective source execution per failed cell",
        },
        "adapter": {
            "id": "search_springer_link",
            "version": runner.adapter_version(),
            "sha256": digest(runner.ADAPTER),
            "entrypoint": str(runner.ADAPTER),
            "target_scoped_backend": {
                "path": str(BACKEND_PATH),
                "sha256": digest(BACKEND_PATH),
            },
        },
        "corrective_run": {
            "sequence": sequence,
            "reason": (
                "The first final run completed every planned source cell, but some "
                "cells became nonmergeable before normal publication. This corrective "
                "run repeats only those cells with unchanged source-native queries, "
                "controls, complete detail capture, and output contract."
            ),
            "superseded_plan": relative(base_plan_path),
            "superseded_plan_sha256": digest(base_plan_path),
            "superseded_run_receipt": relative(base_receipt_path),
            "superseded_run_receipt_sha256": digest(base_receipt_path),
            "superseded_failed_source_cell_count": len(failed),
            "superseded_failure_evidence": failure_evidence,
            "prior_corrective_attempts": prior_attempts,
            "timeout_seconds": timeout_seconds,
            "operational_repairs": [
                "Compare rendered card and detail titles after whitespace and Unicode case normalization while retaining punctuation exactness.",
                "Decode standard HTML character references before comparing the two rendered source title views.",
                "Normalize whitespace immediately before colon, semicolon, and comma title punctuation.",
                "Use committed-response detail navigation followed by the existing rendered metadata gates.",
                "Stop a validated detail document before opening the next card.",
                "Use at most three identical exact card navigation attempts, replacing only the invocation-owned stuck target between attempts.",
                "Allow at most eight refreshes of a page that repeats a prior canonical path, while retaining strict complete-pass reconciliation.",
            ],
            "query_or_filter_change": False,
        },
        "bindings": {
            "files": {
                relative(SCRIPT_PATH): digest(SCRIPT_PATH),
                relative(RUNNER_PATH): digest(RUNNER_PATH),
                relative(base_plan_path): digest(base_plan_path),
                relative(base_receipt_path): digest(base_receipt_path),
                str(BACKEND_PATH): digest(BACKEND_PATH),
                str(runner.ADAPTER): digest(runner.ADAPTER),
            }
        },
        "events": [
            correction_event(event, sequence, timeout_seconds) for event in failed
        ],
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    corrective = plan.get("corrective_run")
    if not isinstance(corrective, Mapping):
        return ["corrective_run"]
    sequence = corrective.get("sequence")
    if not isinstance(sequence, int) or sequence < 2:
        errors.append("sequence")
        sequence = 2
    timeout_seconds = corrective.get("timeout_seconds")
    if (
        not isinstance(timeout_seconds, int)
        or isinstance(timeout_seconds, bool)
        or timeout_seconds < 60
        or timeout_seconds > 600
    ):
        errors.append("timeout_seconds")
        timeout_seconds = DEFAULT_CORRECTIVE_TIMEOUT_SECONDS
    base_plan_path = REPOSITORY_ROOT / str(corrective.get("superseded_plan", ""))
    base_receipt_path = REPOSITORY_ROOT / str(
        corrective.get("superseded_run_receipt", "")
    )
    if not regular(base_plan_path) or not regular(base_receipt_path):
        return [*errors, "superseded_artifacts"]
    base_plan = load(base_plan_path)
    base_receipt = load(base_receipt_path)
    # Validate the frozen schedule without rereading mutable source documents.
    base_errors = runner.validate_plan(base_plan, verify_bindings=False)
    if base_errors:
        errors.extend(f"superseded:{error}" for error in base_errors)
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("source") != base_plan.get("source")
        or plan.get("source_id") != base_plan.get("source_id")
        or plan.get("review_namespace") != base_plan.get("review_namespace")
        or plan.get("review_id") != base_plan.get("review_id")
        or plan.get("event_kind") != "final"
        or plan.get("phase") != base_plan.get("phase")
        or plan.get("strategy_reference") != base_plan.get("strategy_reference")
        or plan.get("repository_head_at_predeclaration")
        != base_plan.get("repository_head_at_predeclaration")
        or corrective.get("superseded_plan_sha256") != digest(base_plan_path)
        or corrective.get("superseded_run_receipt_sha256") != digest(base_receipt_path)
        or plan.get("adapter", {}).get("id") != "search_springer_link"
        or plan.get("adapter", {}).get("version") != runner.adapter_version()
        or plan.get("adapter", {}).get("sha256") != digest(runner.ADAPTER)
        or plan.get("adapter", {}).get("entrypoint") != str(runner.ADAPTER)
        or plan.get("adapter", {}).get("target_scoped_backend", {}).get("path")
        != str(BACKEND_PATH)
        or plan.get("adapter", {}).get("target_scoped_backend", {}).get("sha256")
        != digest(BACKEND_PATH)
        or corrective.get("query_or_filter_change") is not False
        or not isinstance(corrective.get("operational_repairs"), list)
        or len(corrective.get("operational_repairs")) != 7
        or plan.get("cutoff") != base_plan.get("cutoff")
        or plan.get("source_configuration") != base_plan.get("source_configuration")
        or plan.get("translation") != base_plan.get("translation")
        or plan.get("capture_contract") != base_plan.get("capture_contract")
    ):
        errors.append("identity")
    prior_attempts = corrective.get("prior_corrective_attempts")
    if not isinstance(prior_attempts, list) or len(prior_attempts) != max(0, sequence - 2):
        errors.append("prior_corrective_attempts")
    else:
        for expected_sequence, item in enumerate(prior_attempts, start=2):
            if not isinstance(item, Mapping):
                errors.append(f"prior_corrective_attempt:{expected_sequence}")
                continue
            prior_plan = REPOSITORY_ROOT / str(item.get("plan", ""))
            prior_receipt = REPOSITORY_ROOT / str(item.get("receipt", ""))
            if (
                item.get("sequence") != expected_sequence
                or item.get("selected_for_final_union") is not False
                or not regular(prior_plan)
                or not regular(prior_receipt)
                or item.get("plan_sha256") != digest(prior_plan)
                or item.get("receipt_sha256") != digest(prior_receipt)
            ):
                errors.append(f"prior_corrective_attempt:{expected_sequence}")
    try:
        failed = base_failure_events(base_plan, base_receipt)
    except (KeyError, ValueError) as error:
        return [*errors, f"superseded_failure_set:{type(error).__name__}"]
    expected = [
        correction_event(event, sequence, timeout_seconds) for event in failed
    ]
    if plan.get("events") != expected:
        errors.append("source_cell_schedule")
    if corrective.get("superseded_failed_source_cell_count") != len(failed):
        errors.append("failure_count")
    if verify_bindings:
        bindings = plan.get("bindings", {}).get("files") if isinstance(plan.get("bindings"), Mapping) else None
        if not isinstance(bindings, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in bindings.items():
                path = REPOSITORY_ROOT / str(name)
                if not regular(path) or not isinstance(expected_hash, str) or digest(path) != expected_hash:
                    errors.append(f"binding_changed:{name}")
    return errors


def run_corrective(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    *,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid corrective Springer plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The corrective Springer output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not runner.cdp_is_loopback(cdp_url):
        raise ValueError("Corrective Springer execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    started_at = now()
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_file(output_dir, event)
        if runner.output_paths_occupied(output):
            raise FileExistsError(
                f"Refusing to overwrite corrective artifacts for {event['cell_id']}"
            )
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                runner.command_for(event, output, plan, cdp_url),
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            summary = runner.artifact_summary(output, event, plan)
        except Exception as error:
            summary = {
                "artifact_written": regular(output),
                "valid": False,
                "runner_failure": type(error).__name__,
            }
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "correction_of_event_id": event["correction_of_event_id"],
            "parent_event_id": event["parent_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "success": success,
            "artifact": output.name if regular(output) else None,
            "exit_code": exit_code,
            "source_command_attempt_count": 1,
            "stdout_sha256": runner.digest_text(stdout),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": runner.digest_text(stderr),
            "stderr_bytes": len(stderr.encode("utf-8")),
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "cell": event["cell_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": outcome.get("source_total"),
                    "retained_records": outcome.get("retained_record_count"),
                    "full_abstracts": outcome.get("full_abstract_count"),
                    "missing_types": outcome.get("missing_publication_type_count"),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == len(plan["events"]) and all(
        item.get("success") is True for item in outcomes
    )
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": plan["source"],
        "source_id": plan["source_id"],
        "review_namespace": plan["review_namespace"],
        "event_kind": "final",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "corrective_run": plan["corrective_run"],
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "source_command_attempt_count": len(outcomes),
        "accepted_source_cell_count": sum(item.get("success") is True for item in outcomes),
        "all_source_cells_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def selected_events(
    base_plan: Mapping[str, Any],
    base_receipt: Mapping[str, Any],
    base_output_dir: Path,
    corrective_plan: Mapping[str, Any],
    corrective_receipt: Mapping[str, Any],
    corrective_output_dir: Path,
) -> list[dict[str, Any]]:
    base_outcomes = {
        item.get("event_id"): item
        for item in base_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    corrective_outcomes = {
        item.get("correction_of_event_id"): item
        for item in corrective_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    corrective_events = {
        item.get("correction_of_event_id"): item
        for item in corrective_plan.get("events", [])
        if isinstance(item, Mapping)
    }
    selected: list[dict[str, Any]] = []
    for base_event in base_plan["events"]:
        base_outcome = base_outcomes.get(base_event["event_id"])
        if base_outcome is None:
            raise ValueError(f"The superseded receipt lacks {base_event['event_id']}")
        if base_outcome.get("success") is True:
            actual_event = base_event
            actual_plan = base_plan
            actual_outcome = base_outcome
            artifact = output_file(base_output_dir, base_event)
            origin = "initial_final_run"
        else:
            actual_event = corrective_events.get(base_event["event_id"])
            actual_outcome = corrective_outcomes.get(base_event["event_id"])
            if actual_event is None or actual_outcome is None or actual_outcome.get("success") is not True:
                raise ValueError(f"The corrective receipt lacks {base_event['event_id']}")
            actual_plan = corrective_plan
            artifact = output_file(corrective_output_dir, actual_event)
            origin = "corrective_run"
        summary = runner.artifact_summary(artifact, actual_event, actual_plan)
        if summary.get("valid") is not True:
            raise ValueError(f"The selected final artifact is invalid: {artifact}")
        selected.append(
            {
                "logical_event": base_event,
                "actual_event": actual_event,
                "actual_plan": actual_plan,
                "actual_outcome": actual_outcome,
                "artifact": artifact,
                "origin": origin,
                "summary": summary,
            }
        )
    return selected


def reconcile(
    base_plan_path: Path,
    base_receipt_path: Path,
    base_output_dir: Path,
    corrective_plan_path: Path,
    corrective_receipt_path: Path,
    corrective_output_dir: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    base_plan = load(base_plan_path)
    base_receipt = load(base_receipt_path)
    corrective_plan = load(corrective_plan_path)
    corrective_receipt = load(corrective_receipt_path)
    errors = runner.validate_plan(base_plan, verify_bindings=False)
    errors.extend(validate_plan(corrective_plan, verify_bindings=True))
    if (
        corrective_receipt.get("schema_version") != RUN_SCHEMA
        or corrective_receipt.get("plan_sha256") != digest(corrective_plan_path)
        or corrective_receipt.get("success") is not True
    ):
        errors.append("corrective_receipt")
    try:
        selected = selected_events(
            base_plan,
            base_receipt,
            base_output_dir,
            corrective_plan,
            corrective_receipt,
            corrective_output_dir,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"selected_events:{type(error).__name__}")
        selected = []
    outcomes = []
    for item in selected:
        logical = item["logical_event"]
        actual = item["actual_event"]
        summary = item["summary"]
        outcomes.append(
            {
                "logical_event_id": logical["event_id"],
                "event_id": actual["event_id"],
                "parent_event_id": actual["parent_event_id"],
                "partition_id": actual["partition_id"],
                "cell_id": actual["cell_id"],
                "artifact": relative(item["artifact"]),
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_bytes": summary["artifact_bytes"],
                "origin": item["origin"],
                "success": summary["valid"] is True,
                "source_command_reexecuted": item["origin"] == "corrective_run",
                "full_abstract_count": summary["full_abstract_count"],
                "source_abstract_not_available_count": summary[
                    "source_abstract_not_available_count"
                ],
                "publication_type_counts": summary["publication_type_counts"],
                "missing_publication_type_count": summary[
                    "missing_publication_type_count"
                ],
            }
        )
    success = bool(
        not errors
        and len(outcomes) == len(base_plan["events"])
        and all(item["success"] for item in outcomes)
    )
    value = {
        "schema_version": RECONCILIATION_SCHEMA,
        "source": base_plan["source"],
        "source_id": base_plan["source_id"],
        "review_namespace": base_plan["review_namespace"],
        "event_kind": "final",
        "strategy_reference": base_plan["strategy_reference"],
        "strategy_version": base_plan["repository_head_at_predeclaration"],
        "superseded_plan": relative(base_plan_path),
        "superseded_plan_sha256": digest(base_plan_path),
        "superseded_run_receipt": relative(base_receipt_path),
        "superseded_run_receipt_sha256": digest(base_receipt_path),
        "corrective_plan": relative(corrective_plan_path),
        "corrective_plan_sha256": digest(corrective_plan_path),
        "corrective_run_receipt": relative(corrective_receipt_path),
        "corrective_run_receipt_sha256": digest(corrective_receipt_path),
        "source_commands_reexecuted": sum(
            item["source_command_reexecuted"] for item in outcomes
        ),
        "planned_source_cell_count": len(base_plan["events"]),
        "selected_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(item["success"] for item in outcomes),
        "success": success,
        "outcomes": outcomes,
        "validation_errors": errors,
        "reconciled_at_utc": now(),
    }
    write_new(output_path, value)
    return 0 if success else 1


def selected_from_reconciliation(
    reconciliation: Mapping[str, Any],
    base_plan: Mapping[str, Any],
    base_output_dir: Path,
    corrective_plan: Mapping[str, Any],
    corrective_output_dir: Path,
) -> list[dict[str, Any]]:
    if reconciliation.get("schema_version") != RECONCILIATION_SCHEMA or reconciliation.get("success") is not True:
        raise ValueError("The Springer reconciliation is incomplete")
    rows = {
        item.get("logical_event_id"): item
        for item in reconciliation.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    corrective_events = {
        item.get("correction_of_event_id"): item
        for item in corrective_plan.get("events", [])
        if isinstance(item, Mapping)
    }
    selected: list[dict[str, Any]] = []
    for base_event in base_plan["events"]:
        row = rows.get(base_event["event_id"])
        if row is None or row.get("success") is not True:
            raise ValueError(f"The reconciliation lacks {base_event['event_id']}")
        if row.get("origin") == "initial_final_run":
            actual_event = base_event
            actual_plan = base_plan
            artifact = output_file(base_output_dir, base_event)
        elif row.get("origin") == "corrective_run":
            actual_event = corrective_events.get(base_event["event_id"])
            if actual_event is None:
                raise ValueError(f"The corrective plan lacks {base_event['event_id']}")
            actual_plan = corrective_plan
            artifact = output_file(corrective_output_dir, actual_event)
        else:
            raise ValueError(f"The reconciliation has an invalid origin for {base_event['event_id']}")
        summary = runner.artifact_summary(artifact, actual_event, actual_plan)
        if summary.get("valid") is not True:
            raise ValueError(f"The reconciled artifact is invalid: {artifact}")
        if (
            row.get("event_id") != actual_event["event_id"]
            or row.get("artifact_sha256") != summary["artifact_sha256"]
            or row.get("artifact_bytes") != summary["artifact_bytes"]
        ):
            raise ValueError(f"The reconciliation binding changed: {base_event['event_id']}")
        selected.append(
            {
                "logical_event": base_event,
                "actual_event": actual_event,
                "actual_plan": actual_plan,
                "artifact": artifact,
                "summary": summary,
                "origin": row["origin"],
            }
        )
    return selected


def build_cell_declarations(
    reconciliation_path: Path,
    base_plan_path: Path,
    base_output_dir: Path,
    corrective_plan_path: Path,
    corrective_output_dir: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    reconciliation = load(reconciliation_path)
    base_plan = load(base_plan_path)
    corrective_plan = load(corrective_plan_path)
    selected = selected_from_reconciliation(
        reconciliation,
        base_plan,
        base_output_dir,
        corrective_plan,
        corrective_output_dir,
    )
    cells = []
    for item in selected:
        logical = item["logical_event"]
        actual = item["actual_event"]
        summary = item["summary"]
        cells.append(
            {
                "source_id": base_plan["source_id"],
                "partition_id": logical["partition_id"],
                "cell_id": logical["cell_id"],
                "parent_event_id": logical["parent_event_id"],
                "source_run_id": actual["event_id"],
                "query": logical["query"],
                "requested_query": logical["query"],
                "executed_query": logical["query"],
                "source_native_executed_query": logical["query"],
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_byte_count": summary["artifact_bytes"],
                "stable_ids": summary["record_paper_ids"],
                "status": "complete",
                "report_ready": True,
                "artifact": relative(item["artifact"]),
                "origin": item["origin"],
            }
        )
    value = {
        "schema_version": CELL_DECLARATIONS_SCHEMA,
        "source": base_plan["source"],
        "source_id": base_plan["source_id"],
        "review_namespace": base_plan["review_namespace"],
        "reconciliation": relative(reconciliation_path),
        "reconciliation_sha256": digest(reconciliation_path),
        "expected_cells": cells,
    }
    write_new(output_path, value)
    return 0


def create_source_union(
    reconciliation_path: Path,
    base_plan_path: Path,
    base_output_dir: Path,
    corrective_plan_path: Path,
    corrective_output_dir: Path,
    declarations_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    reconciliation = load(reconciliation_path)
    base_plan = load(base_plan_path)
    corrective_plan = load(corrective_plan_path)
    declarations = load(declarations_path)
    if declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA:
        raise ValueError("Unexpected reconciled Springer cell-declaration schema")
    selected = selected_from_reconciliation(
        reconciliation,
        base_plan,
        base_output_dir,
        corrective_plan,
        corrective_output_dir,
    )
    command = [
        "uv",
        "run",
        str(runner.SOURCE_UNION_TOOL),
        "--input",
        *(str(item["artifact"]) for item in selected),
        "--output-path",
        str(output_path),
        "--expected-partitions",
        *runner.PARTITIONS,
        "--expected-sources",
        runner.SOURCE_ID,
        "--review-namespace",
        runner.REVIEW_NAMESPACE,
        "--expected-cells",
        str(declarations_path),
    ]
    completed = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0 or not regular(output_path):
        raise RuntimeError("Could not create the reconciled Springer source union")
    return 0


def assess(
    reconciliation_path: Path,
    base_plan_path: Path,
    base_output_dir: Path,
    corrective_plan_path: Path,
    corrective_output_dir: Path,
    declarations_path: Path,
    union_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    reconciliation = load(reconciliation_path)
    base_plan = load(base_plan_path)
    corrective_plan = load(corrective_plan_path)
    declarations = load(declarations_path)
    source_union = load(union_path)
    errors = runner.validate_plan(base_plan, verify_bindings=False)
    errors.extend(validate_plan(corrective_plan, verify_bindings=True))
    if (
        reconciliation.get("schema_version") != RECONCILIATION_SCHEMA
        or reconciliation.get("success") is not True
        or reconciliation.get("selected_source_cell_count") != len(base_plan["events"])
    ):
        errors.append("reconciliation")
    if (
        declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA
        or declarations.get("reconciliation_sha256") != digest(reconciliation_path)
        or len(declarations.get("expected_cells", [])) != len(base_plan["events"])
    ):
        errors.append("cell_declarations")
    try:
        selected = selected_from_reconciliation(
            reconciliation,
            base_plan,
            base_output_dir,
            corrective_plan,
            corrective_output_dir,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"selected_events:{type(error).__name__}")
        selected = []

    source_total_sum = 0
    retained_count = 0
    excluded_count = 0
    full_abstract_count = 0
    absent_abstract_count = 0
    publication_types: Counter[str] = Counter()
    record_ids: list[str] = []
    event_evidence = []
    for item in selected:
        logical = item["logical_event"]
        actual = item["actual_event"]
        summary = item["summary"]
        total = summary["source_total"]
        retained = summary["retained_record_count"]
        excluded = summary["client_date_excluded_count"]
        if not all(isinstance(value, int) and value >= 0 for value in (total, retained, excluded)):
            errors.append(f"count_shape:{logical['cell_id']}")
        elif total != retained + excluded:
            errors.append(f"date_accounting:{logical['cell_id']}")
        source_total_sum += total if isinstance(total, int) else 0
        retained_count += retained if isinstance(retained, int) else 0
        excluded_count += excluded if isinstance(excluded, int) else 0
        full_abstract_count += summary["full_abstract_count"]
        absent_abstract_count += summary["source_abstract_not_available_count"]
        publication_types.update(summary["publication_type_counts"])
        record_ids.extend(summary["record_paper_ids"])
        event_evidence.append(
            {
                "logical_event_id": logical["event_id"],
                "source_run_id": actual["event_id"],
                "partition_id": logical["partition_id"],
                "cell_id": logical["cell_id"],
                "origin": item["origin"],
                "artifact": relative(item["artifact"]),
                "artifact_sha256": summary["artifact_sha256"],
                "source_total": total,
                "retained_record_count": retained,
                "client_date_excluded_count": excluded,
                "full_abstract_count": summary["full_abstract_count"],
                "source_abstract_not_available_count": summary[
                    "source_abstract_not_available_count"
                ],
                "publication_type_counts": summary["publication_type_counts"],
                "missing_publication_type_count": summary[
                    "missing_publication_type_count"
                ],
                "all_retained_rows_have_abstract_field": summary[
                    "abstract_field_complete"
                ],
                "all_retained_rows_have_publication_type": summary[
                    "publication_type_field_complete"
                ],
            }
        )

    union_source = source_union.get("source_unions", {}).get(runner.SOURCE_ID, {})
    union_valid = bool(
        source_union.get("schema_version") == "academic-search-source-union-receipt/v1"
        and source_union.get("review_namespace") == runner.REVIEW_NAMESPACE
        and source_union.get("review_id") == runner.REVIEW_ID
        and source_union.get("strategy_reference") == runner.STRATEGY_REFERENCE
        and source_union.get("strategy_version")
        == base_plan.get("repository_head_at_predeclaration")
        and source_union.get("expected_partitions") == list(runner.PARTITIONS)
        and source_union.get("expected_sources") == [runner.SOURCE_ID]
        and source_union.get("event_count") == len(base_plan["events"])
        and source_union.get("artifact_count") == len(base_plan["events"])
        and union_source.get("completeness_status") == "complete"
        and union_source.get("failure_status") == "none"
        and union_source.get("event_total_sum") == source_total_sum
    )
    if not union_valid:
        errors.append("source_union")
    cell_unions = union_source.get("cell_unions", {})
    for partition in runner.PARTITIONS:
        expected = sum(event["partition_id"] == partition for event in base_plan["events"])
        if cell_unions.get(partition, {}).get("cell_count") != expected:
            errors.append(f"source_union_cell:{partition}")

    capture_complete = all(
        item["all_retained_rows_have_abstract_field"] is True
        and item["all_retained_rows_have_publication_type"] is True
        and item["missing_publication_type_count"] == 0
        for item in event_evidence
    )
    value = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": base_plan["source"],
        "source_id": base_plan["source_id"],
        "review_namespace": base_plan["review_namespace"],
        "reconciliation": relative(reconciliation_path),
        "reconciliation_sha256": digest(reconciliation_path),
        "source_cell_declarations": relative(declarations_path),
        "source_cell_declarations_sha256": digest(declarations_path),
        "source_union_receipt": relative(union_path),
        "source_union_receipt_sha256": digest(union_path),
        "adapter": base_plan["adapter"],
        "cutoff": base_plan["cutoff"],
        "source_cell_count": len(base_plan["events"]),
        "accepted_source_cell_count": len(selected),
        "source_record_occurrence_count": retained_count,
        "source_client_date_excluded_occurrence_count": excluded_count,
        "source_total_occurrence_count": source_total_sum,
        "unique_retained_source_card_path_count": len(set(record_ids)),
        "unique_retained_source_card_path_set_sha256": runner.digest_set(set(record_ids)),
        "full_abstract_occurrence_count": full_abstract_count,
        "source_abstract_not_available_occurrence_count": absent_abstract_count,
        "publication_type_occurrence_count": sum(publication_types.values()),
        "publication_type_counts": dict(sorted(publication_types.items())),
        "full_abstract_and_publication_type_capture_complete": bool(
            not errors and capture_complete
        ),
        "source_union_valid": union_valid,
        "source_cells": event_evidence,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new(output_path, value)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-plan")
    build.add_argument("--superseded-plan", type=Path, required=True)
    build.add_argument("--superseded-receipt", type=Path, required=True)
    build.add_argument("--sequence", type=int, default=2)
    build.add_argument(
        "--timeout-seconds", type=int, default=DEFAULT_CORRECTIVE_TIMEOUT_SECONDS
    )
    build.add_argument("--output", type=Path, required=True)

    check = subparsers.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--verify-bindings", action="store_true")

    run = subparsers.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)
    run.add_argument("--settle-seconds", type=float, default=3.0)

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("--superseded-plan", type=Path, required=True)
    reconcile_parser.add_argument("--superseded-receipt", type=Path, required=True)
    reconcile_parser.add_argument("--superseded-output-dir", type=Path, required=True)
    reconcile_parser.add_argument("--corrective-plan", type=Path, required=True)
    reconcile_parser.add_argument("--corrective-receipt", type=Path, required=True)
    reconcile_parser.add_argument("--corrective-output-dir", type=Path, required=True)
    reconcile_parser.add_argument("--output", type=Path, required=True)

    declarations = subparsers.add_parser("build-cell-declarations")
    declarations.add_argument("--reconciliation", type=Path, required=True)
    declarations.add_argument("--superseded-plan", type=Path, required=True)
    declarations.add_argument("--superseded-output-dir", type=Path, required=True)
    declarations.add_argument("--corrective-plan", type=Path, required=True)
    declarations.add_argument("--corrective-output-dir", type=Path, required=True)
    declarations.add_argument("--output", type=Path, required=True)

    union = subparsers.add_parser("source-union")
    union.add_argument("--reconciliation", type=Path, required=True)
    union.add_argument("--superseded-plan", type=Path, required=True)
    union.add_argument("--superseded-output-dir", type=Path, required=True)
    union.add_argument("--corrective-plan", type=Path, required=True)
    union.add_argument("--corrective-output-dir", type=Path, required=True)
    union.add_argument("--cell-declarations", type=Path, required=True)
    union.add_argument("--output", type=Path, required=True)

    assessment = subparsers.add_parser("assess")
    assessment.add_argument("--reconciliation", type=Path, required=True)
    assessment.add_argument("--superseded-plan", type=Path, required=True)
    assessment.add_argument("--superseded-output-dir", type=Path, required=True)
    assessment.add_argument("--corrective-plan", type=Path, required=True)
    assessment.add_argument("--corrective-output-dir", type=Path, required=True)
    assessment.add_argument("--cell-declarations", type=Path, required=True)
    assessment.add_argument("--source-union", type=Path, required=True)
    assessment.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan(
            args.superseded_plan,
            args.superseded_receipt,
            sequence=args.sequence,
            timeout_seconds=args.timeout_seconds,
        )
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid corrective Springer plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        if args.settle_seconds < 0:
            raise ValueError("--settle-seconds cannot be negative")
        return run_corrective(
            args.plan,
            args.output_dir,
            args.receipt,
            settle_seconds=args.settle_seconds,
        )
    if args.command == "reconcile":
        return reconcile(
            args.superseded_plan,
            args.superseded_receipt,
            args.superseded_output_dir,
            args.corrective_plan,
            args.corrective_receipt,
            args.corrective_output_dir,
            args.output,
        )
    if args.command == "build-cell-declarations":
        return build_cell_declarations(
            args.reconciliation,
            args.superseded_plan,
            args.superseded_output_dir,
            args.corrective_plan,
            args.corrective_output_dir,
            args.output,
        )
    if args.command == "source-union":
        return create_source_union(
            args.reconciliation,
            args.superseded_plan,
            args.superseded_output_dir,
            args.corrective_plan,
            args.corrective_output_dir,
            args.cell_declarations,
            args.output,
        )
    if args.command == "assess":
        return assess(
            args.reconciliation,
            args.superseded_plan,
            args.superseded_output_dir,
            args.corrective_plan,
            args.corrective_output_dir,
            args.cell_declarations,
            args.source_union,
            args.output,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
