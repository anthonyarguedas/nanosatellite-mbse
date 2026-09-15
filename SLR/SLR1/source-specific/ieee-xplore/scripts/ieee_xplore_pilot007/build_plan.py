#!/usr/bin/env python3
"""Build the IEEE Xplore Pilot 007 native-page investigation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
QUERIES_PATH = SCRIPT_DIR.parent / "ieee_xplore_pilot005" / "queries.py"
ADAPTER_SHA256 = "f033f6edd8c1096dfb90dda1983e327ee9409b2026f9f84232837bf32d3025ed"


def queries() -> Any:
    spec = importlib.util.spec_from_file_location("ieee_p005_queries", QUERIES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERIES_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(schedule_id: str, purpose: str) -> dict:
    query = queries().SCHEDULE[schedule_id]
    return {
        "event_id": f"records-{schedule_id}",
        "schedule_id": schedule_id,
        "mode": "complete",
        "purpose": purpose,
        "query": query,
        "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
        "query_characters": len(query),
        "year_start": 2011,
        "year_end": 2026,
        "output": f"records/{schedule_id}.json",
        "do_not_merge": True,
    }


def build() -> dict:
    return {
        "schema_version": "ieee-xplore-pilot-007-event-plan/v1",
        "source": "IEEE Xplore",
        "pilot": "007",
        "diagnostic_only": True,
        "do_not_merge": True,
        "pilot006_plan_commit": "3d06078",
        "adapter": {"version": "9", "sha256": ADAPTER_SHA256},
        "objective": (
            "Test the Pilot 006 rendered-state diagnosis that a strict page-size preference "
            "must not replace valid native pagination that already fits the caller's page bound."
        ),
        "controls": {
            "publication_year": "2011_2026_Year inclusive",
            "scope": "Documents",
            "access": "All Results",
            "sort": "Oldest",
            "preferred_page_size": 100,
            "max_pages": 20,
            "strict_passes": 2,
            "full_abstracts": False,
            "language": None,
            "publication_type": None,
            "date_added": None,
            "controlled_vocabulary": None,
        },
        "repair_contract": [
            "Keep the current validated native page size when it can exhaust the exact total within max_pages.",
            "Use the preferred page-size control only when current native pagination cannot fit the bound.",
            "Require both strict passes to reconcile total, semantic controls, contiguous pages, ordered Article Numbers, and normalized export.",
            "Persist the compact strict receipt and each pass's native page size and year representation.",
        ],
        "acceptance_checks": [
            "BG2 and BC1 recover from their Pilot 006 rendered-state failures.",
            "B2 captures all 131 records through contiguous native pages in both strict passes.",
            "Every artifact has a valid terminal marker and compact strict receipt.",
            "No event changes a query, date window, source scope, access state, or result refinement.",
        ],
        "events": [
            event(
                "BG2",
                "Repeat the failed Pilot 006 BG2 strict event with workable native paging retained.",
            ),
            event(
                "BC1",
                "Repeat the failed Pilot 006 BC1 strict event with workable native paging retained.",
            ),
            event(
                "B2",
                "Test the historical over-100 partition through complete contiguous native pagination.",
            ),
        ],
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
