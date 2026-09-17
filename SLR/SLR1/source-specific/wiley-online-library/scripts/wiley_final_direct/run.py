#!/usr/bin/env python3
"""Plan, run, reconcile, and assess final Wiley direct searches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_wiley_online_library.py"
)
SOURCE_UNION_TOOL = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "source_union_receipt.py"
)
QUERY_SNAPSHOT = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/wiley-online-library/scripts/wiley_online_library_pilot005/queries.py"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/wiley-online-library/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-wiley-online-library-final-direct-plan/v1"
RUN_SCHEMA = "slr1-wiley-online-library-final-direct-run/v1"
UNION_MANIFEST_SCHEMA = "academic-search-event-manifest/v1"
ASSESSMENT_SCHEMA = "slr1-wiley-online-library-final-direct-assessment/v1"
WILEY_MARKER_SCHEMA = "wiley_output_commit_marker_v1"
WILEY_MARKER_TAG = "WILEY_COMMIT"
WILEY_SCREENSHOT_SCHEMA = "wiley-automatic-screenshots/v1"

SOURCE = "Wiley Online Library"
SOURCE_ID = "wiley_online_library"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-wiley-online-library-main-direct-v1"
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
CONTENT = "articlesChapters"
FIELD = "AllField"
SORT = "Earliest"
PASSES = 2
LIMIT = 5000
MAX_PAGES = 20
MAX_SOURCE_TOTAL = 5000
MAX_SNAPSHOT_ATTEMPTS = 2
TIMEOUT_SECONDS = 180
PAGE_DELAY_SECONDS = 0.05
WILEY_ADVANCED_URL = "https://onlinelibrary.wiley.com/search/advanced"
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "3023004858bfc887914e08e75842693e758eeedf906195efe0afd01789c0b7a7"
)
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
EXPECTED_EVENT_IDS = (
    "A1",
    "A2-mh",
    "A2-mb",
    "A3",
    "B1",
    "B2",
    "BG1",
    "BG2",
    "BC1",
    "BT2",
)


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


def digest_ordered(values: list[str]) -> str:
    return digest_text("\n".join(values))


def digest_set(values: set[str]) -> str:
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
    """Publish a new JSON file without replacing an existing artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
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
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise RuntimeError("Cannot determine the repository revision")
    return value


def adapter_version() -> str:
    text = ADAPTER.read_text(encoding="utf-8")
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE
    )
    if match is None:
        raise RuntimeError("Cannot determine the Wiley adapter version")
    return match.group(1)


