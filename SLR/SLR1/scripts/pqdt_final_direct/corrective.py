#!/usr/bin/env python3
"""Correct and reconcile the initial final PQDT Global search run."""

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
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_pqdt.py"
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/pqdt_pilot004/queries.py"
FINAL_ROOT = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/pqdt-global/final-searches"
)
INITIAL_PLAN = FINAL_ROOT / "final-event-plan.json"
INITIAL_RECEIPT = FINAL_ROOT / "run-receipt.json"
INITIAL_RUNNER = REPOSITORY_ROOT / "SLR/SLR1/scripts/pqdt_final_direct/run.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/pqdt-global/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-pqdt-final-direct-corrective-plan/v1"
RUN_SCHEMA = "slr1-pqdt-final-direct-corrective-run/v1"
RECONCILED_SCHEMA = "slr1-pqdt-final-direct-run-reconciliation/v1"
ASSESSMENT_SCHEMA = "slr1-pqdt-final-direct-assessment/v1"
SOURCE = "ProQuest Dissertations & Theses Global"
SOURCE_ID = "proquest_dissertations_theses_global"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-pqdt-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CORRECTIVE_PARTITIONS = ("A2", "A3", "B1")
INITIAL_ACCEPTED_PARTITIONS = tuple(
    partition for partition in PARTITIONS if partition not in CORRECTIVE_PARTITIONS
)
YEAR_START = 2011
YEAR_END = 2026
CUTOFF = "2026-08-24"
LIMIT = 10_000
MAX_PAGES = 500
TIMEOUT_SECONDS = 180
PAGE_DELAY_SECONDS = 0.1
DETAIL_DELAY_SECONDS = 0.1
INTER_EVENT_DELAY_SECONDS = 2.0
EXPECTED_ADAPTER_VERSION = "6"
SCREENSHOT_SCHEMA = "pqdt-automatic-screenshots/v1"
MARKER_SCHEMA = "pqdt_output_commit_marker_v1"
MARKER_TAG = "PQDT_COMMIT"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_ids(values: list[str] | set[str]) -> str:
    hasher = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
    return hasher.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve(strict=False).relative_to(REPOSITORY_ROOT))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode(
            "utf-8"
        )
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError(f"Could not write {path}")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def adapter_version() -> str:
    require_regular(ADAPTER)
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot determine the PQDT adapter version")
    return match.group(1)


