#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Plan, run, project, and assess final Compendex direct searches."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import subprocess
import sys
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER_ENTRYPOINT = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py"
)
ADAPTER_IMPLEMENTATION = ADAPTER_ENTRYPOINT.with_name("_engineering_village_search.py")
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/compendex_pilot008/queries.py"
PILOT_ASSESSMENT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/compendex/pilots/008/searches/assessment.json"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/compendex/source-specific-guidelines.md"
)

PLAN_SCHEMA = "slr1-compendex-final-direct-plan/v1"
RUN_SCHEMA = "slr1-compendex-final-direct-run/v1"
FAILURE_SCHEMA = "slr1-compendex-final-direct-failure/v1"
ASSESSMENT_SCHEMA = "slr1-compendex-final-direct-assessment/v1"
PROJECTION_SCHEMA = "slr1-compendex-paired-projection/v1"
CAPTURE_SCHEMA = "slr1-compendex-native-record-capture/v1"

SOURCE = "Compendex (Engineering Village)"
SOURCE_ID = "compendex"
INSPEC_SOURCE = "Inspec (Engineering Village)"
REVIEW_NAMESPACE = "main"
REVIEW_ID = "slr1-1.1-restart"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-compendex-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CUTOFF = "2026-08-24"
YEAR_START = 2011
YEAR_END = 2026
PAGE_SIZE = 25
LIMIT = 5000
MAX_PAGES = 200
TIMEOUT_SECONDS = 300.0
PAGE_DELAY_SECONDS = 2.0
EXPECTED_ADAPTER_VERSION = "16"
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "1f5914e19944c42d5357e2c26bd2250a0e4e74619dc885ccd187d9e1a1692014"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_ids(values: Sequence[str] | set[str]) -> str:
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


