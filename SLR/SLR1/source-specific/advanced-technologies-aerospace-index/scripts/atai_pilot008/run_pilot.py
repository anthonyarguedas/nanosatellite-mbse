#!/usr/bin/env python3
"""Execute the predeclared ATAI Pilot 008 strict comparison events."""

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
SCHEMA = "atai-pilot-008-event-plan/v1"
RECEIPT_SCHEMA = "atai-pilot-008-run-receipt/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
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
        or receipt.get("same_directory_as_json") is not True
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


def artifact_is_complete(event: dict[str, Any], artifact: dict[str, Any], output: Path) -> bool:
    metadata = artifact.get("output_metadata", {})
    results = artifact.get("results")
    run = metadata.get("prisma_search_run", {})
    adapter = run.get("adapter", {})
    try:
        adapter_version = int(adapter.get("adapter_version", "0"))
    except (TypeError, ValueError):
        adapter_version = 0
    return (
        artifact.get("schema_version") == "academic-search-result/v1"
        and artifact.get("requested_query") == event["query"]
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and isinstance(artifact.get("total"), int)
        and isinstance(results, list)
        and len(results) == artifact.get("total")
        and adapter.get("adapter_id") == "search_proquest_aerospace"
        and adapter_version >= 6
        and screenshots_are_complete(artifact, output)
    )


def command(event: dict[str, Any], output: Path, fresh_browser: bool) -> list[str]:
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
        "--require-complete",
        "--prisma-run-id",
        f"atai-p008-{event['event_id']}",
        "--prisma-review-id",
        "slr1-atai-pilot-008",
        "--prisma-strategy-reference",
        "slr1-atai-post-proximity-bounded-wildcard-comparison-v1",
        "--prisma-strategy-version",
        event["query_sha256"],
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["schedule_id"],
        "--prisma-partition-label",
        f"{event['schedule_id']} {event['variant']} diagnostic",
        "--prisma-partition-description",
        event["purpose"],
    ]
    if fresh_browser:
        result.extend(
            [
                "--fresh-browser",
                "--headless",
                "--chrome-executable",
                str(
                    Path.home()
                    / "agent-tools/.browser-apps/Google Chrome.app/Contents/MacOS/Google Chrome for Testing"
                ),
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
        "schema_version": RECEIPT_SCHEMA,
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "008",
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
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    resume: bool,
    fresh_browser: bool,
) -> None:
    plan = load(plan_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != SCHEMA
        or not isinstance(events, list)
        or len(events) != 18
    ):
        raise RuntimeError("Unexpected ATAI Pilot 008 plan")
    if not ADAPTER.is_file():
        raise RuntimeError(f"ATAI adapter does not exist: {ADAPTER}")

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

        process = subprocess.run(command(event, output, fresh_browser), check=False)
        outcome: dict[str, Any] = {
            "event_id": event["event_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "return_code": process.returncode,
            "output": str(output.relative_to(pilot_root)),
            "output_exists": output.exists(),
            "reused_existing": False,
            "browser_mode": "fresh_headless" if fresh_browser else "shared_cdp",
        }
        artifact: dict[str, Any] | None = None
        if output.exists():
            artifact = load(output)
            outcome.update(
                {
                    "artifact_status": artifact.get("output_metadata", {}).get("status"),
                    "source_total": artifact.get("total"),
                    "records": len(artifact.get("results", [])),
                }
            )
        complete = (
            process.returncode == 0
            and artifact is not None
            and artifact_is_complete(event, artifact, output)
        )
        outcome["contract_complete"] = complete
        outcomes.append(outcome)
        write_receipt(
            receipt_path,
            plan_path,
            started,
            outcomes,
            len(events),
            "running" if complete else "stopped_on_source_or_adapter_failure",
        )
        if not complete:
            raise RuntimeError(f"Pilot 008 stopped at {event['event_id']}")

    write_receipt(receipt_path, plan_path, started, outcomes, len(events), "complete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--fresh-browser",
        action="store_true",
        help="Use one invocation-owned headless Chrome per remaining event.",
    )
    args = parser.parse_args()
    try:
        run(
            args.event_plan,
            args.pilot_root,
            args.receipt,
            args.resume,
            args.fresh_browser,
        )
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
