#!/usr/bin/env python3
"""Plan, run, and assess final IEEE Xplore direct searches."""

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
from urllib.parse import quote, quote_plus, urlencode, urlparse
from urllib.request import Request, urlopen


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
)
SOURCE_UNION_TOOL = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/ieee_xplore_pilot005/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-ieee-xplore-final-direct-plan/v1"
RUN_SCHEMA = "slr1-ieee-xplore-final-direct-run/v1"
ASSESSMENT_SCHEMA = "slr1-ieee-xplore-final-direct-assessment/v1"
SOURCE_UNION_SCHEMA = "academic-search-source-union-receipt/v1"
MARKER_SCHEMA = "ieee_xplore_output_commit_marker_v1"
MARKER_TAG = "IEEE_COMMIT"
SCREENSHOT_SCHEMA = "ieee-automatic-screenshots/v1"

SOURCE = "IEEE Xplore"
SOURCE_ID = "ieee_xplore"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-ieee-xplore-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")

DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
YEAR_ENVELOPE = "2011_2026_Year"
PAGE_SIZE = 100
LIMIT = 10_000
MAX_PAGES = 100
TIMEOUT_SECONDS = 180
PAGE_DELAY_SECONDS = 0.0
DETAIL_DELAY_SECONDS = 0.0
MAX_REQUEST_TARGET_BYTES = 7_800
IEEE_ADVANCED_URL = "https://ieeexplore.ieee.org/search/advanced"

# This snapshot generated the literal schedule verified in IEEE Pilots 005 and
# 009. A final run must not silently adopt a changed term set.
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "03e205bff7defb4f4faec597027d4d35a9869fc579fc0b597a97ff20d7a78627"
)


def now() -> str:
    """Return a UTC timestamp suitable for a portable receipt."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    """Return the SHA-256 digest of one regular file."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_ids(values: set[str]) -> str:
    """Hash an unordered ID set with explicit record boundaries."""
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
    """Create one JSON artifact without replacing a prior artifact."""
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


def repository_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise RuntimeError("Cannot determine the repository revision")
    return value


def adapter_version() -> str:
    text = ADAPTER.read_text(encoding="utf-8")
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE
    )
    if match is None:
        raise RuntimeError("Cannot determine the IEEE Xplore adapter version")
    return match.group(1)


def load_queries() -> Any:
    """Load only the accepted literal IEEE query snapshot."""
    if not QUERY_SNAPSHOT.is_file() or QUERY_SNAPSHOT.is_symlink():
        raise RuntimeError("The accepted IEEE query snapshot is unavailable")
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted IEEE query snapshot changed")
    spec = importlib.util.spec_from_file_location("ieee_xplore_final_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted IEEE partition schedule changed")
    if tuple(module.SCHEDULE) != PARTITIONS:
        raise RuntimeError("The accepted IEEE query order changed")
    if any("*" in query or "?" in query for query in module.SCHEDULE.values()):
        raise RuntimeError("The accepted IEEE literal schedule contains a wildcard")
    return module


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{MARKER_TAG}.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def request_target_bytes(query: str, *, compact: bool) -> int:
    encoded = urlencode(
        [("newsearch", "true"), ("queryText", query)],
        quote_via=quote_plus if compact else quote,
        safe="()" if compact else "",
    )
    return len(f"/search/searchresult.jsp?{encoded}".encode("ascii"))


def transport_plan(query: str) -> dict[str, Any]:
    percent_bytes = request_target_bytes(query, compact=False)
    compact_bytes = request_target_bytes(query, compact=True)
    use_compact = percent_bytes > MAX_REQUEST_TARGET_BYTES
    selected_bytes = compact_bytes if use_compact else percent_bytes
    if selected_bytes > MAX_REQUEST_TARGET_BYTES:
        raise RuntimeError("The IEEE query exceeds the validated request envelope")
    return {
        "decoded_parameter_sequence": ["newsearch=true", "queryText=<exact query>"],
        "percent_component_request_target_bytes": percent_bytes,
        "compact_equivalent_request_target_bytes": compact_bytes,
        "selected_encoding": "compact_space_and_safe_parentheses"
        if use_compact
        else "percent_component",
        "selected_request_target_bytes": selected_bytes,
        "validated_request_target_bound_bytes": MAX_REQUEST_TARGET_BYTES,
        "decoded_query_changed": False,
    }


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {relative(path): digest(path) for path in paths}


