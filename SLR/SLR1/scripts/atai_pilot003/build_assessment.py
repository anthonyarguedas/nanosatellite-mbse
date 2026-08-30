#!/usr/bin/env python3
"""Reconcile ATAI Pilot 003 source cells without promoting them to final runs."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
PILOT_ROOT = ROOT / "source-specific/advanced-technologies-aerospace-index/pilots/003"
SEARCH_DIR = PILOT_ROOT / "searches"
PLAN_PATH = SEARCH_DIR / "event-plan.json"
SCHEDULE_DIR = ROOT / "scripts/pilot_schedule"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
THRESHOLD = 100


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} is not a JSON object.")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def source_artifact(partition: str) -> Path:
    # A3 has a purpose-specific repair receipt. Other cells use the generic
    # stable-ID pair receipt when present; otherwise they retain the strict
    # adapter artifact under the schedule ID.
    if partition == "A3":
        return SEARCH_DIR / "A3-repaired-pass2.json"
    if (SEARCH_DIR / f"{partition}-stable-id-reconciliation.json").exists():
        return SEARCH_DIR / f"{partition}-stable-id-pass2.json"
    return SEARCH_DIR / f"{partition}.json"


def supporting_capture_artifacts(partition: str) -> list[str]:
    if partition == "A3":
        return [
            "A3.strict-complete.NON_MERGEABLE_FAILURE.json",
            "A3-repaired-pass1.json",
            "A3-repair-reconciliation.json",
        ]
    receipt = SEARCH_DIR / f"{partition}-stable-id-reconciliation.json"
    if receipt.exists():
        output = [f"{partition}-stable-id-pass1.json", receipt.name]
        strict_failure = SEARCH_DIR / f"{partition}.strict-complete.NON_MERGEABLE_FAILURE.json"
        if strict_failure.exists():
            output.insert(0, strict_failure.name)
        return output
    return []


def repaired_a3_evidence() -> dict[str, Any]:
    path = SEARCH_DIR / "A3-repair-reconciliation.json"
    payload = load(path)
    if payload.get("schema_version") != "atai-pilot-003-a3-stable-id-repair/v1":
        raise RuntimeError("A3 repair evidence has an unsupported schema.")
    repair = payload.get("repair")
    if not isinstance(repair, dict) or repair.get("stable_id_equality") is not True:
        raise RuntimeError("A3 repair did not prove ordered stable-ID equality.")
    return {"artifact": path.name, "sha256": sha256(path), **payload}


def generic_stable_id_pair_evidence(partition: str) -> dict[str, Any] | None:
    path = SEARCH_DIR / f"{partition}-stable-id-reconciliation.json"
    if not path.exists():
        return None
    payload = load(path)
    if payload.get("schema_version") != "atai-pilot-003-stable-id-pair/v1":
        raise RuntimeError(f"{partition} stable-ID pair has an unsupported schema.")
    if payload.get("stable_id_equality") is not True:
        raise RuntimeError(f"{partition} stable-ID pair did not prove ordered equality.")
    return {"artifact": path.name, "sha256": sha256(path), **payload}


def record_id(record: dict[str, Any], *, artifact: Path) -> str:
    value = record.get("paperId")
    if not isinstance(value, str) or not value.isascii() or not value.isdigit():
        raise RuntimeError(f"{artifact.name}: non-numeric ATAI stable ID {value!r}.")
    return value


def field_value(record: dict[str, Any], *names: str) -> str:
    for name in names:
        value = record.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "not_reported"


def compact_control_projection(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("output_metadata")
    receipt = metadata.get("prisma_search_run") if isinstance(metadata, dict) else None
    if not isinstance(receipt, dict):
        return {"state": "not_available_in_artifact"}
    strategy = receipt.get("strategy")
    if not isinstance(strategy, dict):
        return {"state": "not_available_in_artifact"}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, dict) else {}
    return {
        "selected_scope": strategy.get("search_scope"),
        "language": limits.get("language"),
        "publication_date": limits.get("publication_date"),
        "document_type": limits.get("document_type"),
        "peer_reviewed": limits.get("peer_reviewed"),
        "full_text": limits.get("full_text"),
        "access": limits.get("access"),
        "sort": strategy.get("sort"),
        "query_syntax": strategy.get("query_syntax"),
    }


def load_schedule() -> tuple[dict[str, Any], dict[str, str]]:
    plan = load(PLAN_PATH)
    events = plan.get("events")
    if not isinstance(events, list):
        raise RuntimeError("The event plan has no event list.")
    events_by_partition = {
        event.get("partition_id"): event
        for event in events
        if isinstance(event, dict) and isinstance(event.get("partition_id"), str)
    }
    if tuple(events_by_partition) != PARTITIONS:
        raise RuntimeError("The event plan does not have the ordered ATAI schedule.")
    if str(SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(SCHEDULE_DIR))
    from queries import partition_query  # noqa: PLC0415

    queries: dict[str, str] = {}
    for partition in PARTITIONS:
        event = events_by_partition[partition]
        query = event.get("query")
        expected = partition_query("proquest_aerospace_index", partition)
        if query != expected:
            raise RuntimeError(f"{partition}: plan no longer matches the shared schedule.")
        queries[partition] = expected
    return events_by_partition, queries


def build_cell_ledger(
    events: dict[str, Any], queries: dict[str, str]
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    cells: dict[str, Any] = {}
    records_by_partition: dict[str, list[dict[str, Any]]] = {}
    source_events: list[dict[str, Any]] = []
    for partition in PARTITIONS:
        path = source_artifact(partition)
        payload = load(path)
        metadata = payload.get("output_metadata")
        if not isinstance(metadata, dict):
            raise RuntimeError(f"{path.name}: missing output metadata.")
        total = payload.get("total")
        results = payload.get("results")
        if not isinstance(total, int) or isinstance(total, bool):
            raise RuntimeError(f"{path.name}: source total is not an exact integer.")
        if not isinstance(results, list) or len(results) != total:
            raise RuntimeError(f"{path.name}: rows do not reconcile to source total.")
        if metadata.get("status") != "success" or metadata.get("retrieval_complete") is not True:
            raise RuntimeError(f"{path.name}: complete source retrieval was not retained.")
        cell = payload.get("pilot_cell")
        if not isinstance(cell, dict) or cell.get("semantic_partition") != partition:
            raise RuntimeError(f"{path.name}: missing pilot-cell linkage.")
        if payload.get("do_not_merge") is not True or metadata.get("merge_eligible") is not False:
            raise RuntimeError(f"{path.name}: pilot-only merge gate is missing.")
        expected_query = queries[partition]
        if payload.get("requested_query", payload.get("query")) != expected_query:
            raise RuntimeError(f"{path.name}: requested source query changed.")
        if cell.get("source_native_query_sha256") != hashlib.sha256(expected_query.encode()).hexdigest():
            raise RuntimeError(f"{path.name}: source-query digest changed.")
        ids: list[str] = []
        normalized_records: list[dict[str, Any]] = []
        for ordinal, raw in enumerate(results, start=1):
            if not isinstance(raw, dict):
                raise RuntimeError(f"{path.name}: result {ordinal} is not an object.")
            stable_id = record_id(raw, artifact=path)
            ids.append(stable_id)
            normalized_records.append(raw)
            source_events.append(
                {
                    "partition_id": partition,
                    "cell_id": cell["cell_id"],
                    "source_rank": raw.get("rank", ordinal),
                    "stable_id": stable_id,
                }
            )
        unique_ids = ordered_unique(ids)
        duplicate_ids = [
            stable_id
            for stable_id, count in Counter(ids).items()
            if count > 1
        ]
        cells[partition] = {
            "event_id": events[partition]["event_id"],
            "cell_id": cell["cell_id"],
            "artifact": path.name,
            "artifact_sha256": sha256(path),
            "source_native_query_sha256": cell["source_native_query_sha256"],
            "source_native_query_characters": cell["source_native_query_characters"],
            "source_total": total,
            "records_retrieved": len(ids),
            "stable_ids_in_source_order": ids,
            "stable_id_count": len(ids),
            "within_cell_duplicate_stable_ids": duplicate_ids,
            "deduplicated_cell_total": len(unique_ids),
            "controls": compact_control_projection(payload),
            "capture_mode": cell.get("capture_mode", "adapter_strict_two_complete_passes"),
            "supporting_failure_or_repair_artifacts": supporting_capture_artifacts(partition),
        }
        records_by_partition[partition] = normalized_records
    return cells, records_by_partition, source_events


def union_from_cells(cells: dict[str, Any], partitions: Iterable[str]) -> dict[str, Any]:
    selected = tuple(partitions)
    source_ids: list[str] = []
    for partition in selected:
        source_ids.extend(cells[partition]["stable_ids_in_source_order"])
    deduplicated = ordered_unique(source_ids)
    return {
        "partitions": list(selected),
        "source_event_total": len(source_ids),
        "deduplicated_stable_ids": deduplicated,
        "deduplicated_union_total": len(deduplicated),
        "duplicates_across_selected_cells": len(source_ids) - len(deduplicated),
    }


def first_records_for_union(
    stable_ids: Iterable[str], records_by_partition: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    wanted = set(stable_ids)
    selected: list[dict[str, Any]] = []
    for partition in PARTITIONS:
        for record in records_by_partition[partition]:
            identifier = record_id(record, artifact=source_artifact(partition))
            if identifier not in wanted:
                continue
            wanted.remove(identifier)
            selected.append(
                {
                    "stable_id": identifier,
                    "first_seen_partition": partition,
                    "title": field_value(record, "title"),
                    "year": record.get("year"),
                    "source_type": field_value(record, "source_type", "sourceType", "publication_type"),
                    "publication": field_value(record, "publication", "journal"),
                }
            )
            if not wanted:
                return selected
    if wanted:
        raise RuntimeError("A union stable ID was not present in a source cell.")
    return selected


def build_noise_investigation(
    cells: dict[str, Any],
    stream_unions: dict[str, Any],
    records_by_partition: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    candidates: dict[str, dict[str, Any]] = {
        f"partition:{partition}": {
            "partitions": [partition],
            "stable_ids": cells[partition]["stable_ids_in_source_order"],
            "deduplicated_union_total": cells[partition]["deduplicated_cell_total"],
        }
        for partition in PARTITIONS
    }
    candidates.update(stream_unions)
    triggered: list[dict[str, Any]] = []
    for name, union in candidates.items():
        total = union.get("deduplicated_union_total")
        if not isinstance(total, int) or total <= THRESHOLD:
            continue
        ids = ordered_unique(
            union.get("stable_ids", union.get("deduplicated_stable_ids", []))
        )
        records = first_records_for_union(ids, records_by_partition)
        type_counts = Counter(record["source_type"] for record in records)
        publication_counts = Counter(record["publication"] for record in records)
        triggered.append(
            {
                "union": name,
                "partitions": union["partitions"],
                "deduplicated_union_total": total,
                "sample_method": "first 25 stable records in the frozen partition/Oldest-first order; descriptive metadata only",
                "sample": records[:25],
                "source_type_frequency_across_union": dict(sorted(type_counts.items())),
                "publication_frequency_across_union": dict(sorted(publication_counts.items())),
                "interpretation": "Visible metadata is a noise diagnostic only. ATAI NOFT can match indexed or full-text material not shown on the card, so this does not classify records as false matches or assess eligibility.",
            }
        )
    return {
        "schema_version": "atai-pilot-003-noise-investigation/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "003",
        "do_not_merge": True,
        "investigation_threshold": {
            "deduplicated_stable_records": THRESHOLD,
            "rule": "Every semantic-partition, stream, expanded-stream, and all-schedule stable-ID union above 100 is described below.",
        },
        "triggered_unions": triggered,
        "candidate_refinements": [
            {
                "control": "Document type / DTYPE / result Document type facet",
                "decision": "not_applied",
                "reason": "No lossless union of all shared eligible report types and missing-type behavior is proved for ATAI.",
            },
            {
                "control": "Source type, publication title, or Language result facets",
                "decision": "not_applied",
                "reason": "The fixed LA(English) Command Line restriction is already applied; no other facet has a validated no-loss eligible-report union.",
            },
            {
                "control": "Technology Thesaurus supplement",
                "decision": "not_applied",
                "reason": "No descriptor mapping for a protocol block was validated for this pilot; browse labels, hierarchy, and expansion are insufficient to add or require a term.",
            },
            {
                "control": "Peer review, full text, access, or availability",
                "decision": "not_applied",
                "reason": "Peer review is not a shared eligibility condition; Full text and Access are unavailable on ATAI and must not be emulated with a database sibling or card link.",
            },
        ],
        "outcome": "No noise refinement was applied. The complete literal NOFT cells remain the only Pilot 003 translations.",
    }


def main() -> int:
    events, queries = load_schedule()
    a3_repair = repaired_a3_evidence()
    generic_pairs = {
        partition: evidence
        for partition in PARTITIONS
        if partition != "A3"
        if (evidence := generic_stable_id_pair_evidence(partition)) is not None
    }
    cells, records_by_partition, source_events = build_cell_ledger(events, queries)
    if cells["A3"]["stable_ids_in_source_order"] != a3_repair["repair"]["ordered_stable_ids"]:
        raise RuntimeError("A3 active cell differs from its stable-ID repair reconciliation.")
    for partition, evidence in generic_pairs.items():
        if cells[partition]["stable_ids_in_source_order"] != evidence["ordered_stable_ids"]:
            raise RuntimeError(f"{partition} active cell differs from its stable-ID pair receipt.")
    partition_unions: dict[str, Any] = {}
    for partition in PARTITIONS:
        union = union_from_cells(cells, (partition,))
        partition_unions[partition] = {
            "cell_ids": [cells[partition]["cell_id"]],
            **union,
        }

    stream_unions = {
        "stream_A": union_from_cells(cells, ("A1", "A2", "A3")),
        "core_stream_B": union_from_cells(cells, ("B1", "B2")),
        "expanded_stream_B": union_from_cells(cells, ("BG1", "BG2", "BC1", "BT2")),
        "all_schedule": union_from_cells(cells, PARTITIONS),
    }
    a_ids = set(stream_unions["stream_A"]["deduplicated_stable_ids"])
    core_b_ids = set(stream_unions["core_stream_B"]["deduplicated_stable_ids"])
    expanded_b_ids = set(stream_unions["expanded_stream_B"]["deduplicated_stable_ids"])
    stream_overlap = {
        "stream_A_only": len(a_ids - core_b_ids - expanded_b_ids),
        "core_stream_B_only": len(core_b_ids - a_ids - expanded_b_ids),
        "expanded_stream_B_only": len(expanded_b_ids - a_ids - core_b_ids),
        "stream_A_and_core_stream_B": len(a_ids & core_b_ids),
        "stream_A_and_expanded_stream_B": len(a_ids & expanded_b_ids),
        "core_stream_B_and_expanded_stream_B": len(core_b_ids & expanded_b_ids),
        "all_three": len(a_ids & core_b_ids & expanded_b_ids),
    }

    assessment = {
        "schema_version": "atai-pilot-003-stable-id-union-reconciliation/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "source_id": "proquest_aerospace_index",
        "pilot": "003",
        "do_not_merge": True,
        "purpose": "Pilot-only complete-record diagnostic. P-001 is unset; no event is a final search.",
        "event_plan": {"artifact": PLAN_PATH.name, "sha256": sha256(PLAN_PATH)},
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "basis": "Publication date",
            "inclusive": "both",
            "role": "labelled diagnostic window only; not the unset P-001/common evidence cutoff",
        },
        "translation": {
            "renderer": "shared scripts/pilot_schedule/queries.py proquest_aerospace_index",
            "source_field": "NOFT",
            "wildcards": "none",
            "source_query_limit": 50_000,
            "query_cells": "Each full expression was accepted below the documented adapter limit; no split or compression was needed.",
            "pair_rule": "Every declared pair is the source-native unordered NOFT(\"left\" NEAR/5 \"right\") atom.",
        },
        "fixed_controls": {
            "scope": "Advanced Technologies & Aerospace Index only",
            "language": "LA(English)",
            "publication_type": "No type, peer-review, access, or full-text filter",
            "variants": "Spelling, form, and show-variants controls frozen off",
            "sort": "DateAsc / Oldest first",
            "record_capture": "A1/A2 passed the adapter's strict two-full-record-pass contract. A3/B1/B2/BG1/BG2/BC1/BT2 retain two same-query full source-total ordinary traversals with exact ordered stable-ID equality; A3/B1 also retain their strict full-record-signature failures.",
        },
        "a3_repaired_capture": {
            "active_artifact": source_artifact("A3").name,
            "repair_reconciliation": a3_repair["artifact"],
            "repair_reconciliation_sha256": a3_repair["sha256"],
            "initial_failure_artifact": a3_repair["initial_failure"]["artifact"],
            "limitation": a3_repair["limitation"],
        },
        "stable_id_pair_captures": {
            partition: {
                "active_artifact": source_artifact(partition).name,
                "reconciliation": evidence["artifact"],
                "reconciliation_sha256": evidence["sha256"],
                "initial_strict_failure": evidence["initial_strict_failure"],
                "limitation": evidence["limitation"],
            }
            for partition, evidence in generic_pairs.items()
        },
        "cells": cells,
        "partition_unions": partition_unions,
        "stream_unions": stream_unions,
        "stream_overlap_counts": stream_overlap,
        "source_events": source_events,
        "source_event_total": len(source_events),
        "all_schedule_deduplicated_total": stream_unions["all_schedule"]["deduplicated_union_total"],
        "limitations": [
            "Full text and Access/Availability limiters are unavailable on the exact ATAI route; neither was emulated.",
            "ATAI's source type and document type facets have no proved lossless eligible-report union, so none was used.",
            "Technology Thesaurus has no validated protocol-block descriptor supplement, stable term ID, release, or expansion control for this pilot.",
            "LA(English) is metadata evidence only; full-text English screening remains required.",
            "The source's 10,000-record pageable cap remains a hard completeness limit. Every successful cell stayed below it; every non-strict capture has two equal ordered full source-total stable-ID traversals, while the strict full-record-signature failures for A3 and B1 remain preserved.",
        ],
        "outcome": "All records and stable IDs are retained as non-mergeable Pilot 003 diagnostics. No translation or final-search decision is accepted.",
    }
    noise = build_noise_investigation(cells, stream_unions, records_by_partition)
    write_json(SEARCH_DIR / "stable-id-union-reconciliation.json", assessment)
    write_json(SEARCH_DIR / "noise-investigation.json", noise)
    print(
        json.dumps(
            {
                "saved": ["stable-id-union-reconciliation.json", "noise-investigation.json"],
                "partition_totals": {
                    partition: partition_unions[partition]["deduplicated_union_total"]
                    for partition in PARTITIONS
                },
                "all_schedule_deduplicated_total": assessment["all_schedule_deduplicated_total"],
                "noise_unions_over_100": len(noise["triggered_unions"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
