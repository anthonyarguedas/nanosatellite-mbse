#!/usr/bin/env python3
"""Build the predeclared ATAI Pilot 008 wildcard comparison plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from queries import (
    FAMILY_COUNT,
    FAMILY_RECEIPTS,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    REPLACED_TERM_COUNT,
    SCHEDULE_IDS,
    TERM_COUNTS,
    TERM_SNAPSHOT_PATH,
    TERM_SNAPSHOT_SHA256,
    WILDCARD_OPERATOR_COUNT_BY_BLOCK,
    WILDCARD_SCHEDULE,
)

PILOT = "008"
SOURCE = "Advanced Technologies & Aerospace Index"
SOURCE_ID = "proquest_aerospace_index"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
QUERY_LIMIT = 50_000
SCHEMA = "atai-pilot-008-event-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PILOT_ROOT = (
    SLR1_DIR
    / "source-specific"
    / "advanced-technologies-aerospace-index"
    / "pilots"
    / PILOT
)
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.name
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def event(variant: str, schedule_id: str, query: str) -> dict[str, Any]:
    event_id = f"{variant}-{schedule_id}"
    output = f"events/{event_id}.json"
    return {
        "event_id": event_id,
        "schedule_id": schedule_id,
        "variant": variant,
        "purpose": (
            f"Strict complete two-pass {variant} capture for the {schedule_id} "
            "wildcard comparison."
        ),
        "query": query,
        "query_characters": len(query),
        "query_sha256": digest(query),
        "mode": "strict_complete_two_pass",
        "language": "English",
        "date_start": DATE_START,
        "date_end": DATE_END,
        "output": output,
        "screenshots": screenshot_names(output),
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    events = []
    for schedule_id in SCHEDULE_IDS:
        # Keep each comparison adjacent to reduce the chance that a source update
        # falls between its literal and wildcard observations.
        events.append(event("literal", schedule_id, LITERAL_SCHEDULE[schedule_id]))
        events.append(event("wildcard", schedule_id, WILDCARD_SCHEDULE[schedule_id]))

    literal_lengths = {key: len(value) for key, value in LITERAL_SCHEDULE.items()}
    wildcard_lengths = {key: len(value) for key, value in WILDCARD_SCHEDULE.items()}
    reductions = {
        key: literal_lengths[key] - wildcard_lengths[key] for key in SCHEDULE_IDS
    }
    wildcard_counts = {
        key: WILDCARD_SCHEDULE[key].count("[*") for key in SCHEDULE_IDS
    }
    if max((*literal_lengths.values(), *wildcard_lengths.values())) >= QUERY_LIMIT:
        raise RuntimeError("An ATAI Pilot 008 query reaches the validated source limit")

    return {
        "schema_version": SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "platform": "ProQuest",
        "pilot": PILOT,
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Compare complete literal and maximally bounded-wildcard translations of all "
            "nine post-proximity schedule partitions while preserving exact IF indexed terms."
        ),
        "adapter": {
            "id": "search_proquest_aerospace",
            "minimum_version": 6,
            "mandatory_automatic_screenshots": True,
            "screenshot_opt_out": False,
        },
        "term_snapshot": {
            "path": str(TERM_SNAPSHOT_PATH),
            "sha256": TERM_SNAPSHOT_SHA256,
            "term_counts": TERM_COUNTS,
        },
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "status": "labelled pilot window, not the unset common review cutoff",
            "basis": "Publication date",
            "inclusive": "both",
        },
        "controls": {
            "database": SOURCE,
            "language": "LA(English)",
            "publication_type": None,
            "peer_reviewed": False,
            "full_text": False,
            "access": False,
            "spelling_variants": False,
            "form_variants": False,
            "show_expansions": False,
            "sort": "DateAsc",
            "passes_per_event": 2,
            "proximity": False,
            "pair_expansion": False,
            "screenshots": (
                "required automatic search-page and results-page PNGs beside every JSON"
            ),
        },
        "translation": {
            "literal_atom": "(NOFT(quoted literal) OR IF.EXACT(quoted literal))",
            "wildcard_family_atom": (
                "NOFT(ordered phrase or token with the smallest bounded [*n]) OR every "
                "replaced IF.EXACT literal"
            ),
            "wildcard_scope": (
                "Every declared variant family with one common source stem. Singleton, "
                "punctuation, and unsafe-stem alternatives remain literal."
            ),
            "if_exact_policy": (
                "Keep every IF.EXACT literal explicit because NOFT does not cover IF and "
                "wildcards inside the exact indexed-term operator are not assumed."
            ),
            "compound_blocks": {
                "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
                "G_structure": (
                    "G_structure_fixed OR G_product_exact OR G_variation OR "
                    "(G_product AND M_B)"
                ),
                "C1": "C1_fixed OR G_DSL",
                "BT2": "P AND M_B AND T_precise",
            },
            "wildcard_family_count": FAMILY_COUNT,
            "replaced_literal_occurrence_count_across_blocks": REPLACED_TERM_COUNT,
            "wildcard_operators_by_block": WILDCARD_OPERATOR_COUNT_BY_BLOCK,
            "wildcard_families": FAMILY_RECEIPTS,
            "literal_query_lengths": literal_lengths,
            "wildcard_query_lengths": wildcard_lengths,
            "character_reductions": reductions,
            "wildcard_operators_by_partition": wildcard_counts,
            "literal_query_sha256": {
                key: digest(value) for key, value in LITERAL_SCHEDULE.items()
            },
            "wildcard_query_sha256": {
                key: digest(value) for key, value in WILDCARD_SCHEDULE.items()
            },
            "validated_character_limit": QUERY_LIMIT,
        },
        "acceptance_checks": [
            "Every event receives exact source query, database, date, language, variant, and sort readback.",
            "Every event completes the adapter's strict two-full-record-pass contract.",
            "Every event saves both mandatory sibling screenshots and matching JSON receipts.",
            "Every wildcard partition contains every stable ID from its fresh adjacent literal partition.",
            "Every wildcard-only record is inspected against the intended concept before adoption.",
            "No proximity, pair expansion, result-driven split, type, access, or vocabulary restriction is introduced.",
        ],
        "schedule_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = payload.get("events")
    if payload.get("schema_version") != SCHEMA:
        errors.append("Plan schema changed")
    if not isinstance(events, list) or len(events) != 18:
        return [*errors, "Plan must contain eighteen events"]
    expected_ids = [
        f"{variant}-{partition}"
        for partition in SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    ]
    if [item.get("event_id") for item in events] != expected_ids:
        errors.append("Event order or identity changed")
    for item in events:
        partition = item.get("schedule_id")
        variant = item.get("variant")
        schedule = LITERAL_SCHEDULE if variant == "literal" else WILDCARD_SCHEDULE
        query = item.get("query")
        if partition not in schedule or query != schedule[partition]:
            errors.append(f"Canonical query changed for {item.get('event_id')}")
            continue
        if item.get("query_sha256") != digest(query) or item.get("query_characters") != len(query):
            errors.append(f"Query receipt changed for {item.get('event_id')}")
        if "NEAR" in query.upper() or " PRE/" in query.upper():
            errors.append(f"Proximity syntax found for {item.get('event_id')}")
        if variant == "literal" and ("*" in query or "?" in query):
            errors.append(f"Wildcard found in literal event {item.get('event_id')}")
        if variant == "wildcard" and ("[*" not in query or "?" in query):
            errors.append(f"Bounded wildcard missing for {item.get('event_id')}")
        if len(query) >= QUERY_LIMIT:
            errors.append(f"Query reaches source limit for {item.get('event_id')}")
        if item.get("screenshots") != screenshot_names(item["output"]):
            errors.append(f"Screenshot names changed for {item.get('event_id')}")
    return errors


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        payload = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate(payload)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}, indent=2))
        return 1 if errors else 0
    payload = build()
    errors = validate(payload)
    if errors:
        raise RuntimeError("Generated plan is invalid: " + "; ".join(errors))
    write_create_only(args.output, payload)
    print(json.dumps({"saved": str(args.output), "events": len(payload["events"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
