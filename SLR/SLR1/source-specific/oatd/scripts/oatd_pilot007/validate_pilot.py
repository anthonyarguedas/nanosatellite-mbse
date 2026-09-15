#!/usr/bin/env python3
"""Validate all retained OATD Pilot 007 hydration evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-007-validation/v1"
PILOT_ROOT = Path(__file__).resolve().parents[4] / "source-specific/oatd/pilots/007"


def has_private_context(value: Any, key: str = "") -> bool:
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
        "checkpointpath",
    }:
        return True
    if isinstance(value, Mapping):
        return any(
            has_private_context(child, str(child_key))
            for child_key, child in value.items()
        )
    if isinstance(value, list):
        return any(has_private_context(child, key) for child in value)
    if isinstance(value, str) and normalized_key in {
        "url",
        "requestedquery",
        "executedquery",
    }:
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
    checkpoint_path = PILOT_ROOT / "searches/checkpoint/hydrated-union.checkpoint.json"
    union_path = PILOT_ROOT / "searches/hydrated-union.json"
    assessment_path = PILOT_ROOT / "searches/assessment.json"
    plan = base.load(plan_path)
    run = base.load(run_path)
    checkpoint = base.load(checkpoint_path)
    union = base.load(union_path)
    assessment = base.load(assessment_path)
    adapter = base.load_adapter()
    local_path = base.REPOSITORY_ROOT / plan["local_matching_plan"]["path"]
    local_plan = adapter.load_local_matching_plan(local_path)
    pilot006_reconciliation = base.load(
        base.REPOSITORY_ROOT / plan["pilot006_evidence"]["reconciliation"]["path"]
    )
    target_ids = [record["paperId"] for record in pilot006_reconciliation["records"]]

    if (
        run.get("success") is not True
        or run.get("status") != "complete"
        or run.get("plan_sha256") != base.digest(plan_path)
        or run.get("checkpoint_completed_ids_before") != 0
        or run.get("checkpoint_completed_ids_after") != 26
        or run.get("detail_requests_this_attempt") != 26
        or run.get("detail_busy_retries_performed") != 0
        or run.get("complete_gate_count") != 8
        or run.get("complete_source_pass_count") != 16
    ):
        errors.append("run_receipt")

    gate_sets: dict[str, set[str]] = {}
    for event in plan["events"]:
        output = PILOT_ROOT / event["output"]
        try:
            artifact = base.validate_gate_artifact(adapter, output, event["event_id"])
        except Exception as error:
            errors.append(
                f"gate:{event['event_id']}:{' '.join(str(error).split())[:200]}"
            )
            continue
        initial_ids = {card["paperId"] for card in artifact["initial_pass"]["cards"]}
        confirmation_ids = {
            card["paperId"] for card in artifact["confirmation_pass"]["cards"]
        }
        if (
            artifact.get("requested_query") != queries.GATE_QUERIES[event["event_id"]]
            or artifact.get("source_total")
            != queries.EXPECTED_COUNTS[event["event_id"]]
            or initial_ids != confirmation_ids
            or artifact.get("initial_pass", {}).get("stable_record_ids_sha256")
            != event["expected_stable_record_ids_sha256"]
            or artifact.get("record_details_requested_by_gate_passes") is not False
            or artifact.get("busy_retries_performed") != 0
            or has_private_context(artifact)
        ):
            errors.append(f"gate_contract:{event['event_id']}")
        gate_sets[event["event_id"]] = initial_ids
    gate_union = set().union(*gate_sets.values()) if gate_sets else set()
    try:
        persisted_union = base.validate_union_artifact(union_path)
    except Exception as error:
        errors.append(f"union_artifact:{' '.join(str(error).split())[:200]}")
        persisted_union = union
    results = persisted_union.get("results", [])
    result_ids = [record.get("paperId") for record in results]
    if (
        result_ids != target_ids
        or set(result_ids) != gate_union
        or persisted_union.get("stable_union_ids_sha256")
        != adapter._stable_record_ids_sha256(result_ids)
        or persisted_union.get("ordered_union_ids_sha256")
        != adapter._ordered_record_ids_sha256(result_ids)
        or persisted_union.get("gate_occurrence_total") != 34
        or persisted_union.get("exact_deduplicated_union_total") != 26
        or has_private_context(persisted_union)
    ):
        errors.append("union_reconciliation")

    first_configuration = adapter.build_oatd_search_configuration(
        plan["events"][0]["query"],
        language="English",
        year_start=2011,
        year_end=2026,
        page_size=30,
    )
    normalized_results = []
    for result in results:
        record = {
            key: value
            for key, value in result.items()
            if key not in {"unionRank", "gateProvenance"}
        }
        try:
            normalized_results.append(
                adapter._validate_shared_population_checkpoint_record(
                    record,
                    configuration=first_configuration,
                    plan=local_plan,
                )
            )
        except Exception as error:
            errors.append(
                f"record:{result.get('paperId')}:{' '.join(str(error).split())[:150]}"
            )
    if (
        checkpoint.get("schema_version") != base.CHECKPOINT_SCHEMA
        or checkpoint.get("completed_ids") != target_ids
        or len(checkpoint.get("records", [])) != 26
        or [record.get("paperId") for record in checkpoint.get("records", [])]
        != target_ids
        or adapter._checkpoint_has_unsafe_content(checkpoint)
        or len(normalized_results) != 26
    ):
        errors.append("checkpoint")
    cutoff_unresolved = [
        record["paperId"]
        for record in results
        if record.get("year") == 2026 and record.get("publicationDate") == "2026"
    ]
    accounting = assessment.get("accounting", {})
    if (
        accounting.get("exact_deduplicated_union_total") != 26
        or accounting.get("complete_normalized_detail_records") != 26
        or accounting.get("unique_detail_requests") != 26
        or accounting.get("pilot004_detail_records_reused") != 0
        or accounting.get("complete_source_pass_count") != 16
        or accounting.get("busy_retries") != 0
        or len(
            assessment.get("metadata_observations", {}).get(
                "cutoff_year_records_with_unresolved_exact_day", []
            )
        )
        != 1
    ):
        errors.append("assessment")
    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "pilot": "007",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "validated_gate_count": len(gate_sets),
        "validated_source_pass_count": len(gate_sets) * 2,
        "validated_normalized_detail_records": len(normalized_results),
        "exact_deduplicated_union_total": len(set(result_ids)),
        "detail_busy_retries": run.get("detail_busy_retries_performed"),
        "cutoff_year_exact_day_unresolved_ids": cutoff_unresolved,
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
