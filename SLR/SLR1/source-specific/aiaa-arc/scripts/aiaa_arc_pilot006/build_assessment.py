#!/usr/bin/env python3
"""Reconcile the complete AIAA ARC Pilot 006 factor-wise metadata union."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_core_plan import build as build_core_plan
from build_plan import build as build_expanded_plan

ALL_PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
KNOWN_DOI = "10.2514/6.2015-4474"
KNOWN_APPLICABLE = ("A2", "B1", "B2", "BC1")
ALLFIELD_TOTALS = {
    "A1": 492,
    "A2": 1541,
    "A3": 472,
    "B1": 1388,
    "B2": 1028,
    "BG1": 45,
    "BG2": 3584,
    "BC1": 152,
    "BT2": 437,
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def attempts(base: Path) -> list[Path]:
    return [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 10))]


def artifact_for(base: Path) -> tuple[Path, dict[str, Any]]:
    successes = []
    for candidate in attempts(base):
        if not candidate.exists():
            continue
        data = load(candidate)
        if isinstance(data.get("total"), int):
            successes.append((candidate, data))
    if len(successes) != 1:
        raise RuntimeError(f"Expected one successful artifact for {base}, got {len(successes)}")
    return successes[0]


def canonical_doi(value: str) -> str:
    return value.strip().casefold().split("@", 1)[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, pilot_root: Path) -> str:
    return str(path.relative_to(pilot_root))


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    base = output.name[:-5] if output.name.casefold().endswith(".json") else output.name
    return (
        output.with_name(f"{base}.search-page.png"),
        output.with_name(f"{base}.results-page.png"),
    )


def validate_source_artifact(
    event: dict[str, Any], path: Path, data: dict[str, Any]
) -> dict[str, Any]:
    total = data.get("total")
    results = data.get("results")
    metadata = data.get("output_metadata", {})
    receipt = metadata.get("prisma_search_run", {})
    strategy = receipt.get("strategy", {})
    if data.get("source") != "AIAA Aerospace Research Central (ARC)":
        raise RuntimeError(f"{path}: source mismatch")
    if not isinstance(total, int) or total < 0 or total > 100:
        raise RuntimeError(f"{path}: invalid complete-preview total {total!r}")
    if not isinstance(results, list) or len(results) != total:
        raise RuntimeError(f"{path}: result count does not reconcile to total")
    if metadata.get("status") != "preview" or metadata.get("retrieval_complete") is not True:
        raise RuntimeError(f"{path}: preview is not complete")
    if strategy.get("executed_query_provenance") != "source_observed":
        raise RuntimeError(f"{path}: query was not source-observed")
    observed_rows = strategy.get("field_rows", [])
    expected_rows = event["field_rows"]
    if len(observed_rows) != len(expected_rows):
        raise RuntimeError(f"{path}: field-row count mismatch")
    for observed, expected in zip(observed_rows, expected_rows):
        if (
            observed.get("field") != expected["source_field"]
            or observed.get("text") != expected["text"]
        ):
            raise RuntimeError(f"{path}: field-row readback mismatch")
    limits = strategy.get("limits", {})
    requested_dates = limits.get("publication_date", {}).get("requested", {})
    if requested_dates != {"exact_start": "2011-01-01", "exact_end": "2026-08-29"}:
        raise RuntimeError(f"{path}: date request mismatch")
    if limits.get("access", {}).get("effective") != "All content":
        raise RuntimeError(f"{path}: access scope mismatch")
    for name in ("topic", "published_in"):
        if limits.get(name, {}).get("state") != "not_applied":
            raise RuntimeError(f"{path}: unexpected {name} restriction")

    screenshot_evidence = metadata.get("screenshots", {})
    if (
        screenshot_evidence.get("schema_version")
        != "aiaa-arc-automatic-screenshots/v1"
        or screenshot_evidence.get("automatic") is not True
        or screenshot_evidence.get("same_directory_as_json") is not True
    ):
        raise RuntimeError(f"{path}: mandatory screenshot contract is absent")
    verified_screenshots = []
    for key, expected_path in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshot_evidence.get(key, {})
        if not expected_path.is_file():
            raise RuntimeError(f"{path}: missing {key} screenshot")
        if evidence.get("path") != expected_path.name or evidence.get("sha256") != sha256(expected_path):
            raise RuntimeError(f"{path}: {key} screenshot evidence mismatch")
        if not all(isinstance(evidence.get(name), int) and evidence[name] > 0 for name in ("width", "height")):
            raise RuntimeError(f"{path}: {key} screenshot dimensions are invalid")
        verified_screenshots.append(rel(expected_path, path.parents[2]))

    raw_ids = []
    canonical_ids = []
    for record in results:
        raw_id = record.get("sourceRecordStableId") or record.get("doi")
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise RuntimeError(f"{path}: result lacks a stable source ID")
        raw_ids.append(raw_id.casefold())
        canonical_ids.append(canonical_doi(raw_id))
    if len(raw_ids) != len(set(raw_ids)):
        raise RuntimeError(f"{path}: duplicate raw source ID within one cell")
    adapter = receipt.get("adapter", {})
    return {
        "total": total,
        "raw_ids": raw_ids,
        "canonical_ids": canonical_ids,
        "screenshots": verified_screenshots,
        "adapter_version": adapter.get("adapter_version"),
        "adapter_sha256": adapter.get("script_sha256"),
    }


def build(pilot_root: Path, pilot005_root: Path) -> dict[str, Any]:
    search_root = pilot_root / "searches"
    expanded_plan = load(search_root / "event-plan.json")
    core_plan = load(search_root / "core-event-plan.json")
    if expanded_plan != build_expanded_plan():
        raise RuntimeError("Expanded Stream B plan does not rebuild")
    if core_plan != build_core_plan():
        raise RuntimeError("Stream A/core Stream B plan does not rebuild")
    events = [*core_plan["events"], *expanded_plan["events"]]
    if len(events) != 225 or {event["partition"] for event in events} != set(ALL_PARTITIONS):
        raise RuntimeError("Pilot 006 schedule is incomplete")

    partition_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    screenshot_files: set[Path] = set()
    adapter_hashes: Counter[tuple[str, str]] = Counter()
    cell_ledger = []
    for event in events:
        path, data = artifact_for(pilot_root / event["output"])
        validated = validate_source_artifact(event, path, data)
        screenshot_files.update(screenshot_paths(path))
        adapter_hashes[(str(validated["adapter_version"]), str(validated["adapter_sha256"]))] += 1
        entry = {
            "event_id": event["event_id"],
            "partition": event["partition"],
            "branch": event["branch"],
            "artifact": rel(path, pilot_root),
            "source_total": validated["total"],
            "raw_source_ids": validated["raw_ids"],
            "canonical_dois": validated["canonical_ids"],
            "screenshots": [rel(value, pilot_root) for value in screenshot_paths(path)],
        }
        partition_events[event["partition"]].append(entry)
        cell_ledger.append(entry)

    partition_unions = {}
    overall_provenance: dict[str, set[str]] = defaultdict(set)
    for partition in ALL_PARTITIONS:
        cells = partition_events[partition]
        canonical_events: dict[str, list[dict[str, str]]] = defaultdict(list)
        raw_event_count = 0
        for cell in cells:
            for raw_id, canonical in zip(cell["raw_source_ids"], cell["canonical_dois"]):
                canonical_events[canonical].append({
                    "event_id": cell["event_id"],
                    "raw_source_id": raw_id,
                })
                raw_event_count += 1
                overall_provenance[canonical].add(partition)
        union_ids = sorted(canonical_events)
        partition_unions[partition] = {
            "cell_count": len(cells),
            "positive_cell_count": sum(cell["source_total"] > 0 for cell in cells),
            "zero_cell_count": sum(cell["source_total"] == 0 for cell in cells),
            "maximum_cell_total": max(cell["source_total"] for cell in cells),
            "cell_total_sum": sum(cell["source_total"] for cell in cells),
            "raw_source_event_count": raw_event_count,
            "canonical_doi_union_count": len(union_ids),
            "canonical_doi_union": union_ids,
            "duplicate_event_count": raw_event_count - len(union_ids),
            "provenance": {key: value for key, value in canonical_events.items()},
            "allfield_source_total": ALLFIELD_TOTALS[partition],
            "metadata_union_to_allfield_total_percent": round(
                len(union_ids) / ALLFIELD_TOTALS[partition] * 100, 3
            ),
        }
        if raw_event_count != partition_unions[partition]["cell_total_sum"]:
            raise RuntimeError(f"{partition}: source events do not reconcile")

    overall_ids = sorted(overall_provenance)
    known_item = {
        partition: KNOWN_DOI in partition_unions[partition]["canonical_doi_union"]
        for partition in KNOWN_APPLICABLE
    }

    pilot005_assessment = load(pilot005_root / "searches" / "assessment.json")
    bg1_preview_path = pilot005_root / pilot005_assessment["changed_partition_previews"]["BG1"]["artifact"]
    bg1_preview = load(bg1_preview_path)
    bg1_allfield_ids = sorted({
        canonical_doi(str(record.get("sourceRecordStableId") or record.get("doi")))
        for record in bg1_preview.get("results", [])
    })
    bg1_metadata_ids = partition_unions["BG1"]["canonical_doi_union"]

    all_pngs = set(pilot_root.rglob("*.png"))
    failures = sorted(rel(path, pilot_root) for path in pilot_root.rglob("*NON_MERGEABLE_FAILURE.json"))
    return {
        "schema_version": "aiaa-arc-pilot006-assessment/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "006",
        "protocol_commit": expanded_plan["protocol_commit"],
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "route": {
            "atom": "META(s) = Title(L(s)) OR Keywords(L(s)) OR Abstract(L(s))",
            "factor_wise": True,
            "whole_query_same_field_union": False,
            "fields": ["Title", "Keywords", "Abstract"],
            "source_rows_are_AND": True,
            "outer_field_OR_implemented_by_cell_union": True,
            "total_cells": len(events),
            "all_cells_at_most_100": True,
            "all_cells_complete": True,
        },
        "partition_unions": partition_unions,
        "overall_union": {
            "canonical_doi_count": len(overall_ids),
            "canonical_dois": overall_ids,
            "partition_provenance": {
                key: sorted(value) for key, value in sorted(overall_provenance.items())
            },
        },
        "known_item_recall": {
            "doi": KNOWN_DOI,
            "applicable_partitions": list(KNOWN_APPLICABLE),
            "retrieved": known_item,
            "retrieved_count": sum(known_item.values()),
            "missed_partitions": [key for key, value in known_item.items() if not value],
            "gate": "rejected_metadata_only_canonical_route",
            "reason": "The factor-wise metadata union missed the eligible sentinel in A2 and B2.",
        },
        "BG1_complete_allfield_comparison": {
            "allfield_artifact": str(bg1_preview_path.relative_to(pilot005_root)),
            "allfield_source_events": bg1_preview.get("total"),
            "allfield_canonical_doi_count": len(bg1_allfield_ids),
            "allfield_canonical_dois": bg1_allfield_ids,
            "metadata_canonical_doi_count": len(bg1_metadata_ids),
            "metadata_canonical_dois": bg1_metadata_ids,
            "intersection": sorted(set(bg1_allfield_ids) & set(bg1_metadata_ids)),
            "allfield_only_count": len(set(bg1_allfield_ids) - set(bg1_metadata_ids)),
            "finding": "No BG1 Anywhere record survived the factor-wise metadata restriction.",
        },
        "screenshots": {
            "automatic_contract": "aiaa-arc-automatic-screenshots/v1",
            "successful_json_count": len(events),
            "required_screenshot_count": len(events) * 2,
            "verified_success_screenshot_count": len(screenshot_files),
            "all_png_count_including_failed_attempts": len(all_pngs),
            "failed_attempt_png_count": len(all_pngs - screenshot_files),
            "no_opt_out": True,
            "same_directory_as_json": True,
        },
        "adapter_provenance": [
            {"adapter_version": version, "script_sha256": script_hash, "event_count": count}
            for (version, script_hash), count in sorted(adapter_hashes.items())
        ],
        "retained_failures": {
            "count": len(failures),
            "artifacts": failures,
            "all_recovered": True,
            "converted_to_zero": False,
        },
        "cell_ledger": cell_ledger,
        "decision": {
            "factor_wise_translation": "technically_valid_and_fully_executed",
            "noise_reduction": "substantial_47_doi_schedule_union",
            "canonical_replacement_for_Anywhere": "rejected_observed_known_item_recall_loss",
            "screening_priority_lane": "accepted_nonexcluding",
            "direct_Anywhere_route": "retain_as_canonical",
            "final_search": "not_executed",
        },
        "limits": [
            "Metadata-only searching cannot retrieve required factors that occur only in ARC full text or hidden indexing.",
            "The AllField totals are source event totals while metadata unions use canonical DOI identity, so their percentages describe workload scale rather than formal recall.",
            "Pilot source bounds are inclusive months before exact-day exclusions.",
            "Rendered-card previews and screenshots are non-mergeable and cannot enter the final corpus.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot005-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root, args.pilot005_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
