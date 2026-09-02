#!/usr/bin/env python3
"""Run the predeclared Pilot 004 connection recovery and remaining events."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any

from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, file_sha256, load
from build_recovery_plan import OUTPUT as RECOVERY_PLAN
from run_pilot import (
    artifact_summary,
    command_for,
    now,
    safe_tail,
    screenshot_paths,
    write_create_only,
)

SCHEMA = "wos-current-schedule-wildcard-pilot-recovery-run/v1"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "recovery-run-receipt.json"


def run_event(event: dict[str, Any], output: Path, cdp_url: str) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    occupied = [output, *screenshot_paths(output).values()]
    if any(os.path.lexists(path) for path in occupied):
        raise FileExistsError(f"Refusing to overwrite source evidence for {event['event_id']}")
    completed = subprocess.run(
        command_for(event, output=output, cdp_url=cdp_url),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    summary = artifact_summary(output, event)
    outcome = {
        "event_id": event["event_id"],
        "base_event_id": event.get("base_event_id", event["event_id"]),
        "partition_id": event["partition_id"],
        "variant": event["variant"],
        "exit_code": completed.returncode,
        "artifact": str(output.relative_to(PILOT_ROOT)),
        **summary,
    }
    if completed.returncode != 0 or summary.get("valid") is not True:
        outcome["adapter_stderr_tail"] = safe_tail(completed.stderr)
    print(
        json.dumps(
            {
                "event": event["event_id"],
                "exit_code": completed.returncode,
                "total": summary.get("total"),
                "valid": summary.get("valid"),
            }
        ),
        flush=True,
    )
    return outcome


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-plan", type=Path, default=RECOVERY_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--initial-settle-seconds", type=float, default=15.0)
    parser.add_argument("--settle-seconds", type=float, default=2.0)
    args = parser.parse_args()
    if args.initial_settle_seconds < 0 or args.settle_seconds < 0:
        raise SystemExit("Settle intervals cannot be negative")
    if os.path.lexists(args.receipt):
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    recovery = load(args.recovery_plan)
    plan = load(DEFAULT_OUTPUT)
    if (
        recovery.get("schema_version")
        != "wos-current-schedule-wildcard-pilot-recovery-plan/v1"
        or recovery.get("adapter", {}).get("sha256") != file_sha256(ADAPTER)
        or recovery.get("original_plan_sha256") != file_sha256(DEFAULT_OUTPUT)
    ):
        raise SystemExit("Recovery plan or adapter binding changed")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise SystemExit("Recovery requires a loopback browser endpoint")

    by_id = {item["event_id"]: item for item in plan["events"]}
    base_id = recovery["unchanged_event"]["event_id"]
    base_event = dict(by_id[base_id])
    started = now()
    outcomes: list[dict[str, Any]] = []
    selected_artifacts: dict[str, str] = {}
    if args.initial_settle_seconds:
        time.sleep(args.initial_settle_seconds)

    retry_success = False
    for attempt_number, relative_output in enumerate(
        recovery["retry_policy"]["outputs"], start=2
    ):
        retry_event = {
            **base_event,
            "event_id": f"{base_id}-attempt{attempt_number}",
            "base_event_id": base_id,
        }
        outcome = run_event(
            retry_event,
            PILOT_ROOT / "searches" / relative_output,
            cdp_url,
        )
        outcomes.append(outcome)
        if outcome.get("valid") is True and outcome.get("exit_code") == 0:
            selected_artifacts[base_id] = outcome["artifact"]
            retry_success = True
            break
        if args.settle_seconds:
            time.sleep(args.settle_seconds)

    stopped = not retry_success
    if retry_success:
        for event_id in recovery["remaining_original_events"]:
            if args.settle_seconds:
                time.sleep(args.settle_seconds)
            event = by_id[event_id]
            output = PILOT_ROOT / "searches" / event["output"]
            outcome = run_event(event, output, cdp_url)
            outcomes.append(outcome)
            if outcome.get("valid") is not True or outcome.get("exit_code") != 0:
                stopped = True
                break
            selected_artifacts[event_id] = outcome["artifact"]

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Web of Science Core Collection",
        "diagnostic_only": True,
        "do_not_merge": True,
        "recovery_plan": str(args.recovery_plan.relative_to(PILOT_ROOT)),
        "recovery_plan_sha256": file_sha256(args.recovery_plan),
        "adapter": {
            "id": "search_web_of_science",
            "version": plan["adapter"]["version"],
            "sha256": file_sha256(ADAPTER),
        },
        "started_at_utc": started,
        "completed_at_utc": now(),
        "retry_succeeded": retry_success,
        "stopped_after_failure": stopped,
        "success": retry_success and not stopped and len(selected_artifacts) == 7,
        "selected_artifacts": selected_artifacts,
        "outcomes": outcomes,
    }
    write_create_only(args.receipt, receipt)
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
