#!/usr/bin/env python3
"""Run the predeclared retry-safe continuation for NASA NTRS Pilot 004."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run_pilot

SCHEMA = "ntrs-post-proximity-wildcard-continuation-run/v1"
PLAN_SCHEMA = "ntrs-post-proximity-wildcard-continuation-plan/v1"
ADAPTER = run_pilot.ADAPTER


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def retryable_failure(path: Path, returncode: int) -> bool:
    if returncode == 0 or not path.is_file():
        return False
    value = load(path)
    metadata = value.get("output_metadata", {})
    return bool(
        value.get("total") is None
        and value.get("results") == []
        and metadata.get("status") == "error"
        and metadata.get("merge_eligible") is False
    )


def command_for(
    event: dict[str, Any], *, attempt: int, output: Path, cdp_url: str
) -> list[str]:
    command = run_pilot.command_for(event, output=output, cdp_url=cdp_url)
    run_index = command.index("--prisma-run-id") + 1
    command[run_index] = f"{command[run_index]}-attempt{attempt}"
    description_index = command.index("--prisma-partition-description") + 1
    command[description_index] = f"{command[description_index]} attempt {attempt}"
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--settle-seconds", type=float, default=2.0)
    args = parser.parse_args()

    if args.settle_seconds < 0:
        raise SystemExit("--settle-seconds cannot be negative")
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url):
        raise SystemExit("Pilot 004 requires a loopback browser endpoint")

    plan = load(args.plan)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected continuation plan schema")
    adapter_hash = digest(ADAPTER)
    if adapter_hash != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The NTRS adapter changed after continuation predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 18:
        raise SystemExit("Continuation requires exactly 18 semantic events")

    started = now()
    event_outcomes: list[dict[str, Any]] = []
    attempt_count = 0
    stopped = False
    for event_index, event in enumerate(events):
        attempts: list[dict[str, Any]] = []
        accepted_artifact: str | None = None
        for attempt, output_name in enumerate(event["attempt_outputs"], start=1):
            if attempt_count or event_index:
                time.sleep(args.settle_seconds)
            output = args.pilot_root / "searches" / output_name
            output.parent.mkdir(parents=True, exist_ok=True)
            occupied = [
                output,
                run_pilot.marker_path(output),
                *run_pilot.screenshot_paths(output).values(),
            ]
            if any(path.exists() or path.is_symlink() for path in occupied):
                raise SystemExit(
                    f"Refusing to overwrite attempt {attempt} for {event['event_id']}"
                )
            completed = subprocess.run(
                command_for(
                    event,
                    attempt=attempt,
                    output=output,
                    cdp_url=cdp_url,
                ),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=360,
            )
            attempt_count += 1
            summary = run_pilot.artifact_summary(
                output, event["query"], adapter_hash
            )
            retryable = retryable_failure(output, completed.returncode)
            screenshot_files = {
                key: image.is_file()
                for key, image in run_pilot.screenshot_paths(output).items()
            }
            row = {
                "attempt": attempt,
                "exit_code": completed.returncode,
                "artifact": str(output.relative_to(args.pilot_root)),
                "stderr_sha256": hashlib.sha256(
                    completed.stderr.encode("utf-8")
                ).hexdigest(),
                "stderr_bytes": len(completed.stderr.encode("utf-8")),
                "retryable_null_failure": retryable,
                "screenshot_files_written": screenshot_files,
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
                        "retryable": retryable,
                    }
                ),
                flush=True,
            )
            if completed.returncode == 0 and summary.get("valid") is True:
                accepted_artifact = row["artifact"]
                break
            if not retryable:
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
        "pilot": "004",
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
        "source_attempt_count": attempt_count,
        "stopped_after_failure": stopped,
        "success": not stopped and len(event_outcomes) == len(events),
        "events": event_outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
