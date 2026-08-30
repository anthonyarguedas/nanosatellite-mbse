"""Shared Pilot 004 ARC diagnostic construction and offline checks.

This module deliberately imports Pilot 003's normative literals, pairs, and
Boolean builders.  It never copies a concept block into the Pilot 004 code.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "source-specific" / "aiaa-arc" / "pilots" / "004"
SEARCH_DIR = PILOT_DIR / "searches"
PRIMARY_DIR = SEARCH_DIR / "primary"
UNION_DIR = SEARCH_DIR / "unions"
RECALL_DIR = SEARCH_DIR / "recall"
PILOT003_SCRIPTS = ROOT / "scripts" / "aiaa_arc_pilot003"
if str(PILOT003_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PILOT003_SCRIPTS))

from queries import (  # noqa: E402 - import path is intentionally local to SLR1.
    BLOCKS,
    C1_ANCHORS,
    C1_PAIR_LEFTS,
    C1_TERMS,
    EF_TERMS,
    EH_TERMS,
    GMODEL_PAIR_LEFTS,
    GMODEL_TERMS,
    GSTRUCTURE_PRODUCT_LEFTS,
    GSTRUCTURE_TERMS,
    GSTRUCTURE_VARIATION_LEFTS,
    MB_TERMS,
    METADATA_FIELDS,
    MH_TERMS,
    MODEL_ARCHITECTURE_ANCHORS,
    P_TERMS,
    R_TERMS,
    SCHEDULE,
    SCHEDULE_IDS,
    T2_PAIRS,
    T2_SUBBLOCKS,
    and_blocks,
    first_stage_rows,
    refinement_rows,
    semantic_query,
)

DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
KNOWN_DOI = "10.2514/6.2015-4474"
KNOWN_TITLE = (
    "CubeSat Model Based System Engineering (MBSE) Reference Model - "
    "Application in the Concept Lifecycle Phase"
)

ARC_FIELD_VALUES = {
    "Anywhere": "AllField",
    "Title": "Title",
    "Keyword": "Keyword",
    "Abstract": "Abstract",
}
ARC_FIELD_LABELS = {
    "Anywhere": "Anywhere",
    "Title": "Title",
    "Keyword": "Keywords",
    "Abstract": "Abstract",
}
TARGET_SLUG = {
    "M_H": "MH",
    "M_H_OR_M_B": "MH-or-MB",
    "M_B": "MB",
    "G_model": "Gmodel",
    "G_structure": "Gstructure",
    "C1": "C1",
}
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Cell:
    """One prospective source-native cell, with no scientific decision implied."""

    schedule_id: str
    cell_id: str
    rows: tuple[tuple[str, str], ...]
    stage: str
    parent_cell_id: str | None = None
    t2_index: int | None = None

    @property
    def semantic_query(self) -> str:
        return semantic_query(self.schedule_id)


def ensure_directories() -> None:
    for directory in (PILOT_DIR, SEARCH_DIR, PRIMARY_DIR, UNION_DIR, RECALL_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write once; pilot artifacts are immutable after a source attempt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def canonical_doi(value: str) -> str:
    """Use Pilot 003's DOI-first identity before ARC collection suffixes."""
    return value.strip().casefold().split("@", 1)[0]


def expected_field_rows(rows: Iterable[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "field": ARC_FIELD_VALUES[field],
            "label": ARC_FIELD_LABELS[field],
            "text": text,
        }
        for field, text in rows
    ]


def primary_cells(schedule_id: str) -> tuple[Cell, ...]:
    """Pilot 003's P-in-Title/Keywords/Abstract union, with T2 subcells."""
    if schedule_id not in SCHEDULE_IDS:
        raise ValueError(f"Unknown schedule ID: {schedule_id}")
    if schedule_id != "BT2":
        return tuple(
            Cell(
                schedule_id=schedule_id,
                cell_id=f"{schedule_id}-P-{field.lower()}",
                rows=first_stage_rows(schedule_id, field),
                stage="metadata_population_field_union",
            )
            for field in METADATA_FIELDS
        )
    cells: list[Cell] = []
    for population_field in METADATA_FIELDS:
        for index, subblock in enumerate(T2_SUBBLOCKS):
            cells.append(
                Cell(
                    schedule_id="BT2",
                    cell_id=(
                        f"BT2-P-{population_field.lower()}-T2-"
                        f"{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}"
                    ),
                    rows=(
                        (population_field, BLOCKS["P"]),
                        ("Anywhere", and_blocks(BLOCKS["M_B"], subblock)),
                    ),
                    stage="metadata_population_field_union_lossless_t2_or_subcell",
                    parent_cell_id=f"BT2-P-{population_field.lower()}",
                    t2_index=index,
                )
            )
    return tuple(cells)


