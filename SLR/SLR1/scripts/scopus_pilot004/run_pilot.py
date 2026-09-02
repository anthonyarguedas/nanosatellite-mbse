#!/usr/bin/env python3
"""Execute the predeclared Scopus Pilot 004 literal and wildcard events once."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "scopus-post-proximity-wildcard-pilot-run/v1"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def screenshot_paths(output: Path) -> dict[str, Path]:
    return {
        "search_page": output.with_name(f"{output.stem}.search-page.png"),
        "results_page": output.with_name(f"{output.stem}.results-page.png"),
    }


def artifact_summary(path: Path, expected_query: str) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact_written": False, "valid": False}
    value = load(path)
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    ids = [
        record.get("paperId")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("paperId"), str)
    ]
    screenshots = metadata.get("screenshots", {}) if isinstance(metadata, dict) else {}
    screenshot_checks: dict[str, Any] = {}
    for key, image in screenshot_paths(path).items():
        evidence = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        exists = image.is_file()
        digest = digest_file(image) if exists else None
        screenshot_checks[key] = {
            "path": str(image),
            "exists": exists,
            "receipt_path_matches": evidence.get("path") == image.name,
            "receipt_hash_matches": exists and evidence.get("sha256") == digest,
            "width": evidence.get("width"),
            "height": evidence.get("height"),
        }
    valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("query") == expected_query
        and isinstance(value.get("total"), int)
        and value.get("total") == len(records) == len(ids) == len(set(ids))
        and metadata.get("status") == "success"
        and metadata.get("strict_completion") is True
        and metadata.get("retrieval_complete") is True
        and metadata.get("passes_completed") == 2
        and metadata.get("two_pass_order_verified") is True
        and screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
        and all(
            check["exists"]
            and check["receipt_path_matches"]
            and check["receipt_hash_matches"]
            and isinstance(check["width"], int)
            and check["width"] > 0
            and isinstance(check["height"], int)
            and check["height"] > 0
            for check in screenshot_checks.values()
        )
    )
    return {
        "artifact_written": True,
        "valid": valid,
        "status": metadata.get("status"),
        "total": value.get("total"),
        "stable_id_count": len(ids),
        "ordered_stable_ids_sha256": metadata.get("ordered_stable_ids_sha256"),
        "screenshots": screenshot_checks,
    }


def command_for(
    event: dict[str, Any],
    *,
    output: Path,
    cdp_url: str,
    target_id: str,
) -> list[str]:
    event_id = event["event_id"]
    partition = event["partition_id"]
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
        "--result-scope",
        "documents",
        "--language",
        "English",
        "--page-size",
        "200",
        "--limit",
        "1999",
        "--max-pages",
        "10",
        "--timeout",
        "120",
        "--page-delay-seconds",
        "0.5",
        "--skip-full-abstracts",
        "--require-complete",
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"pilot-scopus-004-{event_id}",
        "--prisma-review-id",
        "slr1-pilot-004",
        "--prisma-strategy-reference",
        "slr1-scopus-post-proximity-wildcard-v1",
        "--prisma-strategy-version",
        event["protocol_commit"],
        "--prisma-phase",
        "pilot",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition,
        "--prisma-partition-label",
        partition,
        "--prisma-partition-description",
        f"Scopus Pilot 004 {partition} {event['variant']}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--settle-seconds", type=float, default=2.0)
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Fa-f0-9]{32}", args.target_id):
        raise SystemExit("--target-id must be one explicit 32-hex Scopus target")
    if args.settle_seconds < 0:
        raise SystemExit("--settle-seconds cannot be negative")
    if not ADAPTER.is_file():
        raise SystemExit(f"Scopus adapter is missing: {ADAPTER}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://localhost:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise SystemExit("Pilot 004 requires a loopback browser endpoint")
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")

    plan = load(args.plan)
    if plan.get("schema_version") != "scopus-post-proximity-wildcard-pilot-plan/v1":
        raise SystemExit("Unexpected Pilot 004 plan schema")
    if digest_file(ADAPTER) != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The Scopus adapter changed after predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 18:
        raise SystemExit("Pilot 004 requires exactly 18 predeclared events")

    started = now()
    outcomes: list[dict[str, Any]] = []
    stopped = False
    for index, event in enumerate(events):
        if index and args.settle_seconds:
            import time

            time.sleep(args.settle_seconds)
        output = args.pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        occupied = [output, *screenshot_paths(output).values()]
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise SystemExit(f"Refusing to overwrite an event artifact for {event['event_id']}")
        completed = subprocess.run(
            command_for(
                event,
                output=output,
                cdp_url=cdp_url,
                target_id=args.target_id,
            ),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        summary = artifact_summary(output, event["query"])
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "variant": event["variant"],
            "exit_code": completed.returncode,
            "artifact": str(output.relative_to(args.pilot_root)),
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "event": event["event_id"],
                    "exit_code": completed.returncode,
                    "total": summary.get("total"),
                    "valid": summary.get("valid"),
                }
            ),
            flush=True,
        )
        if completed.returncode != 0 or summary.get("valid") is not True:
            stopped = True
            break

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Scopus",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest_file(args.plan),
        "adapter": {
            "id": "search_scopus",
            "version": plan.get("adapter", {}).get("version"),
            "sha256": digest_file(ADAPTER),
        },
        "target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "completed_event_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": not stopped and len(outcomes) == len(events),
        "outcomes": outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
