#!/usr/bin/env python3
"""Write the prospective Scopus Pilot 003 plan without running a search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from queries import ALL_PARTITIONS, MAIN_PARTITIONS, PSR_PARTITIONS, full_query, membership_audit


SCHEMA_VERSION = "slr1-scopus-pilot003-plan/v1"
DIAGNOSTIC_CUTOFF = "2026-08-29"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def event(partition: str, namespace: str) -> dict[str, object]:
    query = full_query(partition)
    main = namespace == "main"
    return {
        "event_id": f"pilot-{namespace}-{partition}-scopus-003",
        "partition_id": partition,
        "review_namespace": namespace,
        "event_kind": "pilot",
        "query": query,
        "query_sha256": digest(query),
        "query_character_count": len(query),
        "source": "Scopus",
        "source_scope": "Documents",
        "sort": "Date (oldest)",
        "year_control": {
            "start": 2011 if main else None,
            "end": 2026,
            "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
            "cutoff_year_screening": "Records dated in 2026 remain date-unresolved until screened against 2026-08-29.",
        },
        "language": "English visible facet" if main else "not applied",
        "document_type": "not applied",
        "subject_area": "not applied",
        "access": "not applied",
        "controlled_vocabulary": "No Scopus searchable thesaurus or expansion control; no supplement is preselected.",
        "full_abstracts": "native Show all abstracts; retain blank only when Scopus exposes no native abstract",
    }


def build() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "pilot_id": "003",
        "source": "Scopus",
        "purpose": "Diagnostic pilot only; no artifact is a final search.",
        "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
        "literal_translation": True,
        "wildcard_policy": {
            "accepted": False,
            "reason": "Pilot 002's 10-wildcard A1 proposal has no complete stable-ID literal superset comparison.",
            "future_requirement": "Validate every wildcard independently by partition with complete stable publication-ID superset evidence.",
        },
        "membership": membership_audit(),
        "events": [
            *(event(partition, "main") for partition in MAIN_PARTITIONS),
            *(event(partition, "prior_secondary_reviews") for partition in PSR_PARTITIONS),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_path
    if output.exists() or output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
