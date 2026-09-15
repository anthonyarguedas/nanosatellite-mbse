#!/usr/bin/env python3

"""Execute the predeclared ATAI Pilot 006 source cells."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ADAPTER = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def validate_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != "atai-pilot-006-event-plan/v1":
        raise RuntimeError("Unexpected Pilot 006 event-plan schema.")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 13:
        raise RuntimeError("Pilot 006 requires 13 predeclared events.")
    ids = [event.get("event_id") for event in events]
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise RuntimeError("Pilot 006 event IDs are missing or duplicated.")
    for event in events:
        if event.get("require_complete") is not True or event.get("do_not_merge") is not True:
            raise RuntimeError(f"Event {event.get('event_id')} is not strict and non-mergeable.")
        if not isinstance(event.get("query"), str) or not event["query"]:
            raise RuntimeError(f"Event {event.get('event_id')} has no query.")


def command_for(event: dict[str, Any], output_path: Path) -> list[str]:
    command = [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        event["query"],
        "--date-start",
        event["date_start"],
        "--date-end",
        event["date_end"],
        "--require-complete",
        "--max-pages",
        "500",
        "--timeout",
        "120",
        "--page-delay-seconds",
        "0.25",
        "--output-path",
        str(output_path),
        "--prisma-run-id",
        f"atai-p006-{event['event_id']}",
        "--prisma-review-id",
        "slr1-atai-pilot-006",
        "--prisma-strategy-reference",
        "slr1-atai-field-pair-language-validation-v1",
        "--prisma-strategy-version",
        event["query_sha256"],
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["event_id"],
        "--prisma-partition-label",
        event["event_id"],
        "--prisma-partition-description",
        event["purpose"],
    ]
    if event.get("language") is not None:
        command.extend(["--language", event["language"]])
    return command


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> None:
    plan = load(plan_path)
    validate_plan(plan)
    if not ADAPTER.exists():
        raise RuntimeError(f"ATAI adapter is missing: {ADAPTER}")
    started = now()
    outcomes: list[dict[str, Any]] = []
    for event in plan["events"]:
        output_path = pilot_root / "searches" / event["output"]
        if output_path.exists():
            raise RuntimeError(f"Refusing to overwrite existing source artifact {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        event_started = now()
        completed = subprocess.run(command_for(event, output_path), check=False)
        outcome = {
            "event_id": event["event_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "return_code": completed.returncode,
            "output": str(output_path.relative_to(pilot_root)),
            "output_exists": output_path.exists(),
        }
        if output_path.exists():
            artifact = load(output_path)
            outcome.update(
                {
                    "artifact_status": artifact.get("output_metadata", {}).get("status"),
                    "source_total": artifact.get("total"),
                    "records": len(artifact.get("results", [])),
                    "do_not_merge": artifact.get("do_not_merge"),
                }
            )
        outcomes.append(outcome)
        receipt = {
            "schema_version": "atai-pilot-006-run-receipt/v1",
            "source": plan["source"],
            "pilot": "006",
            "status": "running" if completed.returncode == 0 else "stopped_on_source_or_adapter_failure",
            "do_not_merge": True,
            "started_at_utc": started,
            "updated_at_utc": now(),
            "event_plan": str(plan_path),
            "predeclared_event_count": len(plan["events"]),
            "completed_event_count": len(outcomes),
            "outcomes": outcomes,
        }
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
        if completed.returncode != 0:
            raise RuntimeError(
                f"ATAI Pilot 006 stopped at {event['event_id']} with return code {completed.returncode}."
            )
    receipt["status"] = "complete"
    receipt["completed_at_utc"] = now()
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        run(args.event_plan, args.pilot_root, args.receipt)
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
