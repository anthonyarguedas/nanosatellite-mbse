#!/usr/bin/env python3
"""Build the all-partition wildcard population plan for IAF Pilot 006."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

PILOT = "006"
SCHEMA = "iaf-digital-library-pilot006-cell-plan/v1"
PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
MAX_QUERY_CHARACTERS = 500

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / PILOT
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "cell-plan.json"
PILOT003_ROOT = SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / "003"
PILOT004_ROOT = SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / "004"
PILOT004_SCRIPT_DIR = SLR1_DIR / "source-specific" / "iaf-digital-library" / "scripts" / "iaf_digital_library_pilot004"

if str(PILOT004_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT004_SCRIPT_DIR))
explicit = importlib.import_module("plan")
queries = importlib.import_module("queries")

WILDCARD_POPULATION_ATOMS = (
    "CubeSat*",
    '"cube sat*"',
    "cube-sat*",
    "nanosat*",
    "nano-sat*",
    '"nano sat*"',
    "SmallSat*",
    '"small sat*"',
)
EXPECTED_CELL_COUNTS = {
    "A1": 37,
    "A2": 48,
    "A3": 21,
    "B1": 4,
    "B2": 20,
    "BG1": 6,
    "BG2": 6,
    "BC1": 3,
    "BT2": 13,
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def wildcard_population_factor() -> Any:
    return explicit.Factor(
        name="P_wildcard",
        alternatives=tuple(
            explicit.Alternative(ordinal=index, text=atom)
            for index, atom in enumerate(WILDCARD_POPULATION_ATOMS, start=1)
        ),
    )


def factor_for(name: str) -> Any:
    return wildcard_population_factor() if name == "P" else explicit.factor_for(name)


def build_partitions() -> dict[str, Any]:
    partitions: dict[str, Any] = {}
    for partition_id in queries.SCHEDULE_IDS:
        branch_entries = []
        flat_cells = []
        next_cell = 1
        for branch_id, factor_names in queries.PARTITION_BRANCHES[partition_id]:
            factors = tuple(factor_for(name) for name in factor_names)
            packed = explicit.pack_factors(factors)
            certificate = explicit.coverage_certificate(factors, packed)
            if certificate.get("exactly_once") is not True:
                raise RuntimeError(f"Coverage failed for {partition_id}/{branch_id}")
            branch_cells = []
            for branch_cell_number, groups in enumerate(packed, start=1):
                query = explicit.render_groups(groups)
                cell = {
                    "cell_id": f"cell-{next_cell:04d}",
                    "branch_cell_id": f"{branch_id}-{branch_cell_number:04d}",
                    "branch_id": branch_id,
                    "query": query,
                    "query_characters": len(query),
                    "query_sha256": text_sha256(query),
                    "factor_ranges": [
                        {
                            "factor_index": factor_index,
                            "factor": factor.name,
                            "alternative_range": explicit.group_range(group),
                        }
                        for factor_index, (factor, group) in enumerate(
                            zip(factors, groups), start=1
                        )
                    ],
                }
                branch_cells.append(cell)
                flat_cells.append(cell)
                next_cell += 1
            branch_entries.append(
                {
                    "branch_id": branch_id,
                    "factor_names": [
                        "P_wildcard" if name == "P" else name for name in factor_names
                    ],
                    "factor_alternative_counts": [
                        len(factor.alternatives) for factor in factors
                    ],
                    "packed_cell_count": len(branch_cells),
                    "cell_character_range": {
                        "minimum": min(
                            cell["query_characters"] for cell in branch_cells
                        ),
                        "maximum": max(
                            cell["query_characters"] for cell in branch_cells
                        ),
                    },
                    "coverage_certificate": certificate,
                    "cells": branch_cells,
                }
            )
        if len(flat_cells) != EXPECTED_CELL_COUNTS[partition_id]:
            raise RuntimeError(f"Unexpected cell count for {partition_id}")
        partitions[partition_id] = {
            "boolean_form": explicit.BOOLEAN_FORMS[partition_id],
            "branch_count": len(branch_entries),
            "packed_cell_count": len(flat_cells),
            "branches": branch_entries,
            "cells": flat_cells,
        }
    return partitions


def baseline_evidence() -> dict[str, Any]:
    pilot003_plan = PILOT003_ROOT / "searches" / "cell-plan.json"
    pilot003_assessment = PILOT003_ROOT / "searches" / "assessment.json"
    pilot004_plan = PILOT004_ROOT / "searches" / "cell-plan.json"
    pilot004_assessment = PILOT004_ROOT / "searches" / "assessment.json"
    old = load(pilot003_assessment)
    current = load(pilot004_assessment)
    entries = {}
    for partition_id in queries.SCHEDULE_IDS:
        source = old if partition_id in ("A1", "A2", "A3", "B1", "B2") else current
        entry = source["entries"][partition_id]
        entries[partition_id] = {
            "source_pilot": "003" if source is old else "004",
            "raw_count": entry["raw_paper_id_union"]["deduplicated_count"],
            "raw_ids": entry["raw_paper_id_union"]["paper_ids"],
            "diagnostic_window_count": entry["diagnostic_window_paper_id_union"][
                "deduplicated_count"
            ],
            "diagnostic_window_ids": entry["diagnostic_window_paper_id_union"][
                "paper_ids"
            ],
        }
    return {
        "scope": (
            "Pilot 003 supplies the unchanged A1 through B2 explicit unions. "
            "Pilot 004 supplies the current BG1, BG2, BC1, and BT2 explicit unions."
        ),
        "pilot003_plan": str(pilot003_plan.relative_to(SLR1_DIR)),
        "pilot003_plan_sha256": file_sha256(pilot003_plan),
        "pilot003_assessment": str(pilot003_assessment.relative_to(SLR1_DIR)),
        "pilot003_assessment_sha256": file_sha256(pilot003_assessment),
        "pilot004_plan": str(pilot004_plan.relative_to(SLR1_DIR)),
        "pilot004_plan_sha256": file_sha256(pilot004_plan),
        "pilot004_assessment": str(pilot004_assessment.relative_to(SLR1_DIR)),
        "pilot004_assessment_sha256": file_sha256(pilot004_assessment),
        "entries": entries,
    }


def build() -> dict[str, Any]:
    partitions = build_partitions()
    events = [
        {
            "event_id": f"wildcard-{partition_id.lower()}",
            "partition_id": partition_id,
            "mode": "strict_complete_cells",
            "query_cells": [
                {
                    "cell_id": cell["cell_id"],
                    "branch_id": cell["branch_id"],
                    "query": cell["query"],
                    "query_sha256": cell["query_sha256"],
                }
                for cell in partitions[partition_id]["cells"]
            ],
        }
        for partition_id in queries.SCHEDULE_IDS
    ]
    total_cells = sum(entry["packed_cell_count"] for entry in partitions.values())
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": {"id": "iaf_digital_library", "label": "IAF Digital Library"},
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test the eight-atom wildcard population translation in every current "
            "partition and compare complete stable-ID unions with the explicit schedule."
        ),
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "inclusive": True,
            "mode": "local post-filter after complete raw traversal",
        },
        "controls": {
            "database_scope": "full IAF Digital Library",
            "language": "not applied",
            "event": "not applied",
            "publication_type": "no added restriction",
            "access": "not applied",
            "source_date": "not applied",
            "controlled_vocabulary": "not applied",
            "proximity": False,
            "pair_expansion": False,
            "complete_source_total_cap": 5000,
            "maximum_query_characters": MAX_QUERY_CHARACTERS,
        },
        "wildcard_population": {
            "operator": "trailing *",
            "atoms": list(WILDCARD_POPULATION_ATOMS),
            "atom_count": len(WILDCARD_POPULATION_ATOMS),
            "replaces_explicit_population_term_count": 26,
            "validation_source": "IAF Pilot 005 positive BG1 fixed-branch comparison",
        },
        "packing": {
            "method": (
                "Pilot 004 nested contiguous factor packing with P replaced by the "
                "eight-atom wildcard factor"
            ),
            "lossless_candidate_coverage": (
                "Every branch certificate covers each wildcard-factor and ordinary-factor "
                "alternative tuple exactly once."
            ),
            "explicit_schedule_cells": 551,
            "wildcard_schedule_cells": total_cells,
            "cell_reduction": 551 - total_cells,
            "partition_cell_counts": EXPECTED_CELL_COUNTS,
        },
        "explicit_baseline": baseline_evidence(),
        "discrepancy_rule": {
            "missing_explicit_id": (
                "Stop adoption. Predeclare and run a fresh explicit schedule for each affected "
                "partition before attributing the difference to wildcard behavior."
            ),
            "wildcard_only_id": (
                "Inspect visible metadata and the matching wildcard family. Accept broader recall "
                "only when the suffix completion remains a population term in scope."
            ),
            "source_or_adapter_failure": (
                "Retain the failure and retry without changing the query. Do not convert a failure to zero."
            ),
        },
        "acceptance_checks": [
            "All 158 candidate cells complete strict two-pass capture with exact query readback.",
            "Every explicit baseline ID is present in the corresponding wildcard partition union.",
            "Every wildcard-only ID receives a recorded lexical and scope inspection.",
            "No result-driven filter or query refinement is introduced.",
            "The final decision distinguishes wildcard syntax approval from final-search execution.",
        ],
        "partitions": partitions,
        "events": events,
    }


def validate(payload: Mapping[str, Any]) -> list[str]:
    errors = []
    if payload.get("schema_version") != SCHEMA:
        errors.append("Plan schema changed")
    if payload.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Protocol commit changed")
    if payload.get("wildcard_population", {}).get("atoms") != list(
        WILDCARD_POPULATION_ATOMS
    ):
        errors.append("Wildcard atoms changed")
    if payload.get("packing", {}).get("partition_cell_counts") != EXPECTED_CELL_COUNTS:
        errors.append("Partition cell counts changed")
    if payload.get("packing", {}).get("wildcard_schedule_cells") != 158:
        errors.append("Total cell count changed")
    partitions = payload.get("partitions")
    if not isinstance(partitions, Mapping) or tuple(partitions) != queries.SCHEDULE_IDS:
        return [*errors, "Partition schedule changed"]
    for partition_id in queries.SCHEDULE_IDS:
        entry = partitions[partition_id]
        cells = entry.get("cells")
        if (
            not isinstance(cells, list)
            or len(cells) != EXPECTED_CELL_COUNTS[partition_id]
        ):
            errors.append(f"Cell schedule changed for {partition_id}")
            continue
        for index, cell in enumerate(cells, start=1):
            query = cell.get("query")
            if cell.get("cell_id") != f"cell-{index:04d}":
                errors.append(f"Cell order changed for {partition_id}")
            if not isinstance(query, str) or not query:
                errors.append(f"Missing query for {partition_id}/{index}")
                continue
            if len(query) > MAX_QUERY_CHARACTERS:
                errors.append(f"Over-cap query for {partition_id}/{index}")
            if cell.get("query_characters") != len(query) or cell.get(
                "query_sha256"
            ) != text_sha256(query):
                errors.append(f"Query evidence changed for {partition_id}/{index}")
            if "*" not in query or "NEAR" in query.upper() or " AND " in query:
                errors.append(f"Candidate syntax changed for {partition_id}/{index}")
        if any(
            branch.get("coverage_certificate", {}).get("exactly_once") is not True
            for branch in entry.get("branches", [])
        ):
            errors.append(f"Coverage certificate failed for {partition_id}")
    baseline = payload.get("explicit_baseline", {}).get("entries", {})
    if tuple(baseline) != queries.SCHEDULE_IDS:
        errors.append("Explicit baseline schedule changed")
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != 9:
        errors.append("Event schedule changed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        payload = load(args.output)
        errors = validate(payload)
        print(
            json.dumps(
                {"status": "ok" if not errors else "error", "errors": errors}, indent=2
            )
        )
        return 1 if errors else 0
    payload = build()
    errors = validate(payload)
    if errors:
        raise RuntimeError("Generated plan failed validation: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "saved": str(args.output),
                "partitions": len(payload["partitions"]),
                "wildcard_cells": payload["packing"]["wildcard_schedule_cells"],
                "explicit_cells": payload["packing"]["explicit_schedule_cells"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
