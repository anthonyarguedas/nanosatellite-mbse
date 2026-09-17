#!/usr/bin/env python3
"""Reproduce the offline integrity checks for Web of Science Pilot 004."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from assess import (
    DEFAULT_ASSESSMENT,
    DEFAULT_RECEIPT,
    DEFAULT_RECOVERY_RECEIPT,
    INITIAL_VALIDATION_RECEIPT,
    build as build_assessment,
)
from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, file_sha256, load, validate


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.ACADEMIC_SEARCH_COMMIT.json")


def check_marker(output: Path) -> list[str]:
    errors: list[str] = []
    marker = marker_path(output)
    try:
        receipt = load(marker)
        data = output.read_bytes()
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        return [f"Could not read output marker for {output}: {error}"]
    normalized = receipt.get("normalized_json", {})
    if (
        receipt.get("schema") != "academic_search_output_commit_marker_v1"
        or normalized.get("sha256") != hashlib.sha256(data).hexdigest()
        or normalized.get("bytes") != len(data)
    ):
        errors.append(f"Output marker does not bind {output}")
    return errors


def main() -> int:
    errors: list[str] = []
    plan = load(DEFAULT_OUTPUT)
    errors.extend(validate(plan))
    if plan.get("adapter", {}).get("sha256") != file_sha256(ADAPTER):
        errors.append("Installed adapter differs from the predeclared adapter")

    recovery = load(DEFAULT_RECOVERY_RECEIPT)
    selected = recovery.get("selected_artifacts", {})
    successful_outputs: list[Path] = []
    for event in plan.get("events", []):
        recovered = selected.get(event["event_id"])
        output = (
            PILOT_ROOT / recovered
            if isinstance(recovered, str)
            else PILOT_ROOT / "searches" / event["output"]
        )
        successful_outputs.append(output)
        errors.extend(check_marker(output))

    failed_output = PILOT_ROOT / "searches" / "events" / "wildcard-BG1.json"
    errors.extend(check_marker(failed_output))
    failure = load(failed_output)
    if (
        failure.get("total") is not None
        or failure.get("do_not_merge") is not True
        or failure.get("output_metadata", {}).get("status") != "error"
        or failure.get("output_metadata", {}).get("error_stage") != "connection"
        or failure.get("output_metadata", {}).get("screenshots", {}).get("complete")
        is not False
    ):
        errors.append("Retained wildcard-BG1 failure changed")

    try:
        regenerated = build_assessment(
            PILOT_ROOT,
            DEFAULT_OUTPUT,
            DEFAULT_RECEIPT,
            DEFAULT_RECOVERY_RECEIPT,
        )
        persisted = load(DEFAULT_ASSESSMENT)
        if regenerated != persisted:
            errors.append("Persisted assessment is not reproducible")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"Could not reproduce assessment: {error}")
        persisted = {}

    pngs = sorted((PILOT_ROOT / "searches").rglob("*.png"))
    if len(pngs) != 36 or len(set(pngs)) != 36:
        errors.append("Pilot does not contain 36 unique successful-event PNGs")
    if (
        persisted.get("status") != "passed"
        or persisted.get("wildcard_acceptance", {}).get("all_nine_sets_equal")
        is not True
        or persisted.get("wildcard_acceptance", {}).get("wildcard_only_wos_ids")
        != []
        or persisted.get("screenshots", {}).get("verified_file_count") != 36
        or persisted.get("schedule_reconciliation", {}).get("literal_main_union_count")
        != 154
    ):
        errors.append("Accepted assessment conclusions changed")

    initial = load(INITIAL_VALIDATION_RECEIPT)
    primary = load(DEFAULT_RECEIPT)
    if (
        initial.get("completed_event_count") != 1
        or primary.get("completed_event_count") != 12
        or recovery.get("success") is not True
        or len(successful_outputs) != 18
    ):
        errors.append("Run history changed")

    report: dict[str, Any] = {
        "schema_version": "wos-current-schedule-wildcard-pilot-validation/v1",
        "status": "passed" if not errors else "failed",
        "checks": {
            "plan": "passed" if not validate(plan) else "failed",
            "adapter_hash": (
                "passed"
                if plan.get("adapter", {}).get("sha256") == file_sha256(ADAPTER)
                else "failed"
            ),
            "successful_source_events": len(successful_outputs),
            "retained_source_failures": 1,
            "mandatory_screenshots": len(pngs),
            "marker_bound_source_artifacts": len(successful_outputs) + 1,
            "assessment_reproducible": regenerated == persisted if "regenerated" in locals() else False,
        },
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
