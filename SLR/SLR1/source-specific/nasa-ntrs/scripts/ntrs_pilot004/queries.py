"""Canonical NASA NTRS literal and wildcard queries for Pilot 004.

The concept membership and compound Boolean definitions are pinned to protocol
commit 3194156e90497186664260a8e86435e78d2e2aa1. The wildcard candidate uses
only standalone NTRS trailing-prefix terms. Every phrase, acronym, punctuation
form, isolated term, and Boolean relationship otherwise remains literal.
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
TERM_SNAPSHOT_PATH = Path(__file__).resolve().parents[4] / "source-specific" / "advanced-technologies-aerospace-index" / "scripts" / "atai_pilot007" / "queries.py"

_spec = importlib.util.spec_from_file_location(
    "ntrs_pilot004_term_snapshot", TERM_SNAPSHOT_PATH
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

TERM_BLOCKS: dict[str, tuple[str, ...]] = {
    "P": _terms.P_TERMS,
    "E_H": _terms.EH_TERMS,
    "E_F": _terms.EF_TERMS,
    "M_H": _terms.MH_TERMS,
    "M_B": _terms.MB_TERMS,
    "R": _terms.R_TERMS,
    "G_model_fixed": _terms.GMODEL_FIXED_TERMS,
    "G_mission": _terms.GMISSION_TERMS,
    "G_mission_exact": _terms.GMISSION_EXACT_TERMS,
    "G_structure_fixed": _terms.GSTRUCTURE_FIXED_TERMS,
    "G_product": _terms.GPRODUCT_TERMS,
    "G_product_exact": _terms.GPRODUCT_EXACT_TERMS,
    "G_variation": _terms.GVARIATION_TERMS,
    "C1_fixed": _terms.C1_FIXED_TERMS,
    "G_DSL": _terms.GDSL_TERMS,
    "T_precise": _terms.TPRECISE_TERMS,
}

# Each tuple is (source wildcard atom, replaced protocol literals). These are
# all useful standalone-token morphology families. Phrase wildcards stay out
# because NTRS does not document that quotes retain exact phrase semantics when
# one quoted term carries `*`. Acronyms stay literal to preserve standalone
# lexical matching. The broad `batter*` root stays out because it crosses into
# an unrelated lexeme.
WILDCARD_REPLACEMENTS: dict[
    str, tuple[tuple[str, tuple[str, ...]], ...]
] = {
    "P": (
        ("CubeSat*", ("CubeSat", "CubeSats")),
        ("nanosat*", ("nanosat", "nanosats", "nanosatellite", "nanosatellites")),
        ("SmallSat*", ("SmallSat", "SmallSats")),
    ),
    "E_H": (),
    "E_F": (),
    "M_H": (),
    "M_B": (),
    "R": (
        ("requirement*", ("requirement", "requirements")),
        ("function*", ("function", "functions", "functional")),
        ("behavior*", ("behavior", "behaviors", "behavioral")),
        ("behaviour*", ("behaviour", "behaviours", "behavioural")),
        ("architectur*", ("architecture", "architectures", "architectural")),
        ("interface*", ("interface", "interfaces")),
        ("trace*", ("traceability", "trace", "traceable", "traced")),
        ("allocat*", ("allocation", "allocate", "allocated")),
        ("constraint*", ("constraint", "constraints")),
        ("parametric*", ("parametric", "parametrics")),
        ("analys*", ("analysis", "analyses")),
        ("design*", ("design", "designs", "designed", "designing")),
        ("decision*", ("decision", "decisions")),
        ("tradeoff*", ("tradeoff", "tradeoffs")),
        ("verif*", ("verification", "verifications", "verify", "verifies", "verified", "verifying")),
        ("validat*", ("validation", "validations", "validate", "validates", "validated", "validating")),
    ),
    "G_model_fixed": (),
    "G_mission": (),
    "G_mission_exact": (),
    "G_structure_fixed": (
        ("metamodel*", ("metamodel", "metamodels")),
    ),
    "G_product": (),
    "G_product_exact": (),
    "G_variation": (),
    "C1_fixed": (),
    "G_DSL": (),
    "T_precise": (
        ("tailor*", ("tailor", "tailors", "tailored", "tailoring")),
        ("customiz*", ("customize", "customizes", "customized", "customizing", "customization")),
        ("customis*", ("customise", "customises", "customised", "customising", "customisation")),
        ("parameteriz*", ("parameterize", "parameterizes", "parameterized", "parameterizing", "parameterization")),
        ("parameteris*", ("parameterise", "parameterises", "parameterised", "parameterising", "parameterisation")),
        ("instantiat*", ("instantiate", "instantiates", "instantiated", "instantiating", "instantiation")),
    ),
}


def literal_atom(value: str) -> str:
    if '"' in value or "*" in value:
        raise ValueError("An NTRS literal must not contain quote or wildcard syntax")
    return f'"{value}"'


def wildcard_atom(value: str) -> str:
    root = value[:-1] if value.endswith("*") else ""
    if value.count("*") != 1 or len(root) < 4 or not root.isalnum():
        raise ValueError("An NTRS wildcard must be one standalone trailing prefix")
    return value


def any_of(expressions: Iterable[str]) -> str:
    values = tuple(expressions)
    if not values:
        raise ValueError("OR requires at least one expression")
    return "(" + " | ".join(values) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " + ".join(expressions) + ")"


def literal_block(block_id: str) -> str:
    return any_of(literal_atom(value) for value in TERM_BLOCKS[block_id])


def wildcard_block(block_id: str) -> str:
    terms = TERM_BLOCKS[block_id]
    replacements = WILDCARD_REPLACEMENTS[block_id]
    by_first_index: dict[int, str] = {}
    replaced: set[str] = set()
    for candidate, values in replacements:
        wildcard_atom(candidate)
        if not values or any(value not in terms for value in values):
            raise RuntimeError(f"Invalid wildcard replacement in {block_id}: {candidate}")
        if replaced.intersection(values):
            raise RuntimeError(f"Overlapping wildcard replacement in {block_id}: {candidate}")
        first_index = min(terms.index(value) for value in values)
        if first_index in by_first_index:
            raise RuntimeError(f"Wildcard insertion collision in {block_id}")
        by_first_index[first_index] = candidate
        replaced.update(values)
    atoms: list[str] = []
    for index, value in enumerate(terms):
        if index in by_first_index:
            atoms.append(by_first_index[index])
        if value not in replaced:
            atoms.append(literal_atom(value))
    return any_of(atoms)


def blocks(variant: str) -> dict[str, str]:
    if variant == "literal":
        ordinary = {key: literal_block(key) for key in TERM_BLOCKS}
    elif variant == "wildcard":
        ordinary = {key: wildcard_block(key) for key in TERM_BLOCKS}
    else:
        raise ValueError(f"Unknown NTRS query variant: {variant}")
    return {
        **ordinary,
        "M": any_of((ordinary["M_H"], ordinary["M_B"])),
        "G_model": any_of(
            (
                ordinary["G_model_fixed"],
                ordinary["G_mission_exact"],
                all_of(ordinary["G_mission"], ordinary["M_B"]),
            )
        ),
        "G_structure": any_of(
            (
                ordinary["G_structure_fixed"],
                ordinary["G_product_exact"],
                ordinary["G_variation"],
                all_of(ordinary["G_product"], ordinary["M_B"]),
            )
        ),
        "C1": any_of((ordinary["C1_fixed"], ordinary["G_DSL"])),
    }


def schedule(variant: str) -> dict[str, str]:
    value = blocks(variant)
    return {
        "A1": all_of(value["P"], value["E_H"], value["M_H"]),
        "A2": all_of(value["P"], value["E_F"], value["M"]),
        "A3": all_of(value["P"], value["E_H"], value["M_B"]),
        "B1": all_of(value["P"], value["M_H"]),
        "B2": all_of(value["P"], value["M_B"], value["R"]),
        "BG1": all_of(value["P"], value["G_model"]),
        "BG2": all_of(value["P"], value["G_structure"]),
        "BC1": all_of(value["P"], value["C1"]),
        "BT2": all_of(value["P"], value["M_B"], value["T_precise"]),
    }


LITERAL_BLOCKS = blocks("literal")
WILDCARD_BLOCKS = blocks("wildcard")
LITERAL_SCHEDULE = schedule("literal")
WILDCARD_SCHEDULE = schedule("wildcard")
WILDCARD_ATOM_COUNT = sum(len(values) for values in WILDCARD_REPLACEMENTS.values())
REPLACED_LITERAL_COUNT = sum(
    len(literals)
    for replacements in WILDCARD_REPLACEMENTS.values()
    for _candidate, literals in replacements
)

assert tuple(TERM_BLOCKS) == tuple(_terms.ORDINARY_BLOCKS)
assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert set(WILDCARD_REPLACEMENTS) == set(TERM_BLOCKS)
assert WILDCARD_ATOM_COUNT == 26
assert REPLACED_LITERAL_COUNT == 88
assert all("~" not in query and "NEAR" not in query.upper() for query in LITERAL_SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all("*" in query and "~" not in query for query in WILDCARD_SCHEDULE.values())
assert all(len(WILDCARD_SCHEDULE[key]) <= len(LITERAL_SCHEDULE[key]) for key in SCHEDULE_IDS)
