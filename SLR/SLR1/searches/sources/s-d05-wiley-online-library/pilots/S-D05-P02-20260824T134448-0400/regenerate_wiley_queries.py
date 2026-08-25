#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Regenerate S-D05 Wiley query bytes from the current v4 dictionary in memory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CANDIDATES = (
    "model-based engineering", "model based engineering", "model-driven engineering",
    "model driven engineering", "model-based design", "model based design",
    "model-driven design", "model driven design", "MBE", "MDE", "MBD",
    "digital thread", "digital threads", "digital twin", "digital twins",
    "MagicGrid", "Harmony-SE", "Harmony SE", "RFLP", "Cameo Systems Modeler",
    "MagicDraw", "IBM Engineering Systems Design Rhapsody", "Rational Rhapsody",
    "Vitech CORE", "Vitech GENESYS", "OpenMBEE", "Enterprise Architect",
    "MATLAB System Composer", "System Composer", "Modelio", "Cameo", "Rhapsody",
    "CORE", "GENESYS",
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atom(term: str) -> str:
    if not isinstance(term, str) or not term:
        raise ValueError("dictionary term must be a nonempty string")
    return '"' + term.replace('"', '\\"') + '"'


def grouped(op: str, values: list[str]) -> str:
    if not values:
        raise ValueError(f"empty {op} group")
    return "(" + f" {op} ".join(values) + ")"


def pairs(concept: dict[str, Any]) -> list[str]:
    if concept["kind"] == "union_of_terms_and_pairs":
        rules = concept["pair_rules"]
    elif concept["kind"] == "paired_terms":
        rules = [{"left": concept["left"], "right": concept["right"]}]
    else:
        return []
    values = [f"({atom(left)} AND {atom(right)})" for rule in rules for left in rule["left"] for right in rule["right"]]
    if len(values) != len(set(values)):
        raise ValueError("duplicate dictionary pair clause")
    return values


def terms(concepts: dict[str, Any], concept_id: str) -> set[str]:
    concept = concepts[concept_id]
    if concept["kind"] == "finite_terms":
        return set(concept["terms"])
    if concept["kind"] == "union":
        return set().union(*(terms(concepts, child) for child in concept["members"]))
    if concept["kind"] == "union_of_terms_and_pairs":
        return set(concept["terms"]) | {value for rule in concept["pair_rules"] for side in ("left", "right") for value in rule[side]}
    if concept["kind"] == "paired_terms":
        return set(concept["left"]) | set(concept["right"])
    raise ValueError(f"unsupported concept kind {concept['kind']}")


def render_concept(concepts: dict[str, Any], concept_id: str) -> str:
    concept = concepts[concept_id]
    if concept["kind"] == "finite_terms":
        return grouped("OR", [atom(value) for value in concept["terms"]])
    if concept["kind"] == "union":
        return grouped("OR", [render_concept(concepts, child) for child in concept["members"]])
    if concept["kind"] == "union_of_terms_and_pairs":
        return grouped("OR", [atom(value) for value in concept["terms"]] + pairs(concept))
    if concept["kind"] == "paired_terms":
        return grouped("OR", pairs(concept))
    raise ValueError(f"unsupported concept kind {concept['kind']}")


def render_expression(concepts: dict[str, Any], expression: Any) -> str:
    if isinstance(expression, str):
        return render_concept(concepts, expression)
    return grouped(expression["op"], [render_expression(concepts, item) for item in expression["args"]])


def concept_ids(expression: Any) -> set[str]:
    if isinstance(expression, str):
        return {expression}
    return set().union(*(concept_ids(item) for item in expression["args"]))


