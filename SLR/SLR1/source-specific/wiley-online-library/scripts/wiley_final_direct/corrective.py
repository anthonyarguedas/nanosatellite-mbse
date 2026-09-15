#!/usr/bin/env python3
"""Run missing Wiley final cells and reconcile the complete final source union."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Mapping, Sequence

import run as base


SCRIPT_PATH = Path(__file__).resolve()
CORRECTIVE_PLAN_SCHEMA = "slr1-wiley-online-library-final-direct-corrective-plan/v1"
CORRECTIVE_RUN_SCHEMA = "slr1-wiley-online-library-final-direct-corrective-run/v1"
FINAL_ASSESSMENT_SCHEMA = "slr1-wiley-online-library-final-direct-assessment/v1"
CORRECTIVE_SEQUENCE = 2
CORRECTIVE_CELL_KEYS = (("A2", "mb"), ("B2", "direct"))
MERGE_TOOL = (
    Path.home()
    / "agent-tools"
    / "academic-api-search"
    / "skills"
    / "academic-api-search"
    / "scripts"
    / "merge_search_results.py"
)


def state_value(value: Any, expected: Any) -> bool:
    return bool(
        isinstance(value, Mapping)
        and value.get("state") == "applied"
        and value.get("value") == expected
    )


def state_not_applied(value: Any) -> bool:
    return bool(isinstance(value, Mapping) and value.get("state") == "not_applied")


def corrected_event_id(partition_id: str, cell_id: str) -> str:
    suffix = "" if cell_id == "direct" else f"-{cell_id}"
    return (
        f"final-main-{partition_id}{suffix}-wiley-online-library-"
        f"{CORRECTIVE_SEQUENCE:03d}"
    )


def build_corrective_plan(
    initial_plan_path: Path, initial_receipt_path: Path
) -> dict[str, Any]:
    initial = base.load(initial_plan_path)
    if base.validate_plan(initial, verify_bindings=False):
        raise ValueError("The initial Wiley final plan failed structural validation")
    initial_bindings = initial.get("bindings", {}).get("files", {})
    source_affecting_paths = (
        base.SCRIPT_PATH,
        base.QUERY_SNAPSHOT,
        base.SOURCE_GUIDELINE,
        base.DISCOVERY_PROTOCOL,
    )
    if any(
        initial_bindings.get(base.relative(path)) != base.digest(path)
        for path in source_affecting_paths
    ) or initial.get("adapter", {}).get("sha256") != base.digest(base.ADAPTER):
        raise ValueError("A source-affecting initial Wiley binding changed")
    initial_receipt = base.load(initial_receipt_path)
    if not (
        initial_receipt.get("schema_version") == base.RUN_SCHEMA
        and initial_receipt.get("plan_sha256") == base.digest(initial_plan_path)
        and initial_receipt.get("all_source_cells_attempted") is True
        and initial_receipt.get("success") is False
    ):
        raise ValueError("The initial Wiley final failure receipt is not eligible for correction")
    source_events = {
        (event["partition_id"], event["cell_id"]): event
        for event in initial["events"]
    }
    receipt_outcomes = {
        (outcome.get("partition_id"), outcome.get("cell_id")): outcome
        for outcome in initial_receipt.get("outcomes", [])
        if isinstance(outcome, Mapping)
    }
    events: list[dict[str, Any]] = []
    for key in CORRECTIVE_CELL_KEYS:
        source = source_events.get(key)
        outcome = receipt_outcomes.get(key)
        if source is None or outcome is None or outcome.get("exit_code") != 1:
            raise ValueError(f"The initial null failure for {key} is not established")
        failed_artifact = initial_plan_path.parent / str(source["output_filename"])
        failed_value = base.load(failed_artifact)
        failed_metadata = failed_value.get("output_metadata")
        failed_metadata = failed_metadata if isinstance(failed_metadata, Mapping) else {}
        failed_prisma = failed_metadata.get("prisma_search_run")
        failed_prisma = failed_prisma if isinstance(failed_prisma, Mapping) else {}
        if not (
            failed_value.get("schema_version") == "academic-search-result/v1"
            and failed_value.get("total") is None
            and failed_value.get("results") == []
            and failed_metadata.get("status") == "error"
            and failed_metadata.get("merge_eligible") is False
            and failed_value.get("do_not_merge") is True
            and failed_prisma.get("report_ready") is False
        ):
            raise ValueError(f"The initial failure artifact for {key} is not null and nonmergeable")
        partition_id, cell_id = key
        event_id = corrected_event_id(partition_id, cell_id)
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
                "superseded_failure_artifact": {
                    "path": base.relative(failed_artifact),
                    "sha256": base.digest(failed_artifact),
                    "bytes": failed_artifact.stat().st_size,
                    "source_total": None,
                    "stable_ids": [],
                    "merge_eligible": False,
                },
            }
        )
    return {
        "schema_version": CORRECTIVE_PLAN_SCHEMA,
        "created_at_utc": base.now(),
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "review_id": initial["review_id"],
        "phase": initial["phase"],
        "strategy_reference": initial["strategy_reference"],
        "strategy_version": initial["repository_head_at_predeclaration"],
        "corrective_sequence": CORRECTIVE_SEQUENCE,
        "reason": (
            "The initial final A2-mb and B2 commands ended with null, nonmergeable "
            "failure artifacts. They contributed no source total, stable ID, record, "
            "RIS file, or screenshot to the final union. This corrective plan runs "
            "fresh unchanged source cells and reuses no browser or source state."
        ),
        "initial_final_plan": {
            "path": base.relative(initial_plan_path),
            "sha256": base.digest(initial_plan_path),
        },
        "initial_final_run_receipt": {
            "path": base.relative(initial_receipt_path),
            "sha256": base.digest(initial_receipt_path),
        },
        "post_predeclaration_protocol_drift": {
            "path": base.relative(base.MAIN_PROTOCOL),
            "planned_sha256": initial_bindings.get(base.relative(base.MAIN_PROTOCOL)),
            "current_sha256": base.digest(base.MAIN_PROTOCOL),
            "source_affecting": False,
            "basis": (
                "The intervening protocol change concerns extraction and synthesis units. "
                "The cutoff, discovery schedule, Wiley translation, and adopted queries are unchanged."
            ),
        },
        "source_configuration": initial["source_configuration"],
        "capture_contract": initial["capture_contract"],
        "cutoff": initial["cutoff"],
        "execution_policy": {
            **initial["execution_policy"],
            "selected_null_failure_cells_only": True,
            "reuse_initial_source_state": False,
        },
        "adapter": initial["adapter"],
        "bindings": {
            "files": {
                base.relative(SCRIPT_PATH): base.digest(SCRIPT_PATH),
                base.relative(base.SCRIPT_PATH): base.digest(base.SCRIPT_PATH),
                base.relative(base.QUERY_SNAPSHOT): base.digest(base.QUERY_SNAPSHOT),
                base.relative(base.SOURCE_GUIDELINE): base.digest(base.SOURCE_GUIDELINE),
                base.relative(base.DISCOVERY_PROTOCOL): base.digest(base.DISCOVERY_PROTOCOL),
            }
        },
        "events": events,
    }


def validate_corrective_plan(
    plan: Mapping[str, Any], *, verify_bindings: bool = False
) -> list[str]:
    errors: list[str] = []
    if (
        plan.get("schema_version") != CORRECTIVE_PLAN_SCHEMA
        or plan.get("source") != base.SOURCE
        or plan.get("source_id") != base.SOURCE_ID
        or plan.get("review_namespace") != base.REVIEW_NAMESPACE
        or plan.get("review_id") != base.REVIEW_ID
        or plan.get("phase") != base.PHASE
        or plan.get("strategy_reference") != base.STRATEGY_REFERENCE
        or plan.get("corrective_sequence") != CORRECTIVE_SEQUENCE
    ):
        errors.append("identity")
    if not (
        isinstance(plan.get("reason"), str)
        and "null, nonmergeable" in plan["reason"]
        and "reuses no browser or source state" in plan["reason"]
    ):
        errors.append("reason")
    drift = plan.get("post_predeclaration_protocol_drift")
    if not isinstance(drift, Mapping) or (
        drift.get("path") != base.relative(base.MAIN_PROTOCOL)
        or not isinstance(drift.get("planned_sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", drift["planned_sha256"])
        or not isinstance(drift.get("current_sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", drift["current_sha256"])
        or drift.get("source_affecting") is not False
    ):
        errors.append("protocol_drift")
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
    ] != list(CORRECTIVE_CELL_KEYS):
        return [*errors, "event_schedule"]
    for event in events:
        partition_id = str(event["partition_id"])
        cell_id = str(event["cell_id"])
        query = event.get("query")
        failure = event.get("superseded_failure_artifact")
        if (
            event.get("event_id") != corrected_event_id(partition_id, cell_id)
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
            or not isinstance(failure, Mapping)
            or failure.get("source_total") is not None
            or failure.get("stable_ids") != []
            or failure.get("merge_eligible") is not False
            or not isinstance(failure.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", failure["sha256"])
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
        for reference in ("initial_final_plan", "initial_final_run_receipt"):
            item = plan.get(reference)
            path = (
                base.REPOSITORY_ROOT / str(item.get("path", ""))
                if isinstance(item, Mapping)
                else Path()
            )
            if not path.is_file() or base.digest(path) != item.get("sha256"):
                errors.append(f"changed:{reference}")
        for event in events:
            failure = event["superseded_failure_artifact"]
            path = base.REPOSITORY_ROOT / failure["path"]
            if (
                not path.is_file()
                or base.digest(path) != failure["sha256"]
                or path.stat().st_size != failure["bytes"]
            ):
                errors.append(f"changed_failure:{event['event_id']}")
    return errors


def merge_contract_valid(path: Path) -> bool:
    if not MERGE_TOOL.is_file():
        return False
    with tempfile.TemporaryDirectory(prefix="wiley-final-merge-check-") as directory:
        output = Path(directory) / "merged.json"
        completed = subprocess.run(
            [
                "uv",
                "run",
                str(MERGE_TOOL),
                "--input",
                str(path),
                "--output-path",
                str(output),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if completed.returncode != 0 or not output.is_file():
            return False
        try:
            value = base.load(output)
        except (OSError, ValueError, json.JSONDecodeError):
            return False
        return bool(
            value.get("report_ready") is True
            and value.get("dedup_summary", {}).get("input_files") == 1
        )


def native_ris_valid(native_dir: Path, metadata: Mapping[str, Any]) -> bool:
    if not native_dir.is_dir() or native_dir.is_symlink():
        return False
    files = sorted(
        path for path in native_dir.glob("*.ris") if path.is_file() and not path.is_symlink()
    )
    return bool(
        files
        and len(files) == metadata.get("native_export_artifact_count")
        and sum(path.stat().st_size for path in files)
        == metadata.get("native_export_total_bytes")
        and sum(path.name.startswith("preflight-page-") for path in files)
        == metadata.get("native_export_preflight_count")
        and sum(path.name.startswith("page-") for path in files)
        == metadata.get("native_export_page_scoped_count")
        and all(path.stat().st_size > 0 for path in files)
        and isinstance(metadata.get("native_export_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", metadata["native_export_sha256"])
    )


def normalized_summary(
    path: Path,
    event: Mapping[str, Any],
    plan: Mapping[str, Any],
    native_dir: Path,
    *,
    verify_merge_contract: bool = True,
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"valid": False, "artifact_written": False}
    try:
        value = base.load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    coverage = prisma.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    counts = prisma.get("staged_counts")
    counts = counts if isinstance(counts, Mapping) else {}
    rows = value.get("results")
    rows = rows if isinstance(rows, list) else []
    total = value.get("total")
    source_total = counts.get("source_reported_total")
    excluded_count = counts.get("client_side_exclusions")
    retained_count = counts.get("records_exported")
    expected_strategy_version = plan.get(
        "strategy_version", plan.get("repository_head_at_predeclaration")
    )
    record_ids: list[str] = []
    full_abstracts = 0
    source_omitted_abstracts = 0
    publication_types: dict[str, int] = {}
    missing_publication_types = 0
    unresolved_exact_dates = 0
    records_valid = True
    for row in rows:
        if not isinstance(row, Mapping):
            records_valid = False
            continue
        paper_id = row.get("paperId")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if (
            not isinstance(paper_id, str)
            or not paper_id
            or paper_id != row.get("doi")
            or paper_id in record_ids
            or not isinstance(abstract, str)
            or row.get("exactDateFilterStatus") not in {"included", "unresolved"}
            or row.get("query") != event.get("query")
        ):
            records_valid = False
        if isinstance(paper_id, str):
            record_ids.append(paper_id)
        if isinstance(abstract, str) and abstract:
            full_abstracts += 1
        else:
            source_omitted_abstracts += 1
        if isinstance(document_type, str) and document_type.strip():
            publication_types[document_type] = publication_types.get(document_type, 0) + 1
        else:
            missing_publication_types += 1
            records_valid = False
        if row.get("exactDateFilterStatus") == "unresolved":
            unresolved_exact_dates += 1
    records_valid = bool(
        records_valid
        and isinstance(source_total, int)
        and isinstance(excluded_count, int)
        and isinstance(retained_count, int)
        and source_total == total
        and counts.get("raw_source_records") == source_total
        and retained_count == len(rows)
        and source_total == retained_count + excluded_count
        and len(record_ids) == len(set(record_ids))
        and missing_publication_types == 0
    )
    controls_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == base.SOURCE
        and value.get("executed_query") == event.get("query")
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_contract") == "academic-search-merge/v1"
        and metadata.get("merge_eligible") is True
        and strategy.get("executed_query") == event.get("query")
        and strategy.get("executed_query_provenance") == "source_observed"
        and strategy.get("query_fields") == ["Anywhere", "AllField"]
        and strategy.get("search_scope") == "whole-platform Articles & Chapters"
        and state_value(limits.get("date_start"), base.DATE_START)
        and state_value(limits.get("date_end"), base.DATE_END)
        and state_value(limits.get("source_month_start"), "2011-01")
        and state_value(limits.get("source_month_end"), "2026-08")
        and state_value(limits.get("content"), base.CONTENT)
        and state_value(limits.get("target"), "default")
        and state_not_applied(limits.get("language"))
        and state_not_applied(limits.get("publication_type"))
        and state_not_applied(limits.get("open_access"))
        and state_not_applied(limits.get("subject_id"))
        and limits.get("date_input_mode") == "exact_dates"
        and limits.get("date_filter_mode") == "source_month_plus_client_exact_day"
        and strategy.get("sort")
        == {"state": "applied", "value": base.SORT, "provenance": "derived"}
    )
    prisma_valid = bool(
        prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == expected_strategy_version
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and prisma.get("report_readiness_reasons") == []
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("is_full_source_coverage") is False
        and coverage.get("partition_id") == event.get("partition_id")
        and adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    screenshots_valid, screenshots = base.screenshot_evidence(
        path, metadata.get("screenshots")
    )
    screenshot_contract_valid = bool(
        isinstance(metadata.get("screenshots"), Mapping)
        and metadata["screenshots"].get("schema_version")
        == base.WILEY_SCREENSHOT_SCHEMA
        and metadata["screenshots"].get("automatic") is True
        and metadata["screenshots"].get("no_opt_out") is True
        and screenshots_valid
    )
    native_valid = native_ris_valid(native_dir, metadata)
    marker_valid = base.marker_valid(path)
    contract_valid = merge_contract_valid(path) if verify_merge_contract else marker_valid
    return {
        "valid": bool(
            records_valid
            and controls_valid
            and prisma_valid
            and screenshot_contract_valid
            and native_valid
            and marker_valid
            and contract_valid
        ),
        "artifact_written": True,
        "artifact_sha256": base.digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "source_total": source_total,
        "retained_record_count": len(rows),
        "client_date_excluded_count": excluded_count,
        "unresolved_exact_date_count": unresolved_exact_dates,
        "stable_id_count": len(record_ids),
        "stable_id_set_sha256": base.digest_set(set(record_ids)),
        "full_abstract_count": full_abstracts,
        "source_omitted_abstract_count": source_omitted_abstracts,
        "all_retained_rows_have_abstract_field": all(
            isinstance(row, Mapping) and isinstance(row.get("abstract"), str)
            for row in rows
        ),
        "publication_type_counts": dict(sorted(publication_types.items())),
        "missing_publication_type_count": missing_publication_types,
        "all_retained_rows_have_publication_type": missing_publication_types == 0,
        "native_ris_artifact_count": metadata.get("native_export_artifact_count"),
        "native_ris_page_count": metadata.get("native_export_page_scoped_count"),
        "native_ris_total_bytes": metadata.get("native_export_total_bytes"),
        "controls_valid": controls_valid,
        "prisma_valid": prisma_valid,
        "screenshots_valid": screenshot_contract_valid,
        "native_ris_valid": native_valid,
        "terminal_marker_valid": marker_valid,
        "merge_contract_valid": contract_valid,
        "screenshots": screenshots,
    }


def corrective_final_command(
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


def run_corrective(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    *,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = base.load(plan_path)
    errors = validate_corrective_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid corrective Wiley plan: " + ", ".join(errors))
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"Refusing to reuse {output_dir}")
    output_dir.mkdir(parents=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Corrective Wiley execution requires a loopback browser endpoint")
    outcomes: list[dict[str, Any]] = []
    started = base.now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / event["output_filename"]
        native_dir = output_dir / event["native_ris_directory"]
        target_id: str | None = None
        target_closed = False
        exit_code: int | None = None
        stderr_tail: str | None = None
        try:
            target_id = base.create_authorized_wiley_target(cdp_url)
            completed = subprocess.run(
                corrective_final_command(
                    event, output, native_dir, cdp_url, target_id, plan
                ),
                check=False,
                capture_output=True,
                text=True,
            )
            exit_code = completed.returncode
            if exit_code != 0:
                stderr_tail = " ".join(completed.stderr.split())[-500:] or None
            summary = normalized_summary(output, event, plan, native_dir)
        except Exception as error:
            summary = {
                "valid": False,
                "artifact_written": output.is_file() and not output.is_symlink(),
                "runner_failure": type(error).__name__,
            }
            stderr_tail = type(error).__name__
        finally:
            if target_id is not None:
                target_closed = base.close_target(cdp_url, target_id)
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcomes.append(
            {
                "event_id": event["event_id"],
                "superseded_event_id": event["superseded_event_id"],
                "parent_event_id": event["parent_event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "success": success,
                "artifact": output.name if output.is_file() and not output.is_symlink() else None,
                "native_ris_directory": event["native_ris_directory"],
                "exit_code": exit_code,
                "source_command_attempt_count": 1,
                "authorized_target_created": target_id is not None,
                "authorized_target_close_requested": target_closed,
                "target_identifier_retained": False,
                **({"safe_stderr_tail": stderr_tail} if stderr_tail else {}),
                **summary,
            }
        )
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "cell": event["cell_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": summary.get("source_total"),
                    "full_abstracts": summary.get("full_abstract_count"),
                    "missing_publication_types": summary.get(
                        "missing_publication_type_count"
                    ),
                }
            ),
            flush=True,
        )
    complete = bool(
        len(outcomes) == len(plan["events"])
        and all(outcome.get("success") is True for outcome in outcomes)
    )
    receipt = {
        "schema_version": CORRECTIVE_RUN_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "event_kind": "corrective_final",
        "plan": plan_path.name,
        "plan_sha256": base.digest(plan_path),
        "corrective_sequence": CORRECTIVE_SEQUENCE,
        "target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": base.now(),
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "success": complete,
        "outcomes": outcomes,
    }
    base.write_new(receipt_path, receipt)
    return 0 if complete else 1


def select_complete_artifacts(
    initial_plan: Mapping[str, Any],
    initial_dir: Path,
    corrective_plan: Mapping[str, Any],
    corrective_dir: Path,
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path]]:
    corrected = {
        (event["partition_id"], event["cell_id"]): event
        for event in corrective_plan["events"]
    }
    selected: list[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path]] = []
    for initial_event in initial_plan["events"]:
        key = (initial_event["partition_id"], initial_event["cell_id"])
        event = corrected.get(key, initial_event)
        directory = corrective_dir if key in corrected else initial_dir
        path = directory / event["output_filename"]
        native_dir = directory / event["native_ris_directory"]
        selected.append((event, corrective_plan if key in corrected else initial_plan, path, native_dir))
    return selected


def build_union_manifest(
    initial_plan_path: Path,
    initial_plan: Mapping[str, Any],
    corrective_plan_path: Path,
    corrective_plan: Mapping[str, Any],
    selected: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path]],
) -> dict[str, Any]:
    by_partition: dict[str, list[dict[str, Any]]] = {}
    for event, plan, path, native_dir in selected:
        summary = normalized_summary(path, event, plan, native_dir)
        if summary.get("valid") is not True:
            raise ValueError(f"Cannot bind incomplete Wiley event {event['event_id']}")
        by_partition.setdefault(event["partition_id"], []).append(
            {
                "cell_id": event["cell_id"],
                "source_id": base.SOURCE_ID,
                "partition_id": event["partition_id"],
                "parent_event_id": base.parent_event_id(event["partition_id"]),
                "source_run_id": event["event_id"],
                "query": event["query"],
                "requested_query": event["query"],
                "artifact_sha256": base.digest(path),
                "artifact_byte_count": path.stat().st_size,
                "status": "final_complete",
                "report_ready": True,
            }
        )
    rows = []
    for partition_id in base.PARTITIONS:
        cells = sorted(by_partition.get(partition_id, []), key=lambda item: item["cell_id"])
        if not cells:
            raise ValueError(f"Missing final Wiley partition {partition_id}")
        rows.append(
            {
                "event_id": base.parent_event_id(partition_id),
                "event_kind": "final",
                "review_namespace": base.REVIEW_NAMESPACE,
                "source_id": base.SOURCE_ID,
                "partition_id": partition_id,
                "status": "final_complete",
                "query_cells": cells,
            }
        )
    return {
        "schema_version": base.UNION_MANIFEST_SCHEMA,
        "created_at_utc": base.now(),
        "review_namespace": base.REVIEW_NAMESPACE,
        "review": {
            "review_id": initial_plan["review_id"],
            "strategy_reference": initial_plan["strategy_reference"],
            "strategy_version": initial_plan["repository_head_at_predeclaration"],
            "phase": initial_plan["phase"],
        },
        "source_union_expected_partitions": list(base.PARTITIONS),
        "source_union_expected_sources": [base.SOURCE_ID],
        "initial_final_plan": {
            "artifact": base.relative(initial_plan_path),
            "sha256": base.digest(initial_plan_path),
        },
        "corrective_final_plan": {
            "artifact": base.relative(corrective_plan_path),
            "sha256": base.digest(corrective_plan_path),
        },
        "events": rows,
    }


def create_reconciled_source_union(
    initial_plan_path: Path,
    initial_dir: Path,
    corrective_plan_path: Path,
    corrective_dir: Path,
    manifest_path: Path,
    source_union_path: Path,
) -> int:
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {manifest_path}")
    if source_union_path.exists() or source_union_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {source_union_path}")
    initial_plan = base.load(initial_plan_path)
    corrective_plan = base.load(corrective_plan_path)
    if base.validate_plan(initial_plan) or validate_corrective_plan(corrective_plan):
        raise ValueError("Cannot reconcile invalid Wiley plans")
    selected = select_complete_artifacts(
        initial_plan, initial_dir, corrective_plan, corrective_dir
    )
    manifest = build_union_manifest(
        initial_plan_path,
        initial_plan,
        corrective_plan_path,
        corrective_plan,
        selected,
    )
    base.write_new(manifest_path, manifest)
    completed = subprocess.run(
        [
            "uv",
            "run",
            str(base.SOURCE_UNION_TOOL),
            "--input",
            *(str(path) for _event, _plan, path, _native_dir in selected),
            "--output-path",
            str(source_union_path),
            "--review-namespace",
            base.REVIEW_NAMESPACE,
            "--campaign-manifest",
            str(manifest_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Wiley source-union receipt creation failed: "
            + " ".join(completed.stderr.split())[-500:]
        )
    return 0


def assess(
    initial_plan_path: Path,
    initial_receipt_path: Path,
    initial_dir: Path,
    corrective_plan_path: Path,
    corrective_receipt_path: Path,
    corrective_dir: Path,
    manifest_path: Path,
    source_union_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    initial_plan = base.load(initial_plan_path)
    initial_receipt = base.load(initial_receipt_path)
    corrective_plan = base.load(corrective_plan_path)
    corrective_receipt = base.load(corrective_receipt_path)
    manifest = base.load(manifest_path)
    source_union = base.load(source_union_path)
    errors = base.validate_plan(initial_plan)
    errors.extend(validate_corrective_plan(corrective_plan))
    if not (
        initial_receipt.get("schema_version") == base.RUN_SCHEMA
        and initial_receipt.get("plan_sha256") == base.digest(initial_plan_path)
        and initial_receipt.get("all_source_cells_attempted") is True
    ):
        errors.append("initial_run_receipt")
    if not (
        corrective_receipt.get("schema_version") == CORRECTIVE_RUN_SCHEMA
        and corrective_receipt.get("plan_sha256") == base.digest(corrective_plan_path)
        and corrective_receipt.get("success") is True
        and corrective_receipt.get("accepted_source_cell_count")
        == len(corrective_plan["events"])
    ):
        errors.append("corrective_run_receipt")
    selected = select_complete_artifacts(
        initial_plan, initial_dir, corrective_plan, corrective_dir
    )
    expected_manifest = build_union_manifest(
        initial_plan_path,
        initial_plan,
        corrective_plan_path,
        corrective_plan,
        selected,
    )
    comparable_expected = dict(expected_manifest)
    comparable_saved = dict(manifest)
    comparable_expected.pop("created_at_utc", None)
    comparable_saved.pop("created_at_utc", None)
    if comparable_expected != comparable_saved:
        errors.append("source_union_manifest")

    event_evidence: list[dict[str, Any]] = []
    source_total_rows = 0
    retained_rows = 0
    excluded_rows = 0
    unresolved_rows = 0
    full_abstract_rows = 0
    source_omitted_abstract_rows = 0
    publication_types: dict[str, int] = {}
    all_ids: set[str] = set()
    screenshot_receipts: list[dict[str, Any]] = []
    for event, plan, path, native_dir in selected:
        summary = normalized_summary(path, event, plan, native_dir)
        if summary.get("valid") is not True:
            errors.append(f"event:{event['event_id']}")
        value = base.load(path)
        rows = value.get("results") if isinstance(value.get("results"), list) else []
        all_ids.update(
            row["paperId"]
            for row in rows
            if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
        )
        source_total_rows += summary.get("source_total", 0)
        retained_rows += summary.get("retained_record_count", 0)
        excluded_rows += summary.get("client_date_excluded_count", 0)
        unresolved_rows += summary.get("unresolved_exact_date_count", 0)
        full_abstract_rows += summary.get("full_abstract_count", 0)
        source_omitted_abstract_rows += summary.get("source_omitted_abstract_count", 0)
        for publication_type, count in summary.get("publication_type_counts", {}).items():
            publication_types[publication_type] = publication_types.get(publication_type, 0) + count
        screenshot_receipts.extend(summary.get("screenshots", []))
        event_evidence.append(
            {
                "event_id": event["event_id"],
                "supersedes_null_failure_event": event.get("superseded_event_id"),
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": base.relative(path),
                "artifact_sha256": summary.get("artifact_sha256"),
                "source_total": summary.get("source_total"),
                "retained_record_count": summary.get("retained_record_count"),
                "client_date_excluded_count": summary.get("client_date_excluded_count"),
                "unresolved_exact_date_count": summary.get("unresolved_exact_date_count"),
                "stable_id_count": summary.get("stable_id_count"),
                "stable_id_set_sha256": summary.get("stable_id_set_sha256"),
                "native_ris_artifact_count": summary.get("native_ris_artifact_count"),
                "native_ris_page_count": summary.get("native_ris_page_count"),
                "native_ris_total_bytes": summary.get("native_ris_total_bytes"),
                "full_abstract_count": summary.get("full_abstract_count"),
                "source_omitted_abstract_count": summary.get(
                    "source_omitted_abstract_count"
                ),
                "all_retained_rows_have_abstract_field": summary.get(
                    "all_retained_rows_have_abstract_field"
                ),
                "publication_type_counts": summary.get("publication_type_counts"),
                "all_retained_rows_have_publication_type": summary.get(
                    "all_retained_rows_have_publication_type"
                ),
                "screenshots": summary.get("screenshots"),
            }
        )
    source_section = source_union.get("source_unions", {}).get(base.SOURCE_ID, {})
    source_union_valid = bool(
        source_union.get("schema_version")
        == "academic-search-source-union-receipt/v1"
        and source_union.get("review_namespace") == base.REVIEW_NAMESPACE
        and source_union.get("review_id") == initial_plan.get("review_id")
        and source_union.get("strategy_reference")
        == initial_plan.get("strategy_reference")
        and source_union.get("strategy_version")
        == initial_plan.get("repository_head_at_predeclaration")
        and source_union.get("expected_partitions") == list(base.PARTITIONS)
        and source_union.get("expected_sources") == [base.SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and source_section.get("raw_record_count") == retained_rows
        and source_section.get("event_total_sum") == retained_rows
        and set(source_section.get("stable_record_ids", [])) == all_ids
    )
    if not source_union_valid:
        errors.append("source_union")
    capture_complete = bool(
        len(event_evidence) == len(initial_plan["events"])
        and sum(publication_types.values()) == retained_rows
        and full_abstract_rows + source_omitted_abstract_rows == retained_rows
        and all(
            event.get("all_retained_rows_have_abstract_field") is True
            and event.get("all_retained_rows_have_publication_type") is True
            for event in event_evidence
        )
    )
    if not capture_complete:
        errors.append("abstract_or_publication_type_capture")
    if source_total_rows != retained_rows + excluded_rows:
        errors.append("cutoff_accounting")
    validated_screenshots = sum(
        item.get("valid") is True for item in screenshot_receipts
    )
    if validated_screenshots != 2 * len(event_evidence):
        errors.append("screenshots")
    complete = not errors
    assessment = {
        "schema_version": FINAL_ASSESSMENT_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "event_kind": "final",
        "status": "passed" if complete else "failed",
        "final_search_partitions_complete": complete,
        "initial_final_run": {
            "plan": base.relative(initial_plan_path),
            "plan_sha256": base.digest(initial_plan_path),
            "run_receipt": base.relative(initial_receipt_path),
            "run_receipt_sha256": base.digest(initial_receipt_path),
            "complete_source_cells_retained": len(initial_plan["events"])
            - len(corrective_plan["events"]),
            "null_failure_source_cells_superseded": len(corrective_plan["events"]),
        },
        "corrective_final_run": {
            "plan": base.relative(corrective_plan_path),
            "plan_sha256": base.digest(corrective_plan_path),
            "run_receipt": base.relative(corrective_receipt_path),
            "run_receipt_sha256": base.digest(corrective_receipt_path),
            "complete_source_cells_retained": len(corrective_plan["events"]),
        },
        "source_union_manifest": {
            "artifact": base.relative(manifest_path),
            "sha256": base.digest(manifest_path),
        },
        "source_union": {
            "artifact": base.relative(source_union_path),
            "sha256": base.digest(source_union_path),
            "valid": source_union_valid,
        },
        "adapter": initial_plan["adapter"],
        "accepted_source_cell_count": len(event_evidence),
        "events": event_evidence,
        "cutoff_accounting": {
            "common_evidence_cutoff": base.DATE_END,
            "source_record_count_before_client_exact_day_filter": source_total_rows,
            "retained_record_count": retained_rows,
            "excluded_after_exact_cutoff_count": excluded_rows,
            "unresolved_exact_date_count": unresolved_rows,
            "complete": source_total_rows == retained_rows + excluded_rows,
        },
        "abstract_and_publication_type_capture": {
            "source_export": "visible page-scoped native RIS export with abstracts",
            "abstract_field": "abstract",
            "abstract_source_tags": ["N2", "AB"],
            "publication_type_field": "documentType",
            "publication_type_source_tag": "TY",
            "retained_rows": retained_rows,
            "rows_with_full_native_abstract": full_abstract_rows,
            "rows_where_native_ris_omitted_an_abstract": source_omitted_abstract_rows,
            "all_retained_rows_preserve_an_abstract_field": all(
                event.get("all_retained_rows_have_abstract_field") is True
                for event in event_evidence
            ),
            "all_retained_rows_preserve_a_publication_type": all(
                event.get("all_retained_rows_have_publication_type") is True
                for event in event_evidence
            ),
            "publication_type_counts": dict(sorted(publication_types.items())),
            "source_omission_policy": (
                "An empty abstract records Wiley's native RIS omission. No result-card "
                "description substitutes for a full abstract."
            ),
            "complete": capture_complete,
        },
        "stable_id_union": {
            "source_event_retained_record_count": retained_rows,
            "unique_stable_id_count": len(all_ids),
            "cross_partition_duplicate_occurrences": retained_rows - len(all_ids),
            "stable_id_set_sha256": base.digest_set(all_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "screenshots": {
            "expected_png_count": 2 * len(event_evidence),
            "validated_png_count": validated_screenshots,
            "receipts": screenshot_receipts,
        },
        "errors": errors,
    }
    base.write_new(output_path, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "source_records": source_total_rows,
                "retained_records": retained_rows,
                "unique_records": len(all_ids),
                "full_abstract_rows": full_abstract_rows,
                "publication_type_counts": publication_types,
            }
        )
    )
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--initial-plan", type=Path, required=True)
    plan_parser.add_argument("--initial-receipt", type=Path, required=True)
    plan_parser.add_argument("--output", type=Path, required=True)
    check_parser = commands.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=5.0)
    union_parser = commands.add_parser("source-union")
    union_parser.add_argument("--initial-plan", type=Path, required=True)
    union_parser.add_argument("--initial-dir", type=Path, required=True)
    union_parser.add_argument("--corrective-plan", type=Path, required=True)
    union_parser.add_argument("--corrective-dir", type=Path, required=True)
    union_parser.add_argument("--manifest", type=Path, required=True)
    union_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--initial-plan", type=Path, required=True)
    assess_parser.add_argument("--initial-receipt", type=Path, required=True)
    assess_parser.add_argument("--initial-dir", type=Path, required=True)
    assess_parser.add_argument("--corrective-plan", type=Path, required=True)
    assess_parser.add_argument("--corrective-receipt", type=Path, required=True)
    assess_parser.add_argument("--corrective-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union-manifest", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "plan":
        plan = build_corrective_plan(
            args.initial_plan.resolve(strict=True),
            args.initial_receipt.resolve(strict=True),
        )
        errors = validate_corrective_plan(plan)
        if errors:
            raise ValueError("Invalid generated corrective Wiley plan: " + ", ".join(errors))
        base.write_new(args.output, plan)
        print(json.dumps({"status": "saved", "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_corrective_plan(base.load(args.plan), verify_bindings=True)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        return run_corrective(
            args.plan.resolve(strict=True),
            args.output_dir.resolve(strict=False),
            args.receipt.resolve(strict=False),
            settle_seconds=args.settle_seconds,
        )
    if args.command == "source-union":
        return create_reconciled_source_union(
            args.initial_plan.resolve(strict=True),
            args.initial_dir.resolve(strict=True),
            args.corrective_plan.resolve(strict=True),
            args.corrective_dir.resolve(strict=True),
            args.manifest.resolve(strict=False),
            args.source_union.resolve(strict=False),
        )
    return assess(
        args.initial_plan.resolve(strict=True),
        args.initial_receipt.resolve(strict=True),
        args.initial_dir.resolve(strict=True),
        args.corrective_plan.resolve(strict=True),
        args.corrective_receipt.resolve(strict=True),
        args.corrective_dir.resolve(strict=True),
        args.source_union_manifest.resolve(strict=True),
        args.source_union.resolve(strict=True),
        args.output.resolve(strict=False),
    )


if __name__ == "__main__":
    raise SystemExit(main())
