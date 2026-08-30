#!/usr/bin/env python3
"""Reconcile Pilot 004's immutable normal-CLI cell receipts offline."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import (
    KNOWN_DOI,
    PRIMARY_DIR,
    SEARCH_DIR,
    UNION_DIR,
    Cell,
    artifact_path,
    artifact_total,
    atomic_write_json,
    canonical_doi,
    failure_path,
    final_cells_by_schedule,
    load_json,
    primary_cells,
    scheduled_visible_blocks,
    successful_attempt,
    validate_preview_artifact,
    validate_zero_count_artifact,
    visible_block_hits,
)
from queries import SCHEDULE_IDS


def primary_sums() -> dict[str, int]:
    artifact = SEARCH_DIR / "primary-field-union.json"
    if not artifact.exists():
        raise RuntimeError("missing primary-field-union.json")
    values = load_json(artifact).get("conservative_primary_cell_sums")
    if not isinstance(values, dict) or set(values) != set(SCHEDULE_IDS):
        raise RuntimeError("primary field-union assessment is incomplete")
    result = {key: values[key] for key in SCHEDULE_IDS}
    if not all(isinstance(value, int) and value >= 0 for value in result.values()):
        raise RuntimeError("primary field-union totals are invalid")
    return result


def accepted_artifact(cell: Cell) -> tuple[Path, dict[str, Any], str]:
    preview = successful_attempt(artifact_path(UNION_DIR, cell))
    if preview is not None:
        data = load_json(preview)
        errors = validate_preview_artifact(data, cell)
        if not errors:
            return preview, data, "complete_preview"
    zero = successful_attempt(artifact_path(UNION_DIR, cell, ".zero-count"))
    if zero is not None:
        data = load_json(zero)
        errors = validate_zero_count_artifact(data, cell)
        if not errors:
            return zero, data, "exact_zero_count_fallback"
    details = []
    if preview is not None:
        details.append(f"preview={preview.name}")
    if zero is not None:
        details.append(f"zero={zero.name}")
    raise RuntimeError(f"No accepted final artifact for {cell.cell_id}: {', '.join(details) or 'none'}")


def failures_for(cell: Cell) -> list[str]:
    names = []
    for candidate in sorted(UNION_DIR.glob(f"{cell.cell_id}*.NON_MERGEABLE_FAILURE.json")):
        # Every such sidecar is deliberately retained. The selected complete
        # preview/count receipt determines the cell's current usable state.
        names.append(candidate.name)
    return names


def union_for(schedule_id: str, cells: tuple[Cell, ...], primary_sum: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cell_rows: list[dict[str, Any]] = []
    source_events: list[dict[str, Any]] = []
    source_failures: list[str] = []
    errors: list[str] = []
    for cell in cells:
        path, data, capture_kind = accepted_artifact(cell)
        total = artifact_total(data)
        rows = data.get("results", [])
        if capture_kind == "complete_preview":
            if not isinstance(rows, list) or len(rows) != total:
                errors.append(f"{cell.cell_id}: preview count does not equal source total")
            else:
                for rank, record in enumerate(rows, start=1):
                    if not isinstance(record, dict):
                        errors.append(f"{cell.cell_id}: non-object preview record")
                        continue
                    raw = record.get("doi")
                    if not isinstance(raw, str) or not raw.strip():
                        errors.append(f"{cell.cell_id}: preview record lacks DOI")
                        continue
                    source_events.append(
                        {
                            "source_cell": cell.cell_id,
                            "source_rank": record.get("rank", rank),
                            "source_manifestation_id": raw,
                            "doi": canonical_doi(raw),
                            "title": record.get("title"),
                            "url": record.get("url"),
                        }
                    )
        elif total != 0:
            errors.append(f"{cell.cell_id}: count fallback was not zero")
        cell_rows.append(
            {
                "cell_id": cell.cell_id,
                "stage": cell.stage,
                "artifact": str(path.relative_to(SEARCH_DIR.parent)),
                "capture_kind": capture_kind,
                "source_total": total,
                "results_retrieved": len(rows) if isinstance(rows, list) else None,
                "failure_artifacts_preserved": failures_for(cell),
            }
        )
        source_failures.extend(failures_for(cell))

    first_by_doi: dict[str, dict[str, Any]] = {}
    duplicate_events: list[dict[str, Any]] = []
    for event in source_events:
        doi = event["doi"]
        if doi in first_by_doi:
            duplicate_events.append({"duplicate_of_doi": doi, **event})
        else:
            first_by_doi[doi] = event
    unique_records = list(first_by_doi.values())
    raw_total = sum(row["source_total"] for row in cell_rows)
    reconciled = raw_total == len(source_events)
    if not reconciled:
        errors.append("sum of source totals does not equal retained source events")
    unique_count = len(unique_records)
    over_100 = unique_count > 100
    refinement_used = primary_sum > 100
    result = {
        "schedule_id": schedule_id,
        "semantic_query": cells[0].semantic_query if cells else None,
        "primary_conservative_cell_sum": primary_sum,
        "refinement_used": refinement_used,
        "selection_reason": (
            "primary P-field sum exceeded 100; used the 3-by-3 P/defining-block union"
            if refinement_used and schedule_id != "BT2"
            else "primary P-field sum exceeded 100; used the 3-by-3 P/M_B union and four disjoint T2 OR subcells"
            if refinement_used and schedule_id == "BT2"
            else "primary P-field sum did not exceed 100; retained the three-cell P field union"
        ),
        "cells": cell_rows,
        "source_event_count": len(source_events),
        "sum_of_final_cell_source_totals": raw_total,
        "cell_total_reconciliation": reconciled,
        "doi_first_identity_rule": "normalized DOI before an ARC virtual-collection @ suffix; raw manifestation IDs remain in source events",
        "unique_doi_count": unique_count,
        "doi_first_records": unique_records,
        "duplicate_manifestation_events": duplicate_events,
        "source_failures_preserved": sorted(set(source_failures)),
        "over_100_work": {
            "primary_cell_sum_exceeded_100": refinement_used,
            "deduplicated_doi_set_exceeded_100": over_100,
            "status": (
                "investigation_required_before_acceptance"
                if over_100
                else "no_deduplicated_set_over_100; overlapping raw cell events do not themselves trigger the threshold"
            ),
        },
        "errors": errors,
    }
    return result, unique_records


def visible_title_audit(entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    audit_entries: dict[str, Any] = {}
    for schedule_id, entry in entries.items():
        blocks = scheduled_visible_blocks(schedule_id)
        records = []
        warning_count = 0
        for record in entry["doi_first_records"]:
            title = record.get("title") if isinstance(record.get("title"), str) else ""
            hits = {block: visible_block_hits(title, block) for block in blocks}
            warnings = [block for block, value in hits.items() if not value["matched"]]
            if warnings:
                warning_count += 1
            records.append(
                {
                    "doi": record["doi"],
                    "title": title,
                    "source_cell": record["source_cell"],
                    "required_block_title_hits": hits,
                    "visible_title_warnings": warnings,
                    "classification": (
                        "visible_title_incomplete_or_hidden_anywhere_full_text_match_possible"
                        if warnings
                        else "all_scheduled_blocks_have_an_exact_visible_title_hit"
                    ),
                }
            )
        audit_entries[schedule_id] = {
            "required_blocks": list(blocks),
            "doi_first_record_count": len(records),
            "records_with_visible_title_warning": warning_count,
            "records": records,
        }
    return {
        "schema_version": "aiaa-arc-pilot004-visible-title-term-audit/v1",
        "pilot": "004",
        "source": "AIAA Aerospace Research Central (ARC)",
        "do_not_merge": True,
        "method": {
            "visible_text": "Only the rendered result-card title retained in the non-mergeable preview artifact.",
            "literal_matching": "case-folded ordered lexical token phrase matching against the unmodified Pilot 003 literal lists.",
            "pair_matching": "either order with no more than five intervening lexical tokens, against the unmodified declared pairs.",
            "scope": "A warning is not a false-match or eligibility decision. ARC Anywhere can match hidden indexing or full text, and keyword/abstract fields are not retained by preview mode.",
        },
        "entries": audit_entries,
    }


def main() -> int:
    recall = load_json(SEARCH_DIR / "known-item-recall.json")
    if recall.get("decision", {}).get("status") != "accepted_observed_known_item_recall":
        raise SystemExit("known-item recall is not accepted")
    sums = primary_sums()
    selected = final_cells_by_schedule(sums)
    entries: dict[str, dict[str, Any]] = {}
    all_errors: list[str] = []
    for schedule_id in SCHEDULE_IDS:
        entry, _ = union_for(schedule_id, selected[schedule_id], sums[schedule_id])
        entries[schedule_id] = entry
        all_errors.extend(f"{schedule_id}: {error}" for error in entry["errors"])
        if entry["over_100_work"]["deduplicated_doi_set_exceeded_100"]:
            all_errors.append(f"{schedule_id}: deduplicated set exceeds 100 and needs investigation")
    known_in_unions = {
        schedule_id: KNOWN_DOI in {record["doi"] for record in entry["doi_first_records"]}
        for schedule_id, entry in entries.items()
    }
    assessment = {
        "schema_version": "aiaa-arc-pilot004-schedule-unions/v1",
        "pilot": "004",
        "source": "AIAA Aerospace Research Central (ARC)",
        "diagnostic_only": True,
        "do_not_merge": True,
        "date_window": {
            "requested_start": "2011-01-01",
            "requested_end": "2026-08-29",
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "count_scope": "ARC source-month totals before exact-day exclusions; conservative at the requested 2026-08-29 cutoff.",
        },
        "field_union": {
            "population_fields": ["Title", "Keywords", "Abstract"],
            "high_volume_refinement": "3-by-3 P/defining-block assignments, with any third block left Anywhere",
            "t2": "Four disjoint 56-pair T2 OR subcells restore all 224 declared pairs exactly once where T2 is split.",
            "normal_cli": "Every artifact was generated with repeatable repaired normal --field-row CLI arguments; no Pilot 003 import-side writer was used.",
        },
        "threshold": {
            "records": 100,
            "applies_to": "a conservative P-field cell sum and any DOI-first deduplicated union",
            "does_not_apply_to": "overlapping raw source events across field-assignment cells",
        },
        "entries": entries,
        "known_item_membership_in_final_unions": known_in_unions,
        "all_cell_unions_reconciled": not all_errors,
        "errors": all_errors,
    }
    title_audit = visible_title_audit(entries)
    assessment_path = SEARCH_DIR / "schedule-unions.json"
    audit_path = SEARCH_DIR / "visible-title-term-audit.json"
    if assessment_path.exists() or audit_path.exists():
        raise SystemExit("assessment output already exists; immutable pilot artifacts cannot be overwritten")
    atomic_write_json(assessment_path, assessment)
    atomic_write_json(audit_path, title_audit)
    print(
        json.dumps(
            {
                "saved": [str(assessment_path), str(audit_path)],
                "union_totals": {key: entry["unique_doi_count"] for key, entry in entries.items()},
                "errors": all_errors,
            },
            indent=2,
        )
    )
    return 0 if not all_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
