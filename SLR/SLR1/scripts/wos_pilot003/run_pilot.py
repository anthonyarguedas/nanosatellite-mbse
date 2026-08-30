#!/usr/bin/env python3
"""Run create-only, strict-completeness Web of Science Pilot 003 events.

Each invocation uses the shared-browser launcher and creates exactly one
adapter-owned browser tab.  It deliberately does not retry a failed source
event: the adapter's null failure receipt is retained as evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from queries import MAIN_IDS, PSR_IDS, SLR1_DIR, event_by_name, events


AGENT_TOOLS = Path.home() / "agent-tools"
BROWSER_RUNNER = AGENT_TOOLS / "internet" / "skills" / "browser" / "scripts" / "run_with_browser.py"
WOS_ADAPTER = AGENT_TOOLS / "internet" / "skills" / "browser" / "scripts" / "search_web_of_science.py"
PILOT_ROOT = (
    SLR1_DIR
    / "source-specific"
    / "web-of-science-core-collection"
    / "pilots"
    / "003"
)

# These capacities are intentionally above any anticipated pilot total.  The
# adapter itself fails closed at its documented 100,000-record source boundary.
LIMIT = 100_000
MAX_PAGES = 2_000
TIMEOUT_SECONDS = 120


def output_path(namespace: str, partition_id: str) -> Path:
    return PILOT_ROOT / "searches" / namespace / f"{partition_id}.json"


def build_command(namespace: str, partition_id: str) -> list[str]:
    planned = event_by_name(namespace, partition_id)
    output = output_path(namespace, partition_id)
    return [
        "caffeinate",
        "-dims",
        "uv",
        "run",
        str(BROWSER_RUNNER),
        "--",
        "uv",
        "run",
        str(WOS_ADAPTER),
        "--raw-query",
        planned.executed_query,
        "--require-complete",
        "--limit",
        str(LIMIT),
        "--max-pages",
        str(MAX_PAGES),
        "--timeout",
        str(TIMEOUT_SECONDS),
        "--output-path",
        str(output),
    ]


def artifact_summary(path: Path, returncode: int) -> dict[str, Any]:
    if not path.exists():
        return {
            "artifact": str(path),
            "runner_returncode": returncode,
            "status": "no_artifact_written",
            "total": None,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "artifact": str(path),
            "runner_returncode": returncode,
            "status": "unreadable_artifact",
            "total": None,
            "error": type(error).__name__,
        }
    metadata = payload.get("output_metadata", {})
    receipt = metadata.get("prisma_search_run", {}) if isinstance(metadata, dict) else {}
    rows = payload.get("results", [])
    ordered_ids = [row.get("paperId") for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    return {
        "artifact": str(path),
        "runner_returncode": returncode,
        "status": metadata.get("status"),
        "total": payload.get("total"),
        "receipt_completion_status": receipt.get("completion_status") if isinstance(receipt, dict) else None,
        "ordered_wos_id_count": len(ordered_ids),
    }


def run_one(namespace: str, partition_id: str, *, print_command: bool) -> dict[str, Any]:
    path = output_path(namespace, partition_id)
    marker = path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")
    if path.exists() or marker.exists():
        raise SystemExit(f"Refusing to overwrite existing Pilot 003 artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    command = build_command(namespace, partition_id)
    if print_command:
        print(json.dumps({"namespace": namespace, "partition_id": partition_id, "command": command}, indent=2))
        return {"namespace": namespace, "partition_id": partition_id, "status": "not_run"}
    completed = subprocess.run(
        command,
        check=False,
        env=os.environ.copy(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        # The adapter writes a null failure artifact itself.  Keep only a
        # bounded console diagnostic; raw browser output is not a pilot record.
        diagnostic = "\n".join(
            value
            for value in (completed.stdout, completed.stderr)
            if value
        )
        if diagnostic:
            print(diagnostic[-4000:], file=sys.stderr)
    summary = artifact_summary(path, completed.returncode)
    summary.update({"namespace": namespace, "partition_id": partition_id})
    print(json.dumps(summary, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", choices=("main", "psr"))
    parser.add_argument("--partition-id")
    parser.add_argument("--all", action="store_true", help="Run all 13 events serially")
    parser.add_argument("--print-command", action="store_true")
    args = parser.parse_args()
    if args.all == (args.namespace is not None or args.partition_id is not None):
        parser.error("Specify --all or both --namespace and --partition-id")
    if not args.all and not args.namespace:
        parser.error("Specify --all or both --namespace and --partition-id")
    if not args.all:
        expected = MAIN_IDS if args.namespace == "main" else PSR_IDS
        if args.partition_id not in expected:
            parser.error(f"{args.partition_id!r} is not a {args.namespace} partition")
        summaries = [run_one(args.namespace, args.partition_id, print_command=args.print_command)]
    else:
        summaries = [
            run_one(item.namespace, item.partition_id, print_command=args.print_command)
            for item in events()
        ]
    failures = [item for item in summaries if item.get("status") not in {"success", "not_run"}]
    print(json.dumps({"events": summaries, "failed_or_incomplete": len(failures)}, indent=2))
    # A failure's receipt is expected evidence, so do not make a completed
    # serial pilot runner erase or replace it.  The command's own nonzero exit
    # remains visible in each event summary and the later reconciliation.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
