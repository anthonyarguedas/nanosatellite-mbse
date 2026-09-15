#!/usr/bin/env python3
"""Validate AIAA ARC Pilot 007 plans, unions, recall, and documentation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_assessment import build
from build_plan import build as build_plan

EXPECTED_UNIONS = {
    "A1": 18,
    "A2": 40,
    "A3": 12,
    "B1": 37,
    "B2": 23,
    "BG1": 44,
    "BG2": 2,
    "BC1": 36,
    "BT2": 11,
}
EXPECTED_CELLS = {
    "A1": 9,
    "A2": 9,
    "A3": 9,
    "B1": 9,
    "B2": 9,
    "BG1": 1,
    "BG2": 36,
    "BC1": 3,
    "BT2": 9,
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def check(condition: bool, name: str, checks: list[dict[str, Any]], detail: str = "") -> None:
    checks.append({"check": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise RuntimeError(f"Validation failed: {name}. {detail}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--pilot-document", type=Path, required=True)
    parser.add_argument("--gitignore", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    search_root = args.pilot_root / "searches"
    assessment = load(search_root / "assessment.json")
    check(assessment == build(args.pilot_root, args.pilot006_root), "assessment_rebuild", checks)
    check(load(search_root / "event-plan.json") == build_plan(), "plan_rebuild", checks)
    check(assessment.get("status") == "complete", "assessment_complete", checks)
    check(assessment["execution"]["total_cells"] == 94, "all_94_cells", checks)
    check(assessment["execution"]["all_cells_complete"] is True, "all_cells_complete", checks)
    check(assessment["execution"]["largest_cell_total"] == 45, "largest_cell_45", checks)

    for partition, expected in EXPECTED_UNIONS.items():
        entry = assessment["partition_unions"][partition]
        check(entry["cell_count"] == EXPECTED_CELLS[partition], f"{partition}_cell_count", checks)
        check(entry["canonical_doi_union_count"] == expected, f"{partition}_union_count", checks)
        check(entry["maximum_cell_total"] <= 100, f"{partition}_bounded", checks)
        check(entry["cell_total_sum"] == entry["raw_source_event_count"], f"{partition}_reconciliation", checks)

    check(assessment["overall_union"]["canonical_doi_count"] == 119, "overall_119", checks)
    known = assessment["known_item_recall"]
    check(known["retrieved"] == {"A2": True, "B1": True, "B2": True, "BC1": True}, "known_item_all_partitions", checks)
    check(known["all_applicable_partitions_retrieved"] is True, "known_item_gate_passed", checks)
    comparison = assessment["factor_wise_comparison"]
    check(comparison["pilot006_union_count"] == 47, "factor_wise_47", checks)
    check(comparison["hybrid_union_count"] == 119, "hybrid_119", checks)
    check(comparison["intersection_count"] == 47, "factor_intersection_47", checks)
    check(comparison["hybrid_additional_count"] == 72, "hybrid_additional_72", checks)
    check(comparison["factor_wise_only_count"] == 0, "no_factor_only_loss", checks)

    screenshots = assessment["screenshots"]
    check(screenshots["required_screenshot_count"] == 188, "required_188_screenshots", checks)
    check(screenshots["verified_success_screenshot_count"] == 188, "verified_188_screenshots", checks)
    check(screenshots["all_png_count_including_failed_attempts"] == 189, "all_189_pngs", checks)
    check(screenshots["ignored_by_project_git"] is True, "screenshots_gitignored", checks)
    failures = assessment["retained_failures"]
    check(failures["count"] == 3, "retained_three_failures", checks)
    check(failures["all_recovered"] is True, "failures_recovered", checks)
    check(not list(args.pilot_root.rglob(".*.tmp")), "no_atomic_temp_links", checks)

    decision = assessment["decision"]
    check(decision["hybrid_route"] == "accept_prospective_canonical_screening_translation", "hybrid_accepted", checks)
    check(decision["screening_workload"] == "feasible_119_canonical_dois", "workload_feasible", checks)
    check(decision["full_Anywhere_schedule"] == "retain_as_sensitivity_evidence_not_screening_corpus", "Anywhere_sensitivity_only", checks)

    guideline = args.guideline.read_text()
    pilot_document = args.pilot_document.read_text()
    for text in (
        "Pilot 007 accepted hybrid route",
        "119` canonical DOIs",
        "prospective canonical screening translation",
        "META(P) AND META(M_B) AND ANY(R)",
        "Do not use the complete Anywhere schedule as the screening corpus",
    ):
        check(text.casefold() in guideline.casefold(), f"guideline_contains_{text}", checks)
    for text in (
        "# Pilot 007",
        "119 canonical DOIs",
        "retrieved it in all four applicable partitions",
        "94 cells",
        "188 required screenshots",
        "prospective canonical AIAA screening translation",
    ):
        check(text.casefold() in pilot_document.casefold(), f"pilot_contains_{text}", checks)

    ignore_text = args.gitignore.read_text()
    check("/SLR/SLR1/source-specific/**/*.png" in ignore_text, "png_gitignore_rule", checks)
    check("/SLR/SLR1/source-specific/**/*.jpg" in ignore_text, "jpg_gitignore_rule", checks)

    report = {
        "schema_version": "aiaa-arc-pilot007-validation/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "007",
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
