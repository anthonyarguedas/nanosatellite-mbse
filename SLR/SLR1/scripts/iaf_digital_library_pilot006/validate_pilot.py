#!/usr/bin/env python3
"""Validate IAF Pilot 006 and the approved population wildcard schedule."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from assess import build as build_assessment
from build_plan import (
    EXPECTED_CELL_COUNTS,
    PILOT_ROOT,
    SLR1_DIR,
    load,
    queries,
    validate,
)

EXPECTED_RESULTS = {
    "A1": {"event_sum": 5, "raw": 2, "window": 2},
    "A2": {"event_sum": 24, "raw": 12, "window": 11},
    "A3": {"event_sum": 8, "raw": 7, "window": 7},
    "B1": {"event_sum": 72, "raw": 42, "window": 39},
    "B2": {"event_sum": 154, "raw": 57, "window": 53},
    "BG1": {"event_sum": 4, "raw": 4, "window": 4},
    "BG2": {"event_sum": 4, "raw": 4, "window": 2},
    "BC1": {"event_sum": 9, "raw": 9, "window": 6},
    "BT2": {"event_sum": 8, "raw": 6, "window": 5},
}
EXPECTED_FAILURES = ["A1/cell-0015", "A2/cell-0028", "B2/cell-0001"]


def markdown_link_errors(markdown: Path) -> list[str]:
    errors = []
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        local = target.split("#", 1)[0]
        if local and not (markdown.parent / local).resolve().exists():
            errors.append(f"Missing Markdown link in {markdown}: {target}")
    return errors


def validate_pilot(root: Path, guideline: Path) -> dict[str, Any]:
    errors: list[str] = []
    searches = root / "searches"
    plan_path = searches / "cell-plan.json"
    plan = load(plan_path)
    errors.extend(validate(plan))
    receipt = load(searches / "run-receipt.json")
    if (
        receipt.get("status") != "complete"
        or receipt.get("selected_partitions") != list(queries.SCHEDULE_IDS)
        or receipt.get("predeclared_cell_count") != 158
        or receipt.get("completed_cell_count") != 158
        or receipt.get("outcome_count") != 161
        or receipt.get("source_attempt_count") != 161
        or receipt.get("reused_existing_cell_count") != 0
        or len(receipt.get("retained_failure_artifacts", [])) != 3
    ):
        errors.append("The live run receipt changed")

    assessment = load(searches / "assessment.json")
    threshold = load(searches / "threshold-investigations.json")
    regenerated, regenerated_threshold = build_assessment(root, plan_path)
    if regenerated.get("status") != "complete" or regenerated.get("errors"):
        errors.extend(
            f"Regenerated assessment: {error}"
            for error in regenerated.get("errors", [])
        )
    if assessment.get("entries") != regenerated.get("entries"):
        errors.append("Saved partition entries differ from source artifacts")
    if threshold != regenerated_threshold:
        errors.append("Saved threshold evidence differs from source artifacts")
    if (
        assessment.get("status") != "complete"
        or assessment.get("decision")
        != "approve_eight_atom_population_wildcard_for_all_partitions"
        or assessment.get("canonical_schedule_decision", {}).get("changed") is not True
        or assessment.get("source_artifact_count") != 158
    ):
        errors.append("The wildcard approval decision changed")
    acceptance = assessment.get("acceptance", {})
    if (
        acceptance.get("all_nine_partitions_complete") is not True
        or acceptance.get("all_raw_unions_equal") is not True
        or acceptance.get("all_diagnostic_window_unions_equal") is not True
        or acceptance.get("missing_explicit_id_count") != 0
        or acceptance.get("wildcard_only_id_count") != 0
        or acceptance.get("result_driven_filters_added") is not False
    ):
        errors.append("The all-partition acceptance evidence changed")
    canonical = assessment.get("canonical_schedule_decision", {})
    if (
        canonical.get("schedule_cells_before") != 551
        or canonical.get("schedule_cells_after") != 158
        or canonical.get("cell_reduction") != 393
        or canonical.get("cell_reduction_percent") != 71.32
        or canonical.get("wildcard_scope") != "IAF population block P only"
    ):
        errors.append("The approved schedule compression changed")

    for partition_id, expected in EXPECTED_RESULTS.items():
        entry = assessment.get("entries", {}).get(partition_id, {})
        if (
            entry.get("complete_cells") != EXPECTED_CELL_COUNTS[partition_id]
            or entry.get("raw_source_event_total_sum") != expected["event_sum"]
            or entry.get("raw_union", {}).get("count") != expected["raw"]
            or entry.get("diagnostic_window_union", {}).get("count")
            != expected["window"]
            or entry.get("raw_union", {}).get("sets_equal") is not True
            or entry.get("diagnostic_window_union", {}).get("sets_equal") is not True
            or entry.get("raw_union", {}).get("missing_explicit_ids") != []
            or entry.get("raw_union", {}).get("wildcard_only_ids") != []
            or entry.get("diagnostic_window_union", {}).get("missing_explicit_ids")
            != []
            or entry.get("diagnostic_window_union", {}).get("wildcard_only_ids") != []
        ):
            errors.append(f"The validated result changed for {partition_id}")

    failure_summary = assessment.get("retained_failure_summary", {})
    if (
        failure_summary.get("count") != 3
        or failure_summary.get("failed_cells") != EXPECTED_FAILURES
        or failure_summary.get("all_recovered_by_unchanged_query_retry") is not True
        or failure_summary.get("failure_stage")
        != "before exact executed-query observation"
    ):
        errors.append("The retained failure history changed")
    if (
        threshold.get("status") != "not_triggered"
        or threshold.get("threshold") != 100
        or threshold.get("triggered_partitions") != []
    ):
        errors.append("The threshold decision changed")

    cell_json = sorted((searches / "cells").glob("*/*.json"))
    cell_artifacts = [
        path
        for path in cell_json
        if not path.name.startswith(".")
        and not path.name.endswith(".identity-ledger.json")
    ]
    ledgers = [
        path for path in cell_json if path.name.endswith(".identity-ledger.json")
    ]
    cell_markers = sorted((searches / "cells").glob("*/.*.ACADEMIC_SEARCH_COMMIT.json"))
    failure_artifacts = sorted(
        path
        for path in (searches / "failures").rglob("*.NON_MERGEABLE_FAILURE.json")
        if not path.name.startswith(".")
    )
    failure_markers = sorted(
        (searches / "failures").glob("*/.*.ACADEMIC_SEARCH_COMMIT.json")
    )
    cleanup = list(searches.rglob(".ACADEMIC_SEARCH_OUTPUT_CLEANUP.*"))
    if len(cell_artifacts) != 158 or len(ledgers) != 158 or len(cell_markers) != 158:
        errors.append("The successful source artifact counts changed")
    if len(failure_artifacts) != 3 or len(failure_markers) != 3:
        errors.append("The retained failure artifact counts changed")
    if cleanup:
        errors.append("Transient output cleanup directories remain")

    guideline_text = guideline.read_text(encoding="utf-8")
    for required in (
        "Use the trailing wildcard translation for the population block only.",
        "Wildcard population `F_W(P)`",
        'CubeSat* OR "cube sat*" OR cube-sat* OR nanosat*',
        "These eight atoms replace the 26 explicit `P` terms",
        "The complete wildcard schedule contains 158 cells.",
        "| `A1` | `F_W(P) AND F(E_H) AND F(M_H)` | 37 |",
        "| `BT2` | `F_W(P) AND F(M_B) AND F(T_precise)` | 13 |",
    ):
        if required not in guideline_text:
            errors.append(f"The guideline lacks Pilot 006 text: {required}")

    pilot = root / "pilot.md"
    pilot_text = pilot.read_text(encoding="utf-8")
    for required in (
        "Test the positive Pilot 005 population wildcard candidate in every current partition.",
        "| **Total** | **551** | **158** | **393** |",
        "| `A1` | 37 | 5 | 2 | 2 | 2 | 0 | 0 |",
        "| `B2` | 20 | 154 | 57 | 53 | 53 | 0 | 0 |",
        "| `BT2` | 13 | 8 | 6 | 5 | 5 | 0 | 0 |",
        "Approve the wildcard translation with eight atoms for the IAF population block.",
        "a 71.32% reduction",
    ):
        if required not in pilot_text:
            errors.append(f"The pilot document lacks validated text: {required}")
    task_text = (SLR1_DIR / "TASKS.md").read_text(encoding="utf-8")
    if "**IAF-006: Test population wildcards across all partitions.**" not in task_text:
        errors.append("TASKS.md is not synchronized")
    errors.extend(markdown_link_errors(pilot))
    errors.extend(markdown_link_errors(guideline))

    return {
        "schema_version": "iaf-digital-library-pilot006-validation-report/v1",
        "status": "ok" if not errors else "error",
        "pilot": "006",
        "diagnostic_only": True,
        "do_not_merge": True,
        "checks": {
            "predeclared_all_partition_plan": "passed"
            if not validate(plan)
            else "failed",
            "strict_source_cells": "passed"
            if len(cell_artifacts) == 158 and regenerated.get("status") == "complete"
            else "failed",
            "raw_union_equivalence": "passed"
            if acceptance.get("all_raw_unions_equal") is True
            else "failed",
            "diagnostic_window_union_equivalence": "passed"
            if acceptance.get("all_diagnostic_window_unions_equal") is True
            else "failed",
            "no_missing_or_wildcard_only_ids": "passed"
            if acceptance.get("missing_explicit_id_count") == 0
            and acceptance.get("wildcard_only_id_count") == 0
            else "failed",
            "retained_failures_recovered": "passed"
            if failure_summary.get("all_recovered_by_unchanged_query_retry") is True
            else "failed",
            "wildcard_schedule_approved": "passed"
            if canonical.get("changed") is True
            else "failed",
            "guideline_synchronized": "passed"
            if not any("guideline" in error.lower() for error in errors)
            else "failed",
            "task_synchronized": "passed"
            if not any("TASKS.md" in error for error in errors)
            else "failed",
            "local_markdown_links": "passed"
            if not any("Markdown link" in error for error in errors)
            else "failed",
        },
        "summary": {
            "partitions": 9,
            "successful_source_cells": len(cell_artifacts),
            "identity_ledgers": len(ledgers),
            "success_markers": len(cell_markers),
            "retained_failed_attempts": len(failure_artifacts),
            "failure_markers": len(failure_markers),
            "explicit_schedule_cells": 551,
            "approved_wildcard_schedule_cells": 158,
            "cell_reduction": 393,
            "cell_reduction_percent": 71.32,
            "missing_explicit_ids": 0,
            "wildcard_only_ids": 0,
            "partition_results": EXPECTED_RESULTS,
            "canonical_schedule_changed": True,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_pilot(args.pilot_root, args.guideline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
