"""PQDT Global literal and bounded-wildcard queries for Pilot 004.

The ordinary concept membership and compound Boolean definitions are pinned to
protocol commit 3194156e90497186664260a8e86435e78d2e2aa1. The wildcard
families reuse the reviewed ProQuest family declarations from ATAI Pilot 008.
PQDT renders each family only in NOFT. The smallest declared ``[*n]`` bound is
used for every family with a safe common source stem. Singleton terms,
punctuation variants, and families without a safe common stem remain literal.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
QUERY_LIMIT = 50_000
SHARED_DECLARATION_PATH = (
    Path(__file__).resolve().parents[1] / "atai_pilot008" / "queries.py"
)
EXPECTED_SHARED_DECLARATION_SHA256 = (
    "ce39aeee6c901324a16a588fc368a92ac1f3b5bb15a19705dcb2b8aa7c24a348"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if file_sha256(SHARED_DECLARATION_PATH) != EXPECTED_SHARED_DECLARATION_SHA256:
    raise RuntimeError("The reviewed ProQuest wildcard declarations changed")
_spec = importlib.util.spec_from_file_location(
    "pqdt_pilot004_shared_wildcards", SHARED_DECLARATION_PATH
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(
        f"Could not load ProQuest wildcard declarations from {SHARED_DECLARATION_PATH}"
    )
_shared = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _shared
_spec.loader.exec_module(_shared)
if _shared.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The shared declarations use a different protocol commit")

BLOCK_TERMS: dict[str, tuple[str, ...]] = {
    key: tuple(values) for key, values in _shared.BLOCK_TERMS.items()
}
WILDCARD_FAMILIES: dict[str, tuple[Any, ...]] = {
    key: tuple(values) for key, values in _shared.WILDCARD_FAMILIES.items()
}
TERM_COUNTS = {key: len(values) for key, values in BLOCK_TERMS.items()}
FAMILY_RECEIPTS = _shared.family_receipts()
FAMILY_COUNT = sum(len(values) for values in WILDCARD_FAMILIES.values())
REPLACED_TERM_COUNT = sum(
    len(item.terms)
    for families in WILDCARD_FAMILIES.values()
    for item in families
)
WILDCARD_OPERATOR_COUNT_BY_BLOCK = {
    block: sum(item["wildcard_operators"] for item in receipts)
    for block, receipts in FAMILY_RECEIPTS.items()
}


def quote(value: str) -> str:
    if '"' in value:
        raise ValueError("A PQDT literal cannot contain a straight double quote")
    return f'"{value}"'


def literal_atom(value: str) -> str:
    return f"NOFT({quote(value)})"


def wildcard_atom(item: Any) -> str:
    return f"NOFT({item.pattern})"


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


def literal_block(values: Iterable[str]) -> str:
    atoms = tuple(literal_atom(value) for value in values)
    if not atoms:
        raise ValueError("An ordinary block requires at least one term")
    return any_of(*atoms)


def wildcard_block(block: str) -> str:
    values = BLOCK_TERMS[block]
    declarations = WILDCARD_FAMILIES[block]
    by_first = {item.terms[0]: item for item in declarations}
    replaced = {term for item in declarations for term in item.terms}
    atoms: list[str] = []
    covered: set[str] = set()
    for value in values:
        item = by_first.get(value)
        if item is not None:
            atoms.append(wildcard_atom(item))
            covered.update(item.terms)
        elif value in replaced:
            if value not in covered:
                raise RuntimeError(
                    f"A {block} wildcard family is out of source-term order"
                )
        else:
            atoms.append(literal_atom(value))
    if covered != replaced:
        raise RuntimeError(f"The {block} wildcard rendering omitted a declaration")
    return any_of(*atoms)


def compound_blocks(ordinary: dict[str, str]) -> dict[str, str]:
    return {
        "M": any_of(ordinary["M_H"], ordinary["M_B"]),
        "G_model": any_of(
            ordinary["G_model_fixed"],
            ordinary["G_mission_exact"],
            all_of(ordinary["G_mission"], ordinary["M_B"]),
        ),
        "G_structure": any_of(
            ordinary["G_structure_fixed"],
            ordinary["G_product_exact"],
            ordinary["G_variation"],
            all_of(ordinary["G_product"], ordinary["M_B"]),
        ),
        "C1": any_of(ordinary["C1_fixed"], ordinary["G_DSL"]),
    }


def schedule(ordinary: dict[str, str], compound: dict[str, str]) -> dict[str, str]:
    return {
        "A1": all_of(ordinary["P"], ordinary["E_H"], ordinary["M_H"]),
        "A2": all_of(ordinary["P"], ordinary["E_F"], compound["M"]),
        "A3": all_of(ordinary["P"], ordinary["E_H"], ordinary["M_B"]),
        "B1": all_of(ordinary["P"], ordinary["M_H"]),
        "B2": all_of(ordinary["P"], ordinary["M_B"], ordinary["R"]),
        "BG1": all_of(ordinary["P"], compound["G_model"]),
        "BG2": all_of(ordinary["P"], compound["G_structure"]),
        "BC1": all_of(ordinary["P"], compound["C1"]),
        "BT2": all_of(ordinary["P"], ordinary["M_B"], ordinary["T_precise"]),
    }


LITERAL_ORDINARY_BLOCKS = {
    block: literal_block(values) for block, values in BLOCK_TERMS.items()
}
WILDCARD_ORDINARY_BLOCKS = {
    block: wildcard_block(block) for block in BLOCK_TERMS
}
LITERAL_COMPOUND_BLOCKS = compound_blocks(LITERAL_ORDINARY_BLOCKS)
WILDCARD_COMPOUND_BLOCKS = compound_blocks(WILDCARD_ORDINARY_BLOCKS)
LITERAL_SCHEDULE = schedule(LITERAL_ORDINARY_BLOCKS, LITERAL_COMPOUND_BLOCKS)
WILDCARD_SCHEDULE = schedule(WILDCARD_ORDINARY_BLOCKS, WILDCARD_COMPOUND_BLOCKS)

assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert FAMILY_COUNT == 128
assert REPLACED_TERM_COUNT == 292
assert all(
    "NEAR" not in query.upper() and " PRE/" not in query.upper()
    for query in (*LITERAL_SCHEDULE.values(), *WILDCARD_SCHEDULE.values())
)
assert all(
    "*" not in query and "?" not in query
    for query in LITERAL_SCHEDULE.values()
)
assert all(
    "[*" in query and "?" not in query
    for query in WILDCARD_SCHEDULE.values()
)
assert all(
    len(WILDCARD_SCHEDULE[key]) < len(LITERAL_SCHEDULE[key]) < QUERY_LIMIT
    for key in SCHEDULE_IDS
)
