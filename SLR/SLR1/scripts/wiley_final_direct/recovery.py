#!/usr/bin/env python3
"""Run the third predeclared recovery for two null Wiley final cells."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Mapping
from urllib.parse import urlparse

import corrective
import run as base


SCRIPT_PATH = Path(__file__).resolve()
PLAN_SCHEMA = "slr1-wiley-online-library-final-direct-recovery-plan/v1"
EVENT_RECEIPT_SCHEMA = "slr1-wiley-online-library-final-direct-recovery-event/v1"
RUN_RECEIPT_SCHEMA = "slr1-wiley-online-library-final-direct-recovery-run/v1"
SEQUENCE = 3
EVENT_KEYS = (("A2", "mb"), ("B2", "direct"))


def recovery_event_id(partition_id: str, cell_id: str) -> str:
    suffix = "" if cell_id == "direct" else f"-{cell_id}"
    return f"final-main-{partition_id}{suffix}-wiley-online-library-{SEQUENCE:03d}"


def build_plan(
    initial_plan_path: Path,
    initial_receipt_path: Path,
    prior_plan_path: Path,
    interruption_path: Path,
) -> dict[str, Any]:
    initial = base.load(initial_plan_path)
    prior = base.load(prior_plan_path)
    interruption = base.load(interruption_path)
    if base.validate_plan(initial):
        raise ValueError("The initial Wiley final plan failed structural validation")
    if corrective.validate_corrective_plan(prior):
        raise ValueError("The second Wiley corrective plan failed structural validation")
    if not (
        interruption.get("schema_version")
        == "slr1-wiley-online-library-final-direct-corrective-interruption/v1"
        and interruption.get("plan_sha256") == base.digest(prior_plan_path)
        and interruption.get("status") == "interrupted"
        and interruption.get("accepted_source_cell_count") == 0
    ):
        raise ValueError("The second Wiley corrective interruption is not established")
    prior_events = {
        (event["partition_id"], event["cell_id"]): event for event in prior["events"]
    }
    interruption_outcomes = {
        (outcome.get("partition_id"), outcome.get("cell_id")): outcome
        for outcome in interruption.get("outcomes", [])
        if isinstance(outcome, Mapping)
    }
    events: list[dict[str, Any]] = []
    for key in EVENT_KEYS:
        source = prior_events.get(key)
        outcome = interruption_outcomes.get(key)
        if source is None or outcome is None or outcome.get("source_total") is not None:
            raise ValueError(f"The prior null event for {key} is not established")
        partition_id, cell_id = key
        event_id = recovery_event_id(partition_id, cell_id)
        events.append(
            {
                **{
                    field: source[field]
                    for field in (
                        "parent_event_id",
                        "partition_id",
                        "cell_id",
                        "branch",
                        "query",
                        "query_sha256",
                        "query_characters",
                        "date_start",
                        "date_end",
                        "field",
                        "content",
                        "sort",
                        "passes",
                        "limit",
                        "max_pages",
                        "max_source_total",
                        "max_snapshot_attempts",
                        "timeout_seconds",
                        "page_delay_seconds",
                        "require_complete",
                        "native_ris_with_abstracts",
                        "normalized_record_fields",
                    )
                },
                "event_id": event_id,
                "output_filename": base.source_cell_output_name(partition_id, cell_id),
                "native_ris_directory": (
                    f"native-ris/{base.source_cell_name(partition_id, cell_id)}"
                ),
                "superseded_event_id": source["event_id"],
                "prior_outcome_status": outcome["status"],
            }
        )
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": base.now(),
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "review_id": initial["review_id"],
        "phase": initial["phase"],
        "strategy_reference": initial["strategy_reference"],
        "strategy_version": initial["repository_head_at_predeclaration"],
        "recovery_sequence": SEQUENCE,
        "reason": (
            "The second corrective run accepted no source cell. A2-mb produced a "
            "second null, nonmergeable failure. B2 was interrupted by the coding "
            "harness timeout before any artifact, source total, ID, record, RIS file, "
            "or screenshot was accepted. This recovery runs both unchanged cells from "
            "fresh Wiley pages and retains one immediate receipt per command."
        ),
        "initial_final_plan": {
            "path": base.relative(initial_plan_path),
            "sha256": base.digest(initial_plan_path),
        },
        "initial_final_run_receipt": {
            "path": base.relative(initial_receipt_path),
            "sha256": base.digest(initial_receipt_path),
        },
        "superseded_corrective_plan": {
            "path": base.relative(prior_plan_path),
            "sha256": base.digest(prior_plan_path),
        },
        "superseded_interruption_receipt": {
            "path": base.relative(interruption_path),
            "sha256": base.digest(interruption_path),
        },
        "source_configuration": initial["source_configuration"],
        "capture_contract": initial["capture_contract"],
        "cutoff": initial["cutoff"],
        "execution_policy": {
            **initial["execution_policy"],
            "selected_null_or_interrupted_cells_only": True,
            "one_command_and_immediate_receipt_per_cell": True,
            "reuse_prior_source_state": False,
        },
        "adapter": initial["adapter"],
        "bindings": {
            "files": {
                base.relative(SCRIPT_PATH): base.digest(SCRIPT_PATH),
                base.relative(base.SCRIPT_PATH): base.digest(base.SCRIPT_PATH),
                base.relative(corrective.SCRIPT_PATH): base.digest(corrective.SCRIPT_PATH),
                base.relative(base.QUERY_SNAPSHOT): base.digest(base.QUERY_SNAPSHOT),
                base.relative(base.SOURCE_GUIDELINE): base.digest(base.SOURCE_GUIDELINE),
            }
        },
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool = False) -> list[str]:
    errors: list[str] = []
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("source") != base.SOURCE
        or plan.get("source_id") != base.SOURCE_ID
        or plan.get("review_namespace") != base.REVIEW_NAMESPACE
        or plan.get("review_id") != base.REVIEW_ID
        or plan.get("phase") != base.PHASE
        or plan.get("strategy_reference") != base.STRATEGY_REFERENCE
        or plan.get("recovery_sequence") != SEQUENCE
        or not isinstance(plan.get("strategy_version"), str)
        or not re.fullmatch(r"[0-9a-f]{40}", plan["strategy_version"])
    ):
        errors.append("identity")
    if not (
        isinstance(plan.get("reason"), str)
        and "second null, nonmergeable failure" in plan["reason"]
        and "interrupted by the coding harness timeout" in plan["reason"]
        and "fresh Wiley pages" in plan["reason"]
    ):
        errors.append("reason")
    if (
        plan.get("cutoff", {}).get("exact_common_cutoff") != base.DATE_END
        or plan.get("source_configuration", {}).get("publication_type_filter") is not None
        or plan.get("capture_contract", {}).get("full_abstracts", {}).get("required")
        is not True
        or plan.get("capture_contract", {}).get("publication_types", {}).get("required")
        is not True
    ):
        errors.append("source_contract")
    events = plan.get("events")
    if not isinstance(events, list) or [
        (event.get("partition_id"), event.get("cell_id")) for event in events
    ] != list(EVENT_KEYS):
        return [*errors, "event_schedule"]
    for event in events:
        partition_id = str(event["partition_id"])
        cell_id = str(event["cell_id"])
        query = event.get("query")
        if (
            event.get("event_id") != recovery_event_id(partition_id, cell_id)
            or event.get("output_filename")
            != base.source_cell_output_name(partition_id, cell_id)
            or event.get("native_ris_directory")
            != f"native-ris/{base.source_cell_name(partition_id, cell_id)}"
            or not isinstance(query, str)
            or event.get("query_sha256") != base.digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("date_start") != base.DATE_START
            or event.get("date_end") != base.DATE_END
            or event.get("field") != base.FIELD
            or event.get("content") != base.CONTENT
            or event.get("sort") != base.SORT
            or event.get("passes") != base.PASSES
            or event.get("require_complete") is not True
            or event.get("native_ris_with_abstracts") is not True
            or event.get("prior_outcome_status")
            not in {"null_nonmergeable_failure", "interrupted_without_artifact"}
        ):
            errors.append(f"event_contract:{partition_id}:{cell_id}")
    if verify_bindings:
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected in files.items():
                path = base.REPOSITORY_ROOT / str(name)
                if not path.is_file() or base.digest(path) != expected:
                    errors.append(f"binding_changed:{name}")
        adapter = plan.get("adapter")
        if not isinstance(adapter, Mapping) or (
            adapter.get("id") != "search_wiley_online_library"
            or adapter.get("version") != base.adapter_version()
            or adapter.get("sha256") != base.digest(base.ADAPTER)
        ):
            errors.append("adapter_changed")
        for reference in (
            "initial_final_plan",
            "initial_final_run_receipt",
            "superseded_corrective_plan",
            "superseded_interruption_receipt",
        ):
            item = plan.get(reference)
            path = (
                base.REPOSITORY_ROOT / str(item.get("path", ""))
                if isinstance(item, Mapping)
                else Path()
            )
            if not path.is_file() or base.digest(path) != item.get("sha256"):
                errors.append(f"changed:{reference}")
    return errors


def page_targets(cdp_url: str) -> dict[str, str]:
    values = base.cdp_json(cdp_url, "/json/list")
    if not isinstance(values, list):
        return {}
    return {
        str(item["id"]): str(item.get("url", ""))
        for item in values
        if isinstance(item, Mapping)
        and item.get("type") == "page"
        and isinstance(item.get("id"), str)
    }


def close_new_wiley_pages(cdp_url: str, baseline: set[str]) -> int:
    closed = 0
    for target_id, url in page_targets(cdp_url).items():
        if target_id in baseline:
            continue
        parsed = urlparse(url)
        if parsed.hostname == "onlinelibrary.wiley.com" and base.close_target(
            cdp_url, target_id
        ):
            closed += 1
    return closed


def selected_event(plan: Mapping[str, Any], value: str) -> Mapping[str, Any]:
    normalized = value.casefold().replace("_", "-")
    matches = [
        event
        for event in plan["events"]
        if normalized
        in {
            str(event["event_id"]).casefold(),
            base.source_cell_name(event["partition_id"], event["cell_id"]).casefold(),
        }
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one recovery event for {value}")
    return matches[0]


def final_command(
    event: Mapping[str, Any],
    output: Path,
    native_dir: Path,
    cdp_url: str,
    target_id: str,
    plan: Mapping[str, Any],
) -> list[str]:
    proxy_plan = {
        "review_id": plan["review_id"],
        "strategy_reference": plan["strategy_reference"],
        "repository_head_at_predeclaration": plan["strategy_version"],
        "phase": plan["phase"],
    }
    return base.final_command(event, output, native_dir, cdp_url, target_id, proxy_plan)


def run_event(
    plan_path: Path,
    event_name: str,
    output_dir: Path,
    receipt_path: Path,
    *,
    outer_timeout_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = base.load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid Wiley recovery plan: " + ", ".join(errors))
    event = selected_event(plan, event_name)
    if output_dir.is_symlink():
        raise ValueError("The Wiley recovery output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / event["output_filename"]
    native_dir = output_dir / event["native_ris_directory"]
    if base.output_paths_occupied(output, native_dir):
        raise FileExistsError(f"Refusing to overwrite {event_name} recovery artifacts")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Wiley recovery requires a loopback browser endpoint")
    baseline_targets = set(page_targets(cdp_url))
    target_id: str | None = None
    target_closed = False
    timed_out = False
    stderr_tail: str | None = None
    exit_code: int | None = None
    started = base.now()
    try:
        target_id = base.create_authorized_wiley_target(cdp_url)
        try:
            completed = subprocess.run(
                final_command(event, output, native_dir, cdp_url, target_id, plan),
                check=False,
                capture_output=True,
                text=True,
                timeout=outer_timeout_seconds,
            )
            exit_code = completed.returncode
            stderr_tail = " ".join(completed.stderr.split())[-700:] or None
        except subprocess.TimeoutExpired as error:
            timed_out = True
            stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else error.stderr
            stderr_tail = " ".join((stderr or "").split())[-700:] or "outer_timeout"
        summary = corrective.normalized_summary(
            output, event, plan, native_dir
        )
    except Exception as error:
        summary = {
            "valid": False,
            "artifact_written": output.is_file() and not output.is_symlink(),
            "runner_failure": type(error).__name__,
        }
        stderr_tail = stderr_tail or type(error).__name__
    finally:
        if target_id is not None:
            target_closed = base.close_target(cdp_url, target_id)
        if timed_out:
            time.sleep(2)
            orphaned_pages_closed = close_new_wiley_pages(cdp_url, baseline_targets)
        else:
            orphaned_pages_closed = 0
    success = bool(exit_code == 0 and summary.get("valid") is True)
    receipt = {
        "schema_version": EVENT_RECEIPT_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "event_kind": "corrective_final",
        "plan": base.relative(plan_path),
        "plan_sha256": base.digest(plan_path),
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "status": "complete" if success else ("interrupted" if timed_out else "failed"),
        "success": success,
        "exit_code": exit_code,
        "outer_timeout_seconds": outer_timeout_seconds,
        "outer_timeout_reached": timed_out,
        "authorized_target_created": target_id is not None,
        "authorized_target_close_requested": target_closed,
        "orphaned_owned_wiley_pages_closed_after_timeout": orphaned_pages_closed,
        "target_identifiers_retained": False,
        "artifact": (
            base.relative(output)
            if output.is_file() and not output.is_symlink()
            else None
        ),
        "native_ris_directory": base.relative(native_dir),
        **({"safe_stderr_tail": stderr_tail} if stderr_tail else {}),
        **summary,
        "started_at_utc": started,
        "completed_at_utc": base.now(),
    }
    base.write_new(receipt_path, receipt)
    print(
        json.dumps(
            {
                "event": base.source_cell_name(event["partition_id"], event["cell_id"]),
                "status": receipt["status"],
                "exit_code": exit_code,
                "source_total": summary.get("source_total"),
                "full_abstracts": summary.get("full_abstract_count"),
                "missing_publication_types": summary.get(
                    "missing_publication_type_count"
                ),
                "error": stderr_tail if not success else None,
            }
        )
    )
    return 0 if success else 1


def aggregate(
    plan_path: Path, receipt_paths: list[Path], output_path: Path
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = base.load(plan_path)
    errors = validate_plan(plan)
    receipts = [base.load(path) for path in receipt_paths]
    by_id = {
        receipt.get("event_id"): (path, receipt)
        for path, receipt in zip(receipt_paths, receipts)
    }
    outcomes: list[dict[str, Any]] = []
    for event in plan["events"]:
        linked = by_id.get(event["event_id"])
        if linked is None:
            errors.append(f"missing_receipt:{event['event_id']}")
            continue
        path, receipt = linked
        if not (
            receipt.get("schema_version") == EVENT_RECEIPT_SCHEMA
            and receipt.get("plan_sha256") == base.digest(plan_path)
            and receipt.get("success") is True
            and receipt.get("valid") is True
            and receipt.get("event_id") == event["event_id"]
        ):
            errors.append(f"failed_receipt:{event['event_id']}")
        outcomes.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "event_receipt": base.relative(path),
                "event_receipt_sha256": base.digest(path),
                "success": receipt.get("success") is True,
                "artifact": receipt.get("artifact"),
                "artifact_sha256": receipt.get("artifact_sha256"),
                "source_total": receipt.get("source_total"),
                "retained_record_count": receipt.get("retained_record_count"),
                "full_abstract_count": receipt.get("full_abstract_count"),
                "publication_type_counts": receipt.get("publication_type_counts"),
            }
        )
    complete = not errors and len(outcomes) == len(plan["events"])
    output = {
        "schema_version": RUN_RECEIPT_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "event_kind": "corrective_final",
        "plan": base.relative(plan_path),
        "plan_sha256": base.digest(plan_path),
        "recovery_sequence": SEQUENCE,
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "success": complete,
        "target_identifiers_retained": False,
        "outcomes": outcomes,
        "completed_at_utc": base.now(),
        "errors": errors,
    }
    base.write_new(output_path, output)
    print(json.dumps({"status": "complete" if complete else "failed", "errors": errors}))
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--initial-plan", type=Path, required=True)
    plan_parser.add_argument("--initial-receipt", type=Path, required=True)
    plan_parser.add_argument("--prior-plan", type=Path, required=True)
    plan_parser.add_argument("--interruption-receipt", type=Path, required=True)
    plan_parser.add_argument("--output", type=Path, required=True)
    check_parser = commands.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    event_parser = commands.add_parser("run-event")
    event_parser.add_argument("--plan", type=Path, required=True)
    event_parser.add_argument("--event", required=True)
    event_parser.add_argument("--output-dir", type=Path, required=True)
    event_parser.add_argument("--receipt", type=Path, required=True)
    event_parser.add_argument("--outer-timeout-seconds", type=float, default=3600.0)
    aggregate_parser = commands.add_parser("aggregate")
    aggregate_parser.add_argument("--plan", type=Path, required=True)
    aggregate_parser.add_argument("--event-receipt", type=Path, action="append", required=True)
    aggregate_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "plan":
        plan = build_plan(
            args.initial_plan.resolve(strict=True),
            args.initial_receipt.resolve(strict=True),
            args.prior_plan.resolve(strict=True),
            args.interruption_receipt.resolve(strict=True),
        )
        errors = validate_plan(plan)
        if errors:
            raise ValueError("Invalid generated Wiley recovery plan: " + ", ".join(errors))
        base.write_new(args.output, plan)
        print(json.dumps({"status": "saved", "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(base.load(args.plan), verify_bindings=True)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run-event":
        if not args.outer_timeout_seconds > 0:
            raise ValueError("The outer timeout must be positive")
        return run_event(
            args.plan.resolve(strict=True),
            args.event,
            args.output_dir.resolve(strict=False),
            args.receipt.resolve(strict=False),
            outer_timeout_seconds=args.outer_timeout_seconds,
        )
    return aggregate(
        args.plan.resolve(strict=True),
        [path.resolve(strict=True) for path in args.event_receipt],
        args.output.resolve(strict=False),
    )


if __name__ == "__main__":
    raise SystemExit(main())
