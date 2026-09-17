"""Focused offline checks for the OATD Pilot 005 gate declarations."""

from __future__ import annotations

import hashlib

import queries


def test_gate_order_and_population_factor() -> None:
    assert tuple(queries.GATE_QUERIES) == queries.GATE_IDS
    assert all(queries.P_QUERY in value for value in queries.GATE_QUERIES.values())


def test_every_original_partition_is_covered() -> None:
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


def test_gate_queries_retain_literal_schedule_policy() -> None:
    for value in queries.GATE_QUERIES.values():
        assert "NEAR" not in value.upper()
        assert "~" not in value
        assert "*" not in value
        assert "?" not in value
        assert value.count("(") == value.count(")")
        assert len(hashlib.sha256(value.encode("utf-8")).hexdigest()) == 64
