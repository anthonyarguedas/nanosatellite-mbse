#!/usr/bin/env python3
"""Build the ESA Indico Pilot 007 fixed-ledger query schedule."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import queries
from common import (
    SEARCH_ROOT,
    SOURCE_NAME,
    compact_corpus_binding,
    file_sha256,
    load_validated_corpus,
    relative_to_repository,
    write_new_json,
)

SCHEMA = "esa-indico-pilot007-schedule-plan/v1"
DEFAULT_OUTPUT = SEARCH_ROOT / "schedule-plan.json"
SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_AFFECTING_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "common.py",
    SCRIPT_DIR / "build_plan.py",
    SCRIPT_DIR / "run_pilot.py",
)


def build() -> dict[str, Any]:
    adapter, source, ledger, binding = load_validated_corpus()
    if source.get("requested_query") != queries.SCHEDULE["A1"]:
        raise RuntimeError(
            "Pilot 007 A1 does not reproduce the Pilot 006 anchor expression"
        )
    if (
        source.get("total") != 0
        or ledger.get("matches", {}).get("matched_record_count") != 0
    ):
        raise RuntimeError("Pilot 006 A1 anchor is no longer a verified zero")
    events = [
        {
            "event_id": f"pilot-007-{partition_id}",
            "partition_id": partition_id,
            "semantic_form": queries.SEMANTIC_FORMS[partition_id],
            "source_construction": queries.SOURCE_CONSTRUCTIONS[partition_id],
            "query": queries.SCHEDULE[partition_id],
            "query_characters": queries.QUERY_CHARACTER_COUNTS[partition_id],
            "query_sha256": queries.QUERY_SHA256[partition_id],
            "output": f"searches/{partition_id}.json",
            "maximum_retained_matches": 100,
            "do_not_merge": True,
        }
        for partition_id in queries.SCHEDULE_IDS
    ]
    return {
        "schema_version": SCHEMA,
        "source": SOURCE_NAME,
        "pilot": "007",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Execute all nine current direct-query partitions over the complete, "
            "marker-bound Pilot 006 category-0 metadata ledger with the exact adapter "
            "v8 local matcher."
        ),
        "protocol": {
            "strategy_reference": (
                "SLR/SLR1/protocol-discovery-and-appraisal.md#direct-query-schedule"
            ),
            "term_snapshot_commit": queries.PROTOCOL_COMMIT,
            "term_snapshot": relative_to_repository(queries.TERM_SNAPSHOT_PATH),
            "term_snapshot_sha256": queries.EXPECTED_TERM_SNAPSHOT_SHA256,
            "term_counts": queries.TERM_COUNTS,
            "schedule_ids": list(queries.SCHEDULE_IDS),
            "historical_pair_expansion_replaced_for": list(
                queries.CHANGED_FROM_HISTORICAL_PAIR_SCHEDULE
            ),
        },
        "source_corpus": compact_corpus_binding(binding),
        "execution_method": {
            "kind": "read_only_matching_over_validated_complete_metadata_ledger",
            "source_requests": 0,
            "browser_requests": 0,
            "attachment_body_requests": 0,
            "matcher": adapter.LOCAL_MATCHER_SCHEMA,
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "adapter_path": "~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py",
            "adapter_sha256": file_sha256(Path(adapter.__file__)),
            "record_order": "root snapshot order, then native event export order",
            "one_bounded_match_pass_per_partition": True,
        },
        "source_affecting_scripts": {
            relative_to_repository(path): file_sha256(path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "translation": {
            "literal": "one straight-double-quoted lexical literal",
            "ordinary_block": "source OR across every declared literal",
            "compound_blocks": "current declared AND and OR definitions",
            "boolean": "uppercase AND and OR with explicit parentheses",
            "wildcard": False,
            "proximity": False,
            "pair_expansion": False,
            "controlled_vocabulary_supplement": False,
            "fields_by_record_type": {
                "event": ["title", "description", "keywords"],
                "contribution": ["title", "description", "keywords"],
                "subcontribution": ["title", "description", "keywords"],
                "attachment": ["title", "filename", "description"],
            },
            "phrase_and_boolean_scope": (
                "Phrases stay within one declared field. Boolean factors apply within "
                "one normalized record."
            ),
        },
        "controls": {
            "category_id": 0,
            "category_scope": "selected category and descendants",
            "date_filter": None,
            "date_handling": (
                "No source or local match date restriction. Apply the evidence window "
                "during downstream screening."
            ),
            "language_filter": None,
            "publication_type_filter": None,
            "access_filter": None,
            "full_text_filter": None,
            "result_types": ["events", "contributions", "materials"],
            "notes_and_categories_covered": False,
            "sort": "preserved complete-ledger source order",
        },
        "acceptance_checks": [
            "The Pilot 006 compact artifact, terminal marker, and full ledger pass the shared ESA v8 gate.",
            "Both root snapshots retain the same ordered 440 event IDs.",
            "All 440 event-export witnesses and all 16,517 normalized records reconcile.",
            "The current adapter file hash equals the source artifact adapter hash.",
            "A1 exactly reproduces the Pilot 006 expression and zero-match result.",
            "Every current no-proximity expression parses and runs over every ledger record.",
            "Every match keeps its type-prefixed stable identity and source order.",
            "No partition exceeds 100 matches.",
            "No source, browser, attachment, or full-text request occurs.",
        ],
        "event_count": len(events),
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    plan = build()
    write_new_json(args.output, plan)
    print(f"Wrote {args.output} with {len(plan['events'])} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
