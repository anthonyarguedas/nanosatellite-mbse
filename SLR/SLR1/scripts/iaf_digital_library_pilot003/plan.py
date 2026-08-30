#!/usr/bin/env python3
"""Build and validate Pilot 003's lossless IAF query-cell plan.

The normative literals, declared pairs, and semantic partitions live in the
shared ``pilot_schedule`` module.  This module only packs its IAF renderer's
already-expanded alternatives into source-safe cells; it never changes a
concept or executes a search.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pilot_schedule.queries import (  # noqa: E402
    CONCEPTS,
    MAIN_FACTORS,
    RENDERERS,
    partition_cells,
    partition_query,
)


PILOT_NUMBER = "003"
SOURCE_ID = "iaf_digital_library"
SOURCE_LABEL = "IAF Digital Library"
MAX_QUERY_CHARACTERS = 500
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
REVIEW_ID = "slr1-pilot-003"
STRATEGY_REFERENCE = "slr1-direct-query-schedule-v1"
STRATEGY_VERSION = "276ca87"
PLAN_SCHEMA_VERSION = "academic-search-event-schedule/v1"
PACKING_SCHEMA_VERSION = "iaf-digital-library-lossless-cell-packing/v1"

PILOT_DIR = (
    Path(__file__).resolve().parents[2]
    / "source-specific"
    / "iaf-digital-library"
    / "pilots"
    / PILOT_NUMBER
)
DEFAULT_PLAN_PATH = PILOT_DIR / "searches" / "cell-plan.json"

BOOLEAN_FORMS = {
    "A1": "P AND E_H AND M_H",
    "A2": "P AND E_F AND (M_H OR M_B)",
    "A3": "P AND E_H AND M_B",
    "B1": "P AND M_H",
    "B2": "P AND M_B AND R",
    "BG1": "P AND G_model",
    "BG2": "P AND G_structure",
    "BC1": "P AND C1",
    "BT2": "P AND M_B AND T2",
}


class PlanError(ValueError):
    """Raised when a cell plan is not a lossless IAF translation."""


@dataclass(frozen=True)
class Alternative:
    """One ordered source-rendered literal or declared-pair alternative."""

    ordinal: int
    text: str


Group = tuple[Alternative, ...]
CellGroups = tuple[Group, ...]


@dataclass(frozen=True)
class Factor:
    concept_names: tuple[str, ...]
    alternatives: tuple[Alternative, ...]


def renderer():
    return RENDERERS[SOURCE_ID]


def _group_texts(group: Group) -> tuple[str, ...]:
    return tuple(item.text for item in group)


@lru_cache(maxsize=None)
def _union_length(texts: tuple[str, ...]) -> int:
    return len(renderer().union(texts))


def union_length(group: Group) -> int:
    if not group:
        raise PlanError("a query factor group cannot be empty")
    return _union_length(_group_texts(group))


def render_groups(groups: CellGroups) -> str:
    if not groups:
        raise PlanError("a query cell cannot be empty")
    query = renderer().and_token.join(
        renderer().union(_group_texts(group)) for group in groups
    )
    if len(query) > MAX_QUERY_CHARACTERS:
        raise PlanError(f"IAF query cell exceeds {MAX_QUERY_CHARACTERS} characters")
    return query


def make_factors(partition_id: str) -> tuple[Factor, ...]:
    try:
        named_factors = MAIN_FACTORS[partition_id]
    except KeyError as error:
        raise PlanError(f"unknown main partition {partition_id}") from error
    output: list[Factor] = []
    for concept_names in named_factors:
        rendered = renderer().alternatives(concept_names)
        output.append(
            Factor(
                tuple(concept_names),
                tuple(
                    Alternative(ordinal=index, text=text)
                    for index, text in enumerate(rendered, start=1)
                ),
            )
        )
    return tuple(output)


def group_range(group: Group) -> dict[str, int]:
    if not group:
        raise PlanError("cannot serialize an empty group")
    expected = tuple(range(group[0].ordinal, group[-1].ordinal + 1))
    observed = tuple(item.ordinal for item in group)
    if observed != expected:
        raise PlanError("lossless packer emitted a non-contiguous factor group")
    return {"start": group[0].ordinal, "end": group[-1].ordinal}


def chunks_for_max_union_length(
    alternatives: tuple[Alternative, ...], maximum: int
) -> tuple[Group, ...] | None:
    """Greedily make the fewest ordered contiguous groups under ``maximum``.

    For positive-length alternatives and a fixed order, filling each group to
    the source cap before starting the next is optimal for the number of
    contiguous groups.  Keeping source order makes every cell auditable by an
    ordinal range rather than a copied concept list.
    """

    chunks: list[Group] = []
    current: list[Alternative] = []
    for alternative in alternatives:
        candidate = tuple((*current, alternative))
        if union_length(candidate) <= maximum:
            current.append(alternative)
            continue
        if not current:
            return None
        chunks.append(tuple(current))
        current = [alternative]
    if current:
        chunks.append(tuple(current))
    return tuple(chunks)


def _plan_two_factors(
    first: Factor,
    second: Factor,
    *,
    fixed_union_length: int = 0,
    fixed_factor_count: int = 0,
) -> tuple[CellGroups, ...] | None:
    """Losslessly tile two factors, optionally below already-fixed factors.

    One factor is split into contiguous groups.  For each such group the other
    factor is greedily repacked with the capacity actually left by that group.
    Dynamic programming chooses the outer grouping with the fewest cells.
    This improves safely on a single equal budget for every factor while every
    output remains a distributive Cartesian rectangle.
    """

    if fixed_factor_count < 0:
        raise PlanError("fixed factor count cannot be negative")
    spaces = fixed_factor_count + 1

    def orient(
        outer: Factor, inner: Factor, *, reversed_output: bool
    ) -> tuple[CellGroups, ...] | None:
        states: list[tuple[int, tuple[tuple[Group, tuple[Group, ...]], ...]] | None]
        states = [None] * (len(outer.alternatives) + 1)
        states[-1] = (0, ())
        for start in range(len(outer.alternatives) - 1, -1, -1):
            best: tuple[int, tuple[tuple[Group, tuple[Group, ...]], ...]] | None = None
            best_key: tuple[int, int] | None = None
            for end in range(start + 1, len(outer.alternatives) + 1):
                outer_group = outer.alternatives[start:end]
                maximum_inner = (
                    MAX_QUERY_CHARACTERS
                    - fixed_union_length
                    - union_length(outer_group)
                    - spaces
                )
                inner_chunks = chunks_for_max_union_length(
                    inner.alternatives, maximum_inner
                )
                suffix = states[end]
                if inner_chunks is None or suffix is None:
                    continue
                candidate = (
                    len(inner_chunks) + suffix[0],
                    ((outer_group, inner_chunks), *suffix[1]),
                )
                candidate_key = (candidate[0], end)
                if best is None or candidate_key < best_key:  # type: ignore[operator]
                    best = candidate
                    best_key = candidate_key
            states[start] = best
        selected = states[0]
        if selected is None:
            return None
        cells: list[CellGroups] = []
        for outer_group, inner_chunks in selected[1]:
            for inner_group in inner_chunks:
                cells.append(
                    (inner_group, outer_group)
                    if reversed_output
                    else (outer_group, inner_group)
                )
        return tuple(cells)

    candidates = [
        (index, value)
        for index, value in enumerate(
            (
                orient(first, second, reversed_output=False),
                orient(second, first, reversed_output=True),
            )
        )
        if value is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: (len(item[1]), item[0]))[1]


def _plan_three_factors(factors: tuple[Factor, Factor, Factor]) -> tuple[CellGroups, ...]:
    """Losslessly tile three factors with a deterministic nested partition."""

    candidates: list[tuple[CellGroups, int]] = []
    for outer_index in range(3):
        outer = factors[outer_index]
        remaining_indices = tuple(index for index in range(3) if index != outer_index)
        first = factors[remaining_indices[0]]
        second = factors[remaining_indices[1]]
        inner_cache: dict[int, tuple[CellGroups, ...] | None] = {}

        def inner_plan(outer_group: Group) -> tuple[CellGroups, ...] | None:
            length = union_length(outer_group)
            if length not in inner_cache:
                inner_cache[length] = _plan_two_factors(
                    first,
                    second,
                    fixed_union_length=length,
                    fixed_factor_count=1,
                )
            return inner_cache[length]

        states: list[tuple[int, tuple[tuple[Group, tuple[CellGroups, ...]], ...]] | None]
        states = [None] * (len(outer.alternatives) + 1)
        states[-1] = (0, ())
        for start in range(len(outer.alternatives) - 1, -1, -1):
            best: tuple[int, tuple[tuple[Group, tuple[CellGroups, ...]], ...]] | None = None
            best_key: tuple[int, int] | None = None
            for end in range(start + 1, len(outer.alternatives) + 1):
                outer_group = outer.alternatives[start:end]
                nested = inner_plan(outer_group)
                suffix = states[end]
                if nested is None or suffix is None:
                    continue
                candidate = (
                    len(nested) + suffix[0],
                    ((outer_group, nested), *suffix[1]),
                )
                candidate_key = (candidate[0], end)
                if best is None or candidate_key < best_key:  # type: ignore[operator]
                    best = candidate
                    best_key = candidate_key
            states[start] = best
        selected = states[0]
        if selected is None:
            continue
        cells: list[CellGroups] = []
        for outer_group, nested_cells in selected[1]:
            for nested in nested_cells:
                if len(nested) != 2:
                    raise PlanError("nested two-factor plan has the wrong arity")
                groups: list[Group | None] = [None, None, None]
                groups[outer_index] = outer_group
                groups[remaining_indices[0]] = nested[0]
                groups[remaining_indices[1]] = nested[1]
                if any(group is None for group in groups):
                    raise PlanError("nested factor plan omitted a group")
                cells.append(tuple(groups))  # type: ignore[arg-type]
        candidates.append((tuple(cells), outer_index))
    if not candidates:
        raise PlanError("no source-safe three-factor packing exists")
    return min(candidates, key=lambda item: (len(item[0]), item[1]))[0]


def pack_partition(partition_id: str) -> tuple[tuple[Factor, ...], tuple[CellGroups, ...]]:
    factors = make_factors(partition_id)
    if len(factors) == 2:
        cells = _plan_two_factors(factors[0], factors[1])
        if cells is None:
            raise PlanError(f"no source-safe two-factor packing exists for {partition_id}")
    elif len(factors) == 3:
        cells = _plan_three_factors((factors[0], factors[1], factors[2]))
    else:  # The direct protocol schedule has only two- and three-factor entries.
        raise PlanError(f"unsupported factor count for {partition_id}: {len(factors)}")
    for cell in cells:
        if len(cell) != len(factors):
            raise PlanError(f"{partition_id} cell has wrong factor arity")
        render_groups(cell)
    return factors, cells


def _coordinate_digest(coordinates: Iterable[tuple[int, ...]]) -> str:
    digest = hashlib.sha256()
    for coordinate in sorted(coordinates):
        digest.update("/".join(str(value) for value in coordinate).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def coverage_certificate(
    factors: Sequence[Factor], cells: Sequence[CellGroups]
) -> dict[str, Any]:
    """Prove every alternative tuple is covered once by the packed rectangles."""

    expected_count = 1
    for factor in factors:
        expected_count *= len(factor.alternatives)
    covered: set[tuple[int, ...]] = set()
    overlap_count = 0
    rectangle_volume = 0
    for cell in cells:
        ranges = [
            range(group[0].ordinal, group[-1].ordinal + 1)
            for group in cell
        ]
        for coordinate in itertools.product(*ranges):
            rectangle_volume += 1
            if coordinate in covered:
                overlap_count += 1
            covered.add(coordinate)
    expected_coordinates = itertools.product(
        *(range(1, len(factor.alternatives) + 1) for factor in factors)
    )
    exact = (
        overlap_count == 0
        and rectangle_volume == expected_count
        and len(covered) == expected_count
    )
    return {
        "method": "enumerated_distributive_alternative_tuples",
        "expected_cartesian_combinations": expected_count,
        "rectangle_combination_volume": rectangle_volume,
        "covered_combinations": len(covered),
        "overlap_combinations": overlap_count,
        "gap_combinations": expected_count - len(covered),
        "exactly_once": exact,
        "covered_coordinate_sha256": _coordinate_digest(covered),
        "expected_coordinate_sha256": _coordinate_digest(expected_coordinates),
    }


def _concept_audit() -> dict[str, dict[str, int]]:
    return {
        name: {
            "literals": len(concept.literals),
            "declared_pairs": len(concept.pairs),
            "alternatives": concept.alternative_count,
        }
        for name, concept in CONCEPTS.items()
    }


def _cell_payload(
    index: int, factors: Sequence[Factor], groups: CellGroups
) -> dict[str, Any]:
    query = render_groups(groups)
    return {
        "cell_id": f"cell-{index:04d}",
        "query": query,
        "query_characters": len(query),
        "factor_ranges": [
            {
                "factor_index": factor_index,
                "concepts": list(factor.concept_names),
                "alternative_range": group_range(group),
            }
            for factor_index, (factor, group) in enumerate(zip(factors, groups), start=1)
        ],
    }


def build_plan_payload() -> dict[str, Any]:
    entries: dict[str, Any] = {}
    events: list[dict[str, Any]] = []
    baseline_total = 0
    packed_total = 0
    for partition_id in MAIN_FACTORS:
        factors, groups = pack_partition(partition_id)
        cells = [
            _cell_payload(index, factors, group)
            for index, group in enumerate(groups, start=1)
        ]
        baseline = partition_cells(
            SOURCE_ID,
            partition_id,
            maximum_characters=MAX_QUERY_CHARACTERS,
        )
        certificate = coverage_certificate(factors, groups)
        if not certificate["exactly_once"]:
            raise PlanError(f"{partition_id} packing does not cover alternatives exactly once")
        if certificate["covered_coordinate_sha256"] != certificate["expected_coordinate_sha256"]:
            raise PlanError(f"{partition_id} coordinate coverage digest does not reconcile")
        if any("*" in cell["query"] or "?" in cell["query"] for cell in cells):
            raise PlanError(f"{partition_id} inserted an unaccepted wildcard")
        if any(cell["query_characters"] > MAX_QUERY_CHARACTERS for cell in cells):
            raise PlanError(f"{partition_id} contains an over-cap cell")
        baseline_total += len(baseline)
        packed_total += len(cells)
        entries[partition_id] = {
            "boolean_form": BOOLEAN_FORMS[partition_id],
            "factor_concepts": [list(factor.concept_names) for factor in factors],
            "factor_alternative_counts": [
                len(factor.alternatives) for factor in factors
            ],
            "unsubmitted_full_query": partition_query(SOURCE_ID, partition_id),
            "unsubmitted_full_query_characters": len(
                partition_query(SOURCE_ID, partition_id)
            ),
            "shared_equal_budget_cell_count": len(baseline),
            "packed_cell_count": len(cells),
            "cell_character_range": {
                "minimum": min(cell["query_characters"] for cell in cells),
                "maximum": max(cell["query_characters"] for cell in cells),
            },
            "coverage_certificate": certificate,
            "cells": cells,
        }
        events.append(
            {
                "event_id": f"pilot-main-{partition_id}-{SOURCE_ID}-{PILOT_NUMBER}",
                "event_kind": "pilot",
                "pilot_mode": "strict",
                "review_namespace": "main",
                "source": SOURCE_ID,
                "partition_id": partition_id,
                "review_id": REVIEW_ID,
                "strategy_reference": STRATEGY_REFERENCE,
                "strategy_version": STRATEGY_VERSION,
                "phase": "identification",
                "query_mode": "structured",
                "query_cells": [
                    {"cell_id": cell["cell_id"], "query": cell["query"]}
                    for cell in cells
                ],
            }
        )
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "packing_schema_version": PACKING_SCHEMA_VERSION,
        "pilot": PILOT_NUMBER,
        "run_id": "pilot-main-iaf-digital-library-003",
        "source": {"id": SOURCE_ID, "label": SOURCE_LABEL},
        "requested_window": {
            "start_date": DATE_START,
            "cutoff_date": DATE_END,
            "inclusive": True,
            "mode": "diagnostic_only_local_post_filter",
        },
        "planned_sources": {"main": [SOURCE_ID]},
        "planned_partitions": {"main": list(MAIN_FACTORS)},
        "controls": {
            "database_scope": "full_iaf_digital_library",
            "date": "no source-side date clause; inclusive local post-filter after each complete raw traversal",
            "language": "not applied; language assignment completeness and missing-value behavior are unproved",
            "publication_type": "not applied; IAF Digital Library is conference-paper scoped",
            "access": "not applied",
            "wildcard": "not used or accepted; every planned query contains only exact declared literals and pair atoms",
            "controlled_vocabulary": "not applied; no validated IAF descriptor vocabulary",
        },
        "source_syntax": {
            "literal": "one straight double-quoted literal",
            "pair": "(quoted-left whitespace quoted-right) broader same-Any-keyword fallback",
            "and": "documented whitespace conjunction",
            "or": "documented uppercase OR",
            "maximum_query_characters": MAX_QUERY_CHARACTERS,
        },
        "concept_audit": _concept_audit(),
        "packing": {
            "method": "nested contiguous factor partition with dynamic programming and greedy inner packing",
            "lossless_basis": "Each cell is a conjunction of OR groups. Outer factor groups partition their ordered alternatives; the remaining groups are independently partitioned inside each outer group, so the cell union is an exactly-once distributive Cartesian cover.",
            "shared_equal_budget_baseline_cells": baseline_total,
            "packed_cells": packed_total,
            "cell_reduction": baseline_total - packed_total,
            "wildcards_inserted": False,
        },
        "partitions": entries,
        "events": events,
    }


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _lookup_group(factor: Factor, range_payload: Mapping[str, Any]) -> Group:
    raw = range_payload.get("alternative_range")
    if not isinstance(raw, Mapping):
        raise PlanError("factor range has no alternative_range object")
    start = raw.get("start")
    end = raw.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or start < 1
        or end < start
        or end > len(factor.alternatives)
    ):
        raise PlanError("factor range has invalid alternative bounds")
    return factor.alternatives[start - 1 : end]


def validate_plan_payload(payload: Mapping[str, Any]) -> list[str]:
    """Return all deterministic plan-integrity errors without running a search."""

    errors: list[str] = []
    _require(payload.get("schema_version") == PLAN_SCHEMA_VERSION, "wrong plan schema", errors)
    _require(payload.get("packing_schema_version") == PACKING_SCHEMA_VERSION, "wrong packing schema", errors)
    _require(payload.get("pilot") == PILOT_NUMBER, "wrong pilot number", errors)
    _require(payload.get("planned_partitions", {}).get("main") == list(MAIN_FACTORS), "main partition schedule changed", errors)
    _require(payload.get("planned_sources", {}).get("main") == [SOURCE_ID], "source plan changed", errors)
    _require(payload.get("controls", {}).get("language", "").startswith("not applied"), "language restriction was accepted", errors)
    _require(payload.get("controls", {}).get("publication_type", "").startswith("not applied"), "type restriction was accepted", errors)
    _require(payload.get("controls", {}).get("access") == "not applied", "access restriction was accepted", errors)
    partitions = payload.get("partitions")
    if not isinstance(partitions, Mapping):
        return [*errors, "partitions is not an object"]
    _require(tuple(partitions) == tuple(MAIN_FACTORS), "partition order or membership changed", errors)
    total_cells = 0
    expected_baseline = 0
    for partition_id in MAIN_FACTORS:
        entry = partitions.get(partition_id)
        if not isinstance(entry, Mapping):
            errors.append(f"{partition_id}: missing partition entry")
            continue
        try:
            factors = make_factors(partition_id)
        except PlanError as error:
            errors.append(f"{partition_id}: {error}")
            continue
        _require(entry.get("boolean_form") == BOOLEAN_FORMS[partition_id], f"{partition_id}: Boolean form changed", errors)
        _require(entry.get("factor_concepts") == [list(factor.concept_names) for factor in factors], f"{partition_id}: factor concepts changed", errors)
        _require(entry.get("factor_alternative_counts") == [len(factor.alternatives) for factor in factors], f"{partition_id}: factor alternative counts changed", errors)
        _require(entry.get("unsubmitted_full_query") == partition_query(SOURCE_ID, partition_id), f"{partition_id}: full source translation changed", errors)
        cells = entry.get("cells")
        if not isinstance(cells, list) or not cells:
            errors.append(f"{partition_id}: no cells")
            continue
        parsed_groups: list[CellGroups] = []
        seen_ids: set[str] = set()
        for index, cell in enumerate(cells, start=1):
            if not isinstance(cell, Mapping):
                errors.append(f"{partition_id}: cell {index} is not an object")
                continue
            expected_id = f"cell-{index:04d}"
            cell_id = cell.get("cell_id")
            _require(cell_id == expected_id, f"{partition_id}: cell ID {cell_id!r} is not {expected_id}", errors)
            if isinstance(cell_id, str):
                _require(cell_id not in seen_ids, f"{partition_id}: duplicate cell ID {cell_id}", errors)
                seen_ids.add(cell_id)
            ranges = cell.get("factor_ranges")
            if not isinstance(ranges, list) or len(ranges) != len(factors):
                errors.append(f"{partition_id}: {expected_id} has wrong factor ranges")
                continue
            groups: list[Group] = []
            for factor_index, (factor, range_payload) in enumerate(zip(factors, ranges), start=1):
                if not isinstance(range_payload, Mapping):
                    errors.append(f"{partition_id}: {expected_id} factor {factor_index} is malformed")
                    continue
                _require(range_payload.get("factor_index") == factor_index, f"{partition_id}: {expected_id} factor index changed", errors)
                _require(range_payload.get("concepts") == list(factor.concept_names), f"{partition_id}: {expected_id} factor concepts changed", errors)
                try:
                    groups.append(_lookup_group(factor, range_payload))
                except PlanError as error:
                    errors.append(f"{partition_id}: {expected_id} factor {factor_index}: {error}")
            if len(groups) != len(factors):
                continue
            query = render_groups(tuple(groups))
            _require(cell.get("query") == query, f"{partition_id}: {expected_id} query changed", errors)
            _require(cell.get("query_characters") == len(query), f"{partition_id}: {expected_id} character count changed", errors)
            _require(len(query) <= MAX_QUERY_CHARACTERS, f"{partition_id}: {expected_id} exceeds source cap", errors)
            _require("*" not in query and "?" not in query, f"{partition_id}: {expected_id} contains wildcard syntax", errors)
            for forbidden in ("language:", "event:", "year:"):
                _require(forbidden not in query, f"{partition_id}: {expected_id} added {forbidden} restriction", errors)
            parsed_groups.append(tuple(groups))
        certificate = coverage_certificate(factors, parsed_groups)
        _require(certificate["exactly_once"] is True, f"{partition_id}: coverage is not exactly once", errors)
        _require(certificate["covered_coordinate_sha256"] == certificate["expected_coordinate_sha256"], f"{partition_id}: coverage digest differs", errors)
        _require(entry.get("coverage_certificate") == certificate, f"{partition_id}: stored coverage certificate changed", errors)
        _require(entry.get("packed_cell_count") == len(cells), f"{partition_id}: stored packed count changed", errors)
        baseline = len(partition_cells(SOURCE_ID, partition_id, maximum_characters=MAX_QUERY_CHARACTERS))
        _require(entry.get("shared_equal_budget_cell_count") == baseline, f"{partition_id}: shared baseline count changed", errors)
        total_cells += len(cells)
        expected_baseline += baseline
    packing = payload.get("packing", {})
    if not isinstance(packing, Mapping):
        errors.append("packing is not an object")
    else:
        _require(packing.get("shared_equal_budget_baseline_cells") == expected_baseline, "shared baseline total changed", errors)
        _require(packing.get("packed_cells") == total_cells, "packed total changed", errors)
        _require(packing.get("cell_reduction") == expected_baseline - total_cells, "cell reduction changed", errors)
        _require(packing.get("wildcards_inserted") is False, "wildcard insertion state changed", errors)
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != len(MAIN_FACTORS):
        errors.append("event schedule is incomplete")
    else:
        for partition_id, event in zip(MAIN_FACTORS, events):
            entry = partitions.get(partition_id)
            expected_cells = entry.get("cells") if isinstance(entry, Mapping) else []
            _require(event.get("event_kind") == "pilot", f"{partition_id}: event is not a pilot", errors)
            _require(event.get("pilot_mode") == "strict", f"{partition_id}: pilot is not complete-mode", errors)
            _require(event.get("partition_id") == partition_id, f"{partition_id}: event partition changed", errors)
            _require(event.get("source") == SOURCE_ID, f"{partition_id}: event source changed", errors)
            _require(event.get("query_cells") == [{"cell_id": item["cell_id"], "query": item["query"]} for item in expected_cells], f"{partition_id}: event cells differ from packing cells", errors)
    return errors


def write_json_no_clobber(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise PlanError(f"refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--check", action="store_true", help="validate an existing plan instead of building it")
    args = parser.parse_args(argv)
    path = args.output_path.expanduser()
    if args.check:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"FAILED\n- could not load plan: {error}")
            return 1
        errors = validate_plan_payload(payload)
        if errors:
            print("FAILED")
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print(json.dumps({"status": "ok", "plan": str(path), "packed_cells": payload["packing"]["packed_cells"]}, indent=2))
        return 0
    payload = build_plan_payload()
    errors = validate_plan_payload(payload)
    if errors:
        raise PlanError("generated plan failed validation: " + "; ".join(errors))
    write_json_no_clobber(path, payload)
    print(
        json.dumps(
            {
                "saved": str(path),
                "partitions": list(MAIN_FACTORS),
                "shared_equal_budget_cells": payload["packing"]["shared_equal_budget_baseline_cells"],
                "packed_cells": payload["packing"]["packed_cells"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
