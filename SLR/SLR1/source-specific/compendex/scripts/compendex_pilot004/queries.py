"""Post-proximity Compendex queries for controlled-vocabulary Pilot 004.

The normative concept membership and compound definitions are pinned to
protocol-discovery-and-appraisal.md at commit
3194156e90497186664260a8e86435e78d2e2aa1. The reviewed post-proximity term
snapshot in atai_pilot007 supplies the literals. This module renders every
literal independently in Engineering Village ``ALL``. It uses no proximity,
pair expansion, wildcard, or controlled term in the normative free-text
schedule.
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
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CHANGED_BY_PROTOCOL_COMMIT = ("BG1", "BG2", "BC1", "BT2")

_TERM_MODULE_PATH = Path(__file__).resolve().parents[4] / "source-specific" / "advanced-technologies-aerospace-index" / "scripts" / "atai_pilot007" / "queries.py"
_spec = importlib.util.spec_from_file_location(
    "compendex_pilot004_post_proximity_terms", _TERM_MODULE_PATH
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load the post-proximity term snapshot at {_TERM_MODULE_PATH}")
_terms = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _terms
_spec.loader.exec_module(_terms)
if _terms.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The post-proximity term snapshot is pinned to a different protocol commit")
TERM_SNAPSHOT_SHA256 = hashlib.sha256(_TERM_MODULE_PATH.read_bytes()).hexdigest()
if TERM_SNAPSHOT_SHA256 != EXPECTED_TERM_SNAPSHOT_SHA256:
    raise RuntimeError("The reviewed post-proximity term snapshot changed")


def atom(value: str) -> str:
    return f'("{value}" WN ALL)'


def controlled_atom(value: str) -> str:
    return f"({{{value}}} WN CV)"


def ordinary_block(values: tuple[str, ...]) -> str:
    if not values:
        raise ValueError("An ordinary block requires at least one literal")
    return "(" + " OR ".join(atom(value) for value in values) + ")"


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


def without(left: str, right: str) -> str:
    return f"({left} NOT {right})"


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

BLOCKS = {
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

SCHEDULE = {
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

LANGUAGE_CLAUSE = "(English WN LA)"
SOURCE_SCHEDULE = {
    partition_id: all_of(query, LANGUAGE_CLAUSE)
    for partition_id, query in SCHEDULE.items()
}

# Candidates are limited to exact Ei descriptors assigned to selected known
# records. Generic Systems engineering is context-only under the protocol.
P_CONTROLLED = any_of(
    controlled_atom("Nanosatellites"),
    controlled_atom("Small satellites"),
)
M_H_CONTROLLED = all_of(
    controlled_atom("Systems engineering"),
    controlled_atom("Modeling languages"),
)
P_AUGMENTED = any_of(BLOCKS["P"], P_CONTROLLED)
M_H_AUGMENTED = any_of(BLOCKS["M_H"], M_H_CONTROLLED)

B1_LITERAL = SOURCE_SCHEDULE["B1"]
B1_AUGMENTED = all_of(P_AUGMENTED, M_H_AUGMENTED, LANGUAGE_CLAUSE)

# These two disjoint logical routes cover augmented B1 minus literal B1.
# Route M covers records lacking free-text M_H. Route P covers the remaining
# records that have free-text M_H but lack free-text P.
B1_M_CANDIDATE_ONLY = all_of(
    without(all_of(P_AUGMENTED, M_H_CONTROLLED), BLOCKS["M_H"]),
    LANGUAGE_CLAUSE,
)
B1_P_CANDIDATE_ONLY = all_of(
    without(all_of(P_CONTROLLED, M_H_AUGMENTED), BLOCKS["P"]),
    LANGUAGE_CLAUSE,
)

SELECTED_KNOWN_RECORDS = (
    (
        "20122115042229",
        "Applying model based systems engineering (MBSE) to a standard CubeSat",
    ),
    (
        "20142617854738",
        "Small satellite systems design methodology: A formal and agile design process",
    ),
    (
        "20163002629469",
        "Developing a CubeSat Model-Based System Engineering (MBSE) reference model - Interim status #2",
    ),
    (
        "20171603573466",
        "Integrated system modeling in SysML for small satellites",
    ),
    (
        "20182005200201",
        "Application of model-based systems engineering in small satellite conceptual design-A SysML approach",
    ),
    (
        "20204209361264",
        "Applying a Model-Based Approach to Develop a Standardized Template for CubeSat-class Satellites",
    ),
    (
        "20223712726738",
        "A Model-Based Approach to Risk Management for RVSAT-1: a Student Nano-satellite Project-Using SysML",
    ),
    (
        "20232514262795",
        "Open-source CubeSat MBSE Approach to Address Traceability: Power Subsystem",
    ),
    (
        "20241215786220",
        "Effective Model-Based Systems Engineering framework for academic nanosatellite project management and design",
    ),
    (
        "20241916046896",
        "A Tailored Systems Engineering Process for Developing Student-Built CubeSat Class Satellites",
    ),
    (
        "20251318145456",
        "Integrating Model-Based Systems Engineering into CubeSat Development: A Case Study of the BOREALIS Mission",
    ),
)
KNOWN_SET = any_of(*(f"({accession} WN AN)" for accession, _ in SELECTED_KNOWN_RECORDS))
KNOWN_P_CONTROLLED = all_of(KNOWN_SET, P_CONTROLLED, LANGUAGE_CLAUSE)
KNOWN_M_H_CONTROLLED = all_of(KNOWN_SET, M_H_CONTROLLED, LANGUAGE_CLAUSE)
KNOWN_SYSML_CONTROLLED = all_of(
    KNOWN_SET, controlled_atom("SysML"), LANGUAGE_CLAUSE
)

VALUE_CELLS = {
    "known-P-controlled": KNOWN_P_CONTROLLED,
    "known-MH-controlled": KNOWN_M_H_CONTROLLED,
    "known-SysML-controlled": KNOWN_SYSML_CONTROLLED,
    "B1-MH-candidate-only": B1_M_CANDIDATE_ONLY,
    "B1-P-candidate-only": B1_P_CANDIDATE_ONLY,
}

TERM_COUNTS = dict(_terms.TERM_COUNTS)
EXPECTED_TERM_COUNTS = dict(_terms.EXPECTED_COUNTS)

assert tuple(SCHEDULE) == SCHEDULE_IDS
assert TERM_COUNTS == EXPECTED_TERM_COUNTS
assert B1_LITERAL == all_of(SCHEDULE["B1"], LANGUAGE_CLAUSE)
assert all("NEAR" not in query.upper() for query in SOURCE_SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in SOURCE_SCHEDULE.values())
assert all("NEAR" not in query.upper() for query in VALUE_CELLS.values())
assert all("*" not in query and "?" not in query for query in VALUE_CELLS.values())
for _p_free in (False, True):
    for _p_controlled in (False, True):
        for _mh_free in (False, True):
            for _mh_controlled in (False, True):
                _augmented = (_p_free or _p_controlled) and (
                    _mh_free or _mh_controlled
                )
                _literal = _p_free and _mh_free
                _mh_route = (
                    (_p_free or _p_controlled)
                    and _mh_controlled
                    and not _mh_free
                )
                _p_route = (
                    _p_controlled
                    and (_mh_free or _mh_controlled)
                    and not _p_free
                )
                assert (_augmented and not _literal) == (_mh_route or _p_route)
