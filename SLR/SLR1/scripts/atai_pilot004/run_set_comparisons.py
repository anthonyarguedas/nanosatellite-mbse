#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Compare literal and controlled-vocabulary-augmented ATAI B1 sets."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)
SOURCE_NAME = "Advanced Technologies & Aerospace Index"
PARTITION_ORDER = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
SELECTED_IDS = (
    "3371247439",
    "3062738113",
    "2035264195",
    "1825532815",
    "3110716244",
    "3181339955",
    "1709719593",
)
CV_P_TERMS = ("Cubesat", "Nanosatellites", "Small satellites")
CV_M_MODEL_TERMS = ("Model-based systems", "Modelling")
CV_M_CONTEXT_TERM = "Systems engineering"


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot004_set_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load ATAI adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def split_top_level_and(query: str) -> tuple[str, str]:
    depth = 0
    in_quote = False
    escaped = False
    matches: list[int] = []
    for index, character in enumerate(query):
        if escaped:
            escaped = False
            continue
        if character == "\\" and in_quote:
            escaped = True
            continue
        if character == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                raise RuntimeError("B1 query has unbalanced parentheses.")
        elif depth == 0 and query.startswith(" AND ", index):
            matches.append(index)
    if depth != 0 or in_quote or len(matches) != 1:
        raise RuntimeError("B1 query did not contain one top-level AND.")
    split = matches[0]
    return query[:split], query[split + len(" AND ") :]


def exact_subject(term: str) -> str:
    return f"MAINSUBJECT.EXACT({json.dumps(term, ensure_ascii=False)})"


def build_queries(event_plan_path: Path) -> dict[str, str]:
    event_plan = json.loads(event_plan_path.read_text())
    matches = [
        event
        for event in event_plan.get("events", [])
        if event.get("partition_id") == "B1"
    ]
    if len(matches) != 1:
        raise RuntimeError("Pilot 003 event plan did not contain one B1 query.")
    literal = clean_text(matches[0].get("query"))
    population, mbse = split_top_level_and(literal)
    cv_population = " OR ".join(exact_subject(term) for term in CV_P_TERMS)
    cv_mbse_models = " OR ".join(exact_subject(term) for term in CV_M_MODEL_TERMS)
    cv_mbse = f"({exact_subject(CV_M_CONTEXT_TERM)} AND ({cv_mbse_models}))"
    augmented = f"({population} OR {cv_population}) AND ({mbse} OR {cv_mbse})"
    known_ids = " OR ".join(f"AN({paper_id})" for paper_id in SELECTED_IDS)
    known_mapping = f"({known_ids}) AND {cv_mbse}"
    return {
        "known-set-cv-mapping": known_mapping,
        "B1-literal": literal,
        "B1-augmented": augmented,
    }


def validate_candidate_receipt(path: Path) -> None:
    artifact = json.loads(path.read_text())
    if artifact.get("status") != "complete_two_pass_readback":
        raise RuntimeError("Technology Thesaurus candidate validation is incomplete.")
    observed = {
        item["term"]
        for item in artifact.get("candidates", [])
        if item.get("status") == "verified_exact_technology_thesaurus_descriptor"
    }
    expected = set(CV_P_TERMS) | set(CV_M_MODEL_TERMS) | {CV_M_CONTEXT_TERM}
    if observed != expected:
        raise RuntimeError("Technology Thesaurus candidate validation does not cover the comparison terms.")


def save_artifact(adapter: Any, path: Path, result: dict[str, Any], context: dict[str, Any]) -> None:
    artifact = adapter.mark_non_mergeable(result)
    compact = adapter.compact_search_result_for_output(artifact)
    compact["pilot_context"] = context
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(compact, indent=2, ensure_ascii=False) + "\n")


def record_projection(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": clean_text(record.get("paperId")),
        "title": clean_text(record.get("title")),
        "year": record.get("year"),
        "document_type": clean_text(record.get("documentType")),
        "abstract": clean_text(record.get("abstract")),
        "canonical_url": clean_text(record.get("url")),
    }


