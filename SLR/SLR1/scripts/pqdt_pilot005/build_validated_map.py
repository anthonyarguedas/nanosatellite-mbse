#!/usr/bin/env python3
"""Finalize PQDT block mappings from the live exact-label validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries

SCHEMA = "pqdt-global-pilot005-validated-candidate-map/v1"
DEFAULT_MAP = queries.PILOT_ROOT / "searches" / "candidate-map.json"
DEFAULT_VALIDATION = queries.PILOT_ROOT / "searches" / "candidate-validation.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "validated-candidate-map.json"


def clauses_by_id(candidates: list[dict[str, Any]], candidate_ids: list[str]) -> list[str]:
    by_id = {item["candidate_id"]: item for item in candidates}
    missing = [candidate_id for candidate_id in candidate_ids if candidate_id not in by_id]
    if missing:
        raise RuntimeError(f"Validated construction lacks candidates: {missing!r}")
    return [by_id[candidate_id]["executed_clause"] for candidate_id in candidate_ids]


def build(map_path: Path, validation_path: Path) -> dict[str, Any]:
    candidate_map = queries.load_object(map_path)
    validation = queries.load_object(validation_path)
    if candidate_map.get("schema_version") != "pqdt-global-pilot005-candidate-map/v1":
        raise RuntimeError("Unexpected PQDT candidate-map schema")
    if validation.get("schema_version") != "pqdt-global-pilot005-candidate-validation/v1":
        raise RuntimeError("Unexpected PQDT candidate-validation schema")
    if validation.get("status") != "complete_two_pass_exact_browse_readback":
        raise RuntimeError("PQDT exact-label validation is incomplete")
    if validation.get("input_candidate_map_sha256") != queries.file_sha256(map_path):
        raise RuntimeError("PQDT exact-label validation does not bind the candidate map")
    candidates = validation.get("candidates")
    if not isinstance(candidates, list):
        raise RuntimeError("PQDT exact-label validation has no candidate list")
    verified = [
        item for item in candidates if item.get("status") == "verified_exact_browse_label"
    ]
    rejected = [
        item for item in candidates if item.get("status") != "verified_exact_browse_label"
    ]
    if [item.get("candidate_id") for item in rejected] != ["IF-R-01"]:
        raise RuntimeError("The set of assigned labels absent from exact browse changed")

    p_ids = [item["candidate_id"] for item in verified if item.get("blocks") == ["P"]]
    direct_mh_ids = [
        item["candidate_id"] for item in verified if item.get("blocks") == ["M_H"]
    ]
    context_ids = [
        item["candidate_id"]
        for item in verified
        if item.get("blocks") == ["M_H_context"]
    ]
    model_context_ids = [
        item["candidate_id"]
        for item in verified
        if "M_H_model_context" in item.get("blocks", [])
    ]
    mb_ids = [
        item["candidate_id"] for item in verified if "M_B" in item.get("blocks", [])
    ]
    r_ids = [item["candidate_id"] for item in verified if item.get("blocks") == ["R"]]
    descriptor_expressions = {
        "P": queries.any_of(*clauses_by_id(verified, p_ids)),
        "M_H": queries.any_of(
            queries.any_of(*clauses_by_id(verified, direct_mh_ids)),
            queries.all_of(
                queries.any_of(*clauses_by_id(verified, context_ids)),
                queries.any_of(*clauses_by_id(verified, model_context_ids)),
            ),
        ),
        "M_B": queries.any_of(*clauses_by_id(verified, mb_ids)),
        "R": queries.any_of(*clauses_by_id(verified, r_ids)),
    }
    _, _, augmented = queries.build_augmented_schedule_from_expressions(
        descriptor_expressions
    )
    affected = [
        partition_id
        for partition_id in queries.SCHEDULE_IDS
        if augmented[partition_id] != queries.FREE_TEXT_SCHEDULE[partition_id]
    ]

    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "validated_for_value_comparison",
        "diagnostic_only": True,
        "do_not_merge": True,
        "inputs": {
            "candidate_map": {
                "path": str(map_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(map_path),
            },
            "candidate_validation": {
                "path": str(validation_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(validation_path),
            },
        },
        "assigned_candidate_count": len(candidates),
        "validated_candidate_count": len(verified),
        "rejected_candidate_count": len(rejected),
        "validated_candidates": verified,
        "rejected_candidates": [
            {
                "candidate_id": item["candidate_id"],
                "field": item["field"],
                "assigned_term": item.get("assigned_term", item["term"]),
                "tested_browse_labels": ["Architecture", "architecture"],
                "decision": "exclude_from_value_comparison",
                "reason": (
                    "The assigned IF label had no exact selectable Index term browse label "
                    "under either observed capitalization."
                ),
            }
            for item in rejected
        ],
        "controlled_constructions": {
            block: {
                "protocol_block": block,
                "expression": expression,
                "expression_sha256": queries.sha256_text(expression),
                "combination_with_free_text": "OR",
            }
            for block, expression in descriptor_expressions.items()
        },
        "affected_partitions": affected,
        "mapping_limits": {
            "E_H": "No assigned exact PSUB or IF candidate mapped without broadening.",
            "E_F": "PSUB Budgets lacked an electrical power or energy qualifier.",
            "G_model": "No assigned exact candidate established a reusable model or template.",
            "G_structure": "Scalable systems architecture did not establish a reusable structural artifact.",
            "C1": "No assigned exact candidate established a conservative central asset.",
            "T_precise": "No assigned exact candidate represented a declared tailoring operation.",
        },
        "source_limits": {
            "term_ids": "not_exposed",
            "vocabulary_versions": "not_published",
            "scope_notes": "not_exposed",
            "hierarchy": "not_exposed",
            "explosion": "unknown_and_not_requested",
            "major_topic": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--candidate-validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(
        args.candidate_map.expanduser().resolve(),
        args.candidate_validation.expanduser().resolve(),
    )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 validated candidate map differs")
        return 0
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
