#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.48",
# ]
# ///

"""Plan, run, and validate final IAF Digital Library discovery searches."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
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
ADAPTER = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py"
)
SOURCE_UNION_TOOL = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
ACCEPTED_PLAN = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/iaf-digital-library/pilots/006/searches/cell-plan.json"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/iaf-digital-library/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = (
    REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
)

SOURCE = "IAF Digital Library"
SOURCE_ID = "iaf_digital_library"
REVIEW_ID = "slr1-1.1-restart"
PHASE = "identification"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CELL_COUNTS = {
    "A1": 37,
    "A2": 48,
    "A3": 21,
    "B1": 4,
    "B2": 20,
    "BG1": 6,
    "BG2": 6,
    "BC1": 3,
    "BT2": 13,
}
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
ACCEPTED_PLAN_SHA256 = (
    "3a156f38693de299cc37f6f40d925b99544451844b666e7de799e8fb25e15d2e"
)
SOURCE_PUBLICATION_TYPE = "conference paper"
DOCUMENT_TYPE = "Conference Paper"
ABSTRACT_SOURCE = "native_iaf_rendered_detail_page"
PUBLICATION_TYPE_SOURCE = "IAF Digital Library conference-paper collection"
LIMIT = 5000
MAX_PAGES = 100
PAGE_SIZE = 500
PASSES = 2
TIMEOUT_SECONDS = 120.0
PAGE_DELAY_SECONDS = 0.05
RETRIES = 2
PROCESS_TIMEOUT_SECONDS = 420.0
INTER_EVENT_DELAY_SECONDS = 0.05

PLAN_SCHEMA = "slr1-iaf-final-direct-plan/v1"
RUN_SCHEMA = "slr1-iaf-final-direct-run/v1"
CAPTURE_SCHEMA = "slr1-iaf-final-direct-cell-capture/v1"
CELL_DECLARATIONS_SCHEMA = "slr1-iaf-final-direct-cell-declarations/v1"
RECORD_UNION_SCHEMA = "slr1-iaf-final-direct-record-union/v1"
ASSESSMENT_SCHEMA = "slr1-iaf-final-direct-assessment/v1"
SCREENSHOT_SCHEMA = "iaf-automatic-screenshots/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sequence_digest(values: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def canonical_set_digest(values: Sequence[str]) -> str:
    hasher = hashlib.sha256()
    for value in sorted(set(values)):
        encoded = value.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
    return hasher.hexdigest()


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
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
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
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise RuntimeError("Cannot determine the repository revision")
    return value


def adapter_constant(name: str) -> str:
    require_regular(ADAPTER)
    match = re.search(
        rf'^{re.escape(name)}\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError(f"Cannot determine {name} from the IAF adapter")
    return match.group(1)


def adapter_identity() -> dict[str, Any]:
    return {
        "id": adapter_constant("ADAPTER_ID"),
        "version": adapter_constant("ADAPTER_VERSION"),
        "sha256": digest(ADAPTER),
        "entrypoint": str(ADAPTER),
    }


def accepted_schedule() -> dict[str, Any]:
    require_regular(ACCEPTED_PLAN)
    if digest(ACCEPTED_PLAN) != ACCEPTED_PLAN_SHA256:
        raise ValueError("The accepted IAF Pilot 006 plan changed")
    plan = load(ACCEPTED_PLAN)
    errors: list[str] = []
    if plan.get("schema_version") != "iaf-digital-library-pilot006-cell-plan/v1":
        errors.append("schema")
    if plan.get("packing", {}).get("wildcard_schedule_cells") != 158:
        errors.append("cell_total")
    if plan.get("packing", {}).get("partition_cell_counts") != CELL_COUNTS:
        errors.append("cell_counts")
    partitions = plan.get("partitions")
    if not isinstance(partitions, Mapping) or tuple(partitions) != PARTITIONS:
        errors.append("partitions")
        partitions = {}
    for partition in PARTITIONS:
        cells = partitions.get(partition, {}).get("cells", [])
        if not isinstance(cells, list) or len(cells) != CELL_COUNTS[partition]:
            errors.append(f"cells:{partition}")
            continue
        for index, cell in enumerate(cells, start=1):
            query = cell.get("query") if isinstance(cell, Mapping) else None
            if (
                not isinstance(query, str)
                or not query
                or len(query) > 500
                or cell.get("cell_id") != f"cell-{index:04d}"
                or cell.get("query_characters") != len(query)
                or cell.get("query_sha256") != digest_text(query)
            ):
                errors.append(f"query:{partition}:{index}")
    if errors:
        raise ValueError("Invalid accepted IAF schedule: " + ", ".join(errors))
    return plan


def expected_events(schedule: Mapping[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for partition in PARTITIONS:
        count = CELL_COUNTS[partition]
        cells = schedule["partitions"][partition]["cells"]
        for index, cell in enumerate(cells, start=1):
            cell_id = f"{partition}-cell-{index:04d}-of-{count:04d}"
            basename = f"cell-{index:04d}-of-{count:04d}"
            events.append(
                {
                    "event_id": f"final-main-iaf-{cell_id.lower()}",
                    "parent_event_id": f"final-main-iaf-{partition.lower()}",
                    "event_kind": "final",
                    "review_namespace": "main",
                    "source_id": SOURCE_ID,
                    "partition_id": partition,
                    "cell_id": cell_id,
                    "accepted_cell_id": cell["cell_id"],
                    "cell_number": index,
                    "cell_count": count,
                    "branch_id": cell["branch_id"],
                    "factor_ranges": copy.deepcopy(cell["factor_ranges"]),
                    "query": cell["query"],
                    "query_characters": len(cell["query"]),
                    "query_sha256": digest_text(cell["query"]),
                    "output": f"{partition}/{basename}.json",
                    "capture_receipt": f"{partition}/{basename}.capture-receipt.json",
                }
            )
    return events


def strategy_reference() -> str:
    return "slr1-iaf-main-direct-v1"


def build_plan() -> dict[str, Any]:
    schedule = accepted_schedule()
    strategy_version = repository_head()
    bound_paths = (
        SCRIPT_PATH,
        ACCEPTED_PLAN,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    for path in bound_paths:
        require_regular(path)
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "review_id": REVIEW_ID,
        "event_kind": "final",
        "phase": PHASE,
        "strategy_reference": strategy_reference(),
        "strategy_version": strategy_version,
        "accepted_translation": {
            "artifact": relative(ACCEPTED_PLAN),
            "sha256": ACCEPTED_PLAN_SHA256,
            "pilot": "006",
            "population_translation": schedule["wildcard_population"]["atoms"],
            "cell_count": 158,
            "partition_cell_counts": CELL_COUNTS,
            "maximum_query_characters": 500,
        },
        "cutoff": {
            "exact_common_cutoff": DATE_END,
            "source_date_start": DATE_START,
            "source_date_end_inclusive": DATE_END,
            "source_precision": "year",
            "application": "local post-filter after complete unbounded source traversal",
            "cutoff_year_handling": (
                "Retain unresolved year-only 2026 records for exact cutoff screening."
            ),
        },
        "source_configuration": {
            "collection": "Full IAF Digital Library",
            "url": "https://dl.iafastro.directory/search/",
            "field": "Unqualified Any keyword in the rendered search wizard",
            "language_filter": None,
            "publication_type_filter": None,
            "event_filter": None,
            "peer_review_filter": None,
            "access_filter": None,
            "full_text_filter": None,
            "source_date_filter": None,
            "ordering": "source native rendered order",
            "controlled_vocabulary_supplement": False,
            "proximity": False,
            "pair_expansion": False,
        },
        "record_capture_contract": {
            "full_abstracts": {
                "required": True,
                "field": "abstract",
                "source": ABSTRACT_SOURCE,
                "source_location": "complete rendered paper detail abstract",
                "source_omissions_allowed": False,
            },
            "source_publication_types": {
                "required": True,
                "source_field": "sourcePublicationType",
                "source_value": SOURCE_PUBLICATION_TYPE,
                "normalized_field": "documentType",
                "normalized_value": DOCUMENT_TYPE,
                "basis": PUBLICATION_TYPE_SOURCE,
                "reviewer_coding": (
                    "This source class is metadata. Reviewer publication_type coding remains deferred to screening."
                ),
            },
        },
        "strict_contract": {
            "required_passes": PASSES,
            "equal_source_totals": True,
            "equal_ordered_paper_ids": True,
            "equal_rendered_capture_hashes": True,
            "exact_query_readback": True,
            "complete_detail_capture": True,
            "automatic_screenshots_required": True,
            "cell_capture_receipts_required": True,
            "complete_source_total_cap": LIMIT,
        },
        "execution_policy": {
            "one_source_execution_per_cell": True,
            "continue_after_cell_failure": True,
            "retry_policy": "none after final-plan execution begins",
            "new_owned_browser_page_per_cell": True,
            "inter_event_delay_seconds": INTER_EVENT_DELAY_SECONDS,
            "page_delay_seconds": PAGE_DELAY_SECONDS,
            "adapter_retries_within_event": RETRIES,
        },
        "record_projection": {
            "applied_by": relative(SCRIPT_PATH),
            "applied_by_sha256": digest(SCRIPT_PATH),
            "fields_added_before_marker_bound_publication": [
                "abstract_source",
                "sourcePublicationType",
                "sourcePublicationTypeSource",
                "documentType",
            ],
        },
        "adapter": adapter_identity(),
        "bindings": {
            "files": {relative(path): digest(path) for path in bound_paths}
        },
        "partition_ids": list(PARTITIONS),
        "source_cell_count": 158,
        "events": expected_events(schedule),
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    try:
        schedule = accepted_schedule()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"accepted_schedule:{type(error).__name__}"]
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != "main"
        or plan.get("review_id") != REVIEW_ID
        or plan.get("event_kind") != "final"
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != strategy_reference()
    ):
        errors.append("identity")
    strategy_version = plan.get("strategy_version")
    if not isinstance(strategy_version, str) or re.fullmatch(
        r"[0-9a-f]{40}", strategy_version
    ) is None:
        errors.append("strategy_version")
    accepted = plan.get("accepted_translation", {})
    if (
        accepted.get("artifact") != relative(ACCEPTED_PLAN)
        or accepted.get("sha256") != ACCEPTED_PLAN_SHA256
        or accepted.get("cell_count") != 158
        or accepted.get("partition_cell_counts") != CELL_COUNTS
    ):
        errors.append("accepted_translation")
    cutoff = plan.get("cutoff", {})
    if (
        cutoff.get("exact_common_cutoff") != DATE_END
        or cutoff.get("source_date_start") != DATE_START
        or cutoff.get("source_date_end_inclusive") != DATE_END
        or cutoff.get("source_precision") != "year"
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("collection") != "Full IAF Digital Library"
        or configuration.get("field")
        != "Unqualified Any keyword in the rendered search wizard"
        or configuration.get("language_filter") is not None
        or configuration.get("publication_type_filter") is not None
        or configuration.get("event_filter") is not None
        or configuration.get("source_date_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not False
        or configuration.get("proximity") is not False
        or configuration.get("pair_expansion") is not False
    ):
        errors.append("source_configuration")
    capture = plan.get("record_capture_contract", {})
    if (
        capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("source") != ABSTRACT_SOURCE
        or capture.get("full_abstracts", {}).get("source_omissions_allowed")
        is not False
        or capture.get("source_publication_types", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("source_value")
        != SOURCE_PUBLICATION_TYPE
        or capture.get("source_publication_types", {}).get("normalized_value")
        != DOCUMENT_TYPE
    ):
        errors.append("record_capture_contract")
    strict = plan.get("strict_contract", {})
    if any(
        strict.get(key) is not True
        for key in (
            "equal_source_totals",
            "equal_ordered_paper_ids",
            "equal_rendered_capture_hashes",
            "exact_query_readback",
            "complete_detail_capture",
            "automatic_screenshots_required",
            "cell_capture_receipts_required",
        )
    ) or strict.get("required_passes") != PASSES:
        errors.append("strict_contract")
    projection = plan.get("record_projection", {})
    if (
        projection.get("applied_by") != relative(SCRIPT_PATH)
        or projection.get("applied_by_sha256") != digest(SCRIPT_PATH)
    ):
        errors.append("record_projection")
    expected = expected_events(schedule)
    if plan.get("partition_ids") != list(PARTITIONS):
        errors.append("partition_ids")
    if plan.get("source_cell_count") != 158 or plan.get("events") != expected:
        errors.append("events")
    if verify_bindings:
        try:
            if plan.get("adapter") != adapter_identity():
                errors.append("adapter")
        except (OSError, RuntimeError, ValueError):
            errors.append("adapter")
        files = plan.get("bindings", {}).get("files", {})
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in files.items():
                path = REPOSITORY_ROOT / str(name)
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or digest(path) != expected_hash
                ):
                    errors.append(f"binding:{name}")
    return errors


def load_adapter() -> Any:
    require_regular(ADAPTER)
    spec = importlib.util.spec_from_file_location("iaf_final_direct_adapter", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the maintained IAF adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def capture_receipt_path(output_root: Path, event: Mapping[str, Any]) -> Path:
    return output_root / str(event["capture_receipt"])


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if marker.is_symlink() or not marker.is_file():
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = value.get("normalized_json")
    return bool(
        value.get("schema") == "academic_search_output_commit_marker_v1"
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def adapter_arguments(
    adapter: Any,
    event: Mapping[str, Any],
    plan: Mapping[str, Any],
    output: Path,
) -> argparse.Namespace:
    values = [
        "--query",
        str(event["query"]),
        "--output-path",
        str(output),
        "--limit",
        str(LIMIT),
        "--max-pages",
        str(MAX_PAGES),
        "--page-size",
        str(PAGE_SIZE),
        "--passes",
        str(PASSES),
        "--timeout",
        str(TIMEOUT_SECONDS),
        "--page-delay-seconds",
        str(PAGE_DELAY_SECONDS),
        "--retries",
        str(RETRIES),
        "--require-complete",
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--prisma-run-id",
        str(event["event_id"]),
        "--prisma-review-id",
        REVIEW_ID,
        "--prisma-strategy-reference",
        str(plan["strategy_reference"]),
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
        (
            f"Lossless IAF source cell {event['cell_number']} of "
            f"{event['cell_count']} for semantic partition {event['partition_id']}"
        ),
    ]
    return adapter.build_parser().parse_args(values)


def project_records(result: dict[str, Any]) -> dict[str, int]:
    rows = result.get("results")
    if not isinstance(rows, list):
        raise TypeError("The complete IAF result lacks a record list")
    full_abstracts = 0
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError("The complete IAF result contains a malformed record")
        abstract = row.get("abstract")
        if (
            not isinstance(abstract, str)
            or not abstract.strip()
            or row.get("abstract_not_available") is True
        ):
            raise ValueError("A retained IAF record lacks its full source abstract")
        row["abstract_source"] = ABSTRACT_SOURCE
        row["sourcePublicationType"] = SOURCE_PUBLICATION_TYPE
        row["sourcePublicationTypeSource"] = PUBLICATION_TYPE_SOURCE
        row["documentType"] = DOCUMENT_TYPE
        full_abstracts += 1
    return {"records": len(rows), "full_abstracts": full_abstracts}


def in_memory_strict_valid(result: Mapping[str, Any]) -> bool:
    metadata = result.get("output_metadata")
    if not isinstance(metadata, Mapping):
        return False
    total = result.get("total")
    rows = result.get("results")
    raw_ids = metadata.get("ordered_paper_ids")
    retained_ids = metadata.get("in_scope_ordered_paper_ids")
    reports = metadata.get("pass_reports")
    date_accounting = metadata.get("date_filter_accounting")
    if (
        isinstance(total, bool)
        or not isinstance(total, int)
        or total < 0
        or not isinstance(rows, list)
        or not isinstance(raw_ids, list)
        or len(raw_ids) != total
        or len(raw_ids) != len(set(raw_ids))
        or not isinstance(retained_ids, list)
        or retained_ids != [row.get("paperId") for row in rows]
        or not isinstance(reports, list)
        or len(reports) != PASSES
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("source_traversal_complete") is not True
        or metadata.get("two_pass_order_verified") is not True
        or metadata.get("two_pass_capture_verified") is not True
        or metadata.get("detail_capture_complete") is not True
        or metadata.get("local_date_filter_complete") is not True
        or metadata.get("normalized_merge_eligible") is not True
        or not isinstance(date_accounting, Mapping)
        or date_accounting.get("raw_total") != total
        or date_accounting.get("retained") != len(rows)
        or date_accounting.get("excluded") != total - len(rows)
    ):
        return False
    baseline_capture: str | None = None
    for report in reports:
        if (
            not isinstance(report, Mapping)
            or report.get("ordered_paper_ids") != raw_ids
            or report.get("ordered_paper_ids_sha256") != sequence_digest(raw_ids)
            or not isinstance(report.get("capture_sha256"), str)
            or not report.get("capture_sha256")
            or not isinstance(report.get("pages"), list)
            or not report.get("pages")
        ):
            return False
        if baseline_capture is None:
            baseline_capture = str(report["capture_sha256"])
        elif report.get("capture_sha256") != baseline_capture:
            return False
    return True


def image_evidence(path: Path, screenshots: Any) -> tuple[bool, list[dict[str, Any]]]:
    if not isinstance(screenshots, Mapping):
        return False, []
    expected_paths = screenshot_paths(path)
    rows: list[dict[str, Any]] = []
    valid = bool(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
    )
    for key, image in zip(("search_page", "results_page"), expected_paths):
        receipt = screenshots.get(key)
        image_valid = bool(
            isinstance(receipt, Mapping)
            and image.is_file()
            and not image.is_symlink()
            and image.stat().st_size > 24
            and receipt.get("path") == image.name
            and receipt.get("sha256") == digest(image)
            and isinstance(receipt.get("width"), int)
            and receipt.get("width", 0) > 0
            and isinstance(receipt.get("height"), int)
            and receipt.get("height", 0) > 0
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


def build_capture_receipt(
    result: Mapping[str, Any],
    persisted: Mapping[str, Any],
    *,
    plan_path: Path,
    event: Mapping[str, Any],
    output: Path,
) -> dict[str, Any]:
    if not in_memory_strict_valid(result):
        raise ValueError("The IAF result lacks complete two-pass evidence")
    metadata = result["output_metadata"]
    rows = persisted.get("results")
    if not isinstance(rows, list):
        raise TypeError("The persisted IAF artifact lacks records")
    screenshots = persisted.get("output_metadata", {}).get("screenshots")
    screenshots_ok, images = image_evidence(output, screenshots)
    if not screenshots_ok or not marker_valid(output):
        raise ValueError("The persisted IAF artifact lacks bound image evidence")
    record_capture: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise TypeError("The persisted IAF artifact contains a malformed row")
        abstract = row.get("abstract")
        if not isinstance(abstract, str) or not abstract:
            raise ValueError("The persisted IAF artifact lost a full abstract")
        record_capture.append(
            {
                "paper_id": row.get("paperId"),
                "abstract_characters": len(abstract),
                "abstract_sha256": digest_text(abstract),
                "abstract_source": row.get("abstract_source"),
                "source_publication_type": row.get("sourcePublicationType"),
                "document_type": row.get("documentType"),
            }
        )
    marker = marker_path(output)
    return {
        "schema_version": CAPTURE_SCHEMA,
        "created_at_utc": now(),
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "event_id": event["event_id"],
        "parent_event_id": event["parent_event_id"],
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "query": event["query"],
        "query_sha256": event["query_sha256"],
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "artifact": relative(output),
        "artifact_sha256": digest(output),
        "artifact_bytes": output.stat().st_size,
        "artifact_commit_marker": {
            "path": marker.name,
            "sha256": digest(marker),
        },
        "source_total": result["total"],
        "retained_record_count": len(rows),
        "raw_ordered_paper_ids": copy.deepcopy(metadata["ordered_paper_ids"]),
        "raw_ordered_paper_ids_sha256": metadata["ordered_paper_ids_sha256"],
        "retained_ordered_paper_ids": copy.deepcopy(
            metadata["in_scope_ordered_paper_ids"]
        ),
        "retained_ordered_paper_ids_sha256": metadata[
            "in_scope_ordered_paper_ids_sha256"
        ],
        "pass_reports": copy.deepcopy(metadata["pass_reports"]),
        "two_pass_order_verified": metadata["two_pass_order_verified"],
        "two_pass_capture_verified": metadata["two_pass_capture_verified"],
        "detail_capture_complete": metadata["detail_capture_complete"],
        "detail_captures": copy.deepcopy(metadata["detail_captures"]),
        "date_filter_accounting": copy.deepcopy(metadata["date_filter_accounting"]),
        "screenshots": copy.deepcopy(screenshots),
        "screenshot_files": images,
        "record_capture": record_capture,
        "publication_type_projection": {
            "sourcePublicationType": SOURCE_PUBLICATION_TYPE,
            "documentType": DOCUMENT_TYPE,
            "basis": PUBLICATION_TYPE_SOURCE,
            "reviewer_publication_type_inferred": False,
        },
        "complete": True,
    }


def save_failure(
    adapter: Any,
    args: argparse.Namespace,
    event: Mapping[str, Any],
    error: Exception,
    prisma_context: Mapping[str, Any] | None,
) -> None:
    output = Path(args.output_path).expanduser().resolve()
    failure = adapter.error_result(
        event["query"],
        error,
        query_mode="raw_query",
        limit=args.limit,
        partition_by=args.partition_by,
        year_start=args.year_start,
        year_end=args.year_end,
        date_start=args.date_start,
        date_end=args.date_end,
        max_pages=args.max_pages,
        page_size=args.page_size,
        passes=args.passes,
        timeout_seconds=args.timeout_seconds,
        page_delay_seconds=args.page_delay_seconds,
        retries=args.retries,
        count_only=args.count_only,
        require_complete=args.require_complete,
    )
    marked = adapter.mark_non_mergeable(
        failure,
        source=adapter.SOURCE_NAME,
        reason="Failed final IAF source cell. Do not merge this artifact.",
        prisma_context=adapter._error_prisma_context(prisma_context),
    )
    adapter._save_search_result(output, marked)


def run_cell(
    plan_path: Path,
    output_root: Path,
    event_id: str,
) -> int:
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid IAF final plan: " + ", ".join(errors))
    event = next(
        (item for item in plan["events"] if item.get("event_id") == event_id), None
    )
    if event is None:
        raise ValueError(f"Unknown final IAF event: {event_id}")
    output = output_root / event["output"]
    capture = capture_receipt_path(output_root, event)
    occupied = (output, marker_path(output), *screenshot_paths(output), capture)
    if any(path.exists() or path.is_symlink() for path in occupied):
        raise FileExistsError(f"Refusing to overwrite final IAF event {event_id}")
    output.parent.mkdir(parents=True, exist_ok=True)
    adapter = load_adapter()
    args = adapter_arguments(adapter, event, plan, output)
    prisma_context: Mapping[str, Any] | None = None
    try:
        prisma_context = adapter.configure_prisma_search_run_from_args(
            args,
            adapter_id=adapter.ADAPTER_ID,
            adapter_version=adapter.ADAPTER_VERSION,
            adapter_script=ADAPTER,
        )
        executed, query_mode, rows, operators = adapter.validate_cli_args(args)
        if executed != event["query"] or query_mode != "raw_query":
            raise ValueError("The adapter execution differs from the planned IAF cell")
        result = adapter.search_iaf_digital_library(
            args.query,
            wizard_rows=rows if query_mode == "typed_wizard" else None,
            operators=operators if query_mode == "typed_wizard" else None,
            limit=args.limit,
            max_pages=args.max_pages,
            page_size=args.page_size,
            passes=args.passes,
            partition_by=args.partition_by,
            year_start=args.year_start,
            year_end=args.year_end,
            date_start=args.date_start,
            date_end=args.date_end,
            timeout_seconds=args.timeout_seconds,
            page_delay_seconds=args.page_delay_seconds,
            retries=args.retries,
            count_only=args.count_only,
            require_complete=args.require_complete,
            cdp_url=args.cdp_url,
            target_id=args.target_id,
            headless=args.headless,
            chrome_executable=args.chrome_executable,
            prisma_context=prisma_context,
            screenshot_paths=args.screenshot_paths,
        )
        adapter.assert_complete_iaf_result(result)
        capture_counts = project_records(result)
        adapter.assert_complete_iaf_result(result)
        if not in_memory_strict_valid(result):
            raise ValueError("The final IAF cell failed strict two-pass validation")
        adapter._save_search_result(output, result)
        persisted = load(output)
        receipt = build_capture_receipt(
            result,
            persisted,
            plan_path=plan_path,
            event=event,
            output=output,
        )
        write_new(capture, receipt)
        print(
            json.dumps(
                {
                    "event_id": event_id,
                    "status": "complete",
                    "source_total": result["total"],
                    "retained": capture_counts["records"],
                    "full_abstracts": capture_counts["full_abstracts"],
                    "publication_type": SOURCE_PUBLICATION_TYPE,
                }
            ),
            flush=True,
        )
        return 0
    except Exception as error:  # noqa: BLE001 - final cell retains a failure artifact.
        if not output.exists() and not output.is_symlink():
            try:
                source_error = (
                    error
                    if isinstance(error, adapter.IAFDigitalLibraryError)
                    else adapter.IAFDigitalLibraryBrowserError(
                        "Unexpected final IAF browser workflow failure"
                    )
                )
                if source_error is not error:
                    source_error.__cause__ = error
                save_failure(adapter, args, event, source_error, prisma_context)
            except Exception as save_error:  # noqa: BLE001
                print(
                    f"iaf_final_failure_artifact_failed:{type(save_error).__name__}",
                    file=sys.stderr,
                )
        print(f"iaf_final_cell_failed:{type(error).__name__}", file=sys.stderr)
        return 1


def record_capture_summary(rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list):
        return {
            "valid": False,
            "records": 0,
            "full_abstract_count": 0,
            "missing_abstract_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
        }
    valid = True
    full_abstracts = 0
    missing_abstracts = 0
    missing_types = 0
    types: Counter[str] = Counter()
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            valid = False
            continue
        paper_id = row.get("paperId")
        abstract = row.get("abstract")
        if not isinstance(paper_id, str) or not paper_id:
            valid = False
        else:
            ids.append(paper_id)
        if (
            isinstance(abstract, str)
            and bool(abstract.strip())
            and row.get("abstract_source") == ABSTRACT_SOURCE
            and row.get("abstract_not_available") is not True
        ):
            full_abstracts += 1
        else:
            missing_abstracts += 1
            valid = False
        source_type = row.get("sourcePublicationType")
        document_type = row.get("documentType")
        if (
            source_type == SOURCE_PUBLICATION_TYPE
            and document_type == DOCUMENT_TYPE
            and row.get("sourcePublicationTypeSource") == PUBLICATION_TYPE_SOURCE
            and "publication_type" not in row
        ):
            types[str(source_type)] += 1
        else:
            missing_types += 1
            valid = False
    if len(ids) != len(set(ids)):
        valid = False
    return {
        "valid": valid,
        "records": len(rows),
        "full_abstract_count": full_abstracts,
        "missing_abstract_count": missing_abstracts,
        "publication_type_counts": dict(sorted(types.items())),
        "missing_publication_type_count": missing_types,
        "ordered_paper_ids": ids,
        "ordered_paper_ids_sha256": sequence_digest(ids),
    }


def capture_receipt_valid(
    receipt: Mapping[str, Any],
    *,
    path: Path,
    plan_path: Path,
    event: Mapping[str, Any],
    rows: Sequence[Any],
) -> bool:
    raw_ids = receipt.get("raw_ordered_paper_ids")
    retained_ids = receipt.get("retained_ordered_paper_ids")
    reports = receipt.get("pass_reports")
    captures = receipt.get("record_capture")
    if (
        receipt.get("schema_version") != CAPTURE_SCHEMA
        or receipt.get("complete") is not True
        or receipt.get("event_id") != event["event_id"]
        or receipt.get("partition_id") != event["partition_id"]
        or receipt.get("cell_id") != event["cell_id"]
        or receipt.get("query") != event["query"]
        or receipt.get("query_sha256") != event["query_sha256"]
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("artifact_sha256") != digest(path)
        or receipt.get("artifact_bytes") != path.stat().st_size
        or not isinstance(raw_ids, list)
        or len(raw_ids) != receipt.get("source_total")
        or receipt.get("raw_ordered_paper_ids_sha256") != sequence_digest(raw_ids)
        or not isinstance(retained_ids, list)
        or retained_ids != [row.get("paperId") for row in rows if isinstance(row, Mapping)]
        or receipt.get("retained_ordered_paper_ids_sha256")
        != sequence_digest(retained_ids)
        or receipt.get("retained_record_count") != len(rows)
        or receipt.get("two_pass_order_verified") is not True
        or receipt.get("two_pass_capture_verified") is not True
        or receipt.get("detail_capture_complete") is not True
        or not isinstance(reports, list)
        or len(reports) != PASSES
        or not isinstance(captures, list)
        or len(captures) != len(rows)
    ):
        return False
    pass_capture: str | None = None
    for report in reports:
        if (
            not isinstance(report, Mapping)
            or report.get("ordered_paper_ids") != raw_ids
            or report.get("ordered_paper_ids_sha256") != sequence_digest(raw_ids)
            or not report.get("capture_sha256")
        ):
            return False
        if pass_capture is None:
            pass_capture = str(report["capture_sha256"])
        elif report.get("capture_sha256") != pass_capture:
            return False
    for row, capture in zip(rows, captures, strict=True):
        if not isinstance(row, Mapping) or not isinstance(capture, Mapping):
            return False
        abstract = row.get("abstract")
        if (
            not isinstance(abstract, str)
            or capture.get("paper_id") != row.get("paperId")
            or capture.get("abstract_characters") != len(abstract)
            or capture.get("abstract_sha256") != digest_text(abstract)
            or capture.get("abstract_source") != ABSTRACT_SOURCE
            or capture.get("source_publication_type") != SOURCE_PUBLICATION_TYPE
            or capture.get("document_type") != DOCUMENT_TYPE
        ):
            return False
    marker = receipt.get("artifact_commit_marker")
    return not (
        not isinstance(marker, Mapping)
        or marker.get("path") != marker_path(path).name
        or marker.get("sha256") != digest(marker_path(path))
    )


def artifact_summary(
    path: Path,
    capture_path: Path,
    event: Mapping[str, Any],
    plan: Mapping[str, Any],
    plan_path: Path,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        return {"valid": False, "artifact_written": False}
    try:
        value = load(path)
        capture = load(capture_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    coverage = prisma.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    publication_date = limits.get("publication_date")
    publication_date = (
        publication_date if isinstance(publication_date, Mapping) else {}
    )
    requested_dates = publication_date.get("requested")
    requested_dates = requested_dates if isinstance(requested_dates, Mapping) else {}
    counts = prisma.get("staged_counts")
    counts = counts if isinstance(counts, Mapping) else {}
    rows = value.get("results")
    capture_summary = record_capture_summary(rows)
    screenshots_ok, images = image_evidence(path, metadata.get("screenshots"))
    total = value.get("total")
    totals_ok = bool(
        isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 0
        and counts.get("source_reported_total") == total
        and counts.get("source_reported_total_status") == "reported"
        and counts.get("source_reported_total_exact") is True
        and counts.get("source_universe_total") == total
        and counts.get("local_match_count") == capture_summary["records"]
        and counts.get("records_exported") == capture_summary["records"]
        and counts.get("client_side_exclusions")
        == total - capture_summary["records"]
    )
    controls_ok = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and value.get("executed_query") == event["query"]
        and prisma.get("run_id") == event["event_id"]
        and prisma.get("review_id") == REVIEW_ID
        and prisma.get("strategy_reference") == plan["strategy_reference"]
        and prisma.get("strategy_version") == plan["strategy_version"]
        and prisma.get("phase") == PHASE
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("partition_id") == event["partition_id"]
        and adapter.get("adapter_id") == plan["adapter"]["id"]
        and adapter.get("adapter_version") == plan["adapter"]["version"]
        and adapter.get("script_sha256") == plan["adapter"]["sha256"]
        and strategy.get("executed_query") == event["query"]
        and requested_dates.get("start") == DATE_START
        and requested_dates.get("end") == DATE_END
        and requested_dates.get("inclusive") is True
        and limits.get("date_filter_mode") == "client_side_publication_date"
    )
    completion_ok = bool(
        metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("count_only") is False
        and metadata.get("merge_eligible") is True
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and prisma.get("report_readiness_reasons") == []
    )
    receipt_ok = bool(
        capture_path.is_file()
        and not capture_path.is_symlink()
        and isinstance(rows, list)
        and capture_receipt_valid(
            capture,
            path=path,
            plan_path=plan_path,
            event=event,
            rows=rows,
        )
    )
    valid = bool(
        controls_ok
        and completion_ok
        and totals_ok
        and capture_summary["valid"]
        and screenshots_ok
        and marker_valid(path)
        and receipt_ok
    )
    return {
        "valid": valid,
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "capture_receipt": relative(capture_path),
        "capture_receipt_sha256": digest(capture_path)
        if capture_path.is_file()
        else None,
        "source_total": total,
        "retained_record_count": capture_summary["records"],
        "client_side_exclusions": counts.get("client_side_exclusions"),
        "unresolved_exact_dates_retained": sum(
            isinstance(row, Mapping)
            and row.get("exactDateFilterStatus") == "unresolved"
            for row in (rows if isinstance(rows, list) else [])
        ),
        "ordered_paper_ids": capture_summary["ordered_paper_ids"],
        "ordered_paper_ids_sha256": capture_summary["ordered_paper_ids_sha256"],
        "controls_valid": controls_ok,
        "completion_valid": completion_ok,
        "totals_valid": totals_ok,
        "strict_capture_receipt_valid": receipt_ok,
        "screenshots_valid": screenshots_ok,
        "terminal_marker_valid": marker_valid(path),
        "record_capture": capture_summary,
        "screenshots": images,
    }


def run_final(
    plan_path: Path,
    output_root: Path,
    receipt_path: Path,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid IAF final plan: " + ", ".join(errors))
    if output_root.is_symlink():
        raise ValueError("The final IAF output root cannot be a symlink")
    output_root.mkdir(parents=True, exist_ok=True)
    for event in plan["events"]:
        output = output_root / event["output"]
        capture = capture_receipt_path(output_root, event)
        occupied = (output, marker_path(output), *screenshot_paths(output), capture)
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise FileExistsError(f"Final IAF cell path is occupied: {event['cell_id']}")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_root / event["output"]
        capture = capture_receipt_path(output_root, event)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(SCRIPT_PATH),
            "cell",
            "--plan",
            str(plan_path),
            "--output-root",
            str(output_root),
            "--event-id",
            str(event["event_id"]),
        ]
        child_started = now()
        try:
            completed = subprocess.run(
                command,
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
            exit_code: int | None = completed.returncode
            summary = artifact_summary(output, capture, event, plan, plan_path)
            diagnostic = (completed.stderr or "").strip().splitlines()
        except Exception as error:  # noqa: BLE001 - retain final runner outcome.
            exit_code = None
            summary = {
                "valid": False,
                "artifact_written": output.is_file(),
                "runner_failure": type(error).__name__,
            }
            diagnostic = [type(error).__name__]
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "parent_event_id": event["parent_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "started_at_utc": child_started,
            "completed_at_utc": now(),
            "success": success,
            "artifact": relative(output) if output.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            **summary,
        }
        if not success and diagnostic:
            outcome["diagnostic"] = diagnostic[-1][:300]
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "cell": event["cell_id"],
                    "position": index + 1,
                    "planned": len(plan["events"]),
                    "success": success,
                    "source_total": outcome.get("source_total"),
                    "retained": outcome.get("retained_record_count"),
                    "full_abstracts": outcome.get("record_capture", {}).get(
                        "full_abstract_count"
                    ),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == 158 and all(
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
        "record_projection": plan["record_projection"],
        "execution_policy": plan["execution_policy"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_source_cell_count": 158,
        "attempted_source_cell_count": len(outcomes),
        "accepted_source_cell_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "all_source_cells_attempted": len(outcomes) == 158,
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def successful_event_artifacts(
    plan: Mapping[str, Any],
    run: Mapping[str, Any],
    output_root: Path,
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]]:
    if run.get("schema_version") != RUN_SCHEMA or run.get("success") is not True:
        raise ValueError("The final IAF run is incomplete")
    outcome_map = {
        item.get("event_id"): item
        for item in run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    selected = []
    for event in plan["events"]:
        outcome = outcome_map.get(event["event_id"])
        path = output_root / event["output"]
        if not isinstance(outcome, Mapping) or outcome.get("success") is not True:
            raise ValueError(f"Final IAF event is incomplete: {event['cell_id']}")
        require_regular(path)
        selected.append((event, outcome, path, load(path)))
    return selected


def build_cell_declarations(
    plan_path: Path,
    receipt_path: Path,
    output_root: Path,
    output: Path,
) -> dict[str, Any]:
    plan = load(plan_path)
    run = load(receipt_path)
    if validate_plan(plan, verify_bindings=False):
        raise ValueError("The final IAF plan is invalid")
    selected = successful_event_artifacts(plan, run, output_root)
    cells = []
    for event, outcome, path, data in selected:
        rows = data["results"]
        run_id = data["output_metadata"]["prisma_search_run"]["run_id"]
        cells.append(
            {
                "source_id": SOURCE_ID,
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "parent_event_id": event["parent_event_id"],
                "source_run_id": run_id,
                "query": event["query"],
                "requested_query": event["query"],
                "executed_query": event["query"],
                "source_native_executed_query": event["query"],
                "artifact_sha256": outcome["artifact_sha256"],
                "artifact_byte_count": outcome["artifact_bytes"],
                "stable_ids": [row["paperId"] for row in rows],
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
        raise ValueError("Unexpected IAF cell-declaration schema")
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
        detail = (completed.stderr or completed.stdout or "").strip().splitlines()
        raise RuntimeError(
            "Could not create the IAF source-union receipt"
            + (f": {detail[-1]}" if detail else "")
        )
    return 0


def build_record_union(
    plan_path: Path,
    receipt_path: Path,
    output_root: Path,
    output: Path,
) -> dict[str, Any]:
    plan = load(plan_path)
    run = load(receipt_path)
    selected = successful_event_artifacts(plan, run, output_root)
    records: dict[str, dict[str, Any]] = {}
    input_artifacts: list[dict[str, Any]] = []
    partition_ids: dict[str, list[str]] = {partition: [] for partition in PARTITIONS}
    raw_total_sum = 0
    retained_total_sum = 0
    exclusion_sum = 0
    for event, outcome, path, data in selected:
        rows = data["results"]
        raw_total = data["total"]
        retained = len(rows)
        exclusions = raw_total - retained
        raw_total_sum += raw_total
        retained_total_sum += retained
        exclusion_sum += exclusions
        input_artifacts.append(
            {
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": relative(path),
                "artifact_sha256": outcome["artifact_sha256"],
                "raw_source_total": raw_total,
                "retained_record_count": retained,
                "client_side_exclusions": exclusions,
            }
        )
        for row in rows:
            paper_id = row["paperId"]
            partition_ids[event["partition_id"]].append(paper_id)
            item = records.setdefault(
                paper_id,
                {
                    "paperId": paper_id,
                    "discovery_cells": [],
                    "discovery_partitions": [],
                    "occurrence_count": 0,
                    "record": copy.deepcopy(row),
                },
            )
            item["occurrence_count"] += 1
            if event["cell_id"] not in item["discovery_cells"]:
                item["discovery_cells"].append(event["cell_id"])
            if event["partition_id"] not in item["discovery_partitions"]:
                item["discovery_partitions"].append(event["partition_id"])
            current = item["record"]
            if len(str(row.get("abstract") or "")) > len(
                str(current.get("abstract") or "")
            ):
                item["record"] = copy.deepcopy(row)
    union_rows = []
    for paper_id in sorted(records):
        item = records[paper_id]
        item["discovery_cells"].sort()
        item["discovery_partitions"].sort(key=PARTITIONS.index)
        union_rows.append(item)
    capture = record_capture_summary([item["record"] for item in union_rows])
    partition_unions = {
        partition: {
            "cell_count": CELL_COUNTS[partition],
            "source_event_record_count": len(partition_ids[partition]),
            "unique_paper_id_count": len(set(partition_ids[partition])),
            "duplicate_occurrences": len(partition_ids[partition])
            - len(set(partition_ids[partition])),
            "paper_ids": sorted(set(partition_ids[partition])),
            "paper_id_set_sha256": canonical_set_digest(partition_ids[partition]),
        }
        for partition in PARTITIONS
    }
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": "main",
        "purpose": (
            "Deduplicated final IAF source records with full abstracts and source publication types"
        ),
        "reviewer_publication_type_coding": "deferred to screening",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "input_artifacts": input_artifacts,
        "raw_source_event_total_sum": raw_total_sum,
        "client_side_exclusion_sum": exclusion_sum,
        "source_event_record_count": retained_total_sum,
        "unique_paper_id_count": len(union_rows),
        "cross_cell_duplicate_occurrences": retained_total_sum - len(union_rows),
        "paper_id_set_sha256": canonical_set_digest(list(records)),
        "records_with_full_abstract": capture["full_abstract_count"],
        "records_without_full_abstract": capture["missing_abstract_count"],
        "records_with_source_publication_type": sum(
            capture["publication_type_counts"].values()
        ),
        "records_missing_source_publication_type": capture[
            "missing_publication_type_count"
        ],
        "source_publication_type_counts": capture["publication_type_counts"],
        "partition_unions": partition_unions,
        "complete": capture["valid"],
        "records": union_rows,
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
    plan = load(plan_path)
    run = load(receipt_path)
    declarations = load(declarations_path)
    source_union = load(source_union_path)
    record_union = load(record_union_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_source_cell_count") != 158
    ):
        errors.append("run_receipt")
    if (
        declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA
        or declarations.get("plan_sha256") != digest(plan_path)
        or declarations.get("run_receipt_sha256") != digest(receipt_path)
        or len(declarations.get("expected_cells", [])) != 158
    ):
        errors.append("cell_declarations")
    try:
        selected = successful_event_artifacts(plan, run, output_root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"events:{type(error).__name__}")
        selected = []

    event_evidence: list[dict[str, Any]] = []
    retained_ids: list[str] = []
    retained_occurrences = 0
    raw_total_sum = 0
    exclusion_sum = 0
    unresolved_sum = 0
    screenshot_count = 0
    partition_ids: dict[str, list[str]] = {partition: [] for partition in PARTITIONS}
    outcome_map = {
        item.get("event_id"): item
        for item in run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    for event, _, path, data in selected:
        outcome = outcome_map[event["event_id"]]
        capture_path = capture_receipt_path(output_root, event)
        summary = artifact_summary(path, capture_path, event, plan, plan_path)
        if summary.get("valid") is not True or outcome.get("success") is not True:
            errors.append(f"event:{event['cell_id']}")
        if (
            outcome.get("artifact_sha256") != digest(path)
            or outcome.get("capture_receipt_sha256") != digest(capture_path)
        ):
            errors.append(f"artifact_binding:{event['cell_id']}")
        ids = summary.get("ordered_paper_ids", [])
        retained_ids.extend(ids)
        partition_ids[event["partition_id"]].extend(ids)
        retained_occurrences += summary.get("retained_record_count", 0)
        raw_total_sum += summary.get("source_total", 0)
        exclusion_sum += summary.get("client_side_exclusions", 0)
        unresolved_sum += summary.get("unresolved_exact_dates_retained", 0)
        screenshot_count += len(summary.get("screenshots", []))
        event_evidence.append(
            {
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": relative(path),
                "artifact_sha256": digest(path),
                "capture_receipt": relative(capture_path),
                "capture_receipt_sha256": digest(capture_path),
                "raw_source_total": summary.get("source_total"),
                "retained_record_count": summary.get("retained_record_count"),
                "client_side_exclusions": summary.get("client_side_exclusions"),
                "strict_two_pass_valid": summary.get(
                    "strict_capture_receipt_valid"
                ),
                "screenshots_valid": summary.get("screenshots_valid"),
                "full_abstract_count": summary.get("record_capture", {}).get(
                    "full_abstract_count"
                ),
                "source_publication_types": summary.get("record_capture", {}).get(
                    "publication_type_counts"
                ),
            }
        )

    union_source = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    source_union_valid = bool(
        source_union.get("review_namespace") == "main"
        and source_union.get("review_id") == REVIEW_ID
        and source_union.get("strategy_reference") == plan["strategy_reference"]
        and source_union.get("strategy_version") == plan["strategy_version"]
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and source_union.get("artifact_count") == 158
        and union_source.get("event_total_sum") == retained_occurrences
        and set(union_source.get("stable_record_ids", [])) == set(retained_ids)
    )
    if not source_union_valid:
        errors.append("source_union")
    cell_unions = source_union.get("cell_unions", {}).get(SOURCE_ID, {})
    for partition in PARTITIONS:
        cell_union = cell_unions.get(partition, {})
        if (
            cell_union.get("cell_count") != CELL_COUNTS[partition]
            or set(cell_union.get("stable_record_ids", []))
            != set(partition_ids[partition])
        ):
            errors.append(f"source_union_cell:{partition}")

    records = record_union.get("records")
    record_union_valid = bool(
        record_union.get("schema_version") == RECORD_UNION_SCHEMA
        and record_union.get("plan_sha256") == digest(plan_path)
        and record_union.get("run_receipt_sha256") == digest(receipt_path)
        and record_union.get("raw_source_event_total_sum") == raw_total_sum
        and record_union.get("client_side_exclusion_sum") == exclusion_sum
        and record_union.get("source_event_record_count") == retained_occurrences
        and record_union.get("unique_paper_id_count") == len(set(retained_ids))
        and record_union.get("records_with_full_abstract") == len(set(retained_ids))
        and record_union.get("records_without_full_abstract") == 0
        and record_union.get("records_with_source_publication_type")
        == len(set(retained_ids))
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("source_publication_type_counts")
        == {SOURCE_PUBLICATION_TYPE: len(set(retained_ids))}
        and record_union.get("complete") is True
        and isinstance(records, list)
        and len(records) == len(set(retained_ids))
    )
    if not record_union_valid:
        errors.append("record_union")
    partition_unions = record_union.get("partition_unions", {})
    for partition in PARTITIONS:
        entry = partition_unions.get(partition, {})
        if (
            entry.get("cell_count") != CELL_COUNTS[partition]
            or entry.get("unique_paper_id_count") != len(set(partition_ids[partition]))
            or entry.get("paper_ids") != sorted(set(partition_ids[partition]))
            or entry.get("unique_paper_id_count", 101) > 100
        ):
            errors.append(f"partition_union:{partition}")

    complete = bool(len(event_evidence) == 158 and not errors)
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
        "adapter": plan["adapter"],
        "record_projection": plan["record_projection"],
        "accepted_source_cell_count": len(event_evidence),
        "events": event_evidence,
        "stable_id_union": {
            "raw_source_event_total_sum": raw_total_sum,
            "client_side_exclusion_sum": exclusion_sum,
            "retained_source_event_record_count": retained_occurrences,
            "unique_paper_id_count": len(set(retained_ids)),
            "cross_cell_duplicate_occurrences": retained_occurrences
            - len(set(retained_ids)),
            "paper_id_set_sha256": canonical_set_digest(retained_ids),
        },
        "partition_unions": copy.deepcopy(partition_unions),
        "record_capture": {
            "full_abstracts_required": True,
            "source_publication_types_required": True,
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
        "strict_execution": {
            "two_pass_cell_count": len(event_evidence),
            "automatic_screenshot_count": screenshot_count,
            "expected_automatic_screenshot_count": 316,
            "all_capture_receipts_valid": all(
                event.get("strict_two_pass_valid") is True
                for event in event_evidence
            ),
            "all_screenshots_valid": all(
                event.get("screenshots_valid") is True for event in event_evidence
            ),
        },
        "cutoff": {
            **plan["cutoff"],
            "unresolved_exact_dates_retained_occurrences": unresolved_sum,
        },
    }
    write_new(output, assessment)
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)

    cell_parser = commands.add_parser("cell")
    cell_parser.add_argument("--plan", type=Path, required=True)
    cell_parser.add_argument("--output-root", type=Path, required=True)
    cell_parser.add_argument("--event-id", required=True)

    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-root", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument(
        "--settle-seconds", type=float, default=INTER_EVENT_DELAY_SECONDS
    )

    declarations_parser = commands.add_parser("cell-declarations")
    declarations_parser.add_argument("--plan", type=Path, required=True)
    declarations_parser.add_argument("--receipt", type=Path, required=True)
    declarations_parser.add_argument("--output-root", type=Path, required=True)
    declarations_parser.add_argument("--output", type=Path, required=True)

    source_union_parser = commands.add_parser("source-union")
    source_union_parser.add_argument("--plan", type=Path, required=True)
    source_union_parser.add_argument("--receipt", type=Path, required=True)
    source_union_parser.add_argument("--output-root", type=Path, required=True)
    source_union_parser.add_argument("--cell-declarations", type=Path, required=True)
    source_union_parser.add_argument("--output", type=Path, required=True)

    record_union_parser = commands.add_parser("record-union")
    record_union_parser.add_argument("--plan", type=Path, required=True)
    record_union_parser.add_argument("--receipt", type=Path, required=True)
    record_union_parser.add_argument("--output-root", type=Path, required=True)
    record_union_parser.add_argument("--output", type=Path, required=True)

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
            write_new(args.output, build_plan())
            return 0
        if args.command == "cell":
            return run_cell(args.plan, args.output_root, args.event_id)
        if args.command == "run":
            if args.settle_seconds < 0:
                raise ValueError("Settle time cannot be negative")
            return run_final(
                args.plan, args.output_root, args.receipt, args.settle_seconds
            )
        if args.command == "cell-declarations":
            build_cell_declarations(
                args.plan, args.receipt, args.output_root, args.output
            )
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
    except (OSError, RuntimeError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"iaf_final_direct_failed:{type(error).__name__}:{error}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
