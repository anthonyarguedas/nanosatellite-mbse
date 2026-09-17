#!/usr/bin/env python3
"""Plan, execute, and assess final Springer Nature Link direct searches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from collections import Counter
from collections.abc import Mapping
from datetime import date, datetime, timezone
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.parse import urlparse


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_springer_link.py"
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
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/springer-nature-link/scripts/springer_nature_link_pilot004/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/springer-nature-link/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-springer-nature-link-final-direct-plan/v1"
RUN_SCHEMA = "slr1-springer-nature-link-final-direct-run/v1"
CELL_DECLARATIONS_SCHEMA = "slr1-springer-nature-link-final-direct-cell-declarations/v1"
ASSESSMENT_SCHEMA = "slr1-springer-nature-link-final-direct-assessment/v1"

SOURCE = "Springer Nature Link"
SOURCE_ID = "springer_nature_link"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-springer-nature-link-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
LANGUAGE = "En"
SORT = "oldestFirst"
PASSES = 2
LIMIT = 1000
MAX_PAGES = 50
TIMEOUT_SECONDS = 60
PAGE_DELAY_SECONDS = 0.1
UNSTABLE_B2_YEARS = (2021, 2022, 2024)
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "27b0ba8c6030d4e0cd36060375bb032a5431cd77d39c3b2e478d1c16342f0f5e"
)
SPRINGER_MARKER_SCHEMA = "springer_normal_output_commit_v1"
SPRINGER_SCREENSHOT_SCHEMA = "springer-automatic-screenshots/v1"

PARTITION_BRANCHES = {
    "A1": "P AND E_H AND M_H",
    "A3": "P AND E_H AND M_B",
    "B1": "P AND M_H",
    "BG1": "P AND G_model",
    "BG2": "P AND G_structure",
    "BC1": "P AND C1",
    "BT2": "P AND M_B AND T_precise",
}


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


def require_regular(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Expected a regular file: {path}")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    """Write one JSON artifact without replacing an existing path."""
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
        raise RuntimeError("Cannot determine the Springer adapter version")
    return match.group(1)


def load_queries() -> Any:
    require_regular(QUERY_SNAPSHOT)
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted Springer query snapshot changed")
    module_name = "slr1_springer_final_direct_queries"
    spec = importlib.util.spec_from_file_location(module_name, QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted Springer partition schedule changed")
    if tuple(module.WILDCARD_SCHEDULE) != PARTITIONS:
        raise RuntimeError("The accepted Springer wildcard schedule changed")
    if len(module.WILDCARD_A2_MB_CHUNK_CELLS) != 4:
        raise RuntimeError("The accepted Springer A2 source-cell schedule changed")
    if len(module.WILDCARD_B2_BOOLEAN_CELLS) != 4:
        raise RuntimeError("The accepted Springer B2 source-cell schedule changed")
    return module


def source_cell_name(partition_id: str, cell_id: str) -> str:
    return partition_id if cell_id == "direct" else f"{partition_id}-{cell_id}"


def event_id(partition_id: str, cell_id: str) -> str:
    return f"final-main-{source_cell_name(partition_id, cell_id)}-springer-nature-link-001"


def parent_event_id(partition_id: str) -> str:
    return f"final-main-{partition_id}-springer-nature-link-001"


def date_window_for_year(year: int | None) -> tuple[str, str, int, int]:
    if year is None:
        return DATE_START, DATE_END, 2011, 2026
    start = max(date.fromisoformat(DATE_START), date(year, 1, 1))
    end = min(date.fromisoformat(DATE_END), date(year, 12, 31))
    if start > end:
        raise ValueError(f"Source year {year} falls outside the final date window")
    return start.isoformat(), end.isoformat(), year, year


def make_event(
    *,
    partition_id: str,
    cell_id: str,
    branch: str,
    query: str,
    strategy_version: str,
    source_year: int | None = None,
) -> dict[str, Any]:
    date_start, date_end, source_year_start, source_year_end = date_window_for_year(
        source_year
    )
    output_filename = f"{source_cell_name(partition_id, cell_id)}.json"
    return {
        "event_id": event_id(partition_id, cell_id),
        "parent_event_id": parent_event_id(partition_id),
        "event_kind": "final",
        "review_namespace": REVIEW_NAMESPACE,
        "source_id": SOURCE_ID,
        "partition_id": partition_id,
        "cell_id": cell_id,
        "branch": branch,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "population_wildcard_count": query.count("*"),
        "output_filename": output_filename,
        "date_start": date_start,
        "date_end": date_end,
        "source_year_start": source_year_start,
        "source_year_end": source_year_end,
        "source_year_partition": source_year,
        "language": LANGUAGE,
        "sort": SORT,
        "passes": PASSES,
        "limit": LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": TIMEOUT_SECONDS,
        "page_delay_seconds": PAGE_DELAY_SECONDS,
        "require_complete": True,
        "count_only": False,
        "full_abstracts": True,
        "source_document_types": True,
        "strategy_version": strategy_version,
    }


def planned_events(strategy_version: str) -> list[dict[str, Any]]:
    queries = load_queries()
    events: list[dict[str, Any]] = []

    events.append(
        make_event(
            partition_id="A1",
            cell_id="direct",
            branch=PARTITION_BRANCHES["A1"],
            query=queries.WILDCARD_SCHEDULE["A1"],
            strategy_version=strategy_version,
        )
    )

    a2_mh = next(
        cell for cell in queries.WILDCARD_A2_CELLS if cell.get("cell_id") == "mh"
    )
    events.append(
        make_event(
            partition_id="A2",
            cell_id=str(a2_mh["cell_id"]),
            branch=str(a2_mh["branch"]),
            query=str(a2_mh["query"]),
            strategy_version=strategy_version,
        )
    )
    for cell in queries.WILDCARD_A2_MB_CHUNK_CELLS:
        events.append(
            make_event(
                partition_id="A2",
                cell_id=str(cell["cell_id"]),
                branch=str(cell["branch"]),
                query=str(cell["query"]),
                strategy_version=strategy_version,
            )
        )

    for partition_id in ("A3", "B1"):
        events.append(
            make_event(
                partition_id=partition_id,
                cell_id="direct",
                branch=PARTITION_BRANCHES[partition_id],
                query=queries.WILDCARD_SCHEDULE[partition_id],
                strategy_version=strategy_version,
            )
        )

    for source_year in range(2011, 2027):
        if source_year in UNSTABLE_B2_YEARS:
            for cell in queries.WILDCARD_B2_BOOLEAN_CELLS:
                base_cell_id = str(cell["cell_id"])
                events.append(
                    make_event(
                        partition_id="B2",
                        cell_id=f"year-{source_year}-{base_cell_id}",
                        branch=f"{cell['branch']}; source year {source_year}",
                        query=str(cell["query"]),
                        strategy_version=strategy_version,
                        source_year=source_year,
                    )
                )
        else:
            events.append(
                make_event(
                    partition_id="B2",
                    cell_id=f"year-{source_year}",
                    branch=f"P AND M_B AND R; source year {source_year}",
                    query=queries.WILDCARD_SCHEDULE["B2"],
                    strategy_version=strategy_version,
                    source_year=source_year,
                )
            )

    for partition_id in ("BG1", "BG2", "BC1", "BT2"):
        events.append(
            make_event(
                partition_id=partition_id,
                cell_id="direct",
                branch=PARTITION_BRANCHES[partition_id],
                query=queries.WILDCARD_SCHEDULE[partition_id],
                strategy_version=strategy_version,
            )
        )

    if len(events) != 37:
        raise RuntimeError("The accepted Springer final source-cell schedule changed")
    return events


def binding_paths() -> tuple[Path, ...]:
    return (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )


def build_plan() -> dict[str, Any]:
    strategy_version = repository_head()
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
        "concept_schedule_commit": load_queries().PROTOCOL_COMMIT,
        "accepted_translation_snapshot": relative(QUERY_SNAPSHOT),
        "accepted_translation_snapshot_sha256": digest(QUERY_SNAPSHOT),
        "source_union_expected_partitions": list(PARTITIONS),
        "source_union_expected_sources": [SOURCE_ID],
        "cutoff": {
            "exact_common_cutoff": DATE_END,
            "source_date_start": DATE_START,
            "source_date_end": DATE_END,
            "source_precision": "year_filter_with_rendered_detail_exact_day_reconciliation",
            "screening_requirement": (
                "Retain unresolved exact detail dates. Exclude only a date proved "
                "outside the inclusive common evidence window."
            ),
        },
        "source_configuration": {
            "platform": "Full Springer Nature Link platform",
            "url": "https://link.springer.com/search",
            "field": "Raw Keywords over title, abstract, and body text",
            "language_filter": LANGUAGE,
            "publication_type_filter": None,
            "peer_review_filter": None,
            "access_filter": None,
            "full_text_filter": None,
            "content_type_filter": None,
            "discipline_filter": None,
            "subdiscipline_filter": None,
            "taxonomy_filter": None,
            "controlled_vocabulary_supplement": None,
            "sort": "Date published (old to new)",
            "proximity_operators": False,
            "pair_expansion": False,
            "population_wildcards": ["CubeSat*", "nanosat*", "SmallSat*"],
        },
        "translation": {
            "literal": "one straight-double-quoted token or ordered phrase",
            "boolean": "uppercase AND and OR with full parentheses",
            "a2": "one M_H cell and four fixed contiguous M_B cells",
            "b2": (
                "one source-year cell for 2011-2020, 2023, 2025, and 2026, "
                "plus a fixed two-by-two M_B and R union in 2021, 2022, and 2024"
            ),
            "source_year_partitions": list(range(2011, 2027)),
            "unstable_b2_years": list(UNSTABLE_B2_YEARS),
            "wildcards_replaced_only": ["CubeSat", "CubeSats", "nanosat", "nanosats", "nanosatellite", "nanosatellites", "SmallSat", "SmallSats"],
        },
        "capture_contract": {
            "two_complete_canonical_card_path_passes": True,
            "automatic_screenshots": True,
            "full_abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "source_method": "matching rendered canonical Springer Link content page",
                "source_omission_policy": (
                    "Retain an empty abstract only with abstract_not_available=true "
                    "after the canonical content page exposes no abstract."
                ),
            },
            "publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "source_method": "rendered Springer Link result-card content type",
                "filter_applied": None,
                "reviewer_coding": "Do not infer screening publication_type from source metadata.",
            },
            "detail_route_contract": (
                "Keep the raw Link card path as identity. Accept only the same-DOI "
                "book-to-referencework alias and the approved Link 10.1038 to Nature "
                "canonical metadata URL."
            ),
        },
        "execution_policy": {
            "one_source_execution_per_cell": True,
            "continue_after_source_cell_failure": True,
            "retry_policy": "none within this final plan",
            "failed_events_are_nonmergeable": True,
            "corrective_run_required_after_any_failure": True,
            "count_only": False,
            "skip_full_abstracts": False,
            "target_identifiers_retained": False,
        },
        "adapter": {
            "id": "search_springer_link",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "bindings": {
            "files": {relative(path): digest(path) for path in binding_paths()}
        },
        "events": planned_events(strategy_version),
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
    strategy_version = plan.get("repository_head_at_predeclaration")
    if not isinstance(strategy_version, str) or re.fullmatch(r"[0-9a-f]{40}", strategy_version) is None:
        errors.append("strategy_version")
        strategy_version = ""
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("event_kind") != "final"
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("accepted_translation_snapshot") != relative(QUERY_SNAPSHOT)
        or plan.get("accepted_translation_snapshot_sha256") != EXPECTED_QUERY_SNAPSHOT_SHA256
        or plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("source_union_expected_sources") != [SOURCE_ID]
    ):
        errors.append("identity")
    cutoff = plan.get("cutoff")
    if not isinstance(cutoff, Mapping) or (
        cutoff.get("exact_common_cutoff") != DATE_END
        or cutoff.get("source_date_start") != DATE_START
        or cutoff.get("source_date_end") != DATE_END
    ):
        errors.append("cutoff")
    configuration = plan.get("source_configuration")
    expected_configuration = {
        "platform": "Full Springer Nature Link platform",
        "url": "https://link.springer.com/search",
        "field": "Raw Keywords over title, abstract, and body text",
        "language_filter": LANGUAGE,
        "publication_type_filter": None,
        "peer_review_filter": None,
        "access_filter": None,
        "full_text_filter": None,
        "content_type_filter": None,
        "discipline_filter": None,
        "subdiscipline_filter": None,
        "taxonomy_filter": None,
        "controlled_vocabulary_supplement": None,
        "sort": "Date published (old to new)",
        "proximity_operators": False,
        "pair_expansion": False,
        "population_wildcards": ["CubeSat*", "nanosat*", "SmallSat*"],
    }
    if not isinstance(configuration, Mapping) or any(
        configuration.get(key) != value for key, value in expected_configuration.items()
    ):
        errors.append("source_configuration")
    capture = plan.get("capture_contract")
    if not isinstance(capture, Mapping) or (
        capture.get("two_complete_canonical_card_path_passes") is not True
        or capture.get("automatic_screenshots") is not True
        or capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("normalized_field") != "abstract"
        or capture.get("publication_types", {}).get("required") is not True
        or capture.get("publication_types", {}).get("normalized_field") != "documentType"
        or capture.get("publication_types", {}).get("filter_applied") is not None
    ):
        errors.append("capture_contract")
    execution = plan.get("execution_policy")
    if not isinstance(execution, Mapping) or (
        execution.get("one_source_execution_per_cell") is not True
        or execution.get("continue_after_source_cell_failure") is not True
        or execution.get("retry_policy") != "none within this final plan"
        or execution.get("count_only") is not False
        or execution.get("skip_full_abstracts") is not False
    ):
        errors.append("execution_policy")
    events = plan.get("events")
    expected_events = planned_events(strategy_version) if strategy_version else []
    if events != expected_events:
        errors.append("source_cell_schedule")
    for event in events if isinstance(events, list) else []:
        query = event.get("query") if isinstance(event, Mapping) else None
        if not isinstance(query, str):
            continue
        if (
            query.count("*") != 3
            or "?" in query
            or "NEAR" in query.upper()
            or " W/" in query.upper()
            or " PRE/" in query.upper()
            or "~" in query
        ):
            errors.append(f"query_translation:{event.get('cell_id')}")
    if verify_bindings:
        adapter = plan.get("adapter")
        if not isinstance(adapter, Mapping) or (
            adapter.get("id") != "search_springer_link"
            or adapter.get("version") != adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_binding")
        files = plan.get("bindings", {}).get("files") if isinstance(plan.get("bindings"), Mapping) else None
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_digest in files.items():
                path = REPOSITORY_ROOT / str(name)
                if (
                    not path.is_file()
                    or path.is_symlink()
                    or not isinstance(expected_digest, str)
                    or digest(path) != expected_digest
                ):
                    errors.append(f"binding_changed:{name}")
    return errors


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.SPRINGER_COMMIT.json")


def screenshot_paths(path: Path) -> dict[str, Path]:
    return {
        "search_page": path.with_name(f"{path.stem}.search-page.png"),
        "results_page": path.with_name(f"{path.stem}.results-page.png"),
    }


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
    normalized = value.get("normalized_json")
    return bool(
        value.get("schema") == SPRINGER_MARKER_SCHEMA
        and isinstance(value.get("transaction_id"), str)
        and re.fullmatch(r"[0-9a-f]{64}", value["transaction_id"])
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def screenshot_evidence(path: Path, value: Any) -> tuple[bool, list[dict[str, Any]]]:
    receipt = value if isinstance(value, Mapping) else {}
    valid = True
    rows: list[dict[str, Any]] = []
    for kind, image in screenshot_paths(path).items():
        evidence = receipt.get(kind) if isinstance(receipt, Mapping) else None
        image_valid = False
        if image.is_file() and not image.is_symlink() and isinstance(evidence, Mapping):
            payload = image.read_bytes()
            image_valid = bool(
                payload.startswith(b"\x89PNG\r\n\x1a\n")
                and evidence.get("path") == image.name
                and evidence.get("sha256") == hashlib.sha256(payload).hexdigest()
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


def source_card_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "link.springer.com"
        or parsed.port is not None
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith("/")
    ):
        return None
    return parsed.path


def record_capture_summary(rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list):
        return {
            "valid": False,
            "retained_record_count": None,
            "full_abstract_count": 0,
            "source_abstract_not_available_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
            "paper_ids": [],
        }
    valid = True
    paper_ids: list[str] = []
    full_abstract_count = 0
    source_abstract_not_available_count = 0
    publication_types: Counter[str] = Counter()
    missing_publication_type_count = 0
    for row in rows:
        if not isinstance(row, Mapping):
            valid = False
            continue
        paper_id = row.get("paperId")
        abstract = row.get("abstract")
        abstract_not_available = row.get("abstract_not_available")
        document_type = row.get("documentType")
        if (
            not isinstance(paper_id, str)
            or not paper_id
            or not isinstance(abstract, str)
            or not isinstance(abstract_not_available, bool)
            or abstract_not_available != (not bool(abstract))
            or row.get("exactDateFilterStatus") not in {"included", "unresolved"}
            or not isinstance(row.get("sourceCardUrl"), str)
            or source_card_path(row.get("sourceCardUrl")) != paper_id
        ):
            valid = False
        if isinstance(paper_id, str):
            paper_ids.append(paper_id)
        if isinstance(abstract, str) and abstract:
            full_abstract_count += 1
        else:
            source_abstract_not_available_count += 1
        if isinstance(document_type, str) and document_type.strip():
            publication_types[document_type] += 1
        else:
            missing_publication_type_count += 1
            valid = False
    if len(paper_ids) != len(set(paper_ids)):
        valid = False
    return {
        "valid": valid,
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstract_count,
        "source_abstract_not_available_count": source_abstract_not_available_count,
        "publication_type_counts": dict(sorted(publication_types.items())),
        "missing_publication_type_count": missing_publication_type_count,
        "paper_ids": paper_ids,
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
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    coverage = prisma.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    staged_counts = prisma.get("staged_counts")
    staged_counts = staged_counts if isinstance(staged_counts, Mapping) else {}
    rows = value.get("results")
    capture = record_capture_summary(rows)
    screenshots_ok, screenshot_rows = screenshot_evidence(
        path, metadata.get("screenshots")
    )

    total = value.get("total")
    client_exclusions = staged_counts.get("client_side_exclusions")
    aliases = metadata.get("detail_route_aliases")
    aliases = aliases if isinstance(aliases, Mapping) else {}
    evidence = aliases.get("evidence")
    evidence = evidence if isinstance(evidence, list) else []
    date_status_counts = aliases.get("date_status_counts")
    date_status_counts = date_status_counts if isinstance(date_status_counts, Mapping) else {}
    alias_paths: list[str] = []
    route_evidence_valid = True
    for item in evidence:
        if not isinstance(item, Mapping):
            route_evidence_valid = False
            continue
        path_value = source_card_path(item.get("source_card_url"))
        if path_value is None or item.get("date_status") not in {
            "included",
            "unresolved",
            "excluded",
        }:
            route_evidence_valid = False
        elif path_value is not None:
            alias_paths.append(path_value)
    if len(alias_paths) != len(set(alias_paths)):
        route_evidence_valid = False

    dates_valid = bool(
        isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 0
        and isinstance(client_exclusions, int)
        and not isinstance(client_exclusions, bool)
        and client_exclusions >= 0
        and capture["retained_record_count"] is not None
        and capture["retained_record_count"] + client_exclusions == total
        and len(evidence) == total
        and len(alias_paths) == total
        and aliases.get("schema") == "springer-detail-route-aliases/v2"
        and aliases.get("raw_card_path_passes_reconciled") is True
        and aliases.get("date_input_mode") == "exact_dates"
        and aliases.get("date_start") == event.get("date_start")
        and aliases.get("date_end") == event.get("date_end")
        and date_status_counts.get("excluded") == client_exclusions
        and date_status_counts.get("included", 0) + date_status_counts.get("unresolved", 0)
        == capture["retained_record_count"]
        and sum(
            date_status_counts.get(key, 0)
            for key in ("excluded", "included", "unresolved", "not_applied")
        )
        == total
        and set(capture["paper_ids"])
        == {
            source_card_path(item.get("source_card_url"))
            for item in evidence
            if isinstance(item, Mapping) and item.get("date_status") in {"included", "unresolved"}
        }
    )

    not_applied_controls = (
        "content_types",
        "open_access",
        "disciplines",
        "subdisciplines",
        "sdgs",
        "book_accessibility",
        "content_type",
        "access",
        "venue",
        "discipline",
        "subdiscipline",
        "sdg",
    )
    controls_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and value.get("executed_query") == event.get("query")
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and metadata.get("normal_output_commit_required") is True
        and metadata.get("normal_output_commit_schema") == SPRINGER_MARKER_SCHEMA
        and metadata.get("normal_output_commit_state") == "marker_required"
        and strategy.get("executed_query") == event.get("query")
        and strategy.get("search_scope") == "whole_springer_nature_link_platform"
        and limits.get("date_start", {}).get("value") == event.get("date_start")
        and limits.get("date_end", {}).get("value") == event.get("date_end")
        and limits.get("language", {}).get("value") == LANGUAGE
        and limits.get("date_input_mode") == "exact_dates"
        and limits.get("year_start") == event.get("source_year_start")
        and limits.get("year_end") == event.get("source_year_end")
        and strategy.get("sort", {}).get("requested") == SORT
        and strategy.get("sort", {}).get("effective") == "Date published (old to new)"
        and all(limits.get(key, {}).get("state") == "not_applied" for key in not_applied_controls)
        and limits.get("facets_requested", {}).get("requested")
        == {
            "content_types": [],
            "open_access": False,
            "taxonomies": [],
            "disciplines": [],
            "subdisciplines": [],
            "sdgs": [],
            "book_accessibility": [],
        }
    )
    prisma_valid = bool(
        prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("partition_id") == event.get("partition_id")
        and adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
        and staged_counts.get("source_reported_total") == total
        and staged_counts.get("source_reported_total_exact") is True
        and staged_counts.get("raw_source_records") == total
        and staged_counts.get("client_side_exclusions") == client_exclusions
        and staged_counts.get("records_exported") == capture["retained_record_count"]
    )
    adapter_version_value = str(plan.get("adapter", {}).get("version", ""))
    observed_source_year_partition = metadata.get("source_year_partition")
    expected_source_year_partition = event.get("source_year_partition")
    source_year_partition_valid = bool(
        observed_source_year_partition == expected_source_year_partition
        if adapter_version_value.isdigit() and int(adapter_version_value) >= 23
        else observed_source_year_partition in {None, expected_source_year_partition}
    )
    recovery_count = metadata.get("detail_target_recovery_count")
    recovery_evidence_valid = bool(
        (
            isinstance(recovery_count, int)
            and not isinstance(recovery_count, bool)
            and recovery_count >= 0
        )
        if adapter_version_value.isdigit() and int(adapter_version_value) >= 18
        else recovery_count is None
        or (
            isinstance(recovery_count, int)
            and not isinstance(recovery_count, bool)
            and recovery_count >= 0
        )
    )
    screenshot_contract_valid = bool(
        isinstance(metadata.get("screenshots"), Mapping)
        and metadata["screenshots"].get("schema_version") == SPRINGER_SCREENSHOT_SCHEMA
        and metadata["screenshots"].get("automatic") is True
        and metadata["screenshots"].get("no_opt_out") is True
        and screenshots_ok
    )
    terminal_marker_valid = marker_valid(path)
    valid = bool(
        controls_valid
        and prisma_valid
        and dates_valid
        and route_evidence_valid
        and capture["valid"]
        and source_year_partition_valid
        and recovery_evidence_valid
        and screenshot_contract_valid
        and terminal_marker_valid
    )
    return {
        "artifact_written": True,
        "valid": valid,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "source_total": total,
        "retained_record_count": capture["retained_record_count"],
        "client_date_excluded_count": client_exclusions,
        "unresolved_exact_date_count": date_status_counts.get("unresolved"),
        "stable_source_card_path_count": len(alias_paths),
        "stable_source_card_paths_sha256": digest_ordered(alias_paths),
        "controls_valid": controls_valid,
        "prisma_valid": prisma_valid,
        "date_reconciliation_valid": dates_valid,
        "detail_route_evidence_valid": route_evidence_valid,
        "source_year_partition": observed_source_year_partition,
        "source_year_partition_valid": source_year_partition_valid,
        "detail_target_recovery_count": recovery_count,
        "detail_target_recovery_evidence_valid": recovery_evidence_valid,
        "full_abstract_count": capture["full_abstract_count"],
        "source_abstract_not_available_count": capture[
            "source_abstract_not_available_count"
        ],
        "abstract_field_complete": capture["valid"],
        "publication_type_counts": capture["publication_type_counts"],
        "missing_publication_type_count": capture["missing_publication_type_count"],
        "publication_type_field_complete": capture[
            "missing_publication_type_count"
        ]
        == 0,
        "record_paper_ids": capture["paper_ids"],
        "screenshots_valid": screenshot_contract_valid,
        "terminal_marker_valid": terminal_marker_valid,
        "screenshots": screenshot_rows,
    }


def cdp_is_loopback(value: str) -> bool:
    parsed = urlparse(value)
    return bool(
        parsed.scheme == "http"
        and parsed.hostname in {"127.0.0.1", "localhost"}
        and parsed.port is not None
        and not parsed.username
        and not parsed.password
        and not parsed.path.rstrip("/")
        and not parsed.query
        and not parsed.fragment
    )


def command_for(
    event: Mapping[str, Any], output: Path, plan: Mapping[str, Any], cdp_url: str
) -> list[str]:
    command = [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
        "--date-start",
        str(event["date_start"]),
        "--date-end",
        str(event["date_end"]),
        "--language",
        LANGUAGE,
        "--sort",
        SORT,
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--passes",
        str(event["passes"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
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
        source_cell_name(str(event["partition_id"]), str(event["cell_id"])),
        "--prisma-partition-description",
        (
            "Springer Nature Link final direct discovery partition "
            f"{event['partition_id']} source cell {event['cell_id']}"
        ),
    ]
    source_year_partition = event.get("source_year_partition")
    if source_year_partition is not None:
        date_end_index = command.index("--date-end") + 2
        command[date_end_index:date_end_index] = [
            "--source-year-partition",
            str(source_year_partition),
        ]
    return command


def output_paths_occupied(output: Path) -> bool:
    return any(
        candidate.exists() or candidate.is_symlink()
        for candidate in (output, marker_path(output), *screenshot_paths(output).values())
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
        raise ValueError("Invalid final Springer plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The final Springer output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_is_loopback(cdp_url):
        raise ValueError("Final Springer execution requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    started_at = now()
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for index, event in enumerate(plan["events"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        if output_paths_occupied(output):
            raise FileExistsError(
                f"Refusing to overwrite artifacts for {event['partition_id']} {event['cell_id']}"
            )
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                command_for(event, output, plan, cdp_url),
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            summary = artifact_summary(output, event, plan)
        except Exception as error:  # The receipt must retain every attempted cell.
            summary = {
                "artifact_written": output.is_file() and not output.is_symlink(),
                "valid": False,
                "runner_failure": type(error).__name__,
            }
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "parent_event_id": event["parent_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "success": success,
            "artifact": output.name if output.is_file() and not output.is_symlink() else None,
            "exit_code": exit_code,
            "source_command_attempt_count": 1,
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
                    "cell": event["cell_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": outcome.get("source_total"),
                    "retained_records": outcome.get("retained_record_count"),
                    "full_abstracts": outcome.get("full_abstract_count"),
                    "missing_types": outcome.get("missing_publication_type_count"),
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
        "target_identifier_retained": False,
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "planned_source_cell_count": len(plan["events"]),
        "attempted_source_cell_count": len(outcomes),
        "source_command_attempt_count": sum(
            outcome.get("source_command_attempt_count", 0) for outcome in outcomes
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


def successful_artifacts(
    plan: Mapping[str, Any], run: Mapping[str, Any], output_dir: Path
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]]:
    if run.get("schema_version") != RUN_SCHEMA or run.get("success") is not True:
        raise ValueError("The Springer final run receipt is incomplete")
    outcomes = {
        item.get("event_id"): item
        for item in run.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    selected: list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]] = []
    for event in plan["events"]:
        outcome = outcomes.get(event["event_id"])
        output = output_dir / str(event["output_filename"])
        if outcome is None or outcome.get("success") is not True:
            raise ValueError(f"Missing successful final source cell {event['cell_id']}")
        summary = artifact_summary(output, event, plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Invalid final Springer artifact {output}")
        selected.append((event, outcome, output, load(output)))
    return selected


def build_cell_declarations(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(plan_path)
    run = load(receipt_path)
    errors = validate_plan(plan, verify_bindings=False)
    if errors:
        raise ValueError("Invalid final Springer plan: " + ", ".join(errors))
    selected = successful_artifacts(plan, run, output_dir)
    cells: list[dict[str, Any]] = []
    for event, outcome, output, _artifact in selected:
        summary = artifact_summary(output, event, plan)
        cells.append(
            {
                "source_id": SOURCE_ID,
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "parent_event_id": event["parent_event_id"],
                "source_run_id": event["event_id"],
                "query": event["query"],
                "requested_query": event["query"],
                "executed_query": event["query"],
                "source_native_executed_query": event["query"],
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_byte_count": summary["artifact_bytes"],
                "stable_ids": summary["record_paper_ids"],
                "status": "complete",
                "report_ready": True,
                "artifact": relative(output),
                "artifact_outcome_sha256": outcome.get("artifact_sha256"),
            }
        )
    value = {
        "schema_version": CELL_DECLARATIONS_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "expected_cells": cells,
    }
    write_new(output_path, value)
    return 0


def create_source_union(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    declarations_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(plan_path)
    run = load(receipt_path)
    declarations = load(declarations_path)
    if declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA:
        raise ValueError("Unexpected Springer source-cell declaration schema")
    selected = successful_artifacts(plan, run, output_dir)
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *(str(output) for _event, _outcome, output, _artifact in selected),
        "--output-path",
        str(output_path),
        "--expected-partitions",
        *PARTITIONS,
        "--expected-sources",
        SOURCE_ID,
        "--review-namespace",
        REVIEW_NAMESPACE,
        "--expected-cells",
        str(declarations_path),
    ]
    completed = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0 or not output_path.is_file():
        raise RuntimeError("Could not create the Springer source-union receipt")
    return 0


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    declarations_path: Path,
    union_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(plan_path)
    run = load(receipt_path)
    declarations = load(declarations_path)
    source_union = load(union_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_source_cell_count") != len(plan["events"])
    ):
        errors.append("run_receipt")
    if (
        declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA
        or declarations.get("plan_sha256") != digest(plan_path)
        or declarations.get("run_receipt_sha256") != digest(receipt_path)
        or len(declarations.get("expected_cells", [])) != len(plan["events"])
    ):
        errors.append("cell_declarations")

    try:
        selected = successful_artifacts(plan, run, output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"events:{type(error).__name__}")
        selected = []

    event_evidence: list[dict[str, Any]] = []
    source_total_sum = 0
    raw_retained_records = 0
    client_excluded_records = 0
    unresolved_dates = 0
    full_abstracts = 0
    abstract_not_available = 0
    publication_types: Counter[str] = Counter()
    record_ids: list[str] = []
    screenshots: list[dict[str, Any]] = []
    for event, outcome, output, _artifact in selected:
        summary = artifact_summary(output, event, plan)
        if (
            outcome.get("success") is not True
            or summary.get("valid") is not True
            or outcome.get("artifact_sha256") != summary.get("artifact_sha256")
            or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
        ):
            errors.append(f"event:{event['cell_id']}")
        total = summary.get("source_total")
        retained = summary.get("retained_record_count")
        excluded = summary.get("client_date_excluded_count")
        if not all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in (total, retained, excluded)
        ):
            errors.append(f"count_shape:{event['cell_id']}")
        elif total != retained + excluded:
            errors.append(f"date_accounting:{event['cell_id']}")
        source_total_sum += total if isinstance(total, int) else 0
        raw_retained_records += retained if isinstance(retained, int) else 0
        client_excluded_records += excluded if isinstance(excluded, int) else 0
        unresolved = summary.get("unresolved_exact_date_count")
        unresolved_dates += unresolved if isinstance(unresolved, int) else 0
        full_abstracts += summary.get("full_abstract_count", 0)
        abstract_not_available += summary.get("source_abstract_not_available_count", 0)
        publication_types.update(summary.get("publication_type_counts", {}))
        record_ids.extend(summary.get("record_paper_ids", []))
        screenshots.extend(summary.get("screenshots", []))
        event_evidence.append(
            {
                "event_id": event["event_id"],
                "parent_event_id": event["parent_event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": relative(output),
                "artifact_sha256": summary.get("artifact_sha256"),
                "source_total": total,
                "retained_record_count": retained,
                "client_date_excluded_count": excluded,
                "unresolved_exact_date_count": unresolved,
                "full_abstract_count": summary.get("full_abstract_count"),
                "source_abstract_not_available_count": summary.get(
                    "source_abstract_not_available_count"
                ),
                "publication_type_counts": summary.get("publication_type_counts"),
                "missing_publication_type_count": summary.get(
                    "missing_publication_type_count"
                ),
                "all_retained_rows_have_abstract_field": summary.get(
                    "abstract_field_complete"
                ),
                "all_retained_rows_have_publication_type": summary.get(
                    "publication_type_field_complete"
                ),
                "stable_source_card_paths_sha256": summary.get(
                    "stable_source_card_paths_sha256"
                ),
                "screenshots": summary.get("screenshots"),
            }
        )

    union_source = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    source_union_valid = bool(
        source_union.get("schema_version") == "academic-search-source-union-receipt/v1"
        and source_union.get("review_namespace") == REVIEW_NAMESPACE
        and source_union.get("review_id") == REVIEW_ID
        and source_union.get("strategy_reference") == STRATEGY_REFERENCE
        and source_union.get("strategy_version")
        == plan.get("repository_head_at_predeclaration")
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("event_count") == len(plan["events"])
        and source_union.get("artifact_count") == len(plan["events"])
        and union_source.get("expected_partitions") == list(PARTITIONS)
        and union_source.get("completeness_status") == "complete"
        and union_source.get("failure_status") == "none"
        and union_source.get("event_total_sum") == source_total_sum
    )
    if not source_union_valid:
        errors.append("source_union")
    cell_unions = union_source.get("cell_unions", {})
    for partition_id in PARTITIONS:
        expected_count = sum(
            event["partition_id"] == partition_id for event in plan["events"]
        )
        if cell_unions.get(partition_id, {}).get("cell_count") != expected_count:
            errors.append(f"source_union_cell:{partition_id}")

    unique_ids = set(record_ids)
    all_capture_fields_complete = bool(
        len(selected) == len(plan["events"])
        and all(
            row.get("all_retained_rows_have_abstract_field") is True
            and row.get("all_retained_rows_have_publication_type") is True
            and row.get("missing_publication_type_count") == 0
            for row in event_evidence
        )
    )
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
        "source_cell_declarations": relative(declarations_path),
        "source_cell_declarations_sha256": digest(declarations_path),
        "source_union_receipt": relative(union_path),
        "source_union_receipt_sha256": digest(union_path),
        "adapter": plan["adapter"],
        "cutoff": plan["cutoff"],
        "source_cell_count": len(plan["events"]),
        "accepted_source_cell_count": len(selected),
        "source_record_occurrence_count": raw_retained_records,
        "source_client_date_excluded_occurrence_count": client_excluded_records,
        "source_total_occurrence_count": source_total_sum,
        "unique_retained_source_card_path_count": len(unique_ids),
        "unique_retained_source_card_path_set_sha256": digest_set(unique_ids),
        "full_abstract_occurrence_count": full_abstracts,
        "source_abstract_not_available_occurrence_count": abstract_not_available,
        "publication_type_occurrence_count": sum(publication_types.values()),
        "publication_type_counts": dict(sorted(publication_types.items())),
        "full_abstract_and_publication_type_capture_complete": bool(
            not errors and all_capture_fields_complete
        ),
        "unresolved_exact_date_occurrence_count": unresolved_dates,
        "screenshots_valid": all(item.get("valid") is True for item in screenshots),
        "source_union_valid": source_union_valid,
        "source_cells": event_evidence,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new(output_path, assessment)
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
    run_parser.add_argument("--settle-seconds", type=float, default=2.0)

    declarations_parser = subparsers.add_parser("build-cell-declarations")
    declarations_parser.add_argument("--plan", type=Path, required=True)
    declarations_parser.add_argument("--receipt", type=Path, required=True)
    declarations_parser.add_argument("--output-dir", type=Path, required=True)
    declarations_parser.add_argument("--output", type=Path, required=True)

    union_parser = subparsers.add_parser("source-union")
    union_parser.add_argument("--plan", type=Path, required=True)
    union_parser.add_argument("--receipt", type=Path, required=True)
    union_parser.add_argument("--output-dir", type=Path, required=True)
    union_parser.add_argument("--cell-declarations", type=Path, required=True)
    union_parser.add_argument("--output", type=Path, required=True)

    assess_parser = subparsers.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--cell-declarations", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan()
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid final Springer plan: " + ", ".join(errors))
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
    if args.command == "build-cell-declarations":
        return build_cell_declarations(
            args.plan, args.receipt, args.output_dir, args.output
        )
    if args.command == "source-union":
        return create_source_union(
            args.plan,
            args.receipt,
            args.output_dir,
            args.cell_declarations,
            args.output,
        )
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.output_dir,
            args.cell_declarations,
            args.source_union,
            args.output,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
