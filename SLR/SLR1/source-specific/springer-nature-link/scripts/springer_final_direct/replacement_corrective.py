#!/usr/bin/env python3
"""Correct failed Springer source-year replacement cells and reconcile them."""

from __future__ import annotations

import argparse
import copy
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


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
RUNNER_PATH = SCRIPT_PATH.with_name("run.py")
REPLACEMENT_PATH = SCRIPT_PATH.with_name("replacement.py")
SEQUENCE = 7
PLAN_SCHEMA = "slr1-springer-nature-link-source-year-replacement-corrective-plan/v1"
RUN_SCHEMA = "slr1-springer-nature-link-source-year-replacement-corrective-run/v1"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("slr1_springer_replacement_correction_runner", RUNNER_PATH)
replacement = load_module(
    "slr1_springer_replacement_correction_parent", REPLACEMENT_PATH
)


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


def failed_events(
    parent_plan: Mapping[str, Any], parent_run: Mapping[str, Any]
) -> list[dict[str, Any]]:
    outcomes = {
        item.get("event_id"): item
        for item in parent_run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    rows = []
    for event in parent_plan["events"]:
        outcome = outcomes.get(event["event_id"])
        if outcome is None:
            raise ValueError(f"Missing replacement outcome {event['event_id']}")
        if outcome.get("success") is not True:
            corrected = copy.deepcopy(event)
            corrected["correction_of_event_id"] = event["event_id"]
            corrected["event_id"] = f"{event['event_id']}-corrective-{SEQUENCE:03d}"
            corrected["correction_sequence"] = SEQUENCE
            rows.append(corrected)
    return rows


def build_plan(parent_plan_path: Path, parent_run_path: Path) -> dict[str, Any]:
    parent_plan = load(parent_plan_path)
    parent_run = load(parent_run_path)
    errors = replacement.validate_plan(parent_plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid parent replacement plan: " + ", ".join(errors))
    if (
        parent_run.get("schema_version") != replacement.RUN_SCHEMA
        or parent_run.get("plan_sha256") != digest(parent_plan_path)
        or parent_run.get("success") is not False
        or parent_run.get("all_source_cells_attempted") is not True
    ):
        raise ValueError("The parent replacement receipt is not a complete failed run")
    events = failed_events(parent_plan, parent_run)
    if [event["cell_id"] for event in events] != [
        "year-2021",
        "year-2022",
        "year-2025",
    ] or any(event["partition_id"] != "BT2" for event in events):
        raise ValueError("The corrective replacement failure set changed")
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": parent_plan["source"],
        "source_id": parent_plan["source_id"],
        "review_namespace": parent_plan["review_namespace"],
        "review_id": parent_plan["review_id"],
        "event_kind": "final",
        "phase": parent_plan["phase"],
        "strategy_reference": parent_plan["strategy_reference"],
        "strategy_version": parent_plan["strategy_version"],
        "correction_sequence": SEQUENCE,
        "reason": (
            "Repeat only three unchanged BT2 source-year cells after two screenshot "
            "capture failures and one transient source challenge."
        ),
        "query_filter_or_date_change": False,
        "capture_contract": copy.deepcopy(parent_plan["capture_contract"]),
        "adapter": copy.deepcopy(parent_plan["adapter"]),
        "parent": {
            "plan": relative(parent_plan_path),
            "plan_sha256": digest(parent_plan_path),
            "run_receipt": relative(parent_run_path),
            "run_receipt_sha256": digest(parent_run_path),
        },
        "bindings": {
            "files": {
                relative(SCRIPT_PATH): digest(SCRIPT_PATH),
                relative(RUNNER_PATH): digest(RUNNER_PATH),
                relative(REPLACEMENT_PATH): digest(REPLACEMENT_PATH),
                relative(parent_plan_path): digest(parent_plan_path),
                relative(parent_run_path): digest(parent_run_path),
                str(runner.ADAPTER): digest(runner.ADAPTER),
                str(replacement.BACKEND_PATH): digest(replacement.BACKEND_PATH),
            }
        },
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    parent = plan.get("parent")
    if not isinstance(parent, Mapping):
        return ["parent"]
    parent_plan_path = REPOSITORY_ROOT / str(parent.get("plan", ""))
    parent_run_path = REPOSITORY_ROOT / str(parent.get("run_receipt", ""))
    if not regular(parent_plan_path) or not regular(parent_run_path):
        return ["parent_artifacts"]
    parent_plan = load(parent_plan_path)
    parent_run = load(parent_run_path)
    parent_errors = replacement.validate_plan(parent_plan, verify_bindings=True)
    errors.extend(f"parent:{error}" for error in parent_errors)
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("source") != parent_plan.get("source")
        or plan.get("source_id") != parent_plan.get("source_id")
        or plan.get("review_namespace") != parent_plan.get("review_namespace")
        or plan.get("review_id") != parent_plan.get("review_id")
        or plan.get("event_kind") != "final"
        or plan.get("phase") != parent_plan.get("phase")
        or plan.get("strategy_reference") != parent_plan.get("strategy_reference")
        or plan.get("strategy_version") != parent_plan.get("strategy_version")
        or plan.get("correction_sequence") != SEQUENCE
        or plan.get("query_filter_or_date_change") is not False
        or plan.get("capture_contract") != parent_plan.get("capture_contract")
        or plan.get("adapter") != parent_plan.get("adapter")
        or parent.get("plan_sha256") != digest(parent_plan_path)
        or parent.get("run_receipt_sha256") != digest(parent_run_path)
    ):
        errors.append("identity")
    try:
        expected = failed_events(parent_plan, parent_run)
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"events:{type(error).__name__}")
        expected = []
    if plan.get("events") != expected:
        errors.append("events")
    if verify_bindings:
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in files.items():
                path = Path(str(name))
                if not path.is_absolute():
                    path = REPOSITORY_ROOT / path
                if not regular(path) or digest(path) != expected_hash:
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
        raise ValueError("Invalid replacement correction plan: " + ", ".join(errors))
    output_root.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not runner.cdp_is_loopback(cdp_url):
        raise ValueError("Replacement correction requires a loopback browser endpoint")
    outcomes = []
    started_at = now()
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_root / event["output_filename"]
        output.parent.mkdir(parents=True, exist_ok=True)
        if runner.output_paths_occupied(output):
            raise FileExistsError(f"Refusing to overwrite {event['event_id']}")
        completed = subprocess.run(
            runner.command_for(event, output, plan, cdp_url),
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        summary = runner.artifact_summary(output, event, plan)
        success = completed.returncode == 0 and summary.get("valid") is True
        outcomes.append(
            {
                "event_id": event["event_id"],
                "correction_of_event_id": event["correction_of_event_id"],
                "parent_event_id": event["parent_event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "source_year_partition": event["source_year_partition"],
                "success": success,
                "artifact": relative(output) if regular(output) else None,
                "exit_code": completed.returncode,
                "attempt_count": 1,
                "stdout_sha256": runner.digest_text(completed.stdout),
                "stderr_sha256": runner.digest_text(completed.stderr),
                "safe_stderr_tail": completed.stderr.strip()[-1000:]
                if not success
                else None,
                **summary,
            }
        )
        print(
            json.dumps(
                {
                    "cell": event["cell_id"],
                    "success": success,
                    "total": summary.get("source_total"),
                    "retained": summary.get("retained_record_count"),
                    "abstracts": summary.get("full_abstract_count"),
                    "missing_types": summary.get("missing_publication_type_count"),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == len(plan["events"]) and all(
        item["success"] for item in outcomes
    )
    value = {
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
    write_new(receipt_path, value)
    return 0 if success else 1


def selected_replacement_cells(
    parent_plan: Mapping[str, Any],
    parent_run: Mapping[str, Any],
    parent_root: Path,
    correction_plan: Mapping[str, Any],
    correction_run: Mapping[str, Any],
    correction_root: Path,
) -> list[dict[str, Any]]:
    parent_outcomes = {
        item.get("event_id"): item
        for item in parent_run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    correction_events = {
        item.get("correction_of_event_id"): item
        for item in correction_plan.get("events", [])
        if isinstance(item, Mapping)
    }
    correction_outcomes = {
        item.get("correction_of_event_id"): item
        for item in correction_run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    selected = []
    for parent_event in parent_plan["events"]:
        parent_outcome = parent_outcomes.get(parent_event["event_id"])
        if parent_outcome is None:
            raise ValueError(f"Missing parent outcome {parent_event['event_id']}")
        if parent_outcome.get("success") is True:
            event = parent_event
            plan = parent_plan
            artifact = parent_root / event["output_filename"]
            origin = "source_year_replacement_006"
        else:
            event = correction_events.get(parent_event["event_id"])
            outcome = correction_outcomes.get(parent_event["event_id"])
            if event is None or outcome is None or outcome.get("success") is not True:
                raise ValueError(f"Missing correction {parent_event['event_id']}")
            plan = correction_plan
            artifact = correction_root / event["output_filename"]
            origin = "source_year_replacement_corrective_007"
        summary = runner.artifact_summary(artifact, event, plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Invalid selected replacement artifact {artifact}")
        selected.append(
            {
                "logical_event_id": parent_event["replacement_of_event_id"],
                "logical_cell_id": parent_event["cell_id"],
                "event": copy.deepcopy(event),
                "plan_contract": replacement.plan_contract(plan),
                "artifact": artifact,
                "origin": origin,
                "summary": summary,
            }
        )
    return selected


def build_reconciled_run(
    parent_plan_path: Path,
    parent_run_path: Path,
    correction_plan_path: Path,
    correction_run_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    parent_plan = load(parent_plan_path)
    parent_run = load(parent_run_path)
    correction_plan = load(correction_plan_path)
    correction_run = load(correction_run_path)
    if correction_run.get("success") is not True:
        raise ValueError("The replacement correction did not complete")
    corrected = {
        item["correction_of_event_id"]: item
        for item in correction_run["outcomes"]
    }
    outcomes = []
    for event, original in zip(parent_plan["events"], parent_run["outcomes"]):
        selected = original if original.get("success") is True else corrected.get(event["event_id"])
        if selected is None or selected.get("success") is not True:
            raise ValueError(f"Missing successful replacement outcome {event['event_id']}")
        outcomes.append(
            {
                **copy.deepcopy(selected),
                "event_id": event["event_id"],
                "selected_source_run_id": selected["event_id"],
                "correction_applied": original.get("success") is not True,
            }
        )
    value = {
        "schema_version": replacement.RUN_SCHEMA,
        "source": parent_plan["source"],
        "source_id": parent_plan["source_id"],
        "review_namespace": parent_plan["review_namespace"],
        "event_kind": "final",
        "plan": relative(parent_plan_path),
        "plan_sha256": digest(parent_plan_path),
        "adapter": parent_plan["adapter"],
        "original_run_receipt": relative(parent_run_path),
        "original_run_receipt_sha256": digest(parent_run_path),
        "corrective_plan": relative(correction_plan_path),
        "corrective_plan_sha256": digest(correction_plan_path),
        "corrective_run_receipt": relative(correction_run_path),
        "corrective_run_receipt_sha256": digest(correction_run_path),
        "planned_source_cell_count": len(outcomes),
        "attempted_source_cell_count": len(outcomes),
        "accepted_source_cell_count": len(outcomes),
        "all_source_cells_attempted": True,
        "success": True,
        "outcomes": outcomes,
        "reconciled_at_utc": now(),
    }
    write_new(output_path, value)
    return 0


def reconcile_final(
    parent_plan_path: Path,
    parent_run_path: Path,
    parent_root: Path,
    reconciled_run_path: Path,
    correction_plan_path: Path,
    correction_run_path: Path,
    correction_root: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    parent_plan = load(parent_plan_path)
    parent_run = load(parent_run_path)
    correction_plan = load(correction_plan_path)
    correction_run = load(correction_run_path)
    reconciled_run = load(reconciled_run_path)
    lineage = parent_plan["lineage"]
    base_plan_path = REPOSITORY_ROOT / lineage["base_plan"]
    base_receipt_path = REPOSITORY_ROOT / lineage["base_receipt"]
    accepted_plan_path = REPOSITORY_ROOT / lineage["accepted_corrective_plan"]
    accepted_receipt_path = REPOSITORY_ROOT / lineage[
        "accepted_corrective_receipt"
    ]
    base_plan = load(base_plan_path)
    base_receipt = load(base_receipt_path)
    accepted_plan = load(accepted_plan_path)
    accepted_receipt = load(accepted_receipt_path)
    errors = replacement.validate_plan(parent_plan, verify_bindings=True)
    errors.extend(validate_plan(correction_plan, verify_bindings=True))
    if (
        correction_run.get("schema_version") != RUN_SCHEMA
        or correction_run.get("plan_sha256") != digest(correction_plan_path)
        or correction_run.get("success") is not True
        or reconciled_run.get("schema_version") != replacement.RUN_SCHEMA
        or reconciled_run.get("plan_sha256") != digest(parent_plan_path)
        or reconciled_run.get("success") is not True
    ):
        errors.append("run_receipts")
    try:
        selected = replacement.choose_nonreplacement_cells(
            base_plan,
            base_receipt,
            base_plan_path.parent,
            accepted_plan,
            accepted_receipt,
            accepted_plan_path.parent,
        )
        selected.extend(
            selected_replacement_cells(
                parent_plan,
                parent_run,
                parent_root,
                correction_plan,
                correction_run,
                correction_root,
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
    success = not errors and len(rows) == 67
    value = {
        "schema_version": replacement.RECONCILIATION_SCHEMA,
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "event_kind": "final",
        "strategy_reference": runner.STRATEGY_REFERENCE,
        "strategy_version": parent_plan["strategy_version"],
        "replacement_plan": relative(parent_plan_path),
        "replacement_plan_sha256": digest(parent_plan_path),
        "replacement_receipt": relative(reconciled_run_path),
        "replacement_receipt_sha256": digest(reconciled_run_path),
        "replacement_corrective_plan": relative(correction_plan_path),
        "replacement_corrective_plan_sha256": digest(correction_plan_path),
        "replacement_corrective_receipt": relative(correction_run_path),
        "replacement_corrective_receipt_sha256": digest(correction_run_path),
        "selected_source_cell_count": len(rows),
        "success": success,
        "source_cells": rows,
        "validation_errors": errors,
        "reconciled_at_utc": now(),
    }
    write_new(output_path, value)
    return 0 if success else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-plan")
    build.add_argument("--parent-plan", type=Path, required=True)
    build.add_argument("--parent-receipt", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)

    check = subparsers.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--verify-bindings", action="store_true")

    run = subparsers.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--output-root", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)
    run.add_argument("--settle-seconds", type=float, default=5.0)

    reconcile_run = subparsers.add_parser("reconcile-run")
    reconcile_run.add_argument("--parent-plan", type=Path, required=True)
    reconcile_run.add_argument("--parent-receipt", type=Path, required=True)
    reconcile_run.add_argument("--corrective-plan", type=Path, required=True)
    reconcile_run.add_argument("--corrective-receipt", type=Path, required=True)
    reconcile_run.add_argument("--output", type=Path, required=True)

    reconcile_final_parser = subparsers.add_parser("reconcile-final")
    reconcile_final_parser.add_argument("--parent-plan", type=Path, required=True)
    reconcile_final_parser.add_argument("--parent-receipt", type=Path, required=True)
    reconcile_final_parser.add_argument("--parent-root", type=Path, required=True)
    reconcile_final_parser.add_argument("--reconciled-run", type=Path, required=True)
    reconcile_final_parser.add_argument("--corrective-plan", type=Path, required=True)
    reconcile_final_parser.add_argument("--corrective-receipt", type=Path, required=True)
    reconcile_final_parser.add_argument("--corrective-root", type=Path, required=True)
    reconcile_final_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan(args.parent_plan, args.parent_receipt)
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid correction plan: " + ", ".join(errors))
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
    if args.command == "reconcile-run":
        return build_reconciled_run(
            args.parent_plan,
            args.parent_receipt,
            args.corrective_plan,
            args.corrective_receipt,
            args.output,
        )
    if args.command == "reconcile-final":
        return reconcile_final(
            args.parent_plan,
            args.parent_receipt,
            args.parent_root,
            args.reconciled_run,
            args.corrective_plan,
            args.corrective_receipt,
            args.corrective_root,
            args.output,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
