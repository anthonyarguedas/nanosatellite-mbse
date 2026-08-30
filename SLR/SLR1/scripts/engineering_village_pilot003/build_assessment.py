#!/usr/bin/env python3
"""Reconcile Pilot 003 paired events and investigate source-specific unions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from preflight import (  # type: ignore[import-not-found]
    DEFAULT_OUTPUT as PREFLIGHT_PATH,
    PILOT_DIR,
    SCHEDULE_IDS,
    build_payload,
    raw_query,
)

SEARCH_DIR = PILOT_DIR / "searches"
RECONCILIATION_PATH = SEARCH_DIR / "reconciliation.json"
OVER_100_PATH = SEARCH_DIR / "over-100-investigation.json"
DATABASES = ("compendex", "inspec")
SOURCE_TO_DATABASE = {
    "Compendex (Engineering Village)": "compendex",
    "Inspec (Engineering Village)": "inspec",
}
THRESHOLD = 100


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_doi(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().casefold()
    normalized = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", normalized)
    normalized = normalized.rstrip(". ,;)")
    return normalized or None


def validate_preflight() -> None:
    if load(PREFLIGHT_PATH) != build_payload():
        raise ValueError("Saved preflight differs from current pilot_schedule concepts")


def success_event(partition_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path = SEARCH_DIR / f"{partition_id}.json"
    data = load(path)
    metadata = data.get("output_metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{partition_id}: missing output metadata")
    run = metadata.get("prisma_search_run")
    if not isinstance(run, dict):
        raise ValueError(f"{partition_id}: missing PRISMA source-run receipt")
    strategy = run.get("strategy")
    staged = run.get("staged_counts")
    if not isinstance(strategy, dict) or not isinstance(staged, dict):
        raise ValueError(f"{partition_id}: malformed PRISMA source-run receipt")
    if strategy.get("requested_query") != raw_query(partition_id):
        raise ValueError(f"{partition_id}: requested query differs from preflight")
    if strategy.get("databases") != list(DATABASES):
        raise ValueError(f"{partition_id}: selected database set is not paired")
    if run.get("completion_status") != "complete" or run.get("report_ready") is not True:
        raise ValueError(f"{partition_id}: strict source event is incomplete")
    if staged.get("source_reported_total") != data.get("total") or staged.get("records_exported") != data.get("total"):
        raise ValueError(f"{partition_id}: source total does not reconcile to export")
    records = data.get("results")
    if not isinstance(records, list) or len(records) != data.get("total"):
        raise ValueError(f"{partition_id}: retained records do not reconcile to total")
    expected_by_database = staged.get("records_exported_by_database")
    if not isinstance(expected_by_database, dict) or set(expected_by_database) != set(DATABASES):
        raise ValueError(f"{partition_id}: source receipt lacks separate database counts")

    projections: dict[str, list[dict[str, Any]]] = {database: [] for database in DATABASES}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f"{partition_id}: malformed normalized record")
        database = SOURCE_TO_DATABASE.get(record.get("source"))
        accession = record.get("paperId")
        if database is None or not isinstance(accession, str) or not accession.strip():
            raise ValueError(f"{partition_id}: record lacks database-scoped stable accession")
        projections[database].append(record)
    observed_by_database = {database: len(projections[database]) for database in DATABASES}
    if observed_by_database != expected_by_database or sum(observed_by_database.values()) != data.get("total"):
        raise ValueError(f"{partition_id}: paired projection counts disagree with source receipt")
    for database, projection in projections.items():
        accessions = [record["paperId"].strip() for record in projection]
        if len(accessions) != len(set(accessions)):
            raise ValueError(f"{partition_id}: duplicate {database} accession inside strict event")

    event = {
        "partition_id": partition_id,
        "outcome": "strict_two_pass_success",
        "artifact": path.name,
        "csv_artifact": f"{partition_id}.csv",
        "terminal_marker": f".{partition_id}.json.commit.json",
        "paired_source_total": data["total"],
        "projections": {
            database: {
                "source_total": observed_by_database[database],
                "ordered_accession_ids": [record["paperId"].strip() for record in projections[database]],
                "ordered_accession_ids_sha256": sha256_json(
                    [record["paperId"].strip() for record in projections[database]]
                ),
            }
            for database in DATABASES
        },
        "reconciliation": {
            "source_total_equals_projection_sum": True,
            "source_total_equals_retained_records": True,
            "strict_capture": "fixed adapter accepted its two independent complete accession/RIS passes before marker-gated compact publication",
            "controls": {
                "published": "2011-2026",
                "language_clause": "(English WN LA)",
                "autostemming": "off",
                "sort": "Date (Oldest)",
                "document_type_filter": "not_applied",
                "open_access_filter": "not_applied",
                "controlled_vocabulary_supplement": "not_requested",
                "wildcard": "not_used_or_accepted",
            },
        },
    }
    return event, [
        {"partition_id": partition_id, "database": database, "record": record}
        for database in DATABASES
        for record in projections[database]
    ]


def failure_event(partition_id: str) -> dict[str, Any]:
    path = SEARCH_DIR / f"{partition_id}.NON_MERGEABLE_FAILURE.json"
    data = load(path)
    request = data.get("request")
    execution = data.get("execution")
    if not isinstance(request, dict) or not isinstance(execution, dict):
        raise ValueError(f"{partition_id}: malformed explicit failure receipt")
    if data.get("merge_eligible") is not False or data.get("do_not_merge") is not True:
        raise ValueError(f"{partition_id}: failure receipt is not explicitly non-mergeable")
    if request.get("query_requested_raw") != raw_query(partition_id):
        raise ValueError(f"{partition_id}: failure request differs from preflight")
    if execution.get("source_total") is not None or execution.get("compendex_accession_ids") is not None or execution.get("inspec_accession_ids") is not None or execution.get("native_ris_capture") is not None:
        raise ValueError(f"{partition_id}: failure receipt incorrectly exposes a partial total, accession list, or accepted RIS capture")
    if not isinstance(execution.get("private_partial_capture_disposition"), str):
        raise ValueError(f"{partition_id}: failure receipt does not quarantine any private partial pass")
    return {
        "partition_id": partition_id,
        "outcome": "explicit_strict_null_failure",
        "artifact": path.name,
        "paired_source_total": None,
        "projections": {
            database: {"source_total": None, "ordered_accession_ids": None}
            for database in DATABASES
        },
        "reconciliation": {
            "source_total_equals_projection_sum": None,
            "source_total_equals_retained_records": None,
            "strict_capture": "not available; explicit null failure retained",
            "reason": data.get("failure", {}).get("message"),
        },
    }


def deduplicated_union(records: list[dict[str, Any]], database: str) -> dict[str, Any]:
    first_by_accession: dict[str, dict[str, Any]] = {}
    for item in records:
        if item["database"] != database:
            continue
        record = item["record"]
        accession = record["paperId"].strip()
        existing = first_by_accession.get(accession)
        event = item["partition_id"]
        if existing is None:
            first_by_accession[accession] = {
                "accession_id": accession,
                "title": record.get("title") or "",
                "year": record.get("year"),
                "doi": normalize_doi(record.get("doi")),
                "first_partition": event,
                "partitions": [event],
                "event_occurrences": 1,
            }
        else:
            existing["event_occurrences"] += 1
            if event not in existing["partitions"]:
                existing["partitions"].append(event)
    union = list(first_by_accession.values())
    raw_event_count = sum(1 for item in records if item["database"] == database)
    overlap_profile = Counter(item["event_occurrences"] for item in union)
    return {
        "database": database,
        "raw_successful_event_records": raw_event_count,
        "unique_database_scoped_accessions": len(union),
        "duplicate_event_occurrences_removed": raw_event_count - len(union),
        "overlap_profile_by_partition_event_count": {
            str(key): overlap_profile[key] for key in sorted(overlap_profile)
        },
        "ordered_accession_ids": [item["accession_id"] for item in union],
        "ordered_accession_ids_sha256": sha256_json([item["accession_id"] for item in union]),
        "records": union,
    }


def cross_database_doi_groups(unions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for database, union in unions.items():
        for record in union["records"]:
            doi = record.get("doi")
            if doi:
                grouped[doi][database].append(record["accession_id"])
    return [
        {
            "doi": doi,
            "compendex_accession_ids": values.get("compendex", []),
            "inspec_accession_ids": values.get("inspec", []),
        }
        for doi, values in sorted(grouped.items())
        if set(values) == set(DATABASES)
    ]


def build_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    validate_preflight()
    events = []
    records: list[dict[str, Any]] = []
    failures = []
    for partition_id in SCHEDULE_IDS:
        success_path = SEARCH_DIR / f"{partition_id}.json"
        failure_path = SEARCH_DIR / f"{partition_id}.NON_MERGEABLE_FAILURE.json"
        if success_path.exists() and failure_path.exists():
            raise ValueError(f"{partition_id}: both success and failure artifacts exist")
        if success_path.exists():
            event, event_records = success_event(partition_id)
            events.append(event)
            records.extend(event_records)
        elif failure_path.exists():
            event = failure_event(partition_id)
            events.append(event)
            failures.append(partition_id)
        else:
            raise ValueError(f"{partition_id}: no strict output or explicit null failure")

    unions = {database: deduplicated_union(records, database) for database in DATABASES}
    paired_unique = sum(unions[database]["unique_database_scoped_accessions"] for database in DATABASES)
    reconciliation = {
        "schema_version": "slr1-engineering-village-pilot003-reconciliation/v1",
        "pilot": "003",
        "source": "Compendex and Inspec (Engineering Village)",
        "pilot_only": True,
        "do_not_merge": True,
        "partition_order": list(SCHEDULE_IDS),
        "events": events,
        "source_specific_unions": {
            database: {
                key: value
                for key, value in union.items()
                if key != "records"
            }
            for database, union in unions.items()
        },
        "paired_database_scoped_union": {
            "raw_successful_event_records": sum(
                union["raw_successful_event_records"] for union in unions.values()
            ),
            "unique_database_scoped_accessions": paired_unique,
            "identity_rule": "database name plus stable accession; same-looking identifiers from different indexes are never silently merged",
        },
        "schedule_completeness": {
            "successful_partitions": [event["partition_id"] for event in events if event["outcome"] == "strict_two_pass_success"],
            "explicit_null_failure_partitions": failures,
            "complete_for_final_use": False,
            "reason": "Pilot only; B2 is an explicit strict null failure, and no final search is claimed.",
        },
        "controlled_vocabulary": {
            "status": "not_added",
            "reason": "No candidate descriptor had both an exact normative-block mapping and a known eligible-record assignment in the paired projections. Free text remains intact and un-replaced.",
        },
        "limitations": [
            "Engineering Village exposes year-level Published bounds only; the protocol common evidence cutoff remains TBD, so any 2026 exact-date decision is deferred to screening.",
            "The compact public adapter output retains marker-gated source-run provenance and records; its detailed two-pass native RIS manifests remain in the owner-only rights-aware directory.",
            "Compendex and Inspec totals, accessions, and within-source unions remain separate. Exact DOI collisions across databases are diagnostic only and are not a cross-source merge.",
        ],
    }

    investigations = []
    for database, union in unions.items():
        exceeded = union["unique_database_scoped_accessions"] > THRESHOLD
        investigations.append(
            {
                "database": database,
                "threshold": THRESHOLD,
                "threshold_exceeded": exceeded,
                "raw_successful_event_records": union["raw_successful_event_records"],
                "unique_database_scoped_accessions": union["unique_database_scoped_accessions"],
                "duplicate_event_occurrences_removed": union["duplicate_event_occurrences_removed"],
                "overlap_profile_by_partition_event_count": union["overlap_profile_by_partition_event_count"],
                "record_ledger": union["records"] if exceeded else [],
                "investigation_disposition": (
                    "Every deduplicated stable-accession record is retained with its partition provenance; no post-hoc source narrowing, deletion, or eligibility decision was made."
                    if exceeded
                    else "Below threshold after stable-accession deduplication."
                ),
            }
        )
    over_100 = {
        "schema_version": "slr1-engineering-village-pilot003-over-100-investigation/v1",
        "pilot": "003",
        "source": "Compendex and Inspec (Engineering Village)",
        "pilot_only": True,
        "do_not_merge": True,
        "threshold": THRESHOLD,
        "identity_rule": "within each database: stable accession; databases remain separate",
        "successful_partition_scope": [event["partition_id"] for event in events if event["outcome"] == "strict_two_pass_success"],
        "incomplete_partition_scope": failures,
        "investigations": investigations,
        "cross_database_exact_doi_collision_diagnostic": {
            "group_count": len(cross_database_doi_groups(unions)),
            "groups": cross_database_doi_groups(unions),
            "disposition": "Diagnostic only. Separate Compendex and Inspec projections and counts are preserved; no cross-database record was merged in this pilot.",
        },
        "limitation": "Because B2 has an explicit null failure, the successful-event unions are not full-schedule totals and cannot be used as final-search counts.",
    }
    return reconciliation, over_100


def write_no_clobber(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    reconciliation, over_100 = build_payloads()
    if args.check:
        if load(RECONCILIATION_PATH) != reconciliation or load(OVER_100_PATH) != over_100:
            raise SystemExit("Saved assessment differs from strict event artifacts")
        print(json.dumps({"status": "ok", "reconciliation": RECONCILIATION_PATH.name, "over_100": OVER_100_PATH.name}, indent=2))
        return 0
    write_no_clobber(RECONCILIATION_PATH, reconciliation)
    write_no_clobber(OVER_100_PATH, over_100)
    print(json.dumps({"status": "saved", "reconciliation": RECONCILIATION_PATH.name, "over_100": OVER_100_PATH.name}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
