#!/usr/bin/env python3
"""Run the six predeclared Scopus tied-order diagnostic events once."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "scopus-tied-order-diagnostic-run/v1"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def summarize(path: Path, event: dict[str, Any], expected_ids: set[str]) -> dict[str, Any]:
    if not path.is_file():
        return {"valid": False, "artifact_written": False}
    value = load(path)
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    ids = [
        record.get("paperId")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("paperId"), str)
    ]
    screenshots = metadata.get("screenshots", {}) if isinstance(metadata, dict) else {}
    image_evidence = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        receipt = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        image_evidence.append(
            {
                "kind": key,
                "path": str(image),
                "exists": image.is_file(),
                "hash_matches": image.is_file()
                and receipt.get("sha256") == digest(image),
                "path_matches": receipt.get("path") == image.name,
                "width": receipt.get("width"),
                "height": receipt.get("height"),
            }
        )
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, dict) else {}
    valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("requested_query") == event["query"]
        and value.get("total") == 4
        and len(ids) == 4
        and len(set(ids)) == 4
        and set(ids) == expected_ids
        and metadata.get("status") == "partial"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is False
        and prisma.get("phase") == "pilot"
        and screenshots.get("schema_version") == "scopus-automatic-screenshots/v1"
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
        and all(
            item["exists"]
            and item["hash_matches"]
            and item["path_matches"]
            and isinstance(item["width"], int)
            and item["width"] > 0
            and isinstance(item["height"], int)
            and item["height"] > 0
            for item in image_evidence
        )
    )
    return {
        "valid": valid,
        "artifact_written": True,
        "status": metadata.get("status"),
        "total": value.get("total"),
        "ordered_paper_ids": ids,
        "ordered_years": [record.get("year") for record in records],
        "screenshots": image_evidence,
    }


def command(event: dict[str, Any], output: Path, cdp_url: str, target_id: str) -> list[str]:
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
        "10",
        "--limit",
        "10",
        "--max-pages",
        "1",
        "--timeout",
        "120",
        "--skip-full-abstracts",
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"pilot-scopus-010-{event['event_id']}",
        "--prisma-review-id",
        "slr1-pilot-010",
        "--prisma-strategy-reference",
        "slr1-scopus-tied-order-diagnostic-v1",
        "--prisma-strategy-version",
        event["protocol_commit"],
        "--prisma-phase",
        "pilot",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        "B1-order-diagnostic",
        "--prisma-partition-label",
        "B1 order diagnostic",
        "--prisma-partition-description",
        f"Scopus Pilot 010 {event['event_id']}",
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
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://localhost:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise SystemExit("Pilot 010 requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != "scopus-tied-order-diagnostic-plan/v1":
        raise SystemExit("Unexpected plan schema")
    if digest(ADAPTER) != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The Scopus adapter changed after predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 6:
        raise SystemExit("Pilot 010 requires six events")
    expected_ids = set(plan["identity_query"]["paper_ids"])

    outcomes = []
    stopped = False
    started = now()
    for index, event in enumerate(events):
        if index and args.settle_seconds:
            time.sleep(args.settle_seconds)
        output = args.pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        if any(
            path.exists() or path.is_symlink()
            for path in (output, *screenshot_paths(output))
        ):
            raise SystemExit(f"Refusing to overwrite {event['event_id']}")
        result = subprocess.run(
            command(event, output, cdp_url, args.target_id),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        summary = summarize(output, event, expected_ids)
        outcomes.append(
            {
                "event_id": event["event_id"],
                "pass_number": event["pass_number"],
                "exit_code": result.returncode,
                "artifact": str(output.relative_to(args.pilot_root)),
                **summary,
            }
        )
        print(
            json.dumps(
                {
                    "event": event["event_id"],
                    "exit_code": result.returncode,
                    "valid": summary.get("valid"),
                    "order": summary.get("ordered_paper_ids"),
                }
            ),
            flush=True,
        )
        if result.returncode != 0 or summary.get("valid") is not True:
            stopped = True
            break
    receipt = {
        "schema_version": SCHEMA,
        "pilot": "010",
        "diagnostic_only": True,
        "do_not_merge": True,
        "target_identifier_retained": False,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "adapter": plan["adapter"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "completed_event_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": not stopped and len(outcomes) == len(events),
        "outcomes": outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
