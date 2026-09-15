#!/usr/bin/env python3
"""Validate AIAA ARC Pilot 005 plans, source artifacts, assessment, and docs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_assessment import build
from build_bg2_fixed_plan import build as build_bg2_fixed_plan
from build_phrase_plan import build as build_phrase_plan
from build_plan import build as build_main_plan
from build_threshold_plan import build as build_threshold_plan
from queries import PROTOCOL_COMMIT, SCHEDULE, SCHEDULE_IDS, TERM_COUNTS

EXPECTED_SCHEDULE_COUNTS = {
    "A1": 492,
    "A2": 1541,
    "A3": 472,
    "B1": 1388,
    "B2": 1028,
    "BG1": 45,
    "BG2": 3584,
    "BC1": 152,
    "BT2": 437,
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object in {path}")
    return value


def check(condition: bool, name: str, checks: list[dict[str, Any]], detail: str = "") -> None:
    checks.append({"check": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise RuntimeError(f"Validation failed: {name}. {detail}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--pilot-document", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    search_root = args.pilot_root / "searches"
    actual = load(search_root / "assessment.json")
    rebuilt = build(args.pilot_root)
    check(actual == rebuilt, "assessment_rebuild_is_byte_semantic_equal", checks)
    check(actual.get("protocol_commit") == PROTOCOL_COMMIT, "protocol_commit", checks, PROTOCOL_COMMIT)
    check(actual.get("schedule_counts") == EXPECTED_SCHEDULE_COUNTS, "schedule_counts", checks)
    check(actual.get("changed_totals_repeated_exactly") is True, "changed_count_repetition", checks)
    check(actual["known_item_recall"]["all_applicable_partitions_retrieved"] is True, "known_item_recall", checks)
    check(actual["direct_BT2"]["single_cell_accepted"] is True, "direct_BT2", checks)
    check(actual["direct_BT2"]["query_characters"] == len(SCHEDULE["BT2"]), "BT2_query_length", checks)
    check(actual["historical_BG1_comparator"]["current_direct_total"] == 45, "BG1_low_volume", checks)
    check(
        actual["ordered_phrase_validation"]["status"] == "accepted_bounded_title_controls",
        "ordered_phrase_controls",
        checks,
    )
    check(
        actual["issue_resolution"]["overall"]
        == "semantic_and_recall_translation_issues_resolved_precision_only_partly_resolved",
        "bounded_issue_resolution",
        checks,
    )
    check(actual["retained_source_failures"]["count"] == 13, "retained_failure_count", checks)
    check(actual["retained_source_failures"]["all_recovered_by_exact_retries"] is True, "failure_recovery", checks)

    generated_plans = {
        "event-plan.json": build_main_plan(),
        "threshold-event-plan.json": build_threshold_plan(search_root / "counts"),
        "bg2-fixed-event-plan.json": build_bg2_fixed_plan(search_root / "branch-counts" / "BG2-fixed.json"),
        "phrase-event-plan.json": build_phrase_plan(
            search_root / "branch-counts" / "BG2-fixed-literal-01.json"
        ),
    }
    plan_expectations = {
        "event-plan.json": 21,
        "threshold-event-plan.json": 16,
        "bg2-fixed-event-plan.json": 8,
        "phrase-event-plan.json": 8,
    }
    for name, expected_count in plan_expectations.items():
        check(load(search_root / name) == generated_plans[name], f"{name}_rebuild", checks)
        plan = load(search_root / name)
        check(len(plan.get("events", [])) == expected_count, f"{name}_event_count", checks)
        check(plan.get("protocol_commit") == PROTOCOL_COMMIT, f"{name}_protocol_commit", checks)
        for event in plan["events"]:
            output = args.pilot_root / event["output"]
            candidates = [output, *(output.with_name(f"{output.stem}-retry{i}{output.suffix}") for i in range(1, 8))]
            successes = [candidate for candidate in candidates if candidate.exists() and isinstance(load(candidate).get("total"), int)]
            check(len(successes) == 1, f"source_success_{event['event_id']}", checks, str(successes))

    check(tuple(SCHEDULE) == SCHEDULE_IDS, "schedule_order", checks)
    check(TERM_COUNTS == actual["translation"]["term_counts"], "term_membership_counts", checks)
    check(
        all("NEAR" not in query.upper() and "*" not in query and "?" not in query for query in SCHEDULE.values()),
        "no_proximity_or_wildcard",
        checks,
    )
    check(not list(args.pilot_root.rglob(".*.tmp")), "no_atomic_temp_links", checks)

    guideline = args.guideline.read_text()
    pilot_document = args.pilot_document.read_text()
    required_guideline_text = (
        "Pilot 005 Anywhere sensitivity route",
        "T_precise",
        "3,584",
        "complete Anywhere schedule is retained as sensitivity evidence",
        "Pilot 007 accepted hybrid route",
    )
    for text in required_guideline_text:
        check(text in guideline, f"guideline_contains_{text}", checks)
    required_pilot_text = (
        "# Pilot 005",
        "8,088",
        "3,584",
        "1,822",
        "semantic and recall issues",
        "precision remains",
    )
    for text in required_pilot_text:
        check(text.casefold() in pilot_document.casefold(), f"pilot_document_contains_{text}", checks)

    report = {
        "schema_version": "aiaa-arc-pilot005-validation/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "005",
        "status": "passed",
        "checks_passed": len(checks),
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "passed", "checks": len(checks)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
