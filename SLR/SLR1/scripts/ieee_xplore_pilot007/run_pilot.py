#!/usr/bin/env python3
"""Execute the predeclared IEEE Xplore Pilot 007 strict events once."""

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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.IEEE_COMMIT.json")


def marker_valid(output: Path) -> bool:
    marker = marker_path(output)
    if not output.is_file() or not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == sha256(output)
        and evidence.get("bytes") == output.stat().st_size
    )


def strict_receipt(artifact: dict[str, Any]) -> dict[str, Any]:
    value = artifact.get("output_metadata", {}).get(
        "ieee_strict_completion_receipt", {}
    )
    return value if isinstance(value, dict) else {}


def artifact_complete(event: dict[str, Any], artifact: dict[str, Any]) -> bool:
    metadata = artifact.get("output_metadata", {})
    receipt = strict_receipt(artifact)
    total = artifact.get("total")
    return (
        artifact.get("executed_query") == event["query"]
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and isinstance(total, int)
        and len(artifact.get("results", [])) == total
        and receipt.get("schema_version")
        == "ieee-xplore-strict-two-pass-receipt/v1"
        and receipt.get("status") == "success"
        and receipt.get("passes_completed") == 2
        and receipt.get("source_reported_total") == total
        and len(receipt.get("pass_reports", [])) == 2
        and all(report.get("complete") is True for report in receipt["pass_reports"])
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
        "--require-complete",
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"ieee-p007-{event['event_id']}",
        "--prisma-review-id",
        "slr1-ieee-pilot-007",
        "--prisma-strategy-reference",
        "slr1-ieee-native-pagination-investigation-v1",
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


def run(plan_path: Path, pilot_root: Path, receipt_path: Path, delay: float) -> int:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "ieee-xplore-pilot-007-event-plan/v1"
        or not isinstance(events, list)
        or len(events) != 3
    ):
        raise RuntimeError("Unexpected IEEE Pilot 007 plan")
    if sha256(ADAPTER) != plan["adapter"]["sha256"]:
        raise RuntimeError("IEEE adapter differs from the predeclared Pilot 007 hash")

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
        compact = strict_receipt(artifact)
        reports = compact.get("pass_reports", [])
        complete = (
            process.returncode == 0
            and marker_valid(output)
            and artifact_complete(event, artifact)
        )
        outcomes.append(
            {
                "event_id": event["event_id"],
                "schedule_id": event["schedule_id"],
                "completed_at_utc": now(),
                "return_code": process.returncode,
                "output": str(output.relative_to(pilot_root)),
                "artifact_status": artifact.get("output_metadata", {}).get("status"),
                "source_total": artifact.get("total"),
                "record_count": len(artifact.get("results", [])),
                "commit_marker_valid": marker_valid(output),
                "strict_receipt_present": bool(compact),
                "strict_pass_page_sizes": [report.get("page_size") for report in reports],
                "strict_pass_page_counts": [report.get("pages_retrieved") for report in reports],
                "strict_pass_year_readbacks": [
                    report.get("year_range_readback") for report in reports
                ],
                "strict_pass_control_hashes": [
                    report.get("control_signature_sha256") for report in reports
                ],
                "successful_source_event": complete,
                "error_stage": artifact.get("output_metadata", {}).get("error_stage"),
            }
        )
        running = {
            "schema_version": "ieee-xplore-pilot-007-run-receipt/v1",
            "source": "IEEE Xplore",
            "pilot": "007",
            "status": "running",
            "diagnostic_only": True,
            "do_not_merge": True,
            "started_at_utc": started,
            "updated_at_utc": now(),
            "predeclared_event_count": len(events),
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
