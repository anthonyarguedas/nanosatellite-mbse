#!/usr/bin/env python3
"""Build the predeclared AIAA ARC Pilot 005 event plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from queries import (
    CHANGED_IDS,
    PROTOCOL_COMMIT,
    SCHEDULE,
    SCHEDULE_IDS,
    TERM_COUNTS,
    all_of,
    literal,
)

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
KNOWN_DOI = "10.2514/6.2015-4474"
KNOWN_APPLICABLE_IDS = ("A2", "B1", "B2", "BC1")
OLD_BT2_CHARACTERS = 7_679
OLD_BG1_TOTAL = 8_088


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def event(
    event_id: str,
    purpose: str,
    query: str,
    mode: str,
    output: str,
    schedule_id: str,
) -> dict:
    return {
        "event_id": event_id,
        "schedule_id": schedule_id,
        "purpose": purpose,
        "query": query,
        "query_characters": len(query),
        "query_sha256": digest(query),
        "field_rows": [{"field": "Anywhere", "source_field": "AllField", "text": query}],
        "mode": mode,
        "output": output,
        "do_not_merge": True,
    }


def build() -> dict:
    events = []
    for schedule_id in SCHEDULE_IDS:
        query = SCHEDULE[schedule_id]
        events.append(
            event(
                f"count-{schedule_id}",
                "Prove direct one-row acceptance, exact readback, controls, and source total.",
                query,
                "count",
                f"searches/counts/{schedule_id}.json",
                schedule_id,
            )
        )
    for schedule_id in CHANGED_IDS:
        query = SCHEDULE[schedule_id]
        events.append(
            event(
                f"repeat-count-{schedule_id}",
                "Repeat the changed partition total independently.",
                query,
                "count",
                f"searches/repeat-counts/{schedule_id}.json",
                schedule_id,
            )
        )
        events.append(
            event(
                f"preview-{schedule_id}",
                "Capture up to the first 100 rendered cards for the changed partition precision audit.",
                query,
                "preview",
                f"searches/previews/{schedule_id}.json",
                schedule_id,
            )
        )
    for schedule_id in KNOWN_APPLICABLE_IDS:
        query = all_of(SCHEDULE[schedule_id], literal(KNOWN_DOI))
        events.append(
            event(
                f"known-item-{schedule_id}",
                "Check direct Anywhere retrieval of the source-located eligible sentinel in an applicable partition.",
                query,
                "preview",
                f"searches/known-item/{schedule_id}.json",
                schedule_id,
            )
        )
    return {
        "schema_version": "aiaa-arc-pilot005-event-plan/v1",
        "source": SOURCE,
        "pilot": "005",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test a direct, exact post-proximity translation of all nine partitions in one Anywhere row, "
            "including direct BT2 execution and the changed expanded-Stream-B precision profile."
        ),
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_bounds": "inclusive source months before exact-day treatment",
        },
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "published_in": None,
            "wildcard": False,
            "proximity": False,
            "field_narrowing": False,
        },
        "translation": {
            "literal": "one straight double-quoted literal",
            "ordinary_block": "quoted literals joined by explicit uppercase OR",
            "compound_block": "the protocol-declared nested AND/OR expression with full parentheses",
            "partition": "protocol factors joined by explicit uppercase AND",
            "field": "one Anywhere (AllField) row",
            "blocks": {
                "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
                "G_structure": "G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)",
                "C1": "C1_fixed OR G_DSL",
                "BT2": "P AND M_B AND T_precise",
            },
            "term_counts": TERM_COUNTS,
            "query_lengths": {key: len(value) for key, value in SCHEDULE.items()},
            "query_sha256": {key: digest(value) for key, value in SCHEDULE.items()},
            "no_pair_expansion": True,
        },
        "historical_comparators": {
            "old_pair_fallback_BG1_total": OLD_BG1_TOTAL,
            "old_pair_expanded_BT2_remainder_characters": OLD_BT2_CHARACTERS,
            "scope_warning": "Historical queries used the superseded concept definitions and are diagnostic comparators only.",
        },
        "known_item": {
            "doi": KNOWN_DOI,
            "applicable_partitions_under_current_protocol": list(KNOWN_APPLICABLE_IDS),
            "BT2_change": "The old adapted/model pair no longer establishes BT2 membership. The PDF has no T_precise literal.",
        },
        "acceptance_checks": [
            "All nine complete one-row expressions receive exact source readback and controls.",
            "Changed-partition repeated totals agree with their primary counts.",
            "BT2 executes directly without pair subcells.",
            "The eligible sentinel is retrieved in every current source-located applicable partition.",
            "Changed-partition previews quantify remaining visible-title precision without excluding hidden matches.",
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
