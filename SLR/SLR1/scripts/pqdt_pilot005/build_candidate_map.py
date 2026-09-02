#!/usr/bin/env python3
"""Map assigned PQDT labels to bounded protocol-block candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries

SCHEMA = "pqdt-global-pilot005-candidate-map/v1"
DEFAULT_ASSIGNMENTS = queries.PILOT_ROOT / "searches" / "assigned-terms.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "candidate-map.json"

CANDIDATES: tuple[dict[str, Any], ...] = (
    {"candidate_id": "IF-P-01", "field": "IF", "term": "CubeSats", "blocks": ["P"], "role": "Exact population label."},
    {"candidate_id": "IF-P-02", "field": "IF", "term": "Cube Satellites", "blocks": ["P"], "role": "Exact population phrase modulo source capitalization."},
    {"candidate_id": "IF-P-03", "field": "IF", "term": "CubeSat", "blocks": ["P"], "role": "Exact population label."},
    {"candidate_id": "IF-P-04", "field": "IF", "term": "Cubesats", "blocks": ["P"], "role": "Exact population label modulo source capitalization."},
    {"candidate_id": "IF-P-05", "field": "IF", "term": "CubeSat design", "blocks": ["P"], "role": "Narrower assigned label that entails a CubeSat population."},
    {"candidate_id": "IF-P-06", "field": "IF", "term": "Cubesat designs", "blocks": ["P"], "role": "Narrower assigned label that entails a CubeSat population."},
    {"candidate_id": "IF-P-07", "field": "IF", "term": "CubeSats environmental testing", "blocks": ["P"], "role": "Narrower assigned label that entails a CubeSat population."},
    {"candidate_id": "IF-P-08", "field": "IF", "term": "Lunar CubeSat Missions", "blocks": ["P"], "role": "Narrower assigned label that entails a CubeSat population."},
    {"candidate_id": "IF-P-09", "field": "IF", "term": "Small Satellites", "blocks": ["P"], "role": "Exact population phrase modulo source capitalization."},
    {"candidate_id": "IF-P-10", "field": "IF", "term": "Small satellites", "blocks": ["P"], "role": "Exact population phrase."},
    {"candidate_id": "IF-MH-01", "field": "IF", "term": "Model-based systems engineering", "blocks": ["M_H"], "role": "Specific assigned MBSE label."},
    {"candidate_id": "IF-MH-02", "field": "IF", "term": "MBSE", "blocks": ["M_H"], "role": "Specific assigned MBSE acronym."},
    {"candidate_id": "IF-MH-03", "field": "IF", "term": "SysML", "blocks": ["M_H"], "role": "Specific assigned systems modeling language label."},
    {"candidate_id": "IF-MH-04", "field": "IF", "term": "Systems Modeling Language", "blocks": ["M_H"], "role": "Specific assigned systems modeling language phrase."},
    {"candidate_id": "PSUB-MH-CONTEXT-01", "field": "PSUB", "assigned_term": "Systems engineering", "term": "systems engineering", "blocks": ["M_H_context"], "role": "Lower-case browse candidate for the assigned generic systems engineering context. It cannot satisfy M_H alone."},
    {"candidate_id": "IF-MH-CONTEXT-01", "field": "IF", "term": "Systems engineering", "blocks": ["M_H_context"], "role": "Generic systems engineering context. It cannot satisfy M_H alone."},
    {"candidate_id": "IF-MH-MODEL-01", "field": "IF", "term": "System modeling", "blocks": ["M_H_model_context", "M_B"], "role": "Assigned model descriptor. It requires systems engineering context for M_H and maps directly to M_B."},
    {"candidate_id": "IF-MH-MODEL-02", "field": "IF", "term": "Executable modeling", "blocks": ["M_H_model_context"], "role": "Assigned modeling descriptor. It requires systems engineering context for M_H."},
    {"candidate_id": "IF-MB-01", "field": "IF", "term": "Digital Engineering", "blocks": ["M_B"], "role": "Exact broad structured-model label modulo source capitalization."},
    {"candidate_id": "IF-MB-02", "field": "IF", "term": "Digital engineering", "blocks": ["M_B"], "role": "Exact broad structured-model label."},
    {"candidate_id": "IF-MB-03", "field": "IF", "term": "Digital Twin", "blocks": ["M_B"], "role": "Exact broad structured-model label modulo source capitalization."},
    {"candidate_id": "IF-MB-04", "field": "IF", "term": "System architecture model", "blocks": ["M_B"], "role": "Exact broad structured-model phrase."},
    {"candidate_id": "IF-R-01", "field": "IF", "assigned_term": "Architecture", "term": "architecture", "blocks": ["R"], "role": "Lower-case browse candidate for the assigned architecture concern."},
    {"candidate_id": "IF-R-02", "field": "IF", "term": "Mission architecture", "blocks": ["R"], "role": "Narrower architecture concern."},
    {"candidate_id": "IF-R-03", "field": "IF", "assigned_term": "System architecture", "term": "system architecture", "blocks": ["R"], "role": "Lower-case browse candidate for the assigned system architecture concern."},
    {"candidate_id": "IF-R-04", "field": "IF", "term": "Requirements prioritization", "blocks": ["R"], "role": "Narrower requirements concern."},
    {"candidate_id": "IF-R-05", "field": "IF", "term": "Scalable systems architecture", "blocks": ["R"], "role": "Narrower architecture concern. Scalable does not establish a reusable artifact."},
    {"candidate_id": "PSUB-R-01", "field": "PSUB", "assigned_term": "Product design", "term": "product design", "blocks": ["R"], "role": "Lower-case browse candidate for the assigned product design concern."},
)

EXCLUSIONS: tuple[dict[str, Any], ...] = (
    {
        "field": "PSUB",
        "term": "Budgets",
        "proposed_block": "E_F",
        "decision": "reject_mapping",
        "reason": "The unqualified subject covers budgets outside electrical power and energy.",
    },
    {
        "field": "IF",
        "term": "Evaluation",
        "proposed_block": "R",
        "decision": "reject_mapping",
        "reason": "The generic label does not establish a declared relationship, analysis, verification, or validation concern.",
    },
    {
        "field": "IF",
        "term": "Test",
        "proposed_block": "R",
        "decision": "reject_mapping",
        "reason": "The protocol does not use generic test as a direct-discovery relationship term.",
    },
    {
        "field": "IF",
        "term": "Scalable systems architecture",
        "proposed_block": "G_structure",
        "decision": "reject_mapping",
        "reason": "Scalable does not by itself establish a reusable structural artifact.",
    },
    {
        "field": "SUBJECT",
        "term": "Power and related broad Subject labels",
        "proposed_block": "E_H or E_F",
        "decision": "outside_candidate_fields",
        "reason": "The record page exposes these through the broader SUBJECT route, not the separately validated PSUB or IF indexes.",
    },
)


def assignment_index(artifact: dict[str, Any]) -> dict[tuple[str, str], list[str]]:
    index: dict[tuple[str, str], list[str]] = {}
    for record in artifact.get("records", []):
        paper_id = record["paper_id"]
        for term in record.get("pq_subject_terms", []):
            index.setdefault(("PSUB", term), []).append(paper_id)
        for term in record.get("index_terms", []):
            index.setdefault(("IF", term), []).append(paper_id)
    return index


def clause(candidate: dict[str, Any]) -> str:
    return queries.exact_clause(candidate["field"], candidate["term"])


def by_id(candidates: list[dict[str, Any]], *candidate_ids: str) -> list[str]:
    wanted = set(candidate_ids)
    found = [item["executed_clause"] for item in candidates if item["candidate_id"] in wanted]
    if len(found) != len(wanted):
        raise RuntimeError(f"Candidate construction is incomplete: {sorted(wanted)!r}")
    return found


def build(assignments_path: Path) -> dict[str, Any]:
    assignments = queries.load_object(assignments_path)
    if assignments.get("status") != "complete_two_pass_assignment_readback":
        raise RuntimeError("PQDT assigned-term harvest is incomplete")
    if assignments.get("pass_reconciliation", {}).get("ordered_assignments_equal") is not True:
        raise RuntimeError("PQDT assigned-term passes do not reconcile")
    index = assignment_index(assignments)

    mapped: list[dict[str, Any]] = []
    for declared in CANDIDATES:
        assigned_term = declared.get("assigned_term", declared["term"])
        assigned_ids = index.get((declared["field"], assigned_term), [])
        if not assigned_ids:
            raise RuntimeError(
                f"Candidate {declared['field']} {assigned_term!r} lacks selected-record assignment"
            )
        mapped.append(
            {
                **declared,
                "assigned_term": assigned_term,
                "status": "assigned_pending_exact_browse_validation",
                "executed_clause": clause(declared),
                "assigned_record_count": len(assigned_ids),
                "assigned_document_ids": assigned_ids,
                "term_id": None,
                "vocabulary_version": None,
                "expansion": None,
                "major_topic": False,
            }
        )

    p_ids = [item["candidate_id"] for item in mapped if item["blocks"] == ["P"]]
    direct_mh_ids = [
        item["candidate_id"] for item in mapped if item["blocks"] == ["M_H"]
    ]
    context_ids = [
        "PSUB-MH-CONTEXT-01",
        "IF-MH-CONTEXT-01",
    ]
    model_context_ids = ["IF-MH-MODEL-01", "IF-MH-MODEL-02"]
    mb_ids = [
        item["candidate_id"]
        for item in mapped
        if "M_B" in item["blocks"]
    ]
    r_ids = [item["candidate_id"] for item in mapped if item["blocks"] == ["R"]]

    p_expression = queries.any_of(*by_id(mapped, *p_ids))
    direct_mh = queries.any_of(*by_id(mapped, *direct_mh_ids))
    context_mh = queries.all_of(
        queries.any_of(*by_id(mapped, *context_ids)),
        queries.any_of(*by_id(mapped, *model_context_ids)),
    )
    descriptor_expressions = {
        "P": p_expression,
        "M_H": queries.any_of(direct_mh, context_mh),
        "M_B": queries.any_of(*by_id(mapped, *mb_ids)),
        "R": queries.any_of(*by_id(mapped, *r_ids)),
    }
    _, _, augmented = queries.build_augmented_schedule_from_expressions(
        descriptor_expressions
    )
    affected = [
        partition_id
        for partition_id in queries.SCHEDULE_IDS
        if augmented[partition_id] != queries.FREE_TEXT_SCHEDULE[partition_id]
    ]
    if affected != list(queries.SCHEDULE_IDS):
        raise RuntimeError("The P descriptor supplement should affect every partition")

    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "mapped_pending_exact_browse_validation",
        "diagnostic_only": True,
        "do_not_merge": True,
        "input_assignments": str(assignments_path.relative_to(queries.PILOT_ROOT)),
        "input_assignments_sha256": queries.file_sha256(assignments_path),
        "mapping_policy": {
            "free_text_mandatory": True,
            "mapped_fields": ["PSUB.EXACT", "IF.EXACT"],
            "term_ids": "not_exposed",
            "vocabulary_versions": "not_published",
            "hierarchy": "not_exposed",
            "explosion": "not_requested",
            "major_topic": False,
            "same_descriptor_across_blocks": (
                "Each construction retains its block role. System modeling maps to M_B "
                "directly and appears in M_H only with a systems engineering context."
            ),
        },
        "candidate_count": len(mapped),
        "candidates": mapped,
        "controlled_constructions": {
            block: {
                "protocol_block": block,
                "expression": expression,
                "expression_sha256": queries.sha256_text(expression),
                "combination_with_free_text": "OR",
            }
            for block, expression in descriptor_expressions.items()
        },
        "unmapped_or_rejected_examples": list(EXCLUSIONS),
        "affected_partitions": affected,
        "baseline_query_sha256": {
            key: queries.sha256_text(value)
            for key, value in queries.FREE_TEXT_SCHEDULE.items()
        },
        "augmented_query_sha256": {
            key: queries.sha256_text(value) for key, value in augmented.items()
        },
        "validation_rule": (
            "Validate each distinct field and label twice through its own PQDT browse and "
            "Add-to-search route before any comparison event."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(args.assignments.expanduser().resolve())
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 candidate map differs")
        return 0
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