def run(
    event_plan_path: Path,
    candidate_receipt_path: Path,
    output_dir: Path,
    reconciliation_path: Path,
    failure_path: Path,
    timeout_seconds: float,
) -> None:
    adapter = load_adapter()
    validate_candidate_receipt(candidate_receipt_path)
    queries = build_queries(event_plan_path)
    started_at = adapter.utc_now()
    cells: dict[str, list[dict[str, Any]]] = {}
    try:
        for cell_id, query in queries.items():
            cells[cell_id] = []
            for pass_number in (1, 2):
                run_id = f"atai-p004-{cell_id.lower()}-pass{pass_number}"
                result = adapter.search_proquest_aerospace(
                    query,
                    limit=10_000,
                    language="English",
                    max_pages=500,
                    timeout_seconds=timeout_seconds,
                    page_delay_seconds=0.25,
                    count_only=False,
                    require_complete=False,
                    date_start="2011-01-01",
                    date_end="2026-08-29",
                    cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                    prisma_context={
                        "run_id": run_id,
                        "review_id": "slr1-atai-pilot-004",
                        "strategy_reference": "slr1-atai-controlled-vocabulary-pilot-v1",
                        "strategy_version": sha256_text(query),
                        "phase": "identification",
                        "coverage_scope": "partition",
                        "is_full_source_coverage": False,
                        "partition_id": cell_id,
                        "partition_label": cell_id,
                        "partition_description": "Pilot-only controlled-vocabulary diagnostic cell.",
                    },
                )
                artifact_name = f"{cell_id}-pass{pass_number}.json"
                save_artifact(
                    adapter,
                    output_dir / artifact_name,
                    result,
                    {
                        "pilot": "004",
                        "cell_id": cell_id,
                        "pass": pass_number,
                        "do_not_merge": True,
                        "query_sha256": sha256_text(query),
                    },
                )
                cells[cell_id].append(result)
    except Exception as error:
        failure = {
            "schema_version": "atai-controlled-vocabulary-set-comparison-failure/v1",
            "source": SOURCE_NAME,
            "pilot": "004",
            "status": "error",
            "do_not_merge": True,
            "started_at_utc": started_at,
            "failed_at_utc": adapter.utc_now(),
            "stage": "literal_and_augmented_set_capture",
            "error_type": type(error).__name__,
            "error": clean_text(error),
            "completed_cells": {
                cell_id: len(passes) for cell_id, passes in cells.items()
            },
            "predeclared_cell_order": list(queries),
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False) + "\n")
        raise

    reconciled: dict[str, dict[str, Any]] = {}
    for cell_id, passes in cells.items():
        if len(passes) != 2:
            raise RuntimeError(f"{cell_id} did not complete two passes.")
        pass_ids = [
            [clean_text(record.get("paperId")) for record in result.get("results", [])]
            for result in passes
        ]
        totals = [result.get("total") for result in passes]
        if totals[0] != totals[1] or pass_ids[0] != pass_ids[1]:
            raise RuntimeError(f"{cell_id} source total or ordered stable IDs changed across passes.")
        if totals[1] != len(pass_ids[1]) or len(set(pass_ids[1])) != len(pass_ids[1]):
            raise RuntimeError(f"{cell_id} did not reconcile its source total to unique stable IDs.")
        reconciled[cell_id] = {
            "query": queries[cell_id],
            "query_sha256": sha256_text(queries[cell_id]),
            "source_total": totals[1],
            "stable_ids_in_source_order": pass_ids[1],
            "stable_id_count": len(pass_ids[1]),
            "passes": 2,
            "ordered_ids_equal": True,
            "artifacts": [f"{cell_id}-pass1.json", f"{cell_id}-pass2.json"],
        }

    baseline_ids = reconciled["B1-literal"]["stable_ids_in_source_order"]
    augmented_ids = reconciled["B1-augmented"]["stable_ids_in_source_order"]
    baseline_set = set(baseline_ids)
    augmented_set = set(augmented_ids)
    if not baseline_set.issubset(augmented_set):
        raise RuntimeError("The controlled-vocabulary augmentation lost literal B1 IDs.")
    candidate_only_ids = [paper_id for paper_id in augmented_ids if paper_id not in baseline_set]
    augmented_records = {
        clean_text(record.get("paperId")): record
        for record in cells["B1-augmented"][1].get("results", [])
    }
    known_mapping_ids = reconciled["known-set-cv-mapping"]["stable_ids_in_source_order"]
    if not set(known_mapping_ids).issubset(set(SELECTED_IDS)):
        raise RuntimeError("The known-set mapping query returned an undeclared record ID.")

    reconciliation = {
        "schema_version": "atai-controlled-vocabulary-set-comparison/v1",
        "source": SOURCE_NAME,
        "source_id": "proquest_aerospace_index",
        "platform": "ProQuest",
        "pilot": "004",
        "purpose": "Compare fresh literal B1 with a no-loss OR augmentation built from exact descriptors assigned to selected relevant records.",
        "status": "complete_two_pass_stable_id_comparison",
        "do_not_merge": True,
        "started_at_utc": started_at,
        "completed_at_utc": adapter.utc_now(),
        "controls": {
            "database": SOURCE_NAME,
            "publication_date_start": "2011-01-01",
            "publication_date_end": "2026-08-29",
            "language": "LA(English)",
            "document_type": None,
            "peer_reviewed": False,
            "full_text": None,
            "access": None,
            "sort": "DateAsc",
            "spelling_variants": False,
            "form_variants": False,
            "show_variants": False,
        },
        "controlled_vocabulary_construction": {
            "population_descriptors": list(CV_P_TERMS),
            "mbse_context_descriptor": CV_M_CONTEXT_TERM,
            "mbse_model_descriptors": list(CV_M_MODEL_TERMS),
            "mbse_supplement_boolean": "Systems engineering AND (Model-based systems OR Modelling)",
            "combination_rule": "OR each descriptor supplement with its normative free-text block.",
            "major_topic": False,
            "explosion": None,
        },
        "selected_known_record_ids": list(SELECTED_IDS),
        "cells": reconciled,
        "known_set_mapping": {
            "matched_ids": known_mapping_ids,
            "matched_count": len(known_mapping_ids),
            "unmatched_selected_ids": [
                paper_id for paper_id in SELECTED_IDS if paper_id not in set(known_mapping_ids)
            ],
        },
        "comparison": {
            "literal_total": len(baseline_ids),
            "augmented_total": len(augmented_ids),
            "literal_is_subset": True,
            "candidate_only_total": len(candidate_only_ids),
            "candidate_only_ids": candidate_only_ids,
            "candidate_only_records": [
                record_projection(augmented_records[paper_id])
                for paper_id in candidate_only_ids
            ],
        },
        "limitations": [
            "Ordinary full traversals are reconciled by source total and ordered stable IDs across two passes. They do not replace the adapter's strict full-record signature contract.",
            "The comparison tests B1, the partition directly represented by all seven selected known records. It does not authorize descriptors in other partitions without applying the same mapped block construction.",
            "The source exposes no stable descriptor IDs, vocabulary release, or explosion state.",
        ],
    }
    reconciliation_path.parent.mkdir(parents=True, exist_ok=True)
    reconciliation_path.write_text(
        json.dumps(reconciliation, indent=2, ensure_ascii=False) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--candidate-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--failure-output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    run(
        args.event_plan,
        args.candidate_receipt,
        args.output_dir,
        args.reconciliation,
        args.failure_output,
        args.timeout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
