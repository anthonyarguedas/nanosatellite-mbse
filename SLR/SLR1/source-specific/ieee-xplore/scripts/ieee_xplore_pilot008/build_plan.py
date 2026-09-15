#!/usr/bin/env python3
"""Build the unchanged direct A2 readiness retest."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
QUERIES_PATH = SCRIPT_DIR.parent / "ieee_xplore_pilot005" / "queries.py"
ADAPTER_SHA256 = "0b47f673fe6652b511e240025ba5934d6993d0f636d7cc66ff83cbf7e9b3e225"


def queries() -> Any:
    spec = importlib.util.spec_from_file_location("ieee_p005_queries", QUERIES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERIES_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build() -> dict:
    query = queries().SCHEDULE["A2"]
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    events = [
        {
            "event_id": f"count-A2-pass{number}",
            "schedule_id": "A2",
            "mode": "count",
            "purpose": (
                f"Unchanged direct A2 initial-readiness retest pass {number}. "
                "No query split or source narrowing."
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
        "schema_version": "ieee-xplore-pilot-008-event-plan/v1",
        "source": "IEEE Xplore",
        "pilot": "008",
        "diagnostic_only": True,
        "do_not_merge": True,
        "adapter": {"version": "9", "sha256": ADAPTER_SHA256},
        "objective": (
            "Retest the exact unchanged direct A2 expression twice and determine whether "
            "the initial rendered result page now reaches a stable source total."
        ),
        "query_identity": {
            "boolean_form": "P AND E_F AND (M_H OR M_B)",
            "characters": len(query),
            "sha256": query_hash,
            "matches_pilot005": True,
            "source_cells": 1,
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
            "Both events use the exact Pilot 005 A2 query hash.",
            "Both initial result pages expose exact query echo, stable summary, cards, sort, and source total.",
            "Both native-Year totals agree.",
            "No query split, retry, wildcard, filter, or result-driven restriction is introduced.",
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
