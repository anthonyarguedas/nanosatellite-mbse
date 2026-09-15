#!/usr/bin/env python3
"""Plan, execute, and assess final NASA NTRS direct searches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ntrs.py"
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot005/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/nasa-ntrs/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)

PLAN_SCHEMA = "slr1-ntrs-final-direct-plan/v1"
RUN_SCHEMA = "slr1-ntrs-final-direct-run/v1"
ASSESSMENT_SCHEMA = "slr1-ntrs-final-direct-assessment/v1"
SCREENSHOT_SCHEMA = "ntrs-automatic-screenshots/v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "53dd5b38a1c3777b88d089e19220a715bb35eb7bbc0ecd0fd43fd73022bb53bc"
)
CUTOFF_START = "2011-01-01"
CUTOFF_END = "2026-08-24"
PAGE_SIZE = 100
LIMIT = 10000
MAX_PAGES = 100
TIMEOUT_SECONDS = 300


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
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def repository_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
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
        raise RuntimeError("Cannot determine the NTRS adapter version")
    return match.group(1)


def load_queries() -> Any:
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted NTRS query snapshot changed")
    spec = importlib.util.spec_from_file_location(
        "ntrs_final_direct_queries", QUERY_SNAPSHOT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted NTRS partition schedule changed")
    if tuple(module.WILDCARD_SCHEDULE) != PARTITIONS:
        raise RuntimeError("The accepted NTRS wildcard schedule changed")
    return module


def binding_paths() -> tuple[Path, ...]:
    return (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )


def build_plan() -> dict[str, Any]:
    queries = load_queries()
    strategy_version = repository_head()
    events = []
    for index, partition in enumerate(PARTITIONS, start=1):
        query = queries.WILDCARD_SCHEDULE[partition]
        events.append(
            {
                "event_id": f"final-main-{partition}-ntrs-{index:03d}",
                "partition_id": partition,
                "query": query,
                "query_sha256": digest_text(query),
                "query_characters": len(query),
                "wildcard_count": query.count("*"),
                "output_filename": f"{partition}.json",
                "page_size": PAGE_SIZE,
                "limit": LIMIT,
                "max_pages": MAX_PAGES,
                "timeout_seconds": TIMEOUT_SECONDS,
                "require_complete": True,
                "strict_passes": 2,
                "full_abstracts": True,
                "source_document_types": True,
                "strategy_version": strategy_version,
            }
        )
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "source": "NASA Technical Reports Server (NTRS)",
        "source_id": "nasa_ntrs",
        "review_namespace": "main",
        "review_id": "slr1-1.1-restart",
        "phase": "identification",
        "strategy_reference": "slr1-ntrs-main-direct-v1",
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "date_window": {
            "publication_date_start": CUTOFF_START,
            "publication_date_end": CUTOFF_END,
            "inclusive": True,
            "source_precision": "calendar_day",
        },
        "source_configuration": {
            "source_or_collection": "full public NTRS database",
            "field": "general q over metadata and indexed document text",
            "sort": "Publication Date (Oldest)",
            "page_size": PAGE_SIZE,
            "language_filter": None,
            "document_type_filter": None,
            "other_filters": None,
            "controlled_vocabulary_supplement": None,
            "full_abstracts": True,
            "source_document_types": True,
            "detail_capture": (
                "Visit each canonical rendered citation page and retain its complete "
                "visible abstract and visible source document type assignment."
            ),
        },
        "translation": {
            "boolean": "+ for AND, | for OR, with explicit parentheses",
            "proximity": False,
            "pair_expansion": False,
            "wildcard_atom_count": queries.WILDCARD_ATOM_COUNT,
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "phrase_wildcards": False,
            "acronym_wildcards": False,
            "accepted_query_snapshot": relative(QUERY_SNAPSHOT),
            "accepted_query_snapshot_sha256": digest(QUERY_SNAPSHOT),
        },
        "strict_contract": {
            "complete_rendered_passes": 2,
            "stable_pre_submit_state": True,
            "stable_changed_post_submit_state": True,
            "matching_totals_ranges_controls_and_ordered_ids": True,
            "automatic_screenshots_required": True,
            "successful_detail_page_required_for_every_retained_record": True,
        },
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "retry_policy": "none within this final plan",
            "failed_events_are_nonmergeable": True,
            "corrective_run_required_after_any_failure": True,
            "skip_full_abstracts": False,
        },
        "adapter": {
            "id": "search_ntrs",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
            "detail_projection": {
                "abstract_field": "abstract",
                "document_type_field": "documentType",
                "document_type_list_field": "documentTypes",
            },
        },
        "bindings": {
            "files": {relative(path): digest(path) for path in binding_paths()}
        },
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source_id") != "nasa_ntrs"
        or plan.get("review_namespace") != "main"
        or plan.get("review_id") != "slr1-1.1-restart"
        or plan.get("phase") != "identification"
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
    ):
        errors.append("identity")
    window = plan.get("date_window", {})
    if (
        window.get("publication_date_start") != CUTOFF_START
        or window.get("publication_date_end") != CUTOFF_END
        or window.get("inclusive") is not True
        or window.get("source_precision") != "calendar_day"
    ):
        errors.append("date_window")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("source_or_collection") != "full public NTRS database"
        or configuration.get("field")
        != "general q over metadata and indexed document text"
        or configuration.get("language_filter") is not None
        or configuration.get("document_type_filter") is not None
        or configuration.get("other_filters") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
        or configuration.get("full_abstracts") is not True
        or configuration.get("source_document_types") is not True
    ):
        errors.append("source_configuration")
    execution = plan.get("execution_policy", {})
    if execution.get("skip_full_abstracts") is not False:
        errors.append("abstract_policy")
    events = plan.get("events")
    if not isinstance(events, list) or [
        event.get("partition_id") for event in events if isinstance(event, Mapping)
    ] != list(PARTITIONS):
        errors.append("partition_coverage")
        return errors
    for index, event in enumerate(events, start=1):
        partition = event.get("partition_id")
        query = event.get("query")
        if (
            not isinstance(partition, str)
            or not isinstance(query, str)
            or query != queries.WILDCARD_SCHEDULE.get(partition)
            or event.get("event_id") != f"final-main-{partition}-ntrs-{index:03d}"
            or event.get("query_sha256") != digest_text(query)
            or event.get("query_characters") != len(query)
            or event.get("wildcard_count") != query.count("*")
            or event.get("output_filename") != f"{partition}.json"
            or event.get("page_size") != PAGE_SIZE
            or event.get("limit") != LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("timeout_seconds") != TIMEOUT_SECONDS
            or event.get("require_complete") is not True
            or event.get("strict_passes") != 2
            or event.get("full_abstracts") is not True
            or event.get("source_document_types") is not True
        ):
            errors.append(f"event_contract:{partition}")
        if any(token in query.upper() for token in (" NEAR", " W/", " PRE/")):
            errors.append(f"query_translation:{partition}")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        if (
            adapter.get("id") != "search_ntrs"
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_changed")
        for name, expected in plan.get("bindings", {}).get("files", {}).items():
            path = REPOSITORY_ROOT / name
            if not path.is_file() or path.is_symlink() or digest(path) != expected:
                errors.append(f"binding_changed:{name}")
    return errors


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.NTRS_COMMIT.json")


def screenshot_paths(path: Path) -> dict[str, Path]:
    return {
        "search_page": path.with_name(f"{path.stem}.search-page.png"),
        "results_page": path.with_name(f"{path.stem}.results-page.png"),
    }


def artifact_summary(
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
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    prisma = (
        metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    )
    strategy = prisma.get("strategy", {}) if isinstance(prisma, Mapping) else {}
    limits = strategy.get("limits", {}) if isinstance(strategy, Mapping) else {}
    publication = (
        limits.get("publication_date", {}) if isinstance(limits, Mapping) else {}
    )
    normalized = (
        metadata.get("normalized_export", {}) if isinstance(metadata, Mapping) else {}
    )
    reconciliation = (
        normalized.get("count_reconciliation", {})
        if isinstance(normalized, Mapping)
        else {}
    )
    ids = (
        [
            row.get("paperId")
            for row in records
            if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
        ]
        if isinstance(records, list)
        else []
    )

    abstract_capture = []
    type_capture = []
    if isinstance(records, list):
        for row in records:
            if not isinstance(row, Mapping):
                abstract_capture.append(False)
                type_capture.append(False)
                continue
            abstract = row.get("abstract")
            abstract_capture.append(
                bool(
                    isinstance(abstract, str)
                    and (
                        (
                            bool(abstract)
                            and row.get("abstract_source")
                            == "matching_rendered_citation_page"
                            and row.get("abstract_not_available") is False
                        )
                        or (
                            not abstract
                            and row.get("abstract_source") == "not_available"
                            and row.get("abstract_not_available") is True
                        )
                    )
                )
            )
            document_types = row.get("documentTypes")
            expected_document_type = (
                "; ".join(document_types)
                if isinstance(document_types, list)
                and all(isinstance(item, str) and item for item in document_types)
                else ""
            )
            type_capture.append(
                bool(
                    isinstance(document_types, list)
                    and len(document_types) == len(set(document_types))
                    and row.get("documentType") == expected_document_type
                    and (
                        (
                            bool(document_types)
                            and row.get("document_type_source")
                            == "matching_rendered_citation_page"
                            and row.get("document_type_not_available") is False
                        )
                        or (
                            not document_types
                            and row.get("document_type_source") == "not_available"
                            and row.get("document_type_not_available") is True
                        )
                    )
                )
            )

    screenshot_receipt = (
        metadata.get("screenshots", {}) if isinstance(metadata, Mapping) else {}
    )
    screenshot_rows = []
    for key, image in screenshot_paths(path).items():
        receipt = (
            screenshot_receipt.get(key, {})
            if isinstance(screenshot_receipt, Mapping)
            else {}
        )
        valid_image = bool(
            image.is_file()
            and not image.is_symlink()
            and receipt.get("path") == image.name
            and receipt.get("sha256") == digest(image)
            and isinstance(receipt.get("width"), int)
            and receipt["width"] > 0
            and isinstance(receipt.get("height"), int)
            and receipt["height"] > 0
        )
        screenshot_rows.append(
            {
                "kind": key,
                "path": image.name,
                "sha256": digest(image) if image.is_file() else None,
                "valid": valid_image,
            }
        )
    marker_file = marker_path(path)
    marker = (
        load(marker_file)
        if marker_file.is_file() and not marker_file.is_symlink()
        else {}
    )
    marker_valid = bool(
        marker.get("schema") == "ntrs_output_commit_marker_v1"
        and marker.get("normalized_json", {}).get("sha256") == digest(path)
        and marker.get("normalized_json", {}).get("bytes") == path.stat().st_size
    )
    filters_empty = all(
        limits.get(key, {}).get("state") == "not_applied"
        for key in (
            "acquired_date",
            "title",
            "author",
            "organization",
            "document_type",
            "center",
            "subject",
            "report_number",
            "funding_number",
            "keyword",
            "collection",
            "source",
            "distribution",
            "subject_category",
            "thesaurus_term",
        )
    )
    controls_valid = bool(
        prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("coverage", {}).get("coverage_scope") == "partition"
        and prisma.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and strategy.get("executed_query") == event.get("query")
        and strategy.get("sort", {}).get("value") == "Publication Date (Oldest)"
        and publication.get("state") == "applied"
        and publication.get("value", {}).get("gte") == CUTOFF_START
        and publication.get("value", {}).get("lte") == CUTOFF_END
        and publication.get("value", {}).get("precision") == "calendar_day"
        and publication.get("value", {}).get("inclusive") is True
        and filters_empty
    )
    total = value.get("total")
    count_valid = bool(
        isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 0
        and isinstance(records, list)
        and total == len(records) == len(ids) == len(set(ids))
        and reconciliation.get("source_total") == total
        and reconciliation.get("source_entries_retrieved") == total
        and reconciliation.get("records_retained") == total
        and reconciliation.get("source_traversal_reconciled") is True
    )
    adapter = prisma.get("adapter", {}) if isinstance(prisma, Mapping) else {}
    adapter_valid = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == "NASA Technical Reports Server (NTRS)"
        and value.get("executed_query") == event.get("query")
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and prisma.get("completion_status") == "complete"
        and controls_valid
        and count_valid
        and adapter_valid
        and screenshot_receipt.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshot_receipt.get("automatic") is True
        and screenshot_receipt.get("same_directory_as_json") is True
        and all(row["valid"] for row in screenshot_rows)
        and marker_valid
        and all(abstract_capture)
        and all(type_capture)
    )
    return {
        "artifact_written": True,
        "valid": valid,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "total": total,
        "stable_id_count": len(ids),
        "stable_id_set_sha256": digest_ids(set(ids)),
        "controls_valid": controls_valid,
        "count_reconciliation_valid": count_valid,
        "adapter_binding_valid": adapter_valid,
        "screenshots_valid": all(row["valid"] for row in screenshot_rows),
        "terminal_marker_valid": marker_valid,
        "detail_capture_valid": all(abstract_capture) and all(type_capture),
        "full_abstract_count": sum(
            bool(row.get("abstract")) for row in records if isinstance(row, Mapping)
        )
        if isinstance(records, list)
        else 0,
        "source_abstract_not_available_count": sum(
            row.get("abstract_not_available") is True
            for row in records
            if isinstance(row, Mapping)
        )
        if isinstance(records, list)
        else 0,
        "source_document_type_count": sum(
            bool(row.get("documentTypes"))
            for row in records
            if isinstance(row, Mapping)
        )
        if isinstance(records, list)
        else 0,
        "source_document_type_not_available_count": sum(
            row.get("document_type_not_available") is True
            for row in records
            if isinstance(row, Mapping)
        )
        if isinstance(records, list)
        else 0,
        "screenshots": screenshot_rows,
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
        "--date-start",
        CUTOFF_START,
        "--date-end",
        CUTOFF_END,
        "--page-size",
        str(event["page_size"]),
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        "0",
        "--detail-delay-seconds",
        "0",
        "--full-abstracts",
        "--require-complete",
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
        f"NASA NTRS final direct discovery partition {event['partition_id']}",
    ]


def run_final(
    plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid final NTRS plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The final NTRS output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url):
        raise ValueError("Final NTRS execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            import time

            time.sleep(settle_seconds)
        output = output_dir / event["output_filename"]
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
                timeout=event["timeout_seconds"] + 90,
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
                    "abstracts": outcome.get("full_abstract_count"),
                    "document_types": outcome.get("source_document_type_count"),
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
    ):
        errors.append("run_receipt")
    summaries: list[dict[str, Any]] = []
    all_ids: set[str] = set()
    occurrence_count = 0
    input_paths: list[Path] = []
    for event in plan["events"]:
        path = output_dir / event["output_filename"]
        summary = artifact_summary(path, event, plan)
        summaries.append(
            {
                "partition_id": event["partition_id"],
                "path": relative(path),
                **summary,
            }
        )
        if summary.get("valid") is not True:
            errors.append(f"artifact:{event['partition_id']}")
            continue
        input_paths.append(path)
        value = load(path)
        ids = {row["paperId"] for row in value["results"]}
        all_ids.update(ids)
        occurrence_count += len(ids)
    if receipt.get("success") is not True:
        errors.append("run_unsuccessful")
    outcomes = receipt.get("outcomes")
    if not isinstance(outcomes, list) or [
        outcome.get("partition_id")
        for outcome in outcomes
        if isinstance(outcome, Mapping)
    ] != list(PARTITIONS):
        errors.append("run_partition_coverage")
    elif any(outcome.get("success") is not True for outcome in outcomes):
        errors.append("run_event_failure")

    if not errors:
        command = [
            "uv",
            "run",
            str(SOURCE_UNION_TOOL),
            "--input",
            *[str(path) for path in input_paths],
            "--output-path",
            str(union_path),
            "--expected-partitions",
            *PARTITIONS,
            "--expected-source",
            "nasa_ntrs",
            "--review-namespace",
            "main",
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode != 0 or not union_path.is_file():
            errors.append("source_union_receipt")
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": plan["source"],
        "source_id": plan["source_id"],
        "review_namespace": plan["review_namespace"],
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "adapter": plan["adapter"],
        "date_window": plan["date_window"],
        "partition_count": len(summaries),
        "accepted_partition_count": sum(
            summary.get("valid") is True for summary in summaries
        ),
        "record_occurrence_count": occurrence_count,
        "unique_source_record_count": len(all_ids),
        "unique_source_record_id_set_sha256": digest_ids(all_ids),
        "full_abstract_occurrence_count": sum(
            summary.get("full_abstract_count", 0) for summary in summaries
        ),
        "source_abstract_not_available_occurrence_count": sum(
            summary.get("source_abstract_not_available_count", 0)
            for summary in summaries
        ),
        "source_document_type_occurrence_count": sum(
            summary.get("source_document_type_count", 0) for summary in summaries
        ),
        "source_document_type_not_available_occurrence_count": sum(
            summary.get("source_document_type_not_available_count", 0)
            for summary in summaries
        ),
        "detail_capture_complete": bool(
            not errors
            and all(
                summary.get("detail_capture_valid") is True for summary in summaries
            )
        ),
        "source_union_receipt": relative(union_path) if union_path.is_file() else None,
        "source_union_receipt_sha256": digest(union_path)
        if union_path.is_file()
        else None,
        "partitions": summaries,
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
    assess_parser.add_argument("--union-receipt", type=Path, required=True)
    assess_parser.add_argument("--assessment", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan()
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 1 if errors else 0
    if args.command == "run":
        if args.settle_seconds < 0:
            raise ValueError("--settle-seconds cannot be negative")
        return run_final(args.plan, args.output_dir, args.receipt, args.settle_seconds)
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.output_dir,
            args.union_receipt,
            args.assessment,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