def load_queries() -> Any:
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted Wiley query snapshot changed")
    spec = importlib.util.spec_from_file_location("wiley_final_direct_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.EXPECTED_EVENT_IDS) != EXPECTED_EVENT_IDS:
        raise RuntimeError("The adopted Wiley source-cell schedule changed")
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The adopted Wiley partition schedule changed")
    return module


def parent_event_id(partition_id: str) -> str:
    return f"final-main-{partition_id}-wiley-online-library-001"


def final_event_id(partition_id: str, cell_id: str) -> str:
    suffix = "" if cell_id == "direct" else f"-{cell_id}"
    return f"final-main-{partition_id}{suffix}-wiley-online-library-001"


def source_cell_name(partition_id: str, cell_id: str) -> str:
    return partition_id if cell_id == "direct" else f"{partition_id}-{cell_id}"


def source_cell_output_name(partition_id: str, cell_id: str) -> str:
    return f"{source_cell_name(partition_id, cell_id)}.json"


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {relative(path): digest(path) for path in paths}


def plan_event(source: Mapping[str, Any]) -> dict[str, Any]:
    partition_id = str(source["partition_id"])
    cell_id = str(source["cell_id"])
    query = str(source["query"])
    event_id = final_event_id(partition_id, cell_id)
    return {
        "event_id": event_id,
        "parent_event_id": parent_event_id(partition_id),
        "partition_id": partition_id,
        "cell_id": cell_id,
        "branch": str(source["branch"]),
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output_filename": source_cell_output_name(partition_id, cell_id),
        "native_ris_directory": f"native-ris/{source_cell_name(partition_id, cell_id)}",
        "date_start": DATE_START,
        "date_end": DATE_END,
        "field": FIELD,
        "content": CONTENT,
        "sort": SORT,
        "passes": PASSES,
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "max_source_total": MAX_SOURCE_TOTAL,
        "max_snapshot_attempts": MAX_SNAPSHOT_ATTEMPTS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "page_delay_seconds": PAGE_DELAY_SECONDS,
        "require_complete": True,
        "native_ris_with_abstracts": True,
        "normalized_record_fields": {
            "abstract": "full native RIS N2/AB content",
            "documentType": "native RIS TY publication type",
        },
    }


def build_plan() -> dict[str, Any]:
    queries = load_queries()
    events = [plan_event(item) for item in queries.ADOPTED_EVENTS]
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": REVIEW_ID,
        "phase": PHASE,
        "strategy_reference": STRATEGY_REFERENCE,
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "source_union_expected_partitions": list(PARTITIONS),
        "source_union_expected_sources": [SOURCE_ID],
        "cutoff": {
            "exact_common_cutoff": DATE_END,
            "source_date_start": DATE_START,
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "source_precision": "month_with_visible_first_published_exact_day_accounting",
            "screening_requirement": (
                "Retain unresolved visible First published days. Exclude only a date "
                "proved outside the inclusive common evidence window."
            ),
        },
        "source_configuration": {
            "route": "Full Wiley Online Library Articles & Chapters",
            "advanced_search_url": WILEY_ADVANCED_URL,
            "field": "One Anywhere row (AllField)",
            "content": CONTENT,
            "sort": "Date / sortBy=Earliest",
            "language_filter": None,
            "publication_type_filter": None,
            "peer_review_filter": None,
            "access_filter": None,
            "collections_filter": None,
            "full_text_filter": None,
            "controlled_vocabulary_supplement": None,
            "proximity_operators": False,
            "pair_expansion": False,
            "population_wildcards": ["CubeSat*", "nanosat*", "SmallSat*"],
        },
        "capture_contract": {
            "passes": PASSES,
            "full_abstracts": {
                "required": True,
                "source_method": "visible page-scoped native RIS export with abstracts",
                "normalized_field": "abstract",
                "source_tags": ["N2", "AB"],
                "source_omission_policy": (
                    "Retain an empty abstract only when Wiley's native RIS omits "
                    "the abstract. Do not replace it with a result-card snippet."
                ),
            },
            "publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "source_tag": "TY",
                "filter_applied": None,
            },
            "native_ris": "Preserve reconciled page-scoped RIS files for every final source cell.",
            "screenshots": "Automatic configured Advanced Search and first results PNGs.",
        },
        "execution_policy": {
            "one_fresh_owned_page_per_source_cell": True,
            "fresh_authorized_wiley_target_per_source_cell": True,
            "target_identifiers_retained": False,
            "two_complete_ordered_doi_passes": True,
            "retry_policy": "at most two fresh attempts, only for an isolated source snapshot change",
            "continue_after_source_cell_failure": True,
            "reuse_prior_pilot_state": False,
        },
        "adapter": {
            "id": "search_wiley_online_library",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "bindings": {"files": bindings()},
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool = False) -> list[str]:
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
    cutoff = plan.get("cutoff")
    if not isinstance(cutoff, Mapping) or (
        cutoff.get("exact_common_cutoff") != DATE_END
        or cutoff.get("source_date_start") != DATE_START
        or cutoff.get("source_month_start") != "2011-01"
        or cutoff.get("source_month_end") != "2026-08"
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration")
    if not isinstance(configuration, Mapping) or (
        configuration.get("route") != "Full Wiley Online Library Articles & Chapters"
        or configuration.get("field") != "One Anywhere row (AllField)"
        or configuration.get("content") != CONTENT
        or configuration.get("sort") != "Date / sortBy=Earliest"
        or configuration.get("language_filter") is not None
        or configuration.get("publication_type_filter") is not None
        or configuration.get("peer_review_filter") is not None
        or configuration.get("access_filter") is not None
        or configuration.get("collections_filter") is not None
        or configuration.get("full_text_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
        or configuration.get("proximity_operators") is not False
        or configuration.get("pair_expansion") is not False
        or configuration.get("population_wildcards")
        != ["CubeSat*", "nanosat*", "SmallSat*"]
    ):
        errors.append("source_configuration")
    capture = plan.get("capture_contract")
    if not isinstance(capture, Mapping) or (
        capture.get("passes") != PASSES
        or capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("normalized_field") != "abstract"
        or capture.get("full_abstracts", {}).get("source_tags") != ["N2", "AB"]
        or capture.get("publication_types", {}).get("required") is not True
        or capture.get("publication_types", {}).get("normalized_field") != "documentType"
        or capture.get("publication_types", {}).get("source_tag") != "TY"
        or capture.get("publication_types", {}).get("filter_applied") is not None
    ):
        errors.append("capture_contract")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != len(EXPECTED_EVENT_IDS):
        return [*errors, "event_count"]
    expected_sources = list(queries.ADOPTED_EVENTS)
    if [event.get("event_id") for event in events] != [
        final_event_id(str(item["partition_id"]), str(item["cell_id"]))
        for item in expected_sources
    ]:
        errors.append("event_order")
    for event, expected in zip(events, expected_sources):
        if not isinstance(event, Mapping):
            errors.append("malformed_event")
            continue
        partition_id = str(expected["partition_id"])
        cell_id = str(expected["cell_id"])
        query = str(expected["query"])
        if (
            event.get("event_id") != final_event_id(partition_id, cell_id)
            or event.get("parent_event_id") != parent_event_id(partition_id)
            or event.get("partition_id") != partition_id
            or event.get("cell_id") != cell_id
            or event.get("branch") != expected["branch"]
            or event.get("query") != query
            or event.get("query_sha256") != digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("output_filename")
            != source_cell_output_name(partition_id, cell_id)
            or event.get("native_ris_directory")
            != f"native-ris/{source_cell_name(partition_id, cell_id)}"
            or event.get("date_start") != DATE_START
            or event.get("date_end") != DATE_END
            or event.get("field") != FIELD
            or event.get("content") != CONTENT
            or event.get("sort") != SORT
            or event.get("passes") != PASSES
            or event.get("limit") != LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("max_source_total") != MAX_SOURCE_TOTAL
            or event.get("max_snapshot_attempts") != MAX_SNAPSHOT_ATTEMPTS
            or event.get("timeout_seconds") != TIMEOUT_SECONDS
            or event.get("page_delay_seconds") != PAGE_DELAY_SECONDS
            or event.get("require_complete") is not True
            or event.get("native_ris_with_abstracts") is not True
            or event.get("normalized_record_fields", {}).get("abstract")
            != "full native RIS N2/AB content"
            or event.get("normalized_record_fields", {}).get("documentType")
            != "native RIS TY publication type"
        ):
            errors.append(f"event_contract:{partition_id}:{cell_id}")
        if (
            len(query) > 2700
            or "NEAR" in query.upper()
            or " W/" in query.upper()
            or " PRE/" in query.upper()
            or any(token not in query for token in ("CubeSat*", "nanosat*", "SmallSat*"))
        ):
            errors.append(f"query_translation:{partition_id}:{cell_id}")
    if verify_bindings:
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_digest in files.items():
                path = REPOSITORY_ROOT / str(name)
                if not path.is_file() or digest(path) != expected_digest:
                    errors.append(f"binding_changed:{name}")
        adapter = plan.get("adapter")
        if not isinstance(adapter, Mapping) or (
            adapter.get("id") != "search_wiley_online_library"
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_changed")
    return errors


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{WILEY_MARKER_TAG}.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not marker.is_file() or marker.is_symlink() or not path.is_file() or path.is_symlink():
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = value.get("normalized_json")
    return bool(
        value.get("schema") == WILEY_MARKER_SCHEMA
        and isinstance(value.get("transaction_id"), str)
        and re.fullmatch(r"[0-9a-f]{64}", value["transaction_id"])
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def screenshot_evidence(
    path: Path, screenshots: Any
) -> tuple[bool, list[dict[str, Any]]]:
    valid = True
    rows: list[dict[str, Any]] = []
    evidence_map = screenshots if isinstance(screenshots, Mapping) else {}
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = evidence_map.get(key)
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
                "sha256": digest(image) if image.is_file() and not image.is_symlink() else None,
                "valid": image_valid,
            }
        )
    return valid, rows


def native_ris_directory_valid(native_dir: Path, metadata: Mapping[str, Any]) -> bool:
    if not native_dir.is_dir() or native_dir.is_symlink():
        return False
    ris_files = [path for path in native_dir.glob("*.ris") if path.is_file() and not path.is_symlink()]
    source_total = metadata.get("source_entries_retrieved")
    if source_total == 0:
        return len(ris_files) == 0
    return bool(
        metadata.get("native_capture", {}).get("preserved_native_files") is True
        and metadata.get("native_export_artifact_count") == len(ris_files)
        and len(ris_files) > 0
        and all(path.stat().st_size > 0 for path in ris_files)
        and any(path.name.startswith("preflight-") for path in ris_files)
    )


def record_fields_valid(
    rows: Any, ordered_ids: list[str], source_total: int, excluded_count: int
) -> tuple[bool, dict[str, Any]]:
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "source_omitted_abstract_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
        }
    valid = len(rows) + excluded_count == source_total
    seen: set[str] = set()
    full_abstract_count = 0
    source_omitted_abstract_count = 0
    publication_type_counts: dict[str, int] = {}
    missing_publication_type_count = 0
    for row in rows:
        if not isinstance(row, Mapping):
            valid = False
            continue
        paper_id = row.get("paperId")
        doi = row.get("doi")
        abstract = row.get("abstract")
        publication_type = row.get("documentType")
        if (
            not isinstance(paper_id, str)
            or not paper_id
            or paper_id != doi
            or paper_id not in ordered_ids
            or paper_id in seen
            or not isinstance(abstract, str)
            or row.get("exactDateFilterStatus") not in {"included", "unresolved"}
        ):
            valid = False
        seen.add(paper_id) if isinstance(paper_id, str) else None
        if isinstance(abstract, str) and abstract:
            full_abstract_count += 1
        else:
            source_omitted_abstract_count += 1
        if isinstance(publication_type, str) and publication_type.strip():
            publication_type_counts[publication_type] = (
                publication_type_counts.get(publication_type, 0) + 1
            )
        else:
            missing_publication_type_count += 1
            valid = False
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstract_count,
        "source_omitted_abstract_count": source_omitted_abstract_count,
        "publication_type_counts": dict(sorted(publication_type_counts.items())),
        "missing_publication_type_count": missing_publication_type_count,
        "all_retained_rows_have_abstract_field": all(
            isinstance(row, Mapping) and isinstance(row.get("abstract"), str)
            for row in rows
        ),
        "all_retained_rows_have_publication_type": missing_publication_type_count == 0,
    }


