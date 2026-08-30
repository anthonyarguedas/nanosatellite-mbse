#!/usr/bin/env python3
"""Build and validate the literal IEEE Xplore Pilot 004 cell schedule.

The protocol-owned literals, declared pairs, and Boolean schedule are imported
from ``pilot_schedule``.  This script only partitions long IEEE expressions;
it does not add terms, wildcards, or source filters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PILOT_SCHEDULE_DIR = SCRIPT_DIR.parent / "pilot_schedule"
sys.path.insert(0, str(PILOT_SCHEDULE_DIR))

from queries import (  # noqa: E402
    CONCEPTS,
    MAIN_FACTORS,
    RENDERERS,
    partition_cells,
    partition_query,
)

SOURCE_ID = "ieee_xplore"
PILOT_ID = "004"
# Pilot 001/002 proved a 4,776-character literal A1 expression could reach
# IEEE's rendered query field.  5,000 is a conservative orchestration ceiling,
# not a claimed IEEE maximum.  It keeps every unproven longer expression in a
# lossless source-side cell union.
CELL_CHARACTER_LIMIT = 5_000
DIAGNOSTIC_CUTOFF = "2026-08-29"
YEAR_START = 2011
YEAR_END = 2026


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _cells(partition_id: str) -> tuple[dict[str, str], ...]:
    query = partition_query(SOURCE_ID, partition_id)
    if len(query) <= CELL_CHARACTER_LIMIT:
        return ({"cell_id": "full", "query": query},)
    return partition_cells(
        SOURCE_ID,
        partition_id,
        maximum_characters=CELL_CHARACTER_LIMIT,
    )


def _alternatives_for_factor(factor: tuple[str, ...]) -> tuple[str, ...]:
    return RENDERERS[SOURCE_ID].alternatives(factor)


def _partition_payload(partition_id: str) -> dict[str, Any]:
    full_query = partition_query(SOURCE_ID, partition_id)
    factors = MAIN_FACTORS[partition_id]
    cells = _cells(partition_id)
    return {
        "partition_id": partition_id,
        "boolean_factors": [list(factor) for factor in factors],
        "full_literal_query": full_query,
        "full_literal_query_sha256": _sha256(full_query),
        "full_literal_query_character_count": len(full_query),
        "cells": [
            {
                "cell_id": cell["cell_id"],
                "query": cell["query"],
                "query_sha256": _sha256(cell["query"]),
                "query_character_count": len(cell["query"]),
            }
            for cell in cells
        ],
        "lossless_union": {
            "required": len(cells) > 1,
            "basis": (
                "single complete source expression is within the conservative "
                "pilot ceiling"
                if len(cells) == 1
                else "Cartesian union of disjoint OR-factor chunks; records may overlap and must be deduplicated by Article Number"
            ),
        },
        "expected_factor_alternative_counts": {
            "factor_" + str(index + 1): sum(
                CONCEPTS[name].alternative_count for name in factor
            )
            for index, factor in enumerate(factors)
        },
    }


def build_schedule() -> dict[str, Any]:
    return {
        "schema_version": "slr1-ieee-xplore-pilot004-schedule/v1",
        "source": "IEEE Xplore",
        "source_id": SOURCE_ID,
        "pilot_id": PILOT_ID,
        "provenance": {
            "concept_renderer": "SLR/SLR1/scripts/pilot_schedule/queries.py",
            "renderer": SOURCE_ID,
            "strategy": "slr1-direct-query-schedule-v1",
            "literal_and_pair_policy": "all protocol literals and every declared unordered pair are rendered as literal All Metadata atoms; no wildcard is used",
        },
        "controls": {
            "publication_year_apply": {
                "year_start": YEAR_START,
                "year_end": YEAR_END,
                "inclusive": True,
                "source_field": "Publication Year",
                "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
                "cutoff_handling": "The source-native control is a year envelope. The diagnostic cutoff is recorded separately and is not Date Added or an unobserved native day filter.",
            },
            "date_added": {
                "applied": False,
                "reason": "Date Added is a separate IEEE indexing-date control and is not Date of Publication.",
            },
            "language": {"applied": False, "reason": "No validated lossless language control."},
            "publication_type": {"applied": False, "reason": "No validated lossless eligible-report type union."},
            "access": {"applied": False, "reason": "No access restriction is permitted."},
            "controlled_vocabulary": {"applied": False, "reason": "No source-specific descriptor supplement was validated for these concepts."},
            "wildcards": {"accepted": False, "used": False, "reason": "Pilot 003 candidate remains unaccepted without a partition-specific stable-ID comparison."},
        },
        "cell_policy": {
            "conservative_maximum_query_characters": CELL_CHARACTER_LIMIT,
            "basis": "Pilot 001/002 accepted a 4,776-character literal A1 readback. This pilot does not claim a native IEEE maximum; expressions longer than 5,000 characters are partitioned prospectively.",
            "stable_union_key": "IEEE Xplore Article Number (paperId/documentId)",
        },
        "partitions": [_partition_payload(partition_id) for partition_id in MAIN_FACTORS],
    }


def validate_schedule(schedule: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if schedule.get("source_id") != SOURCE_ID:
        failures.append("wrong source_id")
    expected_ids = tuple(MAIN_FACTORS)
    actual_ids = tuple(item.get("partition_id") for item in schedule.get("partitions", []))
    if actual_ids != expected_ids:
        failures.append(f"partition IDs differ: {actual_ids!r}")
    if schedule.get("controls", {}).get("wildcards", {}).get("used") is not False:
        failures.append("wildcards were used")

    for partition in schedule.get("partitions", []):
        partition_id = partition["partition_id"]
        expected_query = partition_query(SOURCE_ID, partition_id)
        if partition.get("full_literal_query") != expected_query:
            failures.append(f"{partition_id}: full query differs from pilot_schedule")
        cells = partition.get("cells", [])
        if not cells:
            failures.append(f"{partition_id}: no cells")
            continue
        expected_cells = _cells(partition_id)
        observed_pairs = tuple(
            (cell.get("cell_id"), cell.get("query")) for cell in cells
        )
        required_pairs = tuple(
            (cell["cell_id"], cell["query"]) for cell in expected_cells
        )
        if observed_pairs != required_pairs:
            failures.append(f"{partition_id}: cells differ from the prospective lossless renderer")
        observed_cells = [cell.get("query", "") for cell in cells]
        if any(len(query) > CELL_CHARACTER_LIMIT for query in observed_cells):
            failures.append(f"{partition_id}: a cell exceeds {CELL_CHARACTER_LIMIT}")
        if any("*" in query or "?" in query for query in observed_cells):
            failures.append(f"{partition_id}: a cell contains a wildcard")
        # Each term/pair atom in the protocol must survive into at least one
        # source-side cell.  The cells can overlap at the record level only.
        for factor in MAIN_FACTORS[partition_id]:
            for atom in _alternatives_for_factor(factor):
                if not any(atom in query for query in observed_cells):
                    failures.append(f"{partition_id}: missing atom {atom}")
        # Every cell must retain the Boolean conjunction between the semantic
        # factors; the schedule renderer writes one AND between each factor.
        minimum_ands = len(MAIN_FACTORS[partition_id]) - 1
        if any(query.count(" AND ") < minimum_ands for query in observed_cells):
            failures.append(f"{partition_id}: a cell lost a factor conjunction")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", type=Path)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    schedule = build_schedule()
    failures = validate_schedule(schedule) if args.validate else []
    if args.output_path:
        output = args.output_path
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            existing = json.loads(output.read_text(encoding="utf-8"))
            if existing != schedule:
                raise SystemExit(f"refusing to replace non-identical schedule: {output}")
        else:
            output.write_text(json.dumps(schedule, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.print_summary:
        for partition in schedule["partitions"]:
            print(
                f"{partition['partition_id']}: {len(partition['cells'])} cell(s); "
                f"full={partition['full_literal_query_character_count']} characters"
            )
    if failures:
        print("schedule validation failed:", *failures, sep="\n- ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
