#!/usr/bin/env python3
"""Reduce repetitive adapter diagnostics while retaining every fielded-cell control."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from run_fielded_count import load_adapter
from run_stage1 import SEARCH_DIR

# These fields are the source evidence needed to reproduce/audit a count cell.
KEEP = (
    "source",
    "source_endpoint",
    "access_method",
    "query_submission",
    "search_url_controls_proven",
    "observed_exact_query_echo",
    "executed_query",
    "exact_date_controls_proven",
    "search_scope",
    "query_field",
    "field_rows",
    "executed_clauses",
    "access_choice",
    "result_facets",
    "request_method",
    "language_filter",
    "publication_type_filter",
    "venue_filter",
    "open_access_filter",
    "export_method",
    "extracted_at",
    "requested_limit",
    "max_pages",
    "page_size",
    "page_size_evidence",
    "sort_native_value",
    "sort",
    "sort_evidence",
    "passes_requested",
    "passes_completed",
    "ordered_doi_passes_reconciled",
    "portal_total",
    "total_is_exact",
    "count_only",
    "retrieval_complete",
    "verification_scope",
    "status",
    "control_readback",
    "date_input_mode",
    "date_start",
    "date_end",
    "source_month_start",
    "source_month_end",
    "date_filter_mode",
    "total_scope",
    "browser_page_ownership",
    "visible_owned_browser",
    "complete_run_visibility",
    "require_complete",
    "publication_contract",
    "execution_completion_status",
    "fielded_count_artifact_schema",
    "records_omitted_for_diagnostic",
)
TOP_KEEP = (
    "query",
    "requested_query",
    "schema_version",
    "source",
    "executed_query",
    "total",
    "pages_retrieved",
    "results_retrieved",
    "results",
    "do_not_merge",
    "diagnostic_kind",
    "diagnostic_mode",
    "private_diagnostic",
    "merge_eligible",
    "publication_state",
    "reason",
    "normalized_results_omitted",
    "normalized_csv_omitted",
    "native_export_omitted",
    "pilot_cell",
)


def replace_json(path: Path, payload: dict) -> None:
    descriptor, raw = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    adapter = load_adapter()
    compacted = 0
    for path in sorted(SEARCH_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        metadata = data.get("output_metadata")
        if not isinstance(metadata, dict) or metadata.get("fielded_count_artifact_schema") != "aiaa-arc-fielded-count/v1":
            continue
        # The shared compact result keeps the normalized count/PRISMA receipt;
        # restore the exact ARC field rows and verified controls that a generic
        # compact receipt deliberately omits.
        compact = adapter.compact_search_result_for_output(data)
        compact_metadata = compact.setdefault("output_metadata", {})
        for key in KEEP:
            if key in metadata:
                compact_metadata[key] = metadata[key]
        compact_metadata["fielded_count_projection"] = {
            "schema": "aiaa-arc-fielded-count-projection/v1",
            "preserved": ["exact_field_rows", "source_control_readback", "exact_date_controls", "source_total", "count_status"],
            "omitted_repetitive_adapter_diagnostics": ["topic_taxonomy", "semantic_validation", "search_log", "execution_ledger", "full_prisma_receipt"],
        }
        for key in TOP_KEEP:
            if key in data:
                compact[key] = data[key]
        compact["results"] = []
        compact["do_not_merge"] = True
        replace_json(path, compact)
        compacted += 1
    print(json.dumps({"compacted_fielded_count_artifacts": compacted}, indent=2))


if __name__ == "__main__":
    main()
