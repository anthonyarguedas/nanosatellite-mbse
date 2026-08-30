#!/usr/bin/env python3
"""Offline integrity checks for Wiley Online Library Pilot 003."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "source-specific/wiley-online-library/pilots/003"
SEARCH_DIR = PILOT_DIR / "searches"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_artifacts import (  # noqa: E402
    CELL_PARENTS,
    DIRECT_LEDGER,
    SCHEDULE_IDS,
    _ordered_union_from_entries,
    sequence_sha256,
    validate_query_plan,
)


EXPECTED_HIGH_SETS = {
    "A2": 129,
    "BT2": 209,
    "BT2-cell-0001": 102,
    "BT2-cell-0004": 122,
    "BT2-cell-0007": 106,
    "BT2-cell-0009": 126,
    "Stream_A": 151,
    "expanded_Stream_B_successful_subset": 256,
    "all_successful_partitions": 316,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_json(errors: list[str]) -> int:
    paths = sorted(SEARCH_DIR.glob("*.json"))
    for path in paths:
        try:
            load(path)
        except Exception as error:  # noqa: BLE001
            errors.append(f"invalid JSON {path.name}: {error}")
    return len(paths)


def check_docs(errors: list[str]) -> None:
    for path in (PILOT_DIR / "pilot.md", PILOT_DIR.parent.parent / "source-specific-guidelines.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            require((path.parent / target).resolve().exists(), f"broken link {path.name}: {target}", errors)
    guideline = (PILOT_DIR.parent.parent / "source-specific-guidelines.md").read_text(encoding="utf-8")
    for line in (
        "Final searches saved in commit: NA",
        "Source excluded from review due to search failure in commit: NA",
    ):
        require(line in guideline, f"overall completion state changed: missing {line}", errors)


def check_query_and_receipts(errors: list[str]) -> tuple[dict, dict]:
    plan = load(SEARCH_DIR / "query-plan.json")
    try:
        audit = validate_query_plan(plan)
    except Exception as error:  # noqa: BLE001
        errors.append(f"query membership/cell plan: {error}")
        audit = {}
    receipt = load(SEARCH_DIR / "source-id-unions.json")
    entries = receipt.get("entries", {})
    require(tuple(entries) == SCHEDULE_IDS, "union receipt schedule order changed", errors)
    for partition_id in SCHEDULE_IDS:
        entry = entries.get(partition_id, {})
        if partition_id in {"B2", "BG1"}:
            require(entry.get("status") == "source_failure", f"{partition_id}: source failure not retained", errors)
            require(entry.get("source_total") is None, f"{partition_id}: failure total is not null", errors)
            continue
        require(str(entry.get("status", "")).startswith("success_"), f"{partition_id}: missing successful receipt", errors)
        events = entry.get("source_events", [])
        source_cells = entry.get("source_cells", [])
        require(len(events) == entry.get("source_cell_event_total"), f"{partition_id}: event total mismatch", errors)
        require(len(entry.get("ordered_source_ids", [])) == entry.get("unique_source_id_count"), f"{partition_id}: union cardinality mismatch", errors)
        require(
            entry.get("ordered_source_ids_sha256") == sequence_sha256(entry.get("ordered_source_ids", [])),
            f"{partition_id}: union order digest mismatch",
            errors,
        )
        require(
            entry.get("duplicate_source_event_count") == len(entry.get("duplicate_source_events", [])),
            f"{partition_id}: duplicate event ledger mismatch",
            errors,
        )
        require(
            len(events) - len(entry.get("ordered_source_ids", [])) == entry.get("duplicate_source_event_count"),
            f"{partition_id}: duplicate arithmetic mismatch",
            errors,
        )
        require(all(isinstance(event.get("source_id"), str) and event.get("source_id") for event in events), f"{partition_id}: missing source ID", errors)
        if partition_id in CELL_PARENTS:
            require(entry.get("source_total") is None, f"{partition_id}: overlapping cell total should be null", errors)
            require(len(source_cells) == len(plan["source_cell_unions"][partition_id]["cell_ids"]), f"{partition_id}: incomplete cells", errors)
            if partition_id in {"A2", "BC1"}:
                parent = load(SEARCH_DIR / f"{partition_id}.source-id-ledger.json")
                require(parent.get("status") == "error" and parent.get("source_total") is None, f"{partition_id}: full-query failure must retain null", errors)
        else:
            require(entry.get("source_total") == len(events), f"{partition_id}: source total mismatch", errors)
            ledger = load(SEARCH_DIR / DIRECT_LEDGER[partition_id])
            require(ledger.get("status") == "success", f"{partition_id}: direct ledger not successful", errors)
            require(ledger.get("source_total") == len(events), f"{partition_id}: direct ledger total mismatch", errors)
    for name in ("A1.json", "A2.json"):
        standard = load(SEARCH_DIR / name)
        require(standard.get("total") is None, f"{name}: native capture failure total must be null", errors)
        require(standard.get("do_not_merge") is True, f"{name}: failure must be non-mergeable", errors)
    return plan, receipt


def check_metadata(receipt: dict, errors: list[str]) -> None:
    audit = load(SEARCH_DIR / "metadata-audit.json")
    records = audit.get("records", [])
    entries = receipt["entries"]
    expected_ids = _ordered_union_from_entries(entries, SCHEDULE_IDS)
    actual_ids = [record.get("source_id") for record in records]
    require(actual_ids == expected_ids, "metadata audit source-ID order differs from successful union", errors)
    require(all(record.get("not_excluded") is True for record in records), "metadata audit excluded a source ID", errors)
    high = audit.get("investigated_deduplicated_sets_over_100", {})
    require(set(high) == set(EXPECTED_HIGH_SETS), "high-volume investigation set changed", errors)
    for name, count in EXPECTED_HIGH_SETS.items():
        item = high.get(name, {})
        require(item.get("deduplicated_records") == count, f"{name}: wrong dedup count", errors)
        require(item.get("metadata_rows_covered") == count, f"{name}: incomplete metadata investigation", errors)
    pairs = audit.get("pair_partition_summary", {})
    require(pairs.get("BG1", {}).get("status") == "source_failure_no_pair_audit", "BG1 pair failure was turned into zero", errors)
    for partition_id in ("BG2", "BC1", "BT2"):
        item = pairs.get(partition_id, {})
        require(item.get("deduplicated_records") == entries[partition_id].get("unique_source_id_count"), f"{partition_id}: pair audit denominator mismatch", errors)
        require("No DOI lacking" in item.get("recall_protection", ""), f"{partition_id}: pair audit lacks recall protection", errors)


def check_assessment(receipt: dict, errors: list[str]) -> None:
    assessment = load(SEARCH_DIR / "schedule-assessment.json")
    entries = assessment.get("entries", {})
    require(tuple(entries) == SCHEDULE_IDS, "assessment schedule order changed", errors)
    require(entries.get("B2", {}).get("source_total") is None, "assessment B2 total is not null", errors)
    require(entries.get("BG1", {}).get("source_total") is None, "assessment BG1 total is not null", errors)
    unions = assessment.get("unions", {})
    require(unions.get("Stream_A", {}).get("unique_source_id_count") == 151, "Stream A union mismatch", errors)
    require(unions.get("core_Stream_B", {}).get("status") == "incomplete_due_to_B2_source_failure", "core Stream B failure lost", errors)
    require(unions.get("expanded_Stream_B", {}).get("status") == "incomplete_due_to_BG1_source_failure", "expanded Stream B failure lost", errors)
    require(unions.get("all_nine_partitions", {}).get("status") == "incomplete_due_to_B2_and_BG1_source_failures", "all-nine failure lost", errors)
    require(receipt.get("do_not_merge") is True and assessment.get("do_not_merge") is True, "pilot artifacts mergeable", errors)


def main() -> int:
    errors: list[str] = []
    json_files = check_json(errors)
    check_docs(errors)
    _plan, receipt = check_query_and_receipts(errors)
    check_metadata(receipt, errors)
    check_assessment(receipt, errors)
    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "json_files": json_files,
                "schedule_entries": len(SCHEDULE_IDS),
                "cell_union_parents": list(CELL_PARENTS),
                "high_volume_investigations": EXPECTED_HIGH_SETS,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
