#!/usr/bin/env python3
"""Execute ESA Indico Pilot 007 over the validated Pilot 006 ledger."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import queries
from build_plan import build as build_plan
from common import (
    PILOT007_ROOT,
    SEARCH_ROOT,
    SOURCE_NAME,
    compact_corpus_binding,
    file_sha256,
    load_json,
    load_validated_corpus,
    match_partition,
    operation_for,
    relative_to_pilot,
    text_sha256,
    write_new_json,
)

RESULT_SCHEMA = "esa-indico-pilot007-ledger-query/v1"
RECEIPT_SCHEMA = "esa-indico-pilot007-run-receipt/v1"
DEFAULT_PLAN = SEARCH_ROOT / "schedule-plan.json"
DEFAULT_RECEIPT = SEARCH_ROOT / "run-receipt.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _type_counts(rows: list[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row.get("sourceType")) for row in rows)
    return {
        "events": counts["event"],
        "contributions": counts["contribution"],
        "subcontributions": counts["subcontribution"],
        "materials": counts["attachment"],
    }


def build_partition_result(
    adapter: Any,
    ledger: Mapping[str, Any],
    binding: Mapping[str, Any],
    event: Mapping[str, Any],
    *,
    completed_at_utc: str,
) -> dict[str, Any]:
    partition_id = event["partition_id"]
    query = queries.SCHEDULE[partition_id]
    if (
        event.get("query") != query
        or event.get("query_sha256") != queries.QUERY_SHA256[partition_id]
    ):
        raise RuntimeError(f"{partition_id}: plan query changed")
    identities, results, operations = match_partition(adapter, ledger, partition_id)
    if len(results) > event["maximum_retained_matches"]:
        raise RuntimeError(
            f"{partition_id}: {len(results)} matches exceed the predeclared 100-record bound"
        )
    if [row.get("ledgerRecordIdentity") for row in results] != identities:
        raise RuntimeError(f"{partition_id}: normalized rows changed source order")
    operation = operation_for(adapter, query, ledger)
    event_ids = list(dict.fromkeys(str(row["eventId"]) for row in results))
    corpus_records = binding["counts"]["records"]
    return {
        "schema_version": RESULT_SCHEMA,
        "source": SOURCE_NAME,
        "pilot": "007",
        "event_id": event["event_id"],
        "partition_id": partition_id,
        "semantic_form": event["semantic_form"],
        "source_construction": event["source_construction"],
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "completed_at_utc": completed_at_utc,
        "requested_query": query,
        "requested_query_sha256": queries.QUERY_SHA256[partition_id],
        "executed_query": operation,
        "executed_query_sha256": text_sha256(operation),
        "source_query_submitted": False,
        "source_corpus": compact_corpus_binding(binding),
        "matcher": {
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "adapter_sha256": file_sha256(Path(adapter.__file__)),
            "schema": adapter.LOCAL_MATCHER_SCHEMA,
            "operation_count": operations,
            "operation_limit": adapter.LOCAL_MATCHER_MAX_OPERATIONS,
            "record_passes": 1,
            "records_evaluated": corpus_records,
            "phrase_scope": "one declared field",
            "boolean_scope": "one normalized record",
            "attachment_content_used": False,
        },
        "total": len(results),
        "results_retrieved": len(results),
        "matched_record_identities": identities,
        "matched_parent_event_ids": event_ids,
        "counts": {
            "source_reported_total": None,
            "source_universe_events": binding["root_snapshot_count"],
            "source_export_records": corpus_records,
            "local_match_count": len(results),
            "metadata_nonmatch_count": corpus_records - len(results),
            "matches_by_type": _type_counts(results),
            "matched_parent_event_count": len(event_ids),
            "records_exported": len(results),
        },
        "results": results,
        "output_metadata": {
            "retrieval_complete": True,
            "status": "complete_offline_pilot_projection",
            "merge_eligible": False,
            "merge_ineligibility_reason": (
                "Pilot-only derivative of the marker-bound complete corpus. It is not a "
                "new source harvest or adapter publication transaction."
            ),
            "full_metadata_ledger_reused": True,
            "source_requests": 0,
            "browser_requests": 0,
            "attachment_body_requests": 0,
            "date_filter_applied": False,
            "language_filter_applied": False,
            "publication_type_filter_applied": False,
        },
    }


def build_receipt(
    plan_path: Path,
    plan: Mapping[str, Any],
    ledger: Mapping[str, Any],
    artifacts: list[tuple[Path, Mapping[str, Any]]],
    *,
    completed_at_utc: str,
) -> dict[str, Any]:
    matched_set: set[str] = set()
    memberships: dict[str, list[str]] = {}
    events = []
    for path, artifact in artifacts:
        partition_id = artifact["partition_id"]
        identities = artifact["matched_record_identities"]
        for identity in identities:
            memberships.setdefault(identity, []).append(partition_id)
            matched_set.add(identity)
        events.append(
            {
                "event_id": artifact["event_id"],
                "partition_id": partition_id,
                "artifact": relative_to_pilot(path),
                "artifact_sha256": file_sha256(path),
                "status": artifact["status"],
                "local_match_count": artifact["total"],
                "matcher_operation_count": artifact["matcher"]["operation_count"],
            }
        )
    union = [
        identity for identity in ledger["record_identities"] if identity in matched_set
    ]
    if len(union) != len(matched_set):
        raise RuntimeError(
            "The schedule union contains an identity outside the source ledger"
        )
    ordered_memberships = {identity: memberships[identity] for identity in union}
    return {
        "schema_version": RECEIPT_SCHEMA,
        "source": SOURCE_NAME,
        "pilot": "007",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "completed_at_utc": completed_at_utc,
        "plan": relative_to_pilot(plan_path),
        "plan_sha256": file_sha256(plan_path),
        "source_corpus": plan["source_corpus"],
        "event_count": len(events),
        "completed_event_count": len(events),
        "failed_event_count": 0,
        "events": events,
        "schedule_union": {
            "matched_record_count": len(union),
            "matched_record_identities": union,
            "partition_memberships": ordered_memberships,
        },
        "source_requests": 0,
        "browser_requests": 0,
        "attachment_body_requests": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    plan = load_json(args.plan, maximum_bytes=2_000_000)
    expected_plan = build_plan()
    if plan != expected_plan:
        raise RuntimeError("The persisted schedule plan does not rebuild exactly")
    adapter, _source, ledger, binding = load_validated_corpus()
    if plan.get("source_corpus") != compact_corpus_binding(binding):
        raise RuntimeError("The source corpus changed after plan creation")
    completed_at_utc = utc_now()
    pending: list[tuple[Path, dict[str, Any]]] = []
    for event in plan["events"]:
        path = PILOT007_ROOT / event["output"]
        if path.exists():
            raise RuntimeError(f"Refusing to overwrite {path}")
        result = build_partition_result(
            adapter,
            ledger,
            binding,
            event,
            completed_at_utc=completed_at_utc,
        )
        pending.append((path, result))
    if args.receipt.exists():
        raise RuntimeError(f"Refusing to overwrite {args.receipt}")
    for path, result in pending:
        write_new_json(path, result)
    receipt = build_receipt(
        args.plan,
        plan,
        ledger,
        pending,
        completed_at_utc=completed_at_utc,
    )
    write_new_json(args.receipt, receipt)
    print(
        f"Completed {len(pending)} partitions with "
        f"{receipt['schedule_union']['matched_record_count']} union records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
