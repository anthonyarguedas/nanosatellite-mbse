#!/usr/bin/env python3
"""Validate the accepted NASA NTRS schedule, wildcard, and screenshot evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import queries

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_plan_script_hashes(plan: dict[str, Any], root: Path, errors: list[str]) -> None:
    for relative, expected in plan.get("source_affecting_scripts", {}).items():
        path = root / relative
        if not path.is_file() or digest(path) != expected:
            errors.append(f"source-affecting script mismatch: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--pilot004-root", type=Path, required=True)
    parser.add_argument("--pilot005-root", type=Path, required=True)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    errors: list[str] = []
    p004_run = load(args.pilot004_root / "searches/run-receipt.json")
    p004_continuation = load(
        args.pilot004_root / "searches/continuation-run-receipt.json"
    )
    if p004_run.get("success") is not False or p004_continuation.get("success") is not False:
        errors.append("Pilot 004 null failures were not retained")
    for receipt in (p004_run, p004_continuation):
        for event in receipt.get("outcomes", receipt.get("events", [])):
            attempts = event.get("attempts", [event])
            for attempt in attempts:
                if attempt.get("total") is not None:
                    errors.append("Pilot 004 failure acquired a numeric total")

    p005_plan_path = args.pilot005_root / "searches/event-plan.json"
    p005_run_path = args.pilot005_root / "searches/run-receipt.json"
    p005_assessment_path = args.pilot005_root / "searches/assessment.json"
    p005_plan = load(p005_plan_path)
    p005_run = load(p005_run_path)
    p005 = load(p005_assessment_path)
    if p005.get("status") != "passed":
        errors.append("Pilot 005 assessment did not pass")
    if p005.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Pilot 005 protocol commit mismatch")
    if p005.get("accepted_source_event_count") != 18:
        errors.append("Pilot 005 accepted event count mismatch")
    if p005.get("verified_accepted_screenshot_file_count") != 36:
        errors.append("Pilot 005 screenshot count mismatch")
    if p005.get("wildcard", {}).get("decision") != (
        "adopt_standalone_wildcards_for_all_main_partitions"
    ):
        errors.append("Pilot 005 wildcard decision mismatch")
    if any(item.get("set_relation") != "equal" for item in p005.get("comparisons", [])):
        errors.append("Pilot 005 has a partition set difference")
    if p005.get("schedule_union", {}).get("literal_unique_ids") != 14:
        errors.append("Pilot 005 literal union mismatch")
    if p005.get("schedule_union", {}).get("wildcard_unique_ids") != 14:
        errors.append("Pilot 005 wildcard union mismatch")
    if p005_run.get("success") is not True or p005_run.get("source_attempt_count") != 19:
        errors.append("Pilot 005 run receipt mismatch")

    p006_plan_path = args.pilot006_root / "searches/event-plan.json"
    p006_run_path = args.pilot006_root / "searches/run-receipt.json"
    p006_assessment_path = args.pilot006_root / "searches/assessment.json"
    p006_plan = load(p006_plan_path)
    p006_run = load(p006_run_path)
    p006 = load(p006_assessment_path)
    if p006.get("status") != "passed":
        errors.append("Pilot 006 evidence validation did not pass")
    if p006.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Pilot 006 protocol commit mismatch")
    if p006.get("accepted_source_event_count") != 9:
        errors.append("Pilot 006 accepted event count mismatch")
    if p006.get("verified_screenshot_file_count") != 18:
        errors.append("Pilot 006 screenshot count mismatch")
    if p006.get("wildcard", {}).get("decision") != (
        "reject_maximal_translation_retain_pilot005_standalone_wildcards"
    ):
        errors.append("Pilot 006 wildcard decision mismatch")
    if p006.get("schedule_union", {}).get("missing_literal_count") != 5:
        errors.append("Pilot 006 missing-ID count mismatch")
    if p006.get("wildcard", {}).get("partition_missing_occurrences") != 6:
        errors.append("Pilot 006 missing-occurrence count mismatch")
    if p006_run.get("success") is not True or p006_run.get("source_attempt_count") != 12:
        errors.append("Pilot 006 run receipt mismatch")

    adapter_hash = digest(args.adapter)
    for label, plan in (("Pilot 005", p005_plan), ("Pilot 006", p006_plan)):
        if plan.get("adapter", {}).get("sha256") != adapter_hash:
            errors.append(f"{label} adapter hash mismatch")
        check_plan_script_hashes(plan, args.repository_root, errors)
    if p006_plan.get("baseline", {}).get("assessment", {}).get("sha256") != digest(
        p005_assessment_path
    ):
        errors.append("Pilot 006 baseline assessment binding mismatch")

    accepted_artifacts = []
    screenshot_count = 0
    for pilot_root, run in ((args.pilot005_root, p005_run), (args.pilot006_root, p006_run)):
        for event in run.get("events", []):
            accepted = event.get("accepted_artifact")
            if not isinstance(accepted, str):
                errors.append(f"missing accepted artifact: {event.get('event_id')}")
                continue
            path = pilot_root / accepted
            value = load(path)
            screenshots = value.get("output_metadata", {}).get("screenshots", {})
            if (
                screenshots.get("schema_version") != "ntrs-automatic-screenshots/v1"
                or screenshots.get("automatic") is not True
                or screenshots.get("same_directory_as_json") is not True
            ):
                errors.append(f"screenshot receipt mismatch: {path}")
            for key, suffix in (
                ("search_page", ".search-page.png"),
                ("results_page", ".results-page.png"),
            ):
                image = path.with_name(f"{path.stem}{suffix}")
                receipt = screenshots.get(key, {})
                if (
                    not image.is_file()
                    or receipt.get("path") != image.name
                    or receipt.get("sha256") != digest(image)
                    or not isinstance(receipt.get("width"), int)
                    or receipt["width"] <= 0
                    or not isinstance(receipt.get("height"), int)
                    or receipt["height"] <= 0
                ):
                    errors.append(f"invalid screenshot: {image}")
                screenshot_count += 1
            accepted_artifacts.append(
                {
                    "event_id": event["event_id"],
                    "path": str(path),
                    "sha256": digest(path),
                    "total": value.get("total"),
                }
            )
    if len(accepted_artifacts) != 27 or screenshot_count != 54:
        errors.append("combined accepted artifact or screenshot count mismatch")

    guideline = args.guideline.read_text(encoding="utf-8")
    for text in (
        "There is no screenshot opt-out.",
        "commit `3194156e90497186664260a8e86435e78d2e2aa1`",
        "Use no proximity operator, token distance rule, pair expansion, or local pair filter.",
        "These 26 wildcard atoms replace 88 literals.",
        "Pilot 006 tested 114 aggressive wildcard atoms that replaced 284 literals",
        "`B2` | `F*(P) AND F(M_B) AND F*(R)`",
        "Pilot 005",
        "Pilot 006",
    ):
        if text not in guideline:
            errors.append(f"guideline text missing: {text}")
    adapter = args.adapter.read_text(encoding="utf-8")
    for text in (
        ".search-page.png",
        ".results-page.png",
        "ntrs-automatic-screenshots/v1",
        "PRE_SUBMIT_RESULT_STABILITY_SECONDS",
        "RESULT_PAGE_STABILITY_SECONDS",
    ):
        if text not in adapter:
            errors.append(f"adapter contract missing: {text}")
    if "--no-screenshot" in adapter or "--skip-screenshot" in adapter:
        errors.append("adapter exposes a screenshot opt-out")
    for query in (*queries.LITERAL_SCHEDULE.values(), *queries.WILDCARD_SCHEDULE.values()):
        if "~" in query or "NEAR" in query.upper():
            errors.append("query contains proximity syntax")

    report = {
        "schema_version": "ntrs-pilot-006-validation/v1",
        "status": "passed" if not errors else "failed",
        "protocol_commit": PROTOCOL_COMMIT,
        "accepted_source_event_count": len(accepted_artifacts),
        "verified_screenshot_file_count": screenshot_count,
        "accepted_wildcard_decision": p005.get("wildcard", {}).get("decision"),
        "rejected_wildcard_decision": p006.get("wildcard", {}).get("decision"),
        "artifacts": accepted_artifacts,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "events": len(accepted_artifacts),
                "screenshots": screenshot_count,
                "errors": len(errors),
            }
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
