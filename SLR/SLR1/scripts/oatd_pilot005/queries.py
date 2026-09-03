"""Exact five-gate candidate union for OATD Pilot 005."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
BASE_PATH = Path(__file__).resolve().parents[1] / "oatd_pilot004" / "queries.py"
EXPECTED_BASE_SHA256 = (
    "e8d9fc06b30680dc62d7278b52102a3089d6bb07dd9c65c34c899afdfc07ac8f"
)
GATE_IDS = ("G1-MH", "G2-MB", "G3-GMODEL", "G4-GSTRUCTURE", "G5-C1")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if file_sha256(BASE_PATH) != EXPECTED_BASE_SHA256:
    raise RuntimeError("The reviewed OATD Pilot 004 query declarations changed")
_spec = importlib.util.spec_from_file_location("oatd_pilot005_base_queries", BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE_PATH}")
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)
if _base.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The OATD gate queries use a different protocol commit")

P_QUERY = _base.ORDINARY_BLOCKS["P"]
GATE_QUERIES = {
    "G1-MH": _base.all_of(P_QUERY, _base.ORDINARY_BLOCKS["M_H"]),
    "G2-MB": _base.all_of(
        P_QUERY,
        _base.ORDINARY_BLOCKS["M_B"],
        _base.any_of(
            _base.ORDINARY_BLOCKS["E_F"],
            _base.ORDINARY_BLOCKS["E_H"],
            _base.ORDINARY_BLOCKS["R"],
            _base.ORDINARY_BLOCKS["T_precise"],
        ),
    ),
    "G3-GMODEL": _base.all_of(P_QUERY, _base.COMPOUND_BLOCKS["G_model"]),
    "G4-GSTRUCTURE": _base.all_of(P_QUERY, _base.COMPOUND_BLOCKS["G_structure"]),
    "G5-C1": _base.all_of(P_QUERY, _base.COMPOUND_BLOCKS["C1"]),
}

# These branch assignments prove that the five-gate union equals the original
# nine-partition candidate union. A1 and the M_H arm of A2 are subsets of B1.
PARTITION_BRANCH_COVERAGE = {
    "A1": ("G1-MH",),
    "A2": ("G1-MH", "G2-MB"),
    "A3": ("G2-MB",),
    "B1": ("G1-MH",),
    "B2": ("G2-MB",),
    "BG1": ("G3-GMODEL",),
    "BG2": ("G4-GSTRUCTURE",),
    "BC1": ("G5-C1",),
    "BT2": ("G2-MB",),
}
ALGEBRAIC_IDENTITY = (
    "P AND [M_H OR (M_B AND (E_F OR E_H OR R OR T_precise)) OR "
    "G_model OR G_structure OR C1]"
)

assert tuple(GATE_QUERIES) == GATE_IDS
assert tuple(PARTITION_BRANCH_COVERAGE) == _base.SCHEDULE_IDS
assert set().union(*map(set, PARTITION_BRANCH_COVERAGE.values())) == set(GATE_IDS)
assert all(P_QUERY in query for query in GATE_QUERIES.values())
assert all(
    "NEAR" not in query.upper()
    and "~" not in query
    and "*" not in query
    and "?" not in query
    for query in GATE_QUERIES.values()
)
