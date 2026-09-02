#!/usr/bin/env python3
"""Build the Web of Science Pilot 005 broad wildcard plan."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

from queries import (
    BROAD_WILDCARD_SCHEDULE,
    EXPECTED_BASELINE_SHA256,
    EXPECTED_FAMILY_SHA256,
    FAMILY_COUNT,
    FAMILY_RECEIPTS,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    REPLACED_TERM_COUNT,
    SCHEDULE_IDS,
)

PILOT = "005"
SCHEMA = "wos-broad-wildcard-pilot-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PILOT_ROOT = SLR1_DIR / "source-specific" / "web-of-science-core-collection" / "pilots" / PILOT
PILOT004_ROOT = PILOT_ROOT.parent / "004"
PILOT004_ASSESSMENT = PILOT004_ROOT / "searches" / "assessment.json"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_web_of_science.py"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"


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
    spec = importlib.util.spec_from_file_location("wos_pilot005_adapter_plan", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if getattr(module, "ADAPTER_VERSION", None) != "2":
        raise RuntimeError("Web of Science adapter version 2 is required")
    return module.ADAPTER_VERSION


def build() -> dict[str, Any]:
    baseline = load(PILOT004_ASSESSMENT)
    if baseline.get("status") != "passed":
        raise RuntimeError("Pilot 004 is not an accepted literal baseline")
    events = []
    for partition_id in SCHEDULE_IDS:
        baseline_event = baseline["partition_results"][partition_id]["literal"]
        query = BROAD_WILDCARD_SCHEDULE[partition_id]
        events.append(
            {
                "event_id": f"broad-wildcard-{partition_id}",
                "partition_id": partition_id,
                "variant": "broad_wildcard",
                "query": query,
                "query_sha256": sha256_text(query),
                "query_characters": len(query),
                "literal_query_characters": len(LITERAL_SCHEDULE[partition_id]),
                "character_reduction": len(LITERAL_SCHEDULE[partition_id]) - len(query),
                "wildcard_operator_count": query.count("*") + query.count("$"),
                "literal_baseline": {
                    "artifact": baseline_event["artifact"],
                    "artifact_sha256": sha256_file(PILOT004_ROOT / baseline_event["artifact"]),
                    "total": baseline_event["total"],
                    "ordered_wos_ids_sha256": baseline_event["ordered_wos_ids_sha256"],
                },
                "attempt_outputs": [
                    f"events/{partition_id}.attempt-{attempt:02d}.json"
                    for attempt in range(1, 4)
                ],
                "diagnostic_only": True,
                "do_not_merge": True,
            }
        )
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": "Web of Science Core Collection",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Use a source-specific wildcard for every ordinary variant family with "
            "one reviewed stem, then compare each complete set with Pilot 004's fresh "
            "literal baseline."
        ),
        "adapter": {
            "id": "search_web_of_science",
            "version": adapter_version(),
            "sha256": sha256_file(ADAPTER),
            "mandatory_screenshots": True,
            "screenshot_opt_out": False,
        },
        "dependencies": {
            "wos_pilot004_queries_sha256": EXPECTED_BASELINE_SHA256,
            "ordinary_family_map_sha256": EXPECTED_FAMILY_SHA256,
            "pilot004_assessment": str(PILOT004_ASSESSMENT.relative_to(SLR1_DIR)),
            "pilot004_assessment_sha256": sha256_file(PILOT004_ASSESSMENT),
        },
        "wildcard_policy": {
            "family_count": FAMILY_COUNT,
            "replaced_term_occurrence_count": REPLACED_TERM_COUNT,
            "zero_or_one_character_operator": "$",
            "zero_or_more_character_operator": "*",
            "rule": (
                "Use `$` when every declared suffix differs by at most one character. "
                "Use `*` only when a reviewed family requires a longer suffix. Keep "
                "singletons and families without one safe common stem literal."
            ),
            "ordered_phrase_rule": "Keep every multiword pattern in straight double quotes.",
            "families": FAMILY_RECEIPTS,
        },
        "controls": {
            "field": "TS Topic",
            "year": "PY=(2011-2026)",
            "language": "LA=(English)",
            "editions": "all currently exposed editions",
            "sort": "Date: oldest first",
            "page_size": 50,
            "strict_passes": 2,
            "native_export": "RIS (other reference software)",
            "proximity": False,
            "pair_expansion": False,
            "publication_type": None,
            "subject": None,
            "access": None,
            "controlled_vocabulary": None,
        },
        "retry_policy": {
            "maximum_attempts_per_event": 3,
            "exact_query_only": True,
            "fresh_owned_page_per_attempt": True,
            "stop_after_first_success": True,
            "retain_every_failure": True,
            "retryable": "source or adapter failure with total null",
        },
        "acceptance_rule": (
            "Accept each family-bearing schedule query only when strict capture succeeds, "
            "every Pilot 004 literal ID is retained, and every wildcard-only record is "
            "confirmed to satisfy the intended concept. Exact set equality requires no "
            "wildcard-only review."
        ),
        "schedule_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != SCHEMA or plan.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Plan identity changed")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 9:
        return [*errors, "Plan must contain nine events"]
    if [item.get("partition_id") for item in events] != list(SCHEDULE_IDS):
        errors.append("Partition order changed")
    outputs: set[str] = set()
    for item in events:
        partition_id = item.get("partition_id")
        query = item.get("query")
        if query != BROAD_WILDCARD_SCHEDULE.get(partition_id):
            errors.append(f"Query changed for {partition_id}")
            continue
        if item.get("query_sha256") != sha256_text(query) or item.get("query_characters") != len(query):
            errors.append(f"Query receipt changed for {partition_id}")
        if "NEAR" in query.upper() or " SAME " in query.upper() or "?" in query or "[*" in query:
            errors.append(f"Invalid wildcard or proximity syntax in {partition_id}")
        if query.count("*") + query.count("$") != item.get("wildcard_operator_count"):
            errors.append(f"Wildcard count changed for {partition_id}")
        attempts = item.get("attempt_outputs")
        if not isinstance(attempts, list) or len(attempts) != 3:
            errors.append(f"Attempt plan changed for {partition_id}")
        else:
            for output in attempts:
                if output in outputs:
                    errors.append(f"Repeated output {output}")
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
