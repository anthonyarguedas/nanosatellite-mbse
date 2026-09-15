#!/usr/bin/env python3
"""Resume OATD Pilot 004 after the multiple-resource-URL repair."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import queries
import run_page_size_retry as page_retry
import run_pilot as base

SCHEMA = "oatd-pilot-004-resource-url-repair-plan/v1"
RECEIPT_SCHEMA = "oatd-pilot-004-resource-url-repair-receipt/v1"


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[Any, dict[str, Any], Path, Path, Path]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != SCHEMA
        or plan.get("pilot") != "004"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or len(events) != 1
    ):
        raise RuntimeError("Unexpected OATD Pilot 004 resource-URL repair plan")
    prior_descriptor = plan.get("rate_safe_retry_plan")
    if not isinstance(prior_descriptor, dict):
        raise RuntimeError("The rate-safe retry plan binding is missing")
    prior_path = pilot_root / prior_descriptor.get("path", "")
    if (
        prior_descriptor.get("path") != "searches/event-plan.rate-safe.json"
        or not prior_path.is_file()
        or base.file_sha256(prior_path) != prior_descriptor.get("sha256")
    ):
        raise RuntimeError("The rate-safe retry plan changed")
    event = events[0]
    if event != base.load(prior_path).get("events", [{}])[0]:
        raise RuntimeError("The resource-URL repair changed the source event")

    adapter = base.load_adapter()
    adapter_descriptor = plan.get("adapter")
    if (
        not isinstance(adapter_descriptor, dict)
        or adapter_descriptor.get("id") != adapter.ADAPTER_ID
        or adapter_descriptor.get("version") != adapter.ADAPTER_VERSION
        or adapter.ADAPTER_VERSION != "10"
    ):
        raise RuntimeError("The resource-URL repair adapter version changed")
    files = adapter_descriptor.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("The repaired adapter bindings are missing")
    for name, path in base.ADAPTER_FILES.items():
        descriptor = files.get(name)
        if not isinstance(descriptor, dict) or descriptor.get(
            "sha256"
        ) != base.file_sha256(path):
            raise RuntimeError(f"The resource-URL OATD adapter changed: {name}")
    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("Resource-URL retry script bindings are missing")
    for relative, expected_hash in scripts.items():
        path = base.REPOSITORY_ROOT / relative
        if not path.is_file() or base.file_sha256(path) != expected_hash:
            raise RuntimeError(f"A resource-URL retry script changed: {relative}")

    local_plan = pilot_root / event["local_matching_plan"]
    checkpoint = pilot_root / event["checkpoint"]
    output = pilot_root / event["output"]
    if not local_plan.is_file() or not checkpoint.is_file() or output.exists():
        raise RuntimeError("The resource-URL retry input or output state is invalid")
    typed_plan = adapter.load_local_matching_plan(local_plan)
    configuration = adapter.build_oatd_search_configuration(
        event["query"],
        language=event["language"],
        year_start=event["year_start"],
        year_end=event["year_end"],
        page_size=event["page_size"],
    )
    checkpoint_value = adapter.load_shared_population_checkpoint(
        checkpoint,
        configuration=configuration,
        plan=typed_plan,
    )
    source = checkpoint_value.get("source_population", {})
    repair = plan.get("resource_url_repair", {})
    if (
        len(checkpoint_value.get("completed_ids", []))
        < repair.get("minimum_completed_ids", 0)
        or source.get("source_reported_total") != repair.get("source_reported_total")
        or source.get("stable_record_ids_sha256")
        != repair.get("stable_record_ids_sha256")
        or source.get("page_size") != 30
    ):
        raise RuntimeError("The resource-URL retry checkpoint identity changed")
    resolved_paths = {
        path.resolve() for path in (plan_path, local_plan, checkpoint, output)
    }
    if len(resolved_paths) != 4:
        raise RuntimeError("Resource-URL retry paths collide")
    return adapter, event, local_plan, checkpoint, output


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    final_receipt_path: Path,
) -> int:
    plan = base.load(plan_path)
    adapter, event, local_plan, checkpoint, output = validate_plan(
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
    started = base.now()
    completed_before = len(base.load(checkpoint).get("completed_ids", []))
    process = subprocess.run(
        base.command(event, local_plan, checkpoint, output), check=False
    )
    completed_after = (
        len(base.load(checkpoint).get("completed_ids", []))
        if checkpoint.is_file()
        else None
    )
    outcome: dict[str, Any] = {
        "event_id": event["event_id"],
        "started_at_utc": started,
        "completed_at_utc": base.now(),
        "return_code": process.returncode,
        "page_size": 30,
        "max_pages": 100,
        "page_delay_seconds": 6.0,
        "detail_delay_seconds": 6.0,
        "resumed_from_checkpoint": True,
        "checkpoint_completed_ids_before": completed_before,
        "checkpoint_completed_ids_after": completed_after,
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

    artifact = base.load(output)
    page_retry.validate_page_size_30_success(adapter, artifact, event, output)
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
    final_receipt["successful_operational_refinements"] = [
        {
            "page_size": "100 to 30",
            "max_pages": "30 to 100",
            "source_semantics_changed": False,
        },
        {
            "checkpoint_public_text_safety_scan": "narrowed to operational locations",
            "public_bibliographic_text_changed": False,
            "source_semantics_changed": False,
        },
        {
            "page_delay_seconds": "0.75 to 6.0",
            "detail_delay_seconds": "0.5 to 6.0",
            "source_semantics_changed": False,
        },
        {
            "multiple_resource_urls": "landing and direct PDF retained separately",
            "source_records_removed": 0,
            "source_semantics_changed": False,
        },
    ]
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
