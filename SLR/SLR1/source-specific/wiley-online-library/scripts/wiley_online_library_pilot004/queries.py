"""Canonical Wiley queries for the current schedule and wildcard comparison."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
SOURCE_QUERY_LIMIT = 2700

# Reuse the protocol-pinned term tuple transcription already validated by the
# post-proximity AIAA pilot. Rendering below is Wiley-specific.
_CANONICAL_PATH = Path(__file__).resolve().parents[4] / "source-specific" / "aiaa-arc" / "scripts" / "aiaa_arc_pilot005" / "queries.py"
_spec = importlib.util.spec_from_file_location("wiley_p004_protocol_terms", _CANONICAL_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load canonical terms from {_CANONICAL_PATH}")
_terms = importlib.util.module_from_spec(_spec)
sys.modules.setdefault(_spec.name, _terms)
_spec.loader.exec_module(_terms)
if _terms.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("Canonical term transcription uses a different protocol commit")

P_TERMS = _terms.P_TERMS
EH_TERMS = _terms.EH_TERMS
EF_TERMS = _terms.EF_TERMS
MH_TERMS = _terms.MH_TERMS
MB_TERMS = _terms.MB_TERMS
R_TERMS = _terms.R_TERMS
GMODEL_FIXED_TERMS = _terms.GMODEL_FIXED_TERMS
GMISSION_TERMS = _terms.GMISSION_TERMS
GMISSION_EXACT_TERMS = _terms.GMISSION_EXACT_TERMS
GSTRUCTURE_FIXED_TERMS = _terms.GSTRUCTURE_FIXED_TERMS
GPRODUCT_TERMS = _terms.GPRODUCT_TERMS
GPRODUCT_EXACT_TERMS = _terms.GPRODUCT_EXACT_TERMS
GVARIATION_TERMS = _terms.GVARIATION_TERMS
C1_FIXED_TERMS = _terms.C1_FIXED_TERMS
GDSL_TERMS = _terms.GDSL_TERMS
TPRECISE_TERMS = _terms.TPRECISE_TERMS

WILDCARD_REPLACEMENTS = (
    (("CubeSat", "CubeSats"), "CubeSat*"),
    (("nanosat", "nanosats", "nanosatellite", "nanosatellites"), "nanosat*"),
    (("SmallSat", "SmallSats"), "SmallSat*"),
)


def literal(value: str) -> str:
    return f'"{value}"'


def block_from_atoms(atoms: Iterable[str]) -> str:
    values = tuple(atoms)
    if not values:
        raise ValueError("A Wiley block requires at least one atom")
    return "(" + " OR ".join(values) + ")"


def ordinary_block(terms: Iterable[str]) -> str:
    return block_from_atoms(literal(term) for term in terms)


def any_of(*expressions: str) -> str:
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    # Top-level partition conjunctions deliberately have no redundant outer
    # parentheses. Each factor is already parenthesized, matching Pilot 003.
    return " AND ".join(expressions)


def wildcard_population_atoms() -> tuple[str, ...]:
    replacement_by_first = {terms[0]: (terms, atom) for terms, atom in WILDCARD_REPLACEMENTS}
    replaced = {term for terms, _atom in WILDCARD_REPLACEMENTS for term in terms}
    atoms: list[str] = []
    for term in P_TERMS:
        replacement = replacement_by_first.get(term)
        if replacement is not None:
            atoms.append(replacement[1])
        elif term not in replaced:
            atoms.append(literal(term))
    return tuple(atoms)


ORDINARY = {
    "E_H": ordinary_block(EH_TERMS),
    "E_F": ordinary_block(EF_TERMS),
    "M_H": ordinary_block(MH_TERMS),
    "M_B": ordinary_block(MB_TERMS),
    "R": ordinary_block(R_TERMS),
    "G_model_fixed": ordinary_block(GMODEL_FIXED_TERMS),
    "G_mission": ordinary_block(GMISSION_TERMS),
    "G_mission_exact": ordinary_block(GMISSION_EXACT_TERMS),
    "G_structure_fixed": ordinary_block(GSTRUCTURE_FIXED_TERMS),
    "G_product": ordinary_block(GPRODUCT_TERMS),
    "G_product_exact": ordinary_block(GPRODUCT_EXACT_TERMS),
    "G_variation": ordinary_block(GVARIATION_TERMS),
    "C1_fixed": ordinary_block(C1_FIXED_TERMS),
    "G_DSL": ordinary_block(GDSL_TERMS),
    "T_precise": ordinary_block(TPRECISE_TERMS),
}

COMPOUND = {
    "M": any_of(ORDINARY["M_H"], ORDINARY["M_B"]),
    "G_model": any_of(
        ORDINARY["G_model_fixed"],
        ORDINARY["G_mission_exact"],
        "(" + all_of(ORDINARY["G_mission"], ORDINARY["M_B"]) + ")",
    ),
    "G_structure": any_of(
        ORDINARY["G_structure_fixed"],
        ORDINARY["G_product_exact"],
        ORDINARY["G_variation"],
        "(" + all_of(ORDINARY["G_product"], ORDINARY["M_B"]) + ")",
    ),
    "C1": any_of(ORDINARY["C1_fixed"], ORDINARY["G_DSL"]),
}


def population_block(variant: str) -> str:
    if variant == "literal":
        return ordinary_block(P_TERMS)
    if variant == "wildcard":
        return block_from_atoms(wildcard_population_atoms())
    raise ValueError(f"Unknown Wiley population variant: {variant}")


def full_schedule(variant: str) -> dict[str, str]:
    p = population_block(variant)
    return {
        "A1": all_of(p, ORDINARY["E_H"], ORDINARY["M_H"]),
        "A2": all_of(p, ORDINARY["E_F"], COMPOUND["M"]),
        "A3": all_of(p, ORDINARY["E_H"], ORDINARY["M_B"]),
        "B1": all_of(p, ORDINARY["M_H"]),
        "B2": all_of(p, ORDINARY["M_B"], ORDINARY["R"]),
        "BG1": all_of(p, COMPOUND["G_model"]),
        "BG2": all_of(p, COMPOUND["G_structure"]),
        "BC1": all_of(p, COMPOUND["C1"]),
        "BT2": all_of(p, ORDINARY["M_B"], ORDINARY["T_precise"]),
    }


def schedule_cells(variant: str) -> dict[str, tuple[dict[str, str], ...]]:
    """Return the lossless source cells for each semantic partition."""
    p = population_block(variant)
    schedule = full_schedule(variant)
    cells: dict[str, tuple[dict[str, str], ...]] = {}
    for partition_id in SCHEDULE_IDS:
        if partition_id == "A2":
            cells[partition_id] = (
                {
                    "cell_id": "mh",
                    "branch": "P AND E_F AND M_H",
                    "query": all_of(p, ORDINARY["E_F"], ORDINARY["M_H"]),
                },
                {
                    "cell_id": "mb",
                    "branch": "P AND E_F AND M_B",
                    "query": all_of(p, ORDINARY["E_F"], ORDINARY["M_B"]),
                },
            )
        else:
            cells[partition_id] = (
                {"cell_id": "direct", "branch": partition_id, "query": schedule[partition_id]},
            )
    return cells


LITERAL_SCHEDULE = full_schedule("literal")
WILDCARD_SCHEDULE = full_schedule("wildcard")
LITERAL_CELLS = schedule_cells("literal")
WILDCARD_CELLS = schedule_cells("wildcard")

assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert len(P_TERMS) == 26
assert len(wildcard_population_atoms()) == 21
assert all("NEAR" not in query.upper() for query in LITERAL_SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all("*" in query for query in WILDCARD_SCHEDULE.values())
assert len(LITERAL_SCHEDULE["A1"]) == 2770  # historically accepted source expression
for variant, cells in (("literal", LITERAL_CELLS), ("wildcard", WILDCARD_CELLS)):
    for partition_id, partition_cells in cells.items():
        for cell in partition_cells:
            if len(cell["query"]) > SOURCE_QUERY_LIMIT and not (
                variant == "literal" and partition_id == "A1" and cell["cell_id"] == "direct"
            ):
                raise AssertionError(f"Over-limit Wiley cell: {variant}/{partition_id}/{cell['cell_id']}")