def refinement_cells(schedule_id: str) -> tuple[Cell, ...]:
    """The lossless 3-by-3 defining-block refinement for one partition."""
    if schedule_id == "BT2":
        cells: list[Cell] = []
        for population_field in METADATA_FIELDS:
            for defining_field in METADATA_FIELDS:
                for index, subblock in enumerate(T2_SUBBLOCKS):
                    cells.append(
                        Cell(
                            schedule_id="BT2",
                            cell_id=(
                                f"BT2-P-{population_field.lower()}-MB-"
                                f"{defining_field.lower()}-T2-"
                                f"{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}"
                            ),
                            rows=(
                                (population_field, BLOCKS["P"]),
                                (defining_field, BLOCKS["M_B"]),
                                ("Anywhere", subblock),
                            ),
                            stage="metadata_population_and_defining_block_3_by_3_t2_or_subcell",
                            t2_index=index,
                        )
                    )
        return tuple(cells)
    entry = SCHEDULE[schedule_id]
    slug = TARGET_SLUG[entry["defining_name"]]
    return tuple(
        Cell(
            schedule_id=schedule_id,
            cell_id=(
                f"{schedule_id}-P-{population_field.lower()}-{slug}-"
                f"{defining_field.lower()}"
            ),
            rows=refinement_rows(schedule_id, population_field, defining_field),
            stage="metadata_population_and_defining_block_3_by_3",
        )
        for population_field in METADATA_FIELDS
        for defining_field in METADATA_FIELDS
    )


def final_cells(primary_sums: dict[str, int]) -> tuple[Cell, ...]:
    """Use refinement only where the P-field conservative sum exceeds 100."""
    output: list[Cell] = []
    for schedule_id in SCHEDULE_IDS:
        if primary_sums[schedule_id] > 100:
            output.extend(refinement_cells(schedule_id))
        else:
            output.extend(primary_cells(schedule_id))
    return tuple(output)


def final_cells_by_schedule(primary_sums: dict[str, int]) -> dict[str, tuple[Cell, ...]]:
    return {
        schedule_id: tuple(cell for cell in final_cells(primary_sums) if cell.schedule_id == schedule_id)
        for schedule_id in SCHEDULE_IDS
    }


def recall_cells() -> dict[str, tuple[Cell, ...]]:
    """Cells sufficient to test the known item's membership in each applicable union.

    The target's P and M blocks are source-located in its title, so the Title/
    Title assignments test a real member of the proposed union.  BT2 retains
    all four disjoint T2 subcells; no T2 alternative is silently dropped.
    """
    output: dict[str, tuple[Cell, ...]] = {}
    for schedule_id in ("A2", "B1", "B2"):
        entry = SCHEDULE[schedule_id]
        slug = TARGET_SLUG[entry["defining_name"]]
        output[schedule_id] = (
            Cell(
                schedule_id=schedule_id,
                cell_id=f"{schedule_id}-P-title-{slug}-title",
                rows=refinement_rows(schedule_id, "Title", "Title"),
                stage="known_item_recall_3_by_3_member",
            ),
        )
    output["BC1"] = (
        Cell(
            schedule_id="BC1",
            cell_id="BC1-P-title",
            rows=first_stage_rows("BC1", "Title"),
            stage="known_item_recall_population_union_member",
        ),
    )
    output["BT2"] = tuple(
        Cell(
            schedule_id="BT2",
            cell_id=(
                f"BT2-P-title-MB-title-T2-{index + 1:02d}-"
                f"of-{len(T2_SUBBLOCKS):02d}"
            ),
            rows=(
                ("Title", BLOCKS["P"]),
                ("Title", BLOCKS["M_B"]),
                ("Anywhere", subblock),
            ),
            stage="known_item_recall_3_by_3_lossless_t2_or_subcell",
            t2_index=index,
        )
        for index, subblock in enumerate(T2_SUBBLOCKS)
    )
    return output


def artifact_path(directory: Path, cell: Cell, suffix: str = "") -> Path:
    return directory / f"{cell.cell_id}{suffix}.json"


def failure_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE{path.suffix}")


