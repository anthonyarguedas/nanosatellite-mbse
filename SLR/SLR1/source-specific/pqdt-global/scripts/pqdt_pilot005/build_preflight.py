#!/usr/bin/env python3
"""Build the predeclared input boundary for PQDT Global Pilot 005."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries

SCHEMA = "pqdt-global-pilot005-preflight/v1"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "preflight.json"


def pilot004_records() -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    records: dict[str, dict[str, Any]] = {}
    memberships: dict[str, list[str]] = {}
    for partition_id in queries.SCHEDULE_IDS:
        path = (
            queries.PILOT004_ROOT
            / "searches"
            / "events"
            / f"wildcard-{partition_id}.json"
        )
        artifact = queries.load_object(path)
        for row in artifact.get("results", []):
            if not isinstance(row, dict):
                raise RuntimeError(f"Pilot 004 {partition_id} has a malformed record")
            paper_id = str(row.get("paperId", ""))
            if not paper_id.isascii() or not paper_id.isdigit():
                raise RuntimeError(f"Pilot 004 {partition_id} has an invalid document ID")
            existing = records.setdefault(paper_id, row)
            if existing.get("title") != row.get("title"):
                raise RuntimeError(f"Pilot 004 title changed for {paper_id}")
            memberships.setdefault(paper_id, []).append(partition_id)
    return records, memberships


def build() -> dict[str, Any]:
    assessment = queries.load_object(queries.PILOT004_ASSESSMENT)
    event_plan = queries.load_object(queries.PILOT004_EVENT_PLAN)
    if assessment.get("status") != "complete":
        raise RuntimeError("PQDT Pilot 004 assessment is incomplete")
    if assessment.get("decision") != "accept_and_prefer_bounded_wildcard_translation":
        raise RuntimeError("PQDT Pilot 004 wildcard decision changed")
    if event_plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        raise RuntimeError("PQDT Pilot 004 event plan uses another protocol commit")

    source_records, memberships = pilot004_records()
    selected: list[dict[str, Any]] = []
    for expected in queries.SELECTED_KNOWN_RECORDS:
        paper_id = expected["paper_id"]
        row = source_records.get(paper_id)
        if row is None:
            raise RuntimeError(f"Selected record {paper_id} is absent from Pilot 004")
        if str(row.get("title", "")).casefold() != expected["title"].casefold():
            raise RuntimeError(f"Selected record title changed for {paper_id}")
        if memberships[paper_id] != expected["pilot004_partitions"]:
            raise RuntimeError(f"Pilot 004 partition membership changed for {paper_id}")
        selected.append(
            {
                "paper_id": paper_id,
                "title": expected["title"],
                "year": row.get("year"),
                "canonical_url": f"https://www.proquest.com/pqdtglobal/docview/{paper_id}",
                "pilot004_partitions": list(expected["pilot004_partitions"]),
            }
        )

    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "predeclared",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Inspect source-assigned Subject and Index term labels on selected known "
            "records, map bounded candidates to protocol blocks, compare free-text and "
            "free-text-plus-descriptor unions, and review every descriptor-only record."
        ),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_window": {
            "year_start": queries.DIAGNOSTIC_YEAR_START,
            "year_end": queries.DIAGNOSTIC_YEAR_END,
            "exact_cutoff": queries.DIAGNOSTIC_CUTOFF,
            "cutoff_handling": (
                "PQDT applies year precision. Records in 2026 require later screening "
                "against the exact diagnostic cutoff."
            ),
        },
        "source_controls": {
            "database": "exactly one allowed PQDT Global database label",
            "language": "LA(English)",
            "sort": "DateAsc / Oldest first",
            "page_size": 20,
            "full_text": False,
            "exclude_duplicates": False,
            "spelling_variants": False,
            "form_variants": False,
            "show_variants": False,
            "degree_or_document_type": None,
        },
        "record_selection": {
            "basis": (
                "Fourteen Pilot 004 records whose title or abstract explicitly joins a "
                "CubeSat or nanosatellite case to MBSE, SysML, digital engineering, or "
                "structured system-model work."
            ),
            "purpose": "Known items for this vocabulary test only.",
            "final_screening_state": "not_a_final_eligibility_decision",
            "record_count": len(selected),
            "records": selected,
        },
        "assignment_plan": {
            "passes": 2,
            "route": "source-created Abstract/Details view from each canonical PQDT record",
            "fields": ["SUBJECT", "INDEX TERM"],
            "acceptance": (
                "Both complete passes must return the same ordered field groups and labels "
                "for every selected document ID."
            ),
        },
        "candidate_plan": {
            "mapping_rule": (
                "A candidate must be assigned to at least one selected record and must "
                "represent one declared protocol block without broadening its meaning."
            ),
            "generic_systems_engineering_rule": (
                "A generic systems engineering label cannot satisfy M_H alone. It requires "
                "an assigned model or modeling label in the same field construction."
            ),
            "fields_kept_separate": ["PSUB.EXACT", "IF.EXACT"],
            "free_text_mandatory": True,
            "major_topic": False,
            "explosion": None,
        },
        "comparison_plan": {
            "baseline": "accepted Pilot 004 bounded-wildcard free-text schedule",
            "candidate": "each free-text block OR its validated exact descriptor block",
            "events": "fresh strict baseline and augmented events for every affected partition",
            "acceptance": (
                "The augmented set must retain every baseline ID. Every descriptor-only "
                "record must be reviewed against the intended mapped concepts before adoption."
            ),
        },
        "pinned_inputs": {
            "pilot004_query_module": {
                "path": str(queries.PILOT004_QUERY_MODULE.relative_to(queries.SLR1_ROOT)),
                "sha256": queries.file_sha256(queries.PILOT004_QUERY_MODULE),
            },
            "pilot004_event_plan": {
                "path": str(queries.PILOT004_EVENT_PLAN.relative_to(queries.SLR1_ROOT)),
                "sha256": queries.file_sha256(queries.PILOT004_EVENT_PLAN),
            },
            "pilot004_assessment": {
                "path": str(queries.PILOT004_ASSESSMENT.relative_to(queries.SLR1_ROOT)),
                "sha256": queries.file_sha256(queries.PILOT004_ASSESSMENT),
            },
            "adapter": {
                "path": str(queries.ADAPTER_PATH),
                "sha256": queries.file_sha256(queries.ADAPTER_PATH),
                "expected_version": "5",
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 preflight differs from the declared inputs")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
