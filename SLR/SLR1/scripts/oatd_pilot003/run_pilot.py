#!/usr/bin/env python3
"""Plan and run the lossless OATD Pilot 003 diagnostic.

This is deliberately a pilot-only runner.  It imports the shared OATD adapter
and the shared nine-partition schedule without copying either.  It never
navigates a complete oversized expression: every browser submission is an
explicit distributive, route-guarded cell and uses the adapter's strict
(two-pass Record-ID) mode.  A failed, over-cap, or unattempted cell leaves its
partition total and Record-ID union null.

Run source work only through the shared browser wrapper, for example:

  caffeinate -dims uv run /Users/antho/agent-tools-worktrees/slr-integration/internet/skills/browser/scripts/run_with_browser.py -- \
    python3 SLR/SLR1/scripts/oatd_pilot003/run_pilot.py --execute

Without ``--execute`` the runner writes/rechecks the exact offline plan only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


PILOT = "003"
SOURCE_ID = "oatd"
SOURCE_NAME = "Open Access Theses and Dissertations (OATD)"
DIAGNOSTIC_START = "2011-01-01"
DIAGNOSTIC_CUTOFF = "2026-08-29"
SOURCE_YEAR_START = 2011
SOURCE_YEAR_END = 2026
LANGUAGE = "English"
CELL_TARGET = 1_500
NAVIGATION_GUARD = 8_000
ADAPTER_VERSION_EXPECTED = "8"
PLAN_SCHEMA = "oatd-pilot-003-lossless-plan/v1"
ASSESSMENT_SCHEMA = "oatd-pilot-003-execution-assessment/v1"
PREFLIGHT_SCHEMA = "oatd-pilot-003-browser-preflight/v1"
INVESTIGATION_SCHEMA = "oatd-pilot-003-over-100-investigation/v1"

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[1]
PILOT_DIR = SLR1_ROOT / "source-specific" / "oatd" / "pilots" / PILOT
DEFAULT_OUTPUT_DIR = PILOT_DIR / "searches"
SCHEDULE_QUERIES_PATH = SLR1_ROOT / "scripts" / "pilot_schedule" / "queries.py"
INTEGRATION_ROOT = Path(
    os.environ.get(
        "SLR_INTEGRATION_ROOT", "/Users/antho/agent-tools-worktrees/slr-integration"
    )
)
OATD_ADAPTER_PATH = (
    INTEGRATION_ROOT / "internet" / "skills" / "browser" / "scripts" / "search_oatd.py"
)
EVENT_RUNNER_PATH = (
    INTEGRATION_ROOT / "internet" / "skills" / "browser" / "scripts" / "run_search_events.py"
)
BROWSER_RUNNER_PATH = (
    INTEGRATION_ROOT
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "run_with_browser.py"
)

# These are route-safe rectangular grids derived offline with the adapter's
# 1,500-character default.  The runner verifies every result against the
# adapter rather than trusting these values.  Keeping a complete named-field
# pair together is intentional: it preserves both orders and all six fields
# in every query cell, including the very large T2 block.
GRID_COUNTS: dict[str, tuple[int, ...]] = {
    "A1": (2, 2, 4),
    "A2": (2, 2, 5),
    "A3": (2, 2, 2),
    "B1": (1, 3),
    "B2": (2, 2, 2),
    "BG1": (1, 17),
    "BG2": (1, 17),
    "BC1": (4, 37),
    "BT2": (2, 4, 224),
}

PARTITION_FACTORS: dict[str, tuple[tuple[str, ...], ...]] = {
    "A1": (("P",), ("E_H",), ("M_H",)),
    "A2": (("P",), ("E_F",), ("M_H", "M_B")),
    "A3": (("P",), ("E_H",), ("M_B",)),
    "B1": (("P",), ("M_H",)),
    "B2": (("P",), ("M_B",), ("R",)),
    "BG1": (("P",), ("G_model",)),
    "BG2": (("P",), ("G_structure",)),
    "BC1": (("P",), ("C1",)),
    "BT2": (("P",), ("M_B",), ("T2",)),
}

LOCAL_PATH = re.compile(r"(?:/Users/[^\s'\"]+|/var/[^\s'\"]+|/tmp/[^\s'\"]+)")


class PilotError(RuntimeError):
    """A fail-closed Pilot 003 planning or execution error."""


@dataclass(frozen=True)
class PlannedCell:
    partition_id: str
    cell_id: str
    query: str
    query_sha256: str
    encoded_route_characters: int
    factor_group_indices: tuple[int, ...]
    factor_alternative_counts: tuple[int, ...]


@dataclass(frozen=True)
class AdapterModules:
    oatd: Any
    schedule: Any
    events: Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_text(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return LOCAL_PATH.sub("<local-path>", text)[:800]


def no_clobber_json(path: Path, value: Mapping[str, Any], *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise PilotError(f"Refusing to overwrite existing artifact: {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_module(name: str, path: Path) -> Any:
    if not path.is_file():
        raise PilotError(f"Required read-only integration/source file is unavailable: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PilotError(f"Could not load module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_modules() -> AdapterModules:
    schedule = load_module("oatd_pilot003_schedule", SCHEDULE_QUERIES_PATH)
    oatd = load_module("oatd_pilot003_adapter", OATD_ADAPTER_PATH)
    events = load_module("oatd_pilot003_events", EVENT_RUNNER_PATH)
    if getattr(oatd, "ADAPTER_VERSION", None) != ADAPTER_VERSION_EXPECTED:
        raise PilotError(
            "Pilot 003 is pinned to the repaired OATD adapter version "
            f"{ADAPTER_VERSION_EXPECTED}; found {getattr(oatd, 'ADAPTER_VERSION', None)!r}."
        )
    if tuple(schedule.MAIN_FACTORS) != tuple(PARTITION_FACTORS):
        raise PilotError("The shared pilot schedule no longer matches Pilot 003's nine partitions.")
    return AdapterModules(oatd=oatd, schedule=schedule, events=events)


def encoded_atom_characters(value: str) -> int:
    """Use URL encoding as the stable weight used for contiguous grouping."""
    return len(urlencode((("q", value),))) - 2


def weighted_contiguous_chunks(alternatives: Sequence[str], count: int) -> tuple[tuple[str, ...], ...]:
    """Split source-order alternatives into nonempty, contiguous OR groups.

    The grouping is a purely distributive partition; it never edits, removes,
    deduplicates, or reorders an alternative.  URL-encoded weights make the
    source's real route length, rather than raw character count, the input.
    """
    if count < 1 or count > len(alternatives):
        raise PilotError("Invalid requested OATD distributive group count.")
    weights = [encoded_atom_characters(item) + encoded_atom_characters(" OR ") for item in alternatives]
    target = sum(weights) / count
    groups: list[tuple[str, ...]] = []
    current: list[str] = []
    current_weight = 0
    consumed = 0
    for item, weight in zip(alternatives, weights):
        remaining_after_current = len(alternatives) - consumed - len(current)
        must_leave = count - len(groups) - 1
        if (
            len(groups) < count - 1
            and current
            and current_weight + weight > target
            and remaining_after_current >= must_leave
        ):
            groups.append(tuple(current))
            consumed += len(current)
            current = []
            current_weight = 0
        current.append(item)
        current_weight += weight
    if current:
        groups.append(tuple(current))
    if len(groups) != count or any(not group for group in groups):
        raise PilotError("Could not make the requested nonempty OATD OR groups.")
    if tuple(item for group in groups for item in group) != tuple(alternatives):
        raise PilotError("OATD OR grouping changed source-order alternative membership.")
    return tuple(groups)


def or_block(alternatives: Sequence[str]) -> str:
    if not alternatives:
        raise PilotError("OATD OR block cannot be empty.")
    return "(" + " OR ".join(alternatives) + ")"


def grouped_distributive_query(groups: Sequence[Sequence[str]]) -> str:
    """Render only the adapter planner's explicitly grouped safe shape."""
    blocks = [or_block(group) for group in groups]
    if len(blocks) == 2:
        # The outer form is ``(left AND (term OR ...))`` exactly.
        return f"({blocks[0]} AND {blocks[1]})"
    if len(blocks) == 3:
        # Parenthesize the left conjunction before the planner-facing OR arm.
        return f"(({blocks[0]} AND {blocks[1]}) AND {blocks[2]})"
    raise PilotError("Pilot 003 supports only two- or three-factor schedule partitions.")


