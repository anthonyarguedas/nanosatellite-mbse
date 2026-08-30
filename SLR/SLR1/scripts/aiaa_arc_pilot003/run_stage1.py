#!/usr/bin/env python3
"""Run Pilot 003's three-cell metadata population field union, sequentially."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from queries import (
    METADATA_FIELDS,
    SCHEDULE,
    SCHEDULE_IDS,
    first_stage_rows,
    semantic_query,
)
from run_fielded_count import load_adapter, write_full_json

PILOT = "003"
PILOT_DIR = Path(__file__).resolve().parents[2] / "source-specific/aiaa-arc/pilots/003"
SEARCH_DIR = PILOT_DIR / "searches"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"


def path_for(schedule_id: str, field: str) -> Path:
    return SEARCH_DIR / f"{schedule_id}-P-{field.lower()}.json"


def failure_path_for(path: Path) -> Path:
    return path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE{path.suffix}")


def write_failure(adapter, path: Path, rows: tuple[tuple[str, str], ...], error: Exception, cell: dict) -> None:
    payload = {
        "schema_version": "aiaa-arc-fielded-count/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot_cell": cell,
        "requested_field_rows": [{"field": field, "text": text} for field, text in rows],
        "controls": {
            "date_start": DATE_START,
            "date_end": DATE_END,
            "access": "all",
            "language_filter": None,
            "publication_type_filter": None,
            "topic_selections": [],
            "result_facets": [],
            "mode": "count_only",
        },
        "executed_query": None,
        "total": None,
        "results": [],
        "do_not_merge": True,
        "failure": {
            "error_type": type(error).__name__,
            "error": adapter.safe_error_message(error),
        },
    }
    write_full_json(failure_path_for(path), payload)


def run_cell(adapter, schedule_id: str, field: str, path: Path) -> dict:
    rows = first_stage_rows(schedule_id, field)
    entry = SCHEDULE[schedule_id]
    cell = {
        "pilot": PILOT,
        "stage": "metadata_population_field_union",
        "schedule_id": schedule_id,
        "cell_id": f"{schedule_id}-P-{field.lower()}",
        "semantic_query": semantic_query(schedule_id),
        "population_block": "P",
        "population_field": field,
        "remainder_field": "Anywhere",
        "remainder": entry["remainder"],
        "union_coverage_claim": "P occurs in Title OR Keywords OR Abstract; cells are summed only as a conservative upper bound, not deduplicated.",
    }
    try:
        result = adapter.search_aiaa_arc(
            None,
            field_rows=tuple(adapter.FieldRow(name, text) for name, text in rows),
            date_start=date.fromisoformat(DATE_START),
            date_end=date.fromisoformat(DATE_END),
            count_only=True,
            cdp_url=os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL),
        )
        metadata = result.get("output_metadata", {})
        observed_rows = metadata.get("field_rows")
        if observed_rows != [
            {"field": adapter.normalize_arc_field(name), "label": adapter.ARC_FIELD_LABELS[adapter.normalize_arc_field(name)], "text": text}
            for name, text in rows
        ]:
            raise RuntimeError("ARC field-row readback did not preserve this cell")
        if not (
            metadata.get("count_only") is True
            and metadata.get("observed_exact_query_echo") is True
            and metadata.get("exact_date_controls_proven") is True
            and metadata.get("language_filter") is None
            and metadata.get("publication_type_filter") is None
            and isinstance(result.get("total"), int)
            and result["total"] >= 0
        ):
            raise RuntimeError("ARC count-only result lacked the required exact control evidence")
        result.update(
            {
                "diagnostic_kind": "NON_MERGEABLE_FIELD_ASSIGNMENT_COUNT_ONLY",
                "diagnostic_mode": "count_only",
                "private_diagnostic": True,
                "do_not_merge": True,
                "merge_eligible": False,
                "publication_state": "count_only_diagnostic",
                "reason": "ARC count-only fielded pilot; normalized records were intentionally omitted",
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
        return {"cell": cell["cell_id"], "status": "failure", "total": None, "path": str(failure_path_for(path)), "error": adapter.safe_error_message(error)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", choices=SCHEDULE_IDS)
    args = parser.parse_args()
    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    selected = tuple(args.only) if args.only else SCHEDULE_IDS
    adapter = load_adapter()
    summary = []
    for schedule_id in selected:
        for field in METADATA_FIELDS:
            path = path_for(schedule_id, field)
            if path.exists():
                data = json.loads(path.read_text())
                summary.append({
                    "cell": f"{schedule_id}-P-{field.lower()}",
                    "status": "existing",
                    "total": data.get("total"),
                    "path": str(path),
                })
                continue
            summary.append(run_cell(adapter, schedule_id, field, path))
    print(json.dumps(summary, indent=2))
    return 1 if any(row["status"] == "failure" for row in summary) else 0


if __name__ == "__main__":
    raise SystemExit(main())
