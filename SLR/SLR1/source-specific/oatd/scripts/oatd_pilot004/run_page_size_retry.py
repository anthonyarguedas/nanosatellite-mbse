#!/usr/bin/env python3
"""Run the predeclared OATD Pilot 004 native-page-size retry."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-004-page-size-retry-plan/v1"
RECEIPT_SCHEMA = "oatd-pilot-004-page-size-retry-receipt/v1"


def validate_retry_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[dict[str, Any], Path, Path, Path]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != SCHEMA
        or plan.get("pilot") != "004"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or len(events) != 1
    ):
        raise RuntimeError("Unexpected OATD Pilot 004 page-size retry plan")
    initial_descriptor = plan.get("initial_plan")
    if not isinstance(initial_descriptor, dict):
        raise RuntimeError("The initial plan binding is missing")
    initial_path = pilot_root / initial_descriptor.get("path", "")
    if (
        initial_descriptor.get("path") != "searches/event-plan.json"
        or not initial_path.is_file()
        or base.file_sha256(initial_path) != initial_descriptor.get("sha256")
    ):
        raise RuntimeError("The initial OATD Pilot 004 plan changed")
    initial = base.load(initial_path)
    initial_event, local_plan, checkpoint, output = base.validate_plan(
        initial, initial_path, pilot_root
    )

    event = events[0]
    permitted_changes = {
        "page_size": (100, 30),
        "max_pages": (30, 100),
    }
    for key, value in initial_event.items():
        if key in permitted_changes:
            if (
                value != permitted_changes[key][0]
                or event.get(key) != permitted_changes[key][1]
            ):
                raise RuntimeError(f"The predeclared {key} refinement changed")
        elif event.get(key) != value:
            raise RuntimeError(f"The retry changed source semantics at {key}")
    if set(event) != set(initial_event):
        raise RuntimeError("The retry event shape differs from the initial event")

    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("The retry script bindings are missing")
    for relative, expected_hash in scripts.items():
        path = base.REPOSITORY_ROOT / relative
        if not path.is_file() or base.file_sha256(path) != expected_hash:
            raise RuntimeError(f"A retry source script changed: {relative}")
    if plan.get("adapter") != initial.get("adapter"):
        raise RuntimeError("The retry changed the predeclared adapter")
    if plan_path.resolve() in {
        output.resolve(),
        checkpoint.resolve(),
        local_plan.resolve(),
    }:
        raise RuntimeError("The retry plan path collides with an execution artifact")
    return event, local_plan, checkpoint, output


def validate_page_size_30_success(
    adapter: Any,
    artifact: dict[str, Any],
    event: dict[str, Any],
    output: Path,
) -> None:
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
    expected_query = (
        f"{event['query']} AND language:(en OR eng OR english) AND "
        "pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
    )
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("requested_query") != event["query"]
        or artifact.get("executed_query") != expected_query
        or not isinstance(total, int)
        or isinstance(total, bool)
        or total < 1
        or not isinstance(results, list)
        or len(results) != total
        or len({record.get("paperId") for record in results}) != total
        or not isinstance(metadata, dict)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("require_complete") is not True
        or metadata.get("strict_complete_pass_count") != 2
        or metadata.get("strict_stable_record_id_set_reconciled") is not True
        or metadata.get("source_population_total") != total
        or metadata.get("page_size") != 30
        or metadata.get("observed_exact_query_echo") is not True
        or not isinstance(source_population, dict)
        or source_population.get("source_reported_total") != total
        or source_population.get("page_size") != 30
        or source_population.get("two_complete_id_passes_reconciled") is not True
        or not isinstance(local, dict)
        or local.get("plan_sha256")
        != base.load(output.parent / "local-matching-plan.json").get("plan_sha256")
        or local.get("mode") != "annotation_only_no_source_record_exclusion"
    ):
        raise RuntimeError("The page-size-30 shared harvest is incomplete")
    expressions = local.get("expressions")
    if (
        not isinstance(expressions, list)
        or [item.get("id") for item in expressions] != list(queries.SCHEDULE_IDS)
        or any(
            item.get("retained_source_population_records") != total
            or sum(
                item.get(key, -total)
                for key in (
                    "local_match_count",
                    "visible_fields_nonmatch_count",
                    "unresolved_missing_required_field_count",
                )
            )
            != total
            for item in expressions
        )
        or any(
            record.get("localMatching", {}).get("exclusion_status")
            != "unresolved_for_exclusion"
            for record in results
        )
    ):
        raise RuntimeError("The current local schedule annotations are incomplete")
    base.validate_screenshot_receipt(artifact, output)
    if not adapter._is_strict_complete_oatd_result(artifact):
        raise RuntimeError("The adapter strict verifier rejected the retry artifact")
    if not adapter.verify_commit_gated_publication(output, artifact):
        raise RuntimeError("The retry publication marker did not verify")


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    final_receipt_path: Path,
) -> int:
    plan = base.load(plan_path)
    event, local_plan, checkpoint, output = validate_retry_plan(
        plan, plan_path, pilot_root
    )
    screenshots = base.expected_screenshot_paths(output)
    marker = output.with_name(f".{output.name}.OATD_COMMIT.json")
    revocation = Path(f"{marker}.revoked")
    if any(
        os.path.lexists(path)
        for path in (output, marker, revocation, *screenshots.values())
    ):
        raise RuntimeError("Refusing to overwrite an existing OATD Pilot 004 output")
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    started = base.now()
    resumed = checkpoint.exists()
    process = subprocess.run(
        base.command(event, local_plan, checkpoint, output), check=False
    )
    outcome: dict[str, Any] = {
        "event_id": event["event_id"],
        "started_at_utc": started,
        "completed_at_utc": base.now(),
        "return_code": process.returncode,
        "page_size": 30,
        "max_pages": 100,
        "resumed_from_checkpoint": resumed,
        "checkpoint_exists": checkpoint.is_file(),
        "output_exists": output.is_file(),
        "search_page_screenshot_exists": screenshots["search_page"].is_file(),
        "results_page_screenshot_exists": screenshots["results_page"].is_file(),
    }
    if process.returncode != 0 or not output.is_file():
        receipt = {
            "schema_version": RECEIPT_SCHEMA,
            "source": plan["source"],
            "pilot": "004",
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "status": "stopped_on_source_or_adapter_failure",
            "do_not_merge": True,
            "started_at_utc": started,
            "completed_at_utc": base.now(),
            "retry_plan": str(plan_path.relative_to(pilot_root)),
            "outcomes": [outcome],
        }
        base.write_atomic(receipt_path, receipt)
        return 1

    adapter = base.load_adapter()
    artifact = base.load(output)
    validate_page_size_30_success(adapter, artifact, event, output)
    marking = base.mark_pilot_only(artifact, output, adapter)
    checkpoint_value = base.load(checkpoint)
    outcome.update(
        {
            "contract_complete": True,
            "source_total": artifact["total"],
            "records_retained": len(artifact["results"]),
            "checkpoint_completed_ids": len(checkpoint_value.get("completed_ids", [])),
            "checkpoint_sha256": base.file_sha256(checkpoint),
            "screenshots": {
                key: {
                    "path": str(path.relative_to(pilot_root)),
                    "sha256": base.file_sha256(path),
                }
                for key, path in screenshots.items()
            },
            "pilot_marking": marking,
        }
    )
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "source": plan["source"],
        "pilot": "004",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "status": "complete",
        "do_not_merge": True,
        "started_at_utc": started,
        "completed_at_utc": base.now(),
        "retry_plan": str(plan_path.relative_to(pilot_root)),
        "predeclared_event_count": 1,
        "completed_event_count": 1,
        "outcomes": [outcome],
    }
    base.write_atomic(receipt_path, receipt)
    final_receipt = dict(receipt)
    final_receipt["schema_version"] = "oatd-pilot-004-run-receipt/v1"
    final_receipt["event_plan"] = str(plan_path.relative_to(pilot_root))
    final_receipt["successful_operational_refinement"] = {
        "page_size": "100 to 30",
        "max_pages": "30 to 100",
        "source_semantics_changed": False,
    }
    base.write_atomic(final_receipt_path, final_receipt)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retry-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--final-receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(
            args.retry_plan,
            args.pilot_root,
            args.receipt,
            args.final_receipt,
        )
    except Exception as error:
        print(" ".join(str(error).split())[:1000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
