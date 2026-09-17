#!/usr/bin/env python3
"""Validate PQDT Pilot 005 artifacts and synchronized decisions."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

import queries
import run_pilot

DEFAULT_GUIDELINE = (
    queries.PILOT_ROOT.parent.parent / "source-specific-guidelines.md"
)
DEFAULT_TASKS = queries.SLR1_ROOT / "TASKS.md"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "validation-report.json"
EXPECTED_TOTALS = {
    "A1": 1,
    "A2": 3,
    "A3": 1,
    "B1": 21,
    "B2": 13,
    "BG1": 1,
    "BG2": 3,
    "BC1": 3,
    "BT2": 1,
}


def load(path: Path) -> dict[str, Any]:
    return queries.load_object(path)


def validate(guideline_path: Path, tasks_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    searches = queries.PILOT_ROOT / "searches"
    preflight = load(searches / "preflight.json")
    assignments = load(searches / "assigned-terms.json")
    initial_map = load(searches / "candidate-map-initial.json")
    initial_validation = load(searches / "candidate-validation-initial.json")
    candidate_map = load(searches / "candidate-map.json")
    candidate_validation = load(searches / "candidate-validation.json")
    validated_map = load(searches / "validated-candidate-map.json")
    plan = load(searches / "event-plan.json")
    receipt = load(searches / "run-receipt.json")
    comparison = load(searches / "set-comparison.json")
    review = load(searches / "descriptor-only-review.json")
    assessment = load(searches / "inclusion-assessment.json")

    if preflight.get("status") != "predeclared":
        errors.append("Preflight is not predeclared.")
    if preflight.get("record_selection", {}).get("record_count") != 14:
        errors.append("Preflight does not select fourteen known records.")
    if preflight.get("pinned_inputs", {}).get("adapter", {}).get(
        "sha256"
    ) != queries.file_sha256(queries.ADAPTER_PATH):
        errors.append("Preflight adapter hash changed.")

    if assignments.get("status") != "complete_two_pass_assignment_readback":
        errors.append("Assigned-term harvest is incomplete.")
    if assignments.get("selected_record_count") != 14:
        errors.append("Assigned-term record count changed.")
    if assignments.get("pq_subject_unique_term_count") != 9:
        errors.append("PQ Subject unique-term count changed.")
    if assignments.get("index_term_unique_term_count") != 42:
        errors.append("Index term unique-term count changed.")
    if assignments.get("pass_reconciliation", {}).get(
        "ordered_assignments_equal"
    ) is not True:
        errors.append("Assigned-term passes do not reconcile.")
    if assignments.get("method", {}).get("scope", {}).get(
        "restoration_verified"
    ) is not True:
        errors.append("Assigned-term scope cleanup is unverified.")

    if initial_map.get("candidate_count") != 28:
        errors.append("Initial candidate-map count changed.")
    if initial_validation.get("verified_exact_label_count") != 24:
        errors.append("Initial exact-label result count changed.")
    if initial_validation.get("assigned_but_absent_count") != 4:
        errors.append("Initial absent-label result count changed.")
    if candidate_map.get("candidate_count") != 28:
        errors.append("Case-normalized candidate-map count changed.")
    if candidate_validation.get("status") != "complete_two_pass_exact_browse_readback":
        errors.append("Final exact-label validation is incomplete.")
    if candidate_validation.get("verified_exact_label_count") != 27:
        errors.append("Final verified exact-label count changed.")
    if candidate_validation.get("assigned_but_absent_count") != 1:
        errors.append("Final absent exact-label count changed.")
    rejected = [
        item.get("candidate_id")
        for item in candidate_validation.get("candidates", [])
        if item.get("status") != "verified_exact_browse_label"
    ]
    if rejected != ["IF-R-01"]:
        errors.append("Final rejected candidate is no longer IF Architecture.")
    if candidate_validation.get("pass_reconciliation", {}).get(
        "ordered_candidate_results_equal"
    ) is not True:
        errors.append("Exact-label validation passes do not reconcile.")
    if candidate_validation.get("source_contract", {}).get("scope", {}).get(
        "restoration_verified"
    ) is not True:
        errors.append("Exact-label scope cleanup is unverified.")

    if validated_map.get("status") != "validated_for_value_comparison":
        errors.append("Validated candidate map is incomplete.")
    if validated_map.get("validated_candidate_count") != 27:
        errors.append("Validated candidate-map count changed.")
    if set(validated_map.get("controlled_constructions", {})) != {
        "P",
        "M_H",
        "M_B",
        "R",
    }:
        errors.append("Mapped protocol blocks changed.")
    if validated_map.get("affected_partitions") != list(queries.SCHEDULE_IDS):
        errors.append("Affected partition list changed.")

    plan_errors = run_pilot.validate_plan(plan)
    errors.extend(f"Event plan: {error}." for error in plan_errors)
    if plan.get("local_union_bridge", {}).get("sha256") != queries.file_sha256(
        queries.UNION_BRIDGE_PATH
    ):
        errors.append("Pilot union bridge hash changed.")
    if receipt.get("status") != "complete" or receipt.get(
        "completed_event_count"
    ) != 18:
        errors.append("Source run receipt is incomplete.")
    if receipt.get("event_plan_sha256") != queries.file_sha256(
        searches / "event-plan.json"
    ):
        errors.append("Source run receipt does not bind the event plan.")

    event_errors: list[str] = []
    png_paths: set[Path] = set()
    if not plan_errors:
        for event in plan.get("events", []):
            output = searches / event["output"]
            try:
                summary = run_pilot.strict_artifact_summary(event, output, plan)
            except Exception as error:
                event_errors.append(f"{event.get('event_id')}: {error}")
                continue
            for screenshot in summary["screenshots"].values():
                png_paths.add(queries.PILOT_ROOT / screenshot["path"])
    errors.extend(event_errors)
    if len(png_paths) != 36 or not all(path.is_file() for path in png_paths):
        errors.append("The 18 source events do not retain 36 mandatory PNGs.")

    if comparison.get("status") != "complete_no_descriptor_only_records":
        errors.append("Set comparison status changed.")
    partition_comparisons = comparison.get("partition_comparisons", {})
    if set(partition_comparisons) != set(queries.SCHEDULE_IDS):
        errors.append("Set comparison lacks a partition.")
    else:
        for partition_id, expected_total in EXPECTED_TOTALS.items():
            item = partition_comparisons[partition_id]
            if not all(
                (
                    item.get("free_text_total") == expected_total,
                    item.get("augmented_total") == expected_total,
                    item.get("descriptor_only_total") == 0,
                    item.get("sets_equal") is True,
                    item.get("orders_equal") is True,
                )
            ):
                errors.append(f"{partition_id} comparison changed.")
    union = comparison.get("union_comparison", {})
    if not all(
        (
            union.get("free_text_distinct_ids") == 29,
            union.get("augmented_distinct_ids") == 29,
            union.get("descriptor_only_total") == 0,
            union.get("sets_equal") is True,
        )
    ):
        errors.append("Schedule union comparison changed.")

    if review.get("status") != "complete_empty_review_frame":
        errors.append("Descriptor-only review is incomplete.")
    if review.get("descriptor_only_record_count") != 0 or review.get("records") != []:
        errors.append("Descriptor-only review frame is no longer empty.")
    if assessment.get("decision") != "do_not_add_pq_subject_or_index_term_supplement":
        errors.append("Controlled-term decision changed.")
    if assessment.get("accepted_descriptors") != []:
        errors.append("Assessment unexpectedly accepts a descriptor.")
    evidence = assessment.get("evidence", {})
    if evidence.get("descriptor_only_record_count") != 0:
        errors.append("Assessment descriptor-only count changed.")
    if evidence.get("mapped_protocol_blocks") != ["P", "M_H", "M_B", "R"]:
        errors.append("Assessment mapped-block order changed.")

    historical_plan = load(searches / "event-plan.before-union-bridge.json")
    historical_receipt = load(searches / "run-receipt.before-union-bridge.json")
    if historical_plan.get("event_count") != 18:
        errors.append("Pre-bridge event plan was not preserved.")
    if historical_receipt.get("status") != "stopped_on_source_or_adapter_failure":
        errors.append("Pre-bridge stopped receipt was not preserved.")
    failure_paths = sorted((searches / "failures").glob("*.json"))
    if len(failure_paths) != 5:
        errors.append("Expected five retained setup or browser failures.")
    for path in failure_paths:
        failure = load(path)
        if failure.get("status") != "error" or failure.get("do_not_merge") is not True:
            errors.append(f"Historical failure is malformed: {path.name}.")

    guideline = guideline_path.read_text(encoding="utf-8")
    for required in (
        "Add no `PSUB.EXACT` or `IF.EXACT` supplement",
        "[Pilot 005](pilots/005/pilot.md)",
        "Both schedule unions contained 29 IDs",
        "without a controlled-term supplement",
    ):
        if required not in guideline:
            errors.append(f"Source guideline lacks: {required}.")
    tasks = tasks_path.read_text(encoding="utf-8")
    if "**PQDT-005: Test PQ Subject and Index term value.**" not in tasks:
        errors.append("TASKS.md lacks PQDT-005 completion.")

    pilot_path = queries.PILOT_ROOT / "pilot.md"
    pilot_text = pilot_path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", pilot_text):
        if target.startswith(("http://", "https://", "#")):
            continue
        resolved = (pilot_path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            errors.append(f"Pilot Markdown link is missing: {target}.")

    try:
        spec = importlib.util.spec_from_file_location(
            "pqdt_pilot005_validated_union_bridge", queries.UNION_BRIDGE_PATH
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load union bridge")
        bridge = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = bridge
        spec.loader.exec_module(bridge)
        adapter = bridge.load_adapter()
        bridge.install_raw_union_bridge(adapter)
        bridge.assert_bridge_scope(adapter)
    except Exception as error:
        errors.append(f"Pilot union bridge check failed: {error}.")

    return {
        "schema_version": "pqdt-global-pilot005-validation-report/v1",
        "source": "ProQuest Dissertations & Theses Global",
        "pilot": "005",
        "status": "ok" if not errors else "error",
        "checks": {
            "preflight": "passed" if not any("Preflight" in error for error in errors) else "failed",
            "two_pass_assignment_harvest": "passed" if assignments.get("pass_reconciliation", {}).get("ordered_assignments_equal") is True else "failed",
            "two_pass_exact_label_validation": "passed" if candidate_validation.get("verified_exact_label_count") == 27 else "failed",
            "validated_block_mapping": "passed" if set(validated_map.get("controlled_constructions", {})) == {"P", "M_H", "M_B", "R"} else "failed",
            "strict_source_events": "passed" if not event_errors else "failed",
            "mandatory_screenshots": "passed" if len(png_paths) == 36 else "failed",
            "set_comparison": "passed" if union.get("sets_equal") is True and union.get("descriptor_only_total") == 0 else "failed",
            "descriptor_only_review": "passed" if review.get("status") == "complete_empty_review_frame" else "failed",
            "decision_synchronized": "passed" if assessment.get("accepted_descriptors") == [] else "failed",
            "historical_failures_preserved": "passed" if len(failure_paths) == 5 else "failed",
            "local_markdown_links": "passed" if not any("Markdown link" in error for error in errors) else "failed",
        },
        "summary": {
            "selected_records": 14,
            "unique_pq_subject_terms": 9,
            "unique_index_terms": 42,
            "validated_exact_candidates": 27,
            "mapped_blocks": ["P", "M_H", "M_B", "R"],
            "strict_events": 18,
            "mandatory_pngs": len(png_paths),
            "free_text_union_ids": union.get("free_text_distinct_ids"),
            "augmented_union_ids": union.get("augmented_distinct_ids"),
            "descriptor_only_ids": union.get("descriptor_only_total"),
            "accepted_descriptors": len(assessment.get("accepted_descriptors", [])),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guideline", type=Path, default=DEFAULT_GUIDELINE)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = validate(
        args.guideline.expanduser().resolve(), args.tasks.expanduser().resolve()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "ok":
        for error in report["errors"]:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
