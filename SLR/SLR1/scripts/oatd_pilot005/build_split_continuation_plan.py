#!/usr/bin/env python3
"""Predeclare lossless smaller gates after the combined OATD G2 failure."""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from typing import Any

import run_continuation as prior
import run_pilot as base
import split_queries

SCHEMA = "oatd-pilot-005-split-gate-count-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/005"
INITIAL_PLAN = PILOT_ROOT / "searches/event-plan.json"
INITIAL_RUN = PILOT_ROOT / "searches/run-receipt.json"
CONTINUATION_PLAN = PILOT_ROOT / "searches/continuation-plan.json"
CONTINUATION_RUN = PILOT_ROOT / "searches/continuation-run-receipt.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/split-continuation-plan.json"
MINIMUM_FAILURE_COOLDOWN_SECONDS = 1800
SOURCE_AFFECTING_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "split_queries.py",
    SCRIPT_DIR / "run_pilot.py",
    SCRIPT_DIR / "run_continuation.py",
    SCRIPT_DIR / "build_split_continuation_plan.py",
    SCRIPT_DIR / "run_split_continuation.py",
)


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(base.REPOSITORY_ROOT.resolve()))


def screenshots(output: str) -> dict[str, str]:
    path = Path(output)
    return {
        "search_page": str(path.with_name(f"{path.stem}.search-page.png")),
        "results_page": str(path.with_name(f"{path.stem}.results-page.png")),
    }


def build_event(adapter: Any, template: dict[str, Any], gate_id: str) -> dict[str, Any]:
    query = split_queries.SPLIT_GATE_QUERIES[gate_id]
    configuration = adapter.build_oatd_search_configuration(
        query,
        language="English",
        year_start=2011,
        year_end=2026,
        page_size=30,
    )
    route = adapter.build_search_url(query, configuration=configuration)
    if len(route) > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS:
        raise RuntimeError(f"The split OATD gate is too long: {gate_id}")
    event = deepcopy(template)
    output = f"searches/{gate_id}.json"
    event.update(
        {
            "event_id": gate_id,
            "purpose": "Observe one smaller exact branch of the candidate union by count only.",
            "query": query,
            "query_characters": len(query),
            "query_sha256": base.text_digest(query),
            "effective_query": configuration.effective_query,
            "effective_query_sha256": base.text_digest(configuration.effective_query),
            "navigation_route_characters": len(route),
            "output": output,
            "screenshots": screenshots(output),
        }
    )
    return event