def factor_label(factor: Sequence[str]) -> str:
    return "_OR_".join(factor)


def controls_for_query(modules: AdapterModules, query: str) -> Any:
    return modules.oatd.build_oatd_search_configuration(
        query,
        language=LANGUAGE,
        year_start=SOURCE_YEAR_START,
        year_end=SOURCE_YEAR_END,
        sort="relevance",
        page_size=30,
    )


def raw_encoded_route_characters(modules: AdapterModules, query: str) -> int:
    """Measure a candidate full route without asking the adapter to accept it."""
    source_query = (
        f"{query} AND language:(en OR eng OR english) AND "
        "pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
    )
    parameters = (("q", source_query),)
    return len(modules.oatd.SEARCH_URL + "?" + urlencode(parameters))


def direct_planner_observation(modules: AdapterModules, query: str) -> dict[str, Any]:
    """Record why the complete expression is never navigated.

    This invokes the repaired planner offline only when its ordinary query
    validator accepts the complete expression.  A planner failure is useful
    evidence: it proves that the later explicit rectangular distribution was
    necessary rather than an arbitrary narrowing.
    """
    encoded = raw_encoded_route_characters(modules, query)
    observation: dict[str, Any] = {
        "complete_expression_navigated": False,
        "encoded_route_characters": encoded,
        "navigation_guard_characters": NAVIGATION_GUARD,
        "lossless_cell_target_characters": CELL_TARGET,
    }
    try:
        configuration = controls_for_query(modules, query)
    except Exception as error:  # adapter's input error is a planned safe boundary
        observation.update(
            {
                "adapter_configuration": "rejected_before_navigation",
                "planner_result": "not_called",
                "reason": safe_text(error),
            }
        )
        return observation
    try:
        planned = modules.oatd.plan_lossless_oatd_or_query_cells(configuration)
    except Exception as error:  # source-specific planner intentionally fails closed
        observation.update(
            {
                "adapter_configuration": "accepted_offline",
                "planner_result": "failed_closed",
                "reason": safe_text(error),
            }
        )
        return observation
    observation.update(
        {
            "adapter_configuration": "accepted_offline",
            "planner_result": "cells_available_offline",
            "planner_cell_count": len(planned),
            "planner_max_encoded_route_characters": max(
                modules.oatd.encoded_oatd_search_route_characters(item) for item in planned
            ),
        }
    )
    return observation


