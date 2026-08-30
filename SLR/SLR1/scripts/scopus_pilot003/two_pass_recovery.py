#!/usr/bin/env python3
"""Recover a strict stable-ID proof when the adapter's combined strict pass fails.

The two source runs remain separate Pilot 003 events.  This script never
accepts a prefix: it requires each pass's source total, complete row count,
and ordered Scopus publication-ID ledger to agree before emitting a recovery
receipt.  It is intentionally limited to stable-ID capture; native abstracts
are recovered separately in targeted EID follow-ups.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapter_paths import FOCUSED_ADAPTER_REFERENCE


ADAPTER = Path(__file__).with_name("focused_adapter.py")
SCHEMA = "slr1-scopus-pilot003-two-pass-stable-id-recovery/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_cell_queries(path: Path, requested: set[str]) -> list[dict[str, str]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    cells = value.get("all_cells", value.get("cells"))
    if not isinstance(cells, list):
        raise ValueError("Cell plan does not contain cells")
    selected = [cell for cell in cells if cell.get("cell_id") in requested]
    if {cell.get("cell_id") for cell in selected} != requested:
        raise ValueError("Requested cell absent from plan")
    for cell in selected:
        if not isinstance(cell.get("query"), str) or not cell["query"]:
            raise ValueError("Cell query is invalid")
        if "DOCTYPE" in cell["query"].upper() or "*" in cell["query"] or "?" in cell["query"]:
            raise ValueError("Recovery cell no longer has the literal safe translation")
    return selected


def inspect(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    ids = [record.get("paperId") for record in records if isinstance(record, dict)]
    total = value.get("total")
    complete = (
        isinstance(total, int)
        and total >= 0
        and metadata.get("retrieval_complete") is True
        and len(ids) == total
        and len(ids) == len(set(ids))
        and all(isinstance(value, str) and value.startswith("SCOPUS-PUBLICATION:") for value in ids)
    )
    return {
        "total": total,
        "retrieval_complete": metadata.get("retrieval_complete"),
        "status": metadata.get("status"),
        "stable_ids": ids,
        "complete": complete,
    }


def command(query: str, output: Path, *, run_id: str, partition: str, page_size: int) -> list[str]:
    return [
        "uv", "run", str(ADAPTER),
        "--query", query,
        "--year-end", "2026",
        "--result-scope", "documents",
        "--page-size", str(page_size),
        "--limit", "2000",
        "--max-pages", "10",
        "--timeout", "300",
        "--skip-full-abstracts",
        "--output-path", str(output),
        "--prisma-run-id", run_id,
        "--prisma-review-id", "slr1-pilot-003",
        "--prisma-strategy-reference", "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version", "8f5dc8e",
        "--prisma-phase", "pilot",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", partition,
        "--prisma-partition-label", partition,
        "--prisma-partition-description", "Independent stable-ID recovery pass after a preserved strict-adapter failure",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cell-plan", required=True, type=Path)
    parser.add_argument("--cell-id", required=True, action="append")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--partition", required=True)
    parser.add_argument("--settle-seconds", type=float, default=90.0)
    parser.add_argument("--page-size", type=int, choices=(10, 20, 50, 100, 200), default=200)
    args = parser.parse_args()
    if not ADAPTER.is_file() or not os.environ.get("BH_CDP_URL"):
        raise SystemExit("Run under the shared browser with the focused adapter available")
    root = args.output_dir
    if root.exists():
        raise SystemExit(f"Refusing to overwrite recovery directory {root}")
    root.mkdir(parents=True)
    results = []
    failed = False
    for index, cell in enumerate(load_cell_queries(args.cell_plan, set(args.cell_id))):
        cell_id, query = cell["cell_id"], cell["query"]
        cell_dir = root / cell_id
        cell_dir.mkdir()
        passes = []
        for pass_number in (1, 2):
            if pass_number == 2 and args.settle_seconds:
                time.sleep(args.settle_seconds)
            output = cell_dir / f"pass-{pass_number:02d}.json"
            completed = subprocess.run(
                command(
                    query,
                    output,
                    run_id=f"pilot-psr-{args.partition}-{cell_id}-recovery-pass-{pass_number}",
                    partition=args.partition,
                    page_size=args.page_size,
                ),
                check=False,
                text=True,
            )
            inspected = inspect(output) if output.is_file() else {"complete": False, "stable_ids": []}
            passes.append({"pass": pass_number, "exit_code": completed.returncode, "artifact": str(output), **inspected})
        accepted = (
            all(item["exit_code"] == 0 and item["complete"] for item in passes)
            and passes[0]["total"] == passes[1]["total"]
            and passes[0]["stable_ids"] == passes[1]["stable_ids"]
        )
        results.append({"cell_id": cell_id, "accepted": accepted, "passes": passes})
        failed = failed or not accepted
    receipt = {
        "schema_version": SCHEMA,
        "partition_id": args.partition,
        "cell_plan": str(args.cell_plan),
        "adapter": FOCUSED_ADAPTER_REFERENCE,
        "two_independent_fresh_runs": True,
        "requirements": "Both runs must reconcile source total, complete row count, unique publication IDs, and ordered stable-ID ledger.",
        "results": results,
        "accepted": not failed,
        "completed_at_utc": now(),
    }
    (root / "recovery-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
