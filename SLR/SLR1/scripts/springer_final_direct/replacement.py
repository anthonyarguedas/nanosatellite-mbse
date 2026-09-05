#!/usr/bin/env python3
"""Run and finalize Springer source-year replacement cells."""

from __future__ import annotations

import argparse
import copy
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
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

PLAN_SCHEMA = "slr1-springer-nature-link-source-year-replacement-plan/v1"
RUN_SCHEMA = "slr1-springer-nature-link-source-year-replacement-run/v1"
RECONCILIATION_SCHEMA = "slr1-springer-nature-link-final-reconciliation/v1"
DECLARATIONS_SCHEMA = "slr1-springer-nature-link-final-cell-declarations/v1"
RECORD_UNION_SCHEMA = "slr1-springer-nature-link-final-record-union/v1"
ASSESSMENT_SCHEMA = "slr1-springer-nature-link-final-assessment/v1"
REPLACED_PARTITIONS = ("B2", "BC1", "BT2")
SEQUENCE = 6
TIMEOUT_SECONDS = 180


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("slr1_springer_replacement_runner", RUNNER_PATH)


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


def regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def event_output(root: Path, event: Mapping[str, Any]) -> Path:
    return root / str(event["output_filename"])


def adapter_contract() -> dict[str, Any]:
    return {
        "id": "search_springer_link",
        "version": runner.adapter_version(),
        "sha256": digest(runner.ADAPTER),
        "entrypoint": str(runner.ADAPTER),
        "target_scoped_backend": {
            "path": str(BACKEND_PATH),
            "sha256": digest(BACKEND_PATH),
        },
    }


def replacement_event(
    logical_event: Mapping[str, Any],
    *,
    cell_id: str,
    source_year: int,
    output_filename: str,
) -> dict[str, Any]:
    event = copy.deepcopy(dict(logical_event))
    event.update(
        {
            "event_id": (
                f"final-main-{logical_event['partition_id']}-{cell_id}-"
                f"springer-nature-link-replacement-{SEQUENCE:03d}"
            ),
            "parent_event_id": runner.parent_event_id(
                str(logical_event["partition_id"])
            ),
            "cell_id": cell_id,
            "branch": f"{logical_event['branch']}; source year {source_year}",
            "output_filename": output_filename,
            "date_start": runner.DATE_START,
            "date_end": runner.DATE_END,
            "source_year_start": source_year,
            "source_year_end": source_year,
            "source_year_partition": source_year,
            "timeout_seconds": TIMEOUT_SECONDS,
            "replacement_sequence": SEQUENCE,
            "replacement_of_event_id": logical_event["event_id"],
            "replacement_reason": (
                "separate source-year control with the unchanged global exact-day window"
            ),
        }
    )
    return event


