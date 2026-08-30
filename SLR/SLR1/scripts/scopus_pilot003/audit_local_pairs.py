#!/usr/bin/env python3
"""Audit declared pair expressions locally without filtering source records."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from queries import _schedule


SCHEMA = "slr1-scopus-pilot003-local-pair-audit/v1"
TOKEN = re.compile(r"[a-z0-9]+")


def tokens(value: str) -> list[str]:
    return TOKEN.findall(value.casefold())


def starts(haystack: list[str], needle: list[str]) -> list[tuple[int, int]]:
    if not needle:
        return []
    return [
        (index, index + len(needle))
        for index in range(len(haystack) - len(needle) + 1)
        if haystack[index : index + len(needle)] == needle
    ]


def has_exact_pair(text: str, left: str, right: str, max_between: int = 5) -> bool:
    field = tokens(text)
    left_occurrences = starts(field, tokens(left))
    right_occurrences = starts(field, tokens(right))
    return any(
        0 <= right_start - left_end <= max_between
        or 0 <= left_start - right_end <= max_between
        for left_start, left_end in left_occurrences
        for right_start, right_end in right_occurrences
    )


def records(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("output_metadata", {}).get("retrieval_complete") is not True:
        raise ValueError(f"Incomplete input: {path}")
    return value["results"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True, type=Path)
    parser.add_argument("--union", type=Path, help="Optional final union with recovered native abstracts")
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    if args.output_path.exists() or args.output_path.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output_path}")
    root = args.pilot_root
    abstract_by_id: dict[str, str] = {}
    if args.union is not None:
        union = json.loads(args.union.read_text(encoding="utf-8"))
        abstract_by_id = {
            row["paper_id"]: row["abstract"]
            for row in union["main"]["records"]
            if isinstance(row.get("abstract"), str) and row["abstract"]
        }
    inputs = {
        "BG1": ("G_model", root / "searches/main/strict-ids/BG1.json"),
        "BG2": ("G_structure", root / "searches/main/strict-ids/BG2.json"),
        "BC1": ("C1", root / "searches/main/strict-ids/BC1.json"),
        "BT2": ("T2", root / "searches/main/strict-ids/BT2.json"),
    }
    output: dict[str, Any] = {
        "schema_version": SCHEMA,
        "purpose": "Exact local checks use only retained title text. They are an audit of source W/6 fallback hits, never a source-record exclusion or a proof about unavailable abstract/indexed fields.",
        "max_intervening_lexical_tokens": 5,
        "source_fallback": "Scopus W/6; source result may use title, abstract, author keyword, or indexed metadata not retained in the no-abstract stable-ID pass.",
        "partitions": {},
        "not_applicable": {"B1": "No declared paired block", "B2": "No declared paired block"},
    }
    for partition, (concept_name, path) in inputs.items():
        pairs = _schedule.CONCEPTS[concept_name].pairs
        rows = records(path)
        matched = []
        abstract_checked = 0
        for row in rows:
            title = row.get("title") or ""
            abstract = abstract_by_id.get(row["paperId"], "")
            if abstract:
                abstract_checked += 1
            text = title + "\n" + abstract
            hits = [
                {"left": left, "right": right}
                for left, right in pairs
                if has_exact_pair(text, left, right)
            ]
            if hits:
                matched.append({"paper_id": row["paperId"], "pair_hits": hits, "native_abstract_checked": bool(abstract)})
        output["partitions"][partition] = {
            "concept": concept_name,
            "declared_pair_count": len(pairs),
            "source_record_count": len(rows),
            "native_abstracts_checked": abstract_checked,
            "exact_pair_match_count_in_retained_title_and_available_abstract": len(matched),
            "exact_pair_matches": matched,
            "action": "All source records retained regardless of local match; missing local match is expected when the source hit occurs in unavailable abstract/keyword/indexed metadata.",
        }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
