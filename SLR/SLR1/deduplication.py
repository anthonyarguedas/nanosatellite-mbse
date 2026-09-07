#!/usr/bin/env python3
"""Create compact screening records from completed review searches.

Modes:
- ``psr`` merges the final Scopus and Web of Science prior-review partitions.
- ``citation-chasing`` combines final Scopus and Web of Science forward citation
  artifacts with the deduplicated OCR backward reference ledger, then applies
  validated structured OCR metadata after candidate identity assignment.
- ``review-searches`` uses final direct-review search artifacts.

Source-event validation remains with the source-specific artifacts. This script
uses it internally, then writes only report metadata and minimal discovery
provenance needed for screening. It transfers reviewer-coded publication fields
when rebuilding candidates but never infers them from source metadata.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SLR1_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SLR1_DIR.parents[1]
SOURCE_SPECIFIC_DIR = SLR1_DIR / "source-specific"
MERGER_DIR = (
    Path.home() / "agent-tools/academic-api-search/skills/academic-api-search/scripts"
)
MERGER_PATH = MERGER_DIR / "merge_search_results.py"
MERGER_COMPONENTS = {
    "merge_search_results.py": "7c395b4cfb1fbc2b2f713f2e7b04aa166a8a784dc20f0b430915edec0aa56d63",
    "_merge_contract.py": "676f899a6281bac6060582d625a939e8324cf88a0b82bae58399b1beb8d34b22",
    "_prisma_search_run.py": "a888e75294d368469ace3ff0041d904cc830b36b4bc30389ea9d5e67adc3205d",
}
REVIEW_MERGER_COMPONENTS = {
    "merge_search_results.py": "7931f04941466b65ebec74f385211c5c370058d6fc1f176184903cc2cc124625",
    "_merge_contract.py": "e210b8046fa2d9380b2d405d61490d60b93134589fe592038cab86f7025a577e",
    "_prisma_search_run.py": "a888e75294d368469ace3ff0041d904cc830b36b4bc30389ea9d5e67adc3205d",
}
CANDIDATE_SCHEMA = "slr1-screening-candidates/v2"
MIGRATABLE_CANDIDATE_SCHEMAS = {
    "slr1-screening-candidates/v1",
    CANDIDATE_SCHEMA,
}
COMMON_CUTOFF = "2026-08-24"
MODES = ("psr", "citation-chasing", "review-searches")
FINAL_ARTIFACT_SELECTION_FILENAME = "accepted-final-artifacts.json"
FINAL_ARTIFACT_SELECTION_SCHEMA = "slr1-final-direct-artifact-selection/v1"
FINAL_SOURCE_UNION_RECEIPTS = {
    "advanced-technologies-aerospace-index": (
        "proquest_aerospace_index",
        "source-union-receipt.json",
    ),
    "arxiv": ("arxiv", "corrective-002/source-union-receipt.json"),
    "compendex": ("compendex", "corrective-003/source-union-receipt.json"),
    "esa-indico": ("esa_indico", "corrective-006/source-union-receipt-main.json"),
    "iaf-digital-library": (
        "iaf_digital_library",
        "corrective-002/source-union-receipt.json",
    ),
    "inspec": ("inspec", "corrective-002/source-union-receipt.json"),
    "nasa-ntrs": ("nasa_ntrs", "source-union-receipt.json"),
    "pqdt-global": (
        "proquest_dissertations_theses_global",
        "source-union-receipt.json",
    ),
    "scopus": ("scopus", "corrective-004/source-union-receipt-main.json"),
    "web-of-science-core-collection": (
        "web_of_science_core_collection",
        "source-union-receipt.json",
    ),
    "wiley-online-library": (
        "wiley_online_library",
        "source-union-receipt.json",
    ),
}
FINAL_ACCEPTED_SELECTION_SOURCES = {
    "aiaa-arc": "aiaa_arc",
    "ieee-xplore": "ieee_xplore",
    "springer-nature-link": "springer_nature_link",
}
EXPECTED_FINAL_DIRECT_SOURCES = frozenset(
    source_id for source_id, _receipt in FINAL_SOURCE_UNION_RECEIPTS.values()
) | frozenset(FINAL_ACCEPTED_SELECTION_SOURCES.values()) | {"oatd"}
OATD_FINAL_OUTCOME_PATH = (
    SOURCE_SPECIFIC_DIR / "oatd/final-searches/final-outcome.json"
)
OATD_FINAL_OUTCOME_SCHEMA = "slr1-oatd-final-outcome/v1"
REVIEW_IDENTITY_LINKS_PATH = SLR1_DIR / "review-deduplication-links.json"
REVIEW_IDENTITY_LINKS_SCHEMA = "slr1-review-deduplication-links/v1"
DEFAULT_OUTPUTS = {
    "psr": SLR1_DIR / "psr-candidates.json",
    "citation-chasing": SLR1_DIR / "citation-candidates.json",
    "review-searches": SLR1_DIR / "review-candidates.json",
}
PSR_PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
PSR_SOURCES = {
    "scopus": SOURCE_SPECIFIC_DIR / "scopus/psr-searches/corrective-002",
    "web_of_science_core_collection": (
        SOURCE_SPECIFIC_DIR
        / "web-of-science-core-collection/psr-searches/corrective-002"
    ),
}
PSR_SCOPUS_ABSTRACT_ENRICHMENT = (
    PSR_SOURCES["scopus"] / "abstract-follow-up/abstract-enrichment.json"
)
PSR_SCOPUS_ABSTRACT_ENRICHMENT_SCHEMA = (
    "slr1-scopus-final-psr-abstract-enrichment/v1"
)
CITATION_SOURCE_DIRS = {
    "scopus": SOURCE_SPECIFIC_DIR / "scopus/final-searches",
    "web_of_science_core_collection": (
        SOURCE_SPECIFIC_DIR / "web-of-science-core-collection/final-searches"
    ),
}
BACKWARD_REFERENCE_QUERY_LEDGER = (
    SLR1_DIR
    / "citation-chasing/backward/cycle-1/metadata/deduplicated-reference-queries.json"
)
BACKWARD_REFERENCE_QUERY_SCHEMA = "slr1-backward-reference-query-ledger/v1"
BACKWARD_REFERENCE_SOURCE_ID = "ocr_backward_reference"
BACKWARD_REFERENCE_PARTITION = "citation-cycle-1-backward"
BACKWARD_STRUCTURED_OCR_ENRICHMENT_DIR = (
    SLR1_DIR
    / "citation-chasing/backward/cycle-1/metadata/structured-ocr-enrichment"
)
BACKWARD_STRUCTURED_OCR_ENRICHMENT_SCHEMA = (
    "slr1-ocr-structured-metadata-batch/v1"
)
BACKWARD_STRUCTURED_OCR_CONFIDENCE_VALUES = frozenset(
    {"high", "moderate", "low"}
)
BACKWARD_STRUCTURED_OCR_RECORD_FIELDS = frozenset(
    {
        "candidate_id",
        "backward_query_id",
        "title",
        "authors",
        "publication_title",
        "publication_year",
        "doi",
        "document_type_hint",
        "coding_confidence",
        "evidence_note",
    }
)
BACKWARD_STRUCTURED_OCR_EXPECTED_BATCH_COUNT = 6
BACKWARD_STRUCTURED_OCR_EXPECTED_RECORD_COUNT = 564
BACKWARD_STRUCTURED_OCR_EXPECTED_TITLE_COUNT = 556
OCR_SURNAME_PARTICLES = frozenset(
    {"da", "de", "del", "della", "der", "di", "dos", "du", "la", "le", "van", "von"}
)
PSR_IDENTITY_LINKS_PATH = SLR1_DIR / "psr-deduplication-links.json"
PSR_IDENTITY_LINKS_SCHEMA = "slr1-psr-deduplication-links/v1"
SCREENING_DECISIONS = {
    "psr": {
        "none",
        "include_prior_secondary_review",
        "exclude_not_secondary_review",
        "exclude_narrative_or_no_identifiable_search",
        "exclude_no_space_or_satellite_scope",
        "exclude_no_mbse_or_structured_system_model_scope",
        "exclude_insufficient_completed_report",
        "exclude_wrong_date",
        "exclude_wrong_language",
        "full_text_needed",
        "not_retrieved",
    },
    "citation-chasing": {
        "none",
        "already_included",
        "include_route_A_eps_primary",
        "include_route_B_embedded_eps",
        "exclude_no_qualifying_eps_thread",
        "exclude_not_mbse",
        "exclude_wrong_population",
        "exclude_wrong_publication_type",
        "exclude_wrong_completion_status",
        "exclude_wrong_date",
        "exclude_wrong_language",
        "exclude_secondary_study",
        "full_text_needed",
        "not_retrieved",
    },
    "review-searches": {
        "none",
        "include_route_A_eps_primary",
        "include_route_B_embedded_eps",
        "exclude_no_qualifying_eps_thread",
        "exclude_not_mbse",
        "exclude_wrong_population",
        "exclude_wrong_publication_type",
        "exclude_wrong_completion_status",
        "exclude_wrong_date",
        "exclude_wrong_language",
        "exclude_secondary_study",
        "full_text_needed",
        "not_retrieved",
    },
}
PUBLICATION_TYPES = frozenset(
    {
        "journal_article",
        "conference_paper",
        "workshop_presentation",
        "edited_book_research_chapter",
        "institutional_technical_report",
        "arxiv_preprint",
        "masters_thesis",
        "doctoral_thesis_or_dissertation",
    }
)
DEGREE_LEVELS = frozenset({"masters", "doctoral"})
DEGREE_COMPLETION_STATUSES = frozenset(
    {"completed", "in_progress_or_incomplete", "unclear"}
)
THESIS_PUBLICATION_TYPES = frozenset(
    {"masters_thesis", "doctoral_thesis_or_dissertation"}
)
SCREENING_CODING_FIELDS = (
    "publication_type",
    "degree_level",
    "completion_status",
)
INCLUDED_REVIEW_DECISIONS = frozenset(
    {"include_route_A_eps_primary", "include_route_B_embedded_eps"}
)
PUBLICATION_CODING_DECISIONS = INCLUDED_REVIEW_DECISIONS | {
    "exclude_wrong_publication_type",
    "exclude_wrong_completion_status",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def relative(path: Path) -> str:
    return str(path.relative_to(REPOSITORY_ROOT))


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_merger(mode: str | None = None) -> Any:
    components = (
        REVIEW_MERGER_COMPONENTS
        if mode in {"review-searches", "citation-chasing"}
        else MERGER_COMPONENTS
    )
    for name, expected in components.items():
        path = MERGER_DIR / name
        require_regular(path)
        if digest(path) != expected:
            raise RuntimeError(f"The reviewed merge dependency changed: {name}")
    spec = importlib.util.spec_from_file_location("slr1_screening_merger", MERGER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the reviewed merge utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def normalized_keywords(value: Any) -> list[str]:
    values: list[Any]
    if isinstance(value, str):
        values = value.split(";")
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    elif isinstance(value, Mapping):
        values = list(value.values())
    else:
        values = []
    result: list[str] = []
    for item in values:
        if isinstance(item, Mapping):
            item = item.get("name", item.get("label", item.get("value", "")))
        candidate = text(item)
        if candidate and candidate.casefold() not in {value.casefold() for value in result}:
            result.append(candidate)
    return result


def author_names(value: Any) -> list[str]:
    values = value if isinstance(value, list) else []
    result: list[str] = []
    placeholders = {
        "[no authors found]",
        "no authors found",
        "view all authors",
        "et al",
        "aiaa",
        "ieee",
    }
    for item in values:
        name = text(item.get("name")) if isinstance(item, Mapping) else text(item)
        lowered = name.casefold()
        if lowered in placeholders or "committee member" in lowered:
            continue
        name = re.sub(r"\s*\(author\)\s*$", "", name, flags=re.IGNORECASE).strip()
        if name and name.casefold() not in {value.casefold() for value in result}:
            result.append(name)
    return result


def preferred_text(values: list[str]) -> str | None:
    values = list({value for value in values if value})
    if not values:
        return None
    return max(values, key=lambda value: (len(value), value.casefold(), value))


def report_landing_url(row: Mapping[str, Any]) -> str:
    value = text(row.get("url"))
    return value if value.startswith(("https://", "http://")) else ""


def discovery_partitions(row: Mapping[str, Any], fallback: str) -> list[str]:
    local_matching = row.get("localMatching")
    expressions = (
        local_matching.get("expressions")
        if isinstance(local_matching, Mapping)
        else None
    )
    matched = []
    if isinstance(expressions, list):
        matched = [
            text(expression.get("id"))
            for expression in expressions
            if isinstance(expression, Mapping)
            and expression.get("status") == "matched"
            and text(expression.get("id"))
        ]
    values = matched or ([fallback] if fallback else [])
    return sorted(set(values))


def normalized_full_date(value: Any) -> str | None:
    candidate = text(value)
    if not candidate:
        return None
    iso_prefix = candidate[:10]
    if len(candidate) >= 10:
        try:
            return datetime.strptime(iso_prefix, "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass
    normalized = " ".join(candidate.replace(",", " ").split())
    for date_format in (
        "%b %d %Y",
        "%B %d %Y",
        "%Y %b %d",
        "%Y %B %d",
        "%d %b %Y",
        "%d %B %Y",
    ):
        try:
            return datetime.strptime(normalized, date_format).date().isoformat()
        except ValueError:
            continue
    return None


def source_publication_date(row: Mapping[str, Any]) -> str:
    values = [
        text(row.get("publicationDate")),
        text(row.get("publication_date")),
        text(row.get("date")),
    ]
    detail = row.get("oatdDetail")
    fields = detail.get("fields") if isinstance(detail, Mapping) else None
    issued_dates = fields.get("issued_date") if isinstance(fields, Mapping) else None
    if isinstance(issued_dates, list):
        values.extend(
            text(item.get("value"))
            for item in issued_dates
            if isinstance(item, Mapping)
        )
    candidates = [value for value in values if value]
    if not candidates:
        return ""
    return max(
        candidates,
        key=lambda value: (
            normalized_full_date(value) is not None,
            len(value),
            value.casefold(),
            value,
        ),
    )


def merged_publication_date(
    rows: list[dict[str, Any]],
) -> tuple[str | None, str | None]:
    source_values = sorted(
        {text(row.get("publication_date")) for row in rows if text(row.get("publication_date"))},
        key=lambda value: (value.casefold(), value),
    )
    full_dates = [
        (normalized, source_value)
        for source_value in source_values
        if (normalized := normalized_full_date(source_value)) is not None
    ]
    if full_dates:
        normalized, source_value = max(
            full_dates,
            key=lambda item: (
                len(item[1]),
                item[1].casefold(),
                item[1],
                item[0],
            ),
        )
        return normalized, source_value
    return None, preferred_text(source_values)


def arxiv_record(source_id: str, row: Mapping[str, Any]) -> dict[str, str | None] | None:
    if source_id != "arxiv":
        return None
    arxiv_id = (
        text(row.get("sourceRecordStableId"))
        or text(row.get("sourceRecordId"))
        or text(row.get("paperId"))
    )
    if not arxiv_id:
        return None
    version = text(row.get("sourceRecordVersion")) or None
    version_date_source_value = (
        text(row.get("sourceRecordVersionDate"))
        or text(row.get("sourceVersionDate"))
        or text(row.get("versionDate"))
        or text(row.get("version_date"))
        or text(row.get("updated"))
        or None
    )
    return {
        "arxiv_id": arxiv_id,
        "version": version,
        "version_date": normalized_full_date(version_date_source_value),
        "version_date_source_value": version_date_source_value,
    }


def merged_arxiv_records(rows: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    records: list[dict[str, str | None]] = []
    seen: set[tuple[str | None, str | None, str | None, str | None]] = set()
    for row in rows:
        record = row.get("arxiv_record")
        if not isinstance(record, Mapping):
            continue
        key = (
            text(record.get("arxiv_id")) or None,
            text(record.get("version")) or None,
            text(record.get("version_date")) or None,
            text(record.get("version_date_source_value")) or None,
        )
        if key[0] is None or key in seen:
            continue
        seen.add(key)
        records.append(
            {
                "arxiv_id": key[0],
                "version": key[1],
                "version_date": key[2],
                "version_date_source_value": key[3],
            }
        )
    return sorted(
        records,
        key=lambda record: (
            record["arxiv_id"] or "",
            record["version"] or "",
            record["version_date"] or "",
            record["version_date_source_value"] or "",
        ),
    )


def merged_stable_urls(rows: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {row["stable_url"] for row in rows if text(row.get("stable_url"))},
        key=lambda value: (value.casefold(), value),
    )


def load_psr_identity_links() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    require_regular(PSR_IDENTITY_LINKS_PATH)
    payload = load_json(PSR_IDENTITY_LINKS_PATH)
    if (
        payload.get("schema_version") != PSR_IDENTITY_LINKS_SCHEMA
        or payload.get("review_namespace") != "prior_secondary_reviews"
    ):
        raise ValueError("The PSR identity-link declaration has an unexpected scope")
    links = payload.get("links")
    if not isinstance(links, list) or not links:
        raise ValueError("The PSR identity-link declaration has no links")
    identity_ids: set[str] = set()
    references: set[tuple[str, str]] = set()
    normalized: list[dict[str, Any]] = []
    for link in links:
        if not isinstance(link, Mapping):
            raise ValueError("A PSR identity link is malformed")
        identity_id = text(link.get("identity_id"))
        basis = text(link.get("basis"))
        records = link.get("records")
        if not identity_id or identity_id in identity_ids or not basis:
            raise ValueError("A PSR identity link has an invalid identity or basis")
        if not isinstance(records, list) or len(records) < 2:
            raise ValueError(f"PSR identity link {identity_id} has fewer than two records")
        link_references: list[tuple[str, str]] = []
        for record in records:
            if not isinstance(record, Mapping):
                raise ValueError(f"PSR identity link {identity_id} has a malformed record")
            reference = (text(record.get("source")), text(record.get("record_id")))
            if not all(reference) or reference in references:
                raise ValueError(f"PSR identity link {identity_id} reuses an invalid record")
            references.add(reference)
            link_references.append(reference)
        identity_ids.add(identity_id)
        normalized.append(
            {
                "identity_id": identity_id,
                "basis": basis,
                "references": link_references,
            }
        )
    return normalized, {
        "path": relative(PSR_IDENTITY_LINKS_PATH),
        "sha256": digest(PSR_IDENTITY_LINKS_PATH),
        "link_count": len(normalized),
    }


def load_review_identity_links() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    require_regular(REVIEW_IDENTITY_LINKS_PATH)
    payload = load_json(REVIEW_IDENTITY_LINKS_PATH)
    if (
        payload.get("schema_version") != REVIEW_IDENTITY_LINKS_SCHEMA
        or payload.get("review_namespace") != "main"
        or not text(payload.get("manual_review_scope"))
    ):
        raise ValueError("The review identity-link declaration has an unexpected scope")
    links = payload.get("links")
    reviewed_non_links = payload.get("reviewed_non_link")
    if not isinstance(links, list) or not links:
        raise ValueError("The review identity-link declaration has no links")
    if not isinstance(reviewed_non_links, list):
        raise ValueError("The review identity-link declaration has no non-link ledger")

    identity_ids: set[str] = set()
    references: set[tuple[str, str]] = set()
    normalized: list[dict[str, Any]] = []
    for link in links:
        if not isinstance(link, Mapping):
            raise ValueError("A review identity link is malformed")
        identity_id = text(link.get("identity_id"))
        basis = text(link.get("basis"))
        records = link.get("records")
        if not identity_id or identity_id in identity_ids or not basis:
            raise ValueError("A review identity link has an invalid identity or basis")
        if not isinstance(records, list) or len(records) < 2:
            raise ValueError(
                f"Review identity link {identity_id} has fewer than two records"
            )
        link_references: list[tuple[str, str]] = []
        for record in records:
            if not isinstance(record, Mapping):
                raise ValueError(
                    f"Review identity link {identity_id} has a malformed record"
                )
            reference = (text(record.get("source")), text(record.get("record_id")))
            if not all(reference) or reference in references:
                raise ValueError(
                    f"Review identity link {identity_id} reuses an invalid record"
                )
            references.add(reference)
            link_references.append(reference)
        identity_ids.add(identity_id)
        normalized.append(
            {
                "identity_id": identity_id,
                "basis": basis,
                "references": link_references,
            }
        )

    for item in reviewed_non_links:
        if not isinstance(item, Mapping) or not text(item.get("basis")):
            raise ValueError("A reviewed non-link is malformed")
        records = item.get("records")
        if not isinstance(records, list) or len(records) < 2:
            raise ValueError("A reviewed non-link has fewer than two records")
        item_references = [
            (text(record.get("source")), text(record.get("record_id")))
            for record in records
            if isinstance(record, Mapping)
        ]
        if len(item_references) != len(records) or not all(
            all(reference) for reference in item_references
        ):
            raise ValueError("A reviewed non-link has an invalid record")

    return normalized, {
        "path": relative(REVIEW_IDENTITY_LINKS_PATH),
        "sha256": digest(REVIEW_IDENTITY_LINKS_PATH),
        "link_count": len(normalized),
        "reviewed_non_link_count": len(reviewed_non_links),
    }


def load_psr_abstract_enrichment() -> tuple[dict[tuple[str, str], str], dict[str, Any]]:
    require_regular(PSR_SCOPUS_ABSTRACT_ENRICHMENT)
    payload = load_json(PSR_SCOPUS_ABSTRACT_ENRICHMENT)
    records = payload.get("records")
    if (
        payload.get("schema_version") != PSR_SCOPUS_ABSTRACT_ENRICHMENT_SCHEMA
        or payload.get("source") != "Scopus"
        or payload.get("review_namespace") != "prior_secondary_reviews"
        or payload.get("complete") is not True
        or not isinstance(records, list)
    ):
        raise ValueError("The Scopus PSR abstract enrichment is incomplete")
    result: dict[tuple[str, str], str] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("A Scopus PSR abstract enrichment row is malformed")
        paper_id = text(record.get("paper_id"))
        abstract = text(record.get("abstract"))
        reference = ("scopus", paper_id)
        if (
            not paper_id.startswith("SCOPUS-PUBLICATION:")
            or not abstract
            or record.get("abstract_source") != "native_scopus_result_page"
            or record.get("abstract_detail_verified") is not True
            or record.get("abstract_not_available") is not False
            or reference in result
        ):
            raise ValueError("A Scopus PSR abstract enrichment row is invalid")
        result[reference] = abstract
    if len(result) != payload.get("requested_record_count"):
        raise ValueError("The Scopus PSR abstract enrichment count changed")
    assessment = load_json(PSR_SOURCES["scopus"] / "assessment.json")
    if assessment.get("abstract_enrichment_sha256") != digest(
        PSR_SCOPUS_ABSTRACT_ENRICHMENT
    ):
        raise ValueError("The Scopus PSR assessment does not bind its enrichment")
    return result, {
        "path": relative(PSR_SCOPUS_ABSTRACT_ENRICHMENT),
        "sha256": digest(PSR_SCOPUS_ABSTRACT_ENRICHMENT),
        "record_count": len(result),
    }


def psr_input_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in PSR_SOURCES.values():
        for partition in PSR_PARTITIONS:
            path = directory / f"{partition}.json"
            require_regular(path)
            paths.append(path)
    return paths


def validate_final_direct_artifact(path: Path) -> dict[str, Any]:
    require_regular(path)
    value = load_json(path)
    metadata = value.get("output_metadata")
    if (
        value.get("schema_version") != "academic-search-result/v1"
        or not isinstance(metadata, Mapping)
        or metadata.get("merge_eligible") is not True
        or metadata.get("retrieval_complete") is not True
        or not isinstance(value.get("results"), list)
    ):
        raise ValueError(f"Selected final artifact is not merge eligible: {path}")
    return value


def accepted_final_direct_input_paths(directory: Path) -> list[Path] | None:
    """Resolve one source's explicit selection of non-superseded final events."""
    selection_path = directory / FINAL_ARTIFACT_SELECTION_FILENAME
    if not selection_path.exists() and not selection_path.is_symlink():
        return None
    require_regular(selection_path)
    selection = load_json(selection_path)
    artifacts = selection.get("artifacts")
    if (
        selection.get("schema_version") != FINAL_ARTIFACT_SELECTION_SCHEMA
        or selection.get("status") != "complete"
        or selection.get("review_namespace") != "main"
        or not isinstance(artifacts, list)
        or selection.get("artifact_count") != len(artifacts)
        or not artifacts
    ):
        raise ValueError(f"Invalid final artifact selection in {selection_path}")
    root = directory.resolve()
    selected: list[Path] = []
    seen: set[Path] = set()
    for item in artifacts:
        if not isinstance(item, Mapping):
            raise ValueError(f"Malformed final artifact selection in {selection_path}")
        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not raw_path or Path(raw_path).is_absolute():
            raise ValueError(f"Unsafe final artifact path in {selection_path}")
        path = (REPOSITORY_ROOT / raw_path).resolve(strict=False)
        if not path.is_relative_to(root) or path in seen:
            raise ValueError(f"Out-of-scope final artifact path in {selection_path}")
        require_regular(path)
        if (
            item.get("sha256") != digest(path)
            or item.get("byte_count") != path.stat().st_size
        ):
            raise ValueError(f"Changed selected final artifact: {path}")
        validate_final_direct_artifact(path)
        seen.add(path)
        selected.append(path)
    return selected


