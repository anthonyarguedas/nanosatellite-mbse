#!/usr/bin/env python3
"""Predeclare the OATD Pilot 005 continuation after local validator failure."""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-005-gate-count-continuation-plan/v1"
INITIAL_PLAN_SCHEMA = "oatd-pilot-005-gate-count-plan/v1"
INITIAL_RUN_SCHEMA = "oatd-pilot-005-gate-count-run/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/005"
DEFAULT_INITIAL_PLAN = PILOT_ROOT / "searches/event-plan.json"
DEFAULT_INITIAL_RUN = PILOT_ROOT / "searches/run-receipt.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/continuation-plan.json"
SOURCE_AFFECTING_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "run_pilot.py",
    SCRIPT_DIR / "build_continuation_plan.py",
    SCRIPT_DIR / "run_continuation.py",
)


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(base.REPOSITORY_ROOT.resolve()))


def build(initial_plan_path: Path, initial_run_path: Path) -> dict[str, Any]:
    initial_plan = base.load(initial_plan_path)
    initial_run = base.load(initial_run_path)
    outcomes = initial_run.get("outcomes")
    if (
        initial_plan.get("schema_version") != INITIAL_PLAN_SCHEMA
        or initial_run.get("schema_version") != INITIAL_RUN_SCHEMA
        or initial_run.get("plan_sha256") != base.digest(initial_plan_path)
        or not isinstance(outcomes, list)
        or len(outcomes) != 1
    ):
        raise RuntimeError("The OATD Pilot 005 initial evidence is invalid")
    outcome = outcomes[0]
    if (
        outcome.get("event_id") != "G1-MH"
        or outcome.get("return_code") != 0
        or outcome.get("validation_error") != "The OATD G1-MH marker is invalid"
        or outcome.get("output_exists") is not True
        or outcome.get("marker_exists") is not True
        or outcome.get("screenshots_exist")
        != {"search_page": True, "results_page": True}
    ):
        raise RuntimeError(
            "The continuation requires the retained local G1 validation failure"
        )
    first_event = initial_plan["events"][0]
    output = PILOT_ROOT / first_event["output"]
    artifact = base.load(output)
    if (
        artifact.get("total") != 16
        or artifact.get("output_metadata", {}).get("status") != "count_only"
        or artifact.get("output_metadata", {}).get("merge_eligible") is not False
    ):
        raise RuntimeError("The retained G1 source count is invalid")
    adapter = base.load_adapter()
    marker = adapter.oatd_output_commit_marker_path(output)
    screenshots = base.expected_screenshots(output)
    completed = base.parse_utc(outcome["completed_at_utc"])
    not_before = completed + timedelta(
        seconds=initial_plan["source_safety"]["inter_event_delay_seconds"]
    )
    return {
        "schema_version": SCHEMA,
        "source": initial_plan["source"],
        "source_id": "oatd",
        "platform": "OATD",
        "pilot": "005",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "reason": (
            "G1 completed with total 16 and complete screenshot and terminal marker "
            "evidence. The initial runner incorrectly asked the generic merger to "
            "admit a deliberately nonmergeable count artifact. Generic admission "
            "correctly returned false. This continuation validates the count marker "
            "directly and does not repeat G1."
        ),
        "source_semantics_changed": False,
        "initial_plan": {
            "path": relative(initial_plan_path),
            "sha256": base.digest(initial_plan_path),
        },
        "initial_run": {
            "path": relative(initial_run_path),
            "sha256": base.digest(initial_run_path),
        },
        "adopted_initial_event": {
            "event_id": "G1-MH",
            "source_return_code": 0,
            "total": 16,
            "artifact": first_event["output"],
            "artifact_sha256": base.digest(output),
            "marker_sha256": base.digest(marker),
            "search_page_sha256": base.digest(screenshots["search_page"]),
            "results_page_sha256": base.digest(screenshots["results_page"]),
            "generic_merge_admission_expected": False,
            "count_marker_validated_directly": True,
        },
        "source_safety": {
            "first_source_request_not_before_utc": not_before.isoformat().replace(
                "+00:00", "Z"
            ),
            "inter_event_delay_seconds": initial_plan["source_safety"][
                "inter_event_delay_seconds"
            ],
            "stop_after_first_failed_event": True,
            "runner_level_retries": 0,
            "do_not_repeat_adopted_G1": True,
        },
        "adapter": deepcopy(initial_plan["adapter"]),
        "source_affecting_scripts": {
            relative(path): base.digest(path) for path in SOURCE_AFFECTING_SCRIPTS
        },
        "acceptance_checks": list(initial_plan["acceptance_checks"]),
        "event_count": 4,
        "events": deepcopy(initial_plan["events"][1:]),
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
    parser.add_argument("--initial-plan", type=Path, default=DEFAULT_INITIAL_PLAN)
    parser.add_argument("--initial-run", type=Path, default=DEFAULT_INITIAL_RUN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    plan = build(args.initial_plan, args.initial_run)
    write_new(args.output, plan)
    print(json.dumps({"saved": str(args.output), "remaining_events": 4}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
