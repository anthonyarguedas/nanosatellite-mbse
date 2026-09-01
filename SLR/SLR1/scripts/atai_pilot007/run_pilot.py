#!/usr/bin/env python3
"""Execute the predeclared ATAI Pilot 007 events."""

from __future__ import annotations

import argparse
import hashlib
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def screenshot_paths(output: Path) -> dict[str, Path]:
    stem = output.name[:-5] if output.name.lower().endswith(".json") else output.name
    return {
        "search_page": output.with_name(f"{stem}.search-page.png"),
        "results_page": output.with_name(f"{stem}.results-page.png"),
    }


def screenshots_are_complete(artifact: dict[str, Any], output: Path) -> bool:
    receipt = artifact.get("output_metadata", {}).get("screenshots", {})
    if (
        receipt.get("schema_version") != "atai-automatic-screenshots/v1"
        or receipt.get("automatic") is not True
    ):
        return False
    for key, path in screenshot_paths(output).items():
        evidence = receipt.get(key, {})
        if (
            not path.is_file()
            or evidence.get("path") != path.name
            or evidence.get("sha256") != file_sha256(path)
            or not isinstance(evidence.get("width"), int)
            or evidence["width"] <= 0
            or not isinstance(evidence.get("height"), int)
            or evidence["height"] <= 0
        ):
            return False
    return True


def artifact_is_complete(
    event: dict[str, Any], artifact: dict[str, Any], output: Path
) -> bool:
    metadata = artifact.get("output_metadata", {})
    if (
        artifact.get("requested_query") != event["query"]
        or not screenshots_are_complete(artifact, output)
    ):
        return False
    if event["mode"] == "count":
        return metadata.get("status") == "count_only" and isinstance(artifact.get("total"), int)
    return (
        metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and isinstance(artifact.get("total"), int)
        and len(artifact.get("results", [])) == artifact.get("total")
    )


def command(event: dict[str, Any], output: Path) -> list[str]:
    result = [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        event["query"],
        "--date-start",
        event["date_start"],
        "--date-end",
        event["date_end"],
        "--language",
        event["language"],
        "--max-pages",
        "500",
        "--timeout",
        "180",
        "--page-delay-seconds",
        "0.25",
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"atai-p007-{event['event_id']}",
        "--prisma-review-id",
        "slr1-atai-pilot-007",
        "--prisma-strategy-reference",
        "slr1-direct-query-schedule-post-proximity-v1",
        "--prisma-strategy-version",
        event["query_sha256"],
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["schedule_id"],
        "--prisma-partition-label",
        event["schedule_id"],
        "--prisma-partition-description",
        event["purpose"],
    ]
    if event["mode"] == "count":
        result.append("--count-only")
    elif event["mode"] == "complete":
        result.append("--require-complete")
    else:
        raise RuntimeError(f"Unsupported event mode: {event['mode']}")
    return result


def write_receipt(
    path: Path,
    plan_path: Path,
    started: str,
    outcomes: list[dict[str, Any]],
    event_count: int,
    status: str,
) -> None:
    value: dict[str, Any] = {
        "schema_version": "atai-pilot-007-run-receipt/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "007",
        "status": status,
        "do_not_merge": True,
        "started_at_utc": started,
        "updated_at_utc": now(),
        "event_plan": str(plan_path),
        "predeclared_event_count": event_count,
        "completed_event_count": len(outcomes),
        "outcomes": outcomes,
    }
    if status == "complete":
        value["completed_at_utc"] = now()
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def run(plan_path: Path, pilot_root: Path, receipt_path: Path, resume: bool) -> None:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "atai-pilot-007-event-plan/v1"
        or not isinstance(events, list)
        or len(events) != 22
    ):
        raise RuntimeError("Unexpected ATAI Pilot 007 plan.")

    started = now()
    outcomes: list[dict[str, Any]] = []
    for event in events:
        output = pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        event_started = now()

        if output.exists():
            if not resume:
                raise RuntimeError(f"Refusing to overwrite {output}")
            artifact = load(output)
            if not artifact_is_complete(event, artifact, output):
                raise RuntimeError(f"Existing event is incomplete or mismatched: {output}")
            outcomes.append(
                {
                    "event_id": event["event_id"],
                    "started_at_utc": event_started,
                    "completed_at_utc": now(),
                    "return_code": 0,
                    "output": str(output.relative_to(pilot_root)),
                    "output_exists": True,
                    "artifact_status": artifact.get("output_metadata", {}).get("status"),
                    "source_total": artifact.get("total"),
                    "records": len(artifact.get("results", [])),
                    "reused_existing": True,
                }
            )
            write_receipt(receipt_path, plan_path, started, outcomes, len(events), "running")
            continue

        process = subprocess.run(command(event, output), check=False)
        outcome: dict[str, Any] = {
            "event_id": event["event_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "return_code": process.returncode,
            "output": str(output.relative_to(pilot_root)),
            "output_exists": output.exists(),
            "reused_existing": False,
        }
        if output.exists():
            artifact = load(output)
            outcome.update(
                {
                    "artifact_status": artifact.get("output_metadata", {}).get("status"),
                    "source_total": artifact.get("total"),
                    "records": len(artifact.get("results", [])),
                }
            )
        outcomes.append(outcome)
        failed = process.returncode != 0
        write_receipt(
            receipt_path,
            plan_path,
            started,
            outcomes,
            len(events),
            "stopped_on_source_or_adapter_failure" if failed else "running",
        )
        if failed:
            raise RuntimeError(f"Pilot 007 stopped at {event['event_id']}.")

    write_receipt(receipt_path, plan_path, started, outcomes, len(events), "complete")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    try:
        run(args.event_plan, args.pilot_root, args.receipt, args.resume)
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
