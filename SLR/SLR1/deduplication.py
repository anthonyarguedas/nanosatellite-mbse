#!/usr/bin/env python3
"""Create compact screening records from completed review searches.

Modes:
- ``psr`` merges the final Scopus and Web of Science prior-review partitions.
- ``citation-chasing`` uses final Scopus and Web of Science citation artifacts.
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
import sys
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
CANDIDATE_SCHEMA = "slr1-screening-candidates/v2"
MIGRATABLE_CANDIDATE_SCHEMAS = {
    "slr1-screening-candidates/v1",
    CANDIDATE_SCHEMA,
}
COMMON_CUTOFF = "2026-08-24"
MODES = ("psr", "citation-chasing", "review-searches")
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


def load_merger() -> Any:
    for name, expected in MERGER_COMPONENTS.items():
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
    for item in values:
        name = text(item.get("name")) if isinstance(item, Mapping) else text(item)
        if name.casefold() in {"[no authors found]", "no authors found"}:
            continue
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


def final_direct_input_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in sorted(SOURCE_SPECIFIC_DIR.glob("*/final-searches")):
        for path in sorted(directory.rglob("*.json")):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                value = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            metadata = value.get("output_metadata", {})
            if (
                value.get("schema_version") == "academic-search-result/v1"
                and isinstance(metadata, Mapping)
                and metadata.get("merge_eligible") is True
            ):
                paths.append(path)
    if not paths:
        raise ValueError("No final direct-review search artifacts are available")
    return paths


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
                    "source_record_id": record["paperId"],
                    "doi": record["doi"],
                    "title": record["title"],
                    "normalized_title": merger.normalize_text(record["title"]),
                    "year": record["year"],
                    "publication_date": text(
                        row.get("publicationDate", row.get("publication_date", row.get("date")))
                    ),
                    "abstract": text(row.get("abstract")) or enriched_abstract,
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
) -> dict[str, list[dict[str, Any]]]:
    """Form report identities from every available exact identity signal.

    A DOI-first exclusive key cannot join a DOI-bearing manifestation to the
    same report in a source that omitted its DOI. Connected components let DOI,
    normalized title and year, and source-native IDs reinforce each other.
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
    for index, row in enumerate(rows):
        tokens: list[str] = []
        source_id = row["source_id"]
        source_record_id = row["source_record_id"]
        if source_record_id:
            reference = (source_id, source_record_id)
            reference_rows[reference].append(index)
            tokens.append(f"record:{source_id}:{source_record_id.casefold()}")
        if row["doi"]:
            tokens.append(f"doi:{row['doi']}")
        normalized_year = merger.normalize_year(row["year"])
        if row["normalized_title"] and normalized_year:
            tokens.append(
                f"title:{row['normalized_title']}|year:{normalized_year}"
            )
        for token in tokens:
            owner = token_owner.setdefault(token, index)
            union(index, owner)

    for link in manual_links:
        indexes: list[int] = []
        for reference in link["references"]:
            matched = reference_rows.get(reference, [])
            if not matched:
                raise ValueError(
                    f"Manual identity link {link['identity_id']} references a missing record"
                )
            indexes.extend(matched)
        for index in indexes:
            rows[index]["manual_identity_link_id"] = link["identity_id"]
            union(indexes[0], index)

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[find(index)].append(row)

    result: dict[str, list[dict[str, Any]]] = {}
    for position, group_rows in enumerate(grouped.values()):
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
                    "source_record_id": stable_id,
                    "doi": record["doi"],
                    "title": record["title"],
                    "normalized_title": merger.normalize_text(record["title"]),
                    "year": record["year"],
                    "publication_date": text(row.get("publication_date", row.get("date"))),
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
        title_years = {(row["normalized_title"], row["year"]) for row in rows}
        manual_ids = {row.get("manual_identity_link_id") for row in rows}
        manually_reviewed = len(manual_ids) == 1 and None not in manual_ids
        if len(dois) > 1 or (len(title_years) > 1 and not manually_reviewed):
            conflicts.append(key)
    if conflicts:
        raise ValueError(
            "Identifier conflicts require manual review before deduplication: "
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
        if row["partition"]:
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
    groups = cluster_manifestations(merger, manifestations, manual_links or [])
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


def build(mode: str) -> dict[str, Any]:
    merger = load_merger()
    identity_link_receipt: dict[str, Any] | None = None
    abstract_enrichment_receipt: dict[str, Any] | None = None
    if mode == "psr":
        validate_psr_sources(merger)
        paths = psr_input_paths()
        manual_links, identity_link_receipt = load_psr_identity_links()
        abstract_enrichment, abstract_enrichment_receipt = (
            load_psr_abstract_enrichment()
        )
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
        candidates, raw_count, duplicates_removed = direct_candidates(
            merger,
            paths,
            "review",
        )
        namespace = "main"
    elif mode == "citation-chasing":
        paths = citation_input_paths()
        candidates, raw_count, duplicates_removed = citation_candidates(
            merger,
            paths,
            "citation",
        )
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
        "metadata_enrichment": {
            "scopus_abstracts": abstract_enrichment_receipt,
        },
        "deduplication": {
            "algorithm": (
                "connected components over source-qualified record ID, normalized DOI, "
                "and normalized title plus publication year"
                if mode != "citation-chasing"
                else "shared merger identity key"
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
