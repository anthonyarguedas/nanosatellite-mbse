#!/usr/bin/env python3
"""Validate IEEE Pilot 004 artifacts without touching the fixed integration."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "source-specific/ieee-xplore/pilots/004"
SEARCHES = PILOT / "searches"
GUIDELINE = ROOT / "source-specific/ieee-xplore/source-specific-guidelines.md"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import build_receipts  # noqa: E402
import build_schedule  # noqa: E402


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_marker(marker: Path, failures: list[str]) -> None:
    payload = load(marker)
    if payload.get("schema") != "ieee_xplore_output_commit_marker_v1":
        failures.append(f"{marker}: unexpected marker schema")
        return
    name = marker.name
    prefix, suffix = ".", ".IEEE_COMMIT.json"
    if not name.startswith(prefix) or not name.endswith(suffix):
        failures.append(f"{marker}: unexpected marker name")
        return
    output = marker.with_name(name[len(prefix):-len(suffix)])
    if not output.is_file():
        failures.append(f"{marker}: missing output {output.name}")
        return
    expected = payload.get("normalized_json", {}).get("sha256")
    actual = hashlib.sha256(output.read_bytes()).hexdigest()
    if expected != actual:
        failures.append(f"{marker}: JSON SHA-256 mismatch")


def main() -> int:
    failures: list[str] = []
    schedule = load(SEARCHES / "schedule.json")
    failures.extend(build_schedule.validate_schedule(schedule))
    expected = build_receipts.expected_cells(schedule)

    source_events: dict[str, int] = {query: 0 for query in expected}
    for path in sorted(SEARCHES.rglob("*.json")):
        if path.name.startswith("."):
            continue
        try:
            payload = load(path)
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"{path}: invalid JSON ({type(error).__name__})")
            continue
        if payload.get("source") != "IEEE Xplore" or payload.get("schema_version") != "academic-search-result/v1":
            continue
        query = payload.get("executed_query")
        # The boundary event is intentionally not one of the nine partitions.
        if path.name == "year-boundary-2022-2023.json":
            continue
        if query not in expected:
            failures.append(f"{path}: source query is not an exact scheduled cell")
            continue
        source_events[query] += 1
        metadata = payload.get("output_metadata", {})
        if metadata.get("status") == "error":
            if payload.get("total") is not None:
                failures.append(f"{path}: failure did not preserve total:null")
            if payload.get("do_not_merge") is not True:
                failures.append(f"{path}: failure is not marked non-mergeable")
        if isinstance(query, str) and ("*" in query or "?" in query):
            failures.append(f"{path}: wildcard reached a literal pilot event")
        if payload.get("total") is not None:
            records = payload.get("results")
            if isinstance(records, list) and records:
                ids = [record.get("paperId") for record in records if isinstance(record, dict)]
                if any(not isinstance(value, str) or not value.isdigit() for value in ids):
                    failures.append(f"{path}: non-numeric Article Number in retained records")

    for query, count in source_events.items():
        if not count:
            part, cell = expected[query]
            failures.append(f"{part}/{cell}: no source event artifact")

    for marker in SEARCHES.rglob(".*.IEEE_COMMIT.json"):
        check_marker(marker, failures)

    union = load(SEARCHES / "union-receipt.json")
    if union.get("schema_version") != "slr1-ieee-xplore-pilot004-union-receipt/v1":
        failures.append("union receipt schema mismatch")
    partition_ids = [item.get("partition_id") for item in union.get("partitions", [])]
    if partition_ids != [item["partition_id"] for item in schedule["partitions"]]:
        failures.append("union receipt partition order/membership differs from schedule")
    for partition in union.get("partitions", []):
        complete = partition.get("union_status") == "complete"
        union_ids = partition.get("deduplicated_article_number_union")
        if complete and (not isinstance(union_ids, list) or len(union_ids) != len(set(union_ids))):
            failures.append(f"{partition.get('partition_id')}: invalid complete union")
        if not complete and union_ids is not None:
            failures.append(f"{partition.get('partition_id')}: incomplete union is not null")

    boundary = load(SEARCHES / "year-boundary-receipt.json")
    assertions = boundary.get("assertions", {})
    for key in (
        "lower_endpoint_retained",
        "upper_endpoint_retained",
        "known_2021_record_excluded",
        "native_readback",
        "complete_source_run",
    ):
        if assertions.get(key) is not True:
            failures.append(f"boundary receipt assertion failed: {key}")
    if boundary.get("literal_bracket_form") != "not_reproduced; fixture-only if cited elsewhere":
        failures.append("boundary receipt overclaims literal bracket reproduction")

    over_100 = load(SEARCHES / "over-100-investigation.json")
    if over_100.get("partition_id") != "B2" or over_100.get("threshold") != 100:
        failures.append("over-100 receipt does not identify B2/100")
    if over_100.get("deduplicated_stable_article_number_union") is not None:
        failures.append("over-100 receipt promoted an incomplete B2 union")
    if not any(event.get("total") == 131 for event in over_100.get("source_count_observations", [])):
        failures.append("over-100 receipt lacks the native B2 count of 131")

    pilot_doc = (PILOT / "pilot.md").read_text(encoding="utf-8")
    guideline = GUIDELINE.read_text(encoding="utf-8")
    for text, label in (
        ("year-boundary-receipt.json", "pilot boundary link"),
        ("union-receipt.json", "pilot union link"),
        ("over-100-investigation.json", "pilot >100 link"),
    ):
        if text not in pilot_doc:
            failures.append(f"missing {label}")
    if "Pilot 004" not in guideline or "does not change the source completion state" not in guideline:
        failures.append("guideline does not retain Pilot 004/open completion boundary")
    for text in (
        "Last pilot saved in commit: NA",
        "Final searches saved in commit: NA",
        "Source excluded from review due to search failure in commit: NA",
    ):
        if text not in guideline:
            failures.append("guideline source completion state was changed")

    report = {
        "schema_version": "slr1-ieee-xplore-pilot004-validation/v1",
        "valid": not failures,
        "checks": {
            "json_and_markers": True,
            "schedule_membership": True,
            "literal_no_wildcard": True,
            "failure_nulls": True,
            "boundary": True,
            "unions": True,
            "guideline_completion_state": True,
        },
        "failure_count": len(failures),
        "failures": failures,
    }
    (SEARCHES / "pilot-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if failures:
        print("Pilot validation failed:", *failures, sep="\n- ")
        return 1
    print("Pilot validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
