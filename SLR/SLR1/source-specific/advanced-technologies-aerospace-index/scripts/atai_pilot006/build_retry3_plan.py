#!/usr/bin/env python3

"""Build Pilot 006 retry 3 for IF marginal recall and language exclusions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def augment_indexed_keywords(query: str) -> str:
    # Ordinary literal atoms close immediately after their quoted value.
    # Pair atoms contain NEAR/5 inside NOFT and remain unchanged.
    return re.sub(
        r'NOFT\("([^"]+)"\)',
        lambda match: (
            f'(NOFT("{match.group(1)}") OR IF.EXACT("{match.group(1)}"))'
        ),
        query,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot003-plan", type=Path, required=True)
    parser.add_argument("--pilot006-plan", type=Path, required=True)
    parser.add_argument("--retry2-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_plan = json.loads(args.pilot003_plan.read_text())
    pilot006 = json.loads(args.pilot006_plan.read_text())
    retry2 = json.loads(args.retry2_receipt.read_text())
    if retry2.get("status") != "complete":
        raise RuntimeError("Pilot 006 retry 2 is incomplete.")
    source_events = source_plan.get("events", [])
    if len(source_events) != 9:
        raise RuntimeError("Pilot 003 does not expose nine source partitions.")
    union_event = next(
        event
        for event in pilot006["events"]
        if event["event_id"] == "language-schedule-union-unfiltered"
    )
    union_query = union_event["query"]

    def count_cell(event_id: str, purpose: str, query: str) -> dict:
        return {
            "event_id": event_id,
            "purpose": purpose,
            "query": query,
            "query_sha256": digest(query),
            "language": "English",
            "date_start": "2011-01-01",
            "date_end": "2026-08-29",
            "require_complete": False,
            "count_only": True,
            "do_not_merge": True,
            "output": f"retry3/{event_id}.json",
        }

    events = []
    query_lengths = {}
    for pass_number in (1, 2):
        for source_event in source_events:
            partition = source_event["partition_id"]
            literal = source_event["query"]
            augmented = augment_indexed_keywords(literal)
            if len(augmented) > 50_000:
                raise RuntimeError(f"{partition} IF augmentation exceeds source length.")
            query_lengths[partition] = {
                "literal": len(literal),
                "if_augmented": len(augmented),
            }
            events.append(
                count_cell(
                    f"if-{partition}-literal-count-pass{pass_number}",
                    f"Exact count pass {pass_number} for literal {partition} with LA(English).",
                    literal,
                )
            )
            events.append(
                count_cell(
                    f"if-{partition}-augmented-count-pass{pass_number}",
                    f"Exact count pass {pass_number} for NOFT OR IF.EXACT augmented {partition} with LA(English).",
                    augmented,
                )
            )
    for pass_number in (1, 2):
        event_id = f"language-union-not-english-count-pass{pass_number}"
        query = f"({union_query}) NOT LA(English)"
        events.append(
            {
                "event_id": event_id,
                "purpose": f"Exact count pass {pass_number} for records in the complete schedule union outside LA(English).",
                "query": query,
                "query_sha256": digest(query),
                "language": None,
                "date_start": "2011-01-01",
                "date_end": "2026-08-29",
                "require_complete": False,
                "count_only": True,
                "do_not_merge": True,
                "output": f"retry3/{event_id}.json",
            }
        )

    result = {
        "schema_version": "atai-pilot-006-retry3-plan/v1",
        "source": pilot006["source"],
        "source_id": pilot006["source_id"],
        "platform": pilot006["platform"],
        "pilot": "006",
        "attempt": "retry3",
        "do_not_merge": True,
        "pilot003_plan": str(args.pilot003_plan),
        "pilot006_plan": str(args.pilot006_plan),
        "completed_retry2_receipt": str(args.retry2_receipt),
        "observed_triggers": {
            "indexed_keyword_known_item": {
                "IF_exact_total": 1,
                "NOFT_total": 0,
            },
            "language_schedule_union": {
                "unfiltered_total": 52,
                "english_total": 50,
            },
        },
        "if_augmentation": {
            "ordinary_atom_rule": "Replace each ordinary NOFT quoted literal atom with (NOFT literal OR IF.EXACT literal).",
            "pair_atom_rule": "Keep every NOFT NEAR/5 pair unchanged.",
            "query_lengths": query_lengths,
            "acceptance": "An IF supplement has no observed marginal recall only when each augmented partition equals its literal partition in both exact-count passes. Any increase requires stable-ID capture and relevance inspection.",
        },
        "language_exclusion_query": "Complete schedule union NOT LA(English)",
        "events": events,
    }
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
