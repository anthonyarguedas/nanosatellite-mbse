#!/usr/bin/env python3
"""Validate Pilot 006 plans, unions, screenshots, decisions, and docs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from build_assessment import build
from build_core_plan import build as build_core_plan
from build_plan import build as build_expanded_plan

EXPECTED_UNIONS = {
    "A1": 1,
    "A2": 1,
    "A3": 1,
    "B1": 37,
    "B2": 17,
    "BG1": 0,
    "BG2": 2,
    "BC1": 3,
    "BT2": 1,
}
EXPECTED_CELLS = {
    "A1": 27,
    "A2": 27,
    "A3": 27,
    "B1": 9,
    "B2": 27,
    "BG1": 36,
    "BG2": 36,
    "BC1": 9,
    "BT2": 27,
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
    parser.add_argument("--pilot005-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--pilot-document", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    search_root = args.pilot_root / "searches"
    assessment = load(search_root / "assessment.json")
    rebuilt = build(args.pilot_root, args.pilot005_root)
    check(assessment == rebuilt, "assessment_rebuild", checks)
    check(load(search_root / "event-plan.json") == build_expanded_plan(), "expanded_plan_rebuild", checks)
    check(load(search_root / "core-event-plan.json") == build_core_plan(), "core_plan_rebuild", checks)
    check(assessment.get("status") == "complete", "assessment_complete", checks)
    check(assessment["route"]["total_cells"] == 225, "all_225_cells", checks)
    check(assessment["route"]["all_cells_complete"] is True, "all_cells_complete", checks)
    check(assessment["route"]["all_cells_at_most_100"] is True, "all_cells_bounded", checks)

    for partition, expected in EXPECTED_UNIONS.items():
        entry = assessment["partition_unions"][partition]
        check(entry["cell_count"] == EXPECTED_CELLS[partition], f"{partition}_cell_count", checks)
        check(entry["canonical_doi_union_count"] == expected, f"{partition}_union_count", checks)
        check(entry["maximum_cell_total"] <= 100, f"{partition}_maximum_cell_total", checks)
        check(entry["cell_total_sum"] == entry["raw_source_event_count"], f"{partition}_event_reconciliation", checks)

    check(assessment["overall_union"]["canonical_doi_count"] == 47, "overall_47_doi_union", checks)
    known = assessment["known_item_recall"]
    check(known["retrieved"] == {"A2": False, "B1": True, "B2": False, "BC1": True}, "known_item_partition_gate", checks)
    check(known["gate"] == "rejected_metadata_only_canonical_route", "known_item_rejection", checks)
    bg1 = assessment["BG1_complete_allfield_comparison"]
    check(bg1["allfield_canonical_doi_count"] == 44, "BG1_allfield_44", checks)
    check(bg1["metadata_canonical_doi_count"] == 0, "BG1_metadata_zero", checks)
    check(bg1["allfield_only_count"] == 44, "BG1_observed_loss_44", checks)

    screenshots = assessment["screenshots"]
    check(screenshots["required_screenshot_count"] == 450, "required_450_screenshots", checks)
    check(screenshots["verified_success_screenshot_count"] == 450, "verified_450_screenshots", checks)
    check(screenshots["all_png_count_including_failed_attempts"] == 473, "all_473_pngs", checks)
    check(screenshots["no_opt_out"] is True, "screenshot_no_opt_out", checks)
    failures = assessment["retained_failures"]
    check(failures["count"] == 13, "retained_13_failures", checks)
    check(failures["all_recovered"] is True, "all_failures_recovered", checks)
    check(not list(args.pilot_root.rglob(".*.tmp")), "no_atomic_temp_links", checks)

    decision = assessment["decision"]
    check(decision["canonical_replacement_for_Anywhere"] == "rejected_observed_known_item_recall_loss", "canonical_route_rejected", checks)
    check(decision["screening_priority_lane"] == "accepted_nonexcluding", "priority_lane_accepted", checks)
    check(decision["direct_Anywhere_route"] == "retain_as_canonical", "Anywhere_retained", checks)

    guideline = args.guideline.read_text()
    pilot_document = args.pilot_document.read_text()
    for text in (
        "Pilot 006",
        "225 cells",
        "47` canonical DOIs",
        "missed known eligible DOI",
        "mandatory full-page configured-search and first-results screenshots",
    ):
        check(text.casefold() in guideline.casefold(), f"guideline_contains_{text}", checks)
    for text in (
        "# Pilot 006",
        "factor-wise",
        "225 cells",
        "47 canonical DOIs",
        "A2 and B2",
        "450 required screenshots",
        "no screenshot opt-out",
    ):
        check(text.casefold() in pilot_document.casefold(), f"pilot_contains_{text}", checks)

    adapter_text = args.adapter.read_text()
    check('ADAPTER_VERSION = "5"' in adapter_text, "adapter_version_5", checks)
    check("--preview-cards-only" in adapter_text, "adapter_card_preview", checks)
    check(".search-page.png" in adapter_text and ".results-page.png" in adapter_text, "adapter_screenshot_names", checks)
    check("--no-screenshot" not in adapter_text, "adapter_has_no_screenshot_opt_out", checks)
    help_result = subprocess.run(
        [sys.executable, str(args.adapter), "--help"],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    check(help_result.returncode == 0, "adapter_help_exit", checks, help_result.stderr[-500:])
    check("--preview-cards-only" in help_result.stdout, "adapter_help_card_preview", checks)
    check("--no-screenshot" not in help_result.stdout, "adapter_help_no_opt_out", checks)

    report = {
        "schema_version": "aiaa-arc-pilot006-validation/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "006",
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
