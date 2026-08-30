#!/usr/bin/env python3
"""Offline integrity checks for Pilot 003 cells and documentation links."""

from __future__ import annotations

import json
import re
from pathlib import Path

from queries import (
    BLOCKS,
    C1_ANCHORS,
    C1_PAIR_LEFTS,
    GMODEL_PAIR_LEFTS,
    GSTRUCTURE_PRODUCT_LEFTS,
    GSTRUCTURE_VARIATION_LEFTS,
    METADATA_FIELDS,
    MODEL_ARCHITECTURE_ANCHORS,
    SCHEDULE,
    SCHEDULE_IDS,
    T2_PAIRS,
    T2_SUBBLOCKS,
    first_stage_rows,
    refinement_rows,
)
from run_refinements import TARGET_SLUG

ROOT = Path(__file__).resolve().parents[2] / "source-specific/aiaa-arc/pilots/003"
SEARCH_DIR = ROOT / "searches"


def load(path: Path):
    return json.loads(path.read_text())


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def expected_success(path: Path) -> Path | None:
    if path.exists():
        return path
    for attempt in range(1, 4):
        candidate = path.with_name(f"{path.stem}-retry{attempt}{path.suffix}")
        if candidate.exists():
            return candidate
    return None


def check_count_artifact(path: Path, rows, errors: list[str]) -> None:
    data = load(path)
    metadata = data.get("output_metadata", {})
    expected = []
    # Native fields are stable values; all generated rows are already native-compatible.
    labels = {"Title": "Title", "Keyword": "Keywords", "Abstract": "Abstract", "Anywhere": "Anywhere"}
    fields = {"Title": "Title", "Keyword": "Keyword", "Abstract": "Abstract", "Anywhere": "AllField"}
    for field, text in rows:
        expected.append({"field": fields[field], "label": labels[field], "text": text})
    require(data.get("total") is not None and isinstance(data.get("total"), int), f"{path.name}: missing exact total", errors)
    require(metadata.get("field_rows") == expected, f"{path.name}: field rows differ from generated exact cell", errors)
    require(metadata.get("observed_exact_query_echo") is True, f"{path.name}: query echo not proven", errors)
    require(metadata.get("exact_date_controls_proven") is True, f"{path.name}: date controls not proven", errors)
    require(metadata.get("language_filter") is None, f"{path.name}: unexpected language filter", errors)
    require(metadata.get("publication_type_filter") is None, f"{path.name}: unexpected type filter", errors)
    require("*" not in " ".join(text for _, text in rows) and "?" not in " ".join(text for _, text in rows), f"{path.name}: wildcard unexpectedly present", errors)


