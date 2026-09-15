#!/usr/bin/env python3
"""Validate AIAA ARC Pilot 009 plans, artifacts, assessment, and prose."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_assessment import PARTITIONS, build

EXPECTED_PARTITION_COUNTS = {
    "A1": 18,
    "A2": 40,
    "A3": 12,
    "B1": 37,
    "B2": 23,
    "BG1": 44,
    "BG2": 2,
    "BC1": 36,
    "BT2": 11,
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate(args: argparse.Namespace) -> dict[str, Any]:
    observed = load(args.assessment)
    rebuilt = build(args.pilot_root, args.pilot007_root)
    require(observed == rebuilt, "Assessment does not rebuild exactly")
    require(observed["status"] == "complete", "Pilot status is incomplete")
    execution = observed["execution"]
    require(execution["pair_count"] == 94, "Pair count mismatch")
    require(execution["source_event_count"] == 188, "Source event count mismatch")
    require(execution["all_94_source_totals_equal"] is True, "Paired source totals differ")
    require(execution["all_94_raw_source_id_sets_equal"] is True, "Paired raw stable-ID sets differ")
    require(execution["all_94_canonical_doi_sets_equal"] is True, "Paired canonical DOI sets differ")
    require(execution["largest_source_total"] == 45, "Largest source total mismatch")

    for partition in PARTITIONS:
        entry = observed["partition_unions"][partition]
        expected = EXPECTED_PARTITION_COUNTS[partition]
        require(entry["literal_canonical_doi_count"] == expected, f"{partition}: literal count mismatch")
        require(entry["wildcard_canonical_doi_count"] == expected, f"{partition}: wildcard count mismatch")
        require(entry["sets_equal"] is True, f"{partition}: union sets differ")
    overall = observed["overall_comparison"]
    require(overall["literal_canonical_doi_count"] == 119, "Literal schedule count mismatch")
    require(overall["wildcard_canonical_doi_count"] == 119, "Wildcard schedule count mismatch")
    require(overall["sets_equal"] is True, "Schedule unions differ")
    require(overall["fresh_literal_reproduces_pilot007_union"] is True, "Fresh literal union differs from Pilot 007")
    require(overall["wildcard_only_canonical_dois"] == [], "Wildcard added records")
    require(overall["literal_only_canonical_dois"] == [], "Wildcard lost records")

    acceptance = observed["acceptance"]
    require(acceptance["status"] == "accepted", "Wildcard was not accepted")
    require(acceptance["accepted_wildcard"] == "nanosatellit*", "Accepted wildcard mismatch")
    require(acceptance["general_wildcard_permission"] is False, "Acceptance scope is too broad")
    require(observed["known_item_recall"]["all_literal_and_wildcard_memberships_pass"] is True, "Known-item gate failed")
    require(len(observed["visible_nanosatellite_controls"]) == 2, "Visible nanosatellite control count mismatch")
    require(all(entry["pair_memberships_equal"] for entry in observed["visible_nanosatellite_controls"]), "Visible control memberships differ")

    screenshots = observed["screenshots"]
    require(screenshots["successful_json_count"] == 188, "Successful JSON count mismatch")
    require(screenshots["required_screenshot_count"] == 376, "Required screenshot count mismatch")
    require(screenshots["verified_success_screenshot_count"] == 376, "Verified screenshot count mismatch")
    require(sum(entry["event_count"] for entry in observed["adapter_provenance"]) == 188, "Adapter provenance count mismatch")
    failures = observed["retained_failures"]
    require(failures["count"] == 4, "Failure count mismatch")
    require(failures["all_recovered_by_exact_retry"] is True, "A transient failure remains unresolved")
    require(failures["converted_to_zero"] is False, "A failure was converted to zero")

    primary_receipts = [
        load(args.pilot_root / "searches" / f"run-receipt-{partition}.json")
        for partition in PARTITIONS
    ]
    primary_errors = [
        error
        for receipt in primary_receipts
        for event in receipt["events"]
        for error in event["errors"]
    ]
    require(len(primary_errors) == 4, "Primary run failure count mismatch")
    require(all("Could not create an adapter-owned Chrome page" in error for error in primary_errors), "Unexpected primary failure reason")
    for partition in ("B2", "BG2", "BT2"):
        retry = load(args.pilot_root / "searches" / f"run-receipt-{partition}-retry1.json")
        require(retry["failed_or_incomplete"] == 0, f"{partition}: retry receipt is incomplete")

    pilot_text = args.pilot_document.read_text()
    guideline_text = args.guideline.read_text()
    for text, name in ((pilot_text, "pilot"), (guideline_text, "guideline")):
        require("nanosatellit*" in text, f"{name} omits accepted wildcard")
        require("94" in text and "119" in text, f"{name} omits paired equality evidence")
        require("Pilot 009" in text, f"{name} omits Pilot 009")
    require("Accept this exact wildcard substitution" in guideline_text, "Guideline omits narrow acceptance")
    require("No other wildcard" in guideline_text, "Guideline omits wildcard boundary")
    require("376 mandatory screenshots" in pilot_text, "Pilot prose omits screenshot count")

    return {
        "schema_version": "aiaa-arc-pilot009-validation/v1",
        "source": observed["source"],
        "pilot": "009",
        "status": "pass",
        "assessment": {
            "path": str(args.assessment),
            "sha256": sha256(args.assessment),
            "rebuild_equal": True,
        },
        "checks": {
            "paired_cells": 94,
            "successful_source_events": 188,
            "equal_source_total_pairs": 94,
            "equal_raw_stable_id_pairs": 94,
            "equal_canonical_doi_pairs": 94,
            "literal_schedule_dois": 119,
            "wildcard_schedule_dois": 119,
            "wildcard_only_dois": 0,
            "literal_only_dois": 0,
            "verified_screenshots": 376,
            "known_item_gate_passed": True,
            "wildcard_accepted_with_narrow_scope": True,
            "all_failures_recovered": True,
            "pilot_and_guideline_updated": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot007-root", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--pilot-document", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = validate(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
