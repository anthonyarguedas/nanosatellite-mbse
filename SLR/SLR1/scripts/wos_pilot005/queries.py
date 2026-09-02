"""Broad Web of Science wildcard translation for the current schedule."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCRIPT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = SCRIPT_ROOT / "wos_pilot004" / "queries.py"
FAMILY_PATH = SCRIPT_ROOT / "atai_pilot008" / "queries.py"
EXPECTED_BASELINE_SHA256 = "5f4b3e47f6e775eb34ed8fcfb68cd8b80eebd22f3698275381aeac2d82ac623e"
EXPECTED_FAMILY_SHA256 = "ce39aeee6c901324a16a588fc368a92ac1f3b5bb15a19705dcb2b8aa7c24a348"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if hashlib.sha256(BASELINE_PATH.read_bytes()).hexdigest() != EXPECTED_BASELINE_SHA256:
    raise RuntimeError("The Web of Science Pilot 004 query baseline changed")
if hashlib.sha256(FAMILY_PATH.read_bytes()).hexdigest() != EXPECTED_FAMILY_SHA256:
    raise RuntimeError("The reviewed ordinary-term family map changed")

_baseline = load_module("wos_pilot005_baseline", BASELINE_PATH)
_families = load_module("wos_pilot005_families", FAMILY_PATH)
if _baseline.PROTOCOL_COMMIT != PROTOCOL_COMMIT or _families.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("A query dependency uses a different protocol commit")

SCHEDULE_IDS = _baseline.SCHEDULE_IDS
BLOCK_TERMS = dict(_families.BLOCK_TERMS)
WILDCARD_FAMILIES = dict(_families.WILDCARD_FAMILIES)
WIDTH_PATTERN = re.compile(r"\[\*(\d{1,2})\]")


def wos_pattern(value: str) -> str:
    """Translate a reviewed bounded family stem to WOS `$` or `*` syntax."""
    widths = [int(item) for item in WIDTH_PATTERN.findall(value)]
    if not widths:
        raise ValueError(f"A family pattern has no bounded suffix: {value}")

    def replace(match: re.Match[str]) -> str:
        # WOS `$` is zero or one character. Use unbounded `*` only where a
        # declared family requires a longer suffix.
        return "$" if int(match.group(1)) == 1 else "*"

    rendered = WIDTH_PATTERN.sub(replace, value)
    if "[*" in rendered or "?" in rendered:
        raise ValueError(f"Could not translate family pattern: {value}")
    if rendered.startswith('"') and rendered.endswith('"'):
        return rendered
    if '"' in rendered or any(character.isspace() for character in rendered):
        raise ValueError(f"Malformed unquoted family pattern: {value}")
    return f'"{rendered}"'


def wildcard_atom(item) -> str:
    return f"TS=({wos_pattern(item.pattern)})"


def wildcard_block(block: str) -> str:
    terms = BLOCK_TERMS[block]
    families = WILDCARD_FAMILIES[block]
    by_first = {item.terms[0]: item for item in families}
    replaced = {term for item in families for term in item.terms}
    atoms: list[str] = []
    covered: set[str] = set()
    for term in terms:
        item = by_first.get(term)
        if item is not None:
            atoms.append(wildcard_atom(item))
            covered.update(item.terms)
        elif term in replaced:
            if term not in covered:
                raise RuntimeError(f"A {block} family changed protocol term order")
        else:
            atoms.append(_baseline.literal_atom(term))
    if covered != replaced:
        raise RuntimeError(f"The {block} wildcard block omitted a family")
    return _baseline.any_of(*atoms)


WILDCARD_ORDINARY_BLOCKS = {
    block: wildcard_block(block) for block in BLOCK_TERMS
}
WILDCARD_COMPOUND_BLOCKS = {
    "M": _baseline.any_of(
        WILDCARD_ORDINARY_BLOCKS["M_H"],
        WILDCARD_ORDINARY_BLOCKS["M_B"],
    ),
    "G_model": _baseline.any_of(
        WILDCARD_ORDINARY_BLOCKS["G_model_fixed"],
        WILDCARD_ORDINARY_BLOCKS["G_mission_exact"],
        _baseline.all_of(
            WILDCARD_ORDINARY_BLOCKS["G_mission"],
            WILDCARD_ORDINARY_BLOCKS["M_B"],
        ),
    ),
    "G_structure": _baseline.any_of(
        WILDCARD_ORDINARY_BLOCKS["G_structure_fixed"],
        WILDCARD_ORDINARY_BLOCKS["G_product_exact"],
        WILDCARD_ORDINARY_BLOCKS["G_variation"],
        _baseline.all_of(
            WILDCARD_ORDINARY_BLOCKS["G_product"],
            WILDCARD_ORDINARY_BLOCKS["M_B"],
        ),
    ),
    "C1": _baseline.any_of(
        WILDCARD_ORDINARY_BLOCKS["C1_fixed"],
        WILDCARD_ORDINARY_BLOCKS["G_DSL"],
    ),
}


def schedule() -> dict[str, str]:
    ordinary = WILDCARD_ORDINARY_BLOCKS
    compound = WILDCARD_COMPOUND_BLOCKS
    semantic = {
        "A1": _baseline.all_of(ordinary["P"], ordinary["E_H"], ordinary["M_H"]),
        "A2": _baseline.all_of(ordinary["P"], ordinary["E_F"], compound["M"]),
        "A3": _baseline.all_of(ordinary["P"], ordinary["E_H"], ordinary["M_B"]),
        "B1": _baseline.all_of(ordinary["P"], ordinary["M_H"]),
        "B2": _baseline.all_of(ordinary["P"], ordinary["M_B"], ordinary["R"]),
        "BG1": _baseline.all_of(ordinary["P"], compound["G_model"]),
        "BG2": _baseline.all_of(ordinary["P"], compound["G_structure"]),
        "BC1": _baseline.all_of(ordinary["P"], compound["C1"]),
        "BT2": _baseline.all_of(ordinary["P"], ordinary["M_B"], ordinary["T_precise"]),
    }
    return {key: _baseline.with_main_controls(value) for key, value in semantic.items()}


LITERAL_SCHEDULE = dict(_baseline.LITERAL_SCHEDULE)
POPULATION_WILDCARD_SCHEDULE = dict(_baseline.WILDCARD_SCHEDULE)
BROAD_WILDCARD_SCHEDULE = schedule()
FAMILY_COUNT = sum(len(items) for items in WILDCARD_FAMILIES.values())
REPLACED_TERM_COUNT = sum(
    len(item.terms) for items in WILDCARD_FAMILIES.values() for item in items
)
FAMILY_RECEIPTS = {
    block: [
        {
            "source_pattern": wos_pattern(item.pattern),
            "family_basis": item.pattern,
            "explicit_terms": list(item.terms),
            "operators": WIDTH_PATTERN.sub(
                lambda match: "$" if int(match.group(1)) == 1 else "*",
                item.pattern,
            ).count("$")
            + WIDTH_PATTERN.sub(
                lambda match: "$" if int(match.group(1)) == 1 else "*",
                item.pattern,
            ).count("*"),
        }
        for item in items
    ]
    for block, items in WILDCARD_FAMILIES.items()
}
WILDCARD_OPERATOR_COUNT_BY_BLOCK = {
    block: sum(item["source_pattern"].count("*") + item["source_pattern"].count("$") for item in receipts)
    for block, receipts in FAMILY_RECEIPTS.items()
}

assert FAMILY_COUNT == 128
assert REPLACED_TERM_COUNT == 292
assert tuple(BROAD_WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert all("NEAR" not in query.upper() and " SAME " not in query.upper() for query in BROAD_WILDCARD_SCHEDULE.values())
assert all("[*" not in query and "?" not in query for query in BROAD_WILDCARD_SCHEDULE.values())
assert all(("*" in query or "$" in query) for query in BROAD_WILDCARD_SCHEDULE.values())
assert all(len(BROAD_WILDCARD_SCHEDULE[key]) < len(LITERAL_SCHEDULE[key]) for key in SCHEDULE_IDS)
