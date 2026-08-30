"""Lossless Springer Nature Link Pilot 003 query-cell plan.

This module imports the normative literals, pairs, Boolean factors, and renderer
from ``pilot_schedule``.  It does not substitute terms, add filters, or use
wildcards.  Cell plans only divide a source OR block; their set union is the
same semantic partition as the corresponding complete scheduled expression.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Iterable


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_PILOT_SCHEDULE_QUERIES = SCRIPTS_DIR / "pilot_schedule" / "queries.py"
_spec = spec_from_file_location("springer_pilot003_schedule_queries", _PILOT_SCHEDULE_QUERIES)
if _spec is None or _spec.loader is None:  # pragma: no cover - installation invariant
    raise RuntimeError(f"Could not load {_PILOT_SCHEDULE_QUERIES}")
_schedule = module_from_spec(_spec)
sys.modules[_spec.name] = _schedule
_spec.loader.exec_module(_schedule)

CONCEPTS = _schedule.CONCEPTS
MAIN_FACTORS = _schedule.MAIN_FACTORS
RENDERERS = _schedule.RENDERERS
partition_cells = _schedule.partition_cells
partition_query = _schedule.partition_query


SOURCE_ID = "springer_nature_link"
SCHEDULE_IDS = tuple(MAIN_FACTORS)
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"

# The first successful source readbacks showed a 3,525-character raw query;
# the 9,013-character BT2 row timed out.  These fixed cell boundaries were
# selected prospectively before their cell collections.  They divide OR
# alternatives only and never compress literals with a wildcard.
A2_CELL_MAXIMUM_CHARACTERS = 4_000
B2_CELL_MAXIMUM_CHARACTERS = 1_500
BT2_T2_CELL_MAXIMUM_CHARACTERS = 2_000


@dataclass(frozen=True)
class QueryCell:
    """One source-native exact query and its auditable semantic alternatives."""

    cell_id: str
    query: str
    alternatives: tuple[str, ...]


def direct_query(partition_id: str) -> str:
    """Return the unchanged scheduled Springer Keywords expression."""
    if partition_id not in MAIN_FACTORS:
        raise KeyError(f"Unknown main schedule partition: {partition_id}")
    return partition_query(SOURCE_ID, partition_id)


def generic_cells(partition_id: str, maximum_characters: int) -> tuple[QueryCell, ...]:
    """Expose pilot_schedule's lossless Cartesian OR-cell plan verbatim."""
    cells = partition_cells(
        SOURCE_ID,
        partition_id,
        maximum_characters=maximum_characters,
    )
    return tuple(
        QueryCell(
            cell_id=str(item["cell_id"]),
            query=str(item["query"]),
            # ``partition_cells`` constructs every query from the renderer's
            # alternatives.  The full partition alternatives are retained here
            # as the membership declaration, not a claim that a cell contains
            # every one of them.
            alternatives=(),
        )
        for item in cells
    )


def a2_cells() -> tuple[QueryCell, ...]:
    return generic_cells("A2", A2_CELL_MAXIMUM_CHARACTERS)


def b2_cells() -> tuple[QueryCell, ...]:
    return generic_cells("B2", B2_CELL_MAXIMUM_CHARACTERS)


def _t2_chunks(maximum_characters: int) -> tuple[tuple[str, ...], ...]:
    """Split only BT2's T2 OR alternatives, retaining complete P and M_B."""
    renderer = RENDERERS[SOURCE_ID]
    population = renderer.union(renderer.alternatives(("P",)))
    model = renderer.union(renderer.alternatives(("M_B",)))
    alternatives = renderer.alternatives(("T2",))

    chunks: list[tuple[str, ...]] = []
    current: list[str] = []
    for alternative in alternatives:
        candidate = [*current, alternative]
        query = renderer.and_token.join((population, model, renderer.union(candidate)))
        if len(query) <= maximum_characters:
            current = candidate
            continue
        if not current:
            raise ValueError("One BT2 alternative exceeds the source cell boundary")
        chunks.append(tuple(current))
        current = [alternative]
    if current:
        chunks.append(tuple(current))
    return tuple(chunks)


def bt2_cells() -> tuple[QueryCell, ...]:
    """Return the 11 lossless BT2 cells used after the raw row timed out."""
    renderer = RENDERERS[SOURCE_ID]
    population = renderer.union(renderer.alternatives(("P",)))
    model = renderer.union(renderer.alternatives(("M_B",)))
    chunks = _t2_chunks(BT2_T2_CELL_MAXIMUM_CHARACTERS)
    width = len(str(len(chunks)))
    return tuple(
        QueryCell(
            cell_id=f"T2-{index:0{width}d}-of-{len(chunks):0{width}d}",
            query=renderer.and_token.join((population, model, renderer.union(chunk))),
            alternatives=chunk,
        )
        for index, chunk in enumerate(chunks, start=1)
    )


def bt2_subcells(parent_index: int, *, alternatives_per_cell: int) -> tuple[QueryCell, ...]:
    """Split one BT2 T2 cell again after a documented pagination/detail failure.

    This is a source-route recovery only: P and M_B remain complete in every
    child, while the parent's already-declared T2 alternatives are divided in
    their original order.
    """
    parent = bt2_cells()[parent_index - 1]
    if alternatives_per_cell < 1:
        raise ValueError("alternatives_per_cell must be positive")
    renderer = RENDERERS[SOURCE_ID]
    population = renderer.union(renderer.alternatives(("P",)))
    model = renderer.union(renderer.alternatives(("M_B",)))
    chunks = tuple(
        parent.alternatives[index : index + alternatives_per_cell]
        for index in range(0, len(parent.alternatives), alternatives_per_cell)
    )
    width = len(str(len(chunks)))
    return tuple(
        QueryCell(
            cell_id=f"{parent.cell_id}-sub-{index:0{width}d}-of-{len(chunks):0{width}d}",
            query=renderer.and_token.join((population, model, renderer.union(chunk))),
            alternatives=chunk,
        )
        for index, chunk in enumerate(chunks, start=1)
    )


