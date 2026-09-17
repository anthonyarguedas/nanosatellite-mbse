#!/usr/bin/env python3
"""Run the Scopus CLI while printing ID-free strict-pass predicate diagnostics."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("search_scopus_pilot016_debug", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    adapter = load_adapter()
    original = adapter._scopus_pass_is_complete

    def traced(observation: Any) -> bool:
        stable_ids = observation.ordered_stable_ids
        checks = {
            "stopped_reason": observation.stopped_reason,
            "stopped_reason_valid": observation.stopped_reason
            in {"all_available_records", "zero_results"},
            "total": observation.total,
            "pages_retrieved": observation.pages_retrieved,
            "source_entries_retrieved": observation.source_entries_retrieved,
            "stable_id_count": len(stable_ids),
            "unique_stable_id_count": len(set(stable_ids)),
            "record_count": len(observation.records),
            "expected_page_count": observation.expected_page_count,
            "page_size": observation.page_size,
            "scope_id": observation.scope_id,
            "sort_value": observation.sort_value,
            "native_query_present": bool(
                isinstance(observation.native_query, str)
                and observation.native_query.strip()
            ),
            "native_query_sha256": (
                hashlib.sha256(observation.native_query.encode("utf-8")).hexdigest()
                if isinstance(observation.native_query, str)
                else None
            ),
        }
        checks["original_result"] = original(observation)
        print(
            "SCOPUS_STRICT_PREDICATE_DIAGNOSTIC="
            + json.dumps(checks, sort_keys=True),
            file=sys.stderr,
            flush=True,
        )
        return checks["original_result"]

    adapter._scopus_pass_is_complete = traced
    return adapter.main()


if __name__ == "__main__":
    raise SystemExit(main())
