#!/usr/bin/env python3
"""Write the predeclared arXiv browser Pilot 004 plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode

from queries import BLOCK_ROWS, CELLS, PROTOCOL_COMMIT, SCHEDULE_IDS

DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
LIMIT = 1000
MAX_PAGES = 20


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def event(cell) -> dict:
    parameters = [("advanced", "1")]
    for index, row in enumerate(cell.rows):
        parameters.extend(
            (
                (f"terms-{index}-operator", "AND"),
                (f"terms-{index}-term", row),
                (f"terms-{index}-field", "all"),
            )
        )
    parameters.extend(
        (
            ("classification-physics_archives", "all"),
            ("classification-include_cross_list", "include"),
            ("date-filter_by", "date_range"),
            ("date-from_date", DATE_START),
            ("date-to_date", "2026-08-30"),
            ("date-date_type", "submitted_date_first"),
            ("abstracts", "show"),
            ("size", "100"),
            ("order", "submitted_date"),
        )
    )
    encoded = urlencode(parameters)
    return {
        "event_id": cell.cell_id,
        "partition_id": cell.partition_id,
        "cell_number": cell.cell_number,
        "cell_count": cell.cell_count,
        "branch": cell.branch,
        "factors": list(cell.factors),
        "rows": [
            {"operator": "AND", "field": "all", "term": row}
            for row in cell.rows
        ],
        "serialized_query": cell.serialized_query,
        "query_sha256": cell.query_sha256,
        "row_character_counts": [len(row) for row in cell.rows],
        "encoded_request_query_characters": len(encoded),
        "mode": "strict_complete",
        "output": (
            f"cells/{cell.partition_id}/"
            f"cell-{cell.cell_number:02d}-of-{cell.cell_count:02d}.json"
        ),
        "do_not_merge": True,
    }


def build() -> dict:
    events = [event(cell) for cell in CELLS]
    return {
        "schema_version": "arxiv-browser-pilot004-event-plan/v1",
        "source": "arXiv",
        "interface": "rendered Advanced Search web interface",
        "platform": "arXiv Search",
        "pilot": "004",
        "plan_revision": 2,
        "revision_reason": (
            "The initial direct A2 cell was rejected before a source total. Revision 2 "
            "distributes only its unchanged M_H OR M_B factor into two cells."
        ),
        "superseded_plan": "event-plan-initial.json",
        "original_failure_receipt": "run-receipt-attempt2.json",
        "retained_failure_reproduction": (
            "failures/A2-direct-cell-failure-reproduction.NON_MERGEABLE_FAILURE.json"
        ),
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Replace the prospective Atom route with a rendered Advanced Search "
            "translation for all nine direct partitions and validate complete capture."
        ),
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "status": "labelled pilot window, not the unset common review cutoff",
            "basis": "original submission date",
            "requested_calendar_inclusive": True,
            "source_upper_exclusive": "2026-08-30",
        },
        "controls": {
            "field": "All fields for every row",
            "subject_categories": [],
            "physics_archive": "all",
            "cross_lists": "include",
            "language": "unavailable",
            "publication_type": "arXiv submissions/e-prints, with no type limiter",
            "include_older_versions": False,
            "abstracts": "show",
            "sort": "Submission date (oldest first)",
            "limit": LIMIT,
            "max_pages": MAX_PAGES,
            "strict_pass_delay_seconds": 10,
            "inter_event_delay_seconds": 30,
            "screenshots": (
                "mandatory automatic configured-search PNG before execution and "
                "first-results PNG for every source event"
            ),
        },
        "translation": {
            "literal": "one exact straight-double-quoted literal",
            "ordinary_block": (
                "all literals joined by homogeneous uppercase OR inside one "
                "rendered All-fields row"
            ),
            "conjunction": "one rendered row per factor, joined by outer AND controls",
            "compound_distribution": {
                "A2": "two-cell union: P AND E_F AND M_H, then P AND E_F AND M_B",
                "BG1": (
                    "two-cell union: P AND (G_model_fixed OR G_mission_exact), "
                    "then P AND G_mission AND M_B"
                ),
                "BG2": (
                    "two-cell union: P AND (G_structure_fixed OR G_product_exact "
                    "OR G_variation), then P AND G_product AND M_B"
                ),
            },
            "wildcards": False,
            "proximity": False,
            "pair_expansion": False,
            "block_row_sha256": {
                name: digest(value) for name, value in BLOCK_ROWS.items()
            },
        },
        "partition_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
        "acceptance_checks": [
            "Every normative ordinary term occurs in its declared browser row.",
            "Each cell receives exact rendered query and control readback.",
            "Each cell exhausts the exact source total twice with the same ordered arXiv IDs.",
            "Every cell saves both mandatory screenshots beside its JSON.",
            "The three distributed compound partitions are reconciled as stable-ID unions.",
            "No result-driven filter, wildcard, proximity syntax, or controlled-vocabulary supplement is added.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
