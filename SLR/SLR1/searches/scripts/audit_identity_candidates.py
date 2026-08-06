#!/usr/bin/env python3
"""Audit deduplication links among the isolated accepted new-run search inputs.

This helper is read-only with respect to raw search files.  It exists to make the
manual title/year-confirmation pass reproducible before the final deterministic
merge is built.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

INPUTS: list[dict[str, str]] = [
    {"file": "scopus__S-A1_pilot_r1.json", "query_id": "S-A1", "source": "Scopus", "stream": "A", "phase": "primary"},
    {"file": "scopus__S-A2_pilot_r1.json", "query_id": "S-A2", "source": "Scopus", "stream": "A", "phase": "primary"},
    {"file": "scopus__S-B1r1_pilot-population-wildcard.json", "query_id": "S-B1r1", "source": "Scopus", "stream": "B", "phase": "primary"},
    {"file": "scopus__S-B3_pilot-systems-engineering-relation.json", "query_id": "S-B3", "source": "Scopus", "stream": "B", "phase": "primary"},
    {"file": "scopus__S-B4_pilot-population-wildcard.json", "query_id": "S-B4", "source": "Scopus", "stream": "B", "phase": "primary"},
    {"file": "ieee-xplore__I-A1-F1-full.json", "query_id": "I-A1-F1", "source": "IEEE Xplore", "stream": "A", "phase": "primary"},
    {"file": "ieee-xplore__I-A2-F1-full.json", "query_id": "I-A2-F1", "source": "IEEE Xplore", "stream": "A", "phase": "primary"},
    {"file": "ieee-xplore__I-A4-F1-full.json", "query_id": "I-A4-F1", "source": "IEEE Xplore", "stream": "A", "phase": "primary"},
    {"file": "ieee-xplore__I-A5-F1-full.json", "query_id": "I-A5-F1", "source": "IEEE Xplore", "stream": "A", "phase": "primary"},
    {"file": "ieee-xplore__I-B1-F1-full.json", "query_id": "I-B1-F1", "source": "IEEE Xplore", "stream": "B", "phase": "primary"},
    {"file": "ieee-xplore__I-B2-F1-full.json", "query_id": "I-B2-F1", "source": "IEEE Xplore", "stream": "B", "phase": "primary"},
    {"file": "scopus__S-CG-M3-P1-digital-thread-twin-stream-b.json", "query_id": "S-CG-M3", "source": "Scopus", "stream": "B", "phase": "coverage_gap"},
    {"file": "ieee-xplore__I-CG-M3-F1-digital-thread-twin-stream-b-full.json", "query_id": "I-CG-M3", "source": "IEEE Xplore", "stream": "B", "phase": "coverage_gap"},
    {"file": "scopus__S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json", "query_id": "S-CG-M3R1", "source": "Scopus", "stream": "B", "phase": "coverage_gap"},
    {"file": "scopus__S-CG-M4R1-P1-executable-integration-structured-stream-b.json", "query_id": "S-CG-M4R1", "source": "Scopus", "stream": "B", "phase": "coverage_gap"},
    {"file": "scopus__S-CG-M5-P1-model-based-conceptual-design-stream-b.json", "query_id": "S-CG-M5", "source": "Scopus", "stream": "B", "phase": "coverage_gap"},
    {"file": "ieee-xplore__I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json", "query_id": "I-CG-M6", "source": "IEEE Xplore", "stream": "B", "phase": "coverage_gap"},
]

DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_doi(value: Any) -> str:
    text = DOI_PREFIX.sub("", str(value or "").strip()).strip().lower()
    return text.rstrip(".,;:)]}")


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    return NON_ALNUM.sub(" ", text).strip()


def concise(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "occurrence_id": rec["occurrence_id"],
        "source": rec["source"],
        "query_id": rec["query_id"],
        "stream": rec["stream"],
        "phase": rec["phase"],
        "rank": rec["rank"],
        "paperId": rec["paperId"],
        "doi": rec["doi"],
        "title": rec["title"],
        "normalized_title": rec["normalized_title"],
        "year": rec["year"],
        "authors": rec["authors"],
    }


def grouped_links(groups: dict[tuple[Any, ...], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out = []
    for key, items in groups.items():
        if len(items) > 1:
            out.append({"key": list(key), "occurrences": [concise(r) for r in items]})
    return sorted(out, key=lambda x: (str(x["key"]), x["occurrences"][0]["occurrence_id"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    args = parser.parse_args()

    occurrences: list[dict[str, Any]] = []
    for item in INPUTS:
        path = args.input_dir / item["file"]
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        for rank, raw in enumerate(data.get("results", []), 1):
            if not isinstance(raw, dict) or not str(raw.get("title", "")).strip():
                continue
            occurrence = {
                **item,
                "occurrence_id": f"{item['query_id']}:{rank}",
                "rank": rank,
                "paperId": str(raw.get("paperId", "")).strip(),
                "doi": normalize_doi(raw.get("doi")),
                "title": str(raw.get("title", "")).strip(),
                "normalized_title": normalize_title(raw.get("title")),
                "year": raw.get("year"),
                "authors": raw.get("authors", []) or [],
            }
            occurrences.append(occurrence)

    doi_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    source_id_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    title_year_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    title_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for rec in occurrences:
        if rec["doi"]:
            doi_groups[(rec["doi"],)].append(rec)
        if rec["paperId"]:
            source_id_groups[(rec["source"].lower(), rec["paperId"].lower())].append(rec)
        title_year_groups[(rec["normalized_title"], rec["year"])].append(rec)
        title_groups[(rec["normalized_title"],)].append(rec)

    # Fuzzy links are only an inspection queue: no link is asserted by this script.
    distinct_title_year = []
    seen = set()
    for rec in occurrences:
        key = (rec["normalized_title"], rec["year"])
        if key not in seen:
            seen.add(key)
            distinct_title_year.append(rec)
    fuzzy_links: list[dict[str, Any]] = []
    for i, left in enumerate(distinct_title_year):
        for right in distinct_title_year[i + 1:]:
            if not left["normalized_title"] or not right["normalized_title"]:
                continue
            if left["normalized_title"] == right["normalized_title"]:
                continue
            left_year, right_year = left["year"], right["year"]
            if isinstance(left_year, int) and isinstance(right_year, int) and abs(left_year - right_year) > 1:
                continue
            score = SequenceMatcher(None, left["normalized_title"], right["normalized_title"]).ratio()
            if score >= 0.88:
                fuzzy_links.append({
                    "similarity": round(score, 4),
                    "left": concise(left),
                    "right": concise(right),
                })
    fuzzy_links.sort(key=lambda x: (-x["similarity"], x["left"]["occurrence_id"], x["right"]["occurrence_id"]))

    title_only_cross_year = []
    for link in grouped_links(title_groups):
        years = {o["year"] for o in link["occurrences"]}
        if len(years) > 1:
            title_only_cross_year.append(link)

    payload = {
        "method": {
            "doi_normalization": "trim, remove DOI resolver/prefix, lower-case, strip terminal punctuation",
            "title_normalization": "Unicode NFKD de-accenting, lower-case, ampersand→and, non-alphanumerics collapsed",
            "warning": "Fuzzy and title-only links are review queues only; this artifact makes no deduplication decision.",
        },
        "input_count": len(INPUTS),
        "raw_bibliographic_occurrences": len(occurrences),
        "same_normalized_doi_groups": grouped_links(doi_groups),
        "same_source_paper_id_groups": grouped_links(source_id_groups),
        "same_normalized_title_year_groups": grouped_links(title_year_groups),
        "same_normalized_title_cross_year_groups": title_only_cross_year,
        "fuzzy_title_year_near_matches": fuzzy_links,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
