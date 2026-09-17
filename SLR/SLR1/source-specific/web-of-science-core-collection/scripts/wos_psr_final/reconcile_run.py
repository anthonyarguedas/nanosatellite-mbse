#!/usr/bin/env python3
"""Reconcile final Web of Science artifacts after a local sidecar receipt check."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "slr1-wos-final-psr-run-reconciled/v1"
INITIAL_RUN_SCHEMA = "slr1-wos-final-psr-run/v1"
PLAN_SCHEMA = "slr1-wos-final-psr-plan/v1"
PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
SCRIPT_ROOT = Path(__file__).resolve().parent
RUNNER = SCRIPT_ROOT / "run_final.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wos_final_psr_reconcile_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--initial-run-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    plan = load(args.plan)
    initial = load(args.initial_run_receipt)
    runner = load_runner()
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected final WoS PSR plan schema")
    if initial.get("schema_version") != INITIAL_RUN_SCHEMA:
        raise SystemExit("Unexpected initial final WoS PSR run schema")
    if initial.get("plan_sha256") != digest(args.plan):
        raise SystemExit("Initial run receipt does not bind the plan")
    if initial.get("source_command_attempt_count") != 4:
        raise SystemExit("Initial run receipt does not show exactly four source commands")
    if initial.get("all_partitions_attempted") is not True:
        raise SystemExit("Initial run receipt did not attempt every partition")
    if initial.get("target_identifier_retained") is not False:
        raise SystemExit("Initial run receipt does not meet target privacy requirements")

    events = {event["partition_id"]: event for event in plan.get("events", [])}
    initial_outcomes = {
        outcome["partition_id"]: outcome for outcome in initial.get("outcomes", [])
    }
    if set(events) != set(PARTITIONS) or set(initial_outcomes) != set(PARTITIONS):
        raise SystemExit("Plan and initial receipt must each cover PSR1 through PSR4")

    outcomes: list[dict[str, Any]] = []
    errors: list[str] = []
    for partition in PARTITIONS:
        event = events[partition]
        prior = initial_outcomes[partition]
        artifact = args.output_dir / event["output_filename"]
        summary = runner.summarize(artifact, event, plan)
        prior_validity_failure = bool(
            prior.get("success") is False
            and prior.get("exit_code") == 0
            and prior.get("attempt_count") == 1
            and prior.get("artifact") == event["output_filename"]
            and prior.get("controls_valid") is True
            and prior.get("completion_valid") is True
            and prior.get("adapter_binding_valid") is True
            and prior.get("screenshots_valid") is True
            and prior.get("terminal_marker_valid") is True
            and prior.get("native_ris_valid") is False
        )
        if not prior_validity_failure and prior.get("success") is not True:
            errors.append(f"initial_receipt:{partition}")
        if summary.get("valid") is not True:
            errors.append(f"corrected_validation:{partition}")
        outcomes.append(
            {
                "event_id": event["event_id"],
                "partition_id": partition,
                "source_execution_replayed": False,
                "success": summary.get("valid") is True,
                "attempt_count": 1,
                "initial_outcome_success": prior.get("success"),
                "initial_native_ris_valid": prior.get("native_ris_valid"),
                "initial_local_validation_failure": prior_validity_failure,
                "artifact": artifact.name if artifact.is_file() else None,
                "native_ris_artifact": prior.get("native_ris_artifact"),
                "artifact_sha256": summary.get("artifact_sha256"),
                "artifact_bytes": summary.get("artifact_bytes"),
                "corrected_validation_success": summary.get("valid") is True,
                "total": summary.get("total"),
                "native_ris": summary.get("native_ris"),
                "screenshots": summary.get("screenshots"),
            }
        )

    success = not errors and all(
        outcome.get("corrected_validation_success") is True for outcome in outcomes
    )
    receipt = {
        "schema_version": SCHEMA,
        "source": "Web of Science Core Collection",
        "source_id": "web_of_science_core_collection",
        "review_namespace": "prior_secondary_reviews",
        "event_kind": "final",
        "plan": args.plan.name,
        "plan_sha256": digest(args.plan),
        "initial_run_receipt": args.initial_run_receipt.name,
        "initial_run_receipt_sha256": digest(args.initial_run_receipt),
        "source_execution_replayed": False,
        "reconciliation_reason": (
            "The original runner interpreted the path-free native RIS receipt "
            "field local_path_persisted as a sidecar-existence flag. The adapter "
            "defines that field as false even when a caller-side RIS file is retained."
        ),
        "adapter": plan.get("adapter"),
        "target_identifier_retained": False,
        "source_command_attempt_count": initial.get("source_command_attempt_count"),
        "accepted_event_count": sum(
            outcome.get("corrected_validation_success") is True for outcome in outcomes
        ),
        "all_partitions_attempted": True,
        "success": success,
        "outcomes": outcomes,
        "errors": errors,
        "completed_at_utc": now(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "passed" if success else "failed",
                "replayed": False,
                "accepted_event_count": receipt["accepted_event_count"],
                "errors": errors,
            }
        )
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
