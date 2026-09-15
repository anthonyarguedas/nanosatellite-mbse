#!/usr/bin/env python3
"""Build the triggered ARC ordered-phrase behavior checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from queries import P_TERMS, PROTOCOL_COMMIT, all_of, literal, ordinary_block

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
KNOWN_DOI = "10.2514/6.2015-4474"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def event(event_id: str, purpose: str, rows: list[dict[str, str]]) -> dict:
    serialized = " AND ".join(f"{row['field']}={row['text']}" for row in rows)
    return {
        "event_id": event_id,
        "schedule_id": "phrase_diagnostic",
        "purpose": purpose,
        "query": serialized,
        "query_characters": len(serialized),
        "query_sha256": digest(serialized),
        "field_rows": [
            {
                "field": row["field"],
                "source_field": "AllField" if row["field"] == "Anywhere" else row["field"],
                "text": row["text"],
            }
            for row in rows
        ],
        "mode": "count",
        "output": f"searches/phrase-checks/{event_id.removeprefix('phrase-')}.json",
        "do_not_merge": True,
    }


def title_event(event_id: str, purpose: str, title_query: str) -> dict:
    return event(
        event_id,
        purpose,
        [
            {"field": "Anywhere", "text": literal(KNOWN_DOI)},
            {"field": "Title", "text": title_query},
        ],
    )


def build(parent_artifact: Path) -> dict:
    parent_total = json.loads(parent_artifact.read_text()).get("total")
    if parent_total != 3_536:
        raise RuntimeError(f"Expected P AND quoted reference architecture total 3536, got {parent_total!r}")
    population = ordinary_block(P_TERMS)
    events = [
        event(
            "phrase-anywhere-reference-architecture-repeat",
            "Repeat the dominant quoted two-word literal.",
            [{"field": "Anywhere", "text": all_of(population, literal("reference architecture"))}],
        ),
        event(
            "phrase-anywhere-reference-and-architecture",
            "Compare the quoted phrase with an explicit conjunction of its component words.",
            [{
                "field": "Anywhere",
                "text": all_of(population, all_of(literal("reference"), literal("architecture"))),
            }],
        ),
        event(
            "phrase-anywhere-architecture-reference",
            "Test the reversed quoted phrase against the same population block.",
            [{"field": "Anywhere", "text": all_of(population, literal("architecture reference"))}],
        ),
        title_event(
            "phrase-title-contiguous-cubesat-model",
            "Positive control for a contiguous ordered phrase in the known title.",
            literal("CubeSat Model"),
        ),
        title_event(
            "phrase-title-contiguous-reference-model",
            "Second positive control for a contiguous ordered phrase in the known title.",
            literal("Reference Model"),
        ),
        title_event(
            "phrase-title-noncontiguous-cubesat-reference",
            "Negative control with the title words in source order but separated by other words.",
            literal("CubeSat Reference"),
        ),
        title_event(
            "phrase-title-reversed-reference-cubesat",
            "Negative control with separated title words in reverse order.",
            literal("Reference CubeSat"),
        ),
        title_event(
            "phrase-title-cubesat-and-reference",
            "Explicit component-word conjunction control for the same noncontiguous title words.",
            all_of(literal("CubeSat"), literal("Reference")),
        ),
    ]
    return {
        "schema_version": "aiaa-arc-pilot005-phrase-event-plan/v1",
        "source": SOURCE,
        "pilot": "005",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "trigger": {
            "observation": "P AND quoted reference architecture returned 3536 records.",
            "reason": "Validate that straight double quotes still implement the protocol's ordered-phrase requirement.",
        },
        "date_window": {"requested_start": DATE_START, "requested_end": DATE_END},
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "wildcard": False,
            "proximity": False,
        },
        "known_title": "CubeSat Model Based System Engineering (MBSE) Reference Model - Application in the Concept Lifecycle Phase",
        "expected_if_quotes_are_ordered_phrases": {
            "phrase-title-contiguous-cubesat-model": 1,
            "phrase-title-contiguous-reference-model": 1,
            "phrase-title-noncontiguous-cubesat-reference": 0,
            "phrase-title-reversed-reference-cubesat": 0,
            "phrase-title-cubesat-and-reference": 1,
        },
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.parent_artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