def tree_digest(directory: Path) -> str:
    accumulator = hashlib.sha256()
    for path in sorted(directory.glob("*.txt")):
        accumulator.update(path.name.encode("utf-8"))
        accumulator.update(b"\0")
        accumulator.update(digest(path.read_bytes()).encode("ascii"))
        accumulator.update(b"\n")
    return accumulator.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictionary", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--pilot-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    dictionary_path = Path(args.dictionary).resolve()
    source_root = Path(args.source_root).resolve()
    output_path = Path(args.output).resolve()
    if output_path.exists() or output_path.is_symlink():
        raise SystemExit(f"refusing to overwrite {output_path}")
    dictionary_bytes = dictionary_path.read_bytes()
    dictionary = json.loads(dictionary_bytes)
    if dictionary.get("artifact_version") != "slr1-search-concepts/v4":
        raise SystemExit("current dictionary is not v4")
    schedule = dictionary.get("direct_partitions", [])
    by_id = {item["id"]: item for item in schedule}
    if tuple(item["id"] for item in schedule) != PARTITIONS:
        raise SystemExit("direct-partition schedule differs from the required nine IDs")
    rows: list[dict[str, Any]] = []
    all_equal = True
    for partition_id in PARTITIONS:
        partition = by_id[partition_id]
        generated = (render_expression(dictionary["concepts"], partition["expression"]) + "\n").encode("utf-8")
        query_path = source_root / "queries" / f"{partition_id}.wiley-allfield.txt"
        on_disk = query_path.read_bytes()
        used = concept_ids(partition["expression"])
        expected_terms = set().union(*(terms(dictionary["concepts"], item) for item in used))
        expected_pairs = [clause for item in used for clause in pairs(dictionary["concepts"][item])]
        if len(expected_pairs) != len(set(expected_pairs)):
            raise AssertionError(f"duplicate expected pair clauses in {partition_id}")
        missing_terms = sorted(value for value in expected_terms if atom(value).encode("utf-8") not in generated)
        bad_pair_counts = sorted(clause for clause in expected_pairs if generated.decode("utf-8").count(clause) != 1)
        candidate_hits = sorted(value for value in CANDIDATES if atom(value).encode("utf-8") in generated)
        terminal_lf_only = generated.endswith(b"\n") and not generated.endswith(b"\n\n")
        equal = generated == on_disk
        all_equal = all_equal and equal
        if missing_terms or bad_pair_counts or candidate_hits or b"*" in generated or not terminal_lf_only:
            raise AssertionError(f"query audit failed for {partition_id}")
        rows.append({
            "partition_id": partition_id,
            "query_file": f"queries/{query_path.name}",
            "concept_ids": sorted(used),
            "term_atom_count": len(expected_terms),
            "pair_cross_product_clause_count": len(expected_pairs),
            "missing_terms": missing_terms,
            "missing_or_nonunique_pair_clauses": bad_pair_counts,
            "candidate_terminology_hits": candidate_hits,
            "wildcard_present": b"*" in generated,
            "terminal_lf_only": terminal_lf_only,
            "regenerated_sha256": digest(generated),
            "root_file_sha256": digest(on_disk),
            "utf8_bytes_including_terminal_lf": len(generated),
            "root_file_equals_regenerated": equal,
        })
    receipt = {
        "schema_version": "slr1-s-d05-p02-query-regeneration-audit/v1",
        "pilot_id": args.pilot_id,
        "basis": "observed",
        "source_requests_made": 0,
        "dictionary_artifact_version": dictionary["artifact_version"],
        "dictionary_sha256": digest(dictionary_bytes),
        "required_partition_ids": list(PARTITIONS),
        "all_finite_literals_explicit": True,
        "wildcard_compression_used": False,
        "candidate_terminology_added": False,
        "pair_cross_products_expanded": True,
        "pair_proximity_semantics_validated": False,
        "root_query_tree_sha256": tree_digest(source_root / "queries"),
        "partitions": rows,
        "result": "passed_regenerated_in_memory_and_reconciled_to_existing_root_files" if all_equal else "failed_root_bytes_differ_from_regeneration",
    }
    output_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not all_equal:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
