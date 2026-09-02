"""Canonical Scopus post-proximity and population-wildcard queries.

The ordinary concept membership and compound Boolean definitions are pinned to
protocol commit 3194156e90497186664260a8e86435e78d2e2aa1. The wildcard
candidate reproduces the ten deferred Pilot 002 population replacements. Every
other term and Boolean relationship remains literal.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CHANGED_IDS = ("BG1", "BG2", "BC1", "BT2")
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
TERM_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1] / "atai_pilot007" / "queries.py"
)

_spec = importlib.util.spec_from_file_location(
    "scopus_pilot004_term_snapshot", TERM_SNAPSHOT_PATH
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load the term snapshot at {TERM_SNAPSHOT_PATH}")
_terms = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _terms
_spec.loader.exec_module(_terms)

TERM_SNAPSHOT_SHA256 = hashlib.sha256(TERM_SNAPSHOT_PATH.read_bytes()).hexdigest()
if _terms.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The term snapshot uses a different protocol commit")
if TERM_SNAPSHOT_SHA256 != EXPECTED_TERM_SNAPSHOT_SHA256:
    raise RuntimeError("The reviewed post-proximity term snapshot changed")


def literal_atom(value: str) -> str:
    if '"' in value:
        raise ValueError("A Scopus literal cannot contain a straight double quote")
    return f'TITLE-ABS-KEY("{value}")'


def wildcard_atom(value: str) -> str:
    if value.count("*") != 1 or not value.endswith("*"):
        raise ValueError("A Scopus wildcard candidate requires one trailing asterisk")
    return literal_atom(value)


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


def ordinary_block(values: tuple[str, ...]) -> str:
    if not values:
        raise ValueError("An ordinary block requires at least one term")
    return any_of(*(literal_atom(value) for value in values))


WILDCARD_REPLACEMENTS = (
    {
        "candidate": "CubeSat*",
        "replaced_literals": ("CubeSat", "CubeSats"),
    },
    {
        "candidate": "cube sat*",
        "replaced_literals": ("cube sat", "cube sats"),
    },
    {
        "candidate": "cube-sat*",
        "replaced_literals": ("cube-sat", "cube-sats"),
    },
    {
        "candidate": "cube satellite*",
        "replaced_literals": ("cube satellite", "cube satellites"),
    },
    {
        "candidate": "nanosat*",
        "replaced_literals": (
            "nanosat",
            "nanosats",
            "nanosatellite",
            "nanosatellites",
        ),
    },
    {
        "candidate": "nano-sat*",
        "replaced_literals": ("nano-sat", "nano-sats"),
    },
    {
        "candidate": "nano sat*",
        "replaced_literals": ("nano sat", "nano sats"),
    },
    {
        "candidate": "nano-satellite*",
        "replaced_literals": ("nano-satellite", "nano-satellites"),
    },
    {
        "candidate": "nano satellite*",
        "replaced_literals": ("nano satellite", "nano satellites"),
    },
    {
        "candidate": "SmallSat*",
        "replaced_literals": ("SmallSat", "SmallSats"),
    },
)

_REPLACEMENT_BY_FIRST = {
    item["replaced_literals"][0]: item for item in WILDCARD_REPLACEMENTS
}
_REPLACED_LITERALS = {
    value
    for item in WILDCARD_REPLACEMENTS
    for value in item["replaced_literals"]
}


def wildcard_population_block() -> str:
    atoms: list[str] = []
    covered: set[str] = set()
    for value in _terms.P_TERMS:
        replacement = _REPLACEMENT_BY_FIRST.get(value)
        if replacement is not None:
            atoms.append(wildcard_atom(replacement["candidate"]))
            covered.update(replacement["replaced_literals"])
            continue
        if value in _REPLACED_LITERALS:
            if value not in covered:
                raise RuntimeError("A wildcard family is out of source-term order")
            continue
        atoms.append(literal_atom(value))
    if covered != _REPLACED_LITERALS:
        raise RuntimeError("The wildcard candidate did not cover every declaration")
    return any_of(*atoms)


ORDINARY_BLOCKS = {
    "P": ordinary_block(_terms.P_TERMS),
    "E_H": ordinary_block(_terms.EH_TERMS),
    "E_F": ordinary_block(_terms.EF_TERMS),
    "M_H": ordinary_block(_terms.MH_TERMS),
    "M_B": ordinary_block(_terms.MB_TERMS),
    "R": ordinary_block(_terms.R_TERMS),
    "G_model_fixed": ordinary_block(_terms.GMODEL_FIXED_TERMS),
    "G_mission": ordinary_block(_terms.GMISSION_TERMS),
    "G_mission_exact": ordinary_block(_terms.GMISSION_EXACT_TERMS),
    "G_structure_fixed": ordinary_block(_terms.GSTRUCTURE_FIXED_TERMS),
    "G_product": ordinary_block(_terms.GPRODUCT_TERMS),
    "G_product_exact": ordinary_block(_terms.GPRODUCT_EXACT_TERMS),
    "G_variation": ordinary_block(_terms.GVARIATION_TERMS),
    "C1_fixed": ordinary_block(_terms.C1_FIXED_TERMS),
    "G_DSL": ordinary_block(_terms.GDSL_TERMS),
    "T_precise": ordinary_block(_terms.TPRECISE_TERMS),
}

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


def schedule(population: str) -> dict[str, str]:
    return {
        "A1": all_of(population, ORDINARY_BLOCKS["E_H"], ORDINARY_BLOCKS["M_H"]),
        "A2": all_of(population, ORDINARY_BLOCKS["E_F"], COMPOUND_BLOCKS["M"]),
        "A3": all_of(population, ORDINARY_BLOCKS["E_H"], ORDINARY_BLOCKS["M_B"]),
        "B1": all_of(population, ORDINARY_BLOCKS["M_H"]),
        "B2": all_of(population, ORDINARY_BLOCKS["M_B"], ORDINARY_BLOCKS["R"]),
        "BG1": all_of(population, COMPOUND_BLOCKS["G_model"]),
        "BG2": all_of(population, COMPOUND_BLOCKS["G_structure"]),
        "BC1": all_of(population, COMPOUND_BLOCKS["C1"]),
        "BT2": all_of(
            population,
            ORDINARY_BLOCKS["M_B"],
            ORDINARY_BLOCKS["T_precise"],
        ),
    }


P_LITERAL = ORDINARY_BLOCKS["P"]
P_WILDCARD = wildcard_population_block()
LITERAL_SCHEDULE = schedule(P_LITERAL)
WILDCARD_SCHEDULE = schedule(P_WILDCARD)
TERM_COUNTS = dict(_terms.TERM_COUNTS)
REPLACED_LITERAL_COUNT = len(_REPLACED_LITERALS)

assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert REPLACED_LITERAL_COUNT == 22
assert len(WILDCARD_REPLACEMENTS) == 10
assert all(" W/" not in query.upper() and " PRE/" not in query.upper() for query in LITERAL_SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all(query.count("*") == 10 and "?" not in query for query in WILDCARD_SCHEDULE.values())
assert all(len(LITERAL_SCHEDULE[key]) - len(WILDCARD_SCHEDULE[key]) == 375 for key in SCHEDULE_IDS)
