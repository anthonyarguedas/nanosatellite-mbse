#!/usr/bin/env python3
"""Run Scopus Pilot 003 events through the already-authorized browser.

Run this script itself under the shared-browser wrapper.  It invokes the
read-only Scopus adapter once per prospective pilot event and records only a
compact local receipt; each adapter JSON remains the authoritative source
artifact.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from queries import MAIN_PARTITIONS, PSR_PARTITIONS, lossless_cells, membership_audit


REFERENCE_ROOT = Path("/Users/antho/agent-tools-worktrees/slr-integration")
ADAPTER = REFERENCE_ROOT / "internet/skills/browser/scripts/search_scopus.py"
FOCUSED_ADAPTER = Path(__file__).with_name("focused_adapter.py")
SCHEMA_VERSION = "slr1-scopus-pilot003-run-receipt/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_plan(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != "slr1-scopus-pilot003-plan/v1":
        raise ValueError("Not a Scopus Pilot 003 plan")
    membership_audit()
    return value


def selected_events(plan: dict[str, Any], namespace: str, requested: set[str]) -> list[dict[str, Any]]:
    expected = MAIN_PARTITIONS if namespace == "main" else PSR_PARTITIONS
    wanted = requested or set(expected)
    unknown = wanted - set(expected)
    if unknown:
        raise ValueError(f"Partitions not in {namespace}: {sorted(unknown)}")
    events = [
        event
        for event in plan["events"]
        if event["review_namespace"] == namespace and event["partition_id"] in wanted
    ]
    if {event["partition_id"] for event in events} != wanted:
        raise ValueError("Plan does not contain every requested partition")
    return sorted(events, key=lambda event: expected.index(event["partition_id"]))


def build_command(
    event: dict[str, Any],
    output: Path,
    mode: str,
    timeout: int,
    *,
    query: str | None = None,
    cell_id: str | None = None,
    adapter: Path = ADAPTER,
    page_size: int | None = 200,
    max_pages: int = 10,
    skip_full_abstracts: bool = False,
) -> list[str]:
    namespace = event["review_namespace"]
    partition = event["partition_id"]
    query = event["query"] if query is None else query
    if "*" in query or "?" in query or "DOCTYPE" in query.upper():
        raise ValueError(f"Unsafe literal translation for {partition}")
    command = [
        "uv",
        "run",
        str(adapter),
        "--query",
        query,
        "--year-end",
        "2026",
        "--result-scope",
        "documents",
        *( ("--page-size", str(page_size)) if page_size is not None else () ),
        "--limit",
        "2000",
        "--max-pages",
        str(max_pages),
        "--timeout",
        str(timeout),
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"pilot-{'main' if namespace == 'main' else 'psr'}-{partition}-scopus-003-{mode}"
        + (f"-{cell_id}" if cell_id else ""),
        "--prisma-review-id",
        "slr1-pilot-003",
        "--prisma-strategy-reference",
        "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version",
        "8f5dc8e",
        "--prisma-phase",
        "pilot",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition,
        "--prisma-partition-label",
        partition,
        "--prisma-partition-description",
        f"Scopus Pilot 003 {namespace} {partition} {mode}",
    ]
    if namespace == "main":
        command.extend(("--year-start", "2011", "--language", "English"))
    # PSR deliberately has no lower date, language, document-type, subject,
    # access, or peer-review restriction.  No event ever receives DOCTYPE.
    command.append("--count-only" if mode == "count" else "--require-complete")
    if skip_full_abstracts:
        command.append("--skip-full-abstracts")
    return command


def artifact_summary(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact": str(path), "artifact_written": False}
    value = json.loads(path.read_text(encoding="utf-8"))
    metadata = value.get("output_metadata", {})
    return {
        "artifact": str(path),
        "artifact_written": True,
        "status": metadata.get("status"),
        "total": value.get("total"),
        "retrieval_complete": metadata.get("retrieval_complete"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "stable_id_count": len(
            [
                item
                for item in value.get("results", [])
                if isinstance(item, dict) and isinstance(item.get("paperId"), str)
            ]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--namespace", choices=("main", "prior_secondary_reviews"), required=True)
    parser.add_argument("--mode", choices=("count", "strict"), required=True)
    parser.add_argument("--partition", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--page-size", type=int, choices=(0, 10, 20, 50, 100, 200), default=50, help="0 retains Scopus's visible default page size.")
    parser.add_argument("--max-pages", type=int, default=40)
    parser.add_argument(
        "--skip-full-abstracts",
        action="store_true",
        help="Capture a strict stable-ID ledger first; use only when a separate native abstract follow-up is planned.",
    )
    parser.add_argument(
        "--focused-adapter",
        action="store_true",
        help="Use the local passive-editor-readback harness around the read-only adapter.",
    )
    parser.add_argument(
        "--settle-seconds",
        type=float,
        default=0.0,
        help="Passive delay before each event/cell after the first; no source action is repeated.",
    )
    parser.add_argument(
        "--label",
        help="Distinct artifact-directory/receipt label; defaults to --mode.",
    )
    parser.add_argument(
        "--cell-max-characters",
        type=int,
        help="Prospectively use a validated lossless OR-cell union for each selected partition.",
    )
    parser.add_argument(
        "--cell-id",
        action="append",
        default=[],
        help="Run only named lossless cell(s); requires --cell-max-characters.",
    )
    args = parser.parse_args()

    adapter = FOCUSED_ADAPTER if args.focused_adapter else ADAPTER
    if not adapter.is_file():
        raise SystemExit("Selected Scopus adapter is unavailable")
    if not os.environ.get("BH_CDP_URL"):
        raise SystemExit("Run under run_with_browser.py; BH_CDP_URL is absent")
    if args.max_pages < 1:
        raise SystemExit("--max-pages must be positive")
    if args.cell_id and args.cell_max_characters is None:
        raise SystemExit("--cell-id requires --cell-max-characters")
    plan = load_plan(args.plan)
    events = selected_events(plan, args.namespace, set(args.partition))
    label = args.label or args.mode
    if not label.replace("-", "").replace("_", "").isalnum():
        raise SystemExit("--label must be an ASCII word-like label")
    destination = args.root / "searches" / ("main" if args.namespace == "main" else "psr") / label
    destination.mkdir(parents=True, exist_ok=True)
    receipt_path = destination / "run-receipt.json"
    if receipt_path.exists() or receipt_path.is_symlink():
        raise SystemExit(f"Refusing to overwrite {receipt_path}")

    rows = []
    any_failed = False
    invocation_count = 0
    for event in events:
        partition = event["partition_id"]
        all_cells = (
            lossless_cells(partition, args.cell_max_characters)
            if args.cell_max_characters is not None
            else ({"cell_id": None, "query": event["query"]},)
        )
        requested_cell_ids = set(args.cell_id)
        if requested_cell_ids:
            available_cell_ids = {cell["cell_id"] for cell in all_cells}
            unknown_cell_ids = requested_cell_ids - available_cell_ids
            if unknown_cell_ids:
                raise SystemExit(f"Unknown {partition} cell IDs: {sorted(unknown_cell_ids)}")
            cells = tuple(cell for cell in all_cells if cell["cell_id"] in requested_cell_ids)
        else:
            cells = all_cells
        if args.cell_max_characters is not None:
            cell_dir = destination / partition
            cell_dir.mkdir(parents=True, exist_ok=True)
            cell_plan_path = cell_dir / "cell-plan.json"
            if cell_plan_path.exists() or cell_plan_path.is_symlink():
                raise SystemExit(f"Refusing to overwrite {cell_plan_path}")
            cell_plan_path.write_text(
                json.dumps(
                    {
                        "schema_version": "slr1-scopus-pilot003-lossless-cell-plan/v1",
                        "partition_id": partition,
                        "full_query": event["query"],
                        "maximum_characters": args.cell_max_characters,
                        "all_cells": all_cells,
                        "executed_cells": cells,
                        "selected_cell_ids": sorted(requested_cell_ids) if requested_cell_ids else None,
                        "reason": "A fresh full-expression pilot event did not yield a complete usable artifact; each replacement preserves source atoms and Boolean factors.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        cell_rows = []
        for cell in cells:
            if invocation_count and args.settle_seconds:
                time.sleep(args.settle_seconds)
            invocation_count += 1
            cell_id = cell["cell_id"]
            output = (
                destination / f"{partition}.json"
                if cell_id is None
                else destination / partition / f"{cell_id}.json"
            )
            if output.exists() or output.is_symlink():
                raise SystemExit(f"Refusing to overwrite {output}")
            command = build_command(
                event,
                output,
                args.mode,
                args.timeout,
                query=cell["query"],
                cell_id=cell_id,
                adapter=adapter,
                page_size=None if args.page_size == 0 else args.page_size,
                max_pages=args.max_pages,
                skip_full_abstracts=args.skip_full_abstracts,
            )
            completed = subprocess.run(command, check=False, text=True)
            summary = artifact_summary(output)
            cell_rows.append(
                {
                    "cell_id": cell_id,
                    "exit_code": completed.returncode,
                    "query_character_count": len(cell["query"]),
                    **summary,
                }
            )
        row = {
            "partition_id": partition,
            "event_id": event["event_id"],
            "logical_query_character_count": event["query_character_count"],
            "cells": cell_rows,
        }
        if len(cell_rows) == 1 and cell_rows[0]["cell_id"] is None:
            row.update({key: value for key, value in cell_rows[0].items() if key != "cell_id"})
        rows.append(row)
        any_failed = any_failed or any(
            item["exit_code"] != 0 or not item["artifact_written"] for item in cell_rows
        )

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "pilot_id": "003",
        "source": "Scopus",
        "namespace": args.namespace,
        "mode": args.mode,
        "label": label,
        "settle_seconds": args.settle_seconds,
        "page_size": None if args.page_size == 0 else args.page_size,
        "max_pages": args.max_pages,
        "skip_full_abstracts": args.skip_full_abstracts,
        "started_and_completed_on": now(),
        "adapter": str(adapter),
        "adapter_read_only": True,
        "focused_adapter_overlay": bool(args.focused_adapter),
        "results": rows,
        "success": not any_failed,
        "note": "Pilot only. Adapter artifacts, including null-total failures, are authoritative.",
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
