#!/usr/bin/env python3
"""Build and validate the lossless IAF Pilot 004 cell plan."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from queries import (
    CHANGED_IDS,
    PARTITION_BRANCHES,
    PROTOCOL_COMMIT,
    SCHEDULE,
    SCHEDULE_IDS,
    TERM_COUNTS,
    TERM_SETS,
    atom,
)

PILOT_NUMBER = "004"
SOURCE_ID = "iaf_digital_library"
SOURCE_LABEL = "IAF Digital Library"
MAX_QUERY_CHARACTERS = 500
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
REVIEW_ID = "slr1-iaf-pilot-004"
STRATEGY_REFERENCE = "slr1-direct-query-schedule-post-proximity-v1"
STRATEGY_VERSION = PROTOCOL_COMMIT
PLAN_SCHEMA_VERSION = "iaf-digital-library-pilot004-cell-plan/v1"
PACKING_SCHEMA_VERSION = "iaf-digital-library-lossless-branch-cell-packing/v1"

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_DIR = (
    SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / PILOT_NUMBER
)
DEFAULT_PLAN_PATH = PILOT_DIR / "searches" / "cell-plan.json"
PILOT003_ROOT = SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / "003"
PILOT003_PLAN = PILOT003_ROOT / "searches" / "cell-plan.json"
PILOT003_ASSESSMENT = PILOT003_ROOT / "searches" / "assessment.json"
UNCHANGED_IDS = tuple(value for value in SCHEDULE_IDS if value not in CHANGED_IDS)

BOOLEAN_FORMS = {
    "A1": "P AND E_H AND M_H",
    "A2": "P AND E_F AND (M_H OR M_B)",
    "A3": "P AND E_H AND M_B",
    "B1": "P AND M_H",
    "B2": "P AND M_B AND R",
    "BG1": "P AND (G_model_fixed OR G_mission_exact OR (G_mission AND M_B))",
    "BG2": "P AND (G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B))",
    "BC1": "P AND (C1_fixed OR G_DSL)",
    "BT2": "P AND M_B AND T_precise",
}


class PlanError(ValueError):
    """Raised when a plan is not a lossless source translation."""


@dataclass(frozen=True)
class Alternative:
    ordinal: int
    text: str


@dataclass(frozen=True)
class Factor:
    name: str
    alternatives: tuple[Alternative, ...]


Group = tuple[Alternative, ...]
CellGroups = tuple[Group, ...]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def factor_for(name: str) -> Factor:
    try:
        terms = TERM_SETS[name]
    except KeyError as error:
        raise PlanError(f"Unknown factor {name}") from error
    return Factor(
        name=name,
        alternatives=tuple(
            Alternative(ordinal=index, text=atom(term))
            for index, term in enumerate(terms, start=1)
        ),
    )


@cache
def union_from_texts(texts: tuple[str, ...]) -> str:
    if not texts:
        raise PlanError("A source OR group cannot be empty")
    return "(" + " OR ".join(texts) + ")"


def render_union(group: Group) -> str:
    return union_from_texts(tuple(item.text for item in group))


def union_length(group: Group) -> int:
    return len(render_union(group))


def render_groups(groups: CellGroups) -> str:
    if not groups:
        raise PlanError("A source cell cannot be empty")
    query = " ".join(render_union(group) for group in groups)
    if len(query) > MAX_QUERY_CHARACTERS:
        raise PlanError(f"IAF query exceeds {MAX_QUERY_CHARACTERS} characters")
    return query


def chunks_for_maximum(
    alternatives: tuple[Alternative, ...], maximum: int
) -> tuple[Group, ...] | None:
    chunks: list[Group] = []
    current: list[Alternative] = []
    for alternative in alternatives:
        candidate = (*current, alternative)
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


def plan_two_factors(
    first: Factor,
    second: Factor,
    *,
    fixed_union_length: int = 0,
    fixed_factor_count: int = 0,
) -> tuple[CellGroups, ...] | None:
    spaces = fixed_factor_count + 1

    def orient(
        outer: Factor, inner: Factor, *, reverse_output: bool
    ) -> tuple[CellGroups, ...] | None:
        states: list[tuple[int, tuple[tuple[Group, tuple[Group, ...]], ...]] | None]
        states = [None] * (len(outer.alternatives) + 1)
        states[-1] = (0, ())
        for start in range(len(outer.alternatives) - 1, -1, -1):
            best = None
            best_key = None
            for end in range(start + 1, len(outer.alternatives) + 1):
                outer_group = outer.alternatives[start:end]
                maximum_inner = (
                    MAX_QUERY_CHARACTERS
                    - fixed_union_length
                    - union_length(outer_group)
                    - spaces
                )
                inner_chunks = chunks_for_maximum(inner.alternatives, maximum_inner)
                suffix = states[end]
                if inner_chunks is None or suffix is None:
                    continue
                candidate = (
                    len(inner_chunks) + suffix[0],
                    ((outer_group, inner_chunks), *suffix[1]),
                )
                candidate_key = (candidate[0], end)
                if best is None or candidate_key < best_key:
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
                    if reverse_output
                    else (outer_group, inner_group)
                )
        return tuple(cells)

    candidates = [
        candidate
        for candidate in (
            orient(first, second, reverse_output=False),
            orient(second, first, reverse_output=True),
        )
        if candidate is not None
    ]
    return min(candidates, key=len) if candidates else None


def plan_three_factors(
    factors: tuple[Factor, Factor, Factor],
) -> tuple[CellGroups, ...]:
    candidates: list[tuple[tuple[CellGroups, ...], int]] = []
    for outer_index in range(3):
        outer = factors[outer_index]
        inner_indices = tuple(index for index in range(3) if index != outer_index)
        first = factors[inner_indices[0]]
        second = factors[inner_indices[1]]
        inner_cache: dict[int, tuple[CellGroups, ...] | None] = {}

        def inner_plan(
            outer_group: Group,
            cache_for_length: dict[int, tuple[CellGroups, ...] | None] = inner_cache,
            first_factor: Factor = first,
            second_factor: Factor = second,
        ) -> tuple[CellGroups, ...] | None:
            length = union_length(outer_group)
            if length not in cache_for_length:
                cache_for_length[length] = plan_two_factors(
                    first_factor,
                    second_factor,
                    fixed_union_length=length,
                    fixed_factor_count=1,
                )
            return cache_for_length[length]

        states: list[
            tuple[int, tuple[tuple[Group, tuple[CellGroups, ...]], ...]] | None
        ]
        states = [None] * (len(outer.alternatives) + 1)
        states[-1] = (0, ())
        for start in range(len(outer.alternatives) - 1, -1, -1):
            best = None
            best_key = None
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
                if best is None or candidate_key < best_key:
                    best = candidate
                    best_key = candidate_key
            states[start] = best
        selected = states[0]
        if selected is None:
            continue
        cells: list[CellGroups] = []
        for outer_group, nested_cells in selected[1]:
            for nested in nested_cells:
                groups: list[Group | None] = [None, None, None]
                groups[outer_index] = outer_group
                groups[inner_indices[0]] = nested[0]
                groups[inner_indices[1]] = nested[1]
                if any(group is None for group in groups):
                    raise PlanError("A nested plan omitted a factor")
                cells.append(tuple(groups))  # type: ignore[arg-type]
        candidates.append((tuple(cells), outer_index))
    if not candidates:
        raise PlanError("No source-safe three-factor packing exists")
    return min(candidates, key=lambda item: (len(item[0]), item[1]))[0]


def pack_factors(factors: tuple[Factor, ...]) -> tuple[CellGroups, ...]:
    if len(factors) == 2:
        cells = plan_two_factors(factors[0], factors[1])
        if cells is None:
            raise PlanError("No source-safe two-factor packing exists")
        return cells
    if len(factors) == 3:
        return plan_three_factors((factors[0], factors[1], factors[2]))
    raise PlanError(f"Unsupported factor count: {len(factors)}")


def coordinate_sha256(coordinates: Iterable[tuple[int, ...]]) -> str:
    digest = hashlib.sha256()
    for coordinate in sorted(coordinates):
        digest.update("/".join(str(value) for value in coordinate).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def coverage_certificate(
    factors: Sequence[Factor], cells: Sequence[CellGroups]
) -> dict[str, Any]:
    expected_count = 1
    for factor in factors:
        expected_count *= len(factor.alternatives)
    covered: set[tuple[int, ...]] = set()
    overlaps = 0
    rectangle_volume = 0
    for cell in cells:
        ranges = [range(group[0].ordinal, group[-1].ordinal + 1) for group in cell]
        for coordinate in itertools.product(*ranges):
            rectangle_volume += 1
            if coordinate in covered:
                overlaps += 1
            covered.add(coordinate)
    expected = itertools.product(
        *(range(1, len(factor.alternatives) + 1) for factor in factors)
    )
    expected_digest = coordinate_sha256(expected)
    observed_digest = coordinate_sha256(covered)
    return {
        "method": "enumerated_distributive_alternative_tuples",
        "expected_cartesian_combinations": expected_count,
        "rectangle_combination_volume": rectangle_volume,
        "covered_combinations": len(covered),
        "overlap_combinations": overlaps,
        "gap_combinations": expected_count - len(covered),
        "exactly_once": (
            overlaps == 0
            and rectangle_volume == expected_count
            and len(covered) == expected_count
            and observed_digest == expected_digest
        ),
        "covered_coordinate_sha256": observed_digest,
        "expected_coordinate_sha256": expected_digest,
    }


def group_range(group: Group) -> dict[str, int]:
    observed = tuple(item.ordinal for item in group)
    expected = tuple(range(group[0].ordinal, group[-1].ordinal + 1))
    if observed != expected:
        raise PlanError("The packer emitted a noncontiguous factor range")
    return {"start": group[0].ordinal, "end": group[-1].ordinal}


def build_partitions() -> dict[str, Any]:
    partitions: dict[str, Any] = {}
    for partition_id in SCHEDULE_IDS:
        branches = []
        partition_cells = []
        next_cell = 1
        for branch_id, factor_names in PARTITION_BRANCHES[partition_id]:
            factors = tuple(factor_for(name) for name in factor_names)
            groups = pack_factors(factors)
            certificate = coverage_certificate(factors, groups)
            if not certificate["exactly_once"]:
                raise PlanError(f"{partition_id}/{branch_id} coverage is incomplete")
            branch_cells = []
            for branch_cell_number, cell_groups in enumerate(groups, start=1):
                query = render_groups(cell_groups)
                cell = {
                    "cell_id": f"cell-{next_cell:04d}",
                    "branch_cell_id": f"{branch_id}-{branch_cell_number:04d}",
                    "branch_id": branch_id,
                    "query": query,
                    "query_characters": len(query),
                    "query_sha256": text_sha256(query),
                    "factor_ranges": [
                        {
                            "factor_index": factor_index,
                            "factor": factor.name,
                            "alternative_range": group_range(group),
                        }
                        for factor_index, (factor, group) in enumerate(
                            zip(factors, cell_groups), start=1
                        )
                    ],
                }
                branch_cells.append(cell)
                partition_cells.append(cell)
                next_cell += 1
            branches.append(
                {
                    "branch_id": branch_id,
                    "factor_names": list(factor_names),
                    "factor_alternative_counts": [
                        len(factor.alternatives) for factor in factors
                    ],
                    "unsubmitted_branch_query": " ".join(
                        render_union(tuple(factor.alternatives)) for factor in factors
                    ),
                    "packed_cell_count": len(branch_cells),
                    "cell_character_range": {
                        "minimum": min(
                            cell["query_characters"] for cell in branch_cells
                        ),
                        "maximum": max(
                            cell["query_characters"] for cell in branch_cells
                        ),
                    },
                    "coverage_certificate": certificate,
                    "cells": branch_cells,
                }
            )
        partitions[partition_id] = {
            "boolean_form": BOOLEAN_FORMS[partition_id],
            "semantic_expression": SCHEDULE[partition_id],
            "branch_count": len(branches),
            "packed_cell_count": len(partition_cells),
            "branches": branches,
            "cells": partition_cells,
        }
    return partitions


def carry_forward_evidence(partitions: Mapping[str, Any]) -> dict[str, Any]:
    old_plan = json.loads(PILOT003_PLAN.read_text(encoding="utf-8"))
    old_assessment = json.loads(PILOT003_ASSESSMENT.read_text(encoding="utf-8"))
    entries = {}
    for partition_id in UNCHANGED_IDS:
        old_queries = [
            cell["query"] for cell in old_plan["partitions"][partition_id]["cells"]
        ]
        current_queries = [cell["query"] for cell in partitions[partition_id]["cells"]]
        old_entry = old_assessment["entries"][partition_id]
        identical = old_queries == current_queries
        if not identical:
            raise PlanError(
                f"{partition_id} no longer matches the strict Pilot 003 cell schedule"
            )
        entries[partition_id] = {
            "query_cells_identical": True,
            "cell_count": len(current_queries),
            "pilot003_status": old_entry.get("status"),
            "pilot003_raw_paper_id_union": old_entry.get("raw_paper_id_union", {}).get(
                "deduplicated_count"
            ),
            "pilot003_diagnostic_window_union": old_entry.get(
                "diagnostic_window_paper_id_union", {}
            ).get("deduplicated_count"),
        }
    return {
        "basis": (
            "Commit 3194156 changed only BG1, BG2, BC1, and BT2. The five "
            "unchanged partitions reproduce every strict Pilot 003 source cell byte for byte."
        ),
        "pilot003_plan": str(PILOT003_PLAN.relative_to(SLR1_DIR)),
        "pilot003_plan_sha256": file_sha256(PILOT003_PLAN),
        "pilot003_assessment": str(PILOT003_ASSESSMENT.relative_to(SLR1_DIR)),
        "pilot003_assessment_sha256": file_sha256(PILOT003_ASSESSMENT),
        "entries": entries,
        "all_query_cells_identical": all(
            entry["query_cells_identical"] for entry in entries.values()
        ),
    }


def build_plan_payload() -> dict[str, Any]:
    partitions = build_partitions()
    carry_forward = carry_forward_evidence(partitions)
    events = []
    for partition_id in CHANGED_IDS:
        events.append(
            {
                "event_id": f"pilot-004-{partition_id.lower()}",
                "partition_id": partition_id,
                "event_kind": "diagnostic_pilot",
                "mode": "strict_complete_cells",
                "query_cells": [
                    {
                        "cell_id": cell["cell_id"],
                        "branch_id": cell["branch_id"],
                        "query": cell["query"],
                        "query_sha256": cell["query_sha256"],
                    }
                    for cell in partitions[partition_id]["cells"]
                ],
            }
        )
    total_cells = sum(entry["packed_cell_count"] for entry in partitions.values())
    live_cells = sum(
        partitions[partition_id]["packed_cell_count"] for partition_id in CHANGED_IDS
    )
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "packing_schema_version": PACKING_SCHEMA_VERSION,
        "pilot": PILOT_NUMBER,
        "source": {"id": SOURCE_ID, "label": SOURCE_LABEL},
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "requested_window": {
            "start_date": DATE_START,
            "cutoff_date": DATE_END,
            "inclusive": True,
            "mode": "local post-filter after complete raw traversal",
        },
        "schedule_partitions": list(SCHEDULE_IDS),
        "live_run_partitions": list(CHANGED_IDS),
        "carried_forward_partitions": list(UNCHANGED_IDS),
        "controls": {
            "database_scope": "full IAF Digital Library",
            "date": "no lossy source date clause; apply the diagnostic bounds locally",
            "language": "not applied",
            "publication_type": "no added restriction; source is conference-paper scoped",
            "access": "not applied",
            "controlled_vocabulary": "not applied",
            "wildcard": False,
            "proximity": False,
            "pair_expansion": False,
            "complete_source_total_cap": 5000,
        },
        "source_syntax": {
            "literal": "one straight double-quoted token or ordered phrase",
            "and": "whitespace conjunction",
            "or": "uppercase OR",
            "maximum_query_characters": MAX_QUERY_CHARACTERS,
            "compound_translation": "distribute named outer OR branches, then pack each conjunction branch into deterministic cells",
        },
        "term_counts": TERM_COUNTS,
        "packing": {
            "method": "nested contiguous factor partition with dynamic programming and greedy inner packing",
            "lossless_basis": (
                "Every branch cell is a Cartesian rectangle over ordinary term alternatives. "
                "Each branch certificate covers every alternative tuple exactly once. The union "
                "of declared branches is the protocol compound Boolean expression."
            ),
            "complete_schedule_cells": total_cells,
            "live_pilot_cells": live_cells,
            "wildcards_inserted": False,
        },
        "carry_forward": carry_forward,
        "partitions": partitions,
        "events": events,
    }


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def factor_group(factor: Factor, payload: Mapping[str, Any]) -> Group:
    bounds = payload.get("alternative_range")
    if not isinstance(bounds, Mapping):
        raise PlanError("A factor range is missing")
    start = bounds.get("start")
    end = bounds.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or start < 1
        or end < start
        or end > len(factor.alternatives)
    ):
        raise PlanError("A factor range is invalid")
    return factor.alternatives[start - 1 : end]


def validate_plan_payload(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    require(
        payload.get("schema_version") == PLAN_SCHEMA_VERSION,
        "Wrong plan schema",
        errors,
    )
    require(
        payload.get("packing_schema_version") == PACKING_SCHEMA_VERSION,
        "Wrong packing schema",
        errors,
    )
    require(
        payload.get("protocol_commit") == PROTOCOL_COMMIT,
        "Wrong protocol commit",
        errors,
    )
    require(
        payload.get("schedule_partitions") == list(SCHEDULE_IDS),
        "Schedule changed",
        errors,
    )
    require(
        payload.get("live_run_partitions") == list(CHANGED_IDS),
        "Live scope changed",
        errors,
    )
    require(
        payload.get("controls", {}).get("wildcard") is False, "Wildcard enabled", errors
    )
    require(
        payload.get("controls", {}).get("proximity") is False,
        "Proximity enabled",
        errors,
    )
    require(
        payload.get("controls", {}).get("pair_expansion") is False,
        "Pair expansion enabled",
        errors,
    )
    require(payload.get("term_counts") == TERM_COUNTS, "Term counts changed", errors)
    partitions = payload.get("partitions")
    if not isinstance(partitions, Mapping):
        return [*errors, "Partitions are missing"]
    require(tuple(partitions) == SCHEDULE_IDS, "Partition order changed", errors)
    total_cells = 0
    live_cells = 0
    for partition_id in SCHEDULE_IDS:
        entry = partitions.get(partition_id)
        if not isinstance(entry, Mapping):
            errors.append(f"{partition_id}: missing entry")
            continue
        require(
            entry.get("boolean_form") == BOOLEAN_FORMS[partition_id],
            f"{partition_id}: Boolean form changed",
            errors,
        )
        branches = entry.get("branches")
        expected_branches = PARTITION_BRANCHES[partition_id]
        if not isinstance(branches, list) or len(branches) != len(expected_branches):
            errors.append(f"{partition_id}: branch schedule changed")
            continue
        parsed_partition_cells = []
        expected_cell_number = 1
        for branch, (expected_branch_id, factor_names) in zip(
            branches, expected_branches
        ):
            if not isinstance(branch, Mapping):
                errors.append(f"{partition_id}: malformed branch")
                continue
            require(
                branch.get("branch_id") == expected_branch_id,
                f"{partition_id}: branch ID changed",
                errors,
            )
            require(
                branch.get("factor_names") == list(factor_names),
                f"{partition_id}/{expected_branch_id}: factors changed",
                errors,
            )
            factors = tuple(factor_for(name) for name in factor_names)
            cells = branch.get("cells")
            if not isinstance(cells, list) or not cells:
                errors.append(f"{partition_id}/{expected_branch_id}: cells missing")
                continue
            parsed_groups = []
            for branch_cell_number, cell in enumerate(cells, start=1):
                if not isinstance(cell, Mapping):
                    errors.append(
                        f"{partition_id}/{expected_branch_id}: malformed cell"
                    )
                    continue
                expected_cell_id = f"cell-{expected_cell_number:04d}"
                expected_branch_cell_id = (
                    f"{expected_branch_id}-{branch_cell_number:04d}"
                )
                require(
                    cell.get("cell_id") == expected_cell_id,
                    f"{partition_id}: cell order changed",
                    errors,
                )
                require(
                    cell.get("branch_cell_id") == expected_branch_cell_id,
                    f"{partition_id}: branch cell order changed",
                    errors,
                )
                ranges = cell.get("factor_ranges")
                if not isinstance(ranges, list) or len(ranges) != len(factors):
                    errors.append(f"{partition_id}/{expected_cell_id}: ranges changed")
                    continue
                groups = []
                for factor_index, (factor, range_payload) in enumerate(
                    zip(factors, ranges), start=1
                ):
                    if not isinstance(range_payload, Mapping):
                        errors.append(
                            f"{partition_id}/{expected_cell_id}: malformed range"
                        )
                        continue
                    require(
                        range_payload.get("factor_index") == factor_index
                        and range_payload.get("factor") == factor.name,
                        f"{partition_id}/{expected_cell_id}: factor metadata changed",
                        errors,
                    )
                    try:
                        groups.append(factor_group(factor, range_payload))
                    except PlanError as error:
                        errors.append(f"{partition_id}/{expected_cell_id}: {error}")
                if len(groups) != len(factors):
                    continue
                query = render_groups(tuple(groups))
                require(
                    cell.get("query") == query,
                    f"{partition_id}/{expected_cell_id}: query changed",
                    errors,
                )
                require(
                    cell.get("query_characters") == len(query)
                    and cell.get("query_sha256") == text_sha256(query),
                    f"{partition_id}/{expected_cell_id}: query evidence changed",
                    errors,
                )
                require(
                    len(query) <= MAX_QUERY_CHARACTERS,
                    f"{partition_id}/{expected_cell_id}: query exceeds cap",
                    errors,
                )
                require(
                    "*" not in query
                    and "?" not in query
                    and "NEAR" not in query.upper()
                    and " AND " not in query,
                    f"{partition_id}/{expected_cell_id}: source syntax changed",
                    errors,
                )
                parsed_groups.append(tuple(groups))
                parsed_partition_cells.append(cell)
                expected_cell_number += 1
            certificate = coverage_certificate(factors, parsed_groups)
            require(
                certificate.get("exactly_once") is True
                and branch.get("coverage_certificate") == certificate,
                f"{partition_id}/{expected_branch_id}: coverage changed",
                errors,
            )
            require(
                branch.get("packed_cell_count") == len(cells),
                f"{partition_id}/{expected_branch_id}: cell count changed",
                errors,
            )
        require(
            entry.get("cells") == parsed_partition_cells
            and entry.get("packed_cell_count") == len(parsed_partition_cells),
            f"{partition_id}: flat cell schedule changed",
            errors,
        )
        total_cells += len(parsed_partition_cells)
        if partition_id in CHANGED_IDS:
            live_cells += len(parsed_partition_cells)
    packing = payload.get("packing", {})
    require(
        packing.get("complete_schedule_cells") == total_cells,
        "Complete cell total changed",
        errors,
    )
    require(
        packing.get("live_pilot_cells") == live_cells, "Live cell total changed", errors
    )
    carry = payload.get("carry_forward", {})
    require(
        carry.get("all_query_cells_identical") is True
        and tuple(carry.get("entries", {})) == UNCHANGED_IDS,
        "Pilot 003 carry-forward evidence changed",
        errors,
    )
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != len(CHANGED_IDS):
        errors.append("Live events changed")
    else:
        for event, partition_id in zip(events, CHANGED_IDS):
            require(
                event.get("partition_id") == partition_id
                and event.get("query_cells")
                == [
                    {
                        "cell_id": cell["cell_id"],
                        "branch_id": cell["branch_id"],
                        "query": cell["query"],
                        "query_sha256": cell["query_sha256"],
                    }
                    for cell in partitions[partition_id]["cells"]
                ],
                f"{partition_id}: live event changed",
                errors,
            )
    return errors


def write_json_no_clobber(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise PlanError(f"Refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output = args.output_path.expanduser()
    if args.check:
        payload = json.loads(output.read_text(encoding="utf-8"))
        errors = validate_plan_payload(payload)
        print(
            json.dumps(
                {"status": "ok" if not errors else "error", "errors": errors}, indent=2
            )
        )
        return 1 if errors else 0
    payload = build_plan_payload()
    errors = validate_plan_payload(payload)
    if errors:
        raise PlanError("Generated plan failed validation: " + "; ".join(errors))
    write_json_no_clobber(output, payload)
    print(
        json.dumps(
            {
                "saved": str(output),
                "complete_schedule_cells": payload["packing"][
                    "complete_schedule_cells"
                ],
                "live_pilot_cells": payload["packing"]["live_pilot_cells"],
                "carry_forward_cells": payload["packing"]["complete_schedule_cells"]
                - payload["packing"]["live_pilot_cells"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
