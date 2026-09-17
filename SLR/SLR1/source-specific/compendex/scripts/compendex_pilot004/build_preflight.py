#!/usr/bin/env python3

"""Build the post-proximity Compendex Pilot 004 query preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import queries


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build() -> dict[str, object]:
    schedule = {
        partition_id: {
            "query": query,
            "query_sha256": digest(query),
            "query_characters": len(query),
            "has_proximity": "NEAR" in query.upper(),
            "has_wildcard": "*" in query or "?" in query,
        }
        for partition_id, query in queries.SOURCE_SCHEDULE.items()
    }
    cells = {
        cell_id: {
            "query": query,
            "query_sha256": digest(query),
            "query_characters": len(query),
            "has_proximity": "NEAR" in query.upper(),
            "has_wildcard": "*" in query or "?" in query,
        }
        for cell_id, query in queries.VALUE_CELLS.items()
    }
    if any(item["has_proximity"] or item["has_wildcard"] for item in schedule.values()):
        raise RuntimeError("The post-proximity schedule contains a proximity or wildcard expression")
    if any(item["has_proximity"] or item["has_wildcard"] for item in cells.values()):
        raise RuntimeError("A controlled-vocabulary value cell contains proximity or wildcard syntax")
    return {
        "schema_version": "compendex-controlled-vocabulary-preflight/v1",
        "source": "Compendex",
        "platform": "Engineering Village",
        "pilot": "004",
        "status": "complete",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "protocol_change": {
            "commit_subject": "Remove proximity operator",
            "changed_partitions": list(queries.CHANGED_BY_PROTOCOL_COMMIT),
            "B1_semantic_factors": "P AND M_H",
            "B1_change_state": "unchanged_by_protocol_commit",
            "historical_pilot_003_boundary": (
                "Pilot 003 used the superseded proximity schedule. Its B1 native RIS may be "
                "used only for record-level assignment evidence because B1 remained P AND M_H."
            ),
        },
        "term_snapshot": {
            "module": "SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot007/queries.py",
            "sha256": queries.TERM_SNAPSHOT_SHA256,
            "term_counts": queries.TERM_COUNTS,
        },
        "source_translation": {
            "literal": '("literal" WN ALL)',
            "language": queries.LANGUAGE_CLAUSE,
            "autostemming": "off",
            "wildcards": "none",
            "proximity": "none",
            "compound_definitions": {
                "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
                "G_structure": (
                    "G_structure_fixed OR G_product_exact OR G_variation OR "
                    "(G_product AND M_B)"
                ),
                "C1": "C1_fixed OR G_DSL",
                "BT2": "P AND M_B AND T_precise",
            },
        },
        "schedule": schedule,
        "controlled_vocabulary_candidate": {
            "P": queries.P_CONTROLLED,
            "M_H": queries.M_H_CONTROLLED,
            "combination_rule": (
                "Each controlled construction is OR-unioned with its complete normative "
                "free-text block. Free text remains mandatory."
            ),
            "major_topic": "not requested",
            "explosion": "not requested",
            "focus": "not requested",
        },
        "B1": {
            "literal_query": queries.B1_LITERAL,
            "literal_query_sha256": digest(queries.B1_LITERAL),
            "augmented_query": queries.B1_AUGMENTED,
            "augmented_query_sha256": digest(queries.B1_AUGMENTED),
            "candidate_only_decomposition": [
                "B1-MH-candidate-only",
                "B1-P-candidate-only",
            ],
            "decomposition_is_lossless": True,
            "decomposition_truth_table_cases": 16,
            "decomposition_reason": (
                "Any augmented record outside literal B1 either lacks free-text M_H and "
                "enters the M_H route, or has free-text M_H, lacks free-text P, and enters "
                "the P route."
            ),
        },
        "value_cells": cells,
        "selected_known_record_ids": [
            accession for accession, _title in queries.SELECTED_KNOWN_RECORDS
        ],
        "validation": {
            "schedule_ids": list(queries.SCHEDULE_IDS),
            "all_schedule_queries_without_proximity": True,
            "all_schedule_queries_without_wildcards": True,
            "all_value_queries_without_proximity": True,
            "all_value_queries_without_wildcards": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
