"""Scopus Pilot 003 query and membership helpers.

This module imports the review-wide pilot schedule rather than maintaining a
second term list.  It renders only the literal Scopus expressions accepted by
the source guideline: TITLE-ABS-KEY atoms and W/6 pair fallbacks.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import sys
from typing import Any


_SCHEDULE_PATH = Path(__file__).resolve().parents[1] / "pilot_schedule" / "queries.py"
_spec = spec_from_file_location("slr1_pilot_schedule_queries", _SCHEDULE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover - installation fault
    raise RuntimeError(f"Could not load {_SCHEDULE_PATH}")
_schedule = module_from_spec(_spec)
sys.modules[_spec.name] = _schedule
_spec.loader.exec_module(_schedule)

MAIN_PARTITIONS = tuple(_schedule.MAIN_FACTORS)
PSR_PARTITIONS = tuple(_schedule.PSR_FACTORS)
ALL_PARTITIONS = (*MAIN_PARTITIONS, *PSR_PARTITIONS)
SCOPUS_RENDERER = _schedule.RENDERERS["scopus"]

# These counts are the protocol declarations tested by pilot_schedule itself.
EXPECTED_MEMBERSHIP = {
    "P": (26, 0),
    "E_H": (38, 0),
    "E_F": (37, 0),
    "M_H": (54, 0),
    "M_B": (31, 0),
    "R": (55, 0),
    "G_model": (14, 16),
    "G_structure": (8, 16),
    "C1": (26, 36),
    "T2": (0, 224),
    "X": (39, 0),
    "Q": (16, 0),
}


def full_query(partition_id: str) -> str:
    """Return the complete, literal source expression for one partition."""
    if partition_id not in ALL_PARTITIONS:
        raise ValueError(f"Unknown Pilot 003 partition: {partition_id}")
    return _schedule.partition_query("scopus", partition_id)


def membership_audit() -> dict[str, Any]:
    """Return deterministic proof that imported concept membership is intact."""
    observed = {
        name: (len(concept.literals), len(concept.pairs))
        for name, concept in _schedule.CONCEPTS.items()
    }
    if observed != EXPECTED_MEMBERSHIP:
        raise AssertionError(f"Concept membership changed: {observed!r}")
    queries = {partition: full_query(partition) for partition in ALL_PARTITIONS}
    if any("*" in query or "?" in query for query in queries.values()):
        raise AssertionError("An unaccepted wildcard entered a Pilot 003 query")
    if any("DOCTYPE" in query.upper() for query in queries.values()):
        raise AssertionError("A document-type restriction entered a Pilot 003 query")
    return {
        "concept_membership": {
            name: {"literals": literals, "pairs": pairs}
            for name, (literals, pairs) in observed.items()
        },
        "main_partitions": list(MAIN_PARTITIONS),
        "psr_partitions": list(PSR_PARTITIONS),
        "query_character_counts": {
            partition: len(query) for partition, query in queries.items()
        },
        "wildcards_present": False,
        "doctype_present": False,
    }


def _balanced_split(alternatives: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split one OR list into two nonempty contiguous, character-balanced lists."""
    if len(alternatives) < 2:
        raise ValueError("Cannot split a one-atom factor")
    candidates = []
    for index in range(1, len(alternatives)):
        left, right = alternatives[:index], alternatives[index:]
        candidates.append(
            (
                max(
                    len(SCOPUS_RENDERER.union(left)),
                    len(SCOPUS_RENDERER.union(right)),
                ),
                left,
                right,
            )
        )
    _, left, right = min(candidates, key=lambda item: item[0])
    return left, right


def lossless_cells(partition_id: str, maximum_characters: int) -> tuple[dict[str, str], ...]:
    """Prospectively split long OR factors without changing their Boolean form.

    Each factor remains an OR list and every resulting cell remains the original
    AND construction.  If more than one factor needs splitting, the Cartesian
    product is retained; overlaps are expected and must be reconciled by stable
    publication ID after collection.
    """
    if maximum_characters < 100:
        raise ValueError("maximum_characters is implausibly small")
    factors = _schedule.SCHEDULE_FACTORS[partition_id]
    groups: list[list[tuple[str, ...]]] = [
        [tuple(SCOPUS_RENDERER.alternatives(names))] for names in factors
    ]

    def worst_length() -> int:
        return sum(
            max(len(SCOPUS_RENDERER.union(chunk)) for chunk in factor_groups)
            for factor_groups in groups
        ) + len(SCOPUS_RENDERER.and_token) * (len(groups) - 1)

    # Split the largest current source factor first.  This avoids splitting
    # small population blocks merely because doing so initially adds fewer
    # Cartesian cells than splitting the actual long factor.
    while worst_length() > maximum_characters:
        candidates = [
            (
                max(
                    len(SCOPUS_RENDERER.union(chunk))
                    for chunk in factor_groups
                ),
                factor_index,
            )
            for factor_index, factor_groups in enumerate(groups)
            if any(len(chunk) > 1 for chunk in factor_groups)
        ]
        if not candidates:
            raise ValueError(
                f"{partition_id} cannot fit within {maximum_characters} characters"
            )
        _, factor_index = max(candidates)
        factor_groups = groups[factor_index]
        chunk_index = max(
            (
                index
                for index, chunk in enumerate(factor_groups)
                if len(chunk) > 1
            ),
            key=lambda index: len(SCOPUS_RENDERER.union(factor_groups[index])),
        )
        left, right = _balanced_split(factor_groups[chunk_index])
        groups[factor_index] = (
            factor_groups[:chunk_index] + [left, right] + factor_groups[chunk_index + 1 :]
        )

    cells = []
    for index, selected in enumerate(product(*groups), start=1):
        query = SCOPUS_RENDERER.and_token.join(
            SCOPUS_RENDERER.union(chunk) for chunk in selected
        )
        if len(query) > maximum_characters:
            raise AssertionError("Cell planner exceeded its declared limit")
        cells.append({"cell_id": f"cell-{index:02d}", "query": query})
    validate_lossless_cells(partition_id, cells)
    return tuple(cells)


def validate_lossless_cells(partition_id: str, cells: tuple[dict[str, str], ...] | list[dict[str, str]]) -> None:
    """Check that cells use only schedule atoms and cover each factor exactly."""
    if not cells:
        raise AssertionError("A lossless cell plan must contain at least one cell")
    full = full_query(partition_id)
    factor_count = len(_schedule.SCHEDULE_FACTORS[partition_id])
    expected_atoms = [
        tuple(SCOPUS_RENDERER.alternatives(names))
        for names in _schedule.SCHEDULE_FACTORS[partition_id]
    ]
    observed_by_factor: list[set[str]] = [set() for _ in range(factor_count)]
    for cell in cells:
        query = cell.get("query")
        if not isinstance(query, str) or not query:
            raise AssertionError("Cell has no query")
        # An atom may occur in more than one cell because cells cross product
        # independently split factors.  It must never be absent or foreign.
        for factor_index, atoms in enumerate(expected_atoms):
            hits = [atom for atom in atoms if atom in query]
            if not hits:
                raise AssertionError(f"Cell lacks factor {factor_index} in {partition_id}")
            observed_by_factor[factor_index].update(hits)
        if "*" in query or "?" in query or "DOCTYPE" in query.upper():
            raise AssertionError("Cell changed the accepted literal source translation")
    for expected, observed in zip(expected_atoms, observed_by_factor, strict=True):
        if set(expected) != observed:
            raise AssertionError("Cells do not cover a schedule factor exactly")
    if not full:
        raise AssertionError("Missing full expression")
