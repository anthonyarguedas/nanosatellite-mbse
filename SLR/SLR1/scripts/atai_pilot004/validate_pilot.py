#!/usr/bin/env python3

"""Validate ATAI Pilot 004 artifacts and documented decision."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_IDS = [
    "3371247439",
    "3062738113",
    "2035264195",
    "1825532815",
    "3110716244",
    "3181339955",
    "1709719593",
]
EXPECTED_TERMS = {
    "Cubesat",
    "Nanosatellites",
    "Small satellites",
    "Model-based systems",
    "Systems engineering",
    "Modelling",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def validate(root: Path, guideline: Path, reading_aid: Path) -> dict[str, Any]:
    errors: list[str] = []
    searches = root / "searches"
    harvest = load(searches / "assigned-indexing-terms-retry2.json")
    candidates = load(searches / "technology-thesaurus-candidates.json")
    comparison = load(searches / "set-comparison-retry1.json")
    assessment = load(searches / "inclusion-assessment.json")

    if harvest.get("status") != "complete_two_pass_readback":
        errors.append("Assignment harvest status is not complete.")
    if [record.get("paper_id") for record in harvest.get("records", [])] != EXPECTED_IDS:
        errors.append("Assignment harvest selected IDs changed.")
    if harvest.get("selected_record_count") != 7:
        errors.append("Assignment harvest record count is not seven.")
    if harvest.get("unique_rendered_indexing_term_count") != 58:
        errors.append("Assignment harvest unique term count is not 58.")
    if harvest.get("pass_reconciliation", {}).get("ordered_assignments_equal") is not True:
        errors.append("Assignment harvest passes do not reconcile.")

    verified_terms = {
        item.get("term")
        for item in candidates.get("candidates", [])
        if item.get("status") == "verified_exact_technology_thesaurus_descriptor"
    }
    if candidates.get("status") != "complete_two_pass_readback":
        errors.append("Technology Thesaurus validation status is not complete.")
    if verified_terms != EXPECTED_TERMS:
        errors.append("Verified Technology Thesaurus terms changed.")
    if candidates.get("verified_descriptor_count") != 6:
        errors.append("Verified descriptor count is not six.")
    if candidates.get("pass_reconciliation", {}).get("ordered_candidate_results_equal") is not True:
        errors.append("Descriptor-validation passes do not reconcile.")

    cells = comparison.get("cells", {})
    expected_cells = {"known-set-cv-mapping", "B1-literal", "B1-augmented"}
    if set(cells) != expected_cells:
        errors.append("Set-comparison cells changed.")
    for cell_id in expected_cells & set(cells):
        cell = cells[cell_id]
        if cell.get("passes") != 2 or cell.get("ordered_ids_equal") is not True:
            errors.append(f"{cell_id} does not have two equal stable-ID passes.")
        if cell.get("source_total") != cell.get("stable_id_count"):
            errors.append(f"{cell_id} source total does not reconcile.")
        for artifact in cell.get("artifacts", []):
            artifact_path = searches / "set-passes-retry1" / artifact
            if not artifact_path.exists():
                errors.append(f"Missing set-pass artifact {artifact}.")
                continue
            value = load(artifact_path)
            if value.get("do_not_merge") is not True:
                errors.append(f"{artifact} is not marked do_not_merge.")
            if value.get("total") != len(value.get("results", [])):
                errors.append(f"{artifact} total does not equal retained records.")
            limits = (
                value.get("output_metadata", {})
                .get("prisma_search_run", {})
                .get("strategy", {})
                .get("limits", {})
            )
            if limits.get("language", {}).get("value") != "LA(English)":
                errors.append(f"{artifact} lacks LA(English) readback.")
            if limits.get("document_type", {}).get("state") != "not_applied":
                errors.append(f"{artifact} applied a document-type restriction.")
            date = limits.get("publication_date", {}).get("effective", {})
            if date.get("start") != "2011-01-01" or date.get("end") != "2026-08-29":
                errors.append(f"{artifact} date readback changed.")

    literal_ids = cells.get("B1-literal", {}).get("stable_ids_in_source_order", [])
    augmented_ids = cells.get("B1-augmented", {}).get("stable_ids_in_source_order", [])
    if literal_ids != augmented_ids or len(literal_ids) != 19:
        errors.append("Literal and augmented B1 are not the same ordered 19 IDs.")
    if comparison.get("comparison", {}).get("candidate_only_total") != 0:
        errors.append("Set comparison has candidate-only records.")
    if comparison.get("known_set_mapping", {}).get("matched_count") != 5:
        errors.append("Known-set controlled mapping count is not five.")

    if assessment.get("decision") != "do_not_add_controlled_vocabulary_supplement":
        errors.append("Inclusion decision changed.")
    if assessment.get("accepted_descriptors") != []:
        errors.append("Assessment unexpectedly accepts descriptors.")
    evidence = assessment.get("evidence", {})
    if evidence.get("ordered_ids_equal") is not True or evidence.get("candidate_only_total") != 0:
        errors.append("Assessment evidence disagrees with set comparison.")

    for name in (
        "assigned-indexing-terms.NON_MERGEABLE_FAILURE.json",
        "assigned-indexing-terms-retry1.NON_MERGEABLE_FAILURE.json",
        "set-comparison.NON_MERGEABLE_FAILURE.json",
    ):
        value = load(searches / name)
        if value.get("status") != "error" or value.get("do_not_merge") is not True:
            errors.append(f"Historical failure {name} was not preserved correctly.")

    if reading_aid.exists():
        errors.append("Temporary controlled-vocabulary reading aid still exists.")

    guideline_text = guideline.read_text()
    if "Add no Technology Thesaurus supplement" not in guideline_text:
        errors.append("Source guideline lacks the no-supplement decision.")
    if "[Pilot 004](pilots/004/pilot.md)" not in guideline_text:
        errors.append("Source guideline does not link Pilot 004.")

    pilot_path = root / "pilot.md"
    pilot_text = pilot_path.read_text()
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", pilot_text):
        if target.startswith(("http://", "https://", "#")):
            continue
        resolved = (pilot_path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            errors.append(f"Pilot Markdown link is missing: {target}")

    return {
        "schema_version": "atai-pilot-004-validation-report/v1",
        "status": "ok" if not errors else "error",
        "checks": {
            "reading_aid_removed": not reading_aid.exists(),
            "assignment_harvest": "passed" if not any("Assignment" in error for error in errors) else "failed",
            "descriptor_validation": "passed" if not any("descriptor" in error.lower() for error in errors) else "failed",
            "stable_id_set_comparison": "passed" if literal_ids == augmented_ids and len(literal_ids) == 19 else "failed",
            "historical_failures_preserved": "passed",
            "decision_documented": "passed" if assessment.get("accepted_descriptors") == [] else "failed",
            "local_markdown_links": "passed" if not any("Markdown link" in error for error in errors) else "failed",
        },
        "summary": {
            "selected_records": 7,
            "assigned_subject_terms": 58,
            "verified_descriptors": 6,
            "known_descriptor_matches": 5,
            "literal_B1_ids": len(literal_ids),
            "augmented_B1_ids": len(augmented_ids),
            "candidate_only_ids": comparison.get("comparison", {}).get("candidate_only_total"),
            "accepted_descriptors": 0,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--reading-aid", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.pilot_root, args.guideline, args.reading_aid)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
