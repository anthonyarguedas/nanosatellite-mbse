#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# ///
"""Offline integrity audit for immutable NTRS draft cells and P02 query files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED = ["A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_expression(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        raise ValueError("invalid expression")
    return f" {value['op']} ".join(
        f"({canonical_expression(item)})" if isinstance(item, dict) else canonical_expression(item)
        for item in value["args"]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--pilot-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    pilot = Path(args.pilot_dir).resolve()
    source = repo / "SLR/SLR1/searches/sources/s-d13-nasa-ntrs"
    dictionary_path = repo / "SLR/SLR1/searches/search-concept-dictionary.json"
    spec_path = source / "translation-spec.json"
    construction_path = source / "query-construction-receipt.json"
    dictionary_raw = dictionary_path.read_bytes()
    dictionary = json.loads(dictionary_raw)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    construction = json.loads(construction_path.read_text(encoding="utf-8"))
    dictionary_partitions = {entry["id"]: entry for entry in dictionary["direct_partitions"]}
    spec_partitions = {entry["partition_id"]: entry for entry in spec["partitions"]}
    construction_cells = {entry["partition_id"]: entry for entry in construction["partition_cells"]}
    partition_receipts: list[dict[str, Any]] = []
    passed = True
    for partition_id in REQUIRED:
        dictionary_entry = dictionary_partitions.get(partition_id)
        spec_entry = spec_partitions.get(partition_id)
        construction_entry = construction_cells.get(partition_id)
        cell = spec_entry["cells"][0] if isinstance(spec_entry, dict) and len(spec_entry.get("cells", [])) == 1 else None
        query_path = source / cell["query_file"] if isinstance(cell, dict) else None
        raw = query_path.read_bytes() if query_path and query_path.exists() else b""
        utf8_valid = True
        try:
            query = raw.decode("utf-8")
        except UnicodeDecodeError:
            query = ""
            utf8_valid = False
        literal_failures: list[dict[str, Any]] = []
        if isinstance(construction_entry, dict):
            for literal, expected in construction_entry.get("expected_literal_occurrences", {}).items():
                observed = query.count(f'"{literal}"')
                if observed != expected:
                    literal_failures.append({"literal": literal, "expected": expected, "observed": observed})
        normative_expression = canonical_expression(dictionary_entry["expression"]) if dictionary_entry else None
        expression_match = bool(spec_entry and spec_entry.get("normative_expression") == normative_expression)
        sha_match = bool(cell and sha256_bytes(raw) == cell.get("sha256"))
        byte_match = bool(cell and len(raw) == cell.get("utf8_bytes"))
        cell_match = bool(construction_entry and cell and construction_entry.get("cell_id") == cell.get("cell_id"))
        row_passed = bool(dictionary_entry and spec_entry and construction_entry and cell and utf8_valid and expression_match and sha_match and byte_match and cell_match and not literal_failures)
        passed = passed and row_passed
        partition_receipts.append({
            "partition_id": partition_id,
            "source_cell_id": cell.get("cell_id") if cell else None,
            "root_query_path": f"SLR/SLR1/searches/sources/s-d13-nasa-ntrs/{cell['query_file']}" if cell else None,
            "utf8_valid": utf8_valid,
            "terminal_line_ending": "CRLF" if query.endswith("\r\n") else "LF" if query.endswith("\n") else "none",
            "utf8_bytes_match_spec": byte_match,
            "sha256_match_spec": sha_match,
            "normative_boolean_expression": normative_expression,
            "spec_expression_matches_dictionary": expression_match,
            "literal_occurrence_failures": literal_failures,
            "cell_id_matches_construction_receipt": cell_match,
            "offline_literal_and_boolean_audit_passed": row_passed,
            "p02_live_transport_status": "blocked_before_request_by_unreconciled_mandatory_early-gate_timeout",
            "p02_source_reported_total": None,
        })
    candidate_terms = [
        "model-based engineering", "model based engineering", "model-driven engineering", "model driven engineering",
        "model-based design", "model based design", "model-driven design", "model driven design", "MBE", "MDE", "MBD",
        "digital thread", "digital threads", "digital twin", "digital twins", "MagicGrid", "Harmony-SE", "Harmony SE", "RFLP",
        "Cameo Systems Modeler", "MagicDraw", "IBM Engineering Systems Design Rhapsody", "Rational Rhapsody", "Vitech CORE", "Vitech GENESYS", "OpenMBEE", "Enterprise Architect", "MATLAB System Composer", "System Composer", "Modelio", "Cameo", "Rhapsody", "CORE", "GENESYS",
    ]
    candidate_presence = []
    for entry in partition_receipts:
        query_path = repo / entry["root_query_path"] if entry["root_query_path"] else None
        query = query_path.read_text(encoding="utf-8") if query_path else ""
        present = [term for term in candidate_terms if f'"{term}"' in query]
        candidate_presence.append({"partition_id": entry["partition_id"], "non_normative_sc01_candidate_literals_present": present})
        if present:
            passed = False
    p02_query_path = pilot / "queries/Q01-minimal-nanosatellite.txt"
    p02_raw = p02_query_path.read_bytes()
    try:
        p02_text = p02_raw.decode("utf-8")
        p02_utf8_valid = True
    except UnicodeDecodeError:
        p02_text = ""
        p02_utf8_valid = False
    output = {
        "schema_version": "slr1-ntrs-p02-offline-partition-audit/v1",
        "scope": "Offline integrity only; no source request was made by this audit, no root packet file was modified, and it does not validate live parser semantics.",
        "dictionary": {
            "path": "SLR/SLR1/searches/search-concept-dictionary.json",
            "sha256": sha256_bytes(dictionary_raw),
            "sha256_matches_root_translation_spec": sha256_bytes(dictionary_raw) == spec.get("normative_provenance", {}).get("dictionary_sha256"),
            "required_partition_ids": REQUIRED,
            "actual_partition_ids": [entry["id"] for entry in dictionary["direct_partitions"]],
        },
        "translation_spec": {
            "path": "SLR/SLR1/searches/sources/s-d13-nasa-ntrs/translation-spec.json",
            "status": spec.get("status"),
            "required_partition_ids_match": spec.get("normative_provenance", {}).get("required_partition_ids") == REQUIRED,
            "actual_partition_ids": [entry["partition_id"] for entry in spec.get("partitions", [])],
        },
        "nine_partition_receipts": partition_receipts,
        "sc01_candidate_audit": candidate_presence,
        "executed_p02_query": {
            "path": "queries/Q01-minimal-nanosatellite.txt",
            "utf8_valid": p02_utf8_valid,
            "has_no_line_ending": "\n" not in p02_text and "\r" not in p02_text,
            "utf8_bytes": len(p02_raw),
            "sha256": sha256_bytes(p02_raw),
            "exact_text": p02_text,
        },
        "all_offline_integrity_checks_passed": passed and p02_utf8_valid and "\n" not in p02_text and "\r" not in p02_text,
    }
    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_offline_integrity_checks_passed": output["all_offline_integrity_checks_passed"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
