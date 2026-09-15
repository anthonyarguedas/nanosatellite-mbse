#!/usr/bin/env python3
"""Run all predeclared IAF Pilot 005 positive wildcard events."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_plan import (
    DATE_END,
    DATE_START,
    DEFAULT_OUTPUT,
    PILOT_ROOT,
    PROTOCOL_COMMIT,
    load,
    validate,
)

COLLECTOR = Path(__file__).with_name("collect_cell.py")
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def ledger_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.identity-ledger.json")


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def complete_existing(output: Path, query: str) -> bool:
    identity_path = ledger_path(output)
    commit_path = marker_path(output)
    try:
        artifact = load(output)
        identity = load(identity_path)
        marker = load(commit_path)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False
    metadata = artifact.get("output_metadata", {})
    receipt = metadata.get("prisma_search_run", {})
    compact = identity.get("compact_artifact", {})
    marker_json = marker.get("normalized_json", {})
    digest = file_sha256(output)
    return bool(
        artifact.get("executed_query") == query
        and artifact.get("do_not_merge") is True
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is False
        and receipt.get("completion_status") == "complete"
        and identity.get("schema_version")
        == "iaf-digital-library-pilot005-complete-identity-ledger/v1"
        and identity.get("query") == query
        and identity.get("diagnostic_only") is True
        and identity.get("do_not_merge") is True
        and compact.get("file_name") == output.name
        and compact.get("sha256") == digest
        and compact.get("bytes") == output.stat().st_size
        and compact.get("commit_marker") == commit_path.name
        and marker.get("schema") == "academic_search_output_commit_marker_v1"
        and marker_json.get("sha256") == digest
        and marker_json.get("bytes") == output.stat().st_size
    )


def failure_path(root: Path, event_id: str, attempt: int) -> Path:
    return (
        root
        / "searches"
        / "failures"
        / f"{event_id}.attempt-{attempt:02d}.NON_MERGEABLE_FAILURE.json"
    )


def collector_command(
    event: dict[str, Any],
    output: Path,
    failure: Path,
    *,
    attempt: int,
    timeout: float,
    page_delay: float,
    retries: int,
) -> list[str]:
    return [
        "uv",
        "run",
        str(COLLECTOR),
        "--query",
        event["query"],
        "--output-path",
        str(output),
        "--identity-ledger-path",
        str(ledger_path(output)),
        "--failure-path",
        str(failure),
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--limit",
        "5000",
        "--max-pages",
        "100",
        "--page-size",
        "500",
        "--passes",
        "2",
        "--timeout",
        str(timeout),
        "--page-delay-seconds",
        str(page_delay),
        "--retries",
        str(retries),
        "--prisma-run-id",
        f"iaf-p005-{event['event_id']}-attempt-{attempt:02d}",
        "--prisma-review-id",
        "slr1-iaf-pilot-005",
        "--prisma-strategy-reference",
        "slr1-iaf-positive-wildcard-diagnostic-v1",
        "--prisma-strategy-version",
        PROTOCOL_COMMIT,
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        "BG1-wildcard-diagnostic",
        "--prisma-partition-label",
        "BG1 wildcard diagnostic",
        "--prisma-partition-description",
        event["purpose"],
    ]


def write_receipt(
    path: Path,
    *,
    root: Path,
    plan_path: Path,
    started: str,
    events: list[dict[str, Any]],
    outcomes: list[dict[str, Any]],
    status: str,
) -> None:
    failures = sorted((root / "searches" / "failures").glob("*.json"))
    completed_ids = {
        item["event_id"]
        for item in outcomes
        if item.get("status") in ("complete", "reused_existing")
    }
    payload = {
        "schema_version": "iaf-digital-library-pilot005-run-receipt/v1",
        "source": "IAF Digital Library",
        "pilot": "005",
        "status": status,
        "diagnostic_only": True,
        "do_not_merge": True,
        "started_at_utc": started,
        "updated_at_utc": now(),
        "event_plan": relative(plan_path, root),
        "predeclared_event_count": len(events),
        "completed_event_count": len(completed_ids),
        "outcome_count": len(outcomes),
        "source_attempt_count": sum(1 for item in outcomes if "attempt" in item),
        "reused_existing_event_count": sum(
            1 for item in outcomes if item.get("status") == "reused_existing"
        ),
        "retained_failure_artifacts": [relative(item, root) for item in failures],
        "outcomes": outcomes,
    }
    if status == "complete":
        payload["completed_at_utc"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--process-timeout", type=float, default=360.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--max-attempts-per-event", type=int, default=3)
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    plan_path = args.plan.expanduser().resolve()
    root = args.pilot_root.expanduser().resolve()
    receipt_path = args.receipt.expanduser().resolve()
    plan = load(plan_path)
    errors = validate(plan)
    if errors:
        parser.error("; ".join(errors))
    if args.max_attempts_per_event < 1:
        parser.error("--max-attempts-per-event must be positive")
    if args.max_events is not None and args.max_events < 1:
        parser.error("--max-events must be positive")

    events = plan["events"]
    started = now()
    outcomes: list[dict[str, Any]] = []
    selected = events[: args.max_events] if args.max_events is not None else events
    for event in selected:
        output = root / "searches" / event["output"]
        if output.exists() or ledger_path(output).exists():
            status = (
                "reused_existing"
                if complete_existing(output, event["query"])
                else "invalid_existing"
            )
            outcomes.append(
                {
                    "event_id": event["event_id"],
                    "status": status,
                    "output": relative(output, root),
                    "completed_at_utc": now(),
                }
            )
            print(f"{event['event_id']}: {status}", flush=True)
            if status != "reused_existing":
                write_receipt(
                    receipt_path,
                    root=root,
                    plan_path=plan_path,
                    started=started,
                    events=events,
                    outcomes=outcomes,
                    status="stopped_on_existing_artifact_error",
                )
                return 1
            continue

        output.parent.mkdir(parents=True, exist_ok=True)
        existing_failures = len(
            list(
                (root / "searches" / "failures").glob(
                    f"{event['event_id']}.attempt-*.json"
                )
            )
        )
        event_complete = False
        for offset in range(args.max_attempts_per_event):
            attempt = existing_failures + offset + 1
            failure = failure_path(root, event["event_id"], attempt)
            failure.parent.mkdir(parents=True, exist_ok=True)
            command = collector_command(
                event,
                output,
                failure,
                attempt=attempt,
                timeout=args.timeout,
                page_delay=args.page_delay_seconds,
                retries=args.retries,
            )
            if args.dry_run:
                print(json.dumps({"event_id": event["event_id"], "command": command}))
                outcomes.append({"event_id": event["event_id"], "status": "dry_run"})
                event_complete = True
                break
            print(f"{event['event_id']}: attempt {attempt}", flush=True)
            event_started = now()
            environment = os.environ.copy()
            environment.setdefault("PYTHONUNBUFFERED", "1")
            try:
                process = subprocess.run(
                    command,
                    cwd=Path.cwd(),
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=args.process_timeout,
                )
                complete = process.returncode == 0 and complete_existing(
                    output, event["query"]
                )
                outcome = {
                    "event_id": event["event_id"],
                    "attempt": attempt,
                    "started_at_utc": event_started,
                    "completed_at_utc": now(),
                    "return_code": process.returncode,
                    "status": "complete" if complete else "failed",
                    "output": relative(output, root),
                    "failure_artifact": relative(failure, root)
                    if failure.exists()
                    else None,
                }
                if not complete:
                    lines = (
                        (process.stderr or process.stdout or "").strip().splitlines()
                    )
                    outcome["diagnostic"] = (
                        lines[-1][:240] if lines else "no child diagnostic"
                    )
                outcomes.append(outcome)
                if complete:
                    print(f"{event['event_id']}: complete", flush=True)
                    event_complete = True
                    break
                print(f"{event['event_id']}: retained failed attempt", flush=True)
            except subprocess.TimeoutExpired:
                outcomes.append(
                    {
                        "event_id": event["event_id"],
                        "attempt": attempt,
                        "started_at_utc": event_started,
                        "completed_at_utc": now(),
                        "status": "process_timeout",
                        "output": relative(output, root),
                    }
                )
                print(f"{event['event_id']}: process timeout", flush=True)
            write_receipt(
                receipt_path,
                root=root,
                plan_path=plan_path,
                started=started,
                events=events,
                outcomes=outcomes,
                status="running",
            )
        if not event_complete:
            write_receipt(
                receipt_path,
                root=root,
                plan_path=plan_path,
                started=started,
                events=events,
                outcomes=outcomes,
                status="stopped_on_source_or_adapter_failure",
            )
            return 1

    status = "complete" if len(selected) == len(events) else "bounded_stop"
    write_receipt(
        receipt_path,
        root=root,
        plan_path=plan_path,
        started=started,
        events=events,
        outcomes=outcomes,
        status=status,
    )
    print(json.dumps({"status": status, "completed_events": len(selected)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