def successful_attempt(base: Path) -> Path | None:
    """Return the first normal/retry artifact, never hiding prior failures."""
    if base.exists():
        return base
    for retry in range(1, 4):
        candidate = base.with_name(f"{base.stem}-retry{retry}{base.suffix}")
        if candidate.exists():
            return candidate
    return None


def next_attempt(base: Path) -> Path | None:
    """Choose a never-used output path while preserving every failure sidecar."""
    if successful_attempt(base) is not None:
        return None
    if not failure_path(base).exists():
        return base
    for retry in range(1, 4):
        candidate = base.with_name(f"{base.stem}-retry{retry}{base.suffix}")
        if candidate.exists():
            return None
        if not failure_path(candidate).exists():
            return candidate
    return None


def strategy_from_artifact(data: dict[str, Any]) -> dict[str, Any]:
    try:
        strategy = data["output_metadata"]["prisma_search_run"]["strategy"]
    except (KeyError, TypeError) as error:
        raise ValueError("artifact has no compact PRISMA strategy receipt") from error
    if not isinstance(strategy, dict):
        raise ValueError("artifact strategy receipt is not an object")
    return strategy


def artifact_total(data: dict[str, Any]) -> int:
    total = data.get("total")
    if not isinstance(total, int) or total < 0:
        raise ValueError("artifact total is not a nonnegative integer")
    return total


def validate_artifact_common(data: dict[str, Any], cell: Cell) -> list[str]:
    """Validate the compact normal-CLI projection without reconstituting it."""
    errors: list[str] = []
    if data.get("source") != "AIAA Aerospace Research Central (ARC)":
        errors.append("wrong source")
    metadata = data.get("output_metadata", {})
    merge_eligible = data.get("merge_eligible", metadata.get("merge_eligible"))
    if data.get("do_not_merge") is not True or merge_eligible is not False:
        errors.append("artifact is not explicitly non-mergeable")
    try:
        artifact_total(data)
    except ValueError as error:
        errors.append(str(error))
    try:
        strategy = strategy_from_artifact(data)
    except ValueError as error:
        return [*errors, str(error)]
    if strategy.get("field_rows") != expected_field_rows(cell.rows):
        errors.append("field rows differ from the exact generated cell")
    limits = strategy.get("limits", {})
    if not isinstance(limits, dict):
        errors.append("missing strategy limits")
    else:
        if limits.get("language_filter") is not None:
            errors.append("unexpected language filter")
        if limits.get("publication_type_filter") is not None:
            errors.append("unexpected publication-type filter")
        if limits.get("open_access_filter") is not None:
            errors.append("unexpected access restriction")
        access = limits.get("access", {})
        if not isinstance(access, dict) or access.get("requested") != "all" or access.get("effective") != "All content":
            errors.append("ARC access was not the unrestricted All content state")
        if limits.get("topic", {}).get("state") != "not_applied":
            errors.append("unexpected Topic selection")
        if limits.get("published_in", {}).get("state") != "not_applied" or limits.get("venue_filter") is not None:
            errors.append("unexpected venue restriction")
        facets = limits.get("result_facets", {})
        # The compact receipt records ARC's empty source echo as `applied`.
        # Only an actual requested/effective facet value would be narrowing.
        if not isinstance(facets, dict) or facets.get("value", facets.get("requested", [])) not in ([], None):
            errors.append("unexpected result facet")
        if limits.get("date_start") != DATE_START or limits.get("date_end") != DATE_END:
            errors.append("requested exact diagnostic dates differ")
    text = " ".join(part for _, part in cell.rows)
    if "*" in text or "?" in text:
        errors.append("wildcard appeared in a generated field row")
    return errors


def validate_preview_artifact(data: dict[str, Any], cell: Cell) -> list[str]:
    errors = validate_artifact_common(data, cell)
    total = data.get("total")
    rows = data.get("results")
    metadata = data.get("output_metadata", {})
    if metadata.get("status") != "preview":
        errors.append("preview artifact does not have preview status")
    if metadata.get("retrieval_complete") is not True:
        errors.append("preview did not retrieve the complete cell")
    if not isinstance(rows, list) or not isinstance(total, int) or len(rows) != total:
        errors.append("preview rows do not reconcile to the source total")
    elif total <= 0:
        errors.append("zero-result cells must use count-only fallback, not preview")
    else:
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("doi"), str) or not row["doi"].strip():
                errors.append("preview row lacks a stable DOI")
                break
            if row.get("previewOnly") is not True:
                errors.append("preview row is not marked preview-only")
                break
    return errors


