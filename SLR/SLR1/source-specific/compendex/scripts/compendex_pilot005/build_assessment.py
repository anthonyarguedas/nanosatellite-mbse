#!/usr/bin/env python3
"""Build the Compendex Pilot 005 wildcard set assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

DATABASES = ("compendex", "inspec")
SOURCE_LABELS = {
    "compendex": "Compendex (Engineering Village)",
    "inspec": "Inspec (Engineering Village)",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def ordered_difference(left: list[str], right: set[str]) -> list[str]:
    return [value for value in left if value not in right]


def record_projection(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record.get(key)
        for key in ("paperId", "source", "title", "year", "doi", "documentType")
    }


def validate_cell(
    artifact: dict[str, Any], event: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    context = artifact.get("pilot_context")
    metadata = artifact.get("output_metadata")
    results = artifact.get("results")
    if (
        artifact.get("do_not_merge") is not True
        or not isinstance(context, dict)
        or context.get("status") != "strict_two_pass_complete"
        or context.get("event_id") != event["event_id"]
        or context.get("query_sha256") != event["query_sha256"]
        or artifact.get("requested_query") != event["query"]
        or not isinstance(metadata, dict)
        or metadata.get("merge_eligible") is not False
        or metadata.get("pilot_only") is not True
        or not isinstance(results, list)
        or artifact.get("total") != len(results)
    ):
        raise RuntimeError(f"The retained source cell is invalid: {event['event_id']}")
    strict = context.get("strict_complete_comparison_receipt")
    if (
        not isinstance(strict, dict)
        or strict.get("complete_pass_count") != 2
        or strict.get("sequence_match") is not True
    ):
        raise RuntimeError(f"The strict receipt is invalid: {event['event_id']}")
    projections = context.get("projections")
    if not isinstance(projections, dict) or set(projections) != set(DATABASES):
        raise RuntimeError(f"The database projections changed: {event['event_id']}")
    observed: dict[str, dict[str, Any]] = {}
    for database in DATABASES:
        projection = projections[database]
        ids = projection.get("ordered_stable_accessions")
        if not isinstance(ids, list) or any(not isinstance(value, str) for value in ids):
            raise RuntimeError(f"The {database} accession projection is invalid")
        if len(ids) != len(set(ids)) or projection.get("source_total") != len(ids):
            raise RuntimeError(f"The {database} accession projection does not reconcile")
        result_ids = [
            record.get("paperId")
            for record in results
            if record.get("source") == SOURCE_LABELS[database]
        ]
        if result_ids != ids:
            raise RuntimeError(f"The {database} result order changed")
        observed[database] = projection
    if sum(value["source_total"] for value in observed.values()) != artifact["total"]:
        raise RuntimeError("The paired total does not equal the database projections")
    return observed


def build(pilot_root: Path, plan_path: Path, receipt_path: Path) -> dict[str, Any]:
    plan = load(plan_path)
    receipt = load(receipt_path)
    events = plan.get("events")
    if (
        plan.get("schema_version") != "engineering-village-wildcard-pilot-plan/v1"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or not isinstance(events, list)
        or len(events) != 2
        or receipt.get("status") != "complete"
        or receipt.get("completed_event_count") != 2
    ):
        raise RuntimeError("The predeclared run did not complete")

    cells: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, dict[str, Any]] = {}
    for event in events:
        path = pilot_root / "searches" / event["output"]
        artifact = load(path)
        projections = validate_cell(artifact, event)
        artifacts[event["event_id"]] = artifact
        cells[event["event_id"]] = {
            "artifact": str(path.relative_to(pilot_root / "searches")),
            "artifact_sha256": digest_file(path),
            "query_sha256": event["query_sha256"],
            "query_characters": event["query_characters"],
            "paired_source_total": artifact["total"],
            "strict_pass_count": 2,
            "projections": projections,
        }

    candidate = artifacts["wildcard-A1"]
    comparisons: dict[str, dict[str, Any]] = {}
    candidate_only_records: dict[str, list[dict[str, Any]]] = {}
    for database in DATABASES:
        literal_ids = cells["literal-A1"]["projections"][database][
            "ordered_stable_accessions"
        ]
        candidate_ids = cells["wildcard-A1"]["projections"][database][
            "ordered_stable_accessions"
        ]
        literal_set = set(literal_ids)
        candidate_set = set(candidate_ids)
        missing = ordered_difference(literal_ids, candidate_set)
        added = ordered_difference(candidate_ids, literal_set)
        comparisons[database] = {
            "literal_total": len(literal_ids),
            "wildcard_total": len(candidate_ids),
            "literal_accessions": literal_ids,
            "wildcard_accessions": candidate_ids,
            "literal_missing_from_wildcard": missing,
            "wildcard_only_accessions": added,
            "wildcard_is_literal_superset": not missing,
            "sets_equal": not missing and not added,
            "both_captures_complete": True,
        }
        by_id = {
            record.get("paperId"): record
            for record in candidate["results"]
            if record.get("source") == SOURCE_LABELS[database]
        }
        candidate_only_records[database] = [
            record_projection(by_id[paper_id]) for paper_id in added
        ]

    compendex = comparisons["compendex"]
    if compendex["literal_missing_from_wildcard"]:
        decision = "reject_compendex_A1_wildcard_candidate"
        accepted = False
        reason = "The complete wildcard projection omitted a literal Compendex accession."
    elif compendex["wildcard_only_accessions"]:
        decision = "do_not_accept_without_candidate_only_assessment"
        accepted = False
        reason = (
            "The wildcard projection is a complete superset, but candidate-only Compendex "
            "records require an explicit bounded concept assessment before adoption."
        )
    else:
        decision = "accept_three_family_wildcard_for_compendex_A1_only"
        accepted = True
        reason = (
            "The two complete Compendex projections are equal, so the candidate covers every "
            "literal A1 accession without an observed candidate-only record."
        )

    return {
        "schema_version": "engineering-village-wildcard-pilot-assessment/v1",
        "source": "Compendex with retained paired Inspec projection",
        "platform": "Engineering Village",
        "pilot": "005",
        "status": "complete",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "completed_at_utc": now(),
        "provenance": {
            "event_plan": str(plan_path.relative_to(pilot_root / "searches")),
            "event_plan_sha256": digest_file(plan_path),
            "run_receipt": str(receipt_path.relative_to(pilot_root / "searches")),
            "run_receipt_sha256": digest_file(receipt_path),
            "adapter": plan["adapter"],
            "term_snapshot": plan["term_snapshot"],
        },
        "method": {
            "schedule_id": "A1",
            "source_window": "Published 2011-2026",
            "common_evidence_cutoff": "TBD",
            "events": 2,
            "strict_passes_per_event": 2,
            "total_strict_source_passes": 4,
            "identity": "database-scoped Engineering Village stable accession",
            "comparison": "separate complete Compendex and Inspec set differences",
            "count_only_inference": False,
            "raw_ris_persisted": False,
        },
        "candidate": {
            "literal_query_characters": len(queries.A1_LITERAL),
            "wildcard_query_characters": len(queries.A1_WILDCARD),
            "character_reduction": queries.CHARACTER_REDUCTION,
            "character_reduction_percent": round(
                100 * queries.CHARACTER_REDUCTION / len(queries.A1_LITERAL), 2
            ),
            "wildcard_count": len(queries.WILDCARD_REPLACEMENTS),
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "replacements": plan["comparison"]["replacements"],
            "all_other_terms_and_controls_unchanged": True,
        },
        "cells": cells,
        "database_comparisons": comparisons,
        "candidate_only_record_metadata": candidate_only_records,
        "decision": decision,
        "accepted_for_compendex_A1": accepted,
        "accepted_for_other_compendex_partitions": False,
        "reason": reason,
        "inspec_boundary": {
            "set_result": comparisons["inspec"],
            "translation_decision": "outside_this_compendex_guideline_pilot",
            "counts_and_accessions_combined_with_compendex": False,
        },
        "pilot_boundary": [
            "These diagnostic records are not merge eligible and are not final-search records.",
            "The A1 result is not evidence for wildcard use in another partition.",
            "Future suffix completions can change as the database is updated.",
            "Every punctuation, spacing, phrase, and spelling form outside the three replacements stays literal.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(args.pilot_root, args.plan, args.run_receipt)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
