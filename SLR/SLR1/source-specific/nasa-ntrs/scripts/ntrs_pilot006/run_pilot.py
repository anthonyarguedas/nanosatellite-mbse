#!/usr/bin/env python3
"""Execute NASA NTRS Pilot 006 maximal wildcard events."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ntrs-maximal-wildcard-pilot-run/v1"
PLAN_SCHEMA = "ntrs-maximal-wildcard-pilot-plan/v1"
EXPECTED_HELPER_SHA256 = "cc30630e511c2f37877250703666551138f5fe403b05777db3e3747916f34435"
HELPER_PATH = Path(__file__).resolve().parents[1] / "ntrs_pilot005" / "run_pilot.py"
if hashlib.sha256(HELPER_PATH.read_bytes()).hexdigest() != EXPECTED_HELPER_SHA256:
    raise RuntimeError("The pinned NTRS runner helper changed")
_spec = importlib.util.spec_from_file_location("ntrs_pilot006_runner_helper", HELPER_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {HELPER_PATH}")
_helper = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _helper
_spec.loader.exec_module(_helper)
ADAPTER = _helper.ADAPTER


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def command_for(
    event: dict[str, Any], *, attempt: int, output: Path, cdp_url: str
) -> list[str]:
    command = _helper.command_for(
        event, attempt=attempt, output=output, cdp_url=cdp_url
    )
    replacements = {
        "--prisma-run-id": f"pilot-ntrs-006-{event['event_id']}-attempt{attempt}",
        "--prisma-review-id": "slr1-ntrs-pilot006",
        "--prisma-partition-description": (
            f"NASA NTRS Pilot 006 {event['event_id']} attempt {attempt}"
        ),
    }
    for option, value in replacements.items():
        command[command.index(option) + 1] = value
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--settle-seconds", type=float, default=3.0)
    args = parser.parse_args()
    if args.settle_seconds < 0:
        raise SystemExit("--settle-seconds cannot be negative")
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url):
        raise SystemExit("Pilot 006 requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected Pilot 006 plan schema")
    adapter_hash = digest(ADAPTER)
    if adapter_hash != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The NTRS adapter changed after predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 9:
        raise SystemExit("Pilot 006 requires exactly nine events")

    started = now()
    event_outcomes = []
    source_attempt_count = 0
    stopped = False
    for event in events:
        attempts = []
        accepted_artifact: str | None = None
        for attempt, output_name in enumerate(event["attempt_outputs"], start=1):
            if source_attempt_count:
                time.sleep(args.settle_seconds)
            output = args.pilot_root / "searches" / output_name
            output.parent.mkdir(parents=True, exist_ok=True)
            occupied = [
                output,
                _helper.marker_path(output),
                *_helper.screenshot_paths(output).values(),
            ]
            if any(path.exists() or path.is_symlink() for path in occupied):
                raise SystemExit(
                    f"Refusing to overwrite attempt {attempt} for {event['event_id']}"
                )
            completed = subprocess.run(
                command_for(event, attempt=attempt, output=output, cdp_url=cdp_url),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=360,
            )
            source_attempt_count += 1
            summary = _helper.artifact_summary(output, event, adapter_hash)
            row = {
                "attempt": attempt,
                "exit_code": completed.returncode,
                "artifact": str(output.relative_to(args.pilot_root)),
                "stderr_sha256": hashlib.sha256(
                    completed.stderr.encode("utf-8")
                ).hexdigest(),
                "stderr_bytes": len(completed.stderr.encode("utf-8")),
                "screenshot_files_written": {
                    key: path.is_file()
                    for key, path in _helper.screenshot_paths(output).items()
                },
                **summary,
            }
            attempts.append(row)
            print(
                json.dumps(
                    {
                        "event": event["event_id"],
                        "attempt": attempt,
                        "exit_code": completed.returncode,
                        "total": summary.get("total"),
                        "valid": summary.get("valid"),
                        "retryable": summary.get("retryable"),
                    }
                ),
                flush=True,
            )
            if completed.returncode == 0 and summary["valid"]:
                accepted_artifact = row["artifact"]
                break
            if not summary["retryable"]:
                break
        success = accepted_artifact is not None
        event_outcomes.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "variant": event["variant"],
                "success": success,
                "accepted_artifact": accepted_artifact,
                "attempt_count": len(attempts),
                "attempts": attempts,
            }
        )
        if not success:
            stopped = True
            break

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "006",
        "source": "NASA Technical Reports Server (NTRS)",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "adapter": {
            "id": "search_ntrs",
            "version": plan.get("adapter", {}).get("version"),
            "sha256": adapter_hash,
        },
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "completed_event_count": len(event_outcomes),
        "source_attempt_count": source_attempt_count,
        "stopped_after_failure": stopped,
        "success": not stopped and len(event_outcomes) == len(events),
        "events": event_outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
