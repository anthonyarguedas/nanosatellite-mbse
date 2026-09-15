#!/usr/bin/env python3
"""Build the predeclared Web of Science PSR population-wildcard plan."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

from queries import (
    EXPECTED_MAIN_QUERY_SHA256,
    EXPECTED_SUPPORTING_PROTOCOL_SHA256,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    PSR_IDS,
    TERM_COUNTS,
    WILDCARD_REPLACEMENTS,
    WILDCARD_SCHEDULE,
)

PILOT = "006"
SCHEMA = "wos-psr-population-wildcard-pilot-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific/web-of-science-core-collection/pilots/006"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_web_of_science.py"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/event-plan.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected an object in {path}")
    return value


def adapter_version() -> str:
    spec = importlib.util.spec_from_file_location("wos_pilot006_adapter_plan", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if getattr(module, "ADAPTER_VERSION", None) != "2":
        raise RuntimeError("Web of Science adapter version 2 is required")
    return module.ADAPTER_VERSION


def event(partition_id: str, variant: str, query: str) -> dict[str, Any]:
    event_id = f"{variant}-{partition_id}"
    return {
        "event_id": event_id,
        "partition_id": partition_id,
        "variant": variant,
        "query": query,
        "query_sha256": sha256_text(query),
        "query_characters": len(query),
        "wildcard_operator_count": query.count("*"),
        "attempt_outputs": [
            f"events/{event_id}.attempt-{attempt:02d}.json"
            for attempt in range(1, 4)
        ],
        "diagnostic_only": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    events = []
    for partition_id in PSR_IDS:
        events.append(event(partition_id, "literal", LITERAL_SCHEDULE[partition_id]))
        events.append(event(partition_id, "wildcard", WILDCARD_SCHEDULE[partition_id]))
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": "Web of Science Core Collection",
        "namespace": "prior_secondary_review_supporting_search",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Compare all four current PSR partitions with literal P/X population "
            "terms and with the ten population wildcards accepted for the main route."
        ),
        "adapter": {
            "id": "search_web_of_science",
            "version": adapter_version(),
            "sha256": sha256_file(ADAPTER),
            "screenshot_schema": "web-of-science-automatic-screenshots/v1",
            "mandatory_screenshots": True,
            "screenshot_opt_out": False,
        },
        "dependencies": {
            "main_query_snapshot_sha256": EXPECTED_MAIN_QUERY_SHA256,
            "supporting_protocol_sha256": EXPECTED_SUPPORTING_PROTOCOL_SHA256,
            "term_counts": TERM_COUNTS,
        },
        "controls": {
            "field": "TS Topic",
            "source_year_control": "PY=(1900-2026)",
            "protocol_date_scope": "source inception through the 2026-08-29 diagnostic cutoff year",
            "language": "all languages",
            "editions": "all currently exposed Core Collection editions",
            "sort": "Date: oldest first",
            "page_size": 50,
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
        "wildcard_candidate": {
            "candidate_count": 10,
            "replaced_population_literal_count": 22,
            "query_character_reduction": 255,
            "replacements": [
                {
                    "candidate": item["candidate"],
                    "explicit_terms": list(item["replaced_literals"]),
                }
                for item in WILDCARD_REPLACEMENTS
            ],
            "application": {
                "PSR1": "replace the P members nested in X",
                "PSR2": "replace the P members nested in X",
                "PSR3": "replace P",
                "PSR4": "replace the P members nested in X",
            },
            "x_additions": "keep every supporting-protocol X addition literal",
        },
        "retry_policy": {
            "maximum_attempts_per_event": 3,
            "exact_query_only": True,
            "fresh_owned_page_per_attempt": True,
            "stop_after_first_success": True,
            "retry_only_record_free_failure": True,
            "retain_every_attempt": True,
        },
        "acceptance_checks": [
            "All eight literal and wildcard events complete strict two-pass WOS-ID and total reconciliation.",
            "Each successful event retains its configured-search and first-results screenshots.",
            "Each wildcard partition retains every WOS ID from its literal counterpart.",
            "Every wildcard-only record receives a population-scope review before acceptance.",
            "The complete successful query union retrieves Buruso et al. when the source indexes it.",
            "No language, type, subject, access, controlled-term, proximity, or pair restriction is used.",
        ],
        "acceptance_rule": (
            "Accept the ten population wildcards for PSR only if all literal IDs are "
            "retained and every wildcard-only record remains within the declared P meaning."
        ),
        "event_count": len(events),
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != SCHEMA or plan.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Plan identity changed")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 8:
        return [*errors, "Plan must contain eight events"]
    expected = [
        f"{variant}-{partition_id}"
        for partition_id in PSR_IDS
        for variant in ("literal", "wildcard")
    ]
    if [item.get("event_id") for item in events] != expected:
        errors.append("Event identity or order changed")
    outputs: set[str] = set()
    for item in events:
        query = item.get("query")
        partition_id = item.get("partition_id")
        expected_query = (
            LITERAL_SCHEDULE.get(partition_id)
            if item.get("variant") == "literal"
            else WILDCARD_SCHEDULE.get(partition_id)
        )
        if query != expected_query:
            errors.append(f"Query changed for {item.get('event_id')}")
            continue
        if item.get("query_sha256") != sha256_text(query) or item.get("query_characters") != len(query):
            errors.append(f"Query receipt changed for {item.get('event_id')}")
        if "NEAR" in query.upper() or " SAME " in query.upper() or "LA=(" in query or "DT=(" in query:
            errors.append(f"Control or proximity syntax changed for {item.get('event_id')}")
        expected_wildcards = 0 if item.get("variant") == "literal" else 10
        if query.count("*") != expected_wildcards or "?" in query or "$" in query:
            errors.append(f"Wildcard syntax changed for {item.get('event_id')}")
        attempts = item.get("attempt_outputs")
        if not isinstance(attempts, list) or len(attempts) != 3:
            errors.append(f"Attempt plan changed for {item.get('event_id')}")
        else:
            for output in attempts:
                if output in outputs:
                    errors.append(f"Repeated output path {output}")
                outputs.add(output)
    return errors


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    plan = build()
    errors = validate(plan)
    if errors:
        raise SystemExit("; ".join(errors))
    write_create_only(DEFAULT_OUTPUT, plan)
    print(json.dumps({"saved": str(DEFAULT_OUTPUT), "events": len(plan["events"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