def pair_clause_audit(modules: AdapterModules, alternatives: Iterable[str]) -> dict[str, Any]:
    """Assert every declared pair retains both orders in all six named fields."""
    fields = ("title", "author", "abstract", "publisher", "subject", "discipline")
    pairs_checked = 0
    clauses_checked = 0
    for alternative in alternatives:
        # Literal alternatives have no named-field proximity clauses.  The
        # renderer always wraps each declared pair in its own outer group.
        if not alternative.startswith("(") or "~5" not in alternative:
            continue
        inner = modules.oatd._strip_one_oatd_outer_group(alternative)
        clauses = modules.oatd._split_top_level_oatd_operator(inner, "OR")
        if len(clauses) != 12:
            raise PilotError("A declared OATD pair no longer has exactly 12 named clauses.")
        seen: set[str] = set()
        phrases_by_field: dict[str, list[str]] = {field: [] for field in fields}
        for clause in clauses:
            match = re.fullmatch(
                r'(title|author|abstract|publisher|subject|discipline):\("(.+)"~5\)',
                clause,
            )
            if match is None:
                raise PilotError("A named OATD pair clause lost its fielded quoted ~5 form.")
            field, phrase = match.groups()
            seen.add(clause)
            phrases_by_field[field].append(phrase)
        if len(seen) != 12:
            raise PilotError("A declared OATD pair repeated a named-field order clause.")
        two_orders = set(phrases_by_field[fields[0]])
        if len(two_orders) != 2 or any(
            len(phrases_by_field[field]) != 2
            or set(phrases_by_field[field]) != two_orders
            for field in fields
        ):
            raise PilotError(
                "A declared OATD pair did not retain both phrase orders in every named field."
            )
        pairs_checked += 1
        clauses_checked += len(clauses)
    return {"complete_pair_unions_checked": pairs_checked, "named_field_two_order_clauses_checked": clauses_checked}


def build_partition_plan(modules: AdapterModules, partition_id: str) -> dict[str, Any]:
    schedule = modules.schedule
    renderer = schedule.RENDERERS[SOURCE_ID]
    factors = PARTITION_FACTORS[partition_id]
    expected_factors = schedule.MAIN_FACTORS[partition_id]
    if factors != expected_factors:
        raise PilotError(f"{partition_id}: Pilot factor declaration differs from shared schedule.")
    alternatives = tuple(renderer.alternatives(factor) for factor in factors)
    group_counts = GRID_COUNTS[partition_id]
    if len(group_counts) != len(alternatives):
        raise PilotError(f"{partition_id}: Grid dimensionality is wrong.")
    grouped = tuple(
        weighted_contiguous_chunks(factor_alternatives, group_count)
        for factor_alternatives, group_count in zip(alternatives, group_counts)
    )
    full_query = grouped_distributive_query(alternatives)
    cells: list[PlannedCell] = []
    expected_atomic_conjunctions = math.prod(len(item) for item in alternatives)
    covered_atomic_conjunctions = 0
    for number, selected_groups in enumerate(product(*grouped), start=1):
        query = grouped_distributive_query(selected_groups)
        configuration = controls_for_query(modules, query)
        encoded = modules.oatd.encoded_oatd_search_route_characters(configuration)
        if encoded > CELL_TARGET or encoded > NAVIGATION_GUARD:
            raise PilotError(
                f"{partition_id}: planned cell {number} is not route-safe ({encoded} characters)."
            )
        # This is the required adapter planner call for every final cell.  It
        # must be an identity operation because the distributive grid already
        # made every OR branch route-safe.  A nonidentity result indicates a
        # changed adapter/route encoding and fails closed before browser work.
        rechecked = modules.oatd.plan_lossless_oatd_or_query_cells(configuration)
        if len(rechecked) != 1 or rechecked[0].requested_query != query:
            raise PilotError(
                f"{partition_id}: adapter planner changed a preplanned lossless cell."
            )
        factor_indices = tuple(
            next(index for index, group in enumerate(all_groups, start=1) if group == selected)
            for all_groups, selected in zip(grouped, selected_groups)
        )
        factor_counts = tuple(len(group) for group in selected_groups)
        covered_atomic_conjunctions += math.prod(factor_counts)
        cells.append(
            PlannedCell(
                partition_id=partition_id,
                cell_id=f"{partition_id}-{number:04d}-of-{math.prod(group_counts):04d}",
                query=query,
                query_sha256=sha256_text(query),
                encoded_route_characters=encoded,
                factor_group_indices=factor_indices,
                factor_alternative_counts=factor_counts,
            )
        )
    if len(cells) != math.prod(group_counts):
        raise PilotError(f"{partition_id}: grid did not yield its declared cell count.")
    if covered_atomic_conjunctions != expected_atomic_conjunctions:
        raise PilotError(f"{partition_id}: distributive cells do not cover every atomic conjunction.")
    if tuple(item for groups in grouped for group in groups for item in group) != tuple(
        item for factor in alternatives for item in factor
    ):
        # The joined global order differs across factors, so check each one
        # precisely.  This branch remains defensive and intentionally clear.
        for original, grouped_factor in zip(alternatives, grouped):
            if tuple(item for group in grouped_factor for item in group) != original:
                raise PilotError(f"{partition_id}: factor grouping lost/reordered an alternative.")
    for original, grouped_factor in zip(alternatives, grouped):
        if tuple(item for group in grouped_factor for item in group) != original:
            raise PilotError(f"{partition_id}: factor grouping lost/reordered an alternative.")
    pair_audit = pair_clause_audit(modules, (item for factor in alternatives for item in factor))
    if "*" in full_query or "?" in full_query or any("*" in cell.query or "?" in cell.query for cell in cells):
        raise PilotError(f"{partition_id}: wildcard appeared in a normative translation.")
    return {
        "partition_id": partition_id,
        "protocol_boolean_form": {
            "A1": "P AND E_H AND M_H",
            "A2": "P AND E_F AND (M_H OR M_B)",
            "A3": "P AND E_H AND M_B",
            "B1": "P AND M_H",
            "B2": "P AND M_B AND R",
            "BG1": "P AND G_model",
            "BG2": "P AND G_structure",
            "BC1": "P AND C1",
            "BT2": "P AND M_B AND T2",
        }[partition_id],
        "factor_labels": [factor_label(factor) for factor in factors],
        "factor_alternative_counts": [len(value) for value in alternatives],
        "distributive_grid_group_counts": list(group_counts),
        "planned_cell_count": len(cells),
        "complete_expression": {
            "sha256": sha256_text(full_query),
            "raw_characters": len(full_query),
            **direct_planner_observation(modules, full_query),
            "never_submitted_reason": "complete source expression is oversized; only exact route-safe distributive cells are eligible for browser navigation",
        },
        "coverage": {
            "factor_alternatives_preserved_in_source_order": True,
            "expected_atomic_conjunction_count": expected_atomic_conjunctions,
            "covered_atomic_conjunction_count": covered_atomic_conjunctions,
            "each_atomic_conjunction_covered_once_by_disjoint_factor_groups": True,
            "wildcards_present": False,
            **pair_audit,
        },
        "cells": [
            {
                "cell_id": cell.cell_id,
                "query": cell.query,
                "query_sha256": cell.query_sha256,
                "encoded_route_characters": cell.encoded_route_characters,
                "factor_group_indices": list(cell.factor_group_indices),
                "factor_alternative_counts": list(cell.factor_alternative_counts),
                "adapter_planner_rechecked_as_identity": True,
            }
            for cell in cells
        ],
    }


