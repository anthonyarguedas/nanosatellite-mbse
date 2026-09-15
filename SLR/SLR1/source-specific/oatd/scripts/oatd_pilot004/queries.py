"""OATD Pilot 004 population query and local schedule annotations.

The declarations are pinned to the schedule at protocol commit
3194156e90497186664260a8e86435e78d2e2aa1. OATD receives only the complete
literal population block. The nine full expressions run locally against every
hydrated population record. No wildcard, proximity operator, pair expansion,
or extra variant is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
TERM_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[4] / "source-specific" / "advanced-technologies-aerospace-index" / "scripts" / "atai_pilot007" / "queries.py"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if file_sha256(TERM_SNAPSHOT_PATH) != EXPECTED_TERM_SNAPSHOT_SHA256:
    raise RuntimeError("The reviewed post-proximity term snapshot changed")
_spec = importlib.util.spec_from_file_location(
    "oatd_pilot004_term_snapshot", TERM_SNAPSHOT_PATH
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load the term snapshot at {TERM_SNAPSHOT_PATH}")
_terms = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _terms
_spec.loader.exec_module(_terms)
if _terms.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The term snapshot uses a different protocol commit")

BLOCK_TERMS: dict[str, tuple[str, ...]] = {
    "P": tuple(_terms.P_TERMS),
    "E_H": tuple(_terms.EH_TERMS),
    "E_F": tuple(_terms.EF_TERMS),
    "M_H": tuple(_terms.MH_TERMS),
    "M_B": tuple(_terms.MB_TERMS),
    "R": tuple(_terms.R_TERMS),
    "G_model_fixed": tuple(_terms.GMODEL_FIXED_TERMS),
    "G_mission": tuple(_terms.GMISSION_TERMS),
    "G_mission_exact": tuple(_terms.GMISSION_EXACT_TERMS),
    "G_structure_fixed": tuple(_terms.GSTRUCTURE_FIXED_TERMS),
    "G_product": tuple(_terms.GPRODUCT_TERMS),
    "G_product_exact": tuple(_terms.GPRODUCT_EXACT_TERMS),
    "G_variation": tuple(_terms.GVARIATION_TERMS),
    "C1_fixed": tuple(_terms.C1_FIXED_TERMS),
    "G_DSL": tuple(_terms.GDSL_TERMS),
    "T_precise": tuple(_terms.TPRECISE_TERMS),
}
TERM_COUNTS = {key: len(values) for key, values in BLOCK_TERMS.items()}


def literal(value: str) -> str:
    if '"' in value:
        raise ValueError("An OATD local literal cannot contain a double quote")
    return f'"{value}"'


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


def ordinary_block(values: Iterable[str]) -> str:
    atoms = tuple(literal(value) for value in values)
    if not atoms:
        raise ValueError("An ordinary block requires at least one term")
    return any_of(*atoms)


ORDINARY_BLOCKS = {key: ordinary_block(values) for key, values in BLOCK_TERMS.items()}
COMPOUND_BLOCKS = {
    "M": any_of(ORDINARY_BLOCKS["M_H"], ORDINARY_BLOCKS["M_B"]),
    "G_model": any_of(
        ORDINARY_BLOCKS["G_model_fixed"],
        ORDINARY_BLOCKS["G_mission_exact"],
        all_of(ORDINARY_BLOCKS["G_mission"], ORDINARY_BLOCKS["M_B"]),
    ),
    "G_structure": any_of(
        ORDINARY_BLOCKS["G_structure_fixed"],
        ORDINARY_BLOCKS["G_product_exact"],
        ORDINARY_BLOCKS["G_variation"],
        all_of(ORDINARY_BLOCKS["G_product"], ORDINARY_BLOCKS["M_B"]),
    ),
    "C1": any_of(ORDINARY_BLOCKS["C1_fixed"], ORDINARY_BLOCKS["G_DSL"]),
}

P_QUERY = ORDINARY_BLOCKS["P"]
LOCAL_SCHEDULE = {
    "A1": all_of(ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["E_H"], ORDINARY_BLOCKS["M_H"]),
    "A2": all_of(ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["E_F"], COMPOUND_BLOCKS["M"]),
    "A3": all_of(ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["E_H"], ORDINARY_BLOCKS["M_B"]),
    "B1": all_of(ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["M_H"]),
    "B2": all_of(ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["M_B"], ORDINARY_BLOCKS["R"]),
    "BG1": all_of(ORDINARY_BLOCKS["P"], COMPOUND_BLOCKS["G_model"]),
    "BG2": all_of(ORDINARY_BLOCKS["P"], COMPOUND_BLOCKS["G_structure"]),
    "BC1": all_of(ORDINARY_BLOCKS["P"], COMPOUND_BLOCKS["C1"]),
    "BT2": all_of(
        ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["M_B"], ORDINARY_BLOCKS["T_precise"]
    ),
}

EXPECTED_P_QUERY = (
    '("CubeSat" OR "CubeSats" OR "cube sat" OR "cube sats" OR "cube-sat" OR '
    '"cube-sats" OR "cube satellite" OR "cube satellites" OR "nanosat" OR '
    '"nanosats" OR "nanosatellite" OR "nanosatellites" OR "nano-sat" OR '
    '"nano-sats" OR "nano sat" OR "nano sats" OR "nano-satellite" OR '
    '"nano-satellites" OR "nano satellite" OR "nano satellites" OR "SmallSat" OR '
    '"SmallSats" OR "small satellite" OR "small satellites" OR "small sat" OR '
    '"small sats")'
)

assert P_QUERY == EXPECTED_P_QUERY
assert tuple(LOCAL_SCHEDULE) == SCHEDULE_IDS
assert TERM_COUNTS == _terms.EXPECTED_COUNTS
assert all(P_QUERY in expression for expression in LOCAL_SCHEDULE.values())
assert all(
    "NEAR" not in expression.upper()
    and "~" not in expression
    and "*" not in expression
    and "?" not in expression
    for expression in LOCAL_SCHEDULE.values()
)