def plan_event(partition: str, query: str, sequence: int, strategy_version: str) -> dict[str, Any]:
    return {
        "event_id": f"final-main-{partition}-ieee-xplore-{sequence:03d}",
        "partition_id": partition,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "wildcard_count": query.count("*") + query.count("?"),
        "output_filename": f"{partition}.json",
        "page_size": PAGE_SIZE,
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": TIMEOUT_SECONDS,
        "page_delay_seconds": PAGE_DELAY_SECONDS,
        "detail_delay_seconds": DETAIL_DELAY_SECONDS,
        "require_complete": True,
        "strict_passes": 2,
        "full_abstracts": True,
        "source_publication_types": True,
        "transport": transport_plan(query),
        "strategy_version": strategy_version,
    }


def build_plan() -> dict[str, Any]:
    queries = load_queries()
    strategy_version = repository_head()
    events = [
        plan_event(partition, queries.SCHEDULE[partition], index, strategy_version)
        for index, partition in enumerate(PARTITIONS, start=1)
    ]
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": REVIEW_ID,
        "phase": PHASE,
        "strategy_reference": STRATEGY_REFERENCE,
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "source_union_expected_partitions": list(PARTITIONS),
        "source_union_expected_sources": [SOURCE_ID],
        "date_window": {
            "publication_date_start": DATE_START,
            "publication_date_end": DATE_END,
            "inclusive": True,
            "source_year_envelope": YEAR_ENVELOPE,
            "source_precision": "year_envelope_with_rendered_exact_publication_date_accounting",
            "screening_requirement": (
                "Retain unresolved rendered Date of Publication values. Exclude only "
                "records proved outside the inclusive common evidence window."
            ),
        },
        "source_configuration": {
            "collection": "IEEE Xplore Documents",
            "advanced_search_url": IEEE_ADVANCED_URL,
            "field": "Individually fielded All Metadata atoms",
            "scope": "Documents",
            "access_scope": "All Results",
            "search_within": None,
            "sort": "Oldest",
            "language_filter": None,
            "publication_type_filter": None,
            "peer_review_filter": None,
            "full_text_filter": None,
            "controlled_vocabulary_supplement": None,
            "wildcard": False,
            "proximity": False,
            "pair_expansion": False,
            "full_abstracts": True,
            "publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "source_method": "visible rendered result-card document type",
                "filter_applied": None,
            },
            "abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "source_method": "matching rendered IEEE document page",
                "source_omission_policy": (
                    "Retain an empty abstract only when the matching rendered "
                    "document page has no abstract. Do not retain a result snippet "
                    "as a full abstract."
                ),
            },
        },
        "translation": {
            "literal": "one straight double-quoted literal",
            "ordinary_atom": '("All Metadata":"literal")',
            "ordinary_block": "atoms joined by uppercase OR and full parentheses",
            "compound_block": "expanded nested AND and OR without a grouped field wrapper",
            "one_source_expression_per_partition": True,
            "term_counts": queries.TERM_COUNTS,
            "query_character_counts": {
                partition: len(queries.SCHEDULE[partition]) for partition in PARTITIONS
            },
            "query_sha256": {
                partition: digest_text(queries.SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "accepted_pilot_snapshot": relative(QUERY_SNAPSHOT),
            "accepted_pilot_snapshot_sha256": digest(QUERY_SNAPSHOT),
            "no_controlled_vocabulary_supplement": True,
            "wildcard_count": 0,
            "proximity_operators": False,
            "pair_expansion": False,
            "transport": {
                "validated_request_target_bound_bytes": MAX_REQUEST_TARGET_BYTES,
                "compact_encoding_rule": (
                    "Use compact spaces and safe parentheses only when equivalent "
                    "percent-component encoding exceeds the bound."
                ),
            },
        },
        "strict_contract": {
            "complete_rendered_passes": 2,
            "membership_gate": "equal complete ordered stable Article Number and retained export ID ledgers",
            "required_equal_controls": [
                "source total",
                "native page size",
                "scope",
                "access scope",
                "Search Within",
                "Publication Year envelope",
                "Oldest sort",
                "exact date-accounting statuses",
            ],
            "automatic_screenshots_required": True,
            "full_abstract_detail_page_required": True,
            "source_publication_type_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "fresh_authorized_ieee_target_per_partition": True,
            "target_identifiers_retained": False,
            "retry_policy": "none_after_final_plan_execution_begins",
            "skip_full_abstracts": False,
            "publication_type_filter": None,
        },
        "adapter": {
            "id": "search_ieee_xplore",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
            "detail_projection": {
                "abstract_field": "abstract",
                "publication_type_field": "documentType",
            },
        },
        "bindings": {"files": bindings()},
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
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
    ):
        errors.append("identity")
    if (
        plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("source_union_expected_sources") != [SOURCE_ID]
    ):
        errors.append("source_union_schedule")
    date_window = plan.get("date_window", {})
    if (
        date_window.get("publication_date_start") != DATE_START
        or date_window.get("publication_date_end") != DATE_END
        or date_window.get("inclusive") is not True
        or date_window.get("source_year_envelope") != YEAR_ENVELOPE
        or date_window.get("source_precision")
        != "year_envelope_with_rendered_exact_publication_date_accounting"
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
        or configuration.get("wildcard") is not False
        or configuration.get("proximity") is not False
        or configuration.get("pair_expansion") is not False
        or configuration.get("full_abstracts") is not True
        or configuration.get("publication_types", {}).get("required") is not True
        or configuration.get("publication_types", {}).get("normalized_field")
        != "documentType"
        or configuration.get("abstracts", {}).get("required") is not True
        or configuration.get("abstracts", {}).get("normalized_field") != "abstract"
    ):
        errors.append("source_configuration")
    translation = plan.get("translation", {})
    if (
        translation.get("term_counts") != queries.TERM_COUNTS
        or translation.get("accepted_pilot_snapshot") != relative(QUERY_SNAPSHOT)
        or translation.get("accepted_pilot_snapshot_sha256") != digest(QUERY_SNAPSHOT)
        or translation.get("no_controlled_vocabulary_supplement") is not True
        or translation.get("wildcard_count") != 0
        or translation.get("proximity_operators") is not False
        or translation.get("pair_expansion") is not False
        or translation.get("transport", {}).get("validated_request_target_bound_bytes")
        != MAX_REQUEST_TARGET_BYTES
    ):
        errors.append("translation")
    execution = plan.get("execution_policy", {})
    if (
        execution.get("one_source_execution_per_partition") is not True
        or execution.get("continue_after_partition_failure") is not True
        or execution.get("fresh_authorized_ieee_target_per_partition") is not True
        or execution.get("target_identifiers_retained") is not False
        or execution.get("retry_policy") != "none_after_final_plan_execution_begins"
        or execution.get("skip_full_abstracts") is not False
        or execution.get("publication_type_filter") is not None
    ):
        errors.append("execution_policy")
    events = plan.get("events")
    if not isinstance(events, list) or [
        event.get("partition_id") for event in events if isinstance(event, Mapping)
    ] != list(PARTITIONS):
        return [*errors, "partition_coverage"]
    strategy_version = plan.get("repository_head_at_predeclaration")
    for index, event in enumerate(events, start=1):
        if not isinstance(event, Mapping):
            errors.append(f"malformed_event:{index}")
            continue
        partition = event.get("partition_id")
        query = event.get("query")
        if not isinstance(partition, str) or not isinstance(query, str):
            errors.append(f"event_shape:{index}")
            continue
        if (
            event.get("event_id") != f"final-main-{partition}-ieee-xplore-{index:03d}"
            or query != queries.SCHEDULE.get(partition)
            or event.get("query_sha256") != digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("wildcard_count") != 0
            or event.get("output_filename") != f"{partition}.json"
            or event.get("page_size") != PAGE_SIZE
            or event.get("limit") != LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("timeout_seconds") != TIMEOUT_SECONDS
            or event.get("page_delay_seconds") != PAGE_DELAY_SECONDS
            or event.get("detail_delay_seconds") != DETAIL_DELAY_SECONDS
            or event.get("require_complete") is not True
            or event.get("strict_passes") != 2
            or event.get("full_abstracts") is not True
            or event.get("source_publication_types") is not True
            or event.get("transport") != transport_plan(query)
            or event.get("strategy_version") != strategy_version
        ):
            errors.append(f"event_contract:{partition}")
        if (
            "*" in query
            or "?" in query
            or any(token in query.upper() for token in (" NEAR", " W/", " PRE/"))
        ):
            errors.append(f"query_translation:{partition}")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        if (
            adapter.get("id") != "search_ieee_xplore"
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_changed")
        files = plan.get("bindings", {}).get("files", {})
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected in files.items():
                path = REPOSITORY_ROOT / str(name)
                if not path.is_file() or path.is_symlink() or digest(path) != expected:
                    errors.append(f"binding_changed:{name}")
    return errors


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if (
        not path.is_file()
        or path.is_symlink()
        or not marker.is_file()
        or marker.is_symlink()
    ):
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = value.get("normalized_json", {})
    return bool(
        value.get("schema") == MARKER_SCHEMA
        and isinstance(value.get("transaction_id"), str)
        and re.fullmatch(r"[0-9a-f]{64}", value["transaction_id"])
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def screenshot_evidence(path: Path, screenshots: Any) -> tuple[bool, list[dict[str, Any]]]:
    receipt = screenshots if isinstance(screenshots, Mapping) else {}
    valid = bool(
        receipt.get("schema_version") == SCREENSHOT_SCHEMA
        and receipt.get("automatic") is True
        and receipt.get("same_directory_as_json") is True
    )
    rows: list[dict[str, Any]] = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = receipt.get(key, {}) if isinstance(receipt, Mapping) else {}
        image_valid = False
        if image.is_file() and not image.is_symlink() and isinstance(evidence, Mapping):
            data = image.read_bytes()
            image_valid = bool(
                data.startswith(b"\x89PNG\r\n\x1a\n")
                and evidence.get("path") == image.name
                and evidence.get("sha256") == hashlib.sha256(data).hexdigest()
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
                "kind": key,
                "path": image.name,
                "sha256": digest(image)
                if image.is_file() and not image.is_symlink()
                else None,
                "valid": image_valid,
            }
        )
    return valid, rows


def records_capture_summary(rows: Any) -> tuple[bool, dict[str, Any]]:
    """Verify the full-abstract and publication-type capture contract."""
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "source_abstract_not_available_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
        }
    valid = True
    ids: set[str] = set()
    full_abstract_count = 0
    unavailable_abstract_count = 0
    type_counts: dict[str, int] = {}
    missing_type_count = 0
    unresolved_date_count = 0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            valid = False
            continue
        paper_id = row.get("paperId")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if (
            not isinstance(paper_id, str)
            or not paper_id
            or paper_id in ids
            or row.get("source") != SOURCE
            or row.get("scope") != "documents"
            or row.get("documentId") != paper_id
            or not isinstance(abstract, str)
            or row.get("publicationDateFilterStatus") not in {"included", "unresolved"}
            or ("rank" in row and row.get("rank") != index)
        ):
            valid = False
        if isinstance(paper_id, str):
            ids.add(paper_id)
        if abstract:
            full_abstract_count += 1
            if (
                row.get("abstract_source") != "IEEE Xplore rendered document page"
                or row.get("abstract_is_truncated") is True
                or row.get("abstract_not_available") is True
            ):
                valid = False
        else:
            unavailable_abstract_count += 1
            if row.get("abstract_not_available") is not True:
                valid = False
        if row.get("publicationDateFilterStatus") == "unresolved":
            unresolved_date_count += 1
        if isinstance(document_type, str) and document_type.strip():
            type_counts[document_type] = type_counts.get(document_type, 0) + 1
        else:
            missing_type_count += 1
            valid = False
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstract_count,
        "source_abstract_not_available_count": unavailable_abstract_count,
        "publication_type_counts": dict(sorted(type_counts.items())),
        "missing_publication_type_count": missing_type_count,
        "unresolved_exact_date_count": unresolved_date_count,
        "all_retained_rows_have_abstract_field": all(
            isinstance(row, Mapping) and isinstance(row.get("abstract"), str)
            for row in rows
        ),
        "all_retained_rows_have_publication_type": missing_type_count == 0,
    }


