#!/usr/bin/env python3
"""Run Pilot 005's predeclared A2 split and remaining wildcard events."""

from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Any

from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, load, sha256_file
from build_recovery_plan import OUTPUT as RECOVERY_PLAN
from run_pilot import (
    artifact_summary,
    command,
    safe_tail,
    screenshot_paths,
    write_create_only,
)

SCHEMA = "wos-broad-wildcard-pilot-recovery-run/v1"
OUTPUT = PILOT_ROOT / "searches" / "recovery-run-receipt.json"


def run_with_attempts(
    event: dict[str, Any], outputs: list[str], cdp_url: str
) -> tuple[list[dict[str, Any]], str | None]:
    outcomes: list[dict[str, Any]] = []
    for attempt, relative in enumerate(outputs, start=1):
        output = PILOT_ROOT / "searches" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        if any(os.path.lexists(path) for path in (output, *screenshot_paths(output))):
            raise FileExistsError(f"Refusing to overwrite {output}")
        completed = subprocess.run(
            command(event, output, cdp_url, attempt),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        summary = artifact_summary(output, event)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event.get("cell_id"),
            "attempt": attempt,
            "artifact": str(output.relative_to(PILOT_ROOT)),
            "exit_code": completed.returncode,
            **summary,
        }
        if completed.returncode != 0 or summary.get("valid") is not True:
            outcome["adapter_stderr_tail"] = safe_tail(completed.stderr)
        outcomes.append(outcome)
        print(json.dumps({"event": event["event_id"], "cell": event.get("cell_id"), "attempt": attempt, "exit_code": completed.returncode, "total": summary.get("total"), "valid": summary.get("valid")}), flush=True)
        if completed.returncode == 0 and summary.get("valid") is True:
            return outcomes, outcome["artifact"]
        try:
            failure = load(output)
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            failure = {}
        if failure.get("total") is not None:
            break
        time.sleep(12)
    return outcomes, None


def main() -> int:
    if os.path.lexists(OUTPUT):
        raise SystemExit(f"Refusing to overwrite {OUTPUT}")
    recovery = load(RECOVERY_PLAN)
    plan = load(DEFAULT_OUTPUT)
    if (
        recovery.get("schema_version") != "wos-broad-wildcard-pilot-recovery-plan/v1"
        or recovery.get("adapter", {}).get("sha256") != sha256_file(ADAPTER)
        or recovery.get("original_plan_sha256") != sha256_file(DEFAULT_OUTPUT)
    ):
        raise SystemExit("Recovery plan or adapter binding changed")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise SystemExit("Recovery requires a loopback browser endpoint")
    by_id = {item["event_id"]: item for item in plan["events"]}
    initial = load(PILOT_ROOT / "searches" / "run-receipt.json")
    selected: dict[str, Any] = dict(initial.get("selected_artifacts", {}))
    outcomes: list[dict[str, Any]] = []
    stopped = False

    time.sleep(20)
    a2_selected = []
    for cell in recovery["repair"]["cells"]:
        event = {
            "event_id": f"broad-wildcard-A2-{cell['cell_id']}",
            "partition_id": "A2",
            "variant": "broad_wildcard_cell",
            "query": cell["query"],
        }
        cell_outcomes, winner = run_with_attempts(
            event, cell["attempt_outputs"], cdp_url
        )
        outcomes.extend(cell_outcomes)
        if winner is None:
            stopped = True
            break
        a2_selected.append(winner)
        time.sleep(3)
    if not stopped:
        selected["A2"] = a2_selected

    if not stopped:
        for event_id in recovery["remaining_original_events"]:
            time.sleep(3)
            event = by_id[event_id]
            event_outcomes, winner = run_with_attempts(
                event, event["attempt_outputs"], cdp_url
            )
            outcomes.extend(event_outcomes)
            if winner is None:
                stopped = True
                break
            selected[event["partition_id"]] = winner

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "Web of Science Core Collection",
        "diagnostic_only": True,
        "do_not_merge": True,
        "recovery_plan": str(RECOVERY_PLAN.relative_to(PILOT_ROOT)),
        "recovery_plan_sha256": sha256_file(RECOVERY_PLAN),
        "adapter": {"id": "search_web_of_science", "version": "2", "sha256": sha256_file(ADAPTER)},
        "a2_split_completed": len(a2_selected) == 2,
        "successful_partition_count": len(selected),
        "attempt_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": not stopped and len(selected) == 9,
        "selected_artifacts": selected,
        "outcomes": outcomes,
    }
    write_create_only(OUTPUT, receipt)
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
