#!/usr/bin/env python3
"""Reconcile AIAA ARC Pilot 009 literal and wildcard cell pairs."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from run_pilot import screenshot_paths, validate_success
from build_plan import PARTITIONS, build as build_plan

KNOWN_DOI = "10.2514/6.2015-4474"
KNOWN_APPLICABLE = ("A2", "B1", "B2", "BC1")
VISIBLE_NANOSATELLITE_TITLES = {
    "10.2514/6.2013-5325": "EyasSat-cubed: a Low-cost On-ramp for Nanosatellite Programs",
    "10.2514/6.2017-0400": "Probabilistic Methods for Nanosatellite Systems Engineering: A Lasercom Case Study",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def attempts(base: Path) -> list[Path]:
    return [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 20))]


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


def source_ids(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    raw = []
    canonical = []
    for record in data["results"]:
        value = record.get("sourceRecordStableId") or record.get("doi")
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError("Source result lacks a stable DOI")
        raw.append(value.casefold())
        canonical.append(canonical_doi(value))
    if len(raw) != len(set(raw)):
        raise RuntimeError("Source artifact contains duplicate raw stable IDs")
    return raw, canonical


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def validate_artifact(
    pilot_root: Path,
    event: dict[str, Any],
) -> tuple[Path, dict[str, Any], list[str], list[str], tuple[str, str]]:
    path, data = artifact_for(pilot_root / event["output"])
    errors = validate_success(path, event)
    if errors:
        raise RuntimeError(f"{path}: {'; '.join(errors)}")
    raw, canonical = source_ids(data)
    receipt = data["output_metadata"]["prisma_search_run"]
    adapter = receipt["adapter"]
    adapter_key = (str(adapter.get("adapter_version")), str(adapter.get("script_sha256")))
    return path, data, raw, canonical, adapter_key


def build(pilot_root: Path, pilot007_root: Path) -> dict[str, Any]:
    plan_path = pilot_root / "searches" / "event-plan.json"
    plan = load(plan_path)
    if plan != build_plan():
        raise RuntimeError("Pilot 009 event plan does not rebuild")
    if len(plan["events"]) != 188 or len(plan["pair_ledger"]) != 94:
        raise RuntimeError("Pilot 009 paired plan is incomplete")
    events = {event["event_id"]: event for event in plan["events"]}

    partition_literal: dict[str, set[str]] = defaultdict(set)
    partition_wildcard: dict[str, set[str]] = defaultdict(set)
    overall_literal: set[str] = set()
    overall_wildcard: set[str] = set()
    adapter_counts: Counter[tuple[str, str]] = Counter()
    success_screenshots: set[Path] = set()
    pair_results = []
    literal_record_titles: dict[str, str] = {}
    wildcard_record_titles: dict[str, str] = {}

    for declared in plan["pair_ledger"]:
        literal_event = events[declared["literal_event_id"]]
        wildcard_event = events[declared["wildcard_event_id"]]
        literal_path, literal_data, literal_raw, literal_canonical, literal_adapter = validate_artifact(
            pilot_root, literal_event
        )
        wildcard_path, wildcard_data, wildcard_raw, wildcard_canonical, wildcard_adapter = validate_artifact(
            pilot_root, wildcard_event
        )
        adapter_counts[literal_adapter] += 1
        adapter_counts[wildcard_adapter] += 1
        for path in (literal_path, wildcard_path):
            for screenshot in screenshot_paths(path):
                if not screenshot.is_file():
                    raise RuntimeError(f"Missing screenshot {screenshot}")
                success_screenshots.add(screenshot)
        literal_raw_set = set(literal_raw)
        wildcard_raw_set = set(wildcard_raw)
        literal_set = set(literal_canonical)
        wildcard_set = set(wildcard_canonical)
        partition = declared["partition"]
        partition_literal[partition].update(literal_set)
        partition_wildcard[partition].update(wildcard_set)
        overall_literal.update(literal_set)
        overall_wildcard.update(wildcard_set)
        for record in literal_data["results"]:
            raw_id = record.get("sourceRecordStableId") or record.get("doi")
            literal_record_titles[canonical_doi(raw_id)] = record.get("title", "")
        for record in wildcard_data["results"]:
            raw_id = record.get("sourceRecordStableId") or record.get("doi")
            wildcard_record_titles[canonical_doi(raw_id)] = record.get("title", "")
        pair_results.append({
            "pair_id": declared["pair_id"],
            "partition": partition,
            "route": literal_event["route"],
            "literal": {
                "artifact": rel(literal_path, pilot_root),
                "source_total": literal_data["total"],
                "raw_source_ids": sorted(literal_raw_set),
                "canonical_dois": sorted(literal_set),
                "screenshots": [rel(value, pilot_root) for value in screenshot_paths(literal_path)],
            },
            "wildcard": {
                "artifact": rel(wildcard_path, pilot_root),
                "source_total": wildcard_data["total"],
                "raw_source_ids": sorted(wildcard_raw_set),
                "canonical_dois": sorted(wildcard_set),
                "screenshots": [rel(value, pilot_root) for value in screenshot_paths(wildcard_path)],
            },
            "comparison": {
                "source_totals_equal": literal_data["total"] == wildcard_data["total"],
                "raw_source_id_sets_equal": literal_raw_set == wildcard_raw_set,
                "canonical_doi_sets_equal": literal_set == wildcard_set,
                "literal_raw_subset_of_wildcard": literal_raw_set <= wildcard_raw_set,
                "literal_canonical_subset_of_wildcard": literal_set <= wildcard_set,
                "wildcard_only_raw_source_ids": sorted(wildcard_raw_set - literal_raw_set),
                "wildcard_only_canonical_dois": sorted(wildcard_set - literal_set),
                "literal_only_raw_source_ids": sorted(literal_raw_set - wildcard_raw_set),
                "literal_only_canonical_dois": sorted(literal_set - wildcard_set),
            },
        })

    if not all(pair["comparison"]["literal_canonical_subset_of_wildcard"] for pair in pair_results):
        raise RuntimeError("At least one wildcard cell lost a literal canonical DOI")
    partition_results = {}
    for partition in PARTITIONS:
        literal_set = partition_literal[partition]
        wildcard_set = partition_wildcard[partition]
        partition_results[partition] = {
            "pair_count": plan["partition_pair_counts"][partition],
            "literal_canonical_doi_count": len(literal_set),
            "wildcard_canonical_doi_count": len(wildcard_set),
            "literal_canonical_dois": sorted(literal_set),
            "wildcard_canonical_dois": sorted(wildcard_set),
            "literal_subset_of_wildcard": literal_set <= wildcard_set,
            "sets_equal": literal_set == wildcard_set,
            "wildcard_only_canonical_dois": sorted(wildcard_set - literal_set),
            "literal_only_canonical_dois": sorted(literal_set - wildcard_set),
        }

    pilot007 = load(pilot007_root / "searches" / "assessment.json")
    pilot007_union = set(pilot007["overall_union"]["canonical_dois"])
    if overall_literal != pilot007_union:
        raise RuntimeError("Fresh literal schedule does not reproduce the Pilot 007 union")
    if not overall_literal <= overall_wildcard:
        raise RuntimeError("Wildcard schedule lost a literal schedule DOI")

    known_item = {}
    for partition in KNOWN_APPLICABLE:
        known_item[partition] = {
            "literal": KNOWN_DOI in partition_literal[partition],
            "wildcard": KNOWN_DOI in partition_wildcard[partition],
        }
    visible_controls = []
    for doi, expected_title in VISIBLE_NANOSATELLITE_TITLES.items():
        literal_title = literal_record_titles.get(doi)
        wildcard_title = wildcard_record_titles.get(doi)
        if literal_title != expected_title or wildcard_title != expected_title:
            raise RuntimeError(f"Visible nanosatellite control {doi} did not reconcile")
        literal_pairs = sorted(
            pair["pair_id"]
            for pair in pair_results
            if doi in pair["literal"]["canonical_dois"]
        )
        wildcard_pairs = sorted(
            pair["pair_id"]
            for pair in pair_results
            if doi in pair["wildcard"]["canonical_dois"]
        )
        visible_controls.append({
            "doi": doi,
            "title": expected_title,
            "title_visibly_contains": "Nanosatellite",
            "literal_pair_memberships": literal_pairs,
            "wildcard_pair_memberships": wildcard_pairs,
            "pair_memberships_equal": literal_pairs == wildcard_pairs,
        })

    failure_paths = sorted(pilot_root.rglob("*NON_MERGEABLE_FAILURE.json"))
    expected_failures = {
        "searches/cells/B2-hybrid-P-abstract-MB-keywords-R-anywhere-wildcard.NON_MERGEABLE_FAILURE.json",
        "searches/cells/BG2-product-context-metadata-P-abstract-Gproduct-abstract-MB-title-literal.NON_MERGEABLE_FAILURE.json",
        "searches/cells/BG2-product-context-metadata-P-abstract-Gproduct-keywords-MB-title-literal.NON_MERGEABLE_FAILURE.json",
        "searches/cells/BT2-hybrid-P-title-MB-keywords-Tprecise-anywhere-wildcard.NON_MERGEABLE_FAILURE.json",
    }
    if {rel(path, pilot_root) for path in failure_paths} != expected_failures:
        raise RuntimeError("Unexpected Pilot 009 failure ledger")
    all_pngs = set(pilot_root.rglob("*.png"))
    source_totals_equal = all(pair["comparison"]["source_totals_equal"] for pair in pair_results)
    raw_sets_equal = all(pair["comparison"]["raw_source_id_sets_equal"] for pair in pair_results)
    canonical_sets_equal = all(pair["comparison"]["canonical_doi_sets_equal"] for pair in pair_results)
    all_partitions_equal = all(entry["sets_equal"] for entry in partition_results.values())
    overall_equal = overall_literal == overall_wildcard
    all_checks_passed = all((
        source_totals_equal,
        raw_sets_equal,
        canonical_sets_equal,
        all_partitions_equal,
        overall_equal,
        all(value[variant] for value in known_item.values() for variant in ("literal", "wildcard")),
        len(success_screenshots) == 376,
    ))
    if not all_checks_passed:
        raise RuntimeError("Pilot 009 wildcard acceptance checks did not all pass")

    return {
        "schema_version": "aiaa-arc-pilot009-wildcard-assessment/v1",
        "source": plan["source"],
        "pilot": "009",
        "protocol_commit": plan["protocol_commit"],
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "candidate": plan["candidate"],
        "execution": {
            "pair_count": len(pair_results),
            "source_event_count": len(plan["events"]),
            "all_events_complete": True,
            "all_events_at_most_100": True,
            "largest_source_total": max(
                max(pair["literal"]["source_total"], pair["wildcard"]["source_total"])
                for pair in pair_results
            ),
            "all_94_source_totals_equal": source_totals_equal,
            "all_94_raw_source_id_sets_equal": raw_sets_equal,
            "all_94_canonical_doi_sets_equal": canonical_sets_equal,
        },
        "partition_unions": partition_results,
        "overall_comparison": {
            "literal_canonical_doi_count": len(overall_literal),
            "wildcard_canonical_doi_count": len(overall_wildcard),
            "literal_canonical_dois": sorted(overall_literal),
            "wildcard_canonical_dois": sorted(overall_wildcard),
            "literal_subset_of_wildcard": overall_literal <= overall_wildcard,
            "sets_equal": overall_equal,
            "wildcard_only_canonical_dois": sorted(overall_wildcard - overall_literal),
            "literal_only_canonical_dois": sorted(overall_literal - overall_wildcard),
            "fresh_literal_reproduces_pilot007_union": overall_literal == pilot007_union,
        },
        "known_item_recall": {
            "doi": KNOWN_DOI,
            "applicable_partitions": list(KNOWN_APPLICABLE),
            "retrieved": known_item,
            "all_literal_and_wildcard_memberships_pass": all(
                value[variant]
                for value in known_item.values()
                for variant in ("literal", "wildcard")
            ),
        },
        "visible_nanosatellite_controls": visible_controls,
        "acceptance": {
            "status": "accepted",
            "accepted_wildcard": plan["candidate"]["wildcard_fragment"],
            "accepted_replacement": (
                f"{plan['candidate']['literal_fragment']} -> {plan['candidate']['wildcard_fragment']}"
            ),
            "scope": plan["candidate"]["replacement_scope"],
            "basis": (
                "All 94 paired cells had equal source totals, raw stable-ID sets, and canonical DOI sets. "
                "Every partition union and the 119-DOI schedule union were equal."
            ),
            "wildcard_only_records_to_add": 0,
            "general_wildcard_permission": False,
            "other_wildcard_stems_or_positions": "unaccepted",
            "final_search": "not_executed",
        },
        "screenshots": {
            "successful_json_count": len(plan["events"]),
            "required_screenshot_count": len(plan["events"]) * 2,
            "verified_success_screenshot_count": len(success_screenshots),
            "all_png_count_including_failed_attempts": len(all_pngs),
            "failed_attempt_png_count": len(all_pngs - success_screenshots),
            "ignored_by_project_git": True,
            "no_opt_out": True,
        },
        "adapter_provenance": [
            {"adapter_version": version, "script_sha256": script_hash, "event_count": count}
            for (version, script_hash), count in sorted(adapter_counts.items())
        ],
        "retained_failures": {
            "count": len(failure_paths),
            "artifacts": sorted(expected_failures),
            "classification": "transient_owned_page_creation_failure",
            "all_recovered_by_exact_retry": True,
            "converted_to_zero": False,
        },
        "limits": [
            "Acceptance applies only to the exact unquoted trailing wildcard nanosatellit* in place of the two declared unhyphenated literals.",
            "The pilot grants no general permission for other stems, positions, quoted wildcards, or removal of punctuation variants.",
            "The paired evidence is a dated source snapshot and requires revalidation during final execution.",
            "Rendered-card previews cannot enter the final corpus.",
        ],
        "pair_ledger": pair_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot007-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root, args.pilot007_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
