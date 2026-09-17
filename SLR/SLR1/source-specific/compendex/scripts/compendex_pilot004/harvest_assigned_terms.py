#!/usr/bin/env python3

"""Harvest safe Compendex indexing assignments from two private Pilot 003 RIS passes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import queries

RIS_TAG = re.compile(r"^([A-Z0-9]{2})\s{0,2}-\s?(.*)$")
CANDIDATE_TERMS = (
    "Nanosatellites",
    "Small satellites",
    "Systems engineering",
    "Modeling languages",
    "SysML",
)


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_ris(text: str) -> list[dict[str, list[str]]]:
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    last_tag: str | None = None
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        match = RIS_TAG.match(raw_line)
        if match:
            tag, value = match.groups()
            if tag == "ER":
                if current:
                    records.append(current)
                current = None
                last_tag = None
                continue
            if tag == "TY" and current:
                records.append(current)
                current = None
            if current is None:
                current = {}
            current.setdefault(tag, []).append(clean(value))
            last_tag = tag
            continue
        if current is not None and last_tag and raw_line[:1].isspace():
            continuation = clean(raw_line)
            if continuation:
                current[last_tag][-1] = clean(current[last_tag][-1] + " " + continuation)
    if current:
        records.append(current)
    return records


def load_pass(directory: Path) -> dict[str, dict[str, Any]]:
    selected = dict(queries.SELECTED_KNOWN_RECORDS)
    found: dict[str, dict[str, Any]] = {}
    files = sorted(directory.glob("batch-*.ris"))
    if not files:
        raise RuntimeError("The private pass directory contains no batch RIS files")
    for path in files:
        for record in parse_ris(path.read_text(encoding="utf-8", errors="strict")):
            accession = clean(next(iter(record.get("U1", ())), ""))
            if accession not in selected:
                continue
            if clean(next(iter(record.get("M1", ())), "")) != "Compendex":
                raise RuntimeError(f"Selected accession {accession} did not retain Compendex identity")
            if accession in found:
                raise RuntimeError(f"Selected accession {accession} occurred more than once in one pass")
            title = clean(next(iter(record.get("TI", ())), ""))
            if title.casefold() != selected[accession].casefold():
                raise RuntimeError(f"Selected accession {accession} had an unexpected title")
            indexing_terms = [clean(term) for term in record.get("KW", ()) if clean(term)]
            if not indexing_terms or len(indexing_terms) != len(set(indexing_terms)):
                raise RuntimeError(f"Selected accession {accession} had missing or duplicate KW assignments")
            found[accession] = {
                "accession": accession,
                "title": title,
                "rendered_indexing_field": "KW",
                "controlled_terms": indexing_terms,
                "controlled_term_count": len(indexing_terms),
            }
    missing = [accession for accession in selected if accession not in found]
    if missing:
        raise RuntimeError(f"Private pass lacked selected Compendex accessions: {missing!r}")
    return {accession: found[accession] for accession in selected}


def validate_public_b1(path: Path) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(artifact, dict) or not isinstance(artifact.get("results"), list):
        raise RuntimeError("Pilot 003 B1 public artifact is malformed")
    compendex = {
        clean(record.get("paperId")): clean(record.get("title"))
        for record in artifact["results"]
        if clean(record.get("source")) == "Compendex (Engineering Village)"
    }
    for accession, title in queries.SELECTED_KNOWN_RECORDS:
        if compendex.get(accession, "").casefold() != title.casefold():
            raise RuntimeError(f"Public Pilot 003 B1 did not identify selected accession {accession}")


def projection_hash(records: list[dict[str, Any]]) -> str:
    projection = [
        [record["accession"], record["title"], record["controlled_terms"]]
        for record in records
    ]
    encoded = json.dumps(projection, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build(pass_1_dir: Path, pass_2_dir: Path, public_b1: Path) -> dict[str, Any]:
    validate_public_b1(public_b1)
    first = load_pass(pass_1_dir)
    second = load_pass(pass_2_dir)
    if first != second:
        raise RuntimeError("Selected Compendex indexing assignments changed across the two native RIS passes")
    records = list(second.values())
    frequency = Counter(
        term for record in records for term in record["controlled_terms"]
    )
    assignments = {
        term: [
            record["accession"]
            for record in records
            if term in record["controlled_terms"]
        ]
        for term in CANDIDATE_TERMS
    }
    joint_mh = [
        record["accession"]
        for record in records
        if {
            "Systems engineering",
            "Modeling languages",
        }.issubset(record["controlled_terms"])
    ]
    return {
        "schema_version": "compendex-controlled-term-assignment-harvest/v1",
        "source": "Compendex",
        "platform": "Engineering Village",
        "pilot": "004",
        "status": "complete_two_pass_assignment_readback",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "historical_evidence_boundary": {
            "source_event": "paired Engineering Village Pilot 003 B1 strict passes",
            "use": "record-level Compendex controlled-term assignment evidence only",
            "reason_current_B1_is_applicable": (
                "B1 remained P AND M_H in commit " + queries.PROTOCOL_COMMIT
            ),
            "prohibited_uses": [
                "current full-schedule result set",
                "current changed-partition validation",
                "final search",
            ],
        },
        "method": {
            "input_passes": 2,
            "private_paths_persisted": False,
            "private_raw_ris_persisted": False,
            "source_identity_field": "M1=Compendex",
            "stable_identity_field": "U1",
            "assignment_field": "KW",
            "assignment_interpretation": (
                "The Engineering Village abstract-format RIS compilation/indexing term field. "
                "Each candidate label is separately tested against the exact Ei Thesaurus surface."
            ),
            "public_identity_cross_check": (
                "source-specific/compendex/pilots/003/searches/B1.json"
            ),
        },
        "selection": {
            "basis": (
                "Eleven title-explicit CubeSat or nanosatellite MBSE/system-model records from "
                "Pilot 003 B1, selected as known items for vocabulary testing only."
            ),
            "review_decision_state": "not_final_screening",
            "record_count": len(records),
        },
        "records": records,
        "unique_controlled_term_count": len(frequency),
        "term_frequency": [
            {"term": term, "assigned_record_count": count}
            for term, count in sorted(
                frequency.items(), key=lambda item: (-item[1], item[0].casefold())
            )
        ],
        "candidate_assignments": {
            term: {
                "assigned_record_count": len(accessions),
                "assigned_accessions": accessions,
            }
            for term, accessions in assignments.items()
        },
        "context_qualified_M_H_assignment": {
            "construction": "Systems engineering AND Modeling languages",
            "assigned_record_count": len(joint_mh),
            "assigned_accessions": joint_mh,
        },
        "pass_reconciliation": {
            "pass_1_selected_record_count": len(first),
            "pass_2_selected_record_count": len(second),
            "ordered_records_equal": first == second,
            "ordered_assignments_equal": first == second,
            "pass_1_projection_sha256": projection_hash(list(first.values())),
            "pass_2_projection_sha256": projection_hash(list(second.values())),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass-1-dir", type=Path, required=True)
    parser.add_argument("--pass-2-dir", type=Path, required=True)
    parser.add_argument("--public-b1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(args.pass_1_dir, args.pass_2_dir, args.public_b1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
