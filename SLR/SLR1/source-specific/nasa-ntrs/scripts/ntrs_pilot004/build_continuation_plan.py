#!/usr/bin/env python3
"""Build the predeclared continuation after Pilot 004's null A1 failure."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

SCHEMA = "ntrs-post-proximity-wildcard-continuation-plan/v1"
INITIAL_PLAN_SCHEMA = "ntrs-post-proximity-wildcard-pilot-plan/v1"
INITIAL_RUN_SCHEMA = "ntrs-post-proximity-wildcard-pilot-run/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ntrs.py"
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot004/queries.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot004/build_continuation_plan.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot004/run_pilot.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot004/run_continuation.py"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def build(initial_plan_path: Path, initial_run_path: Path) -> dict[str, Any]:
    initial_plan = load(initial_plan_path)
    initial_run = load(initial_run_path)
    if initial_plan.get("schema_version") != INITIAL_PLAN_SCHEMA:
        raise RuntimeError("Unexpected initial plan schema")
    if initial_run.get("schema_version") != INITIAL_RUN_SCHEMA:
        raise RuntimeError("Unexpected initial run schema")
    if initial_run.get("plan_sha256") != digest(initial_plan_path):
        raise RuntimeError("Initial run is not bound to the initial plan")
    outcomes = initial_run.get("outcomes", [])
    if (
        initial_run.get("success") is not False
        or initial_run.get("stopped_after_failure") is not True
        or len(outcomes) != 1
        or outcomes[0].get("event_id") != "A1-literal"
        or outcomes[0].get("total") is not None
    ):
        raise RuntimeError("Continuation requires the retained null A1 failure")
    adapter = initial_plan.get("adapter", {})
    if digest(ADAPTER) != adapter.get("sha256"):
        raise RuntimeError("The NTRS adapter changed after the initial plan")

    events = []
    for item in initial_plan.get("events", []):
        event = dict(item)
        event["maximum_attempts"] = 3
        event["attempt_outputs"] = [
            f"continuation/{event['variant']}/{event['partition_id']}.attempt-{attempt:02d}.json"
            for attempt in range(1, 4)
        ]
        event.pop("output", None)
        events.append(event)
    return {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "NASA Technical Reports Server (NTRS)",
        "created_at_utc": now(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "reason": (
            "The initial predeclared run stopped at a null A1 result-reconciliation "
            "failure after writing both screenshots. This continuation keeps the exact "
            "queries, controls, adapter, event order, and acceptance criteria."
        ),
        "initial_plan": {
            "path": str(initial_plan_path),
            "sha256": digest(initial_plan_path),
        },
        "initial_run": {
            "path": str(initial_run_path),
            "sha256": digest(initial_run_path),
        },
        "adapter": dict(adapter),
        "controls": dict(initial_plan.get("controls", {})),
        "wildcard_candidate": dict(initial_plan.get("wildcard_candidate", {})),
        "acceptance_checks": list(initial_plan.get("acceptance_checks", [])),
        "retry_policy": {
            "maximum_attempts_per_event": 3,
            "same_query_and_controls": True,
            "retry_only_null_nonmergeable_failure": True,
            "retain_every_attempt": True,
            "stop_after_first_event_without_a_valid_success": True,
            "no_narrowing_or_set_inference": True,
        },
        "source_affecting_scripts": {
            str(path): digest(REPOSITORY_ROOT / path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = plan.get("events", [])
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if not isinstance(events, list) or len(events) != 18:
        return [*errors, "event_count"]
    expected = [
        f"{partition}-{variant}"
        for partition in queries.SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    ]
    if [item.get("event_id") for item in events] != expected:
        errors.append("event_order")
    for event in events:
        variant = event.get("variant")
        partition = event.get("partition_id")
        canonical = (
            queries.LITERAL_SCHEDULE if variant == "literal" else queries.WILDCARD_SCHEDULE
        ).get(partition)
        if event.get("query") != canonical:
            errors.append(f"query:{event.get('event_id')}")
        outputs = event.get("attempt_outputs")
        if not isinstance(outputs, list) or len(outputs) != 3 or len(set(outputs)) != 3:
            errors.append(f"attempt_outputs:{event.get('event_id')}")
        if event.get("maximum_attempts") != 3:
            errors.append(f"attempt_count:{event.get('event_id')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-plan", type=Path, required=True)
    parser.add_argument("--initial-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        plan = load(args.output)
        errors = validate(plan)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 1 if errors else 0
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    plan = build(args.initial_plan, args.initial_run)
    errors = validate(plan)
    if errors:
        raise RuntimeError("Invalid continuation plan: " + ", ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
