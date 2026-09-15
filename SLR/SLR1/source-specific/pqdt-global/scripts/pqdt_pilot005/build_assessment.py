#!/usr/bin/env python3
"""Build the PQDT Pilot 005 controlled-term inclusion decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries

SCHEMA = "pqdt-global-pilot005-inclusion-assessment/v1"
DEFAULT_ASSIGNMENTS = queries.PILOT_ROOT / "searches" / "assigned-terms.json"
DEFAULT_VALIDATED_MAP = (
    queries.PILOT_ROOT / "searches" / "validated-candidate-map.json"
)
DEFAULT_COMPARISON = queries.PILOT_ROOT / "searches" / "set-comparison.json"
DEFAULT_REVIEW = queries.PILOT_ROOT / "searches" / "descriptor-only-review.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "inclusion-assessment.json"


def assignment_coverage(
    assignments: dict[str, Any], validated_map: dict[str, Any]
) -> dict[str, Any]:
    by_id = {
        item["candidate_id"]: item
        for item in validated_map["validated_candidates"]
    }
    records = assignments["records"]

    def assigned(record: dict[str, Any], candidate: dict[str, Any]) -> bool:
        expected = candidate.get("assigned_term", candidate["term"])
        values = (
            record["pq_subject_terms"]
            if candidate["field"] == "PSUB"
            else record["index_terms"]
        )
        return expected in values

    p_candidates = [item for item in by_id.values() if item["blocks"] == ["P"]]
    direct_mh = [item for item in by_id.values() if item["blocks"] == ["M_H"]]
    contexts = [
        item for item in by_id.values() if item["blocks"] == ["M_H_context"]
    ]
    model_contexts = [
        item
        for item in by_id.values()
        if "M_H_model_context" in item["blocks"]
    ]
    mb_candidates = [
        item for item in by_id.values() if "M_B" in item["blocks"]
    ]
    r_candidates = [item for item in by_id.values() if item["blocks"] == ["R"]]

    coverage: dict[str, list[str]] = {"P": [], "M_H": [], "M_B": [], "R": []}
    for record in records:
        paper_id = record["paper_id"]
        if any(assigned(record, item) for item in p_candidates):
            coverage["P"].append(paper_id)
        direct = any(assigned(record, item) for item in direct_mh)
        contextual = any(assigned(record, item) for item in contexts) and any(
            assigned(record, item) for item in model_contexts
        )
        if direct or contextual:
            coverage["M_H"].append(paper_id)
        if any(assigned(record, item) for item in mb_candidates):
            coverage["M_B"].append(paper_id)
        if any(assigned(record, item) for item in r_candidates):
            coverage["R"].append(paper_id)
    return {
        block: {
            "assigned_selected_record_count": len(ids),
            "assigned_selected_document_ids": ids,
        }
        for block, ids in coverage.items()
    }


def build(
    assignments_path: Path,
    validated_map_path: Path,
    comparison_path: Path,
    review_path: Path,
) -> dict[str, Any]:
    assignments = queries.load_object(assignments_path)
    validated_map = queries.load_object(validated_map_path)
    comparison = queries.load_object(comparison_path)
    review = queries.load_object(review_path)
    if assignments.get("status") != "complete_two_pass_assignment_readback":
        raise RuntimeError("PQDT assignment evidence is incomplete")
    if validated_map.get("status") != "validated_for_value_comparison":
        raise RuntimeError("PQDT validated candidate map is incomplete")
    if comparison.get("status") not in {
        "complete_pending_descriptor_only_review",
        "complete_no_descriptor_only_records",
    }:
        raise RuntimeError("PQDT set comparison is incomplete")
    if review.get("status") != "complete_empty_review_frame":
        raise RuntimeError("PQDT descriptor-only review is incomplete")
    union = comparison["union_comparison"]
    if union["descriptor_only_total"] != 0 or union["sets_equal"] is not True:
        raise RuntimeError("PQDT evidence no longer supports a zero-gain decision")
    partitions = comparison["partition_comparisons"]
    if set(partitions) != set(queries.SCHEDULE_IDS):
        raise RuntimeError("PQDT partition comparison is incomplete")
    if not all(
        item["sets_equal"] is True
        and item["orders_equal"] is True
        and item["descriptor_only_total"] == 0
        for item in partitions.values()
    ):
        raise RuntimeError("A PQDT partition differs after descriptor augmentation")

    coverage = assignment_coverage(assignments, validated_map)
    totals = {
        partition_id: {
            "free_text": partitions[partition_id]["free_text_total"],
            "augmented": partitions[partition_id]["augmented_total"],
        }
        for partition_id in queries.SCHEDULE_IDS
    }
    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": "do_not_add_pq_subject_or_index_term_supplement",
        "decision_scope": (
            "The current PQDT schedule and the assigned PSUB and IF candidates mapped "
            "from fourteen selected Pilot 004 known records."
        ),
        "inputs": {
            "assigned_terms": {
                "path": str(assignments_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(assignments_path),
            },
            "validated_candidate_map": {
                "path": str(validated_map_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(validated_map_path),
            },
            "set_comparison": {
                "path": str(comparison_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(comparison_path),
            },
            "descriptor_only_review": {
                "path": str(review_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(review_path),
            },
        },
        "evidence": {
            "selected_known_record_count": assignments["selected_record_count"],
            "unique_pq_subject_term_count": assignments["pq_subject_unique_term_count"],
            "unique_index_term_count": assignments["index_term_unique_term_count"],
            "assigned_candidates_tested": validated_map["assigned_candidate_count"],
            "validated_exact_candidates": validated_map["validated_candidate_count"],
            "assigned_candidate_without_exact_browse_label": validated_map[
                "rejected_candidate_count"
            ],
            "mapped_protocol_blocks": list(
                validated_map["controlled_constructions"]
            ),
            "selected_record_assignment_coverage": coverage,
            "partition_totals": totals,
            "all_partition_sets_equal": True,
            "all_partition_orders_equal": True,
            "free_text_schedule_union": union["free_text_distinct_ids"],
            "augmented_schedule_union": union["augmented_distinct_ids"],
            "descriptor_only_record_count": union["descriptor_only_total"],
            "descriptor_only_review_outcome": review["outcome"],
        },
        "criteria": [
            {
                "criterion": "source_assignment",
                "result": "passed_bounded",
                "reason": (
                    "Two complete record-detail passes returned identical PSUB and IF "
                    "assignments for all fourteen selected known records."
                ),
            },
            {
                "criterion": "exact_source_mapping",
                "result": "passed_for_27_candidates",
                "reason": (
                    "Two browse and Add-to-search passes validated 27 assigned or "
                    "case-normalized labels. Assigned IF Architecture had no exact "
                    "selectable label under either tested capitalization."
                ),
            },
            {
                "criterion": "preserve_normative_free_text",
                "result": "passed",
                "reason": (
                    "Every tested construction joined exact descriptors to its complete "
                    "free-text block with OR."
                ),
            },
            {
                "criterion": "marginal_stable_id_recall",
                "result": "failed_to_show_value",
                "reason": (
                    "All nine fresh free-text and augmented partition pairs returned the "
                    "same complete ordered IDs. The schedule unions each contained 29 IDs."
                ),
            },
            {
                "criterion": "descriptor_only_concept_review",
                "result": "complete_empty_frame",
                "reason": "No augmented-only record existed in any partition.",
            },
            {
                "criterion": "reproducible_vocabulary_identity",
                "result": "limited",
                "reason": (
                    "PQDT publishes no stable term IDs, vocabulary release, scope notes, "
                    "hierarchy, or explosion state for these flat browse indexes."
                ),
            },
        ],
        "rationale": [
            "The tested descriptor unions added no numeric PQDT document ID.",
            "Several assigned labels were absent, generic, or unsuitable for a protocol block.",
            "Mapped controlled terms covered only part of the selected known-record set and cannot replace free text.",
            "Adoption would add query and local transport complexity without observed recall value.",
        ],
        "accepted_descriptors": [],
        "prospective_translation": (
            "Retain the accepted bounded-wildcard NOFT schedule without a PSUB.EXACT or "
            "IF.EXACT supplement."
        ),
        "future_candidate_rule": (
            "A new descriptor or indexed term requires another assigned-record mapping and "
            "complete no-loss value comparison before adoption."
        ),
        "limitations": [
            "The test covers labels assigned to fourteen selected records and does not establish the value of every future PQDT label.",
            "The selected records are known items for vocabulary testing and are not final screening decisions.",
            "PQDT applies year precision. Records from 2026 still require exact-cutoff screening.",
            "A pilot-local bridge relaxed the adapter's multiple-raw-field preflight guard. Exact source query echo and every normal strict capture check remained mandatory.",
            "Pilot artifacts create no final-search union.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--validated-map", type=Path, default=DEFAULT_VALIDATED_MAP)
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(
        args.assignments.expanduser().resolve(),
        args.validated_map.expanduser().resolve(),
        args.comparison.expanduser().resolve(),
        args.review.expanduser().resolve(),
    )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 inclusion assessment differs")
        return 0
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
