#!/usr/bin/env python3
"""Assess the final Scopus prior-secondary-review search artifacts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "slr1-scopus-final-psr-assessment/v1"
PLAN_SCHEMA = "slr1-scopus-final-psr-plan/v1"
RUN_SCHEMA = "slr1-scopus-final-psr-run/v1"
PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
KNOWN_ID = "SCOPUS-PUBLICATION:105032155734"
KNOWN_TITLE = "Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review"
SCRIPT_ROOT = Path(__file__).resolve().parent
RUNNER = SCRIPT_ROOT / "run_final.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_ids(values: set[str]) -> str:
    result = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("scopus_final_psr_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_union_valid(
    value: dict[str, Any],
    stable_ids: set[str],
    raw_event_count: int,
    plan: dict[str, Any],
) -> bool:
    union = value.get("source_unions", {}).get("scopus", {})
    return bool(
        value.get("review_namespace") == "prior_secondary_reviews"
        and value.get("review_id") == plan.get("review_id")
        and value.get("strategy_reference") == plan.get("strategy_reference")
        and value.get("expected_partitions") == list(PARTITIONS)
        and value.get("expected_sources") == ["scopus"]
        and value.get("completeness_status") == "complete"
        and value.get("failure_status") == "none"
        and union.get("expected_partitions") == list(PARTITIONS)
        and union.get("event_total_sum") == raw_event_count
        and set(union.get("stable_record_ids", [])) == stable_ids
        and union.get("raw_record_count") == raw_event_count
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-union", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    plan = load(args.plan)
    run = load(args.run_receipt)
    source_union = load(args.source_union)
    runner = load_runner()
    errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("plan_schema")
    if run.get("schema_version") != RUN_SCHEMA:
        errors.append("run_schema")
    if run.get("plan_sha256") != digest(args.plan):
        errors.append("run_plan_binding")
    if run.get("review_namespace") != "prior_secondary_reviews":
        errors.append("run_namespace")
    if run.get("event_kind") != "final":
        errors.append("run_event_kind")
    if run.get("target_identifier_retained") is not False:
        errors.append("target_privacy")

    events = {event["partition_id"]: event for event in plan.get("events", [])}
    outcomes = {
        outcome["partition_id"]: outcome for outcome in run.get("outcomes", [])
    }
    if set(events) != set(PARTITIONS):
        errors.append("plan_partition_coverage")
    if set(outcomes) != set(PARTITIONS):
        errors.append("run_partition_coverage")

    evidence: list[dict[str, Any]] = []
    id_sets: dict[str, set[str]] = {}
    known_item_partitions: list[str] = []
    screenshot_count = 0
    cutoff_year_records = 0
    for partition in PARTITIONS:
        event = events.get(partition)
        outcome = outcomes.get(partition)
        if event is None or outcome is None:
            continue
        artifact_name = outcome.get("artifact")
        if (
            outcome.get("success") is not True
            or outcome.get("attempt_count") != 1
            or artifact_name != event.get("output_filename")
        ):
            errors.append(f"accepted_event:{partition}")
            continue
        path = args.output_dir / artifact_name
        try:
            value = load(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"artifact:{partition}:{type(error).__name__}")
            continue
        summary = runner.summarize(path, event, plan)
        metadata = value.get("output_metadata", {})
        strict = metadata.get("strict_two_pass_receipt", {})
        records = value.get("results", [])
        stable_ids = {
            row.get("paperId")
            for row in records
            if isinstance(row, dict) and isinstance(row.get("paperId"), str)
        }
        id_sets[partition] = stable_ids
        if summary.get("valid") is not True:
            errors.append(f"strict_evidence:{partition}")
        if outcome.get("artifact_sha256") != digest(path):
            errors.append(f"artifact_hash:{partition}")
        if outcome.get("artifact_bytes") != path.stat().st_size:
            errors.append(f"artifact_size:{partition}")
        if value.get("requested_query") != event.get("query"):
            errors.append(f"query_binding:{partition}")
        if any(
            marker in event.get("query", "").upper()
            for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR")
        ) or any(symbol in event.get("query", "") for symbol in ("*", "?")):
            errors.append(f"literal_query:{partition}")
        known_rows = [
            row for row in records if isinstance(row, dict) and row.get("paperId") == KNOWN_ID
        ]
        if known_rows:
            known_item_partitions.append(partition)
            if any(
                row.get("title") != KNOWN_TITLE or row.get("year") != 2026
                for row in known_rows
            ):
                errors.append(f"known_item_identity:{partition}")
        screenshot_count += len(summary.get("screenshots", []))
        cutoff_year_records += sum(
            isinstance(row, dict) and row.get("year") == 2026 for row in records
        )
        evidence.append(
            {
                "partition_id": partition,
                "artifact": path.name,
                "artifact_sha256": digest(path),
                "source_total": value.get("total"),
                "stable_id_count": len(stable_ids),
                "stable_id_set_sha256": strict.get("stable_id_set_sha256"),
                "strict_receipt_schema": strict.get("schema_version"),
                "pass_page_counts": [
                    report.get("pages_retrieved")
                    for report in strict.get("pass_reports", [])
                    if isinstance(report, dict)
                ],
                "pass_order_hashes": summary.get("pass_order_hashes"),
                "two_pass_order_verified": strict.get("two_pass_order_verified"),
                "order_difference_count": strict.get("order_difference_count"),
                "screenshots": summary.get("screenshots", []),
                "abstracts_recovered_in_discovery_event": sum(
                    bool(row.get("abstract"))
                    for row in records
                    if isinstance(row, dict)
                ),
            }
        )

    all_ids = set().union(*id_sets.values()) if id_sets else set()
    raw_event_count = sum(len(values) for values in id_sets.values())
    pair_overlaps = {
        f"{left}_{right}": len(id_sets.get(left, set()) & id_sets.get(right, set()))
        for left, right in itertools.combinations(PARTITIONS, 2)
    }
    known_item_valid = set(known_item_partitions) == {"PSR1", "PSR2"}
    if not known_item_valid:
        errors.append("known_item_recall")
    if screenshot_count != 8:
        errors.append("screenshot_count")
    if (
        run.get("success") is not True
        or run.get("accepted_event_count") != 4
        or run.get("source_command_attempt_count") != 4
        or run.get("all_partitions_attempted") is not True
    ):
        errors.append("run_summary")
    union_ok = source_union_valid(source_union, all_ids, raw_event_count, plan)
    if not union_ok:
        errors.append("source_union")

    complete = bool(len(evidence) == 4 and not errors)
    assessment = {
        "schema_version": SCHEMA,
        "source": "Scopus",
        "review_namespace": "prior_secondary_reviews",
        "event_kind": "final",
        "plan": args.plan.name,
        "plan_sha256": digest(args.plan),
        "run_receipt": args.run_receipt.name,
        "run_receipt_sha256": digest(args.run_receipt),
        "source_union": args.source_union.name,
        "source_union_sha256": digest(args.source_union),
        "adapter": plan.get("adapter"),
        "accepted_source_event_count": len(evidence),
        "verified_screenshot_file_count": screenshot_count,
        "events": evidence,
        "stable_id_union": {
            "source_event_record_count": raw_event_count,
            "unique_stable_id_count": len(all_ids),
            "cross_partition_duplicate_occurrences": raw_event_count - len(all_ids),
            "stable_id_set_sha256": digest_ids(all_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
            "pair_overlap_counts": pair_overlaps,
        },
        "cutoff_screening": {
            "common_evidence_cutoff": plan.get("cutoff", {}).get("exact_common_cutoff"),
            "source_year_upper_bound": plan.get("cutoff", {}).get("source_year_upper_bound"),
            "source_precision": "year",
            "records_in_cutoff_year_requiring_exact_date_screening": cutoff_year_records,
            "status": "pending_screening",
        },
        "abstract_recovery": {
            "discovery_events_used_skip_full_abstracts": all(
                event.get("abstracts_recovered_in_discovery_event") == 0
                for event in evidence
            ),
            "required_route": "canonical EID-only query bound to accepted strict leaves",
            "status": "pending",
            "unresolved_singleton_rule": "remain unresolved",
        },
        "known_item": {
            "citation": plan.get("known_item", {}).get("citation"),
            "doi": plan.get("known_item", {}).get("doi"),
            "stable_id": KNOWN_ID,
            "retrieved_partitions": known_item_partitions,
            "stable_id_and_title_recall_confirmed": known_item_valid,
        },
        "source_union_valid": union_ok,
        "final_search_partitions_complete": complete,
        "status": "passed" if complete else "failed",
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "source_totals": {
                    item["partition_id"]: item["source_total"] for item in evidence
                },
                "stable_id_union": len(all_ids),
                "cutoff_year_records": cutoff_year_records,
            }
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
