"""Offline checks for OATD Pilot 007 declarations and checkpoint shape."""

from __future__ import annotations

from pathlib import Path

import queries
import run_pilot


def test_gate_declarations_are_unchanged() -> None:
    assert tuple(queries.GATE_QUERIES) == queries.GATE_IDS
    assert tuple(queries.EXPECTED_COUNTS) == queries.GATE_IDS
    assert sum(queries.EXPECTED_COUNTS.values()) == 34


def test_checkpoint_shape_is_path_free() -> None:
    adapter = run_pilot.load_adapter()
    checkpoint = run_pilot.new_checkpoint(
        "a" * 64,
        ["handle:example/1"],
        "b" * 64,
    )
    assert checkpoint["completed_ids"] == []
    assert checkpoint["records"] == []
    assert adapter._checkpoint_has_unsafe_content(checkpoint) is False


def test_local_plan_accepts_pinned_schedule() -> None:
    adapter = run_pilot.load_adapter()
    path = Path(
        "SLR/SLR1/source-specific/oatd/pilots/004/searches/local-matching-plan.json"
    )
    plan = adapter.load_local_matching_plan(path)
    assert tuple(expression.expression_id for expression in plan.expressions) == (
        "A1",
        "A2",
        "A3",
        "B1",
        "B2",
        "BG1",
        "BG2",
        "BC1",
        "BT2",
    )
