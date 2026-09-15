"""Current Compendex readiness queries for Pilot 006.

The concept membership and Boolean definitions come from
protocol-discovery-and-appraisal.md at protocol commit
3194156e90497186664260a8e86435e78d2e2aa1. Every ordinary term is one quoted
Engineering Village ALL-field atom. The approved Compendex population
translation replaces exactly three literal families with trailing wildcards.
No proximity operator or pair expansion is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
TERM_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[4] / "source-specific" / "advanced-technologies-aerospace-index" / "scripts" / "atai_pilot007" / "queries.py"
)
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CHANGED_IDS = ("BG1", "BG2", "BC1", "BT2")
LANGUAGE_CLAUSE = "(English WN LA)"
APPROVED_A1_QUERY_SHA256 = (
    "b4596970a6e23c039881b8cf5eed6505bd2f3a8212f07626aef130734c3c3064"
)

_spec = importlib.util.spec_from_file_location(
    "compendex_pilot006_term_snapshot", TERM_SNAPSHOT_PATH
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


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def literal_atom(value: str) -> str:
    return f'("{value}" WN ALL)'


def wildcard_atom(value: str) -> str:
    if not value.endswith("*") or value.count("*") != 1:
        raise ValueError("An approved wildcard atom requires one trailing asterisk")
    return f"({value} WN ALL)"


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
        "candidate": "nanosat*",
        "replaced_literals": (
            "nanosat",
            "nanosats",
            "nanosatellite",
            "nanosatellites",
        ),
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
    value for item in WILDCARD_REPLACEMENTS for value in item["replaced_literals"]
}


def approved_population_block() -> str:
    atoms: list[str] = []
    seen: set[str] = set()
    for value in _terms.P_TERMS:
        replacement = _REPLACEMENT_BY_FIRST.get(value)
        if replacement is not None:
            atoms.append(wildcard_atom(replacement["candidate"]))
            seen.update(replacement["replaced_literals"])
            continue
        if value in _REPLACED_LITERALS:
            if value not in seen:
                raise RuntimeError("An approved wildcard family is out of term order")
            continue
        atoms.append(literal_atom(value))
    if seen != _REPLACED_LITERALS:
        raise RuntimeError(
            "The approved wildcard map did not cover its literal families"
        )
    return any_of(*atoms)


ORDINARY_BLOCKS = {
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

BLOCKS = {
    "P": approved_population_block(),
    **ORDINARY_BLOCKS,
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

CORE_SCHEDULE = {
    "A1": all_of(BLOCKS["P"], BLOCKS["E_H"], BLOCKS["M_H"]),
    "A2": all_of(BLOCKS["P"], BLOCKS["E_F"], BLOCKS["M"]),
    "A3": all_of(BLOCKS["P"], BLOCKS["E_H"], BLOCKS["M_B"]),
    "B1": all_of(BLOCKS["P"], BLOCKS["M_H"]),
    "B2": all_of(BLOCKS["P"], BLOCKS["M_B"], BLOCKS["R"]),
    "BG1": all_of(BLOCKS["P"], BLOCKS["G_model"]),
    "BG2": all_of(BLOCKS["P"], BLOCKS["G_structure"]),
    "BC1": all_of(BLOCKS["P"], BLOCKS["C1"]),
    "BT2": all_of(BLOCKS["P"], BLOCKS["M_B"], BLOCKS["T_precise"]),
}
EVENT_QUERIES = {
    partition: all_of(CORE_SCHEDULE[partition], LANGUAGE_CLAUSE)
    for partition in SCHEDULE_IDS
}

BOOLEAN_FORMS = {
    "A1": "F(P) AND F(E_H) AND F(M_H)",
    "A2": "F(P) AND F(E_F) AND (F(M_H) OR F(M_B))",
    "A3": "F(P) AND F(E_H) AND F(M_B)",
    "B1": "F(P) AND F(M_H)",
    "B2": "F(P) AND F(M_B) AND F(R)",
    "BG1": "F(P) AND F(G_model)",
    "BG2": "F(P) AND F(G_structure)",
    "BC1": "F(P) AND F(C1)",
    "BT2": "F(P) AND F(M_B) AND F(T_precise)",
}
COMPOUND_DEFINITIONS = {
    "F(G_model)": (
        "F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))"
    ),
    "F(G_structure)": (
        "F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR "
        "(F(G_product) AND F(M_B))"
    ),
    "F(C1)": "F(C1_fixed) OR F(G_DSL)",
    "F(T_precise)": "ordinary union of all 32 precise tailoring terms",
}

TERM_COUNTS = dict(_terms.TERM_COUNTS)
EXPECTED_TERM_COUNTS = dict(_terms.EXPECTED_COUNTS)
REPLACED_LITERAL_COUNT = sum(
    len(item["replaced_literals"]) for item in WILDCARD_REPLACEMENTS
)
PROXIMITY_OPERATOR_RE = re.compile(r"\b(?:ONEAR|NEAR)(?:/\d+)?\b", re.IGNORECASE)

assert TERM_COUNTS == EXPECTED_TERM_COUNTS
assert tuple(_terms.SCHEDULE_IDS) == SCHEDULE_IDS
assert tuple(CORE_SCHEDULE) == SCHEDULE_IDS
assert tuple(EVENT_QUERIES) == SCHEDULE_IDS
assert REPLACED_LITERAL_COUNT == 8
assert BLOCKS["P"].count("*") == 3
assert len(BLOCKS["P"].split(" OR ")) == TERM_COUNTS["P"] - 5
assert all(query.count("*") == 3 for query in EVENT_QUERIES.values())
assert all("?" not in query for query in EVENT_QUERIES.values())
assert all(
    PROXIMITY_OPERATOR_RE.search(query) is None for query in EVENT_QUERIES.values()
)
assert all(query.count(LANGUAGE_CLAUSE) == 1 for query in EVENT_QUERIES.values())
assert digest_text(EVENT_QUERIES["A1"]) == APPROVED_A1_QUERY_SHA256
