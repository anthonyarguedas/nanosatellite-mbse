#!/usr/bin/env python3
"""Execute the predeclared IEEE Xplore Pilot 006 investigation once."""

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


def requested_query(artifact: dict[str, Any]) -> str:
    metadata = artifact.get("output_metadata", {})
    return (
        artifact.get("requested_query")
        or metadata.get("requested_query")
        or artifact.get("query")
        or artifact.get("executed_query")
        or ""
    )


def artifact_matches_event(event: dict[str, Any], artifact: dict[str, Any]) -> bool:
    metadata = artifact.get("output_metadata", {})
    status = artifact_status(artifact)
    if requested_query(artifact) != event["query"]:
        return False
    if status == "error":
        return artifact.get("total") is None
    if artifact.get("executed_query") != event["query"]:
        return False
    year = metadata.get("publication_year_readback", {})
    if year.get("requested_search_window") != "2011_2026_Year":
        return False
    if event["mode"] == "count":
        return status == "count_only" and isinstance(artifact.get("total"), int)
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
        "--skip-full-abstracts",
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"ieee-p006-{event['event_id']}",
        "--prisma-review-id",
        "slr1-ieee-pilot-006",
        "--prisma-strategy-reference",
        "slr1-ieee-year-rendered-failure-investigation-v1",
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
        raise RuntimeError(f"Unsupported mode {event['mode']}")
    return result


def outcome(event: dict[str, Any], output: Path, pilot_root: Path, return_code: int) -> dict:
    artifact = load(output) if output.exists() else {}
    status = artifact_status(artifact)
    successful_status = status in {"count_only", "success"}
    marker_valid = marker_is_valid(output)
    retained = (
        output.is_file()
        and artifact_matches_event(event, artifact)
        and (marker_valid if successful_status else status == "error")
    )
    metadata = artifact.get("output_metadata", {})
    receipt = metadata.get("ieee_observation_receipt", {})
    return {
        "event_id": event["event_id"],
        "schedule_id": event["schedule_id"],
        "mode": event["mode"],
        "return_code": return_code,
        "output": str(output.relative_to(pilot_root)),
        "artifact_status": status,
        "source_total": artifact.get("total"),
        "record_count": len(artifact.get("results", [])),
        "commit_marker_valid": marker_valid,
        "artifact_retained": retained,
        "successful_source_event": return_code == 0 and retained and successful_status,
        "year_readback_state": metadata.get("publication_year_readback", {}).get("state"),
        "year_result_refinement_range": metadata.get("publication_year_readback", {}).get(
            "result_refinement_range"
        ),
        "year_control_state": receipt.get("year_control", {}).get("state"),
        "year_apply_transition_count": receipt.get("year_control", {}).get(
            "apply_transition_count", 0
        ),
        "strict_passes_completed": metadata.get(
            "strict_complete_pass_count",
            receipt.get("strict_completion", {}).get("passes_completed", 0),
        ),
        "error_stage": metadata.get("error_stage"),
    }


def write_receipt(
    path: Path,
    plan_path: Path,
    started: str,
    outcomes: list[dict[str, Any]],
    event_count: int,
    status: str,
) -> None:
    failures = sum(item["successful_source_event"] is not True for item in outcomes)
    value = {
        "schema_version": "ieee-xplore-pilot-006-run-receipt/v1",
        "source": "IEEE Xplore",
        "pilot": "006",
        "status": status,
        "diagnostic_only": True,
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


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    delay_seconds: float,
) -> int:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "ieee-xplore-pilot-006-event-plan/v1"
        or not isinstance(events, list)
        or len(events) != 10
    ):
        raise RuntimeError("Unexpected IEEE Pilot 006 plan")
    if not ADAPTER.is_file():
        raise RuntimeError(f"Adapter is unavailable: {ADAPTER}")

    started = now()
    outcomes: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        output = pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() or marker_path(output).exists():
            raise RuntimeError(f"Refusing to overwrite {output}")
        print(f"Running {event['event_id']}", flush=True)
        process = subprocess.run(command(event, output), check=False)
        item = outcome(event, output, pilot_root, process.returncode)
        item["completed_at_utc"] = now()
        outcomes.append(item)
        write_receipt(receipt_path, plan_path, started, outcomes, len(events), "running")
        if index + 1 < len(events) and delay_seconds > 0:
            time.sleep(delay_seconds)

    failures = sum(item["successful_source_event"] is not True for item in outcomes)
    status = "complete" if failures == 0 else "complete_with_retained_source_failures"
    write_receipt(receipt_path, plan_path, started, outcomes, len(events), status)
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
