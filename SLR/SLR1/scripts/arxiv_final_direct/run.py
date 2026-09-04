#!/usr/bin/env python3
"""Plan, run, and validate final arXiv direct discovery searches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_arxiv.py"
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/arxiv_pilot004/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/arxiv/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-arxiv-final-direct-plan/v1"
RUN_SCHEMA = "slr1-arxiv-final-direct-run/v1"
RUN_RECONCILIATION_SCHEMA = "slr1-arxiv-final-direct-run-reconciliation/v1"
CELL_DECLARATIONS_SCHEMA = "slr1-arxiv-final-direct-cell-declarations/v1"
RECORD_UNION_SCHEMA = "slr1-arxiv-final-direct-record-union/v1"
ASSESSMENT_SCHEMA = "slr1-arxiv-final-direct-assessment/v1"

SOURCE = "arXiv"
SOURCE_ID = "arxiv"
REVIEW_ID = "slr1-1.1-restart"
PHASE = "identification"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
CUTOFF = "2026-08-24"
SOURCE_UPPER_EXCLUSIVE = "2026-08-25"
LIMIT = 1000
MAX_PAGES = 20
NATIVE_PAGE_SIZE = 100
TIMEOUT_SECONDS = 300
STRICT_PASS_DELAY_SECONDS = 10
INTER_EVENT_DELAY_SECONDS = 30
ADAPTER_VERSION = "8"
SCREENSHOT_SCHEMA = "arxiv-automatic-screenshots/v1"
ARXIV_ID = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z][a-z.\-]*/\d{7})$", re.IGNORECASE)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_ordered(values: list[str]) -> str:
    value = hashlib.sha256()
    for item in values:
        encoded = item.encode("utf-8")
        value.update(len(encoded).to_bytes(8, "big"))
        value.update(encoded)
    return value.hexdigest()


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


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def repository_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
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
        raise RuntimeError("Cannot determine the arXiv adapter version")
    return match.group(1)


def load_queries() -> Any:
    require_regular(QUERY_SNAPSHOT)
    spec = importlib.util.spec_from_file_location("arxiv_final_direct_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted arXiv partition schedule changed")
    if len(module.CELLS) != 12:
        raise RuntimeError("The accepted arXiv source-cell schedule changed")
    return module


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    for path in paths:
        require_regular(path)
    return {relative(path): digest(path) for path in paths}


def output_path(root: Path, event: Mapping[str, Any]) -> Path:
    return root / str(event["output"])


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def strategy_reference(sequence: int) -> str:
    return f"slr1-arxiv-main-direct-v{sequence}"


def event_from_cell(
    cell: Any, *, sequence: int = 1, strategy_version: str | None = None
) -> dict[str, Any]:
    prefix = "final-main-arxiv" if sequence == 1 else f"final-main-arxiv-r{sequence:03d}"
    value = {
        "event_id": f"{prefix}-{cell.cell_id}",
        "parent_event_id": f"{prefix}-{cell.partition_id}",
        "event_kind": "final",
        "review_namespace": "main",
        "source_id": SOURCE_ID,
        "partition_id": cell.partition_id,
        "cell_id": cell.cell_id,
        "cell_number": cell.cell_number,
        "cell_count": cell.cell_count,
        "branch": cell.branch,
        "factors": list(cell.factors),
        "rows": [
            {"operator": "AND", "field": "all", "term": row}
            for row in cell.rows
        ],
        "serialized_query": cell.serialized_query,
        "query_sha256": cell.query_sha256,
        "row_character_counts": [len(row) for row in cell.rows],
        "output": f"{cell.partition_id}/cell-{cell.cell_number:02d}-of-{cell.cell_count:02d}.json",
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": TIMEOUT_SECONDS,
        "strict_pass_delay_seconds": STRICT_PASS_DELAY_SECONDS,
    }
    if strategy_version is not None:
        value["strategy_version"] = strategy_version
    return value


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
    common_strategy_version = repository_head()
    events = [
        event_from_cell(
            cell,
            sequence=sequence,
            strategy_version=common_strategy_version,
        )
        for cell in queries.CELLS
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": common_strategy_version,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "review_id": REVIEW_ID,
        "event_kind": "final",
        "phase": PHASE,
        "strategy_reference": strategy_reference(sequence),
        "strategy_version": common_strategy_version,
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "accepted_translation_snapshot": relative(QUERY_SNAPSHOT),
        "accepted_translation_snapshot_sha256": digest(QUERY_SNAPSHOT),
        "cutoff": {
            "exact_common_cutoff": CUTOFF,
            "source_date_start": DATE_START,
            "source_date_end_inclusive": CUTOFF,
            "source_upper_bound_exclusive": SOURCE_UPPER_EXCLUSIVE,
            "date_basis": "submitted_date_first",
            "date_basis_label": "Submission date (original)",
        },
        "source_configuration": {
            "interface": "rendered Advanced Search web interface",
            "url": "https://arxiv.org/search/advanced",
            "collection": "Full multidisciplinary arXiv repository",
            "field": "All fields for every repeatable row",
            "subject_categories": [],
            "physics_archive": "all",
            "cross_lists": "include",
            "language_filter": None,
            "publication_type_filter": None,
            "peer_review_filter": None,
            "access_filter": None,
            "full_text_filter": None,
            "include_older_versions": False,
            "sort": "Submission date (oldest first)",
            "abstracts": "show",
            "full_abstracts": True,
        },
        "record_capture_contract": {
            "native_full_abstracts": {
                "required": True,
                "adapter_control": "native per-result More control",
                "forbidden_flags": [
                    "--skip-full-abstracts",
                    "--no-full-abstracts",
                    "--abstracts hide",
                ],
                "required_record_fields": ["abstract", "abstract_source"],
            },
            "source_publication_types": {
                "required": True,
                "required_record_fields": ["sourcePublicationType", "documentType"],
                "expected_source_value": "preprint",
                "expected_document_type": "Preprint",
                "reviewer_coding": "Do not infer screening publication_type from source metadata.",
            },
        },
        "translation": {
            "literal": "one exact straight-double-quoted literal",
            "ordinary_block": "one homogeneous uppercase OR All-fields row",
            "conjunction": "separate rendered rows joined by outer AND",
            "wildcards": False,
            "controlled_vocabulary_supplement": False,
            "compound_distribution": {
                "A2": "M_H branch and M_B branch",
                "BG1": "fixed-or-exact branch and mission-marker-and-M_B branch",
                "BG2": "fixed-exact-or-variation branch and product-marker-and-M_B branch",
            },
            "block_row_sha256": {
                name: digest_text(value) for name, value in queries.BLOCK_ROWS.items()
            },
        },
        "strict_contract": {
            "required_passes": 2,
            "membership_gate": "equal complete ordered arXiv ID ledgers",
            "source_total_gate": "each successful artifact has an exact integer total equal to its retained row count",
            "automatic_screenshots_required": True,
            "failure_total": None,
        },
        "execution_policy": {
            "one_source_execution_per_cell": True,
            "continue_after_cell_failure": True,
            "fresh_browser_per_cell": True,
            "retry_policy": "none after final-plan execution begins",
            "inter_event_delay_seconds": INTER_EVENT_DELAY_SECONDS,
            "skip_full_abstracts": False,
            "abstracts": "show",
        },
        "adapter": {
            "id": "search_arxiv",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "bindings": {"files": bindings()},
        "partition_ids": list(PARTITIONS),
        "source_cell_count": len(events),
        "events": events,
    }
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        plan["corrective_run"] = {
            "sequence": sequence,
            "reason": (
                "The completed first final run used distinct per-cell PRISMA strategy "
                "versions. This corrective run preserves those artifacts and executes "
                "the unchanged cells with one common final strategy version."
            ),
            "superseded_plan": relative(superseded_plan),
            "superseded_plan_sha256": digest(superseded_plan),
            "superseded_run_receipt": relative(superseded_receipt),
            "superseded_run_receipt_sha256": digest(superseded_receipt),
        }
    return plan


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    corrective = plan.get("corrective_run")
    sequence = 1 if corrective is None else corrective.get("sequence")
    if not isinstance(sequence, int) or sequence < 1:
        errors.append("sequence")
        sequence = 1
    common_strategy_version = plan.get("strategy_version")
    if sequence > 1 and (
        not isinstance(common_strategy_version, str)
        or re.fullmatch(r"[0-9a-f]{40}", common_strategy_version) is None
        or not isinstance(corrective, Mapping)
        or not isinstance(corrective.get("reason"), str)
        or not corrective.get("reason").strip()
        or not corrective.get("superseded_plan")
        or not corrective.get("superseded_plan_sha256")
        or not corrective.get("superseded_run_receipt")
        or not corrective.get("superseded_run_receipt_sha256")
    ):
        errors.append("corrective_provenance")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != "main"
        or plan.get("review_id") != REVIEW_ID
        or plan.get("event_kind") != "final"
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != strategy_reference(sequence)
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("accepted_translation_snapshot") != relative(QUERY_SNAPSHOT)
        or plan.get("accepted_translation_snapshot_sha256") != digest(QUERY_SNAPSHOT)
    ):
        errors.append("identity")
    cutoff = plan.get("cutoff", {})
    if (
        cutoff.get("exact_common_cutoff") != CUTOFF
        or cutoff.get("source_date_start") != DATE_START
        or cutoff.get("source_date_end_inclusive") != CUTOFF
        or cutoff.get("source_upper_bound_exclusive") != SOURCE_UPPER_EXCLUSIVE
        or cutoff.get("date_basis") != "submitted_date_first"
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("field") != "All fields for every repeatable row"
        or configuration.get("subject_categories") != []
        or configuration.get("physics_archive") != "all"
        or configuration.get("cross_lists") != "include"
        or configuration.get("language_filter") is not None
        or configuration.get("publication_type_filter") is not None
        or configuration.get("peer_review_filter") is not None
        or configuration.get("access_filter") is not None
        or configuration.get("full_text_filter") is not None
        or configuration.get("include_older_versions") is not False
        or configuration.get("sort") != "Submission date (oldest first)"
        or configuration.get("abstracts") != "show"
        or configuration.get("full_abstracts") is not True
    ):
        errors.append("source_configuration")
    capture = plan.get("record_capture_contract", {})
    if (
        capture.get("native_full_abstracts", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("expected_source_value") != "preprint"
        or capture.get("source_publication_types", {}).get("expected_document_type") != "Preprint"
    ):
        errors.append("record_capture_contract")
    execution = plan.get("execution_policy", {})
    if (
        execution.get("one_source_execution_per_cell") is not True
        or execution.get("continue_after_cell_failure") is not True
        or execution.get("fresh_browser_per_cell") is not True
        or execution.get("skip_full_abstracts") is not False
        or execution.get("abstracts") != "show"
        or execution.get("inter_event_delay_seconds") != INTER_EVENT_DELAY_SECONDS
    ):
        errors.append("execution_policy")
    adapter = plan.get("adapter", {})
    if (
        adapter.get("id") != "search_arxiv"
        or adapter.get("version") != ADAPTER_VERSION
        or adapter.get("version") != adapter_version()
        or adapter.get("sha256") != digest(ADAPTER)
    ):
        errors.append("adapter")
    expected_cells = list(queries.CELLS)
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != len(expected_cells):
        errors.append("source_cell_count")
        events = []
    if plan.get("partition_ids") != list(PARTITIONS):
        errors.append("partitions")
    for event, cell in zip(events, expected_cells, strict=False):
        if not isinstance(event, Mapping):
            errors.append("event_shape")
            continue
        expected = event_from_cell(
            cell,
            sequence=sequence,
            strategy_version=(
                common_strategy_version
                if isinstance(common_strategy_version, str)
                else None
            ),
        )
        fields = (
            "event_id",
            "parent_event_id",
            "event_kind",
            "review_namespace",
            "source_id",
            "partition_id",
            "cell_id",
            "cell_number",
            "cell_count",
            "branch",
            "factors",
            "rows",
            "serialized_query",
            "query_sha256",
            "row_character_counts",
            "output",
            "limit",
            "max_pages",
            "timeout_seconds",
            "strict_pass_delay_seconds",
        )
        if isinstance(common_strategy_version, str):
            fields = (*fields, "strategy_version")
        if any(event.get(field) != expected[field] for field in fields):
            errors.append(f"event:{cell.cell_id}")
    if verify_bindings:
        for name, expected_hash in plan.get("bindings", {}).get("files", {}).items():
            path = REPOSITORY_ROOT / name
            if not path.is_file() or path.is_symlink() or digest(path) != expected_hash:
                errors.append(f"binding:{name}")
    return errors


def final_command(event: Mapping[str, Any], output: Path, plan: Mapping[str, Any]) -> list[str]:
    command = ["uv", "run", str(ADAPTER)]
    for row in event["rows"]:
        command.extend(["--row", row["operator"], row["field"], row["term"]])
    command.extend(
        [
            "--date-start",
            DATE_START,
            "--date-end",
            CUTOFF,
            "--date-type",
            "submitted_date_first",
            "--abstracts",
            "show",
            "--exclude-older-versions",
            "--physics-archive",
            "all",
            "--include-cross-list",
            "--sort",
            "submitted_date",
            "--limit",
            str(event["limit"]),
            "--max-pages",
            str(event["max_pages"]),
            "--timeout",
            str(event["timeout_seconds"]),
            "--page-delay-seconds",
            str(event["strict_pass_delay_seconds"]),
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
            str(event.get("strategy_version", event["query_sha256"])),
            "--prisma-phase",
            str(plan["phase"]),
            "--prisma-coverage-scope",
            "partition",
            "--prisma-partition-id",
            str(event["partition_id"]),
            "--prisma-partition-label",
            str(event["partition_id"]),
            "--prisma-partition-description",
            f"arXiv final direct discovery {event['partition_id']} {event['cell_id']}",
        ]
    )
    return command


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not marker.is_file() or marker.is_symlink():
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = value.get("normalized_json", {})
    return bool(
        value.get("schema") == "academic_search_output_commit_marker_v1"
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def image_evidence(path: Path, screenshots: Any) -> tuple[bool, list[dict[str, Any]]]:
    valid = True
    evidence_rows: list[dict[str, Any]] = []
    receipt = screenshots if isinstance(screenshots, Mapping) else {}
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path), strict=True):
        evidence = receipt.get(key, {}) if isinstance(receipt, Mapping) else {}
        image_valid = bool(
            image.is_file()
            and not image.is_symlink()
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
        evidence_rows.append(
            {
                "kind": key,
                "path": image.name,
                "sha256": digest(image) if image.is_file() else None,
                "valid": image_valid,
            }
        )
    return valid, evidence_rows


def controls_valid(data: Mapping[str, Any], event: Mapping[str, Any], plan: Mapping[str, Any]) -> bool:
    metadata = data.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    strategy = run.get("strategy", {}) if isinstance(run, Mapping) else {}
    limits = strategy.get("limits", {}) if isinstance(strategy, Mapping) else {}
    scope = strategy.get("search_scope", {}) if isinstance(strategy, Mapping) else {}
    sort = strategy.get("sort", {}) if isinstance(strategy, Mapping) else {}
    source_controls = limits.get("source_controls", {}) if isinstance(limits, Mapping) else {}
    date_from = limits.get("from", {}) if isinstance(limits, Mapping) else {}
    date_to = limits.get("to", {}) if isinstance(limits, Mapping) else {}
    basis = limits.get("basis", {}) if isinstance(limits, Mapping) else {}
    cross_lists = limits.get("cross_list_inclusion", {}) if isinstance(limits, Mapping) else {}
    versions = limits.get("include_older_versions", {}) if isinstance(limits, Mapping) else {}
    language = limits.get("language_filter", {}) if isinstance(limits, Mapping) else {}
    document_type = limits.get("document_type_filter", {}) if isinstance(limits, Mapping) else {}
    return bool(
        data.get("source") == SOURCE
        and data.get("executed_query") == event.get("serialized_query")
        and run.get("run_id") == event.get("event_id")
        and run.get("review_id") == plan.get("review_id")
        and run.get("strategy_reference") == plan.get("strategy_reference")
        and run.get("strategy_version") == event.get("strategy_version", event.get("query_sha256"))
        and run.get("phase") == plan.get("phase")
        and run.get("coverage", {}).get("coverage_scope") == "partition"
        and run.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and strategy.get("executed_query") == event.get("serialized_query")
        and scope.get("subject_categories") == []
        and scope.get("physics_archive") == "all"
        and scope.get("cross_list_inclusion") == "include"
        and date_from.get("value") == DATE_START
        and date_to.get("value") == CUTOFF
        and basis.get("value") == "submitted_date_first"
        and source_controls.get("value", {}).get("from") == DATE_START
        and source_controls.get("value", {}).get("to") == SOURCE_UPPER_EXCLUSIVE
        and source_controls.get("value", {}).get("upper_bound_semantics") == "exclusive"
        and cross_lists.get("value") == "include"
        and versions.get("requested") is False
        and sort.get("value") == "Submission date (oldest first)"
        and language.get("state") == "unavailable"
        and document_type.get("state") == "unavailable"
    )


def strict_valid(data: Mapping[str, Any]) -> bool:
    metadata = data.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    rows = data.get("results")
    total = data.get("total")
    ids: list[str] = []
    if not isinstance(rows, list) or not isinstance(total, int) or isinstance(total, bool):
        return False
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            return False
        identifier = row.get("paperId")
        stable = row.get("sourceRecordStableId")
        version = row.get("sourceRecordVersion")
        if (
            not isinstance(identifier, str)
            or ARXIV_ID.fullmatch(identifier) is None
            or stable != identifier + (version or "")
            or row.get("rank") != position
        ):
            return False
        ids.append(identifier)
    return bool(
        total == len(rows)
        and len(ids) == len(set(ids))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and metadata.get("normalized_merge_eligible") in (None, True)
        and run.get("completion_status") == "complete"
        and run.get("report_ready") is True
        and run.get("report_readiness_reasons") in ([], None)
    )


def record_capture_summary(rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list):
        return {
            "records": 0,
            "full_abstract_count": 0,
            "blank_abstract_count": 0,
            "source_publication_type_count": 0,
            "missing_source_publication_type_count": 0,
            "publication_types": {},
            "valid": False,
        }
    full_abstract_count = 0
    blank_abstract_count = 0
    source_type_count = 0
    missing_type_count = 0
    publication_types: Counter[str] = Counter()
    valid = True
    for row in rows:
        if not isinstance(row, Mapping):
            valid = False
            continue
        abstract = row.get("abstract")
        source = row.get("abstract_source")
        if (
            isinstance(abstract, str)
            and bool(abstract.strip())
            and source
            in {
                "native_arxiv_expanded_search_result",
                "native_arxiv_complete_search_result",
            }
            and row.get("abstract_not_available") is not True
        ):
            full_abstract_count += 1
        else:
            blank_abstract_count += 1
            valid = False
        publication_type = row.get("sourcePublicationType")
        if publication_type == "preprint" and row.get("documentType") == "Preprint":
            source_type_count += 1
            publication_types[publication_type] += 1
        else:
            missing_type_count += 1
            valid = False
        if "publication_type" in row:
            valid = False
    return {
        "records": len(rows),
        "full_abstract_count": full_abstract_count,
        "blank_abstract_count": blank_abstract_count,
        "source_publication_type_count": source_type_count,
        "missing_source_publication_type_count": missing_type_count,
        "publication_types": dict(sorted(publication_types.items())),
        "valid": valid,
    }


def artifact_summary(path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"valid": False, "artifact_written": False}
    try:
        data = load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }
    metadata = data.get("output_metadata", {})
    adapter = metadata.get("prisma_search_run", {}).get("adapter", {}) if isinstance(metadata, Mapping) else {}
    screenshots = metadata.get("screenshots", {}) if isinstance(metadata, Mapping) else {}
    screenshots_ok, image_rows = image_evidence(path, screenshots)
    controls_ok = controls_valid(data, event, plan)
    strict_ok = strict_valid(data)
    capture = record_capture_summary(data.get("results"))
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    screenshot_receipt_ok = bool(
        isinstance(screenshots, Mapping)
        and screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
        and screenshots_ok
    )
    rows = data.get("results", [])
    ordered_bare_ids = [row.get("paperId") for row in rows if isinstance(row, Mapping)]
    ids_valid = all(isinstance(item, str) for item in ordered_bare_ids)
    return {
        "valid": bool(
            controls_ok
            and strict_ok
            and adapter_ok
            and screenshot_receipt_ok
            and marker_valid(path)
            and capture["valid"]
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status") if isinstance(metadata, Mapping) else None,
        "error_stage": metadata.get("error_stage") if isinstance(metadata, Mapping) else None,
        "error_reason": metadata.get("error_reason") if isinstance(metadata, Mapping) else None,
        "total": data.get("total"),
        "ordered_bare_ids": ordered_bare_ids if ids_valid else [],
        "ordered_bare_ids_sha256": digest_ordered(ordered_bare_ids) if ids_valid else None,
        "controls_valid": controls_ok,
        "strict_two_pass_valid": strict_ok,
        "adapter_binding_valid": adapter_ok,
        "screenshots_valid": screenshot_receipt_ok,
        "terminal_marker_valid": marker_valid(path),
        "record_capture": capture,
        "screenshots": image_rows,
    }


def run_final(plan_path: Path, output_root: Path, receipt_path: Path, settle_seconds: float) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    require_regular(plan_path)
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid arXiv final plan: " + ", ".join(errors))
    if output_root.is_symlink():
        raise ValueError("Final arXiv output root cannot be a symlink")
    output_root.mkdir(parents=True, exist_ok=True)

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_path(output_root, event)
        occupied = (output, *screenshot_paths(output), marker_path(output))
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise FileExistsError(f"Refusing to overwrite {event['cell_id']} artifacts")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            completed = subprocess.run(
                final_command(event, output, plan),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            exit_code: int | None = completed.returncode
            summary = artifact_summary(output, event, plan)
        except Exception as error:  # noqa: BLE001 - final runner retains an explicit outcome.
            exit_code = None
            summary = {
                "valid": False,
                "artifact_written": output.is_file(),
                "runner_failure": type(error).__name__,
            }
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "parent_event_id": event["parent_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "success": success,
            "artifact": relative(output) if output.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            "fresh_browser": True,
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "cell": event["cell_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "total": outcome.get("total"),
                    "full_abstracts": outcome.get("record_capture", {}).get("full_abstract_count"),
                    "publication_types": outcome.get("record_capture", {}).get("publication_types"),
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
        "review_namespace": "main",
        "event_kind": "final",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(outcome.get("success") is True for outcome in outcomes),
        "all_source_cells_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def successful_event_artifacts(
    plan: Mapping[str, Any], run: Mapping[str, Any], output_root: Path
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, Mapping[str, Any]]]:
    if (
        run.get("schema_version") not in {RUN_SCHEMA, RUN_RECONCILIATION_SCHEMA}
        or run.get("success") is not True
    ):
        raise ValueError("The final run receipt is incomplete")
    outcomes = {item.get("event_id"): item for item in run.get("outcomes", []) if isinstance(item, Mapping)}
    selected: list[tuple[Mapping[str, Any], Mapping[str, Any], Path, Mapping[str, Any]]] = []
    for event in plan["events"]:
        outcome = outcomes.get(event["event_id"])
        path = output_path(output_root, event)
        if outcome is None or outcome.get("success") is not True:
            raise ValueError(f"Missing successful final event {event['cell_id']}")
        summary = artifact_summary(path, event, plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Invalid final artifact {path}")
        selected.append((event, outcome, path, load(path)))
    return selected


def reconcile_run(
    plan_path: Path, original_receipt_path: Path, output_root: Path, output: Path
) -> dict[str, Any]:
    """Revalidate completed source artifacts without rerunning a final cell."""
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    original = load(original_receipt_path)
    if validate_plan(plan, verify_bindings=False):
        raise ValueError("The final plan is invalid")
    if original.get("schema_version") != RUN_SCHEMA:
        raise ValueError("Unexpected original arXiv run receipt schema")
    original_outcomes = {
        item.get("event_id"): item
        for item in original.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    outcomes: list[dict[str, Any]] = []
    for event in plan["events"]:
        original_outcome = original_outcomes.get(event["event_id"])
        if original_outcome is None or original_outcome.get("exit_code") != 0:
            raise ValueError(f"The original run did not complete {event['cell_id']}")
        path = output_path(output_root, event)
        summary = artifact_summary(path, event, plan)
        outcomes.append(
            {
                "event_id": event["event_id"],
                "parent_event_id": event["parent_event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "success": summary.get("valid") is True,
                "artifact": relative(path) if path.is_file() else None,
                "source_command_exit_code": original_outcome.get("exit_code"),
                "source_command_attempt_count": original_outcome.get("attempt_count"),
                "source_commands_reexecuted": False,
                **summary,
            }
        )
    success = len(outcomes) == len(plan["events"]) and all(
        item.get("success") is True for item in outcomes
    )
    value = {
        "schema_version": RUN_RECONCILIATION_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "event_kind": "final",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "original_run_receipt": relative(original_receipt_path),
        "original_run_receipt_sha256": digest(original_receipt_path),
        "reconciliation_reason": (
            "The compact adapter output does not publish normalized_merge_eligible. "
            "This receipt revalidates the completed, report-ready source artifacts "
            "without rerunning a final query cell."
        ),
        "source_commands_reexecuted": False,
        "planned_source_cell_count": len(plan["events"]),
        "validated_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(item.get("success") is True for item in outcomes),
        "success": success,
        "outcomes": outcomes,
        "reconciled_at_utc": now(),
    }
    write_new(output, value)
    return value


def build_cell_declarations(
    plan_path: Path,
    receipt_path: Path,
    output_root: Path,
    output: Path,
) -> dict[str, Any]:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    if validate_plan(plan, verify_bindings=False):
        raise ValueError("The final plan is invalid")
    selected = successful_event_artifacts(plan, run, output_root)
    cells: list[dict[str, Any]] = []
    for event, outcome, path, _ in selected:
        cells.append(
            {
                "source_id": SOURCE_ID,
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "parent_event_id": event["parent_event_id"],
                "source_run_id": event["event_id"],
                "query": event["serialized_query"],
                "requested_query": event["serialized_query"],
                "executed_query": event["serialized_query"],
                "source_native_executed_query": event["serialized_query"],
                "artifact_sha256": outcome["artifact_sha256"],
                "artifact_byte_count": outcome["artifact_bytes"],
                "stable_ids": outcome["ordered_bare_ids"],
                "status": "complete",
                "report_ready": True,
                "artifact": relative(path),
            }
        )
    value = {
        "schema_version": CELL_DECLARATIONS_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "expected_cells": cells,
    }
    write_new(output, value)
    return value


def run_source_union(
    plan_path: Path,
    receipt_path: Path,
    output_root: Path,
    declarations_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    declarations = load(declarations_path)
    if declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA:
        raise ValueError("Unexpected arXiv source-cell declaration schema")
    selected = successful_event_artifacts(plan, run, output_root)
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
        "main",
        "--expected-cells",
        str(declarations_path),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("Could not create the arXiv source-union receipt")
    return 0


def build_record_union(
    plan_path: Path,
    receipt_path: Path,
    output_root: Path,
    output: Path,
) -> dict[str, Any]:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    selected = successful_event_artifacts(plan, run, output_root)
    records: dict[str, dict[str, Any]] = {}
    artifact_rows: list[dict[str, Any]] = []
    for event, outcome, path, data in selected:
        artifact_rows.append(
            {
                "cell_id": event["cell_id"],
                "partition_id": event["partition_id"],
                "artifact": relative(path),
                "artifact_sha256": outcome["artifact_sha256"],
                "record_count": data["total"],
            }
        )
        for row in data["results"]:
            identifier = row["paperId"]
            item = records.setdefault(
                identifier,
                {
                    "paperId": identifier,
                    "source_record_stable_ids": [],
                    "discovery_cells": [],
                    "discovery_partitions": [],
                    "record": row,
                },
            )
            stable = row["sourceRecordStableId"]
            if stable not in item["source_record_stable_ids"]:
                item["source_record_stable_ids"].append(stable)
            if event["cell_id"] not in item["discovery_cells"]:
                item["discovery_cells"].append(event["cell_id"])
            if event["partition_id"] not in item["discovery_partitions"]:
                item["discovery_partitions"].append(event["partition_id"])
            current = item["record"]
            if len(str(row.get("abstract") or "")) > len(str(current.get("abstract") or "")):
                item["record"] = row
    rows = []
    for identifier in sorted(records):
        item = records[identifier]
        item["source_record_stable_ids"].sort()
        item["discovery_cells"].sort()
        item["discovery_partitions"].sort(key=PARTITIONS.index)
        rows.append(item)
    captures = record_capture_summary([item["record"] for item in rows])
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "purpose": "deduplicated_final_direct_source_records_with_full_abstracts_and_source_publication_types",
        "reviewer_publication_type_coding": "not inferred from source metadata",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "input_artifacts": artifact_rows,
        "source_event_record_count": sum(item["record_count"] for item in artifact_rows),
        "unique_bare_arxiv_id_count": len(rows),
        "records_with_full_abstract": captures["full_abstract_count"],
        "records_without_full_abstract": captures["blank_abstract_count"],
        "records_with_source_publication_type": captures["source_publication_type_count"],
        "records_missing_source_publication_type": captures["missing_source_publication_type_count"],
        "source_publication_type_counts": captures["publication_types"],
        "complete": captures["valid"],
        "records": rows,
    }
    write_new(output, value)
    return value


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_root: Path,
    declarations_path: Path,
    source_union_path: Path,
    record_union_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    run = load(receipt_path)
    declarations = load(declarations_path)
    source_union = load(source_union_path)
    record_union = load(record_union_path)
    errors = validate_plan(plan, verify_bindings=False)
    if run.get("schema_version") != RUN_SCHEMA or run.get("plan_sha256") != digest(plan_path):
        errors.append("run_receipt")
    if run.get("success") is not True or run.get("accepted_source_cell_count") != len(plan["events"]):
        errors.append("run_completion")
    if (
        declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA
        or declarations.get("plan_sha256") != digest(plan_path)
        or declarations.get("run_receipt_sha256") != digest(receipt_path)
        or len(declarations.get("expected_cells", [])) != len(plan["events"])
    ):
        errors.append("cell_declarations")
    try:
        selected = successful_event_artifacts(plan, run, output_root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"events:{type(error).__name__}")
        selected = []

    event_evidence: list[dict[str, Any]] = []
    raw_record_count = 0
    bare_ids: list[str] = []
    for event, outcome, path, data in selected:
        summary = artifact_summary(path, event, plan)
        if outcome.get("success") is not True or summary.get("valid") is not True:
            errors.append(f"event:{event['cell_id']}")
        if (
            outcome.get("artifact_sha256") != digest(path)
            or outcome.get("artifact_bytes") != path.stat().st_size
        ):
            errors.append(f"artifact_binding:{event['cell_id']}")
        raw_record_count += data["total"]
        bare_ids.extend(row["paperId"] for row in data["results"])
        event_evidence.append(
            {
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": relative(path),
                "artifact_sha256": digest(path),
                "source_total": data["total"],
                "ordered_bare_ids": summary["ordered_bare_ids"],
                "ordered_bare_ids_sha256": summary["ordered_bare_ids_sha256"],
                "strict_two_pass_valid": summary["strict_two_pass_valid"],
                "full_abstract_count": summary["record_capture"]["full_abstract_count"],
                "blank_abstract_count": summary["record_capture"]["blank_abstract_count"],
                "source_publication_types": summary["record_capture"]["publication_types"],
            }
        )

    union_source = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    union_valid = bool(
        source_union.get("review_namespace") == "main"
        and source_union.get("review_id") == REVIEW_ID
        and source_union.get("strategy_reference") == plan.get("strategy_reference")
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and union_source.get("event_total_sum") == raw_record_count
        and set(union_source.get("stable_record_ids", [])) == set(bare_ids)
        and source_union.get("artifact_count") == len(plan["events"])
    )
    if not union_valid:
        errors.append("source_union")
    cell_unions = source_union.get("cell_unions", {}).get(SOURCE_ID, {})
    for partition in PARTITIONS:
        expected_count = sum(event["partition_id"] == partition for event in plan["events"])
        if cell_unions.get(partition, {}).get("cell_count") != expected_count:
            errors.append(f"source_union_cell:{partition}")

    records = record_union.get("records")
    record_union_valid = bool(
        record_union.get("schema_version") == RECORD_UNION_SCHEMA
        and record_union.get("plan_sha256") == digest(plan_path)
        and record_union.get("run_receipt_sha256") == digest(receipt_path)
        and record_union.get("source_event_record_count") == raw_record_count
        and record_union.get("unique_bare_arxiv_id_count") == len(set(bare_ids))
        and record_union.get("records_with_full_abstract") == len(set(bare_ids))
        and record_union.get("records_without_full_abstract") == 0
        and record_union.get("records_with_source_publication_type") == len(set(bare_ids))
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("source_publication_type_counts") == {"preprint": len(set(bare_ids))}
        and record_union.get("complete") is True
        and isinstance(records, list)
    )
    if not record_union_valid:
        errors.append("record_union")

    complete = bool(
        len(event_evidence) == len(plan["events"])
        and not errors
    )
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "event_kind": "final",
        "complete": complete,
        "errors": errors,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "cell_declarations": relative(declarations_path),
        "cell_declarations_sha256": digest(declarations_path),
        "source_union": relative(source_union_path),
        "source_union_sha256": digest(source_union_path),
        "record_union": relative(record_union_path),
        "record_union_sha256": digest(record_union_path),
        "adapter": plan.get("adapter"),
        "accepted_source_cell_count": len(event_evidence),
        "events": event_evidence,
        "stable_id_union": {
            "source_event_record_count": raw_record_count,
            "unique_bare_arxiv_id_count": len(set(bare_ids)),
            "cross_cell_duplicate_occurrences": raw_record_count - len(set(bare_ids)),
            "bare_arxiv_id_set_sha256": digest_ordered(sorted(set(bare_ids))),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "record_capture": {
            "full_abstracts_required": True,
            "source_publication_types_required": True,
            "reviewer_publication_type_coding": "deferred to screening",
            "unique_records_with_full_abstract": record_union.get("records_with_full_abstract"),
            "unique_records_without_full_abstract": record_union.get("records_without_full_abstract"),
            "source_publication_type_counts": record_union.get("source_publication_type_counts"),
        },
        "cutoff": plan.get("cutoff"),
    }
    write_new(output, assessment)
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--sequence", type=int, default=1)
    plan_parser.add_argument("--superseded-plan", type=Path)
    plan_parser.add_argument("--superseded-receipt", type=Path)

    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-root", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=INTER_EVENT_DELAY_SECONDS)

    reconcile_parser = commands.add_parser("reconcile-run")
    reconcile_parser.add_argument("--plan", type=Path, required=True)
    reconcile_parser.add_argument("--original-receipt", type=Path, required=True)
    reconcile_parser.add_argument("--output-root", type=Path, required=True)
    reconcile_parser.add_argument("--output", type=Path, required=True)

    declarations_parser = commands.add_parser("cell-declarations")
    declarations_parser.add_argument("--plan", type=Path, required=True)
    declarations_parser.add_argument("--receipt", type=Path, required=True)
    declarations_parser.add_argument("--output-root", type=Path, required=True)
    declarations_parser.add_argument("--output", type=Path, required=True)

    union_parser = commands.add_parser("source-union")
    union_parser.add_argument("--plan", type=Path, required=True)
    union_parser.add_argument("--receipt", type=Path, required=True)
    union_parser.add_argument("--output-root", type=Path, required=True)
    union_parser.add_argument("--cell-declarations", type=Path, required=True)
    union_parser.add_argument("--output", type=Path, required=True)

    records_parser = commands.add_parser("record-union")
    records_parser.add_argument("--plan", type=Path, required=True)
    records_parser.add_argument("--receipt", type=Path, required=True)
    records_parser.add_argument("--output-root", type=Path, required=True)
    records_parser.add_argument("--output", type=Path, required=True)

    assessment_parser = commands.add_parser("assess")
    assessment_parser.add_argument("--plan", type=Path, required=True)
    assessment_parser.add_argument("--receipt", type=Path, required=True)
    assessment_parser.add_argument("--output-root", type=Path, required=True)
    assessment_parser.add_argument("--cell-declarations", type=Path, required=True)
    assessment_parser.add_argument("--source-union", type=Path, required=True)
    assessment_parser.add_argument("--record-union", type=Path, required=True)
    assessment_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "plan":
            write_new(
                args.output,
                build_plan(
                    sequence=args.sequence,
                    superseded_plan=args.superseded_plan,
                    superseded_receipt=args.superseded_receipt,
                ),
            )
            return 0
        if args.command == "run":
            return run_final(args.plan, args.output_root, args.receipt, args.settle_seconds)
        if args.command == "reconcile-run":
            reconcile_run(args.plan, args.original_receipt, args.output_root, args.output)
            return 0
        if args.command == "cell-declarations":
            build_cell_declarations(args.plan, args.receipt, args.output_root, args.output)
            return 0
        if args.command == "source-union":
            return run_source_union(
                args.plan,
                args.receipt,
                args.output_root,
                args.cell_declarations,
                args.output,
            )
        if args.command == "record-union":
            build_record_union(args.plan, args.receipt, args.output_root, args.output)
            return 0
        if args.command == "assess":
            return assess(
                args.plan,
                args.receipt,
                args.output_root,
                args.cell_declarations,
                args.source_union,
                args.record_union,
                args.output,
            )
    except Exception as error:  # noqa: BLE001 - CLI boundary.
        print(str(error), file=sys.stderr)
        return 1
    raise RuntimeError("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
