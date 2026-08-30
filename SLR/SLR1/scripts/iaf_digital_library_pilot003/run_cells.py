#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.48",
# ]
# ///

"""Run the already-built IAF Pilot 003 cells as strict diagnostic searches.

This runner deliberately invokes the maintained rendered IAF adapter rather
than reimplementing source interaction.  Invoke this script once through the
shared browser wrapper; child adapters inherit that proven local endpoint and
create/close only their own pages.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from plan import (
    DATE_END,
    DATE_START,
    DEFAULT_PLAN_PATH,
    MAIN_FACTORS,
    PILOT_DIR,
    REVIEW_ID,
    SOURCE_ID,
    STRATEGY_REFERENCE,
    STRATEGY_VERSION,
    validate_plan_payload,
)


CELL_COLLECTOR = Path(__file__).with_name("collect_cell.py")
DEFAULT_SEARCH_DIR = PILOT_DIR / "searches"


def load_plan(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_plan_payload(payload)
    if errors:
        raise ValueError("invalid cell plan: " + "; ".join(errors))
    return payload


def artifact_path(search_dir: Path, partition_id: str, cell_id: str) -> Path:
    return search_dir / "cells" / partition_id / f"{cell_id}.json"


def identity_ledger_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.identity-ledger.json")


def existing_status(path: Path, ledger: Path) -> str:
    """Classify an existing no-clobber compact result and identity sidecar."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "unreadable_existing"
    metadata = data.get("output_metadata")
    receipt = metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    if not isinstance(metadata, Mapping) or not isinstance(receipt, Mapping):
        return "malformed_existing"
    if (
        metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("count_only") is False
        and receipt.get("completion_status") == "complete"
        and receipt.get("report_ready") is True
        and ledger.is_file()
        and not ledger.is_symlink()
    ):
        return "complete_existing"
    if metadata.get("status") == "success" and ledger.is_file() is False:
        return "missing_identity_ledger_existing"
    return "noncomplete_existing"


def adapter_command(
    *,
    query: str,
    output: Path,
    partition_id: str,
    cell_id: str,
    timeout_seconds: float,
    page_delay_seconds: float,
    retries: int,
    page_size: int,
) -> list[str]:
    run_id = f"pilot-003-iaf-{partition_id.lower()}-{cell_id}"
    return [
        "uv",
        "run",
        str(CELL_COLLECTOR),
        "--query",
        query,
        "--output-path",
        str(output),
        "--identity-ledger-path",
        str(identity_ledger_path(output)),
        "--limit",
        "5000",
        "--max-pages",
        "100",
        "--page-size",
        str(page_size),
        "--passes",
        "2",
        "--timeout",
        str(timeout_seconds),
        "--page-delay-seconds",
        str(page_delay_seconds),
        "--retries",
        str(retries),
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--prisma-run-id",
        run_id,
        "--prisma-review-id",
        REVIEW_ID,
        "--prisma-strategy-reference",
        STRATEGY_REFERENCE,
        "--prisma-strategy-version",
        STRATEGY_VERSION,
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition_id,
        "--prisma-partition-label",
        partition_id,
        "--prisma-partition-description",
        f"Pilot 003 diagnostic lossless source cell for semantic partition {partition_id}",
    ]


