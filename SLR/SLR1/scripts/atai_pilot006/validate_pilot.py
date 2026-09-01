#!/usr/bin/env python3

"""Validate ATAI Pilot 006 artifacts and prospective source decisions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
EXPECTED_IF_COUNTS = {
    "A1": (0, 0),
    "A2": (5, 5),
    "A3": (1, 1),
    "B1": (19, 25),
    "B2": (29, 34),
    "BG1": (2, 2),
    "BG2": (7, 7),
    "BC1": (1, 2),
    "BT2": (2, 3),
}
EXPECTED_LANGUAGE_COUNTS = {
    "A1": (0, 0),
    "A2": (5, 5),
    "A3": (1, 1),
    "B1": (25, 25),
    "B2": (36, 34),
    "BG1": (2, 2),
    "BG2": (7, 7),
    "BC1": (2, 2),
    "BT2": (3, 3),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def validate(root: Path, guideline: Path) -> dict[str, Any]:
    errors = []
    searches = root / "searches"
    assessment = load(searches / "assessment.json")
    if assessment.get("status") != "complete":
        errors.append("Assessment is incomplete.")
    decisions = assessment.get("decisions", {})
    expected_decisions = {
        "NOFT_field_coverage": "validated_for_TI_AB_MAINSUBJECT_but_not_IF",
        "indexed_keyword_translation": "accept_IF_EXACT_OR_supplement_for_every_ordinary_literal",
        "pair_translation": "retain_NOFT_NEAR_5",
        "language_filter": "retain_LA_English",
    }
    if decisions != expected_decisions:
        errors.append("Assessment decisions changed.")

    for name, expected_status in (
        ("run-receipt.json", "stopped_on_source_or_adapter_failure"),
        ("run-receipt-retry1.json", "stopped_on_source_or_adapter_failure"),
        ("run-receipt-retry2.json", "complete"),
        ("run-receipt-retry3.json", "complete"),
        ("run-receipt-retry7.json", "complete"),
    ):
        if load(searches / name).get("status") != expected_status:
            errors.append(f"Run receipt {name} has the wrong status.")

    field = assessment.get("field_coverage", {})
    known = field.get("known_item_contrasts", [])
    if len(known) != 3 or any(not item.get("same_stable_id") for item in known):
        errors.append("Title, abstract, or subject NOFT known-item coverage failed.")
    repeated_index = field.get("indexed_keyword_contrast", {}).get("repeated_totals")
    if repeated_index != {
        "pass_1": {"IF_exact": 1, "NOFT": 0},
        "pass_2": {"IF_exact": 1, "NOFT": 0},
    }:
        errors.append("IF versus NOFT known-item contrast changed.")

    pair = assessment.get("pair_validation", {})
    pair_records = pair.get("positive_records", [])
    if (
        [record.get("paper_id") for record in pair_records] != ["1825532815", "2728408177"]
        or [record.get("local_abstract_minimum_intervening_words") for record in pair_records] != [3, 4]
        or pair.get("cross_field_negative", {}).get("source_total") != 0
    ):
        errors.append("Pair validation changed.")

    if_assessment = assessment.get("indexed_keyword_assessment", {})
    if if_assessment.get("candidate_only_union_total") != 9:
        errors.append("IF candidate-only union is not nine.")
    if if_assessment.get("plausible_review_candidate_count") != 6:
        errors.append("IF plausible-candidate count is not six.")
    if if_assessment.get("historical_literal_union_overlap") != []:
        errors.append("IF-only candidates overlap the historical literal union.")
    for partition, expected in EXPECTED_IF_COUNTS.items():
        value = if_assessment.get("two_pass_partition_counts", {}).get(partition, {})
        if (value.get("literal"), value.get("if_augmented")) != expected or value.get("passes_equal") is not True:
            errors.append(f"IF counts changed for {partition}.")

    if_ids = load(searches / "if-stable-id-reconciliation.json")
    if if_ids.get("status") != "complete_two_pass_card_id_reconciliation" or if_ids.get("candidate_only_union_total") != 9:
        errors.append("IF stable-ID reconciliation is incomplete.")
    details = load(searches / "candidate-detail-harvest.json")
    if details.get("status") != "complete_two_pass_detail_readback" or details.get("record_count") != 11:
        errors.append("Candidate detail harvest is incomplete.")

    language = assessment.get("language_assessment", {})
    if language.get("excluded_stable_ids") != ["896198854", "2621176457"]:
        errors.append("Language-excluded stable IDs changed.")
    for record in language.get("excluded_records", []):
        if record.get("language_of_publication") != "Chinese":
            errors.append("A language-excluded record is not source-labelled Chinese.")
    for partition, expected in EXPECTED_LANGUAGE_COUNTS.items():
        value = language.get("two_pass_final_partition_counts", {}).get(partition, {})
        if (value.get("unfiltered"), value.get("english")) != expected or value.get("passes_equal") is not True:
            errors.append(f"Final language counts changed for {partition}.")
    final_exclusions = load(searches / "final-language-exclusion-id-reconciliation.json")
    if final_exclusions.get("stable_ids_in_source_order") != ["896198854", "2621176457"]:
        errors.append("Final language exclusion reconciliation changed.")

    marking = load(searches / "nonmergeable-marking.json")
    marked_paths = marking.get("marked_artifacts", [])
    if marking.get("status") != "complete" or marking.get("marked_artifact_count") != len(marked_paths):
        errors.append("Non-mergeable marking receipt is invalid.")
    source_artifacts = []
    for path in searches.rglob("*.json"):
        value = load(path)
        if value.get("schema_version") == "academic-search-result/v1":
            source_artifacts.append(path)
            metadata = value.get("output_metadata", {})
            if value.get("do_not_merge") is not True or metadata.get("merge_eligible") is not False:
                errors.append(f"Source artifact is mergeable: {path.relative_to(root)}")
    if len(source_artifacts) != marking.get("marked_artifact_count"):
        errors.append("Non-mergeable marking count does not cover every source artifact.")

    guideline_text = guideline.read_text()
    required_guideline_text = (
        'Atom `A(s)`: `(NOFT(L(s)) OR IF.EXACT(L(s)))`',
        "Both excluded records were source-labelled `Language of publication: Chinese`",
        "[Pilot 006](pilots/006/pilot.md)",
    )
    for text in required_guideline_text:
        if text not in guideline_text:
            errors.append(f"Guideline lacks Pilot 006 decision text: {text}")
    pair_translation_retained = "Do not emulate a pair in `IF`" in guideline_text
    pair_translation_superseded = (
        "Use no proximity operators, pair expansions, or wildcards." in guideline_text
        and "[Pilot 007](pilots/007/pilot.md)" in guideline_text
    )
    if not pair_translation_retained and not pair_translation_superseded:
        errors.append("Guideline neither retains nor explicitly supersedes the Pilot 006 pair decision.")

    pilot = root / "pilot.md"
    pilot_text = pilot.read_text()
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", pilot_text):
        if target.startswith(("http://", "https://", "#")):
            continue
        path = (pilot.parent / target.split("#", 1)[0]).resolve()
        if not path.exists():
            errors.append(f"Pilot Markdown link is missing: {target}")

    return {
        "schema_version": "atai-pilot-006-validation-report/v1",
        "status": "ok" if not errors else "error",
        "checks": {
            "retained_failures": "passed" if not any("receipt" in error.lower() for error in errors) else "failed",
            "NOFT_field_contrasts": "passed" if len(known) == 3 else "failed",
            "IF_gap_detected": "passed" if repeated_index else "failed",
            "pair_gate": "passed" if not any("Pair" in error for error in errors) else "failed",
            "IF_marginal_recall": "passed" if if_assessment.get("candidate_only_union_total") == 9 else "failed",
            "language_audit": "passed" if language.get("excluded_stable_ids") == ["896198854", "2621176457"] else "failed",
            "all_source_artifacts_nonmergeable": "passed" if len(source_artifacts) == marking.get("marked_artifact_count") else "failed",
            "guideline_synchronized": "passed" if not any("Guideline" in error for error in errors) else "failed",
            "local_markdown_links": "passed" if not any("Markdown link" in error for error in errors) else "failed",
        },
        "summary": {
            "source_artifact_count": len(source_artifacts),
            "NOFT_positive_fields": ["TI", "AB", "MAINSUBJECT"],
            "NOFT_missing_field": "IF",
            "pair_positive_records": 2,
            "cross_field_pair_total": 0,
            "IF_candidate_only_ids": 9,
            "IF_plausible_candidates": 6,
            "final_language_excluded_ids": 2,
            "final_language_excluded_source_language": "Chinese",
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.pilot_root, args.guideline)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