def strict_result_valid(value: Mapping[str, Any], event: Mapping[str, Any], plan: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Validate the adapter's strict two-pass result contract."""
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    rows = value.get("results")
    records_valid, record_summary = records_capture_summary(rows)
    total = value.get("total")
    excluded = metadata.get("excluded_by_client_date_filter")
    duplicates = metadata.get("within_source_duplicates_removed")
    malformed = metadata.get("malformed_records_dropped")
    counts_valid = all(
        isinstance(item, int) and not isinstance(item, bool) and item >= 0
        for item in (total, excluded, duplicates, malformed)
    )
    retained_expected = (
        total - excluded - duplicates - malformed if counts_valid else None
    )
    ids = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(rows, list) else []
    effective_page_size = metadata.get("effective_page_size")
    expected_pages = (
        max(1, (total + effective_page_size - 1) // effective_page_size)
        if counts_valid
        and isinstance(effective_page_size, int)
        and not isinstance(effective_page_size, bool)
        and effective_page_size > 0
        else None
    )
    date_window = metadata.get("publication_window")
    date_window = date_window if isinstance(date_window, Mapping) else {}
    year_readback = metadata.get("publication_year_readback")
    year_readback = year_readback if isinstance(year_readback, Mapping) else {}
    pass_reports = metadata.get("pass_reports")
    pass_reports = pass_reports if isinstance(pass_reports, list) else []
    strict_receipt = metadata.get("ieee_strict_completion_receipt")
    strict_receipt = strict_receipt if isinstance(strict_receipt, Mapping) else {}
    strict_completion = metadata.get("strict_completion")
    strict_completion = strict_completion if isinstance(strict_completion, Mapping) else {}
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    coverage = prisma.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    full_abstract_enrichment = metadata.get("full_abstract_enrichment")
    full_abstract_enrichment = (
        full_abstract_enrichment
        if isinstance(full_abstract_enrichment, Mapping)
        else {}
    )
    expected_query = event.get("query")
    controls_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and value.get("query") == expected_query
        and value.get("executed_query") == expected_query
        and metadata.get("requested_query") == expected_query
        and metadata.get("effective_query") == expected_query
        and metadata.get("executed_query") == expected_query
        and metadata.get("observed_exact_query_echo") is True
        and metadata.get("scope") == "documents"
        and metadata.get("effective_scope") == "documents"
        and metadata.get("access_scope") == "all"
        and metadata.get("effective_access_scope") == "all"
        and metadata.get("search_within") is None
        and metadata.get("effective_search_within") is None
        and metadata.get("sort_requested") == "Oldest"
        and metadata.get("sort_effective") == "Oldest"
        and metadata.get("year_range") == YEAR_ENVELOPE
        and metadata.get("publication_date_start") == DATE_START
        and metadata.get("publication_date_end") == DATE_END
        and date_window.get("state") == "exact_dates"
        and date_window.get("field") == "Date of Publication"
        and date_window.get("requested_start") == DATE_START
        and date_window.get("requested_end") == DATE_END
        and date_window.get("source_year_range") == YEAR_ENVELOPE
        and date_window.get("source_filter") == "Publication Year"
        and date_window.get("source_precision") == "year"
        and date_window.get("local_filter_applied") is True
        and date_window.get("local_filter_required") is True
        and date_window.get("inclusive") is True
        and date_window.get("date_added_is_not_publication_date") is True
        and date_window.get("unresolved_policy") == "retain_and_report"
        and year_readback.get("requested_search_window") == YEAR_ENVELOPE
        and year_readback.get("state")
        in {
            "exact_source_echo",
            "result_refinement_range_within_requested_window",
            "not_needed_source_zero",
        }
        and metadata.get("date_added_start") is None
        and metadata.get("date_added_end") is None
        and metadata.get("date_added_range") is None
        and metadata.get("date_added_is_publication_date") is False
        and metadata.get("content_type_refinements") == []
        and metadata.get("result_facet_refinements") == []
        and metadata.get("controlled_term_clauses") == []
        and metadata.get("filters_applied_in_ui") in {False, True}
        and prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("partition_id") == event.get("partition_id")
        and adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
        and strategy.get("executed_query") == expected_query
        and strategy.get("executed_query_provenance") == "source_observed"
    )
    strict_valid = bool(
        counts_valid
        and isinstance(rows, list)
        and retained_expected == len(rows) == len(ids) == len(set(ids))
        and value.get("results_retrieved") == len(rows)
        and metadata.get("source_total") == total
        and metadata.get("source_total_before_local_filter") == total
        and metadata.get("source_rows_rendered") == total
        and metadata.get("source_card_rows_seen") == total
        and metadata.get("source_entries_traversed") == total
        and metadata.get("source_entries_retrieved") == total
        and metadata.get("raw_source_records") == total
        and metadata.get("filtered_records_retained") == retained_expected
        and metadata.get("detail_records_retrieved") == total
        and expected_pages is not None
        and value.get("pages_retrieved") == expected_pages
        and metadata.get("browser_pages_observed") == expected_pages * 2
        and metadata.get("count_only") is False
        and metadata.get("require_complete") is True
        and metadata.get("passes_requested") == 2
        and metadata.get("passes_completed") == 2
        and metadata.get("strict_complete_pass_count") == 2
        and metadata.get("strict_total_reconciled") is True
        and metadata.get("strict_controls_reconciled") is True
        and metadata.get("strict_ordered_document_ids_reconciled") is True
        and metadata.get("strict_ordered_record_ids_reconciled") is True
        and metadata.get("strict_export_reconciled") is True
        and metadata.get("retrieval_complete") is True
        and metadata.get("normalized_export_complete") is True
        and metadata.get("export_complete") is True
        and metadata.get("status") == "success"
        and metadata.get("execution_completion_status") == "complete"
        and metadata.get("merge_eligible") is True
        and strict_completion.get("passes_completed") == 2
        and strict_completion.get("total_reconciled") is True
        and strict_completion.get("controls_reconciled") is True
        and strict_completion.get("ordered_ids_reconciled") is True
        and strict_completion.get("retrieval_complete") is True
        and strict_completion.get("export_complete") is True
        and metadata.get("verification_scope")
        == "complete_two_pass_record_id_reconciliation"
        and strict_receipt.get("schema_version")
        == "ieee-xplore-strict-two-pass-receipt/v1"
        and strict_receipt.get("status") == "success"
        and strict_receipt.get("passes_requested") == 2
        and strict_receipt.get("passes_completed") == 2
        and strict_receipt.get("source_reported_total") == total
        and strict_receipt.get("source_entries_traversed") == total
        and strict_receipt.get("records_exported") == retained_expected
        and strict_receipt.get("total_reconciled") is True
        and strict_receipt.get("controls_reconciled") is True
        and strict_receipt.get("ordered_ids_reconciled") is True
        and strict_receipt.get("export_reconciled") is True
        and isinstance(metadata.get("ordered_document_ids_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", metadata["ordered_document_ids_sha256"])
        and metadata.get("ordered_result_ids_sha256")
        == metadata.get("ordered_document_ids_sha256")
        and isinstance(metadata.get("ordered_exported_result_ids_sha256"), str)
        and re.fullmatch(
            r"[0-9a-f]{64}", metadata["ordered_exported_result_ids_sha256"]
        )
        and len(pass_reports) == 2
        and all(
            isinstance(report, Mapping)
            and report.get("pass_number") == number
            and report.get("source_reported_total") == total
            and report.get("pages_retrieved") == expected_pages
            and report.get("source_rows_rendered") == total
            and report.get("source_entries_traversed") == total
            and report.get("detail_records_retrieved") == total
            and report.get("exported_records") == retained_expected
            and report.get("complete") is True
            for number, report in enumerate(pass_reports, start=1)
        )
    )
    abstract_contract_valid = bool(
        records_valid
        and full_abstract_enrichment.get("enabled") is True
        and full_abstract_enrichment.get("method")
        == "matching_rendered_document_pages"
        and full_abstract_enrichment.get("attempted") == total
        and full_abstract_enrichment.get("enriched")
        == record_summary["full_abstract_count"]
        and full_abstract_enrichment.get("unavailable")
        == record_summary["source_abstract_not_available_count"]
        and full_abstract_enrichment.get("not_attempted") == 0
    )
    return bool(controls_valid and strict_valid and abstract_contract_valid), {
        "controls_valid": controls_valid,
        "strict_two_pass_valid": strict_valid,
        "record_capture_valid": abstract_contract_valid,
        "source_total": total,
        "retained_record_count": record_summary["retained_record_count"],
        "client_date_excluded_count": excluded,
        "unresolved_exact_date_count": record_summary["unresolved_exact_date_count"],
        "stable_id_count": len(ids),
        "stable_id_set_sha256": digest_ids(set(ids)),
        "ordered_source_ids_sha256": metadata.get("ordered_document_ids_sha256"),
        "ordered_retained_ids_sha256": metadata.get("ordered_exported_result_ids_sha256"),
        "effective_page_size": effective_page_size,
        "pages_per_pass": expected_pages,
        **record_summary,
    }


def artifact_summary(path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]) -> dict[str, Any]:
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
    artifact_valid, strict = strict_result_valid(value, event, plan)
    screenshots_valid, screenshot_rows = screenshot_evidence(
        path, metadata.get("screenshots")
    )
    terminal_marker_valid = marker_valid(path)
    return {
        "artifact_written": True,
        "valid": bool(artifact_valid and screenshots_valid and terminal_marker_valid),
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "screenshots_valid": screenshots_valid,
        "terminal_marker_valid": terminal_marker_valid,
        "screenshots": screenshot_rows,
        **strict,
    }


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urlopen(request, timeout=120) as response:
        return json.load(response)


def create_authorized_ieee_target(cdp_url: str, timeout_seconds: float = 60.0) -> str:
    """Create one temporary IEEE page that authorizes the owned adapter page."""
    created = cdp_json(
        cdp_url,
        f"/json/new?{quote(IEEE_ADVANCED_URL, safe='')}",
        method="PUT",
    )
    target_id = created.get("id") if isinstance(created, Mapping) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not return an explicit IEEE target")
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        targets = cdp_json(cdp_url, "/json/list")
        target = next(
            (
                item
                for item in targets
                if isinstance(item, Mapping) and item.get("id") == target_id
            ),
            None,
        )
        if isinstance(target, Mapping):
            parsed = urlparse(str(target.get("url", "")))
            if (
                target.get("type") == "page"
                and parsed.scheme == "https"
                and parsed.hostname == "ieeexplore.ieee.org"
            ):
                return target_id
        time.sleep(0.5)
    raise RuntimeError("The IEEE authorization target did not become ready")


def close_target(cdp_url: str, target_id: str) -> bool:
    try:
        with urlopen(f"{cdp_url.rstrip('/')}/json/close/{target_id}", timeout=15) as response:
            response.read()
    except Exception:
        return False
    return True


def final_command(
    event: Mapping[str, Any],
    output: Path,
    cdp_url: str,
    target_id: str,
    plan: Mapping[str, Any],
) -> list[str]:
    """Return the final adapter command without diagnostic abstract suppression."""
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
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
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
        f"IEEE Xplore final direct discovery partition {event['partition_id']}",
    ]


