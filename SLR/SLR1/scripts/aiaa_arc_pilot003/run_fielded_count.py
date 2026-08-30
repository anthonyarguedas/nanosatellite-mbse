#!/usr/bin/env python3
"""Run one non-mergeable ARC fielded count-only cell through the shared adapter.

The current adapter CLI performs the browser search correctly for field-row-only
count-only runs, but then passes its empty raw-query alias to the generic receipt
writer.  This small pilot-only caller uses the adapter's public functions and
passes the adapter's displayed fielded query to that writer instead.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

ADAPTER_PATH = Path.home() / "agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("aiaa_arc_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_row(value: str) -> tuple[str, str]:
    field, separator, text = value.partition("=")
    if not separator or not field.strip() or not text.strip():
        raise argparse.ArgumentTypeError("field row must be FIELD=TEXT")
    return field.strip(), text.strip()


def write_full_json(path: Path, payload: dict[str, Any]) -> None:
    """Publish a full diagnostic receipt without the adapter's compact projection."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--field-row", action="append", type=parse_row, required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--date-start", default="2011-01-01")
    parser.add_argument("--date-end", default="2026-08-29")
    args = parser.parse_args()

    adapter = load_adapter()
    rows = tuple(adapter.FieldRow(field, text) for field, text in args.field_row)
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = adapter.search_aiaa_arc(
            None,
            field_rows=rows,
            date_start=date.fromisoformat(args.date_start),
            date_end=date.fromisoformat(args.date_end),
            count_only=True,
            cdp_url=os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL),
        )
        metadata = result["output_metadata"]
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
        write_full_json(output_path, result)
        print(f"saved={output_path}")
        print(f"total={result['total']}")
        return 0
    except Exception as error:  # noqa: BLE001 - preserve a record-free failure artifact.
        failure_path = output_path.with_name(
            f"{output_path.stem}.NON_MERGEABLE_FAILURE{output_path.suffix or '.json'}"
        )
        diagnostic = {
            "schema_version": "aiaa-arc-fielded-count/v1",
            "source": "AIAA Aerospace Research Central (ARC)",
            "requested_field_rows": [
                {"field": field, "text": text} for field, text in args.field_row
            ],
            "executed_query": None,
            "total": None,
            "results": [],
            "do_not_merge": True,
            "failure": {
                "error_type": type(error).__name__,
                "error": adapter.safe_error_message(error),
            },
        }
        write_full_json(failure_path, diagnostic)
        print(f"failure_saved={failure_path}")
        print(f"error={adapter.safe_error_message(error)}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
