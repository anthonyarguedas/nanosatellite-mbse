#!/usr/bin/env python3
"""Offline integrity checks for the complete Web of Science Pilot 003 bundle."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from analyze_pilot import ANALYSIS_ROOT, PILOT_ROOT, SEARCH_ROOT, compact_event
from queries import DIAGNOSTIC_CUTOFF, MAIN_IDS, PSR_IDS, audit, event_by_name, events


EXPECTED_MAIN_TOTALS = {
    "A1": 1,
    "A2": 11,
    "A3": 2,
    "B1": 93,
    "B2": 78,
    "BG1": 3,
    "BG2": 8,
    "BC1": 17,
    "BT2": 6,
}
EXPECTED_PSR_TOTALS = {"PSR1": 22, "PSR2": 60, "PSR3": 0, "PSR4": 27}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_markdown_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        candidate = (path.parent / target).resolve()
        require(candidate.exists(), f"{path}: broken local link {target}", errors)


def check_all_json(errors: list[str]) -> int:
    paths = sorted(PILOT_ROOT.rglob("*.json"))
    for path in paths:
        try:
            load(path)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(PILOT_ROOT)}: invalid JSON ({error})")
    return len(paths)


def check_event(namespace: str, partition_id: str, expected_total: int, errors: list[str]) -> list[str] | None:
    record = compact_event(namespace, partition_id)
    require(not record["errors"], f"{namespace}/{partition_id}: {'; '.join(record['errors'])}", errors)
    require(record["source_status"] == "complete_two_pass_requested", f"{namespace}/{partition_id}: strict complete capture not evidenced", errors)
    require(record["source_total"] == expected_total, f"{namespace}/{partition_id}: source total changed", errors)
    identifiers = record["ordered_wos_ids"]
    require(isinstance(identifiers, list) and len(identifiers) == expected_total, f"{namespace}/{partition_id}: ordered ID ledger does not reconcile", errors)
    planned = event_by_name(namespace, partition_id)
    require(record["raw_query"] == planned.executed_query, f"{namespace}/{partition_id}: raw query differs from plan", errors)
    require(record["translation"] == planned.translation, f"{namespace}/{partition_id}: translation label differs from plan", errors)
    if namespace == "main":
        require(record["raw_query"].endswith("PY=(2011-2026) AND LA=(English)"), f"{partition_id}: missing exact main PY/LA controls", errors)
        require("DT=(" not in record["raw_query"], f"{partition_id}: prohibited DT union present", errors)
    else:
        require(record["raw_query"].endswith("PY=(1900-2026)"), f"{partition_id}: missing exact PSR upper-year control", errors)
        require("LA=(" not in record["raw_query"] and "DT=(" not in record["raw_query"], f"{partition_id}: PSR has a prohibited language/type control", errors)
    path = SEARCH_ROOT / namespace / f"{partition_id}.json"
    marker = path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")
    require(marker.exists(), f"{namespace}/{partition_id}: output commit marker absent", errors)
    return identifiers


def main() -> int:
    errors: list[str] = []
    json_count = check_all_json(errors)

    plan = load(SEARCH_ROOT / "query-plan.json")
    current_audit = audit()
    require(plan == current_audit, "query-plan.json differs from the deterministic query audit", errors)
    require(plan.get("membership_check", {}).get("status") == "ok", "query membership check did not pass", errors)
    require(len(plan.get("events", [])) == 13, "query plan does not contain exactly 13 scheduled events", errors)
    require(plan.get("a1_wildcard_exception", {}).get("scope") == "A1 only", "A1 wildcard exception scope changed", errors)
    require(plan.get("a1_wildcard_exception", {}).get("wildcard_count") == 10, "A1 wildcard count changed", errors)

    for partition_id, total in EXPECTED_MAIN_TOTALS.items():
        check_event("main", partition_id, total, errors)
    for partition_id, total in EXPECTED_PSR_TOTALS.items():
        check_event("psr", partition_id, total, errors)

    reconciliation = load(ANALYSIS_ROOT / "reconciliation.json")
    require(reconciliation.get("do_not_merge") is True, "reconciliation is not pilot-only", errors)
    require(reconciliation.get("diagnostic_cutoff") == DIAGNOSTIC_CUTOFF, "reconciliation cutoff changed", errors)
    main_union = reconciliation.get("main", {}).get("union", {})
    psr_union = reconciliation.get("prior_secondary_reviews", {}).get("union", {})
    require(main_union.get("source_event_total") == 219 and main_union.get("deduplicated_total") == 155, "main union no longer reconciles 219 event occurrences to 155 IDs", errors)
    require(psr_union.get("source_event_total") == 109 and psr_union.get("deduplicated_total") == 102, "PSR union no longer reconciles 109 event occurrences to 102 IDs", errors)
    semantic = reconciliation.get("main", {}).get("semantic_unions", {})
    require(semantic.get("stream_A", {}).get("deduplicated_total") == 12, "Stream A union changed", errors)
    require(semantic.get("core_stream_B", {}).get("deduplicated_total") == 144, "core Stream B union changed", errors)
    require(semantic.get("expanded_stream_B", {}).get("deduplicated_total") == 31, "expanded Stream B union changed", errors)
    for namespace_key, expected_ids in (("main", MAIN_IDS), ("prior_secondary_reviews", PSR_IDS)):
        actual_ids = tuple(reconciliation.get(namespace_key, {}).get("partition_order", []))
        require(actual_ids == expected_ids, f"{namespace_key}: partition order changed", errors)
        for entry in reconciliation.get(namespace_key, {}).get("events", []):
            require(entry.get("source_status") == "complete_two_pass_requested", f"{namespace_key}/{entry.get('partition_id')}: non-complete source status", errors)
            require(entry.get("errors") == [], f"{namespace_key}/{entry.get('partition_id')}: reconciliation errors present", errors)
            require(entry.get("editions_requested") == ["All"], f"{namespace_key}/{entry.get('partition_id')}: all-edition request absent", errors)
            editions = entry.get("editions")
            require(isinstance(editions, list) and editions, f"{namespace_key}/{entry.get('partition_id')}: all-edition readback absent", errors)
            if entry.get("source_total") == 0:
                require(entry.get("source_sort") in {None, "not_applicable_zero"}, f"{namespace_key}/{entry.get('partition_id')}: zero event has an invalid source-sort state", errors)
            else:
                require(entry.get("source_sort") == "Date: oldest first", f"{namespace_key}/{entry.get('partition_id')}: oldest-first source sort absent", errors)

    known = load(ANALYSIS_ROOT / "known-item-check.json")
    checks = known.get("checks", {})
    require(checks.get("A1_prior_pilot_known_record", {}).get("result") == "retrieved", "A1 known item was not retrieved", errors)
    require(checks.get("PSR_Buruso_2026", {}).get("result") == "retrieved_by_successful_PSR_union", "Buruso known item was not retrieved by PSR union", errors)
    require(len(checks.get("PSR_Buruso_2026", {}).get("hits", [])) == 2, "Buruso PSR discovery-event count changed", errors)

    cutoff = load(ANALYSIS_ROOT / "cutoff-screening.json")
    counts = cutoff.get("classification_counts", {})
    require(cutoff.get("retained_2026_unique_wos_ids") == 30, "2026 cutoff frame changed", errors)
    require(counts == {"native_DOP_on_or_before_2026-08-29": 29, "native_DOP_after_2026-08-29": 1}, "cutoff classification changed", errors)
    require(
        cutoff.get("scope_effects") == {
            "main_raw_union": {"raw_deduplicated_ids": 155, "DOP_after_cutoff_ids": 1, "diagnostic_cutoff_screened_ids": 154},
            "main_core_stream_B": {"raw_deduplicated_ids": 144, "DOP_after_cutoff_ids": 1, "diagnostic_cutoff_screened_ids": 143},
            "supporting_PSR_union": {"raw_deduplicated_ids": 102, "DOP_after_cutoff_ids": 0, "diagnostic_cutoff_screened_ids": 102},
        },
        "cutoff union effects changed",
        errors,
    )
    cutoff_markers = [
        ANALYSIS_ROOT / f".cutoff-on-or-before-{DIAGNOSTIC_CUTOFF}.json.ACADEMIC_SEARCH_COMMIT.json",
        ANALYSIS_ROOT / f".cutoff-after-{DIAGNOSTIC_CUTOFF}.json.ACADEMIC_SEARCH_COMMIT.json",
    ]
    for marker in cutoff_markers:
        require(marker.exists(), f"missing cutoff control marker {marker.name}", errors)

    near6 = load(ANALYSIS_ROOT / "near6-local-validation.json")
    near_counts = near6.get("overall_state_counts", {})
    require(sum(near_counts.values()) == 61, "local NEAR/6 audit row count changed", errors)
    require(near_counts.get("fallback_only_gap_six_visible", 0) == 0, "unexpected locally visible six-token-only pair", errors)

    high_volume = load(ANALYSIS_ROOT / "high-volume-investigation.json")
    refinements = high_volume.get("refinements", [])
    expected_refinement_totals = {
        "main_core_stream_B": 144,
        "main_all_nine_partitions": 155,
        "supporting_PSR_union": 102,
    }
    require({item.get("scope"): item.get("deduplicated_stable_id_total") for item in refinements} == expected_refinement_totals, "over-100 investigation scopes or totals changed", errors)
    require(all("No type, subject, access, language" in item.get("investigation", {}).get("query_refinement", "") for item in refinements), "over-100 investigation contains an unapproved narrowing", errors)

    check_markdown_links(PILOT_ROOT / "pilot.md", errors)
    check_markdown_links(PILOT_ROOT.parent.parent / "source-specific-guidelines.md", errors)
    final_search_files = sorted((PILOT_ROOT.parent.parent / "final-searches").glob("*"))
    require([path.name for path in final_search_files] == [".gitkeep"], "pilot wrote a final-search artifact", errors)
    task_diff = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "SLR/SLR1/TASKS.md"], check=False)
    require(task_diff.returncode == 0, "TASKS.md completion state changed", errors)

    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "json_files": json_count,
                "main_events": len(MAIN_IDS),
                "psr_events": len(PSR_IDS),
                "main_union": 155,
                "psr_union": 102,
                "high_volume_refinements": len(refinements),
                "cutoff_screened_2026_records": 30,
                "near6_rows": 61,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
