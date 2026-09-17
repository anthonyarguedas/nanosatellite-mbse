#!/usr/bin/env python3
"""Build the paired AIAA ARC Pilot 009 wildcard acceptance plan."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
PILOT007_SCRIPTS = ROOT / "source-specific" / "aiaa-arc" / "scripts" / "aiaa_arc_pilot007"
if str(PILOT007_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PILOT007_SCRIPTS))
PARENT_SPEC = importlib.util.spec_from_file_location(
    "aiaa_arc_pilot007_build_plan",
    PILOT007_SCRIPTS / "build_plan.py",
)
if PARENT_SPEC is None or PARENT_SPEC.loader is None:
    raise RuntimeError("Unable to load the Pilot 007 plan builder")
PARENT_MODULE = importlib.util.module_from_spec(PARENT_SPEC)
PARENT_SPEC.loader.exec_module(PARENT_MODULE)
build_pilot007_plan = PARENT_MODULE.build

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
LITERAL_FRAGMENT = '"nanosatellite" OR "nanosatellites"'
WILDCARD_FRAGMENT = "nanosatellit*"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def replace_population_fragment(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    replacements = 0
    output = []
    for row in rows:
        text = row["text"]
        count = text.count(LITERAL_FRAGMENT)
        replacements += count
        output.append({**row, "text": text.replace(LITERAL_FRAGMENT, WILDCARD_FRAGMENT)})
    if replacements != 1:
        raise RuntimeError(f"Expected one population replacement, observed {replacements}")
    return output


def serialized(rows: list[dict[str, str]]) -> str:
    return " AND ".join(f"{row['field']}={row['text']}" for row in rows)


def event(
    parent: dict[str, Any],
    variant: str,
    rows: list[dict[str, str]],
) -> dict[str, Any]:
    pair_id = parent["event_id"]
    event_id = f"{pair_id}-{variant}"
    query = serialized(rows)
    return {
        "event_id": event_id,
        "pair_id": pair_id,
        "partition": parent["partition"],
        "route": parent["route"],
        "variant": variant,
        "field_rows": rows,
        "serialized_query": query,
        "serialized_query_sha256": digest(query),
        "mode": "card_preview",
        "output": f"searches/cells/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/cells/{event_id}.search-page.png",
            "results_page": f"searches/cells/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    parent = build_pilot007_plan()
    parent_events = parent["events"]
    if len(parent_events) != 94:
        raise RuntimeError("Pilot 007 parent plan must contain 94 cells")
    events = []
    pair_ledger = []
    for source_event in parent_events:
        literal_rows = [dict(row) for row in source_event["field_rows"]]
        wildcard_rows = replace_population_fragment(literal_rows)
        literal_query = serialized(literal_rows)
        wildcard_query = serialized(wildcard_rows)
        if literal_query.count(LITERAL_FRAGMENT) != 1:
            raise RuntimeError("Literal pair does not contain exactly one target fragment")
        if WILDCARD_FRAGMENT in literal_query or LITERAL_FRAGMENT in wildcard_query:
            raise RuntimeError("Wildcard transformation did not remain isolated")
        if len(literal_query) - len(wildcard_query) != len(LITERAL_FRAGMENT) - len(WILDCARD_FRAGMENT):
            raise RuntimeError("Unexpected wildcard query-length change")
        events.append(event(source_event, "literal", literal_rows))
        events.append(event(source_event, "wildcard", wildcard_rows))
        pair_ledger.append({
            "pair_id": source_event["event_id"],
            "partition": source_event["partition"],
            "literal_event_id": f"{source_event['event_id']}-literal",
            "wildcard_event_id": f"{source_event['event_id']}-wildcard",
            "literal_query_sha256": digest(literal_query),
            "wildcard_query_sha256": digest(wildcard_query),
            "query_character_reduction": len(literal_query) - len(wildcard_query),
        })
    if len(events) != 188 or len({entry["event_id"] for entry in events}) != 188:
        raise RuntimeError("Pilot 009 must contain 188 unique paired events")
    pair_counts = {
        partition: sum(entry["partition"] == partition for entry in pair_ledger)
        for partition in PARTITIONS
    }
    if pair_counts != parent["translation"]["cell_counts"]:
        raise RuntimeError("Pilot 009 pair counts differ from Pilot 007")
    return {
        "schema_version": "aiaa-arc-pilot009-wildcard-plan/v1",
        "source": SOURCE,
        "pilot": "009",
        "protocol_commit": parent["protocol_commit"],
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test and prospectively accept one narrow trailing-wildcard compression by paired, "
            "complete stable-DOI comparison across every current Pilot 007 hybrid cell."
        ),
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_scope": "inclusive ARC months before exact-day exclusions",
        },
        "candidate": {
            "literal_fragment": LITERAL_FRAGMENT,
            "wildcard_fragment": WILDCARD_FRAGMENT,
            "replacement_scope": (
                "Replace only the two unhyphenated nanosatellite singular/plural literals inside P. "
                "Keep nanosat, hyphenated, spaced, CubeSat, SmallSat, and small-satellite forms literal."
            ),
            "wildcard_position": "unquoted trailing asterisk",
            "query_character_reduction_per_cell": len(LITERAL_FRAGMENT) - len(WILDCARD_FRAGMENT),
            "generation": "one exact text replacement per cell",
        },
        "parent_route": {
            "pilot": "007",
            "plan_schema": parent["schema_version"],
            "translation": parent["translation"],
            "parent_plan_sha256": digest(json.dumps(parent, sort_keys=True, separators=(",", ":"))),
        },
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "proximity": False,
        },
        "capture": {
            "mode": "non-mergeable rendered-card preview",
            "limit": 100,
            "max_pages": 5,
            "stable_identity": "canonical DOI before an ARC virtual-collection suffix",
            "automatic_screenshots_required": True,
        },
        "acceptance_checks": [
            "Every literal and wildcard event receives exact source-observed field-row readback.",
            "The paired query texts differ only by the one predeclared fragment replacement.",
            "Every source event remains at most 100 records and is captured completely.",
            "Every wildcard cell canonical DOI set is a superset of its paired literal cell set.",
            "Every literal partition union is a subset of its wildcard partition union.",
            "The complete literal schedule union is a subset of the complete wildcard schedule union.",
            "Every wildcard-only record remains in the prospective screening corpus.",
            "The wildcard schedule remains operationally feasible.",
            "Every successful JSON has both mandatory sibling screenshots.",
        ],
        "acceptance_boundary": {
            "accept_if_all_checks_pass": True,
            "accepted_syntax_if_passed": WILDCARD_FRAGMENT,
            "no_general_wildcard_permission": True,
            "future_source_revalidation_required": True,
            "final_search_status_unchanged": True,
        },
        "pair_count": len(pair_ledger),
        "event_count": len(events),
        "partition_pair_counts": pair_counts,
        "pair_ledger": pair_ledger,
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
