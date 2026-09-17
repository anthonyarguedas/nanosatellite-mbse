#!/usr/bin/env python3
"""Build the factor-wise metadata union plan for AIAA ARC Pilot 006."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[4]
PILOT005 = ROOT / "source-specific" / "aiaa-arc" / "scripts" / "aiaa_arc_pilot005"
if str(PILOT005) not in sys.path:
    sys.path.insert(0, str(PILOT005))

from queries import (  # noqa: E402
    C1_FIXED_TERMS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    P_TERMS,
    PROTOCOL_COMMIT,
    TPRECISE_TERMS,
    all_of,
    ordinary_block,
)

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
PARTITIONS = ("BG1", "BG2", "BC1", "BT2")
FIELDS = ("Title", "Keywords", "Abstract")
SOURCE_FIELDS = {"Title": "Title", "Keywords": "Keyword", "Abstract": "Abstract"}

P_BLOCK = ordinary_block(P_TERMS)
MB_BLOCK = ordinary_block(MB_TERMS)
GMODEL_DIRECT_BLOCK = ordinary_block(GMODEL_FIXED_TERMS + GMISSION_EXACT_TERMS)
GMISSION_BLOCK = ordinary_block(GMISSION_TERMS)
GSTRUCTURE_DIRECT_BLOCK = ordinary_block(
    GSTRUCTURE_FIXED_TERMS + GPRODUCT_EXACT_TERMS + GVARIATION_TERMS
)
GPRODUCT_BLOCK = ordinary_block(GPRODUCT_TERMS)
C1_BLOCK = ordinary_block(C1_FIXED_TERMS + GDSL_TERMS)
TPRECISE_BLOCK = ordinary_block(TPRECISE_TERMS)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def slug(field: str) -> str:
    return field.casefold()


def grouped_rows(assignments: Iterable[tuple[str, str]]) -> list[dict[str, str]]:
    """Combine factors assigned to the same source field with explicit AND."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for field, expression in assignments:
        grouped[field].append(expression)
    rows = []
    for field in FIELDS:
        expressions = grouped.get(field, [])
        if not expressions:
            continue
        text = expressions[0] if len(expressions) == 1 else all_of(*expressions)
        rows.append({
            "field": field,
            "source_field": SOURCE_FIELDS[field],
            "text": text,
        })
    return rows


def event(
    event_id: str,
    partition: str,
    branch: str,
    assignments: Iterable[tuple[str, str]],
) -> dict:
    rows = grouped_rows(assignments)
    serialized = " AND ".join(f"{row['field']}={row['text']}" for row in rows)
    return {
        "event_id": event_id,
        "partition": partition,
        "branch": branch,
        "field_assignments": [
            {"field": field, "expression_sha256": digest(expression)}
            for field, expression in assignments
        ],
        "field_rows": rows,
        "serialized_query": serialized,
        "serialized_query_sha256": digest(serialized),
        "mode": "preview",
        "output": f"searches/cells/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/cells/{event_id}.search-page.png",
            "results_page": f"searches/cells/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def two_factor_cells(
    partition: str,
    branch: str,
    left_name: str,
    left: str,
    right_name: str,
    right: str,
) -> list[dict]:
    cells = []
    for left_field in FIELDS:
        for right_field in FIELDS:
            cell_id = (
                f"{partition}-{branch}-{left_name}-{slug(left_field)}-"
                f"{right_name}-{slug(right_field)}"
            )
            cells.append(
                event(
                    cell_id,
                    partition,
                    branch,
                    ((left_field, left), (right_field, right)),
                )
            )
    return cells


def three_factor_cells(
    partition: str,
    branch: str,
    factors: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
) -> list[dict]:
    cells = []
    for first_field in FIELDS:
        for second_field in FIELDS:
            for third_field in FIELDS:
                assignments = (
                    (first_field, factors[0][1]),
                    (second_field, factors[1][1]),
                    (third_field, factors[2][1]),
                )
                cell_id = (
                    f"{partition}-{branch}-{factors[0][0]}-{slug(first_field)}-"
                    f"{factors[1][0]}-{slug(second_field)}-"
                    f"{factors[2][0]}-{slug(third_field)}"
                )
                cells.append(event(cell_id, partition, branch, assignments))
    return cells


