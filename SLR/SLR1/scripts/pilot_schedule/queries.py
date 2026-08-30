"""Build lossless source translations of the pilot query schedule.

The protocol literals and declared pairs remain defined in the Pilot 003 AIAA
module. This module adds the supporting-review blocks and source renderers. It
does not execute searches or select source controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
from typing import Callable, Iterable


_AIAA_QUERIES_PATH = (
    Path(__file__).resolve().parents[1] / "aiaa_arc_pilot003" / "queries.py"
)
_spec = spec_from_file_location("aiaa_arc_pilot003_queries", _AIAA_QUERIES_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {_AIAA_QUERIES_PATH}")
_aiaa = module_from_spec(_spec)
_spec.loader.exec_module(_aiaa)


@dataclass(frozen=True)
class Concept:
    literals: tuple[str, ...]
    pairs: tuple[tuple[str, str], ...] = ()

    @property
    def alternative_count(self) -> int:
        return len(self.literals) + len(self.pairs)


P = Concept(_aiaa.P_TERMS)
E_H = Concept(_aiaa.EH_TERMS)
E_F = Concept(_aiaa.EF_TERMS)
M_H = Concept(_aiaa.MH_TERMS)
M_B = Concept(_aiaa.MB_TERMS)
R = Concept(_aiaa.R_TERMS)
G_MODEL = Concept(
    _aiaa.GMODEL_TERMS,
    tuple(
        (left, right)
        for left in _aiaa.GMODEL_PAIR_LEFTS
        for right in _aiaa.MODEL_ARCHITECTURE_ANCHORS
    ),
)
G_STRUCTURE = Concept(
    _aiaa.GSTRUCTURE_TERMS,
    tuple(
        (left, right)
        for left in _aiaa.GSTRUCTURE_PRODUCT_LEFTS
        for right in ("model", "models")
    )
    + tuple(
        (left, right)
        for left in _aiaa.GSTRUCTURE_VARIATION_LEFTS
        for right in _aiaa.MODEL_ARCHITECTURE_ANCHORS
    ),
)
C1 = Concept(
    _aiaa.C1_TERMS,
    tuple(
        (left, right)
        for left in _aiaa.C1_PAIR_LEFTS
        for right in _aiaa.C1_ANCHORS
    ),
)
T2 = Concept((), _aiaa.T2_PAIRS)

_X_ADDITIONS = (
    "spacecraft",
    "space system",
    "space systems",
    "space mission",
    "space missions",
    "space engineering",
    "space systems engineering",
    "space application",
    "space applications",
    "space sector",
    "space industry",
    "satellite",
    "satellites",
)
X = Concept(tuple(dict.fromkeys((*P.literals, *_X_ADDITIONS))))
Q = Concept(
    (
        "systematic review",
        "systematic literature review",
        "systematic mapping",
        "systematic mapping study",
        "mapping study",
        "scoping review",
        "literature review",
        "literature survey",
        "bibliometric review",
        "bibliometric analysis",
        "evidence synthesis",
        "secondary study",
        "state-of-the-art review",
        "state of the art review",
        "survey paper",
        "survey",
    )
)

CONCEPTS = {
    "P": P,
    "E_H": E_H,
    "E_F": E_F,
    "M_H": M_H,
    "M_B": M_B,
    "R": R,
    "G_model": G_MODEL,
    "G_structure": G_STRUCTURE,
    "C1": C1,
    "T2": T2,
    "X": X,
    "Q": Q,
}

# Each partition is a conjunction of factors. A factor is the union of all
# alternatives in its named concepts.
MAIN_FACTORS = {
    "A1": (("P",), ("E_H",), ("M_H",)),
    "A2": (("P",), ("E_F",), ("M_H", "M_B")),
    "A3": (("P",), ("E_H",), ("M_B",)),
    "B1": (("P",), ("M_H",)),
    "B2": (("P",), ("M_B",), ("R",)),
    "BG1": (("P",), ("G_model",)),
    "BG2": (("P",), ("G_structure",)),
    "BC1": (("P",), ("C1",)),
    "BT2": (("P",), ("M_B",), ("T2",)),
}
PSR_FACTORS = {
    "PSR1": (("X",), ("M_H",), ("Q",)),
    "PSR2": (("X",), ("M_B",), ("R",), ("Q",)),
    "PSR3": (("P",), ("E_H", "E_F"), ("M_H", "M_B"), ("Q",)),
    "PSR4": (("X",), ("G_model", "G_structure", "C1"), ("Q",)),
}
SCHEDULE_FACTORS = {**MAIN_FACTORS, **PSR_FACTORS}


@dataclass(frozen=True)
class Renderer:
    source_id: str
    literal_atom: Callable[[str], str]
    pair_atom: Callable[[str, str], str]
    or_token: str = " OR "
    and_token: str = " AND "

    def alternatives(self, concept_names: Iterable[str]) -> tuple[str, ...]:
        values: list[str] = []
        for name in concept_names:
            concept = CONCEPTS[name]
            values.extend(self.literal_atom(value) for value in concept.literals)
            values.extend(self.pair_atom(left, right) for left, right in concept.pairs)
        return tuple(values)

    def union(self, alternatives: Iterable[str]) -> str:
        values = tuple(alternatives)
        if not values:
            raise ValueError("A source union cannot be empty")
        return f"({self.or_token.join(values)})"

    def partition(self, partition_id: str) -> str:
        factors = SCHEDULE_FACTORS[partition_id]
        return self.and_token.join(
            self.union(self.alternatives(names)) for names in factors
        )


def quoted(value: str) -> str:
    return f'"{value}"'


def _same_field_and(left: str, right: str) -> str:
    return f"({quoted(left)} AND {quoted(right)})"


def _same_field_space(left: str, right: str) -> str:
    return f"({quoted(left)} {quoted(right)})"


def _ntrs_pair(left: str, right: str) -> str:
    return f'("{left} {right}"~5 | "{right} {left}"~5)'


def _oatd_pair(left: str, right: str) -> str:
    clauses = []
    for field in ("title", "author", "abstract", "publisher", "subject", "discipline"):
        clauses.extend(
            (
                f'{field}:("{left} {right}"~5)',
                f'{field}:("{right} {left}"~5)',
            )
        )
    return f"({' OR '.join(clauses)})"


RENDERERS = {
    "scopus": Renderer(
        "scopus",
        lambda value: f"TITLE-ABS-KEY({quoted(value)})",
        lambda left, right: f"TITLE-ABS-KEY({quoted(left)} W/6 {quoted(right)})",
    ),
    "web_of_science_core_collection": Renderer(
        "web_of_science_core_collection",
        lambda value: f"TS=({quoted(value)})",
        lambda left, right: f"TS=({quoted(left)} NEAR/6 {quoted(right)})",
    ),
    "ieee_xplore": Renderer(
        "ieee_xplore",
        lambda value: f'("All Metadata":{quoted(value)})',
        lambda left, right: (
            f'(("All Metadata":{quoted(left)}) NEAR/6 '
            f'("All Metadata":{quoted(right)}))'
        ),
    ),
    "engineering_village_compendex_inspec": Renderer(
        "engineering_village_compendex_inspec",
        lambda value: f"({quoted(value)} WN ALL)",
        lambda left, right: f"(({quoted(left)} NEAR/5 {quoted(right)}) WN ALL)",
    ),
    "wiley_online_library": Renderer(
        "wiley_online_library", quoted, _same_field_and
    ),
    "springer_nature_link": Renderer(
        "springer_nature_link", quoted, _same_field_and
    ),
    "proquest_aerospace_index": Renderer(
        "proquest_aerospace_index",
        lambda value: f"NOFT({quoted(value)})",
        lambda left, right: f"NOFT({quoted(left)} NEAR/5 {quoted(right)})",
    ),
    "proquest_dissertations_theses_global": Renderer(
        "proquest_dissertations_theses_global",
        lambda value: f"NOFT({quoted(value)})",
        lambda left, right: f"NOFT({quoted(left)} NEAR/5 {quoted(right)})",
    ),
    "aiaa_arc": Renderer("aiaa_arc", quoted, _same_field_space, and_token=" "),
    "iaf_digital_library": Renderer(
        "iaf_digital_library", quoted, _same_field_space, and_token=" "
    ),
    "oatd": Renderer("oatd", quoted, _oatd_pair),
    "esa_indico": Renderer(
        "esa_indico",
        quoted,
        lambda left, right: f"{quoted(left)} NEAR/5 {quoted(right)}",
    ),
    "nasa_ntrs": Renderer(
        "nasa_ntrs", quoted, _ntrs_pair, or_token=" | ", and_token=" + "
    ),
}


def partition_query(source_id: str, partition_id: str) -> str:
    """Return one complete source expression without source controls."""
    return RENDERERS[source_id].partition(partition_id)


def _chunks_for_factor(
    renderer: Renderer,
    concept_names: tuple[str, ...],
    maximum_characters: int,
) -> tuple[tuple[str, ...], ...]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for alternative in renderer.alternatives(concept_names):
        candidate = [*current, alternative]
        if len(renderer.union(candidate)) <= maximum_characters:
            current = candidate
            continue
        if not current:
            raise ValueError(
                f"One {renderer.source_id} alternative exceeds the cell limit"
            )
        chunks.append(current)
        current = [alternative]
    if current:
        chunks.append(current)
    return tuple(tuple(chunk) for chunk in chunks)


def partition_cells(
    source_id: str,
    partition_id: str,
    *,
    maximum_characters: int,
) -> tuple[dict[str, str], ...]:
    """Split OR factors into a lossless Cartesian union below a fixed limit."""
    renderer = RENDERERS[source_id]
    factors = SCHEDULE_FACTORS[partition_id]
    # Reserve the complete conjunction overhead while making each factor chunk.
    factor_budget = maximum_characters - len(renderer.and_token) * (len(factors) - 1)
    chunked = [
        _chunks_for_factor(renderer, names, max(1, factor_budget // len(factors)))
        for names in factors
    ]
    cells: list[dict[str, str]] = []
    for index, selected in enumerate(product(*chunked), start=1):
        query = renderer.and_token.join(renderer.union(chunk) for chunk in selected)
        if len(query) > maximum_characters:
            raise ValueError(
                f"{source_id} {partition_id} cell {index} exceeds {maximum_characters}"
            )
        cells.append({"cell_id": f"cell-{index:04d}", "query": query})
    return tuple(cells)


def audit() -> dict[str, object]:
    return {
        "concept_counts": {
            name: {
                "literals": len(concept.literals),
                "pairs": len(concept.pairs),
                "alternatives": concept.alternative_count,
            }
            for name, concept in CONCEPTS.items()
        },
        "main_partitions": list(MAIN_FACTORS),
        "psr_partitions": list(PSR_FACTORS),
        "renderers": list(RENDERERS),
    }


assert len(X.literals) == 39
assert len(Q.literals) == 16
assert tuple(MAIN_FACTORS) == _aiaa.SCHEDULE_IDS
assert all("*" not in value and "?" not in value for value in X.literals + Q.literals)
