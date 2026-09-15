#!/usr/bin/env python3
"""Assess the clean current-literal Scopus PSR strict pilot."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "scopus-current-literal-psr-post-pagination-fix-assessment/v1"
PILOT = "021"
PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
KNOWN_ID = "SCOPUS-PUBLICATION:105032155734"
KNOWN_TITLE = "Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review"
SCRIPT_ROOT = Path(__file__).resolve().parent
RUNNER = SCRIPT_ROOT / "run_pilot.py"


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


def load_runner():
    spec = importlib.util.spec_from_file_location("scopus_pilot021_assessment_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    plan = load(args.plan)
    run_receipt = load(args.run_receipt)
    runner = load_runner()
    errors: list[str] = []
    if plan.get("pilot") != PILOT or run_receipt.get("pilot") != PILOT:
        errors.append("pilot_identity")
    if run_receipt.get("plan_sha256") != digest(args.plan):
        errors.append("plan_binding")
    if run_receipt.get("success") is not True:
        errors.append("run_receipt_status")
    if run_receipt.get("safe_preexecution_retry_count") != 0:
        errors.append("unexpected_retry")

    event_by_partition = {
        event["partition_id"]: event for event in plan.get("events", [])
    }
    outcome_by_partition = {
        outcome["partition_id"]: outcome
        for outcome in run_receipt.get("outcomes", [])
    }
    if set(event_by_partition) != set(PARTITIONS):
        errors.append("plan_partition_coverage")
    if set(outcome_by_partition) != set(PARTITIONS):
        errors.append("run_partition_coverage")

    evidence: list[dict[str, Any]] = []
    id_sets: dict[str, set[str]] = {}
    known_item_partitions: list[str] = []
    known_item_rows: list[dict[str, Any]] = []
    screenshot_count = 0
    for partition in PARTITIONS:
        event = event_by_partition.get(partition)
        outcome = outcome_by_partition.get(partition)
        if event is None or outcome is None:
            continue
        accepted_relative = outcome.get("accepted_artifact")
        if (
            outcome.get("success") is not True
            or outcome.get("attempt_count") != 1
            or not isinstance(accepted_relative, str)
        ):
            errors.append(f"accepted_event:{partition}")
            continue
        path = args.pilot_root / accepted_relative
        try:
            value = load(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"artifact:{partition}:{type(error).__name__}")
            continue
        summary = runner.summarize(path, event)
        metadata = value.get("output_metadata", {})
        strict = metadata.get("strict_two_pass_receipt", {})
        results = value.get("results", [])
        stable_ids = {
            row.get("paperId")
            for row in results
            if isinstance(row, dict) and isinstance(row.get("paperId"), str)
        }
        id_sets[partition] = stable_ids
        known_rows = [
            row
            for row in results
            if isinstance(row, dict) and row.get("paperId") == KNOWN_ID
        ]
        if known_rows:
            known_item_partitions.append(partition)
            known_item_rows.extend(known_rows)
        if summary.get("valid") is not True:
            errors.append(f"strict_evidence:{partition}")
        if value.get("requested_query") != event.get("query"):
            errors.append(f"query_binding:{partition}")
        if any(
            marker in event.get("query", "").upper()
            for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR")
        ) or any(symbol in event.get("query", "") for symbol in ("*", "?")):
            errors.append(f"nonliteral_query:{partition}")
        pass_reports = strict.get("pass_reports", [])
        screenshot_count += len(summary.get("screenshots", []))
        evidence.append(
            {
                "partition_id": partition,
                "artifact": str(path),
                "artifact_sha256": digest(path),
                "valid": summary.get("valid"),
                "source_total": value.get("total"),
                "stable_id_count": len(stable_ids),
                "stable_id_set_sha256": strict.get("stable_id_set_sha256"),
                "strict_receipt_schema": strict.get("schema_version"),
                "pass_page_counts": [
                    report.get("pages_retrieved")
                    for report in pass_reports
                    if isinstance(report, dict)
                ],
                "pass_source_totals": [
                    report.get("source_reported_total")
                    for report in pass_reports
                    if isinstance(report, dict)
                ],
                "two_pass_order_verified": strict.get("two_pass_order_verified"),
                "order_difference_count": strict.get("order_difference_count"),
                "screenshots": summary.get("screenshots", []),
                "known_item_retrieved": bool(known_rows),
            }
        )

    all_ids = set().union(*id_sets.values()) if id_sets else set()
    source_event_record_count = sum(len(values) for values in id_sets.values())
    pair_overlaps = {
        f"{left}_{right}": len(id_sets.get(left, set()) & id_sets.get(right, set()))
        for left, right in itertools.combinations(PARTITIONS, 2)
    }
    known_item_valid = bool(
        set(known_item_partitions) == {"PSR1", "PSR2"}
        and all(
            row.get("title") == KNOWN_TITLE and row.get("year") == 2026
            for row in known_item_rows
        )
    )
    if not known_item_valid:
        errors.append("known_item_recall")
    if screenshot_count != 8:
        errors.append("screenshot_count")
    psr2 = next(
        (item for item in evidence if item["partition_id"] == "PSR2"), None
    )
    psr4 = next(
        (item for item in evidence if item["partition_id"] == "PSR4"), None
    )
    priority_complete = bool(
        psr2 is not None
        and psr2.get("valid") is True
        and psr4 is not None
        and psr4.get("valid") is True
    )
    if not priority_complete:
        errors.append("priority_partitions")
    complete = bool(len(evidence) == 4 and not errors)
    assessment = {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": "Scopus",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "run_receipt": str(args.run_receipt),
        "run_receipt_sha256": digest(args.run_receipt),
        "adapter": plan.get("adapter"),
        "literal_partition_count": len(evidence),
        "accepted_source_event_count": len(evidence),
        "strict_receipt_schema": "academic-search-scopus-strict-two-pass/v2",
        "verified_screenshot_file_count": screenshot_count,
        "restriction_audit": {
            "year_start": None,
            "year_end": 2026,
            "language": "not_applied",
            "document_type": "not_applied",
            "subject_area": "not_applied",
            "access": "not_applied",
            "peer_review": "not_applied",
            "search_within": "not_applied",
            "valid": complete,
        },
        "events": evidence,
        "stable_id_union": {
            "source_event_record_count": source_event_record_count,
            "unique_stable_id_count": len(all_ids),
            "cross_partition_duplicate_occurrences": (
                source_event_record_count - len(all_ids)
            ),
            "stable_id_set_sha256": digest_ids(all_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
            "pair_overlap_counts": pair_overlaps,
        },
        "known_item": {
            "citation": (
                "Buruso et al. (2026), Model-Based Systems Engineering in Space "
                "Applications: A Comprehensive Literature Review"
            ),
            "doi": "10.1002/sys.70051",
            "stable_id": KNOWN_ID,
            "retrieved_partitions": known_item_partitions,
            "source_rows_expose_doi": any(row.get("doi") for row in known_item_rows),
            "stable_id_and_title_recall_confirmed": known_item_valid,
        },
        "psr2_and_psr4_strict_completion_confirmed": priority_complete,
        "all_four_current_literal_partitions_strictly_complete": complete,
        "wildcard_comparisons_run": False,
        "adapter_pagination_repair_live_validated": bool(
            complete
            and psr2 is not None
            and psr2.get("source_total") == 237
            and psr2.get("pass_page_counts") == [5, 5]
        ),
        "decision": (
            "accept_current_literal_psr_pilot_evidence"
            if complete
            else "retain_psr_completion_gap"
        ),
        "errors": errors,
        "status": "passed" if complete else "failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "totals": {
                    item["partition_id"]: item["source_total"]
                    for item in evidence
                },
                "union": len(all_ids),
                "buruso_partitions": known_item_partitions,
                "screenshots": screenshot_count,
            }
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
