#!/usr/bin/env python3
"""Run the two predeclared unchanged direct A2 count events once."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.IEEE_COMMIT.json")


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not path.is_file() or not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == sha256(path)
        and evidence.get("bytes") == path.stat().st_size
    )


def command(event: dict[str, Any], output: Path) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        event["query"],
        "--year-start",
        "2011",
        "--year-end",
        "2026",
        "--count-only",
        "--limit",
        "1000",
        "--max-pages",
        "20",
        "--page-size",
        "100",
        "--sort",
        "Oldest",
        "--timeout",
        "120",
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"ieee-p008-{event['event_id']}",
        "--prisma-review-id",
        "slr1-ieee-pilot-008",
        "--prisma-strategy-reference",
        "slr1-ieee-unchanged-a2-readiness-retest-v1",
        "--prisma-strategy-version",
        event["query_sha256"],
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        "A2",
        "--prisma-partition-label",
        "A2",
        "--prisma-partition-description",
        event["purpose"],
    ]


def run(plan_path: Path, pilot_root: Path, receipt_path: Path, delay: float) -> int:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "ieee-xplore-pilot-008-event-plan/v1"
        or not isinstance(events, list)
        or len(events) != 2
    ):
        raise RuntimeError("Unexpected IEEE Pilot 008 plan")
    if sha256(ADAPTER) != plan["adapter"]["sha256"]:
        raise RuntimeError("IEEE adapter differs from the predeclared hash")

    started = now()
    outcomes = []
    for index, event in enumerate(events):
        output = pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() or marker_path(output).exists():
            raise RuntimeError(f"Refusing to overwrite {output}")
        print(f"Running {event['event_id']}", flush=True)
        process = subprocess.run(command(event, output), check=False)
        artifact = load(output) if output.exists() else {}
        metadata = artifact.get("output_metadata", {})
        success = (
            process.returncode == 0
            and artifact.get("executed_query") == event["query"]
            and metadata.get("status") == "count_only"
            and isinstance(artifact.get("total"), int)
            and marker_valid(output)
        )
        outcomes.append(
            {
                "event_id": event["event_id"],
                "completed_at_utc": now(),
                "return_code": process.returncode,
                "output": str(output.relative_to(pilot_root)),
                "artifact_status": metadata.get("status"),
                "source_total": artifact.get("total"),
                "commit_marker_valid": marker_valid(output),
                "year_readback": metadata.get("publication_year_readback"),
                "error_stage": metadata.get("error_stage"),
                "successful_source_event": success,
            }
        )
        running = {
            "schema_version": "ieee-xplore-pilot-008-run-receipt/v1",
            "source": "IEEE Xplore",
            "pilot": "008",
            "status": "running",
            "diagnostic_only": True,
            "do_not_merge": True,
            "started_at_utc": started,
            "updated_at_utc": now(),
            "predeclared_event_count": 2,
            "completed_event_count": len(outcomes),
            "outcomes": outcomes,
        }
        receipt_path.write_text(json.dumps(running, indent=2) + "\n")
        if index + 1 < len(events) and delay > 0:
            time.sleep(delay)

    failures = sum(item["successful_source_event"] is not True for item in outcomes)
    final = load(receipt_path)
    final.update(
        {
            "status": "complete" if failures == 0 else "complete_with_retained_source_failures",
            "completed_at_utc": now(),
            "successful_source_event_count": len(outcomes) - failures,
            "failed_source_event_count": failures,
        }
    )
    receipt_path.write_text(json.dumps(final, indent=2) + "\n")
    return 0 if failures == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--delay-seconds", type=float, default=3.0)
    args = parser.parse_args()
    try:
        return run(args.event_plan, args.pilot_root, args.receipt, args.delay_seconds)
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
