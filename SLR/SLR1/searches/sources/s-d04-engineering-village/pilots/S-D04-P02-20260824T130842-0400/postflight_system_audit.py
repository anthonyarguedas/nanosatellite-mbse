#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Create a redacted P02 power/caffeinate/sleep postflight receipt.

System logs are read only in process.  This script emits counts and checksums,
never raw log lines, process identifiers, commands, or private browser data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PILOT_ID = "S-D04-P02-20260824T130842-0400"
RUNNER_MARKER = "pi-subagent-ev-p02-20260824-130658-17341-21925/prompt.md"
SLEEP_WAKE = re.compile(r"\b(?:sleep|wake)\b", re.IGNORECASE)
PMSET_TIMESTAMP = re.compile(r"\b(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})(?:\.\d+)?\b")


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_text(arguments: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(arguments, text=True, capture_output=True, check=False)
        return completed.returncode, completed.stdout
    except Exception:
        return 127, ""


def count_pmset_events(text: str, start: datetime, end: datetime) -> int:
    local_start = start.astimezone().replace(tzinfo=None)
    local_end = end.astimezone().replace(tzinfo=None)
    count = 0
    for line in text.splitlines():
        if not SLEEP_WAKE.search(line):
            continue
        match = PMSET_TIMESTAMP.search(line)
        if match is None:
            continue
        try:
            observed = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if local_start <= observed <= local_end:
            count += 1
    return count


def count_log_events(start: datetime, end: datetime) -> tuple[int | None, bool]:
    # macOS `log show` accepts these bounded wall-clock values, while the
    # UTC-offset spellings are rejected by this host's command-line parser.
    start_arg = start.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    end_arg = end.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    status, output = run_text(
        [
            "log",
            "show",
            "--style",
            "syslog",
            "--start",
            start_arg,
            "--end",
            end_arg,
            "--predicate",
            'process == "loginwindow"',
        ]
    )
    if status != 0:
        return None, False
    return sum(1 for line in output.splitlines() if SLEEP_WAKE.search(line)), True


def bool_process(marker: str) -> bool:
    try:
        return subprocess.run(["pgrep", "-f", marker], capture_output=True, check=False).returncode == 0
    except Exception:
        return False


def receipt(args: argparse.Namespace) -> dict[str, Any]:
    g01 = json.loads(Path(args.g01_receipt).read_text(encoding="utf-8"))
    start = load_timestamp(g01.get("captured_at"))
    end = load_timestamp(g01.get("ended_at"))
    if end < start:
        raise ValueError
    caffeinate_text = Path(args.caffeinate_receipt).read_text(encoding="utf-8", errors="replace")
    battery_status, battery = run_text(["pmset", "-g", "batt"])
    assertions_status, assertions = run_text(["pmset", "-g", "assertions"])
    pmset_status, pmset_log = run_text(["pmset", "-g", "log"])
    pmset_events = count_pmset_events(pmset_log, start, end) if pmset_status == 0 else None
    login_events, login_checked = count_log_events(start, end)
    baselines = [Path(args.pmset_baseline), Path(args.loginwindow_baseline)]
    baseline_entries = [
        {"name": path.name, "sha256": sha256(path), "read_without_copying": True}
        for path in baselines
    ]
    receipt: dict[str, Any] = {
        "schema_version": "slr1-engineering-village-system-postflight/v1",
        "pilot_id": PILOT_ID,
        "captured_at": iso_now(),
        "live_source_window": {
            "started_at": start.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "ended_at": end.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "operation": "G01 non-query owned-page route probe only",
        },
        "preflight_system_baselines": baseline_entries,
        "power": {
            "current_pmset_battery_query_succeeded": battery_status == 0,
            "source": "AC Power" if "Now drawing from 'AC Power'" in battery else "not_ac_or_unavailable",
        },
        "caffeinate": {
            "preflight_receipt_inspected": True,
            "preflight_receipt_names_runner": RUNNER_MARKER in caffeinate_text,
            "preflight_receipt_required_assertions_present": all(
                marker in caffeinate_text
                for marker in (
                    "PreventDiskIdle                1",
                    "PreventUserIdleDisplaySleep    1",
                    "PreventSystemSleep             1",
                    "PreventUserIdleSystemSleep     1",
                )
            ),
            "current_assertion_query_succeeded": assertions_status == 0,
            "current_prevent_system_sleep_assertion_present": "PreventSystemSleep             1" in assertions,
            "current_runner_caffeinate_process_observed": bool_process(RUNNER_MARKER),
            "note": "Process-scoped caffeinate does not claim protection from manual or clamshell sleep.",
        },
        "sleep_wake_events_during_live_source_window": {
            "pmset_log_checked": pmset_status == 0,
            "pmset_sleep_wake_event_count": pmset_events,
            "loginwindow_log_checked": login_checked,
            "loginwindow_sleep_wake_event_count": login_events,
            "query": "timestamp-bounded case-insensitive Sleep/Wake marker count; raw system-event lines not retained",
            "conclusion": (
                "No Sleep/Wake markers observed in either available timestamp-bounded source."
                if pmset_events == 0 and login_events == 0
                else "Sleep/Wake status is nonzero or unresolved; see counts."
            ),
        },
        "retention_exclusions": ["raw_system_event_logs", "process_id", "process_command", "raw_target_id", "browser_url", "source_page_content"],
    }
    receipt["ended_at"] = iso_now()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a safe P02 system postflight receipt.")
    parser.add_argument("--g01-receipt", required=True)
    parser.add_argument("--caffeinate-receipt", required=True)
    parser.add_argument("--pmset-baseline", required=True)
    parser.add_argument("--loginwindow-baseline", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit("refusing to overwrite an existing system postflight receipt")
    try:
        data = receipt(args)
    except Exception:
        data = {
            "schema_version": "slr1-engineering-village-system-postflight/v1",
            "pilot_id": PILOT_ID,
            "captured_at": iso_now(),
            "postflight_status": "unresolved",
            "error_category": "safe_system_audit_failed",
            "retention_exclusions": ["raw_system_event_logs", "process_id", "process_command", "raw_target_id", "browser_url", "source_page_content"],
        }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