def main() -> int:
    errors: list[str] = []
    json_paths = sorted(SEARCH_DIR.glob("*.json"))
    for path in json_paths:
        try:
            load(path)
        except Exception as error:  # noqa: BLE001
            errors.append(f"{path.name}: invalid JSON: {error}")

    # Exact literal/pair construction checks.
    require(BLOCKS["G_model"].count(" OR ") + 1 == 30, "G_model alternative count is not 14+16", errors)
    require(BLOCKS["G_structure"].count(" OR ") + 1 == 24, "G_structure alternative count is not 8+16", errors)
    require(BLOCKS["C1"].count(" OR ") + 1 == 62, "C1 alternative count is not 26+36", errors)
    require(BLOCKS["T2"].count(" OR ") + 1 == 224, "T2 alternative count is not 224", errors)
    require(len(T2_SUBBLOCKS) == 4 and all(block.count(" OR ") + 1 == 56 for block in T2_SUBBLOCKS), "T2 does not split into four 56-pair OR cells", errors)
    split_pairs = {
        pair
        for start in range(0, len(T2_PAIRS), 56)
        for pair in T2_PAIRS[start : start + 56]
    }
    require(set(T2_PAIRS) == split_pairs, "T2 pair union changed", errors)
    for left in GMODEL_PAIR_LEFTS:
        for right in MODEL_ARCHITECTURE_ANCHORS:
            require(f'("{left}" "{right}")' in BLOCKS["G_model"], f"missing G_model pair {left}/{right}", errors)
    for left in GSTRUCTURE_PRODUCT_LEFTS:
        for right in ("model", "models"):
            require(f'("{left}" "{right}")' in BLOCKS["G_structure"], f"missing G_structure pair {left}/{right}", errors)
    for left in GSTRUCTURE_VARIATION_LEFTS:
        for right in MODEL_ARCHITECTURE_ANCHORS:
            require(f'("{left}" "{right}")' in BLOCKS["G_structure"], f"missing G_structure pair {left}/{right}", errors)
    for left in C1_PAIR_LEFTS:
        for right in C1_ANCHORS:
            require(f'("{left}" "{right}")' in BLOCKS["C1"], f"missing C1 pair {left}/{right}", errors)

    # Every normal primary cell and its exact rows.
    for schedule_id in SCHEDULE_IDS:
        if schedule_id == "BT2":
            continue
        for field in METADATA_FIELDS:
            path = SEARCH_DIR / f"{schedule_id}-P-{field.lower()}.json"
            require(path.exists(), f"missing primary cell {path.name}", errors)
            if path.exists():
                check_count_artifact(path, first_stage_rows(schedule_id, field), errors)

    # BT2's three failed whole cells and all lossless T2 replacement cells.
    for field in METADATA_FIELDS:
        parent_failure = SEARCH_DIR / f"BT2-P-{field.lower()}.NON_MERGEABLE_FAILURE.json"
        require(parent_failure.exists(), f"missing preserved BT2 whole-row failure {parent_failure.name}", errors)
        for index, subblock in enumerate(T2_SUBBLOCKS):
            path = SEARCH_DIR / f"BT2-P-{field.lower()}-T2-{index + 1:02d}-of-04.json"
            require(path.exists(), f"missing BT2 primary subcell {path.name}", errors)
            if path.exists():
                check_count_artifact(path, ((field, BLOCKS["P"]), ("Anywhere", f'{BLOCKS["M_B"]} AND {subblock}')), errors)

    # Every required high-volume refinement cell, allowing recovered retry names.
    for schedule_id in ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2"):
        slug = TARGET_SLUG[SCHEDULE[schedule_id]["defining_name"]]
        for population in METADATA_FIELDS:
            for defining in METADATA_FIELDS:
                base = SEARCH_DIR / f"{schedule_id}-P-{population.lower()}-{slug}-{defining.lower()}.json"
                path = expected_success(base)
                require(path is not None, f"missing refinement cell {base.name}", errors)
                if path is not None:
                    check_count_artifact(path, refinement_rows(schedule_id, population, defining), errors)
    for population in METADATA_FIELDS:
        for defining in METADATA_FIELDS:
            for index, subblock in enumerate(T2_SUBBLOCKS):
                base = SEARCH_DIR / f"BT2-P-{population.lower()}-MB-{defining.lower()}-T2-{index + 1:02d}-of-04.json"
                path = expected_success(base)
                require(path is not None, f"missing BT2 refinement cell {base.name}", errors)
                if path is not None:
                    check_count_artifact(path, ((population, BLOCKS["P"]), (defining, BLOCKS["M_B"]), ("Anywhere", subblock)), errors)

    # DOI-first audits must reconcile their retained discovery events.
    for schedule_id, expected_events, expected_unique in (("A2", 119, 40), ("BT2", 205, 23)):
        audit = load(SEARCH_DIR / f"{schedule_id}-sampled-prefix-doi-dedup-audit.json")
        require(audit.get("source_events_seen") == expected_events, f"{schedule_id}: source-event total changed", errors)
        require(audit.get("unique_doi_count") == expected_unique, f"{schedule_id}: DOI-first count changed", errors)
        require(len(audit.get("sampled_records", [])) == expected_unique, f"{schedule_id}: DOI record list inconsistent", errors)
        require(len(audit.get("duplicate_manifestation_events", [])) == expected_events - expected_unique, f"{schedule_id}: duplicate ledger inconsistent", errors)

    # The aggregate assessment derives exhaustion and threshold scope from the
    # saved cell traversals rather than asserting them as constants.
    assessment = load(SEARCH_DIR / "schedule-assessment.json")
    require(
        assessment.get("date_window", {}).get("count_scope")
        == "source-month totals before exact-day exclusions; therefore conservative for the requested cutoff",
        "schedule assessment does not state the source-month count scope",
        errors,
    )
    require(
        assessment.get("investigation_threshold", {}).get("does_not_apply_to")
        == "overlapping raw source events across cells",
        "schedule assessment does not distinguish records from raw source events",
        errors,
    )
    for schedule_id, expected_cells in (("A2", 9), ("BT2", 36)):
        sampled = assessment.get("entries", {}).get(schedule_id, {}).get("sampled_diagnostics", {})
        derivation = sampled.get("exhaustion_derivation", {})
        require(sampled.get("all_refined_cells_exhausted") is True, f"{schedule_id}: refined cells not exhausted", errors)
        require(derivation.get("expected_cell_count") == expected_cells, f"{schedule_id}: expected-cell derivation changed", errors)
        require(derivation.get("completed_cell_count") == expected_cells, f"{schedule_id}: completed-cell derivation changed", errors)
        require(derivation.get("source_failures") == 0, f"{schedule_id}: sampled traversal retained a source failure", errors)
        require(
            derivation.get("every_cell_results_retrieved_equals_source_total") is True,
            f"{schedule_id}: sampled cell retrieval did not reconcile to totals",
            errors,
        )

    # Markdown links used by the pilot and guideline must resolve locally.
    for markdown in (ROOT / "pilot.md", ROOT.parent.parent / "source-specific-guidelines.md"): 
        text = markdown.read_text()
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            candidate = (markdown.parent / target).resolve()
            require(candidate.exists(), f"{markdown.name}: broken local link {target}", errors)

    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(json.dumps({"status": "ok", "json_files": len(json_paths), "primary_schedule_entries": len(SCHEDULE_IDS), "T2_pairs": len(T2_PAIRS), "doi_first_unions": {"A2": 40, "BT2": 23}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
