#!/usr/bin/env python3

"""Build the Compendex Pilot 004 controlled-vocabulary decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def build(
    preflight_path: Path,
    assignments_path: Path,
    candidates_path: Path,
    comparison_path: Path,
) -> dict[str, Any]:
    preflight = load(preflight_path)
    assignments = load(assignments_path)
    candidates = load(candidates_path)
    comparison = load(comparison_path)
    expected_status = {
        "preflight": (preflight, "complete"),
        "assignments": (assignments, "complete_two_pass_assignment_readback"),
        "candidates": (candidates, "complete_two_pass_readback"),
        "comparison": (comparison, "complete_two_pass_terminal_cell_comparison"),
    }
    for name, (artifact, status) in expected_status.items():
        if artifact.get("status") != status:
            raise RuntimeError(f"The {name} artifact is incomplete")
        if artifact.get("protocol_commit") != queries.PROTOCOL_COMMIT:
            raise RuntimeError(f"The {name} artifact uses a different protocol commit")
        if artifact.get("do_not_merge") is not True:
            raise RuntimeError(f"The {name} artifact is not explicitly diagnostic")

    candidate_by_term = {
        candidate["term"]: candidate for candidate in candidates.get("candidates", [])
    }
    exact_required = (
        "Nanosatellites",
        "Small satellites",
        "Systems engineering",
        "Modeling languages",
    )
    for term in exact_required:
        candidate = candidate_by_term.get(term, {})
        if candidate.get("status") != "verified_exact_preferred_ei_thesaurus_term":
            raise RuntimeError(f"Required descriptor {term!r} is no longer exact")
        if candidate.get("selected_record_assignment_count", 0) < 1:
            raise RuntimeError(f"Required descriptor {term!r} lacks assignment evidence")
    if candidate_by_term.get("SysML", {}).get("selected_record_assignment_count") != 0:
        raise RuntimeError("SysML assignment evidence changed")
    if candidate_by_term.get("Model-based systems engineering", {}).get("status") != "not_an_exact_preferred_ei_thesaurus_term":
        raise RuntimeError("Direct MBSE descriptor availability changed")
    if candidate_by_term.get("CubeSat", {}).get("status") != "not_an_exact_preferred_ei_thesaurus_term":
        raise RuntimeError("Direct CubeSat descriptor availability changed")

    cells = comparison.get("cells", {})
    required_cells = set(queries.VALUE_CELLS)
    if set(cells) != required_cells or not all(cells[cell]["passes_equal"] for cell in required_cells):
        raise RuntimeError("The value comparison lacks stable two-pass cells")
    candidate_only = comparison.get("comparison", {}).get("candidate_only_accessions")
    if candidate_only != []:
        raise RuntimeError("Current evidence no longer supports a zero-gain decision")
    if comparison["comparison"]["candidate_only_union_count"] != 0:
        raise RuntimeError("Candidate-only union count changed")

    known_count = comparison["known_set_mapping"]["selected_record_count"]
    p_known = comparison["known_set_mapping"]["P_controlled_matched_count"]
    mh_known = comparison["known_set_mapping"]["M_H_controlled_matched_count"]
    sysml_known = comparison["known_set_mapping"]["SysML_controlled_matched_count"]
    if (known_count, p_known, mh_known, sysml_known) != (11, 3, 3, 0):
        raise RuntimeError("Known-set controlled-vocabulary mapping changed")

    exact_summary = [
        {
            "term": term,
            "term_id": candidate_by_term[term]["term_id"],
            "field": candidate_by_term[term]["field"],
            "assigned_record_count": candidate_by_term[term][
                "selected_record_assignment_count"
            ],
        }
        for term in exact_required
    ]
    return {
        "schema_version": "compendex-controlled-vocabulary-inclusion-assessment/v1",
        "source": "Compendex",
        "source_id": "compendex",
        "platform": "Engineering Village",
        "pilot": "004",
        "status": "complete",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "decision": "do_not_add_ei_thesaurus_supplement",
        "decision_scope": (
            "The current post-proximity Compendex P and M_H translations and the "
            "assigned descriptors tested against B1."
        ),
        "inputs": {
            "preflight": "preflight.json",
            "assignment_harvest": "assigned-controlled-terms.json",
            "candidate_validation": "ei-thesaurus-candidates.json",
            "value_comparison": "value-comparison.json",
        },
        "schedule_provenance": {
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "changed_partitions": list(queries.CHANGED_BY_PROTOCOL_COMMIT),
            "B1_change_state": "unchanged_P_AND_M_H",
            "value_test_query": "current post-proximity B1",
            "Pilot_003_use": "assignment evidence only for unchanged B1",
            "superseded_proximity_results_used_for_value": False,
        },
        "evidence": {
            "selected_known_record_count": known_count,
            "unique_assigned_controlled_term_count": assignments[
                "unique_controlled_term_count"
            ],
            "exact_assigned_candidate_descriptors": exact_summary,
            "context_qualified_M_H": (
                "{Systems engineering} WN CV AND {Modeling languages} WN CV"
            ),
            "joint_M_H_assignment_count": assignments[
                "context_qualified_M_H_assignment"
            ]["assigned_record_count"],
            "direct_MBSE_descriptor": "not an exact preferred Ei Thesaurus term",
            "direct_CubeSat_descriptor": "not an exact preferred Ei Thesaurus term",
            "SysML_descriptor": {
                "exact": True,
                "selected_record_assignment_count": 0,
            },
            "known_P_controlled_matches": p_known,
            "known_M_H_controlled_matches": mh_known,
            "known_SysML_controlled_matches": sysml_known,
            "B1_M_H_candidate_only_total": cells["B1-MH-candidate-only"]["total"],
            "B1_P_candidate_only_total": cells["B1-P-candidate-only"]["total"],
            "B1_candidate_only_union_total": 0,
            "B1_candidate_only_accessions": [],
        },
        "criteria": [
            {
                "criterion": "post_proximity_schedule",
                "result": "passed",
                "reason": (
                    "The preflight is pinned to commit 3194156 and renders all nine "
                    "partitions without proximity, pair expansion, or wildcards."
                ),
            },
            {
                "criterion": "source_mapping",
                "result": "passed_bounded",
                "reason": (
                    "Four assigned labels were exact preferred Ei Thesaurus concepts with "
                    "numeric IDs, hierarchy, scope-note, and no-explosion evidence read twice."
                ),
            },
            {
                "criterion": "known_record_assignment",
                "result": "passed_bounded",
                "reason": (
                    "Two historical native B1 RIS passes had identical assignments, and fresh "
                    "terminal one-page CV checks reproduced the expected P and M_H known sets."
                ),
            },
            {
                "criterion": "preserve_normative_free_text",
                "result": "passed",
                "reason": (
                    "The candidate constructions were OR supplements to complete P and M_H "
                    "free-text blocks."
                ),
            },
            {
                "criterion": "marginal_B1_recall",
                "result": "failed_to_show_value",
                "reason": (
                    "Both lossless candidate-only routes returned explicit source zero twice, "
                    "so the tested augmented B1 added no Compendex accession."
                ),
            },
            {
                "criterion": "replacement_safety",
                "result": "failed",
                "reason": (
                    "The P and context-qualified M_H controlled constructions each matched only "
                    "3 of 11 selected records. Controlled terms cannot replace free text."
                ),
            },
            {
                "criterion": "hierarchy_expansion",
                "result": "not_requested",
                "reason": (
                    "The source exposed navigational relations without an explode control. "
                    "No broader or narrower concept was silently included."
                ),
            },
        ],
        "rationale": [
            "Nanosatellites and Small satellites repeat normative population labels in a distinct CV field but added no B1 record.",
            "Systems engineering is too generic for M_H alone and was tested only with Modeling languages.",
            "The context-qualified M_H construction had assignment evidence but added no B1 record.",
            "SysML was an exact descriptor but had no selected-record assignment, so it failed the fixed assignment criterion.",
            "The exact direct labels Model-based systems engineering and CubeSat were absent from the preferred-term surface.",
            "An OR supplement with zero observed marginal recall adds complexity without evidence of value.",
        ],
        "accepted_descriptors": [],
        "prospective_translation": (
            "Retain the complete post-proximity literal ALL schedule with no Ei Thesaurus "
            "supplement. Keep free text mandatory."
        ),
        "adapter_repair": {
            "state": "validated_v15",
            "finding": (
                "Engineering Village omits the numeric result interval and mirrors the legacy "
                "Next ID. Adapter v15 accepts the absent interval as optional corroboration, "
                "scopes the top paginator, and waits through the brief empty-row shell after "
                "one click. Bounded one-page, two-page, strict, and paired checks passed."
            ),
        },
        "limitations": [
            "The value test covers P and M_H candidates in B1. It does not prove that every possible descriptor for every other concept lacks value.",
            "The eleven records are vocabulary known items, not final screening decisions.",
            "Pilot 003 assignments are reused only because B1 was unchanged by the protocol commit.",
            "The portal exposes no Ei Thesaurus release identifier or documented concept-ID stability guarantee.",
            "The adapter repair validates capture behavior. No current full schedule or final search was run.",
            "No current changed-partition Pilot 003 set, final search, or merge-eligible pilot artifact was created.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(
        args.preflight, args.assignments, args.candidates, args.comparison
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