def validate_zero_count_artifact(data: dict[str, Any], cell: Cell) -> list[str]:
    errors = validate_artifact_common(data, cell)
    metadata = data.get("output_metadata", {})
    if metadata.get("status") != "count_only":
        errors.append("zero fallback does not have count-only status")
    if data.get("total") != 0:
        errors.append("zero fallback did not observe an exact zero")
    if data.get("results") != []:
        errors.append("zero fallback retained records")
    return errors


def tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.casefold())


def phrase_spans(text: str, phrase: str) -> list[tuple[int, int]]:
    haystack = tokens(text)
    needle = tokens(phrase)
    if not needle:
        return []
    return [
        (index, index + len(needle))
        for index in range(len(haystack) - len(needle) + 1)
        if haystack[index : index + len(needle)] == needle
    ]


def literal_hits(text: str, alternatives: Iterable[str]) -> list[str]:
    return [term for term in alternatives if phrase_spans(text, term)]


def pair_hits(text: str, pairs: Iterable[tuple[str, str]]) -> list[dict[str, str]]:
    """Apply the protocol's either-order, at-most-five-intervening-token rule."""
    hits: list[dict[str, str]] = []
    for left, right in pairs:
        left_spans = phrase_spans(text, left)
        right_spans = phrase_spans(text, right)
        if any(
            max(left_start, right_start) - min(left_end, right_end) <= 5
            for left_start, left_end in left_spans
            for right_start, right_end in right_spans
        ):
            hits.append({"left": left, "right": right})
    return hits


def all_pairs(lefts: Iterable[str], rights: Iterable[str]) -> tuple[tuple[str, str], ...]:
    return tuple((left, right) for left in lefts for right in rights)


def visible_block_hits(text: str, name: str) -> dict[str, Any]:
    """Exact title-only warning check; never a source-side mismatch judgment."""
    definitions: dict[str, tuple[tuple[str, ...], tuple[tuple[str, str], ...]]] = {
        "P": (P_TERMS, ()),
        "E_H": (EH_TERMS, ()),
        "E_F": (EF_TERMS, ()),
        "M_H": (MH_TERMS, ()),
        "M_B": (MB_TERMS, ()),
        "R": (R_TERMS, ()),
        "G_model": (
            GMODEL_TERMS,
            all_pairs(GMODEL_PAIR_LEFTS, MODEL_ARCHITECTURE_ANCHORS),
        ),
        "G_structure": (
            GSTRUCTURE_TERMS,
            all_pairs(GSTRUCTURE_PRODUCT_LEFTS, ("model", "models"))
            + all_pairs(GSTRUCTURE_VARIATION_LEFTS, MODEL_ARCHITECTURE_ANCHORS),
        ),
        "C1": (C1_TERMS, all_pairs(C1_PAIR_LEFTS, C1_ANCHORS)),
        "T2": ((), T2_PAIRS),
    }
    if name == "M_H_OR_M_B":
        left = visible_block_hits(text, "M_H")
        right = visible_block_hits(text, "M_B")
        return {
            "block": name,
            "literal_hits": sorted(set(left["literal_hits"] + right["literal_hits"])),
            "pair_hits": [],
            "matched": bool(left["matched"] or right["matched"]),
        }
    literals, pairs = definitions[name]
    literal = literal_hits(text, literals)
    paired = pair_hits(text, pairs)
    return {
        "block": name,
        "literal_hits": literal,
        "pair_hits": paired,
        "matched": bool(literal or paired),
    }


def scheduled_visible_blocks(schedule_id: str) -> tuple[str, ...]:
    entry = SCHEDULE[schedule_id]
    blocks = ["P", entry["defining_name"]]
    if entry["third_name"] is not None:
        blocks.append(entry["third_name"])
    return tuple(blocks)


# Invariants guard against drift when Pilot 003's normative construction changes.
assert len(SCHEDULE_IDS) == 9
assert len(P_TERMS) == 26 and len(EH_TERMS) == 38 and len(EF_TERMS) == 37
assert len(MH_TERMS) == 54 and len(MB_TERMS) == 31 and len(R_TERMS) == 55
assert len(T2_PAIRS) == 224 and len(T2_SUBBLOCKS) == 4
assert all(subblock.count(" OR ") + 1 == 56 for subblock in T2_SUBBLOCKS)
assert all("*" not in block and "?" not in block for block in BLOCKS.values())
