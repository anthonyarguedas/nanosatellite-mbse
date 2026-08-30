#!/usr/bin/env python3
"""Run the 3-by-3 P/defining-block field assignments for high-volume entries."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from queries import METADATA_FIELDS, SCHEDULE, refinement_rows, semantic_query
from run_fielded_count import load_adapter, write_full_json
from run_stage1 import DATE_END, DATE_START, SEARCH_DIR, write_failure

# These seven entries exceeded 100 when the three P-in-metadata cells were summed.
HIGH_VOLUME = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2")
TARGET_SLUG = {
    "M_H": "MH",
    "M_H_OR_M_B": "MH-or-MB",
    "M_B": "MB",
    "G_model": "Gmodel",
    "G_structure": "Gstructure",
}


def path_for(schedule_id: str, population_field: str, defining_field: str) -> Path:
    target = TARGET_SLUG[SCHEDULE[schedule_id]["defining_name"]]
    return SEARCH_DIR / f"{schedule_id}-P-{population_field.lower()}-{target}-{defining_field.lower()}.json"


def run_cell(
    adapter,
    schedule_id: str,
    population_field: str,
    defining_field: str,
    path: Path,
    *,
    retry_of: Path | None = None,
) -> dict:
    entry = SCHEDULE[schedule_id]
    rows = refinement_rows(schedule_id, population_field, defining_field)
    target_slug = TARGET_SLUG[entry["defining_name"]]
    cell = {
        "pilot": "003",
        "stage": "metadata_population_and_defining_block_3_by_3",
        "schedule_id": schedule_id,
        "cell_id": f"{schedule_id}-P-{population_field.lower()}-{target_slug}-{defining_field.lower()}",
        "semantic_query": semantic_query(schedule_id),
        "population_block": "P",
        "population_field": population_field,
        "defining_block": entry["defining_name"],
        "defining_field": defining_field,
        "third_block": entry["third_name"],
        "third_field": "Anywhere" if entry["third"] is not None else None,
        "same_field_pair_semantics": "Every declared pair remains together inside its defining-block field row; two same-named advanced rows are conjunctive.",
        "union_coverage_claim": "The 3-by-3 cells cover P and the defining block in every combination of Title, Keywords, and Abstract. Their sum is an upper bound, not a deduplicated union.",
        "retry_of": retry_of.name if retry_of is not None else None,
    }
    try:
        result = adapter.search_aiaa_arc(
            None,
            field_rows=tuple(adapter.FieldRow(name, text) for name, text in rows),
            date_start=date.fromisoformat(DATE_START),
            date_end=date.fromisoformat(DATE_END),
            count_only=True,
            timeout_seconds=60.0 if retry_of is not None else adapter.DEFAULT_TIMEOUT_SECONDS,
            page_delay_seconds=1.0 if retry_of is not None else 0.0,
            cdp_url=os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL),
        )
        metadata = result.get("output_metadata", {})
        expected_rows = [
            {"field": adapter.normalize_arc_field(name), "label": adapter.ARC_FIELD_LABELS[adapter.normalize_arc_field(name)], "text": text}
            for name, text in rows
        ]
        if metadata.get("field_rows") != expected_rows:
            raise RuntimeError("ARC field-row readback did not preserve this 3-by-3 cell")
        if not (
            metadata.get("count_only") is True
            and metadata.get("observed_exact_query_echo") is True
            and metadata.get("exact_date_controls_proven") is True
            and metadata.get("language_filter") is None
            and metadata.get("publication_type_filter") is None
            and isinstance(result.get("total"), int)
            and result["total"] >= 0
        ):
            raise RuntimeError("ARC 3-by-3 count-only result lacked required exact control evidence")
        result.update(
            {
                "diagnostic_kind": "NON_MERGEABLE_FIELD_ASSIGNMENT_COUNT_ONLY",
                "diagnostic_mode": "count_only",
                "private_diagnostic": True,
                "do_not_merge": True,
                "merge_eligible": False,
                "publication_state": "count_only_diagnostic",
                "reason": "ARC count-only 3-by-3 field-assignment pilot; normalized records were intentionally omitted",
                "normalized_results_omitted": True,
                "normalized_csv_omitted": True,
                "native_export_omitted": True,
                "pilot_cell": cell,
            }
        )
        metadata.update(
            {
                "fielded_count_artifact_schema": "aiaa-arc-fielded-count/v1",
                "records_omitted_for_diagnostic": True,
                "merge_eligible": False,
                "publication_precommit_eligible": False,
                "publication_eligibility": "diagnostic_only",
            }
        )
        write_full_json(path, result)
        return {"cell": cell["cell_id"], "status": "count_only", "total": result["total"], "path": str(path)}
    except Exception as error:  # noqa: BLE001 - preserve every adapter/source failure.
        write_failure(adapter, path, rows, error, cell)
        return {"cell": cell["cell_id"], "status": "failure", "total": None, "path": str(path), "error": adapter.safe_error_message(error)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", choices=HIGH_VOLUME)
    parser.add_argument("--retry-failed", action="store_true", help="Preserve failed first attempts and run each missing cell once more with a 60-second source timeout and one-second page delay.")
    args = parser.parse_args()
    selected = tuple(args.only) if args.only else HIGH_VOLUME
    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    adapter = load_adapter()
    summary = []
    for schedule_id in selected:
        for population_field in METADATA_FIELDS:
            for defining_field in METADATA_FIELDS:
                path = path_for(schedule_id, population_field, defining_field)
                if path.exists():
                    data = json.loads(path.read_text())
                    summary.append({"cell": path.stem, "status": "existing", "total": data.get("total"), "path": str(path)})
                    continue
                first_failure = path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE{path.suffix}")
                if first_failure.exists() and not args.retry_failed:
                    summary.append({"cell": path.stem, "status": "prior_failure", "total": None, "path": str(first_failure)})
                    continue
                if first_failure.exists():
                    retry_of = first_failure
                    retry_path = None
                    for attempt in range(1, 4):
                        candidate = path.with_name(f"{path.stem}-retry{attempt}{path.suffix}")
                        candidate_failure = candidate.with_name(
                            f"{candidate.stem}.NON_MERGEABLE_FAILURE{candidate.suffix}"
                        )
                        if candidate.exists():
                            data = json.loads(candidate.read_text())
                            summary.append({"cell": candidate.stem, "status": "existing_retry", "total": data.get("total"), "path": str(candidate)})
                            retry_path = None
                            break
                        if candidate_failure.exists():
                            retry_of = candidate_failure
                            continue
                        retry_path = candidate
                        break
                    if retry_path is not None:
                        summary.append(run_cell(adapter, schedule_id, population_field, defining_field, retry_path, retry_of=retry_of))
                    elif not any(row.get("cell", "").startswith(path.stem) for row in summary[-1:]):
                        summary.append({"cell": path.stem, "status": "retry_limit_reached", "total": None, "path": str(retry_of)})
                else:
                    summary.append(run_cell(adapter, schedule_id, population_field, defining_field, path))
    print(json.dumps(summary, indent=2))
    return 1 if any(row["status"] == "failure" for row in summary) else 0


if __name__ == "__main__":
    raise SystemExit(main())
