#!/usr/bin/env python3
"""Fail-closed offline integrity checks for the Pilot 004 ARC diagnostics."""

from __future__ import annotations

import json
import re
from pathlib import Path

from common import (
    DATE_END,
    DATE_START,
    KNOWN_DOI,
    PILOT_DIR,
    PRIMARY_DIR,
    RECALL_DIR,
    ROOT,
    SEARCH_DIR,
    UNION_DIR,
    artifact_path,
    artifact_total,
    final_cells_by_schedule,
    load_json,
    primary_cells,
    recall_cells,
    successful_attempt,
    validate_artifact_common,
    validate_preview_artifact,
    validate_zero_count_artifact,
)
from queries import BLOCKS, SCHEDULE_IDS, T2_PAIRS, T2_SUBBLOCKS


MACHINE_SPECIFIC_PATH = re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/[^/\s]+")
PILOT004_SCOPE = (PILOT_DIR, ROOT / "scripts" / "aiaa_arc_pilot004")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def primary_sums(errors: list[str]) -> dict[str, int]:
    artifact = SEARCH_DIR / "primary-field-union.json"
    require(artifact.exists(), "missing primary-field-union.json", errors)
    if not artifact.exists():
        return {}
    values = load_json(artifact).get("conservative_primary_cell_sums")
    require(isinstance(values, dict) and set(values) == set(SCHEDULE_IDS), "primary sums are incomplete", errors)
    if not isinstance(values, dict) or set(values) != set(SCHEDULE_IDS):
        return {}
    require(all(isinstance(values[key], int) and values[key] >= 0 for key in SCHEDULE_IDS), "primary sums are invalid", errors)
    return {key: values[key] for key in SCHEDULE_IDS}


def selected_final_artifact(cell, errors: list[str]) -> tuple[Path | None, dict | None, str | None]:
    preview = successful_attempt(artifact_path(UNION_DIR, cell))
    if preview is not None:
        data = load_json(preview)
        issues = validate_preview_artifact(data, cell)
        if not issues:
            return preview, data, "complete_preview"
        errors.extend(f"{preview.name}: {issue}" for issue in issues)
        return None, None, None
    zero = successful_attempt(artifact_path(UNION_DIR, cell, ".zero-count"))
    if zero is not None:
        data = load_json(zero)
        issues = validate_zero_count_artifact(data, cell)
        if not issues:
            return zero, data, "exact_zero_count_fallback"
        errors.extend(f"{zero.name}: {issue}" for issue in issues)
        return None, None, None
    errors.append(f"missing accepted final artifact for {cell.cell_id}")
    return None, None, None


def local_markdown_links(markdown: Path, errors: list[str]) -> None:
    if not markdown.exists():
        errors.append(f"missing documentation: {markdown}")
        return
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", markdown.read_text()):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        candidate = (markdown.parent / target).resolve()
        require(candidate.exists(), f"{markdown.name}: broken link {target}", errors)


def machine_specific_paths(errors: list[str]) -> None:
    for directory in PILOT004_SCOPE:
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            require(
                MACHINE_SPECIFIC_PATH.search(text) is None,
                f"{path.relative_to(ROOT)}: machine-specific path",
                errors,
            )


