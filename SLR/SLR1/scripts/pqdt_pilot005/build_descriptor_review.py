#!/usr/bin/env python3
"""Record the PQDT Pilot 005 descriptor-only record review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries

SCHEMA = "pqdt-global-pilot005-descriptor-only-review/v1"
DEFAULT_COMPARISON = queries.PILOT_ROOT / "searches" / "set-comparison.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "descriptor-only-review.json"


def build(comparison_path: Path) -> dict[str, Any]:
    comparison = queries.load_object(comparison_path)
    if comparison.get("schema_version") != "pqdt-global-pilot005-set-comparison/v1":
        raise RuntimeError("Unexpected PQDT set-comparison schema")
    union = comparison.get("union_comparison", {})
    records = comparison.get("descriptor_only_records")
    if not isinstance(records, list):
        raise RuntimeError("PQDT set comparison lacks a descriptor-only review frame")
    ids = union.get("descriptor_only_ids")
    if not isinstance(ids, list) or len(ids) != len(records):
        raise RuntimeError("PQDT descriptor-only review frame does not reconcile")
    if ids:
        raise RuntimeError(
            "Descriptor-only records require explicit record-level review rows before assessment"
        )
    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "complete_empty_review_frame",
        "diagnostic_only": True,
        "do_not_merge": True,
        "input_comparison": {
            "path": str(comparison_path.relative_to(queries.PILOT_ROOT)),
            "sha256": queries.file_sha256(comparison_path),
        },
        "review_scope": (
            "Every distinct record returned by an augmented partition and absent from the "
            "complete free-text schedule union."
        ),
        "review_rule": (
            "Assess each record against the intended mapped P, M_H, M_B, and R concepts. "
            "Do not use this pilot review as a final scientific eligibility decision."
        ),
        "descriptor_only_record_count": 0,
        "reviewed_record_count": 0,
        "records": [],
        "outcome": "no_descriptor_only_records_to_review",
        "reason": (
            "Every augmented partition had the same complete ordered numeric document IDs "
            "as its adjacent free-text baseline."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(args.comparison.expanduser().resolve())
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 descriptor-only review differs")
        return 0
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