def build_plan(modules: AdapterModules) -> dict[str, Any]:
    partitions = {
        partition_id: build_partition_plan(modules, partition_id)
        for partition_id in PARTITION_FACTORS
    }
    return {
        "schema_version": PLAN_SCHEMA,
        "pilot": PILOT,
        "source": SOURCE_NAME,
        "source_id": SOURCE_ID,
        "kind": "diagnostic_only_not_a_final_search",
        "created_at_utc": utc_now(),
        "adapter": {
            "path_is_read_only_integration": True,
            "adapter_id": modules.oatd.ADAPTER_ID,
            "adapter_version": modules.oatd.ADAPTER_VERSION,
            "route_navigation_guard_characters": modules.oatd.MAX_OATD_SEARCH_ROUTE_CHARACTERS,
            "lossless_or_cell_target_characters": modules.oatd.DEFAULT_LOSSLESS_OATD_OR_CELL_ROUTE_CHARACTERS,
        },
        "window": {
            "requested_start": DIAGNOSTIC_START,
            "requested_cutoff": DIAGNOSTIC_CUTOFF,
            "source_year_start": SOURCE_YEAR_START,
            "source_year_end": SOURCE_YEAR_END,
            "source_query_scope": "inclusive pub_dt calendar years 2011 through 2026",
            "cutoff_year_screening_required": True,
            "cutoff_year_screening_reason": "OATD accepts the native year route; the exact 2026-08-29 cutoff remains a screening check for 2026 records.",
        },
        "controls": {
            "language": {
                "requested": LANGUAGE,
                "source_value": "(en OR eng OR english)",
                "apply_condition": "only after a healthy route and this exact source-rendered route/query readback",
                "full_text_language_screening": "required; English metadata does not prove the report language",
            },
            "date": "typed inclusive UTC calendar-year pub_dt clause",
            "sort": "source-rendered Relevance only; no client-side sort",
            "excluded_controls": {
                "degree": "not applied",
                "level": "not applied",
                "completion": "not applied",
                "access": "not applied",
                "full_text": "not applied",
                "publication_type": "not applied",
                "country": "not applied",
                "creative_commons": "not applied",
                "facets": "not applied",
                "controlled_terms": "not applied",
                "wildcard": "not used",
            },
        },
        "execution_policy": {
            "strict_mode": "two complete source-rendered Relevance traversals with ordered OATD Record-ID reconciliation per cell",
            "cell_failure_rule": "any failed, over-cap, or unattempted cell leaves the complete partition total and union null",
            "source_rate_rule": "run sequentially with the adapter's bounded busy policy and stop at the configured source-request budget; never replay the historical oversized route",
            "over_100_rule": "a complete deduplicated Record-ID union over 100 receives a local investigation artifact; only lossless metadata/language/eligible-type/controlled-term controls could justify a later refinement",
        },
        "partition_order": list(PARTITION_FACTORS),
        "partitions": partitions,
        "total_planned_cells": sum(value["planned_cell_count"] for value in partitions.values()),
    }


def browser_preflight() -> dict[str, Any]:
    """Read the shared launcher status without opening a source route."""
    result: dict[str, Any] = {
        "schema_version": PREFLIGHT_SCHEMA,
        "checked_at_utc": utc_now(),
        "launcher": "shared_local_browser_runner_status",
        "source_requests_attempted": 0,
    }
    if not BROWSER_RUNNER_PATH.is_file():
        result.update({"healthy": False, "status": "browser_runner_missing"})
        return result
    try:
        completed = subprocess.run(
            ["uv", "run", str(BROWSER_RUNNER_PATH), "--status"],
            cwd=SLR1_ROOT.parents[1],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        result.update(
            {
                "healthy": False,
                "status": "browser_status_check_failed",
                "error": safe_text(error),
            }
        )
        return result
    payload: dict[str, Any] | None = None
    try:
        parsed = json.loads(completed.stdout.strip()) if completed.stdout.strip() else None
        if isinstance(parsed, dict):
            payload = parsed
    except json.JSONDecodeError:
        payload = None
    healthy = bool(payload and payload.get("healthy") is True and completed.returncode == 0)
    result.update(
        {
            "healthy": healthy,
            "status": "healthy" if healthy else "browser_unavailable",
            "launcher_exit_code": completed.returncode,
            "browser_access": payload.get("browser_access") if payload else None,
            "error": safe_text((payload or {}).get("error") or completed.stderr),
        }
    )
    return result


def expected_language_readback(payload: Mapping[str, Any]) -> bool:
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, Mapping):
        return False
    language = metadata.get("language_filter")
    return (
        metadata.get("observed_exact_query_echo") is True
        and isinstance(language, Mapping)
        and language.get("display_label") == LANGUAGE
        and language.get("source_value") == "(en OR eng OR english)"
    )


