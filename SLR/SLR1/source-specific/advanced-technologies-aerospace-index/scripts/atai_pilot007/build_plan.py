#!/usr/bin/env python3
"""Build the predeclared ATAI Pilot 007 event plan."""

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
)

SOURCE = "Advanced Technologies & Aerospace Index"
SOURCE_ID = "proquest_aerospace_index"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
QUERY_LIMIT = 50_000


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
        "mode": mode,
        "language": "English",
        "date_start": DATE_START,
        "date_end": DATE_END,
        "output": output,
        "do_not_merge": True,
    }


def build() -> dict:
    events = []
    for pass_number in (1, 2):
        for schedule_id in SCHEDULE_IDS:
            query = SCHEDULE[schedule_id]
            events.append(
                event(
                    f"count-{schedule_id}-pass{pass_number}",
                    f"Exact source-total pass {pass_number} for the complete {schedule_id} translation.",
                    query,
                    "count",
                    f"counts/pass{pass_number}/{schedule_id}.json",
                    schedule_id,
                )
            )
    for schedule_id in CHANGED_IDS:
        query = SCHEDULE[schedule_id]
        events.append(
            event(
                f"records-{schedule_id}",
                "Capture every full source record through the adapter's strict two-pass contract for the changed partition.",
                query,
                "complete",
                f"records/{schedule_id}.json",
                schedule_id,
            )
        )

    lengths = {key: len(value) for key, value in SCHEDULE.items()}
    if max(lengths.values()) >= QUERY_LIMIT:
        raise RuntimeError("A complete ATAI query reaches the validated source limit.")

    return {
        "schema_version": "atai-pilot-007-event-plan/v1",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "platform": "ProQuest",
        "pilot": "007",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test the direct ATAI translation of all nine post-proximity partitions, "
            "repeat every source total, and capture complete records for the four changed partitions."
        ),
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "status": "labelled pilot window, not the unset common review cutoff",
            "basis": "Publication date",
            "inclusive": "both",
        },
        "controls": {
            "database": SOURCE,
            "language": "LA(English)",
            "publication_type": None,
            "peer_reviewed": False,
            "full_text": False,
            "access": False,
            "wildcard": False,
            "proximity": False,
            "spelling_variants": False,
            "form_variants": False,
            "show_expansions": False,
            "sort": "DateAsc",
            "screenshots": "required automatic search-page and results-page PNGs for every event",
        },
        "translation": {
            "literal": "one straight double-quoted literal",
            "ordinary_atom": "(NOFT(quoted literal) OR IF.EXACT(quoted literal))",
            "ordinary_block": "ordinary atoms joined by explicit uppercase OR",
            "compound_block": "the protocol-declared nested AND/OR expression with full parentheses",
            "partition": "protocol factors joined by explicit uppercase AND",
            "blocks": {
                "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
                "G_structure": "G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)",
                "C1": "C1_fixed OR G_DSL",
                "BT2": "P AND M_B AND T_precise",
            },
            "term_counts": TERM_COUNTS,
            "query_lengths": lengths,
            "query_sha256": {key: digest(value) for key, value in SCHEDULE.items()},
            "validated_character_limit": QUERY_LIMIT,
            "no_pair_expansion": True,
        },
        "changed_partitions": list(CHANGED_IDS),
        "acceptance_checks": [
            "Every complete expression stays below 50,000 characters and contains no proximity or wildcard syntax.",
            "All nine expressions receive exact source query and control readback in both count passes.",
            "The two source totals agree for every partition.",
            "Each changed partition passes strict complete two-pass full-record capture.",
            "Every source event saves both required full-page screenshots with hashes and dimensions.",
            "Every changed-partition record has a stable numeric ATAI document ID.",
            "No result-driven source narrowing is introduced.",
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
