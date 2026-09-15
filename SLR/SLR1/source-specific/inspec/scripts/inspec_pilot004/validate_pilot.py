#!/usr/bin/env python3
"""Validate Inspec Pilot 004 linked evidence and guideline synchronization."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_linked_assessment as builder

EXPECTED_FILES = (
    "linked-evidence-plan.json",
    "reconciliation.json",
    "source-translation-approval.json",
    "assessment.json",
    "validation-report.json",
)


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


def validate(search_root: Path, guideline: Path, pilot_markdown: Path) -> list[str]:
    errors: list[str] = []
    for name in EXPECTED_FILES:
        if not (search_root / name).is_file():
            errors.append(f"missing:{name}")
    if errors:
        return errors

    # Revalidate every linked source artifact, query, control, accession, and PNG.
    try:
        rebuilt = builder.build_outputs()
    except Exception as error:  # noqa: BLE001
        errors.append(f"linked_source_validation:{type(error).__name__}:{error}")
        return errors

    plan = load(search_root / "linked-evidence-plan.json")
    reconciliation = load(search_root / "reconciliation.json")
    approval = load(search_root / "source-translation-approval.json")
    assessment = load(search_root / "assessment.json")
    validation = load(search_root / "validation-report.json")

    expected_schemas = {
        "plan": builder.PLAN_SCHEMA,
        "reconciliation": builder.RECONCILIATION_SCHEMA,
        "approval": builder.APPROVAL_SCHEMA,
        "assessment": builder.ASSESSMENT_SCHEMA,
        "validation": builder.VALIDATION_SCHEMA,
    }
    values = {
        "plan": plan,
        "reconciliation": reconciliation,
        "approval": approval,
        "assessment": assessment,
        "validation": validation,
    }
    for key, schema in expected_schemas.items():
        if values[key].get("schema_version") != schema:
            errors.append(f"schema:{key}")
        if values[key].get("pilot") != builder.PILOT:
            errors.append(f"pilot:{key}")
        if values[key].get("protocol_commit") != builder.PROTOCOL_COMMIT:
            errors.append(f"protocol_commit:{key}")

    if plan.get("source_event_policy", {}).get("new_source_events") != 0:
        errors.append("duplicate_source_event")
    if len(plan.get("events", [])) != 9:
        errors.append("plan_event_count")
    if assessment.get("status") != "passed" or assessment.get("errors") != []:
        errors.append("assessment_status")
    checks = assessment.get("checks", {})
    required_checks = (
        "all_nine_current_partitions",
        "protocol_commit_pinned",
        "no_proximity_operator_in_any_query",
        "three_population_wildcards_in_every_query",
        "screenshots_beside_json",
        "separate_inspec_projection",
        "a1_literal_wildcard_sets_equal",
    )
    if any(checks.get(key) is not True for key in required_checks):
        errors.append("assessment_checks")
    if (
        checks.get("strict_source_passes") != 18
        or checks.get("expected_strict_source_passes") != 18
    ):
        errors.append("strict_passes")
    if checks.get("mandatory_screenshots") != 18 or checks.get("expected_mandatory_screenshots") != 18:
        errors.append("screenshot_count")
    if checks.get("screenshot_opt_out_available") is not False:
        errors.append("screenshot_opt_out")
    if checks.get("final_search") is not False:
        errors.append("final_search_boundary")

    events = assessment.get("events", [])
    rebuilt_events = rebuilt["assessment.json"].get("events", [])
    stable_event_keys = (
        "partition_id",
        "boolean_form",
        "query_sha256",
        "query_characters",
        "wildcard_count",
        "proximity_operator_count",
        "paired_artifact",
        "paired_artifact_sha256",
        "paired_source_total",
        "inspec_total",
        "ordered_inspec_accessions",
        "ordered_inspec_accessions_sha256",
        "strict_source_passes",
        "mandatory_screenshots",
        "status",
    )
    if len(events) != 9 or len(rebuilt_events) != 9:
        errors.append("assessment_event_count")
    else:
        for saved, current in zip(events, rebuilt_events, strict=True):
            if {key: saved.get(key) for key in stable_event_keys} != {
                key: current.get(key) for key in stable_event_keys
            }:
                errors.append(f"event_drift:{saved.get('partition_id')}")

    if reconciliation.get("event_occurrences") != 236:
        errors.append("event_occurrences")
    if reconciliation.get("unique_stable_accession_count") != 162:
        errors.append("unique_accessions")
    if len(reconciliation.get("stable_accessions", [])) != 162:
        errors.append("accession_ledger")
    if set(reconciliation.get("partitions", {})) != {
        "A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"
    }:
        errors.append("reconciliation_partitions")

    if approval.get("status") != "approved":
        errors.append("approval_status")
    if approval.get("approved_schedule_entries") != [
        "A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"
    ]:
        errors.append("approval_scope")
    if approval.get("approved_population_replacements") != list(
        builder.WILDCARD_REPLACEMENTS
    ):
        errors.append("approval_wildcards")
    if not approval.get("basis", {}).get("inspec_a1_complete_set_comparison", {}).get(
        "sets_equal"
    ):
        errors.append("approval_a1_basis")

    for name, receipt in validation.get("artifacts", {}).items():
        path = search_root / name
        if name not in EXPECTED_FILES[:-1] or not path.is_file():
            errors.append(f"validation_artifact:{name}")
            continue
        if receipt.get("sha256") != digest_file(path):
            errors.append(f"validation_hash:{name}")
    if validation.get("status") != "passed" or validation.get("errors") != []:
        errors.append("validation_status")
    if any(value is not True for value in validation.get("checks", {}).values()):
        errors.append("validation_checks")

    guideline_text = guideline.read_text(encoding="utf-8")
    pilot_text = pilot_markdown.read_text(encoding="utf-8")
    guideline_requirements = (
        "protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`",
        "Use no proximity operator",
        "(CubeSat* WN ALL)",
        "(nanosat* WN ALL)",
        "(SmallSat* WN ALL)",
        "Pilot 004",
        "F(T_precise)",
        "162 unique accessions from 236 partition occurrences",
        "no opt-out",
    )
    for text in guideline_requirements:
        if text not in guideline_text:
            errors.append(f"guideline:{text}")
    pilot_requirements = (
        "# Pilot 004",
        "no proximity",
        "18 strict source passes",
        "18 mandatory screenshots",
        "162",
        "not a final search",
    )
    for text in pilot_requirements:
        if text not in pilot_text:
            errors.append(f"pilot_markdown:{text}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-root", type=Path, default=builder.SEARCH_ROOT)
    parser.add_argument("--guideline", type=Path, default=builder.GUIDELINE)
    parser.add_argument(
        "--pilot-markdown",
        type=Path,
        default=builder.PILOT_ROOT / "pilot.md",
    )
    args = parser.parse_args()
    errors = validate(args.search_root, args.guideline, args.pilot_markdown)
    print(json.dumps({"status": "passed" if not errors else "failed", "errors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
