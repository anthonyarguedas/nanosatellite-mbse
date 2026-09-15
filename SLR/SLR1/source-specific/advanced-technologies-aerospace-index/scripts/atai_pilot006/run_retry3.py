#!/usr/bin/env python3

"""Execute the predeclared ATAI Pilot 006 retry 3 cells."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def command(event: dict[str, Any], output: Path) -> list[str]:
    result = [
        "uv", "run", str(ADAPTER),
        "--query", event["query"],
        "--max-pages", "500",
        "--timeout", "180",
        "--page-delay-seconds", "0.25",
        "--output-path", str(output),
        "--prisma-run-id", f"atai-p006-{event['event_id']}",
        "--prisma-review-id", "slr1-atai-pilot-006",
        "--prisma-strategy-reference", "slr1-atai-field-pair-language-validation-v1",
        "--prisma-strategy-version", event["query_sha256"],
        "--prisma-phase", "identification",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", event["event_id"],
        "--prisma-partition-label", event["event_id"],
        "--prisma-partition-description", event["purpose"],
    ]
    if event.get("date_start") is not None:
        result.extend(["--date-start", event["date_start"], "--date-end", event["date_end"]])
    if event.get("language") is not None:
        result.extend(["--language", event["language"]])
    if event.get("count_only") is True:
        result.append("--count-only")
    elif event.get("require_complete") is True:
        result.append("--require-complete")
    else:
        raise RuntimeError(f"Retry event {event['event_id']} has no completion mode.")
    return result


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> None:
    plan = load(plan_path)
    events = plan.get("events")
    if plan.get("schema_version") != "atai-pilot-006-retry3-plan/v1" or not isinstance(events, list) or len(events) != 38:
        raise RuntimeError("Unexpected Pilot 006 retry 3 plan.")
    started = now()
    outcomes = []
    for event in events:
        output = pilot_root / "searches" / event["output"]
        if output.exists():
            raise RuntimeError(f"Refusing to overwrite {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        event_started = now()
        process = subprocess.run(command(event, output), check=False)
        outcome = {
            "event_id": event["event_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "return_code": process.returncode,
            "output": str(output.relative_to(pilot_root)),
            "output_exists": output.exists(),
        }
        if output.exists():
            artifact = load(output)
            outcome.update({
                "artifact_status": artifact.get("output_metadata", {}).get("status"),
                "source_total": artifact.get("total"),
                "records": len(artifact.get("results", [])),
            })
        outcomes.append(outcome)
        receipt = {
            "schema_version": "atai-pilot-006-retry3-run-receipt/v1",
            "source": plan["source"],
            "pilot": "006",
            "attempt": "retry3",
            "status": "running" if process.returncode == 0 else "stopped_on_source_or_adapter_failure",
            "do_not_merge": True,
            "started_at_utc": started,
            "updated_at_utc": now(),
            "event_plan": str(plan_path),
            "predeclared_event_count": len(events),
            "completed_event_count": len(outcomes),
            "outcomes": outcomes,
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
        if process.returncode != 0:
            raise RuntimeError(f"Pilot 006 retry stopped at {event['event_id']}.")
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
