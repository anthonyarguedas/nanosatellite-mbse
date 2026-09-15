"""Canonical ATAI literal and bounded-wildcard schedule queries for Pilot 008.

The ordinary concept membership and compound Boolean definitions are pinned to
protocol commit 3194156e90497186664260a8e86435e78d2e2aa1. The candidate uses
ProQuest's bounded ``[*n]`` truncation in ``NOFT`` for every declared variant
family that has one safe common source stem. Exact ``IF.EXACT`` alternatives
remain explicit because Pilot 006 proved that this indexed-keyword field adds
records independently of ``NOFT``. Singleton terms, punctuation variants, and
families without a safe common stem remain literal.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
TERM_SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "atai_pilot007" / "queries.py"

_spec = importlib.util.spec_from_file_location("atai_pilot008_term_snapshot", TERM_SNAPSHOT_PATH)
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


@dataclass(frozen=True)
class WildcardFamily:
    pattern: str
    terms: tuple[str, ...]


def family(pattern: str, *terms: str) -> WildcardFamily:
    return WildcardFamily(pattern=pattern, terms=tuple(terms))


# Patterns containing whitespace stay quoted so each cross-source multiword
# entry remains an ordered phrase. The number in [*n] is the smallest bound
# that covers the declared suffixes in that family.
WILDCARD_FAMILIES: dict[str, tuple[WildcardFamily, ...]] = {
    "P": (
        family("CubeSat[*1]", "CubeSat", "CubeSats"),
        family('"cube sat[*1]"', "cube sat", "cube sats"),
        family('"cube-sat[*1]"', "cube-sat", "cube-sats"),
        family('"cube satellite[*1]"', "cube satellite", "cube satellites"),
        family(
            "nanosat[*7]",
            "nanosat",
            "nanosats",
            "nanosatellite",
            "nanosatellites",
        ),
        family('"nano-sat[*1]"', "nano-sat", "nano-sats"),
        family('"nano sat[*1]"', "nano sat", "nano sats"),
        family('"nano-satellite[*1]"', "nano-satellite", "nano-satellites"),
        family('"nano satellite[*1]"', "nano satellite", "nano satellites"),
        family("SmallSat[*1]", "SmallSat", "SmallSats"),
        family('"small satellite[*1]"', "small satellite", "small satellites"),
        family('"small sat[*1]"', "small sat", "small sats"),
    ),
    "E_H": (
        family('"electrical power system[*1]"', "electrical power system", "electrical power systems"),
        family('"electric power system[*1]"', "electric power system", "electric power systems"),
        family('"electrical power subsystem[*1]"', "electrical power subsystem", "electrical power subsystems"),
        family('"electric power subsystem[*1]"', "electric power subsystem", "electric power subsystems"),
        family('"electrical energy subsystem[*1]"', "electrical energy subsystem", "electrical energy subsystems"),
        family("EPS[*1]", "EPS", "EPSs"),
        family('"power subsystem[*1]"', "power subsystem", "power subsystems"),
        family('"power system[*1]"', "power system", "power systems"),
        family('"spacecraft power system[*1]"', "spacecraft power system", "spacecraft power systems"),
        family('"power suppl[*3]"', "power supply", "power supplies"),
        family('"power distribution unit[*1]"', "power distribution unit", "power distribution units"),
        family("PDU[*1]", "PDU", "PDUs"),
        family('"power processing unit[*1]"', "power processing unit", "power processing units"),
        family('"electrical architecture[*1]"', "electrical architecture", "electrical architectures"),
        family('"power architecture[*1]"', "power architecture", "power architectures"),
        family('"DC power bus[*2]"', "DC power bus", "DC power buses"),
        family("PCDU[*1]", "PCDU", "PCDUs"),
        family("PMAD[*1]", "PMAD", "PMADs"),
    ),
    "E_F": (
        family('"power budget[*1]"', "power budget", "power budgets"),
        family('"energy budget[*1]"', "energy budget", "energy budgets"),
        family('"energy balance[*1]"', "energy balance", "energy balances"),
        family('"power balance[*1]"', "power balance", "power balances"),
        family('"power margin[*1]"', "power margin", "power margins"),
        family('"photovoltaic generator[*1]"', "photovoltaic generator", "photovoltaic generators"),
        family('"solar array[*1]"', "solar array", "solar arrays"),
        family('"solar panel[*1]"', "solar panel", "solar panels"),
        family("batter[*3]", "battery", "batteries"),
        family('"state[*1] of charge"', "state of charge", "states of charge"),
        family('"power interface[*1]"', "power interface", "power interfaces"),
        family('"power mode[*1]"', "power mode", "power modes"),
        family('"load profile[*1]"', "load profile", "load profiles"),
    ),
    "M_H": (
        family('"model-based system[*1] engineering"', "model-based systems engineering", "model-based system engineering"),
        family('"model based system[*1] engineering"', "model based systems engineering", "model based system engineering"),
        family('"model-driven system[*1] engineering"', "model-driven systems engineering", "model-driven system engineering"),
        family('"model driven system[*1] engineering"', "model driven systems engineering", "model driven system engineering"),
        family('"model-centric system[*1] engineering"', "model-centric systems engineering", "model-centric system engineering"),
        family('"model centric system[*1] engineering"', "model centric systems engineering", "model centric system engineering"),
        family('"system[*1] modeling language"', "systems modeling language", "system modeling language"),
        family('"system[*1] modelling language"', "systems modelling language", "system modelling language"),
    ),
    "M_B": (
        family('"system[*1] model"', "system model", "systems model"),
        family('"system[*1] modeling"', "system modeling", "systems modeling"),
        family('"system[*1] modelling"', "system modelling", "systems modelling"),
        family('"reference model[*1]"', "reference model", "reference models"),
        family('"object-oriented systems model[*1]"', "object-oriented systems model", "object-oriented systems models"),
        family('"model-based system[*1] design"', "model-based system design", "model-based systems design"),
        family('"model based system[*1] design"', "model based system design", "model based systems design"),
        family(
            '"system[*1] architecture model[*1]"',
            "system architecture model",
            "system architecture models",
            "systems architecture model",
            "systems architecture models",
        ),
        family(
            '"integrated system[*1] model[*1]"',
            "integrated system model",
            "integrated system models",
            "integrated systems model",
            "integrated systems models",
        ),
        family('"system-level model[*1]"', "system-level model", "system-level models"),
        family('"system level model[*1]"', "system level model", "system level models"),
        family('"digital thread[*1]"', "digital thread", "digital threads"),
        family('"digital twin[*1]"', "digital twin", "digital twins"),
    ),
    "R": (
        family("requirement[*1]", "requirement", "requirements"),
        family("function[*2]", "function", "functions", "functional"),
        family("behavior[*2]", "behavior", "behaviors", "behavioral"),
        family("behaviour[*2]", "behaviour", "behaviours", "behavioural"),
        family("architectur[*2]", "architecture", "architectures", "architectural"),
        family("interface[*1]", "interface", "interfaces"),
        family("trace[*7]", "traceability", "trace", "traceable", "traced"),
        family("allocat[*3]", "allocation", "allocate", "allocated"),
        family("constraint[*1]", "constraint", "constraints"),
        family("parametric[*1]", "parametric", "parametrics"),
        family("analys[*2]", "analysis", "analyses"),
        family("design[*3]", "design", "designs", "designed", "designing"),
        family("decision[*1]", "decision", "decisions"),
        family('"trade stud[*3]"', "trade study", "trade studies"),
        family('"trade-off[*1]"', "trade-off", "trade-offs"),
        family("tradeoff[*1]", "tradeoff", "tradeoffs"),
        family("verification[*1]", "verification", "verifications"),
        family("verif[*4]", "verify", "verifies", "verified", "verifying"),
        family("validation[*1]", "validation", "validations"),
        family("validat[*3]", "validate", "validates", "validated", "validating"),
    ),
    "G_model_fixed": (
        family('"generic model[*1]"', "generic model", "generic models"),
        family('"generic system model[*1]"', "generic system model", "generic system models"),
        family('"reusable model[*1]"', "reusable model", "reusable models"),
        family('"reusable system model[*1]"', "reusable system model", "reusable system models"),
        family('"configurable model[*1]"', "configurable model", "configurable models"),
        family('"configurable system model[*1]"', "configurable system model", "configurable system models"),
        family('"model template[*1]"', "model template", "model templates"),
    ),
    "G_mission": (),
    "G_mission_exact": (
        family('"mission-agnostic model[*1]"', "mission-agnostic model", "mission-agnostic models"),
        family('"mission-agnostic architecture[*1]"', "mission-agnostic architecture", "mission-agnostic architectures"),
        family('"mission agnostic model[*1]"', "mission agnostic model", "mission agnostic models"),
        family('"mission agnostic architecture[*1]"', "mission agnostic architecture", "mission agnostic architectures"),
        family('"mission-independent model[*1]"', "mission-independent model", "mission-independent models"),
        family('"mission-independent architecture[*1]"', "mission-independent architecture", "mission-independent architectures"),
        family('"mission independent model[*1]"', "mission independent model", "mission independent models"),
        family('"mission independent architecture[*1]"', "mission independent architecture", "mission independent architectures"),
    ),
    "G_structure_fixed": (
        family('"reference architecture[*1]"', "reference architecture", "reference architectures"),
        family('"domain model[*1]"', "domain model", "domain models"),
        family("metamodel[*1]", "metamodel", "metamodels"),
        family("meta-model[*1]", "meta-model", "meta-models"),
    ),
    "G_product": (),
    "G_product_exact": (
        family('"product-line model[*1]"', "product-line model", "product-line models"),
        family('"product line model[*1]"', "product line model", "product line models"),
        family('"product-family model[*1]"', "product-family model", "product-family models"),
        family('"product family model[*1]"', "product family model", "product family models"),
    ),
    "G_variation": (
        family('"variation point[*1]"', "variation point", "variation points"),
    ),
    "C1_fixed": (
        family('"reference model[*1]"', "reference model", "reference models"),
        family('"system reference model[*1]"', "system reference model", "system reference models"),
        family('"model librar[*3]"', "model library", "model libraries"),
        family('"system model librar[*3]"', "system model library", "system model libraries"),
        family('"model pattern[*1]"', "model pattern", "model patterns"),
        family('"modeling pattern[*1]"', "modeling pattern", "modeling patterns"),
        family('"modelling pattern[*1]"', "modelling pattern", "modelling patterns"),
        family('"system model pattern[*1]"', "system model pattern", "system model patterns"),
        family('"systems model pattern[*1]"', "systems model pattern", "systems model patterns"),
        family('"model profile[*1]"', "model profile", "model profiles"),
        family('"system model profile[*1]"', "system model profile", "system model profiles"),
        family('"systems model profile[*1]"', "systems model profile", "systems model profiles"),
        family('"SysML profile[*1]"', "SysML profile", "SysML profiles"),
    ),
    "G_DSL": (),
    "T_precise": (
        family("tailor[*3]", "tailor", "tailors", "tailored", "tailoring"),
        family("customiz[*5]", "customize", "customizes", "customized", "customizing", "customization"),
        family("customis[*5]", "customise", "customises", "customised", "customising", "customisation"),
        family("parameteriz[*5]", "parameterize", "parameterizes", "parameterized", "parameterizing", "parameterization"),
        family("parameteris[*5]", "parameterise", "parameterises", "parameterised", "parameterising", "parameterisation"),
        family("instantiat[*3]", "instantiate", "instantiates", "instantiated", "instantiating", "instantiation"),
        family('"variation point[*1]"', "variation point", "variation points"),
    ),
}

BLOCK_TERMS: dict[str, tuple[str, ...]] = {
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


def literal(value: str) -> str:
    if '"' in value:
        raise ValueError("A source literal cannot contain a straight double quote")
    return f'"{value}"'


def literal_atom(value: str) -> str:
    rendered = literal(value)
    return f"(NOFT({rendered}) OR IF.EXACT({rendered}))"


def wildcard_atom(item: WildcardFamily) -> str:
    exact_if = (f"IF.EXACT({literal(value)})" for value in item.terms)
    return "(" + " OR ".join((f"NOFT({item.pattern})", *exact_if)) + ")"


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
                raise RuntimeError(f"A {block} wildcard family is out of source-term order")
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


def family_receipts() -> dict[str, list[dict[str, object]]]:
    return {
        block: [
            {
                "pattern": item.pattern,
                "explicit_terms": list(item.terms),
                "wildcard_operators": len(re.findall(r"\[\*\d+\]", item.pattern)),
            }
            for item in families
        ]
        for block, families in WILDCARD_FAMILIES.items()
    }


def _validate_families() -> None:
    if set(WILDCARD_FAMILIES) != set(BLOCK_TERMS):
        raise RuntimeError("Wildcard family blocks differ from the ordinary blocks")
    pattern_re = re.compile(r"\[\*(\d{1,2})\]")
    for block, declarations in WILDCARD_FAMILIES.items():
        values = BLOCK_TERMS[block]
        positions = {value: index for index, value in enumerate(values)}
        seen: set[str] = set()
        for item in declarations:
            widths = [int(value) for value in pattern_re.findall(item.pattern)]
            if not widths or any(width < 1 or width > 20 for width in widths):
                raise RuntimeError(f"Invalid bounded wildcard in {block}: {item.pattern}")
            if pattern_re.sub("", item.pattern).find("*") >= 0 or "?" in item.pattern:
                raise RuntimeError(f"Unbounded wildcard syntax in {block}: {item.pattern}")
            if len(item.terms) < 2 or len(set(item.terms)) != len(item.terms):
                raise RuntimeError(f"Invalid wildcard family membership in {block}")
            if any(value not in positions for value in item.terms):
                raise RuntimeError(f"A {block} wildcard family contains a foreign term")
            if seen.intersection(item.terms):
                raise RuntimeError(f"Overlapping wildcard families in {block}")
            indexes = [positions[value] for value in item.terms]
            if indexes != sorted(indexes):
                raise RuntimeError(f"A {block} wildcard family changes source-term order")
            seen.update(item.terms)


_validate_families()

LITERAL_ORDINARY_BLOCKS = {block: literal_block(values) for block, values in BLOCK_TERMS.items()}
WILDCARD_ORDINARY_BLOCKS = {block: wildcard_block(block) for block in BLOCK_TERMS}
LITERAL_COMPOUND_BLOCKS = compound_blocks(LITERAL_ORDINARY_BLOCKS)
WILDCARD_COMPOUND_BLOCKS = compound_blocks(WILDCARD_ORDINARY_BLOCKS)
LITERAL_SCHEDULE = schedule(LITERAL_ORDINARY_BLOCKS, LITERAL_COMPOUND_BLOCKS)
WILDCARD_SCHEDULE = schedule(WILDCARD_ORDINARY_BLOCKS, WILDCARD_COMPOUND_BLOCKS)

TERM_COUNTS = dict(_terms.TERM_COUNTS)
FAMILY_RECEIPTS = family_receipts()
FAMILY_COUNT = sum(len(items) for items in WILDCARD_FAMILIES.values())
REPLACED_TERM_COUNT = sum(
    len(item.terms) for items in WILDCARD_FAMILIES.values() for item in items
)
WILDCARD_OPERATOR_COUNT_BY_BLOCK = {
    block: sum(item["wildcard_operators"] for item in receipts)
    for block, receipts in FAMILY_RECEIPTS.items()
}

assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert LITERAL_SCHEDULE == _terms.SCHEDULE
assert all("NEAR" not in query.upper() for query in (*LITERAL_SCHEDULE.values(), *WILDCARD_SCHEDULE.values()))
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all("[*" in query and "?" not in query for query in WILDCARD_SCHEDULE.values())
assert all(len(WILDCARD_SCHEDULE[key]) < len(LITERAL_SCHEDULE[key]) for key in SCHEDULE_IDS)
