#!/usr/bin/env python3
"""Plan, run, reconcile, and assess final Web of Science direct searches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from queries import (
    CONCEPT_SCHEDULE_COMMIT,
    EXPECTED_QUERY_SNAPSHOT_SHA256,
    PARTITIONS,
    QUERY_CHARACTER_COUNTS,
    QUERY_SHA256,
    QUERY_SNAPSHOT,
    TERM_COUNTS,
    WILDCARD_REPLACEMENTS,
    WILDCARD_SCHEDULE,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_web_of_science.py"
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/web-of-science-core-collection/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
WOS_ADVANCED_URL = "https://www.webofscience.com/wos/woscc/advanced-search"

SOURCE = "Web of Science Core Collection"
SOURCE_ID = "web_of_science_core_collection"
REVIEW_NAMESPACE = "main"
REVIEW_ID = "slr1-1.1-restart"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-wos-main-direct-v1"

PLAN_SCHEMA = "slr1-wos-final-direct-plan/v1"
RUN_SCHEMA = "slr1-wos-final-direct-run/v1"
RECORD_UNION_SCHEMA = "slr1-wos-final-direct-record-union/v1"
ASSESSMENT_SCHEMA = "slr1-wos-final-direct-assessment/v1"
SOURCE_UNION_SCHEMA = "academic-search-source-union-receipt/v1"
MARKER_SCHEMA = "academic_search_output_commit_marker_v1"
MARKER_TAG = "ACADEMIC_SEARCH_COMMIT"
SCREENSHOT_SCHEMA = "web-of-science-automatic-screenshots/v1"
NATIVE_RIS_RECORD_CONTENT = "Author, Title, Source, Abstract"

CUTOFF_DATE = "2026-08-24"
YEAR_START = 2011
YEAR_END = 2026
PAGE_SIZE = 50
LIMIT = 1999
MAX_PAGES = 40
TIMEOUT_SECONDS = 300
PAGE_DELAY_SECONDS = 0.25
RIS_TAG = re.compile(r"^([A-Z0-9]{2})\s{0,2}-\s?(.*)$")
WOS_ID = re.compile(r"^WOS:[A-Za-z0-9]+$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
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
    """Create a JSON artifact without replacing an earlier artifact."""
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
        raise RuntimeError("Cannot determine the Web of Science adapter version")
    return match.group(1)


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        SCRIPT_PATH.with_name("queries.py"),
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {relative(path): digest(path) for path in paths}


def plan_event(partition: str, query: str, strategy_version: str) -> dict[str, Any]:
    return {
        "event_id": f"final-main-{partition}-web-of-science-core-collection-001",
        "partition_id": partition,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output_filename": f"{partition}.json",
        "native_ris_filename": f"{partition}.ris",
        "page_size": PAGE_SIZE,
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": TIMEOUT_SECONDS,
        "page_delay_seconds": PAGE_DELAY_SECONDS,
        "require_complete": True,
        "strict_passes": 2,
        "full_abstracts": True,
        "source_publication_types": True,
        "strategy_version": strategy_version,
    }


def build_plan() -> dict[str, Any]:
    strategy_version = repository_head()
    events = [
        plan_event(partition, WILDCARD_SCHEDULE[partition], strategy_version)
        for partition in PARTITIONS
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
        "concept_schedule_commit": CONCEPT_SCHEDULE_COMMIT,
        "source_union_expected_partitions": list(PARTITIONS),
        "source_union_expected_sources": [SOURCE_ID],
        "cutoff": {
            "exact_common_cutoff": CUTOFF_DATE,
            "source_year_start": YEAR_START,
            "source_year_upper_bound": YEAR_END,
            "source_precision": "year",
            "native_query_clauses": ["PY=(2011-2026)", "LA=(English)"],
            "screening_requirement": (
                "Screen every 2026 record against the exact common cutoff. "
                "The Web of Science discovery query applies an inclusive year bound."
            ),
        },
        "source_configuration": {
            "database": SOURCE,
            "editions": "All currently exposed editions",
            "advanced_search_url": WOS_ADVANCED_URL,
            "field": "TS Topic",
            "query_mode": "raw",
            "sort": "Date: oldest first",
            "page_size": PAGE_SIZE,
            "language": "English through the raw LA=(English) clause",
            "document_type_controls": [],
            "subject_controls": [],
            "access_controls": [],
            "peer_review_filter": None,
            "full_text_filter": None,
            "controlled_vocabulary": None,
            "native_ris": "RIS (other reference software)",
            "native_ris_record_content": NATIVE_RIS_RECORD_CONTENT,
        },
        "capture_contract": {
            "full_abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "source_method": "native RIS selected as Author, Title, Source, Abstract",
                "source_tags": ["AB", "N2"],
                "require_nonempty_for_every_retained_record": True,
                "normalized_source": "native_web_of_science_abstract_inclusive_ris",
                "snippet_is_not_a_substitute": True,
            },
            "publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "source_tag": "TY",
                "require_nonempty_for_every_retained_record": True,
                "filter_applied": None,
                "reviewer_publication_type_coding": "deferred to screening",
            },
            "native_ris_sidecar_for_positive_event": True,
            "automatic_screenshots": True,
        },
        "translation": {
            "population_wildcards": True,
            "wildcard_count": 10,
            "replaced_population_literals": 22,
            "literal_small_satellite_atoms": 4,
            "proximity_operators": False,
            "pair_expansion": False,
            "local_pair_filter": False,
            "controlled_vocabulary_supplement": None,
            "term_counts": TERM_COUNTS,
            "query_character_counts": QUERY_CHARACTER_COUNTS,
            "query_sha256": QUERY_SHA256,
            "accepted_pilot_snapshot": relative(QUERY_SNAPSHOT),
            "accepted_pilot_snapshot_sha256": EXPECTED_QUERY_SNAPSHOT_SHA256,
            "accepted_wildcard_replacements": [
                {
                    "candidate": item["candidate"],
                    "replaced_literals": list(item["replaced_literals"]),
                }
                for item in WILDCARD_REPLACEMENTS
            ],
        },
        "strict_contract": {
            "strict_mode": "--require-complete",
            "membership_gate": "equal complete ordered WOS-ID sequences",
            "required_equal_controls": [
                "source total",
                "page count",
                "Web of Science Core Collection scope",
                "all current editions",
                "Date: oldest first",
                "native RIS reconciliation",
                NATIVE_RIS_RECORD_CONTENT + " export readback",
            ],
            "automatic_screenshots_required": True,
            "full_abstracts_required": True,
            "source_publication_types_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "fresh_authorized_target_per_partition": True,
            "close_ephemeral_target_after_partition": True,
            "target_identifiers_retained": False,
            "retry_policy": "none_after_final_plan_execution_begins",
            "skip_full_abstracts": False,
            "publication_type_filter": None,
        },
        "adapter": {
            "id": "search_web_of_science",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
            "normalized_record_fields": {
                "abstract": "full native RIS AB or N2 content",
                "documentType": "native RIS TY publication type",
            },
        },
        "bindings": {"files": bindings()},
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("concept_schedule_commit") != CONCEPT_SCHEDULE_COMMIT
    ):
        errors.append("identity")
    if (
        plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("source_union_expected_sources") != [SOURCE_ID]
    ):
        errors.append("source_union_schedule")
    cutoff = plan.get("cutoff", {})
    if (
        cutoff.get("exact_common_cutoff") != CUTOFF_DATE
        or cutoff.get("source_year_start") != YEAR_START
        or cutoff.get("source_year_upper_bound") != YEAR_END
        or cutoff.get("source_precision") != "year"
        or cutoff.get("native_query_clauses") != ["PY=(2011-2026)", "LA=(English)"]
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("database") != SOURCE
        or configuration.get("editions") != "All currently exposed editions"
        or configuration.get("advanced_search_url") != WOS_ADVANCED_URL
        or configuration.get("field") != "TS Topic"
        or configuration.get("query_mode") != "raw"
        or configuration.get("sort") != "Date: oldest first"
        or configuration.get("page_size") != PAGE_SIZE
        or configuration.get("language") != "English through the raw LA=(English) clause"
        or configuration.get("document_type_controls") != []
        or configuration.get("subject_controls") != []
        or configuration.get("access_controls") != []
        or configuration.get("peer_review_filter") is not None
        or configuration.get("full_text_filter") is not None
        or configuration.get("controlled_vocabulary") is not None
        or configuration.get("native_ris_record_content") != NATIVE_RIS_RECORD_CONTENT
    ):
        errors.append("source_configuration")
    capture = plan.get("capture_contract", {})
    if (
        capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("normalized_field") != "abstract"
        or capture.get("full_abstracts", {}).get("source_tags") != ["AB", "N2"]
        or capture.get("full_abstracts", {}).get("require_nonempty_for_every_retained_record")
        is not True
        or capture.get("full_abstracts", {}).get("normalized_source")
        != "native_web_of_science_abstract_inclusive_ris"
        or capture.get("publication_types", {}).get("required") is not True
        or capture.get("publication_types", {}).get("normalized_field") != "documentType"
        or capture.get("publication_types", {}).get("source_tag") != "TY"
        or capture.get("publication_types", {}).get("require_nonempty_for_every_retained_record")
        is not True
        or capture.get("publication_types", {}).get("filter_applied") is not None
        or capture.get("native_ris_sidecar_for_positive_event") is not True
        or capture.get("automatic_screenshots") is not True
    ):
        errors.append("capture_contract")
    translation = plan.get("translation", {})
    if (
        translation.get("population_wildcards") is not True
        or translation.get("wildcard_count") != 10
        or translation.get("replaced_population_literals") != 22
        or translation.get("literal_small_satellite_atoms") != 4
        or translation.get("proximity_operators") is not False
        or translation.get("pair_expansion") is not False
        or translation.get("local_pair_filter") is not False
        or translation.get("controlled_vocabulary_supplement") is not None
        or translation.get("term_counts") != TERM_COUNTS
        or translation.get("query_character_counts") != QUERY_CHARACTER_COUNTS
        or translation.get("query_sha256") != QUERY_SHA256
        or translation.get("accepted_pilot_snapshot") != relative(QUERY_SNAPSHOT)
        or translation.get("accepted_pilot_snapshot_sha256")
        != EXPECTED_QUERY_SNAPSHOT_SHA256
    ):
        errors.append("translation")
    execution = plan.get("execution_policy", {})
    if (
        execution.get("one_source_execution_per_partition") is not True
        or execution.get("continue_after_partition_failure") is not True
        or execution.get("fresh_authorized_target_per_partition") is not True
        or execution.get("close_ephemeral_target_after_partition") is not True
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
    if not isinstance(strategy_version, str) or not re.fullmatch(r"[0-9a-f]{40}", strategy_version):
        errors.append("strategy_version")
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
            event.get("event_id")
            != f"final-main-{partition}-web-of-science-core-collection-001"
            or query != WILDCARD_SCHEDULE.get(partition)
            or event.get("query_sha256") != digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("output_filename") != f"{partition}.json"
            or event.get("native_ris_filename") != f"{partition}.ris"
            or event.get("page_size") != PAGE_SIZE
            or event.get("limit") != LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("timeout_seconds") != TIMEOUT_SECONDS
            or event.get("page_delay_seconds") != PAGE_DELAY_SECONDS
            or event.get("require_complete") is not True
            or event.get("strict_passes") != 2
            or event.get("full_abstracts") is not True
            or event.get("source_publication_types") is not True
            or event.get("strategy_version") != strategy_version
        ):
            errors.append(f"event_contract:{partition}")
        if (
            query.count("*") != 10
            or "?" in query
            or "$" in query
            or not query.endswith(" AND PY=(2011-2026) AND LA=(English)")
            or any(marker in query.upper() for marker in ("NEAR", " SAME ", "DT=("))
        ):
            errors.append(f"query_translation:{partition}")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        if (
            adapter.get("id") != "search_web_of_science"
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


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{MARKER_TAG}.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


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
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def screenshot_evidence(path: Path, screenshots: Any) -> tuple[bool, list[dict[str, Any]]]:
    receipt = screenshots if isinstance(screenshots, Mapping) else {}
    valid = bool(
        receipt.get("schema_version") == SCREENSHOT_SCHEMA
        and receipt.get("automatic") is True
        and receipt.get("no_opt_out") is True
        and receipt.get("same_directory_as_json") is True
        and receipt.get("complete") is True
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


def parse_ris(path: Path) -> list[dict[str, list[str]]]:
    """Parse the retained native RIS file enough to verify AB/N2 and TY."""
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    current_tag: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        match = RIS_TAG.match(raw_line)
        if match is not None:
            tag, value = match.groups()
            value = value.strip()
            if tag == "TY":
                if current is not None:
                    raise ValueError("RIS started a record before ER")
                current = {tag: [value]}
                current_tag = tag
            elif tag == "ER":
                if current is None:
                    raise ValueError("RIS contained ER without TY")
                records.append(current)
                current = None
                current_tag = None
            elif current is None:
                raise ValueError("RIS contained a field outside a record")
            else:
                current.setdefault(tag, []).append(value)
                current_tag = tag
            continue
        if current is None or current_tag is None or not raw_line[:1].isspace():
            raise ValueError("RIS contained an unrecognized line")
        continuation = raw_line.strip()
        if continuation:
            current[current_tag][-1] = f"{current[current_tag][-1]} {continuation}".strip()
    if current is not None:
        raise ValueError("RIS ended before ER")
    return records


def ris_identifier(record: Mapping[str, list[str]]) -> str:
    identifiers = {
        value.strip()
        for tag in ("AN", "UT")
        for value in record.get(tag, [])
        if isinstance(value, str) and WOS_ID.fullmatch(value.strip())
    }
    if len(identifiers) != 1:
        raise ValueError("RIS record does not expose one WOS accession")
    return identifiers.pop()


def ris_record_summary(path: Path, expected_ids: list[str], total: int) -> tuple[bool, dict[str, Any] | None]:
    if total == 0:
        return not path.exists(), None
    if not path.is_file() or path.is_symlink():
        return False, None
    try:
        records = parse_ris(path)
        identifiers = [ris_identifier(record) for record in records]
    except (OSError, UnicodeError, ValueError):
        return False, None
    abstract_missing = sum(
        not any(value.strip() for tag in ("AB", "N2") for value in record.get(tag, []))
        for record in records
    )
    type_missing = sum(
        not any(value.strip() for value in record.get("TY", [])) for record in records
    )
    valid = bool(
        len(records) == total
        and identifiers == expected_ids
        and len(set(identifiers)) == total
        and abstract_missing == 0
        and type_missing == 0
    )
    return valid, {
        "path": path.name,
        "sha256": digest(path),
        "bytes": path.stat().st_size,
        "record_count": len(records),
        "ordered_wos_ids_sha256": digest_ordered(identifiers),
        "full_abstract_count": len(records) - abstract_missing,
        "missing_abstract_count": abstract_missing,
        "publication_type_count": len(records) - type_missing,
        "missing_publication_type_count": type_missing,
        "valid": valid,
    }


def record_capture_summary(rows: Any) -> tuple[bool, dict[str, Any]]:
    """Verify that each retained row preserves a full abstract and source type."""
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "missing_full_abstract_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
        }
    valid = True
    identifiers: set[str] = set()
    full_abstract_count = 0
    missing_abstract_count = 0
    type_counts: Counter[str] = Counter()
    missing_type_count = 0
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            valid = False
            continue
        identifier = row.get("paperId")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if (
            not isinstance(identifier, str)
            or WOS_ID.fullmatch(identifier) is None
            or identifier in identifiers
            or row.get("sourceRecordId") != identifier
            or row.get("sourceRecordKind") != SOURCE_ID
            or row.get("source") != SOURCE
            or row.get("rank") != position
        ):
            valid = False
        if isinstance(identifier, str):
            identifiers.add(identifier)
        if (
            isinstance(abstract, str)
            and bool(abstract.strip())
            and row.get("abstract_source")
            == "native_web_of_science_abstract_inclusive_ris"
            and row.get("abstract_not_available") is False
            and row.get("abstract_detail_verified") is True
        ):
            full_abstract_count += 1
        else:
            missing_abstract_count += 1
            valid = False
        if isinstance(document_type, str) and bool(document_type.strip()):
            type_counts[document_type] += 1
        else:
            missing_type_count += 1
            valid = False
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstract_count,
        "missing_full_abstract_count": missing_abstract_count,
        "publication_type_counts": dict(sorted(type_counts.items())),
        "missing_publication_type_count": missing_type_count,
        "all_retained_rows_have_full_abstract": missing_abstract_count == 0,
        "all_retained_rows_have_publication_type": missing_type_count == 0,
    }


def controls_valid(
    value: Mapping[str, Any], event: Mapping[str, Any], plan: Mapping[str, Any]
) -> bool:
    metadata = value.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    strategy = prisma.get("strategy", {}) if isinstance(prisma, Mapping) else {}
    scope = strategy.get("search_scope", {}) if isinstance(strategy, Mapping) else {}
    controls = scope.get("controls", {}) if isinstance(scope, Mapping) else {}
    database = controls.get("database", {}) if isinstance(controls, Mapping) else {}
    editions = controls.get("editions", {}) if isinstance(controls, Mapping) else {}
    limits = strategy.get("limits", {}) if isinstance(strategy, Mapping) else {}
    sort = strategy.get("sort", {}) if isinstance(strategy, Mapping) else {}
    total = value.get("total")
    positive_sort = bool(
        sort.get("state") == "applied" and sort.get("value") == "Date: oldest first"
    )
    zero_sort = bool(
        total == 0
        and sort.get("state") == "unknown"
        and sort.get("requested") == "Date: oldest first"
    )
    return bool(
        prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("coverage", {}).get("coverage_scope") == "partition"
        and prisma.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and value.get("executed_query") == event.get("query")
        and strategy.get("executed_query") == event.get("query")
        and strategy.get("executed_query_provenance") == "source_observed"
        and strategy.get("query_fields") == ["TS", "PY", "LA"]
        and scope.get("database") == SOURCE
        and scope.get("editions_requested") == ["All"]
        and database.get("state") == "applied"
        and database.get("effective") == SOURCE
        and editions.get("state") == "applied"
        and editions.get("requested") == ["All"]
        and isinstance(editions.get("effective"), list)
        and bool(editions.get("effective"))
        and limits.get("language", {}).get("state") == "not_applied"
        and limits.get("publication_year", {}).get("state") == "not_applied"
        and limits.get("document_type", {}).get("state") == "not_applied"
        and limits.get("document_types", {}).get("state") == "not_applied"
        and (positive_sort or zero_sort)
    )


def native_ris_valid(
    path: Path, value: Mapping[str, Any], event: Mapping[str, Any]
) -> tuple[bool, dict[str, Any] | None]:
    metadata = value.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    native = prisma.get("native_artifact") if isinstance(prisma, Mapping) else None
    total = value.get("total")
    ris_path = path.with_name(str(event["native_ris_filename"]))
    if total == 0:
        return native is None and not ris_path.exists(), None
    records = value.get("results")
    identifiers = [
        row.get("paperId")
        for row in records
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(records, list) else []
    ris_content_valid, ris_summary = ris_record_summary(
        ris_path, identifiers, total if isinstance(total, int) else -1
    )
    expected_pages = math.ceil(total / PAGE_SIZE) if isinstance(total, int) and total > 0 else None
    valid = bool(
        isinstance(total, int)
        and total > 0
        and isinstance(native, Mapping)
        and ris_content_valid
        and native.get("schema_version") == "academic-search-native-artifact/v1"
        and native.get("format") == "RIS"
        and native.get("digest_algorithm") == "sha256"
        and ris_summary is not None
        and native.get("sha256") == ris_summary.get("sha256")
        and native.get("byte_count") == ris_summary.get("bytes")
        and native.get("record_count") == total
        and native.get("record_count_provenance") == "framed_native_file_parse"
        and native.get("pages_exported") == expected_pages
        and native.get("local_path_persisted") is False
    )
    if ris_summary is not None:
        ris_summary["valid"] = valid
    return valid, ris_summary


def artifact_summary(
    path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]
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
    metadata = value.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    staged = prisma.get("staged_counts", {}) if isinstance(prisma, Mapping) else {}
    adapter = prisma.get("adapter", {}) if isinstance(prisma, Mapping) else {}
    rows = value.get("results")
    identifiers = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(rows, list) else []
    total = value.get("total")
    capture_valid, capture = record_capture_summary(rows)
    native_valid, native_summary = native_ris_valid(path, value, event)
    screenshots_valid, images = screenshot_evidence(
        path, metadata.get("screenshots", {}) if isinstance(metadata, Mapping) else {}
    )
    controls_ok = controls_valid(value, event, plan)
    completion_ok = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and isinstance(total, int)
        and total >= 0
        and isinstance(rows, list)
        and total == len(rows) == len(identifiers) == len(set(identifiers))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and prisma.get("report_readiness_reasons") == []
        and staged.get("source_reported_total") == total
        and staged.get("source_reported_total_exact") is True
        and staged.get("raw_source_records") == total
        and staged.get("records_exported") == total
    )
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    marker_ok = marker_valid(path)
    return {
        "valid": bool(
            controls_ok
            and completion_ok
            and adapter_ok
            and native_valid
            and screenshots_valid
            and marker_ok
            and capture_valid
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status") if isinstance(metadata, Mapping) else None,
        "error_stage": metadata.get("error_stage") if isinstance(metadata, Mapping) else None,
        "error_reason": metadata.get("error_reason") if isinstance(metadata, Mapping) else None,
        "total": total,
        "stable_id_count": len(set(identifiers)),
        "ordered_wos_ids_sha256": digest_ordered(identifiers),
        "controls_valid": controls_ok,
        "completion_valid": completion_ok,
        "adapter_binding_valid": adapter_ok,
        "native_ris_valid": native_valid,
        "native_ris": native_summary,
        "screenshots_valid": screenshots_valid,
        "terminal_marker_valid": marker_ok,
        "full_abstract_capture_valid": capture_valid,
        "full_abstract_count": capture["full_abstract_count"],
        "missing_full_abstract_count": capture["missing_full_abstract_count"],
        "publication_type_counts": capture["publication_type_counts"],
        "missing_publication_type_count": capture["missing_publication_type_count"],
        "publication_type_capture_valid": capture[
            "all_retained_rows_have_publication_type"
        ],
        "screenshots": images,
    }


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def create_ephemeral_wos_target(cdp_url: str, timeout_seconds: float = 45.0) -> str:
    encoded = urllib.parse.quote(WOS_ADVANCED_URL, safe="")
    created = cdp_json(cdp_url, f"/json/new?{encoded}", method="PUT")
    target_id = created.get("id") if isinstance(created, Mapping) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not return one explicit Web of Science target")
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
            parsed = urllib.parse.urlparse(str(target.get("url", "")))
            if (
                target.get("type") == "page"
                and parsed.scheme == "https"
                and parsed.hostname in {"webofscience.com", "www.webofscience.com"}
            ):
                return target_id
        time.sleep(0.5)
    raise RuntimeError("The fresh Web of Science target did not become ready")


def close_ephemeral_target(cdp_url: str, target_id: str) -> bool:
    try:
        with urllib.request.urlopen(
            f"{cdp_url.rstrip('/')}/json/close/{target_id}", timeout=10
        ) as response:
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
    ris_path = output.with_name(str(event["native_ris_filename"]))
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--raw-query",
        str(event["query"]),
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--require-complete",
        "--ris-output-path",
        str(ris_path),
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
        f"Web of Science Core Collection final direct discovery partition {event['partition_id']}",
    ]


def run_final(plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid final Web of Science plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("Final Web of Science output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Final Web of Science execution requires a loopback browser")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        ris_path = output_dir / str(event["native_ris_filename"])
        occupied = (output, ris_path, *screenshot_paths(output), marker_path(output))
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise FileExistsError(
                f"Refusing to overwrite final {event['partition_id']} artifacts"
            )
        target_id: str | None = None
        exit_code: int | None = None
        target_closed = False
        try:
            target_id = create_ephemeral_wos_target(cdp_url)
            time.sleep(3)
            completed = subprocess.run(
                final_command(event, output, cdp_url, target_id, plan),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            exit_code = completed.returncode
            summary = artifact_summary(output, event, plan)
        except Exception as error:
            summary = {
                "valid": False,
                "artifact_written": output.is_file(),
                "runner_failure": type(error).__name__,
            }
        finally:
            if target_id is not None:
                target_closed = close_ephemeral_target(cdp_url, target_id)
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() else None,
            "native_ris_artifact": ris_path.name if ris_path.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1 if target_id is not None else 0,
            "ephemeral_target_created": target_id is not None,
            "ephemeral_target_close_requested": target_closed,
            "target_identifier_retained": False,
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
                    "full_abstracts": outcome.get("full_abstract_count"),
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
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": sum(
            outcome.get("attempt_count", 0) for outcome in outcomes
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


def successful_event_artifacts(
    plan: Mapping[str, Any], run: Mapping[str, Any], output_dir: Path
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]]:
    if run.get("success") is not True:
        raise ValueError("The final Web of Science run did not complete")
    outcomes = run.get("outcomes")
    if not isinstance(outcomes, list):
        raise ValueError("The final Web of Science receipt has no outcomes")
    by_partition = {
        item.get("partition_id"): item
        for item in outcomes
        if isinstance(item, Mapping) and isinstance(item.get("partition_id"), str)
    }
    selected: list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]] = []
    for event in plan.get("events", []):
        if not isinstance(event, Mapping):
            raise ValueError("The final Web of Science plan has a malformed event")
        partition = event.get("partition_id")
        outcome = by_partition.get(partition)
        if (
            not isinstance(outcome, Mapping)
            or outcome.get("success") is not True
            or outcome.get("artifact") != event.get("output_filename")
        ):
            raise ValueError(f"The final Web of Science event is incomplete: {partition}")
        path = output_dir / str(event["output_filename"])
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing final Web of Science artifact: {path}")
        data = load(path)
        selected.append((event, outcome, path, data))
    if len(selected) != len(PARTITIONS):
        raise ValueError("The final Web of Science event coverage is incomplete")
    return selected


def run_source_union(
    plan_path: Path, receipt_path: Path, output_dir: Path, output: Path
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    selected = successful_event_artifacts(plan, run, output_dir)
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *(str(path) for _, _, path, _ in selected),
        "--output-path",
        str(output),
        "--expected-partitions",
        *PARTITIONS,
        "--expected-sources",
        SOURCE_ID,
        "--review-namespace",
        REVIEW_NAMESPACE,
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("Could not create the Web of Science source-union receipt")
    return 0


def build_record_union(
    plan_path: Path, receipt_path: Path, output_dir: Path, output: Path
) -> dict[str, Any]:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    selected = successful_event_artifacts(plan, run, output_dir)
    records: dict[str, dict[str, Any]] = {}
    artifacts: list[dict[str, Any]] = []
    for event, outcome, path, data in selected:
        summary = artifact_summary(path, event, plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Final Web of Science artifact failed validation: {path}")
        rows = data.get("results")
        if not isinstance(rows, list):
            raise ValueError(f"Final Web of Science artifact has no records: {path}")
        artifacts.append(
            {
                "partition_id": event["partition_id"],
                "artifact": relative(path),
                "artifact_sha256": outcome.get("artifact_sha256"),
                "record_count": data.get("total"),
                "native_ris": summary.get("native_ris"),
            }
        )
        for row in rows:
            if not isinstance(row, Mapping) or not isinstance(row.get("paperId"), str):
                raise ValueError(f"Malformed final Web of Science row in {path}")
            identifier = row["paperId"]
            current = records.setdefault(
                identifier,
                {
                    "paperId": identifier,
                    "sourceRecordId": row.get("sourceRecordId"),
                    "discovery_partitions": [],
                    "record": dict(row),
                },
            )
            if event["partition_id"] not in current["discovery_partitions"]:
                current["discovery_partitions"].append(event["partition_id"])
            prior_abstract = str(current["record"].get("abstract") or "")
            candidate_abstract = str(row.get("abstract") or "")
            if len(candidate_abstract) > len(prior_abstract):
                current["record"] = dict(row)
    rows: list[dict[str, Any]] = []
    for identifier in sorted(records):
        item = records[identifier]
        item["discovery_partitions"].sort(key=PARTITIONS.index)
        rows.append(item)
    capture_valid, capture = record_capture_summary([item["record"] for item in rows])
    if not capture_valid:
        raise ValueError("The Web of Science record union lacks a full abstract or type")
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "purpose": "deduplicated_final_direct_source_records_with_full_abstracts_and_source_publication_types",
        "reviewer_publication_type_coding": "not inferred from source metadata",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "input_artifacts": artifacts,
        "source_event_record_count": sum(
            int(item["record_count"]) for item in artifacts
        ),
        "unique_wos_id_count": len(rows),
        "stable_id_set_sha256": digest_set({item["paperId"] for item in rows}),
        "records_with_full_abstract": capture["full_abstract_count"],
        "records_without_full_abstract": capture["missing_full_abstract_count"],
        "source_publication_type_field": "documentType",
        "records_with_source_publication_type": sum(
            capture["publication_type_counts"].values()
        ),
        "records_missing_source_publication_type": capture[
            "missing_publication_type_count"
        ],
        "source_publication_type_counts": capture["publication_type_counts"],
        "complete": capture_valid,
        "records": rows,
    }
    write_new(output, value)
    return value


def source_union_valid(
    value: Mapping[str, Any],
    stable_ids: set[str],
    raw_event_count: int,
    plan: Mapping[str, Any],
) -> bool:
    union = value.get("source_unions", {}).get(SOURCE_ID, {})
    return bool(
        value.get("schema_version") == SOURCE_UNION_SCHEMA
        and value.get("review_namespace") == REVIEW_NAMESPACE
        and value.get("review_id") == plan.get("review_id")
        and value.get("strategy_reference") == plan.get("strategy_reference")
        and value.get("expected_partitions") == list(PARTITIONS)
        and value.get("expected_sources") == [SOURCE_ID]
        and value.get("completeness_status") == "complete"
        and value.get("failure_status") == "none"
        and union.get("expected_partitions") == list(PARTITIONS)
        and union.get("event_total_sum") == raw_event_count
        and set(union.get("stable_record_ids", [])) == stable_ids
        and union.get("raw_record_count") == raw_event_count
    )


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    source_union_path: Path,
    record_union_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    source_union = load(source_union_path)
    record_union = load(record_union_path)
    errors = validate_plan(plan, verify_bindings=False)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_event_count") != len(PARTITIONS)
        or run.get("source_command_attempt_count") != len(PARTITIONS)
        or run.get("all_partitions_attempted") is not True
        or run.get("target_identifier_retained") is not False
    ):
        errors.append("run_receipt")
    try:
        selected = successful_event_artifacts(plan, run, output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"events:{type(error).__name__}")
        selected = []

    evidence: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    raw_event_count = 0
    cutoff_year_records = 0
    publication_types: Counter[str] = Counter()
    for event, outcome, path, data in selected:
        summary = artifact_summary(path, event, plan)
        rows = data.get("results")
        if not isinstance(rows, list):
            errors.append(f"rows:{event['partition_id']}")
            continue
        stable_ids = {
            row.get("paperId")
            for row in rows
            if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
        }
        if summary.get("valid") is not True:
            errors.append(f"event:{event['partition_id']}")
        if (
            outcome.get("artifact_sha256") != digest(path)
            or outcome.get("artifact_bytes") != path.stat().st_size
            or outcome.get("full_abstract_count") != summary.get("full_abstract_count")
            or outcome.get("missing_full_abstract_count")
            != summary.get("missing_full_abstract_count")
            or outcome.get("publication_type_counts")
            != summary.get("publication_type_counts")
            or outcome.get("missing_publication_type_count")
            != summary.get("missing_publication_type_count")
        ):
            errors.append(f"artifact_binding:{event['partition_id']}")
        identifiers.update(identifier for identifier in stable_ids if isinstance(identifier, str))
        raw_event_count += len(rows)
        cutoff_year_records += sum(
            isinstance(row, Mapping) and row.get("year") == YEAR_END for row in rows
        )
        publication_types.update(summary.get("publication_type_counts", {}))
        evidence.append(
            {
                "partition_id": event["partition_id"],
                "artifact": path.name,
                "artifact_sha256": digest(path),
                "source_total": data.get("total"),
                "stable_id_count": len(stable_ids),
                "ordered_wos_ids_sha256": summary.get("ordered_wos_ids_sha256"),
                "native_ris": summary.get("native_ris"),
                "full_abstract_count": summary.get("full_abstract_count"),
                "missing_full_abstract_count": summary.get(
                    "missing_full_abstract_count"
                ),
                "publication_type_counts": summary.get("publication_type_counts"),
                "missing_publication_type_count": summary.get(
                    "missing_publication_type_count"
                ),
                "full_abstract_capture_valid": summary.get(
                    "full_abstract_capture_valid"
                ),
                "publication_type_capture_valid": summary.get(
                    "publication_type_capture_valid"
                ),
                "screenshots": summary.get("screenshots", []),
            }
        )

    union_ok = source_union_valid(source_union, identifiers, raw_event_count, plan)
    if not union_ok:
        errors.append("source_union")
    record_rows = record_union.get("records")
    record_union_ok = bool(
        record_union.get("schema_version") == RECORD_UNION_SCHEMA
        and record_union.get("plan_sha256") == digest(plan_path)
        and record_union.get("run_receipt_sha256") == digest(receipt_path)
        and record_union.get("source_event_record_count") == raw_event_count
        and record_union.get("unique_wos_id_count") == len(identifiers)
        and record_union.get("stable_id_set_sha256") == digest_set(identifiers)
        and record_union.get("records_with_full_abstract") == len(identifiers)
        and record_union.get("records_without_full_abstract") == 0
        and record_union.get("source_publication_type_field") == "documentType"
        and record_union.get("records_with_source_publication_type") == len(identifiers)
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("source_publication_type_counts")
        == dict(sorted(publication_types.items()))
        and record_union.get("complete") is True
        and isinstance(record_rows, list)
        and len(record_rows) == len(identifiers)
    )
    if not record_union_ok:
        errors.append("record_union")
    screenshot_count = sum(len(item["screenshots"]) for item in evidence)
    if screenshot_count != len(PARTITIONS) * 2:
        errors.append("screenshot_count")

    complete = bool(len(evidence) == len(PARTITIONS) and not errors)
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final",
        "complete": complete,
        "errors": errors,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "source_union": relative(source_union_path),
        "source_union_sha256": digest(source_union_path),
        "record_union": relative(record_union_path),
        "record_union_sha256": digest(record_union_path),
        "adapter": plan.get("adapter"),
        "accepted_source_event_count": len(evidence),
        "verified_screenshot_file_count": screenshot_count,
        "events": evidence,
        "stable_id_union": {
            "source_event_record_count": raw_event_count,
            "unique_wos_id_count": len(identifiers),
            "cross_partition_duplicate_occurrences": raw_event_count - len(identifiers),
            "stable_id_set_sha256": digest_set(identifiers),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "record_capture": {
            "full_abstracts_required": True,
            "source_publication_types_required": True,
            "source_publication_type_field": "documentType",
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
        "cutoff_screening": {
            "common_evidence_cutoff": CUTOFF_DATE,
            "source_year_upper_bound": YEAR_END,
            "source_precision": "year",
            "records_in_cutoff_year_requiring_exact_date_screening": cutoff_year_records,
            "status": "pending_screening",
        },
        "source_union_valid": union_ok,
        "record_union_valid": record_union_ok,
        "final_search_partitions_complete": complete,
        "status": "passed" if complete else "failed",
    }
    write_new(output, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "source_totals": {
                    item["partition_id"]: item["source_total"] for item in evidence
                },
                "unique_wos_ids": len(identifiers),
            }
        )
    )
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)

    validate_parser = commands.add_parser("validate-plan")
    validate_parser.add_argument("--plan", type=Path, required=True)
    validate_parser.add_argument("--verify-bindings", action="store_true")

    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=5.0)

    union_parser = commands.add_parser("source-union")
    union_parser.add_argument("--plan", type=Path, required=True)
    union_parser.add_argument("--receipt", type=Path, required=True)
    union_parser.add_argument("--output-dir", type=Path, required=True)
    union_parser.add_argument("--output", type=Path, required=True)

    records_parser = commands.add_parser("record-union")
    records_parser.add_argument("--plan", type=Path, required=True)
    records_parser.add_argument("--receipt", type=Path, required=True)
    records_parser.add_argument("--output-dir", type=Path, required=True)
    records_parser.add_argument("--output", type=Path, required=True)

    assessment_parser = commands.add_parser("assess")
    assessment_parser.add_argument("--plan", type=Path, required=True)
    assessment_parser.add_argument("--receipt", type=Path, required=True)
    assessment_parser.add_argument("--output-dir", type=Path, required=True)
    assessment_parser.add_argument("--source-union", type=Path, required=True)
    assessment_parser.add_argument("--record-union", type=Path, required=True)
    assessment_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "plan":
            plan = build_plan()
            errors = validate_plan(plan, verify_bindings=True)
            if errors:
                raise ValueError("Generated plan is invalid: " + ", ".join(errors))
            write_new(args.output, plan)
            print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
            return 0
        if args.command == "validate-plan":
            errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
            print(json.dumps({"status": "passed" if not errors else "failed", "errors": errors}))
            return 0 if not errors else 1
        if args.command == "run":
            if args.settle_seconds < 0:
                raise ValueError("--settle-seconds cannot be negative")
            return run_final(args.plan, args.output_dir, args.receipt, args.settle_seconds)
        if args.command == "source-union":
            return run_source_union(args.plan, args.receipt, args.output_dir, args.output)
        if args.command == "record-union":
            build_record_union(args.plan, args.receipt, args.output_dir, args.output)
            return 0
        if args.command == "assess":
            return assess(
                args.plan,
                args.receipt,
                args.output_dir,
                args.source_union,
                args.record_union,
                args.output,
            )
    except (FileExistsError, OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
