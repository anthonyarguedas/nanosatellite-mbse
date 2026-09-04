#!/usr/bin/env python3
"""Plan, execute, and assess final PQDT Global direct searches."""

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
PILOT004_ASSESSMENT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/pqdt-global/pilots/004/searches/assessment.json"
)
PILOT005_ASSESSMENT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/pqdt-global/pilots/005/searches/inclusion-assessment.json"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/pqdt-global/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-pqdt-final-direct-plan/v1"
RUN_SCHEMA = "slr1-pqdt-final-direct-run/v1"
ASSESSMENT_SCHEMA = "slr1-pqdt-final-direct-assessment/v1"
SOURCE = "ProQuest Dissertations & Theses Global"
SOURCE_ID = "proquest_dissertations_theses_global"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-pqdt-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
YEAR_START = 2011
YEAR_END = 2026
CUTOFF = "2026-08-24"
PAGE_SIZE = 20
LIMIT = 10_000
MAX_PAGES = 500
TIMEOUT_SECONDS = 180
PAGE_DELAY_SECONDS = 0.1
DETAIL_DELAY_SECONDS = 0.1
INTER_EVENT_DELAY_SECONDS = 1.0
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
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


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
    spec = importlib.util.spec_from_file_location("pqdt_final_direct_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted PQDT partition schedule changed")
    if tuple(module.WILDCARD_SCHEDULE) != PARTITIONS:
        raise RuntimeError("The accepted PQDT wildcard schedule changed")
    if module.FAMILY_COUNT != 128 or module.QUERY_LIMIT != 50_000:
        raise RuntimeError("The accepted PQDT wildcard or query-limit evidence changed")
    for partition, query in module.WILDCARD_SCHEDULE.items():
        if (
            not isinstance(query, str)
            or len(query) >= module.QUERY_LIMIT
            or "[*" not in query
            or "NEAR" in query.upper()
            or " PRE/" in query.upper()
        ):
            raise RuntimeError(f"The accepted PQDT query is invalid for {partition}")
    return module


def readiness_evidence(queries: Any) -> dict[str, Any]:
    pilot004 = load(PILOT004_ASSESSMENT)
    pilot005 = load(PILOT005_ASSESSMENT)
    comparisons = pilot004.get("partition_comparisons")
    if (
        pilot004.get("decision") != "accept_and_prefer_bounded_wildcard_translation"
        or pilot004.get("accepted_for_partitions") != list(PARTITIONS)
        or pilot004.get("translation", {}).get("wildcard_family_count")
        != queries.FAMILY_COUNT
        or not isinstance(comparisons, Mapping)
        or any(
            comparisons.get(partition, {}).get("sets_equal") is not True
            or comparisons.get(partition, {}).get("orders_equal") is not True
            for partition in PARTITIONS
        )
    ):
        raise RuntimeError("PQDT bounded-wildcard readiness evidence changed")
    if (
        pilot005.get("decision")
        != "do_not_add_pq_subject_or_index_term_supplement"
        or pilot005.get("prospective_translation")
        != "Retain the accepted bounded-wildcard NOFT schedule without a PSUB.EXACT or IF.EXACT supplement."
        or pilot005.get("evidence", {}).get("descriptor_only_record_count") != 0
    ):
        raise RuntimeError("PQDT controlled-vocabulary readiness evidence changed")
    return {
        "bounded_wildcard_equivalence": {
            "pilot": "004",
            "assessment": relative(PILOT004_ASSESSMENT),
            "assessment_sha256": digest(PILOT004_ASSESSMENT),
            "accepted_wildcard_family_count": queries.FAMILY_COUNT,
            "complete_result_bound": LIMIT,
            "acceptance": "literal and bounded-wildcard stable-ID sets and source order were equal in every partition",
        },
        "controlled_vocabulary_decision": {
            "pilot": "005",
            "assessment": relative(PILOT005_ASSESSMENT),
            "assessment_sha256": digest(PILOT005_ASSESSMENT),
            "decision": "no PSUB.EXACT or IF.EXACT supplement",
        },
    }


