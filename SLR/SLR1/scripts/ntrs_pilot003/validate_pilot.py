#!/usr/bin/env python3
"""Offline integrity checks for NASA NTRS Pilot 003 artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from build_artifacts import (  # noqa: E402
    DATE_END,
    DATE_START,
    PILOT_DIR,
    SEARCH_DIR,
    SCHEDULE_IDS,
    build_entries,
    build_pair_checks,
    failure_summary,
    ids,
    load_json,
    sha256_bytes,
)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def marker_path(artifact: str) -> Path:
    return SEARCH_DIR / f".{artifact}.NTRS_COMMIT.json"


def validate_marker(artifact: str, digest: str, errors: list[str]) -> None:
    path = marker_path(artifact)
    require(path.exists(), f"{artifact}: missing NTRS output commit marker", errors)
    if not path.exists():
        return
    try:
        marker = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001
        errors.append(f"{path.name}: invalid JSON: {error}")
        return
    require(marker.get("schema") == "ntrs_output_commit_marker_v1", f"{path.name}: wrong marker schema", errors)
    normalized = marker.get("normalized_json", {})
    require(normalized.get("sha256") == digest, f"{path.name}: digest does not bind terminal artifact", errors)
    try:
        size = (SEARCH_DIR / artifact).stat().st_size
    except OSError as error:
        errors.append(f"{artifact}: cannot stat terminal artifact: {error}")
    else:
        require(normalized.get("bytes") == size, f"{path.name}: byte count does not bind terminal artifact", errors)


def validate_json_files(errors: list[str]) -> None:
    for path in sorted(SEARCH_DIR.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:  # noqa: BLE001
            errors.append(f"{path.name}: invalid JSON: {error}")


def validate_plan(errors: list[str]) -> None:
    try:
        plan = json.loads((SEARCH_DIR / "plan.json").read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001
        errors.append(f"plan.json: unreadable: {error}")
        return
    events = plan.get("events")
    require(isinstance(events, list) and len(events) == len(SCHEDULE_IDS), "plan.json: missing complete nine-entry schedule", errors)
    if not isinstance(events, list):
        return
    observed = []
    for event in events:
        if not isinstance(event, dict):
            errors.append("plan.json: malformed event")
            continue
        partition = event.get("partition_id")
        observed.append(partition)
        require(event.get("source") == "nasa_ntrs", f"plan.json {partition}: wrong source", errors)
        require(event.get("query_cells") is None, f"plan.json {partition}: unexpected prospective split", errors)
        try:
            from queries import partition_query  # imported after build_artifacts path setup
            expected = partition_query("nasa_ntrs", partition)
        except Exception as error:  # noqa: BLE001
            errors.append(f"plan.json {partition}: cannot render expected query: {error}")
            continue
        require(event.get("query") == expected, f"plan.json {partition}: query differs from pilot_schedule literal translation", errors)
        require("*" not in expected and "?" not in expected, f"plan.json {partition}: unaccepted wildcard present", errors)
    require(tuple(observed) == SCHEDULE_IDS, "plan.json: schedule order or membership differs", errors)
    adapter_args = [item for event in events if isinstance(event, dict) for item in event.get("adapter_args", [])]
    require("--date-start=2011-01-01" in adapter_args and "--date-end=2026-08-29" in adapter_args, "plan.json: exact diagnostic dates missing", errors)
    require(not any("type" in str(item).casefold() or "language" in str(item).casefold() for item in adapter_args), "plan.json: unexpected language/type control", errors)


def validate_entries(errors: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    assessment, _ = load_json("schedule-assessment.json")
    expected_entries = build_entries()
    observed_entries = assessment.get("entries")
    require(list(observed_entries or {}) == list(SCHEDULE_IDS), "schedule assessment: schedule order/membership differs", errors)
    require(observed_entries == expected_entries, "schedule assessment: entries do not reproduce terminal artifact reconciliation", errors)
    require(assessment.get("mode") == "diagnostic_only_not_a_final_search", "schedule assessment: pilot incorrectly marked final", errors)
    dates = assessment.get("date_window", {})
    require(dates.get("publication_start") == DATE_START and dates.get("publication_end") == DATE_END, "schedule assessment: exact diagnostic dates differ", errors)
    translation = assessment.get("translation", {})
    require(translation.get("wildcards_present") is False, "schedule assessment: wildcard use recorded", errors)

    terminal_names = set()
    raw_ids: list[str] = []
    if isinstance(observed_entries, dict):
        for partition, entry in observed_entries.items():
            if not isinstance(entry, dict):
                errors.append(f"{partition}: malformed entry")
                continue
            cells = entry.get("terminal_cells", [])
            cell_ids = []
            for cell in cells:
                if not isinstance(cell, dict):
                    errors.append(f"{partition}: malformed terminal cell")
                    continue
                artifact = cell.get("artifact")
                cell_ids.append(cell.get("cell_id"))
                terminal_names.add(artifact)
                try:
                    data, digest = load_json(artifact)
                except Exception as error:  # noqa: BLE001
                    errors.append(f"{partition} {artifact}: unreadable: {error}")
                    continue
                metadata = data.get("output_metadata", {})
                run = metadata.get("prisma_search_run", {})
                require(cell.get("artifact_sha256") == digest, f"{partition} {artifact}: stale assessment digest", errors)
                require(data.get("total") == cell.get("source_total") == len(ids(data)), f"{partition} {artifact}: total/ID reconciliation differs", errors)
                require(len(ids(data)) == len(set(ids(data))), f"{partition} {artifact}: duplicate canonical ID within cell", errors)
                require(metadata.get("retrieval_complete") is True and metadata.get("status") == "success", f"{partition} {artifact}: not complete", errors)
                require(run.get("completion_status") == "complete", f"{partition} {artifact}: PRISMA receipt not complete", errors)
                require("pilot" in str(run.get("run_id", "")).casefold(), f"{partition} {artifact}: not a pilot run ID", errors)
                for row in data.get("results", []):
                    paper_id = row.get("paperId") if isinstance(row, dict) else None
                    require(row.get("url") == f"https://ntrs.nasa.gov/citations/{paper_id}", f"{partition} {artifact}: noncanonical citation URL", errors)
                validate_marker(artifact, digest, errors)
                raw_ids.extend(ids(data))
            reported_union = entry.get("union", {})
            deduplicated = list(dict.fromkeys(
                item for cell in cells if isinstance(cell, dict) for item in cell.get("canonical_citation_ids", [])
            ))
            require(reported_union.get("canonical_citation_id_union") == deduplicated, f"{partition}: union IDs differ from terminal cells", errors)
            require(reported_union.get("deduplicated_union_count") == len(deduplicated), f"{partition}: union count differs", errors)
            require(reported_union.get("investigation_threshold_exceeded") is False, f"{partition}: unsupported >100 threshold state", errors)
            if partition == "BT2":
                ranges = [cell.get("t2_pair_index_range_1_based") for cell in cells if isinstance(cell, dict)]
                expanded = [index for pair in ranges if isinstance(pair, list) and len(pair) == 2 for index in range(pair[0], pair[1] + 1)]
                require(expanded == list(range(1, 225)), "BT2: terminal cells do not cover pair indexes 1–224 exactly once", errors)
            if partition == "BC1":
                require(len(cell_ids) == 4, "BC1: expected four terminal literal cells", errors)

    current_markers = {path.name[len(".") : -len(".NTRS_COMMIT.json")] for path in SEARCH_DIR.glob(".*.NTRS_COMMIT.json")}
    require(current_markers == terminal_names, "NTRS markers do not exactly match terminal pilot artifacts", errors)
    overall = assessment.get("overall_schedule_union", {})
    overall_ids = list(dict.fromkeys(raw_ids))
    require(overall.get("canonical_citation_id_union") == overall_ids, "overall union IDs differ from terminal artifacts", errors)
    require(overall.get("deduplicated_union_count") == len(overall_ids) == 15, "overall union count is not 15", errors)
    require(overall.get("source_event_total") == len(raw_ids) == 19, "overall raw source-event total is not 19", errors)
    return assessment, expected_entries


def validate_failures(assessment: dict[str, Any], errors: list[str]) -> None:
    expected = []
    for path in sorted(SEARCH_DIR.glob("*.json")):
        if path.name in {"plan.json", "schedule-assessment.json", "pair-checks.json"}:
            continue
        data, _ = load_json(path.name)
        if data.get("output_metadata", {}).get("status") == "error":
            expected.append(failure_summary(path.name))
    require(assessment.get("failures") == expected, "failure register does not match all saved error artifacts", errors)
    for failure in expected:
        require(failure.get("source_total") is None, f"{failure.get('artifact')}: failure total is not null", errors)
        require(failure.get("canonical_citation_ids") == [], f"{failure.get('artifact')}: failure retains IDs", errors)


def validate_pair_checks(entries: dict[str, Any], errors: list[str]) -> None:
    observed, _ = load_json("pair-checks.json")
    expected = build_pair_checks(entries)
    require(observed == expected, "pair checks do not reproduce exact retained-field inspection", errors)
    uncertainty = observed.get("full_text_uncertainty", {})
    require(uncertainty.get("status") == "unresolved", "pair checks do not preserve full-text uncertainty", errors)
    bg2 = observed.get("checks", {}).get("BG2", {})
    require(bg2.get("record_count") == 4, "BG2 pair check does not cover all retained candidates", errors)
    require(bg2.get("observed_pair_hit_count") == 4, "BG2 pair check hit count changed", errors)


def validate_markdown_links(errors: list[str]) -> None:
    pilot = PILOT_DIR / "pilot.md"
    require(pilot.exists(), "pilot.md is missing", errors)
    if not pilot.exists():
        return
    text = pilot.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        require((pilot.parent / target).resolve().exists(), f"pilot.md: broken local link {target}", errors)


def main() -> int:
    errors: list[str] = []
    validate_json_files(errors)
    validate_plan(errors)
    assessment, entries = validate_entries(errors)
    validate_failures(assessment, errors)
    validate_pair_checks(entries, errors)
    validate_markdown_links(errors)
    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(json.dumps({
        "status": "ok",
        "schedule_entries": len(SCHEDULE_IDS),
        "terminal_artifacts": sum(len(entry["terminal_cells"]) for entry in entries.values()),
        "failure_artifacts": len(assessment["failures"]),
        "partition_unions": {
            key: value["union"]["deduplicated_union_count"] for key, value in entries.items()
        },
        "overall_union": assessment["overall_schedule_union"]["deduplicated_union_count"],
        "dates": [DATE_START, DATE_END],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