def selected_partitions(values: Sequence[str] | None) -> tuple[str, ...]:
    if not values:
        return tuple(MAIN_FACTORS)
    selected = tuple(dict.fromkeys(values))
    unknown = [value for value in selected if value not in MAIN_FACTORS]
    if unknown:
        raise ValueError("unknown partition(s): " + ", ".join(unknown))
    return tuple(value for value in MAIN_FACTORS if value in selected)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--search-dir", type=Path, default=DEFAULT_SEARCH_DIR)
    parser.add_argument("--partition", action="append", help="run only a named planned partition; repeatable")
    parser.add_argument("--max-cells", type=int, help="bounded resume aid; omit to run every selected cell")
    parser.add_argument("--timeout", type=float, default=90.0, help="adapter-visible source timeout")
    parser.add_argument("--process-timeout", type=float, default=300.0, help="outer child-process timeout")
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--page-size", type=int, choices=(10, 50, 100, 200, 500), default=500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.max_cells is not None and args.max_cells < 1:
        parser.error("--max-cells must be positive")
    if args.timeout <= 0 or args.process_timeout <= 0:
        parser.error("timeouts must be positive")
    if args.page_delay_seconds < 0 or args.page_delay_seconds > 1:
        parser.error("page delay must be between zero and one second")
    if args.retries < 0:
        parser.error("--retries cannot be negative")
    if not CELL_COLLECTOR.is_file():
        parser.error("the IAF complete-cell collector is unavailable")

    try:
        plan = load_plan(args.plan.expanduser())
        partitions = selected_partitions(args.partition)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    search_dir = args.search_dir.expanduser().resolve()
    attempted = 0
    skipped = 0
    failures = 0
    planned = sum(
        len(plan["partitions"][partition_id]["cells"])
        for partition_id in partitions
    )
    for partition_id in partitions:
        cells = plan["partitions"][partition_id]["cells"]
        for cell in cells:
            if args.max_cells is not None and attempted >= args.max_cells:
                print(
                    json.dumps(
                        {
                            "status": "bounded_stop",
                            "attempted": attempted,
                            "skipped_existing": skipped,
                            "failures": failures,
                            "selected_planned_cells": planned,
                        }
                    )
                )
                return 1 if failures else 0
            cell_id = cell["cell_id"]
            output = artifact_path(search_dir, partition_id, cell_id)
            ledger = identity_ledger_path(output)
            if output.exists() or output.is_symlink():
                status = existing_status(output, ledger)
                if status == "missing_identity_ledger_existing":
                    backfill = [
                        "uv",
                        "run",
                        str(CELL_COLLECTOR),
                        "--output-path",
                        str(output),
                        "--identity-ledger-path",
                        str(ledger),
                        "--date-start",
                        DATE_START,
                        "--date-end",
                        DATE_END,
                        "--prisma-run-id",
                        f"pilot-003-iaf-{partition_id.lower()}-{cell_id}",
                        "--prisma-review-id",
                        REVIEW_ID,
                        "--prisma-strategy-reference",
                        STRATEGY_REFERENCE,
                        "--prisma-phase",
                        "identification",
                        "--prisma-coverage-scope",
                        "partition",
                        "--prisma-partition-id",
                        partition_id,
                        "--prisma-partition-label",
                        partition_id,
                        "--prisma-partition-description",
                        f"Pilot 003 diagnostic lossless source cell for semantic partition {partition_id}",
                        "--backfill-existing",
                    ]
                    if args.dry_run:
                        print(json.dumps({"partition": partition_id, "cell": cell_id, "backfill": backfill}))
                    else:
                        completed = subprocess.run(
                            backfill,
                            cwd=Path.cwd(),
                            env=os.environ.copy(),
                            capture_output=True,
                            text=True,
                            check=False,
                            timeout=args.process_timeout,
                        )
                        if completed.returncode != 0:
                            failures += 1
                    status = existing_status(output, ledger)
                skipped += 1
                print(f"{partition_id}/{cell_id}: {status}")
                if status != "complete_existing":
                    failures += 1
                continue
            if ledger.exists() or ledger.is_symlink():
                failures += 1
                print(f"{partition_id}/{cell_id}: orphan_identity_ledger")
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            command = adapter_command(
                query=cell["query"],
                output=output,
                partition_id=partition_id,
                cell_id=cell_id,
                timeout_seconds=args.timeout,
                page_delay_seconds=args.page_delay_seconds,
                retries=args.retries,
                page_size=args.page_size,
            )
            if args.dry_run:
                print(json.dumps({"partition": partition_id, "cell": cell_id, "command": command}))
                attempted += 1
                continue
            attempted += 1
            print(f"{partition_id}/{cell_id}: running ({attempted}/{planned})", flush=True)
            environment = os.environ.copy()
            environment.setdefault("PYTHONUNBUFFERED", "1")
            try:
                completed = subprocess.run(
                    command,
                    cwd=Path.cwd(),
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=args.process_timeout,
                )
                if completed.returncode != 0:
                    failures += 1
                    diagnostic_lines = (completed.stderr or completed.stdout or "").strip().splitlines()
                    diagnostic = diagnostic_lines[-1].replace(str(Path.cwd()), "<worktree>") if diagnostic_lines else "no_child_diagnostic"
                    print(f"{partition_id}/{cell_id}: adapter_exit_nonzero:{diagnostic[:240]}", flush=True)
                else:
                    print(
                        f"{partition_id}/{cell_id}: {existing_status(output, ledger) if output.exists() else 'missing_artifact'}",
                        flush=True,
                    )
                    if not output.exists() or existing_status(output, ledger) != "complete_existing":
                        failures += 1
            except subprocess.TimeoutExpired:
                failures += 1
                print(f"{partition_id}/{cell_id}: adapter_process_timeout", flush=True)
    print(
        json.dumps(
            {
                "status": "completed_with_failures" if failures else "completed",
                "attempted": attempted,
                "skipped_existing": skipped,
                "failures": failures,
                "selected_planned_cells": planned,
            }
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