def source_union_final_direct_input_paths(
    directory: Path,
    source_id: str,
    receipt_relative_path: str,
) -> list[Path]:
    """Resolve the exact final events bound by one source-union receipt."""
    receipt_path = directory / receipt_relative_path
    require_regular(receipt_path)
    receipt = load_json(receipt_path)
    events = receipt.get("events")
    if (
        receipt.get("schema_version") != "academic-search-source-union-receipt/v1"
        or receipt.get("review_namespace") != "main"
        or receipt.get("expected_sources") != [source_id]
        or not isinstance(events, list)
        or receipt.get("event_count") != len(events)
        or not events
    ):
        raise ValueError(f"Invalid final source-union receipt: {receipt_path}")

    requirements: list[tuple[str, int, Mapping[str, Any]]] = []
    for event in events:
        if not isinstance(event, Mapping):
            raise ValueError(f"Malformed final source-union event: {receipt_path}")
        artifact = event.get("artifact")
        sha256 = text(event.get("artifact_sha256"))
        byte_count = event.get("artifact_byte_count")
        if (
            event.get("review_namespace") != "main"
            or event.get("source_id") != source_id
            or event.get("completion_status") != "complete"
            or event.get("report_ready") is not True
            or not isinstance(artifact, Mapping)
            or artifact.get("sha256") != sha256
            or artifact.get("byte_count") != byte_count
            or not re.fullmatch(r"[0-9a-f]{64}", sha256)
            or not isinstance(byte_count, int)
            or byte_count < 0
        ):
            raise ValueError(f"Invalid final source-union event: {receipt_path}")
        requirements.append((sha256, byte_count, event))

    required_sizes = {byte_count for _sha256, byte_count, _event in requirements}
    matches: dict[tuple[str, int], list[Path]] = defaultdict(list)
    for path in sorted(directory.rglob("*.json")):
        if path.is_symlink() or not path.is_file():
            continue
        byte_count = path.stat().st_size
        if byte_count not in required_sizes:
            continue
        key = (digest(path), byte_count)
        if any(key[:2] == requirement[:2] for requirement in requirements):
            matches[key].append(path.resolve())

    selected: list[Path] = []
    seen: set[Path] = set()
    for sha256, byte_count, event in requirements:
        candidates = matches.get((sha256, byte_count), [])
        if len(candidates) != 1:
            raise ValueError(
                f"Final source-union artifact has {len(candidates)} matches: "
                f"{source_id} {event.get('event_id')}"
            )
        path = candidates[0]
        value = validate_final_direct_artifact(path)
        if isinstance(event.get("raw_count"), int) and event.get("raw_count") != len(
            value["results"]
        ):
            raise ValueError(f"Final source-union count changed: {path}")
        if path in seen:
            raise ValueError(f"Final source-union receipt reuses an artifact: {path}")
        seen.add(path)
        selected.append(path)
    return selected


