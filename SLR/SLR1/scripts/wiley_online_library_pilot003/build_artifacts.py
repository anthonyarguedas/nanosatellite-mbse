#!/usr/bin/env python3
"""Build DOI-first union receipts and metadata/pair audits for Wiley Pilot 003."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "source-specific/wiley-online-library/pilots/003"
SEARCH_DIR = PILOT_DIR / "searches"
SCHEDULE_DIR = ROOT / "scripts/pilot_schedule"
sys.path.insert(0, str(SCHEDULE_DIR))
from queries import CONCEPTS, MAIN_FACTORS, partition_cells, partition_query  # noqa: E402


SCHEDULE_IDS = tuple(MAIN_FACTORS)
CELL_PARENTS = ("A2", "BC1", "BT2")
DIRECT_LEDGER = {
    "A1": "A1.source-id-ledger.json",
    "A3": "A3.source-id-ledger.json",
    "B1": "B1.source-id-ledger.json",
    "B2": "B2.source-id-ledger.json",
    "BG1": "BG1.source-id-ledger.json",
    "BG2": "BG2.source-id-ledger.json",
}
PARENT_FAILURE = {
    "A2": "A2.source-id-ledger.json",
    "BC1": "BC1.source-id-ledger.json",
}
DETAIL_METADATA = (
    "A1-A3-B1.detail-metadata.json",
    "BG2.detail-metadata.json",
    "BC1-BT2.detail-metadata.json",
)
PAIR_CONCEPT_BY_PARTITION = {
    "BG1": "G_model",
    "BG2": "G_structure",
    "BC1": "C1",
    "BT2": "T2",
}
WORD = re.compile(r"[^\W_]+", re.UNICODE)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def sequence_sha256(values: Iterable[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def normalized_tokens(value: str) -> list[str]:
    # Source validation permits observed hyphen/space equivalence.  This does
    # not stem, truncate, expand, or turn an acronym into a substring.
    text = unicodedata.normalize("NFKD", value or "").casefold()
    return WORD.findall(text)


def phrase_starts(tokens: list[str], phrase: str) -> list[int]:
    needle = normalized_tokens(phrase)
    if not needle or len(needle) > len(tokens):
        return []
    return [
        start
        for start in range(len(tokens) - len(needle) + 1)
        if tokens[start : start + len(needle)] == needle
    ]


def literal_matches(value: str, literals: Iterable[str]) -> list[str]:
    tokens = normalized_tokens(value)
    return [literal for literal in literals if phrase_starts(tokens, literal)]


def exact_pair_matches(value: str, pairs: Iterable[tuple[str, str]]) -> list[dict[str, Any]]:
    """Check either order in one field with at most five intervening tokens."""
    tokens = normalized_tokens(value)
    matches: list[dict[str, Any]] = []
    for left, right in pairs:
        left_tokens = normalized_tokens(left)
        right_tokens = normalized_tokens(right)
        found = False
        for left_start in phrase_starts(tokens, left):
            left_end = left_start + len(left_tokens)
            for right_start in phrase_starts(tokens, right):
                right_end = right_start + len(right_tokens)
                if left_end <= right_start and right_start - left_end <= 5:
                    matches.append(
                        {
                            "left": left,
                            "right": right,
                            "order": "left_then_right",
                            "intervening_lexical_tokens": right_start - left_end,
                        }
                    )
                    found = True
                    break
                if right_end <= left_start and left_start - right_end <= 5:
                    matches.append(
                        {
                            "left": left,
                            "right": right,
                            "order": "right_then_left",
                            "intervening_lexical_tokens": left_start - right_end,
                        }
                    )
                    found = True
                    break
            if found:
                break
    return matches


def rendered_a1_query() -> str:
    query = partition_query("wiley_online_library", "A1")
    for old, new in (
        ('"CubeSat" OR "CubeSats"', "CubeSat*"),
        ('"nanosat" OR "nanosats" OR "nanosatellite" OR "nanosatellites"', "nanosat*"),
        ('"SmallSat" OR "SmallSats"', "SmallSat*"),
    ):
        if query.count(old) != 1:
            raise RuntimeError(f"A1 compression input missing: {old}")
        query = query.replace(old, new)
    return query


def validate_query_plan(plan: dict[str, Any]) -> dict[str, Any]:
    queries = plan.get("queries", {})
    if tuple(plan.get("schedule_ids", ())) != SCHEDULE_IDS:
        raise RuntimeError("query plan does not preserve the full ordered nine-partition schedule")
    for partition_id in SCHEDULE_IDS:
        expected = rendered_a1_query() if partition_id == "A1" else partition_query(
            "wiley_online_library", partition_id
        )
        if queries.get(partition_id) != expected:
            raise RuntimeError(f"query plan differs from the canonical {partition_id} translation")
    for partition_id, query in queries.items():
        if partition_id != "A1" and ("*" in query or "?" in query):
            raise RuntimeError(f"unvalidated wildcard in {partition_id}")
    cell_plan = plan.get("query_cells", {})
    unions = plan.get("source_cell_unions", {})
    for parent in CELL_PARENTS:
        specification = unions.get(parent)
        if not isinstance(specification, dict):
            raise RuntimeError(f"missing source-cell union declaration for {parent}")
        expected = partition_cells(
            "wiley_online_library", parent, maximum_characters=2700
        )
        expected_ids = [f"{parent}-{cell['cell_id']}" for cell in expected]
        if specification.get("cell_ids") != expected_ids:
            raise RuntimeError(f"{parent} source-cell IDs are not complete or ordered")
        for cell, cell_id in zip(expected, expected_ids):
            if cell_plan.get(cell_id) != cell["query"]:
                raise RuntimeError(f"{parent} source-cell query changed: {cell_id}")
            if len(cell["query"]) > 2700:
                raise RuntimeError(f"{parent} source cell exceeds its validated ceiling")
            if "*" in cell["query"] or "?" in cell["query"]:
                raise RuntimeError(f"unvalidated wildcard in source cell {cell_id}")
    return {
        "schedule_ids": list(SCHEDULE_IDS),
        "literal_counts": {
            name: {
                "literals": len(concept.literals),
                "pairs": len(concept.pairs),
                "alternatives": concept.alternative_count,
            }
            for name, concept in CONCEPTS.items()
            if name in {"P", "E_H", "E_F", "M_H", "M_B", "R", "G_model", "G_structure", "C1", "T2"}
        },
        "A1_wildcard_only": True,
        "source_cell_parents": list(CELL_PARENTS),
    }


def expected_ledger_paths(plan: dict[str, Any], partition_id: str) -> list[Path]:
    if partition_id in CELL_PARENTS:
        return [
            SEARCH_DIR / f"{cell_id.replace('-', '.', 1)}.source-id-ledger.json"
            for cell_id in plan["source_cell_unions"][partition_id]["cell_ids"]
        ]
    return [SEARCH_DIR / DIRECT_LEDGER[partition_id]]


def failure_summary(path: Path) -> dict[str, Any]:
    data = load(path)
    return {
        "artifact": path.name,
        "status": data.get("status"),
        "source_total": data.get("source_total"),
        "failure": data.get("failure"),
    }


def ledger_event_rows(path: Path, expected_partition: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load(path)
    if data.get("status") != "success":
        raise RuntimeError(f"successful receipt required, found {data.get('status')}: {path}")
    if data.get("partition_id") != expected_partition:
        raise RuntimeError(f"wrong partition in {path}")
    total = data.get("source_total")
    records = data.get("records")
    ids = data.get("ordered_source_ids")
    if not isinstance(total, int) or total < 0 or not isinstance(records, list) or not isinstance(ids, list):
        raise RuntimeError(f"malformed successful source ledger: {path}")
    if total != len(records) or ids != [record.get("source_id") for record in records]:
        raise RuntimeError(f"source total/record sequence mismatch in {path}")
    if data.get("ordered_source_ids_sha256") != sequence_sha256(ids):
        raise RuntimeError(f"source sequence digest mismatch in {path}")
    if len(data.get("passes", [])) != 2 or not data.get("owned_page_cleanup_verified"):
        raise RuntimeError(f"two-pass/owned-page contract failed in {path}")
    query_id = data.get("source_query_id") or expected_partition
    rows = []
    for record in records:
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise RuntimeError(f"missing source ID in {path}")
        rows.append(
            {
                "source_id": source_id,
                "doi": record.get("doi") or source_id,
                "source_query_id": query_id,
                "source_cell_artifact": path.name,
                "source_rank": record.get("rank"),
                "title": record.get("title", ""),
                "source_publication_date": record.get("source_publication_date", ""),
                "exact_date_filter_status": record.get("exact_date_filter_status"),
            }
        )
    return data, rows


def union_receipt(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    entries: dict[str, Any] = {}
    materialized: dict[str, dict[str, Any]] = {}
    for partition_id in SCHEDULE_IDS:
        paths = expected_ledger_paths(plan, partition_id)
        parent_failure = SEARCH_DIR / PARENT_FAILURE[partition_id] if partition_id in PARENT_FAILURE else None
        if partition_id in DIRECT_LEDGER:
            primary = paths[0]
            data = load(primary)
            if data.get("status") != "success":
                entries[partition_id] = {
                    "status": "source_failure",
                    "source_total": None,
                    "failure_receipt": failure_summary(primary),
                    "source_cells": [],
                    "ordered_source_ids": [],
                }
                continue
        if parent_failure is not None:
            failure = load(parent_failure)
            if failure.get("status") != "error" or failure.get("source_total") is not None:
                raise RuntimeError(f"unaccepted full-query failure receipt for {partition_id}")
        cell_receipts: list[dict[str, Any]] = []
        events: list[dict[str, Any]] = []
        for path in paths:
            data, rows = ledger_event_rows(path, partition_id)
            events.extend(rows)
            cell_receipts.append(
                {
                    "artifact": path.name,
                    "source_query_id": data.get("source_query_id") or partition_id,
                    "source_total": data["source_total"],
                    "source_id_sequence_sha256": data["ordered_source_ids_sha256"],
                    "client_exact_date_counts": data.get("client_exact_date_counts"),
                }
            )
        first_by_id: dict[str, dict[str, Any]] = {}
        duplicate_events: list[dict[str, Any]] = []
        for event in events:
            source_id = event["source_id"]
            if source_id in first_by_id:
                duplicate_events.append(
                    {"duplicate_of_source_id": source_id, **event}
                )
            else:
                first_by_id[source_id] = event
        unique = list(first_by_id.values())
        statuses = defaultdict(int)
        for event in unique:
            statuses[event.get("exact_date_filter_status") or "unresolved"] += 1
        retained = [
            event["source_id"]
            for event in unique
            if event.get("exact_date_filter_status") != "excluded"
        ]
        status = (
            "success_lossless_cell_union"
            if partition_id in {"A2", "BC1"}
            else (
                "success_prospectively_split_lossless_cell_union"
                if partition_id == "BT2"
                else "success_single_source_query"
            )
        )
        entry = {
            "status": status,
            "source_total": len(events) if len(paths) == 1 else None,
            "source_cell_event_total": len(events),
            "source_cell_event_total_interpretation": (
                "sum across independently retrieved, overlapping source cells; not a deduplicated source total"
            ),
            "source_cells": cell_receipts,
            "unsplit_parent_failure": failure_summary(parent_failure) if parent_failure else None,
            "source_events": events,
            "ordered_source_ids": [event["source_id"] for event in unique],
            "ordered_source_ids_sha256": sequence_sha256(event["source_id"] for event in unique),
            "unique_source_id_count": len(unique),
            "duplicate_source_event_count": len(duplicate_events),
            "duplicate_source_events": duplicate_events,
            "client_exact_date_counts_after_deduplication": dict(sorted(statuses.items())),
            "ordered_client_retained_source_ids": retained,
            "ordered_client_retained_source_ids_sha256": sequence_sha256(retained),
        }
        entries[partition_id] = entry
        materialized[partition_id] = {
            "events": events,
            "unique": unique,
            "entry": entry,
        }
    return {
        "schema_version": "wiley-online-library-pilot-source-id-unions/v1",
        "pilot": "003",
        "source": "Wiley Online Library",
        "do_not_merge": True,
        "date_window": {
            "requested_start": "2011-01-01",
            "requested_end": "2026-08-29",
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "reconciliation": "Every successful source ledger retains source-month IDs and a visible First published exact-day status; source totals are pre-client-day totals.",
        },
        "identity_rule": "Wiley normalized DOI/source ID, case-preserved from the two-pass Articles & Chapters card ledger; first occurrence follows scheduled cell then native Date order.",
        "entries": entries,
    }, materialized


def detail_by_doi() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for name in DETAIL_METADATA:
        data = load(SEARCH_DIR / name)
        if data.get("status") not in {"success", "partial_access_blocked"}:
            raise RuntimeError(f"unusable detail metadata artifact: {name}")
        for record in data.get("records", []):
            doi = record.get("doi")
            if not isinstance(doi, str) or not doi:
                continue
            current = values.get(doi)
            # Prefer a visible abstract when duplicate detail reads differ.
            if current is None or (not current.get("abstract") and record.get("abstract")):
                values[doi] = record
    return values


def concept_confirmation(title: str, abstract: str, concept_name: str) -> dict[str, Any]:
    concept = CONCEPTS[concept_name]
    title_literals = literal_matches(title, concept.literals)
    abstract_literals = literal_matches(abstract, concept.literals)
    title_pairs = exact_pair_matches(title, concept.pairs)
    abstract_pairs = exact_pair_matches(abstract, concept.pairs)
    return {
        "confirmed": bool(title_literals or abstract_literals or title_pairs or abstract_pairs),
        "title_literal_matches": title_literals,
        "abstract_literal_matches": abstract_literals,
        "title_pair_matches": title_pairs,
        "abstract_pair_matches": abstract_pairs,
    }


def factor_confirmation(title: str, abstract: str, factor: tuple[str, ...]) -> dict[str, Any]:
    checks = {name: concept_confirmation(title, abstract, name) for name in factor}
    return {
        "concepts": checks,
        "confirmed": any(check["confirmed"] for check in checks.values()),
    }


def union_ids(materialized: dict[str, dict[str, Any]], members: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for member in members:
        data = materialized.get(member)
        if data is None:
            continue
        for record in data["unique"]:
            source_id = record["source_id"]
            if source_id not in seen:
                seen.add(source_id)
                result.append(source_id)
    return result


def metadata_audit(materialized: dict[str, dict[str, Any]]) -> dict[str, Any]:
    details = detail_by_doi()
    records_by_id: dict[str, dict[str, Any]] = {}
    membership: dict[str, list[str]] = defaultdict(list)
    for partition_id, data in materialized.items():
        for record in data["unique"]:
            source_id = record["source_id"]
            membership[source_id].append(partition_id)
            records_by_id.setdefault(source_id, record)
    global_order = union_ids(materialized, SCHEDULE_IDS)
    audited: list[dict[str, Any]] = []
    pair_summary = {}
    for source_id in global_order:
        source = records_by_id[source_id]
        detail = details.get(source_id, {})
        title = source.get("title", "")
        abstract = detail.get("abstract", "") if detail.get("detail_status") == "success" else ""
        partition_checks = {}
        for partition_id in membership[source_id]:
            factors = MAIN_FACTORS[partition_id]
            partition_checks[partition_id] = {
                "factors": [factor_confirmation(title, abstract, factor) for factor in factors],
                "local_metadata_confirmation": all(
                    factor_confirmation(title, abstract, factor)["confirmed"] for factor in factors
                ),
            }
        audited.append(
            {
                "source_id": source_id,
                "doi": source.get("doi") or source_id,
                "source_card_title": title,
                "title_field_status": "validated_two_pass_rendered_card",
                "source_publication_date": source.get("source_publication_date", ""),
                "abstract": abstract,
                "abstract_field_status": detail.get("abstract_status", "not_exposed"),
                "detail_status": detail.get("detail_status", "not_collected"),
                "partitions": membership[source_id],
                "partition_checks": partition_checks,
                "not_excluded": True,
                "absence_interpretation": "A missing visible title/abstract match is not a false source match and does not remove this DOI; Wiley Anywhere can match other indexed or full-text material.",
            }
        )
    by_id = {record["source_id"]: record for record in audited}
    for partition_id, concept_name in PAIR_CONCEPT_BY_PARTITION.items():
        if partition_id not in materialized:
            pair_summary[partition_id] = {
                "status": "source_failure_no_pair_audit",
                "concept": concept_name,
                "deduplicated_records": None,
                "visible_title_or_abstract_block_confirmation": None,
                "visible_fixed_literal_confirmation": None,
                "visible_exact_pair_confirmation": None,
                "abstracts_exposed": None,
                "local_rule": "Not applied because the source run failed with total:null; no zero result or zero pair-match claim is made.",
                "recall_protection": "No DOI was available to remove or classify.",
            }
            continue
        ids = union_ids(materialized, (partition_id,))
        confirmed = 0
        exact_pair_confirmed = 0
        fixed_literal_confirmed = 0
        abstract_available = 0
        for source_id in ids:
            check = concept_confirmation(
                by_id[source_id]["source_card_title"], by_id[source_id]["abstract"], concept_name
            )
            fixed = bool(check["title_literal_matches"] or check["abstract_literal_matches"])
            pairs = bool(check["title_pair_matches"] or check["abstract_pair_matches"])
            confirmed += check["confirmed"]
            exact_pair_confirmed += pairs
            fixed_literal_confirmed += fixed
            abstract_available += bool(by_id[source_id]["abstract"])
        pair_summary[partition_id] = {
            "concept": concept_name,
            "deduplicated_records": len(ids),
            "visible_title_or_abstract_block_confirmation": confirmed,
            "visible_fixed_literal_confirmation": fixed_literal_confirmed,
            "visible_exact_pair_confirmation": exact_pair_confirmed,
            "abstracts_exposed": abstract_available,
            "local_rule": "Either declared pair order, one title or one abstract field at a time, at most five intervening lexical tokens; no title/abstract concatenation.",
            "recall_protection": "No DOI lacking a visible literal or exact-pair confirmation was removed or called a false source match.",
        }
    canonical_sets: dict[str, list[str]] = {}
    for partition_id, data in materialized.items():
        canonical_sets[partition_id] = [record["source_id"] for record in data["unique"]]
        if len(data["entry"]["source_cells"]) > 1:
            for cell in data["entry"]["source_cells"]:
                artifact = SEARCH_DIR / cell["artifact"]
                ledger = load(artifact)
                canonical_sets[cell["source_query_id"]] = ledger["ordered_client_retained_source_ids"]
    canonical_sets["Stream_A"] = union_ids(materialized, ("A1", "A2", "A3"))
    canonical_sets["core_Stream_B_successful_subset"] = union_ids(materialized, ("B1",))
    canonical_sets["expanded_Stream_B_successful_subset"] = union_ids(materialized, ("BG2", "BC1", "BT2"))
    canonical_sets["all_successful_partitions"] = global_order
    investigations = {}
    for name, ids in canonical_sets.items():
        unique = list(dict.fromkeys(ids))
        if len(unique) <= 100:
            continue
        title_available = sum(bool(by_id[doi]["source_card_title"]) for doi in unique)
        abstract_available = sum(bool(by_id[doi]["abstract"]) for doi in unique)
        investigations[name] = {
            "deduplicated_records": len(unique),
            "ordered_source_ids_sha256": sequence_sha256(unique),
            "metadata_rows_covered": sum(doi in by_id for doi in unique),
            "validated_title_fields_available": title_available,
            "detail_abstract_fields_available": abstract_available,
            "method": "Every DOI is retained in metadata-audit records and checked against its scheduled local concept/pair rules where applicable; no metadata absence was used as an exclusion.",
        }
    return {
        "schema_version": "wiley-online-library-pilot-metadata-audit/v1",
        "pilot": "003",
        "source": "Wiley Online Library",
        "do_not_merge": True,
        "threshold": {
            "records": 100,
            "applies_to": "every named DOI/source-ID deduplicated source cell, partition, or reported stream/overall union",
            "does_not_apply_to": "overlapping raw source events before DOI/source-ID deduplication",
        },
        "metadata_fields": {
            "title": "Wiley rendered result-card title verified across two ordered source passes",
            "abstract": "Wiley detail-page visible DOM or citation_abstract metadata when exposed; absent abstracts remain absent rather than inferred",
            "date": "Wiley rendered result-card First published used for source-month/client-day reconciliation",
        },
        "exact_pair_rule": "Either order in the same title or the same abstract, with at most five intervening lexical tokens; source title and abstract are never concatenated.",
        "pair_partition_summary": pair_summary,
        "investigated_deduplicated_sets_over_100": investigations,
        "records": audited,
    }


def compact_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if entry["status"] == "source_failure":
        return {
            "status": entry["status"],
            "source_total": None,
            "failure_receipt": entry["failure_receipt"],
        }
    return {
        "status": entry["status"],
        "source_total": entry["source_total"],
        "source_cell_event_total": entry["source_cell_event_total"],
        "unique_source_id_count": entry["unique_source_id_count"],
        "duplicate_source_event_count": entry["duplicate_source_event_count"],
        "ordered_source_ids_sha256": entry["ordered_source_ids_sha256"],
        "client_exact_date_counts_after_deduplication": entry[
            "client_exact_date_counts_after_deduplication"
        ],
        "source_cells": entry["source_cells"],
        "unsplit_parent_failure": entry["unsplit_parent_failure"],
    }


def schedule_assessment(
    plan: dict[str, Any], query_audit: dict[str, Any], receipt: dict[str, Any], metadata: dict[str, Any]
) -> dict[str, Any]:
    entries = receipt["entries"]
    stream_a = union_ids(
        {key: value for key, value in _materialized_from_receipt(entries).items()}, ("A1", "A2", "A3")
    )
    # Failure-aware stream descriptions avoid silently treating a partial source
    # set as a complete Stream B or all-schedule union.
    return {
        "schema_version": "wiley-online-library-pilot-schedule-assessment/v1",
        "pilot": "003",
        "source": "Wiley Online Library",
        "do_not_merge": True,
        "mode": "diagnostic_only_not_a_final_search",
        "date_window": receipt["date_window"],
        "controls": {
            "source_family": "Articles & Chapters / articlesChapters",
            "field": "One Anywhere / AllField Context Search row",
            "sort": "Date / sortBy=Earliest; observed newest-to-oldest; no Oldest option",
            "language": "unavailable; none applied",
            "publication_type": "no PubType refinement; articlesChapters is the record-family boundary",
            "access": "none applied",
            "peer_review": "none applied",
            "full_text": "none applied",
            "controlled_vocabulary": "none added",
            "source_proximity": "not supported; local exact pair check retained as a no-exclusion diagnostic",
        },
        "translation_audit": query_audit,
        "entries": {key: compact_entry(value) for key, value in entries.items()},
        "unions": {
            "Stream_A": {
                "status": "complete_from_successful_A1_A2_A3",
                "members": ["A1", "A2", "A3"],
                "unique_source_id_count": len(stream_a),
                "ordered_source_ids_sha256": sequence_sha256(stream_a),
            },
            "core_Stream_B": {
                "status": "incomplete_due_to_B2_source_failure",
                "successful_members_only": ["B1"],
                "failed_member": "B2",
                "successful_subset_unique_source_id_count": entries["B1"].get("unique_source_id_count"),
            },
            "expanded_Stream_B": {
                "status": "incomplete_due_to_BG1_source_failure",
                "successful_members_only": ["BG2", "BC1", "BT2"],
                "failed_member": "BG1",
                "successful_subset_unique_source_id_count": len(
                    _ordered_union_from_entries(entries, ("BG2", "BC1", "BT2"))
                ),
            },
            "all_nine_partitions": {
                "status": "incomplete_due_to_B2_and_BG1_source_failures",
                "successful_partition_unique_source_id_count": len(
                    _ordered_union_from_entries(entries, SCHEDULE_IDS)
                ),
            },
        },
        "metadata_investigation": {
            "artifact": "metadata-audit.json",
            "sets_over_100": metadata["investigated_deduplicated_sets_over_100"],
            "pair_partition_summary": metadata["pair_partition_summary"],
        },
        "native_export_status": {
            "A1_adapter_failure": "A1.json retained total:null after Wiley citation export was not recognizable RIS.",
            "A2_adapter_failure": "A2.json retained total:null after Wiley did not expose its page-scoped Export Citations control.",
            "identifier_ledger_fallback": "Successful non-mergeable ledgers validate complete two-pass DOI/source-ID sequences and visible First published day reconciliation only; they do not claim native RIS or final bibliographic export.",
        },
        "source_limit_decisions": {
            "observed_accepted_expression": "Pilot 001 accepted literal A1 at 2,770 characters.",
            "cell_ceiling": "2,700 characters, prospectively documented in query-plan.json.",
            "A2": "Complete 3,431-character expression twice produced invalid explicit-zero/positive-total state; lossless three-cell union used.",
            "BC1": "Complete 3,525-character expression changed total between passes; lossless three-cell union used.",
            "BT2": "Complete 9,013-character expression exceeds observed accepted expression; prospective lossless nine-cell union used.",
        },
        "limitations": [
            "B2 and BG1 have source failures with null totals; no complete core Stream B, expanded Stream B, or all-nine union is claimed.",
            "Wiley applies source-month bounds through 2026-08; exact-day reconciliation uses rendered First published dates and preserves no unobserved date inference.",
            "Local metadata diagnostics identify only visible confirmations; they cannot establish that an Anywhere source match is false and remove no DOI.",
        ],
    }


def _materialized_from_receipt(entries: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Small adapter for schedule summary; source events already retain union order."""
    result = {}
    for key, entry in entries.items():
        if entry.get("status") == "source_failure":
            continue
        first = []
        seen = set()
        for event in entry["source_events"]:
            if event["source_id"] not in seen:
                seen.add(event["source_id"])
                first.append(event)
        result[key] = {"unique": first}
    return result


