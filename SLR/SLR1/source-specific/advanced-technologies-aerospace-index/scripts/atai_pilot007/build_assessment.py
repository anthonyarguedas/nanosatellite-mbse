#!/usr/bin/env python3
"""Build the ATAI Pilot 007 schedule assessment."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from queries import (
    C1_FIXED_TERMS,
    CHANGED_IDS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    P_TERMS,
    SCHEDULE_IDS,
    TPRECISE_TERMS,
)

VISIBLE_BLOCKS = {
    "P": P_TERMS,
    "M_B": MB_TERMS,
    "G_model_fixed": GMODEL_FIXED_TERMS,
    "G_mission": GMISSION_TERMS,
    "G_mission_exact": GMISSION_EXACT_TERMS,
    "G_structure_fixed": GSTRUCTURE_FIXED_TERMS,
    "G_product": GPRODUCT_TERMS,
    "G_product_exact": GPRODUCT_EXACT_TERMS,
    "G_variation": GVARIATION_TERMS,
    "C1_fixed": C1_FIXED_TERMS,
    "G_DSL": GDSL_TERMS,
    "T_precise": TPRECISE_TERMS,
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def stable_ids(artifact: dict[str, Any]) -> list[str]:
    return [str(record["paperId"]) for record in artifact.get("results", [])]


def visible_hits(record: dict[str, Any]) -> dict[str, list[str]]:
    text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
    result = {}
    for block, terms in VISIBLE_BLOCKS.items():
        hits = [term for term in terms if term.lower() in text]
        if hits:
            result[block] = hits
    return result


def old_ids(pilot003: Path, pilot006: Path, partition: str) -> list[str]:
    if partition in ("BG1", "BG2"):
        artifact = load(pilot003 / "searches" / f"{partition}-stable-id-pass2.json")
    else:
        artifact = load(
            pilot006
            / "searches"
            / "retry4"
            / f"{partition}-augmented-card-pass1.json"
        )
    return stable_ids(artifact)


def build(root: Path, pilot003: Path, pilot006: Path) -> dict[str, Any]:
    searches = root / "searches"
    plan = load(searches / "event-plan.json")
    receipt = load(searches / "run-receipt.json")
    marking = load(searches / "nonmergeable-marking.json")
    errors: list[str] = []

    if receipt.get("status") != "complete" or receipt.get("completed_event_count") != 22:
        errors.append("The predeclared run did not complete all 22 events.")

    counts: dict[str, dict[str, Any]] = {}
    for partition in SCHEDULE_IDS:
        first = load(searches / "counts" / "pass1" / f"{partition}.json")
        second = load(searches / "counts" / "pass2" / f"{partition}.json")
        first_total = first.get("total")
        second_total = second.get("total")
        counts[partition] = {
            "pass_1": first_total,
            "pass_2": second_total,
            "passes_equal": first_total == second_total,
        }
        if first_total != second_total:
            errors.append(f"Repeated totals differ for {partition}.")

    changed_records: dict[str, Any] = {}
    changed_sets: dict[str, set[str]] = {}
    title_groups: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for partition in CHANGED_IDS:
        artifact = load(searches / "records" / f"{partition}.json")
        metadata = artifact.get("output_metadata", {})
        ids = stable_ids(artifact)
        changed_sets[partition] = set(ids)
        if (
            metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or artifact.get("total") != len(ids)
            or artifact.get("total") != counts[partition]["pass_1"]
        ):
            errors.append(f"Strict complete capture failed for {partition}.")
        if len(ids) != len(set(ids)) or any(not paper_id.isdigit() for paper_id in ids):
            errors.append(f"Stable IDs are invalid for {partition}.")

        profiles = []
        for record in artifact.get("results", []):
            title = str(record.get("title", ""))
            title_groups[title.casefold()].append(
                {"partition": partition, "paper_id": str(record["paperId"]), "title": title}
            )
            profiles.append(
                {
                    "paper_id": str(record["paperId"]),
                    "title": title,
                    "year": record.get("year"),
                    "visible_title_or_abstract_hits": visible_hits(record),
                }
            )
        changed_records[partition] = {
            "source_total": artifact.get("total"),
            "stable_ids_in_source_order": ids,
            "records": profiles,
        }

    changed_union = set().union(*changed_sets.values())
    intersections = {}
    for index, left in enumerate(CHANGED_IDS):
        for right in CHANGED_IDS[index + 1 :]:
            overlap = sorted(changed_sets[left] & changed_sets[right])
            if overlap:
                intersections[f"{left}_and_{right}"] = overlap

    repeated_titles = [
        {
            "title": members[0]["title"],
            "records": members,
        }
        for members in title_groups.values()
        if len(members) > 1
    ]

    old_counts = {}
    for partition in CHANGED_IDS:
        prior = load(
            pilot006
            / "searches"
            / "retry7"
            / f"final-language-{partition}-english-count-pass1.json"
        )
        old_counts[partition] = prior.get("total")

    historical = {}
    for partition in CHANGED_IDS:
        previous_ids = old_ids(pilot003, pilot006, partition)
        current_ids = changed_records[partition]["stable_ids_in_source_order"]
        previous_set = set(previous_ids)
        current_set = set(current_ids)
        historical[partition] = {
            "superseded_total": old_counts[partition],
            "current_total": counts[partition]["pass_1"],
            "total_delta": counts[partition]["pass_1"] - old_counts[partition],
            "superseded_stable_ids": previous_ids,
            "current_stable_ids": current_ids,
            "retained_ids": [paper_id for paper_id in current_ids if paper_id in previous_set],
            "current_only_ids": [paper_id for paper_id in current_ids if paper_id not in previous_set],
            "superseded_only_ids": [paper_id for paper_id in previous_ids if paper_id not in current_set],
        }

    source_artifacts = []
    successful_source_artifacts = []
    retained_failure_artifacts = []
    screenshot_files = []
    screenshot_events = []
    for path in sorted(searches.rglob("*.json")):
        value = load(path)
        if value.get("schema_version") != "academic-search-result/v1":
            continue
        source_artifacts.append(path)
        metadata = value.get("output_metadata", {})
        if metadata.get("status") == "error":
            retained_failure_artifacts.append(path)
        else:
            successful_source_artifacts.append(path)
            screenshot_receipt = metadata.get("screenshots", {})
            if (
                screenshot_receipt.get("schema_version") != "atai-automatic-screenshots/v1"
                or screenshot_receipt.get("automatic") is not True
            ):
                errors.append(f"Screenshot receipt is missing: {path.relative_to(root)}")
            screenshot_event = {"json": str(path.relative_to(root))}
            for key, suffix in (
                ("search_page", ".search-page.png"),
                ("results_page", ".results-page.png"),
            ):
                screenshot = path.with_name(f"{path.stem}{suffix}")
                if screenshot.is_file():
                    screenshot_files.append(screenshot)
                    screenshot_event[key] = {
                        **screenshot_receipt.get(key, {}),
                        "repository_path": str(screenshot.relative_to(root)),
                    }
                else:
                    errors.append(f"Screenshot file is missing: {screenshot.relative_to(root)}")
            screenshot_events.append(screenshot_event)
        if (
            value.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
            or metadata.get("pilot_only") is not True
        ):
            errors.append(f"Source artifact is mergeable: {path.relative_to(root)}")
    if len(source_artifacts) != marking.get("marked_artifact_count"):
        errors.append("The non-mergeable receipt does not cover every source artifact.")
    if len(successful_source_artifacts) != 22 or len(retained_failure_artifacts) != 1:
        errors.append("The source artifact success and retained-failure counts differ.")
    if len(screenshot_files) != 2 * len(successful_source_artifacts):
        errors.append("Every successful source event does not have two screenshots.")

    plan_events = {event["event_id"]: event for event in plan.get("events", [])}
    for outcome in receipt.get("outcomes", []):
        event = plan_events.get(outcome.get("event_id"))
        if not event:
            errors.append(f"Run outcome lacks a plan event: {outcome.get('event_id')}")
            continue
        artifact = load(root / outcome["output"])
        if artifact.get("requested_query") != event["query"]:
            errors.append(f"Source query readback differs for {event['event_id']}.")
        strategy = artifact.get("output_metadata", {}).get("prisma_search_run", {}).get("strategy", {})
        limits = strategy.get("limits", {})
        publication_date = limits.get("publication_date", {}).get("effective", {})
        if (
            strategy.get("search_scope") != "Advanced Technologies & Aerospace Index"
            or strategy.get("query_syntax", {}).get("spelling_variants") is not False
            or strategy.get("query_syntax", {}).get("form_variants") is not False
            or limits.get("language", {}).get("value") != "LA(English)"
            or publication_date.get("start") != "2011-01-01"
            or publication_date.get("end") != "2026-08-29"
            or strategy.get("sort", {}).get("value") != "DateAsc"
        ):
            errors.append(f"Source controls differ for {event['event_id']}.")

    query_lengths = plan.get("translation", {}).get("query_lengths", {})
    if (
        set(query_lengths) != set(SCHEDULE_IDS)
        or any(length >= 50_000 for length in query_lengths.values())
        or any("NEAR/" in event["query"].upper() for event in plan.get("events", []))
        or any("*" in event["query"] or "?" in event["query"] for event in plan.get("events", []))
    ):
        errors.append("A query violates the accepted no-proximity, no-wildcard direct translation.")

    return {
        "schema_version": "atai-pilot-007-assessment/v1",
        "status": "complete" if not errors else "error",
        "source": plan.get("source"),
        "pilot": "007",
        "protocol_commit": plan.get("protocol_commit"),
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": "accept_direct_no_proximity_translation",
        "decision_basis": (
            "All nine complete expressions received exact source readback twice with identical totals. "
            "The four changed partitions passed strict complete full-record capture, and every event saved both required screenshots."
        ),
        "translation": {
            "ordinary_atom": "(NOFT(L(s)) OR IF.EXACT(L(s)))",
            "compound_blocks": plan.get("translation", {}).get("blocks"),
            "query_lengths": query_lengths,
            "maximum_query_characters": max(query_lengths.values()),
            "proximity_operators": 0,
            "pair_expansions": 0,
            "wildcards": 0,
            "query_cells_per_partition": 1,
        },
        "repeated_partition_totals": counts,
        "changed_partition_capture": changed_records,
        "changed_partition_union": {
            "record_occurrences": sum(len(ids) for ids in changed_sets.values()),
            "deduplicated_stable_ids": len(changed_union),
            "stable_ids": sorted(changed_union),
            "cross_partition_intersections": intersections,
            "repeated_title_groups": repeated_titles,
        },
        "superseded_schedule_comparison": {
            "scope_warning": (
                "The prior expressions implement superseded concept definitions. "
                "Their sets describe semantic schedule changes and are not a recall benchmark."
            ),
            "BG1_BG2_id_source": "Pilot 003 complete NOFT captures; Pilot 006 found no IF.EXACT count delta for either partition.",
            "BC1_BT2_id_source": "Pilot 006 complete augmented card captures.",
            "source_artifacts": {
                "superseded_counts": {
                    partition: str(
                        pilot006
                        / "searches"
                        / "retry7"
                        / f"final-language-{partition}-english-count-pass1.json"
                    )
                    for partition in CHANGED_IDS
                },
                "superseded_ids": {
                    "BG1": str(pilot003 / "searches" / "BG1-stable-id-pass2.json"),
                    "BG2": str(pilot003 / "searches" / "BG2-stable-id-pass2.json"),
                    "BC1": str(pilot006 / "searches" / "retry4" / "BC1-augmented-card-pass1.json"),
                    "BT2": str(pilot006 / "searches" / "retry4" / "BT2-augmented-card-pass1.json"),
                },
            },
            "partitions": historical,
        },
        "precision_observation": (
            "Every changed total was below 100. Visible metadata includes expected expansion noise, "
            "especially repeated BG2 metamodel records and one BC1 reference-model use outside MBSE. "
            "No result-driven narrowing is accepted because these blocks are recall concepts and final screening is authoritative."
        ),
        "controls": plan.get("controls"),
        "automatic_screenshots": {
            "required_per_successful_source_event": 2,
            "successful_source_event_count": len(successful_source_artifacts),
            "screenshot_file_count": len(screenshot_files),
            "events": screenshot_events,
        },
        "retained_source_failures": [
            str(path.relative_to(root)) for path in retained_failure_artifacts
        ],
        "source_artifact_count": len(source_artifacts),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot003-root", type=Path, required=True)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assessment = build(args.pilot_root, args.pilot003_root, args.pilot006_root)
    args.output.write_text(json.dumps(assessment, indent=2, ensure_ascii=False) + "\n")
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
