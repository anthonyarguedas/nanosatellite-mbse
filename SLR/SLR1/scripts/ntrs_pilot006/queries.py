"""Maximal term-prefix wildcard translation for NASA NTRS Pilot 006."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
EXPECTED_BASE_SHA256 = "2e04dc8aee492aab669b30b98fa365cb49f87c68192d0f227acd5abbf932b745"
BASE_PATH = Path(__file__).resolve().parents[1] / "ntrs_pilot005" / "queries.py"
if hashlib.sha256(BASE_PATH.read_bytes()).hexdigest() != EXPECTED_BASE_SHA256:
    raise RuntimeError("The accepted literal query snapshot changed")
_spec = importlib.util.spec_from_file_location("ntrs_pilot006_base", BASE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {BASE_PATH}")
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)
if _base.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The base schedule uses a different protocol commit")

SCHEDULE_IDS = _base.SCHEDULE_IDS
TERM_BLOCKS = _base.TERM_BLOCKS
LITERAL_SCHEDULE = _base.LITERAL_SCHEDULE
TERM_SNAPSHOT_PATH = _base.TERM_SNAPSHOT_PATH
TERM_SNAPSHOT_SHA256 = _base.TERM_SNAPSHOT_SHA256

# Every candidate combines declared forms from one lexical family. Phrase
# candidates keep straight quotes and place `*` at a term boundary. Acronyms
# stay literal because the protocol requires standalone acronym matches.
WILDCARD_REPLACEMENTS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "P": (
        ("CubeSat*", ("CubeSat", "CubeSats")),
        ("cube sat*", ("cube sat", "cube sats", "cube satellite", "cube satellites")),
        ("cube-sat*", ("cube-sat", "cube-sats")),
        ("nanosat*", ("nanosat", "nanosats", "nanosatellite", "nanosatellites")),
        ("nano-sat*", ("nano-sat", "nano-sats", "nano-satellite", "nano-satellites")),
        ("nano sat*", ("nano sat", "nano sats", "nano satellite", "nano satellites")),
        ("SmallSat*", ("SmallSat", "SmallSats")),
        ("small sat*", ("small satellite", "small satellites", "small sat", "small sats")),
    ),
    "E_H": (
        ("electrical power system*", ("electrical power system", "electrical power systems")),
        ("electric power system*", ("electric power system", "electric power systems")),
        ("electrical power subsystem*", ("electrical power subsystem", "electrical power subsystems")),
        ("electric power subsystem*", ("electric power subsystem", "electric power subsystems")),
        ("electrical energy subsystem*", ("electrical energy subsystem", "electrical energy subsystems")),
        ("power subsystem*", ("power subsystem", "power subsystems")),
        ("power system*", ("power system", "power systems")),
        ("spacecraft power system*", ("spacecraft power system", "spacecraft power systems")),
        ("power suppl*", ("power supply", "power supplies")),
        ("power distribution unit*", ("power distribution unit", "power distribution units")),
        ("power processing unit*", ("power processing unit", "power processing units")),
        ("electrical architecture*", ("electrical architecture", "electrical architectures")),
        ("power architecture*", ("power architecture", "power architectures")),
        ("DC power bus*", ("DC power bus", "DC power buses")),
    ),
    "E_F": (
        ("power budget*", ("power budget", "power budgets")),
        ("energy budget*", ("energy budget", "energy budgets")),
        ("energy balance*", ("energy balance", "energy balances")),
        ("power balance*", ("power balance", "power balances")),
        ("power margin*", ("power margin", "power margins")),
        ("photovoltaic generator*", ("photovoltaic generator", "photovoltaic generators")),
        ("solar array*", ("solar array", "solar arrays")),
        ("solar panel*", ("solar panel", "solar panels")),
        ("power interface*", ("power interface", "power interfaces")),
        ("power mode*", ("power mode", "power modes")),
        ("load profile*", ("load profile", "load profiles")),
    ),
    "M_H": (
        ("model-based system* engineering", ("model-based systems engineering", "model-based system engineering")),
        ("model based system* engineering", ("model based systems engineering", "model based system engineering")),
        ("model-driven system* engineering", ("model-driven systems engineering", "model-driven system engineering")),
        ("model driven system* engineering", ("model driven systems engineering", "model driven system engineering")),
        ("model-centric system* engineering", ("model-centric systems engineering", "model-centric system engineering")),
        ("model centric system* engineering", ("model centric systems engineering", "model centric system engineering")),
        ("system* modeling language", ("systems modeling language", "system modeling language")),
        ("system* modelling language", ("systems modelling language", "system modelling language")),
    ),
    "M_B": (
        ("system* model*", ("system model", "systems model", "system modeling", "systems modeling", "system modelling", "systems modelling")),
        ("reference model*", ("reference model", "reference models")),
        ("object-oriented systems model*", ("object-oriented systems model", "object-oriented systems models")),
        ("model-based system* design", ("model-based system design", "model-based systems design")),
        ("model based system* design", ("model based system design", "model based systems design")),
        ("system* architecture model*", ("system architecture model", "system architecture models", "systems architecture model", "systems architecture models")),
        ("integrated system* model*", ("integrated system model", "integrated system models", "integrated systems model", "integrated systems models")),
        ("system-level model*", ("system-level model", "system-level models")),
        ("system level model*", ("system level model", "system level models")),
        ("digital thread*", ("digital thread", "digital threads")),
        ("digital twin*", ("digital twin", "digital twins")),
    ),
    "R": _base.WILDCARD_REPLACEMENTS["R"] + (
        ("trade stud*", ("trade study", "trade studies")),
        ("trade-off*", ("trade-off", "trade-offs")),
    ),
    "G_model_fixed": (
        ("generic model*", ("generic model", "generic models")),
        ("generic system model*", ("generic system model", "generic system models")),
        ("reusable model*", ("reusable model", "reusable models")),
        ("reusable system model*", ("reusable system model", "reusable system models")),
        ("configurable model*", ("configurable model", "configurable models")),
        ("configurable system model*", ("configurable system model", "configurable system models")),
        ("model template*", ("model template", "model templates")),
    ),
    "G_mission": (),
    "G_mission_exact": (
        ("mission-agnostic model*", ("mission-agnostic model", "mission-agnostic models")),
        ("mission-agnostic architecture*", ("mission-agnostic architecture", "mission-agnostic architectures")),
        ("mission agnostic model*", ("mission agnostic model", "mission agnostic models")),
        ("mission agnostic architecture*", ("mission agnostic architecture", "mission agnostic architectures")),
        ("mission-independent model*", ("mission-independent model", "mission-independent models")),
        ("mission-independent architecture*", ("mission-independent architecture", "mission-independent architectures")),
        ("mission independent model*", ("mission independent model", "mission independent models")),
        ("mission independent architecture*", ("mission independent architecture", "mission independent architectures")),
    ),
    "G_structure_fixed": (
        ("reference architecture*", ("reference architecture", "reference architectures")),
        ("domain model*", ("domain model", "domain models")),
        ("metamodel*", ("metamodel", "metamodels")),
        ("meta-model*", ("meta-model", "meta-models")),
    ),
    "G_product": (),
    "G_product_exact": (
        ("product-line model*", ("product-line model", "product-line models")),
        ("product line model*", ("product line model", "product line models")),
        ("product-family model*", ("product-family model", "product-family models")),
        ("product family model*", ("product family model", "product family models")),
    ),
    "G_variation": (("variation point*", ("variation point", "variation points")),),
    "C1_fixed": (
        ("reference model*", ("reference model", "reference models")),
        ("system reference model*", ("system reference model", "system reference models")),
        ("model librar*", ("model library", "model libraries")),
        ("system model librar*", ("system model library", "system model libraries")),
        ("model pattern*", ("model pattern", "model patterns")),
        ("modeling pattern*", ("modeling pattern", "modeling patterns")),
        ("modelling pattern*", ("modelling pattern", "modelling patterns")),
        ("system* model pattern*", ("system model pattern", "system model patterns", "systems model pattern", "systems model patterns")),
        ("model profile*", ("model profile", "model profiles")),
        ("system* model profile*", ("system model profile", "system model profiles", "systems model profile", "systems model profiles")),
        ("SysML profile*", ("SysML profile", "SysML profiles")),
    ),
    "G_DSL": (
        ("domain-specific model* language", ("domain-specific modeling language", "domain-specific modelling language")),
        ("domain specific model* language", ("domain specific modeling language", "domain specific modelling language")),
    ),
    "T_precise": _base.WILDCARD_REPLACEMENTS["T_precise"] + (
        ("variation point*", ("variation point", "variation points")),
    ),
}


def literal_atom(value: str) -> str:
    return f'"{value}"'


def wildcard_atom(value: str) -> str:
    parts = value.split()
    if not parts or not any("*" in part for part in parts):
        raise ValueError("A wildcard candidate requires at least one term prefix")
    if any(part.count("*") > 1 or ("*" in part and not part.endswith("*")) for part in parts):
        raise ValueError("Every asterisk must end one NTRS query term")
    return f'"{value}"' if len(parts) > 1 else value


def any_of(expressions: Iterable[str]) -> str:
    values = tuple(expressions)
    if not values:
        raise ValueError("OR requires at least one expression")
    return "(" + " | ".join(values) + ")"


def all_of(*expressions: str) -> str:
    return "(" + " + ".join(expressions) + ")"


def wildcard_block(block_id: str) -> str:
    terms = TERM_BLOCKS[block_id]
    replacements = WILDCARD_REPLACEMENTS[block_id]
    inserted: dict[int, str] = {}
    replaced: set[str] = set()
    for candidate, values in replacements:
        atom = wildcard_atom(candidate)
        if not values or any(value not in terms for value in values):
            raise RuntimeError(f"Invalid {block_id} wildcard: {candidate}")
        if replaced.intersection(values):
            raise RuntimeError(f"Overlapping {block_id} wildcard: {candidate}")
        index = min(terms.index(value) for value in values)
        if index in inserted:
            raise RuntimeError(f"Insertion collision in {block_id}")
        inserted[index] = atom
        replaced.update(values)
    atoms = []
    for index, term in enumerate(terms):
        if index in inserted:
            atoms.append(inserted[index])
        if term not in replaced:
            atoms.append(literal_atom(term))
    return any_of(atoms)


ORDINARY = {block_id: wildcard_block(block_id) for block_id in TERM_BLOCKS}
COMPOUND = {
    "M": any_of((ORDINARY["M_H"], ORDINARY["M_B"])),
    "G_model": any_of((
        ORDINARY["G_model_fixed"],
        ORDINARY["G_mission_exact"],
        all_of(ORDINARY["G_mission"], ORDINARY["M_B"]),
    )),
    "G_structure": any_of((
        ORDINARY["G_structure_fixed"],
        ORDINARY["G_product_exact"],
        ORDINARY["G_variation"],
        all_of(ORDINARY["G_product"], ORDINARY["M_B"]),
    )),
    "C1": any_of((ORDINARY["C1_fixed"], ORDINARY["G_DSL"])),
}
BLOCKS = {**ORDINARY, **COMPOUND}
WILDCARD_SCHEDULE = {
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
WILDCARD_ATOM_COUNT = sum(len(group) for group in WILDCARD_REPLACEMENTS.values())
REPLACED_LITERAL_COUNT = sum(
    len(literals)
    for group in WILDCARD_REPLACEMENTS.values()
    for _candidate, literals in group
)

assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert set(WILDCARD_REPLACEMENTS) == set(TERM_BLOCKS)
assert WILDCARD_ATOM_COUNT == 114
assert REPLACED_LITERAL_COUNT == 284
assert all("~" not in query and "NEAR" not in query.upper() for query in WILDCARD_SCHEDULE.values())
assert all(len(WILDCARD_SCHEDULE[key]) < len(LITERAL_SCHEDULE[key]) for key in SCHEDULE_IDS)
