#!/usr/bin/env python3
"""Build the ESA Indico Pilot 007 schedule assessment."""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping

import queries
from build_plan import build as build_plan
from common import (
    PILOT007_ROOT,
    SEARCH_ROOT,
    SOURCE_NAME,
    file_sha256,
    load_json,
    relative_to_pilot,
    write_new_json,
)
from run_pilot import RECEIPT_SCHEMA, RESULT_SCHEMA

SCHEMA = "esa-indico-pilot007-assessment/v1"
DEFAULT_PLAN = SEARCH_ROOT / "schedule-plan.json"
DEFAULT_RECEIPT = SEARCH_ROOT / "run-receipt.json"
DEFAULT_OUTPUT = SEARCH_ROOT / "assessment.json"


def _canonical_result(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in {"rank", "query"}}


def _ordered_subset(order: list[str], values: set[str]) -> list[str]:
    output = [identity for identity in order if identity in values]
    if len(output) != len(values):
        raise RuntimeError(
            "A result set contains an identity outside the schedule union"
        )
    return output


def _type_counts(
    identities: list[str], records: Mapping[str, Mapping[str, Any]]
) -> dict[str, int]:
    counts = Counter(records[identity]["sourceType"] for identity in identities)
    return {
        "events": counts["event"],
        "contributions": counts["contribution"],
        "subcontributions": counts["subcontribution"],
        "materials": counts["attachment"],
    }


