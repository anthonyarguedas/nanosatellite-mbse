#!/usr/bin/env python3
"""Build the triggered BG2 fixed-literal diagnostic plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from queries import GSTRUCTURE_FIXED_TERMS, P_TERMS, PROTOCOL_COMMIT, all_of, literal, ordinary_block

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def build(branch_artifact: Path) -> dict:
    branch_total = json.loads(branch_artifact.read_text()).get("total")
    if branch_total != 3_571:
        raise RuntimeError(f"Expected triggered BG2 fixed total 3571, got {branch_total!r}")
    events = []
    for index, term in enumerate(GSTRUCTURE_FIXED_TERMS, start=1):
        query = all_of(ordinary_block(P_TERMS), literal(term))
        event_id = f"branch-BG2-fixed-literal-{index:02d}"
        events.append({
            "event_id": event_id,
            "schedule_id": "BG2",
            "branch": "G_structure_fixed",
            "literal": term,
            "purpose": "Attribute the dominant BG2 fixed branch to one normative literal.",
            "query": query,
            "query_characters": len(query),
            "query_sha256": digest(query),
            "field_rows": [{"field": "Anywhere", "source_field": "AllField", "text": query}],
            "mode": "count",
            "output": f"searches/branch-counts/BG2-fixed-literal-{index:02d}.json",
            "do_not_merge": True,
        })
    return {
        "schema_version": "aiaa-arc-pilot005-bg2-fixed-event-plan/v1",
        "source": SOURCE,
        "pilot": "005",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "trigger": {
            "parent_branch": "P AND G_structure_fixed",
            "parent_source_total": branch_total,
            "reason": "The fixed branch accounts for nearly all of the 3584-record BG2 total.",
        },
        "date_window": {"requested_start": DATE_START, "requested_end": DATE_END},
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "wildcard": False,
            "proximity": False,
            "field_narrowing": False,
        },
        "interpretation": "Literal totals overlap and do not replace the complete BG2 query.",
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch-artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.branch_artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