def main() -> int:
    errors: list[str] = []
    # Parse every retained actual artifact, including null failure receipts.
    json_paths = sorted(path for path in SEARCH_DIR.rglob("*.json") if not path.name.startswith("."))
    require(json_paths != [], "no Pilot 004 JSON artifacts found", errors)
    for path in json_paths:
        try:
            load_json(path)
        except Exception as error:  # noqa: BLE001 - validation needs all parser errors.
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {error}")

    # Construction invariants, not a shortened synonym/wildcard translation.
    require(BLOCKS["G_model"].count(" OR ") + 1 == 30, "G_model is not 14 literals + 16 pairs", errors)
    require(BLOCKS["G_structure"].count(" OR ") + 1 == 24, "G_structure is not 8 literals + 16 pairs", errors)
    require(BLOCKS["C1"].count(" OR ") + 1 == 62, "C1 is not 26 literals + 36 pairs", errors)
    require(len(T2_PAIRS) == 224, "T2 pair declaration count changed", errors)
    require(len(T2_SUBBLOCKS) == 4 and all(block.count(" OR ") + 1 == 56 for block in T2_SUBBLOCKS), "T2 is not four disjoint 56-pair subcells", errors)
    require(all("*" not in block and "?" not in block for block in BLOCKS.values()), "wildcard found in normative block", errors)

    # The source-indexing event establishes the DOI as an ARC record before the
    # metadata-field recall gate is used.
    indexing = SEARCH_DIR / "known-item-source-indexing-doi-retry1.json"
    require(indexing.exists(), "missing successful DOI source-indexing receipt", errors)
    if indexing.exists():
        indexed = load_json(indexing)
        index_errors = validate_preview_artifact(
            indexed,
            type("IndexCell", (), {"rows": (("Anywhere", f'"{KNOWN_DOI}"'),), "cell_id": "known-item-source-indexing-doi"})(),
        )
        errors.extend(f"{indexing.name}: {issue}" for issue in index_errors)
        require(
            KNOWN_DOI in {str(row.get("doi", "")).casefold() for row in indexed.get("results", []) if isinstance(row, dict)},
            "DOI source-indexing receipt does not retain the known DOI",
            errors,
        )

    evidence_path = SEARCH_DIR / "known-item-evidence.json"
    require(evidence_path.exists(), "missing source-located known-item evidence", errors)
    if evidence_path.exists():
        evidence = load_json(evidence_path)
        require(evidence.get("known_item", {}).get("doi") == KNOWN_DOI, "known-item evidence DOI differs", errors)
        require(evidence.get("known_item", {}).get("pdf_page_count") == 11, "known-item evidence does not retain the 11-page PDF", errors)
        expected_applicable = ["A2", "B1", "B2", "BC1", "BT2"]
        require(
            evidence.get("exact_full_text_block_check", {}).get("applicable_scheduled_partitions") == expected_applicable,
            "source-located known-item partition membership differs",
            errors,
        )

    recall_path = SEARCH_DIR / "known-item-recall.json"
    require(recall_path.exists(), "missing final known-item recall decision", errors)
    if recall_path.exists():
        recall = load_json(recall_path)
        require(recall.get("decision", {}).get("status") == "accepted_observed_known_item_recall", "field-union recall was not accepted", errors)
        applicable = recall.get("applicable_partitions", {})
        require(set(applicable) == {"A2", "B1", "B2", "BC1", "BT2"}, "recall partition set differs", errors)
        for schedule_id, cells in recall_cells().items():
            entry = applicable.get(schedule_id, {})
            require(entry.get("known_doi_retrieved") is True, f"{schedule_id}: known DOI was not retrieved", errors)
            require(entry.get("status") == "retrieved", f"{schedule_id}: recall cell union not complete", errors)
            if schedule_id == "BT2":
                require(entry.get("all_lossless_subcells_executed") is True, "BT2 recall did not retain all four T2 subcells", errors)
            for cell in cells:
                artifact = successful_attempt(artifact_path(RECALL_DIR, cell))
                require(artifact is not None, f"{schedule_id}: missing recall cell {cell.cell_id}", errors)
                if artifact is not None:
                    issues = validate_preview_artifact(load_json(artifact), cell)
                    errors.extend(f"{artifact.name}: {issue}" for issue in issues)

    sums = primary_sums(errors)
    if sums:
        primary_count = 0
        for schedule_id in SCHEDULE_IDS:
            observed_sum = 0
            for cell in primary_cells(schedule_id):
                artifact = successful_attempt(artifact_path(PRIMARY_DIR, cell))
                require(artifact is not None, f"missing primary cell {cell.cell_id}", errors)
                if artifact is None:
                    continue
                data = load_json(artifact)
                issues = validate_artifact_common(data, cell)
                errors.extend(f"{artifact.name}: {issue}" for issue in issues)
                metadata = data.get("output_metadata", {})
                require(metadata.get("status") == "count_only", f"{artifact.name}: primary cell is not count-only", errors)
                require(data.get("results") == [], f"{artifact.name}: count-only cell retained results", errors)
                observed_sum += artifact_total(data)
                primary_count += 1
            require(observed_sum == sums[schedule_id], f"{schedule_id}: primary sum does not reconcile", errors)
        require(primary_count == 36, f"expected 36 primary cells, found {primary_count}", errors)

        selected = final_cells_by_schedule(sums)
        expected_count = sum(len(cells) for cells in selected.values())
        require(expected_count == 102, f"expected 102 final cells, derived {expected_count}", errors)
        final_manifest = SEARCH_DIR / "final-cell-capture.json"
        require(final_manifest.exists(), "missing final-cell-capture.json", errors)
        final_cells_seen = 0
        for schedule_id in SCHEDULE_IDS:
            for cell in selected[schedule_id]:
                artifact, data, _kind = selected_final_artifact(cell, errors)
                if artifact is not None and data is not None:
                    final_cells_seen += 1
        require(final_cells_seen == expected_count, f"final accepted cells {final_cells_seen}/{expected_count}", errors)

    union_path = SEARCH_DIR / "schedule-unions.json"
    title_audit_path = SEARCH_DIR / "visible-title-term-audit.json"
    require(union_path.exists(), "missing schedule union reconciliation", errors)
    require(title_audit_path.exists(), "missing visible title warning audit", errors)
    if union_path.exists() and sums:
        unions = load_json(union_path)
        require(unions.get("all_cell_unions_reconciled") is True, "union receipt reports unreconciled cells", errors)
        require(unions.get("errors") == [], "union receipt retains errors", errors)
        entries = unions.get("entries", {})
        require(set(entries) == set(SCHEDULE_IDS), "union receipt lacks a schedule entry", errors)
        for schedule_id, entry in entries.items():
            require(entry.get("cell_total_reconciliation") is True, f"{schedule_id}: cell total union is unreconciled", errors)
            require(entry.get("source_event_count") == entry.get("sum_of_final_cell_source_totals"), f"{schedule_id}: source-event count differs from cell sum", errors)
            records = entry.get("doi_first_records", [])
            require(entry.get("unique_doi_count") == len(records), f"{schedule_id}: DOI-first count differs from records", errors)
            require(entry.get("unique_doi_count", 0) <= 100, f"{schedule_id}: deduplicated union over 100 lacks investigation", errors)
            require(
                entry.get("over_100_work", {}).get("deduplicated_doi_set_exceeded_100") is False,
                f"{schedule_id}: >100 work is unresolved",
                errors,
            )
        for schedule_id in ("A2", "B1", "B2", "BC1", "BT2"):
            dois = {record.get("doi") for record in entries[schedule_id].get("doi_first_records", [])}
            require(KNOWN_DOI in dois, f"{schedule_id}: final union lost the known DOI", errors)

    # Null failures are a retained audit trail, not converted into zero hits.
    for path in SEARCH_DIR.rglob("*.NON_MERGEABLE_FAILURE.json"):
        data = load_json(path)
        require(data.get("total") is None, f"{path.name}: failure receipt has a non-null total", errors)
        require(data.get("results") == [], f"{path.name}: failure receipt retained results", errors)
        require(data.get("do_not_merge") is True, f"{path.name}: failure receipt is mergeable", errors)

    pilot_markdown = ROOT / "source-specific" / "aiaa-arc" / "pilots" / "004" / "pilot.md"
    guideline = ROOT / "source-specific" / "aiaa-arc" / "source-specific-guidelines.md"
    local_markdown_links(pilot_markdown, errors)
    local_markdown_links(guideline, errors)
    machine_specific_paths(errors)
    if guideline.exists():
        text = guideline.read_text()
        require("Last pilot saved in commit: NA" in text, "guideline changed pilot completion state", errors)
        require("Final searches saved in commit: NA" in text, "guideline changed final-search completion state", errors)

    if errors:
        print("FAILED")
        print("\n".join(f"- {item}" for item in errors))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "json_artifacts": len(json_paths),
                "primary_cells": 36,
                "final_cells": 102,
                "union_totals": {
                    key: load_json(union_path)["entries"][key]["unique_doi_count"]
                    for key in SCHEDULE_IDS
                },
                "known_item": KNOWN_DOI,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
