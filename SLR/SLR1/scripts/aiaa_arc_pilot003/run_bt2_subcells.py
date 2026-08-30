#!/usr/bin/env python3
"""Run BT2's lossless T2 OR-subcells after the full T2 row timed out."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from queries import (
    BLOCKS,
    METADATA_FIELDS,
    T2_PAIRS,
    T2_SUBBLOCKS,
    and_blocks,
    semantic_query,
)
from run_fielded_count import load_adapter, write_full_json
from run_stage1 import DATE_END, DATE_START, SEARCH_DIR, write_failure


def path_for(field: str, index: int) -> Path:
    return SEARCH_DIR / f"BT2-P-{field.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}.json"


def run_cell(adapter, field: str, index: int, path: Path) -> dict:
    t2_subblock = T2_SUBBLOCKS[index]
    pair_start = index * 56 + 1
    pair_end = pair_start + 55
    rows = ((field, BLOCKS["P"]), ("Anywhere", and_blocks(BLOCKS["M_B"], t2_subblock)))
    cell = {
        "pilot": "003",
        "stage": "metadata_population_field_union_lossless_t2_or_subcell",
        "schedule_id": "BT2",
        "cell_id": f"BT2-P-{field.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}",
        "parent_cell": f"BT2-P-{field.lower()}",
        "semantic_query": semantic_query("BT2"),
        "population_block": "P",
        "population_field": field,
        "remainder_field": "Anywhere",
        "fixed_remainder_block": "M_B",
        "split_block": "T2",
        "split_kind": "disjoint_OR_alternatives",
        "pair_ordinal_range": [pair_start, pair_end],
        "pair_count": 56,
        "subcell_pair_literals": list(T2_PAIRS[index * 56:(index + 1) * 56]),
        "union_restoration": "OR across T2-01-of-04 through T2-04-of-04 restores every one of the 224 declared T2 pairs exactly once.",
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
        expected_rows = [
            {"field": adapter.normalize_arc_field(name), "label": adapter.ARC_FIELD_LABELS[adapter.normalize_arc_field(name)], "text": text}
            for name, text in rows
        ]
        if metadata.get("field_rows") != expected_rows:
            raise RuntimeError("ARC field-row readback did not preserve this T2 subcell")
        if not (
            metadata.get("count_only") is True
            and metadata.get("observed_exact_query_echo") is True
            and metadata.get("exact_date_controls_proven") is True
            and metadata.get("language_filter") is None
            and metadata.get("publication_type_filter") is None
            and isinstance(result.get("total"), int)
            and result["total"] >= 0
        ):
            raise RuntimeError("ARC T2 subcell lacked required exact control evidence")
        result.update(
            {
                "diagnostic_kind": "NON_MERGEABLE_FIELD_ASSIGNMENT_COUNT_ONLY",
                "diagnostic_mode": "count_only",
                "private_diagnostic": True,
                "do_not_merge": True,
                "merge_eligible": False,
                "publication_state": "count_only_diagnostic",
                "reason": "ARC count-only fielded T2 OR-subcell; normalized records were intentionally omitted",
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
    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    adapter = load_adapter()
    summary = []
    for field in METADATA_FIELDS:
        for index in range(len(T2_SUBBLOCKS)):
            path = path_for(field, index)
            if path.exists():
                summary.append({"cell": path.stem, "status": "existing", "total": json.loads(path.read_text()).get("total"), "path": str(path)})
            else:
                summary.append(run_cell(adapter, field, index, path))
    print(json.dumps(summary, indent=2))
    return 1 if any(row["status"] == "failure" for row in summary) else 0


if __name__ == "__main__":
    raise SystemExit(main())
