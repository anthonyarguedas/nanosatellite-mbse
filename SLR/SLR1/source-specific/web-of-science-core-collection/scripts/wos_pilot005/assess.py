#!/usr/bin/env python3
"""Assess the stopped Web of Science Pilot 005 broad wildcard diagnostic."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from build_plan import DEFAULT_OUTPUT, PILOT004_ROOT, PILOT_ROOT, load, validate
from build_recovery_plan import OUTPUT as RECOVERY_PLAN

OUTPUT = PILOT_ROOT / "searches" / "assessment.json"
INITIAL_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
RECOVERY_RECEIPT = PILOT_ROOT / "searches" / "recovery-run-receipt.json"


def ids(path: Path) -> list[str]:
    artifact = load(path)
    rows = artifact.get("results", [])
    return [
        row["paperId"]
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ]


def screenshot_count(path: Path) -> tuple[int, list[str]]:
    artifact = load(path)
    receipt = artifact.get("output_metadata", {}).get("screenshots", {})
    count = 0
    errors = []
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        evidence = receipt.get(key)
        if not isinstance(evidence, Mapping):
            continue
        image = path.with_name(path.name.removesuffix(".json") + suffix)
        if (
            not image.is_file()
            or evidence.get("path") != image.name
            or evidence.get("sha256") != hashlib.sha256(image.read_bytes()).hexdigest()
        ):
            errors.append(f"Screenshot receipt mismatch for {path.name} {key}")
        else:
            count += 1
    return count, errors


def build() -> dict[str, Any]:
    errors: list[str] = []
    plan = load(DEFAULT_OUTPUT)
    errors.extend(validate(plan))
    initial = load(INITIAL_RECEIPT)
    recovery_plan = load(RECOVERY_PLAN)
    recovery = load(RECOVERY_RECEIPT)
    if (
        initial.get("success") is not False
        or initial.get("successful_event_count") != 1
        or initial.get("attempt_count") != 5
        or recovery.get("success") is not False
        or recovery.get("a2_split_completed") is not False
        or len(recovery.get("outcomes", [])) != 4
        or len(recovery_plan.get("retained_failures", [])) != 3
    ):
        errors.append("Stopped run history changed")

    outcomes = [*initial.get("outcomes", []), *recovery.get("outcomes", [])]
    attempt_rows = []
    total_screenshots = 0
    source_failures = 0
    for outcome in outcomes:
        path = PILOT_ROOT / outcome["artifact"]
        artifact = load(path)
        count, shot_errors = screenshot_count(path)
        total_screenshots += count
        errors.extend(shot_errors)
        success = artifact.get("output_metadata", {}).get("status") == "success"
        if not success:
            source_failures += 1
            if artifact.get("total") is not None or artifact.get("do_not_merge") is not True:
                errors.append(f"Failure semantics changed for {path.name}")
        attempt_rows.append(
            {
                "event_id": outcome["event_id"],
                "attempt": outcome["attempt"],
                "artifact": outcome["artifact"],
                "status": artifact.get("output_metadata", {}).get("status"),
                "error_stage": artifact.get("output_metadata", {}).get("error_stage"),
                "total": artifact.get("total"),
                "screenshot_count": count,
            }
        )

    a1_path = PILOT_ROOT / initial["selected_artifacts"]["A1"]
    a1_ids = ids(a1_path)
    baseline_assessment = load(PILOT004_ROOT / "searches" / "assessment.json")
    baseline_a1 = baseline_assessment["partition_results"]["A1"]["literal"]["ordered_wos_ids"]
    a2_mh_outcome = next(
        item for item in recovery["outcomes"] if item["event_id"] == "broad-wildcard-A2-mh"
    )
    a2_mh_ids = ids(PILOT_ROOT / a2_mh_outcome["artifact"])
    if a1_ids != baseline_a1:
        errors.append("Broad A1 no longer matches the Pilot 004 literal baseline")
    if total_screenshots != 10 or source_failures != 7:
        errors.append("Attempt screenshot or failure counts changed")

    return {
        "schema_version": "wos-broad-wildcard-pilot-assessment/v1",
        "pilot": "005",
        "source": "Web of Science Core Collection",
        "status": "complete" if not errors else "invalid",
        "outcome": "broad_schedule_candidate_not_accepted",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": {
            "broad_128_family_map": "rejected_for_schedule_use",
            "reason": (
                "Broad A2 timed out at submit in three direct attempts. Its lossless M_H "
                "cell completed, while its M_B cell timed out in three unchanged attempts. "
                "No complete A2 union or schedule comparison exists."
            ),
            "pilot004_population_map": "remains_accepted_and_preferred",
            "broad_a1": "diagnostic_equal_set_only_not_adopted",
        },
        "observations": {
            "broad_a1_total": len(a1_ids),
            "broad_a1_equals_literal_baseline": a1_ids == baseline_a1,
            "broad_a2_direct_attempts": 3,
            "broad_a2_direct_result": "submit_timeout_total_null",
            "broad_a2_mh_cell_total": len(a2_mh_ids),
            "broad_a2_mb_cell_attempts": 3,
            "broad_a2_mb_cell_result": "submit_timeout_total_null",
            "unexecuted_partition_ids": ["A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"],
        },
        "attempt_accounting": {
            "attempt_count": len(attempt_rows),
            "successful_source_events": len(attempt_rows) - source_failures,
            "record_free_failures": source_failures,
            "connection_failures": sum(item["error_stage"] == "connection" for item in attempt_rows),
            "submit_failures": sum(item["error_stage"] == "submit" for item in attempt_rows),
            "retained_screenshot_files": total_screenshots,
            "attempts": attempt_rows,
        },
        "limitations": [
            "A submit timeout does not prove that one wildcard token or syntax is invalid.",
            "The stopped diagnostic does not test the broad family map in seven partitions.",
            "Only Pilot 004 supplies the accepted complete current schedule comparison.",
        ],
        "errors": errors,
    }


def main() -> int:
    if os.path.lexists(OUTPUT):
        raise SystemExit(f"Refusing to overwrite {OUTPUT}")
    assessment = build()
    OUTPUT.write_text(json.dumps(assessment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": assessment["status"], "outcome": assessment["outcome"], "errors": assessment["errors"]}, indent=2))
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