def load_oatd_final_evidence() -> tuple[dict[str, Any], dict[str, Path]]:
    require_regular(OATD_FINAL_OUTCOME_PATH)
    outcome = load_json(OATD_FINAL_OUTCOME_PATH)
    if (
        outcome.get("schema_version") != OATD_FINAL_OUTCOME_SCHEMA
        or outcome.get("source_id") != "oatd"
        or outcome.get("status") != "complete"
        or outcome.get("source_disposition") != "include_complete_source_union"
    ):
        raise ValueError("The final OATD outcome is not a completed source union")

    outcome_root = OATD_FINAL_OUTCOME_PATH.parent.resolve()
    evidence: dict[str, Path] = {}
    for field in (
        "source_union",
        "source_validation",
        "full_abstracts",
        "full_abstracts_validation",
    ):
        item = outcome.get(field)
        if not isinstance(item, Mapping):
            raise ValueError(f"The final OATD outcome has no {field} evidence")
        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not raw_path or Path(raw_path).is_absolute():
            raise ValueError(f"The final OATD outcome has an unsafe {field} path")
        path = (outcome_root / raw_path).resolve(strict=False)
        if not path.is_relative_to(outcome_root):
            raise ValueError(f"The final OATD outcome has an unsafe {field} path")
        require_regular(path)
        if item.get("sha256") != digest(path):
            raise ValueError(f"The final OATD {field} evidence changed")
        evidence[field] = path
    return outcome, evidence


def oatd_final_direct_input_paths() -> list[Path]:
    outcome, evidence = load_oatd_final_evidence()
    validation = load_json(evidence["source_validation"])
    if (
        validation.get("status") != "valid"
        or validation.get("merge_eligible_hydrated_union") is not True
    ):
        raise ValueError("The final OATD validation did not pass")
    artifact = validate_final_direct_artifact(evidence["source_union"])
    if outcome.get("records") != len(artifact["results"]):
        raise ValueError("The final OATD source-union count changed")
    return [evidence["source_union"]]


def final_direct_input_paths() -> list[Path]:
    paths: list[Path] = []
    for source_directory, (source_id, receipt_path) in sorted(
        FINAL_SOURCE_UNION_RECEIPTS.items()
    ):
        directory = SOURCE_SPECIFIC_DIR / source_directory / "final-searches"
        paths.extend(
            source_union_final_direct_input_paths(directory, source_id, receipt_path)
        )
    for source_directory, source_id in sorted(FINAL_ACCEPTED_SELECTION_SOURCES.items()):
        directory = SOURCE_SPECIFIC_DIR / source_directory / "final-searches"
        selected = accepted_final_direct_input_paths(directory)
        if selected is None:
            raise ValueError(f"Missing final artifact selection for {source_id}")
        selection = load_json(directory / FINAL_ARTIFACT_SELECTION_FILENAME)
        if selection.get("source_id") != source_id:
            raise ValueError(f"Final artifact selection has the wrong source: {source_id}")
        paths.extend(selected)
    paths.extend(oatd_final_direct_input_paths())
    if len(paths) != len(set(paths)):
        raise ValueError("A final direct-review artifact was selected more than once")
    if not paths:
        raise ValueError("No final direct-review search artifacts are available")
    return sorted(paths)