def encode_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_new_bytes(path: Path, value: bytes) -> None:
    """Write one new regular file without replacing an existing artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(value)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:  # pragma: no cover - OS write invariant
                raise OSError(f"Could not write {path}")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    write_new_bytes(path, encode_json(value))


def repository_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise RuntimeError("Cannot determine the repository revision")
    return value


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def load_queries() -> Any:
    require_regular(QUERY_SNAPSHOT)
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted Compendex query snapshot changed")
    spec = importlib.util.spec_from_file_location("compendex_final_direct_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted Compendex partition schedule changed")
    if tuple(module.EVENT_QUERIES) != PARTITIONS:
        raise RuntimeError("The accepted Compendex query order changed")
    if module.LANGUAGE_CLAUSE != "(English WN LA)":
        raise RuntimeError("The required Compendex language clause changed")
    return module


def adapter_version() -> str:
    require_regular(ADAPTER_IMPLEMENTATION)
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER_IMPLEMENTATION.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot determine the Engineering Village adapter version")
    return match.group(1)


def bindings() -> dict[str, str]:
    paths = (SCRIPT_PATH, QUERY_SNAPSHOT, PILOT_ASSESSMENT, SOURCE_GUIDELINE)
    for path in paths:
        require_regular(path)
    return {relative(path): digest(path) for path in paths}


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.commit.json")


def csv_path(output: Path) -> Path:
    return output.with_suffix(".csv")


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    return (
        output.with_name(f"{output.stem}.search-page.png"),
        output.with_name(f"{output.stem}.results-page.png"),
    )


def failure_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.NON_MERGEABLE_FAILURE.json")


def strategy_reference_for(sequence: int) -> str:
    return f"slr1-compendex-main-direct-v{sequence}"


def event_id(partition: str, sequence: int = 1) -> str:
    return f"final-main-{partition}-compendex-{sequence:03d}"


def plan_event(
    partition: str, query: str, strategy_version: str, *, sequence: int
) -> dict[str, Any]:
    return {
        "event_id": event_id(partition, sequence),
        "partition_id": partition,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "population_wildcard_count": query.count("*"),
        "output_filename": f"{partition}.json",
        "csv_filename": f"{partition}.csv",
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


def build_plan(
    *,
    sequence: int = 1,
    superseded_plan: Path | None = None,
    superseded_receipt: Path | None = None,
) -> dict[str, Any]:
    if sequence < 1:
        raise ValueError("Final-run sequence must be positive")
    if sequence > 1 and (superseded_plan is None or superseded_receipt is None):
        raise ValueError("A corrective final plan requires the superseded plan and receipt")
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        require_regular(superseded_plan)
        require_regular(superseded_receipt)
    queries = load_queries()
    if adapter_version() != EXPECTED_ADAPTER_VERSION:
        raise RuntimeError("The final Compendex plan requires Engineering Village adapter v16")
    strategy_version = repository_head()
    events = [
        plan_event(
            partition,
            queries.EVENT_QUERIES[partition],
            strategy_version,
            sequence=sequence,
        )
        for partition in PARTITIONS
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "final_run_sequence": sequence,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": REVIEW_ID,
        "phase": PHASE,
        "strategy_reference": strategy_reference_for(sequence),
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "accepted_translation_snapshot": relative(QUERY_SNAPSHOT),
        "accepted_translation_snapshot_sha256": digest(QUERY_SNAPSHOT),
        "readiness_evidence": {
            "pilot": "008",
            "assessment": relative(PILOT_ASSESSMENT),
            "assessment_sha256": digest(PILOT_ASSESSMENT),
            "decision": "current Compendex translation and paired adapter route passed",
        },
        "cutoff": {
            "exact_common_cutoff": CUTOFF,
            "source_year_start": YEAR_START,
            "source_year_upper_bound": YEAR_END,
            "source_precision": "year",
            "screening_requirement": (
                "Screen every 2026 record against the exact common cutoff. "
                "Engineering Village applies an inclusive Published-year range only."
            ),
        },
        "source_configuration": {
            "source_or_collection": "Compendex",
            "platform": "Engineering Village Expert Search",
            "url": "https://www.engineeringvillage.com/search/expert.url?database=1",
            "paired_database_selection": ["compendex", "inspec"],
            "database_mask": "3",
            "published_year_start": YEAR_START,
            "published_year_end": YEAR_END,
            "field": "ALL",
            "language_clause": "(English WN LA)",
            "autostemming": "off",
            "sort": "Date (Oldest)",
            "page_size": PAGE_SIZE,
            "document_type_filter": None,
            "peer_review_filter": None,
            "open_access_filter": None,
            "full_text_filter": None,
            "controlled_vocabulary_supplement": None,
        },
        "record_capture_contract": {
            "full_abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "native_source": "Engineering Village RIS AB/N2",
                "require_nonempty_for_each_projected_record": True,
                "snippet_substitution": False,
            },
            "source_publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "native_source": "Engineering Village RIS TY",
                "require_nonempty_for_each_projected_record": True,
                "source_filter_applied": None,
                "reviewer_coding": "Do not infer screening publication_type from source metadata.",
            },
            "native_ris": {
                "displayformat": "abstract",
                "strict_passes": 2,
                "private_preservation": True,
                "public_raw_ris": False,
            },
        },
        "translation": {
            "literal_atom": '("ordinary token or ordered phrase" WN ALL)',
            "population_wildcards": ["CubeSat*", "nanosat*", "SmallSat*"],
            "population_wildcard_count": 3,
            "other_wildcards": False,
            "proximity_operators": False,
            "pair_expansion": False,
            "controlled_vocabulary_supplement": False,
            "query_sha256": {
                partition: digest_text(queries.EVENT_QUERIES[partition])
                for partition in PARTITIONS
            },
            "query_character_counts": {
                partition: len(queries.EVENT_QUERIES[partition])
                for partition in PARTITIONS
            },
        },
        "strict_contract": {
            "paired_source_event": True,
            "complete_passes": 2,
            "membership_gate": "equal ordered database-scoped stable accession sequences",
            "native_ris_gate": "every rendered row reconciles to native RIS in both passes",
            "automatic_screenshots_required": True,
            "compendex_projection_only": True,
            "inspec_rows_published_in_this_directory": False,
        },
        "execution_policy": {
            "one_paired_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "retry_policy": "none_after_final_plan_execution_begins",
            "corrective_run_required_after_any_failure": True,
            "skip_full_abstracts": False,
            "source_publication_type_capture": True,
            "private_native_ris_retention": True,
        },
        "adapter": {
            "id": "engineering_village_search",
            "version": adapter_version(),
            "entrypoint": str(ADAPTER_ENTRYPOINT),
            "entrypoint_sha256": digest(ADAPTER_ENTRYPOINT),
            "implementation": str(ADAPTER_IMPLEMENTATION),
            "implementation_sha256": digest(ADAPTER_IMPLEMENTATION),
            "execution_route": "strict paired search_compendex_inspec Python API",
        },
        "bindings": {"files": bindings()},
        "events": events,
    }
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        plan["corrective_run"] = {
            "sequence": sequence,
            "reason": (
                "The first final plan retained a source control failure and local "
                "screenshot-receipt validation failures. This corrective plan reruns "
                "every unchanged partition from a fresh paired source event."
            ),
            "superseded_plan": relative(superseded_plan),
            "superseded_plan_sha256": digest(superseded_plan),
            "superseded_run_receipt": relative(superseded_receipt),
            "superseded_run_receipt_sha256": digest(superseded_receipt),
        }
    return plan


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool = False) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    sequence = plan.get("final_run_sequence", 1)
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        errors.append("sequence")
        sequence = 1
    corrective = plan.get("corrective_run")
    if sequence == 1:
        if corrective is not None:
            errors.append("unexpected_corrective")
    elif not isinstance(corrective, Mapping) or (
        corrective.get("sequence") != sequence
        or not isinstance(corrective.get("reason"), str)
        or not corrective.get("reason").strip()
        or not isinstance(corrective.get("superseded_plan"), str)
        or not isinstance(corrective.get("superseded_plan_sha256"), str)
        or not isinstance(corrective.get("superseded_run_receipt"), str)
        or not isinstance(corrective.get("superseded_run_receipt_sha256"), str)
    ):
        errors.append("corrective_provenance")
    elif (
        not (REPOSITORY_ROOT / corrective["superseded_plan"]).is_file()
        or not (REPOSITORY_ROOT / corrective["superseded_run_receipt"]).is_file()
        or digest(REPOSITORY_ROOT / corrective["superseded_plan"])
        != corrective["superseded_plan_sha256"]
        or digest(REPOSITORY_ROOT / corrective["superseded_run_receipt"])
        != corrective["superseded_run_receipt_sha256"]
    ):
        errors.append("corrective_binding")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != strategy_reference_for(sequence)
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("accepted_translation_snapshot") != relative(QUERY_SNAPSHOT)
        or plan.get("accepted_translation_snapshot_sha256") != digest(QUERY_SNAPSHOT)
    ):
        errors.append("identity")
    readiness = plan.get("readiness_evidence", {})
    if (
        not isinstance(readiness, Mapping)
        or readiness.get("pilot") != "008"
        or readiness.get("assessment") != relative(PILOT_ASSESSMENT)
        or readiness.get("assessment_sha256") != digest(PILOT_ASSESSMENT)
    ):
        errors.append("readiness_evidence")
    cutoff = plan.get("cutoff", {})
    if (
        not isinstance(cutoff, Mapping)
        or cutoff.get("exact_common_cutoff") != CUTOFF
        or cutoff.get("source_year_start") != YEAR_START
        or cutoff.get("source_year_upper_bound") != YEAR_END
        or cutoff.get("source_precision") != "year"
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration", {})
    if (
        not isinstance(configuration, Mapping)
        or configuration.get("source_or_collection") != "Compendex"
        or configuration.get("platform") != "Engineering Village Expert Search"
        or configuration.get("paired_database_selection") != ["compendex", "inspec"]
        or configuration.get("database_mask") != "3"
        or configuration.get("published_year_start") != YEAR_START
        or configuration.get("published_year_end") != YEAR_END
        or configuration.get("field") != "ALL"
        or configuration.get("language_clause") != queries.LANGUAGE_CLAUSE
        or configuration.get("autostemming") != "off"
        or configuration.get("sort") != "Date (Oldest)"
        or configuration.get("page_size") != PAGE_SIZE
        or configuration.get("document_type_filter") is not None
        or configuration.get("peer_review_filter") is not None
        or configuration.get("open_access_filter") is not None
        or configuration.get("full_text_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
    ):
        errors.append("source_configuration")
    capture = plan.get("record_capture_contract", {})
    if (
        not isinstance(capture, Mapping)
        or capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("normalized_field") != "abstract"
        or capture.get("full_abstracts", {}).get("native_source")
        != "Engineering Village RIS AB/N2"
        or capture.get("full_abstracts", {}).get("require_nonempty_for_each_projected_record")
        is not True
        or capture.get("source_publication_types", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("normalized_field")
        != "documentType"
        or capture.get("source_publication_types", {}).get("native_source")
        != "Engineering Village RIS TY"
        or capture.get("source_publication_types", {}).get(
            "require_nonempty_for_each_projected_record"
        )
        is not True
        or capture.get("source_publication_types", {}).get("source_filter_applied")
        is not None
    ):
        errors.append("record_capture_contract")
    translation = plan.get("translation", {})
    if (
        not isinstance(translation, Mapping)
        or translation.get("population_wildcards")
        != ["CubeSat*", "nanosat*", "SmallSat*"]
        or translation.get("population_wildcard_count") != 3
        or translation.get("other_wildcards") is not False
        or translation.get("proximity_operators") is not False
        or translation.get("pair_expansion") is not False
        or translation.get("controlled_vocabulary_supplement") is not False
    ):
        errors.append("translation")
    strict = plan.get("strict_contract", {})
    if (
        not isinstance(strict, Mapping)
        or strict.get("paired_source_event") is not True
        or strict.get("complete_passes") != 2
        or strict.get("automatic_screenshots_required") is not True
        or strict.get("compendex_projection_only") is not True
        or strict.get("inspec_rows_published_in_this_directory") is not False
    ):
        errors.append("strict_contract")
    execution = plan.get("execution_policy", {})
    if (
        not isinstance(execution, Mapping)
        or execution.get("one_paired_source_execution_per_partition") is not True
        or execution.get("continue_after_partition_failure") is not True
        or execution.get("retry_policy") != "none_after_final_plan_execution_begins"
        or execution.get("skip_full_abstracts") is not False
        or execution.get("source_publication_type_capture") is not True
        or execution.get("private_native_ris_retention") is not True
    ):
        errors.append("execution_policy")
    events = plan.get("events")
    if not isinstance(events, list) or [
        event.get("partition_id") for event in events if isinstance(event, Mapping)
    ] != list(PARTITIONS):
        return [*errors, "partition_coverage"]
    for partition, event in zip(PARTITIONS, events, strict=True):
        query = queries.EVENT_QUERIES[partition]
        if not isinstance(event, Mapping) or (
            event.get("event_id") != event_id(partition, sequence)
            or event.get("partition_id") != partition
            or event.get("query") != query
            or event.get("query_sha256") != digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("population_wildcard_count") != 3
            or event.get("output_filename") != f"{partition}.json"
            or event.get("csv_filename") != f"{partition}.csv"
            or event.get("page_size") != PAGE_SIZE
            or event.get("limit") != LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("timeout_seconds") != TIMEOUT_SECONDS
            or event.get("page_delay_seconds") != PAGE_DELAY_SECONDS
            or event.get("require_complete") is not True
            or event.get("strict_passes") != 2
            or event.get("full_abstracts") is not True
            or event.get("source_publication_types") is not True
            or event.get("strategy_version")
            != plan.get("repository_head_at_predeclaration")
        ):
            errors.append(f"event_contract:{partition}")
        if (
            query.count("*") != 3
            or query.count(queries.LANGUAGE_CLAUSE) != 1
            or "?" in query
            or re.search(r"\b(?:NEAR|ONEAR)(?:/\d+)?\b", query, re.IGNORECASE)
        ):
            errors.append(f"query_translation:{partition}")
    if verify_bindings:
        expected_bindings = bindings()
        if plan.get("bindings", {}).get("files") != expected_bindings:
            errors.append("bindings")
        adapter = plan.get("adapter", {})
        if (
            not isinstance(adapter, Mapping)
            or adapter.get("id") != "engineering_village_search"
            or adapter.get("version") != EXPECTED_ADAPTER_VERSION
            or adapter.get("version") != adapter_version()
            or adapter.get("entrypoint_sha256") != digest(ADAPTER_ENTRYPOINT)
            or adapter.get("implementation_sha256") != digest(ADAPTER_IMPLEMENTATION)
        ):
            errors.append("adapter")
    return errors


def load_adapter() -> Any:
    require_regular(ADAPTER_ENTRYPOINT)
    spec = importlib.util.spec_from_file_location(
        "compendex_final_direct_adapter", ADAPTER_ENTRYPOINT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_ENTRYPOINT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if (
        module.ADAPTER_ID != "engineering_village_search"
        or module.ADAPTER_VERSION != EXPECTED_ADAPTER_VERSION
    ):
        raise RuntimeError("The paired Engineering Village adapter changed")
    return module


def safe_error(adapter: Any | None, error: BaseException) -> str:
    implementation = getattr(adapter, "_implementation", None) if adapter else None
    cleaner = getattr(implementation, "safe_error_message", None)
    if callable(cleaner) and isinstance(error, Exception):
        return cleaner(error)
    return " ".join(str(error).split())[:500]


def image_state(path: Path) -> dict[str, Any]:
    return {
        "file_name": path.name,
        "exists": path.is_file() and not path.is_symlink(),
        "sha256": digest(path) if path.is_file() and not path.is_symlink() else None,
    }


def image_evidence_valid(output: Path, screenshots: Any) -> tuple[bool, list[dict[str, Any]]]:
    receipt = screenshots if isinstance(screenshots, Mapping) else {}
    rows: list[dict[str, Any]] = []
    valid = bool(
        receipt.get("schema_version") == "engineering-village-automatic-screenshots/v1"
        and receipt.get("automatic") is True
        and receipt.get("opt_out_available") is False
        and receipt.get("same_directory_as_json") is True
    )
    expected_pages = {
        "search_page": "configured_search_page",
        "results_page": "verified_first_results_page",
    }
    for key, image in zip(("search_page", "results_page"), screenshot_paths(output), strict=True):
        evidence = receipt.get(key, {}) if isinstance(receipt, Mapping) else {}
        image_valid = bool(
            image.is_file()
            and not image.is_symlink()
            and image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            and isinstance(evidence, Mapping)
            and evidence.get("page") == expected_pages[key]
            and evidence.get("file_name") == image.name
            and evidence.get("sha256") == digest(image)
            and isinstance(evidence.get("width"), int)
            and evidence["width"] > 0
            and isinstance(evidence.get("height"), int)
            and evidence["height"] > 0
            and isinstance(evidence.get("email_elements_masked"), int)
            and evidence["email_elements_masked"] >= 0
            and isinstance(evidence.get("account_elements_masked"), int)
            and evidence["account_elements_masked"] >= 0
            and evidence.get("full_page") is True
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


def _count_by_source(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        source = row.get("source")
        if not isinstance(source, str):
            raise ValueError("A paired Engineering Village record lacks a source label")
        counts[source] += 1
    return dict(counts)


def _strict_projection_evidence(result: Mapping[str, Any]) -> dict[str, Any]:
    metadata = result.get("output_metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("The paired result lacks output metadata")
    receipt = metadata.get("strict_complete_comparison_receipt")
    if not isinstance(receipt, Mapping):
        raise ValueError("The paired result lacks the strict comparison receipt")
    stable = receipt.get("stable_counts")
    if not isinstance(stable, Mapping):
        raise ValueError("The paired strict comparison lacks stable counts")
    if (
        receipt.get("complete_pass_count") != 2
        or receipt.get("sequence_match") is not True
        or stable.get("selected_databases") != ["compendex", "inspec"]
        or stable.get("selected_database_mask") != "3"
    ):
        raise ValueError("The paired strict result does not retain the required two-pass controls")
    for field in (
        "first_pass_sequence_sha256",
        "second_pass_sequence_sha256",
        "ordered_stable_id_sequence_sha256",
        "native_ris_batch_hash_sequence_sha256",
    ):
        value = receipt.get(field)
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"The paired strict receipt has an invalid {field}")
    counts = stable.get("source_export_ids_seen_by_database")
    if not isinstance(counts, Mapping) or set(counts) != {"compendex", "inspec"}:
        raise ValueError("The paired strict receipt lacks separate database counts")
    compendex_total = counts.get("compendex")
    inspec_total = counts.get("inspec")
    portal_total = stable.get("portal_total")
    if (
        isinstance(compendex_total, bool)
        or not isinstance(compendex_total, int)
        or compendex_total < 0
        or isinstance(inspec_total, bool)
        or not isinstance(inspec_total, int)
        or inspec_total < 0
        or isinstance(portal_total, bool)
        or not isinstance(portal_total, int)
        or portal_total != compendex_total + inspec_total
    ):
        raise ValueError("The paired strict database totals do not reconcile")
    return {
        "paired_source_total": portal_total,
        "compendex_total": compendex_total,
        "inspec_total": inspec_total,
        "strict_receipt": {
            "comparison": receipt.get("comparison"),
            "algorithm": receipt.get("algorithm"),
            "complete_pass_count": receipt.get("complete_pass_count"),
            "sequence_match": receipt.get("sequence_match"),
            "first_pass_sequence_sha256": receipt.get("first_pass_sequence_sha256"),
            "second_pass_sequence_sha256": receipt.get("second_pass_sequence_sha256"),
            "ordered_stable_id_sequence_sha256": receipt.get(
                "ordered_stable_id_sequence_sha256"
            ),
            "native_ris_batch_hash_sequence_sha256": receipt.get(
                "native_ris_batch_hash_sequence_sha256"
            ),
            "stable_counts": {
                "selected_databases": stable.get("selected_databases"),
                "selected_database_mask": stable.get("selected_database_mask"),
                "selected_database_scope": stable.get("selected_database_scope"),
                "portal_total": portal_total,
                "expected_page_count": stable.get("expected_page_count"),
                "pages_retrieved": stable.get("pages_retrieved"),
                "source_entries_retrieved": stable.get("source_entries_retrieved"),
                "source_document_ids_seen": stable.get("source_document_ids_seen"),
                "source_export_ids_seen": stable.get("source_export_ids_seen"),
                "results_retrieved": stable.get("results_retrieved"),
                "source_entries_retrieved_by_database": stable.get(
                    "source_entries_retrieved_by_database"
                ),
                "source_document_ids_seen_by_database": stable.get(
                    "source_document_ids_seen_by_database"
                ),
                "source_export_ids_seen_by_database": stable.get(
                    "source_export_ids_seen_by_database"
                ),
                "ordered_stable_id_count": stable.get("ordered_stable_id_count"),
                "native_ris_batch_count": stable.get("native_ris_batch_count"),
                "native_ris_record_counts": stable.get("native_ris_record_counts"),
                "execution_control_sha256": stable.get("execution_control_sha256"),
            },
        },
    }


def project_compendex_result(
    adapter: Any,
    result: Mapping[str, Any],
    event: Mapping[str, Any],
    plan: Mapping[str, Any],
    output: Path,
    started_at: str,
) -> dict[str, Any]:
    """Return a validated Compendex-only projection of one paired strict result."""
    adapter.assert_strict_complete_publication(result)
    paths = adapter.screenshot_paths_for_output(output)
    adapter.assert_automatic_screenshot_evidence(result, paths)
    if result.get("requested_query") != event.get("query"):
        raise ValueError("The source did not retain the requested query")
    metadata = result.get("output_metadata")
    rows = result.get("results")
    if not isinstance(metadata, Mapping) or not isinstance(rows, list):
        raise ValueError("The paired result lacks metadata or records")
    if (
        metadata.get("status") != "success"
        or metadata.get("observed_exact_query_echo") is not True
        or metadata.get("databases") != ["compendex", "inspec"]
        or metadata.get("database_mask") != "3"
        or metadata.get("autostemming_off_observed") is not True
        or metadata.get("year_range_selected_observed") is not True
        or metadata.get("last_update_selected_observed") is not False
        or metadata.get("source_year_control_values") != {"start": "2011", "end": "2026"}
        or metadata.get("sort") != "Date (Oldest)"
        or metadata.get("observed_page_size") != PAGE_SIZE
        or metadata.get("document_type_filter") is not None
        or metadata.get("result_facets") != []
    ):
        raise ValueError("The paired result does not preserve the final source controls")
    if result.get("total") != len(rows):
        raise ValueError("The paired result total does not equal its record count")
    evidence = _strict_projection_evidence(result)
    typed_rows: list[Mapping[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("The paired result contains a malformed record")
        typed_rows.append(row)
    observed_counts = _count_by_source(typed_rows)
    if observed_counts != {
        SOURCE: evidence["compendex_total"],
        INSPEC_SOURCE: evidence["inspec_total"],
    }:
        raise ValueError("The paired records do not reconcile to the strict database projections")
    projected_rows: list[dict[str, Any]] = []
    stable_ids: list[str] = []
    type_counts: Counter[str] = Counter()
    for index, row in enumerate(typed_rows, start=1):
        if row.get("source") != SOURCE:
            continue
        projected = copy.deepcopy(dict(row))
        paper_id = projected.get("paperId")
        abstract = projected.get("abstract")
        document_type = projected.get("documentType")
        if (
            not isinstance(paper_id, str)
            or not paper_id.strip()
            or not isinstance(abstract, str)
            or not abstract.strip()
            or not isinstance(document_type, str)
            or not document_type.strip()
        ):
            raise ValueError(
                "A projected Compendex record lacks a stable accession, full abstract, or source publication type"
            )
        stable_ids.append(paper_id)
        type_counts[document_type] += 1
        projected["source"] = SOURCE
        projected["rank"] = len(projected_rows) + 1
        projected_rows.append(projected)
    if (
        len(projected_rows) != evidence["compendex_total"]
        or len(stable_ids) != len(set(stable_ids))
    ):
        raise ValueError("The Compendex projection has duplicate or missing stable accessions")
    screenshots = metadata.get("screenshots")
    screenshots_valid, screenshot_rows = image_evidence_valid(output, screenshots)
    if not screenshots_valid:
        raise ValueError("The paired event screenshots do not match their receipt")
    executed_query = result.get("executed_query")
    if not isinstance(executed_query, str) or not executed_query.strip():
        raise ValueError("The paired event lacks a source-observed executed query")
    source_metadata: dict[str, Any] = {
        "status": "success",
        "retrieval_complete": True,
        "merge_eligible": True,
        "observed_exact_query_echo": True,
        "query_effective_native": executed_query,
        "search_mode": "expert",
        "databases": ["compendex", "inspec"],
        "database_mask": "3",
        "source_total": len(projected_rows),
        "source_reported_total": len(projected_rows),
        "source_reported_total_exact": True,
        "source_reported_total_scope": (
            "Compendex database-scoped projection of one complete paired "
            "Engineering Village source event"
        ),
        "raw_source_records": len(projected_rows),
        "client_side_exclusions": 0,
        "within_source_duplicates_removed": 0,
        "malformed_records_dropped": 0,
        "source_entries_retrieved": len(projected_rows),
        "source_document_ids_seen": len(projected_rows),
        "source_export_ids_seen": len(projected_rows),
        "source_entries_retrieved_by_database": {"compendex": len(projected_rows)},
        "source_document_ids_seen_by_database": {"compendex": len(projected_rows)},
        "source_export_ids_seen_by_database": {"compendex": len(projected_rows)},
        "source_side_date_filter": True,
        "source_side_year_start": YEAR_START,
        "source_side_year_end": YEAR_END,
        "year_filter_mode": "source_side_published_year",
        "year_start": YEAR_START,
        "year_end": YEAR_END,
        "sort": "Date (Oldest)",
        "sort_value": metadata.get("sort_value"),
        "document_type_filter": None,
        "result_facets": [],
        "screenshots": copy.deepcopy(screenshots),
    }
    raw_projection = {
        "schema_version": "academic-search-result/v1",
        "source": SOURCE,
        "requested_query": event["query"],
        "executed_query": executed_query,
        "total": len(projected_rows),
        "results": projected_rows,
        "output_metadata": source_metadata,
    }
    prisma_context = {
        "run_id": event["event_id"],
        "run_id_provenance": "explicitly_supplied",
        "review_id": plan["review_id"],
        "strategy_reference": plan["strategy_reference"],
        "strategy_version": event["strategy_version"],
        "phase": plan["phase"],
        "coverage_scope": "partition",
        "partition_id": event["partition_id"],
        "partition_label": event["partition_id"],
        "partition_description": (
            "Compendex final direct discovery partition "
            f"{event['partition_id']} from one paired Engineering Village event"
        ),
        "started_at_utc": started_at,
        "adapter_id": plan["adapter"]["id"],
        "adapter_version": plan["adapter"]["version"],
        "script_sha256": plan["adapter"]["implementation_sha256"],
        "script_hash_provenance": "predeclared_local_file_sha256",
    }
    finalized = adapter._implementation.finalize_search_result(
        raw_projection,
        source=SOURCE,
        executed_query=executed_query,
        merge_eligible=True,
        prisma_context=prisma_context,
    )
    compact = adapter._implementation.compact_search_result_for_output(finalized)
    compact["source"] = SOURCE
    compact["requested_query"] = event["query"]
    compact["executed_query"] = executed_query
    compact["total"] = len(projected_rows)
    compact["results"] = projected_rows
    compact_metadata = compact.get("output_metadata")
    if not isinstance(compact_metadata, dict):
        raise ValueError("The Compendex projection lost output metadata")
    compact_metadata.update(
        {
            "status": "success",
            "retrieval_complete": True,
            "merge_eligible": True,
            "screenshots": copy.deepcopy(screenshots),
            "projection": {
                "schema_version": PROJECTION_SCHEMA,
                "source_id": SOURCE_ID,
                "source_label": SOURCE,
                "projection": "Compendex rows only from a paired Compendex and Inspec event",
                "paired_database_selection": ["compendex", "inspec"],
                "database_mask": "3",
                "paired_source_total": evidence["paired_source_total"],
                "compendex_projection_total": len(projected_rows),
                "inspec_total_not_published": evidence["inspec_total"],
                "strict_two_pass_receipt": evidence["strict_receipt"],
                "source_rows_excluded_from_public_projection": evidence["inspec_total"],
            },
            "record_capture": {
                "schema_version": CAPTURE_SCHEMA,
                "abstract_field": "abstract",
                "abstract_source": "Engineering Village native RIS AB/N2",
                "records_with_full_abstract": len(projected_rows),
                "records_missing_full_abstract": 0,
                "publication_type_field": "documentType",
                "publication_type_source": "Engineering Village native RIS TY",
                "records_with_source_publication_type": len(projected_rows),
                "records_missing_source_publication_type": 0,
                "source_publication_type_counts": dict(sorted(type_counts.items())),
                "raw_ris_publication": "private only",
            },
            "screenshot_validation": screenshot_rows,
        }
    )
    prisma = compact_metadata.get("prisma_search_run")
    if not isinstance(prisma, Mapping) or (
        prisma.get("schema_version") != "academic-search-prisma-search-run/v2"
        or prisma.get("run_id") != event["event_id"]
        or prisma.get("source_descriptor", {}).get("source_id") != SOURCE_ID
        or prisma.get("coverage", {}).get("partition_id") != event["partition_id"]
        or prisma.get("staged_counts", {}).get("records_exported") != len(projected_rows)
        or prisma.get("completion_status") != "complete"
        or prisma.get("report_ready") is not True
    ):
        raise ValueError("The Compendex projection lacks a complete PRISMA receipt")
    return compact


def csv_bytes(artifact: Mapping[str, Any]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "Merge contract",
            "Schema version",
            "Merge eligible",
            "Search source",
            "Query",
            "Rank",
            "Paper ID",
            "DOI",
            "Title",
            "Authors",
            "Publication year",
            "Abstract",
            "Snippet",
            "Citation count",
            "URL",
            "Open access PDF",
            "Source total",
            "Publication title",
            "Publication date",
            "Document type",
        ]
    )
    rows = artifact.get("results")
    if not isinstance(rows, list):
        raise ValueError("The projected artifact lacks result rows")
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("The projected artifact has a malformed record")
        open_access = row.get("openAccess_pdf")
        writer.writerow(
            [
                "academic-search-merge/v1",
                "academic-search-result/v1",
                "true",
                SOURCE,
                artifact.get("executed_query", ""),
                row.get("rank", ""),
                row.get("paperId", ""),
                row.get("doi", ""),
                row.get("title", ""),
                "; ".join(
                    author.get("name", "")
                    for author in row.get("authors", [])
                    if isinstance(author, Mapping)
                ),
                row.get("year", "") or "",
                row.get("abstract", ""),
                row.get("snippet", ""),
                row.get("citationCount", 0),
                row.get("url", ""),
                open_access.get("url", "") if isinstance(open_access, Mapping) else "",
                artifact.get("total", ""),
                row.get("publicationTitle", ""),
                row.get("publicationDate", ""),
                row.get("documentType", ""),
            ]
        )
    return output.getvalue().encode("utf-8")


def publish_projection(output: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    """Publish a create-only Engineering Village v2 JSON/CSV/marker set."""
    output_csv = csv_path(output)
    marker = marker_path(output)
    paths = (output, output_csv, marker)
    if any(path.exists() or path.is_symlink() for path in paths):
        raise FileExistsError(f"Refusing to overwrite artifacts for {output.stem}")
    metadata = artifact.get("output_metadata")
    if not isinstance(metadata, dict):
        raise ValueError("The projected artifact lacks output metadata")
    transaction_id = secrets.token_hex(32)
    metadata.update(
        {
            "publication_state": "pending_nonmergeable",
            "publication_commit_protocol": "engineering_village_output_commit_v1",
            "publication_commit_state": "marker_required",
            "publication_transaction_id": transaction_id,
            "merge_commit_protocol": "engineering_village_output_commit_v1",
            "merge_commit_state": "marker_required",
            "merge_transaction_id": transaction_id,
            "publication_marker_path_persisted": False,
        }
    )
    json_payload = encode_json(artifact)
    csv_payload = csv_bytes(artifact)
    marker_value = {
        "version": 2,
        "transaction_id": transaction_id,
        "normalized_json": {"sha256": digest_bytes(json_payload), "bytes": len(json_payload)},
        "normalized_csv": {
            "file_name": output_csv.name,
            "sha256": digest_bytes(csv_payload),
            "bytes": len(csv_payload),
        },
    }
    try:
        write_new_bytes(output, json_payload)
        write_new_bytes(output_csv, csv_payload)
        write_new_json(marker, marker_value)
    except BaseException:
        # An unmarked JSON or JSON/CSV pair remains nonmergeable evidence.
        raise
    return marker_value


def marker_valid(output: Path, artifact: Mapping[str, Any]) -> bool:
    marker = marker_path(output)
    output_csv = csv_path(output)
    if not all(path.is_file() and not path.is_symlink() for path in (output, output_csv, marker)):
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    metadata = artifact.get("output_metadata")
    if not isinstance(metadata, Mapping):
        return False
    transaction_id = value.get("transaction_id")
    json_entry = value.get("normalized_json")
    csv_entry = value.get("normalized_csv")
    return bool(
        value.get("version") == 2
        and isinstance(transaction_id, str)
        and re.fullmatch(r"[0-9a-f]{64}", transaction_id)
        and isinstance(json_entry, Mapping)
        and json_entry.get("sha256") == digest(output)
        and json_entry.get("bytes") == output.stat().st_size
        and isinstance(csv_entry, Mapping)
        and csv_entry.get("file_name") == output_csv.name
        and csv_entry.get("sha256") == digest(output_csv)
        and csv_entry.get("bytes") == output_csv.stat().st_size
        and metadata.get("publication_state") == "pending_nonmergeable"
        and metadata.get("publication_commit_protocol")
        == "engineering_village_output_commit_v1"
        and metadata.get("publication_commit_state") == "marker_required"
        and metadata.get("publication_transaction_id") == transaction_id
        and metadata.get("merge_commit_protocol") == "engineering_village_output_commit_v1"
        and metadata.get("merge_commit_state") == "marker_required"
        and metadata.get("merge_transaction_id") == transaction_id
        and metadata.get("publication_marker_path_persisted") is False
    )


def artifact_summary(
    output: Path, event: Mapping[str, Any], plan: Mapping[str, Any]
) -> dict[str, Any]:
    if not output.is_file() or output.is_symlink():
        return {"artifact_written": False, "valid": False}
    try:
        artifact = load(output)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "artifact_written": True,
            "valid": False,
            "parse_error": type(error).__name__,
        }
    metadata = artifact.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    rows = artifact.get("results")
    rows = rows if isinstance(rows, list) else []
    record_errors: list[str] = []
    stable_ids: list[str] = []
    publication_types: Counter[str] = Counter()
    full_abstract_count = 0
    source_publication_type_count = 0
    for rank, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            record_errors.append("malformed")
            continue
        paper_id = row.get("paperId")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if not isinstance(paper_id, str) or not paper_id.strip():
            record_errors.append("missing_paper_id")
        else:
            stable_ids.append(paper_id)
        if row.get("source") != SOURCE:
            record_errors.append("wrong_source")
        if row.get("rank") != rank:
            record_errors.append("rank")
        if isinstance(abstract, str) and abstract.strip():
            full_abstract_count += 1
        else:
            record_errors.append("missing_full_abstract")
        if isinstance(document_type, str) and document_type.strip():
            source_publication_type_count += 1
            publication_types[document_type] += 1
        else:
            record_errors.append("missing_source_publication_type")
    projection = metadata.get("projection")
    capture = metadata.get("record_capture")
    prisma = metadata.get("prisma_search_run")
    screenshots_valid, screenshot_rows = image_evidence_valid(
        output, metadata.get("screenshots")
    )
    total = artifact.get("total")
    projection_valid = bool(
        isinstance(projection, Mapping)
        and projection.get("schema_version") == PROJECTION_SCHEMA
        and projection.get("source_id") == SOURCE_ID
        and projection.get("source_label") == SOURCE
        and projection.get("paired_database_selection") == ["compendex", "inspec"]
        and projection.get("database_mask") == "3"
        and projection.get("compendex_projection_total") == total
        and isinstance(projection.get("inspec_total_not_published"), int)
        and projection.get("inspec_total_not_published") >= 0
        and projection.get("paired_source_total")
        == total + projection.get("inspec_total_not_published")
        and projection.get("source_rows_excluded_from_public_projection")
        == projection.get("inspec_total_not_published")
        and projection.get("strict_two_pass_receipt", {}).get("complete_pass_count") == 2
        and projection.get("strict_two_pass_receipt", {}).get("sequence_match") is True
        and projection.get("strict_two_pass_receipt", {}).get("stable_counts", {}).get(
            "selected_databases"
        )
        == ["compendex", "inspec"]
    )
    capture_valid = bool(
        isinstance(capture, Mapping)
        and capture.get("schema_version") == CAPTURE_SCHEMA
        and capture.get("abstract_field") == "abstract"
        and capture.get("abstract_source") == "Engineering Village native RIS AB/N2"
        and capture.get("records_with_full_abstract") == total
        and capture.get("records_missing_full_abstract") == 0
        and capture.get("publication_type_field") == "documentType"
        and capture.get("publication_type_source") == "Engineering Village native RIS TY"
        and capture.get("records_with_source_publication_type") == total
        and capture.get("records_missing_source_publication_type") == 0
        and capture.get("source_publication_type_counts") == dict(sorted(publication_types.items()))
    )
    prisma_valid = bool(
        isinstance(prisma, Mapping)
        and prisma.get("schema_version") == "academic-search-prisma-search-run/v2"
        and prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("coverage", {}).get("coverage_scope") == "partition"
        and prisma.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and prisma.get("source_descriptor", {}).get("source_id") == SOURCE_ID
        and prisma.get("source_descriptor", {}).get("source_label") == SOURCE
        and prisma.get("adapter", {}).get("adapter_id") == plan.get("adapter", {}).get("id")
        and prisma.get("adapter", {}).get("adapter_version") == plan.get("adapter", {}).get("version")
        and prisma.get("adapter", {}).get("script_sha256")
        == plan.get("adapter", {}).get("implementation_sha256")
        and prisma.get("strategy", {}).get("executed_query") == artifact.get("executed_query")
        and prisma.get("staged_counts", {}).get("records_exported") == total
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
    )
    count_valid = bool(
        isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 0
        and total == len(rows) == len(stable_ids) == len(set(stable_ids))
    )
    controls_valid = bool(
        artifact.get("schema_version") == "academic-search-result/v1"
        and artifact.get("source") == SOURCE
        and artifact.get("requested_query") == event.get("query")
        and isinstance(artifact.get("executed_query"), str)
        and bool(artifact.get("executed_query").strip())
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
    )
    valid = bool(
        controls_valid
        and count_valid
        and not record_errors
        and projection_valid
        and capture_valid
        and prisma_valid
        and screenshots_valid
        and marker_valid(output, artifact)
    )
    return {
        "artifact_written": True,
        "valid": valid,
        "artifact_sha256": digest(output),
        "artifact_bytes": output.stat().st_size,
        "source_total": total,
        "stable_id_count": len(stable_ids),
        "stable_id_set_sha256": digest_ids(set(stable_ids)),
        "full_abstract_count": full_abstract_count,
        "missing_full_abstract_count": len(rows) - full_abstract_count,
        "source_publication_type_count": source_publication_type_count,
        "missing_source_publication_type_count": len(rows)
        - source_publication_type_count,
        "source_publication_type_counts": dict(sorted(publication_types.items())),
        "record_errors": sorted(set(record_errors)),
        "controls_valid": controls_valid,
        "projection_valid": projection_valid,
        "capture_valid": capture_valid,
        "prisma_valid": prisma_valid,
        "screenshots_valid": screenshots_valid,
        "terminal_marker_valid": marker_valid(output, artifact),
        "screenshots": screenshot_rows,
        "paired_source_total": projection.get("paired_source_total")
        if isinstance(projection, Mapping)
        else None,
        "inspec_total_not_published": projection.get("inspec_total_not_published")
        if isinstance(projection, Mapping)
        else None,
    }


def private_native_root(plan_path: Path) -> Path:
    return (
        Path.home()
        / ".cache/nanosatellite-mbse/slr1/compendex-final-direct"
        / digest(plan_path)
    )


def ensure_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    details = path.lstat()
    if path.is_symlink() or not path.is_dir() or details.st_mode & 0o077:
        raise ValueError("The private native RIS directory is not owner-only")
    os.chmod(path, 0o700)


def planned_output_paths(output: Path) -> tuple[Path, ...]:
    return (
        output,
        csv_path(output),
        marker_path(output),
        *screenshot_paths(output),
        failure_path(output),
    )


def preflight_output_paths(output_dir: Path, plan: Mapping[str, Any]) -> None:
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        for path in planned_output_paths(output):
            if path.exists() or path.is_symlink():
                raise FileExistsError(f"Refusing to reuse final artifact path: {path}")


def failure_receipt(
    event: Mapping[str, Any],
    error: BaseException,
    adapter: Any | None,
    output: Path,
    started_at: str,
) -> dict[str, Any]:
    images = {
        "search_page": image_state(screenshot_paths(output)[0]),
        "results_page": image_state(screenshot_paths(output)[1]),
    }
    return {
        "schema_version": FAILURE_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "status": "error",
        "merge_eligible": False,
        "do_not_merge": True,
        "started_at_utc": started_at,
        "failed_at_utc": now(),
        "error_type": type(error).__name__,
        "error_code": getattr(error, "code", None),
        "error": safe_error(adapter, error),
        "source_total": None,
        "compendex_total": None,
        "inspec_total": None,
        "records_retained": 0,
        "screenshots": images,
        "disposition": "A corrective final run is required. Do not reuse this event.",
    }


def run_final(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    *,
    settle_seconds: float,
    native_root: Path | None,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    require_regular(plan_path)
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid final Compendex plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The final Compendex output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    preflight_output_paths(output_dir, plan)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url) is None:
        raise ValueError("Final Compendex execution requires a loopback browser endpoint")
    adapter = load_adapter()
    if (
        digest(ADAPTER_ENTRYPOINT) != plan["adapter"]["entrypoint_sha256"]
        or digest(ADAPTER_IMPLEMENTATION) != plan["adapter"]["implementation_sha256"]
    ):
        raise ValueError("The paired Engineering Village adapter changed after predeclaration")
    private_root = native_root if native_root is not None else private_native_root(plan_path)
    ensure_private_directory(private_root)

    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        native_directory = private_root / str(event["event_id"])
        if native_directory.exists() or native_directory.is_symlink():
            raise FileExistsError(
                "Refusing to reuse a private native RIS directory for "
                f"{event['partition_id']}"
            )
        event_started = now()
        try:
            paths = adapter.screenshot_paths_for_output(output)
            result = adapter.search_compendex_inspec(
                event["query"],
                limit=event["limit"],
                year_start=YEAR_START,
                year_end=YEAR_END,
                max_pages=event["max_pages"],
                timeout_seconds=event["timeout_seconds"],
                page_delay_seconds=event["page_delay_seconds"],
                cdp_url=cdp_url,
                native_export_dir=native_directory,
                screenshot_paths=paths,
                require_complete=True,
                prisma_context={
                    "run_id": event["event_id"],
                    "run_id_provenance": "explicitly_supplied",
                    "review_id": plan["review_id"],
                    "strategy_reference": plan["strategy_reference"],
                    "strategy_version": event["strategy_version"],
                    "phase": plan["phase"],
                    "coverage_scope": "partition",
                    "partition_id": event["partition_id"],
                    "partition_label": event["partition_id"],
                    "partition_description": (
                        "Paired Engineering Village final event before the "
                        "Compendex-only public projection"
                    ),
                    "adapter_id": plan["adapter"]["id"],
                    "adapter_version": plan["adapter"]["version"],
                    "script_sha256": plan["adapter"]["implementation_sha256"],
                    "script_hash_provenance": "predeclared_local_file_sha256",
                },
            )
            artifact = project_compendex_result(
                adapter, result, event, plan, output, event_started
            )
            publish_projection(output, artifact)
            summary = artifact_summary(output, event, plan)
            if summary.get("valid") is not True:
                raise ValueError("The published Compendex projection failed validation")
            outcome = {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "success": True,
                "artifact": output.name,
                "csv": csv_path(output).name,
                "private_native_ris_preserved": True,
                "private_native_ris_path_persisted": False,
                "source_command_attempt_count": 1,
                "started_at_utc": event_started,
                "completed_at_utc": now(),
                **summary,
            }
        except Exception as error:  # noqa: BLE001 - retain a final event failure receipt.
            failure = failure_path(output)
            write_new_json(failure, failure_receipt(event, error, adapter, output, event_started))
            outcome = {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "success": False,
                "artifact": None,
                "failure_artifact": failure.name,
                "source_command_attempt_count": 1,
                "started_at_utc": event_started,
                "completed_at_utc": now(),
                "error_type": type(error).__name__,
                "error_code": getattr(error, "code", None),
                "error": safe_error(adapter, error),
                "screenshots": {
                    "search_page": image_state(screenshot_paths(output)[0]),
                    "results_page": image_state(screenshot_paths(output)[1]),
                },
            }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "success": outcome["success"],
                    "compendex_total": outcome.get("source_total"),
                    "abstracts": outcome.get("full_abstract_count"),
                    "publication_types": outcome.get("source_publication_type_counts"),
                    "error": outcome.get("error"),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == len(plan["events"]) and all(
        outcome.get("success") is True for outcome in outcomes
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
        "private_native_ris_root_persisted": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": sum(
            outcome.get("source_command_attempt_count", 0) for outcome in outcomes
        ),
        "accepted_event_count": sum(outcome.get("success") is True for outcome in outcomes),
        "all_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new_json(receipt_path, receipt)
    return 0 if success else 1


def create_source_union(
    plan_path: Path, receipt_path: Path, output_dir: Path, output: Path
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    receipt = load(receipt_path)
    if validate_plan(plan, verify_bindings=False):
        raise ValueError("Cannot create a source union from an invalid Compendex plan")
    if receipt.get("schema_version") != RUN_SCHEMA or receipt.get("success") is not True:
        raise ValueError("Cannot create a source union from an incomplete final run")
    inputs = [output_dir / str(event["output_filename"]) for event in plan["events"]]
    for path in inputs:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing final Compendex artifact: {path}")
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *[str(path) for path in inputs],
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
    if completed.returncode != 0 or not output.is_file() or output.is_symlink():
        message = " ".join(completed.stderr.split())[:500]
        raise RuntimeError(f"Could not create the Compendex source-union receipt: {message}")
    return 0


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    source_union_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    receipt = load(receipt_path)
    source_union = load(source_union_path)
    errors = validate_plan(plan, verify_bindings=False)
    if (
        receipt.get("schema_version") != RUN_SCHEMA
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("success") is not True
        or receipt.get("accepted_event_count") != len(PARTITIONS)
    ):
        errors.append("run_receipt")
    outcomes = {
        item.get("event_id"): item
        for item in receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    summaries: list[dict[str, Any]] = []
    all_ids: set[str] = set()
    occurrence_count = 0
    full_abstract_count = 0
    source_publication_type_count = 0
    publication_types: Counter[str] = Counter()
    paired_total = 0
    inspec_total = 0
    for event in plan["events"]:
        output_path = output_dir / str(event["output_filename"])
        summary = artifact_summary(output_path, event, plan)
        summaries.append(
            {"partition_id": event["partition_id"], "artifact": output_path.name, **summary}
        )
        outcome = outcomes.get(event["event_id"])
        if (
            outcome is None
            or outcome.get("success") is not True
            or summary.get("valid") is not True
            or outcome.get("artifact_sha256") != summary.get("artifact_sha256")
            or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
        ):
            errors.append(f"event:{event['partition_id']}")
            continue
        data = load(output_path)
        rows = data.get("results", [])
        identifiers = {
            row["paperId"] for row in rows if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
        }
        all_ids.update(identifiers)
        occurrence_count += len(rows)
        full_abstract_count += summary.get("full_abstract_count", 0)
        source_publication_type_count += summary.get("source_publication_type_count", 0)
        paired_total += summary.get("paired_source_total", 0)
        inspec_total += summary.get("inspec_total_not_published", 0)
        for publication_type, count in summary.get("source_publication_type_counts", {}).items():
            if isinstance(publication_type, str) and isinstance(count, int):
                publication_types[publication_type] += count
    union_source = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    source_union_valid = bool(
        source_union.get("schema_version") == "academic-search-source-union-receipt/v1"
        and source_union.get("review_namespace") == REVIEW_NAMESPACE
        and source_union.get("review_id") == REVIEW_ID
        and source_union.get("strategy_reference") == plan.get("strategy_reference")
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and union_source.get("event_total_sum") == occurrence_count
        and set(union_source.get("stable_record_ids", [])) == all_ids
        and source_union.get("artifact_count") == len(PARTITIONS)
    )
    if not source_union_valid:
        errors.append("source_union")
    complete = bool(not errors and len(summaries) == len(PARTITIONS))
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if complete else "failed",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "source_union_receipt": relative(source_union_path),
        "source_union_receipt_sha256": digest(source_union_path),
        "partition_count": len(PARTITIONS),
        "accepted_partition_count": sum(item.get("valid") is True for item in summaries),
        "compendex_record_occurrence_count": occurrence_count,
        "unique_compendex_record_count": len(all_ids),
        "unique_compendex_record_id_set_sha256": digest_ids(all_ids),
        "paired_event_record_occurrence_count": paired_total,
        "inspec_record_occurrence_count_not_published": inspec_total,
        "full_abstract_occurrence_count": full_abstract_count,
        "missing_full_abstract_occurrence_count": occurrence_count - full_abstract_count,
        "source_publication_type_occurrence_count": source_publication_type_count,
        "missing_source_publication_type_occurrence_count": occurrence_count
        - source_publication_type_count,
        "source_publication_type_counts": dict(sorted(publication_types.items())),
        "all_projected_records_have_full_abstracts": full_abstract_count == occurrence_count,
        "all_projected_records_have_source_publication_types": source_publication_type_count
        == occurrence_count,
        "source_union_valid": source_union_valid,
        "partitions": summaries,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new_json(output, assessment)
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-plan")
    build_parser.add_argument("--output", type=Path, required=True)
    build_parser.add_argument("--sequence", type=int, default=1)
    build_parser.add_argument("--superseded-plan", type=Path)
    build_parser.add_argument("--superseded-receipt", type=Path)

    check_parser = subparsers.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    check_parser.add_argument("--verify-bindings", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=10.0)
    run_parser.add_argument("--native-ris-root", type=Path)

    union_parser = subparsers.add_parser("source-union")
    union_parser.add_argument("--plan", type=Path, required=True)
    union_parser.add_argument("--receipt", type=Path, required=True)
    union_parser.add_argument("--output-dir", type=Path, required=True)
    union_parser.add_argument("--output", type=Path, required=True)

    assess_parser = subparsers.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        if args.output.exists() or args.output.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {args.output}")
        plan = build_plan(
            sequence=args.sequence,
            superseded_plan=args.superseded_plan,
            superseded_receipt=args.superseded_receipt,
        )
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid Compendex plan: " + ", ".join(errors))
        write_new_json(args.output, plan)
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
            native_root=args.native_ris_root,
        )
    if args.command == "source-union":
        return create_source_union(args.plan, args.receipt, args.output_dir, args.output)
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.output_dir,
            args.source_union,
            args.output,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
