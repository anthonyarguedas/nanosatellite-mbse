"""Web of Science queries for the current schedule and population wildcards."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
TERM_SNAPSHOT_PATH = Path(__file__).resolve().parents[4] / "source-specific" / "advanced-technologies-aerospace-index" / "scripts" / "atai_pilot007" / "queries.py"
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)

_spec = importlib.util.spec_from_file_location(
    "wos_pilot004_protocol_terms", TERM_SNAPSHOT_PATH
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not load protocol terms from {TERM_SNAPSHOT_PATH}")
_terms = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _terms
_spec.loader.exec_module(_terms)

TERM_SNAPSHOT_SHA256 = hashlib.sha256(TERM_SNAPSHOT_PATH.read_bytes()).hexdigest()
if _terms.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The term snapshot uses a different protocol commit")
if TERM_SNAPSHOT_SHA256 != EXPECTED_TERM_SNAPSHOT_SHA256:
    raise RuntimeError("The reviewed current-schedule term snapshot changed")


def literal_atom(value: str) -> str:
    if '"' in value:
        raise ValueError("A Web of Science literal cannot contain a double quote")
    return f'TS=("{value}")'


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


# Pilot 002 accepted this exact source-specific candidate for A1. Pilot 004
# tests the same replacements in every current main partition.
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


def wildcard_population_atoms() -> tuple[str, ...]:
    atoms: list[str] = []
    covered: set[str] = set()
    for value in _terms.P_TERMS:
        replacement = _REPLACEMENT_BY_FIRST.get(value)
        if replacement is not None:
            atoms.append(literal_atom(replacement["candidate"]))
            covered.update(replacement["replaced_literals"])
            continue
        if value in _REPLACED_LITERALS:
            if value not in covered:
                raise RuntimeError("A wildcard family is out of protocol term order")
            continue
        atoms.append(literal_atom(value))
    if covered != _REPLACED_LITERALS:
        raise RuntimeError("The wildcard candidate did not cover every replacement")
    return tuple(atoms)


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


def with_main_controls(query: str) -> str:
    return f"{query} AND PY=(2011-2026) AND LA=(English)"


P_LITERAL = ORDINARY_BLOCKS["P"]
P_WILDCARD = any_of(*wildcard_population_atoms())
LITERAL_SEMANTIC_SCHEDULE = schedule(P_LITERAL)
WILDCARD_SEMANTIC_SCHEDULE = schedule(P_WILDCARD)
LITERAL_SCHEDULE = {
    key: with_main_controls(value) for key, value in LITERAL_SEMANTIC_SCHEDULE.items()
}
WILDCARD_SCHEDULE = {
    key: with_main_controls(value) for key, value in WILDCARD_SEMANTIC_SCHEDULE.items()
}
TERM_COUNTS = dict(_terms.TERM_COUNTS)
REPLACED_LITERAL_COUNT = len(_REPLACED_LITERALS)

assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert REPLACED_LITERAL_COUNT == 22
assert len(WILDCARD_REPLACEMENTS) == 10
assert len(wildcard_population_atoms()) == 14
assert all("NEAR" not in query.upper() for query in LITERAL_SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all(query.count("*") == 10 and "?" not in query for query in WILDCARD_SCHEDULE.values())
assert all(
    len(LITERAL_SCHEDULE[key]) - len(WILDCARD_SCHEDULE[key]) == 255
    for key in SCHEDULE_IDS
)