def load_queries() -> Any:
    require_regular(QUERY_SNAPSHOT)
    spec = importlib.util.spec_from_file_location(
        "pqdt_final_corrective_queries", QUERY_SNAPSHOT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted PQDT partition schedule changed")
    if tuple(module.WILDCARD_SCHEDULE) != PARTITIONS or module.FAMILY_COUNT != 128:
        raise RuntimeError("The accepted PQDT wildcard translation changed")
    return module


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{MARKER_TAG}.json")


def screenshot_paths(path: Path) -> dict[str, Path]:
    return {
        "search_page": path.with_name(f"{path.stem}.search-page.png"),
        "results_page": path.with_name(f"{path.stem}.results-page.png"),
    }


def _applied(limits: Mapping[str, Any], name: str) -> Any:
    value = limits.get(name)
    if not isinstance(value, Mapping) or value.get("state") != "applied":
        return None
    return value.get("value")


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not path.is_file() or path.is_symlink() or not marker.is_file() or marker.is_symlink():
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = value.get("normalized_json")
    return bool(
        value.get("schema") == MARKER_SCHEMA
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def screenshot_summary(path: Path, value: Any) -> tuple[bool, list[dict[str, Any]]]:
    receipt = value if isinstance(value, Mapping) else {}
    valid = bool(
        receipt.get("schema_version") == SCREENSHOT_SCHEMA
        and receipt.get("automatic") is True
        and receipt.get("no_opt_out") is True
        and receipt.get("same_directory_as_json") is True
    )
    rows: list[dict[str, Any]] = []
    for kind, image in screenshot_paths(path).items():
        evidence = receipt.get(kind)
        image_valid = bool(
            image.is_file()
            and not image.is_symlink()
            and image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            and isinstance(evidence, Mapping)
            and evidence.get("path") == image.name
            and evidence.get("sha256") == digest(image)
            and isinstance(evidence.get("width"), int)
            and evidence["width"] > 0
            and isinstance(evidence.get("height"), int)
            and evidence["height"] > 0
            and evidence.get("browser_chrome_captured") is False
            and evidence.get("complete_page_url_retained") is False
            and evidence.get("session_identifiers_retained") is False
        )
        valid = valid and image_valid
        rows.append(
            {
                "kind": kind,
                "path": image.name,
                "sha256": digest(image) if image.is_file() and not image.is_symlink() else None,
                "valid": image_valid,
            }
        )
    return valid, rows


def capture_summary(rows: Any) -> tuple[bool, dict[str, Any]]:
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "missing_abstract_count": 0,
            "source_publication_type_counts": {},
            "missing_source_publication_type_count": 0,
        }
    valid = True
    full_abstracts = 0
    missing_abstracts = 0
    missing_types = 0
    reviewer_codes = 0
    type_counts: Counter[str] = Counter()
    identifiers: list[str] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            valid = False
            continue
        identifier = row.get("paperId")
        abstract = row.get("abstract")
        source_type = row.get("sourcePublicationType")
        if (
            not isinstance(identifier, str)
            or not identifier.isdigit()
            or row.get("rank") != index
            or row.get("source") != SOURCE
            or not isinstance(abstract, str)
            or row.get("abstract_source") != "PQDT rendered Abstract/Details record"
            or row.get("abstract_detail_verified") is not True
            or row.get("abstract_is_truncated") is not False
        ):
            valid = False
        else:
            identifiers.append(identifier)
        if isinstance(abstract, str) and abstract.strip():
            full_abstracts += 1
            if row.get("abstract_not_available") is not False:
                valid = False
        else:
            missing_abstracts += 1
            valid = False
        if (
            isinstance(source_type, str)
            and source_type.strip()
            and row.get("sourceType") == source_type
            and row.get("documentType") == source_type
            and row.get("source_publication_type_source")
            == "PQDT rendered result card"
            and row.get("document_type_source") == "PQDT rendered result card"
            and row.get("source_publication_type_not_available") is False
            and row.get("document_type_not_available") is False
        ):
            type_counts[source_type] += 1
        else:
            missing_types += 1
            valid = False
        if "publication_type" in row:
            reviewer_codes += 1
            valid = False
    if len(identifiers) != len(set(identifiers)):
        valid = False
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstracts,
        "missing_abstract_count": missing_abstracts,
        "source_publication_type_counts": dict(sorted(type_counts.items())),
        "missing_source_publication_type_count": missing_types,
        "reviewer_publication_type_present_count": reviewer_codes,
        "all_retained_rows_have_full_abstract": full_abstracts == len(rows),
        "all_retained_rows_have_source_publication_type": missing_types == 0,
    }


