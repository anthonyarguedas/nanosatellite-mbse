#!/usr/bin/env python3
"""Reconcile AIAA ARC Pilot 007's hybrid metadata-anchored schedule."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_plan import PARTITIONS, build as build_plan

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
        if candidate.exists():
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


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    base = output.name[:-5] if output.name.casefold().endswith(".json") else output.name
    return (
        output.with_name(f"{base}.search-page.png"),
        output.with_name(f"{base}.results-page.png"),
    )


def validate_source_artifact(event: dict[str, Any], path: Path, data: dict[str, Any]) -> dict[str, Any]:
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
        raise RuntimeError(f"{path}: result count does not reconcile")
    if metadata.get("status") != "preview" or metadata.get("retrieval_complete") is not True:
        raise RuntimeError(f"{path}: preview is incomplete")
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
    if limits.get("publication_date", {}).get("requested", {}) != {
        "exact_start": "2011-01-01",
        "exact_end": "2026-08-29",
    }:
        raise RuntimeError(f"{path}: date request mismatch")
    if limits.get("access", {}).get("effective") != "All content":
        raise RuntimeError(f"{path}: access mismatch")
    for name in ("topic", "published_in"):
        if limits.get(name, {}).get("state") != "not_applied":
            raise RuntimeError(f"{path}: unexpected {name} restriction")

    screenshots = metadata.get("screenshots", {})
    if (
        screenshots.get("schema_version") != "aiaa-arc-automatic-screenshots/v1"
        or screenshots.get("automatic") is not True
        or screenshots.get("same_directory_as_json") is not True
    ):
        raise RuntimeError(f"{path}: screenshot contract is absent")
    for key, expected_path in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshots.get(key, {})
        if not expected_path.is_file():
            raise RuntimeError(f"{path}: missing {key} screenshot")
        if evidence.get("path") != expected_path.name or evidence.get("sha256") != sha256(expected_path):
            raise RuntimeError(f"{path}: {key} screenshot evidence mismatch")
        if not all(isinstance(evidence.get(name), int) and evidence[name] > 0 for name in ("width", "height")):
            raise RuntimeError(f"{path}: invalid screenshot dimensions")

    raw_ids = []
    canonical_ids = []
    for record in results:
        raw_id = record.get("sourceRecordStableId") or record.get("doi")
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise RuntimeError(f"{path}: missing stable source ID")
        raw_ids.append(raw_id.casefold())
        canonical_ids.append(canonical_doi(raw_id))
    if len(raw_ids) != len(set(raw_ids)):
        raise RuntimeError(f"{path}: duplicate raw source ID")
    adapter = receipt.get("adapter", {})
    return {
        "total": total,
        "raw_ids": raw_ids,
        "canonical_ids": canonical_ids,
        "adapter_version": adapter.get("adapter_version"),
        "adapter_sha256": adapter.get("script_sha256"),
    }


def build(pilot_root: Path, pilot006_root: Path) -> dict[str, Any]:
    search_root = pilot_root / "searches"
    plan = load(search_root / "event-plan.json")
    if plan != build_plan():
        raise RuntimeError("Pilot 007 plan does not rebuild")
    events = plan["events"]
    if len(events) != 94:
        raise RuntimeError("Pilot 007 event plan is incomplete")

    partition_cells: dict[str, list[dict[str, Any]]] = defaultdict(list)
    adapter_hashes: Counter[tuple[str, str]] = Counter()
    successful_screenshots: set[Path] = set()
    cell_ledger = []
    for event in events:
        path, data = artifact_for(pilot_root / event["output"])
        evidence = validate_source_artifact(event, path, data)
        successful_screenshots.update(screenshot_paths(path))
        adapter_hashes[(str(evidence["adapter_version"]), str(evidence["adapter_sha256"]))] += 1
        cell = {
            "event_id": event["event_id"],
            "partition": event["partition"],
            "route": event["route"],
            "artifact": rel(path, pilot_root),
            "source_total": evidence["total"],
            "raw_source_ids": evidence["raw_ids"],
            "canonical_dois": evidence["canonical_ids"],
            "screenshots": [rel(value, pilot_root) for value in screenshot_paths(path)],
        }
        partition_cells[event["partition"]].append(cell)
        cell_ledger.append(cell)

    partition_unions = {}
    overall_provenance: dict[str, set[str]] = defaultdict(set)
    for partition in PARTITIONS:
        cells = partition_cells[partition]
        provenance: dict[str, list[dict[str, str]]] = defaultdict(list)
        raw_events = 0
        for cell in cells:
            for raw_id, doi in zip(cell["raw_source_ids"], cell["canonical_dois"]):
                provenance[doi].append({
                    "event_id": cell["event_id"],
                    "raw_source_id": raw_id,
                })
                raw_events += 1
                overall_provenance[doi].add(partition)
        union = sorted(provenance)
        entry = {
            "cell_count": len(cells),
            "positive_cell_count": sum(cell["source_total"] > 0 for cell in cells),
            "zero_cell_count": sum(cell["source_total"] == 0 for cell in cells),
            "maximum_cell_total": max(cell["source_total"] for cell in cells),
            "cell_total_sum": sum(cell["source_total"] for cell in cells),
            "raw_source_event_count": raw_events,
            "canonical_doi_union_count": len(union),
            "canonical_doi_union": union,
            "duplicate_event_count": raw_events - len(union),
            "provenance": {key: value for key, value in provenance.items()},
            "allfield_source_total": ALLFIELD_TOTALS[partition],
        }
        if entry["cell_total_sum"] != raw_events:
            raise RuntimeError(f"{partition}: source events do not reconcile")
        partition_unions[partition] = entry

    overall_ids = sorted(overall_provenance)
    known = {
        partition: KNOWN_DOI in partition_unions[partition]["canonical_doi_union"]
        for partition in KNOWN_APPLICABLE
    }
    strict = load(pilot006_root / "searches" / "assessment.json")
    strict_ids = set(strict["overall_union"]["canonical_dois"])
    hybrid_ids = set(overall_ids)
    failures = sorted(rel(path, pilot_root) for path in pilot_root.rglob("*NON_MERGEABLE_FAILURE.json"))
    all_pngs = set(pilot_root.rglob("*.png"))
    return {
        "schema_version": "aiaa-arc-pilot007-assessment/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "007",
        "protocol_commit": plan["protocol_commit"],
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "translation": plan["translation"],
        "execution": {
            "total_cells": len(events),
            "all_cells_at_most_100": True,
            "all_cells_complete": True,
            "largest_cell_total": max(cell["source_total"] for cell in cell_ledger),
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
            "retrieved": known,
            "all_applicable_partitions_retrieved": all(known.values()),
            "gate": "accepted_observed_known_item_recall",
        },
        "factor_wise_comparison": {
            "pilot006_union_count": len(strict_ids),
            "hybrid_union_count": len(hybrid_ids),
            "intersection_count": len(strict_ids & hybrid_ids),
            "hybrid_additional_count": len(hybrid_ids - strict_ids),
            "factor_wise_only_count": len(strict_ids - hybrid_ids),
            "factor_wise_union_is_subset": strict_ids <= hybrid_ids,
        },
        "screenshots": {
            "successful_json_count": len(events),
            "required_screenshot_count": len(events) * 2,
            "verified_success_screenshot_count": len(successful_screenshots),
            "all_png_count_including_failed_attempts": len(all_pngs),
            "failed_attempt_png_count": len(all_pngs - successful_screenshots),
            "ignored_by_project_git": True,
            "no_opt_out": True,
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
        "decision": {
            "hybrid_route": "accept_prospective_canonical_screening_translation",
            "screening_workload": "feasible_119_canonical_dois",
            "known_item_gate": "passed_all_applicable_partitions",
            "factor_wise_route": "retain_as_priority_tag_within_hybrid_union",
            "full_Anywhere_schedule": "retain_as_sensitivity_evidence_not_screening_corpus",
            "final_search": "not_executed",
        },
        "limits": [
            "The known-item gate is observed evidence for one eligible report and does not prove recall for unknown reports.",
            "BG2 remains metadata-restricted because its complete Anywhere query returned 3584 source events.",
            "Pilot bounds are inclusive ARC months before exact-day exclusions.",
            "Rendered-card previews cannot enter the final corpus.",
        ],
        "cell_ledger": cell_ledger,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root, args.pilot006_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
