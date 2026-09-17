#!/usr/bin/env python3
"""Validate all retained OATD Pilot 005 evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_continuation as count_validation
import run_pilot as base
import split_queries

SCHEMA = "oatd-pilot-005-validation/v1"
PILOT_ROOT = Path(__file__).resolve().parents[4] / "source-specific/oatd/pilots/005"
EXPECTED_COUNTS = {
    "G1-MH": 16,
    "G2A-MB-EF": 2,
    "G2B-MB-EH": 2,
    "G2C-MB-R": 10,
    "G2D-MB-T": 0,
    "G3-GMODEL": 0,
    "G4-GSTRUCTURE": 3,
    "G5-C1": 1,
}


def validate() -> dict[str, Any]:
    errors: list[str] = []
    initial_plan_path = PILOT_ROOT / "searches/event-plan.json"
    split_plan_path = PILOT_ROOT / "searches/split-continuation-plan.json"
    run_path = PILOT_ROOT / "searches/split-continuation-run-receipt.json"
    assessment_path = PILOT_ROOT / "searches/assessment.json"
    initial_plan = base.load(initial_plan_path)
    split_plan = base.load(split_plan_path)
    run = base.load(run_path)
    assessment = base.load(assessment_path)
    adapter = base.load_adapter()

    first_event = initial_plan["events"][0]
    events = [first_event, *split_plan["events"]]
    if [event["event_id"] for event in events] != list(EXPECTED_COUNTS):
        errors.append("gate_order")
    observed_counts: dict[str, int] = {}
    for event in events:
        output = PILOT_ROOT / event["output"]
        try:
            total = count_validation.validate_count_marker(
                adapter, base.load(output), event, output
            )
            observed_counts[event["event_id"]] = total
            if total != EXPECTED_COUNTS[event["event_id"]]:
                errors.append(f"count:{event['event_id']}")
        except Exception as error:
            errors.append(
                f"artifact:{event['event_id']}:{' '.join(str(error).split())[:200]}"
            )
    if (
        run.get("success") is not True
        or run.get("completed_gate_count") != 8
        or run.get("stopped_after_failure") is not False
    ):
        errors.append("run_receipt")
    if assessment.get("gate_counts") != EXPECTED_COUNTS:
        errors.append("assessment_counts")
    accounting = assessment.get("accounting", {})
    if (
        accounting.get("largest_gate_total") != 16
        or accounting.get("gate_occurrence_total") != 34
        or accounting.get("candidate_union_upper_bound") != 34
        or accounting.get("candidate_union_exact_total") is not None
    ):
        errors.append("assessment_accounting")
    if split_plan.get("algebraic_candidate_union", {}).get(
        "relationship_to_original_schedule"
    ) != "exact_union_equality" or split_plan.get("algebraic_candidate_union", {}).get(
        "partition_branch_coverage"
    ) != {
        key: list(value)
        for key, value in split_queries.PARTITION_BRANCH_COVERAGE.items()
    }:
        errors.append("algebraic_identity")
    failed = PILOT_ROOT / "searches/G2-MB.json"
    failed_value = base.load(failed)
    if (
        failed_value.get("total") is not None
        or failed_value.get("output_metadata", {}).get("error")
        != "OATD page did not become ready in time."
        or failed_value.get("output_metadata", {}).get("observed_exact_query_echo")
        is not False
    ):
        errors.append("combined_gate_failure")
    return {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "Open Access Theses and Dissertations (OATD)",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "validated_gate_count": len(observed_counts),
        "counts": observed_counts,
        "gate_occurrence_total": sum(observed_counts.values()),
        "candidate_union_exact_total": None,
        "do_not_merge": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=PILOT_ROOT / "searches/validation-report.json",
    )
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    report = validate()
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