def _ordered_union_from_entries(entries: dict[str, Any], members: Iterable[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for member in members:
        entry = entries[member]
        if entry.get("status") == "source_failure":
            continue
        for source_id in entry["ordered_source_ids"]:
            if source_id not in seen:
                seen.add(source_id)
                output.append(source_id)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-plan", type=Path, default=SEARCH_DIR / "query-plan.json")
    parser.add_argument("--union-output", type=Path, default=SEARCH_DIR / "source-id-unions.json")
    parser.add_argument("--metadata-output", type=Path, default=SEARCH_DIR / "metadata-audit.json")
    parser.add_argument("--assessment-output", type=Path, default=SEARCH_DIR / "schedule-assessment.json")
    args = parser.parse_args()
    plan = load(args.query_plan)
    query_audit = validate_query_plan(plan)
    receipt, materialized = union_receipt(plan)
    metadata = metadata_audit(materialized)
    assessment = schedule_assessment(plan, query_audit, receipt, metadata)
    atomic_json(args.union_output, receipt)
    atomic_json(args.metadata_output, metadata)
    atomic_json(args.assessment_output, assessment)
    print(
        json.dumps(
            {
                "union_output": str(args.union_output),
                "metadata_output": str(args.metadata_output),
                "assessment_output": str(args.assessment_output),
                "successful_partitions": sorted(materialized),
                "investigated_sets": sorted(metadata["investigated_deduplicated_sets_over_100"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
