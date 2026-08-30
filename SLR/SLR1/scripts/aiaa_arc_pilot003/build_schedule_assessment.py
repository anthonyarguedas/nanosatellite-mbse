#!/usr/bin/env python3
"""Build Pilot 003's compact, linkable schedule assessment from saved cells."""

from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Any

from queries import (
    BLOCKS,
    METADATA_FIELDS,
    SCHEDULE,
    SCHEDULE_IDS,
    T2_PAIRS,
    T2_SUBBLOCKS,
)
from run_fielded_count import write_full_json

PILOT_DIR = Path(__file__).resolve().parents[2] / "source-specific/aiaa-arc/pilots/003"
SEARCH_DIR = PILOT_DIR / "searches"
TARGET_SLUG = {"M_H": "MH", "M_H_OR_M_B": "MH-or-MB", "M_B": "MB", "G_model": "Gmodel", "G_structure": "Gstructure"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def failure_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE{path.suffix}")


def success_or_retry(path: Path) -> tuple[Path | None, list[Path]]:
    failures = []
    if path.exists():
        return path, failures
    candidate = path
    for attempt in range(4):
        if attempt:
            candidate = path.with_name(f"{path.stem}-retry{attempt}{path.suffix}")
        prior = failure_path(candidate)
        if prior.exists():
            failures.append(prior)
        if candidate.exists():
            return candidate, failures
    return None, failures


def successful_cell(cell_id: str, path: Path) -> dict[str, Any]:
    selected, failures = success_or_retry(path)
    if selected is None:
        return {
            "cell_id": cell_id,
            "artifact": None,
            "source_total": None,
            "status": "source_failure",
            "failure_artifacts": [item.name for item in failures],
        }
    data = load(selected)
    metadata = data.get("output_metadata", {})
    source_status = metadata.get("status", "unknown")
    return {
        "cell_id": cell_id,
        "artifact": selected.name,
        "source_total": data.get("total"),
        "status": "success_count_only" if metadata.get("count_only") is True else source_status,
        "source_status": source_status,
        "failure_artifacts": [item.name for item in failures],
        "controls_proven": bool(metadata.get("observed_exact_query_echo") and metadata.get("exact_date_controls_proven")),
    }


def primary_cells(schedule_id: str) -> dict[str, Any]:
    if schedule_id != "BT2":
        cells = [
            successful_cell(
                f"{schedule_id}-P-{field.lower()}", SEARCH_DIR / f"{schedule_id}-P-{field.lower()}.json"
            )
            for field in METADATA_FIELDS
        ]
        totals = [cell["source_total"] for cell in cells]
        return {
            "stage": "metadata_population_field_union",
            "cells": cells,
            "conservative_sum": sum(totals) if all(isinstance(value, int) for value in totals) else None,
            "sum_interpretation": "Sum of overlapping cells; an upper bound, not an identifier union.",
        }
    parents = []
    cells = []
    for field in METADATA_FIELDS:
        parent = SEARCH_DIR / f"BT2-P-{field.lower()}.json"
        failure = failure_path(parent)
        parents.append(
            {
                "cell_id": f"BT2-P-{field.lower()}",
                "artifact": failure.name if failure.exists() else None,
                "source_total": None,
                "status": "source_failure_length_or_complexity_unclassified",
            }
        )
        for index in range(len(T2_SUBBLOCKS)):
            path = SEARCH_DIR / f"BT2-P-{field.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}.json"
            cells.append(successful_cell(path.stem, path))
    totals = [cell["source_total"] for cell in cells]
    return {
        "stage": "metadata_population_field_union_with_lossless_T2_OR_subcells",
        "unsplit_parent_cells": parents,
        "cells": cells,
        "split": {
            "block": "T2",
            "subcells": len(T2_SUBBLOCKS),
            "pair_count_per_subcell": 56,
            "total_declared_pairs": len(T2_PAIRS),
            "restoration": "OR across four disjoint, source-order T2 pair subcells restores all 224 declared pairs exactly once.",
        },
        "conservative_sum": sum(totals) if all(isinstance(value, int) for value in totals) else None,
        "sum_interpretation": "Sum of overlapping P-field and T2-OR subcells; an upper bound, not an identifier union.",
    }


def refined_cells(schedule_id: str) -> dict[str, Any] | None:
    if schedule_id == "BC1":
        return None
    if schedule_id != "BT2":
        entry = SCHEDULE[schedule_id]
        target = TARGET_SLUG[entry["defining_name"]]
        cells = []
        for population in METADATA_FIELDS:
            for defining in METADATA_FIELDS:
                path = SEARCH_DIR / f"{schedule_id}-P-{population.lower()}-{target}-{defining.lower()}.json"
                cells.append(successful_cell(path.stem, path))
        totals = [cell["source_total"] for cell in cells]
        return {
            "stage": "P_and_defining_block_3_by_3",
            "defining_block": entry["defining_name"],
            "third_block_anywhere": entry["third_name"],
            "cells": cells,
            "conservative_sum": sum(totals) if all(isinstance(value, int) for value in totals) else None,
            "sum_interpretation": "Sum of overlapping 3-by-3 cells; an upper bound, not an identifier union.",
        }
    cells = []
    for population in METADATA_FIELDS:
        for defining in METADATA_FIELDS:
            for index in range(len(T2_SUBBLOCKS)):
                path = SEARCH_DIR / f"BT2-P-{population.lower()}-MB-{defining.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}.json"
                cells.append(successful_cell(path.stem, path))
    totals = [cell["source_total"] for cell in cells]
    return {
        "stage": "P_and_M_B_3_by_3_with_T2_OR_subcells",
        "defining_block": "M_B",
        "third_block_anywhere": "T2",
        "cells": cells,
        "conservative_sum": sum(totals) if all(isinstance(value, int) for value in totals) else None,
        "sum_interpretation": "Sum of overlapping 3-by-3 and T2 OR-subcells; an upper bound, not an identifier union.",
    }


def sample_summary(schedule_id: str) -> dict[str, Any] | None:
    audit = SEARCH_DIR / f"{schedule_id}-sampled-prefix-doi-dedup-audit.json"
    if not audit.exists():
        return None
    data = load(audit)
    prefix = load(SEARCH_DIR / f"{schedule_id}-sampled-prefix-preview.json")
    records = data["sampled_records"]
    diagnostics = [record.get("diagnostic", {}) for record in records]
    page_metadata = [record.get("page_metadata", {}) for record in records]
    if schedule_id == "A2":
        target_key = "M_H_or_M_B_assigned_field"
        third_key = "E_F_any_visible_field"
    else:
        target_key = "M_B_assigned_field"
        third_key = "T2_pair_any_visible_field"
    types: dict[str, int] = {}
    for metadata in page_metadata:
        label = (
            metadata.get("publication_subtype_context")
            or metadata.get("publication_type_visible")
            or metadata.get("publication_type_og")
            or "metadata_missing"
        )
        types[label] = types.get(label, 0) + 1
    expected_cell_count = 9 if schedule_id == "A2" else 36
    source_runs = prefix.get("source_runs", [])
    all_refined_cells_exhausted = (
        len(source_runs) == expected_cell_count
        and not prefix.get("source_failures")
        and all(
            run.get("source_total") == run.get("results_retrieved")
            for run in source_runs
        )
    )
    return {
        "artifact": audit.name,
        "source_events_across_all_refined_cells": data["source_events_seen"],
        "doi_first_deduplicated_records": data["unique_doi_count"],
        "duplicate_manifestation_events": len(data["duplicate_manifestation_events"]),
        "all_refined_cells_exhausted": all_refined_cells_exhausted,
        "exhaustion_derivation": {
            "expected_cell_count": expected_cell_count,
            "completed_cell_count": len(source_runs),
            "source_failures": len(prefix.get("source_failures", [])),
            "every_cell_results_retrieved_equals_source_total": all(
                run.get("source_total") == run.get("results_retrieved")
                for run in source_runs
            ),
        },
        "visible_population_confirmation": sum(bool(item.get("visible_population_confirmation")) for item in diagnostics),
        "visible_target_confirmation": sum(bool(item.get("visible_target_confirmation")) for item in diagnostics),
        "visible_third_block_confirmation": sum(bool(item.get("visible_third_block_confirmation")) for item in diagnostics),
        "assigned_P_field_confirmation": sum(bool(item.get("expected_field_confirmation", {}).get("P_assigned_field")) for item in diagnostics),
        "assigned_target_field_confirmation": sum(bool(item.get("expected_field_confirmation", {}).get(target_key)) for item in diagnostics),
        "assigned_third_field_confirmation": sum(bool(item.get("expected_field_confirmation", {}).get(third_key)) for item in diagnostics),
        "possible_hidden_or_full_text_matches": sum(bool(item.get("possible_hidden_or_full_text_match")) for item in diagnostics),
        "likely_scope": {"metadata_incomplete_or_hidden_match_possible": len(records)},
        "acronym_only_or_acronym_target_records": sum(
            bool(item.get("acronym_hits")) and any(item.get("acronym_hits", {}).values())
            for item in diagnostics
        ),
        "wildcard_noise": "none; no wildcard translation was accepted or used",
        "publication_type_visible_metadata": types,
        "recurring_removable_noise": (
            "Only 1/40 records visibly confirms E_F; generic CubeSat/SmallSat model records recur across cells. Do not call the other 39 false matches without full text."
            if schedule_id == "A2"
            else "No sampled record visibly confirms a declared T2 pair. T2 is recurring possible hidden or full-text match noise, not a proved false-match class."
        ),
    }


def failure_register() -> list[dict[str, Any]]:
    output = []
    for name in sorted(glob.glob(str(SEARCH_DIR / "*.NON_MERGEABLE_FAILURE.json"))):
        path = Path(name)
        data = load(path)
        failure = data.get("failure", {})
        cell = data.get("pilot_cell", {})
        output.append(
            {
                "artifact": path.name,
                "cell_id": cell.get("cell_id") or cell.get("parent_cell") or path.stem,
                "error_type": failure.get("error_type"),
                "error": failure.get("error"),
                "disposition": "preserved; see successful retry or lossless subcell replacement where named in the relevant stage",
            }
        )
    # The first A2 RIS-prefix attempt is an intentionally retained aggregate
    # diagnostic rather than a suffix-named cell failure.
    for schedule_id in ("A2", "BT2"):
        prefix = SEARCH_DIR / f"{schedule_id}-sampled-prefix.json"
        if prefix.exists():
            for failure in load(prefix).get("source_failures", []):
                output.append(
                    {
                        "artifact": prefix.name,
                        "cell_id": failure.get("cell_id"),
                        "error_type": failure.get("error_type"),
                        "error": failure.get("error"),
                        "disposition": "preserved; preview-mode DOI capture succeeded separately and did not relabel the RIS failure as zero or a false match",
                    }
                )
    return output


def main() -> None:
    output_path = SEARCH_DIR / "schedule-assessment.json"
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite {output_path}")
    primary = {schedule_id: primary_cells(schedule_id) for schedule_id in SCHEDULE_IDS}
    refined = {schedule_id: refined_cells(schedule_id) for schedule_id in SCHEDULE_IDS}
    samples = {schedule_id: sample_summary(schedule_id) for schedule_id in SCHEDULE_IDS}
    final = {
        "A1": "low_volume_conservative_upper_bound_after_3_by_3:42; field proposal remains unaccepted",
        "A2": "low_volume_doi_first_union:40 after 119 source events; visible E_F noise remains; field proposal remains unaccepted",
        "A3": "low_volume_conservative_upper_bound_after_3_by_3:33; field proposal remains unaccepted",
        "B1": "low_volume_conservative_upper_bound_after_3_by_3:87; two transient source failures recovered; field proposal remains unaccepted",
        "B2": "low_volume_conservative_upper_bound_after_3_by_3:56; field proposal remains unaccepted",
        "BG1": "low_volume_conservative_upper_bound_after_3_by_3:93; four transient source failures recovered; field proposal remains unaccepted",
        "BG2": "low_volume_conservative_upper_bound_after_3_by_3:20; transient source failures recovered through retry2; field proposal remains unaccepted",
        "BC1": "low_volume_conservative_upper_bound:52; no refinement needed; field proposal remains unaccepted",
        "BT2": "low_volume_doi_first_union:23 after 205 source events; all sampled records lack visible T2-pair confirmation; field proposal remains unaccepted",
    }
    payload = {
        "schema_version": "aiaa-arc-schedule-assessment/v1",
        "pilot": "003",
        "source": "AIAA Aerospace Research Central (ARC)",
        "date_window": {
            "requested_start": "2011-01-01",
            "requested_end": "2026-08-29",
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "count_scope": "source-month totals before exact-day exclusions; therefore conservative for the requested cutoff",
            "mode": "diagnostic_only",
        },
        "investigation_threshold": {
            "records": 100,
            "applies_to": "conservative cell-sum upper bound or DOI-first deduplicated investigation records",
            "does_not_apply_to": "overlapping raw source events across cells",
        },
        "controls": {
            "access": "All content",
            "language": "unavailable: no ARC language control or facet; no source restriction applied",
            "publication_type": "no type filter: visible facets do not prove a lossless eligible-type union",
            "topic": "not applied: ConceptID lacks descriptor, scope, hierarchy, and explosion semantics",
            "wildcard": "not used: Pilot 002 did not establish stable-ID equality/superset for nanosatellit*",
            "advanced_rows": "AND across visible rows; all successful cells retain source-readback field rows and exact month controls",
        },
        "translation_audit": {
            "literal_counts": {"P": 26, "E_H": 38, "E_F": 37, "M_H": 54, "M_B": 31, "R": 55, "G_model_fixed": 14, "G_structure_fixed": 8, "C1_fixed": 26},
            "pair_counts": {"G_model": 16, "G_structure": 16, "C1": 36, "T2": len(T2_PAIRS)},
            "wildcards_present": False,
            "all_blocks_parenthesized": all(value.startswith("(") and value.endswith(")") for value in BLOCKS.values()),
        },
        "entries": {
            schedule_id: {
                "primary": primary[schedule_id],
                "refinement": refined[schedule_id],
                "sampled_diagnostics": samples[schedule_id],
                "final_status": final[schedule_id],
            }
            for schedule_id in SCHEDULE_IDS
        },
        "known_item_check": {
            "status": "not_sufficient_to_accept_field_narrowing",
            "repository_check": "No stable-ID register of known eligible AIAA reports was found. Pilot 001 A1/BG1 runs were count-only; its BG1 preview is not an eligible-item register.",
            "sanity_observation": "The non-eligibility-sentinel AIAA record 10.2514/6.2016-5551 is retained in the A2/BT2 DOI-prefix diagnostics, but it cannot establish eligible EPS recall.",
            "decision": "No translation is accepted. A known eligible AIAA sentinel set or a later full-text recall check is required before adopting P/defining-block metadata narrowing.",
        },
        "source_failures": failure_register(),
        "overall": {
            "candidate_field_strategy": "For each scheduled query, union P in Title, Keywords, and Abstract. Where its upper bound exceeds 100, use the P-by-defining-block 3-by-3 union and leave the third semantic block in Anywhere. Split only T2 OR alternatives where the unsplit field row failed.",
            "acceptance": "unaccepted_uncommitted_proposal",
            "blockers": [
                "No verified known eligible AIAA sentinel demonstrates that metadata-only P/defining-block placement has no observed recall loss versus Anywhere.",
                "A2 and BT2 remain visibly noisy because required Anywhere blocks often lack visible metadata evidence and may occur only in hidden indexed content or full text.",
                "ARC has no language limiter. Type facets cannot be shown to be lossless. Topic semantics are insufficient for a safe noise filter.",
            ],
        },
    }
    write_full_json(output_path, payload)
    print(json.dumps({"saved": str(output_path), "entries": list(payload["entries"]), "source_failures": len(payload["source_failures"])}, indent=2))


if __name__ == "__main__":
    main()
