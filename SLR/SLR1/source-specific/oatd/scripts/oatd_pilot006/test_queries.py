"""Offline declaration checks for OATD Pilot 006."""

from __future__ import annotations

import queries


def test_gate_order_and_counts() -> None:
    assert tuple(queries.GATE_QUERIES) == queries.GATE_IDS
    assert tuple(queries.EXPECTED_PILOT005_COUNTS) == queries.GATE_IDS
    assert sum(queries.EXPECTED_PILOT005_COUNTS.values()) == 34


def test_exact_union_branch_coverage() -> None:
    assert tuple(queries.PARTITION_BRANCH_COVERAGE) == (
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
    assert set().union(
        *(set(value) for value in queries.PARTITION_BRANCH_COVERAGE.values())
    ) == set(queries.GATE_IDS)


def test_every_gate_keeps_population_and_literal_policy() -> None:
    for query in queries.GATE_QUERIES.values():
        assert queries._base.P_QUERY in query
        assert "NEAR" not in query.upper()
        assert "~" not in query
        assert "*" not in query
        assert "?" not in query
        assert query.count("(") == query.count(")")
