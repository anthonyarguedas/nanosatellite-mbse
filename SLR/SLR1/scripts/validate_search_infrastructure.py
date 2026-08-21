#!/usr/bin/env python3
"""Validate the new-run SLR1 search infrastructure without using prior-run data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCHES = ROOT / "searches"

DIRECT_IDS = {"A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2", "V1", "O1"}
CONCEPT_IDS = {
    "P",
    "E_H",
    "E_F",
    "E",
    "M_H",
    "M_B",
    "M",
    "R",
    "G_model",
    "G_structure",
    "C1",
    "T2",
    "E_probe",
    "M_probe",
    "V1",
    "O1",
}
EXPECTED_TERM_COUNTS = {
    "P": 10,
    "E_H": 10,
    "E_F": 15,
    "M_H": 9,
    "M_B": 9,
    "R": 17,
    "E_probe": 8,
    "M_probe": 6,
    "V1": 21,
    "O1": 31,
}
EXPECTED_TASKS = {
    "S-D01",
    "S-D02",
    "S-D03",
    "S-D04",
    "S-D05",
    "S-D06",
    "S-D07",
    "S-D08",
    "S-D09",
    "S-D10",
    "S-D11",
    "S-D12",
    "S-D13",
    "S-L02",
}


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expression_refs(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.get("args", []):
            yield from expression_refs(item)


def validate_dictionary() -> None:
    data = load(SEARCHES / "search-concept-dictionary.json")
    require(data["provenance"]["created_new_for_run"] is True, "dictionary lacks new-run provenance")
    require(data["provenance"]["restored_from_prior_run"] is False, "dictionary says it was restored")
    concepts = data["concepts"]
    require(set(concepts) == CONCEPT_IDS, f"concept IDs differ: {set(concepts) ^ CONCEPT_IDS}")
    for concept_id, count in EXPECTED_TERM_COUNTS.items():
        terms = concepts[concept_id]["terms"]
        require(len(terms) == count, f"{concept_id} has {len(terms)} terms, expected {count}")
        require(len(terms) == len(set(terms)), f"{concept_id} contains duplicate terms")
    require(concepts["E"]["members"] == ["E_H", "E_F"], "E union differs")
    require(concepts["M"]["members"] == ["M_H", "M_B"], "M union differs")
    partitions = data["direct_partitions"]
    ids = [item["id"] for item in partitions]
    require(set(ids) == DIRECT_IDS and len(ids) == len(DIRECT_IDS), "direct partition schedule differs")
    for item in partitions:
        unknown = set(expression_refs(item["expression"])) - CONCEPT_IDS
        require(not unknown, f"{item['id']} references unknown concepts: {unknown}")
    local = data["local_method_minimum"]
    require(set(local["independent_tags"]) == {"R", "T2", "V1", "O1"}, "local tags differ")
    require({x["id"] for x in local["expansion_candidates"]} == {"BG1", "BG2", "BC1"}, "local expansions differ")


def validate_crosswalk() -> None:
    data = load(SEARCHES / "source-interface-prisma-crosswalk.json")
    sources = data["sources"]
    interfaces = data["interfaces"]
    require(len(sources) == 15, f"crosswalk has {len(sources)} source rows")
    require(len({x["source_id"] for x in sources}) == 15, "source IDs are not unique")
    require(len(interfaces) == 13, f"crosswalk has {len(interfaces)} interfaces")
    interface_ids = {x["interface_id"] for x in interfaces}
    require(len(interface_ids) == 13, "interface IDs are not unique")
    require({x["task_id"] for x in sources} == EXPECTED_TASKS, "source task coverage differs")
    require(all(x["interface_id"] in interface_ids for x in sources), "source references unknown interface")
    oatd = next(x for x in sources if x["source_id"] == "oatd")
    require(oatd["prisma_2020_column"] == "other_methods", "OATD PRISMA column differs")
    require(
        all(x["prisma_2020_column"] == "databases_registers" for x in sources if x["source_id"] != "oatd"),
        "a non-OATD source is outside databases/registers",
    )
    require(all(x["separate_total"] is True for x in sources), "a source lacks a separate total")


def validate_schemas() -> None:
    schema_paths = sorted((SEARCHES / "schemas").glob("*.schema.json"))
    require(len(schema_paths) == 3, "expected exactly three infrastructure schemas")
    schemas = [load(path) for path in schema_paths]
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        Draft202012Validator = None
    if Draft202012Validator:
        for schema in schemas:
            Draft202012Validator.check_schema(schema)
        pilot_schema = load(SEARCHES / "schemas" / "pilot-manifest.schema.json")
        template = load(SEARCHES / "templates" / "pilot-manifest.template.json")
        Draft202012Validator(pilot_schema).validate(template)


def validate_layout() -> None:
    required = [
        ROOT / "search-log.md",
        SEARCHES / "README.md",
        SEARCHES / "templates" / "source-guideline.md",
        SEARCHES / "templates" / "source-pilot-prompt.md",
        SEARCHES / "final-events" / "README.md",
    ]
    for path in required:
        require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    final_files = [p for p in (SEARCHES / "final-events").rglob("*") if p.is_file() and p.name != "README.md"]
    require(not final_files, f"final-events contains premature artifacts: {final_files}")


def main() -> int:
    checks = [validate_dictionary, validate_crosswalk, validate_schemas, validate_layout]
    for check in checks:
        check()
        print(f"ok: {check.__name__}")
    print("SLR1 search infrastructure validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
