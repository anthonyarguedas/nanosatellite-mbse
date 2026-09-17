#!/usr/bin/env python3
"""Validate IEEE Xplore Pilot 005 without executing a source search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_assessment import build as build_assessment
from build_plan import build as build_plan
from queries import CHANGED_IDS, SCHEDULE, SCHEDULE_IDS
from run_pilot import artifact_matches_event, artifact_status, marker_is_valid, marker_path


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def validate(pilot_root: Path, guideline: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    searches = pilot_root / "searches"
    plan_path = searches / "event-plan.json"
    raw_receipt_path = searches / "run-receipt-raw.json"
    receipt_path = searches / "run-receipt.json"
    assessment_path = searches / "assessment.json"
    old_union_path = pilot_root.parent / "004" / "searches" / "union-receipt.json"

    plan = load(plan_path)
    raw_receipt = load(raw_receipt_path)
    receipt = load(receipt_path)
    assessment = load(assessment_path)
    expected_assessment = build_assessment(
        pilot_root,
        plan_path,
        raw_receipt_path,
        receipt_path,
        old_union_path,
    )
    events = plan.get("events", [])
    entries = assessment.get("artifact_ledger", [])
    entry_by_event = {entry["event_id"]: entry for entry in entries}

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, observed: Any = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    check("plan_matches_builder", plan == build_plan())
    check("plan_schema", plan.get("schema_version") == "ieee-xplore-pilot-005-event-plan/v1")
    check("plan_event_count", len(events) == 22, len(events))
    check(
        "plan_precedes_source_artifacts",
        all(
            plan_path.stat().st_mtime <= (pilot_root / "searches" / event["output"]).stat().st_mtime
            for event in events
        ),
    )
    check("schedule_order", tuple(SCHEDULE) == SCHEDULE_IDS)
    check(
        "plan_queries_match_canonical_schedule",
        all(event["query"] == SCHEDULE[event["schedule_id"]] for event in events),
    )
    check(
        "plan_query_hashes_match",
        all(event["query_sha256"] == sha256_text(event["query"]) for event in events),
    )
    check(
        "no_proximity_or_wildcard_syntax",
        all(
            "NEAR" not in event["query"].upper()
            and "*" not in event["query"]
            and "?" not in event["query"]
            for event in events
        ),
    )
    check(
        "one_direct_query_per_partition",
        plan.get("translation", {}).get("source_cells_per_partition") == 1,
    )

    output_paths = [pilot_root / "searches" / event["output"] for event in events]
    check("all_source_artifacts_present", all(path.is_file() for path in output_paths))
    check("assessment_artifact_count", len(entries) == 22, len(entries))
    check(
        "every_artifact_matches_event",
        all(
            artifact_matches_event(event, load(pilot_root / "searches" / event["output"]))
            for event in events
        ),
    )
    check(
        "every_artifact_is_nonmergeable",
        all(load(path).get("do_not_merge") is True for path in output_paths),
    )
    cleanup_dirs = list(searches.rglob(".ACADEMIC_SEARCH_OUTPUT_CLEANUP.*"))
    check("no_private_cleanup_residue", not cleanup_dirs, len(cleanup_dirs))

    successful = [
        event
        for event in events
        if artifact_status(load(pilot_root / "searches" / event["output"]))
        in {"count_only", "success"}
    ]
    failed = [
        event
        for event in events
        if artifact_status(load(pilot_root / "searches" / event["output"])) == "error"
    ]
    check("successful_event_count", len(successful) == 6, len(successful))
    check("failed_event_count", len(failed) == 16, len(failed))
    check(
        "successful_commit_markers_valid",
        len(successful) == 6
        and all(
            marker_is_valid(pilot_root / "searches" / event["output"])
            for event in successful
        ),
    )
    check(
        "failed_artifacts_have_no_terminal_marker",
        len(failed) == 16
        and all(
            not marker_path(pilot_root / "searches" / event["output"]).exists()
            for event in failed
        ),
    )
    check(
        "plan_all_artifact_marker_check_failed_and_is_documented",
        assessment.get("execution", {}).get("successful_commit_marker_count") == 6
        and assessment.get("execution", {}).get("failed_artifact_commit_marker_count") == 0,
    )

    check(
        "all_partitions_have_exact_query_echo",
        all(
            assessment["partitions"][schedule_id]["direct_query_echo_observed"] is True
            for schedule_id in SCHEDULE_IDS
        ),
    )
    expected_totals = {
        "A1": None,
        "A2": None,
        "A3": 6,
        "B1": None,
        "B2": 131,
        "BG1": 1,
        "BG2": None,
        "BC1": None,
        "BT2": None,
    }
    check(
        "repeated_totals_match",
        assessment.get("findings", {}).get("repeated_totals") == expected_totals,
        assessment.get("findings", {}).get("repeated_totals"),
    )
    check(
        "changed_strict_events_are_explicit_nulls",
        all(
            entry_by_event[f"records-{schedule_id}"]["status"] == "error"
            and entry_by_event[f"records-{schedule_id}"]["total"] is None
            for schedule_id in CHANGED_IDS
        ),
    )
    check(
        "changed_strict_pass_accounting",
        {
            schedule_id: entry_by_event[f"records-{schedule_id}"]["strict_passes_completed"]
            for schedule_id in CHANGED_IDS
        }
        == {"BG1": 1, "BG2": 0, "BC1": 0, "BT2": 0},
    )
    check(
        "failure_stage_counts",
        {
            "year": assessment["findings"]["year_fill_or_enable_failures"],
            "initial": assessment["findings"]["initial_form_readiness_failures"],
            "rendered": assessment["findings"]["rendered_state_failures"],
        }
        == {"year": 12, "initial": 2, "rendered": 2},
    )

    check("raw_receipt_retained", raw_receipt.get("successful_source_event_count") == 0)
    check(
        "reconciled_receipt_reused_without_source_execution",
        receipt.get("status") == "complete_with_retained_source_failures"
        and receipt.get("successful_source_event_count") == 6
        and receipt.get("failed_source_event_count") == 16
        and all(outcome.get("reused_existing") is True for outcome in receipt.get("outcomes", [])),
    )
    check("assessment_rebuild_is_identical", assessment == expected_assessment)

    guideline_text = guideline.read_text()
    pilot_text = (pilot_root / "pilot.md").read_text()
    required_guideline_fragments = (
        "F(G_model_fixed)",
        "F(G_mission_exact)",
        "F(G_product_exact)",
        "F(G_variation)",
        "F(G_DSL)",
        "F(T_precise)",
        "pilots/005/pilot.md",
        "Only `A3`, `B2`, and `BG1` returned equal totals twice",
    )
    check(
        "guideline_contains_current_translation",
        all(fragment in guideline_text for fragment in required_guideline_fragments),
    )
    check("guideline_removes_current_pair_schedule", "F(T2)" not in guideline_text)
    check(
        "pilot_documents_null_strict_outcomes",
        "All four changed strict events remain null" in pilot_text,
    )
    check(
        "pilot_documents_no_final_authorization",
        "no Pilot 005 artifact belongs in `final-searches/`" in pilot_text,
    )

    summary = {
        "source_event_count": len(events),
        "successful_source_event_count": len(successful),
        "failed_source_event_count": len(failed),
        "valid_success_marker_count": sum(
            marker_is_valid(pilot_root / "searches" / event["output"])
            for event in successful
        ),
        "repeated_totals": expected_totals,
        "changed_strict_success_count": 0,
        "changed_strict_null_count": 4,
    }
    return checks, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks, summary = validate(args.pilot_root, args.guideline)
    failures = [item["check"] for item in checks if not item["passed"]]
    value = {
        "schema_version": "ieee-xplore-pilot-005-validation/v1",
        "source": "IEEE Xplore",
        "pilot": "005",
        "status": "passed" if not failures else "failed",
        "diagnostic_only": True,
        "do_not_merge": True,
        "check_count": len(checks),
        "failure_count": len(failures),
        "failures": failures,
        "summary": summary,
        "checks": checks,
    }
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
