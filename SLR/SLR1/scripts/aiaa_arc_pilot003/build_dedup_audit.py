#!/usr/bin/env python3
"""Reconcile rendered ARC manifestation IDs to DOI-first sampled-prefix identities."""

from __future__ import annotations

import argparse
import json

from run_fielded_count import write_full_json
from run_stage1 import SEARCH_DIR


def canonical_doi(value: str) -> str:
    """Keep the DOI before ARC's virtual-collection manifestation suffix."""
    return value.strip().casefold().split("@", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True, choices=("A2", "BT2"))
    args = parser.parse_args()
    prefix_path = SEARCH_DIR / f"{args.schedule}-sampled-prefix-preview.json"
    recheck_suffix = "recheck2" if args.schedule == "A2" else "recheck"
    recheck_path = SEARCH_DIR / f"{args.schedule}-sampled-prefix-page-metadata-{recheck_suffix}.json"
    output_path = SEARCH_DIR / f"{args.schedule}-sampled-prefix-doi-dedup-audit.json"
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite {output_path}")
    prefix = json.loads(prefix_path.read_text())
    recheck = json.loads(recheck_path.read_text())
    page_by_manifestation = {record["doi"]: record for record in recheck["records"]}
    first_by_doi = {}
    duplicate_events = []
    source_events = 0
    for run in prefix["source_runs"]:
        for record in run["records"]:
            source_events += 1
            manifestation = record.get("doi")
            if not isinstance(manifestation, str) or not manifestation:
                continue
            doi = canonical_doi(manifestation)
            event = {
                "doi": doi,
                "source_manifestation_id": manifestation,
                "source_cell": run["cell_id"],
                "source_rank": record.get("rank"),
                "title": record.get("title"),
                "url": record.get("url"),
            }
            if doi in first_by_doi:
                duplicate_events.append({"duplicate_of_doi": doi, **event})
                continue
            page_record = page_by_manifestation.get(manifestation)
            first_by_doi[doi] = {
                **event,
                "page_metadata": page_record.get("page_metadata") if page_record else {"status": "metadata_unavailable"},
                "diagnostic": page_record.get("diagnostic") if page_record else {"status": "metadata_unavailable"},
            }
    payload = {
        "schema_version": "aiaa-arc-doi-first-sampled-prefix-audit/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "003",
        "schedule_id": args.schedule,
        "do_not_merge": True,
        "input_prefix_artifact": prefix_path.name,
        "input_page_metadata_artifact": recheck_path.name,
        "identity_rule": "normalized DOI before a source virtual-collection @ manifestation suffix; raw ARC manifestation ID remains a discovery event.",
        "source_order_contract": {
            "cell_order": "configured field-assignment order in the source-prefix artifact",
            "within_cell_order": "ARC rendered Date/Earliest order",
            "stable_identifier": "DOI-bearing ARC checkbox/source manifestation ID, reconciled DOI-first here",
            "pass_verification": "sample_prefix.py invoked the ARC adapter with passes=2; the adapter fails closed if its ordered DOI sequence changes between passes",
        },
        "source_cell_order": [run["cell_id"] for run in prefix["source_runs"]],
        "source_events_seen": source_events,
        "unique_doi_count": len(first_by_doi),
        "sampled_records": list(first_by_doi.values()),
        "duplicate_manifestation_events": duplicate_events,
        "limitations": [
            "Each source cell was previewed in ARC source order; this is a non-mergeable diagnostic union, not a final source run.",
            "The DOI-first audit removes a virtual-collection manifestation but does not classify any record's scientific eligibility.",
        ],
    }
    write_full_json(output_path, payload)
    print(json.dumps({"saved": str(output_path), "source_events": source_events, "unique_dois": len(first_by_doi), "manifestation_duplicates": len(duplicate_events)}, indent=2))


if __name__ == "__main__":
    main()