def build_events(base_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    base_events = [
        event for event in base_plan["events"] if isinstance(event, Mapping)
    ]
    events: list[dict[str, Any]] = []

    for logical in base_events:
        if logical.get("partition_id") != "B2":
            continue
        year = logical.get("source_year_partition")
        if not isinstance(year, int) or isinstance(year, bool):
            raise ValueError("The accepted B2 source cell lacks its source year")
        cell_id = str(logical["cell_id"])
        events.append(
            replacement_event(
                logical,
                cell_id=cell_id,
                source_year=year,
                output_filename=f"B2/{cell_id}.json",
            )
        )

    direct_by_partition = {
        str(event["partition_id"]): event
        for event in base_events
        if event.get("partition_id") in {"BC1", "BT2"}
    }
    for partition in ("BC1", "BT2"):
        logical = direct_by_partition.get(partition)
        if logical is None or logical.get("cell_id") != "direct":
            raise ValueError(f"The accepted {partition} direct cell is unavailable")
        for year in range(2011, 2027):
            cell_id = f"year-{year}"
            events.append(
                replacement_event(
                    logical,
                    cell_id=cell_id,
                    source_year=year,
                    output_filename=f"{partition}/{cell_id}.json",
                )
            )

    if len(events) != 57:
        raise ValueError("The Springer source-year replacement schedule changed")
    return events


def prior_attempts(base_plan_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sequence in range(2, 6):
        root = base_plan_path.parent / f"corrective-{sequence:03d}"
        plan = root / "final-event-plan.json"
        receipt_candidates = (
            root / "run-receipt.json",
            root / "interrupted-run-receipt.json",
        )
        receipt = next((path for path in receipt_candidates if regular(path)), None)
        if not regular(plan) or receipt is None:
            raise ValueError(f"Missing corrective attempt {sequence:03d}")
        value = load(receipt)
        rows.append(
            {
                "sequence": sequence,
                "plan": relative(plan),
                "plan_sha256": digest(plan),
                "receipt": relative(receipt),
                "receipt_sha256": digest(receipt),
                "status": value.get("status"),
                "success": value.get("success"),
                "selected_wholesale": False,
            }
        )
    return rows


def build_plan(
    base_plan_path: Path,
    base_receipt_path: Path,
    accepted_corrective_plan_path: Path,
    accepted_corrective_receipt_path: Path,
) -> dict[str, Any]:
    base_plan = load(base_plan_path)
    base_receipt = load(base_receipt_path)
    corrective_plan = load(accepted_corrective_plan_path)
    corrective_receipt = load(accepted_corrective_receipt_path)
    errors = runner.validate_plan(base_plan, verify_bindings=False)
    if errors:
        raise ValueError("Invalid frozen Springer base plan: " + ", ".join(errors))
    if (
        base_receipt.get("schema_version") != runner.RUN_SCHEMA
        or base_receipt.get("plan_sha256") != digest(base_plan_path)
        or base_receipt.get("all_source_cells_attempted") is not True
        or corrective_receipt.get("plan_sha256")
        != digest(accepted_corrective_plan_path)
        or corrective_receipt.get("all_source_cells_attempted") is not True
    ):
        raise ValueError("The Springer predecessor receipts are incomplete")
    events = build_events(base_plan)
    bindings = (
        SCRIPT_PATH,
        RUNNER_PATH,
        runner.QUERY_SNAPSHOT,
        runner.SOURCE_GUIDELINE,
        base_plan_path,
        base_receipt_path,
        accepted_corrective_plan_path,
        accepted_corrective_receipt_path,
        runner.ADAPTER,
        BACKEND_PATH,
    )
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "review_id": runner.REVIEW_ID,
        "event_kind": "final",
        "phase": runner.PHASE,
        "strategy_reference": runner.STRATEGY_REFERENCE,
        "strategy_version": base_plan["repository_head_at_predeclaration"],
        "replacement_sequence": SEQUENCE,
        "source_union_expected_partitions": list(runner.PARTITIONS),
        "source_union_expected_sources": [runner.SOURCE_ID],
        "replacement_scope": {
            "partitions": list(REPLACED_PARTITIONS),
            "B2": (
                "Repeat every accepted B2 source-year or fixed Boolean cell. "
                "Keep the source year separate from the global exact-day window."
            ),
            "BC1": "Replace the repeatedly unstable direct cell with 16 source-year cells.",
            "BT2": "Replace the repeatedly unstable direct cell with 16 source-year cells.",
            "lossless_boolean_union": True,
            "query_terms_added_or_removed": False,
            "result_based_exclusions": False,
        },
        "date_contract": {
            "client_exact_date_start": runner.DATE_START,
            "client_exact_date_end": runner.DATE_END,
            "source_year_control": "one inclusive Link source year per event",
            "cross_year_detail_date_rule": (
                "Retain a detail date assigned to another source year when it remains "
                "inside the global exact evidence window."
            ),
        },
        "capture_contract": {
            "full_visible_abstracts_required": True,
            "source_abstract_absence_must_be_explicit": True,
            "raw_source_document_type_required": True,
            "publication_type_filter": None,
            "two_complete_card_path_passes": True,
            "automatic_screenshots_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_cell": True,
            "continue_after_cell_failure": True,
            "retry_policy": "none after replacement plan execution begins",
            "timeout_seconds": TIMEOUT_SECONDS,
            "source_year_partition_option": "--source-year-partition",
            "skip_full_abstracts": False,
        },
        "adapter": adapter_contract(),
        "lineage": {
            "base_plan": relative(base_plan_path),
            "base_plan_sha256": digest(base_plan_path),
            "base_receipt": relative(base_receipt_path),
            "base_receipt_sha256": digest(base_receipt_path),
            "accepted_corrective_plan": relative(accepted_corrective_plan_path),
            "accepted_corrective_plan_sha256": digest(
                accepted_corrective_plan_path
            ),
            "accepted_corrective_receipt": relative(
                accepted_corrective_receipt_path
            ),
            "accepted_corrective_receipt_sha256": digest(
                accepted_corrective_receipt_path
            ),
            "prior_corrective_attempts": prior_attempts(base_plan_path),
        },
        "bindings": {
            "files": {
                str(path) if path.is_absolute() else relative(path): digest(path)
                for path in bindings
            }
        },
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    lineage = plan.get("lineage")
    if not isinstance(lineage, Mapping):
        return ["lineage"]
    base_plan_path = REPOSITORY_ROOT / str(lineage.get("base_plan", ""))
    base_receipt_path = REPOSITORY_ROOT / str(lineage.get("base_receipt", ""))
    corrective_plan_path = REPOSITORY_ROOT / str(
        lineage.get("accepted_corrective_plan", "")
    )
    corrective_receipt_path = REPOSITORY_ROOT / str(
        lineage.get("accepted_corrective_receipt", "")
    )
    if not all(
        regular(path)
        for path in (
            base_plan_path,
            base_receipt_path,
            corrective_plan_path,
            corrective_receipt_path,
        )
    ):
        return ["lineage_artifacts"]
    base_plan = load(base_plan_path)
    base_errors = runner.validate_plan(base_plan, verify_bindings=False)
    errors.extend(f"base:{error}" for error in base_errors)
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("source") != runner.SOURCE
        or plan.get("source_id") != runner.SOURCE_ID
        or plan.get("review_namespace") != runner.REVIEW_NAMESPACE
        or plan.get("review_id") != runner.REVIEW_ID
        or plan.get("event_kind") != "final"
        or plan.get("phase") != runner.PHASE
        or plan.get("strategy_reference") != runner.STRATEGY_REFERENCE
        or plan.get("strategy_version")
        != base_plan.get("repository_head_at_predeclaration")
        or plan.get("replacement_sequence") != SEQUENCE
        or plan.get("source_union_expected_partitions") != list(runner.PARTITIONS)
        or plan.get("source_union_expected_sources") != [runner.SOURCE_ID]
        or lineage.get("base_plan_sha256") != digest(base_plan_path)
        or lineage.get("base_receipt_sha256") != digest(base_receipt_path)
        or lineage.get("accepted_corrective_plan_sha256")
        != digest(corrective_plan_path)
        or lineage.get("accepted_corrective_receipt_sha256")
        != digest(corrective_receipt_path)
    ):
        errors.append("identity")
    scope = plan.get("replacement_scope")
    dates = plan.get("date_contract")
    capture = plan.get("capture_contract")
    execution = plan.get("execution_policy")
    if not isinstance(scope, Mapping) or (
        scope.get("partitions") != list(REPLACED_PARTITIONS)
        or scope.get("lossless_boolean_union") is not True
        or scope.get("query_terms_added_or_removed") is not False
        or scope.get("result_based_exclusions") is not False
    ):
        errors.append("replacement_scope")
    if not isinstance(dates, Mapping) or (
        dates.get("client_exact_date_start") != runner.DATE_START
        or dates.get("client_exact_date_end") != runner.DATE_END
    ):
        errors.append("date_contract")
    if not isinstance(capture, Mapping) or (
        capture.get("full_visible_abstracts_required") is not True
        or capture.get("source_abstract_absence_must_be_explicit") is not True
        or capture.get("raw_source_document_type_required") is not True
        or capture.get("publication_type_filter") is not None
        or capture.get("two_complete_card_path_passes") is not True
        or capture.get("automatic_screenshots_required") is not True
    ):
        errors.append("capture_contract")
    if not isinstance(execution, Mapping) or (
        execution.get("retry_policy")
        != "none after replacement plan execution begins"
        or execution.get("timeout_seconds") != TIMEOUT_SECONDS
        or execution.get("source_year_partition_option")
        != "--source-year-partition"
        or execution.get("skip_full_abstracts") is not False
    ):
        errors.append("execution_policy")
    if plan.get("adapter") != adapter_contract():
        errors.append("adapter")
    try:
        expected_events = build_events(base_plan)
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"events:{type(error).__name__}")
        expected_events = []
    if plan.get("events") != expected_events:
        errors.append("events")
    if verify_bindings:
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected in files.items():
                path = Path(str(name))
                if not path.is_absolute():
                    path = REPOSITORY_ROOT / path
                if not regular(path) or not isinstance(expected, str) or digest(path) != expected:
                    errors.append(f"binding_changed:{name}")
    return errors