def expected_strict_cell(payload: Mapping[str, Any], cell: PlannedCell) -> tuple[bool, str | None]:
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, Mapping):
        return False, "missing_output_metadata"
    rows = payload.get("results")
    total = payload.get("total")
    if not isinstance(rows, list) or not isinstance(total, int) or total < 0:
        return False, "missing_exact_total_or_rows"
    ids = [row.get("paperId") for row in rows if isinstance(row, Mapping)]
    if len(ids) != len(rows) or any(not isinstance(value, str) or not value for value in ids):
        return False, "missing_record_id"
    checks = (
        payload.get("query") == cell.query,
        metadata.get("status") == "success",
        metadata.get("require_complete") is True,
        metadata.get("retrieval_complete") is True,
        metadata.get("passes_completed") == 2,
        metadata.get("strict_ordered_record_ids_reconciled") is True,
        metadata.get("observed_exact_query_echo") is True,
        metadata.get("earliest_year_filter") == SOURCE_YEAR_START,
        metadata.get("latest_year_filter") == SOURCE_YEAR_END,
        metadata.get("country_filter") is None,
        metadata.get("creative_commons_only") is False,
        metadata.get("page_size") == 30,
        len(rows) == total,
        expected_language_readback(payload),
    )
    return (True, None) if all(checks) else (False, "strict_control_or_record_reconciliation_failed")


def adapter_command(
    modules: AdapterModules,
    *,
    query: str,
    output_path: Path,
    run_id: str,
    partition_id: str,
    count_only: bool,
    source_total: int | None = None,
) -> list[str]:
    command = [
        "uv",
        "run",
        str(OATD_ADAPTER_PATH),
        "--query",
        query,
        "--language",
        LANGUAGE,
        "--year-start",
        str(SOURCE_YEAR_START),
        "--year-end",
        str(SOURCE_YEAR_END),
        "--sort",
        "relevance",
        "--page-size",
        "30",
        "--timeout",
        "45",
        "--page-delay-seconds",
        "0.5",
        "--detail-delay-seconds",
        "0.5",
        "--busy-retries",
        "2",
        "--busy-retry-delay-seconds",
        "30",
        "--output-path",
        str(output_path),
        "--prisma-run-id",
        run_id,
        "--prisma-review-id",
        "slr1-oatd-pilot-003",
        "--prisma-strategy-reference",
        "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version",
        "276ca87",
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition_id,
        "--prisma-partition-label",
        partition_id,
        "--prisma-partition-description",
        f"Pilot 003 diagnostic partition {partition_id}",
    ]
    if count_only:
        command.extend(("--count-only", "--limit", "1", "--max-pages", "1"))
    else:
        if source_total is None or source_total < 0:
            raise PilotError("Strict OATD execution requires a count-only source total.")
        command.extend(
            (
                "--require-complete",
                "--limit",
                str(max(1, source_total)),
                "--max-pages",
                str(max(1, math.ceil(source_total / 30))),
            )
        )
    return command


