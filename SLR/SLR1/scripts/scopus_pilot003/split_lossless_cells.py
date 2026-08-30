#!/usr/bin/env python3
"""Create a no-clobber two-way OR split of selected already-lossless cells."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "slr1-scopus-pilot003-nested-lossless-cell-plan/v1"


def split_top_level(value: str, separator: str) -> list[str]:
    depth = 0
    quoted = False
    start = 0
    parts: list[str] = []
    index = 0
    while index < len(value):
        character = value[index]
        if character == '"':
            quoted = not quoted
        elif not quoted:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            elif depth == 0 and value.startswith(separator, index):
                parts.append(value[start:index])
                start = index + len(separator)
                index += len(separator) - 1
        index += 1
    parts.append(value[start:])
    return parts


def unwrap(value: str) -> str:
    if not (value.startswith("(") and value.endswith(")")):
        raise ValueError("Expected a parenthesized source factor")
    return value[1:-1]


def balanced_index(parts: list[str]) -> int:
    if len(parts) < 2:
        raise ValueError("Cannot split a one-atom factor")
    return min(
        range(1, len(parts)),
        key=lambda index: abs(sum(map(len, parts[:index])) - sum(map(len, parts[index:]))),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-plan", required=True, type=Path)
    parser.add_argument("--cell-id", required=True, action="append")
    parser.add_argument("--factor-index", type=int, default=0)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    if args.output_path.exists() or args.output_path.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output_path}")
    parent = json.loads(args.parent_plan.read_text(encoding="utf-8"))
    source_cells = parent.get("all_cells", parent.get("cells", parent.get("children", [])))
    by_id = {cell.get("cell_id"): cell for cell in source_cells}
    children = []
    parents = []
    for cell_id in args.cell_id:
        cell = by_id.get(cell_id)
        if not isinstance(cell, dict) or not isinstance(cell.get("query"), str):
            raise SystemExit(f"Unknown parent cell {cell_id}")
        query = cell["query"]
        factors = split_top_level(query, " AND ")
        if not 0 <= args.factor_index < len(factors):
            raise SystemExit("factor index is outside the parent expression")
        alternatives = split_top_level(unwrap(factors[args.factor_index]), " OR ")
        pivot = balanced_index(alternatives)
        produced = []
        for suffix, alternatives_part in (("a", alternatives[:pivot]), ("b", alternatives[pivot:])):
            revised = list(factors)
            revised[args.factor_index] = "(" + " OR ".join(alternatives_part) + ")"
            child_query = " AND ".join(revised)
            child = {
                "cell_id": f"{cell_id}-{suffix}",
                "parent_cell_id": cell_id,
                "query": child_query,
                "query_sha256": hashlib.sha256(child_query.encode()).hexdigest(),
                "query_character_count": len(child_query),
            }
            produced.append(child)
            children.append(child)
        if alternatives != split_top_level(unwrap(factors[args.factor_index]), " OR "):
            raise AssertionError("Parent factor changed while splitting")
        parents.append(
            {
                "cell_id": cell_id,
                "query": query,
                "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
                "factor_index": args.factor_index,
                "factor_alternative_count": len(alternatives),
                "child_ids": [item["cell_id"] for item in produced],
            }
        )
    payload = {
        "schema_version": SCHEMA,
        "parent_plan": str(args.parent_plan),
        "partition_id": parent.get("partition_id"),
        "operation": "Split one parent OR factor into disjoint contiguous source-atom halves; all other factors are byte-for-byte retained.",
        "parents": parents,
        "children": children,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
