#!/usr/bin/env python3
"""Execute the predeclared arXiv browser Pilot 004 cells."""

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

ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_arxiv.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
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


def artifact_is_complete(event: dict[str, Any], artifact: dict[str, Any], output: Path) -> bool:
    metadata = artifact.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {})
    screenshot_receipt = metadata.get("screenshots", {})
    if (
        artifact.get("source") != "arXiv"
        or artifact.get("executed_query") != event["serialized_query"]
        or not isinstance(artifact.get("total"), int)
        or artifact.get("total") < 0
        or len(artifact.get("results", [])) != artifact.get("total")
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or prisma.get("report_ready") is not True
        or prisma.get("adapter", {}).get("adapter_version") != "8"
        or screenshot_receipt.get("schema_version") != "arxiv-automatic-screenshots/v1"
        or screenshot_receipt.get("automatic") is not True
        or screenshot_receipt.get("same_directory_as_json") is not True
    ):
        return False
    for key, path in screenshot_paths(output).items():
        evidence = screenshot_receipt.get(key, {})
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


def command(event: dict[str, Any], output: Path, plan: dict[str, Any]) -> list[str]:
    result = ["uv", "run", str(ADAPTER)]
    for row in event["rows"]:
        result.extend(
            ["--row", row["operator"], row["field"], row["term"]]
        )
    result.extend(
        [
            "--date-start",
            plan["date_window"]["start"],
            "--date-end",
            plan["date_window"]["end"],
            "--date-type",
            "submitted_date_first",
            "--abstracts",
            "show",
            "--exclude-older-versions",
            "--sort",
            "submitted_date",
            "--limit",
            str(plan["controls"]["limit"]),
            "--max-pages",
            str(plan["controls"]["max_pages"]),
            "--timeout",
            "180",
            "--page-delay-seconds",
            str(plan["controls"]["strict_pass_delay_seconds"]),
            "--require-complete",
            "--output-path",
            str(output),
            "--prisma-run-id",
            f"arxiv-p004-{event['event_id']}",
            "--prisma-review-id",
            "slr1-arxiv-pilot-004",
            "--prisma-strategy-reference",
            "slr1-direct-query-schedule-browser-v1",
            "--prisma-strategy-version",
            event["query_sha256"],
            "--prisma-phase",
            "identification",
            "--prisma-coverage-scope",
            "partition",
            "--prisma-partition-id",
            event["partition_id"],
            "--prisma-partition-label",
            event["partition_id"],
            "--prisma-partition-description",
            f"Pilot 004 browser cell {event['cell_number']} of {event['cell_count']}",
        ]
    )
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
        "schema_version": "arxiv-browser-pilot004-run-receipt/v1",
        "source": "arXiv",
        "interface": "rendered Advanced Search web interface",
        "pilot": "004",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def run(plan_path: Path, pilot_root: Path, receipt_path: Path, resume: bool) -> None:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "arxiv-browser-pilot004-event-plan/v1"
        or not isinstance(events, list)
        or len(events) != 12
    ):
        raise RuntimeError("Unexpected arXiv Pilot 004 plan")
    if not ADAPTER.is_file():
        raise RuntimeError(f"Missing adapter: {ADAPTER}")

    started = now()
    outcomes: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        output = pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        event_started = now()
        if output.exists():
            if not resume:
                raise RuntimeError(f"Refusing to overwrite {output}")
            artifact = load(output)
            if not artifact_is_complete(event, artifact, output):
                raise RuntimeError(f"Existing event is incomplete or mismatched: {output}")
            reused = True
            return_code = 0
        else:
            process = subprocess.run(command(event, output, plan), check=False)
            return_code = process.returncode
            reused = False
            artifact = load(output) if output.exists() else {}

        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "return_code": return_code,
            "output": str(output.relative_to(pilot_root)),
            "output_exists": output.exists(),
            "source_total": artifact.get("total"),
            "records": len(artifact.get("results", [])),
            "screenshots_complete": (
                artifact_is_complete(event, artifact, output) if artifact else False
            ),
            "reused_existing": reused,
        }
        outcomes.append(outcome)
        failed = return_code != 0 or not outcome["screenshots_complete"]
        write_receipt(
            receipt_path,
            plan_path,
            started,
            outcomes,
            len(events),
            "stopped_on_source_or_adapter_failure" if failed else "running",
        )
        if failed:
            raise RuntimeError(f"Pilot 004 stopped at {event['event_id']}")
        if index + 1 < len(events):
            time.sleep(plan["controls"]["inter_event_delay_seconds"])

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
    except Exception as error:  # noqa: BLE001 - CLI boundary reports the failed event.
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