def run_adapter(command: Sequence[str], *, timeout_seconds: float) -> tuple[int | None, str]:
    try:
        completed = subprocess.run(
            list(command),
            cwd=SLR1_ROOT.parents[1],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return completed.returncode, safe_text(completed.stderr or completed.stdout)
    except subprocess.TimeoutExpired:
        return 124, "adapter_process_timeout"
    except (OSError, subprocess.SubprocessError) as error:
        return 127, safe_text(error)


def read_json_if_regular(path: Path) -> dict[str, Any] | None:
    try:
        if not path.is_file() or path.is_symlink():
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def compact_cell_state(cell: PlannedCell, *, status: str, reason: str | None = None, artifact: Path | None = None, total: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "cell_id": cell.cell_id,
        "query_sha256": cell.query_sha256,
        "encoded_route_characters": cell.encoded_route_characters,
        "status": status,
        "total": total,
    }
    if reason:
        result["reason"] = reason
    if artifact is not None:
        result["artifact"] = artifact.name
    return result


def unavailable_partition_states(plan: Mapping[str, Any], reason: str) -> dict[str, list[dict[str, Any]]]:
    states: dict[str, list[dict[str, Any]]] = {}
    for partition_id, partition in plan["partitions"].items():
        states[partition_id] = [
            {
                "cell_id": cell["cell_id"],
                "query_sha256": cell["query_sha256"],
                "encoded_route_characters": cell["encoded_route_characters"],
                "status": "not_attempted",
                "total": None,
                "reason": reason,
            }
            for cell in partition["cells"]
        ]
    return states


def make_unreconciled_union(states: Sequence[Mapping[str, Any]], reason: str) -> dict[str, Any]:
    completed = [state for state in states if state.get("status") == "strict_complete"]
    return {
        "schema_version": "academic-search-query-cell-union/v1",
        "status": "unreconciled",
        "lossless": False,
        "promotion_allowed": False,
        "union_total": None,
        "union_total_status": "unknown",
        "complete_cell_count": len(completed),
        "expected_cell_count": len(states),
        "reason": reason,
        "deduplication_performed": False,
    }


def investigate_over_100(
    partition_id: str,
    union: Mapping[str, Any],
    states: Sequence[Mapping[str, Any]],
    output_dir: Path,
    *,
    overwrite: bool,
) -> str | None:
    total = union.get("union_total")
    if not isinstance(total, int) or total <= 100 or union.get("lossless") is not True:
        return None
    raw = union.get("raw_record_count")
    investigation = {
        "schema_version": INVESTIGATION_SCHEMA,
        "pilot": PILOT,
        "source": SOURCE_NAME,
        "partition_id": partition_id,
        "trigger": "complete deduplicated OATD Record-ID union exceeds 100",
        "record_id_union_total": total,
        "raw_cell_record_events": raw,
        "cross_cell_overlap_count": union.get("cross_cell_overlap_count"),
        "strict_complete_cell_count": sum(state.get("status") == "strict_complete" for state in states),
        "review": {
            "action": "investigated locally; no source query refinement applied",
            "permitted_refinement_classes": [
                "lossless metadata control",
                "native English metadata control with exact route readback",
                "lossless eligible-type control",
                "validated controlled-term control",
            ],
            "rejected_controls": {
                "degree_or_level": "OATD facets are not a lossless completed-master-or-doctoral filter",
                "completion_or_access": "not an eligibility-preserving source filter",
                "publication_type": "no native article/document-type selector",
                "controlled_vocabulary": "no named controlled vocabulary, hierarchy, or explosion setting",
                "wildcard": "not used or introduced",
            },
            "outcome": "no no-loss refinement available from current OATD evidence; preserve the full union for screening",
        },
    }
    path = output_dir / "investigations" / f"{partition_id}-over-100.json"
    no_clobber_json(path, investigation, overwrite=overwrite)
    return path.relative_to(output_dir).as_posix()


def execute_plan(
    modules: AdapterModules,
    plan: Mapping[str, Any],
    output_dir: Path,
    *,
    strict_cell_cap: int,
    source_request_budget: int,
    overwrite: bool,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], int]:
    """Execute conservative count then strict passes, sequentially.

    A count-only route establishes the exact total and typed language readback.
    Strict traversal is then allowed only at or below the declared per-cell
    record cap.  Budget exhaustion records an unattempted cell; it is never
    presented as a source zero or a partial union.
    """
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        reason = "runner_not_started_inside_shared_browser_wrapper"
        return unavailable_partition_states(plan, reason), {"status": reason}, 0
    if not os.environ.get("BH_CDP_URL"):
        reason = "shared_browser_cdp_endpoint_not_supplied"
        return unavailable_partition_states(plan, reason), {"status": reason}, 0
    remaining = source_request_budget
    states: dict[str, list[dict[str, Any]]] = {partition_id: [] for partition_id in plan["partition_order"]}

    # The first route must be a healthy ordinary query, then the same route
    # with the English metadata control.  No schedule cell is submitted until
    # both exact source readbacks have succeeded.
    health: dict[str, Any] = {"status": "pending", "artifacts": []}
    health_dir = output_dir / "health"
    health_queries = (
        ("plain", 'title:(microRNA)', False),
        ("english", 'title:(microRNA)', True),
    )
    for label, query, require_english in health_queries:
        if remaining <= 0:
            health.update({"status": "request_budget_exhausted_before_language_readback"})
            return unavailable_partition_states(plan, health["status"]), health, source_request_budget - remaining
        path = health_dir / f"{label}.json"
        if path.exists():
            # Adapter artifacts are immutable/no-clobber.  Reuse their exact
            # observed result rather than accidentally resubmitting a route.
            payload = read_json_if_regular(path)
            return_code, message = 0, "existing_artifact"
        else:
            # First establish the ordinary healthy route in the pilot's
            # 2011–2026 source-year window. Then submit that same title/year
            # route with only the native English control added.
            command = [
                "uv", "run", str(OATD_ADAPTER_PATH), "--query", query,
                "--count-only", "--limit", "1", "--max-pages", "1",
                "--year-start", str(SOURCE_YEAR_START), "--year-end", str(SOURCE_YEAR_END),
                "--sort", "relevance", "--page-size", "30", "--timeout", "45",
                "--busy-retries", "2", "--busy-retry-delay-seconds", "30",
                "--output-path", str(path),
                "--prisma-run-id", f"pilot-oatd-003-health-{label}",
                "--prisma-review-id", "slr1-oatd-pilot-003",
                "--prisma-strategy-reference", "slr1-direct-query-schedule-v1",
                "--prisma-phase", "identification",
                "--prisma-coverage-scope", "partition",
                "--prisma-partition-id", "health",
                "--prisma-partition-label", "health",
                "--prisma-partition-description", "Pilot 003 healthy OATD route",
            ]
            if require_english:
                command.extend(("--language", LANGUAGE))
            return_code, message = run_adapter(command, timeout_seconds=90)
            payload = read_json_if_regular(path)
        remaining -= 1
        metadata = payload.get("output_metadata") if isinstance(payload, Mapping) else None
        exact = bool(isinstance(metadata, Mapping) and metadata.get("observed_exact_query_echo") is True)
        accepted = exact and (expected_language_readback(payload) if require_english else metadata.get("language_filter") is None)
        health["artifacts"].append(
            {
                "kind": label,
                "artifact": path.relative_to(output_dir).as_posix() if path.exists() else None,
                "adapter_exit_code": return_code,
                "status": "accepted" if accepted else "failed",
                "reason": None if accepted else message or "missing_exact_route_readback",
            }
        )
        if not accepted:
            health["status"] = "healthy_route_or_english_readback_failed"
            return unavailable_partition_states(plan, health["status"]), health, source_request_budget - remaining
    health["status"] = "healthy_route_then_exact_english_readback_confirmed"

    # Round-robin the nine partitions.  If the respectful run-wide request
    # budget is reached, each partition has had an opportunity to establish
    # a bounded diagnostic cell rather than earlier partitions consuming it.
    max_cells = max(
        len(plan["partitions"][partition_id]["cells"])
        for partition_id in plan["partition_order"]
    )
    for cell_number in range(max_cells):
        for partition_id in plan["partition_order"]:
            partition_cells = plan["partitions"][partition_id]["cells"]
            if cell_number >= len(partition_cells):
                continue
            raw_cell = partition_cells[cell_number]
            cell = PlannedCell(
                partition_id=partition_id,
                cell_id=raw_cell["cell_id"],
                query=raw_cell["query"],
                query_sha256=raw_cell["query_sha256"],
                encoded_route_characters=raw_cell["encoded_route_characters"],
                factor_group_indices=tuple(raw_cell["factor_group_indices"]),
                factor_alternative_counts=tuple(raw_cell["factor_alternative_counts"]),
            )
            if remaining <= 0:
                states[partition_id].append(compact_cell_state(cell, status="not_attempted", reason="source_request_budget_exhausted"))
                continue
            count_path = output_dir / "counts" / partition_id / f"{cell.cell_id}.json"
            if count_path.exists():
                count_payload = read_json_if_regular(count_path)
                count_code, count_message = 0, "existing_artifact"
            else:
                command = adapter_command(
                    modules,
                    query=cell.query,
                    output_path=count_path,
                    run_id=f"pilot-oatd-003-{cell.cell_id}-count",
                    partition_id=partition_id,
                    count_only=True,
                )
                count_code, count_message = run_adapter(command, timeout_seconds=90)
                count_payload = read_json_if_regular(count_path)
            remaining -= 1
            count_metadata = count_payload.get("output_metadata") if isinstance(count_payload, Mapping) else None
            total = count_payload.get("total") if isinstance(count_payload, Mapping) else None
            count_ok = (
                count_code == 0
                and isinstance(total, int)
                and total >= 0
                and isinstance(count_metadata, Mapping)
                and count_metadata.get("status") == "count_only"
                and count_metadata.get("observed_exact_query_echo") is True
                and expected_language_readback(count_payload)
            )
            if not count_ok:
                states[partition_id].append(compact_cell_state(cell, status="count_failed", reason=count_message or "count_route_readback_failed", artifact=count_path, total=None))
                continue
            if total > strict_cell_cap:
                states[partition_id].append(compact_cell_state(cell, status="strict_not_attempted_over_record_cap", reason=f"source_total_{total}_exceeds_strict_cell_record_cap_{strict_cell_cap}", artifact=count_path, total=None))
                continue
            # Count-only plus strict adapter invocation are separate source
            # interactions.  Do not start one when no budget remains.
            if remaining <= 0:
                states[partition_id].append(compact_cell_state(cell, status="strict_not_attempted", reason="source_request_budget_exhausted_after_count", artifact=count_path, total=None))
                continue
            strict_path = output_dir / "cells" / partition_id / f"{cell.cell_id}.json"
            if strict_path.exists():
                strict_payload = read_json_if_regular(strict_path)
                strict_code, strict_message = 0, "existing_artifact"
            else:
                command = adapter_command(
                    modules,
                    query=cell.query,
                    output_path=strict_path,
                    run_id=f"pilot-oatd-003-{cell.cell_id}",
                    partition_id=partition_id,
                    count_only=False,
                    source_total=total,
                )
                # Details are paced by the adapter.  Permit a strict low-volume
                # cell enough wall time for two traversals and bounded busy wait.
                strict_code, strict_message = run_adapter(command, timeout_seconds=max(180, 10 * (total + 2)))
                strict_payload = read_json_if_regular(strict_path)
            remaining -= 1
            strict_ok, strict_reason = expected_strict_cell(strict_payload or {}, cell)
            if strict_code == 0 and strict_ok:
                states[partition_id].append(compact_cell_state(cell, status="strict_complete", artifact=strict_path, total=total))
            else:
                states[partition_id].append(compact_cell_state(cell, status="strict_failed", reason=strict_reason or strict_message or "strict_adapter_failure", artifact=strict_path, total=None))
    return states, health, source_request_budget - remaining


