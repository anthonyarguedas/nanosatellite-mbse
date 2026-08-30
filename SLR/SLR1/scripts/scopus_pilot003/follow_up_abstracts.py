#!/usr/bin/env python3
"""Retrieve native Scopus abstracts for an already-complete main ID union.

EID batches are follow-up retrieval only: every requested identifier must
already be in the stable-ID union, and a batch must return exactly that set
before its abstracts are linked.  No discovery partition is changed.
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


ADAPTER = Path(__file__).with_name("focused_adapter.py")
SCHEMA = "slr1-scopus-pilot003-native-abstract-follow-up/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def command(ids: list[str], output: Path, batch: int, *, namespace: str) -> list[str]:
    numeric = [identifier.removeprefix("SCOPUS-PUBLICATION:") for identifier in ids]
    query = "EID(" + " OR ".join(f"2-s2.0-{identifier}" for identifier in numeric) + ")"
    controls = ["--year-end", "2026", "--result-scope", "documents"]
    if namespace == "main":
        controls.extend(("--year-start", "2011", "--language", "English"))
    return [
        "uv", "run", str(ADAPTER), "--query", query,
        *controls,
        "--page-size", "50", "--limit", "2000", "--max-pages", "40", "--timeout", "300",
        "--require-complete", "--output-path", str(output),
        "--prisma-run-id", f"pilot-{'main' if namespace == 'main' else 'psr'}-EID-abstract-follow-up-{batch:03d}-scopus-003",
        "--prisma-review-id", "slr1-pilot-003",
        "--prisma-strategy-reference", "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version", "8f5dc8e", "--prisma-phase", "pilot",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", "ABSTRACT-FOLLOW-UP",
        "--prisma-partition-label", "ABSTRACT-FOLLOW-UP",
        "--prisma-partition-description", "Stable-ID constrained native abstract follow-up; not a new discovery event",
    ]


def inspect(path: Path, expected: list[str]) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact_written": False, "accepted": False}
    value = json.loads(path.read_text(encoding="utf-8"))
    metadata = value.get("output_metadata", {})
    rows = value.get("results", [])
    ids = [row.get("paperId") for row in rows if isinstance(row, dict)]
    accepted = (
        metadata.get("retrieval_complete") is True
        and isinstance(value.get("total"), int)
        and value["total"] == len(expected)
        and set(ids) == set(expected)
        and len(ids) == len(set(ids))
    )
    return {
        "artifact_written": True,
        "status": metadata.get("status"),
        "total": value.get("total"),
        "retrieval_complete": metadata.get("retrieval_complete"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "returned_ids": ids,
        "native_abstract_count": sum(bool(row.get("abstract")) for row in rows if isinstance(row, dict)),
        "explicitly_no_native_abstract_count": sum(bool(row.get("abstract_not_available")) for row in rows if isinstance(row, dict)),
        "accepted": accepted,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--union", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--namespace", choices=("main", "prior_secondary_reviews"), default="main")
    parser.add_argument("--batch-size", type=int, default=12)
    parser.add_argument("--max-batches", type=int)
    parser.add_argument("--settle-seconds", type=float, default=60.0)
    args = parser.parse_args()
    if args.batch_size < 1 or not ADAPTER.is_file() or not os.environ.get("BH_CDP_URL"):
        raise SystemExit("Need a positive batch size, focused adapter, and shared browser")
    if args.output_dir.exists():
        raise SystemExit(f"Refusing to overwrite {args.output_dir}")
    union = json.loads(args.union.read_text(encoding="utf-8"))
    section = union[args.namespace]
    ids = [row["paper_id"] for row in section["records"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("Main union IDs are not unique")
    batches = [ids[index : index + args.batch_size] for index in range(0, len(ids), args.batch_size)]
    if args.max_batches is not None:
        batches = batches[: args.max_batches]
    args.output_dir.mkdir(parents=True)
    rows = []
    for index, batch in enumerate(batches, start=1):
        if index > 1 and args.settle_seconds:
            time.sleep(args.settle_seconds)
        output = args.output_dir / f"batch-{index:03d}.json"
        completed = subprocess.run(command(batch, output, index, namespace=args.namespace), check=False, text=True)
        rows.append({"batch": index, "requested_ids": batch, "exit_code": completed.returncode, "artifact": str(output), **inspect(output, batch)})
    accepted = all(row["accepted"] for row in rows)
    receipt = {
        "schema_version": SCHEMA,
        "source": "Scopus",
        "pilot_only": True,
        "input_union": str(args.union),
        "namespace": args.namespace,
        "batch_size": args.batch_size,
        "requested_record_count": sum(len(row["requested_ids"]) for row in rows),
        "complete_for_requested_batches": accepted,
        "batches": rows,
        "completed_at_utc": now(),
        "limit": "This constrained retrieval adds no discovery IDs and does not resolve final screening or cutoff-day eligibility.",
    }
    (args.output_dir / "abstract-follow-up-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