def run_plan(
    plan_path: Path,
    output_root: Path,
    receipt_path: Path,
    *,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid Springer replacement plan: " + ", ".join(errors))
    if output_root.is_symlink():
        raise ValueError("The Springer replacement root cannot be a symlink")
    output_root.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not runner.cdp_is_loopback(cdp_url):
        raise ValueError("Springer replacement requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started_at = now()
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = event_output(output_root, event)
        output.parent.mkdir(parents=True, exist_ok=True)
        if runner.output_paths_occupied(output):
            raise FileExistsError(f"Refusing to overwrite {event['event_id']}")
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
            "parent_event_id": event["parent_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "source_year_partition": event["source_year_partition"],
            "success": success,
            "artifact": relative(output) if regular(output) else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            "stdout_sha256": runner.digest_text(stdout),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": runner.digest_text(stderr),
            "stderr_bytes": len(stderr.encode("utf-8")),
            "safe_stderr_tail": stderr.strip()[-1000:] if not success else None,
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "cell": event["cell_id"],
                    "year": event["source_year_partition"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": outcome.get("source_total"),
                    "retained": outcome.get("retained_record_count"),
                    "abstracts": outcome.get("full_abstract_count"),
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
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(item["success"] for item in outcomes),
        "all_source_cells_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def plan_contract(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "review_id": plan["review_id"],
        "strategy_reference": plan["strategy_reference"],
        "phase": plan["phase"],
        "adapter": copy.deepcopy(plan["adapter"]),
    }


def choose_nonreplacement_cells(
    base_plan: Mapping[str, Any],
    base_receipt: Mapping[str, Any],
    base_root: Path,
    corrective_plan: Mapping[str, Any],
    corrective_receipt: Mapping[str, Any],
    corrective_root: Path,
) -> list[dict[str, Any]]:
    base_outcomes = {
        item.get("event_id"): item
        for item in base_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    correction_events = {
        item.get("correction_of_event_id"): item
        for item in corrective_plan.get("events", [])
        if isinstance(item, Mapping)
    }
    correction_outcomes = {
        item.get("correction_of_event_id"): item
        for item in corrective_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    selected: list[dict[str, Any]] = []
    for logical in base_plan["events"]:
        if logical["partition_id"] in REPLACED_PARTITIONS:
            continue
        base_outcome = base_outcomes.get(logical["event_id"])
        if base_outcome is None:
            raise ValueError(f"Missing base outcome {logical['event_id']}")
        if base_outcome.get("success") is True:
            actual_event = logical
            actual_plan = base_plan
            artifact = event_output(base_root, logical)
            origin = "initial_final_run"
        else:
            actual_event = correction_events.get(logical["event_id"])
            outcome = correction_outcomes.get(logical["event_id"])
            if actual_event is None or outcome is None or outcome.get("success") is not True:
                raise ValueError(f"Missing accepted correction for {logical['event_id']}")
            actual_plan = corrective_plan
            artifact = event_output(corrective_root, actual_event)
            origin = "corrective_005"
        summary = runner.artifact_summary(artifact, actual_event, actual_plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Invalid selected artifact {artifact}")
        selected.append(
            {
                "logical_event_id": logical["event_id"],
                "logical_cell_id": logical["cell_id"],
                "event": copy.deepcopy(actual_event),
                "plan_contract": plan_contract(actual_plan),
                "artifact": artifact,
                "origin": origin,
                "summary": summary,
            }
        )
    if len(selected) != 10:
        raise ValueError("The nonreplacement Springer cell selection changed")
    return selected


def replacement_cells(
    replacement_plan: Mapping[str, Any],
    replacement_receipt: Mapping[str, Any],
    replacement_root: Path,
) -> list[dict[str, Any]]:
    outcomes = {
        item.get("event_id"): item
        for item in replacement_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    selected: list[dict[str, Any]] = []
    for event in replacement_plan["events"]:
        outcome = outcomes.get(event["event_id"])
        artifact = event_output(replacement_root, event)
        if outcome is None or outcome.get("success") is not True:
            raise ValueError(f"Missing successful replacement {event['event_id']}")
        summary = runner.artifact_summary(artifact, event, replacement_plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Invalid replacement artifact {artifact}")
        selected.append(
            {
                "logical_event_id": event["replacement_of_event_id"],
                "logical_cell_id": event["cell_id"],
                "event": copy.deepcopy(event),
                "plan_contract": plan_contract(replacement_plan),
                "artifact": artifact,
                "origin": "source_year_replacement_006",
                "summary": summary,
            }
        )
    return selected


def reconcile(
    replacement_plan_path: Path,
    replacement_receipt_path: Path,
    replacement_root: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    replacement_plan = load(replacement_plan_path)
    replacement_receipt = load(replacement_receipt_path)
    errors = validate_plan(replacement_plan, verify_bindings=True)
    lineage = replacement_plan["lineage"]
    base_plan_path = REPOSITORY_ROOT / lineage["base_plan"]
    base_receipt_path = REPOSITORY_ROOT / lineage["base_receipt"]
    corrective_plan_path = REPOSITORY_ROOT / lineage["accepted_corrective_plan"]
    corrective_receipt_path = REPOSITORY_ROOT / lineage[
        "accepted_corrective_receipt"
    ]
    base_plan = load(base_plan_path)
    base_receipt = load(base_receipt_path)
    corrective_plan = load(corrective_plan_path)
    corrective_receipt = load(corrective_receipt_path)
    if (
        replacement_receipt.get("schema_version") != RUN_SCHEMA
        or replacement_receipt.get("plan_sha256") != digest(replacement_plan_path)
        or replacement_receipt.get("success") is not True
    ):
        errors.append("replacement_receipt")
    try:
        selected = choose_nonreplacement_cells(
            base_plan,
            base_receipt,
            base_plan_path.parent,
            corrective_plan,
            corrective_receipt,
            corrective_plan_path.parent,
        )
        selected.extend(
            replacement_cells(
                replacement_plan, replacement_receipt, replacement_root
            )
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"selection:{type(error).__name__}")
        selected = []
    rows = []
    for item in selected:
        summary = item["summary"]
        rows.append(
            {
                "logical_event_id": item["logical_event_id"],
                "logical_cell_id": item["logical_cell_id"],
                "source_run_id": item["event"]["event_id"],
                "parent_event_id": item["event"]["parent_event_id"],
                "partition_id": item["event"]["partition_id"],
                "cell_id": item["event"]["cell_id"],
                "query": item["event"]["query"],
                "event_contract": item["event"],
                "plan_contract": item["plan_contract"],
                "artifact": relative(item["artifact"]),
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_bytes": summary["artifact_bytes"],
                "origin": item["origin"],
                "source_total": summary["source_total"],
                "retained_record_count": summary["retained_record_count"],
                "client_date_excluded_count": summary[
                    "client_date_excluded_count"
                ],
                "full_abstract_count": summary["full_abstract_count"],
                "source_abstract_not_available_count": summary[
                    "source_abstract_not_available_count"
                ],
                "publication_type_counts": summary["publication_type_counts"],
                "missing_publication_type_count": summary[
                    "missing_publication_type_count"
                ],
                "success": True,
            }
        )
    success = bool(not errors and len(rows) == 67)
    value = {
        "schema_version": RECONCILIATION_SCHEMA,
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "event_kind": "final",
        "strategy_reference": runner.STRATEGY_REFERENCE,
        "strategy_version": replacement_plan["strategy_version"],
        "replacement_plan": relative(replacement_plan_path),
        "replacement_plan_sha256": digest(replacement_plan_path),
        "replacement_receipt": relative(replacement_receipt_path),
        "replacement_receipt_sha256": digest(replacement_receipt_path),
        "selected_source_cell_count": len(rows),
        "success": success,
        "source_cells": rows,
        "validation_errors": errors,
        "reconciled_at_utc": now(),
    }
    write_new(output_path, value)
    return 0 if success else 1


def validated_reconciled_cells(reconciliation: Mapping[str, Any]) -> list[dict[str, Any]]:
    if (
        reconciliation.get("schema_version") != RECONCILIATION_SCHEMA
        or reconciliation.get("success") is not True
    ):
        raise ValueError("The final Springer reconciliation is incomplete")
    cells = reconciliation.get("source_cells")
    if not isinstance(cells, list) or len(cells) != 67:
        raise ValueError("The final Springer reconciliation has wrong cell coverage")
    selected: list[dict[str, Any]] = []
    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError("The final Springer reconciliation has a malformed cell")
        artifact = REPOSITORY_ROOT / str(row["artifact"])
        event = row.get("event_contract")
        plan = row.get("plan_contract")
        if not isinstance(event, Mapping) or not isinstance(plan, Mapping):
            raise ValueError("A reconciled Springer cell lacks its validation contract")
        summary = runner.artifact_summary(artifact, event, plan)
        if (
            summary.get("valid") is not True
            or row.get("artifact_sha256") != summary.get("artifact_sha256")
            or row.get("artifact_bytes") != summary.get("artifact_bytes")
            or row.get("source_run_id") != event.get("event_id")
        ):
            raise ValueError(f"Reconciled Springer binding changed: {artifact}")
        selected.append(
            {
                "row": row,
                "artifact": artifact,
                "event": event,
                "plan": plan,
                "summary": summary,
                "data": load(artifact),
            }
        )
    return selected


def build_declarations(reconciliation_path: Path, output_path: Path) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    reconciliation = load(reconciliation_path)
    selected = validated_reconciled_cells(reconciliation)
    cells = []
    for item in selected:
        row = item["row"]
        event = item["event"]
        summary = item["summary"]
        cells.append(
            {
                "source_id": runner.SOURCE_ID,
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "parent_event_id": event["parent_event_id"],
                "source_run_id": event["event_id"],
                "query": event["query"],
                "requested_query": event["query"],
                "executed_query": event["query"],
                "source_native_executed_query": event["query"],
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_byte_count": summary["artifact_bytes"],
                "stable_ids": summary["record_paper_ids"],
                "status": "complete",
                "report_ready": True,
                "artifact": row["artifact"],
                "origin": row["origin"],
            }
        )
    value = {
        "schema_version": DECLARATIONS_SCHEMA,
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "reconciliation": relative(reconciliation_path),
        "reconciliation_sha256": digest(reconciliation_path),
        "expected_cells": cells,
    }
    write_new(output_path, value)
    return 0


def create_source_union(
    reconciliation_path: Path,
    declarations_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    reconciliation = load(reconciliation_path)
    declarations = load(declarations_path)
    if declarations.get("schema_version") != DECLARATIONS_SCHEMA:
        raise ValueError("Unexpected Springer declaration schema")
    selected = validated_reconciled_cells(reconciliation)
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
        raise RuntimeError("Could not create the final Springer source union")
    return 0


def build_record_union(reconciliation_path: Path, output_path: Path) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    reconciliation = load(reconciliation_path)
    selected = validated_reconciled_cells(reconciliation)
    records: dict[str, dict[str, Any]] = {}
    for item in selected:
        row = item["row"]
        for record in item["data"]["results"]:
            identifier = record["paperId"]
            entry = records.setdefault(
                identifier,
                {
                    "paperId": identifier,
                    "discovery_partitions": [],
                    "discovery_cells": [],
                    "source_run_ids": [],
                    "records": [],
                },
            )
            for key, value in (
                ("discovery_partitions", row["partition_id"]),
                ("discovery_cells", f"{row['partition_id']}:{row['cell_id']}"),
                ("source_run_ids", row["source_run_id"]),
            ):
                if value not in entry[key]:
                    entry[key].append(value)
            entry["records"].append(record)
    output_records = []
    conflicts = []
    for identifier in sorted(records):
        entry = records[identifier]
        types = {
            record.get("documentType")
            for record in entry["records"]
            if isinstance(record.get("documentType"), str)
            and record["documentType"].strip()
        }
        abstract_states = {
            (record.get("abstract", ""), record.get("abstract_not_available"))
            for record in entry["records"]
        }
        if len(types) != 1:
            conflicts.append({"paperId": identifier, "field": "documentType"})
        if len(abstract_states) != 1:
            conflicts.append({"paperId": identifier, "field": "abstract"})
        chosen = max(
            entry["records"], key=lambda record: len(str(record.get("abstract") or ""))
        )
        output_records.append(
            {
                "paperId": identifier,
                "discovery_partitions": sorted(
                    entry["discovery_partitions"], key=runner.PARTITIONS.index
                ),
                "discovery_cells": sorted(entry["discovery_cells"]),
                "source_run_ids": sorted(entry["source_run_ids"]),
                "record": chosen,
            }
        )
    full_abstracts = sum(
        bool(item["record"].get("abstract")) for item in output_records
    )
    source_absences = sum(
        item["record"].get("abstract_not_available") is True
        for item in output_records
    )
    missing_types = sum(
        not bool(item["record"].get("documentType")) for item in output_records
    )
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "purpose": (
            "deduplicated final Springer records with complete visible abstracts "
            "and raw source publication types"
        ),
        "reviewer_publication_type_coding": (
            "not inferred from Springer source metadata"
        ),
        "reconciliation": relative(reconciliation_path),
        "reconciliation_sha256": digest(reconciliation_path),
        "source_event_record_count": sum(
            len(item["data"]["results"]) for item in selected
        ),
        "unique_source_card_path_count": len(output_records),
        "records_with_full_abstract": full_abstracts,
        "records_with_source_abstract_absence": source_absences,
        "records_missing_abstract_state": (
            len(output_records) - full_abstracts - source_absences
        ),
        "records_with_source_publication_type": len(output_records) - missing_types,
        "records_missing_source_publication_type": missing_types,
        "metadata_conflicts": conflicts,
        "complete": not conflicts
        and missing_types == 0
        and full_abstracts + source_absences == len(output_records),
        "records": output_records,
    }
    write_new(output_path, value)
    return 0 if value["complete"] else 1


def assess(
    replacement_plan_path: Path,
    replacement_receipt_path: Path,
    reconciliation_path: Path,
    declarations_path: Path,
    source_union_path: Path,
    record_union_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(replacement_plan_path)
    run = load(replacement_receipt_path)
    reconciliation = load(reconciliation_path)
    declarations = load(declarations_path)
    source_union = load(source_union_path)
    record_union = load(record_union_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(replacement_plan_path)
        or run.get("success") is not True
        or run.get("accepted_source_cell_count") != len(plan["events"])
    ):
        errors.append("replacement_run")
    if (
        reconciliation.get("schema_version") != RECONCILIATION_SCHEMA
        or reconciliation.get("replacement_plan_sha256")
        != digest(replacement_plan_path)
        or reconciliation.get("replacement_receipt_sha256")
        != digest(replacement_receipt_path)
        or reconciliation.get("success") is not True
    ):
        errors.append("reconciliation")
    if (
        declarations.get("schema_version") != DECLARATIONS_SCHEMA
        or declarations.get("reconciliation_sha256") != digest(reconciliation_path)
        or len(declarations.get("expected_cells", [])) != 67
    ):
        errors.append("declarations")
    try:
        selected = validated_reconciled_cells(reconciliation)
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"cells:{type(error).__name__}")
        selected = []

    source_total_sum = sum(
        item["summary"]["source_total"] for item in selected
    )
    retained_occurrences = sum(
        item["summary"]["retained_record_count"] for item in selected
    )
    excluded_occurrences = sum(
        item["summary"]["client_date_excluded_count"] for item in selected
    )
    full_abstract_occurrences = sum(
        item["summary"]["full_abstract_count"] for item in selected
    )
    absent_abstract_occurrences = sum(
        item["summary"]["source_abstract_not_available_count"]
        for item in selected
    )
    publication_types: Counter[str] = Counter()
    ids: set[str] = set()
    for item in selected:
        publication_types.update(item["summary"]["publication_type_counts"])
        ids.update(item["summary"]["record_paper_ids"])
        if (
            item["summary"]["abstract_field_complete"] is not True
            or item["summary"]["publication_type_field_complete"] is not True
            or item["summary"]["missing_publication_type_count"] != 0
        ):
            errors.append(f"capture:{item['event']['event_id']}")

    union_source = source_union.get("source_unions", {}).get(runner.SOURCE_ID, {})
    union_valid = bool(
        source_union.get("schema_version")
        == "academic-search-source-union-receipt/v1"
        and source_union.get("review_namespace") == runner.REVIEW_NAMESPACE
        and source_union.get("review_id") == runner.REVIEW_ID
        and source_union.get("strategy_reference") == runner.STRATEGY_REFERENCE
        and source_union.get("strategy_version") == plan["strategy_version"]
        and source_union.get("expected_partitions") == list(runner.PARTITIONS)
        and source_union.get("expected_sources") == [runner.SOURCE_ID]
        and source_union.get("event_count") == 67
        and source_union.get("artifact_count") == 67
        and union_source.get("event_total_sum") == source_total_sum
        and union_source.get("completeness_status") == "complete"
        and union_source.get("failure_status") == "none"
    )
    if not union_valid:
        errors.append("source_union")
    expected_cell_counts = {
        "A1": 1,
        "A2": 5,
        "A3": 1,
        "B1": 1,
        "B2": 25,
        "BG1": 1,
        "BG2": 1,
        "BC1": 16,
        "BT2": 16,
    }
    cell_unions = union_source.get("cell_unions", {})
    for partition, count in expected_cell_counts.items():
        if cell_unions.get(partition, {}).get("cell_count") != count:
            errors.append(f"source_union_cell:{partition}")
    record_union_valid = bool(
        record_union.get("schema_version") == RECORD_UNION_SCHEMA
        and record_union.get("reconciliation_sha256") == digest(reconciliation_path)
        and record_union.get("source_event_record_count") == retained_occurrences
        and record_union.get("unique_source_card_path_count") == len(ids)
        and record_union.get("records_missing_abstract_state") == 0
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("metadata_conflicts") == []
        and record_union.get("complete") is True
    )
    if not record_union_valid:
        errors.append("record_union")
    value = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "replacement_plan": relative(replacement_plan_path),
        "replacement_plan_sha256": digest(replacement_plan_path),
        "replacement_receipt": relative(replacement_receipt_path),
        "replacement_receipt_sha256": digest(replacement_receipt_path),
        "reconciliation": relative(reconciliation_path),
        "reconciliation_sha256": digest(reconciliation_path),
        "source_cell_declarations": relative(declarations_path),
        "source_cell_declarations_sha256": digest(declarations_path),
        "source_union_receipt": relative(source_union_path),
        "source_union_receipt_sha256": digest(source_union_path),
        "record_union": relative(record_union_path),
        "record_union_sha256": digest(record_union_path),
        "adapter": plan["adapter"],
        "date_contract": plan["date_contract"],
        "source_cell_count": len(selected),
        "source_cell_counts_by_partition": expected_cell_counts,
        "source_total_occurrence_count": source_total_sum,
        "retained_record_occurrence_count": retained_occurrences,
        "client_date_excluded_occurrence_count": excluded_occurrences,
        "unique_retained_source_card_path_count": len(ids),
        "unique_retained_source_card_path_set_sha256": runner.digest_set(ids),
        "full_abstract_occurrence_count": full_abstract_occurrences,
        "source_abstract_not_available_occurrence_count": absent_abstract_occurrences,
        "publication_type_occurrence_count": sum(publication_types.values()),
        "publication_type_counts": dict(sorted(publication_types.items())),
        "full_abstract_and_publication_type_capture_complete": bool(not errors),
        "source_union_valid": union_valid,
        "record_union_valid": record_union_valid,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new(output_path, value)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-plan")
    build.add_argument("--base-plan", type=Path, required=True)
    build.add_argument("--base-receipt", type=Path, required=True)
    build.add_argument("--corrective-plan", type=Path, required=True)
    build.add_argument("--corrective-receipt", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)

    check = subparsers.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--verify-bindings", action="store_true")

    run = subparsers.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--output-root", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)
    run.add_argument("--settle-seconds", type=float, default=2.0)

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("--plan", type=Path, required=True)
    reconcile_parser.add_argument("--receipt", type=Path, required=True)
    reconcile_parser.add_argument("--output-root", type=Path, required=True)
    reconcile_parser.add_argument("--output", type=Path, required=True)

    declarations = subparsers.add_parser("build-cell-declarations")
    declarations.add_argument("--reconciliation", type=Path, required=True)
    declarations.add_argument("--output", type=Path, required=True)

    source_union = subparsers.add_parser("source-union")
    source_union.add_argument("--reconciliation", type=Path, required=True)
    source_union.add_argument("--cell-declarations", type=Path, required=True)
    source_union.add_argument("--output", type=Path, required=True)

    record_union = subparsers.add_parser("record-union")
    record_union.add_argument("--reconciliation", type=Path, required=True)
    record_union.add_argument("--output", type=Path, required=True)

    assessment = subparsers.add_parser("assess")
    assessment.add_argument("--plan", type=Path, required=True)
    assessment.add_argument("--receipt", type=Path, required=True)
    assessment.add_argument("--reconciliation", type=Path, required=True)
    assessment.add_argument("--cell-declarations", type=Path, required=True)
    assessment.add_argument("--source-union", type=Path, required=True)
    assessment.add_argument("--record-union", type=Path, required=True)
    assessment.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan(
            args.base_plan,
            args.base_receipt,
            args.corrective_plan,
            args.corrective_receipt,
        )
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid replacement plan: " + ", ".join(errors))
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
        return run_plan(
            args.plan,
            args.output_root,
            args.receipt,
            settle_seconds=args.settle_seconds,
        )
    if args.command == "reconcile":
        return reconcile(args.plan, args.receipt, args.output_root, args.output)
    if args.command == "build-cell-declarations":
        return build_declarations(args.reconciliation, args.output)
    if args.command == "source-union":
        return create_source_union(
            args.reconciliation, args.cell_declarations, args.output
        )
    if args.command == "record-union":
        return build_record_union(args.reconciliation, args.output)
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.reconciliation,
            args.cell_declarations,
            args.source_union,
            args.record_union,
            args.output,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
