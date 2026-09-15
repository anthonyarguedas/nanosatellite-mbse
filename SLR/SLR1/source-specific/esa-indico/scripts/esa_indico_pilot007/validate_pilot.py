#!/usr/bin/env python3
"""Validate ESA Indico Pilot 007 plans, matches, assessment, and prose."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import queries
from build_assessment import build as build_assessment
from build_plan import build as build_plan
from common import (
    PILOT007_ROOT,
    SEARCH_ROOT,
    compact_corpus_binding,
    file_sha256,
    load_json,
    load_validated_corpus,
    relative_to_pilot,
    write_new_json,
)
from run_pilot import build_partition_result, build_receipt

SCHEMA = "esa-indico-pilot007-validation/v1"
DEFAULT_PLAN = SEARCH_ROOT / "schedule-plan.json"
DEFAULT_RECEIPT = SEARCH_ROOT / "run-receipt.json"
DEFAULT_ASSESSMENT = SEARCH_ROOT / "assessment.json"
DEFAULT_PILOT_DOCUMENT = PILOT007_ROOT / "pilot.md"
DEFAULT_GUIDELINE = PILOT007_ROOT.parents[1] / "source-specific-guidelines.md"
DEFAULT_OUTPUT = SEARCH_ROOT / "validation-report.json"
EXPECTED_TOTALS = {
    "A1": 0,
    "A2": 0,
    "A3": 0,
    "B1": 22,
    "B2": 2,
    "BG1": 0,
    "BG2": 1,
    "BC1": 2,
    "BT2": 0,
}
EXPECTED_NONZERO_INTERSECTIONS = [
    ("B1", "B2", 1),
    ("B1", "BC1", 1),
    ("B2", "BC1", 2),
]


def validate(
    plan_path: Path,
    receipt_path: Path,
    assessment_path: Path,
    pilot_document: Path,
    guideline: Path,
) -> dict[str, Any]:
    plan = load_json(plan_path, maximum_bytes=2_000_000)
    expected_plan = build_plan()
    if plan != expected_plan:
        raise RuntimeError("The schedule plan does not rebuild exactly")

    adapter, _source, ledger, binding = load_validated_corpus()
    if plan.get("source_corpus") != compact_corpus_binding(binding):
        raise RuntimeError("The validated source corpus differs from the plan")

    persisted_artifacts: list[tuple[Path, dict[str, Any]]] = []
    for event in plan["events"]:
        path = PILOT007_ROOT / event["output"]
        observed = load_json(path, maximum_bytes=5_000_000)
        expected = build_partition_result(
            adapter,
            ledger,
            binding,
            event,
            completed_at_utc=observed.get("completed_at_utc"),
        )
        if observed != expected:
            raise RuntimeError(
                f"{event['partition_id']}: matcher result does not rebuild"
            )
        persisted_artifacts.append((path, observed))

    receipt = load_json(receipt_path, maximum_bytes=2_000_000)
    expected_receipt = build_receipt(
        plan_path,
        plan,
        ledger,
        persisted_artifacts,
        completed_at_utc=receipt.get("completed_at_utc"),
    )
    if receipt != expected_receipt:
        raise RuntimeError("The run receipt does not rebuild exactly")

    assessment = load_json(assessment_path, maximum_bytes=5_000_000)
    rebuilt_assessment = build_assessment(plan_path, receipt_path)
    if assessment != rebuilt_assessment:
        raise RuntimeError("The assessment does not rebuild exactly")
    if assessment.get("status") != "complete":
        raise RuntimeError("The assessment is incomplete")

    observed_totals = {
        key: value.get("local_match_count")
        for key, value in assessment["partition_results"].items()
    }
    if observed_totals != EXPECTED_TOTALS:
        raise RuntimeError(f"Unexpected partition totals: {observed_totals}")
    union = assessment["schedule_union"]
    if (
        union.get("matched_record_count") != 24
        or union.get("matches_by_type")
        != {"events": 0, "contributions": 12, "subcontributions": 0, "materials": 12}
        or union.get("matched_parent_event_count") != 8
        or union.get("records_matching_exactly_n_partitions")
        != {"1": 22, "2": 1, "3": 1}
    ):
        raise RuntimeError("The schedule union accounting changed")
    intersections = [
        (value["left"], value["right"], value["count"])
        for value in union["nonzero_pairwise_intersections"]
    ]
    if intersections != EXPECTED_NONZERO_INTERSECTIONS:
        raise RuntimeError("The partition intersections changed")

    streams = assessment["streams"]
    expected_stream_counts = {
        "stream_A": 0,
        "core_stream_B": 23,
        "expanded_stream_B": 3,
        "all_stream_B": 24,
        "core_expanded_intersection": 2,
        "core_only": 21,
        "expanded_only": 1,
    }
    observed_stream_counts = {
        key: value["matched_record_count"] for key, value in streams.items()
    }
    if observed_stream_counts != expected_stream_counts:
        raise RuntimeError("The stream accounting changed")
    if (
        assessment["execution"].get("all_nine_partitions_complete") is not True
        or assessment["execution"].get("all_16_517_records_evaluated_per_partition")
        is not True
        or assessment["execution"].get("a1_reproduced_pilot006_zero") is not True
        or assessment["execution"].get("partitions_over_100") != []
        or assessment["translation"].get("a1_exactly_reproduces_pilot006_query")
        is not True
        or assessment["decision"].get("final_search") != "not_executed"
    ):
        raise RuntimeError("The execution or decision boundary changed")
    if len(assessment.get("candidate_ledger", [])) != 24:
        raise RuntimeError("The candidate ledger count changed")
    if any(
        value.get("screening_status") != "not_screened"
        for value in assessment["candidate_ledger"]
    ):
        raise RuntimeError("Pilot 007 contains an unrecorded screening decision")

    pilot_text = pilot_document.read_text(encoding="utf-8")
    guideline_text = guideline.read_text(encoding="utf-8")
    for phrase in (
        "16,517 normalized metadata records",
        "B1 returned 22",
        "24 distinct metadata candidates",
        "No source or attachment body request was made",
        "final search was not executed",
    ):
        if phrase not in pilot_text:
            raise RuntimeError(f"Pilot document omits: {phrase}")
    for phrase in (
        "[Pilot 007](pilots/007/pilot.md)",
        "24 distinct metadata records",
        "No proximity or pair expansion is used",
        "F(T_precise)",
    ):
        if phrase not in guideline_text:
            raise RuntimeError(f"Source guideline omits: {phrase}")

    artifact_hashes = {
        relative_to_pilot(path): file_sha256(path)
        for path in (
            plan_path,
            receipt_path,
            assessment_path,
            *(path for path, _artifact in persisted_artifacts),
        )
    }
    return {
        "schema_version": SCHEMA,
        "source": assessment["source"],
        "pilot": "007",
        "status": "pass",
        "validated_corpus": compact_corpus_binding(binding),
        "checks": {
            "source_transaction_gate": "pass",
            "plan_rebuild": "pass",
            "nine_match_rebuilds": "pass",
            "run_receipt_rebuild": "pass",
            "assessment_rebuild": "pass",
            "query_snapshot_hashes": queries.QUERY_SHA256,
            "partition_totals": EXPECTED_TOTALS,
            "schedule_union_records": 24,
            "schedule_union_types": {
                "events": 0,
                "contributions": 12,
                "subcontributions": 0,
                "materials": 12,
            },
            "matched_parent_events": 8,
            "stream_counts": expected_stream_counts,
            "nonzero_intersections": [
                {"left": left, "right": right, "count": count}
                for left, right, count in EXPECTED_NONZERO_INTERSECTIONS
            ],
            "no_partition_over_100": True,
            "source_requests": 0,
            "attachment_body_requests": 0,
            "pilot_and_guideline_updated": True,
        },
        "artifacts": artifact_hashes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--pilot-document", type=Path, default=DEFAULT_PILOT_DOCUMENT)
    parser.add_argument("--guideline", type=Path, default=DEFAULT_GUIDELINE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = validate(
        args.plan,
        args.receipt,
        args.assessment,
        args.pilot_document,
        args.guideline,
    )
    write_new_json(args.output, report)
    print(f"Wrote {args.output}: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
