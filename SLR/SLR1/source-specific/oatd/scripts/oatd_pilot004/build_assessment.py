#!/usr/bin/env python3
"""Build the OATD Pilot 004 shared-population assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import queries

SCHEMA = "oatd-pilot-004-assessment/v1"
LOCAL_STATUSES = (
    "matched",
    "visible_fields_nonmatch",
    "unresolved_missing_required_field",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def screenshot_paths(output: Path) -> dict[str, Path]:
    return {
        "search_page": output.with_name(f"{output.stem}.search-page.png"),
        "results_page": output.with_name(f"{output.stem}.results-page.png"),
    }


def build(root: Path) -> dict[str, Any]:
    searches = root / "searches"
    plan_path = searches / "event-plan.json"
    local_plan_path = searches / "local-matching-plan.json"
    receipt_path = searches / "run-receipt.json"
    plan = load(plan_path)
    local_plan = load(local_plan_path)
    receipt = load(receipt_path)
    event = plan.get("events", [{}])[0]
    output = root / event.get("output", "")
    checkpoint = root / event.get("checkpoint", "")
    artifact = load(output)
    checkpoint_value = load(checkpoint)
    errors: list[str] = []

    if (
        plan.get("schema_version") != "oatd-pilot-004-event-plan/v1"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("event_count") != 1
        or event.get("query") != queries.P_QUERY
        or receipt.get("schema_version") != "oatd-pilot-004-run-receipt/v1"
        or receipt.get("status") != "complete"
        or receipt.get("completed_event_count") != 1
    ):
        errors.append("The predeclared one-event execution is incomplete")

    outcomes = receipt.get("outcomes")
    outcome = outcomes[0] if isinstance(outcomes, list) and len(outcomes) == 1 else {}
    if (
        outcome.get("return_code") != 0
        or outcome.get("contract_complete") is not True
        or outcome.get("output_exists") is not True
        or outcome.get(
            "source_artifact_pilot_sha256",
            outcome.get("pilot_marking", {}).get("source_artifact_pilot_sha256"),
        )
        not in (None, file_sha256(output))
    ):
        errors.append("The run receipt does not bind one complete source event")

    metadata = artifact.get("output_metadata")
    results = artifact.get("results")
    total = artifact.get("total")
    shared = (
        metadata.get("shared_population_harvest")
        if isinstance(metadata, dict)
        else None
    )
    source_population = (
        shared.get("source_population") if isinstance(shared, dict) else None
    )
    local = metadata.get("local_matching") if isinstance(metadata, dict) else None
    pilot_context = artifact.get("pilot_context")
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("requested_query") != queries.P_QUERY
        or not isinstance(total, int)
        or isinstance(total, bool)
        or total < 1
        or not isinstance(results, list)
        or len(results) != total
        or len({record.get("paperId") for record in results}) != total
        or not isinstance(metadata, dict)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("strict_complete_pass_count") != 2
        or metadata.get("strict_stable_record_id_set_reconciled") is not True
        or metadata.get("source_population_total") != total
        or metadata.get("client_side_exclusions") != 0
        or artifact.get("do_not_merge") is not True
        or metadata.get("merge_eligible") is not False
        or metadata.get("normalized_merge_eligible") is not False
        or metadata.get("pilot_only") is not True
        or not isinstance(pilot_context, dict)
        or pilot_context.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or pilot_context.get("source_submission") != "P only"
        or not isinstance(source_population, dict)
        or source_population.get("source_reported_total") != total
        or source_population.get("two_complete_id_passes_reconciled") is not True
        or not isinstance(local, dict)
        or local.get("plan_sha256") != local_plan.get("plan_sha256")
        or local.get("mode") != "annotation_only_no_source_record_exclusion"
    ):
        errors.append("The P-only source artifact or pilot marking is incomplete")

    record_ids = (
        [record.get("paperId") for record in results]
        if isinstance(results, list)
        else []
    )
    if any(not isinstance(record_id, str) or not record_id for record_id in record_ids):
        errors.append("A retained record lacks a stable OATD ID")

    local_expressions = local.get("expressions") if isinstance(local, dict) else None
    aggregate_by_id = {
        item.get("id"): item
        for item in local_expressions or []
        if isinstance(item, dict)
    }
    record_counts = {
        schedule_id: Counter({status: 0 for status in LOCAL_STATUSES})
        for schedule_id in queries.SCHEDULE_IDS
    }
    matched_union = 0
    no_match_visible = 0
    unresolved_union = 0
    for record in results if isinstance(results, list) else []:
        annotations = record.get("localMatching", {}).get("expressions")
        if (
            not isinstance(annotations, list)
            or [item.get("id") for item in annotations] != list(queries.SCHEDULE_IDS)
            or record.get("localMatching", {}).get("exclusion_status")
            != "unresolved_for_exclusion"
        ):
            errors.append(
                "A retained record lacks the complete local schedule annotation"
            )
            continue
        statuses = []
        for item in annotations:
            status = item.get("status")
            schedule_id = item.get("id")
            if schedule_id not in record_counts or status not in LOCAL_STATUSES:
                errors.append("A local schedule annotation has an invalid status")
                continue
            record_counts[schedule_id][status] += 1
            statuses.append(status)
        if "matched" in statuses:
            matched_union += 1
        elif statuses and all(
            status == "visible_fields_nonmatch" for status in statuses
        ):
            no_match_visible += 1
        else:
            unresolved_union += 1

    partition_summary: dict[str, Any] = {}
    for schedule_id in queries.SCHEDULE_IDS:
        counts = record_counts[schedule_id]
        aggregate = aggregate_by_id.get(schedule_id)
        expected_counts = {
            "matched": aggregate.get("local_match_count") if aggregate else None,
            "visible_fields_nonmatch": (
                aggregate.get("visible_fields_nonmatch_count") if aggregate else None
            ),
            "unresolved_missing_required_field": (
                aggregate.get("unresolved_missing_required_field_count")
                if aggregate
                else None
            ),
        }
        if (
            aggregate is None
            or aggregate.get("expression") != queries.LOCAL_SCHEDULE[schedule_id]
            or aggregate.get("retained_source_population_records") != total
            or dict(counts) != expected_counts
            or sum(counts.values()) != total
        ):
            errors.append(
                f"The {schedule_id} aggregate does not match record annotations"
            )
        partition_summary[schedule_id] = {
            "local_match_count": counts["matched"],
            "visible_fields_nonmatch_count": counts["visible_fields_nonmatch"],
            "unresolved_missing_required_field_count": counts[
                "unresolved_missing_required_field"
            ],
            "retained_source_population_records": total,
            "source_reported_partition_total": None,
            "interpretation": "local annotation only",
        }

    field_states: dict[str, Counter[str]] = {
        field: Counter()
        for field in (
            "title",
            "author",
            "abstract",
            "publisher",
            "subject",
            "discipline",
        )
    }
    date_statuses: Counter[str] = Counter()
    for record in results if isinstance(results, list) else []:
        states = record.get("detailFieldStates")
        if not isinstance(states, dict):
            errors.append("A retained record lacks detail field-state evidence")
            continue
        for field in field_states:
            field_states[field][str(states.get(field))] += 1
        date_statuses[str(record.get("publicationDateReadback", {}).get("status"))] += 1

    screenshots = metadata.get("screenshots") if isinstance(metadata, dict) else None
    screenshot_summary: dict[str, Any] = {}
    if (
        not isinstance(screenshots, dict)
        or screenshots.get("schema_version") != "oatd-automatic-screenshots/v1"
        or screenshots.get("automatic") is not True
        or screenshots.get("opt_out_available") is not False
        or screenshots.get("same_directory_as_json") is not True
    ):
        errors.append("Mandatory automatic screenshot metadata is missing")
    for key, path in screenshot_paths(output).items():
        evidence = screenshots.get(key) if isinstance(screenshots, dict) else None
        if (
            not path.is_file()
            or not isinstance(evidence, dict)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != file_sha256(path)
            or not isinstance(evidence.get("width"), int)
            or evidence["width"] < 1
            or not isinstance(evidence.get("height"), int)
            or evidence["height"] < 1
        ):
            errors.append(f"The {key} screenshot does not match its receipt")
        screenshot_summary[key] = {
            "path": str(path.relative_to(root)),
            "sha256": file_sha256(path) if path.is_file() else None,
            "width": evidence.get("width") if isinstance(evidence, dict) else None,
            "height": evidence.get("height") if isinstance(evidence, dict) else None,
        }

    checkpoint_records = checkpoint_value.get("records")
    if (
        checkpoint_value.get("schema_version") != "oatd-shared-population-checkpoint/v1"
        or checkpoint_value.get("local_matching", {}).get("plan_sha256")
        != local_plan.get("plan_sha256")
        or len(checkpoint_value.get("completed_ids", [])) != total
        or not isinstance(checkpoint_records, list)
        or len(checkpoint_records) != total
        or outcome.get("checkpoint_sha256") != file_sha256(checkpoint)
    ):
        errors.append("The durable checkpoint does not cover the complete population")

    marker = output.with_name(f".{output.name}.OATD_COMMIT.json")
    revocation = Path(f"{marker}.revoked")
    marking = outcome.get("pilot_marking") if isinstance(outcome, dict) else None
    if (
        not marker.is_file()
        or not revocation.is_file()
        or not isinstance(marking, dict)
        or marking.get("source_artifact_pilot_sha256") != file_sha256(output)
        or marking.get("commit_marker_sha256") != file_sha256(marker)
        or marking.get("revocation_marker_sha256") != file_sha256(revocation)
    ):
        errors.append("The pilot-only marker revocation is incomplete")

    accepted = not errors
    return {
        "schema_version": SCHEMA,
        "status": "complete" if accepted else "error",
        "source": plan.get("source"),
        "pilot": "004",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": (
            "accept_P_only_source_harvest_with_local_schedule_annotations"
            if accepted
            else "do_not_accept_pending_validation_errors"
        ),
        "decision_basis": (
            "The exact controlled P route produced a complete stable-ID population, two "
            "reconciled source snapshots, one complete detail record per ID, all nine "
            "current local schedule annotations per record, and both mandatory screenshots."
            if accepted
            else "One or more predeclared acceptance checks failed."
        ),
        "source_submission": {
            "query_id": "P-shared",
            "query_sha256": event.get("query_sha256"),
            "source_reported_total": total,
            "records_retained": len(results) if isinstance(results, list) else None,
            "stable_record_ids_sha256": (
                source_population.get("stable_record_ids_sha256")
                if isinstance(source_population, dict)
                else None
            ),
            "two_complete_id_passes_reconciled": (
                source_population.get("two_complete_id_passes_reconciled")
                if isinstance(source_population, dict)
                else None
            ),
            "native_order_drift_observed": (
                source_population.get("native_order_drift_observed")
                if isinstance(source_population, dict)
                else None
            ),
        },
        "local_schedule": {
            "plan_sha256": local_plan.get("plan_sha256"),
            "annotation_only": True,
            "source_partition_totals_observed": False,
            "local_negative_records_removed": 0,
            "partitions": partition_summary,
            "record_union": {
                "matched_one_or_more_local_partitions": matched_union,
                "visible_nonmatch_for_all_partitions": no_match_visible,
                "unresolved_for_one_or_more_partitions_without_a_match": unresolved_union,
                "retained_population": total,
            },
        },
        "visible_detail_field_states": {
            field: dict(sorted(counts.items()))
            for field, counts in field_states.items()
        },
        "publication_date_readback_statuses": dict(sorted(date_statuses.items())),
        "automatic_screenshots": {
            "required": True,
            "opt_out_available": False,
            "same_directory_as_json": True,
            "files": screenshot_summary,
        },
        "checkpoint": {
            "path": str(checkpoint.relative_to(root)),
            "sha256": file_sha256(checkpoint),
            "completed_ids": len(checkpoint_value.get("completed_ids", [])),
            "normalized_records": len(checkpoint_records)
            if isinstance(checkpoint_records, list)
            else None,
            "response_bodies_persisted": False,
            "local_paths_persisted_in_checkpoint": False,
        },
        "pilot_marking": marking,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assessment = build(args.pilot_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
