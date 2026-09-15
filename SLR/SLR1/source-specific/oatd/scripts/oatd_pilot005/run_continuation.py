#!/usr/bin/env python3
"""Continue OATD Pilot 005 after correcting count-marker validation."""

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

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-005-gate-count-continuation-run/v1"
PLAN_SCHEMA = "oatd-pilot-005-gate-count-continuation-plan/v1"


def validate_count_marker(
    adapter: Any, artifact: dict[str, Any], event: dict[str, Any], output: Path
) -> int:
    """Validate a marker-bound nonmergeable count without asking merge admission."""
    total = artifact.get("total")
    metadata = artifact.get("output_metadata")
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("requested_query") != event["query"]
        or artifact.get("executed_query") != event["effective_query"]
        or not isinstance(total, int)
        or isinstance(total, bool)
        or not 0 <= total < 1249
        or artifact.get("results") != []
        or artifact.get("do_not_merge") is not True
        or not isinstance(metadata, dict)
        or metadata.get("status") != "count_only"
        or metadata.get("count_only") is not True
        or metadata.get("observed_exact_query_echo") is not True
        or metadata.get("merge_eligible") is not False
        or metadata.get("normalized_merge_eligible") is not False
        or metadata.get("page_size") != 30
        or metadata.get("earliest_year_filter") != 2011
        or metadata.get("latest_year_filter") != 2026
    ):
        raise RuntimeError(f"The OATD {event['event_id']} count artifact is invalid")
    screenshots = base.expected_screenshots(output)
    receipt = metadata.get("screenshots")
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema_version") != "oatd-automatic-screenshots/v1"
        or receipt.get("automatic") is not True
        or receipt.get("opt_out_available") is not False
        or receipt.get("same_directory_as_json") is not True
    ):
        raise RuntimeError(f"The OATD {event['event_id']} screenshots are invalid")
    for key, path in screenshots.items():
        evidence = receipt.get(key)
        if (
            not path.is_file()
            or not isinstance(evidence, dict)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != base.digest(path)
            or evidence.get("full_page") is not True
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            raise RuntimeError(f"The OATD {event['event_id']} {key} is invalid")

    marker_path = adapter.oatd_output_commit_marker_path(output)
    marker = base.load(marker_path)
    transaction_id = marker.get("transaction_id")
    normalized_json = marker.get("normalized_json")
    if (
        set(marker)
        != {
            "schema",
            "transaction_id",
            "lexical_output_binding",
            "normalized_json",
            "normalized_csv",
        }
        or marker.get("schema") != "oatd_output_commit_marker_v1"
        or not isinstance(transaction_id, str)
        or len(transaction_id) != 64
        or metadata.get("publication_transaction_id") != transaction_id
        or metadata.get("merge_transaction_id") != transaction_id
        or metadata.get("publication_commit_protocol") != "oatd_output_commit_marker_v1"
        or metadata.get("publication_commit_state") != "marker_required"
        or metadata.get("merge_commit_protocol") != "oatd_output_commit_marker_v1"
        or metadata.get("merge_commit_state") != "marker_required"
        or not isinstance(normalized_json, dict)
        or normalized_json.get("sha256") != base.digest(output)
        or normalized_json.get("bytes") != output.stat().st_size
        or marker.get("normalized_csv") is not None
        or not adapter._output._merge_contract.verify_lexical_output_binding(
            marker.get("lexical_output_binding"), output
        )
    ):
        raise RuntimeError(f"The OATD {event['event_id']} count marker is invalid")
    # Generic merge admission must remain false for a count-only artifact.
    if adapter.verify_commit_gated_publication(output, artifact):
        raise RuntimeError(f"The OATD {event['event_id']} count became mergeable")
    return total


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != "005"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or [event.get("event_id") for event in events] != list(queries.GATE_IDS[1:])
    ):
        raise RuntimeError("Unexpected OATD Pilot 005 continuation plan")
    adapter = base.load_adapter()
    adapter_plan = plan.get("adapter")
    if (
        not isinstance(adapter_plan, dict)
        or adapter_plan.get("id") != adapter.ADAPTER_ID
        or adapter_plan.get("version") != adapter.ADAPTER_VERSION
    ):
        raise RuntimeError("The OATD continuation adapter identity changed")
    files = adapter_plan.get("files")
    for name, path in base.ADAPTER_FILES.items():
        descriptor = files.get(name) if isinstance(files, dict) else None
        if not isinstance(descriptor, dict) or descriptor.get("sha256") != base.digest(
            path
        ):
            raise RuntimeError(f"The OATD continuation adapter changed: {name}")
    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("The OATD continuation script bindings are missing")
    for relative, expected in scripts.items():
        path = base.REPOSITORY_ROOT / relative
        if not path.is_file() or base.digest(path) != expected:
            raise RuntimeError(f"An OATD continuation script changed: {relative}")
    for key in ("initial_plan", "initial_run"):
        descriptor = plan.get(key)
        path = (
            base.REPOSITORY_ROOT / descriptor.get("path", "")
            if isinstance(descriptor, dict)
            else Path()
        )
        if (
            not isinstance(descriptor, dict)
            or not path.is_file()
            or base.digest(path) != descriptor.get("sha256")
        ):
            raise RuntimeError(f"The OATD continuation {key} changed")
    initial_plan = base.load(base.REPOSITORY_ROOT / plan["initial_plan"]["path"])
    adopted = plan.get("adopted_initial_event")
    first_event = initial_plan.get("events", [{}])[0]
    if (
        not isinstance(adopted, dict)
        or adopted.get("event_id") != "G1-MH"
        or adopted.get("source_return_code") != 0
        or adopted.get("total") != 16
        or first_event.get("event_id") != "G1-MH"
    ):
        raise RuntimeError("The adopted OATD G1 event is invalid")
    output = pilot_root / first_event["output"]
    for descriptor_key, path in (
        ("artifact_sha256", output),
        ("marker_sha256", adapter.oatd_output_commit_marker_path(output)),
        ("search_page_sha256", base.expected_screenshots(output)["search_page"]),
        ("results_page_sha256", base.expected_screenshots(output)["results_page"]),
    ):
        if not path.is_file() or base.digest(path) != adopted.get(descriptor_key):
            raise RuntimeError(
                f"The adopted OATD G1 evidence changed: {descriptor_key}"
            )
    validate_count_marker(adapter, base.load(output), first_event, output)

    for event in events:
        original = next(
            candidate
            for candidate in initial_plan["events"]
            if candidate["event_id"] == event["event_id"]
        )
        if event != original:
            raise RuntimeError(
                f"The OATD continuation event changed: {event['event_id']}"
            )
        output = pilot_root / event["output"]
        paths = (
            output,
            adapter.oatd_output_commit_marker_path(output),
            *base.expected_screenshots(output).values(),
        )
        if any(os.path.lexists(path) for path in paths):
            raise RuntimeError(
                f"Refusing to overwrite OATD {event['event_id']} evidence"
            )
    if plan_path.resolve() == output.resolve():
        raise RuntimeError("The OATD continuation plan path is unsafe")
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
        print(
            f"Waiting {wait_seconds:.1f} seconds before the continuation.", flush=True
        )
        time.sleep(wait_seconds)

    first_output = pilot_root / first_event["output"]
    first_total = validate_count_marker(
        adapter, base.load(first_output), first_event, first_output
    )
    outcomes: list[dict[str, Any]] = [
        {
            "event_id": "G1-MH",
            "adopted_from_initial_run": True,
            "return_code": 0,
            "valid_count_artifact": True,
            "total": first_total,
            "strictly_below_p_baseline": first_total < 1249,
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
                total = validate_count_marker(adapter, base.load(output), event, output)
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

    success = not stopped and len(outcomes) == 5
    receipt = {
        "schema_version": SCHEMA,
        "source": plan["source"],
        "pilot": "005",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(plan_path.relative_to(pilot_root)),
        "plan_sha256": base.digest(plan_path),
        "started_at_utc": started,
        "completed_at_utc": base.now(),
        "planned_gate_count": 5,
        "completed_gate_count": len(outcomes),
        "source_events_in_continuation": len(outcomes) - 1,
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
