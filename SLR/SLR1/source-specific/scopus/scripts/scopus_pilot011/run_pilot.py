#!/usr/bin/env python3
"""Run the two Scopus set-reconciled strict validation events once."""

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

SCHEMA = "scopus-set-reconciled-strict-validation-run/v1"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
TIED_IDS = {
    "SCOPUS-PUBLICATION:85137554950",
    "SCOPUS-PUBLICATION:105005251801",
    "SCOPUS-PUBLICATION:105002219161",
    "SCOPUS-PUBLICATION:105033917858",
}


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


def summarize(path: Path, event: dict[str, Any]) -> dict[str, Any]:
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
    receipt = metadata.get("strict_two_pass_receipt", {})
    screenshots = metadata.get("screenshots", {})
    images_valid = True
    image_rows = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshots.get(key, {})
        valid = bool(
            image.is_file()
            and evidence.get("path") == image.name
            and evidence.get("sha256") == digest(image)
            and isinstance(evidence.get("width"), int)
            and evidence["width"] > 0
            and isinstance(evidence.get("height"), int)
            and evidence["height"] > 0
        )
        images_valid = images_valid and valid
        image_rows.append({"kind": key, "path": str(image), "valid": valid})
    expected_identity = event["event_id"] != "swapping-papers-strict" or set(ids) == TIED_IDS
    valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("requested_query") == event["query"]
        and isinstance(value.get("total"), int)
        and value["total"] == len(records) == len(ids) == len(set(ids))
        and expected_identity
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and receipt.get("schema_version")
        == "academic-search-scopus-strict-two-pass/v2"
        and receipt.get("strict_completion") is True
        and receipt.get("strict_stable_id_sets_reconciled") is True
        and receipt.get("two_pass_set_verified") is True
        and isinstance(receipt.get("two_pass_order_verified"), bool)
        and isinstance(receipt.get("order_difference_count"), int)
        and receipt.get("source_reported_total") == value.get("total")
        and screenshots.get("schema_version") == "scopus-automatic-screenshots/v1"
        and screenshots.get("automatic") is True
        and images_valid
    )
    return {
        "valid": valid,
        "artifact_written": True,
        "status": metadata.get("status"),
        "total": value.get("total"),
        "stable_id_count": len(ids),
        "stable_id_set_sha256": receipt.get("stable_id_set_sha256"),
        "two_pass_order_verified": receipt.get("two_pass_order_verified"),
        "order_difference_count": receipt.get("order_difference_count"),
        "pass_order_hashes": [
            report.get("ordered_stable_ids_sha256")
            for report in receipt.get("pass_reports", [])
            if isinstance(report, dict)
        ],
        "screenshots": image_rows,
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
        str(event["page_size"]),
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
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
        f"pilot-scopus-011-{event['event_id']}",
        "--prisma-review-id",
        "slr1-pilot-011",
        "--prisma-strategy-reference",
        "slr1-scopus-set-reconciled-strict-v1",
        "--prisma-strategy-version",
        event["protocol_commit"],
        "--prisma-phase",
        "pilot",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["event_id"],
        "--prisma-partition-label",
        event["event_id"],
        "--prisma-partition-description",
        f"Scopus Pilot 011 {event['event_id']}",
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
        raise SystemExit("Pilot 011 requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != "scopus-set-reconciled-strict-validation-plan/v1":
        raise SystemExit("Unexpected plan schema")
    if digest(ADAPTER) != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The Scopus adapter changed after predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 2:
        raise SystemExit("Pilot 011 requires two events")

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
        summary = summarize(output, event)
        outcomes.append(
            {
                "event_id": event["event_id"],
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
                    **{
                        key: summary.get(key)
                        for key in (
                            "valid",
                            "total",
                            "two_pass_order_verified",
                            "order_difference_count",
                        )
                    },
                }
            ),
            flush=True,
        )
        if result.returncode != 0 or summary.get("valid") is not True:
            stopped = True
            break
    receipt = {
        "schema_version": SCHEMA,
        "pilot": "011",
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
