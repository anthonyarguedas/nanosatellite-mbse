#!/usr/bin/env python3
"""Run the predeclared corrective IEEE Xplore final-search campaign."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
REPOSITORY_ROOT = SCRIPT_PATH.parents[4]
CORE_PATH = SCRIPT_DIR / "run.py"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/ieee_xplore_pilot005/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-plan/v1"
RUN_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-run/v1"
ASSESSMENT_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-assessment/v1"
SOURCE_UNION_SCHEMA = "academic-search-source-union-receipt/v1"

SOURCE = "IEEE Xplore"
SOURCE_ID = "ieee_xplore"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-ieee-xplore-main-direct-v2"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
YEAR_ENVELOPE = "2011_2026_Year"
PAGE_SIZE = 100
LIMIT = 10_000
MAX_PAGES = 100
TIMEOUT_SECONDS = 180
SEQUENCE = 2

PREDECESSOR_ROOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/ieee-xplore/final-searches"
PREDECESSOR_PLAN = PREDECESSOR_ROOT / "final-event-plan.json"
PREDECESSOR_RECEIPT = PREDECESSOR_ROOT / "run-receipt.json"
PREDECESSOR_ADAPTER_VERSION = "11"
PREDECESSOR_ADAPTER_SHA256 = (
    "5f237523a80652573fabaa6a04a65c12e5fb7385fda67bcb8d9fa3d599f59bc3"
)


def load_core() -> Any:
    spec = importlib.util.spec_from_file_location("ieee_final_direct_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_core()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return CORE.digest(path)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ordered_digest(values: list[str]) -> str:
    hasher = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
    return hasher.hexdigest()


def relative(path: Path) -> str:
    return CORE.relative(path)


def load(path: Path) -> dict[str, Any]:
    return CORE.load(path)


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise FileExistsError(f"Refusing to overwrite {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        CORE_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {relative(path): digest(path) for path in paths}


def predecessor() -> tuple[dict[str, Any], dict[str, Any]]:
    if not PREDECESSOR_PLAN.is_file() or PREDECESSOR_PLAN.is_symlink():
        raise RuntimeError("The superseded IEEE final plan is unavailable")
    if not PREDECESSOR_RECEIPT.is_file() or PREDECESSOR_RECEIPT.is_symlink():
        raise RuntimeError("The superseded IEEE final run receipt is unavailable")
    plan = load(PREDECESSOR_PLAN)
    receipt = load(PREDECESSOR_RECEIPT)
    if (
        plan.get("schema_version") != CORE.PLAN_SCHEMA
        or plan.get("adapter", {}).get("version") != PREDECESSOR_ADAPTER_VERSION
        or plan.get("adapter", {}).get("sha256") != PREDECESSOR_ADAPTER_SHA256
        or receipt.get("schema_version") != CORE.RUN_SCHEMA
        or receipt.get("plan_sha256") != digest(PREDECESSOR_PLAN)
        or receipt.get("success") is not False
        or receipt.get("all_partitions_attempted") is not True
    ):
        raise RuntimeError("The superseded IEEE final run is not the expected failure")
    return plan, receipt


def build_plan() -> dict[str, Any]:
    predecessor_plan, predecessor_receipt = predecessor()
    queries = CORE.load_queries()
    strategy_version = CORE.repository_head()
    events = []
    for partition in PARTITIONS:
        event = CORE.plan_event(
            partition,
            queries.SCHEDULE[partition],
            SEQUENCE,
            strategy_version,
        )
        event["browser_execution"] = "fresh_visible_browser"
        events.append(event)
    base = CORE.build_plan()
    base.update(
        {
            "schema_version": PLAN_SCHEMA,
            "created_at_utc": now(),
            "repository_head_at_predeclaration": strategy_version,
            "strategy_reference": STRATEGY_REFERENCE,
            "events": events,
            "bindings": {"files": bindings()},
            "execution_policy": {
                "one_source_execution_per_partition": True,
                "continue_after_partition_failure": True,
                "fresh_visible_browser_per_partition": True,
                "target_identifiers_retained": False,
                "retry_policy": "none_after_corrective_plan_execution_begins",
                "skip_full_abstracts": False,
                "publication_type_filter": None,
            },
            "corrective_run": {
                "sequence": SEQUENCE,
                "reason": (
                    "The first final campaign retained only one A1 row although four "
                    "rows had unresolved rendered publication dates. Adapter v11 counted "
                    "those rows as unresolved but omitted them from the normalized export. "
                    "The same campaign also recorded browser-open or rendered-state failures "
                    "for the remaining partitions."
                ),
                "superseded_plan": relative(PREDECESSOR_PLAN),
                "superseded_plan_sha256": digest(PREDECESSOR_PLAN),
                "superseded_run_receipt": relative(PREDECESSOR_RECEIPT),
                "superseded_run_receipt_sha256": digest(PREDECESSOR_RECEIPT),
                "scientific_query_changed": False,
                "adapter_repair": {
                    "prior_adapter_version": predecessor_plan["adapter"]["version"],
                    "prior_adapter_sha256": predecessor_plan["adapter"]["sha256"],
                    "repaired_behavior": (
                        "An unresolved rendered Date of Publication now remains in the "
                        "retained normalized export with publicationDateFilterStatus=unresolved."
                    ),
                    "unit_validation": (
                        "One strict retrieval-pass check retained a record with an "
                        "unresolved exact publication date and its full abstract."
                    ),
                },
            },
        }
    )
    return base


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    predecessor_plan, predecessor_receipt = predecessor()
    queries = CORE.load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("source_union_expected_sources") != [SOURCE_ID]
    ):
        errors.append("identity")
    window = plan.get("date_window", {})
    if (
        window.get("publication_date_start") != DATE_START
        or window.get("publication_date_end") != DATE_END
        or window.get("source_year_envelope") != YEAR_ENVELOPE
        or window.get("inclusive") is not True
    ):
        errors.append("date_window")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("collection") != "IEEE Xplore Documents"
        or configuration.get("field") != "Individually fielded All Metadata atoms"
        or configuration.get("scope") != "Documents"
        or configuration.get("access_scope") != "All Results"
        or configuration.get("search_within") is not None
        or configuration.get("sort") != "Oldest"
        or configuration.get("language_filter") is not None
        or configuration.get("publication_type_filter") is not None
        or configuration.get("peer_review_filter") is not None
        or configuration.get("full_text_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
        or configuration.get("full_abstracts") is not True
        or configuration.get("publication_types", {}).get("required") is not True
        or configuration.get("publication_types", {}).get("normalized_field")
        != "documentType"
        or configuration.get("abstracts", {}).get("required") is not True
        or configuration.get("abstracts", {}).get("normalized_field") != "abstract"
    ):
        errors.append("source_configuration")
    execution = plan.get("execution_policy", {})
    if (
        execution.get("fresh_visible_browser_per_partition") is not True
        or execution.get("target_identifiers_retained") is not False
        or execution.get("retry_policy") != "none_after_corrective_plan_execution_begins"
        or execution.get("skip_full_abstracts") is not False
        or execution.get("publication_type_filter") is not None
    ):
        errors.append("execution_policy")
    corrective = plan.get("corrective_run", {})
    if (
        corrective.get("sequence") != SEQUENCE
        or corrective.get("superseded_plan") != relative(PREDECESSOR_PLAN)
        or corrective.get("superseded_plan_sha256") != digest(PREDECESSOR_PLAN)
        or corrective.get("superseded_run_receipt") != relative(PREDECESSOR_RECEIPT)
        or corrective.get("superseded_run_receipt_sha256") != digest(PREDECESSOR_RECEIPT)
        or corrective.get("scientific_query_changed") is not False
        or corrective.get("adapter_repair", {}).get("prior_adapter_version")
        != predecessor_plan["adapter"]["version"]
        or corrective.get("adapter_repair", {}).get("prior_adapter_sha256")
        != predecessor_plan["adapter"]["sha256"]
        or predecessor_receipt.get("success") is not False
    ):
        errors.append("corrective_provenance")
    strategy_version = plan.get("repository_head_at_predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or [
        event.get("partition_id") for event in events if isinstance(event, Mapping)
    ] != list(PARTITIONS):
        return [*errors, "partition_coverage"]
    for event in events:
        if not isinstance(event, Mapping):
            errors.append("malformed_event")
            continue
        partition = event.get("partition_id")
        query = event.get("query")
        if not isinstance(partition, str) or not isinstance(query, str):
            errors.append("event_shape")
            continue
        expected = CORE.plan_event(partition, queries.SCHEDULE[partition], SEQUENCE, strategy_version)
        expected["browser_execution"] = "fresh_visible_browser"
        if dict(event) != expected:
            errors.append(f"event_contract:{partition}")
        if "*" in query or "?" in query or any(
            token in query.upper() for token in (" NEAR", " W/", " PRE/")
        ):
            errors.append(f"query_translation:{partition}")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        if (
            adapter.get("id") != "search_ieee_xplore"
            or adapter.get("version") != CORE.adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_changed")
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_digest in files.items():
                path = REPOSITORY_ROOT / str(name)
                if not path.is_file() or path.is_symlink() or digest(path) != expected_digest:
                    errors.append(f"binding_changed:{name}")
    return errors


def compact_date_window(prisma: Mapping[str, Any]) -> Mapping[str, Any]:
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    publication = limits.get("publication_date")
    publication = publication if isinstance(publication, Mapping) else {}
    value = publication.get("value")
    return value if isinstance(value, Mapping) else {}


def record_capture(rows: Any) -> tuple[bool, dict[str, Any]]:
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "source_abstract_not_available_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
            "unresolved_exact_date_count": 0,
        }
    valid = True
    seen: set[str] = set()
    full = 0
    unavailable = 0
    unresolved = 0
    type_counts: dict[str, int] = {}
    missing_type = 0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            valid = False
            continue
        identifier = row.get("paperId")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in seen
            or row.get("source") != SOURCE
            or row.get("scope") != "documents"
            or row.get("documentId") != identifier
            or not isinstance(abstract, str)
            or row.get("publicationDateFilterStatus") not in {"included", "unresolved"}
            or ("rank" in row and row.get("rank") != index)
        ):
            valid = False
        if isinstance(identifier, str):
            seen.add(identifier)
        if abstract:
            full += 1
            if (
                row.get("abstract_source") != "IEEE Xplore rendered document page"
                or row.get("abstract_is_truncated") is True
                or row.get("abstract_not_available") is True
            ):
                valid = False
        else:
            unavailable += 1
            if row.get("abstract_not_available") is not True:
                valid = False
        if row.get("publicationDateFilterStatus") == "unresolved":
            unresolved += 1
        if isinstance(document_type, str) and document_type.strip():
            type_counts[document_type] = type_counts.get(document_type, 0) + 1
        else:
            missing_type += 1
            valid = False
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full,
        "source_abstract_not_available_count": unavailable,
        "publication_type_counts": dict(sorted(type_counts.items())),
        "missing_publication_type_count": missing_type,
        "unresolved_exact_date_count": unresolved,
        "all_retained_rows_have_abstract_field": all(
            isinstance(row, Mapping) and isinstance(row.get("abstract"), str)
            for row in rows
        ),
        "all_retained_rows_have_publication_type": missing_type == 0,
    }


def compact_artifact_summary(
    path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"artifact_written": False, "valid": False}
    try:
        value = load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "artifact_written": True,
            "valid": False,
            "parse_error": type(error).__name__,
        }
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    rows = value.get("results")
    records_valid, capture = record_capture(rows)
    strict = metadata.get("ieee_strict_completion_receipt")
    strict = strict if isinstance(strict, Mapping) else {}
    reports = strict.get("pass_reports")
    reports = reports if isinstance(reports, list) else []
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
    staged = prisma.get("staged_counts")
    staged = staged if isinstance(staged, Mapping) else {}
    total = value.get("total")
    retained = capture["retained_record_count"]
    pass_exclusions = [
        report.get("excluded_by_client_date_filter")
        for report in reports
        if isinstance(report, Mapping)
    ]
    excluded = pass_exclusions[0] if len(pass_exclusions) == 2 else None
    ids = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(rows, list) else []
    date_window = compact_date_window(prisma)
    screenshot_valid, screenshots = CORE.screenshot_evidence(path, metadata.get("screenshots"))
    marker_ok = CORE.marker_valid(path)
    controls_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and value.get("executed_query") == event.get("query")
        and metadata.get("status") == "success"
        and metadata.get("merge_eligible") is True
        and metadata.get("retrieval_complete") is True
        and prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("partition_id") == event.get("partition_id")
        and strategy.get("executed_query") == event.get("query")
        and strategy.get("executed_query_provenance") == "source_observed"
        and strategy.get("search_scope") == "documents"
        and limits.get("access_scope", {}).get("value") == "all"
        and limits.get("search_within", {}).get("state") == "not_applied"
        and limits.get("date_added", {}).get("state") in {"not_applicable", "not_applied"}
        and limits.get("content_types", {}).get("state") in {"not_applicable", "not_applied"}
        and limits.get("result_facets", {}).get("state") in {"not_applicable", "not_applied"}
        and strategy.get("sort", {}).get("value") == "Oldest"
        and date_window.get("state") == "exact_dates"
        and date_window.get("field") == "Date of Publication"
        and date_window.get("requested_start") == DATE_START
        and date_window.get("requested_end") == DATE_END
        and date_window.get("source_year_range") == YEAR_ENVELOPE
        and date_window.get("source_filter") == "Publication Year"
        and date_window.get("source_precision") == "year"
        and date_window.get("local_filter_applied") is True
        and date_window.get("local_filter_required") is True
        and date_window.get("unresolved_policy") == "retain_and_report"
        and adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    strict_valid = bool(
        isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 0
        and isinstance(retained, int)
        and isinstance(excluded, int)
        and not isinstance(excluded, bool)
        and total == retained + excluded
        and len(ids) == retained == len(set(ids))
        and strict.get("schema_version") == "ieee-xplore-strict-two-pass-receipt/v1"
        and strict.get("status") == "success"
        and strict.get("passes_requested") == 2
        and strict.get("passes_completed") == 2
        and strict.get("source_reported_total") == total
        and strict.get("source_entries_traversed") == total
        and strict.get("records_exported") == retained
        and strict.get("total_reconciled") is True
        and strict.get("controls_reconciled") is True
        and strict.get("ordered_ids_reconciled") is True
        and strict.get("export_reconciled") is True
        and len(reports) == 2
        and all(
            isinstance(report, Mapping)
            and report.get("pass_number") == number
            and report.get("source_reported_total") == total
            and report.get("source_entries_traversed") == total
            and report.get("detail_records_retrieved") == total
            and report.get("exported_records") == retained
            and report.get("excluded_by_client_date_filter") == excluded
            and report.get("complete") is True
            for number, report in enumerate(reports, start=1)
        )
        and strict.get("ordered_exported_ids_sha256") == ordered_digest(ids)
        and staged.get("source_reported_total") == total
        and staged.get("source_reported_total_status") == "reported"
        and staged.get("source_reported_total_exact") is True
        and staged.get("records_exported") == retained
        and staged.get("client_side_exclusions") == excluded
    )
    capture_valid = bool(
        records_valid
        and all(
            isinstance(report, Mapping)
            and report.get("detail_records_retrieved") == total
            for report in reports
        )
    )
    return {
        "artifact_written": True,
        "valid": bool(
            controls_valid
            and strict_valid
            and capture_valid
            and screenshot_valid
            and marker_ok
        ),
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "controls_valid": controls_valid,
        "strict_two_pass_valid": strict_valid,
        "record_capture_valid": capture_valid,
        "screenshots_valid": screenshot_valid,
        "terminal_marker_valid": marker_ok,
        "source_total": total,
        "retained_record_count": retained,
        "client_date_excluded_count": excluded,
        "unresolved_exact_date_count": capture["unresolved_exact_date_count"],
        "stable_id_count": len(ids),
        "stable_id_set_sha256": CORE.digest_ids(set(ids)),
        "ordered_source_ids_sha256": strict.get("ordered_document_ids_sha256"),
        "ordered_retained_ids_sha256": strict.get("ordered_exported_ids_sha256"),
        "pages_per_pass": [
            report.get("pages_retrieved") for report in reports if isinstance(report, Mapping)
        ],
        "screenshots": screenshots,
        **capture,
    }


def final_command(event: Mapping[str, Any], output: Path, plan: Mapping[str, Any]) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
        "--publication-date-start",
        DATE_START,
        "--publication-date-end",
        DATE_END,
        "--scope",
        "documents",
        "--access-scope",
        "all",
        "--sort",
        "Oldest",
        "--page-size",
        str(event["page_size"]),
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--detail-delay-seconds",
        str(event["detail_delay_seconds"]),
        "--require-complete",
        "--fresh-browser",
        "--output-path",
        str(output),
        "--prisma-run-id",
        str(event["event_id"]),
        "--prisma-review-id",
        str(plan["review_id"]),
        "--prisma-strategy-reference",
        str(plan["strategy_reference"]),
        "--prisma-strategy-version",
        str(event["strategy_version"]),
        "--prisma-phase",
        str(plan["phase"]),
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        str(event["partition_id"]),
        "--prisma-partition-label",
        str(event["partition_id"]),
        "--prisma-partition-description",
        f"IEEE Xplore corrective final direct discovery partition {event['partition_id']}",
    ]


def output_paths_occupied(output: Path) -> bool:
    return any(
        candidate.exists() or candidate.is_symlink()
        for candidate in (
            output,
            CORE.marker_path(output),
            *CORE.screenshot_paths(output),
        )
    )


def run_final(plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid corrective IEEE plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The corrective IEEE output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        if output_paths_occupied(output):
            raise FileExistsError(
                f"Refusing to overwrite corrective artifacts for {event['partition_id']}"
            )
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                final_command(event, output, plan),
                check=False,
                capture_output=True,
                text=True,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            summary = compact_artifact_summary(output, event, plan)
        except Exception as error:
            summary = {
                "artifact_written": output.is_file() and not output.is_symlink(),
                "valid": False,
                "runner_failure": type(error).__name__,
            }
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() and not output.is_symlink() else None,
            "exit_code": exit_code,
            "source_command_attempt_count": 1,
            "browser_execution": "fresh_visible_browser",
            "target_identifier_retained": False,
            "stdout_sha256": digest_text(stdout),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": digest_text(stderr),
            "stderr_bytes": len(stderr.encode("utf-8")),
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": outcome.get("source_total"),
                    "retained_records": outcome.get("retained_record_count"),
                    "full_abstracts": outcome.get("full_abstract_count"),
                    "missing_publication_types": outcome.get("missing_publication_type_count"),
                    "error_stage": outcome.get("error_stage"),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == len(plan["events"]) and all(
        item.get("success") is True for item in outcomes
    )
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final_corrective",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"],
        "target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": len(outcomes),
        "accepted_event_count": sum(item.get("success") is True for item in outcomes),
        "all_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    union_path: Path,
    assessment_path: Path,
) -> int:
    if assessment_path.exists() or assessment_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {assessment_path}")
    plan = load(plan_path)
    run = load(receipt_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan") != relative(plan_path)
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_event_count") != len(plan["events"])
    ):
        errors.append("run_receipt")
    outcomes = {
        item.get("event_id"): item
        for item in run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    partitions: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    source_total_occurrences = 0
    retained_occurrences = 0
    exclusions = 0
    unresolved = 0
    full_abstracts = 0
    abstract_unavailable = 0
    publication_types: dict[str, int] = {}
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        summary = compact_artifact_summary(output, event, plan)
        outcome = outcomes.get(event["event_id"])
        if outcome is None:
            errors.append(f"missing_outcome:{event['partition_id']}")
        elif (
            outcome.get("success") is not True
            or summary.get("valid") is not True
            or outcome.get("artifact_sha256") != summary.get("artifact_sha256")
            or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
        ):
            errors.append(f"event:{event['partition_id']}")
        total = summary.get("source_total")
        retained = summary.get("retained_record_count")
        excluded = summary.get("client_date_excluded_count")
        if not all(isinstance(value, int) and value >= 0 for value in (total, retained, excluded)):
            errors.append(f"count_shape:{event['partition_id']}")
        elif total != retained + excluded:
            errors.append(f"date_accounting:{event['partition_id']}")
        source_total_occurrences += total if isinstance(total, int) else 0
        retained_occurrences += retained if isinstance(retained, int) else 0
        exclusions += excluded if isinstance(excluded, int) else 0
        unresolved += summary.get("unresolved_exact_date_count", 0)
        full_abstracts += summary.get("full_abstract_count", 0)
        abstract_unavailable += summary.get("source_abstract_not_available_count", 0)
        for publication_type, count in summary.get("publication_type_counts", {}).items():
            if isinstance(publication_type, str) and isinstance(count, int):
                publication_types[publication_type] = publication_types.get(publication_type, 0) + count
        if output.is_file() and not output.is_symlink():
            for row in load(output).get("results", []):
                if isinstance(row, Mapping) and isinstance(row.get("paperId"), str):
                    identifiers.add(row["paperId"])
        partitions.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "artifact": output.name,
                **summary,
            }
        )

    union_valid = False
    union_attempt: dict[str, Any] | None = None
    if not errors:
        union_valid, union_attempt = CORE.create_source_union(
            plan_path, output_dir, union_path
        )
        if not union_valid:
            errors.append("source_union_receipt")
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "adapter": plan["adapter"],
        "date_window": plan["date_window"],
        "corrective_run": plan["corrective_run"],
        "partition_count": len(partitions),
        "accepted_partition_count": sum(item.get("valid") is True for item in partitions),
        "source_total_occurrence_count": source_total_occurrences,
        "retained_record_occurrence_count": retained_occurrences,
        "client_date_excluded_occurrence_count": exclusions,
        "unresolved_exact_date_occurrence_count": unresolved,
        "unique_retained_source_record_count": len(identifiers),
        "unique_retained_source_record_id_set_sha256": CORE.digest_ids(identifiers),
        "full_abstract_occurrence_count": full_abstracts,
        "source_abstract_not_available_occurrence_count": abstract_unavailable,
        "publication_type_occurrence_counts": dict(sorted(publication_types.items())),
        "publication_type_field_complete": all(
            item.get("all_retained_rows_have_publication_type") is True for item in partitions
        ),
        "detail_capture_complete": all(
            item.get("record_capture_valid") is True for item in partitions
        ),
        "source_union_receipt": relative(union_path)
        if union_valid and union_path.is_file()
        else None,
        "source_union_receipt_sha256": digest(union_path)
        if union_valid and union_path.is_file()
        else None,
        "source_union_valid": union_valid,
        "source_union_attempt": union_attempt,
        "partitions": partitions,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new(assessment_path, assessment)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-plan")
    build.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--verify-bindings", action="store_true")
    run = commands.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)
    run.add_argument("--settle-seconds", type=float, default=5.0)
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--assessment", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan()
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid corrective IEEE plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        if args.settle_seconds < 0:
            raise ValueError("--settle-seconds cannot be negative")
        return run_final(args.plan, args.output_dir, args.receipt, args.settle_seconds)
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.output_dir,
            args.source_union,
            args.assessment,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
