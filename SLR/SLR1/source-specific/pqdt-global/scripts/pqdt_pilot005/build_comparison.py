#!/usr/bin/env python3
"""Reconcile PQDT Pilot 005 free-text and augmented schedule sets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import queries
import run_pilot

SCHEMA = "pqdt-global-pilot005-set-comparison/v1"
DEFAULT_PLAN = queries.PILOT_ROOT / "searches" / "event-plan.json"
DEFAULT_RECEIPT = queries.PILOT_ROOT / "searches" / "run-receipt.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "set-comparison.json"


def record_projection(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": record.get("paperId"),
        "title": record.get("title"),
        "year": record.get("year"),
        "source_type": record.get("sourceType"),
        "publication_title": record.get("publicationTitle"),
        "abstract": record.get("abstract"),
        "canonical_url": record.get("url"),
    }


def build(plan_path: Path, receipt_path: Path) -> dict[str, Any]:
    plan = queries.load_object(plan_path)
    receipt = queries.load_object(receipt_path)
    errors = run_pilot.validate_plan(plan)
    if errors:
        raise RuntimeError("Invalid PQDT Pilot 005 plan: " + "; ".join(errors))
    if receipt.get("status") != "complete" or receipt.get("completed_event_count") != 18:
        raise RuntimeError("PQDT Pilot 005 source run is incomplete")
    if receipt.get("event_plan_sha256") != queries.file_sha256(plan_path):
        raise RuntimeError("PQDT Pilot 005 run receipt does not bind the current plan")

    by_id = {event["event_id"]: event for event in plan["events"]}
    comparisons: dict[str, Any] = {}
    baseline_union: list[str] = []
    augmented_union: list[str] = []
    baseline_seen: set[str] = set()
    augmented_seen: set[str] = set()
    augmented_only_records: dict[str, dict[str, Any]] = {}

    for partition_id in queries.SCHEDULE_IDS:
        free_event = by_id[f"free-text-{partition_id}"]
        augmented_event = by_id[f"augmented-{partition_id}"]
        free_path = queries.PILOT_ROOT / "searches" / free_event["output"]
        augmented_path = queries.PILOT_ROOT / "searches" / augmented_event["output"]
        free_summary = run_pilot.strict_artifact_summary(free_event, free_path, plan)
        augmented_summary = run_pilot.strict_artifact_summary(
            augmented_event, augmented_path, plan
        )
        free_ids = free_summary["stable_ids_in_source_order"]
        augmented_ids = augmented_summary["stable_ids_in_source_order"]
        free_set = set(free_ids)
        augmented_set = set(augmented_ids)
        missing = [paper_id for paper_id in free_ids if paper_id not in augmented_set]
        added = [paper_id for paper_id in augmented_ids if paper_id not in free_set]
        if missing:
            raise RuntimeError(
                f"PQDT augmented {partition_id} lost free-text IDs: {missing!r}"
            )
        artifact = queries.load_object(augmented_path)
        rows = {
            row["paperId"]: row
            for row in artifact["results"]
            if isinstance(row, Mapping)
        }
        for paper_id in added:
            augmented_only_records.setdefault(paper_id, record_projection(rows[paper_id]))
        for paper_id in free_ids:
            if paper_id not in baseline_seen:
                baseline_seen.add(paper_id)
                baseline_union.append(paper_id)
        for paper_id in augmented_ids:
            if paper_id not in augmented_seen:
                augmented_seen.add(paper_id)
                augmented_union.append(paper_id)
        comparisons[partition_id] = {
            "free_text_total": len(free_ids),
            "augmented_total": len(augmented_ids),
            "free_text_ids_in_source_order": free_ids,
            "augmented_ids_in_source_order": augmented_ids,
            "free_text_ids_missing_from_augmented": missing,
            "descriptor_only_ids": added,
            "descriptor_only_total": len(added),
            "sets_equal": free_set == augmented_set,
            "orders_equal": free_ids == augmented_ids,
            "augmented_is_superset": free_set <= augmented_set,
            "free_text_artifact": free_summary["output"],
            "augmented_artifact": augmented_summary["output"],
            "free_text_screenshots": free_summary["screenshots"],
            "augmented_screenshots": augmented_summary["screenshots"],
        }

    union_added = [
        paper_id for paper_id in augmented_union if paper_id not in baseline_seen
    ]
    union_missing = [
        paper_id for paper_id in baseline_union if paper_id not in augmented_seen
    ]
    if union_missing:
        raise RuntimeError("PQDT augmented schedule union lost free-text records")
    if union_added != list(augmented_only_records):
        raise RuntimeError("PQDT descriptor-only record projection changed union order")

    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": (
            "complete_pending_descriptor_only_review"
            if union_added
            else "complete_no_descriptor_only_records"
        ),
        "diagnostic_only": True,
        "do_not_merge": True,
        "inputs": {
            "event_plan": {
                "path": str(plan_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(plan_path),
            },
            "run_receipt": {
                "path": str(receipt_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(receipt_path),
            },
        },
        "controls": plan["controls"],
        "comparison_method": {
            "events": 18,
            "passes_per_event": 2,
            "stable_identifier": "numeric PQDT document ID",
            "source_order": "DateAsc / Oldest first",
            "free_text": "accepted Pilot 004 bounded-wildcard schedule",
            "augmented": "free text OR validated PSUB.EXACT and IF.EXACT constructions",
            "local_union_bridge": plan["local_union_bridge"],
        },
        "partition_comparisons": comparisons,
        "union_comparison": {
            "free_text_distinct_ids": len(baseline_union),
            "augmented_distinct_ids": len(augmented_union),
            "free_text_ids_in_first_seen_schedule_order": baseline_union,
            "augmented_ids_in_first_seen_schedule_order": augmented_union,
            "free_text_ids_missing_from_augmented": union_missing,
            "descriptor_only_ids": union_added,
            "descriptor_only_total": len(union_added),
            "sets_equal": baseline_seen == augmented_seen,
        },
        "descriptor_only_records": list(augmented_only_records.values()),
        "review_required": bool(union_added),
        "interpretation": (
            "The validated descriptor constructions added no record to any partition."
            if not union_added
            else "Descriptor-only records require concept review before any adoption decision."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(
        args.plan.expanduser().resolve(), args.receipt.expanduser().resolve()
    )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 set comparison differs")
        return 0
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