def partition_assessment(
    modules: AdapterModules,
    partition_id: str,
    raw_plan: Mapping[str, Any],
    states: Sequence[Mapping[str, Any]],
    output_dir: Path,
    *,
    overwrite: bool,
) -> dict[str, Any]:
    planned_cells = raw_plan["cells"]
    strict_states = [state for state in states if state.get("status") == "strict_complete"]
    if len(strict_states) != len(planned_cells):
        union = make_unreconciled_union(states, "one_or_more_cells_not_strict_complete")
        investigation = None
    else:
        union_inputs: list[dict[str, Any]] = []
        cell_by_id = {cell["cell_id"]: cell for cell in planned_cells}
        for state in strict_states:
            artifact_name = state.get("artifact")
            payload = read_json_if_regular(output_dir / "cells" / partition_id / str(artifact_name)) if artifact_name else None
            if payload is None:
                union = make_unreconciled_union(states, "strict_artifact_missing_or_invalid")
                break
            ids = [row.get("paperId") for row in payload.get("results", []) if isinstance(row, Mapping)]
            cell = cell_by_id[state["cell_id"]]
            union_inputs.append(
                {
                    "cell_id": state["cell_id"],
                    "query": cell["query"],
                    "status": "complete",
                    "complete": True,
                    "total": payload.get("total"),
                    "source_total": payload.get("total"),
                    "source_total_status": "reported",
                    "stable_ids": ids,
                }
            )
        else:
            union = modules.events.lossless_query_cell_union(union_inputs)
            if union.get("lossless") is not True:
                union = make_unreconciled_union(states, "stable_record_id_union_failed_closed")
        investigation = investigate_over_100(partition_id, union, states, output_dir, overwrite=overwrite)
    total = union.get("union_total") if union.get("lossless") is True else None
    outcome = "complete" if total is not None else "null_unreconciled"
    return {
        "partition_id": partition_id,
        "planned_cell_count": len(planned_cells),
        "strict_complete_cell_count": len(strict_states),
        "failed_or_unattempted_cell_count": len(planned_cells) - len(strict_states),
        "outcome": outcome,
        "total": total,
        "union": union,
        "over_100_investigation": investigation or "not_triggered_or_union_unavailable",
        "cells": list(states),
    }


