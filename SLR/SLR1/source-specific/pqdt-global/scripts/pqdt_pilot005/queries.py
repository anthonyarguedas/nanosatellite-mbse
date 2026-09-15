"""Pinned inputs and query helpers for PQDT Global Pilot 005."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

SLR1_ROOT = Path(__file__).resolve().parents[4]
PILOT_ROOT = (
    SLR1_ROOT / "source-specific" / "pqdt-global" / "pilots" / "005"
)
PILOT004_ROOT = PILOT_ROOT.parent / "004"
PILOT004_QUERY_MODULE = (
    SLR1_ROOT
    / "source-specific"
    / "pqdt-global"
    / "scripts"
    / "pqdt_pilot004"
    / "queries.py"
)
PILOT004_EVENT_PLAN = PILOT004_ROOT / "searches" / "event-plan.json"
PILOT004_ASSESSMENT = PILOT004_ROOT / "searches" / "assessment.json"
ADAPTER_PATH = (
    Path.home() / "agent-tools" / "internet" / "skills" / "browser" / "scripts" / "search_pqdt.py"
)
UNION_BRIDGE_PATH = Path(__file__).resolve().with_name("pqdt_union_bridge.py")

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
EXPECTED_PILOT004_QUERY_SHA256 = (
    "6bcbb133a45819b084fabd5518d241be16633c8e0266c759ad0f247f4147ce19"
)
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DIAGNOSTIC_YEAR_START = 2011
DIAGNOSTIC_YEAR_END = 2026
DIAGNOSTIC_CUTOFF = "2026-08-29"
LANGUAGE = "English"

SELECTED_KNOWN_RECORDS: tuple[dict[str, Any], ...] = (
    {
        "paper_id": "2838438016",
        "title": "Development of a Cubesat Conceptual Design Tool and Implementation of the EPS Design Module",
        "pilot004_partitions": ["A1", "B1"],
    },
    {
        "paper_id": "2838439210",
        "title": "Sysml Based Cubesat Model Design and Integration with the Horizon Simulation Framework",
        "pilot004_partitions": ["B1", "B2"],
    },
    {
        "paper_id": "2050565383",
        "title": "Model-based (MBSE) System Architecture Development for a Hybrid Inter-satellite Communication System",
        "pilot004_partitions": ["B1", "B2", "BC1"],
    },
    {
        "paper_id": "2838438905",
        "title": "Analysis of Verification and Validation Techniques for Educational Cubesat Programs",
        "pilot004_partitions": ["B1"],
    },
    {
        "paper_id": "2796603206",
        "title": "A Novel Graph-Based Modelling Approach for Reducing Complexity in Model-Based Systems Engineering Environment",
        "pilot004_partitions": ["B1"],
    },
    {
        "paper_id": "2459205256",
        "title": "A Standard Methodology Enabling Execution of Models Described in Sysml Demonstrated in a Model Based Systems Engineering Approach Toward Developing a Space Situational Awareness System Implemented in CubeSats",
        "pilot004_partitions": ["B1", "B2"],
    },
    {
        "paper_id": "2697136573",
        "title": "A Model-based Methodology for Strategic Reuse of Legacy Designs in Space Mission Architecting",
        "pilot004_partitions": ["B1"],
    },
    {
        "paper_id": "2828592607",
        "title": "Sealion Cubesat Mission Architecture Using Model Based Systems Engineering with a Docs as Code Approach",
        "pilot004_partitions": ["B1"],
    },
    {
        "paper_id": "3039685878",
        "title": "Enabling Lunar Cubesat Missions With the Cubesat System Reference Model",
        "pilot004_partitions": ["B1", "B2", "BC1"],
    },
    {
        "paper_id": "3059245100",
        "title": "Development of a Digital Engineering Testing Framework for CubeSat Applications",
        "pilot004_partitions": ["B2"],
    },
    {
        "paper_id": "3241100212",
        "title": "Model-Based Systems Engineering for Aerospace Applications: Strategic Requirements Prioritization in Complex Adaptive Systems and Digital Integration",
        "pilot004_partitions": ["B1", "B2", "BT2"],
    },
    {
        "paper_id": "3244643407",
        "title": "A Scalable System Architecture for CubeSat Test & Evaluation for Enhanced Mission Success",
        "pilot004_partitions": ["B1"],
    },
    {
        "paper_id": "3291109676",
        "title": "A Tailored Systems Engineering Process for Developing Student-Built CubeSat Class Satellites",
        "pilot004_partitions": ["B1"],
    },
    {
        "paper_id": "3304631814",
        "title": "Developing a Model-Based System Engineering Methodology for CubeSat Missions",
        "pilot004_partitions": ["B1", "B2", "BG1"],
    },
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def ordered_id_sha256(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def _load_pilot004_queries() -> Any:
    if file_sha256(PILOT004_QUERY_MODULE) != EXPECTED_PILOT004_QUERY_SHA256:
        raise RuntimeError("The accepted PQDT Pilot 004 query module changed")
    spec = importlib.util.spec_from_file_location(
        "pqdt_pilot005_pinned_pilot004_queries", PILOT004_QUERY_MODULE
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the accepted PQDT Pilot 004 queries")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
        raise RuntimeError("PQDT Pilot 004 uses a different protocol commit")
    return module


PILOT004_QUERIES = _load_pilot004_queries()
BLOCK_TERMS: dict[str, tuple[str, ...]] = {
    name: tuple(values) for name, values in PILOT004_QUERIES.BLOCK_TERMS.items()
}
FREE_TEXT_ORDINARY_BLOCKS: dict[str, str] = dict(
    PILOT004_QUERIES.WILDCARD_ORDINARY_BLOCKS
)
FREE_TEXT_COMPOUND_BLOCKS: dict[str, str] = dict(
    PILOT004_QUERIES.WILDCARD_COMPOUND_BLOCKS
)
FREE_TEXT_SCHEDULE: dict[str, str] = dict(PILOT004_QUERIES.WILDCARD_SCHEDULE)


def any_of(*expressions: str) -> str:
    cleaned = tuple(expression.strip() for expression in expressions if expression.strip())
    if not cleaned:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(cleaned) + ")"


def all_of(*expressions: str) -> str:
    cleaned = tuple(expression.strip() for expression in expressions if expression.strip())
    if not cleaned:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(cleaned) + ")"


def exact_clause(field: str, term: str) -> str:
    if field not in {"PSUB", "IF"}:
        raise ValueError(f"Unsupported PQDT descriptor field: {field}")
    if not term or '"' in term:
        raise ValueError("PQDT descriptor labels must be nonempty and quote-free")
    return f"{field}.EXACT({json.dumps(term, ensure_ascii=False)})"


def descriptor_block(candidates: Iterable[Mapping[str, Any]]) -> str | None:
    clauses = [
        exact_clause(str(item["field"]), str(item["term"]))
        for item in candidates
        if item.get("adoption_candidate") is True
    ]
    return any_of(*clauses) if clauses else None


def union_block(free_text: str, descriptor: str | None) -> str:
    return any_of(free_text, descriptor) if descriptor else free_text


def build_augmented_schedule_from_expressions(
    descriptor_expressions: Mapping[str, str],
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    unknown = set(descriptor_expressions) - set(FREE_TEXT_ORDINARY_BLOCKS)
    if unknown:
        raise RuntimeError(f"Unknown protocol blocks in descriptor map: {sorted(unknown)!r}")
    ordinary: dict[str, str] = {}
    for block, free_text in FREE_TEXT_ORDINARY_BLOCKS.items():
        descriptor = str(descriptor_expressions.get(block, "")).strip() or None
        ordinary[block] = union_block(free_text, descriptor)
    compound = PILOT004_QUERIES.compound_blocks(ordinary)
    schedule = PILOT004_QUERIES.schedule(ordinary, compound)
    if tuple(schedule) != SCHEDULE_IDS:
        raise RuntimeError("The augmented PQDT schedule changed partition order")
    return ordinary, compound, schedule


def build_augmented_schedule(
    candidates_by_block: Mapping[str, Iterable[Mapping[str, Any]]],
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    descriptor_expressions = {
        block: expression
        for block, candidates in candidates_by_block.items()
        if (expression := descriptor_block(candidates)) is not None
    }
    return build_augmented_schedule_from_expressions(descriptor_expressions)


assert tuple(FREE_TEXT_SCHEDULE) == SCHEDULE_IDS
assert len(SELECTED_KNOWN_RECORDS) == len(
    {record["paper_id"] for record in SELECTED_KNOWN_RECORDS}
)
