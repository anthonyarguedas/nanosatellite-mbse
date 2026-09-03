#!/usr/bin/env python3
"""Validate retained OATD Pilot 006 card-ID evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-006-validation/v1"
PILOT_ROOT = Path(__file__).resolve().parents[2] / "source-specific/oatd/pilots/006"


def unsafe_public_value(value: Any, key: str = "") -> bool:
    normalized_key = "".join(
        character for character in key.casefold() if character.isalnum()
    )
    if normalized_key in {
        "cookie",
        "cookies",
        "browsercontext",
        "browsertarget",
        "cdpurl",
        "detailrecordparameter",
        "queryurl",
    }:
        return True
    if isinstance(value, dict):
        return any(
            unsafe_public_value(child, str(child_key))
            for child_key, child in value.items()
        )
    if isinstance(value, list):
        return any(unsafe_public_value(child, key) for child in value)
    if isinstance(value, str):
        lowered = value.casefold()
        return any(
            marker in lowered
            for marker in (
                "/users/",
                "ws://",
                "devtools/",
                "127.0.0.1",
                "oatd/search?q=",
                "oatd/record?record=",
            )
        )
    return False


def validate() -> dict[str, Any]:
    errors: list[str] = []
    plan_path = PILOT_ROOT / "searches/event-plan.json"
    run_path = PILOT_ROOT / "searches/run-receipt.json"
    reconciliation_path = PILOT_ROOT / "searches/reconciliation.json"
    assessment_path = PILOT_ROOT / "searches/assessment.json"
    plan = base.load(plan_path)
    run = base.load(run_path)
    reconciliation = base.load(reconciliation_path)
    assessment = base.load(assessment_path)
    adapter = base.load_adapter()

    if (
        run.get("success") is not True
        or run.get("completed_gate_count") != 8
        or run.get("stopped_after_failure") is not False
        or run.get("plan_sha256") != base.digest(plan_path)
    ):
        errors.append("run_receipt")
    gate_sets: dict[str, set[str]] = {}
    occurrence_total = 0
    for event in plan.get("events", []):
        output = PILOT_ROOT / event["output"]
        try:
            artifact = base.validate_gate_artifact(adapter, output, event["event_id"])
        except Exception as error:
            errors.append(
                f"gate:{event['event_id']}:{' '.join(str(error).split())[:200]}"
            )
            continue
        if artifact.get("requested_query") != queries.GATE_QUERIES[event["event_id"]]:
            errors.append(f"query:{event['event_id']}")
        if (
            artifact.get("source_total")
            != queries.EXPECTED_PILOT005_COUNTS[event["event_id"]]
        ):
            errors.append(f"total:{event['event_id']}")
        if (
            artifact.get("record_details_requested") is not False
            or artifact.get("records_hydrated") != 0
            or unsafe_public_value(artifact)
        ):
            errors.append(f"privacy_or_detail:{event['event_id']}")
        ids = {card["paperId"] for card in artifact["first_pass"]["cards"]}
        gate_sets[event["event_id"]] = ids
        occurrence_total += len(ids)
    union = set().union(*gate_sets.values()) if gate_sets else set()
    records = reconciliation.get("records")
    reconciliation_ids = (
        [record.get("paperId") for record in records]
        if isinstance(records, list)
        else []
    )
    if (
        occurrence_total != 34
        or len(union) != 26
        or len(reconciliation_ids) != 26
        or len(set(reconciliation_ids)) != 26
        or set(reconciliation_ids) != union
        or reconciliation.get("gate_occurrence_total") != 34
        or reconciliation.get("exact_deduplicated_union_total") != 26
        or reconciliation.get("cross_gate_duplicate_occurrences") != 8
        or reconciliation.get("stable_union_ids_sha256")
        != adapter._stable_record_ids_sha256(reconciliation_ids)
        or reconciliation.get("ordered_union_ids_sha256")
        != adapter._ordered_record_ids_sha256(reconciliation_ids)
        or reconciliation.get("record_details_requested") is not False
        or reconciliation.get("records_hydrated") != 0
        or unsafe_public_value(reconciliation)
    ):
        errors.append("reconciliation")
    reuse = reconciliation.get("pilot004_checkpoint_reuse", {})
    if (
        reuse.get("validated_detail_records_available") != 9
        or len(reuse.get("paper_ids", [])) != 9
        or reuse.get("remaining_unique_details_to_hydrate") != 17
        or reuse.get("reuse_is_approved_for_final_search") is not False
    ):
        errors.append("checkpoint_reuse_accounting")
    accounting = assessment.get("accounting", {})
    if (
        accounting.get("complete_source_pass_count") != 16
        or accounting.get("source_detail_requests") != 0
        or accounting.get("gate_occurrence_total") != 34
        or accounting.get("exact_deduplicated_union_total") != 26
        or accounting.get("cross_gate_duplicate_occurrences") != 8
    ):
        errors.append("assessment")
    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "pilot": "006",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "validated_gate_count": len(gate_sets),
        "validated_source_pass_count": len(gate_sets) * 2,
        "gate_occurrence_total": occurrence_total,
        "exact_deduplicated_union_total": len(union),
        "record_detail_requests": 0,
        "do_not_merge": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=PILOT_ROOT / "searches/validation-report.json",
    )
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    report = validate()
    base.write_exclusive_json(args.output, report)
    print(json.dumps(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
