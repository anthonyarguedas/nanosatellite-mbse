"""Canonical Engineering Village A1 wildcard comparison for Pilot 005.

The literal query reproduces the post-proximity concept snapshot at protocol
commit 3194156e90497186664260a8e86435e78d2e2aa1. The candidate changes only
three single-token population families to documented trailing ``*`` forms.
Every other term, phrase, punctuation form, field, and Boolean relationship
stays literal.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
TERM_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1] / "atai_pilot007" / "queries.py"
)

_spec = importlib.util.spec_from_file_location(
    "compendex_pilot005_term_snapshot", TERM_SNAPSHOT_PATH
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

LANGUAGE_CLAUSE = "(English WN LA)"


def literal_atom(value: str) -> str:
    return f'(\"{value}\" WN ALL)'


def wildcard_atom(value: str) -> str:
    if not value.endswith("*") or value.count("*") != 1:
        raise ValueError("A candidate atom requires one trailing wildcard")
    return f"({value} WN ALL)"


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


def literal_block(values: tuple[str, ...]) -> str:
    return any_of(*(literal_atom(value) for value in values))


WILDCARD_REPLACEMENTS = (
    {
        "candidate": "CubeSat*",
        "replaced_literals": ("CubeSat", "CubeSats"),
        "possible_extra_completions": (
            "CubeSatellite",
            "CubeSatellites",
            "other tokens beginning with CubeSat",
        ),
    },
    {
        "candidate": "nanosat*",
        "replaced_literals": (
            "nanosat",
            "nanosats",
            "nanosatellite",
            "nanosatellites",
        ),
        "possible_extra_completions": (
            "other tokens beginning with nanosat",
        ),
    },
    {
        "candidate": "SmallSat*",
        "replaced_literals": ("SmallSat", "SmallSats"),
        "possible_extra_completions": (
            "SmallSatellite",
            "SmallSatellites",
            "other tokens beginning with SmallSat",
        ),
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


def population_candidate_block() -> str:
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
                raise RuntimeError("A wildcard family is out of source-term order")
            continue
        atoms.append(literal_atom(value))
    if seen != _REPLACED_LITERALS:
        raise RuntimeError("The wildcard candidate did not cover its declared literals")
    return any_of(*atoms)


P_LITERAL = literal_block(_terms.P_TERMS)
P_WILDCARD = population_candidate_block()
E_H = literal_block(_terms.EH_TERMS)
M_H = literal_block(_terms.MH_TERMS)

A1_LITERAL_CORE = all_of(P_LITERAL, E_H, M_H)
A1_WILDCARD_CORE = all_of(P_WILDCARD, E_H, M_H)
A1_LITERAL = all_of(A1_LITERAL_CORE, LANGUAGE_CLAUSE)
A1_WILDCARD = all_of(A1_WILDCARD_CORE, LANGUAGE_CLAUSE)

EVENT_QUERIES = {
    "literal-A1": A1_LITERAL,
    "wildcard-A1": A1_WILDCARD,
}

TERM_COUNTS = dict(_terms.TERM_COUNTS)
EXPECTED_TERM_COUNTS = dict(_terms.EXPECTED_COUNTS)
REPLACED_LITERAL_COUNT = sum(
    len(item["replaced_literals"]) for item in WILDCARD_REPLACEMENTS
)
CHARACTER_REDUCTION = len(A1_LITERAL) - len(A1_WILDCARD)

assert TERM_COUNTS == EXPECTED_TERM_COUNTS
assert tuple(_terms.P_TERMS) == tuple(dict.fromkeys(_terms.P_TERMS))
assert len(_terms.P_TERMS) == TERM_COUNTS["P"]
assert "*" not in A1_LITERAL and "?" not in A1_LITERAL
assert A1_WILDCARD.count("*") == len(WILDCARD_REPLACEMENTS)
assert "?" not in A1_WILDCARD
assert "NEAR" not in A1_LITERAL.upper()
assert "NEAR" not in A1_WILDCARD.upper()
assert REPLACED_LITERAL_COUNT == 8
assert CHARACTER_REDUCTION == 130
assert len(P_LITERAL.split(" OR ")) == len(_terms.P_TERMS)
assert len(P_WILDCARD.split(" OR ")) == len(_terms.P_TERMS) - 5
