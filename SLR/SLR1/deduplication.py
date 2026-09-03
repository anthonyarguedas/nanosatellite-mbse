#!/usr/bin/env python3
"""Create compact screening records from completed review searches.

Modes:
- ``psr`` merges the final Scopus and Web of Science prior-review partitions.
- ``citation-chasing`` uses final Scopus and Web of Science citation artifacts.
- ``review-searches`` uses final direct-review search artifacts.

Source-event validation remains with the source-specific artifacts. This script
uses it internally, then writes only report metadata and minimal discovery
provenance needed for screening.
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
CANDIDATE_SCHEMA = "slr1-screening-candidates/v1"
COMMON_CUTOFF = "2026-08-24"
MODES = ("psr", "citation-chasing", "review-searches")
DEFAULT_OUTPUTS = {
    "psr": SLR1_DIR / "psr-candidates.json",
    "citation-chasing": SLR1_DIR / "citation-candidates.json",
    "review-searches": SLR1_DIR / "review-candidates.json",
}
PSR_PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
PSR_SOURCES = {
    "scopus": SOURCE_SPECIFIC_DIR / "scopus/psr-searches",
    "web_of_science_core_collection": (
        SOURCE_SPECIFIC_DIR / "web-of-science-core-collection/psr-searches"
    ),
}
CITATION_SOURCE_DIRS = {
    "scopus": SOURCE_SPECIFIC_DIR / "scopus/final-searches",
    "web_of_science_core_collection": (
        SOURCE_SPECIFIC_DIR / "web-of-science-core-collection/final-searches"
    ),
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
    return max(values, key=lambda value: (len(value), value.casefold()))


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
        if (
            assessment.get("status") != "passed"
            or assessment.get("final_search_partitions_complete") is not True
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


def direct_manifestations(merger: Any, paths: list[Path]) -> tuple[dict[str, list[dict[str, Any]]], int]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
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
            key = merger.make_dedup_key(record, source=source_id)
            groups[key].append(
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
                    "abstract": text(row.get("abstract")),
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
                }
            )
            raw_count += 1
    return dict(groups), raw_count


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
        if len(dois) > 1 or len(title_years) > 1:
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
    values = author_names(preferred.get("authors"))
    for row in rows:
        for name in row["authors"]:
            if name.casefold() not in {value.casefold() for value in values}:
                values.append(name)
    return values


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
    publication_date = preferred_text([row["publication_date"] for row in rows])
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
        "publication_title": preferred_text([row["publication_title"] for row in rows]),
        "document_type": preferred_text([row["document_type"] for row in rows]),
        "doi": doi,
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


def direct_candidates(merger: Any, paths: list[Path]) -> tuple[list[dict[str, Any]], int, int]:
    corpus = merger.merge_records(paths)
    if corpus.get("report_ready") is not True:
        raise ValueError("The direct-search merge is not report-ready")
    groups, raw_count = direct_manifestations(merger, paths)
    assert_no_identifier_conflicts(groups)
    results = corpus.get("results")
    if not isinstance(results, list) or len(results) != len(groups):
        raise ValueError("The direct-search deduplication did not reconcile")
    candidates: list[dict[str, Any]] = []
    for index, preferred in enumerate(results, start=1):
        if not isinstance(preferred, Mapping):
            raise ValueError("The direct-search merge returned a malformed record")
        key = text(preferred.get("dedup_key"))
        rows = groups.get(key)
        if not rows:
            raise ValueError("A merged record has no source manifestations")
        candidates.append(compact_record(f"candidate-{index:04d}", preferred, rows))
    duplicates_removed = raw_count - len(candidates)
    return candidates, raw_count, duplicates_removed


def citation_candidates(merger: Any, paths: list[Path]) -> tuple[list[dict[str, Any]], int, int]:
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
        compact_record(f"candidate-{index:04d}", rows[0], rows)
        for index, (_key, rows) in enumerate(ordered, start=1)
    ]
    return candidates, raw_count, raw_count - len(candidates)


def build(mode: str) -> dict[str, Any]:
    merger = load_merger()
    if mode == "psr":
        validate_psr_sources(merger)
        paths = psr_input_paths()
        candidates, raw_count, duplicates_removed = direct_candidates(merger, paths)
        namespace = "prior_secondary_reviews"
    elif mode == "review-searches":
        paths = final_direct_input_paths()
        candidates, raw_count, duplicates_removed = direct_candidates(merger, paths)
        namespace = "main"
    elif mode == "citation-chasing":
        paths = citation_input_paths()
        candidates, raw_count, duplicates_removed = citation_candidates(merger, paths)
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
        "counts": {
            "source_record_occurrences": raw_count,
            "deduplicated_candidates": len(candidates),
            "duplicate_occurrences_removed": duplicates_removed,
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


def check(path: Path, mode: str) -> None:
    require_regular(path)
    persisted = load_json(path)
    expected = build(mode)
    persisted.pop("generated_at", None)
    expected.pop("generated_at", None)
    if persisted != expected:
        raise ValueError("Candidate records are not reproducible")
    if persisted.get("screening_decision_initial_value") != "none":
        raise ValueError("Candidate records do not initialize screening_decision")
    if any(record.get("screening_decision") != "none" for record in persisted["records"]):
        raise ValueError("Candidate records contain a non-initial screening decision")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="psr")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = (args.output or DEFAULT_OUTPUTS[args.mode]).resolve(strict=False)
    try:
        output.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise SystemExit("The candidate file must be inside this repository") from error
    if args.check:
        check(output, args.mode)
        print(json.dumps({"status": "ok", "output": relative(output)}))
        return 0
    payload = build(args.mode)
    write_create_only(output, payload)
    print(
        json.dumps(
            {
                "status": "saved",
                "output": relative(output),
                **payload["counts"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
