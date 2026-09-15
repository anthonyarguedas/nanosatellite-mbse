"""Exact eight-gate declarations for OATD Pilot 006."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
BASE_PATH = Path(__file__).resolve().parents[1] / "oatd_pilot005/queries.py"
EXPECTED_BASE_SHA256 = (
    "4459898b5199d00ae1a212ebb5570c737f57d397926afe5b74127c7f68b663d1"
)
GATE_IDS = (
    "G1-MH",
    "G2A-MB-EF",
    "G2B-MB-EH",
    "G2C-MB-R",
    "G2D-MB-T",
    "G3-GMODEL",
    "G4-GSTRUCTURE",
    "G5-C1",
)
EXPECTED_PILOT005_COUNTS = {
    "G1-MH": 16,
    "G2A-MB-EF": 2,
    "G2B-MB-EH": 2,
    "G2C-MB-R": 10,
    "G2D-MB-T": 0,
    "G3-GMODEL": 0,
    "G4-GSTRUCTURE": 3,
    "G5-C1": 1,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(BASE_PATH) != EXPECTED_BASE_SHA256:
    raise RuntimeError("The reviewed OATD Pilot 005 gate declarations changed")
_spec = importlib.util.spec_from_file_location("oatd_pilot006_base_queries", BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE_PATH}")
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)
if _base.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The OATD Pilot 006 gates use a different protocol commit")

_blocks = _base._base
P_QUERY = _base.P_QUERY
M_B = _blocks.ORDINARY_BLOCKS["M_B"]
GATE_QUERIES = {
    "G1-MH": _base.GATE_QUERIES["G1-MH"],
    "G2A-MB-EF": _blocks.all_of(P_QUERY, M_B, _blocks.ORDINARY_BLOCKS["E_F"]),
    "G2B-MB-EH": _blocks.all_of(P_QUERY, M_B, _blocks.ORDINARY_BLOCKS["E_H"]),
    "G2C-MB-R": _blocks.all_of(P_QUERY, M_B, _blocks.ORDINARY_BLOCKS["R"]),
    "G2D-MB-T": _blocks.all_of(P_QUERY, M_B, _blocks.ORDINARY_BLOCKS["T_precise"]),
    "G3-GMODEL": _base.GATE_QUERIES["G3-GMODEL"],
    "G4-GSTRUCTURE": _base.GATE_QUERIES["G4-GSTRUCTURE"],
    "G5-C1": _base.GATE_QUERIES["G5-C1"],
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

assert tuple(GATE_QUERIES) == GATE_IDS
assert tuple(EXPECTED_PILOT005_COUNTS) == GATE_IDS
assert tuple(PARTITION_BRANCH_COVERAGE) == _blocks.SCHEDULE_IDS
assert all(P_QUERY in query for query in GATE_QUERIES.values())
assert set().union(*map(set, PARTITION_BRANCH_COVERAGE.values())) == set(GATE_IDS)
