#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.48",
# ]
# ///

"""Correct and reconcile incomplete cells from the first final IAF run."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
CORE_PATH = Path(__file__).with_name("run.py")
SOURCE_UNION_TOOL = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
DEFAULT_INITIAL_ROOT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/iaf-digital-library/final-searches"
)
DEFAULT_INITIAL_PLAN = DEFAULT_INITIAL_ROOT / "final-event-plan.json"
DEFAULT_INITIAL_RUN = DEFAULT_INITIAL_ROOT / "run-receipt.json"

SOURCE = "IAF Digital Library"
SOURCE_ID = "iaf_digital_library"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
MAX_ATTEMPTS = 3
INTER_ATTEMPT_DELAY_SECONDS = 1.0
INTER_CELL_DELAY_SECONDS = 0.25
PROCESS_TIMEOUT_SECONDS = 420.0

PLAN_SCHEMA = "slr1-iaf-final-direct-corrective-plan/v1"
RUN_SCHEMA = "slr1-iaf-final-direct-corrective-run/v1"
COMBINED_SCHEMA = "slr1-iaf-final-direct-combined-run/v1"
DECLARATIONS_SCHEMA = "slr1-iaf-final-direct-combined-cell-declarations/v1"
RECORD_UNION_SCHEMA = "slr1-iaf-final-direct-combined-record-union/v1"
ASSESSMENT_SCHEMA = "slr1-iaf-final-direct-corrective-assessment/v1"


def load_core() -> Any:
    spec = importlib.util.spec_from_file_location("iaf_final_direct_core_v1", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the initial IAF final runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_core()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def failed_initial_events(
    initial_plan: Mapping[str, Any], initial_run: Mapping[str, Any]
) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    outcomes = {
        item.get("event_id"): item
        for item in initial_run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    failed = []
    for event in initial_plan.get("events", []):
        outcome = outcomes.get(event.get("event_id"))
        if not isinstance(outcome, Mapping):
            raise TypeError(f"Initial run lacks {event.get('cell_id')}")
        if outcome.get("success") is not True:
            failed.append((event, outcome))
    return failed


def attempt_declarations(event: Mapping[str, Any]) -> list[dict[str, Any]]:
    stem = Path(str(event["output"])).stem
    partition = str(event["partition_id"])
    cell_slug = str(event["cell_id"]).lower()
    attempts = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        basename = f"{stem}.attempt-{attempt:02d}"
        attempts.append(
            {
                "attempt": attempt,
                "event_id": f"final-main-iaf-r002-{cell_slug}-attempt-{attempt:02d}",
                "parent_event_id": f"final-main-iaf-r002-{partition.lower()}",
                "output": f"{partition}/{basename}.json",
                "capture_receipt": f"{partition}/{basename}.capture-receipt.json",
            }
        )
    return attempts


def corrected_event(event: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any]:
    failure_kind = (
        "source_or_adapter_failure"
        if outcome.get("artifact")
        else "pre_execution_binding_stop"
    )
    return {
        "original_event_id": event["event_id"],
        "original_parent_event_id": event["parent_event_id"],
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "accepted_cell_id": event["accepted_cell_id"],
        "cell_number": event["cell_number"],
        "cell_count": event["cell_count"],
        "branch_id": event["branch_id"],
        "factor_ranges": copy.deepcopy(event["factor_ranges"]),
        "query": event["query"],
        "query_characters": event["query_characters"],
        "query_sha256": event["query_sha256"],
        "initial_failure_kind": failure_kind,
        "initial_diagnostic": outcome.get("diagnostic"),
        "initial_failure_artifact": outcome.get("artifact"),
        "attempts": attempt_declarations(event),
    }


def build_plan(initial_plan_path: Path, initial_run_path: Path) -> dict[str, Any]:
    require_regular(initial_plan_path)
    require_regular(initial_run_path)
    require_regular(SCRIPT_PATH)
    require_regular(CORE_PATH)
    initial_plan = load(initial_plan_path)
    initial_run = load(initial_run_path)
    plan_errors = core.validate_plan(initial_plan, verify_bindings=False)
    if plan_errors:
        raise ValueError("Invalid initial IAF plan: " + ", ".join(plan_errors))
    if (
        initial_run.get("schema_version") != core.RUN_SCHEMA
        or initial_run.get("plan_sha256") != core.digest(initial_plan_path)
        or initial_run.get("success") is not False
        or initial_run.get("attempted_source_cell_count") != 158
    ):
        raise ValueError("The initial IAF run is not the expected incomplete final run")
    failed = failed_initial_events(initial_plan, initial_run)
    browser_failures = sum(
        outcome.get("artifact") is not None for _, outcome in failed
    )
    binding_stops = len(failed) - browser_failures
    bindings = (SCRIPT_PATH, CORE_PATH, initial_plan_path, initial_run_path)
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "review_id": core.REVIEW_ID,
        "event_kind": "final_corrective",
        "phase": core.PHASE,
        "strategy_reference": initial_plan["strategy_reference"],
        "strategy_version": initial_plan["strategy_version"],
        "reason": (
            "Complete unchanged cells after the first final run retained source failures "
            "and stopped later cells when a concurrently edited protocol file changed its predeclared hash."
        ),
        "query_change": False,
        "filter_change": False,
        "initial_run": {
            "plan": core.relative(initial_plan_path),
            "plan_sha256": core.digest(initial_plan_path),
            "run_receipt": core.relative(initial_run_path),
            "run_receipt_sha256": core.digest(initial_run_path),
            "planned_cells": 158,
            "successful_cells": initial_run.get("accepted_source_cell_count"),
            "failed_cells": len(failed),
            "source_or_adapter_failures": browser_failures,
            "pre_execution_binding_stops": binding_stops,
        },
        "accepted_translation": copy.deepcopy(initial_plan["accepted_translation"]),
        "cutoff": copy.deepcopy(initial_plan["cutoff"]),
        "source_configuration": copy.deepcopy(initial_plan["source_configuration"]),
        "record_capture_contract": copy.deepcopy(
            initial_plan["record_capture_contract"]
        ),
        "strict_contract": copy.deepcopy(initial_plan["strict_contract"]),
        "record_projection": copy.deepcopy(initial_plan["record_projection"]),
        "adapter": copy.deepcopy(initial_plan["adapter"]),
        "retry_policy": {
            "maximum_attempts_per_incomplete_cell": MAX_ATTEMPTS,
            "query_changes_between_attempts": False,
            "failed_attempts_retained": True,
            "accept_first_complete_attempt": True,
            "initial_successes_reexecuted": False,
        },
        "bindings": {
            "files": {core.relative(path): core.digest(path) for path in bindings}
        },
        "initial_success_cell_count": 158 - len(failed),
        "corrective_cell_count": len(failed),
        "combined_cell_count": 158,
        "events": [corrected_event(event, outcome) for event, outcome in failed],
    }


def expected_corrective_events(
    initial_plan: Mapping[str, Any], initial_run: Mapping[str, Any]
) -> list[dict[str, Any]]:
    return [
        corrected_event(event, outcome)
        for event, outcome in failed_initial_events(initial_plan, initial_run)
    ]


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    initial = plan.get("initial_run")
    if not isinstance(initial, Mapping):
        return [*errors, "initial_run"]
    try:
        initial_plan_path = REPOSITORY_ROOT / str(initial["plan"])
        initial_run_path = REPOSITORY_ROOT / str(initial["run_receipt"])
        initial_plan = load(initial_plan_path)
        initial_run = load(initial_run_path)
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return [*errors, "initial_inputs"]
    if (
        initial.get("plan_sha256") != core.digest(initial_plan_path)
        or initial.get("run_receipt_sha256") != core.digest(initial_run_path)
    ):
        errors.append("initial_bindings")
    expected = expected_corrective_events(initial_plan, initial_run)
    if plan.get("events") != expected:
        errors.append("events")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_id") != core.REVIEW_ID
        or plan.get("strategy_reference") != initial_plan.get("strategy_reference")
        or plan.get("strategy_version") != initial_plan.get("strategy_version")
        or plan.get("query_change") is not False
        or plan.get("filter_change") is not False
        or plan.get("corrective_cell_count") != len(expected)
        or plan.get("initial_success_cell_count") != 158 - len(expected)
        or plan.get("combined_cell_count") != 158
        or plan.get("adapter") != initial_plan.get("adapter")
        or plan.get("record_capture_contract")
        != initial_plan.get("record_capture_contract")
    ):
        errors.append("identity")
    retry = plan.get("retry_policy", {})
    if (
        retry.get("maximum_attempts_per_incomplete_cell") != MAX_ATTEMPTS
        or retry.get("query_changes_between_attempts") is not False
        or retry.get("failed_attempts_retained") is not True
        or retry.get("accept_first_complete_attempt") is not True
        or retry.get("initial_successes_reexecuted") is not False
    ):
        errors.append("retry_policy")
    if verify_bindings:
        files = plan.get("bindings", {}).get("files", {})
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in files.items():
                path = REPOSITORY_ROOT / str(name)
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or core.digest(path) != expected_hash
                ):
                    errors.append(f"binding:{name}")
        try:
            if plan.get("adapter") != core.adapter_identity():
                errors.append("adapter")
        except (OSError, RuntimeError, ValueError):
            errors.append("adapter")
    return errors


def runtime_event(
    event: Mapping[str, Any], attempt: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "event_id": attempt["event_id"],
        "parent_event_id": attempt["parent_event_id"],
        "event_kind": "final_corrective",
        "review_namespace": "main",
        "source_id": SOURCE_ID,
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "accepted_cell_id": event["accepted_cell_id"],
        "cell_number": event["cell_number"],
        "cell_count": event["cell_count"],
        "branch_id": event["branch_id"],
        "factor_ranges": copy.deepcopy(event["factor_ranges"]),
        "query": event["query"],
        "query_characters": event["query_characters"],
        "query_sha256": event["query_sha256"],
        "output": attempt["output"],
        "capture_receipt": attempt["capture_receipt"],
    }


def run_cell(
    plan_path: Path,
    output_root: Path,
    original_event_id: str,
    attempt_number: int,
) -> int:
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid corrective IAF plan: " + ", ".join(errors))
    event = next(
        (
            item
            for item in plan["events"]
            if item["original_event_id"] == original_event_id
        ),
        None,
    )
    if event is None:
        raise ValueError(f"Unknown corrective IAF cell: {original_event_id}")
    attempt = next(
        (item for item in event["attempts"] if item["attempt"] == attempt_number),
        None,
    )
    if attempt is None:
        raise ValueError(f"Unknown corrective attempt: {attempt_number}")
    current = runtime_event(event, attempt)
    output = output_root / current["output"]
    capture_path = output_root / current["capture_receipt"]
    occupied = (
        output,
        core.marker_path(output),
        *core.screenshot_paths(output),
        capture_path,
    )
    if any(path.exists() or path.is_symlink() for path in occupied):
        raise FileExistsError(f"Refusing to overwrite {current['event_id']}")
    output.parent.mkdir(parents=True, exist_ok=True)
    adapter = core.load_adapter()
    args = core.adapter_arguments(adapter, current, plan, output)
    prisma_context: Mapping[str, Any] | None = None
    try:
        prisma_context = adapter.configure_prisma_search_run_from_args(
            args,
            adapter_id=adapter.ADAPTER_ID,
            adapter_version=adapter.ADAPTER_VERSION,
            adapter_script=core.ADAPTER,
        )
        executed, query_mode, rows, operators = adapter.validate_cli_args(args)
        if executed != current["query"] or query_mode != "raw_query":
            raise ValueError("Corrective execution differs from the original IAF query")
        result = adapter.search_iaf_digital_library(
            args.query,
            wizard_rows=rows if query_mode == "typed_wizard" else None,
            operators=operators if query_mode == "typed_wizard" else None,
            limit=args.limit,
            max_pages=args.max_pages,
            page_size=args.page_size,
            passes=args.passes,
            partition_by=args.partition_by,
            year_start=args.year_start,
            year_end=args.year_end,
            date_start=args.date_start,
            date_end=args.date_end,
            timeout_seconds=args.timeout_seconds,
            page_delay_seconds=args.page_delay_seconds,
            retries=args.retries,
            count_only=args.count_only,
            require_complete=args.require_complete,
            cdp_url=args.cdp_url,
            target_id=args.target_id,
            headless=args.headless,
            chrome_executable=args.chrome_executable,
            prisma_context=prisma_context,
            screenshot_paths=args.screenshot_paths,
        )
        adapter.assert_complete_iaf_result(result)
        counts = core.project_records(result)
        adapter.assert_complete_iaf_result(result)
        if not core.in_memory_strict_valid(result):
            raise ValueError("Corrective IAF cell lacks strict two-pass evidence")
        adapter._save_search_result(output, result)
        persisted = load(output)
        capture = core.build_capture_receipt(
            result,
            persisted,
            plan_path=plan_path,
            event=current,
            output=output,
        )
        write_new(capture_path, capture)
        print(
            json.dumps(
                {
                    "event_id": current["event_id"],
                    "status": "complete",
                    "source_total": result["total"],
                    "retained": counts["records"],
                    "full_abstracts": counts["full_abstracts"],
                }
            ),
            flush=True,
        )
        return 0
    except Exception as error:  # noqa: BLE001 - retain each corrective attempt.
        if not output.exists() and not output.is_symlink():
            try:
                source_error = (
                    error
                    if isinstance(error, adapter.IAFDigitalLibraryError)
                    else adapter.IAFDigitalLibraryBrowserError(
                        "Unexpected corrective IAF browser workflow failure"
                    )
                )
                if source_error is not error:
                    source_error.__cause__ = error
                core.save_failure(
                    adapter, args, current, source_error, prisma_context
                )
            except Exception as save_error:  # noqa: BLE001
                print(
                    f"iaf_corrective_failure_artifact_failed:{type(save_error).__name__}",
                    file=sys.stderr,
                )
        print(f"iaf_corrective_cell_failed:{type(error).__name__}", file=sys.stderr)
        return 1


def run_corrective(
    plan_path: Path,
    output_root: Path,
    receipt_path: Path,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid corrective IAF plan: " + ", ".join(errors))
    if output_root.is_symlink():
        raise ValueError("The corrective IAF output root cannot be a symlink")
    output_root.mkdir(parents=True, exist_ok=True)
    for event in plan["events"]:
        for attempt in event["attempts"]:
            current = runtime_event(event, attempt)
            output = output_root / current["output"]
            capture = output_root / current["capture_receipt"]
            occupied = (
                output,
                core.marker_path(output),
                *core.screenshot_paths(output),
                capture,
            )
            if any(path.exists() or path.is_symlink() for path in occupied):
                raise FileExistsError(
                    f"Corrective IAF attempt path is occupied: {current['event_id']}"
                )

    started = now()
    outcomes: list[dict[str, Any]] = []
    for cell_index, event in enumerate(plan["events"], start=1):
        if cell_index > 1:
            time.sleep(INTER_CELL_DELAY_SECONDS)
        attempts: list[dict[str, Any]] = []
        accepted: dict[str, Any] | None = None
        for attempt_index, attempt in enumerate(event["attempts"], start=1):
            if attempt_index > 1:
                time.sleep(INTER_ATTEMPT_DELAY_SECONDS)
            current = runtime_event(event, attempt)
            output = output_root / current["output"]
            capture_path = output_root / current["capture_receipt"]
            command = [
                sys.executable,
                str(SCRIPT_PATH),
                "cell",
                "--plan",
                str(plan_path),
                "--output-root",
                str(output_root),
                "--original-event-id",
                event["original_event_id"],
                "--attempt",
                str(attempt["attempt"]),
            ]
            attempt_started = now()
            try:
                completed = subprocess.run(
                    command,
                    cwd=REPOSITORY_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=PROCESS_TIMEOUT_SECONDS,
                )
                exit_code: int | None = completed.returncode
                summary = core.artifact_summary(
                    output, capture_path, current, plan, plan_path
                )
                diagnostics = (completed.stderr or "").strip().splitlines()
            except Exception as error:  # noqa: BLE001
                exit_code = None
                summary = {
                    "valid": False,
                    "artifact_written": output.is_file(),
                    "runner_failure": type(error).__name__,
                }
                diagnostics = [type(error).__name__]
            success = bool(exit_code == 0 and summary.get("valid") is True)
            attempt_outcome = {
                "attempt": attempt["attempt"],
                "event_id": current["event_id"],
                "started_at_utc": attempt_started,
                "completed_at_utc": now(),
                "success": success,
                "exit_code": exit_code,
                "artifact": core.relative(output) if output.is_file() else None,
                **summary,
            }
            if not success and diagnostics:
                attempt_outcome["diagnostic"] = diagnostics[-1][:300]
            attempts.append(attempt_outcome)
            if success:
                accepted = attempt_outcome
                break
        outcome = {
            "original_event_id": event["original_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "success": accepted is not None,
            "attempt_count": len(attempts),
            "accepted_attempt": accepted.get("attempt") if accepted else None,
            "accepted_event_id": accepted.get("event_id") if accepted else None,
            "accepted_artifact": accepted.get("artifact") if accepted else None,
            "accepted_capture_receipt": (
                accepted.get("capture_receipt") if accepted else None
            ),
            "attempts": attempts,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "cell": event["cell_id"],
                    "position": cell_index,
                    "planned": len(plan["events"]),
                    "success": outcome["success"],
                    "attempts": outcome["attempt_count"],
                    "source_total": (
                        accepted.get("source_total") if accepted else None
                    ),
                    "retained": (
                        accepted.get("retained_record_count") if accepted else None
                    ),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == plan["corrective_cell_count"] and all(
        outcome["success"] for outcome in outcomes
    )
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "event_kind": "final_corrective",
        "plan": core.relative(plan_path),
        "plan_sha256": core.digest(plan_path),
        "initial_run": copy.deepcopy(plan["initial_run"]),
        "retry_policy": copy.deepcopy(plan["retry_policy"]),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_corrective_cell_count": plan["corrective_cell_count"],
        "attempted_corrective_cell_count": len(outcomes),
        "accepted_corrective_cell_count": sum(
            outcome["success"] for outcome in outcomes
        ),
        "source_attempt_count": sum(
            outcome["attempt_count"] for outcome in outcomes
        ),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def selected_artifacts(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    initial_root: Path,
    corrective_root: Path,
) -> list[dict[str, Any]]:
    corrective_plan = load(corrective_plan_path)
    corrective_run = load(corrective_run_path)
    if corrective_run.get("success") is not True:
        raise ValueError("The corrective IAF run is incomplete")
    initial_info = corrective_plan["initial_run"]
    initial_plan_path = REPOSITORY_ROOT / initial_info["plan"]
    initial_run_path = REPOSITORY_ROOT / initial_info["run_receipt"]
    initial_plan = load(initial_plan_path)
    initial_run = load(initial_run_path)
    initial_outcomes = {
        item["event_id"]: item for item in initial_run["outcomes"]
    }
    corrective_events = {
        item["original_event_id"]: item for item in corrective_plan["events"]
    }
    corrective_outcomes = {
        item["original_event_id"]: item for item in corrective_run["outcomes"]
    }
    selected: list[dict[str, Any]] = []
    for semantic_event in initial_plan["events"]:
        initial_outcome = initial_outcomes[semantic_event["event_id"]]
        if initial_outcome.get("success") is True:
            context_plan_path = initial_plan_path
            context_plan = initial_plan
            runtime = semantic_event
            path = initial_root / semantic_event["output"]
            capture_path = initial_root / semantic_event["capture_receipt"]
            origin = "initial_run"
        else:
            correction = corrective_events[semantic_event["event_id"]]
            correction_outcome = corrective_outcomes[semantic_event["event_id"]]
            if correction_outcome.get("success") is not True:
                raise ValueError(f"No accepted correction for {semantic_event['cell_id']}")
            attempt_number = correction_outcome["accepted_attempt"]
            attempt = next(
                item
                for item in correction["attempts"]
                if item["attempt"] == attempt_number
            )
            runtime = runtime_event(correction, attempt)
            context_plan_path = corrective_plan_path
            context_plan = corrective_plan
            path = corrective_root / runtime["output"]
            capture_path = corrective_root / runtime["capture_receipt"]
            origin = "corrective_002"
        require_regular(path)
        require_regular(capture_path)
        data = load(path)
        summary = core.artifact_summary(
            path,
            capture_path,
            runtime,
            context_plan,
            context_plan_path,
        )
        if summary.get("valid") is not True:
            raise ValueError(f"Selected IAF artifact is invalid: {semantic_event['cell_id']}")
        selected.append(
            {
                "semantic_event": semantic_event,
                "runtime_event": runtime,
                "origin": origin,
                "context_plan": context_plan,
                "context_plan_path": context_plan_path,
                "path": path,
                "capture_path": capture_path,
                "data": data,
                "summary": summary,
            }
        )
    if len(selected) != 158:
        raise ValueError("The combined IAF schedule does not contain 158 cells")
    return selected


def build_combined_run(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    initial_root: Path,
    corrective_root: Path,
    output: Path,
) -> dict[str, Any]:
    corrective_plan = load(corrective_plan_path)
    selected = selected_artifacts(
        corrective_plan_path,
        corrective_run_path,
        initial_root,
        corrective_root,
    )
    rows = []
    for item in selected:
        semantic = item["semantic_event"]
        runtime = item["runtime_event"]
        summary = item["summary"]
        rows.append(
            {
                "partition_id": semantic["partition_id"],
                "cell_id": semantic["cell_id"],
                "original_event_id": semantic["event_id"],
                "accepted_event_id": runtime["event_id"],
                "origin": item["origin"],
                "artifact": core.relative(item["path"]),
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_bytes": summary["artifact_bytes"],
                "capture_receipt": core.relative(item["capture_path"]),
                "capture_receipt_sha256": summary["capture_receipt_sha256"],
                "raw_source_total": summary["source_total"],
                "retained_record_count": summary["retained_record_count"],
                "client_side_exclusions": summary["client_side_exclusions"],
                "full_abstract_count": summary["record_capture"][
                    "full_abstract_count"
                ],
                "source_publication_types": summary["record_capture"][
                    "publication_type_counts"
                ],
                "success": True,
            }
        )
    value = {
        "schema_version": COMBINED_SCHEMA,
        "created_at_utc": now(),
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "event_kind": "final",
        "strategy_reference": corrective_plan["strategy_reference"],
        "strategy_version": corrective_plan["strategy_version"],
        "initial_plan": corrective_plan["initial_run"]["plan"],
        "initial_plan_sha256": corrective_plan["initial_run"]["plan_sha256"],
        "initial_run_receipt": corrective_plan["initial_run"]["run_receipt"],
        "initial_run_receipt_sha256": corrective_plan["initial_run"][
            "run_receipt_sha256"
        ],
        "corrective_plan": core.relative(corrective_plan_path),
        "corrective_plan_sha256": core.digest(corrective_plan_path),
        "corrective_run_receipt": core.relative(corrective_run_path),
        "corrective_run_receipt_sha256": core.digest(corrective_run_path),
        "selected_initial_cell_count": sum(
            item["origin"] == "initial_run" for item in selected
        ),
        "selected_corrective_cell_count": sum(
            item["origin"] == "corrective_002" for item in selected
        ),
        "selected_source_cell_count": len(selected),
        "success": True,
        "outcomes": rows,
    }
    write_new(output, value)
    return value


def load_combined_selection(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    combined_path: Path,
    initial_root: Path,
    corrective_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    combined = load(combined_path)
    selected = selected_artifacts(
        corrective_plan_path,
        corrective_run_path,
        initial_root,
        corrective_root,
    )
    if (
        combined.get("schema_version") != COMBINED_SCHEMA
        or combined.get("corrective_plan_sha256")
        != core.digest(corrective_plan_path)
        or combined.get("corrective_run_receipt_sha256")
        != core.digest(corrective_run_path)
        or combined.get("selected_source_cell_count") != 158
        or combined.get("success") is not True
    ):
        raise ValueError("The combined IAF run receipt is invalid")
    return combined, selected


def build_declarations(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    combined_path: Path,
    initial_root: Path,
    corrective_root: Path,
    output: Path,
) -> dict[str, Any]:
    combined, selected = load_combined_selection(
        corrective_plan_path,
        corrective_run_path,
        combined_path,
        initial_root,
        corrective_root,
    )
    cells = []
    for item in selected:
        semantic = item["semantic_event"]
        data = item["data"]
        prisma = data["output_metadata"]["prisma_search_run"]
        cells.append(
            {
                "source_id": SOURCE_ID,
                "partition_id": semantic["partition_id"],
                "cell_id": semantic["cell_id"],
                "parent_event_id": semantic["parent_event_id"],
                "source_run_id": prisma["run_id"],
                "query": semantic["query"],
                "requested_query": semantic["query"],
                "executed_query": semantic["query"],
                "source_native_executed_query": semantic["query"],
                "artifact_sha256": core.digest(item["path"]),
                "artifact_byte_count": item["path"].stat().st_size,
                "stable_ids": [row["paperId"] for row in data["results"]],
                "status": "complete",
                "report_ready": True,
                "artifact": core.relative(item["path"]),
                "origin": item["origin"],
            }
        )
    value = {
        "schema_version": DECLARATIONS_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "combined_run_receipt": core.relative(combined_path),
        "combined_run_receipt_sha256": core.digest(combined_path),
        "strategy_reference": combined["strategy_reference"],
        "strategy_version": combined["strategy_version"],
        "expected_cells": cells,
    }
    write_new(output, value)
    return value


def run_source_union(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    combined_path: Path,
    declarations_path: Path,
    initial_root: Path,
    corrective_root: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    _, selected = load_combined_selection(
        corrective_plan_path,
        corrective_run_path,
        combined_path,
        initial_root,
        corrective_root,
    )
    declarations = load(declarations_path)
    if (
        declarations.get("schema_version") != DECLARATIONS_SCHEMA
        or declarations.get("combined_run_receipt_sha256")
        != core.digest(combined_path)
        or len(declarations.get("expected_cells", [])) != 158
    ):
        raise ValueError("The combined IAF cell declarations are invalid")
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *(str(item["path"]) for item in selected),
        "--output-path",
        str(output),
        "--expected-partitions",
        *PARTITIONS,
        "--expected-sources",
        SOURCE_ID,
        "--review-namespace",
        "main",
        "--expected-cells",
        str(declarations_path),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        lines = (completed.stderr or completed.stdout or "").strip().splitlines()
        raise RuntimeError(
            "Could not create the combined IAF source-union receipt"
            + (f": {lines[-1]}" if lines else "")
        )
    return 0


def build_record_union(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    combined_path: Path,
    initial_root: Path,
    corrective_root: Path,
    output: Path,
) -> dict[str, Any]:
    combined, selected = load_combined_selection(
        corrective_plan_path,
        corrective_run_path,
        combined_path,
        initial_root,
        corrective_root,
    )
    records: dict[str, dict[str, Any]] = {}
    partition_ids: dict[str, list[str]] = {partition: [] for partition in PARTITIONS}
    inputs = []
    raw_total_sum = 0
    retained_total_sum = 0
    exclusion_sum = 0
    for item in selected:
        semantic = item["semantic_event"]
        data = item["data"]
        rows = data["results"]
        raw_total = data["total"]
        retained = len(rows)
        exclusions = raw_total - retained
        raw_total_sum += raw_total
        retained_total_sum += retained
        exclusion_sum += exclusions
        inputs.append(
            {
                "partition_id": semantic["partition_id"],
                "cell_id": semantic["cell_id"],
                "origin": item["origin"],
                "artifact": core.relative(item["path"]),
                "artifact_sha256": core.digest(item["path"]),
                "raw_source_total": raw_total,
                "retained_record_count": retained,
                "client_side_exclusions": exclusions,
            }
        )
        for row in rows:
            paper_id = row["paperId"]
            partition_ids[semantic["partition_id"]].append(paper_id)
            entry = records.setdefault(
                paper_id,
                {
                    "paperId": paper_id,
                    "discovery_cells": [],
                    "discovery_partitions": [],
                    "occurrence_count": 0,
                    "record": copy.deepcopy(row),
                },
            )
            entry["occurrence_count"] += 1
            if semantic["cell_id"] not in entry["discovery_cells"]:
                entry["discovery_cells"].append(semantic["cell_id"])
            if semantic["partition_id"] not in entry["discovery_partitions"]:
                entry["discovery_partitions"].append(semantic["partition_id"])
            if len(str(row.get("abstract") or "")) > len(
                str(entry["record"].get("abstract") or "")
            ):
                entry["record"] = copy.deepcopy(row)
    union_rows = []
    for paper_id in sorted(records):
        entry = records[paper_id]
        entry["discovery_cells"].sort()
        entry["discovery_partitions"].sort(key=PARTITIONS.index)
        union_rows.append(entry)
    capture = core.record_capture_summary(
        [entry["record"] for entry in union_rows]
    )
    partition_unions = {}
    for partition in PARTITIONS:
        ids = partition_ids[partition]
        partition_unions[partition] = {
            "cell_count": core.CELL_COUNTS[partition],
            "source_event_record_count": len(ids),
            "unique_paper_id_count": len(set(ids)),
            "duplicate_occurrences": len(ids) - len(set(ids)),
            "paper_ids": sorted(set(ids)),
            "paper_id_set_sha256": core.canonical_set_digest(ids),
            "readiness_bound_100_satisfied": len(set(ids)) <= 100,
        }
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "purpose": (
            "Combined final IAF records with complete source abstracts and source publication types"
        ),
        "reviewer_publication_type_coding": "deferred to screening",
        "combined_run_receipt": core.relative(combined_path),
        "combined_run_receipt_sha256": core.digest(combined_path),
        "strategy_reference": combined["strategy_reference"],
        "strategy_version": combined["strategy_version"],
        "input_artifacts": inputs,
        "raw_source_event_total_sum": raw_total_sum,
        "client_side_exclusion_sum": exclusion_sum,
        "source_event_record_count": retained_total_sum,
        "unique_paper_id_count": len(union_rows),
        "cross_cell_duplicate_occurrences": retained_total_sum - len(union_rows),
        "paper_id_set_sha256": core.canonical_set_digest(list(records)),
        "records_with_full_abstract": capture["full_abstract_count"],
        "records_without_full_abstract": capture["missing_abstract_count"],
        "records_with_source_publication_type": sum(
            capture["publication_type_counts"].values()
        ),
        "records_missing_source_publication_type": capture[
            "missing_publication_type_count"
        ],
        "source_publication_type_counts": capture["publication_type_counts"],
        "partition_unions": partition_unions,
        "complete": capture["valid"],
        "records": union_rows,
    }
    write_new(output, value)
    return value


def assess(
    corrective_plan_path: Path,
    corrective_run_path: Path,
    combined_path: Path,
    declarations_path: Path,
    source_union_path: Path,
    record_union_path: Path,
    initial_root: Path,
    corrective_root: Path,
    output: Path,
) -> int:
    plan = load(corrective_plan_path)
    run = load(corrective_run_path)
    combined, selected = load_combined_selection(
        corrective_plan_path,
        corrective_run_path,
        combined_path,
        initial_root,
        corrective_root,
    )
    declarations = load(declarations_path)
    source_union = load(source_union_path)
    record_union = load(record_union_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != core.digest(corrective_plan_path)
        or run.get("success") is not True
        or run.get("accepted_corrective_cell_count")
        != plan.get("corrective_cell_count")
    ):
        errors.append("corrective_run")
    if (
        combined.get("schema_version") != COMBINED_SCHEMA
        or combined.get("selected_source_cell_count") != 158
        or combined.get("selected_initial_cell_count")
        != plan.get("initial_success_cell_count")
        or combined.get("selected_corrective_cell_count")
        != plan.get("corrective_cell_count")
        or combined.get("success") is not True
    ):
        errors.append("combined_run")
    if (
        declarations.get("schema_version") != DECLARATIONS_SCHEMA
        or declarations.get("combined_run_receipt_sha256")
        != core.digest(combined_path)
        or len(declarations.get("expected_cells", [])) != 158
    ):
        errors.append("cell_declarations")

    retained_ids: list[str] = []
    partition_ids: dict[str, list[str]] = {partition: [] for partition in PARTITIONS}
    raw_total_sum = 0
    retained_occurrences = 0
    exclusion_sum = 0
    unresolved_occurrences = 0
    event_evidence = []
    for item in selected:
        semantic = item["semantic_event"]
        summary = item["summary"]
        ids = summary["ordered_paper_ids"]
        retained_ids.extend(ids)
        partition_ids[semantic["partition_id"]].extend(ids)
        raw_total_sum += summary["source_total"]
        retained_occurrences += summary["retained_record_count"]
        exclusion_sum += summary["client_side_exclusions"]
        unresolved_occurrences += summary["unresolved_exact_dates_retained"]
        event_evidence.append(
            {
                "partition_id": semantic["partition_id"],
                "cell_id": semantic["cell_id"],
                "origin": item["origin"],
                "accepted_event_id": item["runtime_event"]["event_id"],
                "artifact": core.relative(item["path"]),
                "artifact_sha256": core.digest(item["path"]),
                "capture_receipt": core.relative(item["capture_path"]),
                "capture_receipt_sha256": core.digest(item["capture_path"]),
                "raw_source_total": summary["source_total"],
                "retained_record_count": summary["retained_record_count"],
                "full_abstract_count": summary["record_capture"][
                    "full_abstract_count"
                ],
                "source_publication_types": summary["record_capture"][
                    "publication_type_counts"
                ],
                "two_pass_capture_valid": summary[
                    "strict_capture_receipt_valid"
                ],
                "screenshots_valid": summary["screenshots_valid"],
            }
        )

    union_source = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    if not (
        source_union.get("review_namespace") == "main"
        and source_union.get("review_id") == core.REVIEW_ID
        and source_union.get("strategy_reference") == plan["strategy_reference"]
        and source_union.get("strategy_version") == plan["strategy_version"]
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and source_union.get("artifact_count") == 158
        and union_source.get("event_total_sum") == retained_occurrences
        and set(union_source.get("stable_record_ids", [])) == set(retained_ids)
    ):
        errors.append("source_union")
    cell_unions = source_union.get("cell_unions", {}).get(SOURCE_ID, {})
    for partition in PARTITIONS:
        cell_union = cell_unions.get(partition, {})
        if (
            cell_union.get("cell_count") != core.CELL_COUNTS[partition]
            or set(cell_union.get("stable_record_ids", []))
            != set(partition_ids[partition])
        ):
            errors.append(f"source_union_cell:{partition}")

    records = record_union.get("records")
    if not (
        record_union.get("schema_version") == RECORD_UNION_SCHEMA
        and record_union.get("combined_run_receipt_sha256")
        == core.digest(combined_path)
        and record_union.get("raw_source_event_total_sum") == raw_total_sum
        and record_union.get("client_side_exclusion_sum") == exclusion_sum
        and record_union.get("source_event_record_count") == retained_occurrences
        and record_union.get("unique_paper_id_count") == len(set(retained_ids))
        and record_union.get("records_with_full_abstract") == len(set(retained_ids))
        and record_union.get("records_without_full_abstract") == 0
        and record_union.get("records_with_source_publication_type")
        == len(set(retained_ids))
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("source_publication_type_counts")
        == {core.SOURCE_PUBLICATION_TYPE: len(set(retained_ids))}
        and record_union.get("complete") is True
        and isinstance(records, list)
        and len(records) == len(set(retained_ids))
    ):
        errors.append("record_union")
    partition_unions = record_union.get("partition_unions", {})
    for partition in PARTITIONS:
        entry = partition_unions.get(partition, {})
        if (
            entry.get("cell_count") != core.CELL_COUNTS[partition]
            or entry.get("paper_ids") != sorted(set(partition_ids[partition]))
            or entry.get("readiness_bound_100_satisfied") is not True
        ):
            errors.append(f"partition_union:{partition}")

    complete = not errors and len(event_evidence) == 158
    value = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "event_kind": "final",
        "complete": complete,
        "errors": errors,
        "initial_run": copy.deepcopy(plan["initial_run"]),
        "corrective_plan": core.relative(corrective_plan_path),
        "corrective_plan_sha256": core.digest(corrective_plan_path),
        "corrective_run_receipt": core.relative(corrective_run_path),
        "corrective_run_receipt_sha256": core.digest(corrective_run_path),
        "combined_run_receipt": core.relative(combined_path),
        "combined_run_receipt_sha256": core.digest(combined_path),
        "cell_declarations": core.relative(declarations_path),
        "cell_declarations_sha256": core.digest(declarations_path),
        "source_union": core.relative(source_union_path),
        "source_union_sha256": core.digest(source_union_path),
        "record_union": core.relative(record_union_path),
        "record_union_sha256": core.digest(record_union_path),
        "adapter": plan["adapter"],
        "selected_source_cell_count": len(event_evidence),
        "events": event_evidence,
        "stable_id_union": {
            "raw_source_event_total_sum": raw_total_sum,
            "client_side_exclusion_sum": exclusion_sum,
            "retained_source_event_record_count": retained_occurrences,
            "unique_paper_id_count": len(set(retained_ids)),
            "cross_cell_duplicate_occurrences": retained_occurrences
            - len(set(retained_ids)),
            "paper_id_set_sha256": core.canonical_set_digest(retained_ids),
        },
        "partition_unions": copy.deepcopy(partition_unions),
        "record_capture": {
            "full_abstracts_required": True,
            "source_publication_types_required": True,
            "reviewer_publication_type_coding": "deferred to screening",
            "unique_records_with_full_abstract": record_union.get(
                "records_with_full_abstract"
            ),
            "unique_records_without_full_abstract": record_union.get(
                "records_without_full_abstract"
            ),
            "source_publication_type_counts": record_union.get(
                "source_publication_type_counts"
            ),
        },
        "strict_execution": {
            "two_pass_cell_count": len(event_evidence),
            "selected_automatic_screenshot_count": 2 * len(event_evidence),
            "expected_automatic_screenshot_count": 316,
            "all_two_pass_capture_receipts_valid": all(
                event["two_pass_capture_valid"] for event in event_evidence
            ),
            "all_selected_screenshots_valid": all(
                event["screenshots_valid"] for event in event_evidence
            ),
        },
        "cutoff": {
            **plan["cutoff"],
            "unresolved_exact_dates_retained_occurrences": unresolved_occurrences,
        },
    }
    write_new(output, value)
    return 0 if complete else 1


def add_selection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--corrective-plan", type=Path, required=True)
    parser.add_argument("--corrective-run", type=Path, required=True)
    parser.add_argument("--combined-run", type=Path, required=True)
    parser.add_argument("--initial-root", type=Path, default=DEFAULT_INITIAL_ROOT)
    parser.add_argument("--corrective-root", type=Path, required=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--initial-plan", type=Path, default=DEFAULT_INITIAL_PLAN)
    plan_parser.add_argument("--initial-run", type=Path, default=DEFAULT_INITIAL_RUN)
    plan_parser.add_argument("--output", type=Path, required=True)

    cell_parser = commands.add_parser("cell")
    cell_parser.add_argument("--plan", type=Path, required=True)
    cell_parser.add_argument("--output-root", type=Path, required=True)
    cell_parser.add_argument("--original-event-id", required=True)
    cell_parser.add_argument("--attempt", type=int, required=True)

    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-root", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)

    combine_parser = commands.add_parser("combine")
    combine_parser.add_argument("--corrective-plan", type=Path, required=True)
    combine_parser.add_argument("--corrective-run", type=Path, required=True)
    combine_parser.add_argument("--initial-root", type=Path, default=DEFAULT_INITIAL_ROOT)
    combine_parser.add_argument("--corrective-root", type=Path, required=True)
    combine_parser.add_argument("--output", type=Path, required=True)

    declarations_parser = commands.add_parser("cell-declarations")
    add_selection_arguments(declarations_parser)
    declarations_parser.add_argument("--output", type=Path, required=True)

    source_union_parser = commands.add_parser("source-union")
    add_selection_arguments(source_union_parser)
    source_union_parser.add_argument("--cell-declarations", type=Path, required=True)
    source_union_parser.add_argument("--output", type=Path, required=True)

    record_union_parser = commands.add_parser("record-union")
    add_selection_arguments(record_union_parser)
    record_union_parser.add_argument("--output", type=Path, required=True)

    assessment_parser = commands.add_parser("assess")
    add_selection_arguments(assessment_parser)
    assessment_parser.add_argument("--cell-declarations", type=Path, required=True)
    assessment_parser.add_argument("--source-union", type=Path, required=True)
    assessment_parser.add_argument("--record-union", type=Path, required=True)
    assessment_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "plan":
            write_new(
                args.output,
                build_plan(args.initial_plan.resolve(), args.initial_run.resolve()),
            )
            return 0
        if args.command == "cell":
            return run_cell(
                args.plan.resolve(),
                args.output_root.resolve(),
                args.original_event_id,
                args.attempt,
            )
        if args.command == "run":
            return run_corrective(
                args.plan.resolve(), args.output_root.resolve(), args.receipt.resolve()
            )
        if args.command == "combine":
            build_combined_run(
                args.corrective_plan.resolve(),
                args.corrective_run.resolve(),
                args.initial_root.resolve(),
                args.corrective_root.resolve(),
                args.output.resolve(),
            )
            return 0
        if args.command == "cell-declarations":
            build_declarations(
                args.corrective_plan.resolve(),
                args.corrective_run.resolve(),
                args.combined_run.resolve(),
                args.initial_root.resolve(),
                args.corrective_root.resolve(),
                args.output.resolve(),
            )
            return 0
        if args.command == "source-union":
            return run_source_union(
                args.corrective_plan.resolve(),
                args.corrective_run.resolve(),
                args.combined_run.resolve(),
                args.cell_declarations.resolve(),
                args.initial_root.resolve(),
                args.corrective_root.resolve(),
                args.output.resolve(),
            )
        if args.command == "record-union":
            build_record_union(
                args.corrective_plan.resolve(),
                args.corrective_run.resolve(),
                args.combined_run.resolve(),
                args.initial_root.resolve(),
                args.corrective_root.resolve(),
                args.output.resolve(),
            )
            return 0
        if args.command == "assess":
            return assess(
                args.corrective_plan.resolve(),
                args.corrective_run.resolve(),
                args.combined_run.resolve(),
                args.cell_declarations.resolve(),
                args.source_union.resolve(),
                args.record_union.resolve(),
                args.initial_root.resolve(),
                args.corrective_root.resolve(),
                args.output.resolve(),
            )
    except (OSError, RuntimeError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(
            f"iaf_final_corrective_failed:{type(error).__name__}:{error}",
            file=sys.stderr,
        )
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
