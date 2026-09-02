"""Springer Pilot 004 queries pinned to the post-proximity protocol."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess
from typing import Iterable

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
PROTOCOL_SHA256 = "5c5fa9551bb92b38c217bfa16589c5bef5e5985eea9fe55ddcf52b20145e3306"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PROTOCOL_PATH = SLR1_DIR / "protocol-discovery-and-appraisal.md"

EXPECTED_COUNTS = {
    "P": 26,
    "E_H": 38,
    "E_F": 37,
    "M_H": 54,
    "M_B": 31,
    "R": 55,
    "G_model_fixed": 14,
    "G_mission": 4,
    "G_mission_exact": 16,
    "G_structure_fixed": 8,
    "G_product": 4,
    "G_product_exact": 8,
    "G_variation": 2,
    "C1_fixed": 26,
    "G_DSL": 4,
    "T_precise": 32,
}

WILDCARD_REPLACEMENTS = (
    (("CubeSat", "CubeSats"), "CubeSat*"),
    (("nanosat", "nanosats", "nanosatellite", "nanosatellites"), "nanosat*"),
    (("SmallSat", "SmallSats"), "SmallSat*"),
)


def _protocol_terms() -> dict[str, tuple[str, ...]]:
    raw = PROTOCOL_PATH.read_bytes() if PROTOCOL_PATH.is_file() else b""
    if hashlib.sha256(raw).hexdigest() != PROTOCOL_SHA256:
        repository = SLR1_DIR.parents[1]
        completed = subprocess.run(
            [
                "git",
                "show",
                f"{PROTOCOL_COMMIT}:SLR/SLR1/protocol-discovery-and-appraisal.md",
            ],
            cwd=repository,
            check=True,
            capture_output=True,
        )
        raw = completed.stdout
    if hashlib.sha256(raw).hexdigest() != PROTOCOL_SHA256:
        raise RuntimeError(
            f"Git object does not match pinned protocol commit {PROTOCOL_COMMIT}"
        )
    blocks: dict[str, tuple[str, ...]] = {}
    pattern = re.compile(r"^- \*\*.+? \(`([^`]+)`\):\*\* (.+)$")
    for line in raw.decode("utf-8").splitlines():
        match = pattern.match(line)
        if match is None or match.group(1) not in EXPECTED_COUNTS:
            continue
        blocks[match.group(1)] = tuple(re.findall(r"`([^`]+)`", match.group(2)))
    observed = {name: len(values) for name, values in blocks.items()}
    if observed != EXPECTED_COUNTS:
        raise RuntimeError(f"Pinned protocol term transcription changed: {observed!r}")
    return blocks


TERMS = _protocol_terms()
P_TERMS = TERMS["P"]


def literal(value: str) -> str:
    return f'"{value}"'


def block_from_atoms(atoms: Iterable[str]) -> str:
    values = tuple(atoms)
    if not values:
        raise ValueError("A Springer block requires at least one atom")
    return "(" + " OR ".join(values) + ")"


def ordinary_block(terms: Iterable[str]) -> str:
    return block_from_atoms(literal(term) for term in terms)


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("Springer OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("Springer AND requires at least one expression")
    return " AND ".join(expressions)


def wildcard_population_atoms() -> tuple[str, ...]:
    replacement_by_first = {
        terms[0]: (terms, candidate) for terms, candidate in WILDCARD_REPLACEMENTS
    }
    replaced = {term for terms, _candidate in WILDCARD_REPLACEMENTS for term in terms}
    atoms: list[str] = []
    covered: set[str] = set()
    for term in P_TERMS:
        replacement = replacement_by_first.get(term)
        if replacement is not None:
            terms, candidate = replacement
            atoms.append(candidate)
            covered.update(terms)
        elif term not in replaced:
            atoms.append(literal(term))
    if covered != replaced:
        raise RuntimeError(
            "Wildcard population replacement did not cover its declaration"
        )
    return tuple(atoms)


ORDINARY = {
    name: ordinary_block(TERMS[name]) for name in EXPECTED_COUNTS if name != "P"
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
    raise ValueError(f"Unknown Springer query variant: {variant}")


def b2_boolean_cells(variant: str) -> tuple[dict[str, str], ...]:
    """Return a fixed two-by-two B2 Boolean partition for unstable years."""
    p = population_block(variant)
    mb_terms = TERMS["M_B"]
    r_terms = TERMS["R"]
    mb_groups = (mb_terms[:18], mb_terms[18:])
    r_groups = (r_terms[:32], r_terms[32:])
    cells = []
    for mb_index, mb_group in enumerate(mb_groups, start=1):
        for r_index, r_group in enumerate(r_groups, start=1):
            cells.append(
                {
                    "cell_id": f"mb-{mb_index}-r-{r_index}",
                    "branch": (
                        f"P AND M_B[{1 if mb_index == 1 else 19}:"
                        f"{18 if mb_index == 1 else len(mb_terms)}] AND "
                        f"R[{1 if r_index == 1 else 33}:"
                        f"{32 if r_index == 1 else len(r_terms)}]"
                    ),
                    "query": all_of(
                        p,
                        ordinary_block(mb_group),
                        ordinary_block(r_group),
                    ),
                }
            )
    return tuple(cells)


def a2_mb_chunk_cells(variant: str) -> tuple[dict[str, str], ...]:
    """Split M_B into four fixed contiguous OR groups for stable pagination."""
    p = population_block(variant)
    terms = TERMS["M_B"]
    boundaries = (0, 8, 16, 24, len(terms))
    cells = []
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:]), start=1):
        cells.append(
            {
                "cell_id": f"mb-{index:02d}",
                "branch": f"P AND E_F AND M_B[{start + 1}:{end}]",
                "query": all_of(
                    p,
                    ORDINARY["E_F"],
                    ordinary_block(terms[start:end]),
                ),
            }
        )
    return tuple(cells)


def a2_cells(variant: str) -> tuple[dict[str, str], ...]:
    """Return a prospective lossless A2 union when the direct route fails."""
    p = population_block(variant)
    return (
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


def schedule(variant: str) -> dict[str, str]:
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


LITERAL_SCHEDULE = schedule("literal")
WILDCARD_SCHEDULE = schedule("wildcard")
LITERAL_A2_CELLS = a2_cells("literal")
WILDCARD_A2_CELLS = a2_cells("wildcard")
LITERAL_A2_MB_CHUNK_CELLS = a2_mb_chunk_cells("literal")
WILDCARD_A2_MB_CHUNK_CELLS = a2_mb_chunk_cells("wildcard")
LITERAL_B2_BOOLEAN_CELLS = b2_boolean_cells("literal")
WILDCARD_B2_BOOLEAN_CELLS = b2_boolean_cells("wildcard")

assert tuple(LITERAL_SCHEDULE) == SCHEDULE_IDS
assert tuple(WILDCARD_SCHEDULE) == SCHEDULE_IDS
assert len(wildcard_population_atoms()) == 21
assert all("NEAR" not in query.upper() for query in LITERAL_SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all(query.count("*") == 3 for query in WILDCARD_SCHEDULE.values())
assert sum(
    len(re.findall(r'"[^"]+"', cell["query"].split(" AND ")[-1]))
    for cell in LITERAL_A2_MB_CHUNK_CELLS
) == len(TERMS["M_B"])
assert all(
    "~" not in query
    for query in (*LITERAL_SCHEDULE.values(), *WILDCARD_SCHEDULE.values())
)