def output_paths_occupied(output: Path) -> bool:
    return any(
        path.exists() or path.is_symlink()
        for path in (output, marker_path(output), *screenshot_paths(output))
    )


def run_final(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    *,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid final IEEE plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The final IEEE output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url):
        raise ValueError("Final IEEE execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        if output_paths_occupied(output):
            raise FileExistsError(
                f"Refusing to overwrite final artifacts for {event['partition_id']}"
            )
        target_id: str | None = None
        target_closed = False
        exit_code: int | None = None
        stdout = ""
        stderr = ""
        try:
            target_id = create_authorized_ieee_target(cdp_url)
            completed = subprocess.run(
                final_command(event, output, cdp_url, target_id, plan),
                check=False,
                capture_output=True,
                text=True,
            )
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
            summary = artifact_summary(output, event, plan)
        except Exception as error:
            summary = {
                "artifact_written": output.is_file() and not output.is_symlink(),
                "valid": False,
                "runner_failure": type(error).__name__,
            }
        finally:
            if target_id is not None:
                target_closed = close_target(cdp_url, target_id)
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() and not output.is_symlink() else None,
            "exit_code": exit_code,
            "source_command_attempt_count": 1 if target_id is not None else 0,
            "authorized_target_created": target_id is not None,
            "authorized_target_close_requested": target_closed,
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
                    "missing_publication_types": outcome.get(
                        "missing_publication_type_count"
                    ),
                    "error_stage": outcome.get("error_stage"),
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
        "event_kind": "final",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"],
        "target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": sum(
            outcome.get("source_command_attempt_count", 0) for outcome in outcomes
        ),
        "accepted_event_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "all_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def create_source_union(
    plan_path: Path, output_dir: Path, output_path: Path
) -> tuple[bool, dict[str, Any]]:
    """Build the shared source-union receipt after every final event succeeds."""
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(plan_path)
    inputs = [output_dir / str(event["output_filename"]) for event in plan["events"]]
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *[str(path) for path in inputs],
        "--output-path",
        str(output_path),
        "--expected-partitions",
        *PARTITIONS,
        "--expected-source",
        SOURCE_ID,
        "--review-namespace",
        REVIEW_NAMESPACE,
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    output_valid = False
    if completed.returncode == 0 and output_path.is_file() and not output_path.is_symlink():
        try:
            receipt = load(output_path)
            output_valid = bool(
                receipt.get("schema_version") == SOURCE_UNION_SCHEMA
                and receipt.get("review_namespace") == REVIEW_NAMESPACE
                and receipt.get("expected_partitions") == list(PARTITIONS)
                and receipt.get("expected_sources") == [SOURCE_ID]
                and receipt.get("completeness_status") == "complete"
                and receipt.get("failure_status") == "none"
            )
        except (OSError, ValueError, json.JSONDecodeError):
            output_valid = False
    return output_valid, {
        "return_code": completed.returncode,
        "stdout_sha256": digest_text(completed.stdout),
        "stdout_bytes": len(completed.stdout.encode("utf-8")),
        "stderr_sha256": digest_text(completed.stderr),
        "stderr_bytes": len(completed.stderr.encode("utf-8")),
        "output_written": output_path.is_file() and not output_path.is_symlink(),
    }


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
        outcome.get("event_id"): outcome
        for outcome in run.get("outcomes", [])
        if isinstance(outcome, Mapping)
    }
    partitions: list[dict[str, Any]] = []
    all_ids: set[str] = set()
    source_total_occurrences = 0
    retained_occurrences = 0
    excluded_occurrences = 0
    unresolved_occurrences = 0
    full_abstract_occurrences = 0
    unavailable_abstract_occurrences = 0
    publication_type_counts: dict[str, int] = {}
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        summary = artifact_summary(output, event, plan)
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
        source_total = summary.get("source_total")
        retained = summary.get("retained_record_count")
        excluded = summary.get("client_date_excluded_count")
        if not all(
            isinstance(value, int) and value >= 0
            for value in (source_total, retained, excluded)
        ):
            errors.append(f"count_shape:{event['partition_id']}")
        elif source_total != retained + excluded:
            errors.append(f"date_accounting:{event['partition_id']}")
        source_total_occurrences += source_total if isinstance(source_total, int) else 0
        retained_occurrences += retained if isinstance(retained, int) else 0
        excluded_occurrences += excluded if isinstance(excluded, int) else 0
        unresolved = summary.get("unresolved_exact_date_count")
        unresolved_occurrences += unresolved if isinstance(unresolved, int) else 0
        full_abstract_occurrences += summary.get("full_abstract_count", 0)
        unavailable_abstract_occurrences += summary.get(
            "source_abstract_not_available_count", 0
        )
        for publication_type, count in summary.get("publication_type_counts", {}).items():
            if isinstance(publication_type, str) and isinstance(count, int):
                publication_type_counts[publication_type] = (
                    publication_type_counts.get(publication_type, 0) + count
                )
        if output.is_file() and not output.is_symlink():
            for row in load(output).get("results", []):
                if isinstance(row, Mapping) and isinstance(row.get("paperId"), str):
                    all_ids.add(row["paperId"])
        partitions.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "artifact": output.name,
                **summary,
            }
        )

    source_union_valid = False
    source_union_attempt: dict[str, Any] | None = None
    if not errors:
        source_union_valid, source_union_attempt = create_source_union(
            plan_path, output_dir, union_path
        )
        if not source_union_valid:
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
        "partition_count": len(partitions),
        "accepted_partition_count": sum(
            partition.get("valid") is True for partition in partitions
        ),
        "source_total_occurrence_count": source_total_occurrences,
        "retained_record_occurrence_count": retained_occurrences,
        "client_date_excluded_occurrence_count": excluded_occurrences,
        "unresolved_exact_date_occurrence_count": unresolved_occurrences,
        "unique_retained_source_record_count": len(all_ids),
        "unique_retained_source_record_id_set_sha256": digest_ids(all_ids),
        "full_abstract_occurrence_count": full_abstract_occurrences,
        "source_abstract_not_available_occurrence_count": unavailable_abstract_occurrences,
        "publication_type_occurrence_counts": dict(sorted(publication_type_counts.items())),
        "publication_type_field_complete": all(
            partition.get("all_retained_rows_have_publication_type") is True
            for partition in partitions
        ),
        "detail_capture_complete": all(
            partition.get("record_capture_valid") is True for partition in partitions
        ),
        "source_union_receipt": relative(union_path)
        if source_union_valid and union_path.is_file()
        else None,
        "source_union_receipt_sha256": digest(union_path)
        if source_union_valid and union_path.is_file()
        else None,
        "source_union_valid": source_union_valid,
        "source_union_attempt": source_union_attempt,
        "partitions": partitions,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new(assessment_path, assessment)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-plan")
    build_parser.add_argument("--output", type=Path, required=True)

    check_parser = subparsers.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    check_parser.add_argument("--verify-bindings", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=5.0)

    assess_parser = subparsers.add_parser("assess")
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
            raise ValueError("Generated an invalid final IEEE plan: " + ", ".join(errors))
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
        return run_final(
            args.plan,
            args.output_dir,
            args.receipt,
            settle_seconds=args.settle_seconds,
        )
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
