#!/usr/bin/env python3
"""Plan, run, enrich, and assess final Scopus direct searches."""

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
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
SCOPUS_ADVANCED_URL = "https://www.scopus.com/pages/search/publications?type=advanced"
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/scopus_pilot009/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/scopus/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)

PLAN_SCHEMA = "slr1-scopus-final-direct-plan/v1"
RUN_SCHEMA = "slr1-scopus-final-direct-run/v1"
ABSTRACT_PLAN_SCHEMA = "slr1-scopus-final-direct-abstract-follow-up-plan/v1"
ABSTRACT_RECEIPT_SCHEMA = "slr1-scopus-final-direct-abstract-follow-up-receipt/v1"
ABSTRACT_ENRICHMENT_SCHEMA = "slr1-scopus-final-direct-abstract-enrichment/v1"
ASSESSMENT_SCHEMA = "slr1-scopus-final-direct-assessment/v1"
RESULTS_SCHEMA = "slr1-scopus-final-direct-results-with-abstracts/v1"
STRICT_SCHEMA = "academic-search-scopus-strict-two-pass/v2"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CUTOFF_DATE = "2026-08-24"
YEAR_START = 2011
YEAR_END = 2026
PAGE_SIZE = 50
LIMIT = 1999
MAX_PAGES = 50
BATCH_SIZE = 50
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "80cc146dc25641c473e805b4d34a35dea40f6483888a4936b9f8615c1e2722af"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_ids(values: set[str]) -> str:
    result = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


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
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def repository_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise RuntimeError("Cannot determine the repository revision")
    return value


def adapter_version() -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot determine the Scopus adapter version")
    return match.group(1)


def load_queries() -> Any:
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted Scopus direct-query snapshot changed")
    spec = importlib.util.spec_from_file_location("scopus_final_direct_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted Scopus schedule changed")
    if tuple(module.WILDCARD_SCHEDULE) != PARTITIONS:
        raise RuntimeError("The wildcard schedule changed")
    return module


def bindings() -> dict[str, str]:
    paths = (SCRIPT_PATH, QUERY_SNAPSHOT, SOURCE_GUIDELINE, MAIN_PROTOCOL, DISCOVERY_PROTOCOL)
    return {relative(path): digest(path) for path in paths}


def expected_executed_query(query: str) -> str:
    return f"({query}) AND PUBYEAR > {YEAR_START - 1} AND PUBYEAR < {YEAR_END + 1}"


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def plan_event(
    partition: str,
    query: str,
    strategy_version: str,
    sequence: int,
    page_size: int,
) -> dict[str, Any]:
    return {
        "event_id": f"final-main-{partition}-scopus-{sequence:03d}",
        "partition_id": partition,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output_filename": f"{partition}.json",
        "page_size": page_size,
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": 300,
        "page_delay_seconds": 0.75,
        "require_complete": True,
        "strict_passes": 2,
        "strategy_version": strategy_version,
    }


