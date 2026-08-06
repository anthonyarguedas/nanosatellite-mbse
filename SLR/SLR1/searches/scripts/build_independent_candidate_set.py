#!/usr/bin/env python3
"""Build the independently rediscovered, deterministic candidate set for eps-mbse-slr-2026.

The script intentionally consumes only the isolated copies of the final accepted
new-run query artifacts.  It preserves every raw search occurrence and its
query-level provenance, runs a second deduplication pass after the stock merger,
and freezes the resulting candidate set before any retained-file cache is read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "eps-mbse-slr-2026"

# This is the closed merge-input inventory derived from the primary-source and
# coverage-gap worklogs.  It deliberately excludes all pilots/refinements not
# retained, count-only artifacts, failures, comparisons, and prior merge output.
INPUTS: list[dict[str, Any]] = [
    {
        "merge_input": "scopus__S-A1_pilot_r1.json",
        "raw_file": "SLR/SLR1/searches/scopus/S-A1_pilot_r1.json",
        "query_id": "S-A1", "source": "Scopus", "source_slug": "scopus",
        "stream": "A", "search_phase": "primary", "expected_results": 3,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 250, "max_pages": 10, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-A2_pilot_r1.json",
        "raw_file": "SLR/SLR1/searches/scopus/S-A2_pilot_r1.json",
        "query_id": "S-A2", "source": "Scopus", "source_slug": "scopus",
        "stream": "A", "search_phase": "primary", "expected_results": 8,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 250, "max_pages": 10, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-B1r1_pilot-population-wildcard.json",
        "raw_file": "SLR/SLR1/searches/scopus/S-B1r1_pilot-population-wildcard.json",
        "query_id": "S-B1r1", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "primary", "expected_results": 79,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 300, "max_pages": 12, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-B3_pilot-systems-engineering-relation.json",
        "raw_file": "SLR/SLR1/searches/scopus/S-B3_pilot-systems-engineering-relation.json",
        "query_id": "S-B3", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "primary", "expected_results": 63,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 300, "max_pages": 12, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-B4_pilot-population-wildcard.json",
        "raw_file": "SLR/SLR1/searches/scopus/S-B4_pilot-population-wildcard.json",
        "query_id": "S-B4", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "primary", "expected_results": 58,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 300, "max_pages": 12, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-A1-F1-full.json",
        "raw_file": "SLR/SLR1/searches/ieee-xplore/I-A1-F1-full.json",
        "query_id": "I-A1-F1", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "A", "search_phase": "primary", "expected_results": 4,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-A2-F1-full.json",
        "raw_file": "SLR/SLR1/searches/ieee-xplore/I-A2-F1-full.json",
        "query_id": "I-A2-F1", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "A", "search_phase": "primary", "expected_results": 2,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-A4-F1-full.json",
        "raw_file": "SLR/SLR1/searches/ieee-xplore/I-A4-F1-full.json",
        "query_id": "I-A4-F1", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "A", "search_phase": "primary", "expected_results": 4,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-A5-F1-full.json",
        "raw_file": "SLR/SLR1/searches/ieee-xplore/I-A5-F1-full.json",
        "query_id": "I-A5-F1", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "A", "search_phase": "primary", "expected_results": 2,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-B1-F1-full.json",
        "raw_file": "SLR/SLR1/searches/ieee-xplore/I-B1-F1-full.json",
        "query_id": "I-B1-F1", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "B", "search_phase": "primary", "expected_results": 37,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-B2-F1-full.json",
        "raw_file": "SLR/SLR1/searches/ieee-xplore/I-B2-F1-full.json",
        "query_id": "I-B2-F1", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "B", "search_phase": "primary", "expected_results": 41,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-CG-M3-P1-digital-thread-twin-stream-b.json",
        "raw_file": "SLR/SLR1/searches/coverage-gap/S-CG-M3-P1-digital-thread-twin-stream-b.json",
        "query_id": "S-CG-M3", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "coverage_gap", "expected_results": 21,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 100, "max_pages": 4, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-CG-M3-F1-digital-thread-twin-stream-b-full.json",
        "raw_file": "SLR/SLR1/searches/coverage-gap/I-CG-M3-F1-digital-thread-twin-stream-b-full.json",
        "query_id": "I-CG-M3", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "B", "search_phase": "coverage_gap", "expected_results": 19,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json",
        "raw_file": "SLR/SLR1/searches/coverage-gap/S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json",
        "query_id": "S-CG-M3R1", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "coverage_gap", "expected_results": 7,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 100, "max_pages": 4, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-CG-M4R1-P1-executable-integration-structured-stream-b.json",
        "raw_file": "SLR/SLR1/searches/coverage-gap/S-CG-M4R1-P1-executable-integration-structured-stream-b.json",
        "query_id": "S-CG-M4R1", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "coverage_gap", "expected_results": 2,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 100, "max_pages": 4, "open_access_filter": False},
    },
    {
        "merge_input": "scopus__S-CG-M5-P1-model-based-conceptual-design-stream-b.json",
        "raw_file": "SLR/SLR1/searches/coverage-gap/S-CG-M5-P1-model-based-conceptual-design-stream-b.json",
        "query_id": "S-CG-M5", "source": "Scopus", "source_slug": "scopus",
        "stream": "B", "search_phase": "coverage_gap", "expected_results": 1,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "document_types": ["ar", "cp", "ch"], "limit": 100, "max_pages": 4, "open_access_filter": False},
    },
    {
        "merge_input": "ieee-xplore__I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json",
        "raw_file": "SLR/SLR1/searches/coverage-gap/I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json",
        "query_id": "I-CG-M6", "source": "IEEE Xplore", "source_slug": "ieee_xplore",
        "stream": "B", "search_phase": "coverage_gap", "expected_results": 1,
        "filters": {"years": "2013-2026 inclusive", "language": "English", "content_types": ["Journals", "Conferences", "Books"], "limit": 100, "page_size": 100, "max_pages": 1, "open_access_filter": False},
    },
]

DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
NON_ALNUM = re.compile(r"[^a-z0-9]+")

# The preceding identity audit found no title/year pair that remained in
# different DOI/source-record components.  Keep explicit whitelists so a later
# rerun cannot silently introduce a title-based merge without documented review.
MANUALLY_CONFIRMED_TITLE_YEAR_EDGES: set[tuple[str, Any]] = set()
MANUALLY_CONFIRMED_TITLE_ONLY_EDGES: set[str] = set()


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, left: int, right: int) -> bool:
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return False
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1
        return True

    def count_components(self) -> int:
        return len({self.find(i) for i in range(len(self.parent))})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_doi(value: Any) -> str:
    text = DOI_PREFIX.sub("", str(value or "").strip()).strip().lower()
    return text.rstrip(".,;:)]}")


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    return NON_ALNUM.sub(" ", text).strip()


def is_present(value: Any) -> bool:
    return value not in (None, "", [], {})


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def distinct_nonempty(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for value in values:
        if not is_present(value):
            continue
        key = canonical_json(value)
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def mixed_case_score(title: str) -> int:
    letters = [ch for ch in title if ch.isalpha()]
    if not letters:
        return 0
    lower = sum(ch.islower() for ch in letters)
    upper = sum(ch.isupper() for ch in letters)
    return 1 if lower and upper else 0


def occurrence_quality(event: dict[str, Any]) -> tuple[Any, ...]:
    raw = event["source_record"]
    return (
        int(bool(raw.get("authors"))),
        int(bool(raw.get("abstract"))),
        len(str(raw.get("abstract", ""))),
        int(bool(raw.get("documentType"))),
        int(bool(raw.get("publicationTitle"))),
        int(bool(raw.get("doi"))),
        mixed_case_score(str(raw.get("title", ""))),
        int(event["source"] == "IEEE Xplore"),
        -event["input_order"],
        -event["source_rank"],
    )


def choose_mode_or_preferred(values: list[Any], preferred: Any) -> Any:
    present = [value for value in values if is_present(value)]
    if not present:
        return None if preferred is None else preferred
    counts = Counter(canonical_json(value) for value in present)
    max_count = max(counts.values())
    tied = {key for key, count in counts.items() if count == max_count}
    preferred_key = canonical_json(preferred) if is_present(preferred) else None
    if preferred_key in tied:
        return preferred
    for value in present:
        if canonical_json(value) in tied:
            return value
    return present[0]


def select_title(events: list[dict[str, Any]], preferred_event: dict[str, Any]) -> str:
    titles = [str(e["source_record"].get("title", "")).strip() for e in events]
    preferred_title = str(preferred_event["source_record"].get("title", "")).strip()
    mixed = [title for title in titles if mixed_case_score(title)]
    if mixed:
        return max(mixed, key=lambda value: (len(value), value))
    return preferred_title or max(titles, key=lambda value: (len(value), value))


def select_longest(events: list[dict[str, Any]], field: str, preferred_event: dict[str, Any]) -> Any:
    values = [e["source_record"].get(field) for e in events]
    present = [value for value in values if is_present(value)]
    if not present:
        return None if field != "authors" else []
    if isinstance(present[0], list):
        return max(present, key=lambda value: (len(value), canonical_json(value)))
    return max(present, key=lambda value: (len(str(value)), str(value)))


def preferred_nonempty(events: list[dict[str, Any]], field: str, preferred_event: dict[str, Any]) -> Any:
    preferred = preferred_event["source_record"].get(field)
    if is_present(preferred):
        return preferred
    for event in events:
        value = event["source_record"].get(field)
        if is_present(value):
            return value
    return None


def event_summary(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "occurrence_id": event["occurrence_id"],
        "source": event["source"],
        "source_slug": event["source_slug"],
        "query_id": event["query_id"],
        "exact_query": event["exact_query"],
        "filters": event["filters"],
        "stream": event["stream"],
        "search_phase": event["search_phase"],
        "input_file": event["raw_file"],
        "isolated_merge_input_file": event["merge_input_path"],
        "source_rank": event["source_rank"],
        "source_paperId": event["source_paper_id"],
        "source_doi": event["normalized_doi"],
        "source_title": event["source_record"].get("title", ""),
        "source_year": event["source_record"].get("year"),
        "search_extracted_at": event["search_extracted_at"],
        "source_record": deepcopy(event["source_record"]),
    }


def metadata_conflicts(events: list[dict[str, Any]]) -> dict[str, list[Any]]:
    fields = [
        "title", "doi", "year", "authors", "abstract", "citationCount",
        "openAccess_pdf", "url", "publicationTitle", "publicationDate",
        "documentType", "contentType", "accessType",
    ]
    output: dict[str, list[Any]] = {}
    for field in fields:
        values = distinct_nonempty([event["source_record"].get(field) for event in events])
        if len(values) > 1:
            output[field] = values
    return output


def group_members(uf: UnionFind, n: int) -> dict[int, list[int]]:
    result: dict[int, list[int]] = defaultdict(list)
    for index in range(n):
        result[uf.find(index)].append(index)
    return result


def source_and_stream_counts(clusters: list[list[dict[str, Any]]]) -> dict[str, Any]:
    source_counter: Counter[str] = Counter()
    stream_counter: Counter[str] = Counter()
    source_patterns: Counter[str] = Counter()
    stream_patterns: Counter[str] = Counter()
    phase_counter: Counter[str] = Counter()
    for cluster in clusters:
        sources = tuple(sorted({event["source"] for event in cluster}))
        streams = tuple(sorted({event["stream"] for event in cluster}))
        phases = tuple(sorted({event["search_phase"] for event in cluster}))
        for source in sources:
            source_counter[source] += 1
        for stream in streams:
            stream_counter[stream] += 1
        for phase in phases:
            phase_counter[phase] += 1
        source_patterns[" + ".join(sources)] += 1
        stream_patterns[" + ".join(streams)] += 1
    return {
        "unique_candidates_with_source": dict(sorted(source_counter.items())),
        "unique_candidates_by_source_pattern": dict(sorted(source_patterns.items())),
        "unique_candidates_with_stream": dict(sorted(stream_counter.items())),
        "unique_candidates_by_stream_pattern": dict(sorted(stream_patterns.items())),
        "unique_candidates_with_search_phase": dict(sorted(phase_counter.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merge-input-dir", type=Path, required=True)
    parser.add_argument("--stock-output", type=Path, required=True)
    parser.add_argument("--merged-output", type=Path, required=True)
    parser.add_argument("--dedup-report-output", type=Path, required=True)
    parser.add_argument("--freeze-output", type=Path, required=True)
    args = parser.parse_args()

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    raw_events: list[dict[str, Any]] = []
    input_inventory: list[dict[str, Any]] = []
    raw_source_counts: Counter[str] = Counter()
    raw_stream_counts: Counter[str] = Counter()
    raw_phase_counts: Counter[str] = Counter()

    for input_order, specification in enumerate(INPUTS):
        copied_path = args.merge_input_dir / specification["merge_input"]
        raw_path = Path(specification["raw_file"])
        if not copied_path.is_file() or not raw_path.is_file():
            raise RuntimeError(f"Missing required merge input or source artifact: {copied_path} / {raw_path}")
        copied_hash, raw_hash = sha256(copied_path), sha256(raw_path)
        if copied_hash != raw_hash:
            raise RuntimeError(f"Isolated copy differs from retained raw artifact: {copied_path}")
        with copied_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        results = data.get("results")
        if not isinstance(results, list):
            raise RuntimeError(f"No valid results array in {copied_path}")
        if len(results) != specification["expected_results"]:
            raise RuntimeError(
                f"Unexpected result count in {copied_path}: {len(results)} != {specification['expected_results']}"
            )
        if data.get("total") != specification["expected_results"]:
            raise RuntimeError(f"Unexpected reported total in {copied_path}: {data.get('total')}")
        extracted_at = (data.get("output_metadata") or {}).get("extracted_at")
        input_inventory.append({
            **{key: value for key, value in specification.items() if key != "merge_input"},
            "merge_input_file": str(copied_path),
            "raw_file_sha256": raw_hash,
            "merge_input_sha256": copied_hash,
            "reported_total": data.get("total"),
            "results_retrieved_field": data.get("results_retrieved", len(results)),
            "results_in_file": len(results),
            "exact_query": data.get("query", ""),
            "search_extracted_at": extracted_at,
        })
        for rank, raw in enumerate(results, start=1):
            if not isinstance(raw, dict) or not str(raw.get("title", "")).strip():
                raise RuntimeError(f"Nonbibliographic/untitled record in accepted input {copied_path}, rank {rank}")
            event = {
                "input_order": input_order,
                "occurrence_id": f"{specification['query_id']}:{rank}",
                "query_id": specification["query_id"],
                "source": specification["source"],
                "source_slug": specification["source_slug"],
                "stream": specification["stream"],
                "search_phase": specification["search_phase"],
                "filters": deepcopy(specification["filters"]),
                "raw_file": specification["raw_file"],
                "merge_input_path": str(copied_path),
                "source_rank": rank,
                "exact_query": data.get("query", ""),
                "search_extracted_at": extracted_at,
                "source_record": deepcopy(raw),
                "source_paper_id": str(raw.get("paperId", "")).strip(),
                "normalized_doi": normalize_doi(raw.get("doi")),
                "normalized_title": normalize_title(raw.get("title")),
                "year": raw.get("year"),
            }
            raw_events.append(event)
            raw_source_counts[event["source"]] += 1
            raw_stream_counts[event["stream"]] += 1
            raw_phase_counts[event["search_phase"]] += 1

    if len(raw_events) != 352:
        raise RuntimeError(f"Closed final input inventory should contain 352 occurrences, got {len(raw_events)}")

    # Stage 1: normalized DOI is the preferred cross-source identity key.
    uf = UnionFind(len(raw_events))
    doi_groups: dict[str, list[int]] = defaultdict(list)
    for index, event in enumerate(raw_events):
        if event["normalized_doi"]:
            doi_groups[event["normalized_doi"]].append(index)
    doi_merges = 0
    for indices in doi_groups.values():
        head = indices[0]
        for index in indices[1:]:
            doi_merges += int(uf.union(head, index))
    components_after_doi = uf.count_components()

    # Stage 2: an exact stable ID from the same source safely joins metadata
    # variants or repeated query occurrences where DOI is absent/inconsistent.
    source_id_groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, event in enumerate(raw_events):
        if event["source_paper_id"]:
            source_id_groups[(event["source_slug"], event["source_paper_id"].lower())].append(index)
    source_id_merges = 0
    for indices in source_id_groups.values():
        head = indices[0]
        for index in indices[1:]:
            source_id_merges += int(uf.union(head, index))
    components_after_source_id = uf.count_components()

    # Stage 3: only title/year relationships explicitly confirmed in the source
    # audit can create a new cross-component link.  This run had no such edge:
    # all exact title/year repetitions already shared DOI or source record ID.
    title_year_groups: dict[tuple[str, Any], list[int]] = defaultdict(list)
    title_groups: dict[str, list[int]] = defaultdict(list)
    for index, event in enumerate(raw_events):
        if event["normalized_title"]:
            title_year_groups[(event["normalized_title"], event["year"])].append(index)
            title_groups[event["normalized_title"]].append(index)
    unreviewed_title_year_groups: list[dict[str, Any]] = []
    title_year_merges = 0
    for key, indices in title_year_groups.items():
        roots = {uf.find(index) for index in indices}
        if len(roots) <= 1:
            continue
        if key not in MANUALLY_CONFIRMED_TITLE_YEAR_EDGES:
            unreviewed_title_year_groups.append({
                "normalized_title": key[0], "year": key[1],
                "occurrence_ids": [raw_events[index]["occurrence_id"] for index in indices],
            })
            continue
        head = indices[0]
        for index in indices[1:]:
            title_year_merges += int(uf.union(head, index))
    components_after_title_year = uf.count_components()

    # Stage 4: title-only matching is deliberately unavailable unless an
    # explicit bibliographically safe confirmation has been recorded.
    unreviewed_title_only_groups: list[dict[str, Any]] = []
    title_only_merges = 0
    for title, indices in title_groups.items():
        roots = {uf.find(index) for index in indices}
        years = {raw_events[index]["year"] for index in indices}
        if len(roots) <= 1 or len(years) <= 1:
            continue
        if title not in MANUALLY_CONFIRMED_TITLE_ONLY_EDGES:
            unreviewed_title_only_groups.append({
                "normalized_title": title,
                "years": sorted(year for year in years if year is not None),
                "occurrence_ids": [raw_events[index]["occurrence_id"] for index in indices],
            })
            continue
        head = indices[0]
        for index in indices[1:]:
            title_only_merges += int(uf.union(head, index))
    components_after_title_only = uf.count_components()

    # Do not silently merge an unreviewed title relation.  The queues remain in
    # the report as a future-run guard; their existence does not affect this run.
    components = group_members(uf, len(raw_events))
    clusters = [
        sorted([raw_events[index] for index in indices], key=lambda event: (event["input_order"], event["source_rank"]))
        for _, indices in sorted(components.items(), key=lambda item: min(item[1]))
    ]

    merged_records: list[dict[str, Any]] = []
    cluster_report: list[dict[str, Any]] = []
    for cluster in clusters:
        preferred_event = max(cluster, key=occurrence_quality)
        title = select_title(cluster, preferred_event)
        doi_values = sorted({event["normalized_doi"] for event in cluster if event["normalized_doi"]})
        selected_doi = preferred_nonempty(cluster, "doi", preferred_event)
        normalized_selected_doi = normalize_doi(selected_doi)
        if not normalized_selected_doi and doi_values:
            normalized_selected_doi = doi_values[0]
        year = choose_mode_or_preferred([event["source_record"].get("year") for event in cluster], preferred_event["source_record"].get("year"))
        authors = select_longest(cluster, "authors", preferred_event)
        abstract = select_longest(cluster, "abstract", preferred_event)
        citation_values = [event["source_record"].get("citationCount", 0) or 0 for event in cluster]
        citation_count = max(citation_values) if citation_values else 0
        oa_values = [
            (event["source_record"].get("openAccess_pdf") or {}).get("url")
            for event in cluster
            if isinstance(event["source_record"].get("openAccess_pdf"), dict)
        ]
        open_access_pdf_url = next((str(value) for value in oa_values if value), None)
        landing_page_urls = distinct_nonempty([event["source_record"].get("url") for event in cluster])
        source_identifiers = [
            {"source": source, "paperId": paper_id}
            for source, paper_id in sorted({(event["source"], event["source_paper_id"]) for event in cluster if event["source_paper_id"]})
        ]
        if normalized_selected_doi:
            identity_key = f"doi:{normalized_selected_doi}"
        elif title and year is not None:
            identity_key = f"title-year:{normalize_title(title)}|{year}"
        elif title:
            identity_key = f"title:{normalize_title(title)}"
        else:
            identity_key = "source-record:" + "+".join(f"{e['source_slug']}:{e['source_paper_id']}" for e in cluster)
        discovery_streams = sorted({event["stream"] for event in cluster})
        discovery_phases = sorted({event["search_phase"] for event in cluster})
        query_ids = sorted({event["query_id"] for event in cluster})
        sources = sorted({event["source"] for event in cluster})
        missingness = {
            "abstract_missing": not bool(abstract),
            "authors_missing": not bool(authors),
            "year_missing": year is None,
            "doi_missing": not bool(normalized_selected_doi),
            "abstract_truncated_in_any_source": any(bool(event["source_record"].get("abstract_is_truncated")) for event in cluster),
        }
        raw_event_summaries = [event_summary(event) for event in cluster]
        selected_from = {
            "occurrence_id": preferred_event["occurrence_id"],
            "source": preferred_event["source"],
            "query_id": preferred_event["query_id"],
            "source_rank": preferred_event["source_rank"],
        }
        record = {
            "report_id": "",  # assigned after deterministic identity-key ordering
            "candidate_id": "",
            "corpus_id": "",  # a stable new-run identifier, never a legacy paper ID
            "dedup_key": identity_key,
            "title": title,
            "doi": normalized_selected_doi or None,
            "authors": authors or [],
            "year": year,
            "abstract": abstract or "",
            "citationCount": citation_count,
            "openAccess_pdf_url": open_access_pdf_url,
            "paperId": preferred_event["source_paper_id"] or None,
            "source_identifiers": source_identifiers,
            "landing_page_urls": landing_page_urls,
            "metadata_missingness": missingness,
            "metadata_conflicts": metadata_conflicts(cluster),
            "metadata_preference_rules": {
                "record_preference": "Prefer richer supplied metadata (authors, then abstract length, then publication type/venue, then DOI); at a tie prefer IEEE Xplore because the corresponding Scopus rows are known to lack abstracts/authors, then fixed input order and source rank.",
                "title": "Prefer a mixed-case title variant; otherwise prefer the selected rich record/longest title.",
                "authors": "Prefer the nonempty list with most supplied names.",
                "abstract": "Prefer the longest nonempty supplied abstract; truncation remains flagged rather than silently treated as complete.",
                "year": "Use modal nonempty source year; tie resolves to selected rich record.",
                "citationCount": "Use the maximum supplied source snapshot and retain conflicting snapshots in provenance/metadata_conflicts.",
                "doi": "Use normalized DOI from the selected rich record; retain all source variants in provenance/metadata_conflicts.",
                "openAccess_pdf_url": "Use a supplied open-access PDF URL only; publisher landing pages are kept separately and are not called open access.",
            },
            "metadata_selected_from": selected_from,
            "sources": sources,
            "discovery_streams": discovery_streams,
            "discovery_phases": discovery_phases,
            "discovery_query_ids": query_ids,
            "duplicate_count": len(cluster),
            "provenance": raw_event_summaries,
        }
        merged_records.append(record)
        cluster_report.append({
            "dedup_key": identity_key,
            "raw_occurrence_count": len(cluster),
            "occurrence_ids": [event["occurrence_id"] for event in cluster],
            "sources": sources,
            "query_ids": query_ids,
            "streams": discovery_streams,
            "identity_evidence": {
                "normalized_dois": doi_values,
                "same_source_identifiers": source_identifiers,
                "manual_title_year_edge_used": False,
                "title_only_edge_used": False,
            },
            "metadata_conflict_fields": sorted(record["metadata_conflicts"]),
        })

    merged_records.sort(key=lambda record: (record["dedup_key"], normalize_title(record["title"]), str(record["year"])))
    for index, record in enumerate(merged_records, start=1):
        report_id = f"{RUN_ID}-r{index:04d}"
        record["report_id"] = report_id
        record["candidate_id"] = report_id
        record["corpus_id"] = report_id
    report_id_by_key = {record["dedup_key"]: record["report_id"] for record in merged_records}
    for cluster in cluster_report:
        cluster["report_id"] = report_id_by_key[cluster["dedup_key"]]
    cluster_report.sort(key=lambda cluster: cluster["report_id"])

    cluster_stats = source_and_stream_counts(clusters)
    stock_data: dict[str, Any] = {}
    if args.stock_output.is_file():
        with args.stock_output.open(encoding="utf-8") as fh:
            stock_data = json.load(fh)
        stock_summary = stock_data.get("dedup_summary") or {}
        if stock_summary.get("raw_results") != len(raw_events) or stock_summary.get("unique_results") != len(merged_records):
            raise RuntimeError("Stock-merger diagnostic does not reconcile with the closed 17-file input inventory")
    stock_provenance_sources = Counter(
        event.get("source", "")
        for result in stock_data.get("results", [])
        for event in result.get("provenance", [])
    )

    dedup_summary = {
        "input_files": len(INPUTS),
        "raw_bibliographic_occurrences": len(raw_events),
        "raw_occurrences_by_source": dict(sorted(raw_source_counts.items())),
        "raw_occurrences_by_stream": dict(sorted(raw_stream_counts.items())),
        "raw_occurrences_by_search_phase": dict(sorted(raw_phase_counts.items())),
        "unique_candidates": len(merged_records),
        "duplicates_removed": len(raw_events) - len(merged_records),
        "unique_yield": cluster_stats,
    }
    merged_payload = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "independently_rediscovered_candidate_set": True,
        "anti_anchoring_status": "Built only from the 17 isolated final accepted new-run database artifacts; retained markdown/pdf cache was not read before this freeze.",
        "input_inventory": input_inventory,
        "dedup_summary": dedup_summary,
        "results": merged_records,
    }
    # The full-file hash freezes this exact run artifact, including its timestamp.
    # This second hash excludes only generated_at so identical inputs and logic
    # reproduce a stable scientific-content digest across reruns.
    timestamp_free_payload = {key: value for key, value in merged_payload.items() if key != "generated_at"}
    merged_content_hash = hashlib.sha256(canonical_json(timestamp_free_payload).encode("utf-8")).hexdigest()
    args.merged_output.parent.mkdir(parents=True, exist_ok=True)
    with args.merged_output.open("w", encoding="utf-8") as fh:
        json.dump(merged_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    merged_hash = sha256(args.merged_output)
    dedup_report = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "scope": "Second deterministic pass over only the isolated final accepted input copies; no retained cache, legacy corpus, or supplementary failure artifact was used.",
        "input_inventory": input_inventory,
        "stock_merger_audit": {
            "authoritative": False,
            "superseded_by": str(args.merged_output),
            "command": "uv run ~/agent-tools/academic-research/skills/academic-search/scripts/merge_search_results.py --input SLR/SLR1/searches/merge-inputs --output-path SLR/SLR1/searches/integration/stock-merged-candidates.json",
            "stock_output": str(args.stock_output),
            "stock_summary": stock_data.get("dedup_summary", {}),
            "stock_provenance_source_labels_by_raw_event": dict(sorted(stock_provenance_sources.items())),
            "correction": "The stock merger correctly read the 17 isolated files but its infer_source implementation has a Scopus branch and no IEEE Xplore branch. All 110 IEEE raw events were labeled `unknown`; this second pass restores IEEE Xplore from the fixed source-prefixed input inventory and preserves source records/provenance.",
        },
        "identity_rules_in_order": [
            "normalized DOI: resolver/prefix removed, lower-case, terminal punctuation removed",
            "same-source stable paperId: only within the same named source",
            "manually confirmed normalized title + year: explicit whitelist only; zero new edges were needed in this run",
            "manually confirmed title-only fallback: explicit whitelist only; zero edges used in this run",
        ],
        "stage_counts": {
            "raw_occurrences": len(raw_events),
            "after_normalized_doi": components_after_doi,
            "after_same_source_paper_id": components_after_source_id,
            "after_manually_confirmed_title_year": components_after_title_year,
            "after_bibliographically_safe_title_only": components_after_title_only,
            "final_unique_candidates": len(merged_records),
            "duplicates_removed": len(raw_events) - len(merged_records),
            "merges_by_stage": {
                "normalized_doi": doi_merges,
                "same_source_paper_id": source_id_merges,
                "manually_confirmed_title_year": title_year_merges,
                "bibliographically_safe_title_only": title_only_merges,
            },
        },
        "manual_title_matching_audit": {
            "manual_title_year_whitelist": [],
            "manual_title_only_whitelist": [],
            "unreviewed_exact_title_year_cross_component_queue": unreviewed_title_year_groups,
            "unreviewed_title_only_cross_year_queue": unreviewed_title_only_groups,
            "decision": "No unlinked normalized title+year pair remained after DOI and same-source paperId matching, and no title-only cross-year collision existed. Therefore no title-based edge was needed or silently applied.",
            "near_title_nonmerge_check": [
                {
                    "records": [
                        "10.1109/aero.2015.7118965", "10.1109/aero.2016.7500592",
                        "10.1109/aero.2017.7943691", "10.2514/6.2018-5328"
                    ],
                    "decision": "not_merged",
                    "reason": "Highly similar CubeSat MBSE reference-model interim-status titles are explicitly numbered and separately dated/DOI-identified reports (#/year variants), so title similarity is not bibliographically safe identity evidence.",
                }
            ],
        },
        "metadata_preference_rules": merged_records[0]["metadata_preference_rules"] if merged_records else {},
        "summary": dedup_summary,
        "candidate_set_path": str(args.merged_output),
        "candidate_set_sha256": merged_hash,
        "candidate_set_timestamp_free_content_sha256": merged_content_hash,
        "clusters": cluster_report,
    }
    args.dedup_report_output.parent.mkdir(parents=True, exist_ok=True)
    with args.dedup_report_output.open("w", encoding="utf-8") as fh:
        json.dump(dedup_report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    freeze_payload = {
        "review_run_id": RUN_ID,
        "frozen_at": now,
        "freeze_stage": "independent primary-and-retained-coverage-gap candidate merge completed before retained markdown/pdf cache inspection",
        "candidate_set": {
            "path": str(args.merged_output),
            "sha256": merged_hash,
            "timestamp_free_content_sha256": merged_content_hash,
            "timestamp_free_content_hash_rule": "SHA-256 of canonical sorted compact JSON after removing only top-level generated_at",
            "unique_candidates": len(merged_records),
            "raw_bibliographic_occurrences": len(raw_events),
            "duplicates_removed": len(raw_events) - len(merged_records),
            "raw_occurrences_by_source": dict(sorted(raw_source_counts.items())),
            "raw_occurrences_by_stream": dict(sorted(raw_stream_counts.items())),
            "unique_yield_by_stream_pattern": cluster_stats["unique_candidates_by_stream_pattern"],
        },
        "input_files": [
            {
                "query_id": item["query_id"], "source": item["source"], "stream": item["stream"],
                "search_phase": item["search_phase"], "raw_file": item["raw_file"],
                "merge_input_file": item["merge_input_file"], "sha256": item["merge_input_sha256"],
                "raw_records": item["results_in_file"],
            }
            for item in input_inventory
        ],
        "excluded_from_merge": {
            "semantic_scholar": "9 documented HTTP 403 service failures; no source records", 
            "google_scholar": "6 documented service failures before rank 1; no source records",
            "note": "Non-retained pilots/refinements, count-only artifacts, failure artifacts, comparisons, audit-only coverage files, and prior merge outputs were excluded by the fixed 17-file inventory.",
        },
        "integrity_assertions": {
            "all_input_copies_match_raw_source_sha256": True,
            "all_input_files_are_final_accepted_artifacts": True,
            "retained_markdown_or_pdf_cache_read_before_freeze": False,
            "legacy_candidate_or_identifier_used": False,
        },
    }
    args.freeze_output.parent.mkdir(parents=True, exist_ok=True)
    with args.freeze_output.open("w", encoding="utf-8") as fh:
        json.dump(freeze_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(json.dumps({
        "status": "success",
        "raw_occurrences": len(raw_events),
        "unique_candidates": len(merged_records),
        "duplicates_removed": len(raw_events) - len(merged_records),
        "merged_candidate_sha256": merged_hash,
        "unreviewed_title_year_queue": len(unreviewed_title_year_groups),
        "unreviewed_title_only_queue": len(unreviewed_title_only_groups),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
