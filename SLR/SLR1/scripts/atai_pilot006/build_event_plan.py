#!/usr/bin/env python3

"""Build the predeclared ATAI Pilot 006 field, pair, and language plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE = "Advanced Technologies & Aerospace Index"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def event(event_id: str, purpose: str, query: str, *, language: str | None = None) -> dict:
    return {
        "event_id": event_id,
        "purpose": purpose,
        "query": query,
        "query_sha256": digest(query),
        "language": language,
        "date_start": DATE_START,
        "date_end": DATE_END,
        "require_complete": True,
        "count_only": False,
        "do_not_merge": True,
        "output": f"cells/{event_id}.json",
    }


def build(pilot003_plan: Path) -> dict:
    prior = json.loads(pilot003_plan.read_text())
    queries = [entry["query"] for entry in prior.get("events", [])]
    if len(queries) != 9:
        raise RuntimeError("Pilot 003 did not expose exactly nine schedule queries.")
    schedule_union = "(" + " OR ".join(f"({query})" for query in queries) + ")"
    if len(schedule_union) > 50_000:
        raise RuntimeError("The complete schedule union exceeds ATAI's validated query length.")

    events = [
        event(
            "field-title-explicit",
            "Known item is retrieved through the explicit title field.",
            'AN(3371247439) AND TI("Integrated Modeling and Simulation Methodology")',
        ),
        event(
            "field-title-noft",
            "The same known title phrase is retrieved through NOFT.",
            'AN(3371247439) AND NOFT("Integrated Modeling and Simulation Methodology")',
        ),
        event(
            "field-abstract-explicit",
            "Known item is retrieved through the explicit abstract field.",
            'AN(3097792411) AND AB("transient and steady-state responses")',
        ),
        event(
            "field-abstract-noft",
            "The same known abstract phrase is retrieved through NOFT.",
            'AN(3097792411) AND NOFT("transient and steady-state responses")',
        ),
        event(
            "field-subject-explicit",
            "Known item is retrieved through an assigned exact subject descriptor.",
            'AN(3181339955) AND MAINSUBJECT.EXACT("Moon")',
        ),
        event(
            "field-subject-noft",
            "The same assigned subject descriptor is retrieved through NOFT.",
            'AN(3181339955) AND NOFT("Moon")',
        ),
        event(
            "field-index-explicit",
            "Known item is retrieved through the explicit identifier-keyword field.",
            'AN(2438984228) AND IF.EXACT("Aerospace engineering")',
        ),
        event(
            "field-index-noft",
            "The same indexed keyword is retrieved through NOFT.",
            'AN(2438984228) AND NOFT("Aerospace engineering")',
        ),
        event(
            "pair-abstract-explicit",
            "Two source-located pair-positive records are retrieved through abstract NEAR/5.",
            '((AN(1825532815) OR AN(2728408177)) AND AB("adapted" NEAR/5 "model"))',
        ),
        event(
            "pair-noft",
            "The same pair-positive records are retrieved through NOFT NEAR/5.",
            '((AN(1825532815) OR AN(2728408177)) AND NOFT("adapted" NEAR/5 "model"))',
        ),
        event(
            "pair-cross-field-negative",
            "A title or abstract marker and a separate assigned subject marker must not form one NOFT pair.",
            'AN(3181339955) AND NOFT("BOREALIS" NEAR/5 "Moon")',
        ),
        event(
            "language-schedule-union-unfiltered",
            "Complete nine-partition schedule union without a language restriction.",
            schedule_union,
        ),
        event(
            "language-schedule-union-english",
            "Complete nine-partition schedule union with exact LA(English).",
            schedule_union,
            language="English",
        ),
    ]
    return {
        "schema_version": "atai-pilot-006-event-plan/v1",
        "source": SOURCE,
        "source_id": "proquest_aerospace_index",
        "platform": "ProQuest",
        "pilot": "006",
        "purpose": "Validate bounded protocol-relevant NOFT field coverage, source pair retention, same-field pair behavior, and language-filter recall across the complete schedule union.",
        "do_not_merge": True,
        "source_plan": str(pilot003_plan),
        "controls": {
            "database": SOURCE,
            "date_start": DATE_START,
            "date_end": DATE_END,
            "document_type": None,
            "peer_reviewed": False,
            "full_text": None,
            "access": None,
            "sort": "DateAsc",
            "spelling_variants": False,
            "form_variants": False,
            "show_variants": False,
        },
        "field_coverage_scope": [
            "TI title",
            "AB abstract",
            "MAINSUBJECT controlled subject",
            "IF identifier keyword",
        ],
        "pair_gate": {
            "positive_record_ids": ["1825532815", "2728408177"],
            "pair": ["adapted", "model"],
            "max_intervening_words": 5,
            "cross_field_negative_record_id": "3181339955",
            "cross_field_markers": ["BOREALIS", "Moon"],
        },
        "language_gate": {
            "coverage": "Boolean union of all nine Pilot 003 schedule expressions",
            "union_query_characters": len(schedule_union),
            "union_query_sha256": digest(schedule_union),
            "comparison": [None, "English"],
            "acceptance": "LA(English) is no-loss in this bounded schedule union only if the unfiltered and English stable-ID sets are equal. Any unfiltered-only ID requires language metadata and report-language investigation before acceptance.",
        },
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot003-event-plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = build(args.pilot003_event_plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
