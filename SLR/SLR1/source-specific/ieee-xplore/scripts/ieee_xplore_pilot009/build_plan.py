#!/usr/bin/env python3
"""Build the IEEE A2 literal transport-repair validation plan."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, quote_plus, urlencode

SCRIPT_DIR = Path(__file__).resolve().parent
QUERIES_PATH = SCRIPT_DIR.parent / "ieee_xplore_pilot005" / "queries.py"
ADAPTER_SHA256 = "c185c7609300e2ed91d975e4939cc1ddf493f2fa58978038d8b40d3bc624575b"
SEARCH_PATH = "/search/searchresult.jsp"


def load_queries() -> Any:
    spec = importlib.util.spec_from_file_location("ieee_p009_queries", QUERIES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERIES_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def request_target_bytes(query: str, *, compact: bool) -> int:
    parameters = [("newsearch", "true"), ("queryText", query)]
    encoded = urlencode(
        parameters,
        quote_via=quote_plus if compact else quote,
        safe="()" if compact else "",
    )
    return len(f"{SEARCH_PATH}?{encoded}".encode("ascii"))


def build() -> dict[str, Any]:
    query = load_queries().SCHEDULE["A2"]
    query_hash = digest(query)
    events = [
        {
            "event_id": f"count-A2-pass{number}",
            "schedule_id": "A2",
            "mode": "count",
            "purpose": (
                f"Adapter v10 compact-transport validation pass {number} for the "
                "unchanged literal A2 expression."
            ),
            "query": query,
            "query_sha256": query_hash,
            "query_characters": len(query),
            "year_start": 2011,
            "year_end": 2026,
            "output": f"counts/A2-pass{number}.json",
            "do_not_merge": True,
        }
        for number in (1, 2)
    ]
    return {
        "schema_version": "ieee-xplore-pilot-009-event-plan/v1",
        "source": "IEEE Xplore",
        "pilot": "009",
        "diagnostic_only": True,
        "do_not_merge": True,
        "adapter": {"version": "10", "sha256": ADAPTER_SHA256},
        "objective": (
            "Validate the adapter transport repair with two unchanged literal A2 "
            "count events and no wildcard or Boolean change."
        ),
        "query_identity": {
            "boolean_form": "P AND E_F AND (M_H OR M_B)",
            "characters": len(query),
            "sha256": query_hash,
            "matches_pilot008": True,
            "source_cells": 1,
            "wildcard_count": query.count("*") + query.count("?"),
        },
        "transport": {
            "former_percent_request_target_bytes": request_target_bytes(
                query, compact=False
            ),
            "repaired_compact_request_target_bytes": request_target_bytes(
                query, compact=True
            ),
            "validated_request_target_bound_bytes": 7800,
            "decoded_query_changed": False,
            "parameter_order_changed": False,
        },
        "controls": {
            "publication_year": "2011_2026_Year inclusive",
            "scope": "Documents",
            "access": "All Results",
            "sort": "Oldest",
            "language": None,
            "publication_type": None,
            "date_added": None,
            "controlled_vocabulary": None,
            "wildcard": False,
            "proximity": False,
            "count_only": True,
        },
        "acceptance_checks": [
            "Both events use the exact Pilot 008 A2 query hash.",
            "The query contains no wildcard and remains one source expression.",
            "Both events expose exact rendered query echo and an integer source total.",
            "Both native-Year totals agree.",
            "No split, filter, controlled term, or Boolean change is introduced.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        if json.loads(args.output.read_text()) != value:
            raise FileExistsError(f"Refusing to overwrite nonidentical plan {args.output}")
        return 0
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