def artifact_summary(
    path: Path,
    *,
    partition: str,
    run_id: str,
    initial_plan: Mapping[str, Any],
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"artifact_written": False, "valid": False}
    try:
        data = load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "artifact_written": True,
            "valid": False,
            "parse_error": type(error).__name__,
        }
    queries = load_queries()
    query = queries.WILDCARD_SCHEDULE[partition]
    executed_query = f"{query} AND YR({YEAR_START}-{YEAR_END}) AND LA(English)"
    metadata = data.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    sort = strategy.get("sort")
    sort = sort if isinstance(sort, Mapping) else {}
    sort_value = sort.get("value")
    sort_value = sort_value if isinstance(sort_value, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    staged = prisma.get("staged_counts")
    staged = staged if isinstance(staged, Mapping) else {}
    rows = data.get("results")
    total = data.get("total")
    controls_valid = bool(
        data.get("schema_version") == "academic-search-result/v1"
        and data.get("source") == SOURCE
        and data.get("requested_query") == query
        and data.get("executed_query") == executed_query
        and prisma.get("run_id") == run_id
        and prisma.get("review_id") == REVIEW_ID
        and prisma.get("strategy_reference") == STRATEGY_REFERENCE
        and prisma.get("strategy_version")
        == initial_plan.get("repository_head_at_predeclaration")
        and prisma.get("phase") == PHASE
        and prisma.get("coverage", {}).get("coverage_scope") == "partition"
        and prisma.get("coverage", {}).get("partition_id") == partition
        and strategy.get("requested_query") == query
        and strategy.get("executed_query") == executed_query
        and strategy.get("executed_query_provenance") == "source_observed"
        and strategy.get("query_fields") == ["NOFT", "YR", "LA"]
        and strategy.get("search_scope") == "PQDT Global"
        and _applied(limits, "publication_date")
        == {"start": YEAR_START, "end": YEAR_END}
        and _applied(limits, "language") == "English"
        and _applied(limits, "publication_date_selector") == "ALL_DATES"
        and _applied(limits, "full_text") is False
        and _applied(limits, "exclude_duplicates") is False
        and _applied(limits, "spelling_variants") is False
        and _applied(limits, "form_variants") is False
        and _applied(limits, "show_variants") is False
        and all(
            isinstance(limits.get(name), Mapping)
            and limits[name].get("state") == "not_applied"
            for name in (
                "subject",
                "index_term",
                "institution",
                "institution_location",
                "document_type",
                "full_text_availability",
            )
        )
        and sort_value.get("value") == "DateAsc"
        and sort_value.get("label") == "Oldest first"
    )
    strict_valid = bool(
        isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 0
        and isinstance(rows, list)
        and total == len(rows)
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and prisma.get("report_readiness_reasons") in ([], None)
        and staged.get("source_reported_total") == total
        and staged.get("source_reported_total_status") == "reported"
        and staged.get("source_reported_total_exact") is True
        and staged.get("raw_source_records") == total
        and staged.get("client_side_exclusions") == 0
        and staged.get("within_source_duplicates_removed") == 0
        and staged.get("malformed_records_dropped") == 0
        and staged.get("records_exported") == total
    )
    adapter_valid = bool(
        adapter.get("adapter_id") == "search_pqdt"
        and adapter.get("adapter_version") == EXPECTED_ADAPTER_VERSION
        and adapter.get("script_sha256") == digest(ADAPTER)
    )
    screenshots_valid, screenshots = screenshot_summary(
        path, metadata.get("screenshots")
    )
    capture_valid, capture = capture_summary(rows)
    identifiers = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(rows, list) else []
    return {
        "artifact_written": True,
        "valid": bool(
            controls_valid
            and strict_valid
            and adapter_valid
            and marker_valid(path)
            and screenshots_valid
            and capture_valid
        ),
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "total": total,
        "stable_id_count": len(identifiers),
        "stable_id_set_sha256": digest_ids(identifiers),
        "controls_valid": controls_valid,
        "strict_complete_valid": strict_valid,
        "adapter_binding_valid": adapter_valid,
        "terminal_marker_valid": marker_valid(path),
        "screenshots_valid": screenshots_valid,
        "record_capture_valid": capture_valid,
        "record_capture": capture,
        "screenshots": screenshots,
    }


def corrective_event(partition: str, initial_plan: Mapping[str, Any]) -> dict[str, Any]:
    initial_events = {
        event["partition_id"]: event
        for event in initial_plan["events"]
        if isinstance(event, Mapping)
    }
    original = initial_events[partition]
    return {
        "event_id": f"final-main-{partition}-pqdt-r002",
        "supersedes_event_id": original["event_id"],
        "partition_id": partition,
        "query": original["query"],
        "query_sha256": original["query_sha256"],
        "query_characters": original["query_characters"],
        "output_filename": original["output_filename"],
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": TIMEOUT_SECONDS,
        "page_delay_seconds": PAGE_DELAY_SECONDS,
        "detail_delay_seconds": DETAIL_DELAY_SECONDS,
        "require_complete": True,
        "strict_passes": 2,
        "full_abstracts": True,
        "source_publication_types": True,
        "strategy_version": initial_plan["repository_head_at_predeclaration"],
    }


def build_corrective_plan() -> dict[str, Any]:
    for path in (
        SCRIPT_PATH,
        ADAPTER,
        QUERY_SNAPSHOT,
        INITIAL_PLAN,
        INITIAL_RECEIPT,
        INITIAL_RUNNER,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    ):
        require_regular(path)
    if adapter_version() != EXPECTED_ADAPTER_VERSION:
        raise RuntimeError("The corrective PQDT run requires adapter version 6")
    initial_plan = load(INITIAL_PLAN)
    initial_receipt = load(INITIAL_RECEIPT)
    if (
        initial_plan.get("schema_version") != "slr1-pqdt-final-direct-plan/v1"
        or initial_receipt.get("schema_version") != "slr1-pqdt-final-direct-run/v1"
        or initial_receipt.get("plan_sha256") != digest(INITIAL_PLAN)
        or initial_receipt.get("all_partitions_attempted") is not True
    ):
        raise RuntimeError("The initial PQDT run evidence changed")
    outcome_by_partition = {
        row["partition_id"]: row
        for row in initial_receipt.get("outcomes", [])
        if isinstance(row, Mapping) and isinstance(row.get("partition_id"), str)
    }
    if set(outcome_by_partition) != set(PARTITIONS):
        raise RuntimeError("The initial PQDT outcome schedule changed")
    initial_successes: dict[str, Any] = {}
    for partition in INITIAL_ACCEPTED_PARTITIONS:
        event = next(
            event
            for event in initial_plan["events"]
            if event["partition_id"] == partition
        )
        path = FINAL_ROOT / f"{partition}.json"
        summary = artifact_summary(
            path,
            partition=partition,
            run_id=event["event_id"],
            initial_plan=initial_plan,
        )
        if summary.get("valid") is not True:
            raise RuntimeError(f"Initial complete PQDT artifact is invalid: {partition}")
        initial_successes[partition] = {
            "event_id": event["event_id"],
            "artifact": relative(path),
            "artifact_sha256": digest(path),
            "marker": relative(marker_path(path)),
            "marker_sha256": digest(marker_path(path)),
            "total": summary["total"],
            "full_abstract_count": summary["record_capture"]["full_abstract_count"],
            "source_publication_type_counts": summary["record_capture"][
                "source_publication_type_counts"
            ],
        }
    failures: dict[str, Any] = {}
    for partition in CORRECTIVE_PARTITIONS:
        path = FINAL_ROOT / f"{partition}.json"
        require_regular(path)
        value = load(path)
        if (
            value.get("total") is not None
            or value.get("results") != []
            or value.get("output_metadata", {}).get("merge_eligible") is not False
            or marker_path(path).exists()
            or any(image.exists() for image in screenshot_paths(path).values())
        ):
            raise RuntimeError(f"Initial PQDT failure boundary changed: {partition}")
        failures[partition] = {
            "superseded_event_id": outcome_by_partition[partition]["event_id"],
            "artifact": relative(path),
            "artifact_sha256": digest(path),
            "artifact_bytes": path.stat().st_size,
            "source_total": None,
            "archive_destination": relative(
                FINAL_ROOT
                / "failures"
                / f"initial-{partition}.NON_MERGEABLE_FAILURE.json"
            ),
        }
    binding_paths = (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        INITIAL_PLAN,
        INITIAL_RECEIPT,
        INITIAL_RUNNER,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "corrective_sequence": 2,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": REVIEW_ID,
        "phase": PHASE,
        "strategy_reference": STRATEGY_REFERENCE,
        "strategy_version": initial_plan["repository_head_at_predeclaration"],
        "reason": (
            "The initial run retained null-total nonmergeable failures for A2, A3, "
            "and B1. It also recorded a local validation false negative for six "
            "marker-bound complete artifacts because the local runner expected the "
            "compact output to retain the nonpersistent results_retrieved field."
        ),
        "initial_run": {
            "plan": relative(INITIAL_PLAN),
            "plan_sha256": digest(INITIAL_PLAN),
            "receipt": relative(INITIAL_RECEIPT),
            "receipt_sha256": digest(INITIAL_RECEIPT),
            "all_partitions_attempted": True,
            "local_validation_false_negative": {
                "affected_partitions": list(INITIAL_ACCEPTED_PARTITIONS),
                "cause": "compact PRISMA output intentionally omits top-level results_retrieved",
                "source_artifacts_changed": False,
                "independent_revalidation_required": True,
            },
            "independently_revalidated_successes": initial_successes,
            "nonmergeable_failures": failures,
        },
        "correction_scope": {
            "partitions": list(CORRECTIVE_PARTITIONS),
            "unchanged_queries": True,
            "same_source_controls": True,
            "same_adapter": True,
            "attempts_per_event": 1,
        },
        "cutoff": {
            "exact_common_cutoff": CUTOFF,
            "source_year_start": YEAR_START,
            "source_year_end": YEAR_END,
            "source_precision": "year",
            "screening_requirement": "Screen every 2026 record against 2026-08-24.",
        },
        "record_capture_contract": {
            "full_abstracts_required_for_every_retained_record": True,
            "source_publication_types_required_for_every_retained_record": True,
            "reviewer_publication_type_coding": "deferred to screening",
        },
        "adapter": initial_plan["adapter"],
        "bindings": {
            "files": {relative(path): digest(path) for path in binding_paths}
        },
        "events": [
            corrective_event(partition, initial_plan)
            for partition in CORRECTIVE_PARTITIONS
        ],
    }


def validate_corrective_plan(
    plan: Mapping[str, Any], *, verify_bindings: bool
) -> list[str]:
    errors: list[str] = []
    initial_plan = load(INITIAL_PLAN)
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("corrective_sequence") != 2
        or plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("strategy_version")
        != initial_plan.get("repository_head_at_predeclaration")
    ):
        errors.append("identity")
    initial = plan.get("initial_run")
    if (
        not isinstance(initial, Mapping)
        or initial.get("plan") != relative(INITIAL_PLAN)
        or initial.get("plan_sha256") != digest(INITIAL_PLAN)
        or initial.get("receipt") != relative(INITIAL_RECEIPT)
        or initial.get("receipt_sha256") != digest(INITIAL_RECEIPT)
        or initial.get("all_partitions_attempted") is not True
        or initial.get("local_validation_false_negative", {}).get(
            "source_artifacts_changed"
        )
        is not False
        or set(initial.get("independently_revalidated_successes", {}))
        != set(INITIAL_ACCEPTED_PARTITIONS)
        or set(initial.get("nonmergeable_failures", {}))
        != set(CORRECTIVE_PARTITIONS)
    ):
        errors.append("initial_run")
    correction = plan.get("correction_scope")
    if (
        not isinstance(correction, Mapping)
        or correction.get("partitions") != list(CORRECTIVE_PARTITIONS)
        or correction.get("unchanged_queries") is not True
        or correction.get("same_source_controls") is not True
        or correction.get("same_adapter") is not True
        or correction.get("attempts_per_event") != 1
    ):
        errors.append("correction_scope")
    cutoff = plan.get("cutoff")
    if (
        not isinstance(cutoff, Mapping)
        or cutoff.get("exact_common_cutoff") != CUTOFF
        or cutoff.get("source_year_start") != YEAR_START
        or cutoff.get("source_year_end") != YEAR_END
        or cutoff.get("source_precision") != "year"
    ):
        errors.append("cutoff")
    capture = plan.get("record_capture_contract")
    if (
        not isinstance(capture, Mapping)
        or capture.get("full_abstracts_required_for_every_retained_record")
        is not True
        or capture.get(
            "source_publication_types_required_for_every_retained_record"
        )
        is not True
    ):
        errors.append("record_capture")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != len(CORRECTIVE_PARTITIONS):
        errors.append("events")
    else:
        for event, partition in zip(events, CORRECTIVE_PARTITIONS, strict=True):
            expected = corrective_event(partition, initial_plan)
            if not isinstance(event, Mapping) or any(
                event.get(key) != value for key, value in expected.items()
            ):
                errors.append(f"event:{partition}")
    if verify_bindings:
        adapter = plan.get("adapter")
        if (
            not isinstance(adapter, Mapping)
            or adapter.get("id") != "search_pqdt"
            or adapter.get("version") != EXPECTED_ADAPTER_VERSION
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter")
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in files.items():
                path = REPOSITORY_ROOT / str(name)
                if not path.is_file() or path.is_symlink() or digest(path) != expected_hash:
                    errors.append(f"binding:{name}")
    return errors


def archive_initial_failures(plan: Mapping[str, Any]) -> None:
    failures = plan["initial_run"]["nonmergeable_failures"]
    for partition in CORRECTIVE_PARTITIONS:
        row = failures[partition]
        source = REPOSITORY_ROOT / row["artifact"]
        destination = REPOSITORY_ROOT / row["archive_destination"]
        require_regular(source)
        if digest(source) != row["artifact_sha256"]:
            raise RuntimeError(f"Initial failure changed before archive: {partition}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {destination}")
        os.rename(source, destination)
        if digest(destination) != row["artifact_sha256"]:
            raise RuntimeError(f"Archived failure digest changed: {partition}")


def command_for(
    event: Mapping[str, Any], output: Path, plan: Mapping[str, Any], cdp_url: str
) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
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
        "--year-start",
        str(YEAR_START),
        "--year-end",
        str(YEAR_END),
        "--language",
        "English",
        "--no-full-text",
        "--no-exclude-duplicates",
        "--no-spelling-variants",
        "--no-form-variants",
        "--no-show-variants",
        "--cdp-url",
        cdp_url,
        "--output-path",
        str(output),
        "--prisma-run-id",
        str(event["event_id"]),
        "--prisma-review-id",
        REVIEW_ID,
        "--prisma-strategy-reference",
        STRATEGY_REFERENCE,
        "--prisma-strategy-version",
        str(plan["strategy_version"]),
        "--prisma-phase",
        PHASE,
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        str(event["partition_id"]),
        "--prisma-partition-label",
        str(event["partition_id"]),
        "--prisma-partition-description",
        f"PQDT Global corrective final direct discovery partition {event['partition_id']}",
    ]