def all_source_queries() -> tuple[str, ...]:
    """Return all current direct and fallback-cell query text for wildcard audit."""
    return (
        *(direct_query(partition_id) for partition_id in SCHEDULE_IDS),
        *(cell.query for cell in a2_cells()),
        *(cell.query for cell in b2_cells()),
        *(cell.query for cell in bt2_cells()),
        *(cell.query for parent in (8, 10, 11) for cell in bt2_subcells(parent, alternatives_per_cell=5)),
        *(cell.query for cell in bt2_subcells(8, alternatives_per_cell=1)[10:15]),
    )


def assert_lossless_cell_membership() -> None:
    """Fail if a named cell plan stops matching the normative renderer plan."""
    for partition_id, maximum, cells in (
        ("A2", A2_CELL_MAXIMUM_CHARACTERS, a2_cells()),
        ("B2", B2_CELL_MAXIMUM_CHARACTERS, b2_cells()),
    ):
        expected = partition_cells(
            SOURCE_ID,
            partition_id,
            maximum_characters=maximum,
        )
        if tuple((cell.cell_id, cell.query) for cell in cells) != tuple(
            (str(item["cell_id"]), str(item["query"])) for item in expected
        ):
            raise AssertionError(f"{partition_id} cell plan differs from pilot_schedule")

    renderer = RENDERERS[SOURCE_ID]
    expected_t2 = renderer.alternatives(("T2",))
    observed_t2 = tuple(
        alternative for cell in bt2_cells() for alternative in cell.alternatives
    )
    if observed_t2 != expected_t2:
        raise AssertionError("BT2 T2 cell plan dropped, reordered, or added an alternative")

    expected_prefix = renderer.and_token.join(
        (
            renderer.union(renderer.alternatives(("P",))),
            renderer.union(renderer.alternatives(("M_B",))),
        )
    )
    for cell in bt2_cells():
        if not cell.query.startswith(expected_prefix + renderer.and_token):
            raise AssertionError("BT2 cell changed P or M_B rather than only splitting T2")
        if len(cell.query) > BT2_T2_CELL_MAXIMUM_CHARACTERS:
            raise AssertionError("BT2 cell exceeds its validated source boundary")

    for parent_index in (8, 10, 11):
        parent = bt2_cells()[parent_index - 1]
        children = bt2_subcells(parent_index, alternatives_per_cell=5)
        if tuple(item for child in children for item in child.alternatives) != parent.alternatives:
            raise AssertionError("BT2 recovery subcells changed their parent T2 membership")
    pair_children = bt2_subcells(8, alternatives_per_cell=1)[10:15]
    if tuple(item for child in pair_children for item in child.alternatives) != bt2_cells()[7].alternatives[10:15]:
        raise AssertionError("BT2 pair recovery changed the failed T2 recovery subcell")

    if any("*" in query or "?" in query for query in all_source_queries()):
        raise AssertionError("An unvalidated wildcard appeared in a Springer Pilot 003 query")


def audit() -> dict[str, object]:
    """Produce a small JSON-safe construction receipt for the pilot artifact."""
    assert_lossless_cell_membership()
    return {
        "schema_version": "springer-pilot003-query-plan/v1",
        "source_id": SOURCE_ID,
        "date_window": {"start": DATE_START, "end": DATE_END},
        "schedule_ids": list(SCHEDULE_IDS),
        "direct_queries": {
            partition_id: {
                "query": direct_query(partition_id),
                "characters": len(direct_query(partition_id)),
            }
            for partition_id in SCHEDULE_IDS
        },
        "lossless_cells": {
            "A2": {
                "maximum_characters": A2_CELL_MAXIMUM_CHARACTERS,
                "cells": [
                    {"cell_id": cell.cell_id, "query": cell.query, "characters": len(cell.query)}
                    for cell in a2_cells()
                ],
            },
            "B2": {
                "maximum_characters": B2_CELL_MAXIMUM_CHARACTERS,
                "cells": [
                    {"cell_id": cell.cell_id, "query": cell.query, "characters": len(cell.query)}
                    for cell in b2_cells()
                ],
            },
            "BT2": {
                "maximum_characters": BT2_T2_CELL_MAXIMUM_CHARACTERS,
                "cells": [
                    {
                        "cell_id": cell.cell_id,
                        "query": cell.query,
                        "characters": len(cell.query),
                        "t2_alternative_count": len(cell.alternatives),
                    }
                    for cell in bt2_cells()
                ],
                "recovery_subcells": {
                    f"T2-{parent:02d}-of-11": [
                        {
                            "cell_id": cell.cell_id,
                            "query": cell.query,
                            "characters": len(cell.query),
                            "t2_alternative_count": len(cell.alternatives),
                        }
                        for cell in bt2_subcells(parent, alternatives_per_cell=5)
                    ]
                    for parent in (8, 10, 11)
                },
                "pair_recovery": {
                    "replaced_cell": "T2-08-of-11-sub-3-of-4",
                    "cells": [
                        {
                            "cell_id": cell.cell_id,
                            "query": cell.query,
                            "characters": len(cell.query),
                            "t2_alternative_count": len(cell.alternatives),
                        }
                        for cell in bt2_subcells(8, alternatives_per_cell=1)[10:15]
                    ],
                },
            },
        },
        "wildcard": {
            "used": False,
            "accepted": False,
            "reason": "No wildcard was submitted; each literal and declared pair remains explicit.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
