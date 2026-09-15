#!/usr/bin/env python3
"""Run the losslessly split continuation of OATD Pilot 005."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_continuation as prior
import run_pilot as base
import split_queries

SCHEMA = "oatd-pilot-005-split-gate-count-run/v1"
PLAN_SCHEMA = "oatd-pilot-005-split-gate-count-plan/v1"


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != "005"
        or plan.get("protocol_commit") != split_queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or [event.get("event_id") for event in events]
        != list(split_queries.SPLIT_GATE_IDS)
    ):
        raise RuntimeError("Unexpected OATD Pilot 005 split-gate plan")
    adapter = base.load_adapter()
    adapter_plan = plan.get("adapter")
    files = adapter_plan.get("files") if isinstance(adapter_plan, dict) else None
    if (
        not isinstance(adapter_plan, dict)
        or adapter_plan.get("id") != adapter.ADAPTER_ID
        or adapter_plan.get("version") != adapter.ADAPTER_VERSION
        or not isinstance(files, dict)
    ):
        raise RuntimeError("The OATD split-gate adapter identity changed")
    for name, path in base.ADAPTER_FILES.items():
        descriptor = files.get(name)
        if not isinstance(descriptor, dict) or descriptor.get("sha256") != base.digest(
            path
        ):
            raise RuntimeError(f"The OATD split-gate adapter changed: {name}")
    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("The OATD split-gate script bindings are missing")
    for relative, expected in scripts.items():
        path = base.REPOSITORY_ROOT / relative
        if not path.is_file() or base.digest(path) != expected:
            raise RuntimeError(f"An OATD split-gate script changed: {relative}")
    for key in (
        "initial_plan",
        "initial_run",
        "first_continuation_plan",
        "first_continuation_run",
    ):
        descriptor = plan.get(key)
        if not isinstance(descriptor, dict):
            raise RuntimeError(f"The OATD split-gate {key} binding is missing")
        path = base.REPOSITORY_ROOT / descriptor.get("path", "")
        if not path.is_file() or base.digest(path) != descriptor.get("sha256"):
            raise RuntimeError(f"The OATD split-gate {key} changed")
    initial_plan = base.load(base.REPOSITORY_ROOT / plan["initial_plan"]["path"])
    first_event = initial_plan["events"][0]
    adopted = plan.get("adopted_initial_event")
    first_output = pilot_root / first_event["output"]
    if (
        not isinstance(adopted, dict)
        or adopted.get("event_id") != "G1-MH"
        or adopted.get("total") != 16
        or adopted.get("artifact_sha256") != base.digest(first_output)
    ):
        raise RuntimeError("The adopted G1 count changed")
    prior.validate_count_marker(
        adapter, base.load(first_output), first_event, first_output
    )
    failed = plan.get("superseded_combined_gate_failure")
    if not isinstance(failed, dict):
        raise RuntimeError("The combined G2 failure binding is missing")
    failed_path = pilot_root / failed.get("artifact", "")
    if (
        not failed_path.is_file()
        or base.digest(failed_path) != failed.get("sha256")
        or base.load(failed_path).get("total") is not None
        or base.load(failed_path).get("output_metadata", {}).get("error")
        != "OATD page did not become ready in time."
    ):
        raise RuntimeError("The combined G2 failure changed")

    for event in events:
        query = split_queries.SPLIT_GATE_QUERIES[event["event_id"]]
        output = pilot_root / event["output"]
        screenshots = base.expected_screenshots(output)
        configuration = adapter.build_oatd_search_configuration(
            query,
            language="English",
            year_start=2011,
            year_end=2026,
            page_size=30,
        )
        route = adapter.build_search_url(query, configuration=configuration)
        if (
            event.get("query") != query
            or event.get("query_sha256") != base.text_digest(query)
            or event.get("effective_query") != configuration.effective_query
            or event.get("effective_query_sha256")
            != base.text_digest(configuration.effective_query)
            or event.get("navigation_route_characters") != len(route)
            or len(route) > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS
            or event.get("count_only") is not True
            or event.get("screenshots")
            != {
                key: str(path.relative_to(pilot_root))
                for key, path in screenshots.items()
            }
        ):
            raise RuntimeError(f"The split gate changed: {event['event_id']}")
        paths = (
            output,
            adapter.oatd_output_commit_marker_path(output),
            *screenshots.values(),
        )
        if any(os.path.lexists(path) for path in paths):
            raise RuntimeError(f"Refusing to overwrite split gate {event['event_id']}")
    if plan_path.resolve() in {
        (pilot_root / event["output"]).resolve() for event in events
    }:
        raise RuntimeError("The split-gate plan path is unsafe")
    return adapter, first_event, events


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> int:
    if os.path.lexists(receipt_path):
        raise RuntimeError(f"Refusing to overwrite {receipt_path}")
    plan = base.load(plan_path)
    adapter, first_event, events = validate_plan(plan, plan_path, pilot_root)
    not_before = base.parse_utc(
        plan["source_safety"]["first_source_request_not_before_utc"]
    )
    wait_seconds = max(0.0, (not_before - datetime.now(timezone.utc)).total_seconds())
    if wait_seconds:
        print(f"Waiting {wait_seconds:.1f} seconds for the OATD cooldown.", flush=True)
        time.sleep(wait_seconds)

    first_output = pilot_root / first_event["output"]
    outcomes: list[dict[str, Any]] = [
        {
            "event_id": "G1-MH",
            "adopted_from_initial_run": True,
            "return_code": 0,
            "valid_count_artifact": True,
            "total": 16,
            "strictly_below_p_baseline": True,
            "output": first_event["output"],
            "output_sha256": base.digest(first_output),
        }
    ]
    started = base.now()
    stopped = False
    for index, event in enumerate(events):
        if index:
            time.sleep(float(plan["source_safety"]["inter_event_delay_seconds"]))
        output = pilot_root / event["output"]
        event_started = base.now()
        timed_out = False
        try:
            completed = subprocess.run(
                base.command(event, output),
                check=False,
                capture_output=True,
                text=True,
                timeout=600,
            )
            return_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            timed_out = True
            return_code = 124
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
        valid = False
        total: int | None = None
        validation_error: str | None = None
        if return_code == 0 and output.is_file():
            try:
                total = prior.validate_count_marker(
                    adapter, base.load(output), event, output
                )
                valid = True
            except Exception as error:
                validation_error = " ".join(str(error).split())[:500]
        elif output.is_file():
            candidate = base.load(output).get("total")
            total = (
                candidate
                if isinstance(candidate, int) and not isinstance(candidate, bool)
                else None
            )
        marker = adapter.oatd_output_commit_marker_path(output)
        screenshots = base.expected_screenshots(output)
        outcome = {
            "event_id": event["event_id"],
            "adopted_from_initial_run": False,
            "started_at_utc": event_started,
            "completed_at_utc": base.now(),
            "return_code": return_code,
            "timed_out": timed_out,
            "valid_count_artifact": valid,
            "total": total,
            "strictly_below_p_baseline": isinstance(total, int) and total < 1249,
            "output": event["output"],
            "output_exists": output.is_file(),
            "output_sha256": base.digest(output) if output.is_file() else None,
            "marker_exists": marker.is_file(),
            "screenshots_exist": {
                key: path.is_file() for key, path in screenshots.items()
            },
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stdout_sha256": base.text_digest(stdout),
            "stderr_bytes": len(stderr.encode("utf-8")),
            "stderr_sha256": base.text_digest(stderr),
            "validation_error": validation_error,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "event": event["event_id"],
                    "return_code": return_code,
                    "total": total,
                    "valid": valid,
                }
            ),
            flush=True,
        )
        if not valid:
            stopped = True
            break

    success = not stopped and len(outcomes) == 8
    receipt = {
        "schema_version": SCHEMA,
        "source": plan["source"],
        "pilot": "005",
        "protocol_commit": split_queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(plan_path.relative_to(pilot_root)),
        "plan_sha256": base.digest(plan_path),
        "planned_gate_count": 8,
        "adopted_gate_count": 1,
        "started_at_utc": started,
        "completed_at_utc": base.now(),
        "completed_gate_count": len(outcomes),
        "source_events_in_split_continuation": len(outcomes) - 1,
        "stopped_after_failure": stopped,
        "success": success,
        "outcomes": outcomes,
    }
    base.write_new(receipt_path, receipt)
    return 0 if success else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args.plan, args.pilot_root, args.receipt)
    except Exception as error:
        print(" ".join(str(error).split())[:1000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
