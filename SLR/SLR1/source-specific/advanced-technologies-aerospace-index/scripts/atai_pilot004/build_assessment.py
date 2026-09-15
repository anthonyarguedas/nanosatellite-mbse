#!/usr/bin/env python3

"""Build the ATAI Pilot 004 controlled-vocabulary inclusion decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SELECTED_IDS = (
    "3371247439",
    "3062738113",
    "2035264195",
    "1825532815",
    "3110716244",
    "3181339955",
    "1709719593",
)
POPULATION_TERMS = ("Cubesat", "Nanosatellites", "Small satellites")
MBSE_TERMS = ("Model-based systems", "Systems engineering", "Modelling")


def ordered_hash(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def build(harvest_path: Path, candidates_path: Path, comparison_path: Path) -> dict[str, Any]:
    harvest = load(harvest_path)
    candidates = load(candidates_path)
    comparison = load(comparison_path)
    if harvest.get("status") != "complete_two_pass_readback":
        raise RuntimeError("Assigned-term harvest is incomplete.")
    if candidates.get("status") != "complete_two_pass_readback":
        raise RuntimeError("Descriptor validation is incomplete.")
    if comparison.get("status") != "complete_two_pass_stable_id_comparison":
        raise RuntimeError("Set comparison is incomplete.")

    records = harvest.get("records", [])
    selected_ids = [record.get("paper_id") for record in records]
    if tuple(selected_ids) != SELECTED_IDS:
        raise RuntimeError("Selected known records changed.")
    verified = [
        item
        for item in candidates.get("candidates", [])
        if item.get("status") == "verified_exact_technology_thesaurus_descriptor"
    ]
    verified_terms = [item["term"] for item in verified]
    expected_terms = set(POPULATION_TERMS) | set(MBSE_TERMS)
    if set(verified_terms) != expected_terms:
        raise RuntimeError("Exact descriptor validation changed.")

    cells = comparison.get("cells", {})
    literal_ids = cells["B1-literal"]["stable_ids_in_source_order"]
    augmented_ids = cells["B1-augmented"]["stable_ids_in_source_order"]
    known_mapping = comparison["known_set_mapping"]
    candidate_only = comparison["comparison"]["candidate_only_ids"]
    if literal_ids != augmented_ids or candidate_only:
        raise RuntimeError("Current evidence no longer supports a zero-gain decision.")
    if not set(SELECTED_IDS).issubset(set(literal_ids)):
        raise RuntimeError("Literal B1 did not retrieve every selected known record.")
    if known_mapping["matched_count"] != 5:
        raise RuntimeError("Known-set controlled mapping count changed.")

    literal_query = cells["B1-literal"]["query"]
    literal_atoms = {
        match.casefold()
        for match in re.findall(r'NOFT\("([^"]+)"\)', literal_query)
    }
    population_lexical_coverage = {
        term: term.casefold() in literal_atoms for term in POPULATION_TERMS
    }
    if not all(population_lexical_coverage.values()):
        raise RuntimeError("A population descriptor no longer duplicates a literal.")

    return {
        "schema_version": "atai-controlled-vocabulary-inclusion-assessment/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "source_id": "proquest_aerospace_index",
        "platform": "ProQuest",
        "pilot": "004",
        "status": "complete",
        "do_not_merge": True,
        "decision": "do_not_add_controlled_vocabulary_supplement",
        "decision_scope": "Current ATAI source translation and the descriptors tested from seven user-selected Pilot 003 records.",
        "inputs": {
            "assigned_term_harvest": str(harvest_path),
            "descriptor_validation": str(candidates_path),
            "set_comparison": str(comparison_path),
        },
        "evidence": {
            "selected_known_record_count": len(SELECTED_IDS),
            "selected_known_record_ids": list(SELECTED_IDS),
            "unique_assigned_subject_term_count": harvest["unique_rendered_indexing_term_count"],
            "exact_technology_thesaurus_descriptors": verified_terms,
            "exact_descriptor_count": len(verified_terms),
            "population_descriptor_lexical_coverage": population_lexical_coverage,
            "known_records_retrieved_by_literal_B1": len(SELECTED_IDS),
            "known_records_matching_candidate_controlled_M_H_construction": known_mapping["matched_count"],
            "known_records_not_matching_candidate_controlled_M_H_construction": known_mapping["unmatched_selected_ids"],
            "literal_B1_total": len(literal_ids),
            "augmented_B1_total": len(augmented_ids),
            "literal_B1_ordered_id_sha256": ordered_hash(literal_ids),
            "augmented_B1_ordered_id_sha256": ordered_hash(augmented_ids),
            "ordered_ids_equal": literal_ids == augmented_ids,
            "candidate_only_total": len(candidate_only),
            "candidate_only_ids": candidate_only,
        },
        "criteria": [
            {
                "criterion": "source_mapping_and_assignment",
                "result": "passed_bounded",
                "reason": "Six assigned SUBJECT labels were exact Technology Thesaurus descriptors with exact MAINSUBJECT insertion read back twice.",
            },
            {
                "criterion": "preserve_normative_free_text",
                "result": "passed",
                "reason": "The candidate used OR supplements and retained every literal B1 factor.",
            },
            {
                "criterion": "marginal_stable_id_recall",
                "result": "failed_to_show_value",
                "reason": "Fresh literal and augmented B1 runs each returned the same ordered 19 stable IDs in two passes, with zero candidate-only IDs.",
            },
            {
                "criterion": "known_relevant_record_rescue",
                "result": "failed_to_show_value",
                "reason": "Literal B1 already retrieved all seven selected records. The candidate controlled MBSE construction matched only five of them.",
            },
            {
                "criterion": "reproducible_vocabulary_identity",
                "result": "limited",
                "reason": "The source publishes no stable descriptor IDs, vocabulary release, or explosion state.",
            },
        ],
        "rationale": [
            "The three population descriptors repeat existing literal labels modulo case and spacing.",
            "The context-qualified MBSE descriptor construction added no B1 record.",
            "B1 is the broad P × M_H partition. Its zero descriptor-only result also rules out gain from the same M_H supplement in narrower A1 and the M_H arm of A2 under these controls.",
            "Requiring controlled terms would lose two selected records, so descriptors cannot replace free text.",
            "An OR supplement adds query complexity without observed recall gain.",
        ],
        "accepted_descriptors": [],
        "prospective_translation": "Retain the literal NOFT schedule with no Technology Thesaurus supplement.",
        "limitations": [
            "The test covers B1 and descriptors assigned to seven selected records. It does not prove that no future descriptor could add recall in another block.",
            "The selected records are known relevant for this vocabulary pilot only. This artifact is not final review screening.",
            "Pilot results are non-mergeable and do not finalize the ATAI search.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harvest", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assessment = build(args.harvest, args.candidates, args.comparison)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assessment, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
