#!/usr/bin/env python3
"""Build PQDT Pilot 003 stable-ID unions and the >100 investigation receipt."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import run_schedule as runner

SEARCH_DIR = runner.SEARCH_DIR
PLAN_PATH = runner.PLAN_PATH
PARTITIONS = runner.PARTITIONS
THRESHOLD = 100
ASSESSMENT_PATH = SEARCH_DIR / "stable-id-union-reconciliation.json"
NOISE_PATH = SEARCH_DIR / "noise-investigation.json"
LEDGER_PATH = SEARCH_DIR / "event-execution-ledger.json"


def ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def load_records(path: Path) -> list[dict[str, Any]]:
    payload = runner.load_json(path)
    rows = payload.get("results")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def load_cells() -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    events = {event["partition_id"]: event for event in runner.load_plan()}
    ledger = runner.load_json(LEDGER_PATH)
    if ledger.get("schema_version") != "pqdt-global-pilot-003-event-execution-ledger/v1":
        raise RuntimeError("The execution ledger has an unsupported schema.")
    if ledger.get("event_plan", {}).get("sha256") != runner.sha256_file(PLAN_PATH):
        raise RuntimeError("The execution ledger does not bind the current event plan.")
    raw_cells = ledger.get("cells")
    if not isinstance(raw_cells, list):
        raise RuntimeError("The execution ledger has no cells.")
    by_partition = {
        cell.get("partition_id"): cell
        for cell in raw_cells
        if isinstance(cell, dict) and isinstance(cell.get("partition_id"), str)
    }
    if tuple(by_partition) != PARTITIONS:
        raise RuntimeError("The execution ledger does not retain all nine source cells in order.")
    cells: dict[str, dict[str, Any]] = {}
    records: dict[str, list[dict[str, Any]]] = {}
    for partition in PARTITIONS:
        event = events[partition]
        cell = by_partition[partition]
        artifact = SEARCH_DIR / str(cell.get("artifact"))
        if not artifact.exists():
            raise RuntimeError(f"{partition}: linked adapter artifact is missing.")
        if cell.get("artifact_sha256") != runner.sha256_file(artifact):
            raise RuntimeError(f"{partition}: linked adapter artifact changed.")
        if cell.get("source_native_query_sha256") != runner.sha256_bytes(event["query"].encode("utf-8")):
            raise RuntimeError(f"{partition}: source query digest differs from the plan.")
        if cell.get("status") == "complete":
            verified = runner._strict_success_entry(artifact, event)
            for key in (
                "source_total",
                "stable_ids_in_source_order",
                "ordered_document_ids_sha256",
                "two_pass_stable_id_reconciliation",
                "scope_readback",
                "control_readback",
            ):
                if cell.get(key) != verified.get(key):
                    raise RuntimeError(f"{partition}: execution ledger {key} differs from immutable source evidence.")
            ids = verified["stable_ids_in_source_order"]
            cells[partition] = {
                **verified,
                "deduplicated_cell_total": len(ids),
                "within_cell_duplicate_stable_ids": [],
            }
            records[partition] = load_records(artifact)
        else:
            failure = runner.load_json(artifact)
            if failure.get("total") is not None or cell.get("source_total") is not None:
                raise RuntimeError(f"{partition}: strict failure must retain null totals.")
            cells[partition] = {
                **cell,
                "source_total": None,
                "stable_ids_in_source_order": None,
                "deduplicated_cell_total": None,
                "within_cell_duplicate_stable_ids": None,
            }
            records[partition] = []
    return cells, records


def union_from_cells(cells: Mapping[str, Mapping[str, Any]], partitions: Iterable[str]) -> dict[str, Any]:
    selected = tuple(partitions)
    failed = [partition for partition in selected if cells[partition].get("status") != "complete"]
    if failed:
        return {
            "partitions": list(selected),
            "status": "incomplete_due_to_strict_failure",
            "failed_partitions": failed,
            "source_event_total": None,
            "deduplicated_stable_ids": None,
            "deduplicated_union_total": None,
            "duplicates_across_selected_cells": None,
        }
    occurrences = [
        document_id
        for partition in selected
        for document_id in cells[partition]["stable_ids_in_source_order"]
    ]
    unique = ordered_unique(occurrences)
    return {
        "partitions": list(selected),
        "status": "complete",
        "failed_partitions": [],
        "source_event_total": len(occurrences),
        "deduplicated_stable_ids": unique,
        "deduplicated_union_total": len(unique),
        "duplicates_across_selected_cells": len(occurrences) - len(unique),
    }


def sample_records(ids: Iterable[str], records: Mapping[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    wanted = set(ids)
    output: list[dict[str, Any]] = []
    for partition in PARTITIONS:
        for row in records[partition]:
            document_id = row.get("paperId")
            if document_id not in wanted:
                continue
            wanted.remove(document_id)
            output.append(
                {
                    "stable_id": document_id,
                    "first_seen_partition": partition,
                    "title": row.get("title") or "not_reported",
                    "year": row.get("year"),
                    "publication": row.get("publication") or "not_reported",
                }
            )
            if len(output) == 25:
                return output
    return output


def build_noise_investigation(
    cells: Mapping[str, Mapping[str, Any]],
    partitions: Mapping[str, Mapping[str, Any]],
    streams: Mapping[str, Mapping[str, Any]],
    records: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    candidates: dict[str, Mapping[str, Any]] = {
        f"partition:{partition}": partitions[partition] for partition in PARTITIONS
    }
    candidates.update(streams)
    triggered: list[dict[str, Any]] = []
    for name, union in candidates.items():
        total = union.get("deduplicated_union_total")
        if not isinstance(total, int) or total <= THRESHOLD:
            continue
        ids = union.get("deduplicated_stable_ids")
        if not isinstance(ids, list):
            raise RuntimeError(f"{name}: complete union lacks stable IDs.")
        sample = sample_records(ids, records)
        publications = Counter(str(item["publication"]) for item in sample)
        years = Counter(str(item["year"]) for item in sample)
        triggered.append(
            {
                "union": name,
                "partitions": union["partitions"],
                "deduplicated_union_total": total,
                "sample_method": "First 25 distinct canonical document IDs in frozen partition/Oldest-first order; descriptive metadata only.",
                "sample": sample,
                "sample_publication_frequency": dict(sorted(publications.items())),
                "sample_year_frequency": dict(sorted(years.items())),
                "interpretation": "The sample investigates volume only. It does not classify relevance, completion, degree status, report language, or eligibility.",
            }
        )
    incomplete = [
        name for name, union in candidates.items()
        if union.get("status") != "complete"
    ]
    return {
        "schema_version": "pqdt-global-pilot-003-noise-investigation/v1",
        "source": runner.SOURCE_LABEL,
        "source_id": runner.SOURCE_ID,
        "pilot": "003",
        "do_not_merge": True,
        "investigation_threshold": {
            "deduplicated_stable_records": THRESHOLD,
            "rule": "Every complete semantic-partition, stream, and all-schedule document-ID union above 100 is sampled and assessed below.",
        },
        "triggered_unions": triggered,
        "incomplete_unions_not_threshold_assessed": incomplete,
        "candidate_refinements": [
            {
                "control": "LA(English)",
                "decision": "already_applied",
                "reason": "The exact language metadata restriction is part of every frozen cell; full-report English remains a screening decision.",
            },
            {
                "control": "PQDT degree, completion, document type, full text, or access",
                "decision": "not_applied",
                "reason": "No lossless eligible-report union is established, and degree/completion status plus availability remain screening decisions rather than search filters.",
            },
            {
                "control": "PQ subject or Index-term browse strings",
                "decision": "not_applied",
                "reason": "PQDT exposes no validated protocol-block descriptor mapping, hierarchy, release, or no-loss expansion; a fielded controlled-term restriction would narrow recall.",
            },
            {
                "control": "Additional source/result facets",
                "decision": "not_applied",
                "reason": "No other source field or facet has a validated no-loss relationship to all eligible reports for this pilot.",
            },
        ],
        "outcome": "No query refinement was applied. The literal schedule, exact PQDT-only scope, and fixed controls remain unchanged.",
    }


def main() -> int:
    if ASSESSMENT_PATH.exists() or NOISE_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing Pilot 003 assessment.")
    cells, records = load_cells()
    partition_unions = {
        partition: {
            "cell_ids": [cells[partition]["cell_id"]],
            **union_from_cells(cells, (partition,)),
        }
        for partition in PARTITIONS
    }
    stream_unions = {
        "stream_A": union_from_cells(cells, ("A1", "A2", "A3")),
        "core_stream_B": union_from_cells(cells, ("B1", "B2")),
        "expanded_stream_B": union_from_cells(cells, ("BG1", "BG2", "BC1", "BT2")),
        "all_schedule": union_from_cells(cells, PARTITIONS),
    }
    complete_cells = [cells[partition] for partition in PARTITIONS if cells[partition]["status"] == "complete"]
    failures = [cells[partition] for partition in PARTITIONS if cells[partition]["status"] != "complete"]
    source_events = [
        {
            "partition_id": partition,
            "cell_id": cells[partition]["cell_id"],
            "source_rank": rank,
            "stable_id": document_id,
        }
        for partition in PARTITIONS
        if cells[partition]["status"] == "complete"
        for rank, document_id in enumerate(cells[partition]["stable_ids_in_source_order"], start=1)
    ]
    all_schedule = stream_unions["all_schedule"]
    assessment = {
        "schema_version": "pqdt-global-pilot-003-stable-id-union-reconciliation/v1",
        "source": runner.SOURCE_LABEL,
        "source_id": runner.SOURCE_ID,
        "pilot": "003",
        "do_not_merge": True,
        "purpose": "Pilot-only complete rendered-record diagnostic. No final search or final source union is created.",
        "event_plan": {"artifact": PLAN_PATH.name, "sha256": runner.sha256_file(PLAN_PATH)},
        "source_window": {
            "source_years": {"start": runner.SOURCE_YEAR_START, "end": runner.SOURCE_YEAR_END},
            "diagnostic_cutoff": runner.DIAGNOSTIC_CUTOFF,
            "precision": "YR is year precision; records dated only 2026 remain for later cutoff screening.",
        },
        "translation": {
            "renderer": "shared scripts/pilot_schedule/queries.py proquest_dissertations_theses_global",
            "source_field": "NOFT",
            "wildcards": "none",
            "source_query_limit": runner.MAX_QUERY_CHARACTERS,
            "query_cells": "One full literal cell per partition because each 1,494-10,923-character expression is below the validated 50,000-character adapter limit.",
            "pair_rule": "Every declared pair is the unordered source-native NOFT(\"left\" NEAR/5 \"right\") atom.",
        },
        "fixed_controls": {
            "scope": "Exactly one PQDT Global database label (or its rendered Full Text Included variant), selected and restored per event.",
            "language": "LA(English)",
            "publication_type": "No degree, completion, document-type, access, or full-text restriction.",
            "variants": "Spelling, form, and display variants frozen off; duplicate exclusion frozen off.",
            "sort": "DateAsc / Oldest first",
            "record_capture": "Each complete cell passed the adapter's two complete rendered passes with identical ordered numeric PQDT document IDs.",
            "complete_result_boundary": runner.MAX_COMPLETE_RESULTS,
        },
        "cells": {partition: cells[partition] for partition in PARTITIONS},
        "partition_unions": partition_unions,
        "stream_unions": stream_unions,
        "source_events": source_events,
        "source_event_total": len(source_events) if not failures else None,
        "successful_source_event_total": len(source_events),
        "all_schedule_deduplicated_total": all_schedule.get("deduplicated_union_total"),
        "strict_failures": [
            {
                "partition_id": cell["partition_id"],
                "artifact": cell["artifact"],
                "source_total": None,
                "scope_readback": cell["scope_readback"],
            }
            for cell in failures
        ],
        "limitations": [
            "PQDT YR bounds source years, not exact days; 2026 records require screening against the diagnostic cutoff 2026-08-29.",
            "LA(English) is metadata evidence only; full-report language remains a screening decision.",
            "Degree subtype, completion, document type, full text, access, and availability were not search filters and remain screening decisions where applicable.",
            "The 10,000-result complete rendered paging/export boundary is hard. A strict failure is retained with a null total and does not become zero or a partial union.",
        ],
        "outcome": "All successful document-ID unions are retained only as Pilot 003 diagnostics. No source translation, controlled term, refinement, or final-search decision is accepted.",
    }
    noise = build_noise_investigation(cells, partition_unions, stream_unions, records)
    runner.write_new_json(ASSESSMENT_PATH, assessment)
    runner.write_new_json(NOISE_PATH, noise)
    print(json.dumps({
        "partition_totals": {partition: cells[partition]["source_total"] for partition in PARTITIONS},
        "all_schedule_deduplicated_total": assessment["all_schedule_deduplicated_total"],
        "strict_failure_count": len(failures),
        "unions_over_100": [item["union"] for item in noise["triggered_unions"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