def build() -> dict:
    events: list[dict] = []
    events.extend(
        two_factor_cells(
            "BG1", "direct", "P", P_BLOCK, "Gdirect", GMODEL_DIRECT_BLOCK
        )
    )
    events.extend(
        three_factor_cells(
            "BG1",
            "mission-context",
            (("P", P_BLOCK), ("Gmission", GMISSION_BLOCK), ("MB", MB_BLOCK)),
        )
    )
    events.extend(
        two_factor_cells(
            "BG2", "direct", "P", P_BLOCK, "Gdirect", GSTRUCTURE_DIRECT_BLOCK
        )
    )
    events.extend(
        three_factor_cells(
            "BG2",
            "product-context",
            (("P", P_BLOCK), ("Gproduct", GPRODUCT_BLOCK), ("MB", MB_BLOCK)),
        )
    )
    events.extend(two_factor_cells("BC1", "complete", "P", P_BLOCK, "C1", C1_BLOCK))
    events.extend(
        three_factor_cells(
            "BT2",
            "complete",
            (("P", P_BLOCK), ("MB", MB_BLOCK), ("Tprecise", TPRECISE_BLOCK)),
        )
    )
    if len(events) != 108 or len({event["event_id"] for event in events}) != 108:
        raise RuntimeError("Pilot 006 must contain 108 unique factor-wise cells")
    partition_counts = {
        partition: sum(event["partition"] == partition for event in events)
        for partition in PARTITIONS
    }
    if partition_counts != {"BG1": 36, "BG2": 36, "BC1": 9, "BT2": 27}:
        raise RuntimeError(f"Unexpected partition cell counts: {partition_counts}")
    return {
        "schema_version": "aiaa-arc-pilot006-factor-wise-plan/v1",
        "source": SOURCE,
        "pilot": "006",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Measure the current expanded-Stream-B factor-wise Title/Keywords/Abstract "
            "union without requiring all factors in one metadata field."
        ),
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_scope": "inclusive ARC months before exact-day exclusions",
        },
        "metadata_route": {
            "fields": list(FIELDS),
            "atom": "META(s) = Title(L(s)) OR Keywords(L(s)) OR Abstract(L(s))",
            "factor_rule": "Rebuild each protocol Boolean expression from META atoms.",
            "source_execution": (
                "ARC rows are AND clauses, so the outer field OR is a stable-ID union "
                "over every field assignment. Factors assigned to one field are grouped "
                "with explicit AND in that row."
            ),
            "whole_query_same_field_union": False,
            "factor_wise_cross_field_combinations_retained": True,
            "cell_counts": partition_counts,
            "total_cells": len(events),
        },
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "wildcard": False,
            "proximity": False,
            "Anywhere": False,
        },
        "capture": {
            "mode": "non-mergeable complete preview when each cell is at most 100",
            "limit": 100,
            "max_pages": 5,
            "stable_identity": "normalized DOI before an ARC virtual-collection @ suffix",
            "automatic_screenshots": {
                "required": True,
                "search_page_suffix": ".search-page.png",
                "results_page_suffix": ".results-page.png",
                "opt_out": False,
            },
        },
        "acceptance_checks": [
            "Every cell receives exact source-observed field-row readback.",
            "Every cell total is at most 100 and its preview retains the complete DOI sequence.",
            "Every JSON has both mandatory sibling screenshot files and matching hashes.",
            "Every partition union reconciles raw events and normalized DOI identity.",
            "The current BC1 known eligible sentinel is retrieved.",
            "The complete Pilot 005 BG1 Anywhere set supplies a direct observed-loss comparison.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
