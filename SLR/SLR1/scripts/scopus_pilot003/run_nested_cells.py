#!/usr/bin/env python3
"""Run a nested lossless Scopus cell plan as pilot-only strict events."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ADAPTER = Path(__file__).with_name("focused_adapter.py")
SCHEMA = "slr1-scopus-pilot003-nested-cell-run-receipt/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def inspect(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact_written": False}
    value = json.loads(path.read_text(encoding="utf-8"))
    metadata = value.get("output_metadata", {})
    return {
        "artifact_written": True,
        "status": metadata.get("status"),
        "total": value.get("total"),
        "retrieval_complete": metadata.get("retrieval_complete"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "stable_id_count": len(value.get("results", [])),
    }


def command(query: str, output: Path, *, partition: str, cell_id: str, page_size: int) -> list[str]:
    return [
        "uv", "run", str(ADAPTER),
        "--query", query,
        "--year-end", "2026",
        "--result-scope", "documents",
        "--page-size", str(page_size),
        "--limit", "2000", "--max-pages", "10", "--timeout", "300",
        "--require-complete", "--skip-full-abstracts",
        "--output-path", str(output),
        "--prisma-run-id", f"pilot-psr-{partition}-{cell_id}-nested-strict",
        "--prisma-review-id", "slr1-pilot-003",
        "--prisma-strategy-reference", "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version", "8f5dc8e",
        "--prisma-phase", "pilot",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", partition,
        "--prisma-partition-label", partition,
        "--prisma-partition-description", "Nested lossless source-atom cell after a preserved parent-cell failure",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--settle-seconds", type=float, default=90.0)
    parser.add_argument("--page-size", type=int, choices=(10, 20, 50, 100, 200), default=200)
    args = parser.parse_args()
    if not os.environ.get("BH_CDP_URL") or not ADAPTER.is_file():
        raise SystemExit("Run under the shared browser with the focused adapter")
    if args.output_dir.exists():
        raise SystemExit(f"Refusing to overwrite {args.output_dir}")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    partition = plan.get("partition_id")
    children = plan.get("children")
    if not isinstance(partition, str) or not isinstance(children, list):
        raise SystemExit("Invalid nested cell plan")
    args.output_dir.mkdir(parents=True)
    rows = []
    for index, cell in enumerate(children):
        if index and args.settle_seconds:
            time.sleep(args.settle_seconds)
        cell_id, query = cell.get("cell_id"), cell.get("query")
        if not isinstance(cell_id, str) or not isinstance(query, str):
            raise SystemExit("Invalid nested cell")
        output = args.output_dir / f"{cell_id}.json"
        completed = subprocess.run(command(query, output, partition=partition, cell_id=cell_id, page_size=args.page_size), check=False, text=True)
        rows.append({"cell_id": cell_id, "exit_code": completed.returncode, "artifact": str(output), **inspect(output)})
    success = all(row["exit_code"] == 0 and row.get("retrieval_complete") for row in rows)
    (args.output_dir / "run-receipt.json").write_text(
        json.dumps({"schema_version": SCHEMA, "plan": str(args.plan), "partition_id": partition, "rows": rows, "success": success, "completed_at_utc": now()}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
