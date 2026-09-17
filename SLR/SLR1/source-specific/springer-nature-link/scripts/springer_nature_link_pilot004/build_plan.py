#!/usr/bin/env python3
"""Build the predeclared Springer Pilot 004 schedule and wildcard plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from queries import (
    LITERAL_A2_CELLS,
    LITERAL_A2_MB_CHUNK_CELLS,
    LITERAL_B2_BOOLEAN_CELLS,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    SCHEDULE_IDS,
    WILDCARD_A2_CELLS,
    WILDCARD_A2_MB_CHUNK_CELLS,
    WILDCARD_B2_BOOLEAN_CELLS,
    WILDCARD_REPLACEMENTS,
    WILDCARD_SCHEDULE,
    wildcard_population_atoms,
)

PILOT = "004"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
LANGUAGE = "En"
SORT = "oldestFirst"
SCHEMA = "springer-nature-link-pilot004-event-plan/v1"
REVISED_SCHEMA = "springer-nature-link-pilot004-event-plan/v2"
STABLE_PAGINATION_SCHEMA = "springer-nature-link-pilot004-event-plan/v3"
YEAR_PARTITION_SCHEMA = "springer-nature-link-pilot004-event-plan/v4"
SNAPSHOT_RETEST_SCHEMA = "springer-nature-link-pilot004-snapshot-retest-plan/v1"
ADAPTER_MIN_VERSION = 10
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific" / "springer-nature-link" / "pilots" / PILOT
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.name
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def event(variant: str, partition_id: str, query: str) -> dict[str, Any]:
    event_id = f"{variant}-{partition_id}"
    output = f"events/{event_id}.json"
    return {
        "event_id": event_id,
        "variant": variant,
        "partition_id": partition_id,
        "query": query,
        "query_characters": len(query),
        "query_sha256": digest_text(query),
        "output": output,
        "screenshots": screenshot_names(output),
        "mode": "two_complete_rendered_card_path_passes",
        "diagnostic_only": True,
        "do_not_merge": True,
    }


def cell_event(
    variant: str,
    partition_id: str,
    cell: dict[str, str],
) -> dict[str, Any]:
    item = event(variant, partition_id, cell["query"])
    item["event_id"] = f"{variant}-{partition_id}-{cell['cell_id']}"
    item["cell_id"] = cell["cell_id"]
    item["branch"] = cell["branch"]
    item["output"] = f"events/{item['event_id']}.json"
    item["screenshots"] = screenshot_names(item["output"])
    return item


def year_event(
    variant: str,
    partition_id: str,
    query: str,
    year: int,
    *,
    cell_id: str = "direct",
    branch: str | None = None,
) -> dict[str, Any]:
    item = event(variant, partition_id, query)
    suffix = f"year-{year}" if cell_id == "direct" else f"year-{year}-{cell_id}"
    item["event_id"] = f"{variant}-{partition_id}-{suffix}"
    item["cell_id"] = cell_id
    item["branch"] = branch or partition_id
    item["source_year_start"] = year
    item["source_year_end"] = year
    item["output"] = f"events/{item['event_id']}.json"
    item["screenshots"] = screenshot_names(item["output"])
    return item


def build() -> dict[str, Any]:
    events = []
    for partition_id in SCHEDULE_IDS:
        events.append(event("literal", partition_id, LITERAL_SCHEDULE[partition_id]))
        events.append(event("wildcard", partition_id, WILDCARD_SCHEDULE[partition_id]))
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": {
            "id": "springer_nature_link",
            "label": "Springer Nature Link",
        },
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Run the current nine-partition schedule without proximity or pair "
            "expansion and compare complete literal and population-wildcard card-path "
            "ledgers for every partition."
        ),
        "adapter": {
            "id": "search_springer_link",
            "minimum_version": ADAPTER_MIN_VERSION,
            "mandatory_automatic_screenshots": True,
            "screenshot_opt_out": False,
            "cli_smoke_requested_output": (
                "adapter-smoke/automatic-screenshot-smoke.json"
            ),
            "cli_smoke_actual_output": (
                "adapter-smoke/automatic-screenshot-smoke.NON_MERGEABLE_DIAGNOSTIC.json"
            ),
        },
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "inclusive": True,
            "source_control": "inclusive Date published years 2011 through 2026",
            "pilot_ledger_scope": (
                "complete source-year card paths; exact-day disposition is diagnostic "
                "and does not remove a raw identity from wildcard comparison"
            ),
        },
        "controls": {
            "source_route": "whole Springer Nature Link platform",
            "field": "raw Keywords over title, abstract, and body text",
            "language": LANGUAGE,
            "sort": SORT,
            "page_size": 20,
            "passes": 2,
            "content_type": None,
            "access": None,
            "taxonomy": None,
            "discipline": None,
            "subdiscipline": None,
            "sdg": None,
            "book_accessibility": None,
            "controlled_vocabulary": None,
            "proximity": False,
            "pair_expansion": False,
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
                "Adopt the candidate in every partition only if each two-pass "
                "wildcard ledger contains every corresponding two-pass literal stable "
                "card path and every wildcard-only path remains within the intended "
                "population meaning. Prefer exact equality."
            ),
            "preference_rule": (
                "Prefer the shorter wildcard rendering after the acceptance rule passes."
            ),
        },
        "acceptance_checks": [
            "Every event has exact source query, years, language, sort, total, and page readback.",
            "Every event completes two full card-path passes from page one.",
            "Every event saves a configured Advanced Search PNG and hydrated first-results PNG beside its JSON.",
            "Every wildcard partition retains every literal stable card path.",
            "Every wildcard-only path is inspected against the population meaning.",
            "No type, access, taxonomy, vocabulary, proximity, pair, or result-driven restriction is used.",
        ],
        "adapter_smoke": {
            "query": '"10.1007/s42064-026-0306-8"',
            "expected_total": 1,
            "count_only": True,
            "passes": 2,
            "purpose": "prove the CLI has no screenshot opt-out and publishes both sibling PNGs",
        },
        "schedule_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
    }


def build_revised() -> dict[str, Any]:
    """Replace only the repeatedly failed direct A2 routes with a fixed union."""
    payload = build()
    events = []
    for partition_id in SCHEDULE_IDS:
        if partition_id == "A2":
            for variant, cells in (
                ("literal", LITERAL_A2_CELLS),
                ("wildcard", WILDCARD_A2_CELLS),
            ):
                events.extend(cell_event(variant, partition_id, cell) for cell in cells)
            continue
        events.append(event("literal", partition_id, LITERAL_SCHEDULE[partition_id]))
        events.append(event("wildcard", partition_id, WILDCARD_SCHEDULE[partition_id]))
    payload.update(
        {
            "schema_version": REVISED_SCHEMA,
            "objective": (
                "Complete the predeclared comparison after both direct A2 variants "
                "repeatedly failed initial result readiness. Replace each failed A2 "
                "route with the prospective lossless union of its M_H and M_B branches."
            ),
            "supersedes_events": ["literal-A2", "wildcard-A2"],
            "supersession_basis": (
                "The unchanged 3435-character literal direct A2 route timed out before "
                "rendered rows on three fresh attempts. No A2 total or source ID was "
                "accepted from those attempts."
            ),
            "a2_cell_plan": {
                "union": ["P AND E_F AND M_H", "P AND E_F AND M_B"],
                "lossless": True,
                "result_driven_terms": False,
            },
            "event_count": len(events),
            "events": events,
        }
    )
    return payload


def build_stable_pagination() -> dict[str, Any]:
    """Replace the repeatedly unstable A2 M_B route with fixed term cells."""
    payload = build_revised()
    events = []
    for partition_id in SCHEDULE_IDS:
        if partition_id == "A2":
            for variant, mh_cell, mb_cells in (
                ("literal", LITERAL_A2_CELLS[0], LITERAL_A2_MB_CHUNK_CELLS),
                ("wildcard", WILDCARD_A2_CELLS[0], WILDCARD_A2_MB_CHUNK_CELLS),
            ):
                events.append(cell_event(variant, partition_id, mh_cell))
                events.extend(
                    cell_event(variant, partition_id, cell) for cell in mb_cells
                )
            continue
        events.append(event("literal", partition_id, LITERAL_SCHEDULE[partition_id]))
        events.append(event("wildcard", partition_id, WILDCARD_SCHEDULE[partition_id]))
    payload.update(
        {
            "schema_version": STABLE_PAGINATION_SCHEMA,
            "objective": (
                "Complete the comparison after the fixed A2 M_B branch repeated a "
                "cross-page card path on three fresh attempts. Keep the successful "
                "M_H branch and replace M_B with four fixed contiguous term cells."
            ),
            "supersedes_events": [
                "literal-A2",
                "wildcard-A2",
                "literal-A2-mb",
                "wildcard-A2-mb",
            ],
            "supersession_basis": (
                "Direct A2 failed initial readiness three times. The literal A2 M_B "
                "branch then repeated a cross-page card path after bounded retries on "
                "three fresh attempts. No source ID or total from a failed attempt is "
                "used."
            ),
            "a2_cell_plan": {
                "mh": "one complete P AND E_F AND M_H cell",
                "mb": (
                    "four fixed contiguous M_B term cells with boundaries 1-8, "
                    "9-16, 17-24, and 25-31"
                ),
                "union": "stable card-path union across five cells per variant",
                "lossless": True,
                "result_driven_terms": False,
            },
            "event_count": len(events),
            "events": events,
        }
    )
    return payload


def build_year_partitioned_b2() -> dict[str, Any]:
    """Use the historical stable B2 year and Boolean source cells."""
    payload = build_stable_pagination()
    events = []
    unstable_years = {2021, 2022, 2024}
    for partition_id in SCHEDULE_IDS:
        if partition_id == "A2":
            for variant, mh_cell, mb_cells in (
                ("literal", LITERAL_A2_CELLS[0], LITERAL_A2_MB_CHUNK_CELLS),
                ("wildcard", WILDCARD_A2_CELLS[0], WILDCARD_A2_MB_CHUNK_CELLS),
            ):
                events.append(cell_event(variant, partition_id, mh_cell))
                events.extend(
                    cell_event(variant, partition_id, cell) for cell in mb_cells
                )
            continue
        if partition_id == "B2":
            for variant, direct_query, boolean_cells in (
                ("literal", LITERAL_SCHEDULE["B2"], LITERAL_B2_BOOLEAN_CELLS),
                ("wildcard", WILDCARD_SCHEDULE["B2"], WILDCARD_B2_BOOLEAN_CELLS),
            ):
                for year in range(2011, 2027):
                    if year in unstable_years:
                        events.extend(
                            year_event(
                                variant,
                                partition_id,
                                cell["query"],
                                year,
                                cell_id=cell["cell_id"],
                                branch=cell["branch"],
                            )
                            for cell in boolean_cells
                        )
                    else:
                        events.append(
                            year_event(variant, partition_id, direct_query, year)
                        )
            continue
        events.append(event("literal", partition_id, LITERAL_SCHEDULE[partition_id]))
        events.append(event("wildcard", partition_id, WILDCARD_SCHEDULE[partition_id]))
    payload.update(
        {
            "schema_version": YEAR_PARTITION_SCHEMA,
            "objective": (
                "Complete the comparison after direct B2 repeated a cross-page card "
                "path on three fresh attempts. Replace B2 with disjoint source years "
                "and the fixed two-by-two Boolean cells already required for the "
                "historically unstable 2021, 2022, and 2024 routes."
            ),
            "supersedes_events": ["literal-B2", "wildcard-B2"],
            "supersession_basis": (
                "The literal direct B2 event repeated a cross-page card path after "
                "bounded retries on three fresh attempts. Failed attempts contribute "
                "no source IDs or totals."
            ),
            "b2_cell_plan": {
                "source_years": list(range(2011, 2027)),
                "ordinary_years": "one complete B2 query per source year",
                "boolean_cell_years": [2021, 2022, 2024],
                "boolean_cells": (
                    "two fixed contiguous M_B groups crossed with two fixed contiguous "
                    "R groups"
                ),
                "lossless": True,
                "result_driven_terms": False,
            },
            "event_count": len(events),
            "events": events,
        }
    )
    return payload


def build_snapshot_retest() -> dict[str, Any]:
    """Retest only partitions affected by apparent between-event source growth."""
    events = []
    for partition_id in ("A3", "BT2"):
        for variant, query in (
            ("literal", LITERAL_SCHEDULE[partition_id]),
            ("wildcard", WILDCARD_SCHEDULE[partition_id]),
        ):
            item = event(variant, partition_id, query)
            item["event_id"] = f"retest-{variant}-{partition_id}"
            item["output"] = f"events/{item['event_id']}.json"
            item["screenshots"] = screenshot_names(item["output"])
            events.append(item)
    for year in (2025, 2026):
        for variant, query in (
            ("literal", LITERAL_SCHEDULE["B2"]),
            ("wildcard", WILDCARD_SCHEDULE["B2"]),
        ):
            item = year_event(variant, "B2", query, year)
            item["event_id"] = f"retest-{variant}-B2-year-{year}"
            item["output"] = f"events/{item['event_id']}.json"
            item["screenshots"] = screenshot_names(item["output"])
            events.append(item)
    return {
        "schema_version": SNAPSHOT_RETEST_SCHEMA,
        "pilot": PILOT,
        "source": {"id": "springer_nature_link", "label": "Springer Nature Link"},
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Repeat both renderings for A3, BT2, and B2 source years 2025-2026 "
            "after the first run showed two wildcard-only paths that also contained "
            "explicit population literals, indicating between-event source growth."
        ),
        "trigger_evidence": {
            "A3": {"literal_union": 126, "wildcard_union": 127},
            "B2": {"literal_union": 539, "wildcard_union": 541},
            "BT2": {"literal_union": 268, "wildcard_union": 269},
            "candidate_paths": [
                "/article/10.1038/s44359-026-00173-2",
                "/chapter/10.1007/978-3-031-96146-5_11",
            ],
            "visible_population_tokens": [
                "smallsats",
                "cubesat",
                "CubeSats",
                "NanoSats",
            ],
        },
        "controls": build_year_partitioned_b2()["controls"],
        "date_window": build_year_partitioned_b2()["date_window"],
        "adapter": build_year_partitioned_b2()["adapter"],
        "event_count": len(events),
        "events": events,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema = payload.get("schema_version")
    if schema not in {
        SCHEMA,
        REVISED_SCHEMA,
        STABLE_PAGINATION_SCHEMA,
        YEAR_PARTITION_SCHEMA,
        SNAPSHOT_RETEST_SCHEMA,
    }:
        errors.append("Plan schema changed")
    events = payload.get("events")
    expected_count = (
        8
        if schema == SNAPSHOT_RETEST_SCHEMA
        else 74
        if schema == YEAR_PARTITION_SCHEMA
        else 26
        if schema == STABLE_PAGINATION_SCHEMA
        else 20
        if schema == REVISED_SCHEMA
        else 18
    )
    if not isinstance(events, list) or len(events) != expected_count:
        return [*errors, f"Plan must contain {expected_count} events"]
    if schema == SNAPSHOT_RETEST_SCHEMA:
        expected_ids = [
            "retest-literal-A3",
            "retest-wildcard-A3",
            "retest-literal-BT2",
            "retest-wildcard-BT2",
            "retest-literal-B2-year-2025",
            "retest-wildcard-B2-year-2025",
            "retest-literal-B2-year-2026",
            "retest-wildcard-B2-year-2026",
        ]
    else:
        expected_ids = []
    for partition_id in () if schema == SNAPSHOT_RETEST_SCHEMA else SCHEDULE_IDS:
        if schema == YEAR_PARTITION_SCHEMA and partition_id == "B2":
            for variant in ("literal", "wildcard"):
                for year in range(2011, 2027):
                    if year in {2021, 2022, 2024}:
                        expected_ids.extend(
                            f"{variant}-B2-year-{year}-mb-{mb}-r-{r}"
                            for mb in (1, 2)
                            for r in (1, 2)
                        )
                    else:
                        expected_ids.append(f"{variant}-B2-year-{year}")
        elif (
            schema in {STABLE_PAGINATION_SCHEMA, YEAR_PARTITION_SCHEMA}
            and partition_id == "A2"
        ):
            expected_ids.extend(
                f"{variant}-A2-{cell_id}"
                for variant in ("literal", "wildcard")
                for cell_id in ("mh", "mb-01", "mb-02", "mb-03", "mb-04")
            )
        elif schema == REVISED_SCHEMA and partition_id == "A2":
            expected_ids.extend(
                f"{variant}-A2-{cell_id}"
                for variant in ("literal", "wildcard")
                for cell_id in ("mh", "mb")
            )
        else:
            expected_ids.extend(
                f"{variant}-{partition_id}" for variant in ("literal", "wildcard")
            )
    if [item.get("event_id") for item in events] != expected_ids:
        errors.append("Event order or identity changed")
    expected_payload = {
        SCHEMA: build,
        REVISED_SCHEMA: build_revised,
        STABLE_PAGINATION_SCHEMA: build_stable_pagination,
        YEAR_PARTITION_SCHEMA: build_year_partitioned_b2,
        SNAPSHOT_RETEST_SCHEMA: build_snapshot_retest,
    }.get(schema, build)()
    if events != expected_payload.get("events"):
        errors.append("Planned queries or source cells changed")
    for item in events:
        query = item.get("query")
        if not isinstance(query, str) or not query:
            errors.append(f"Missing query for {item.get('event_id')}")
            continue
        if item.get("query_characters") != len(query) or item.get(
            "query_sha256"
        ) != digest_text(query):
            errors.append(f"Query receipt changed for {item.get('event_id')}")
        if any(token in query.upper() for token in ("NEAR", " W/")) or "~" in query:
            errors.append(f"Proximity syntax in {item.get('event_id')}")
        if item.get("variant") == "literal" and ("*" in query or "?" in query):
            errors.append(f"Wildcard in literal event {item.get('event_id')}")
        if item.get("variant") == "wildcard" and query.count("*") != 3:
            errors.append(f"Wildcard declaration changed in {item.get('event_id')}")
        if item.get("screenshots") != screenshot_names(item["output"]):
            errors.append(f"Screenshot paths changed for {item.get('event_id')}")
    return errors


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--revised-a2-split", action="store_true")
    parser.add_argument("--stable-pagination", action="store_true")
    parser.add_argument("--year-partitioned-b2", action="store_true")
    parser.add_argument("--snapshot-retest", action="store_true")
    args = parser.parse_args()
    if args.check:
        payload = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate(payload)
        print(
            json.dumps(
                {"status": "ok" if not errors else "error", "errors": errors}, indent=2
            )
        )
        return 1 if errors else 0
    if (
        sum(
            bool(value)
            for value in (
                args.revised_a2_split,
                args.stable_pagination,
                args.year_partitioned_b2,
                args.snapshot_retest,
            )
        )
        > 1
    ):
        parser.error("Choose only one revised plan")
    payload = (
        build_snapshot_retest()
        if args.snapshot_retest
        else build_year_partitioned_b2()
        if args.year_partitioned_b2
        else build_stable_pagination()
        if args.stable_pagination
        else build_revised()
        if args.revised_a2_split
        else build()
    )
    errors = validate(payload)
    if errors:
        raise RuntimeError("Generated plan is invalid: " + "; ".join(errors))
    write_create_only(args.output, payload)
    print(
        json.dumps(
            {"saved": str(args.output), "events": len(payload["events"])}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
