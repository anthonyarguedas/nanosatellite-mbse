#!/usr/bin/env python3
"""Build the predeclared Web of Science Pilot 004 event plan."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

from queries import (
    EXPECTED_TERM_SNAPSHOT_SHA256,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    SCHEDULE_IDS,
    TERM_COUNTS,
    WILDCARD_REPLACEMENTS,
    WILDCARD_SCHEDULE,
    wildcard_population_atoms,
)

PILOT = "004"
SCHEMA = "wos-current-schedule-wildcard-pilot-plan/v1"
ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_web_of_science.py"
)
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PILOT_ROOT = (
    SLR1_DIR
    / "source-specific"
    / "web-of-science-core-collection"
    / "pilots"
    / PILOT
)
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"
DIAGNOSTIC_CUTOFF = "2026-08-29"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def adapter_version() -> str:
    spec = importlib.util.spec_from_file_location("wos_pilot004_adapter_plan", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Web of Science adapter at {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    version = getattr(module, "ADAPTER_VERSION", None)
    if version != "2":
        raise RuntimeError("Web of Science adapter version 2 is required")
    if not hasattr(module, "screenshot_paths_for_output"):
        raise RuntimeError("Web of Science adapter lacks automatic screenshots")
    return version


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.name
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def event(partition_id: str, variant: str, query: str) -> dict[str, Any]:
    event_id = f"{variant}-{partition_id}"
    output = f"events/{event_id}.json"
    return {
        "event_id": event_id,
        "partition_id": partition_id,
        "variant": variant,
        "query": query,
        "query_characters": len(query),
        "query_sha256": sha256_text(query),
        "output": output,
        "screenshots": screenshot_names(output),
        "mode": "strict_two_pass_complete_native_ris",
        "diagnostic_only": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    version = adapter_version()
    events = []
    for partition_id in SCHEDULE_IDS:
        events.append(event(partition_id, "literal", LITERAL_SCHEDULE[partition_id]))
        events.append(event(partition_id, "wildcard", WILDCARD_SCHEDULE[partition_id]))
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": {
            "id": "web_of_science_core_collection",
            "label": "Web of Science Core Collection",
            "platform": "Clarivate Web of Science",
        },
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test all nine main partitions from the no-proximity schedule and compare "
            "each literal result set with the accepted ten-wildcard population candidate."
        ),
        "adapter": {
            "path": str(ADAPTER),
            "id": "search_web_of_science",
            "version": version,
            "sha256": file_sha256(ADAPTER),
            "mandatory_automatic_screenshots": True,
            "screenshot_schema": "web-of-science-automatic-screenshots/v1",
            "screenshot_opt_out": False,
        },
        "term_snapshot": {
            "path": "SLR/SLR1/scripts/atai_pilot007/queries.py",
            "sha256": EXPECTED_TERM_SNAPSHOT_SHA256,
            "counts": TERM_COUNTS,
        },
        "controls": {
            "source": "Web of Science Core Collection",
            "editions": "all currently exposed editions",
            "field": "TS Topic",
            "year": "PY=(2011-2026)",
            "language": "LA=(English)",
            "sort": "Date: oldest first",
            "page_size": 50,
            "limit": 2000,
            "max_pages": 40,
            "timeout_seconds": 120,
            "strict_passes": 2,
            "native_export": "RIS (other reference software)",
            "publication_type": None,
            "subject": None,
            "access": None,
            "full_text": None,
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
            "operator": "documented quoted trailing * in TS",
            "prior_basis": "Pilot 002 accepted this exact candidate for A1",
            "replacements": [
                {
                    "candidate": item["candidate"],
                    "explicit_terms": list(item["replaced_literals"]),
                }
                for item in WILDCARD_REPLACEMENTS
            ],
            "explicit_population_terms": 26,
            "replaced_population_literals": 22,
            "candidate_population_atoms": len(wildcard_population_atoms()),
            "population_atoms_after_compression": list(wildcard_population_atoms()),
            "query_character_reduction": 255,
            "acceptance_rule": (
                "Adopt the candidate in a partition only if its strict complete result "
                "contains every literal stable ID. Inspect every wildcard-only record "
                "before accepting a broader set."
            ),
            "preference_rule": "Prefer the shorter wildcard rendering after acceptance.",
        },
        "acceptance_checks": [
            "All 18 events complete strict two-pass ordered WOS-ID and total reconciliation.",
            "Every event has exact query, Core Collection, all-edition, oldest-sort, page-size, and native RIS evidence.",
            "Every event saves a configured-search PNG and first-results PNG beside its JSON.",
            "No query contains NEAR, SAME, another proximity operator, or pair expansion.",
            "Each wildcard partition retains every literal WOS ID.",
            "Every wildcard-only record receives a population-meaning review before acceptance.",
        ],
        "schedule_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != SCHEMA:
        errors.append("Plan schema changed")
    if plan.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Protocol commit changed")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 18:
        return [*errors, "Plan must contain 18 events"]
    expected_ids = [
        f"{variant}-{partition_id}"
        for partition_id in SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    ]
    if [item.get("event_id") for item in events] != expected_ids:
        errors.append("Event identity or order changed")
    seen_outputs: set[str] = set()
    for item in events:
        event_id = item.get("event_id")
        query = item.get("query")
        if not isinstance(query, str) or not query:
            errors.append(f"Missing query for {event_id}")
            continue
        if item.get("query_characters") != len(query):
            errors.append(f"Query length changed for {event_id}")
        if item.get("query_sha256") != sha256_text(query):
            errors.append(f"Query hash changed for {event_id}")
        if "NEAR" in query.upper() or " SAME " in query.upper():
            errors.append(f"Proximity syntax appears in {event_id}")
        if item.get("variant") == "literal" and ("*" in query or "?" in query):
            errors.append(f"Literal event has a wildcard: {event_id}")
        if item.get("variant") == "wildcard" and query.count("*") != 10:
            errors.append(f"Wildcard event does not have ten candidates: {event_id}")
        if "PY=(2011-2026)" not in query or "LA=(English)" not in query:
            errors.append(f"Main controls changed for {event_id}")
        output = item.get("output")
        if not isinstance(output, str) or output in seen_outputs:
            errors.append(f"Output changed or repeated for {event_id}")
        else:
            seen_outputs.add(output)
            if item.get("screenshots") != screenshot_names(output):
                errors.append(f"Screenshot names changed for {event_id}")
    return errors


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected an object in {path}")
    return value


def write_json_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = validate(load(args.output))
        print(json.dumps({"status": "passed" if not errors else "failed", "errors": errors}, indent=2))
        return 1 if errors else 0
    plan = build()
    errors = validate(plan)
    if errors:
        raise RuntimeError("Invalid generated plan: " + "; ".join(errors))
    write_json_create_only(args.output, plan)
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
