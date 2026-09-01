#!/usr/bin/env python3
"""Execute the predeclared IEEE Xplore Pilot 005 events without retries."""

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
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.IEEE_COMMIT.json")


def marker_is_valid(output: Path) -> bool:
    marker = marker_path(output)
    if not output.is_file() or not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == file_sha256(output)
        and evidence.get("bytes") == output.stat().st_size
    )


def artifact_status(artifact: dict[str, Any]) -> str | None:
    return artifact.get("output_metadata", {}).get("status")


def artifact_matches_event(event: dict[str, Any], artifact: dict[str, Any]) -> bool:
    metadata = artifact.get("output_metadata", {})
    requested = metadata.get("requested_query", artifact.get("query"))
    if requested != event["query"]:
        return False
    status = artifact_status(artifact)
    if status == "error":
        return artifact.get("total") is None
    if event["mode"] == "count":
        return (
            status == "count_only"
            and isinstance(artifact.get("total"), int)
            and metadata.get("observed_exact_query_echo") is True
        )
    return (
        status == "success"
        and metadata.get("require_complete") is True
        and metadata.get("strict_complete_pass_count") == 2
        and metadata.get("strict_total_reconciled") is True
        and metadata.get("strict_controls_reconciled") is True
        and metadata.get("strict_ordered_document_ids_reconciled") is True
        and metadata.get("retrieval_complete") is True
        and isinstance(artifact.get("total"), int)
    )


def command(event: dict[str, Any], output: Path) -> list[str]:
    result = [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        event["query"],
        "--year-start",
        str(event["year_start"]),
        "--year-end",
        str(event["year_end"]),
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
        "--page-delay-seconds",
        "1",
        "--detail-delay-seconds",
        "0.25",
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"ieee-p005-{event['event_id']}",
        "--prisma-review-id",
        "slr1-ieee-pilot-005",
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
    failures = sum(outcome.get("successful_source_event") is not True for outcome in outcomes)
    value: dict[str, Any] = {
        "schema_version": "ieee-xplore-pilot-005-run-receipt/v1",
        "source": "IEEE Xplore",
        "pilot": "005",
        "status": status,
        "do_not_merge": True,
        "started_at_utc": started,
        "updated_at_utc": now(),
        "event_plan": str(plan_path),
        "predeclared_event_count": event_count,
        "completed_event_count": len(outcomes),
        "successful_source_event_count": len(outcomes) - failures,
        "failed_source_event_count": failures,
        "outcomes": outcomes,
    }
    if status.startswith("complete"):
        value["completed_at_utc"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def outcome_for(
    event: dict[str, Any],
    output: Path,
    pilot_root: Path,
    started: str,
    return_code: int,
    reused: bool,
) -> dict[str, Any]:
    artifact = load(output) if output.exists() else {}
    status = artifact_status(artifact)
    total = artifact.get("total")
    success = (
        return_code == 0
        and marker_is_valid(output)
        and artifact_matches_event(event, artifact)
        and status in {"count_only", "success"}
    )
    return {
        "event_id": event["event_id"],
        "schedule_id": event["schedule_id"],
        "mode": event["mode"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "return_code": return_code,
        "output": str(output.relative_to(pilot_root)),
        "output_exists": output.exists(),
        "commit_marker": str(marker_path(output).relative_to(pilot_root)),
        "commit_marker_valid": marker_is_valid(output),
        "artifact_status": status,
        "source_total": total,
        "records": len(artifact.get("results", [])),
        "successful_source_event": success,
        "reused_existing": reused,
    }


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    resume: bool,
    delay_seconds: float,
) -> int:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "ieee-xplore-pilot-005-event-plan/v1"
        or not isinstance(events, list)
        or len(events) != 22
    ):
        raise RuntimeError("Unexpected IEEE Xplore Pilot 005 plan.")
    if not ADAPTER.is_file():
        raise RuntimeError(f"IEEE adapter is unavailable: {ADAPTER}")

    started = now()
    outcomes: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        output = pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        event_started = now()

        if output.exists() or marker_path(output).exists():
            if not resume:
                raise RuntimeError(f"Refusing to overwrite {output}")
            if not output.exists() or not marker_is_valid(output):
                raise RuntimeError(f"Existing event lacks a valid commit pair: {output}")
            artifact = load(output)
            if not artifact_matches_event(event, artifact):
                raise RuntimeError(f"Existing event is mismatched: {output}")
            outcome = outcome_for(event, output, pilot_root, event_started, 0, True)
        else:
            print(f"Running {event['event_id']}", flush=True)
            process = subprocess.run(command(event, output), check=False)
            outcome = outcome_for(
                event, output, pilot_root, event_started, process.returncode, False
            )

        outcomes.append(outcome)
        write_receipt(receipt_path, plan_path, started, outcomes, len(events), "running")
        if index + 1 < len(events) and delay_seconds > 0:
            time.sleep(delay_seconds)

    failures = sum(outcome["successful_source_event"] is not True for outcome in outcomes)
    status = "complete" if failures == 0 else "complete_with_retained_source_failures"
    write_receipt(receipt_path, plan_path, started, outcomes, len(events), status)
    return 0 if failures == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--delay-seconds", type=float, default=3.0)
    args = parser.parse_args()
    try:
        return run(
            args.event_plan,
            args.pilot_root,
            args.receipt,
            args.resume,
            args.delay_seconds,
        )
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