def load_aiaa_abstract_enrichment(
    paths: list[Path],
) -> tuple[dict[tuple[str, str], str], dict[str, Any]]:
    directory = SOURCE_SPECIFIC_DIR / "aiaa-arc/final-searches"
    selection_path = directory / FINAL_ARTIFACT_SELECTION_FILENAME
    require_regular(selection_path)
    selection = load_json(selection_path)
    raw_union_path = selection.get("record_union")
    if (
        selection.get("schema_version") != FINAL_ARTIFACT_SELECTION_SCHEMA
        or selection.get("source_id") != "aiaa_arc"
        or selection.get("full_abstract_capture_complete") is not True
        or not isinstance(raw_union_path, str)
        or not raw_union_path
        or Path(raw_union_path).is_absolute()
    ):
        raise ValueError("The AIAA abstract enrichment selection is invalid")
    union_path = (REPOSITORY_ROOT / raw_union_path).resolve(strict=False)
    if not union_path.is_relative_to(directory.resolve()):
        raise ValueError("The AIAA abstract enrichment path is outside its source")
    require_regular(union_path)
    if selection.get("record_union_sha256") != digest(union_path):
        raise ValueError("The AIAA abstract enrichment changed")

    payload = load_json(union_path)
    records = payload.get("records")
    if (
        payload.get("schema_version")
        != "slr1-aiaa-arc-final-direct-record-union/v1"
        or payload.get("source_id") != "aiaa_arc"
        or payload.get("review_namespace") != "main"
        or payload.get("complete") is not True
        or not isinstance(records, list)
        or payload.get("unique_canonical_doi_count") != len(records)
        or selection.get("unique_canonical_doi_count") != len(records)
    ):
        raise ValueError("The AIAA abstract enrichment is incomplete")

    source_root = directory.resolve()
    selected_ids = {
        text(row.get("paperId"))
        for path in paths
        if path.is_relative_to(source_root)
        for row in load_json(path).get("results", [])
        if isinstance(row, Mapping) and text(row.get("paperId"))
    }
    enrichment: dict[tuple[str, str], str] = {}
    union_ids: set[str] = set()
    unavailable_count = 0
    for item in records:
        if not isinstance(item, Mapping):
            raise ValueError("An AIAA abstract enrichment row is malformed")
        paper_id = text(item.get("paper_id"))
        record = item.get("record")
        if not paper_id or paper_id in union_ids or not isinstance(record, Mapping):
            raise ValueError("An AIAA abstract enrichment identity is invalid")
        abstract = text(record.get("abstract"))
        unavailable = record.get("abstract_not_available")
        status = record.get("abstract_capture_status")
        if text(record.get("paperId")) != paper_id or (
            abstract
            and (unavailable is not False or status != "full_source_abstract")
        ):
            raise ValueError("An AIAA abstract enrichment row is inconsistent")
        if not abstract:
            if unavailable is not True or status != "source_abstract_not_available":
                raise ValueError("An AIAA unavailable abstract state is inconsistent")
            unavailable_count += 1
        else:
            enrichment[("aiaa_arc", paper_id)] = abstract
        union_ids.add(paper_id)

    if (
        union_ids != selected_ids
        or payload.get("records_with_full_abstract") != len(enrichment)
        or payload.get("records_with_source_abstract_unavailable")
        != unavailable_count
    ):
        raise ValueError("The AIAA abstract enrichment identifier ledger changed")
    return enrichment, {
        "path": relative(union_path),
        "sha256": digest(union_path),
        "record_count": len(records),
        "full_abstract_count": len(enrichment),
        "source_abstract_unavailable_count": unavailable_count,
    }


def load_oatd_abstract_enrichment(
    paths: list[Path],
) -> tuple[dict[tuple[str, str], str], dict[str, Any]]:
    outcome, evidence = load_oatd_final_evidence()
    source_union = validate_final_direct_artifact(evidence["source_union"])
    if paths.count(evidence["source_union"]) != 1:
        raise ValueError("The enriched OATD source union is not selected exactly once")

    payload = load_json(evidence["full_abstracts"])
    validation = load_json(evidence["full_abstracts_validation"])
    records = payload.get("records")
    summary = payload.get("summary")
    source_receipt = payload.get("source_union")
    if (
        payload.get("schema_version") != "slr1-oatd-full-abstract-enrichment/v1"
        or payload.get("merge_eligible") is not False
        or payload.get("additional_discovery_event") is not False
        or not isinstance(records, list)
        or not isinstance(summary, Mapping)
        or not isinstance(source_receipt, Mapping)
        or source_receipt.get("sha256") != digest(evidence["source_union"])
        or source_receipt.get("records") != len(source_union["results"])
        or validation.get("schema_version")
        != "slr1-oatd-full-abstract-enrichment-validation/v1"
        or validation.get("status") != "valid"
        or validation.get("artifact_sha256") != digest(evidence["full_abstracts"])
        or validation.get("repository_evidence_hashes_verified") is not True
        or validation.get("additional_discovery_event") is not False
    ):
        raise ValueError("The OATD abstract enrichment is incomplete")

    source_ids = [text(row.get("paperId")) for row in source_union["results"]]
    enrichment: dict[tuple[str, str], str] = {}
    enriched_ids: list[str] = []
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("An OATD abstract enrichment row is malformed")
        paper_id = text(record.get("paperId"))
        abstract = text(record.get("abstract"))
        if (
            not paper_id
            or paper_id in enriched_ids
            or not abstract
            or record.get("abstract_not_available") is not False
            or record.get("abstractCompleteness")
            != "complete_as_provided_by_cited_source"
        ):
            raise ValueError("An OATD abstract enrichment row is inconsistent")
        enrichment[("oatd", paper_id)] = abstract
        enriched_ids.append(paper_id)

    if (
        enriched_ids != source_ids
        or outcome.get("records") != len(enrichment)
        or summary.get("records_with_full_abstracts") != len(enrichment)
        or validation.get("full_abstracts") != len(enrichment)
    ):
        raise ValueError("The OATD abstract enrichment identifier ledger changed")
    repository_enriched_ids = summary.get("repository_enriched_ids")
    if (
        not isinstance(repository_enriched_ids, list)
        or summary.get("repository_enriched_records") != len(repository_enriched_ids)
        or not set(repository_enriched_ids).issubset(enriched_ids)
    ):
        raise ValueError("The OATD repository enrichment ledger changed")
    return enrichment, {
        "path": relative(evidence["full_abstracts"]),
        "sha256": digest(evidence["full_abstracts"]),
        "record_count": len(enrichment),
        "repository_enriched_record_count": len(repository_enriched_ids),
        "validation_path": relative(evidence["full_abstracts_validation"]),
        "validation_sha256": digest(evidence["full_abstracts_validation"]),
    }


def load_review_abstract_enrichment(
    paths: list[Path],
) -> tuple[dict[tuple[str, str], str], dict[str, Any]]:
    aiaa, aiaa_receipt = load_aiaa_abstract_enrichment(paths)
    oatd, oatd_receipt = load_oatd_abstract_enrichment(paths)
    if set(aiaa) & set(oatd):
        raise ValueError("Review abstract enrichments reuse a source record")
    return {**aiaa, **oatd}, {
        "aiaa_arc_abstracts": aiaa_receipt,
        "oatd_abstracts": oatd_receipt,
    }


def citation_input_paths() -> list[Path]:
    paths: list[Path] = []
    for source_id, directory in CITATION_SOURCE_DIRS.items():
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.json")):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                value = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if (
                value.get("schema_version") == "academic-search-citation-artifact/v1"
                and value.get("source_id") == source_id
                and value.get("status") in {"success", "explicit_zero"}
                and value.get("retrieval_complete") is True
            ):
                paths.append(path)
    if not paths:
        raise ValueError(
            "No final Scopus or Web of Science citation-chasing artifacts are available"
        )
    return paths


def validate_psr_sources(merger: Any) -> None:
    assessments = {
        "scopus": PSR_SOURCES["scopus"] / "assessment.json",
        "web_of_science_core_collection": (
            PSR_SOURCES["web_of_science_core_collection"] / "assessment.json"
        ),
    }
    for source_id, directory in PSR_SOURCES.items():
        assessment_path = assessments[source_id]
        require_regular(assessment_path)
        assessment = load_json(assessment_path)
        abstract_recovery = assessment.get("abstract_recovery", {})
        if (
            assessment.get("status") != "passed"
            or assessment.get("final_search_partitions_complete") is not True
            or not isinstance(abstract_recovery, Mapping)
            or abstract_recovery.get("status") != "complete"
        ):
            raise ValueError(f"The final PSR assessment did not pass for {source_id}")
        receipt = directory / "source-union-receipt-prior_secondary_reviews.json"
        require_regular(receipt)
        # This checks the source-specific final artifacts and their terminal
        # markers. Its output is deliberately not copied into screening data.
        merger.merge_records(
            [directory / f"{partition}.json" for partition in PSR_PARTITIONS],
            source_union_receipt=receipt,
            source_union_namespace="prior_secondary_reviews",
        )