def run_corrective(plan_path: Path, receipt_path: Path) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_corrective_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid corrective PQDT plan: " + ", ".join(errors))
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url) is None:
        raise ValueError("Corrective PQDT execution requires a loopback browser endpoint")
    initial_plan = load(INITIAL_PLAN)
    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(plan["events"]):
        if index and INTER_EVENT_DELAY_SECONDS:
            time.sleep(INTER_EVENT_DELAY_SECONDS)
        output = FINAL_ROOT / str(event["output_filename"])
        occupied = [output, marker_path(output), *screenshot_paths(output).values()]
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise FileExistsError(
                f"Refusing to overwrite corrective artifacts for {event['partition_id']}"
            )
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                command_for(event, output, plan, cdp_url),
                check=False,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS * 6,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            summary = artifact_summary(
                output,
                partition=event["partition_id"],
                run_id=event["event_id"],
                initial_plan=initial_plan,
            )
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout if isinstance(error.stdout, str) else ""
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            summary = {
                "artifact_written": output.is_file(),
                "valid": False,
                "runner_failure": "subprocess_timeout",
            }
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "supersedes_event_id": event["supersedes_event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": relative(output) if output.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
            "stderr_bytes": len(stderr.encode("utf-8")),
            "stderr_final_line": (
                stderr.strip().splitlines()[-1][:500] if stderr.strip() else None
            ),
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "total": outcome.get("total"),
                    "full_abstracts": outcome.get("record_capture", {}).get(
                        "full_abstract_count"
                    ),
                    "source_types": outcome.get("record_capture", {}).get(
                        "source_publication_type_counts"
                    ),
                    "error": outcome.get("stderr_final_line"),
                }
            ),
            flush=True,
        )
    success = bool(
        len(outcomes) == len(plan["events"])
        and all(outcome.get("success") is True for outcome in outcomes)
    )
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final_corrective",
        "corrective_sequence": 2,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "accepted_event_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "all_corrective_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def reconcile(
    corrective_plan_path: Path,
    corrective_receipt_path: Path,
    reconciled_path: Path,
    source_union_path: Path,
    assessment_path: Path,
) -> int:
    for output in (reconciled_path, source_union_path, assessment_path):
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {output}")
    corrective_plan = load(corrective_plan_path)
    errors = validate_corrective_plan(corrective_plan, verify_bindings=True)
    corrective_receipt = load(corrective_receipt_path)
    if (
        corrective_receipt.get("schema_version") != RUN_SCHEMA
        or corrective_receipt.get("plan") != relative(corrective_plan_path)
        or corrective_receipt.get("plan_sha256") != digest(corrective_plan_path)
        or corrective_receipt.get("success") is not True
        or corrective_receipt.get("all_corrective_partitions_attempted") is not True
    ):
        errors.append("corrective_receipt")
    initial_plan = load(INITIAL_PLAN)
    initial_events = {
        event["partition_id"]: event
        for event in initial_plan["events"]
        if isinstance(event, Mapping)
    }
    corrective_events = {
        event["partition_id"]: event
        for event in corrective_plan["events"]
        if isinstance(event, Mapping)
    }
    partition_summaries: list[dict[str, Any]] = []
    input_paths: list[Path] = []
    all_ids: set[str] = set()
    occurrences = 0
    abstract_occurrences = 0
    type_occurrences: Counter[str] = Counter()
    for partition in PARTITIONS:
        if partition in corrective_events:
            event = corrective_events[partition]
            provenance = "corrective_002"
        else:
            event = initial_events[partition]
            provenance = "initial_final_run_independently_revalidated"
        path = FINAL_ROOT / f"{partition}.json"
        summary = artifact_summary(
            path,
            partition=partition,
            run_id=event["event_id"],
            initial_plan=initial_plan,
        )
        if summary.get("valid") is not True:
            errors.append(f"artifact:{partition}")
        else:
            input_paths.append(path)
            value = load(path)
            identifiers = {str(row["paperId"]) for row in value["results"]}
            all_ids.update(identifiers)
            occurrences += len(identifiers)
            abstract_occurrences += summary["record_capture"]["full_abstract_count"]
            type_occurrences.update(
                summary["record_capture"]["source_publication_type_counts"]
            )
        partition_summaries.append(
            {
                "partition_id": partition,
                "event_id": event["event_id"],
                "provenance": provenance,
                "artifact": relative(path),
                **summary,
            }
        )
    if errors:
        assessment = {
            "schema_version": ASSESSMENT_SCHEMA,
            "source": SOURCE,
            "status": "failed",
            "errors": errors,
            "partitions": partition_summaries,
        }
        write_new(assessment_path, assessment)
        return 1
    completed = subprocess.run(
        [
            "uv",
            "run",
            str(SOURCE_UNION_TOOL),
            "--input",
            *(str(path) for path in input_paths),
            "--output-path",
            str(source_union_path),
            "--expected-partitions",
            *PARTITIONS,
            "--expected-sources",
            SOURCE_ID,
            "--review-namespace",
            REVIEW_NAMESPACE,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0 or not source_union_path.is_file():
        assessment = {
            "schema_version": ASSESSMENT_SCHEMA,
            "source": SOURCE,
            "status": "failed",
            "errors": ["source_union_receipt"],
            "source_union_command": {
                "exit_code": completed.returncode,
                "stdout_sha256": hashlib.sha256(
                    completed.stdout.encode("utf-8")
                ).hexdigest(),
                "stderr_sha256": hashlib.sha256(
                    completed.stderr.encode("utf-8")
                ).hexdigest(),
                "stderr_final_line": (
                    completed.stderr.strip().splitlines()[-1][:500]
                    if completed.stderr.strip()
                    else None
                ),
            },
            "partitions": partition_summaries,
        }
        write_new(assessment_path, assessment)
        return 1
    source_union = load(source_union_path)
    if (
        source_union.get("schema_version")
        != "academic-search-source-union-receipt/v1"
        or source_union.get("review_namespace") != REVIEW_NAMESPACE
        or source_union.get("expected_partitions") != list(PARTITIONS)
        or source_union.get("expected_sources") != [SOURCE_ID]
        or source_union.get("algorithm", {}).get("version")
        != "academic-search-source-union/v2"
    ):
        errors.append("source_union_contract")
    reconciled = {
        "schema_version": RECONCILED_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final",
        "status": "complete" if not errors else "failed",
        "success": not errors,
        "initial_plan": relative(INITIAL_PLAN),
        "initial_plan_sha256": digest(INITIAL_PLAN),
        "initial_run_receipt": relative(INITIAL_RECEIPT),
        "initial_run_receipt_sha256": digest(INITIAL_RECEIPT),
        "corrective_plan": relative(corrective_plan_path),
        "corrective_plan_sha256": digest(corrective_plan_path),
        "corrective_run_receipt": relative(corrective_receipt_path),
        "corrective_run_receipt_sha256": digest(corrective_receipt_path),
        "source_union_receipt": relative(source_union_path),
        "source_union_receipt_sha256": digest(source_union_path),
        "local_validation_correction": {
            "affected_initial_successes": list(INITIAL_ACCEPTED_PARTITIONS),
            "cause": "initial local validator expected an intentionally compacted top-level field",
            "source_artifacts_modified": False,
            "independent_revalidation": "passed",
        },
        "partition_count": len(PARTITIONS),
        "accepted_event_count": len(input_paths),
        "source_occurrence_count": occurrences,
        "unique_numeric_pqdt_document_id_count": len(all_ids),
        "unique_numeric_pqdt_document_id_set_sha256": digest_ids(all_ids),
        "full_abstract_occurrence_count": abstract_occurrences,
        "missing_abstract_occurrence_count": occurrences - abstract_occurrences,
        "source_publication_type_occurrence_counts": dict(
            sorted(type_occurrences.items())
        ),
        "missing_source_publication_type_occurrence_count": occurrences
        - sum(type_occurrences.values()),
        "partitions": partition_summaries,
        "errors": errors,
    }
    write_new(reconciled_path, reconciled)
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "status": "complete" if not errors else "failed",
        "errors": errors,
        "cutoff": {
            "source_year_window": f"{YEAR_START}-{YEAR_END}",
            "exact_common_cutoff": CUTOFF,
            "cutoff_year_screening_required": True,
        },
        "query_schedule": {
            "partitions": list(PARTITIONS),
            "complete": len(input_paths) == len(PARTITIONS),
            "bounded_wildcard_families": 128,
            "controlled_vocabulary_supplement": False,
        },
        "record_capture": {
            "source_occurrences": occurrences,
            "full_abstract_occurrences": abstract_occurrences,
            "missing_abstract_occurrences": occurrences - abstract_occurrences,
            "source_publication_type_occurrences": sum(type_occurrences.values()),
            "missing_source_publication_type_occurrences": occurrences
            - sum(type_occurrences.values()),
            "source_publication_type_counts": dict(sorted(type_occurrences.items())),
            "reviewer_publication_type_coding": "deferred to screening",
        },
        "source_union": {
            "unique_records": len(all_ids),
            "stable_id_set_sha256": digest_ids(all_ids),
            "receipt": relative(source_union_path),
            "receipt_sha256": digest(source_union_path),
        },
        "reconciled_run_receipt": relative(reconciled_path),
        "reconciled_run_receipt_sha256": digest(reconciled_path),
        "partitions": partition_summaries,
    }
    write_new(assessment_path, assessment)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--plan", type=Path, required=True)
    check = commands.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    run = commands.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)
    finish = commands.add_parser("reconcile")
    finish.add_argument("--plan", type=Path, required=True)
    finish.add_argument("--receipt", type=Path, required=True)
    finish.add_argument("--reconciled-receipt", type=Path, required=True)
    finish.add_argument("--source-union", type=Path, required=True)
    finish.add_argument("--assessment", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "prepare":
        plan = build_corrective_plan()
        errors = validate_corrective_plan(plan, verify_bindings=True)
        if errors:
            raise ValueError("Generated corrective PQDT plan is invalid: " + ", ".join(errors))
        write_new(args.plan, plan)
        archive_initial_failures(plan)
        print(
            json.dumps(
                {
                    "saved": str(args.plan),
                    "archived_failures": list(CORRECTIVE_PARTITIONS),
                    "events": len(plan["events"]),
                }
            )
        )
        return 0
    if args.command == "check-plan":
        errors = validate_corrective_plan(load(args.plan), verify_bindings=True)
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        return 0 if not errors else 1
    if args.command == "run":
        return run_corrective(args.plan, args.receipt)
    if args.command == "reconcile":
        return reconcile(
            args.plan,
            args.receipt,
            args.reconciled_receipt,
            args.source_union,
            args.assessment,
        )
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
