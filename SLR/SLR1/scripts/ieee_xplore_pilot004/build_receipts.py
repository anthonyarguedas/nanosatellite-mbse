#!/usr/bin/env python3
"""Build deterministic Pilot 004 two-pass, union, and boundary receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEARCHES = ROOT / "source-specific/ieee-xplore/pilots/004/searches"
SCHEDULE_PATH = SEARCHES / "schedule.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def ordered_hash(ids: list[str]) -> str:
    digest = hashlib.sha256()
    for value in ids:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def expected_cells(schedule: dict[str, Any]) -> dict[str, tuple[str, str]]:
    return {
        cell["query"]: (partition["partition_id"], cell["cell_id"])
        for partition in schedule["partitions"]
        for cell in partition["cells"]
    }


def ids_from_result(payload: dict[str, Any]) -> list[str]:
    total = payload.get("total")
    records = payload.get("results")
    if not isinstance(total, int) or isinstance(total, bool) or not isinstance(records, list):
        raise ValueError("a completed capture needs integer total and results")
    ids = [record.get("paperId") for record in records if isinstance(record, dict)]
    if len(ids) != len(records) or any(not isinstance(value, str) or not value.isdigit() for value in ids):
        raise ValueError("a completed capture needs numeric Article Numbers")
    if total != len(ids) or len(ids) != len(set(ids)):
        raise ValueError("a completed capture must exhaust unique Article Numbers")
    return ids


def year_observation(payload: dict[str, Any]) -> dict[str, Any]:
    readback = payload.get("output_metadata", {}).get("publication_year_readback", {})
    return {
        "state": readback.get("state"),
        "requested_search_window": readback.get("requested_search_window"),
        "native_range_echo": readback.get("native_range_echo"),
        "result_refinement_range": readback.get("result_refinement_range"),
        "result_refinement_range_within_requested_window": readback.get(
            "result_refinement_range_within_requested_window"
        ),
    }


def valid_year(payload: dict[str, Any]) -> bool:
    observed = year_observation(payload)
    if observed["requested_search_window"] != "2011_2026_Year":
        return False
    if payload["total"] == 0:
        return observed["state"] == "not_needed_source_zero"
    return (
        observed["state"] == "exact_source_echo"
        and observed["native_range_echo"] == "2011_2026_Year"
    ) or (
        observed["state"] == "result_refinement_range_within_requested_window"
        and observed["result_refinement_range_within_requested_window"] is True
    )


def capture_dirs() -> list[Path]:
    return sorted(
        path
        for path in SEARCHES.glob("two-pass*")
        if path.is_dir()
    )


def rebuild_capture_receipts(schedule: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    expected = expected_cells(schedule)
    captures: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for directory in capture_dirs():
        for pass_one_path in sorted(directory.glob("*-pass1.json")):
            prefix = pass_one_path.name.removesuffix("-pass1.json")
            pass_two_path = directory / f"{prefix}-pass2.json"
            if not pass_two_path.exists():
                continue
            first, second = load(pass_one_path), load(pass_two_path)
            query = first.get("executed_query")
            location = expected.get(query)
            if location is None or second.get("executed_query") != query:
                continue
            partition_id, cell_id = location
            try:
                first_ids, second_ids = ids_from_result(first), ids_from_result(second)
                complete = (
                    first_ids == second_ids
                    and valid_year(first)
                    and valid_year(second)
                    and first.get("output_metadata", {}).get("retrieval_complete") is True
                    and second.get("output_metadata", {}).get("retrieval_complete") is True
                    and all(
                        item["total"] == 0
                        or item.get("output_metadata", {})
                        .get("prisma_search_run", {})
                        .get("strategy", {})
                        .get("sort", {})
                        .get("value")
                        == "Oldest"
                        for item in (first, second)
                    )
                )
            except (KeyError, ValueError):
                first_ids, second_ids, complete = [], [], False
            receipt = {
                "schema_version": "slr1-ieee-xplore-pilot004-fresh-two-pass-receipt/v1",
                "source": "IEEE Xplore",
                "partition_id": partition_id,
                "cell_id": cell_id,
                "purpose": "Pilot-only stable Article Number reconciliation; not a final search.",
                "controls": {
                    "requested_search_window": "2011_2026_Year",
                    "diagnostic_cutoff": "2026-08-29",
                    "date_added": "not applied; separate indexing-date control",
                    "language": "not applied",
                    "publication_type": "not applied",
                    "access": "all / not restricted",
                    "wildcards": "not used",
                },
                "pass_artifacts": [pass_one_path.name, pass_two_path.name],
                "pass_1_year_readback": year_observation(first),
                "pass_2_year_readback": year_observation(second),
                "source_totals": [first.get("total"), second.get("total")],
                "ordered_article_number_sha256": [ordered_hash(first_ids), ordered_hash(second_ids)],
                "ordered_article_numbers_identical": first_ids == second_ids,
                "stable_article_number_count": len(first_ids) if complete else None,
                "reconciled": complete,
                "transport": first.get("output_metadata", {}).get("pilot_transport"),
            }
            receipt_path = directory / f"{prefix}-two-pass-receipt.json"
            dump(receipt_path, receipt)
            if complete:
                captures[(partition_id, cell_id)].append(
                    {
                        "pass_1": rel(pass_one_path),
                        "pass_2": rel(pass_two_path),
                        "receipt": rel(receipt_path),
                        "ids": first_ids,
                        "total": first["total"],
                    }
                )
    return captures


def collect_source_events(schedule: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    expected = expected_cells(schedule)
    events: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(SEARCHES.rglob("*.json")):
        if path.name.startswith(".") or "two-pass" in path.name or path.name in {
            "schedule.json",
            "union-receipt.json",
            "year-boundary-receipt.json",
            "over-100-investigation.json",
            "pilot-validation.json",
        }:
            continue
        payload = load(path)
        query = payload.get("executed_query")
        location = expected.get(query)
        if location is None:
            continue
        metadata = payload.get("output_metadata", {})
        events[location].append(
            {
                "artifact": rel(path),
                "total": payload.get("total"),
                "status": metadata.get("status"),
                "error_stage": metadata.get("error_stage"),
                "year_readback": metadata.get("publication_year_readback", {}).get("state"),
                "count_only": metadata.get("count_only"),
            }
        )
    return events


def build_union_receipt(schedule: dict[str, Any], captures: dict[tuple[str, str], list[dict[str, Any]]], events: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    partitions: list[dict[str, Any]] = []
    cross_membership: dict[str, list[str]] = defaultdict(list)
    for partition in schedule["partitions"]:
        partition_id = partition["partition_id"]
        complete = True
        partial_ids: list[str] = []
        cells: list[dict[str, Any]] = []
        for cell in partition["cells"]:
            cell_id = cell["cell_id"]
            cell_captures = captures.get((partition_id, cell_id), [])
            successful = cell_captures[0] if cell_captures else None
            if successful is None:
                complete = False
            else:
                partial_ids.extend(successful["ids"])
                for article_number in successful["ids"]:
                    cross_membership[article_number].append(f"{partition_id}/{cell_id}")
            cells.append(
                {
                    "cell_id": cell_id,
                    "query_sha256": cell["query_sha256"],
                    "reconciled_capture": None if successful is None else {
                        key: successful[key] for key in ("pass_1", "pass_2", "receipt", "total")
                    },
                    "source_events": events.get((partition_id, cell_id), []),
                }
            )
        deduplicated = list(dict.fromkeys(partial_ids))
        partitions.append(
            {
                "partition_id": partition_id,
                "expected_cell_count": len(partition["cells"]),
                "cells": cells,
                "union_status": "complete" if complete else "incomplete_failure_retained",
                "deduplicated_article_number_union": deduplicated if complete else None,
                "deduplicated_article_number_count": len(deduplicated) if complete else None,
                "partial_reconciled_article_numbers_not_a_union": deduplicated if not complete else None,
                "partial_reconciled_article_number_count": len(deduplicated) if not complete else None,
            }
        )
    return {
        "schema_version": "slr1-ieee-xplore-pilot004-union-receipt/v1",
        "source": "IEEE Xplore",
        "pilot_id": "004",
        "purpose": "Pilot-only literal-cell union accounting. No event is a final search or is merged into the review baseline.",
        "controls": {
            "publication_year_apply": "native inclusive 2011_2026_Year",
            "diagnostic_cutoff": "2026-08-29",
            "date_added": "separate indexing-date control; not applied",
            "language": "not applied",
            "publication_type": "not applied",
            "access": "all / not restricted",
            "wildcards": "not used or accepted",
            "controlled_vocabulary": "not applied; no validated source-specific supplement",
        },
        "partitions": partitions,
        "cross_partition_article_number_membership": dict(sorted(cross_membership.items())),
        "final_search": False,
    }


def build_boundary_receipt() -> dict[str, Any]:
    path = SEARCHES / "year-boundary-2022-2023.json"
    payload = load(path)
    ids = [record.get("paperId") for record in payload.get("results", [])]
    years = {record.get("paperId"): record.get("year") for record in payload.get("results", [])}
    readback = payload.get("output_metadata", {}).get("publication_year_readback", {})
    return {
        "schema_version": "slr1-ieee-xplore-pilot004-year-boundary-receipt/v1",
        "source": "IEEE Xplore",
        "artifact": rel(path),
        "known_article_numbers": {
            "outside_lower_boundary": "9438156",
            "lower_endpoint": "10398967",
            "upper_endpoint": "10436175",
        },
        "requested_inclusive_window": "[2022,2023]",
        "source_total": payload.get("total"),
        "returned_article_numbers": ids,
        "returned_years": years,
        "assertions": {
            "lower_endpoint_retained": "10398967" in ids and years.get("10398967") == 2022,
            "upper_endpoint_retained": "10436175" in ids and years.get("10436175") == 2023,
            "known_2021_record_excluded": "9438156" not in ids,
            "native_readback": readback.get("state") == "exact_source_echo" and readback.get("native_range_echo") == "2022_2023_Year",
            "complete_source_run": payload.get("output_metadata", {}).get("prisma_search_run", {}).get("completion_status") == "complete",
        },
        "capture_contract": "The adapter was invoked with --require-complete. Its compact persisted result retains completion_status=complete but not the pass-count fields; the linked artifact remains the authoritative boundary result.",
        "result_page_refinement_interval": readback.get("result_refinement_range"),
        "literal_bracket_form": "not_reproduced; fixture-only if cited elsewhere",
        "date_added": "not requested; it is not Date of Publication",
    }


def build_over_100_receipt(union: dict[str, Any]) -> dict[str, Any]:
    b2 = next(item for item in union["partitions"] if item["partition_id"] == "B2")
    source_counts = [
        event
        for cell in b2["cells"]
        for event in cell["source_events"]
        if event.get("total") is not None
    ]
    return {
        "schema_version": "slr1-ieee-xplore-pilot004-over-100-investigation/v1",
        "source": "IEEE Xplore",
        "partition_id": "B2",
        "threshold": 100,
        "source_count_observations": source_counts,
        "deduplicated_stable_article_number_union": b2["deduplicated_article_number_union"],
        "investigation": {
            "status": "stable_union_unavailable_not_treated_as_a_union",
            "finding": "A native-Year-Apply count-only event reported 131, but the full stable-ID capture failed closed when IEEE omitted page-size evidence outside a complete small page. The subsequent explicit normal result route was also inconsistent. No 100-record prefix or local date-filtered substitute was promoted to a union.",
            "linked_failure_events": [
                event
                for cell in b2["cells"]
                for event in cell["source_events"]
                if event.get("total") is None
            ],
            "action": "Retain total and failures as pilot diagnostics; leave B2 union null and do not merge it into a final search.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    schedule = load(SCHEDULE_PATH)
    captures = rebuild_capture_receipts(schedule)
    events = collect_source_events(schedule)
    union = build_union_receipt(schedule, captures, events)
    boundary = build_boundary_receipt()
    over_100 = build_over_100_receipt(union)
    if args.write:
        dump(SEARCHES / "union-receipt.json", union)
        dump(SEARCHES / "year-boundary-receipt.json", boundary)
        dump(SEARCHES / "over-100-investigation.json", over_100)
    print(
        json.dumps(
            {
                "complete_partitions": [
                    item["partition_id"]
                    for item in union["partitions"]
                    if item["union_status"] == "complete"
                ],
                "incomplete_partitions": [
                    item["partition_id"]
                    for item in union["partitions"]
                    if item["union_status"] != "complete"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