def build_assessment(
    modules: AdapterModules,
    plan: Mapping[str, Any],
    preflight: Mapping[str, Any],
    states: Mapping[str, Sequence[Mapping[str, Any]]],
    health: Mapping[str, Any],
    source_requests_attempted: int,
    output_dir: Path,
    *,
    overwrite: bool,
) -> dict[str, Any]:
    partitions = {
        partition_id: partition_assessment(
            modules,
            partition_id,
            raw_plan,
            states[partition_id],
            output_dir,
            overwrite=overwrite,
        )
        for partition_id, raw_plan in plan["partitions"].items()
    }
    source_attempted = source_requests_attempted > 0
    return {
        "schema_version": ASSESSMENT_SCHEMA,
        "pilot": PILOT,
        "source": SOURCE_NAME,
        "kind": "diagnostic_only_not_a_final_search",
        "assessed_at_utc": utc_now(),
        "plan_schema_version": plan["schema_version"],
        "plan_total_cells": plan["total_planned_cells"],
        "browser_preflight": {
            "healthy": preflight.get("healthy"),
            "status": preflight.get("status"),
            "artifact": "browser-preflight.json",
        },
        "source_requests_attempted": source_requests_attempted,
        "source_route_attempted": source_attempted,
        "english_metadata_control": {
            "technical_evidence": "The dated adapter/source note records a successful native English readback after a healthy route.",
            "pilot_application": health.get("status"),
            "condition": "accepted only after this pilot's healthy route followed by exact English route/query readback",
            "full_text_language_screening": "still required for every retained report",
        },
        "window": plan["window"],
        "controls_and_limits": {
            "ordering": "native oldest-first Date route unavailable; strict mode retains source-rendered Relevance and does not client-sort",
            "type": "no document-type selector; degree and level facets were not used because they are not a lossless completed eligible-thesis filter",
            "controlled_vocabulary": "no named controlled vocabulary, descriptor mapping, hierarchy, or explosion setting available",
            "proximity": "quoted named-field ~5 syntax is preserved in both orders; exact token/slop/direction semantics remain unknown",
            "bulk_export": "OATD provides no bulk or OAI-PMH export; only adapter-normalized strict capture is available",
            "wildcard": "none used",
        },
        "partitions": partitions,
        "overall": {
            "all_nine_partitions_planned": list(partitions) == list(PARTITION_FACTORS),
            "all_partition_totals_null_when_any_cell_unreconciled": all(
                item["total"] is None
                for item in partitions.values()
                if item["strict_complete_cell_count"] != item["planned_cell_count"]
            ),
            "no_final_search": True,
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--execute", action="store_true", help="Run bounded source work only when inside a healthy shared browser wrapper.")
    parser.add_argument("--strict-cell-record-cap", type=int, default=100)
    parser.add_argument("--source-request-budget", type=int, default=32)
    parser.add_argument("--overwrite", action="store_true", help="Replace only pilot plan/assessment artifacts; never overwrite adapter cell artifacts.")
    args = parser.parse_args(argv)
    if args.strict_cell_record_cap < 0:
        parser.error("--strict-cell-record-cap must be nonnegative")
    if args.source_request_budget < 0:
        parser.error("--source-request-budget must be nonnegative")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    modules = load_modules()
    output_dir = args.output_dir.expanduser().resolve()
    plan = build_plan(modules)
    no_clobber_json(output_dir / "lossless-cell-plan.json", plan, overwrite=args.overwrite)
    if args.execute:
        preflight = browser_preflight()
        no_clobber_json(output_dir / "browser-preflight.json", preflight, overwrite=args.overwrite)
        if preflight.get("healthy") is True:
            states, health, attempted = execute_plan(
                modules,
                plan,
                output_dir,
                strict_cell_cap=args.strict_cell_record_cap,
                source_request_budget=args.source_request_budget,
                overwrite=args.overwrite,
            )
        else:
            reason = str(preflight.get("status") or "browser_unavailable")
            states = unavailable_partition_states(plan, reason)
            health = {"status": "not_attempted_browser_unavailable"}
            attempted = 0
    else:
        preflight = {
            "schema_version": PREFLIGHT_SCHEMA,
            "checked_at_utc": utc_now(),
            "healthy": None,
            "status": "not_checked_plan_only",
            "source_requests_attempted": 0,
        }
        states = unavailable_partition_states(plan, "plan_only_not_executed")
        health = {"status": "not_applied_plan_only"}
        attempted = 0
    assessment = build_assessment(
        modules,
        plan,
        preflight,
        states,
        health,
        attempted,
        output_dir,
        overwrite=args.overwrite,
    )
    no_clobber_json(output_dir / "execution-assessment.json", assessment, overwrite=args.overwrite)
    print(
        json.dumps(
            {
                "pilot": PILOT,
                "planned_cells": plan["total_planned_cells"],
                "browser_status": preflight.get("status"),
                "source_requests_attempted": attempted,
                "partition_totals": {
                    key: value["total"] for key, value in assessment["partitions"].items()
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