def _set_summary(
    values: set[str],
    order: list[str],
    records: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    identities = _ordered_subset(order, values)
    event_ids = list(
        dict.fromkeys(str(records[value]["eventId"]) for value in identities)
    )
    return {
        "matched_record_count": len(identities),
        "matched_record_identities": identities,
        "matches_by_type": _type_counts(identities, records),
        "matched_parent_event_count": len(event_ids),
        "matched_parent_event_ids": event_ids,
    }


def build(plan_path: Path, receipt_path: Path) -> dict[str, Any]:
    plan = load_json(plan_path, maximum_bytes=2_000_000)
    expected_plan = build_plan()
    if plan != expected_plan:
        raise RuntimeError("The schedule plan does not rebuild exactly")
    receipt = load_json(receipt_path, maximum_bytes=2_000_000)
    if (
        receipt.get("schema_version") != RECEIPT_SCHEMA
        or receipt.get("status") != "complete"
        or receipt.get("event_count") != len(queries.SCHEDULE_IDS)
        or receipt.get("completed_event_count") != len(queries.SCHEDULE_IDS)
        or receipt.get("failed_event_count") != 0
        or receipt.get("plan_sha256") != file_sha256(plan_path)
        or receipt.get("source_corpus") != plan.get("source_corpus")
        or receipt.get("source_requests") != 0
        or receipt.get("browser_requests") != 0
        or receipt.get("attachment_body_requests") != 0
    ):
        raise RuntimeError("The schedule run receipt is incomplete")

    receipt_events = {
        value.get("partition_id"): value
        for value in receipt.get("events", [])
        if isinstance(value, Mapping)
    }
    if tuple(receipt_events) != queries.SCHEDULE_IDS:
        raise RuntimeError("The run receipt partition order changed")

    partition_sets: dict[str, set[str]] = {}
    partition_artifacts: dict[str, dict[str, Any]] = {}
    record_index: dict[str, dict[str, Any]] = {}
    completed_at = receipt.get("completed_at_utc")
    for event in plan["events"]:
        partition_id = event["partition_id"]
        path = PILOT007_ROOT / event["output"]
        artifact = load_json(path, maximum_bytes=5_000_000)
        receipt_event = receipt_events[partition_id]
        identities = artifact.get("matched_record_identities")
        results = artifact.get("results")
        if (
            artifact.get("schema_version") != RESULT_SCHEMA
            or artifact.get("partition_id") != partition_id
            or artifact.get("event_id") != event["event_id"]
            or artifact.get("status") != "complete"
            or artifact.get("diagnostic_only") is not True
            or artifact.get("do_not_merge") is not True
            or artifact.get("completed_at_utc") != completed_at
            or artifact.get("requested_query") != queries.SCHEDULE[partition_id]
            or artifact.get("requested_query_sha256")
            != queries.QUERY_SHA256[partition_id]
            or artifact.get("source_corpus") != plan["source_corpus"]
            or not isinstance(identities, list)
            or len(identities) != len(set(identities))
            or not isinstance(results, list)
            or artifact.get("total") != len(identities)
            or artifact.get("results_retrieved") != len(results)
            or len(results) != len(identities)
            or [row.get("ledgerRecordIdentity") for row in results] != identities
            or [row.get("rank") for row in results] != list(range(1, len(results) + 1))
            or any(
                row.get("query") != queries.SCHEDULE[partition_id] for row in results
            )
            or artifact.get("counts", {}).get("local_match_count") != len(identities)
            or artifact.get("counts", {}).get("source_export_records") != 16_517
            or artifact.get("counts", {}).get("metadata_nonmatch_count")
            != 16_517 - len(identities)
            or artifact.get("matcher", {}).get("records_evaluated") != 16_517
            or artifact.get("matcher", {}).get("attachment_content_used") is not False
            or artifact.get("output_metadata", {}).get("merge_eligible") is not False
            or artifact.get("output_metadata", {}).get("source_requests") != 0
            or artifact.get("output_metadata", {}).get("browser_requests") != 0
            or artifact.get("output_metadata", {}).get("attachment_body_requests") != 0
            or receipt_event.get("artifact") != relative_to_pilot(path)
            or receipt_event.get("artifact_sha256") != file_sha256(path)
            or receipt_event.get("local_match_count") != len(identities)
            or receipt_event.get("matcher_operation_count")
            != artifact.get("matcher", {}).get("operation_count")
        ):
            raise RuntimeError(f"{partition_id}: result artifact did not reconcile")
        partition_sets[partition_id] = set(identities)
        partition_artifacts[partition_id] = artifact
        for identity, row in zip(identities, results):
            canonical = _canonical_result(row)
            prior = record_index.get(identity)
            if prior is not None and prior != canonical:
                raise RuntimeError(
                    f"{identity}: candidate metadata changed between partitions"
                )
            record_index[identity] = canonical

    union_order = receipt.get("schedule_union", {}).get("matched_record_identities")
    memberships = receipt.get("schedule_union", {}).get("partition_memberships")
    if not isinstance(union_order, list) or len(union_order) != len(set(union_order)):
        raise RuntimeError("The schedule union identity ledger is invalid")
    union_set = set().union(*partition_sets.values())
    if (
        set(union_order) != union_set
        or len(record_index) != len(union_set)
        or receipt.get("schedule_union", {}).get("matched_record_count")
        != len(union_set)
        or not isinstance(memberships, Mapping)
        or list(memberships) != union_order
    ):
        raise RuntimeError("The schedule union did not reconcile")
    for identity in union_order:
        expected = [
            partition_id
            for partition_id in queries.SCHEDULE_IDS
            if identity in partition_sets[partition_id]
        ]
        if memberships.get(identity) != expected:
            raise RuntimeError(f"{identity}: partition membership changed")

    partition_summary: dict[str, Any] = {}
    for partition_id in queries.SCHEDULE_IDS:
        identities = _ordered_subset(union_order, partition_sets[partition_id])
        exclusive = [
            identity for identity in identities if len(memberships[identity]) == 1
        ]
        artifact = partition_artifacts[partition_id]
        partition_summary[partition_id] = {
            "semantic_form": queries.SEMANTIC_FORMS[partition_id],
            "query_sha256": queries.QUERY_SHA256[partition_id],
            "artifact": next(
                event["output"]
                for event in plan["events"]
                if event["partition_id"] == partition_id
            ),
            "artifact_sha256": file_sha256(
                PILOT007_ROOT
                / next(
                    event["output"]
                    for event in plan["events"]
                    if event["partition_id"] == partition_id
                )
            ),
            "local_match_count": len(identities),
            "matches_by_type": artifact["counts"]["matches_by_type"],
            "matched_parent_event_count": artifact["counts"][
                "matched_parent_event_count"
            ],
            "matched_record_identities": identities,
            "exclusive_schedule_record_count": len(exclusive),
            "exclusive_schedule_record_identities": exclusive,
            "over_100_investigation_triggered": len(identities) > 100,
        }

    nonzero_intersections = []
    for left, right in combinations(queries.SCHEDULE_IDS, 2):
        intersection = partition_sets[left] & partition_sets[right]
        if intersection:
            nonzero_intersections.append(
                {
                    "left": left,
                    "right": right,
                    "count": len(intersection),
                    "record_identities": _ordered_subset(union_order, intersection),
                }
            )

    stream_a = set().union(*(partition_sets[key] for key in ("A1", "A2", "A3")))
    core_b = partition_sets["B1"] | partition_sets["B2"]
    expanded_b = set().union(
        *(partition_sets[key] for key in ("BG1", "BG2", "BC1", "BT2"))
    )
    all_b = core_b | expanded_b
    membership_counts = Counter(len(value) for value in memberships.values())

    candidate_ledger = []
    for identity in union_order:
        record = record_index[identity]
        candidate_ledger.append(
            {
                "record_identity": identity,
                "paper_id": record["paperId"],
                "source_type": record["sourceType"],
                "event_id": record["eventId"],
                "title": record["title"],
                "partitions": memberships[identity],
                "screening_status": "not_screened",
            }
        )

    return {
        "schema_version": SCHEMA,
        "source": SOURCE_NAME,
        "pilot": "007",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": plan["objective"],
        "completed_at_utc": completed_at,
        "plan": {
            "path": relative_to_pilot(plan_path),
            "sha256": file_sha256(plan_path),
            "event_count": len(plan["events"]),
        },
        "run_receipt": {
            "path": relative_to_pilot(receipt_path),
            "sha256": file_sha256(receipt_path),
            "completed_event_count": receipt["completed_event_count"],
            "failed_event_count": receipt["failed_event_count"],
        },
        "source_corpus": plan["source_corpus"],
        "translation": {
            "status": "current_post_proximity_compound_definitions_executed",
            "wildcard": False,
            "proximity": False,
            "pair_expansion": False,
            "changed_historical_partitions": list(
                queries.CHANGED_FROM_HISTORICAL_PAIR_SCHEDULE
            ),
            "a1_exactly_reproduces_pilot006_query": (
                queries.QUERY_SHA256["A1"]
                == plan["source_corpus"]["anchor_query_sha256"]
            ),
        },
        "partition_results": partition_summary,
        "schedule_union": {
            **_set_summary(union_set, union_order, record_index),
            "records_matching_exactly_n_partitions": {
                str(count): membership_counts[count]
                for count in sorted(membership_counts)
            },
            "nonzero_pairwise_intersections": nonzero_intersections,
        },
        "streams": {
            "stream_A": _set_summary(stream_a, union_order, record_index),
            "core_stream_B": _set_summary(core_b, union_order, record_index),
            "expanded_stream_B": _set_summary(expanded_b, union_order, record_index),
            "all_stream_B": _set_summary(all_b, union_order, record_index),
            "core_expanded_intersection": _set_summary(
                core_b & expanded_b, union_order, record_index
            ),
            "core_only": _set_summary(core_b - expanded_b, union_order, record_index),
            "expanded_only": _set_summary(
                expanded_b - core_b, union_order, record_index
            ),
        },
        "candidate_ledger": candidate_ledger,
        "execution": {
            "all_nine_partitions_complete": True,
            "all_16_517_records_evaluated_per_partition": True,
            "a1_reproduced_pilot006_zero": len(partition_sets["A1"]) == 0,
            "partitions_over_100": [
                key for key, values in partition_sets.items() if len(values) > 100
            ],
            "source_requests": 0,
            "browser_requests": 0,
            "attachment_body_requests": 0,
        },
        "decision": {
            "source_translation": "accept_current_no_proximity_compound_schedule",
            "source_controls": "no_change",
            "schedule_pilot": "complete_on_pilot006_fixed_corpus",
            "final_search": "not_executed",
            "screening": "not_started",
        },
        "limits": [
            "This is a read-only pilot projection from the 2026-09-02 fixed corpus. It does not refresh the live source.",
            "The 24 union records are metadata candidates. Language, date, report type, full text, and eligibility remain screening decisions.",
            "Notes and Categories remain outside the complete metadata route.",
            "Contribution and attachment identities remain separate until downstream deduplication.",
            "The nine derivative artifacts are pilot-only and cannot enter the merger as new source harvests.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    assessment = build(args.plan, args.receipt)
    write_new_json(args.output, assessment)
    print(
        f"Wrote {args.output} with "
        f"{assessment['schedule_union']['matched_record_count']} union records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
