#!/usr/bin/env python3
"""Build the AIAA ARC Pilot 007 hybrid metadata-anchored plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
PILOT005 = ROOT / "scripts" / "aiaa_arc_pilot005"
if str(PILOT005) not in sys.path:
    sys.path.insert(0, str(PILOT005))

from queries import (  # noqa: E402
    C1_FIXED_TERMS,
    EF_TERMS,
    EH_TERMS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    MH_TERMS,
    P_TERMS,
    PROTOCOL_COMMIT,
    R_TERMS,
    SCHEDULE,
    TPRECISE_TERMS,
    all_of,
    ordinary_block,
)

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
METADATA_FIELDS = ("Title", "Keywords", "Abstract")
ROW_ORDER = (*METADATA_FIELDS, "Anywhere")
SOURCE_FIELDS = {
    "Title": "Title",
    "Keywords": "Keyword",
    "Abstract": "Abstract",
    "Anywhere": "AllField",
}

P_BLOCK = ordinary_block(P_TERMS)
EH_BLOCK = ordinary_block(EH_TERMS)
EF_BLOCK = ordinary_block(EF_TERMS)
MH_BLOCK = ordinary_block(MH_TERMS)
MB_BLOCK = ordinary_block(MB_TERMS)
M_BLOCK = ordinary_block(MH_TERMS + MB_TERMS)
R_BLOCK = ordinary_block(R_TERMS)
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
    grouped: dict[str, list[str]] = defaultdict(list)
    normalized = tuple(assignments)
    for field, expression in normalized:
        grouped[field].append(expression)
    rows = []
    for field in ROW_ORDER:
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
    route: str,
    assignments: Iterable[tuple[str, str]],
) -> dict:
    normalized = tuple(assignments)
    rows = grouped_rows(normalized)
    serialized = " AND ".join(f"{row['field']}={row['text']}" for row in rows)
    return {
        "event_id": event_id,
        "partition": partition,
        "route": route,
        "field_assignments": [
            {"field": field, "expression_sha256": digest(expression)}
            for field, expression in normalized
        ],
        "field_rows": rows,
        "serialized_query": serialized,
        "serialized_query_sha256": digest(serialized),
        "mode": "card_preview",
        "output": f"searches/cells/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/cells/{event_id}.search-page.png",
            "results_page": f"searches/cells/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def two_metadata_factors(
    partition: str,
    route: str,
    left_name: str,
    left: str,
    right_name: str,
    right: str,
    anywhere: tuple[str, str] | None = None,
) -> list[dict]:
    cells = []
    for left_field in METADATA_FIELDS:
        for right_field in METADATA_FIELDS:
            assignments: list[tuple[str, str]] = [
                (left_field, left),
                (right_field, right),
            ]
            suffix = ""
            if anywhere is not None:
                assignments.append(("Anywhere", anywhere[1]))
                suffix = f"-{anywhere[0]}-anywhere"
            cell_id = (
                f"{partition}-{route}-{left_name}-{slug(left_field)}-"
                f"{right_name}-{slug(right_field)}{suffix}"
            )
            cells.append(event(cell_id, partition, route, assignments))
    return cells


def three_metadata_factors(
    partition: str,
    route: str,
    factors: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
) -> list[dict]:
    cells = []
    for first_field in METADATA_FIELDS:
        for second_field in METADATA_FIELDS:
            for third_field in METADATA_FIELDS:
                assignments = (
                    (first_field, factors[0][1]),
                    (second_field, factors[1][1]),
                    (third_field, factors[2][1]),
                )
                cell_id = (
                    f"{partition}-{route}-{factors[0][0]}-{slug(first_field)}-"
                    f"{factors[1][0]}-{slug(second_field)}-"
                    f"{factors[2][0]}-{slug(third_field)}"
                )
                cells.append(event(cell_id, partition, route, assignments))
    return cells


def build() -> dict:
    events: list[dict] = []
    events.extend(
        two_metadata_factors(
            "A1", "hybrid", "P", P_BLOCK, "MH", MH_BLOCK, ("EH", EH_BLOCK)
        )
    )
    events.extend(
        two_metadata_factors(
            "A2", "hybrid", "P", P_BLOCK, "M", M_BLOCK, ("EF", EF_BLOCK)
        )
    )
    events.extend(
        two_metadata_factors(
            "A3", "hybrid", "P", P_BLOCK, "MB", MB_BLOCK, ("EH", EH_BLOCK)
        )
    )
    events.extend(
        two_metadata_factors("B1", "metadata", "P", P_BLOCK, "MH", MH_BLOCK)
    )
    events.extend(
        two_metadata_factors(
            "B2", "hybrid", "P", P_BLOCK, "MB", MB_BLOCK, ("R", R_BLOCK)
        )
    )
    events.append(
        event(
            "BG1-direct-anywhere",
            "BG1",
            "direct_anywhere",
            (("Anywhere", SCHEDULE["BG1"]),),
        )
    )
    events.extend(
        two_metadata_factors(
            "BG2",
            "direct-metadata",
            "P",
            P_BLOCK,
            "Gdirect",
            GSTRUCTURE_DIRECT_BLOCK,
        )
    )
    events.extend(
        three_metadata_factors(
            "BG2",
            "product-context-metadata",
            (("P", P_BLOCK), ("Gproduct", GPRODUCT_BLOCK), ("MB", MB_BLOCK)),
        )
    )
    for population_field in METADATA_FIELDS:
        events.append(
            event(
                f"BC1-hybrid-P-{slug(population_field)}-C1-anywhere",
                "BC1",
                "hybrid",
                ((population_field, P_BLOCK), ("Anywhere", C1_BLOCK)),
            )
        )
    events.extend(
        two_metadata_factors(
            "BT2",
            "hybrid",
            "P",
            P_BLOCK,
            "MB",
            MB_BLOCK,
            ("Tprecise", TPRECISE_BLOCK),
        )
    )

    if len(events) != 94 or len({entry["event_id"] for entry in events}) != 94:
        raise RuntimeError("Pilot 007 must contain 94 unique hybrid cells")
    cell_counts = {
        partition: sum(entry["partition"] == partition for entry in events)
        for partition in PARTITIONS
    }
    expected = {
        "A1": 9,
        "A2": 9,
        "A3": 9,
        "B1": 9,
        "B2": 9,
        "BG1": 1,
        "BG2": 36,
        "BC1": 3,
        "BT2": 9,
    }
    if cell_counts != expected:
        raise RuntimeError(f"Unexpected hybrid cell counts: {cell_counts}")
    return {
        "schema_version": "aiaa-arc-pilot007-hybrid-plan/v1",
        "source": SOURCE,
        "pilot": "007",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test a feasible metadata-anchored search that keeps body-sensitive EPS, "
            "relationship, central-asset, and tailoring factors in Anywhere."
        ),
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_scope": "inclusive ARC months before exact-day exclusions",
        },
        "translation": {
            "META": "Title OR Keywords OR Abstract at factor level",
            "A1": "META(P) AND META(M_H) AND Anywhere(E_H)",
            "A2": "META(P) AND META(M_H OR M_B) AND Anywhere(E_F)",
            "A3": "META(P) AND META(M_B) AND Anywhere(E_H)",
            "B1": "META(P) AND META(M_H)",
            "B2": "META(P) AND META(M_B) AND Anywhere(R)",
            "BG1": "Anywhere(P AND G_model)",
            "BG2": "factor-wise metadata G_structure route from Pilot 006",
            "BC1": "META(P) AND Anywhere(C1)",
            "BT2": "META(P) AND META(M_B) AND Anywhere(T_precise)",
            "cell_counts": cell_counts,
            "total_cells": len(events),
        },
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "wildcard": False,
            "proximity": False,
        },
        "capture": {
            "mode": "non-mergeable rendered-card preview",
            "formatted_citations_required": False,
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
            "Every cell remains at most 100 and is captured completely.",
            "The eligible sentinel is retrieved in A2, B1, B2, and BC1.",
            "Every partition and the schedule union remain feasible for screening.",
            "Every successful JSON has both mandatory sibling screenshots.",
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
