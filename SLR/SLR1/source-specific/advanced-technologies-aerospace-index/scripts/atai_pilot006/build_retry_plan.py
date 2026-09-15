#!/usr/bin/env python3

"""Build the bounded Pilot 006 retry plan after the retained first-run failures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--failed-run-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    original = json.loads(args.event_plan.read_text())
    receipt = json.loads(args.failed_run_receipt.read_text())
    if receipt.get("status") != "stopped_on_source_or_adapter_failure":
        raise RuntimeError("The original run receipt does not preserve a stopped run.")
    outcomes = receipt.get("outcomes", [])
    if not outcomes or outcomes[-1].get("event_id") != "language-schedule-union-unfiltered":
        raise RuntimeError("The retained stop was not the predeclared language union.")
    language_events = {
        event["event_id"]: event
        for event in original["events"]
        if event["event_id"].startswith("language-schedule-union-")
    }
    union_query = language_events["language-schedule-union-unfiltered"]["query"]

    def cell(
        event_id: str,
        purpose: str,
        query: str,
        *,
        language: str | None = None,
        date_start: str | None = "2011-01-01",
        date_end: str | None = "2026-08-29",
        count_only: bool = False,
    ) -> dict:
        return {
            "event_id": event_id,
            "purpose": purpose,
            "query": query,
            "query_sha256": digest(query),
            "language": language,
            "date_start": date_start,
            "date_end": date_end,
            "require_complete": not count_only,
            "count_only": count_only,
            "do_not_merge": True,
            "output": f"retry1/{event_id}.json",
        }

    events = [
        cell(
            "field-index-explicit-no-date",
            "Repeat the documented indexed-keyword known item without the review date window.",
            'AN(2438984228) AND IF.EXACT("Aerospace engineering")',
            date_start=None,
            date_end=None,
        ),
        cell(
            "field-index-noft-no-date",
            "Repeat the matching NOFT known item without the review date window.",
            'AN(2438984228) AND NOFT("Aerospace engineering")',
            date_start=None,
            date_end=None,
        ),
        cell(
            "language-union-unfiltered-count-pass1",
            "First exact source-total pass for the unfiltered complete schedule union.",
            union_query,
            count_only=True,
        ),
        cell(
            "language-union-english-count-pass1",
            "First exact source-total pass for the English-restricted complete schedule union.",
            union_query,
            language="English",
            count_only=True,
        ),
        cell(
            "language-union-unfiltered-count-pass2",
            "Second exact source-total pass for the unfiltered complete schedule union.",
            union_query,
            count_only=True,
        ),
        cell(
            "language-union-english-count-pass2",
            "Second exact source-total pass for the English-restricted complete schedule union.",
            union_query,
            language="English",
            count_only=True,
        ),
    ]
    retry = {
        "schema_version": "atai-pilot-006-retry-plan/v1",
        "source": original["source"],
        "source_id": original["source_id"],
        "platform": original["platform"],
        "pilot": "006",
        "attempt": "retry1",
        "do_not_merge": True,
        "original_event_plan": str(args.event_plan),
        "retained_failed_run_receipt": str(args.failed_run_receipt),
        "repair_boundaries": [
            "The indexed-keyword known item is repeated without a date restriction because the first zero pair was jointly excluded by the date window.",
            "The failed full-record language union remains immutable.",
            "Language recall uses two repeated exact count-only source totals. The English query is the identical union plus AND LA(English), making it a source-read-back subset of the unfiltered query.",
            "Equal unfiltered and English totals in both passes prove bounded set equality under the source Boolean restriction. Any unequal total leaves language recall unresolved.",
        ],
        "events": events,
    }
    args.output.write_text(json.dumps(retry, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