def build() -> dict[str, Any]:
    initial_plan = base.load(INITIAL_PLAN)
    initial_run = base.load(INITIAL_RUN)
    continuation_plan = base.load(CONTINUATION_PLAN)
    continuation_run = base.load(CONTINUATION_RUN)
    outcomes = continuation_run.get("outcomes")
    if (
        initial_plan.get("schema_version") != "oatd-pilot-005-gate-count-plan/v1"
        or initial_run.get("schema_version") != "oatd-pilot-005-gate-count-run/v1"
        or continuation_plan.get("schema_version")
        != "oatd-pilot-005-gate-count-continuation-plan/v1"
        or continuation_run.get("schema_version")
        != "oatd-pilot-005-gate-count-continuation-run/v1"
        or continuation_run.get("success") is not False
        or continuation_run.get("stopped_after_failure") is not True
        or not isinstance(outcomes, list)
        or len(outcomes) != 2
        or outcomes[0].get("event_id") != "G1-MH"
        or outcomes[0].get("total") != 16
        or outcomes[1].get("event_id") != "G2-MB"
        or outcomes[1].get("return_code") != 1
        or outcomes[1].get("total") is not None
    ):
        raise RuntimeError("The split continuation requires the retained G2 failure")
    failed_event = outcomes[1]
    failed_output = PILOT_ROOT / failed_event["output"]
    failed_artifact = base.load(failed_output)
    if (
        failed_artifact.get("output_metadata", {}).get("error")
        != "OATD page did not become ready in time."
        or failed_artifact.get("output_metadata", {}).get("observed_exact_query_echo")
        is not False
    ):
        raise RuntimeError("The retained combined G2 failure changed")
    first_event = initial_plan["events"][0]
    first_output = PILOT_ROOT / first_event["output"]
    adapter = base.load_adapter()
    prior.validate_count_marker(
        adapter, base.load(first_output), first_event, first_output
    )
    marker = adapter.oatd_output_commit_marker_path(first_output)
    first_screenshots = base.expected_screenshots(first_output)

    template = initial_plan["events"][1]
    events = [
        build_event(adapter, template, gate_id)
        for gate_id in split_queries.SPLIT_GATE_IDS
    ]
    failure_completed = base.parse_utc(failed_event["completed_at_utc"])
    not_before = failure_completed + timedelta(seconds=MINIMUM_FAILURE_COOLDOWN_SECONDS)
    return {
        "schema_version": SCHEMA,
        "source": initial_plan["source"],
        "source_id": "oatd",
        "platform": "OATD",
        "pilot": "005",
        "protocol_commit": split_queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Replace the unready combined M_B gate with its four exact smaller "
            "branches, then count the remaining exact union gates."
        ),
        "algebraic_candidate_union": {
            "identity": split_queries.ALGEBRAIC_IDENTITY,
            "relationship_to_original_schedule": "exact_union_equality",
            "partition_branch_coverage": {
                key: list(value)
                for key, value in split_queries.PARTITION_BRANCH_COVERAGE.items()
            },
            "wildcards": False,
            "proximity": False,
            "new_terms": False,
            "source_refinement_from_results": False,
        },
        "initial_plan": {
            "path": relative(INITIAL_PLAN),
            "sha256": base.digest(INITIAL_PLAN),
        },
        "initial_run": {
            "path": relative(INITIAL_RUN),
            "sha256": base.digest(INITIAL_RUN),
        },
        "first_continuation_plan": {
            "path": relative(CONTINUATION_PLAN),
            "sha256": base.digest(CONTINUATION_PLAN),
        },
        "first_continuation_run": {
            "path": relative(CONTINUATION_RUN),
            "sha256": base.digest(CONTINUATION_RUN),
        },
        "adopted_initial_event": {
            "event_id": "G1-MH",
            "total": 16,
            "artifact": first_event["output"],
            "artifact_sha256": base.digest(first_output),
            "marker_sha256": base.digest(marker),
            "search_page_sha256": base.digest(first_screenshots["search_page"]),
            "results_page_sha256": base.digest(first_screenshots["results_page"]),
        },
        "superseded_combined_gate_failure": {
            "event_id": "G2-MB",
            "artifact": failed_event["output"],
            "sha256": base.digest(failed_output),
            "source_total": None,
            "observed_exact_query_echo": False,
            "error": "OATD page did not become ready in time.",
            "replacement_events": list(split_queries.SPLIT_GATE_IDS[:4]),
        },
        "source_safety": {
            "minimum_cooldown_after_combined_gate_failure_seconds": MINIMUM_FAILURE_COOLDOWN_SECONDS,
            "first_source_request_not_before_utc": not_before.isoformat().replace(
                "+00:00", "Z"
            ),
            "inter_event_delay_seconds": 120.0,
            "stop_after_first_failed_event": True,
            "runner_level_retries": 0,
            "do_not_repeat_G1_or_failed_combined_G2": True,
        },
        "adapter": deepcopy(initial_plan["adapter"]),
        "source_affecting_scripts": {
            relative(path): base.digest(path) for path in SOURCE_AFFECTING_SCRIPTS
        },
        "acceptance_checks": list(initial_plan["acceptance_checks"]),
        "event_count": len(events),
        "events": events,
    }


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    plan = build()
    write_new(args.output, plan)
    print(json.dumps({"saved": str(args.output), "events": 7}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
