#!/usr/bin/env python3
"""Validate IAF Pilot 005 and its bounded positive wildcard conclusion."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from assess import build as build_assessment
from build_plan import PILOT_ROOT, SLR1_DIR, load, validate

EXPECTED_IDS = {
    "cube": [
        "iaf-digital-library:IAC-2019:50318",
        "iaf-digital-library:IAC-2015:29581",
        "iaf-digital-library:IAC-2014:21335",
    ],
    "other": [
        "iaf-digital-library:IAC-2019:50318",
        "iaf-digital-library:IAC-2017:41414",
    ],
    "full_set": {
        "iaf-digital-library:IAC-2019:50318",
        "iaf-digital-library:IAC-2017:41414",
        "iaf-digital-library:IAC-2015:29581",
        "iaf-digital-library:IAC-2014:21335",
    },
}


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
    plan_path = searches / "event-plan.json"
    plan = load(plan_path)
    errors.extend(validate(plan))
    receipt = load(searches / "run-receipt.json")
    if (
        receipt.get("status") != "complete"
        or receipt.get("predeclared_event_count") != 7
        or receipt.get("completed_event_count") != 7
        or receipt.get("outcome_count") != 7
        or receipt.get("source_attempt_count") != 7
        or receipt.get("reused_existing_event_count") != 0
        or receipt.get("retained_failure_artifacts") != []
        or any(item.get("status") != "complete" for item in receipt.get("outcomes", []))
    ):
        errors.append("The live run receipt changed")

    assessment = load(searches / "assessment.json")
    regenerated = build_assessment(root, plan_path)
    if regenerated.get("status") != "complete" or regenerated.get("errors"):
        errors.extend(
            f"Regenerated assessment: {error}"
            for error in regenerated.get("errors", [])
        )
    if assessment.get("comparisons") != regenerated.get("comparisons"):
        errors.append("Saved comparisons differ from the source artifacts")
    if (
        assessment.get("status") != "complete"
        or assessment.get("decision")
        != "positive_wildcard_equivalence_confirmed_in_bounded_bg1_context"
        or assessment.get("canonical_schedule_decision", {}).get("changed") is not False
        or assessment.get("source_artifact_count") != 7
        or assessment.get("retained_failure_artifacts") != []
    ):
        errors.append("The bounded wildcard decision changed")

    cube = assessment.get("comparisons", {}).get("cube_family", {})
    other = assessment.get("comparisons", {}).get("other_family", {})
    full = assessment.get("comparisons", {}).get("full_population", {})
    if (
        cube.get("explicit_ids") != EXPECTED_IDS["cube"]
        or cube.get("wildcard_ids") != EXPECTED_IDS["cube"]
        or cube.get("sets_equal") is not True
        or cube.get("non_zero") is not True
    ):
        errors.append("The cube-family comparison changed")
    if (
        other.get("explicit_ids") != EXPECTED_IDS["other"]
        or other.get("wildcard_ids") != EXPECTED_IDS["other"]
        or other.get("sets_equal") is not True
        or other.get("non_zero") is not True
    ):
        errors.append("The other-family comparison changed")
    if (
        set(full.get("explicit_ids", [])) != EXPECTED_IDS["full_set"]
        or set(full.get("wildcard_pass1_ids", [])) != EXPECTED_IDS["full_set"]
        or full.get("wildcard_pass1_ids") != full.get("wildcard_pass2_ids")
        or full.get("sets_equal") is not True
        or full.get("repeated_order_equal") is not True
        or full.get("fresh_explicit_matches_pilot004") is not True
        or full.get("non_zero") is not True
    ):
        errors.append("The full-population comparison changed")
    acceptance = assessment.get("acceptance", {})
    if (
        acceptance.get("all_comparison_groups_non_zero") is not True
        or acceptance.get("all_explicit_ids_retained") is not True
        or acceptance.get("all_comparison_sets_equal") is not True
        or acceptance.get("full_wildcard_repeat_stable") is not True
        or acceptance.get("fresh_explicit_baseline_reproduced") is not True
        or acceptance.get("wildcard_only_record_count") != 0
    ):
        errors.append("Wildcard acceptance evidence changed")
    if assessment.get("compression") != {
        "explicit_population_terms": 26,
        "wildcard_population_atoms": 8,
        "explicit_full_query_characters": 773,
        "wildcard_full_query_characters": 447,
        "character_reduction": 326,
        "explicit_source_cells": 3,
        "wildcard_source_cells": 1,
    }:
        errors.append("The measured compression changed")

    event_files = sorted((searches / "events").glob("*.json"))
    artifacts = [
        path
        for path in event_files
        if not path.name.startswith(".")
        and not path.name.endswith(".identity-ledger.json")
    ]
    ledgers = [
        path for path in event_files if path.name.endswith(".identity-ledger.json")
    ]
    markers = sorted((searches / "events").glob(".*.ACADEMIC_SEARCH_COMMIT.json"))
    failures = list((searches / "failures").glob("*.json"))
    cleanup = list((searches / "events").glob(".ACADEMIC_SEARCH_OUTPUT_CLEANUP.*"))
    if len(artifacts) != 7 or len(ledgers) != 7 or len(markers) != 7:
        errors.append("The source artifact, ledger, or marker count changed")
    if failures:
        errors.append("Unexpected retained source failures exist")
    if cleanup:
        errors.append("Transient output cleanup directories remain")

    guideline_text = guideline.read_text(encoding="utf-8")
    for required in (
        "Wildcard population `F_W(P)`",
        "These eight atoms replace the 26 explicit `P` terms",
        "The complete wildcard schedule contains 158 cells.",
    ):
        if required not in guideline_text:
            errors.append(f"The guideline lacks Pilot 005 text: {required}")

    pilot = root / "pilot.md"
    pilot_text = pilot.read_text(encoding="utf-8")
    for required in (
        "Test documented trailing `*` on a non-zero review search.",
        "| Cube family | 3 | 3 | 0 | 0 |",
        "| Other population family | 2 | 2 | 0 | 0 |",
        "| Full population | 4 | 4 | 0 | 0 |",
        "from 773 to 447 characters",
        "Keep the current 551-cell explicit schedule as the canonical route.",
    ):
        if required not in pilot_text:
            errors.append(f"The pilot document lacks validated text: {required}")
    task_text = (SLR1_DIR / "TASKS.md").read_text(encoding="utf-8")
    if "**IAF-005: Test trailing wildcards on a positive search.**" not in task_text:
        errors.append("TASKS.md is not synchronized")
    errors.extend(markdown_link_errors(pilot))
    errors.extend(markdown_link_errors(guideline))

    return {
        "schema_version": "iaf-digital-library-pilot005-validation-report/v1",
        "status": "ok" if not errors else "error",
        "pilot": "005",
        "diagnostic_only": True,
        "do_not_merge": True,
        "checks": {
            "predeclared_plan": "passed" if not validate(plan) else "failed",
            "strict_source_events": "passed"
            if len(artifacts) == 7 and regenerated.get("status") == "complete"
            else "failed",
            "positive_comparisons": "passed"
            if acceptance.get("all_comparison_groups_non_zero") is True
            else "failed",
            "stable_id_equivalence": "passed"
            if acceptance.get("all_comparison_sets_equal") is True
            else "failed",
            "full_wildcard_repeat": "passed"
            if acceptance.get("full_wildcard_repeat_stable") is True
            else "failed",
            "bounded_canonical_decision": "passed"
            if assessment.get("canonical_schedule_decision", {}).get("changed") is False
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
            "source_events": len(artifacts),
            "identity_ledgers": len(ledgers),
            "commit_markers": len(markers),
            "retained_failures": len(failures),
            "comparison_counts": {"cube": 3, "other": 2, "full": 4},
            "wildcard_only_records": 0,
            "explicit_query_characters": 773,
            "wildcard_query_characters": 447,
            "explicit_cells": 3,
            "wildcard_cells": 1,
            "canonical_schedule_changed": False,
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
