#!/usr/bin/env python3
"""Build the Stream A and core Stream B metadata cells for Pilot 006."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
PILOT005 = ROOT / "scripts" / "aiaa_arc_pilot005"
if str(PILOT005) not in sys.path:
    sys.path.insert(0, str(PILOT005))
if str(SCRIPT_DIR) in sys.path:
    sys.path.remove(str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from queries import (  # noqa: E402
    EF_TERMS,
    EH_TERMS,
    MB_TERMS,
    MH_TERMS,
    P_TERMS,
    PROTOCOL_COMMIT,
    R_TERMS,
    ordinary_block,
)

from build_plan import (  # noqa: E402
    DATE_END,
    DATE_START,
    FIELDS,
    SOURCE,
    three_factor_cells,
    two_factor_cells,
)

PARTITIONS = ("A1", "A2", "A3", "B1", "B2")
P_BLOCK = ordinary_block(P_TERMS)
EH_BLOCK = ordinary_block(EH_TERMS)
EF_BLOCK = ordinary_block(EF_TERMS)
MH_BLOCK = ordinary_block(MH_TERMS)
MB_BLOCK = ordinary_block(MB_TERMS)
M_BLOCK = ordinary_block(MH_TERMS + MB_TERMS)
R_BLOCK = ordinary_block(R_TERMS)


def build() -> dict:
    events: list[dict] = []
    events.extend(
        three_factor_cells(
            "A1", "complete", (("P", P_BLOCK), ("EH", EH_BLOCK), ("MH", MH_BLOCK))
        )
    )
    events.extend(
        three_factor_cells(
            "A2", "complete", (("P", P_BLOCK), ("EF", EF_BLOCK), ("M", M_BLOCK))
        )
    )
    events.extend(
        three_factor_cells(
            "A3", "complete", (("P", P_BLOCK), ("EH", EH_BLOCK), ("MB", MB_BLOCK))
        )
    )
    events.extend(two_factor_cells("B1", "complete", "P", P_BLOCK, "MH", MH_BLOCK))
    events.extend(
        three_factor_cells(
            "B2", "complete", (("P", P_BLOCK), ("MB", MB_BLOCK), ("R", R_BLOCK))
        )
    )
    if len(events) != 117 or len({event["event_id"] for event in events}) != 117:
        raise RuntimeError("Pilot 006 core extension must contain 117 unique cells")
    partition_counts = {
        partition: sum(event["partition"] == partition for event in events)
        for partition in PARTITIONS
    }
    if partition_counts != {"A1": 27, "A2": 27, "A3": 27, "B1": 9, "B2": 27}:
        raise RuntimeError(f"Unexpected core partition cell counts: {partition_counts}")
    return {
        "schema_version": "aiaa-arc-pilot006-factor-wise-core-plan/v1",
        "source": SOURCE,
        "pilot": "006",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Extend the factor-wise Title/Keywords/Abstract union to Stream A and "
            "core Stream B after the expanded-Stream-B cells completed below 100."
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
            "mode": "non-mergeable rendered-card preview",
            "formatted_citations_required": False,
            "limit": 100,
            "max_pages": 5,
            "automatic_screenshots": {
                "required": True,
                "search_page_suffix": ".search-page.png",
                "results_page_suffix": ".results-page.png",
                "opt_out": False,
            },
        },
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