def direct_manifestations(
    merger: Any,
    paths: list[Path],
    abstract_enrichment: Mapping[tuple[str, str], str] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    manifestations: list[dict[str, Any]] = []
    raw_count = 0
    for path in paths:
        data = load_json(path)
        source_id = merger.infer_source(path, data)
        receipt = data.get("output_metadata", {}).get("prisma_search_run", {})
        coverage = receipt.get("coverage", {}) if isinstance(receipt, Mapping) else {}
        partition = text(coverage.get("partition_id")) or "unspecified"
        rows = data.get("results")
        if not isinstance(rows, list):
            raise ValueError(f"A search artifact has no results list: {path}")
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError(f"A search row is malformed: {path}")
            record = {
                "paperId": merger.clean_text(row.get("paperId")),
                "doi": merger.normalize_doi(row.get("doi")),
                "title": merger.clean_text(row.get("title")),
                "year": row.get("year"),
            }
            enriched_abstract = (abstract_enrichment or {}).get(
                (source_id, record["paperId"]), ""
            )
            manifestations.append(
                {
                    "source_id": source_id,
                    "partition": partition,
                    "partitions": discovery_partitions(row, partition),
                    "source_record_id": record["paperId"],
                    "doi": record["doi"],
                    "title": record["title"],
                    "normalized_title": merger.normalize_text(record["title"]),
                    "year": record["year"],
                    "publication_date": source_publication_date(row),
                    "abstract": enriched_abstract or text(row.get("abstract")),
                    "abstract_snippet": text(row.get("snippet")),
                    "keywords": [
                        keyword
                        for field in (
                            "keywords",
                            "authorKeywords",
                            "author_keywords",
                            "keywordsPlus",
                            "keywords_plus",
                        )
                        for keyword in normalized_keywords(row.get(field))
                    ],
                    "authors": author_names(row.get("authors")),
                    "publication_title": text(
                        row.get("publicationTitle", row.get("publication_title"))
                    ),
                    "document_type": text(
                        row.get("documentType", row.get("document_type"))
                    ),
                    "arxiv_record": arxiv_record(source_id, row),
                    "stable_url": report_landing_url(row),
                    "manual_identity_link_id": None,
                }
            )
            raw_count += 1
    return manifestations, raw_count


def cluster_manifestations(
    merger: Any,
    manifestations: list[dict[str, Any]],
    manual_links: list[dict[str, Any]],
    *,
    guarded_title_year: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    """Form conservative report identities from exact and reviewed signals.

    DOI and source-native identifiers are joined first. For review candidates,
    exact title and year joins are accepted only when they introduce no DOI
    conflict, repeated source identity, or thesis versus non-thesis conflict.
    Reviewed links then resolve known variants and manifestation aliases.
    """

    rows = [copy.deepcopy(row) for row in manifestations]
    parent = list(range(len(rows)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    token_owner: dict[str, int] = {}
    reference_rows: dict[tuple[str, str], list[int]] = defaultdict(list)
    title_year_rows: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        source_id = row["source_id"]
        source_record_id = row["source_record_id"]
        tokens: list[str] = []
        if source_record_id:
            reference = (source_id, source_record_id)
            reference_rows[reference].append(index)
            tokens.append(f"record:{source_id}:{source_record_id.casefold()}")
        if row["doi"]:
            tokens.append(f"doi:{row['doi']}")
        for token in tokens:
            owner = token_owner.setdefault(token, index)
            union(index, owner)
        normalized_year = merger.normalize_year(row["year"])
        if row["normalized_title"] and normalized_year:
            title_year_rows[(row["normalized_title"], normalized_year)].append(index)

    def report_class(row: Mapping[str, Any]) -> str | None:
        source_id = text(row.get("source_id"))
        document_type = text(row.get("document_type")).casefold()
        if source_id in {"oatd", "proquest_dissertations_theses_global"}:
            return "thesis"
        if "thes" in document_type or "diss" in document_type:
            return "thesis"
        return "non_thesis" if document_type else None

    for _title_year, indexes in sorted(title_year_rows.items()):
        roots = {find(index) for index in indexes}
        if len(roots) < 2:
            continue
        component_rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for index, row in enumerate(rows):
            root = find(index)
            if root in roots:
                component_rows[root].append(row)
        dois = {
            row["doi"]
            for group_rows in component_rows.values()
            for row in group_rows
            if row["doi"]
        }
        source_counts: dict[str, int] = defaultdict(int)
        for group_rows in component_rows.values():
            for source_id in {row["source_id"] for row in group_rows}:
                source_counts[source_id] += 1
        repeated_sources = {
            source_id for source_id, count in source_counts.items() if count > 1
        }
        report_classes = {
            value
            for group_rows in component_rows.values()
            for row in group_rows
            if (value := report_class(row)) is not None
        }
        incompatible_report_classes = report_classes == {"thesis", "non_thesis"}
        if guarded_title_year and (
            len(dois) > 1 or repeated_sources or incompatible_report_classes
        ):
            continue
        ordered_roots = sorted(roots)
        for root in ordered_roots[1:]:
            union(ordered_roots[0], root)

    manual_ids_by_index: dict[int, str] = {}
    for link in manual_links:
        indexes = []
        for reference in link["references"]:
            matched = reference_rows.get(reference, [])
            if not matched:
                raise ValueError(
                    f"Manual identity link {link['identity_id']} references a missing record"
                )
            indexes.extend(matched)
        for index in indexes:
            manual_ids_by_index[index] = link["identity_id"]
            union(indexes[0], index)

    grouped_indexes: dict[int, list[int]] = defaultdict(list)
    for index in range(len(rows)):
        grouped_indexes[find(index)].append(index)

    result: dict[str, list[dict[str, Any]]] = {}
    for position, indexes in enumerate(grouped_indexes.values()):
        manual_ids = {
            manual_ids_by_index[index]
            for index in indexes
            if index in manual_ids_by_index
        }
        if len(manual_ids) > 1:
            raise ValueError(
                "Multiple manual identity links resolved to one report: "
                + ", ".join(sorted(manual_ids))
            )
        manual_id = next(iter(manual_ids), None)
        group_rows = [rows[index] for index in indexes]
        for row in group_rows:
            row["manual_identity_link_id"] = manual_id
        references = sorted(
            f"{row['source_id']}:{row['source_record_id']}"
            for row in group_rows
            if row["source_record_id"]
        )
        identity_material = references or [
            json.dumps(group_rows, ensure_ascii=False, sort_keys=True, default=str)
        ]
        serialized = "\n".join(identity_material).encode("utf-8")
        key = f"cluster:{position}:" + hashlib.sha256(serialized).hexdigest()
        result[key] = group_rows
    return result


def citation_manifestations(merger: Any, paths: list[Path]) -> tuple[dict[str, list[dict[str, Any]]], int]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    raw_count = 0
    for path in paths:
        data = load_json(path)
        source_id = text(data.get("source_id"))
        if source_id not in CITATION_SOURCE_DIRS:
            raise ValueError(f"Citation artifact has an unexpected source: {path}")
        cycle = data.get("cycle", data.get("citation", {}).get("cycle"))
        partition = f"citation-cycle-{cycle}" if isinstance(cycle, int) else "citation"
        rows = data.get("candidates")
        if not isinstance(rows, list):
            raise ValueError(f"Citation artifact has no candidate list: {path}")
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError(f"Citation candidate is malformed: {path}")
            stable_id = text(row.get("stable_id", row.get("candidate_id")))
            record = {
                "paperId": stable_id,
                "doi": merger.normalize_doi(row.get("doi")),
                "title": text(row.get("title")),
                "year": row.get("year"),
            }
            key = merger.make_dedup_key(record, source=source_id)
            groups[key].append(
                {
                    "source_id": source_id,
                    "partition": partition,
                    "partitions": [partition],
                    "source_record_id": stable_id,
                    "doi": record["doi"],
                    "title": record["title"],
                    "normalized_title": merger.normalize_text(record["title"]),
                    "year": record["year"],
                    "publication_date": source_publication_date(row),
                    "abstract": text(row.get("abstract")),
                    "abstract_snippet": text(row.get("snippet")),
                    "keywords": normalized_keywords(row.get("keywords")),
                    "authors": author_names(row.get("authors")),
                    "publication_title": text(row.get("publication_title")),
                    "document_type": text(row.get("document_type")),
                    "arxiv_record": arxiv_record(source_id, row),
                    "stable_url": report_landing_url(row),
                }
            )
            raw_count += 1
    return dict(groups), raw_count


def assert_no_identifier_conflicts(groups: Mapping[str, list[dict[str, Any]]]) -> None:
    conflicts: list[str] = []
    for key, rows in groups.items():
        if len(rows) < 2:
            continue
        dois = {row["doi"] for row in rows if row["doi"]}
        manual_ids = {
            text(row.get("manual_identity_link_id"))
            for row in rows
            if text(row.get("manual_identity_link_id"))
        }
        if len(dois) > 1 and len(manual_ids) != 1:
            conflicts.append(key)
    if conflicts:
        raise ValueError(
            "Conflicting DOIs require a reviewed identity link: "
            + ", ".join(sorted(conflicts)[:10])
        )


def source_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, set[str]]] = {}
    for row in rows:
        item = grouped.setdefault(
            row["source_id"], {"record_ids": set(), "partitions": set()}
        )
        if row["source_record_id"]:
            item["record_ids"].add(row["source_record_id"])
        partitions = row.get("partitions")
        if isinstance(partitions, list):
            item["partitions"].update(
                text(partition) for partition in partitions if text(partition)
            )
        elif row["partition"]:
            item["partitions"].add(row["partition"])
    return [
        {
            "source": source_id,
            "record_ids": sorted(item["record_ids"]),
            "partitions": sorted(item["partitions"]),
        }
        for source_id, item in sorted(grouped.items())
    ]


def unique_keywords(rows: list[dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for row in rows:
        for keyword in row["keywords"]:
            if keyword.casefold() not in {value.casefold() for value in values}:
                values.append(keyword)
    return sorted(values, key=str.casefold)


def merged_authors(preferred: Mapping[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    candidates = [author_names(preferred.get("authors"))]
    candidates.extend(author_names(row.get("authors")) for row in rows)
    return max(
        candidates,
        key=lambda values: (
            len(values),
            sum(len(value) for value in values),
            tuple(value.casefold() for value in values),
            tuple(values),
        ),
        default=[],
    )


def preferred_manifestation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        rows,
        key=lambda row: (
            bool(row["doi"]),
            len(row["abstract"]),
            len(row["abstract_snippet"]),
            bool(row["publication_date"]),
            bool(row["document_type"]),
            len(row["authors"]),
            len(row["publication_title"]),
            row["source_id"],
            row["source_record_id"],
        ),
    )


def compact_record(
    candidate_id: str,
    preferred: Mapping[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    title = text(preferred.get("title")) or preferred_text([row["title"] for row in rows])
    doi = text(preferred.get("doi")) or preferred_text([row["doi"] for row in rows])
    year = preferred.get("year")
    if not isinstance(year, int):
        values = [row["year"] for row in rows if isinstance(row["year"], int)]
        year = max(values) if values else None
    publication_date, publication_date_source_value = merged_publication_date(rows)
    abstract = preferred_text([text(preferred.get("abstract"))] + [row["abstract"] for row in rows])
    snippet = preferred_text(
        [text(preferred.get("snippet"))] + [row["abstract_snippet"] for row in rows]
    )
    return {
        "candidate_id": candidate_id,
        "title": title,
        "authors": merged_authors(preferred, rows),
        "publication_year": year,
        "publication_date": publication_date,
        "publication_date_source_value": publication_date_source_value,
        "publication_title": preferred_text([row["publication_title"] for row in rows]),
        "document_type": preferred_text([row["document_type"] for row in rows]),
        "doi": doi,
        "arxiv_records": merged_arxiv_records(rows),
        "stable_urls": merged_stable_urls(rows),
        "abstract": abstract,
        "abstract_snippet": snippet,
        "keywords": unique_keywords(rows),
        "source_records": source_records(rows),
        "screening_decision": "none",
        "cutoff_date_screening_status": (
            "pending_exact_cutoff_check"
            if year == 2026
            else "not_required_by_source_year"
        ),
    }


def direct_candidates(
    merger: Any,
    paths: list[Path],
    candidate_prefix: str,
    manual_links: list[dict[str, Any]] | None = None,
    abstract_enrichment: Mapping[tuple[str, str], str] | None = None,
) -> tuple[list[dict[str, Any]], int, int]:
    corpus = merger.merge_records(paths)
    if corpus.get("report_ready") is not True:
        raise ValueError("The direct-search merge is not report-ready")
    manifestations, raw_count = direct_manifestations(
        merger, paths, abstract_enrichment
    )
    groups = cluster_manifestations(
        merger,
        manifestations,
        manual_links or [],
        guarded_title_year=candidate_prefix == "review",
    )
    assert_no_identifier_conflicts(groups)
    results = corpus.get("results")
    if not isinstance(results, list):
        raise ValueError("The direct-search merge returned no results list")
    if raw_count != corpus.get("dedup_summary", {}).get("raw_results"):
        raise ValueError("Raw record accounting disagrees with the validated merge")
    if len(groups) > len(results):
        raise ValueError("Project identity clustering lost a validated merge relation")
    ordered = sorted(
        groups.items(),
        key=lambda item: (
            -max(
                (row["year"] for row in item[1] if isinstance(row["year"], int)),
                default=0,
            ),
            min(
                (row["normalized_title"] for row in item[1] if row["normalized_title"]),
                default="",
            ),
            item[0],
        ),
    )
    candidates = [
        compact_record(
            f"{candidate_prefix}-candidate-{index:04d}",
            preferred_manifestation(rows),
            rows,
        )
        for index, (_key, rows) in enumerate(ordered, start=1)
    ]
    duplicates_removed = raw_count - len(candidates)
    return candidates, raw_count, duplicates_removed


def citation_candidates(
    merger: Any,
    paths: list[Path],
    candidate_prefix: str,
) -> tuple[list[dict[str, Any]], int, int]:
    groups, raw_count = citation_manifestations(merger, paths)
    assert_no_identifier_conflicts(groups)
    ordered = sorted(
        groups.items(),
        key=lambda item: (
            -max(
                (row["year"] for row in item[1] if isinstance(row["year"], int)),
                default=0,
            ),
            item[0],
        ),
    )
    candidates = [
        compact_record(f"{candidate_prefix}-candidate-{index:04d}", rows[0], rows)
        for index, (_key, rows) in enumerate(ordered, start=1)
    ]
    return candidates, raw_count, raw_count - len(candidates)


def normalized_ocr_identity_text(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", text(value)).casefold()
    without_marks = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    return " ".join(re.sub(r"[^a-z0-9]+", " ", without_marks).split())


def ocr_author_surnames(value: Any) -> set[str]:
    authors = value if isinstance(value, list) else []
    result: set[str] = set()
    for author in authors:
        if not isinstance(author, str) or not author.strip():
            continue
        surname_text = author.split(",", 1)[0] if "," in author else author
        words = normalized_ocr_identity_text(surname_text).split()
        while len(words) > 1 and len(words[-1]) == 1:
            words.pop()
        surname = next(
            (
                word
                for word in reversed(words)
                if len(word) > 1 and word not in OCR_SURNAME_PARTICLES
            ),
            "",
        )
        if surname:
            result.add(surname)
    return result


def load_backward_reference_query_ledger() -> dict[str, Any]:
    require_regular(BACKWARD_REFERENCE_QUERY_LEDGER)
    ledger = load_json(BACKWARD_REFERENCE_QUERY_LEDGER)
    if ledger.get("schema_version") != BACKWARD_REFERENCE_QUERY_SCHEMA:
        raise ValueError("The backward-reference query ledger schema changed")
    counts = ledger.get("counts")
    inputs = ledger.get("inputs")
    units = ledger.get("query_units")
    if (
        not isinstance(counts, Mapping)
        or not isinstance(inputs, list)
        or not isinstance(units, list)
    ):
        raise ValueError("The backward-reference query ledger is malformed")
    raw_occurrence_count = counts.get("raw_reference_occurrences")
    unique_unit_count = counts.get("unique_query_units")
    if (
        isinstance(raw_occurrence_count, bool)
        or not isinstance(raw_occurrence_count, int)
        or raw_occurrence_count < 0
        or isinstance(unique_unit_count, bool)
        or not isinstance(unique_unit_count, int)
        or unique_unit_count != len(units)
    ):
        raise ValueError("The backward-reference query counts changed")

    input_occurrences = 0
    for item in inputs:
        if not isinstance(item, Mapping):
            raise ValueError("A backward-reference input receipt is malformed")
        raw_path = text(item.get("path"))
        expected_digest = text(item.get("sha256"))
        occurrence_count = item.get("raw_reference_occurrence_count")
        if (
            not raw_path
            or not expected_digest
            or isinstance(occurrence_count, bool)
            or not isinstance(occurrence_count, int)
            or occurrence_count < 0
        ):
            raise ValueError("A backward-reference input receipt is incomplete")
        source_path = (REPOSITORY_ROOT / raw_path).resolve(strict=False)
        try:
            source_path.relative_to(REPOSITORY_ROOT)
        except ValueError as error:
            raise ValueError("A backward-reference input escaped the repository") from error
        require_regular(source_path)
        if digest(source_path) != expected_digest:
            raise ValueError(f"A backward-reference input changed: {raw_path}")
        input_occurrences += occurrence_count
    if input_occurrences != raw_occurrence_count:
        raise ValueError("Backward-reference input occurrence accounting changed")

    query_ids: set[str] = set()
    unit_occurrences = 0
    for unit in units:
        if not isinstance(unit, Mapping):
            raise ValueError("A backward-reference query unit is malformed")
        query_id = text(unit.get("query_unit_id"))
        identity = unit.get("identity")
        occurrences = unit.get("occurrences")
        occurrence_count = unit.get("occurrence_count")
        if (
            not re.fullmatch(r"backward-query-\d{5}", query_id)
            or query_id in query_ids
            or not isinstance(identity, Mapping)
            or not isinstance(occurrences, list)
            or isinstance(occurrence_count, bool)
            or not isinstance(occurrence_count, int)
            or occurrence_count < 1
            or occurrence_count != len(occurrences)
        ):
            raise ValueError("A backward-reference query unit failed validation")
        query_ids.add(query_id)
        unit_occurrences += len(occurrences)
    if unit_occurrences != raw_occurrence_count:
        raise ValueError("Backward-reference query occurrence accounting changed")
    return ledger


def optional_structured_ocr_text(
    value: Any, field: str, path: Path
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(
            f"A structured OCR {field} value is invalid: {path}"
        )
    return value


def structured_ocr_enrichment_input_paths() -> list[Path]:
    directory = BACKWARD_STRUCTURED_OCR_ENRICHMENT_DIR
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError(
            f"Expected a structured OCR enrichment directory: {directory}"
        )
    paths = sorted(directory.iterdir())
    if len(paths) != BACKWARD_STRUCTURED_OCR_EXPECTED_BATCH_COUNT or any(
        not re.fullmatch(r"batch-\d{4}\.json", path.name) for path in paths
    ):
        raise ValueError("The structured OCR enrichment batch ledger changed")
    for path in paths:
        require_regular(path)
    return paths


def load_structured_ocr_enrichments(
    paths: list[Path] | None = None,
    *,
    expected_record_count: int = BACKWARD_STRUCTURED_OCR_EXPECTED_RECORD_COUNT,
    expected_title_count: int = BACKWARD_STRUCTURED_OCR_EXPECTED_TITLE_COUNT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate structured OCR batches without using their metadata for identity."""
    selected_paths = paths or structured_ocr_enrichment_input_paths()
    if not selected_paths:
        raise ValueError("No structured OCR enrichment batches are available")

    records: list[dict[str, Any]] = []
    input_receipts: list[dict[str, Any]] = []
    candidate_ids: set[str] = set()
    query_ids: set[str] = set()
    for position, path in enumerate(selected_paths, start=1):
        require_regular(path)
        payload = load_json(path)
        batch_id = f"batch-{position:04d}"
        batch_records = payload.get("records")
        if (
            path.name != f"{batch_id}.json"
            or payload.get("schema_version")
            != BACKWARD_STRUCTURED_OCR_ENRICHMENT_SCHEMA
            or payload.get("batch_id") != batch_id
            or not isinstance(batch_records, list)
            or not batch_records
            or len(batch_records) > 100
            or payload.get("assigned_count") != len(batch_records)
        ):
            raise ValueError(f"A structured OCR enrichment batch is invalid: {path}")

        for item in batch_records:
            if not isinstance(item, dict) or set(item) != set(
                BACKWARD_STRUCTURED_OCR_RECORD_FIELDS
            ):
                raise ValueError(f"A structured OCR enrichment row is malformed: {path}")
            candidate_id = item.get("candidate_id")
            query_id = item.get("backward_query_id")
            if (
                not isinstance(candidate_id, str)
                or not re.fullmatch(r"citation-candidate-\d{4}", candidate_id)
                or candidate_id in candidate_ids
                or not isinstance(query_id, str)
                or not re.fullmatch(r"backward-query-\d{5}", query_id)
                or query_id in query_ids
            ):
                raise ValueError(
                    f"A structured OCR enrichment identity is invalid: {path}"
                )

            optional_structured_ocr_text(item.get("title"), "title", path)
            authors = item.get("authors")
            if not isinstance(authors, list) or any(
                not isinstance(author, str)
                or not author
                or author != author.strip()
                for author in authors
            ):
                raise ValueError(
                    f"A structured OCR authors value is invalid: {path}"
                )
            optional_structured_ocr_text(
                item.get("publication_title"), "publication_title", path
            )
            year = item.get("publication_year")
            if year is not None and (
                isinstance(year, bool)
                or not isinstance(year, int)
                or not 1000 <= year <= 9999
            ):
                raise ValueError(
                    f"A structured OCR publication_year value is invalid: {path}"
                )
            doi = optional_structured_ocr_text(item.get("doi"), "doi", path)
            if doi is not None and (
                doi != doi.casefold()
                or not re.fullmatch(r"10\.\d{4,9}/\S+", doi)
            ):
                raise ValueError(f"A structured OCR DOI value is invalid: {path}")
            optional_structured_ocr_text(
                item.get("document_type_hint"), "document_type_hint", path
            )
            if item.get("coding_confidence") not in (
                BACKWARD_STRUCTURED_OCR_CONFIDENCE_VALUES
            ):
                raise ValueError(
                    f"A structured OCR confidence value is invalid: {path}"
                )
            optional_structured_ocr_text(
                item.get("evidence_note"), "evidence_note", path
            )

            candidate_ids.add(candidate_id)
            query_ids.add(query_id)
            records.append(copy.deepcopy(item))

        input_receipts.append(
            {
                "path": relative(path),
                "sha256": digest(path),
                "batch_id": batch_id,
                "record_count": len(batch_records),
            }
        )

    recovered_fields = {
        "title": sum(bool(item["title"]) for item in records),
        "authors": sum(bool(item["authors"]) for item in records),
        "publication_title": sum(
            bool(item["publication_title"]) for item in records
        ),
        "publication_year": sum(
            item["publication_year"] is not None for item in records
        ),
        "doi": sum(bool(item["doi"]) for item in records),
        "document_type_hint": sum(
            bool(item["document_type_hint"]) for item in records
        ),
    }
    if (
        len(records) != expected_record_count
        or len(candidate_ids) != expected_record_count
        or len(query_ids) != expected_record_count
        or recovered_fields["title"] != expected_title_count
    ):
        raise ValueError("The structured OCR enrichment coverage changed")

    receipt = {
        "schema_version": BACKWARD_STRUCTURED_OCR_ENRICHMENT_SCHEMA,
        "inputs": input_receipts,
        "batch_count": len(selected_paths),
        "record_count": len(records),
        "candidate_id_coverage": len(candidate_ids),
        "backward_query_id_coverage": len(query_ids),
        "recovered_fields": recovered_fields,
        "remaining_title_null_records": len(records) - recovered_fields["title"],
    }
    return records, receipt


def backward_stable_urls(identity: Mapping[str, Any]) -> list[str]:
    values = identity.get("other_stable_identifiers")
    values = values if isinstance(values, list) else []
    result: set[str] = set()
    for value in values:
        candidate = text(value)
        if candidate.casefold().startswith("url:"):
            candidate = candidate.split(":", 1)[1].strip()
        if re.match(r"^https?://\S+$", candidate, re.I):
            result.add(candidate)
    return sorted(result)


def backward_candidate(
    merger: Any,
    candidate_id: str,
    unit: Mapping[str, Any],
) -> dict[str, Any]:
    identity = unit["identity"]
    year = identity.get("publication_year")
    if isinstance(year, bool) or not isinstance(year, int):
        year = None
    authors = identity.get("authors")
    if not isinstance(authors, list) or not all(
        isinstance(author, str) for author in authors
    ):
        authors = []
    query_id = text(unit.get("query_unit_id"))
    return {
        "candidate_id": candidate_id,
        "title": text(identity.get("title")),
        "authors": authors,
        "publication_year": year,
        "publication_date": None,
        "publication_date_source_value": None,
        "publication_title": None,
        "document_type": None,
        "doi": merger.normalize_doi(identity.get("doi_normalized")),
        "arxiv_records": [],
        "stable_urls": backward_stable_urls(identity),
        "abstract": None,
        "abstract_snippet": None,
        "keywords": [],
        "source_records": [
            {
                "source": BACKWARD_REFERENCE_SOURCE_ID,
                "record_ids": [query_id],
                "partitions": [BACKWARD_REFERENCE_PARTITION],
            }
        ],
        "screening_decision": "none",
        "cutoff_date_screening_status": (
            "pending_exact_cutoff_check"
            if year == 2026
            else "not_required_by_source_year"
        ),
    }


def add_backward_source_record(candidate: dict[str, Any], query_id: str) -> None:
    rows = candidate.get("source_records")
    if not isinstance(rows, list):
        raise ValueError("A citation candidate has no source-record list")
    rows.append(
        {
            "source": BACKWARD_REFERENCE_SOURCE_ID,
            "record_ids": [query_id],
            "partitions": [BACKWARD_REFERENCE_PARTITION],
        }
    )
    rows.sort(key=lambda row: text(row.get("source")))


def candidate_backward_query_ids(candidate: Mapping[str, Any]) -> list[str]:
    rows = candidate.get("source_records")
    if not isinstance(rows, list):
        return []
    return [
        text(record_id)
        for row in rows
        if isinstance(row, Mapping)
        and row.get("source") == BACKWARD_REFERENCE_SOURCE_ID
        and isinstance(row.get("record_ids"), list)
        for record_id in row["record_ids"]
        if text(record_id)
    ]


def augment_with_backward_references(
    merger: Any,
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int, dict[str, Any]]:
    ledger = load_backward_reference_query_ledger()
    units = sorted(
        ledger["query_units"], key=lambda unit: text(unit.get("query_unit_id"))
    )
    by_doi: dict[str, list[int]] = defaultdict(list)
    by_title: dict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        doi = merger.normalize_doi(candidate.get("doi"))
        if doi:
            by_doi[doi].append(index)
        title = normalized_ocr_identity_text(candidate.get("title"))
        if title:
            by_title[title].append(index)

    matched = 0
    ambiguous = 0
    appended = 0
    title_bearing = 0
    for unit in units:
        identity = unit["identity"]
        if text(identity.get("title")):
            title_bearing += 1
        indexes: list[int] = []
        doi = merger.normalize_doi(identity.get("doi_normalized"))
        if doi:
            indexes = list(by_doi.get(doi, []))
        if not indexes:
            normalized_title = normalized_ocr_identity_text(identity.get("title"))
            unit_year = identity.get("publication_year")
            unit_surnames = ocr_author_surnames(identity.get("author_last_names"))
            for index in by_title.get(normalized_title, []):
                candidate = candidates[index]
                candidate_doi = merger.normalize_doi(candidate.get("doi"))
                if doi and candidate_doi and doi != candidate_doi:
                    continue
                candidate_year = candidate.get("publication_year")
                if (
                    isinstance(unit_year, int)
                    and not isinstance(unit_year, bool)
                    and isinstance(candidate_year, int)
                    and not isinstance(candidate_year, bool)
                    and unit_year != candidate_year
                ):
                    continue
                candidate_surnames = ocr_author_surnames(candidate.get("authors"))
                if (
                    unit_surnames
                    and candidate_surnames
                    and not (unit_surnames & candidate_surnames)
                ):
                    continue
                indexes.append(index)
        indexes = sorted(set(indexes))
        query_id = text(unit.get("query_unit_id"))
        if len(indexes) == 1:
            add_backward_source_record(candidates[indexes[0]], query_id)
            matched += 1
            continue
        if len(indexes) > 1:
            ambiguous += 1
        candidate_id = f"citation-candidate-{len(candidates) + 1:04d}"
        candidates.append(backward_candidate(merger, candidate_id, unit))
        appended += 1

    raw_occurrences = ledger["counts"]["raw_reference_occurrences"]
    duplicate_occurrences = raw_occurrences - appended
    receipt = {
        "path": relative(BACKWARD_REFERENCE_QUERY_LEDGER),
        "sha256": digest(BACKWARD_REFERENCE_QUERY_LEDGER),
        "raw_reference_occurrences": raw_occurrences,
        "unique_query_units": len(units),
        "title_bearing_query_units": title_bearing,
        "matched_forward_candidates": matched,
        "ambiguous_matches_appended": ambiguous,
        "new_candidates_appended": appended,
    }
    return candidates, raw_occurrences, duplicate_occurrences, receipt


def apply_structured_ocr_enrichments(
    merger: Any,
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Enrich already identified candidates without changing candidate identity."""
    enrichments, receipt = load_structured_ocr_enrichments()
    original_candidate_ids = [candidate.get("candidate_id") for candidate in candidates]
    if len(original_candidate_ids) != len(set(original_candidate_ids)):
        raise ValueError("Citation candidate IDs are not unique before OCR enrichment")
    by_candidate_id = {
        text(candidate.get("candidate_id")): candidate for candidate in candidates
    }
    enrichment_ids = {item["candidate_id"] for item in enrichments}
    prior_title_null_ids = {
        text(candidate.get("candidate_id"))
        for candidate in candidates
        if not text(candidate.get("title"))
    }
    if prior_title_null_ids != enrichment_ids:
        raise ValueError(
            "Structured OCR enrichments do not exactly cover title-null candidates"
        )

    for item in enrichments:
        candidate = by_candidate_id.get(item["candidate_id"])
        if candidate is None or candidate_backward_query_ids(candidate) != [
            item["backward_query_id"]
        ]:
            raise ValueError(
                "A structured OCR enrichment is linked to the wrong backward query: "
                f"{item['candidate_id']}"
            )
        candidate["title"] = text(item["title"])
        candidate["authors"] = list(item["authors"])
        candidate["publication_title"] = item["publication_title"]
        candidate["publication_year"] = item["publication_year"]
        candidate["doi"] = merger.normalize_doi(item["doi"])
        candidate["document_type"] = item["document_type_hint"]
        candidate["cutoff_date_screening_status"] = (
            "pending_exact_cutoff_check"
            if item["publication_year"] == 2026
            else "not_required_by_source_year"
        )

    if original_candidate_ids != [
        candidate.get("candidate_id") for candidate in candidates
    ]:
        raise ValueError("Structured OCR enrichment changed candidate IDs or order")
    remaining_title_null = sum(
        not text(by_candidate_id[candidate_id].get("title"))
        for candidate_id in enrichment_ids
    )
    if remaining_title_null != receipt["remaining_title_null_records"]:
        raise ValueError("Structured OCR title-null accounting changed")
    receipt.update(
        {
            "prior_title_null_candidate_coverage": len(prior_title_null_ids),
            "enriched_candidate_coverage": len(enrichment_ids),
            "remaining_title_null_candidates": remaining_title_null,
            "application_stage": (
                "after backward query matching and candidate ID assignment"
            ),
        }
    )
    return candidates, receipt


def build(mode: str) -> dict[str, Any]:
    merger = load_merger(mode)
    identity_link_receipt: dict[str, Any] | None = None
    metadata_enrichment: dict[str, Any] = {"scopus_abstracts": None}
    if mode == "psr":
        validate_psr_sources(merger)
        paths = psr_input_paths()
        manual_links, identity_link_receipt = load_psr_identity_links()
        abstract_enrichment, abstract_enrichment_receipt = (
            load_psr_abstract_enrichment()
        )
        metadata_enrichment["scopus_abstracts"] = abstract_enrichment_receipt
        candidates, raw_count, duplicates_removed = direct_candidates(
            merger,
            paths,
            "psr",
            manual_links,
            abstract_enrichment,
        )
        namespace = "prior_secondary_reviews"
    elif mode == "review-searches":
        paths = final_direct_input_paths()
        actual_sources = {
            merger.infer_source(path, load_json(path)) for path in paths
        }
        if actual_sources != EXPECTED_FINAL_DIRECT_SOURCES:
            raise ValueError(
                "Final direct-review source coverage changed: "
                + ", ".join(sorted(actual_sources ^ EXPECTED_FINAL_DIRECT_SOURCES))
            )
        manual_links, identity_link_receipt = load_review_identity_links()
        abstract_enrichment, enrichment_receipts = load_review_abstract_enrichment(
            paths
        )
        metadata_enrichment.update(enrichment_receipts)
        candidates, raw_count, duplicates_removed = direct_candidates(
            merger,
            paths,
            "review",
            manual_links,
            abstract_enrichment,
        )
        namespace = "main"
    elif mode == "citation-chasing":
        paths = citation_input_paths()
        candidates, raw_count, duplicates_removed = citation_candidates(
            merger,
            paths,
            "citation",
        )
        (
            candidates,
            backward_raw_count,
            backward_duplicates_removed,
            backward_receipt,
        ) = augment_with_backward_references(merger, candidates)
        candidates, structured_ocr_receipt = apply_structured_ocr_enrichments(
            merger, candidates
        )
        raw_count += backward_raw_count
        duplicates_removed += backward_duplicates_removed
        metadata_enrichment["ocr_backward_references"] = backward_receipt
        metadata_enrichment["ocr_structured_metadata"] = structured_ocr_receipt
        namespace = "citation_chasing"
    else:  # pragma: no cover - argparse guards this
        raise ValueError(f"Unknown mode: {mode}")
    return {
        "schema_version": CANDIDATE_SCHEMA,
        "mode": mode,
        "review_namespace": namespace,
        "generated_at": now(),
        "common_evidence_cutoff": COMMON_CUTOFF,
        "screening_decision_initial_value": "none",
        "metadata_enrichment": metadata_enrichment,
        "deduplication": {
            "algorithm": (
                "shared merger identity key for forward artifacts, followed by "
                "normalized DOI or guarded normalized title, year, and author "
                "matching for OCR-extracted backward references"
                if mode == "citation-chasing"
                else (
                    "connected components over source-qualified record ID, normalized "
                    "DOI, guarded normalized title plus publication year, and reviewed "
                    "identity links"
                    if mode == "review-searches"
                    else "connected components over source-qualified record ID, "
                    "normalized DOI, and normalized title plus publication year"
                )
            ),
            "manual_identity_links": identity_link_receipt,
        },
        "counts": {
            "source_record_occurrences": raw_count,
            "deduplicated_candidates": len(candidates),
            "duplicate_occurrences_removed": duplicates_removed,
            "candidates_with_full_abstract": sum(
                bool(candidate["abstract"]) for candidate in candidates
            ),
            "candidates_with_abstract_snippet": sum(
                bool(candidate["abstract_snippet"]) for candidate in candidates
            ),
            "candidates_without_abstract_or_snippet": sum(
                not candidate["abstract"] and not candidate["abstract_snippet"]
                for candidate in candidates
            ),
        },
        "records": candidates,
    }


def write_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def reviewer_screening_coding(
    record: Mapping[str, Any], mode: str
) -> dict[str, str]:
    """Validate and return fields assigned during full-text screening."""
    if mode not in MODES:
        raise ValueError(f"Unknown screening mode: {mode}")

    allowed_values = {
        "publication_type": PUBLICATION_TYPES,
        "degree_level": DEGREE_LEVELS,
        "completion_status": DEGREE_COMPLETION_STATUSES,
    }
    coding: dict[str, str] = {}
    for field in SCREENING_CODING_FIELDS:
        if field not in record:
            continue
        value = record[field]
        if not isinstance(value, str) or value not in allowed_values[field]:
            raise ValueError(f"Invalid reviewer-coded {field}: {value!r}")
        coding[field] = value

    if mode == "psr":
        if coding:
            raise ValueError("PSR candidates cannot contain main-review publication coding")
        return coding

    decision = text(record.get("screening_decision"))
    if coding and decision not in PUBLICATION_CODING_DECISIONS:
        raise ValueError(
            "Reviewer-coded publication fields require an inclusion or "
            "publication-related exclusion decision"
        )
    if decision in INCLUDED_REVIEW_DECISIONS and "publication_type" not in coding:
        raise ValueError("An included report requires reviewer-coded publication_type")

    publication_type = coding.get("publication_type")
    degree_fields = {"degree_level", "completion_status"} & coding.keys()
    if degree_fields and publication_type not in THESIS_PUBLICATION_TYPES:
        raise ValueError(
            "degree_level and completion_status are allowed only for a thesis or "
            "dissertation"
        )
    if publication_type in THESIS_PUBLICATION_TYPES and degree_fields != {
        "degree_level",
        "completion_status",
    }:
        raise ValueError(
            "A reviewer-coded thesis or dissertation requires degree_level and "
            "completion_status"
        )

    degree_level = coding.get("degree_level")
    if publication_type == "masters_thesis" and degree_level != "masters":
        raise ValueError("masters_thesis requires degree_level 'masters'")
    if (
        publication_type == "doctoral_thesis_or_dissertation"
        and degree_level != "doctoral"
    ):
        raise ValueError(
            "doctoral_thesis_or_dissertation requires degree_level 'doctoral'"
        )
    if (
        decision in INCLUDED_REVIEW_DECISIONS
        and publication_type in THESIS_PUBLICATION_TYPES
        and coding.get("completion_status") != "completed"
    ):
        raise ValueError("An included thesis or dissertation must be completed")
    if decision == "exclude_wrong_completion_status":
        if publication_type not in THESIS_PUBLICATION_TYPES:
            raise ValueError(
                "exclude_wrong_completion_status requires a thesis or dissertation"
            )
        if coding.get("completion_status") == "completed":
            raise ValueError(
                "exclude_wrong_completion_status requires a non-completed status"
            )
    return coding


def record_references(record: Mapping[str, Any]) -> set[tuple[str, str]]:
    references: set[tuple[str, str]] = set()
    source_values = record.get("source_records")
    if not isinstance(source_values, list):
        return references
    for source_record in source_values:
        if not isinstance(source_record, Mapping):
            continue
        source = text(source_record.get("source"))
        record_ids = source_record.get("record_ids")
        if not source or not isinstance(record_ids, list):
            continue
        references.update(
            (source, text(record_id)) for record_id in record_ids if text(record_id)
        )
    return references


def apply_screening_decisions(
    payload: dict[str, Any], prior: Mapping[str, Any], mode: str
) -> int:
    if (
        prior.get("schema_version") not in MIGRATABLE_CANDIDATE_SCHEMAS
        or prior.get("mode") != mode
    ):
        raise ValueError("The screening-decision source has an incompatible scope")
    allowed = SCREENING_DECISIONS[mode]
    coding_by_reference: dict[
        tuple[str, str], tuple[str, tuple[tuple[str, str], ...]]
    ] = {}
    old_records = prior.get("records")
    if not isinstance(old_records, list):
        raise ValueError("The screening-decision source has no records list")
    for record in old_records:
        if not isinstance(record, Mapping):
            raise ValueError("The screening-decision source contains a malformed record")
        decision = text(record.get("screening_decision"))
        if decision not in allowed:
            raise ValueError(f"Unexpected screening decision: {decision}")
        coding = reviewer_screening_coding(record, mode)
        screening_state = (decision, tuple(sorted(coding.items())))
        references = record_references(record)
        if not references:
            raise ValueError("A prior screening record has no source identifier")
        for reference in references:
            existing = coding_by_reference.setdefault(reference, screening_state)
            if existing != screening_state:
                raise ValueError("One source identifier has conflicting prior screening coding")

    transferred = 0
    used_references: set[tuple[str, str]] = set()
    for record in payload["records"]:
        references = record_references(record)
        screening_states = {
            coding_by_reference[reference]
            for reference in references
            if reference in coding_by_reference
        }
        if not screening_states:
            raise ValueError("A rebuilt candidate has no prior screening decision")
        if len(screening_states) != 1:
            raise ValueError(
                "Merged duplicate candidates have conflicting screening coding"
            )
        decision, coding_items = screening_states.pop()
        record["screening_decision"] = decision
        record.update(coding_items)
        used_references.update(references)
        transferred += 1
    if used_references != set(coding_by_reference):
        raise ValueError("The rebuilt candidate set changed the source identifier ledger")
    return transferred


def check(path: Path, mode: str) -> None:
    require_regular(path)
    persisted = load_json(path)
    expected = build(mode)
    if persisted.get("screening_decision_initial_value") != "none":
        raise ValueError("Candidate records do not initialize screening_decision")
    records = persisted.get("records")
    if not isinstance(records, list):
        raise ValueError("Candidate records are missing")
    allowed = SCREENING_DECISIONS[mode]
    for record in records:
        if not isinstance(record, dict) or record.get("screening_decision") not in allowed:
            raise ValueError("Candidate records contain an invalid screening decision")
        reviewer_screening_coding(record, mode)
        record["screening_decision"] = "none"
        for field in SCREENING_CODING_FIELDS:
            record.pop(field, None)
    persisted.pop("generated_at", None)
    expected.pop("generated_at", None)
    if persisted != expected:
        raise ValueError("Candidate records are not reproducible")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="psr")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--screening-decisions-from",
        type=Path,
        help=(
            "transfer decisions and reviewer-coded publication fields by source "
            "record ID while rebuilding a candidate file"
        ),
    )
    args = parser.parse_args()
    output = (args.output or DEFAULT_OUTPUTS[args.mode]).resolve(strict=False)
    try:
        output.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise SystemExit("The candidate file must be inside this repository") from error
    if args.check:
        if args.screening_decisions_from is not None:
            raise SystemExit("--check cannot transfer screening decisions")
        check(output, args.mode)
        print(json.dumps({"status": "ok", "output": relative(output)}))
        return 0
    payload = build(args.mode)
    transferred = 0
    if args.screening_decisions_from is not None:
        source_path = args.screening_decisions_from.resolve(strict=False)
        require_regular(source_path)
        transferred = apply_screening_decisions(
            payload, load_json(source_path), args.mode
        )
    write_create_only(output, payload)
    print(
        json.dumps(
            {
                "status": "saved",
                "output": relative(output),
                "screening_decisions_transferred": transferred,
                **payload["counts"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
