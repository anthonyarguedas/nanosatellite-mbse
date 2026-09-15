"""Lossless split of the OATD Pilot 005 combined M_B gate."""

from __future__ import annotations

import queries

PROTOCOL_COMMIT = queries.PROTOCOL_COMMIT
SPLIT_GATE_IDS = (
    "G2A-MB-EF",
    "G2B-MB-EH",
    "G2C-MB-R",
    "G2D-MB-T",
    "G3-GMODEL",
    "G4-GSTRUCTURE",
    "G5-C1",
)

P_QUERY = queries.P_QUERY
M_B = queries._base.ORDINARY_BLOCKS["M_B"]
SPLIT_GATE_QUERIES = {
    "G2A-MB-EF": queries._base.all_of(
        P_QUERY, M_B, queries._base.ORDINARY_BLOCKS["E_F"]
    ),
    "G2B-MB-EH": queries._base.all_of(
        P_QUERY, M_B, queries._base.ORDINARY_BLOCKS["E_H"]
    ),
    "G2C-MB-R": queries._base.all_of(P_QUERY, M_B, queries._base.ORDINARY_BLOCKS["R"]),
    "G2D-MB-T": queries._base.all_of(
        P_QUERY, M_B, queries._base.ORDINARY_BLOCKS["T_precise"]
    ),
    "G3-GMODEL": queries.GATE_QUERIES["G3-GMODEL"],
    "G4-GSTRUCTURE": queries.GATE_QUERIES["G4-GSTRUCTURE"],
    "G5-C1": queries.GATE_QUERIES["G5-C1"],
}

PARTITION_BRANCH_COVERAGE = {
    "A1": ("G1-MH",),
    "A2": ("G1-MH", "G2A-MB-EF"),
    "A3": ("G2B-MB-EH",),
    "B1": ("G1-MH",),
    "B2": ("G2C-MB-R",),
    "BG1": ("G3-GMODEL",),
    "BG2": ("G4-GSTRUCTURE",),
    "BC1": ("G5-C1",),
    "BT2": ("G2D-MB-T",),
}
ALGEBRAIC_IDENTITY = (
    "(P AND M_H) OR (P AND M_B AND E_F) OR (P AND M_B AND E_H) OR "
    "(P AND M_B AND R) OR (P AND M_B AND T_precise) OR "
    "(P AND G_model) OR (P AND G_structure) OR (P AND C1)"
)

assert tuple(SPLIT_GATE_QUERIES) == SPLIT_GATE_IDS
assert tuple(PARTITION_BRANCH_COVERAGE) == queries._base.SCHEDULE_IDS
assert set().union(*map(set, PARTITION_BRANCH_COVERAGE.values())) == {
    "G1-MH",
    *SPLIT_GATE_IDS,
}
assert all(P_QUERY in query for query in SPLIT_GATE_QUERIES.values())
assert all(
    "NEAR" not in query.upper()
    and "~" not in query
    and "*" not in query
    and "?" not in query
    for query in SPLIT_GATE_QUERIES.values()
)
