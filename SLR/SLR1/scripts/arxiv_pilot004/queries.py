"""Build the arXiv browser cells for Pilot 004.

The term lists come from the accepted post-proximity schedule used by ATAI
Pilot 007. This module changes only the source rendering. Every browser row is
one homogeneous OR block in the rendered Advanced Search All-fields control.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

SOURCE_TERMS_PATH = (
    Path(__file__).resolve().parents[1] / "atai_pilot007" / "queries.py"
)
spec = importlib.util.spec_from_file_location("arxiv_p004_source_terms", SOURCE_TERMS_PATH)
if spec is None or spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not load {SOURCE_TERMS_PATH}")
terms = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = terms
spec.loader.exec_module(terms)

PROTOCOL_COMMIT = terms.PROTOCOL_COMMIT
SCHEDULE_IDS = terms.SCHEDULE_IDS


@dataclass(frozen=True)
class Cell:
    partition_id: str
    cell_number: int
    cell_count: int
    branch: str
    factors: tuple[str, ...]
    rows: tuple[str, ...]

    @property
    def cell_id(self) -> str:
        return f"{self.partition_id}-cell-{self.cell_number:02d}-of-{self.cell_count:02d}"

    @property
    def serialized_query(self) -> str:
        return "; ".join(f"AND all={row}" for row in self.rows)

    @property
    def query_sha256(self) -> str:
        return hashlib.sha256(self.serialized_query.encode()).hexdigest()


def quoted_or(values: Iterable[str]) -> str:
    values = tuple(values)
    if not values:
        raise ValueError("An arXiv OR row needs at least one literal")
    if any('"' in value or not value.strip() for value in values):
        raise ValueError("arXiv Pilot 004 literals must be nonempty and quote-free")
    return " OR ".join(f'"{value}"' for value in values)


BLOCK_ROWS = {
    "P": quoted_or(terms.P_TERMS),
    "E_H": quoted_or(terms.EH_TERMS),
    "E_F": quoted_or(terms.EF_TERMS),
    "M_H": quoted_or(terms.MH_TERMS),
    "M_B": quoted_or(terms.MB_TERMS),
    "M": quoted_or((*terms.MH_TERMS, *terms.MB_TERMS)),
    "R": quoted_or(terms.R_TERMS),
    "G_model_direct": quoted_or(
        (*terms.GMODEL_FIXED_TERMS, *terms.GMISSION_EXACT_TERMS)
    ),
    "G_mission": quoted_or(terms.GMISSION_TERMS),
    "G_structure_direct": quoted_or(
        (
            *terms.GSTRUCTURE_FIXED_TERMS,
            *terms.GPRODUCT_EXACT_TERMS,
            *terms.GVARIATION_TERMS,
        )
    ),
    "G_product": quoted_or(terms.GPRODUCT_TERMS),
    "C1": quoted_or((*terms.C1_FIXED_TERMS, *terms.GDSL_TERMS)),
    "T_precise": quoted_or(terms.TPRECISE_TERMS),
}

CELL_FACTORS = {
    "A1": (("direct", ("P", "E_H", "M_H")),),
    "A2": (
        ("M_H-branch", ("P", "E_F", "M_H")),
        ("M_B-branch", ("P", "E_F", "M_B")),
    ),
    "A3": (("direct", ("P", "E_H", "M_B")),),
    "B1": (("direct", ("P", "M_H")),),
    "B2": (("direct", ("P", "M_B", "R")),),
    "BG1": (
        ("fixed-or-exact", ("P", "G_model_direct")),
        ("mission-marker-and-M_B", ("P", "G_mission", "M_B")),
    ),
    "BG2": (
        ("fixed-exact-or-variation", ("P", "G_structure_direct")),
        ("product-marker-and-M_B", ("P", "G_product", "M_B")),
    ),
    "BC1": (("direct", ("P", "C1")),),
    "BT2": (("direct", ("P", "M_B", "T_precise")),),
}


def build_cells() -> tuple[Cell, ...]:
    cells: list[Cell] = []
    for partition_id in SCHEDULE_IDS:
        declarations = CELL_FACTORS[partition_id]
        for index, (branch, factors) in enumerate(declarations, start=1):
            cells.append(
                Cell(
                    partition_id=partition_id,
                    cell_number=index,
                    cell_count=len(declarations),
                    branch=branch,
                    factors=factors,
                    rows=tuple(BLOCK_ROWS[factor] for factor in factors),
                )
            )
    return tuple(cells)


CELLS = build_cells()

assert tuple(CELL_FACTORS) == SCHEDULE_IDS
assert len(CELLS) == 12
assert all(len(cell.rows) in {2, 3} for cell in CELLS)
assert all("*" not in row and "?" not in row and "~" not in row for cell in CELLS for row in cell.rows)
assert all("(" not in row and ")" not in row for cell in CELLS for row in cell.rows)