def build_plan(
    *,
    sequence: int = 1,
    page_size: int = PAGE_SIZE,
    prior_plan: Path | None = None,
    prior_receipt: Path | None = None,
    corrective_reason: str | None = None,
) -> dict[str, Any]:
    if sequence < 1:
        raise ValueError("Final-run sequence must be positive")
    if page_size not in {10, 20, 50, 100, 200}:
        raise ValueError("Final-run page size must be one native Scopus value")
    if sequence > 1 and (prior_plan is None or prior_receipt is None):
        raise ValueError("A corrective final plan requires the superseded plan and receipt")
    queries = load_queries()
    strategy_version = repository_head()
    events = [
        plan_event(
            partition,
            queries.WILDCARD_SCHEDULE[partition],
            strategy_version,
            sequence,
            page_size,
        )
        for partition in PARTITIONS
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "source": "Scopus",
        "review_namespace": "main",
        "review_id": "slr1-1.1-restart",
        "phase": "identification",
        "strategy_reference": f"slr1-scopus-main-direct-v{sequence}",
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "cutoff": {
            "exact_common_cutoff": CUTOFF_DATE,
            "source_year_start": YEAR_START,
            "source_year_upper_bound": YEAR_END,
            "source_precision": "year",
            "screening_requirement": (
                "Screen every 2026 record against the exact common cutoff. "
                "The Scopus discovery query can apply only inclusive calendar-year bounds."
            ),
        },
        "source_configuration": {
            "result_scope": "Documents",
            "field": "TITLE-ABS-KEY",
            "sort": "Date (oldest)",
            "page_size": page_size,
            "language_facets": ["English"],
            "document_type_facets": [],
            "subject_area_controls": [],
            "access_facets": [],
            "peer_review_filter": None,
            "search_within": None,
            "full_abstracts": True,
            "abstract_recovery": (
                "Use native Show all abstracts during the first strict pass. "
                "Recover any remaining blank result through canonical EID-only queries."
            ),
        },
        "translation": {
            "population_wildcards": True,
            "wildcard_count": 10,
            "replaced_population_literals": 22,
            "literal_small_satellite_atoms": 4,
            "proximity_operators": False,
            "pair_expansion": False,
            "local_pair_filter": False,
            "term_counts": queries.TERM_COUNTS,
            "query_character_counts": {
                partition: len(queries.WILDCARD_SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "query_sha256": {
                partition: digest_text(queries.WILDCARD_SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "accepted_pilot_snapshot": relative(QUERY_SNAPSHOT),
            "accepted_pilot_snapshot_sha256": digest(QUERY_SNAPSHOT),
        },
        "strict_contract": {
            "receipt_schema": STRICT_SCHEMA,
            "membership_gate": "equal complete unique stable-ID sets",
            "required_equal_controls": [
                "source total",
                "page count",
                "page size",
                "scope",
                "Date (oldest) control",
                "English language facet",
            ],
            "order_handling": (
                "Preserve both pass-order hashes and the changed-position count. "
                "A changed stable-ID set fails."
            ),
            "automatic_screenshots_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "fresh_authorized_target_per_partition": True,
            "close_ephemeral_target_after_partition": True,
            "target_identifiers_retained": False,
            "retry_policy": "none_after_final-plan execution begins",
            "skip_full_abstracts": False,
        },
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "bindings": {"files": bindings()},
        "events": events,
    }
    if sequence > 1:
        assert prior_plan is not None and prior_receipt is not None
        if not prior_plan.is_file() or prior_plan.is_symlink():
            raise ValueError("The superseded final plan must be a regular file")
        if not prior_receipt.is_file() or prior_receipt.is_symlink():
            raise ValueError("The superseded final receipt must be a regular file")
        plan["corrective_run"] = {
            "sequence": sequence,
            "reason": corrective_reason
            or (
                "The first planned final run was interrupted when its Chrome window "
                "was closed. This clean corrective run replaces the incomplete event set."
            ),
            "superseded_plan": relative(prior_plan),
            "superseded_plan_sha256": digest(prior_plan),
            "superseded_run_receipt": relative(prior_receipt),
            "superseded_run_receipt_sha256": digest(prior_receipt),
        }
    return plan


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool = False) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    corrective = plan.get("corrective_run")
    sequence = 1 if corrective is None else corrective.get("sequence")
    if not isinstance(sequence, int) or sequence < 1:
        errors.append("sequence")
        sequence = 1
    if (
        plan.get("source") != "Scopus"
        or plan.get("review_namespace") != "main"
        or plan.get("review_id") != "slr1-1.1-restart"
        or plan.get("phase") != "identification"
        or plan.get("strategy_reference") != f"slr1-scopus-main-direct-v{sequence}"
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
    ):
        errors.append("identity")
    if sequence == 1 and corrective is not None:
        errors.append("unexpected_corrective")
    if sequence > 1 and not bool(
        isinstance(corrective, Mapping)
        and corrective.get("superseded_plan")
        and corrective.get("superseded_plan_sha256")
        and corrective.get("superseded_run_receipt")
        and corrective.get("superseded_run_receipt_sha256")
        and isinstance(corrective.get("reason"), str)
        and corrective.get("reason").strip()
    ):
        errors.append("corrective_provenance")
    cutoff = plan.get("cutoff", {})
    if (
        cutoff.get("exact_common_cutoff") != CUTOFF_DATE
        or cutoff.get("source_year_start") != YEAR_START
        or cutoff.get("source_year_upper_bound") != YEAR_END
        or cutoff.get("source_precision") != "year"
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration", {})
    configured_page_size = configuration.get("page_size")
    if (
        configuration.get("result_scope") != "Documents"
        or configuration.get("field") != "TITLE-ABS-KEY"
        or configuration.get("sort") != "Date (oldest)"
        or configured_page_size not in {10, 20, 50, 100, 200}
        or configuration.get("language_facets") != ["English"]
        or configuration.get("document_type_facets") != []
        or configuration.get("subject_area_controls") != []
        or configuration.get("access_facets") != []
        or configuration.get("peer_review_filter") is not None
        or configuration.get("search_within") is not None
        or configuration.get("full_abstracts") is not True
    ):
        errors.append("configuration")
    translation = plan.get("translation", {})
    if (
        translation.get("population_wildcards") is not True
        or translation.get("wildcard_count") != 10
        or translation.get("replaced_population_literals") != 22
        or translation.get("literal_small_satellite_atoms") != 4
        or translation.get("proximity_operators") is not False
        or translation.get("pair_expansion") is not False
    ):
        errors.append("translation")
    execution = plan.get("execution_policy", {})
    if execution.get("skip_full_abstracts") is not False:
        errors.append("abstract_policy")
    events = plan.get("events")
    if not isinstance(events, list) or [event.get("partition_id") for event in events] != list(PARTITIONS):
        errors.append("partition_coverage")
        return errors
    for event in events:
        partition = event["partition_id"]
        query = event.get("query", "")
        if (
            event.get("event_id") != f"final-main-{partition}-scopus-{sequence:03d}"
            or event.get("output_filename") != f"{partition}.json"
            or event.get("query") != queries.WILDCARD_SCHEDULE[partition]
            or event.get("query_sha256") != digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("page_size") != configured_page_size
            or event.get("limit") != LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("timeout_seconds") != 300
            or event.get("require_complete") is not True
            or event.get("strict_passes") != 2
        ):
            errors.append(f"event_contract:{partition}")
        if (
            query.count("*") != 10
            or "?" in query
            or any(marker in query.upper() for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR"))
        ):
            errors.append(f"query_translation:{partition}")
    if verify_bindings:
        for name, expected in plan.get("bindings", {}).get("files", {}).items():
            path = REPOSITORY_ROOT / name
            if not path.is_file() or digest(path) != expected:
                errors.append(f"binding_changed:{name}")
        adapter = plan.get("adapter", {})
        if (
            adapter.get("id") != "search_scopus"
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_changed")
    return errors


def committed_artifact_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not marker.is_file() or marker.is_symlink():
        return False
    try:
        receipt = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = receipt.get("normalized_json", {})
    return bool(
        normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def screenshot_evidence(path: Path, screenshots: Mapping[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    valid = True
    rows: list[dict[str, Any]] = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshots.get(key, {}) if isinstance(screenshots, Mapping) else {}
        image_valid = bool(
            image.is_file()
            and not image.is_symlink()
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
                "kind": key,
                "path": image.name,
                "sha256": digest(image) if image.is_file() else None,
                "valid": image_valid,
            }
        )
    return valid, rows


def abstract_state_valid(row: Mapping[str, Any]) -> bool:
    abstract = row.get("abstract")
    return bool(
        (
            isinstance(abstract, str)
            and bool(abstract)
            and row.get("abstract_source") == "native_scopus_result_page"
            and row.get("abstract_not_available") is False
            and row.get("abstract_detail_verified") is True
        )
        or (
            abstract in ("", None)
            and row.get("abstract_source") == "not_rendered"
            and row.get("abstract_not_available") is True
        )
    )


def controls_valid(value: Mapping[str, Any], event: Mapping[str, Any], plan: Mapping[str, Any]) -> bool:
    metadata = value.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {})
    strategy = run.get("strategy", {})
    limits = strategy.get("limits", {})
    year = limits.get("year_interval", {})
    facets = limits.get("result_facets", {})
    scope = strategy.get("search_scope", {})
    sort = strategy.get("sort", {})
    total = value.get("total")
    positive_sort = bool(
        sort.get("state") == "applied"
        and sort.get("value", {}).get("value") == "plf-t"
        and sort.get("value", {}).get("label") == "Date (oldest)"
    )
    zero_sort = total == 0 and sort.get("state") == "not_applicable"
    requested_facets = facets.get("requested")
    effective_facets = facets.get("effective")
    language = bool(
        facets.get("state") == "applied"
        and requested_facets == [{"group": "language", "value": "English"}]
        and isinstance(effective_facets, list)
        and len(effective_facets) == 1
        and effective_facets[0].get("group") == "language"
        and effective_facets[0].get("value") == "English"
    )
    return bool(
        run.get("review_id") == plan.get("review_id")
        and run.get("strategy_reference") == plan.get("strategy_reference")
        and run.get("strategy_version") == event.get("strategy_version")
        and run.get("phase") == plan.get("phase")
        and run.get("coverage", {}).get("coverage_scope") == "partition"
        and run.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and strategy.get("requested_query") == event.get("query")
        and value.get("requested_query") == event.get("query")
        and value.get("executed_query") == expected_executed_query(event.get("query", ""))
        and strategy.get("executed_query") == value.get("executed_query")
        and year.get("state") == "applied"
        and year.get("value", {}).get("start") == YEAR_START
        and year.get("value", {}).get("end") == YEAR_END
        and year.get("value", {}).get("inclusive") is True
        and limits.get("search_within", {}).get("state") == "not_applied"
        and language
        and scope.get("tab_id") == "s"
        and scope.get("label") == "Documents"
        and (positive_sort or zero_sort)
    )


def strict_receipt_valid(value: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    metadata = value.get("output_metadata", {})
    receipt = metadata.get("strict_two_pass_receipt", {})
    records = value.get("results", [])
    total = value.get("total")
    ids = [
        row.get("paperId")
        for row in records
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ]
    reports = receipt.get("pass_reports", [])
    if not isinstance(total, int) or total < 0:
        return False
    if not isinstance(reports, list) or len(reports) != 2:
        return False
    expected_pages = math.ceil(total / event["page_size"]) if total else 0
    for number, report in enumerate(reports, 1):
        if not isinstance(report, Mapping):
            return False
        if not bool(
            report.get("pass_number") == number
            and report.get("complete") is True
            and report.get("native_query_readback_observed") is True
            and report.get("source_reported_total") == total
            and report.get("source_entries_traversed") == total
            and report.get("normalized_records_retrieved") == total
            and report.get("stable_id_set_sha256") == receipt.get("stable_id_set_sha256")
        ):
            return False
        if total > 0 and not bool(
            report.get("pages_retrieved") == expected_pages
            and report.get("expected_page_count") == expected_pages
            and report.get("page_size") == event["page_size"]
            and report.get("scope_id") == "s"
            and report.get("sort_value") == "plf-t"
        ):
            return False
    return bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == "Scopus"
        and value.get("requested_query") == event.get("query")
        and total == len(records) == len(ids) == len(set(ids))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and receipt.get("schema_version") == STRICT_SCHEMA
        and receipt.get("status") == "success"
        and receipt.get("strict_completion") is True
        and receipt.get("strict_stable_id_sets_reconciled") is True
        and receipt.get("strict_record_id_sets_reconciled") is True
        and receipt.get("strict_publication_id_sets_reconciled") is True
        and receipt.get("strict_total_reconciled") is True
        and receipt.get("two_pass_set_verified") is True
        and receipt.get("two_pass_total_verified") is True
        and isinstance(receipt.get("two_pass_order_verified"), bool)
        and isinstance(receipt.get("order_difference_count"), int)
        and receipt.get("order_difference_count") >= 0
        and receipt.get("source_reported_total") == total
        and receipt.get("source_entries_retrieved") == total
        and receipt.get("records_exported") == total
        and receipt.get("stable_id_set_sha256")
        == receipt.get("record_id_set_sha256")
        == receipt.get("publication_id_set_sha256")
    )


def artifact_summary(path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]) -> dict[str, Any]:
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
    receipt = metadata.get("strict_two_pass_receipt", {})
    screenshots = metadata.get("screenshots", {})
    screenshots_ok, image_rows = screenshot_evidence(path, screenshots)
    controls_ok = controls_valid(value, event, plan)
    strict_ok = strict_receipt_valid(value, event)
    marker_ok = committed_artifact_valid(path)
    adapter = metadata.get("prisma_search_run", {}).get("adapter", {})
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    screenshot_receipt_ok = bool(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
        and screenshots_ok
    )
    records = value.get("results", [])
    abstract_capture_ok = bool(
        isinstance(records, list)
        and all(isinstance(row, Mapping) and abstract_state_valid(row) for row in records)
    )
    return {
        "valid": bool(
            controls_ok
            and strict_ok
            and adapter_ok
            and screenshot_receipt_ok
            and marker_ok
            and abstract_capture_ok
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "total": value.get("total"),
        "stable_id_count": len(
            {
                row.get("paperId")
                for row in records
                if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
            }
        ),
        "stable_id_set_sha256": receipt.get("stable_id_set_sha256"),
        "two_pass_order_verified": receipt.get("two_pass_order_verified"),
        "order_difference_count": receipt.get("order_difference_count"),
        "pass_order_hashes": [
            report.get("ordered_stable_ids_sha256")
            for report in receipt.get("pass_reports", [])
            if isinstance(report, Mapping)
        ],
        "controls_valid": controls_ok,
        "strict_v2_valid": strict_ok,
        "adapter_binding_valid": adapter_ok,
        "screenshots_valid": screenshot_receipt_ok,
        "terminal_marker_valid": marker_ok,
        "abstract_capture_observed": abstract_capture_ok,
        "full_abstract_count": sum(
            bool(row.get("abstract")) for row in records if isinstance(row, Mapping)
        ),
        "blank_abstract_count": sum(
            row.get("abstract") in ("", None)
            for row in records
            if isinstance(row, Mapping)
        ),
        "screenshots": image_rows,
    }


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def create_target(cdp_url: str, timeout_seconds: float = 45.0) -> str:
    encoded = urllib.parse.quote(SCOPUS_ADVANCED_URL, safe="")
    created = cdp_json(cdp_url, f"/json/new?{encoded}", method="PUT")
    target_id = created.get("id") if isinstance(created, Mapping) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not return one explicit Scopus target")
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
                and parsed.hostname in {"scopus.com", "www.scopus.com"}
                and "Scopus" in str(target.get("title", ""))
            ):
                return target_id
        time.sleep(0.5)
    raise RuntimeError("The fresh Scopus target did not become ready")


def close_target(cdp_url: str, target_id: str) -> bool:
    try:
        with urllib.request.urlopen(
            f"{cdp_url.rstrip('/')}/json/close/{target_id}", timeout=10
        ) as response:
            response.read()
    except Exception:
        return False
    return True


def final_command(
    event: Mapping[str, Any], output: Path, cdp_url: str, target_id: str, plan: Mapping[str, Any]
) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
        "--year-start",
        str(YEAR_START),
        "--year-end",
        str(YEAR_END),
        "--result-scope",
        "documents",
        "--language",
        "English",
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
        f"Scopus final direct discovery partition {event['partition_id']}",
    ]


def run_final(plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid final direct plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("Final Scopus output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Final Scopus execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / event["output_filename"]
        occupied = (output, *screenshot_paths(output), marker_path(output))
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise FileExistsError(f"Refusing to overwrite {event['partition_id']} artifacts")
        try:
            target_id = create_target(cdp_url)
        except Exception as error:
            outcome = {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "success": False,
                "artifact": None,
                "exit_code": None,
                "attempt_count": 0,
                "runner_failure": "ephemeral_target_creation_failed",
                "runner_failure_class": type(error).__name__,
                "source_execution_not_started": True,
                "target_identifier_retained": False,
            }
            outcomes.append(outcome)
            print(json.dumps({"partition": event["partition_id"], "success": False, "runner_failure": outcome["runner_failure"]}), flush=True)
            continue
        time.sleep(3)
        try:
            completed = subprocess.run(
                final_command(event, output, cdp_url, target_id, plan),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            exit_code: int | None = completed.returncode
            summary = artifact_summary(output, event, plan)
        except Exception as error:
            exit_code = None
            summary = {
                "valid": False,
                "artifact_written": output.is_file(),
                "runner_failure": "subprocess_or_summary_failed",
                "runner_failure_class": type(error).__name__,
            }
        finally:
            target_closed = close_target(cdp_url, target_id)
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            "ephemeral_target_created": True,
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
                    "abstracts": outcome.get("full_abstract_count"),
                    "blank_abstracts": outcome.get("blank_abstract_count"),
                    "strict_v2_valid": outcome.get("strict_v2_valid"),
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
        "source": "Scopus",
        "review_namespace": "main",
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
        "source_command_attempt_count": sum(outcome.get("attempt_count", 0) for outcome in outcomes),
        "accepted_event_count": sum(outcome.get("success") is True for outcome in outcomes),
        "all_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def source_records(input_dir: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, list[str]]]:
    records: dict[str, dict[str, Any]] = {}
    artifacts: list[dict[str, Any]] = []
    discovery_partitions: dict[str, list[str]] = {}
    for partition in PARTITIONS:
        path = input_dir / f"{partition}.json"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing regular final Scopus artifact: {path}")
        value = load(path)
        metadata = value.get("output_metadata", {})
        rows = value.get("results")
        if (
            value.get("schema_version") != "academic-search-result/v1"
            or metadata.get("merge_eligible") is not True
            or not isinstance(rows, list)
        ):
            raise ValueError(f"Scopus artifact is not a final merge input: {path}")
        artifacts.append(
            {
                "partition_id": partition,
                "path": relative(path),
                "sha256": digest(path),
                "record_count": len(rows),
            }
        )
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Malformed Scopus row in {path}")
            paper_id = row.get("paperId")
            if not isinstance(paper_id, str) or not paper_id.startswith("SCOPUS-PUBLICATION:"):
                raise ValueError(f"Invalid Scopus publication ID in {path}")
            discovery_partitions.setdefault(paper_id, []).append(partition)
            current = records.get(paper_id)
            if current is None or len(str(row.get("abstract") or "")) > len(str(current.get("abstract") or "")):
                records[paper_id] = row
    return records, artifacts, discovery_partitions


def eid_query(ids: list[str]) -> str:
    values = ["2-s2.0-" + identifier.removeprefix("SCOPUS-PUBLICATION:") for identifier in ids]
    return "EID(" + " OR ".join(values) + ")"


def build_abstract_plan(input_dir: Path) -> dict[str, Any]:
    records, artifacts, _ = source_records(input_dir)
    requested = sorted(identifier for identifier, row in records.items() if not row.get("abstract"))
    batches = [requested[index : index + BATCH_SIZE] for index in range(0, len(requested), BATCH_SIZE)]
    return {
        "schema_version": ABSTRACT_PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": "Scopus",
        "review_namespace": "main",
        "purpose": "metadata_enrichment_only",
        "discovery_ids_may_be_added": False,
        "input_directory": relative(input_dir),
        "input_artifacts": artifacts,
        "accepted_final_id_count": len(records),
        "accepted_final_id_set_sha256": digest_ids(set(records)),
        "already_recovered_abstract_count": sum(bool(row.get("abstract")) for row in records.values()),
        "requested_record_count": len(requested),
        "requested_id_set_sha256": digest_ids(set(requested)),
        "batch_size": BATCH_SIZE,
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "runner": {"path": relative(SCRIPT_PATH), "sha256": digest(SCRIPT_PATH)},
        "settings": {
            "query": "canonical EID only",
            "year_bounds": None,
            "facets": [],
            "search_within": None,
            "result_scope": "Documents",
            "page_size": PAGE_SIZE,
            "max_pages": 1,
            "full_abstracts": True,
            "strict_passes": 2,
        },
        "batches": [
            {
                "batch": index,
                "event_id": f"final-main-scopus-abstract-follow-up-001-{index:03d}",
                "output_filename": f"batch-{index:03d}.json",
                "requested_ids": ids,
                "requested_id_set_sha256": digest_ids(set(ids)),
                "query": eid_query(ids),
            }
            for index, ids in enumerate(batches, start=1)
        ],
    }


def validate_abstract_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> None:
    if plan.get("schema_version") != ABSTRACT_PLAN_SCHEMA:
        raise ValueError("Unexpected abstract follow-up plan schema")
    batches = plan.get("batches")
    if not isinstance(batches, list):
        raise ValueError("Abstract follow-up plan has no batch list")
    requested: list[str] = []
    for index, batch in enumerate(batches, start=1):
        if not isinstance(batch, Mapping):
            raise ValueError(f"Malformed abstract follow-up batch {index}")
        ids = batch.get("requested_ids")
        if not isinstance(ids, list) or not 1 <= len(ids) <= BATCH_SIZE:
            raise ValueError(f"Invalid abstract follow-up batch IDs {index}")
        if (
            len(ids) != len(set(ids))
            or batch.get("batch") != index
            or batch.get("event_id") != f"final-main-scopus-abstract-follow-up-001-{index:03d}"
            or batch.get("output_filename") != f"batch-{index:03d}.json"
            or batch.get("requested_id_set_sha256") != digest_ids(set(ids))
            or batch.get("query") != eid_query(ids)
        ):
            raise ValueError(f"Invalid abstract follow-up batch {index}")
        requested.extend(ids)
    if (
        len(requested) != len(set(requested))
        or len(requested) != plan.get("requested_record_count")
        or digest_ids(set(requested)) != plan.get("requested_id_set_sha256")
    ):
        raise ValueError("Abstract follow-up requested-ID ledger changed")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        runner = plan.get("runner", {})
        if (
            adapter.get("id") != "search_scopus"
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
            or runner.get("sha256") != digest(SCRIPT_PATH)
        ):
            raise ValueError("Abstract follow-up implementation changed")
        input_dir = REPOSITORY_ROOT / str(plan.get("input_directory", ""))
        records, artifacts, _ = source_records(input_dir)
        if (
            artifacts != plan.get("input_artifacts")
            or len(records) != plan.get("accepted_final_id_count")
            or digest_ids(set(records)) != plan.get("accepted_final_id_set_sha256")
        ):
            raise ValueError("Abstract follow-up input artifacts changed")


def abstract_command(
    plan: Mapping[str, Any], batch: Mapping[str, Any], output: Path, cdp_url: str, target_id: str
) -> list[str]:
    ids = batch["requested_ids"]
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(batch["query"]),
        "--result-scope",
        "documents",
        "--page-size",
        str(PAGE_SIZE),
        "--limit",
        str(len(ids)),
        "--max-pages",
        "1",
        "--timeout",
        "300",
        "--page-delay-seconds",
        "0",
        "--require-complete",
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
        "--output-path",
        str(output),
        "--prisma-run-id",
        str(batch["event_id"]),
        "--prisma-review-id",
        "slr1-1.1-restart",
        "--prisma-strategy-reference",
        "slr1-scopus-main-abstract-follow-up-v1",
        "--prisma-strategy-version",
        str(plan["adapter"]["sha256"]),
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        f"ABSTRACT-FOLLOW-UP-{batch['batch']:03d}",
        "--prisma-partition-label",
        f"ABSTRACT-FOLLOW-UP-{batch['batch']:03d}",
        "--prisma-partition-description",
        "Canonical EID-only metadata enrichment for accepted final Scopus direct records",
    ]


def inspect_abstract_artifact(path: Path, batch: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"accepted": False, "artifact_written": False}
    value = load(path)
    rows = value.get("results")
    metadata = value.get("output_metadata", {})
    ids = [row.get("paperId") for row in rows] if isinstance(rows, list) else []
    receipt = metadata.get("strict_two_pass_receipt", {})
    screenshots_ok, _ = screenshot_evidence(path, metadata.get("screenshots", {}))
    abstract_capture_ok = bool(
        isinstance(rows, list)
        and all(isinstance(row, Mapping) and abstract_state_valid(row) for row in rows)
    )
    accepted = bool(
        value.get("total") == len(batch["requested_ids"])
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and receipt.get("schema_version") == STRICT_SCHEMA
        and receipt.get("strict_completion") is True
        and receipt.get("two_pass_set_verified") is True
        and len(ids) == len(set(ids))
        and set(ids) == set(batch["requested_ids"])
        and screenshots_ok
        and committed_artifact_valid(path)
        and abstract_capture_ok
    )
    return {
        "accepted": accepted,
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "total": value.get("total"),
        "returned_id_set_sha256": digest_ids(set(identifier for identifier in ids if isinstance(identifier, str))),
        "full_abstract_count": sum(bool(row.get("abstract")) for row in rows if isinstance(row, Mapping)) if isinstance(rows, list) else 0,
        "blank_abstract_count": sum(row.get("abstract") in ("", None) for row in rows if isinstance(row, Mapping)) if isinstance(rows, list) else 0,
        "abstract_capture_valid": abstract_capture_ok,
        "screenshots_valid": screenshots_ok,
        "terminal_marker_valid": committed_artifact_valid(path),
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
    }


def run_abstract_plan(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    enrichment_path: Path,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink() or enrichment_path.exists() or enrichment_path.is_symlink():
        raise FileExistsError("Refusing to overwrite abstract follow-up artifacts")
    plan = load(plan_path)
    validate_abstract_plan(plan, verify_bindings=True)
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"Refusing to reuse {output_dir}")
    output_dir.mkdir(parents=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Scopus abstract recovery requires a loopback browser endpoint")
    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, batch in enumerate(plan["batches"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / batch["output_filename"]
        target_id: str | None = None
        exit_code: int | None = None
        target_closed = False
        try:
            target_id = create_target(cdp_url)
            completed = subprocess.run(
                abstract_command(plan, batch, output, cdp_url, target_id),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            exit_code = completed.returncode
            inspected = inspect_abstract_artifact(output, batch)
        except Exception as error:
            inspected = {
                "accepted": False,
                "artifact_written": output.is_file(),
                "runner_failure": type(error).__name__,
            }
        finally:
            if target_id is not None:
                target_closed = close_target(cdp_url, target_id)
        outcome = {
            "batch": batch["batch"],
            "event_id": batch["event_id"],
            "requested_record_count": len(batch["requested_ids"]),
            "requested_id_set_sha256": batch["requested_id_set_sha256"],
            "output": batch["output_filename"] if output.is_file() else None,
            "exit_code": exit_code,
            "target_identifier_retained": False,
            "target_close_requested": target_closed,
            **inspected,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "batch": batch["batch"],
                    "accepted": outcome["accepted"],
                    "total": outcome.get("total"),
                    "abstracts": outcome.get("full_abstract_count"),
                    "blank_abstracts": outcome.get("blank_abstract_count"),
                }
            ),
            flush=True,
        )
    complete = all(outcome["accepted"] for outcome in outcomes)
    if complete:
        enrichment_rows: list[dict[str, Any]] = []
        for batch, outcome in zip(plan["batches"], outcomes):
            path = output_dir / batch["output_filename"]
            for row in load(path)["results"]:
                enrichment_rows.append(
                    {
                        "paper_id": row["paperId"],
                        "abstract": row.get("abstract") or None,
                        "abstract_not_available": row.get("abstract_not_available"),
                        "abstract_source": row.get("abstract_source"),
                        "abstract_detail_verified": row.get("abstract_detail_verified"),
                        "follow_up_event_id": batch["event_id"],
                        "follow_up_artifact": relative(path),
                        "follow_up_artifact_sha256": outcome["artifact_sha256"],
                    }
                )
        if len(enrichment_rows) != plan["requested_record_count"]:
            raise ValueError("Abstract enrichment row count changed")
        enrichment = {
            "schema_version": ABSTRACT_ENRICHMENT_SCHEMA,
            "source": "Scopus",
            "review_namespace": "main",
            "purpose": "metadata_enrichment_only",
            "plan": relative(plan_path),
            "plan_sha256": digest(plan_path),
            "complete": True,
            "requested_record_count": plan["requested_record_count"],
            "full_abstract_count": sum(bool(row["abstract"]) for row in enrichment_rows),
            "blank_abstract_count": sum(not row["abstract"] for row in enrichment_rows),
            "records": sorted(enrichment_rows, key=lambda row: row["paper_id"]),
        }
        write_new(enrichment_path, enrichment)
    receipt = {
        "schema_version": ABSTRACT_RECEIPT_SCHEMA,
        "source": "Scopus",
        "review_namespace": "main",
        "purpose": "metadata_enrichment_only",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "started_from_accepted_final_id_count": plan["accepted_final_id_count"],
        "requested_record_count": plan["requested_record_count"],
        "attempted_batch_count": len(outcomes),
        "accepted_batch_count": sum(outcome["accepted"] for outcome in outcomes),
        "complete": complete,
        "discovery_ids_added": 0,
        "target_identifier_retained": False,
        "enrichment": relative(enrichment_path) if complete else None,
        "enrichment_sha256": digest(enrichment_path) if complete else None,
        "outcomes": outcomes,
        "started_at_utc": started,
        "completed_at_utc": now(),
    }
    write_new(receipt_path, receipt)
    return 0 if complete else 1


def source_union_command(artifacts: list[Path], output: Path) -> list[str]:
    return [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *(str(path) for path in artifacts),
        "--output-path",
        str(output),
        "--expected-partitions",
        *PARTITIONS,
        "--expected-sources",
        "scopus",
        "--review-namespace",
        "main",
    ]


def build_results_with_abstracts(
    records: Mapping[str, Mapping[str, Any]],
    discovery_partitions: Mapping[str, list[str]],
    abstracts: Mapping[str, str],
    output: Path,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for paper_id in sorted(records):
        record = dict(records[paper_id])
        abstract = abstracts.get(paper_id)
        if abstract:
            record["abstract"] = abstract
            record["abstract_not_available"] = False
            record["abstract_source"] = "native_scopus_result_page"
            record["abstract_detail_verified"] = True
        record["discovery_partitions"] = sorted(set(discovery_partitions[paper_id]))
        rows.append(record)
    result = {
        "schema_version": RESULTS_SCHEMA,
        "source": "Scopus",
        "review_namespace": "main",
        "purpose": "deduplicated_final_direct_records_with_abstracts",
        "record_count": len(rows),
        "records_with_full_abstract": sum(bool(row.get("abstract")) for row in rows),
        "records_without_full_abstract": sum(not bool(row.get("abstract")) for row in rows),
        "complete": all(bool(row.get("abstract")) for row in rows),
        "records": rows,
    }
    write_new(output, result)
    return result


def assess(
    plan_path: Path,
    run_receipt_path: Path,
    output_dir: Path,
    source_union_path: Path,
    abstract_plan_path: Path,
    abstract_receipt_path: Path,
    enrichment_path: Path,
    results_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink() or results_path.exists() or results_path.is_symlink():
        raise FileExistsError("Refusing to overwrite final assessment artifacts")
    plan = load(plan_path)
    run = load(run_receipt_path)
    source_union = load(source_union_path)
    abstract_plan = load(abstract_plan_path)
    abstract_receipt = load(abstract_receipt_path)
    enrichment = load(enrichment_path)
    errors = validate_plan(plan, verify_bindings=False)
    if run.get("schema_version") != RUN_SCHEMA or run.get("plan_sha256") != digest(plan_path):
        errors.append("run_receipt")
    if run.get("success") is not True or run.get("accepted_event_count") != len(PARTITIONS):
        errors.append("run_completion")
    if abstract_plan.get("schema_version") != ABSTRACT_PLAN_SCHEMA:
        errors.append("abstract_plan_schema")
    if abstract_receipt.get("schema_version") != ABSTRACT_RECEIPT_SCHEMA or abstract_receipt.get("complete") is not True:
        errors.append("abstract_receipt")
    if enrichment.get("schema_version") != ABSTRACT_ENRICHMENT_SCHEMA or enrichment.get("complete") is not True:
        errors.append("abstract_enrichment")

    events = {event["partition_id"]: event for event in plan.get("events", [])}
    outcomes = {outcome["partition_id"]: outcome for outcome in run.get("outcomes", [])}
    if set(events) != set(PARTITIONS) or set(outcomes) != set(PARTITIONS):
        errors.append("partition_coverage")

    records, artifacts, discovery_partitions = source_records(output_dir)
    raw_event_count = sum(item["record_count"] for item in artifacts)
    direct_abstracts = {
        paper_id: str(row.get("abstract"))
        for paper_id, row in records.items()
        if isinstance(row.get("abstract"), str) and row.get("abstract")
    }
    direct_missing = set(records) - set(direct_abstracts)
    event_evidence: list[dict[str, Any]] = []
    cutoff_year_records = 0
    for partition in PARTITIONS:
        event = events.get(partition)
        outcome = outcomes.get(partition)
        path = output_dir / f"{partition}.json"
        if event is None or outcome is None:
            continue
        summary = artifact_summary(path, event, plan)
        value = load(path)
        strict = value.get("output_metadata", {}).get("strict_two_pass_receipt", {})
        rows = value.get("results", [])
        if outcome.get("success") is not True or summary.get("valid") is not True:
            errors.append(f"event:{partition}")
        if outcome.get("artifact_sha256") != digest(path) or outcome.get("artifact_bytes") != path.stat().st_size:
            errors.append(f"artifact_binding:{partition}")
        cutoff_year_records += sum(
            isinstance(row, Mapping) and row.get("year") == YEAR_END for row in rows
        )
        event_evidence.append(
            {
                "partition_id": partition,
                "artifact": path.name,
                "artifact_sha256": digest(path),
                "source_total": value.get("total"),
                "stable_id_count": len({row.get("paperId") for row in rows if isinstance(row, Mapping)}),
                "stable_id_set_sha256": strict.get("stable_id_set_sha256"),
                "pass_page_counts": [
                    report.get("pages_retrieved")
                    for report in strict.get("pass_reports", [])
                    if isinstance(report, Mapping)
                ],
                "pass_order_hashes": summary.get("pass_order_hashes"),
                "two_pass_order_verified": strict.get("two_pass_order_verified"),
                "order_difference_count": strict.get("order_difference_count"),
                "direct_run_full_abstract_count": summary.get("full_abstract_count"),
                "blank_abstract_count_before_follow_up": summary.get("blank_abstract_count"),
            }
        )

    enrichment_rows = enrichment.get("records", [])
    enriched: dict[str, str] = {}
    enrichment_ids: set[str] = set()
    if not isinstance(enrichment_rows, list):
        errors.append("enrichment_rows")
        enrichment_rows = []
    for row in enrichment_rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("paper_id"), str):
            errors.append("enrichment_row")
            continue
        paper_id = row["paper_id"]
        if paper_id in enrichment_ids:
            errors.append("enrichment_duplicate")
            continue
        enrichment_ids.add(paper_id)
        abstract = row.get("abstract")
        if isinstance(abstract, str) and abstract:
            enriched[paper_id] = abstract
        elif abstract is not None:
            errors.append("enrichment_row")
    if enrichment_ids != direct_missing:
        errors.append("enrichment_coverage")
    abstracts = {**direct_abstracts, **enriched}
    all_ids = set(records)
    if set(abstracts) != all_ids:
        errors.append("abstracts_incomplete")
    if abstract_plan.get("accepted_final_id_set_sha256") != digest_ids(all_ids):
        errors.append("abstract_plan_input")
    if abstract_plan.get("requested_id_set_sha256") != digest_ids(direct_missing):
        errors.append("abstract_plan_coverage")

    source_section = source_union.get("source_unions", {}).get("scopus", {})
    union_valid = bool(
        source_union.get("review_namespace") == "main"
        and source_union.get("review_id") == plan.get("review_id")
        and source_union.get("strategy_reference") == plan.get("strategy_reference")
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == ["scopus"]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and source_section.get("event_total_sum") == raw_event_count
        and set(source_section.get("stable_record_ids", [])) == all_ids
        and source_section.get("raw_record_count") == raw_event_count
    )
    if not union_valid:
        errors.append("source_union")

    results = build_results_with_abstracts(records, discovery_partitions, abstracts, results_path)
    complete = bool(
        len(event_evidence) == len(PARTITIONS)
        and results["complete"] is True
        and not errors
    )
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": "Scopus",
        "review_namespace": "main",
        "event_kind": "final",
        "plan": plan_path.name,
        "plan_sha256": digest(plan_path),
        "run_receipt": run_receipt_path.name,
        "run_receipt_sha256": digest(run_receipt_path),
        "source_union": source_union_path.name,
        "source_union_sha256": digest(source_union_path),
        "abstract_plan": relative(abstract_plan_path),
        "abstract_plan_sha256": digest(abstract_plan_path),
        "abstract_receipt": relative(abstract_receipt_path),
        "abstract_receipt_sha256": digest(abstract_receipt_path),
        "abstract_enrichment": relative(enrichment_path),
        "abstract_enrichment_sha256": digest(enrichment_path),
        "results_with_abstracts": results_path.name,
        "results_with_abstracts_sha256": digest(results_path),
        "adapter": plan.get("adapter"),
        "accepted_source_event_count": len(event_evidence),
        "events": event_evidence,
        "stable_id_union": {
            "source_event_record_count": raw_event_count,
            "unique_stable_id_count": len(all_ids),
            "cross_partition_duplicate_occurrences": raw_event_count - len(all_ids),
            "stable_id_set_sha256": digest_ids(all_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "cutoff_screening": {
            "common_evidence_cutoff": CUTOFF_DATE,
            "source_year_start": YEAR_START,
            "source_year_upper_bound": YEAR_END,
            "source_precision": "year",
            "records_in_cutoff_year_requiring_exact_date_screening": cutoff_year_records,
            "status": "pending_screening",
        },
        "abstract_recovery": {
            "discovery_events_requested_full_abstracts": True,
            "unique_records_with_full_abstract": len(abstracts),
            "unique_records_without_full_abstract": len(all_ids - set(abstracts)),
            "direct_run_full_abstract_count": len(direct_abstracts),
            "follow_up_record_count": len(enrichment_ids),
            "follow_up_full_abstract_count": len(enriched),
            "follow_up_coverage_complete": enrichment_ids == direct_missing,
            "results_with_abstracts_complete": results["complete"],
            "status": "complete" if results["complete"] else "failed",
        },
        "source_union_valid": union_valid,
        "final_search_partitions_complete": complete,
        "status": "passed" if complete else "failed",
        "errors": errors,
    }
    write_new(output, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "source_totals": {item["partition_id"]: item["source_total"] for item in event_evidence},
                "stable_id_union": len(all_ids),
                "abstract_count": len(abstracts),
            }
        )
    )
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--sequence", type=int, default=1)
    plan_parser.add_argument("--page-size", type=int, default=PAGE_SIZE)
    plan_parser.add_argument("--prior-plan", type=Path)
    plan_parser.add_argument("--corrective-reason")
    plan_parser.add_argument("--prior-receipt", type=Path)
    check_parser = commands.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=5.0)
    abstract_plan_parser = commands.add_parser("abstract-plan")
    abstract_plan_parser.add_argument("--input-dir", type=Path, required=True)
    abstract_plan_parser.add_argument("--output", type=Path, required=True)
    abstract_run_parser = commands.add_parser("abstract-run")
    abstract_run_parser.add_argument("--plan", type=Path, required=True)
    abstract_run_parser.add_argument("--output-dir", type=Path, required=True)
    abstract_run_parser.add_argument("--receipt", type=Path, required=True)
    abstract_run_parser.add_argument("--enrichment", type=Path, required=True)
    abstract_run_parser.add_argument("--settle-seconds", type=float, default=5.0)
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--run-receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--abstract-plan", type=Path, required=True)
    assess_parser.add_argument("--abstract-receipt", type=Path, required=True)
    assess_parser.add_argument("--enrichment", type=Path, required=True)
    assess_parser.add_argument("--results-with-abstracts", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "plan":
        plan = build_plan(
            sequence=args.sequence,
            page_size=args.page_size,
            prior_plan=args.prior_plan,
            prior_receipt=args.prior_receipt,
            corrective_reason=args.corrective_reason,
        )
        errors = validate_plan(plan)
        if errors:
            raise ValueError("Invalid generated plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"status": "saved", "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=True)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        return run_final(args.plan, args.output_dir, args.receipt, args.settle_seconds)
    if args.command == "abstract-plan":
        plan = build_abstract_plan(args.input_dir.resolve(strict=True))
        validate_abstract_plan(plan, verify_bindings=False)
        write_new(args.output, plan)
        print(json.dumps({"status": "saved", "requested_records": plan["requested_record_count"], "batches": len(plan["batches"])}))
        return 0
    if args.command == "abstract-run":
        return run_abstract_plan(
            args.plan.resolve(strict=True),
            args.output_dir.resolve(strict=False),
            args.receipt.resolve(strict=False),
            args.enrichment.resolve(strict=False),
            args.settle_seconds,
        )
    return assess(
        args.plan.resolve(strict=True),
        args.run_receipt.resolve(strict=True),
        args.output_dir.resolve(strict=True),
        args.source_union.resolve(strict=True),
        args.abstract_plan.resolve(strict=True),
        args.abstract_receipt.resolve(strict=True),
        args.enrichment.resolve(strict=True),
        args.results_with_abstracts.resolve(strict=False),
        args.output.resolve(strict=False),
    )


if __name__ == "__main__":
    raise SystemExit(main())
