#!/usr/bin/env python3
"""Build the predeclared IEEE Xplore Pilot 005 event plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from queries import CHANGED_IDS, PROTOCOL_COMMIT, SCHEDULE, SCHEDULE_IDS, TERM_COUNTS

SOURCE = "IEEE Xplore"
SOURCE_ID = "ieee_xplore"
YEAR_START = 2011
YEAR_END = 2026
DIAGNOSTIC_CUTOFF = "2026-08-29"
ADAPTER_QUERY_LIMIT = 50_000


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
        "year_start": YEAR_START,
        "year_end": YEAR_END,
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
                    f"Native-year source-total pass {pass_number} for the complete direct {schedule_id} translation.",
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
                "Capture the changed partition through the adapter's strict two-pass source-exhaustive contract.",
                query,
                "complete",
                f"records/{schedule_id}.json",
                schedule_id,
            )
        )

    lengths = {key: len(value) for key, value in SCHEDULE.items()}
    if max(lengths.values()) >= ADAPTER_QUERY_LIMIT:
        raise RuntimeError("A complete IEEE query reaches the adapter input limit.")

    return {
        "schema_version": "ieee-xplore-pilot-005-event-plan/v1",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "platform": "IEEE Xplore",
        "pilot": "005",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test one direct IEEE All Metadata expression for every post-proximity partition, "
            "repeat every native-year total, and strictly capture the four changed partitions."
        ),
        "date_window": {
            "source_control": "Publication Year",
            "year_start": YEAR_START,
            "year_end": YEAR_END,
            "source_token": f"{YEAR_START}_{YEAR_END}_Year",
            "inclusive": True,
            "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
            "cutoff_status": (
                "Recorded separately. The pilot uses the source's year-precision control and "
                "does not relabel it as an exact day window."
            ),
        },
        "controls": {
            "scope": "Documents",
            "access": "All Results",
            "language": None,
            "publication_type": None,
            "date_added": None,
            "controlled_vocabulary": None,
            "wildcard": False,
            "proximity": False,
            "sort": "Oldest",
            "page_size": 100,
            "strict_passes": 2,
            "full_abstracts": True,
            "screenshots": "The IEEE adapter defines no automatic screenshot output contract.",
        },
        "translation": {
            "literal": "one straight double-quoted literal",
            "ordinary_atom": "(\"All Metadata\":\"literal\")",
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
            "adapter_input_character_limit": ADAPTER_QUERY_LIMIT,
            "no_pair_expansion": True,
            "source_cells_per_partition": 1,
        },
        "changed_partitions": list(CHANGED_IDS),
        "acceptance_checks": [
            "Every complete expression stays below 50,000 characters and contains no proximity or wildcard syntax.",
            "Each partition is submitted as one direct source expression without result-driven splitting.",
            "All nine expressions receive exact source query and control readback in both count passes.",
            "The two source totals agree for every partition.",
            "Each changed partition passes strict complete two-pass ordered Article Number reconciliation.",
            "Every successful or failed adapter artifact retains its matching IEEE commit marker.",
            "No language, type, access, Date Added, wildcard, or controlled-vocabulary restriction is introduced.",
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
        existing = json.loads(args.output.read_text())
        if existing != payload:
            raise FileExistsError(f"Refusing to overwrite nonidentical plan {args.output}")
        return 0
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
