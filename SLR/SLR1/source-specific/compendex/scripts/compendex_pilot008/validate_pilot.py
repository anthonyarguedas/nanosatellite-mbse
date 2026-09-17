#!/usr/bin/env python3
"""Validate Compendex Pilot 008 artifacts and synchronized documentation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import build_assessment
import build_plan
import queries

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
PILOT_ROOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/compendex/pilots/008"
PLAN = PILOT_ROOT / "searches/event-plan.json"
RUN_RECEIPT = PILOT_ROOT / "searches/run-receipt.json"
ASSESSMENT = PILOT_ROOT / "searches/assessment.json"
RECONCILIATION = PILOT_ROOT / "searches/reconciliation.json"
PILOT_REPORT = PILOT_ROOT / "pilot.md"
GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/compendex/source-specific-guidelines.md"
)
INSPEC_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/inspec/source-specific-guidelines.md"
)
TASKS = REPOSITORY_ROOT / "SLR/SLR1/TASKS.md"
VALIDATION_SCHEMA = "engineering-village-readiness-pilot-validation/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def without_creation_time(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "created_at_utc"}


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def validate() -> dict[str, Any]:
    errors: list[str] = []
    required = [
        PLAN,
        RUN_RECEIPT,
        ASSESSMENT,
        RECONCILIATION,
        PILOT_REPORT,
        GUIDELINE,
        INSPEC_GUIDELINE,
        TASKS,
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing:{path.relative_to(REPOSITORY_ROOT)}")
    if errors:
        return {
            "schema_version": VALIDATION_SCHEMA,
            "pilot": "008",
            "created_at_utc": now(),
            "status": "failed",
            "errors": errors,
        }

    plan = load(PLAN)
    run_receipt = load(RUN_RECEIPT)
    assessment = load(ASSESSMENT)
    reconciliation = load(RECONCILIATION)
    errors.extend(f"plan:{item}" for item in build_plan.validate(plan))

    if (
        run_receipt.get("status") != "complete"
        or run_receipt.get("success") is not True
    ):
        errors.append("run_receipt_incomplete")
    if run_receipt.get("successful_event_count") != 9:
        errors.append("successful_event_count")
    if run_receipt.get("accepted_strict_source_pass_count") != 18:
        errors.append("strict_source_pass_count")
    if run_receipt.get("accepted_mandatory_screenshot_count") != 18:
        errors.append("accepted_screenshot_count")
    if run_receipt.get("total_attempt_count") != 10:
        errors.append("total_attempt_count")

    rebuilt_assessment, rebuilt_reconciliation = build_assessment.build(
        PILOT_ROOT.relative_to(REPOSITORY_ROOT),
        PLAN.relative_to(REPOSITORY_ROOT),
        RUN_RECEIPT.relative_to(REPOSITORY_ROOT),
    )
    if rebuilt_assessment.get("status") != "passed" or rebuilt_assessment.get("errors"):
        errors.append("rebuilt_assessment")
    if without_creation_time(assessment) != without_creation_time(rebuilt_assessment):
        errors.append("assessment_rebuild_mismatch")
    if without_creation_time(reconciliation) != without_creation_time(
        rebuilt_reconciliation
    ):
        errors.append("reconciliation_rebuild_mismatch")

    checks = assessment.get("checks", {})
    expected_true = (
        "all_nine_current_partitions",
        "approved_population_wildcards_in_every_query",
        "no_proximity_operator_in_any_query",
        "adapter_v16",
        "fresh_attempt_policy_observed",
        "B2_current_strict_capture",
        "changed_definitions_live",
        "separate_database_reconciliation",
    )
    for key in expected_true:
        if checks.get(key) is not True:
            errors.append(f"assessment_check:{key}")
    if checks.get("strict_paired_source_passes") != 18:
        errors.append("assessment_strict_passes")
    if checks.get("mandatory_screenshots") != 18:
        errors.append("assessment_screenshots")
    if checks.get("retained_failed_attempts") != 1:
        errors.append("assessment_failure_count")

    outcomes = run_receipt.get("outcomes", [])
    accepted_images: list[Path] = []
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            errors.append("invalid_outcome")
            continue
        partition = outcome.get("partition_id")
        output_value = outcome.get("accepted_output")
        if partition not in queries.SCHEDULE_IDS or not isinstance(output_value, str):
            errors.append(f"invalid_outcome:{partition}")
            continue
        output = PILOT_ROOT / output_value
        if not output.is_file():
            errors.append(f"missing_output:{partition}")
            continue
        if outcome.get("accepted_output_sha256") != digest_file(output):
            errors.append(f"output_hash:{partition}")
        artifact = load(output)
        context = artifact.get("pilot_context", {})
        if (
            artifact.get("do_not_merge") is not True
            or artifact.get("output_metadata", {}).get("merge_eligible") is not False
            or context.get("status") != "strict_two_pass_complete"
            or context.get("adapter", {}).get("version") != "16"
            or context.get("query_sha256")
            != queries.digest_text(queries.EVENT_QUERIES[partition])
            or context.get("wildcard_count") != 3
            or context.get("proximity_operator_count") != 0
            or context.get("strict_complete_comparison_receipt", {}).get(
                "sequence_match"
            )
            is not True
        ):
            errors.append(f"artifact_contract:{partition}")
        screenshot_result, screenshot_errors = build_assessment.screenshot_check(
            output, artifact.get("output_metadata", {})
        )
        if screenshot_errors or screenshot_result.get("valid") is not True:
            errors.append(f"screenshots:{partition}")
        accepted_images.extend(
            [
                output.with_name(f"{output.stem}.search-page.png"),
                output.with_name(f"{output.stem}.results-page.png"),
            ]
        )

    if (
        len(accepted_images) != 18
        or len({path.resolve() for path in accepted_images}) != 18
    ):
        errors.append("accepted_image_paths")
    if not all(path.is_file() for path in accepted_images):
        errors.append("accepted_image_presence")
    all_images = list(PILOT_ROOT.glob("searches/**/*.png"))
    if len(all_images) != 18:
        errors.append("retained_image_count")

    failed_attempts = assessment.get("retained_failed_attempts", [])
    if len(failed_attempts) != 1:
        errors.append("failed_attempt_ledger")
    elif (
        failed_attempts[0].get("partition_id") != "A2"
        or failed_attempts[0].get("attempt_ordinal") != 1
        or failed_attempts[0].get("valid_null_non_mergeable_receipt") is not True
    ):
        errors.append("failed_attempt_contract")

    expected_totals = {
        "A1": (9, 6, 3),
        "A2": (43, 29, 14),
        "A3": (10, 6, 4),
        "B1": (244, 153, 91),
        "B2": (263, 173, 90),
        "BG1": (8, 6, 2),
        "BG2": (21, 13, 8),
        "BC1": (51, 32, 19),
        "BT2": (14, 9, 5),
    }
    observed_totals = {
        item.get("partition_id"): (
            item.get("paired_source_total"),
            item.get("compendex_total"),
            item.get("inspec_total"),
        )
        for item in assessment.get("events", [])
        if isinstance(item, dict)
    }
    if observed_totals != expected_totals:
        errors.append("partition_totals")

    unions = reconciliation.get("database_unions", {})
    for database, expected_count in (("compendex", 305), ("inspec", 162)):
        union = unions.get(database, {})
        accessions = union.get("stable_accessions", [])
        if (
            union.get("unique_stable_accession_count") != expected_count
            or len(accessions) != expected_count
            or union.get("exceeds_100") is not True
        ):
            errors.append(f"union:{database}")

    report = PILOT_REPORT.read_text(encoding="utf-8")
    guideline = GUIDELINE.read_text(encoding="utf-8")
    inspec_guideline = INSPEC_GUIDELINE.read_text(encoding="utf-8")
    tasks = TASKS.read_text(encoding="utf-8")
    required_report_text = (
        "**Status:** passed",
        "All 18 PNGs exist",
        "173 Compendex accessions and 90 Inspec accessions",
        "305 unique accessions",
        "162 unique accessions",
        "ready for a separate final search",
        "No final-search artifact was created",
    )
    for text in required_report_text:
        if text not in report:
            errors.append(f"pilot_report:{text}")
    if "[Pilot 008](pilots/008/pilot.md)" not in guideline:
        errors.append("compendex_guideline")
    if "Linked Compendex Pilot 008" not in inspec_guideline:
        errors.append("inspec_guideline")
    if "COMPENDEX-008" not in tasks:
        errors.append("tasks")

    final_search_files = [
        path
        for path in (
            REPOSITORY_ROOT / "SLR/SLR1/source-specific/compendex/final-searches"
        ).iterdir()
        if path.name != ".gitkeep"
    ]
    if final_search_files:
        errors.append("unexpected_final_search_artifact")

    return {
        "schema_version": VALIDATION_SCHEMA,
        "pilot": "008",
        "created_at_utc": now(),
        "status": "passed" if not errors else "failed",
        "checks": {
            "predeclared_plan": not any(item.startswith("plan:") for item in errors),
            "all_nine_current_queries": observed_totals == expected_totals,
            "approved_wildcards": checks.get(
                "approved_population_wildcards_in_every_query"
            ),
            "no_proximity": checks.get("no_proximity_operator_in_any_query"),
            "adapter_v16": checks.get("adapter_v16"),
            "strict_paired_source_passes": checks.get("strict_paired_source_passes"),
            "verified_mandatory_screenshots": checks.get("mandatory_screenshots"),
            "B2_confirmed": checks.get("B2_current_strict_capture"),
            "changed_definitions_live": checks.get("changed_definitions_live"),
            "separate_reconciliation": checks.get("separate_database_reconciliation"),
            "final_search_absent": not final_search_files,
            "documentation_synchronized": not any(
                item in errors
                for item in (
                    "compendex_guideline",
                    "inspec_guideline",
                    "tasks",
                )
            ),
        },
        "artifact_hashes": {
            str(path.relative_to(REPOSITORY_ROOT)): digest_file(path)
            for path in (PLAN, RUN_RECEIPT, ASSESSMENT, RECONCILIATION, PILOT_REPORT)
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=PILOT_ROOT / "searches/validation-report.json",
    )
    args = parser.parse_args()
    report = validate()
    write_new(args.output, report)
    print(json.dumps({"status": report["status"], "errors": report["errors"]}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
