#!/usr/bin/env python3
"""Build the predeclared Wiley Pilot 004 schedule and wildcard plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from queries import (
    LITERAL_CELLS,
    PROTOCOL_COMMIT,
    SCHEDULE_IDS,
    SOURCE_QUERY_LIMIT,
    WILDCARD_CELLS,
    WILDCARD_REPLACEMENTS,
    wildcard_population_atoms,
)

PILOT = "004"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
SCHEMA = "wiley-online-library-pilot004-event-plan/v1"
ADAPTER_MIN_VERSION = 12
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific" / "wiley-online-library" / "pilots" / PILOT
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.name
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def event(variant: str, partition_id: str, cell: dict[str, str]) -> dict[str, Any]:
    cell_id = cell["cell_id"]
    event_id = f"{variant}-{partition_id}-{cell_id}"
    output = f"events/{event_id}.json"
    query = cell["query"]
    return {
        "event_id": event_id,
        "variant": variant,
        "partition_id": partition_id,
        "cell_id": cell_id,
        "branch": cell["branch"],
        "query": query,
        "query_characters": len(query),
        "query_sha256": digest_text(query),
        "output": output,
        "screenshots": screenshot_names(output),
        "mode": "two_complete_rendered_doi_passes",
        "diagnostic_only": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    events = []
    for variant, cells in (("literal", LITERAL_CELLS), ("wildcard", WILDCARD_CELLS)):
        for partition_id in SCHEDULE_IDS:
            events.extend(event(variant, partition_id, cell) for cell in cells[partition_id])

    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": {"id": "wiley_online_library", "label": "Wiley Online Library"},
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Run the current nine-partition schedule without proximity or pair expansion, "
            "then compare every literal partition union with the same schedule using the "
            "three previously tested trailing-wildcard population atoms."
        ),
        "adapter": {
            "id": "search_wiley_online_library",
            "minimum_version": ADAPTER_MIN_VERSION,
            "mandatory_automatic_screenshots": True,
            "screenshot_opt_out": False,
        },
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "inclusive": True,
            "source_control": "enclosing AfterMonth/AfterYear/BeforeMonth/BeforeYear",
            "exact_day_disposition": "visible First published",
        },
        "controls": {
            "source_route": "articlesChapters/default",
            "field": "one Anywhere/AllField row",
            "sort": "Date / sortBy=Earliest (observed newest-first)",
            "page_size": 20,
            "passes": 2,
            "max_source_total": 5000,
            "language": "not available and not applied",
            "publication_type": "articlesChapters record-family boundary only",
            "publication_type_facet": "not applied",
            "access": "not applied",
            "controlled_vocabulary": "not applied",
            "proximity": False,
            "pair_expansion": False,
            "native_ris": "not used in this diagnostic stable-ID comparison",
            "query_limit": SOURCE_QUERY_LIMIT,
            "literal_A1_exception": (
                "The 2770-character literal A1 is retained as the historically accepted "
                "comparison baseline. Every other submitted cell is at most 2700 characters."
            ),
        },
        "current_compound_blocks": {
            "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
            "G_structure": (
                "G_structure_fixed OR G_product_exact OR G_variation OR "
                "(G_product AND M_B)"
            ),
            "C1": "C1_fixed OR G_DSL",
            "BT2": "P AND M_B AND T_precise",
        },
        "cell_plan": {
            "A2": (
                "Lossless union of P AND E_F AND M_H and P AND E_F AND M_B. "
                "All other partitions use one direct expression."
            ),
            "union_operator": "OR with stable-ID deduplication",
            "result_driven_split": False,
        },
        "wildcard_candidate": {
            "operator": "documented unquoted trailing *",
            "replacements": [
                {"explicit_terms": list(terms), "candidate": candidate}
                for terms, candidate in WILDCARD_REPLACEMENTS
            ],
            "population_atoms_after_compression": list(wildcard_population_atoms()),
            "explicit_population_terms": 26,
            "candidate_population_atoms": len(wildcard_population_atoms()),
            "acceptance_rule": (
                "Adopt the candidate for every partition only if each complete wildcard "
                "union retains every literal stable ID, repeated event passes agree, and "
                "any wildcard-only records remain within the intended population meaning."
            ),
            "preference_rule": (
                "Prefer the shorter wildcard rendering after the acceptance rule passes."
            ),
        },
        "acceptance_checks": [
            "Every event has exact source query, date, route, page, and active-tab readback.",
            "Every event completes two identical ordered DOI passes from page zero.",
            "Every event saves one Advanced Search PNG and one first-results PNG beside its JSON.",
            "A2 literal and wildcard unions include both predeclared branches.",
            "Each wildcard partition union contains its complete literal partition union.",
            "Every wildcard-only record is inspected against the population meaning.",
            "No language, type-facet, access, vocabulary, proximity, or result-driven restriction is used.",
        ],
        "schedule_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA:
        errors.append("Plan schema changed")
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != 20:
        return [*errors, "Plan must contain twenty events"]
    expected = []
    for variant, cells in (("literal", LITERAL_CELLS), ("wildcard", WILDCARD_CELLS)):
        for partition_id in SCHEDULE_IDS:
            expected.extend(
                f"{variant}-{partition_id}-{cell['cell_id']}" for cell in cells[partition_id]
            )
    if [item.get("event_id") for item in events] != expected:
        errors.append("Event order or identity changed")
    for item in events:
        query = item.get("query")
        if not isinstance(query, str) or not query:
            errors.append(f"Missing query for {item.get('event_id')}")
            continue
        if item.get("query_characters") != len(query) or item.get("query_sha256") != digest_text(query):
            errors.append(f"Query receipt changed for {item.get('event_id')}")
        if "NEAR" in query.upper():
            errors.append(f"Proximity syntax in {item.get('event_id')}")
        if item.get("variant") == "literal" and ("*" in query or "?" in query):
            errors.append(f"Wildcard in literal event {item.get('event_id')}")
        if item.get("variant") == "wildcard" and "*" not in query:
            errors.append(f"Wildcard missing from {item.get('event_id')}")
        over_limit = len(query) > SOURCE_QUERY_LIMIT
        if over_limit and item.get("event_id") != "literal-A1-direct":
            errors.append(f"Over-limit query for {item.get('event_id')}")
        expected_shots = screenshot_names(item["output"])
        if item.get("screenshots") != expected_shots:
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
