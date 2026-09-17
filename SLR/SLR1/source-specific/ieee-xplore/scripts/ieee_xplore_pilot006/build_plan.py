#!/usr/bin/env python3
"""Build the predeclared IEEE Xplore Pilot 006 failure investigation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PILOT005_QUERIES = SCRIPT_DIR.parent / "ieee_xplore_pilot005" / "queries.py"
BASELINE_ADAPTER_SHA256 = "dbb78f58b939bd52704b28996eed0c8308bcaa0ed0afc85f17cc66d17661b9e1"
YEAR_START = 2011
YEAR_END = 2026


def load_queries() -> Any:
    spec = importlib.util.spec_from_file_location("ieee_p005_queries", PILOT005_QUERIES)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {PILOT005_QUERIES}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def event(event_id: str, schedule_id: str, mode: str, output: str, purpose: str) -> dict:
    query = load_queries().SCHEDULE[schedule_id]
    return {
        "event_id": event_id,
        "schedule_id": schedule_id,
        "mode": mode,
        "purpose": purpose,
        "query": query,
        "query_sha256": digest(query),
        "query_characters": len(query),
        "year_start": YEAR_START,
        "year_end": YEAR_END,
        "output": output,
        "do_not_merge": True,
    }


def build() -> dict:
    events = [
        event(
            "count-A1-pass1",
            "A1",
            "count",
            "counts/A1-pass1.json",
            "Repeat the A1 native-Year event that reset or lost rendered state in Pilot 005.",
        ),
        event(
            "count-A1-pass2",
            "A1",
            "count",
            "counts/A1-pass2.json",
            "Independently repeat A1 to distinguish a transient rendered failure from stable behavior.",
        ),
        event(
            "count-B1",
            "B1",
            "count",
            "counts/B1.json",
            "Investigate the Pilot 005 native start-year reset.",
        ),
        event(
            "count-BG2",
            "BG2",
            "count",
            "counts/BG2.json",
            "Investigate the Pilot 005 native start-year reset for a changed partition.",
        ),
        event(
            "count-BC1",
            "BC1",
            "count",
            "counts/BC1.json",
            "Investigate the Pilot 005 disabled Apply state after both requested years read back.",
        ),
        event(
            "count-BT2",
            "BT2",
            "count",
            "counts/BT2.json",
            "Investigate the Pilot 005 native start-year reset for a changed partition.",
        ),
        event(
            "records-BG1",
            "BG1",
            "complete",
            "records/BG1.json",
            "Test strict reconciliation when two passes use equivalent exact-token and contained-result-range evidence.",
        ),
        event(
            "records-BG2",
            "BG2",
            "complete",
            "records/BG2.json",
            "Test strict capture after the contained-result-range year repair.",
        ),
        event(
            "records-BC1",
            "BC1",
            "complete",
            "records/BC1.json",
            "Test strict capture after the disabled no-op Apply repair.",
        ),
        event(
            "records-BT2",
            "BT2",
            "complete",
            "records/BT2.json",
            "Test strict capture after the contained-result-range year repair.",
        ),
    ]
    return {
        "schema_version": "ieee-xplore-pilot-006-event-plan/v1",
        "source": "IEEE Xplore",
        "pilot": "006",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": "3194156e90497186664260a8e86435e78d2e2aa1",
        "pilot005_commit": "9ec7508b0bbd0ce7d499e48b53ce3dfa23f37ad4",
        "baseline_adapter": {
            "version": "8",
            "sha256": BASELINE_ADAPTER_SHA256,
        },
        "objective": (
            "Determine whether Pilot 005 year failures are no-op range interactions and "
            "whether its BG1 strict failure is an equivalent-readback reconciliation defect."
        ),
        "hypotheses": {
            "year_fill_reset": (
                "The visible Year widget already describes the complete result interval. "
                "When that interval lies inside 2011 through 2026, a broader input is a no-op."
            ),
            "disabled_apply": (
                "Apply stays disabled when the requested bounds do not narrow the current result interval."
            ),
            "strict_rendered_state": (
                "The first pass can expose a contained result interval after Apply while the explicit "
                "verification route exposes the exact requested token. Both independently prove the same window."
            ),
            "a1_rendered_state": (
                "The one A1 rendered-state event was transient if two unchanged repaired events reconcile."
            ),
        },
        "repair_contract": [
            "Skip Year input and Apply only when one visible disabled Year widget reports a complete interval contained in the requested inclusive window.",
            "Record the requested window and contained result interval separately.",
            "Keep uncontained intervals, enabled staged controls, changed native tokens, and ambiguous controls fatal.",
            "Reconcile strict controls by semantic requested values after each pass independently validates its native year evidence.",
            "Keep totals and stable IDs null on every remaining failure.",
        ],
        "controls": {
            "publication_year": "2011_2026_Year inclusive",
            "diagnostic_cutoff": "2026-08-29 recorded separately",
            "scope": "Documents",
            "access": "All Results",
            "sort": "Oldest",
            "language": None,
            "publication_type": None,
            "date_added": None,
            "controlled_vocabulary": None,
            "wildcard": False,
            "proximity": False,
            "strict_passes": 2,
            "full_abstracts": False,
            "full_abstract_reason": "Isolate rendered control, pagination, and stable-ID behavior.",
        },
        "acceptance_checks": [
            "Both A1 counts complete with equal totals and valid year evidence.",
            "B1, BG2, BC1, and BT2 complete without forcing or clicking a no-op Year control.",
            "All four changed partitions pass two strict rendered stable-ID traversals.",
            "At least one strict event reconciles different native year representations for one requested window.",
            "No repair accepts an uncontained interval, enabled staged control, or changed native token.",
            "No source event is retried or merged into the review baseline.",
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
        existing = json.loads(args.output.read_text())
        if existing != value:
            raise FileExistsError(f"Refusing to overwrite nonidentical plan {args.output}")
        return 0
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
