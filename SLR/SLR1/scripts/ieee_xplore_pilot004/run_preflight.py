#!/usr/bin/env python3
"""Run no-clobber IEEE Pilot 004 count diagnostics from its literal schedule.

This runner deliberately invokes the read-only fixed IEEE adapter.  It uses the
already-proven local shared-browser launcher only to supply an owned tab; it
never changes the adapter, browser profile, source controls, or queries.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEDULE = (
    ROOT
    / "source-specific/ieee-xplore/pilots/004/searches/schedule.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "source-specific/ieee-xplore/pilots/004/searches/preflight"
FIXED_ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
SHARED_BROWSER_RUNNER = Path.home() / "agent-tools/internet/skills/browser/scripts/run_with_browser.py"


def _artifact_label(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def _artifact_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"artifact": _artifact_label(path), "artifact_written": False, "total": None}
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata = payload.get("output_metadata", {})
    return {
        "artifact": _artifact_label(path),
        "artifact_written": True,
        "total": payload.get("total"),
        "status": metadata.get("status"),
        "merge_eligible": metadata.get("merge_eligible"),
        "query_sha256": next(
            (
                cell["query_sha256"]
                for partition in json.loads(DEFAULT_SCHEDULE.read_text(encoding="utf-8"))["partitions"]
                for cell in partition["cells"]
                if cell["query"] == payload.get("executed_query")
            ),
            None,
        ),
    }


def _command(
    query: str,
    output: Path,
    *,
    partition_id: str,
    cell_id: str,
    attempt: str,
) -> list[str]:
    run_id = f"slr1-ieee-pilot004-{attempt}-{partition_id.lower()}-{cell_id}"
    return [
        "uv",
        "run",
        str(SHARED_BROWSER_RUNNER),
        "--",
        "uv",
        "run",
        str(FIXED_ADAPTER),
        "--query",
        query,
        "--year-start",
        "2011",
        "--year-end",
        "2026",
        "--count-only",
        "--limit",
        "100",
        "--page-size",
        "100",
        "--timeout",
        "90",
        "--output-path",
        str(output),
        "--prisma-run-id",
        run_id,
        "--prisma-review-id",
        "slr1",
        "--prisma-strategy-reference",
        "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version",
        "8f5dc8e",
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        f"PILOT004-{partition_id}-{cell_id}",
        "--prisma-partition-label",
        f"IEEE Pilot 004 {partition_id} literal cell {cell_id} count diagnostic",
        "--prisma-partition-description",
        "Pilot-only literal source cell; native inclusive Publication Year 2011-2026; no final-search merge.",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, default=DEFAULT_SCHEDULE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument(
        "--only-cell",
        action="append",
        default=[],
        metavar="PARTITION:CELL",
        help="Run only an exact scheduled cell, for example BT2:cell-0002.",
    )
    parser.add_argument(
        "--attempt",
        default="preflight",
        help="Stable label for a new retry event namespace (default: preflight).",
    )
    args = parser.parse_args()

    if not FIXED_ADAPTER.is_file():
        raise SystemExit(f"fixed adapter is unavailable: {FIXED_ADAPTER}")
    if not SHARED_BROWSER_RUNNER.is_file():
        raise SystemExit(f"shared browser runner is unavailable: {SHARED_BROWSER_RUNNER}")
    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    selected = set(args.only)
    selected_cells = set(args.only_cell)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    failures = 0

    for partition in schedule["partitions"]:
        partition_id = partition["partition_id"]
        if selected and partition_id not in selected:
            continue
        for cell in partition["cells"]:
            cell_id = cell["cell_id"]
            if selected_cells and f"{partition_id}:{cell_id}" not in selected_cells:
                continue
            output = output_dir / f"{partition_id}-{cell_id}.json"
            if output.exists():
                print(f"Reusing {partition_id}/{cell_id} count diagnostic", flush=True)
                summaries.append(
                    {
                        "partition_id": partition_id,
                        "cell_id": cell_id,
                        "returncode": 0,
                        "reused_existing_artifact": True,
                        **_artifact_summary(output),
                    }
                )
                continue
            print(f"Running {partition_id}/{cell_id} count diagnostic", flush=True)
            completed = subprocess.run(
                _command(
                    cell["query"],
                    output,
                    partition_id=partition_id,
                    cell_id=cell_id,
                    attempt=args.attempt,
                ),
                check=False,
            )
            summary = {
                "partition_id": partition_id,
                "cell_id": cell_id,
                "returncode": completed.returncode,
                **_artifact_summary(output),
            }
            summaries.append(summary)
            if completed.returncode:
                failures += 1

    summary_path = output_dir / "preflight-summary.json"
    summary_payload = {
        "schema_version": "slr1-ieee-xplore-pilot004-preflight-summary/v1",
        "purpose": "Count-only planning diagnostics. These are not stable-ID union captures or final searches.",
        "attempt": args.attempt,
        "source": "IEEE Xplore",
        "controls": {
            "publication_year": "2011_2026_Year inclusive native Apply",
            "diagnostic_cutoff": "2026-08-29",
            "date_added": "not applied; separate indexing-date control",
            "language": "not applied",
            "publication_type": "not applied",
            "access": "all / not restricted",
            "wildcards": "not used",
        },
        "events": summaries,
    }
    if summary_path.exists():
        raise SystemExit(
            f"refusing to overwrite existing summary: {summary_path}; use a fresh output directory"
        )
    summary_path.write_text(
        json.dumps(summary_payload, indent=2) + "\n", encoding="utf-8"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
