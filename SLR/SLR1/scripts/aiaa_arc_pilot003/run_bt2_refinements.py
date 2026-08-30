#!/usr/bin/env python3
"""Run BT2's 3-by-3 P/M_B field assignments with lossless T2 OR subcells."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from queries import (
    BLOCKS,
    METADATA_FIELDS,
    T2_PAIRS,
    T2_SUBBLOCKS,
    semantic_query,
)
from run_fielded_count import load_adapter, write_full_json
from run_stage1 import DATE_END, DATE_START, SEARCH_DIR, write_failure


def path_for(population_field: str, defining_field: str, index: int, retry: int | None = None) -> Path:
    stem = f"BT2-P-{population_field.lower()}-MB-{defining_field.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}"
    if retry is not None:
        stem += f"-retry{retry}"
    return SEARCH_DIR / f"{stem}.json"


def failure_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE{path.suffix}")


def run_cell(adapter, population_field: str, defining_field: str, index: int, path: Path, retry_of: Path | None = None) -> dict:
    t2_subblock = T2_SUBBLOCKS[index]
    pair_start = index * 56 + 1
    pair_end = pair_start + 55
    rows = (
        (population_field, BLOCKS["P"]),
        (defining_field, BLOCKS["M_B"]),
        ("Anywhere", t2_subblock),
    )
    cell = {
        "pilot": "003",
        "stage": "metadata_population_and_defining_block_3_by_3_t2_or_subcell",
        "schedule_id": "BT2",
        "cell_id": f"BT2-P-{population_field.lower()}-MB-{defining_field.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}",
        "semantic_query": semantic_query("BT2"),
        "population_block": "P",
        "population_field": population_field,
        "defining_block": "M_B",
        "defining_field": defining_field,
        "third_block": "T2",
        "third_field": "Anywhere",
        "split_kind": "disjoint_OR_alternatives",
        "pair_ordinal_range": [pair_start, pair_end],
        "pair_count": 56,
        "subcell_pair_literals": list(T2_PAIRS[index * 56:(index + 1) * 56]),
        "same_field_pair_semantics": "Every declared T2 pair remains wholly inside the Anywhere row; two same-named P/M_B advanced rows, when applicable, are conjunctive.",
        "union_coverage_claim": "The 3-by-3 P/M_B assignments combined with the four disjoint T2 OR subcells cover the full BT2 semantic query. The summed total is only an upper bound.",
        "retry_of": retry_of.name if retry_of is not None else None,
    }
    try:
        result = adapter.search_aiaa_arc(
            None,
            field_rows=tuple(adapter.FieldRow(name, text) for name, text in rows),
            date_start=date.fromisoformat(DATE_START),
            date_end=date.fromisoformat(DATE_END),
            count_only=True,
            timeout_seconds=60.0,
            page_delay_seconds=1.0,
            cdp_url=os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL),
        )
        metadata = result.get("output_metadata", {})
        expected_rows = [
            {"field": adapter.normalize_arc_field(name), "label": adapter.ARC_FIELD_LABELS[adapter.normalize_arc_field(name)], "text": text}
            for name, text in rows
        ]
        if metadata.get("field_rows") != expected_rows:
            raise RuntimeError("ARC field-row readback did not preserve this BT2 3-by-3 subcell")
        if not (
            metadata.get("count_only") is True
            and metadata.get("observed_exact_query_echo") is True
            and metadata.get("exact_date_controls_proven") is True
            and metadata.get("language_filter") is None
            and metadata.get("publication_type_filter") is None
            and isinstance(result.get("total"), int)
            and result["total"] >= 0
        ):
            raise RuntimeError("ARC BT2 3-by-3 subcell lacked required exact control evidence")
        result.update(
            {
                "diagnostic_kind": "NON_MERGEABLE_FIELD_ASSIGNMENT_COUNT_ONLY",
                "diagnostic_mode": "count_only",
                "private_diagnostic": True,
                "do_not_merge": True,
                "merge_eligible": False,
                "publication_state": "count_only_diagnostic",
                "reason": "ARC count-only BT2 3-by-3 T2 OR-subcell; normalized records were intentionally omitted",
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
        return {"cell": cell["cell_id"], "status": "failure", "total": None, "path": str(failure_path(path)), "error": adapter.safe_error_message(error)}


def choose_attempt(population_field: str, defining_field: str, index: int, retry_failed: bool) -> tuple[Path | None, Path | None, dict | None]:
    original = path_for(population_field, defining_field, index)
    if original.exists():
        return None, None, {"cell": original.stem, "status": "existing", "total": json.loads(original.read_text()).get("total"), "path": str(original)}
    prior_failure = failure_path(original)
    if not prior_failure.exists():
        return original, None, None
    if not retry_failed:
        return None, None, {"cell": original.stem, "status": "prior_failure", "total": None, "path": str(prior_failure)}
    for attempt in range(1, 4):
        candidate = path_for(population_field, defining_field, index, retry=attempt)
        candidate_failure = failure_path(candidate)
        if candidate.exists():
            return None, None, {"cell": candidate.stem, "status": "existing_retry", "total": json.loads(candidate.read_text()).get("total"), "path": str(candidate)}
        if candidate_failure.exists():
            prior_failure = candidate_failure
            continue
        return candidate, prior_failure, None
    return None, None, {"cell": original.stem, "status": "retry_limit_reached", "total": None, "path": str(prior_failure)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population-field", nargs="*", choices=METADATA_FIELDS)
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    fields = tuple(args.population_field) if args.population_field else METADATA_FIELDS
    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    adapter = load_adapter()
    summary = []
    for population_field in fields:
        for defining_field in METADATA_FIELDS:
            for index in range(len(T2_SUBBLOCKS)):
                path, retry_of, existing = choose_attempt(population_field, defining_field, index, args.retry_failed)
                if existing is not None:
                    summary.append(existing)
                else:
                    assert path is not None
                    summary.append(run_cell(adapter, population_field, defining_field, index, path, retry_of))
    print(json.dumps(summary, indent=2))
    return 1 if any(row["status"] == "failure" for row in summary) else 0


if __name__ == "__main__":
    raise SystemExit(main())
