#!/usr/bin/env python3
"""Build Pilot 003 stable-publication-ID union receipts from completed artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from queries import MAIN_PARTITIONS, PSR_PARTITIONS


SCHEMA = "slr1-scopus-pilot003-stable-id-unions/v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("source") != "Scopus":
        raise ValueError(f"Not a Scopus artifact: {path}")
    return value


def successful_records(path: Path) -> list[dict[str, Any]]:
    value = load(path)
    metadata = value.get("output_metadata", {})
    if metadata.get("retrieval_complete") is not True:
        raise ValueError(f"Not complete: {path}")
    records = value.get("results")
    if not isinstance(records, list) or len(records) != value.get("total"):
        raise ValueError(f"Unreconciled records: {path}")
    for record in records:
        if not isinstance(record, dict) or not str(record.get("paperId", "")).startswith("SCOPUS-PUBLICATION:"):
            raise ValueError(f"Missing publication ID: {path}")
    return records


def record_projection(record: dict[str, Any], partition: str) -> dict[str, Any]:
    return {
        "paper_id": record["paperId"],
        "doi": record.get("doi", ""),
        "title": record.get("title", ""),
        "year": record.get("year"),
        "publication_title": record.get("publicationTitle", ""),
        "document_type_observed": record.get("documentType", ""),
        "discovery_partitions": [partition],
        "abstract": None,
        "abstract_status": "not_collected_in_complete_ID_capture",
    }


def merge_records(events: dict[str, Path], abstract_followups: list[Path]) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    merged: dict[str, dict[str, Any]] = {}
    event_counts: dict[str, dict[str, int]] = {}
    for partition, path in events.items():
        rows = successful_records(path)
        event_counts[partition] = {"source_total": len(rows), "unique_publication_ids": len({row["paperId"] for row in rows})}
        for row in rows:
            key = row["paperId"]
            candidate = record_projection(row, partition)
            existing = merged.get(key)
            if existing is None:
                merged[key] = candidate
            else:
                existing["discovery_partitions"].append(partition)
                for field in ("doi", "title", "year", "publication_title", "document_type_observed"):
                    if not existing.get(field) and candidate.get(field):
                        existing[field] = candidate[field]
    for path in abstract_followups:
        for row in successful_records(path):
            abstract = row.get("abstract")
            if row["paperId"] in merged and isinstance(abstract, str) and abstract:
                merged[row["paperId"]]["abstract"] = abstract
                merged[row["paperId"]]["abstract_status"] = "native_EID_or_title_follow_up"
    for row in merged.values():
        row["discovery_partitions"].sort()
    return sorted(merged.values(), key=lambda row: row["paper_id"]), event_counts


def artifact_rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def completed_artifacts(directory: Path) -> list[Path]:
    """Return only follow-up JSONs that independently completed."""
    result = []
    for path in sorted(directory.glob("batch-*.json")):
        value = load(path)
        if value.get("output_metadata", {}).get("retrieval_complete") is True:
            result.append(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True, type=Path)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    root = args.pilot_root
    if args.output_path.exists() or args.output_path.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output_path}")

    main_events = {
        "A1": root / "searches/main/strict-ids/A1.json",
        "A2": root / "searches/main/strict-ids/A2.json",
        "A3": root / "searches/main/strict-ids/A3.json",
        "B1": root / "searches/main/strict-ids-B200/B1.json",
        "B2": root / "searches/main/strict-ids-B200/B2.json",
        "BG1": root / "searches/main/strict-ids/BG1.json",
        "BG2": root / "searches/main/strict-ids/BG2.json",
        "BC1": root / "searches/main/strict-ids/BC1.json",
        "BT2": root / "searches/main/strict-ids/BT2.json",
    }
    abstract_followup_paths = [
        root / "searches/diagnostics/focused-abstract-follow-up.json",
        root / "searches/diagnostics/EID-abstract-follow-up-known-item.json",
        root / "searches/diagnostics/EID-two-record-abstract-follow-up.json",
        root / "searches/diagnostics/EID-six-record-abstract-follow-up.json",
        *completed_artifacts(root / "searches/main/abstract-follow-up-all"),
    ]
    main_records, main_counts = merge_records(main_events, abstract_followup_paths)

    psr_complete_events = {
        "PSR1": root / "searches/psr/strict-ids/PSR1.json",
        "PSR3": root / "searches/psr/strict-ids/PSR3.json",
    }
    psr_abstract_followup_paths = completed_artifacts(
        root / "searches/psr/abstract-follow-up-complete-subunion"
    )
    psr_records, psr_counts = merge_records(psr_complete_events, psr_abstract_followup_paths)
    psr_incomplete = {
        "PSR2": {
            "status": "incomplete_no_union",
            "reason": "The complete full-expression run and later lossless-cell recovery each retain non-mergeable null-total failures; no partial prefix is called a union.",
            "full_event": artifact_rel(root, root / "searches/psr/strict-ids/PSR2.json"),
            "cell_attempt": artifact_rel(root, root / "searches/psr/strict-cells-2500-PSR2/run-receipt.json"),
        },
        "PSR4": {
            "status": "incomplete_no_union",
            "reason": "The complete full-expression run and lossless-cell attempts retain non-mergeable null-total failures; no partial prefix is called a union.",
            "full_event": artifact_rel(root, root / "searches/psr/strict-ids/PSR4.json"),
            "cell_attempt": artifact_rel(root, root / "searches/psr/strict-cells-3000/run-receipt.json"),
        },
    }

    def year_uncertain(rows: list[dict[str, Any]]) -> int:
        return sum(row.get("year") == 2026 for row in rows)

    outcome_rows = [
        {
            "partition_id": partition,
            "route": "main",
            "status": "complete_stable_id_union",
            "source_total": main_counts[partition]["source_total"],
            "unique_publication_ids": main_counts[partition]["unique_publication_ids"],
            "artifact": artifact_rel(root, path),
        }
        for partition, path in main_events.items()
    ] + [
        {
            "partition_id": partition,
            "route": "prior_secondary_reviews",
            "status": "complete_stable_id_union",
            "source_total": psr_counts[partition]["source_total"],
            "unique_publication_ids": psr_counts[partition]["unique_publication_ids"],
            "artifact": artifact_rel(root, path),
        }
        for partition, path in psr_complete_events.items()
    ] + [
        {"partition_id": partition, "route": "prior_secondary_reviews", **details}
        for partition, details in psr_incomplete.items()
    ]
    output = {
        "schema_version": SCHEMA,
        "pilot_id": "003",
        "source": "Scopus",
        "pilot_only": True,
        "identity": "exact Scopus publication ID; no DOI/title substitution in these source unions",
        "main": {
            "partitions": list(MAIN_PARTITIONS),
            "complete": True,
            "event_record_total": sum(item["source_total"] for item in main_counts.values()),
            "stable_publication_id_union_total": len(main_records),
            "event_overlap_total": sum(item["source_total"] for item in main_counts.values()) - len(main_records),
            "cutoff_year_records_requiring_screening": year_uncertain(main_records),
            "full_abstracts": {
                "native_follow_up_records": sum(row["abstract"] is not None for row in main_records),
                "unresolved_after_batch_native_expansion_failures": sum(row["abstract"] is None for row in main_records),
                "successful_follow_up_artifacts": [artifact_rel(root, path) for path in abstract_followup_paths],
                "failed_follow_up_register": "searches/main/abstract-follow-up-all/abstract-follow-up-receipt.json",
                "note": "The complete ID ledgers used --skip-full-abstracts after the repaired page-level native expansion still failed. EID-constrained native follow-up recovered abstracts only for batches whose returned stable-ID set exactly matched the requested union IDs. Remaining abstracts are not silently represented as unavailable.",
            },
            "events": {partition: artifact_rel(root, path) for partition, path in main_events.items()},
            "event_counts": main_counts,
            "records": main_records,
        },
        "prior_secondary_reviews": {
            "partitions": list(PSR_PARTITIONS),
            "complete": False,
            "complete_subunion_partitions": list(psr_complete_events),
            "complete_subunion_total": len(psr_records),
            "cutoff_year_records_requiring_screening": year_uncertain(psr_records),
            "events": {partition: artifact_rel(root, path) for partition, path in psr_complete_events.items()},
            "event_counts": psr_counts,
            "full_abstracts": {
                "native_follow_up_records": sum(row["abstract"] is not None for row in psr_records),
                "unresolved_after_batch_native_expansion_failures": sum(row["abstract"] is None for row in psr_records),
                "successful_follow_up_artifacts": [artifact_rel(root, path) for path in psr_abstract_followup_paths],
                "failed_follow_up_register": "searches/psr/abstract-follow-up-complete-subunion/abstract-follow-up-receipt.json",
            },
            "records": psr_records,
            "incomplete_partitions": psr_incomplete,
        },
        "outcomes": sorted(outcome_rows, key=lambda row: (*({"main": 0, "prior_secondary_reviews": 1}[row["route"]],), row["partition_id"])),
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
