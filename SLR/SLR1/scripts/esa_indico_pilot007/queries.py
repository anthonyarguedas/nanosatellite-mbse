"""Exact ESA Indico expressions for Pilot 007.

The concept membership and compound Boolean definitions are pinned to the
reviewed post-proximity snapshot at protocol commit
3194156e90497186664260a8e86435e78d2e2aa1. ESA atoms are straight-double-
quoted literals. The current schedule uses no wildcard, proximity operator, or
pair expansion.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CHANGED_FROM_HISTORICAL_PAIR_SCHEDULE = ("BG1", "BG2", "BC1", "BT2")
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
TERM_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1] / "atai_pilot007" / "queries.py"
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if file_sha256(TERM_SNAPSHOT_PATH) != EXPECTED_TERM_SNAPSHOT_SHA256:
    raise RuntimeError("The reviewed post-proximity term snapshot changed")
_spec = importlib.util.spec_from_file_location(
    "esa_indico_pilot007_term_snapshot", TERM_SNAPSHOT_PATH
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
    if not value or '"' in value:
        raise ValueError("An ESA local literal must be nonempty and quote-free")
    return f'"{value}"'


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


def partition_all_of(*expressions: str) -> str:
    """Join top-level factors without a redundant outer pair of parentheses."""
    if not expressions:
        raise ValueError("A partition requires at least one factor")
    return " AND ".join(expressions)


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

SCHEDULE = {
    "A1": partition_all_of(
        ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["E_H"], ORDINARY_BLOCKS["M_H"]
    ),
    "A2": partition_all_of(
        ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["E_F"], COMPOUND_BLOCKS["M"]
    ),
    "A3": partition_all_of(
        ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["E_H"], ORDINARY_BLOCKS["M_B"]
    ),
    "B1": partition_all_of(ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["M_H"]),
    "B2": partition_all_of(
        ORDINARY_BLOCKS["P"], ORDINARY_BLOCKS["M_B"], ORDINARY_BLOCKS["R"]
    ),
    "BG1": partition_all_of(ORDINARY_BLOCKS["P"], COMPOUND_BLOCKS["G_model"]),
    "BG2": partition_all_of(ORDINARY_BLOCKS["P"], COMPOUND_BLOCKS["G_structure"]),
    "BC1": partition_all_of(ORDINARY_BLOCKS["P"], COMPOUND_BLOCKS["C1"]),
    "BT2": partition_all_of(
        ORDINARY_BLOCKS["P"],
        ORDINARY_BLOCKS["M_B"],
        ORDINARY_BLOCKS["T_precise"],
    ),
}

SEMANTIC_FORMS = {
    "A1": "P AND E_H AND M_H",
    "A2": "P AND E_F AND (M_H OR M_B)",
    "A3": "P AND E_H AND M_B",
    "B1": "P AND M_H",
    "B2": "P AND M_B AND R",
    "BG1": "P AND G_model",
    "BG2": "P AND G_structure",
    "BC1": "P AND C1",
    "BT2": "P AND M_B AND T_precise",
}

SOURCE_CONSTRUCTIONS = {
    "A1": "F(P) AND F(E_H) AND F(M_H)",
    "A2": "F(P) AND F(E_F) AND (F(M_H) OR F(M_B))",
    "A3": "F(P) AND F(E_H) AND F(M_B)",
    "B1": "F(P) AND F(M_H)",
    "B2": "F(P) AND F(M_B) AND F(R)",
    "BG1": (
        "F(P) AND (F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B)))"
    ),
    "BG2": (
        "F(P) AND (F(G_structure_fixed) OR F(G_product_exact) OR "
        "F(G_variation) OR (F(G_product) AND F(M_B)))"
    ),
    "BC1": "F(P) AND (F(C1_fixed) OR F(G_DSL))",
    "BT2": "F(P) AND F(M_B) AND F(T_precise)",
}

QUERY_SHA256 = {
    key: hashlib.sha256(value.encode("utf-8")).hexdigest()
    for key, value in SCHEDULE.items()
}
QUERY_CHARACTER_COUNTS = {key: len(value) for key, value in SCHEDULE.items()}
EXPECTED_QUERY_SHA256 = {
    "A1": "51d735e837882a684cc179c8a2a4d255e7c7fd52bc2a82f5a224e52e8a9daebd",
    "A2": "c6961edcc4430dd808cb78534cbd62fba2a1516813ad2c21ff6d69972462bf0c",
    "A3": "767d7c1356fd6e0b54bdf7ecfab8ea7ec14cf847c72c6a53ac0bf998689eade4",
    "B1": "56b814cd675d898b037b395a8aea505ceb12bb4d4bc498ff5ddf48a23e418134",
    "B2": "d5ed8b9575e46788b385d58b9c0ee13bd708342c13056eb72ada432b21057fb2",
    "BG1": "ff7ec78671cc07df476754d2cd472c7ba742702a55fe0597a52c299739a959ec",
    "BG2": "a38a2929dab333cec902b7f0e4381980d561aeb82116fbb6c57efe641303b8fd",
    "BC1": "6653e5d892a49cd3612e0b5d6f90e4af7d151ea70c3ad7408aa06eba7d4c8745",
    "BT2": "6aab427f16bd73dbbc67045cd8eefd58eee5d461e5a67f694b0e2170094497f5",
}

assert tuple(SCHEDULE) == SCHEDULE_IDS
assert tuple(SEMANTIC_FORMS) == SCHEDULE_IDS
assert tuple(SOURCE_CONSTRUCTIONS) == SCHEDULE_IDS
assert TERM_COUNTS == _terms.EXPECTED_COUNTS
assert QUERY_SHA256 == EXPECTED_QUERY_SHA256
assert all(ORDINARY_BLOCKS["P"] in expression for expression in SCHEDULE.values())
assert all(
    marker not in expression.upper()
    for expression in SCHEDULE.values()
    for marker in ("NEAR/", "PRE/", "ONEAR/", " W/")
)
assert all(
    marker not in expression
    for expression in SCHEDULE.values()
    for marker in ("*", "?", "~")
)