def binding_paths() -> tuple[Path, ...]:
    return (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        PILOT004_ASSESSMENT,
        PILOT005_ASSESSMENT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.{MARKER_TAG}.json")


def screenshot_paths(path: Path) -> dict[str, Path]:
    return {
        "search_page": path.with_name(f"{path.stem}.search-page.png"),
        "results_page": path.with_name(f"{path.stem}.results-page.png"),
    }


def plan_event(
    partition: str, query: str, index: int, strategy_version: str
) -> dict[str, Any]:
    return {
        "event_id": f"final-main-{partition}-pqdt-{index:03d}",
        "partition_id": partition,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "wildcard_operator_count": query.count("[*"),
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
        "strategy_version": strategy_version,
    }


def build_plan() -> dict[str, Any]:
    queries = load_queries()
    if adapter_version() != EXPECTED_ADAPTER_VERSION:
        raise RuntimeError("The final PQDT plan requires adapter version 6")
    strategy_version = repository_head()
    events = [
        plan_event(
            partition,
            queries.WILDCARD_SCHEDULE[partition],
            index,
            strategy_version,
        )
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
        "event_kind": "final",
        "phase": PHASE,
        "strategy_reference": STRATEGY_REFERENCE,
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "accepted_translation_snapshot": relative(QUERY_SNAPSHOT),
        "accepted_translation_snapshot_sha256": digest(QUERY_SNAPSHOT),
        "readiness_evidence": readiness_evidence(queries),
        "cutoff": {
            "exact_common_cutoff": CUTOFF,
            "source_year_start": YEAR_START,
            "source_year_end": YEAR_END,
            "source_precision": "year",
            "screening_requirement": (
                "Retain every 2026 record for screening against the exact common "
                "cutoff of 2026-08-24. PQDT YR has year precision."
            ),
        },
        "source_configuration": {
            "source_or_collection": SOURCE,
            "platform": "ProQuest",
            "url": "https://www.proquest.com/pqdtglobal/commandline",
            "database_selection": "exactly one PQDT Global database label",
            "field": "Command Line Search NOFT",
            "language_clause": "LA(English)",
            "sort": "DateAsc / Oldest first",
            "page_size": PAGE_SIZE,
            "full_text_filter": False,
            "duplicate_exclusion": False,
            "spelling_variants": False,
            "form_variants": False,
            "show_variants": False,
            "degree_filter": None,
            "completion_filter": None,
            "publication_type_filter": None,
            "peer_review_filter": None,
            "access_filter": None,
            "controlled_vocabulary_supplement": None,
        },
        "record_capture_contract": {
            "full_abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "required_state_fields": [
                    "abstract_source",
                    "abstract_detail_verified",
                    "abstract_is_truncated",
                    "abstract_not_available",
                ],
                "source_method": "complete visible rendered Abstract/Details field",
                "snippet_substitution": False,
                "source_absence_policy": "retain an empty abstract only with explicit source absence",
            },
            "source_publication_types": {
                "required": True,
                "required_fields": ["sourcePublicationType", "documentType"],
                "source_method": "visible rendered PQDT result-card source type",
                "source_filter_applied": None,
                "reviewer_coding": "Do not infer screening publication_type from source metadata.",
            },
        },
        "translation": {
            "literal_atom": "NOFT(straight-double-quoted literal)",
            "family_atom": "NOFT(shortest safe stem[*n])",
            "one_source_expression_per_partition": True,
            "wildcard_family_count": queries.FAMILY_COUNT,
            "wildcard_operators_by_partition": {
                partition: queries.WILDCARD_SCHEDULE[partition].count("[*")
                for partition in PARTITIONS
            },
            "query_character_counts": {
                partition: len(queries.WILDCARD_SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "query_sha256": {
                partition: digest_text(queries.WILDCARD_SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "controlled_vocabulary_supplement": False,
            "proximity": False,
            "pair_expansion": False,
        },
        "strict_contract": {
            "complete_rendered_passes": 2,
            "membership_gate": "equal complete ordered numeric PQDT document-ID ledgers",
            "source_total_bound": LIMIT,
            "automatic_screenshots_required": True,
            "marker_bound_json_required": True,
            "full_abstract_detail_page_required": True,
            "source_publication_type_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "retry_policy": "none after final-plan execution begins",
            "corrective_run_required_after_any_failure": True,
            "skip_full_abstracts": False,
            "source_publication_type_capture": True,
            "inter_event_delay_seconds": INTER_EVENT_DELAY_SECONDS,
        },
        "adapter": {
            "id": "search_pqdt",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
            "detail_projection": {
                "abstract_field": "abstract",
                "source_publication_type_field": "sourcePublicationType",
                "document_type_field": "documentType",
            },
        },
        "bindings": {
            "files": {relative(path): digest(path) for path in binding_paths()}
        },
        "source_union_expected_partitions": list(PARTITIONS),
        "source_union_expected_sources": [SOURCE_ID],
        "events": events,
    }


def _applied(limits: Mapping[str, Any], name: str) -> Any:
    item = limits.get(name)
    if not isinstance(item, Mapping) or item.get("state") != "applied":
        return None
    return item.get("value")


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
        or plan.get("event_kind") != "final"
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("accepted_translation_snapshot") != relative(QUERY_SNAPSHOT)
        or plan.get("accepted_translation_snapshot_sha256") != digest(QUERY_SNAPSHOT)
    ):
        errors.append("identity")
    if (
        plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("source_union_expected_sources") != [SOURCE_ID]
    ):
        errors.append("source_union_schedule")
    cutoff = plan.get("cutoff")
    if (
        not isinstance(cutoff, Mapping)
        or cutoff.get("exact_common_cutoff") != CUTOFF
        or cutoff.get("source_year_start") != YEAR_START
        or cutoff.get("source_year_end") != YEAR_END
        or cutoff.get("source_precision") != "year"
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration")
    if (
        not isinstance(configuration, Mapping)
        or configuration.get("database_selection")
        != "exactly one PQDT Global database label"
        or configuration.get("field") != "Command Line Search NOFT"
        or configuration.get("language_clause") != "LA(English)"
        or configuration.get("sort") != "DateAsc / Oldest first"
        or configuration.get("page_size") != PAGE_SIZE
        or configuration.get("full_text_filter") is not False
        or configuration.get("duplicate_exclusion") is not False
        or configuration.get("spelling_variants") is not False
        or configuration.get("form_variants") is not False
        or configuration.get("show_variants") is not False
        or any(
            configuration.get(name) is not None
            for name in (
                "degree_filter",
                "completion_filter",
                "publication_type_filter",
                "peer_review_filter",
                "access_filter",
                "controlled_vocabulary_supplement",
            )
        )
    ):
        errors.append("source_configuration")
    capture = plan.get("record_capture_contract")
    if (
        not isinstance(capture, Mapping)
        or capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("normalized_field") != "abstract"
        or capture.get("full_abstracts", {}).get("snippet_substitution") is not False
        or capture.get("source_publication_types", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("required_fields")
        != ["sourcePublicationType", "documentType"]
        or capture.get("source_publication_types", {}).get("source_filter_applied")
        is not None
    ):
        errors.append("record_capture_contract")
    translation = plan.get("translation")
    if (
        not isinstance(translation, Mapping)
        or translation.get("wildcard_family_count") != queries.FAMILY_COUNT
        or translation.get("controlled_vocabulary_supplement") is not False
        or translation.get("proximity") is not False
        or translation.get("pair_expansion") is not False
    ):
        errors.append("translation")
    try:
        expected_readiness = readiness_evidence(queries)
    except (OSError, ValueError, RuntimeError) as error:
        errors.append(f"readiness:{type(error).__name__}")
    else:
        if plan.get("readiness_evidence") != expected_readiness:
            errors.append("readiness")
    execution = plan.get("execution_policy")
    if (
        not isinstance(execution, Mapping)
        or execution.get("one_source_execution_per_partition") is not True
        or execution.get("continue_after_partition_failure") is not True
        or execution.get("retry_policy") != "none after final-plan execution begins"
        or execution.get("corrective_run_required_after_any_failure") is not True
        or execution.get("skip_full_abstracts") is not False
        or execution.get("source_publication_type_capture") is not True
        or execution.get("inter_event_delay_seconds") != INTER_EVENT_DELAY_SECONDS
    ):
        errors.append("execution_policy")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != len(PARTITIONS):
        return [*errors, "partition_coverage"]
    strategy_version = plan.get("repository_head_at_predeclaration")
    if not isinstance(strategy_version, str) or re.fullmatch(r"[0-9a-f]{40}", strategy_version) is None:
        errors.append("strategy_version")
    for index, (event, partition) in enumerate(zip(events, PARTITIONS, strict=True), start=1):
        if not isinstance(event, Mapping):
            errors.append(f"event_shape:{partition}")
            continue
        expected = plan_event(
            partition,
            queries.WILDCARD_SCHEDULE[partition],
            index,
            strategy_version if isinstance(strategy_version, str) else "",
        )
        fields = tuple(expected)
        if any(event.get(field) != expected[field] for field in fields):
            errors.append(f"event_contract:{partition}")
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


def screenshot_evidence(path: Path, receipt: Any) -> tuple[bool, list[dict[str, Any]]]:
    screenshots = receipt if isinstance(receipt, Mapping) else {}
    valid = bool(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
        and screenshots.get("same_directory_as_json") is True
    )
    rows: list[dict[str, Any]] = []
    for kind, image in screenshot_paths(path).items():
        evidence = screenshots.get(kind)
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


def record_capture_summary(rows: Any) -> tuple[bool, dict[str, Any]]:
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "source_abstract_not_available_count": 0,
            "source_publication_type_counts": {},
            "missing_source_publication_type_count": 0,
            "reviewer_publication_type_present_count": 0,
        }
    valid = True
    full_abstracts = 0
    missing_abstracts = 0
    missing_types = 0
    reviewer_codes = 0
    type_counts: Counter[str] = Counter()
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            valid = False
            continue
        abstract = row.get("abstract")
        source_type = row.get("sourcePublicationType")
        if (
            row.get("rank") != index
            or row.get("source") != SOURCE
            or not isinstance(row.get("paperId"), str)
            or not row["paperId"].isdigit()
            or not isinstance(abstract, str)
            or row.get("abstract_source") != "PQDT rendered Abstract/Details record"
            or row.get("abstract_detail_verified") is not True
            or row.get("abstract_is_truncated") is not False
        ):
            valid = False
        if abstract.strip():
            full_abstracts += 1
            if row.get("abstract_not_available") is not False:
                valid = False
        else:
            missing_abstracts += 1
            if row.get("abstract_not_available") is not True:
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
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstracts,
        "source_abstract_not_available_count": missing_abstracts,
        "source_publication_type_counts": dict(sorted(type_counts.items())),
        "missing_source_publication_type_count": missing_types,
        "reviewer_publication_type_present_count": reviewer_codes,
        "all_retained_rows_have_complete_abstract_or_explicit_source_absence": valid
        and full_abstracts + missing_abstracts == len(rows),
        "all_retained_rows_have_source_publication_type": missing_types == 0,
    }


def controls_valid(
    data: Mapping[str, Any], event: Mapping[str, Any], plan: Mapping[str, Any]
) -> bool:
    metadata = data.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    run = metadata.get("prisma_search_run")
    run = run if isinstance(run, Mapping) else {}
    strategy = run.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    sort = strategy.get("sort")
    sort = sort if isinstance(sort, Mapping) else {}
    sort_value = sort.get("value")
    sort_value = sort_value if isinstance(sort_value, Mapping) else {}
    expected_executed = f"{event['query']} AND YR({YEAR_START}-{YEAR_END}) AND LA(English)"
    frozen_controls = {
        "full_text": False,
        "exclude_duplicates": False,
        "spelling_variants": False,
        "form_variants": False,
        "show_variants": False,
    }
    return bool(
        data.get("schema_version") == "academic-search-result/v1"
        and data.get("source") == SOURCE
        and data.get("requested_query") == event.get("query")
        and data.get("executed_query") == expected_executed
        and run.get("run_id") == event.get("event_id")
        and run.get("review_id") == plan.get("review_id")
        and run.get("strategy_reference") == plan.get("strategy_reference")
        and run.get("strategy_version") == event.get("strategy_version")
        and run.get("phase") == plan.get("phase")
        and run.get("coverage", {}).get("coverage_scope") == "partition"
        and run.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and strategy.get("requested_query") == event.get("query")
        and strategy.get("executed_query") == expected_executed
        and strategy.get("executed_query_provenance") == "source_observed"
        and strategy.get("query_fields") == ["NOFT", "YR", "LA"]
        and strategy.get("search_scope") == "PQDT Global"
        and _applied(limits, "publication_date") == {"start": YEAR_START, "end": YEAR_END}
        and _applied(limits, "language") == "English"
        and _applied(limits, "publication_date_selector") == "ALL_DATES"
        and all(_applied(limits, name) == value for name, value in frozen_controls.items())
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


def strict_result_valid(data: Mapping[str, Any]) -> bool:
    metadata = data.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    run = metadata.get("prisma_search_run")
    run = run if isinstance(run, Mapping) else {}
    rows = data.get("results")
    total = data.get("total")
    if not isinstance(rows, list) or not isinstance(total, int) or isinstance(total, bool):
        return False
    identifiers = [row.get("paperId") for row in rows if isinstance(row, Mapping)]
    return bool(
        total >= 0
        and total == len(rows) == len(identifiers) == len(set(identifiers))
        and all(isinstance(identifier, str) and identifier.isdigit() for identifier in identifiers)
        and data.get("results_retrieved") == len(rows)
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and run.get("completion_status") == "complete"
        and run.get("report_ready") is True
        and run.get("report_readiness_reasons") in ([], None)
        and run.get("staged_counts", {}).get("source_reported_total") == total
        and run.get("staged_counts", {}).get("source_reported_total_exact") is True
        and run.get("staged_counts", {}).get("raw_source_records") == total
        and run.get("staged_counts", {}).get("records_exported") == total
    )


def artifact_summary(
    path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]
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
    metadata = data.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    run = metadata.get("prisma_search_run")
    run = run if isinstance(run, Mapping) else {}
    adapter = run.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    screenshots_valid, screenshots = screenshot_evidence(
        path, metadata.get("screenshots")
    )
    capture_valid, capture = record_capture_summary(data.get("results"))
    controls_ok = controls_valid(data, event, plan)
    strict_ok = strict_result_valid(data)
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    rows = data.get("results")
    identifiers = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(rows, list) else []
    return {
        "artifact_written": True,
        "valid": bool(
            controls_ok
            and strict_ok
            and adapter_ok
            and screenshots_valid
            and marker_valid(path)
            and capture_valid
        ),
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error"),
        "total": data.get("total"),
        "stable_id_count": len(identifiers),
        "stable_id_set_sha256": digest_ids(identifiers),
        "controls_valid": controls_ok,
        "strict_two_pass_valid": strict_ok,
        "adapter_binding_valid": adapter_ok,
        "screenshots_valid": screenshots_valid,
        "terminal_marker_valid": marker_valid(path),
        "record_capture_valid": capture_valid,
        "record_capture": capture,
        "screenshots": screenshots,
    }


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
        f"PQDT Global final direct discovery partition {event['partition_id']}",
    ]


def run_final(plan_path: Path, output_dir: Path, receipt_path: Path) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid final PQDT plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The final PQDT output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url) is None:
        raise ValueError("Final PQDT execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(plan["events"]):
        if index and INTER_EVENT_DELAY_SECONDS:
            time.sleep(INTER_EVENT_DELAY_SECONDS)
        output = output_dir / str(event["output_filename"])
        occupied = [output, marker_path(output), *screenshot_paths(output).values()]
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise FileExistsError(
                f"Refusing to overwrite artifacts for {event['partition_id']}"
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
            summary = artifact_summary(output, event, plan)
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
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
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
                    "total": outcome.get("total"),
                    "full_abstracts": outcome.get("record_capture", {}).get(
                        "full_abstract_count"
                    ),
                    "source_types": outcome.get("record_capture", {}).get(
                        "source_publication_type_counts"
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
        "source": plan["source"],
        "source_id": plan["source_id"],
        "review_namespace": plan["review_namespace"],
        "event_kind": "final",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": len(outcomes),
        "accepted_event_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
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
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    receipt = load(receipt_path)
    if (
        receipt.get("schema_version") != RUN_SCHEMA
        or receipt.get("plan") != relative(plan_path)
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("success") is not True
    ):
        errors.append("run_receipt")
    summaries: list[dict[str, Any]] = []
    input_paths: list[Path] = []
    all_ids: set[str] = set()
    occurrence_count = 0
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        summary = artifact_summary(output, event, plan)
        summaries.append(
            {
                "partition_id": event["partition_id"],
                "artifact": relative(output),
                **summary,
            }
        )
        if summary.get("valid") is not True:
            errors.append(f"artifact:{event['partition_id']}")
            continue
        value = load(output)
        identifiers = {str(row["paperId"]) for row in value["results"]}
        input_paths.append(output)
        all_ids.update(identifiers)
        occurrence_count += len(identifiers)
    if errors:
        result = {
            "schema_version": ASSESSMENT_SCHEMA,
            "source": SOURCE,
            "status": "failed",
            "errors": errors,
            "partitions": summaries,
        }
        write_new(assessment_path, result)
        return 1
    if union_path.exists() or union_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {union_path}")
    completed = subprocess.run(
        [
            "uv",
            "run",
            str(SOURCE_UNION_TOOL),
            "--input",
            *(str(path) for path in input_paths),
            "--output-path",
            str(union_path),
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
    if completed.returncode != 0 or not union_path.is_file():
        result = {
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
            },
            "partitions": summaries,
        }
        write_new(assessment_path, result)
        return 1
    union = load(union_path)
    if (
        union.get("schema_version") != "academic-search-source-union-receipt/v2"
        or union.get("review_namespace") != REVIEW_NAMESPACE
    ):
        errors.append("source_union_contract")
    capture_totals = {
        "full_abstract_count": sum(
            item["record_capture"]["full_abstract_count"] for item in summaries
        ),
        "source_abstract_not_available_count": sum(
            item["record_capture"]["source_abstract_not_available_count"]
            for item in summaries
        ),
        "source_publication_type_counts": dict(
            sum(
                (
                    Counter(item["record_capture"]["source_publication_type_counts"])
                    for item in summaries
                ),
                Counter(),
            )
        ),
    }
    result = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "status": "complete" if not errors else "failed",
        "errors": errors,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "source_union_receipt": relative(union_path),
        "source_union_receipt_sha256": digest(union_path),
        "partition_count": len(summaries),
        "source_occurrence_count": occurrence_count,
        "unique_numeric_pqdt_document_id_count": len(all_ids),
        "unique_numeric_pqdt_document_id_set_sha256": digest_ids(all_ids),
        "record_capture": capture_totals,
        "reviewer_publication_type_coding": "deferred to screening",
        "partitions": summaries,
    }
    write_new(assessment_path, result)
    return 0 if not errors else 1


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
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "plan":
        plan = build_plan()
        errors = validate_plan(plan, verify_bindings=True)
        if errors:
            raise ValueError("Generated PQDT plan is invalid: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=True)
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        return 0 if not errors else 1
    if args.command == "run":
        return run_final(args.plan, args.output_dir, args.receipt)
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.output_dir,
            args.source_union,
            args.output,
        )
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