def artifact_summary(
    path: Path, event: Mapping[str, Any], plan: Mapping[str, Any], native_dir: Path
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"valid": False, "artifact_written": False}
    try:
        value = load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    rows = value.get("results")
    ordered_ids = metadata.get("ordered_source_ids")
    ordered_ids = ordered_ids if isinstance(ordered_ids, list) else []
    total = value.get("total")
    excluded_count = metadata.get("excluded_by_client_date_filter")
    excluded_count = excluded_count if isinstance(excluded_count, int) else -1
    records_valid, record_summary = record_fields_valid(
        rows, ordered_ids, total if isinstance(total, int) else -1, excluded_count
    )
    screenshots = metadata.get("screenshots")
    screenshots_valid, image_rows = screenshot_evidence(path, screenshots)
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    coverage = prisma.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    pass_reports = metadata.get("pass_reports")
    pass_reports = pass_reports if isinstance(pass_reports, list) else []
    ordered_hash = digest_ordered(ordered_ids)
    native_diagnostics = metadata.get("ris_export_diagnostics")
    native_diagnostics = native_diagnostics if isinstance(native_diagnostics, list) else []
    controls_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and value.get("requested_query") == event.get("query")
        and value.get("executed_query") == event.get("query")
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("require_complete") is True
        and metadata.get("execution_completion_status") == "complete"
        and metadata.get("content") == CONTENT
        and metadata.get("query_field") == "Anywhere"
        and metadata.get("date_start") == DATE_START
        and metadata.get("date_end") == DATE_END
        and metadata.get("date_filter_mode") == "source_month_plus_client_exact_day"
        and metadata.get("language_filter") is None
        and metadata.get("publication_type_filter") is None
        and metadata.get("open_access_filter") is False
        and metadata.get("subject_facet_ids") == []
        and metadata.get("sort_parameter") == SORT
        and metadata.get("passes_completed") == PASSES
        and metadata.get("source_entries_retrieved") == total
        and metadata.get("stopped_reason") in {"all_available_records", "zero_results"}
        and metadata.get("export_method")
        == "visible_page_scoped_normal_ui_ris_with_abstracts"
        and metadata.get("native_export_commit_state") == "marker_required"
    )
    pass_valid = bool(
        isinstance(total, int)
        and total >= 0
        and len(ordered_ids) == total
        and len(ordered_ids) == len(set(ordered_ids))
        and metadata.get("ordered_source_ids_sha256") == ordered_hash
        and len(pass_reports) == PASSES
        and all(
            isinstance(report, Mapping)
            and report.get("pass_number") == number
            and report.get("ordered_ids_sha256") == ordered_hash
            and sum(
                page.get("rendered_cards", 0)
                for page in report.get("pages", [])
                if isinstance(page, Mapping)
            )
            == total
            for number, report in enumerate(pass_reports, start=1)
        )
    )
    native_ris_valid = bool(
        metadata.get("native_capture", {}).get("preserved_native_files") is True
        and (total == 0 or len(native_diagnostics) > 0)
        and all(
            isinstance(item, Mapping)
            and item.get("completed_state") == "completed"
            and item.get("selected_doi_count") == item.get("exported_doi_count")
            and item.get("selected_doi_count") == item.get("ty_count")
            and item.get("selected_doi_count") == item.get("er_count")
            and isinstance(item.get("byte_count"), int)
            and item["byte_count"] > 0
            and isinstance(item.get("sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
            for item in native_diagnostics
        )
        and native_ris_directory_valid(native_dir, metadata)
    )
    prisma_valid = bool(
        prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == plan.get("repository_head_at_predeclaration")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("partition_id") == event.get("partition_id")
        and adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    screenshot_contract_valid = bool(
        isinstance(screenshots, Mapping)
        and screenshots.get("schema_version") == WILEY_SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
        and screenshots_valid
    )
    terminal_marker_valid = marker_valid(path)
    return {
        "valid": bool(
            controls_valid
            and pass_valid
            and native_ris_valid
            and records_valid
            and prisma_valid
            and screenshot_contract_valid
            and terminal_marker_valid
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "source_total": total,
        "retained_record_count": record_summary["retained_record_count"],
        "client_date_excluded_count": excluded_count,
        "unresolved_exact_date_count": metadata.get("unresolved_exact_dates_retained"),
        "ordered_source_id_count": len(ordered_ids),
        "ordered_source_ids_sha256": ordered_hash,
        "pages_per_pass": metadata.get("pages_per_pass"),
        "pass_valid": pass_valid,
        "controls_valid": controls_valid,
        "native_ris_valid": native_ris_valid,
        "native_ris_download_count": len(native_diagnostics),
        "native_ris_download_bytes": sum(
            item.get("byte_count", 0)
            for item in native_diagnostics
            if isinstance(item, Mapping) and isinstance(item.get("byte_count"), int)
        ),
        "full_abstract_count": record_summary["full_abstract_count"],
        "source_omitted_abstract_count": record_summary["source_omitted_abstract_count"],
        "abstract_field_complete": record_summary["all_retained_rows_have_abstract_field"],
        "publication_type_counts": record_summary["publication_type_counts"],
        "missing_publication_type_count": record_summary["missing_publication_type_count"],
        "publication_type_field_complete": record_summary[
            "all_retained_rows_have_publication_type"
        ],
        "prisma_valid": prisma_valid,
        "screenshots_valid": screenshot_contract_valid,
        "terminal_marker_valid": terminal_marker_valid,
        "screenshots": image_rows,
        "adapter_snapshot_attempts_started": (
            metadata.get("snapshot_attempt_recovery", {}).get("attempts_started", 1)
            if isinstance(metadata.get("snapshot_attempt_recovery"), Mapping)
            else 1
        ),
    }


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urlopen(request, timeout=120) as response:
        return json.load(response)


def create_authorized_wiley_target(cdp_url: str, timeout_seconds: float = 60.0) -> str:
    """Create the caller-owned Wiley authorization page for one source cell."""
    created = cdp_json(cdp_url, f"/json/new?{quote(WILEY_ADVANCED_URL, safe='')}", method="PUT")
    target_id = created.get("id") if isinstance(created, Mapping) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not return an explicit Wiley target")
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
                and parsed.hostname == "onlinelibrary.wiley.com"
            ):
                return target_id
        time.sleep(0.5)
    raise RuntimeError("The Wiley authorization target did not become ready")


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
    native_dir: Path,
    cdp_url: str,
    target_id: str,
    plan: Mapping[str, Any],
) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
        "--field1",
        FIELD,
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--content",
        CONTENT,
        "--sort",
        SORT,
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--max-source-total",
        str(event["max_source_total"]),
        "--max-snapshot-attempts",
        str(event["max_snapshot_attempts"]),
        "--passes",
        str(event["passes"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--require-complete",
        "--native-export-dir",
        str(native_dir),
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
        str(plan["repository_head_at_predeclaration"]),
        "--prisma-phase",
        str(plan["phase"]),
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        str(event["partition_id"]),
        "--prisma-partition-label",
        str(event["partition_id"]),
        "--prisma-partition-description",
        (
            "Wiley final direct discovery partition "
            f"{event['partition_id']} source cell {event['cell_id']}"
        ),
    ]


def output_paths_occupied(output: Path, native_dir: Path) -> bool:
    return any(
        path.exists() or path.is_symlink()
        for path in (output, marker_path(output), *screenshot_paths(output), native_dir)
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
        raise ValueError("Invalid final Wiley plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("Final Wiley output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Final Wiley execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        native_dir = output_dir / str(event["native_ris_directory"])
        if output_paths_occupied(output, native_dir):
            raise FileExistsError(
                f"Refusing to overwrite {event['partition_id']} {event['cell_id']} artifacts"
            )
        target_id: str | None = None
        target_closed = False
        exit_code: int | None = None
        summary: dict[str, Any]
        try:
            target_id = create_authorized_wiley_target(cdp_url)
            completed = subprocess.run(
                final_command(event, output, native_dir, cdp_url, target_id, plan),
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            exit_code = completed.returncode
            summary = artifact_summary(output, event, plan, native_dir)
        except Exception as error:
            summary = {
                "valid": False,
                "artifact_written": output.is_file() and not output.is_symlink(),
                "runner_failure": type(error).__name__,
            }
        finally:
            if target_id is not None:
                target_closed = close_target(cdp_url, target_id)
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
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
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "cell": event["cell_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": outcome.get("source_total"),
                    "retained_records": outcome.get("retained_record_count"),
                    "abstracts": outcome.get("full_abstract_count"),
                    "missing_types": outcome.get("missing_publication_type_count"),
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
        "plan": plan_path.name,
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "target_identifier_retained": False,
        "execution_policy": plan["execution_policy"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "source_command_attempt_count": sum(
            outcome.get("source_command_attempt_count", 0) for outcome in outcomes
        ),
        "adapter_snapshot_attempt_count": sum(
            outcome.get("adapter_snapshot_attempts_started", 0) for outcome in outcomes
        ),
        "accepted_source_cell_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "all_source_cells_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def build_union_manifest(
    plan_path: Path, plan: Mapping[str, Any], output_dir: Path
) -> dict[str, Any]:
    cells_by_parent: dict[str, list[dict[str, Any]]] = {}
    events_by_parent: dict[str, Mapping[str, Any]] = {}
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        artifact = load(output)
        metadata = artifact.get("output_metadata")
        metadata = metadata if isinstance(metadata, Mapping) else {}
        prisma = metadata.get("prisma_search_run")
        prisma = prisma if isinstance(prisma, Mapping) else {}
        if not (
            artifact.get("requested_query") == event.get("query")
            and prisma.get("run_id") == event.get("event_id")
            and prisma.get("report_ready") is True
        ):
            raise ValueError(f"Cannot bind incomplete Wiley event {event['event_id']}")
        cell = {
            "cell_id": event["cell_id"],
            "source_id": SOURCE_ID,
            "partition_id": event["partition_id"],
            "parent_event_id": event["parent_event_id"],
            "source_run_id": event["event_id"],
            "query": event["query"],
            "requested_query": event["query"],
            "artifact_sha256": digest(output),
            "artifact_byte_count": output.stat().st_size,
            "status": "final_complete",
            "report_ready": True,
        }
        cells_by_parent.setdefault(str(event["parent_event_id"]), []).append(cell)
        events_by_parent[str(event["parent_event_id"])] = event
    rows: list[dict[str, Any]] = []
    for partition in PARTITIONS:
        parent = parent_event_id(partition)
        event = events_by_parent.get(parent)
        cells = sorted(cells_by_parent.get(parent, []), key=lambda item: item["cell_id"])
        if event is None or not cells:
            raise ValueError(f"Missing Wiley cells for {partition}")
        rows.append(
            {
                "event_id": parent,
                "event_kind": "final",
                "review_namespace": REVIEW_NAMESPACE,
                "source_id": SOURCE_ID,
                "partition_id": partition,
                "status": "final_complete",
                "query_cells": cells,
            }
        )
    return {
        "schema_version": UNION_MANIFEST_SCHEMA,
        "created_at_utc": now(),
        "review_namespace": REVIEW_NAMESPACE,
        "review": {
            "review_id": plan["review_id"],
            "strategy_reference": plan["strategy_reference"],
            "strategy_version": plan["repository_head_at_predeclaration"],
            "phase": plan["phase"],
        },
        "source_union_expected_partitions": list(PARTITIONS),
        "source_union_expected_sources": [SOURCE_ID],
        "final_plan": {
            "artifact": plan_path.name,
            "sha256": digest(plan_path),
        },
        "events": rows,
    }


def create_source_union(
    plan_path: Path,
    output_dir: Path,
    manifest_path: Path,
    receipt_path: Path,
) -> int:
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {manifest_path}")
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    if validate_plan(plan):
        raise ValueError("Cannot create a source union from an invalid final plan")
    manifest = build_union_manifest(plan_path, plan, output_dir)
    write_new(manifest_path, manifest)
    inputs = [output_dir / str(event["output_filename"]) for event in plan["events"]]
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *(str(path) for path in inputs),
        "--output-path",
        str(receipt_path),
        "--review-namespace",
        REVIEW_NAMESPACE,
        "--campaign-manifest",
        str(manifest_path),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("Wiley source-union receipt creation failed")
    return 0


def assess(
    plan_path: Path,
    run_receipt_path: Path,
    output_dir: Path,
    union_manifest_path: Path,
    source_union_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(plan_path)
    run = load(run_receipt_path)
    union_manifest = load(union_manifest_path)
    source_union = load(source_union_path)
    errors = validate_plan(plan)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_source_cell_count") != len(plan["events"])
    ):
        errors.append("run_receipt")
    if (
        union_manifest.get("schema_version") != UNION_MANIFEST_SCHEMA
        or union_manifest.get("final_plan", {}).get("sha256") != digest(plan_path)
    ):
        errors.append("union_manifest")
    if source_union.get("schema_version") != "academic-search-source-union-receipt/v1":
        errors.append("source_union_schema")

    outcomes = {
        outcome.get("event_id"): outcome
        for outcome in run.get("outcomes", [])
        if isinstance(outcome, Mapping)
    }
    event_evidence: list[dict[str, Any]] = []
    all_retained_ids: set[str] = set()
    raw_retained_rows = 0
    source_total_rows = 0
    client_excluded_rows = 0
    unresolved_rows = 0
    full_abstract_rows = 0
    source_omitted_abstract_rows = 0
    publication_types: dict[str, int] = {}
    screenshot_receipts: list[dict[str, Any]] = []
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        native_dir = output_dir / str(event["native_ris_directory"])
        outcome = outcomes.get(event["event_id"])
        if outcome is None:
            errors.append(f"missing_outcome:{event['event_id']}")
            continue
        summary = artifact_summary(output, event, plan, native_dir)
        artifact = load(output) if output.is_file() and not output.is_symlink() else {}
        metadata = artifact.get("output_metadata")
        metadata = metadata if isinstance(metadata, Mapping) else {}
        rows = artifact.get("results")
        rows = rows if isinstance(rows, list) else []
        if (
            outcome.get("success") is not True
            or summary.get("valid") is not True
            or outcome.get("artifact_sha256") != summary.get("artifact_sha256")
            or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
        ):
            errors.append(f"event:{event['event_id']}")
        source_total = summary.get("source_total")
        retained_count = summary.get("retained_record_count")
        excluded_count = summary.get("client_date_excluded_count")
        if not all(isinstance(value, int) and value >= 0 for value in (source_total, retained_count, excluded_count)):
            errors.append(f"count_shape:{event['event_id']}")
        elif source_total != retained_count + excluded_count:
            errors.append(f"date_accounting:{event['event_id']}")
        source_total_rows += source_total if isinstance(source_total, int) else 0
        raw_retained_rows += retained_count if isinstance(retained_count, int) else 0
        client_excluded_rows += excluded_count if isinstance(excluded_count, int) else 0
        unresolved = summary.get("unresolved_exact_date_count")
        unresolved_rows += unresolved if isinstance(unresolved, int) else 0
        full_abstract_rows += summary.get("full_abstract_count", 0)
        source_omitted_abstract_rows += summary.get("source_omitted_abstract_count", 0)
        for publication_type, count in summary.get("publication_type_counts", {}).items():
            if isinstance(publication_type, str) and isinstance(count, int):
                publication_types[publication_type] = publication_types.get(publication_type, 0) + count
        for row in rows:
            if isinstance(row, Mapping) and isinstance(row.get("paperId"), str):
                all_retained_ids.add(row["paperId"])
        screenshot_receipts.extend(summary.get("screenshots", []))
        event_evidence.append(
            {
                "event_id": event["event_id"],
                "parent_event_id": event["parent_event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": output.name,
                "artifact_sha256": summary.get("artifact_sha256"),
                "source_total": source_total,
                "retained_record_count": retained_count,
                "client_date_excluded_count": excluded_count,
                "unresolved_exact_date_count": unresolved,
                "ordered_source_ids_sha256": summary.get("ordered_source_ids_sha256"),
                "pages_per_pass": summary.get("pages_per_pass"),
                "native_ris_download_count": summary.get("native_ris_download_count"),
                "native_ris_download_bytes": summary.get("native_ris_download_bytes"),
                "full_abstract_count": summary.get("full_abstract_count"),
                "source_omitted_abstract_count": summary.get("source_omitted_abstract_count"),
                "publication_type_counts": summary.get("publication_type_counts"),
                "all_retained_rows_have_abstract_field": summary.get("abstract_field_complete"),
                "all_retained_rows_have_publication_type": summary.get(
                    "publication_type_field_complete"
                ),
                "screenshots": summary.get("screenshots"),
            }
        )

    source_section = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    source_union_valid = bool(
        source_union.get("review_namespace") == REVIEW_NAMESPACE
        and source_union.get("review_id") == plan.get("review_id")
        and source_union.get("strategy_reference") == plan.get("strategy_reference")
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and source_section.get("raw_record_count") == raw_retained_rows
        and source_section.get("event_total_sum") == raw_retained_rows
        and set(source_section.get("stable_record_ids", [])) == all_retained_ids
    )
    if not source_union_valid:
        errors.append("source_union")
    capture_complete = bool(
        len(event_evidence) == len(plan["events"])
        and all(
            event.get("all_retained_rows_have_abstract_field") is True
            and event.get("all_retained_rows_have_publication_type") is True
            for event in event_evidence
        )
        and sum(publication_types.values()) == raw_retained_rows
    )
    if not capture_complete:
        errors.append("capture_contract")
    if len(screenshot_receipts) != 2 * len(plan["events"]):
        errors.append("screenshots")
    complete = bool(not errors and capture_complete and source_union_valid)
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final",
        "plan": plan_path.name,
        "plan_sha256": digest(plan_path),
        "run_receipt": run_receipt_path.name,
        "run_receipt_sha256": digest(run_receipt_path),
        "source_union_manifest": union_manifest_path.name,
        "source_union_manifest_sha256": digest(union_manifest_path),
        "source_union": source_union_path.name,
        "source_union_sha256": digest(source_union_path),
        "adapter": plan.get("adapter"),
        "accepted_source_cell_count": len(event_evidence),
        "events": event_evidence,
        "cutoff_accounting": {
            "common_evidence_cutoff": DATE_END,
            "source_record_count_before_client_exact_day_filter": source_total_rows,
            "retained_record_count": raw_retained_rows,
            "excluded_after_exact_cutoff_count": client_excluded_rows,
            "unresolved_exact_date_count": unresolved_rows,
            "complete": source_total_rows == raw_retained_rows + client_excluded_rows,
        },
        "abstract_and_publication_type_capture": {
            "source_export": "visible page-scoped native RIS export with abstracts",
            "abstract_field": "abstract",
            "abstract_source_tags": ["N2", "AB"],
            "publication_type_field": "documentType",
            "publication_type_source_tag": "TY",
            "retained_rows": raw_retained_rows,
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
                "An empty abstract is retained only as Wiley's native RIS omission. "
                "No result-card description substitutes for a full abstract."
            ),
            "complete": capture_complete,
        },
        "stable_id_union": {
            "source_event_retained_record_count": raw_retained_rows,
            "unique_stable_id_count": len(all_retained_ids),
            "cross_partition_duplicate_occurrences": raw_retained_rows - len(all_retained_ids),
            "stable_id_set_sha256": digest_set(all_retained_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "screenshots": {
            "expected_png_count": 2 * len(plan["events"]),
            "validated_png_count": sum(
                item.get("valid") is True for item in screenshot_receipts
            ),
            "receipts": screenshot_receipts,
        },
        "source_union_valid": source_union_valid,
        "final_search_partitions_complete": complete,
        "status": "passed" if complete else "failed",
        "errors": errors,
    }
    write_new(output_path, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "source_records": source_total_rows,
                "retained_records": raw_retained_rows,
                "unique_records": len(all_retained_ids),
                "full_abstracts": full_abstract_rows,
                "publication_types": publication_types,
            }
        )
    )
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)
    check_parser = commands.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=2.0)
    union_parser = commands.add_parser("source-union")
    union_parser.add_argument("--plan", type=Path, required=True)
    union_parser.add_argument("--output-dir", type=Path, required=True)
    union_parser.add_argument("--manifest", type=Path, required=True)
    union_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--run-receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union-manifest", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "plan":
        plan = build_plan()
        errors = validate_plan(plan)
        if errors:
            raise ValueError("Invalid generated final Wiley plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"status": "saved", "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=True)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        return run_final(
            args.plan.resolve(strict=True),
            args.output_dir.resolve(strict=False),
            args.receipt.resolve(strict=False),
            settle_seconds=args.settle_seconds,
        )
    if args.command == "source-union":
        return create_source_union(
            args.plan.resolve(strict=True),
            args.output_dir.resolve(strict=True),
            args.manifest.resolve(strict=False),
            args.receipt.resolve(strict=False),
        )
    return assess(
        args.plan.resolve(strict=True),
        args.run_receipt.resolve(strict=True),
        args.output_dir.resolve(strict=True),
        args.source_union_manifest.resolve(strict=True),
        args.source_union.resolve(strict=True),
        args.output.resolve(strict=False),
    )


if __name__ == "__main__":
    raise SystemExit(main())
