#!/usr/bin/env python3
"""Build the complete AIAA ARC Pilot 008 Topic yield assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_corpus_plan import build as build_corpus_plan
from build_projected_corpus_plan import build as build_projected_plan
from build_title_corpus_plan import build as build_title_plan
from run_plan import screenshot_paths, validate_success

KNOWN_DOI = "10.2514/6.2015-4474"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def canonical_doi(value: str) -> str:
    return value.strip().casefold().split("@", 1)[0]


def source_ids(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    raw = []
    canonical = []
    for record in data.get("results", []):
        value = record.get("sourceRecordStableId") or record.get("doi")
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError("Source result lacks a stable DOI")
        raw.append(value.casefold())
        canonical.append(canonical_doi(value))
    if len(raw) != len(set(raw)):
        raise RuntimeError("Source artifact contains duplicate raw stable IDs")
    return raw, canonical


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


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_plan(
    pilot_root: Path,
    plan: dict[str, Any],
) -> tuple[list[dict[str, Any]], set[Path], Counter[tuple[str, str]]]:
    ledger = []
    screenshots: set[Path] = set()
    adapters: Counter[tuple[str, str]] = Counter()
    for event in plan["events"]:
        path, data = artifact_for(pilot_root / event["output"])
        errors = validate_success(path, event)
        if errors:
            raise RuntimeError(f"{path}: {'; '.join(errors)}")
        raw, canonical = source_ids(data)
        metadata = data["output_metadata"]["prisma_search_run"]
        adapter = metadata["adapter"]
        adapters[(str(adapter.get("adapter_version")), str(adapter.get("script_sha256")))] += 1
        event_screenshots = screenshot_paths(path)
        for screenshot in event_screenshots:
            if not screenshot.is_file():
                raise RuntimeError(f"Missing successful-event screenshot {screenshot}")
            screenshots.add(screenshot)
        ledger.append({
            "event_id": event["event_id"],
            "phase": event["phase"],
            "chunk_id": event.get("chunk_id"),
            "artifact": rel(path, pilot_root),
            "source_total": data["total"],
            "raw_source_ids": raw,
            "canonical_dois": canonical,
            "canonical_doi_count": len(set(canonical)),
            "topic_selection": event.get("topic_selection"),
            "screenshots": [rel(value, pilot_root) for value in event_screenshots],
        })
    return ledger, screenshots, adapters


def baseline_specificity(plan: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    events = {event["event_id"]: event for event in plan["events"]}
    entries = []
    outside_union = set()
    for result in ledger:
        if result["topic_selection"] is not None:
            continue
        event = events[result["event_id"]]
        expected = set(event["expected_canonical_dois"])
        observed = set(result["canonical_dois"])
        missing = expected - observed
        outside = observed - expected
        if missing:
            raise RuntimeError(f"{result['event_id']}: baseline missed expected corpus DOIs")
        outside_union.update(outside)
        entries.append({
            "event_id": result["event_id"],
            "artifact": result["artifact"],
            "source_total": result["source_total"],
            "expected_canonical_doi_count": len(expected),
            "observed_canonical_doi_count": len(observed),
            "missing_expected_count": 0,
            "outside_allowlist_count": len(outside),
            "outside_allowlist_canonical_dois": sorted(outside),
        })
    return {
        "baseline_count": len(entries),
        "all_expected_dois_retrieved": True,
        "outside_allowlist_event_sum": sum(entry["outside_allowlist_count"] for entry in entries),
        "outside_allowlist_union_count": len(outside_union),
        "outside_allowlist_union": sorted(outside_union),
        "ledger": entries,
    }


def projected_yield(
    plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    pilot007_assessment: dict[str, Any],
) -> dict[str, Any]:
    events = {event["event_id"]: event for event in plan["events"]}
    by_event = {entry["event_id"]: entry for entry in ledger}
    topic_definitions = plan["topic_selections"]
    topic_keys = [entry["concept_id"] for entry in topic_definitions]
    topic_labels = {entry["concept_id"]: entry["label"] for entry in topic_definitions}
    baseline_union = set()
    topic_unions: dict[str, set[str]] = {key: set() for key in topic_keys}
    outside_source_matches: dict[str, set[str]] = defaultdict(set)
    chunk_ledger = []

    baseline_events = [event for event in plan["events"] if event.get("topic_selection") is None]
    for baseline_event in baseline_events:
        chunk = baseline_event["chunk_id"]
        allowlist = set(baseline_event["expected_canonical_dois"])
        baseline_result = by_event[baseline_event["event_id"]]
        baseline_observed = set(baseline_result["canonical_dois"])
        missing = allowlist - baseline_observed
        if missing:
            raise RuntimeError(f"{chunk}: projected baseline missed {sorted(missing)}")
        baseline_projected = baseline_observed & allowlist
        if baseline_projected != allowlist:
            raise RuntimeError(f"{chunk}: projected baseline did not equal its allowlist")
        baseline_union.update(baseline_projected)
        topic_entries = {}
        for topic in topic_definitions:
            suffix = "-".join(topic["label"].casefold().split())
            event_id = f"{chunk}-topic-{suffix}"
            event = events[event_id]
            result = by_event[event_id]
            observed = set(result["canonical_dois"])
            projected = observed & allowlist
            outside = observed - allowlist
            if not projected <= baseline_projected:
                raise RuntimeError(f"{event_id}: projected Topic set is not a baseline subset")
            concept_id = topic["concept_id"]
            if event["topic_selection"] != topic:
                raise RuntimeError(f"{event_id}: Topic selection changed")
            topic_unions[concept_id].update(projected)
            outside_source_matches[concept_id].update(outside)
            topic_entries[concept_id] = {
                "label": topic["label"],
                "artifact": result["artifact"],
                "source_total": result["source_total"],
                "projected_canonical_doi_count": len(projected),
                "projected_canonical_dois": sorted(projected),
                "outside_allowlist_count": len(outside),
                "outside_allowlist_canonical_dois": sorted(outside),
            }
        chunk_ledger.append({
            "chunk_id": chunk,
            "allowlist_count": len(allowlist),
            "baseline_artifact": baseline_result["artifact"],
            "baseline_source_total": baseline_result["source_total"],
            "baseline_projected_count": len(baseline_projected),
            "baseline_outside_allowlist_count": len(baseline_observed - allowlist),
            "baseline_outside_allowlist_canonical_dois": sorted(baseline_observed - allowlist),
            "topics": topic_entries,
        })

    accepted = set(plan["accepted_corpus"]["canonical_dois"])
    if baseline_union != accepted or len(baseline_union) != 119:
        raise RuntimeError("Projected baseline union did not reproduce the accepted 119-DOI corpus")
    topic_results = {}
    for concept_id in topic_keys:
        retained = topic_unions[concept_id]
        removed = accepted - retained
        topic_results[concept_id] = {
            "label": topic_labels[concept_id],
            "concept_id": concept_id,
            "retained_canonical_doi_count": len(retained),
            "removed_canonical_doi_count": len(removed),
            "retention_percent": round(100 * len(retained) / len(accepted), 2),
            "reduction_percent": round(100 * len(removed) / len(accepted), 2),
            "retained_canonical_dois": sorted(retained),
            "removed_canonical_dois": sorted(removed),
            "known_eligible_sentinel_retrieved": KNOWN_DOI in retained,
            "outside_allowlist_source_match_count": len(outside_source_matches[concept_id]),
            "outside_allowlist_source_matches": sorted(outside_source_matches[concept_id]),
        }
    at_least_one = set().union(*(topic_unions[key] for key in topic_keys))
    all_four = set.intersection(*(topic_unions[key] for key in topic_keys))
    removed_by_union = accepted - at_least_one

    provenance = pilot007_assessment["overall_union"]["partition_provenance"]
    partition_yield = {}
    for partition in PARTITIONS:
        partition_ids = {doi for doi in accepted if partition in provenance[doi]}
        retained_partition = partition_ids & at_least_one
        partition_yield[partition] = {
            "accepted_corpus_doi_count": len(partition_ids),
            "at_least_one_topic_retained_count": len(retained_partition),
            "at_least_one_topic_removed_count": len(partition_ids - retained_partition),
            "at_least_one_topic_retention_percent": round(
                100 * len(retained_partition) / len(partition_ids), 2
            ) if partition_ids else None,
            "per_topic_retained_count": {
                concept_id: len(partition_ids & topic_unions[concept_id])
                for concept_id in topic_keys
            },
        }

    subset_relations = []
    for left in topic_keys:
        for right in topic_keys:
            if left == right:
                continue
            if topic_unions[left] < topic_unions[right]:
                subset_relations.append({
                    "subset_concept_id": left,
                    "subset_label": topic_labels[left],
                    "superset_concept_id": right,
                    "superset_label": topic_labels[right],
                    "strict": True,
                })
    return {
        "denominator": {
            "accepted_canonical_doi_count": len(accepted),
            "projected_baseline_canonical_doi_count": len(baseline_union),
            "all_accepted_dois_retrieved": True,
        },
        "per_topic": topic_results,
        "at_least_one_promoted_topic_union": {
            "retained_canonical_doi_count": len(at_least_one),
            "removed_canonical_doi_count": len(removed_by_union),
            "retention_percent": round(100 * len(at_least_one) / len(accepted), 2),
            "reduction_percent": round(100 * len(removed_by_union) / len(accepted), 2),
            "retained_canonical_dois": sorted(at_least_one),
            "removed_canonical_dois": sorted(removed_by_union),
            "known_eligible_sentinel_retrieved": KNOWN_DOI in at_least_one,
        },
        "all_four_topic_intersection": {
            "canonical_doi_count": len(all_four),
            "canonical_dois": sorted(all_four),
        },
        "strict_subset_relations": subset_relations,
        "partition_yield": partition_yield,
        "chunk_ledger": chunk_ledger,
    }


def build(
    pilot_root: Path,
    pilot007_root: Path,
    discovery_assessment_path: Path,
    doi_plan_path: Path,
    title_plan_path: Path,
    projected_plan_path: Path,
) -> dict[str, Any]:
    discovery = load(discovery_assessment_path)
    if discovery.get("status") != "complete":
        raise RuntimeError("Pilot 008 discovery assessment is incomplete")
    pilot007_assessment_path = pilot007_root / "searches" / "assessment.json"
    pilot007 = load(pilot007_assessment_path)

    doi_plan = load(doi_plan_path)
    if doi_plan != build_corpus_plan(discovery_assessment_path, pilot007_assessment_path):
        raise RuntimeError("Pilot 008 DOI corpus plan does not rebuild")
    title_plan = load(title_plan_path)
    if title_plan != build_title_plan(pilot_root, doi_plan_path, pilot007_root):
        raise RuntimeError("Pilot 008 title corpus plan does not rebuild")
    projected_plan = load(projected_plan_path)
    if projected_plan != build_projected_plan(pilot_root, title_plan_path):
        raise RuntimeError("Pilot 008 projected corpus plan does not rebuild")

    all_screenshots: set[Path] = set()
    all_adapters: Counter[tuple[str, str]] = Counter()
    plan_executions = {}
    ledgers = {}
    for name, plan in (
        ("doi_anywhere_anchor", doi_plan),
        ("title_phrase_anchor", title_plan),
        ("predeclared_projected_anchor", projected_plan),
    ):
        ledger, screenshots, adapters = validate_plan(pilot_root, plan)
        ledgers[name] = ledger
        all_screenshots.update(screenshots)
        all_adapters.update(adapters)
        specificity = baseline_specificity(plan, ledger)
        plan_executions[name] = {
            "plan": rel(
                {
                    "doi_anywhere_anchor": doi_plan_path,
                    "title_phrase_anchor": title_plan_path,
                    "predeclared_projected_anchor": projected_plan_path,
                }[name],
                pilot_root,
            ),
            "event_count": len(plan["events"]),
            "all_events_complete": True,
            "largest_source_total": max(entry["source_total"] for entry in ledger),
            "baseline_specificity": specificity,
        }

    projected = projected_yield(projected_plan, ledgers["predeclared_projected_anchor"], pilot007)
    discovery_screenshots = {
        pilot_root / path
        for path in discovery["screenshots"]["digests"]
    }
    for path in discovery_screenshots:
        if not path.is_file() or sha256(path) != discovery["screenshots"]["digests"][rel(path, pilot_root)]:
            raise RuntimeError(f"Discovery screenshot evidence mismatch for {path}")
    all_screenshots.update(discovery_screenshots)
    discovery_artifacts = {
        entry["artifact"] for entry in discovery["baselines"].values()
    }
    for candidate in discovery["candidates"]:
        if candidate["status"] != "resolved_and_executed":
            continue
        discovery_artifacts.add(candidate["sentinel"]["artifact"])
        discovery_artifacts.add(candidate["bg1"]["artifact"])
    if len(discovery_artifacts) != discovery["screenshots"]["successful_json_count"]:
        raise RuntimeError("Discovery successful-artifact count does not reconcile")
    for artifact in discovery_artifacts:
        data = load(pilot_root / artifact)
        adapter = data["output_metadata"]["prisma_search_run"]["adapter"]
        all_adapters[(str(adapter.get("adapter_version")), str(adapter.get("script_sha256")))] += 1

    failure_paths = sorted(pilot_root.rglob("*NON_MERGEABLE_FAILURE.json"))
    expected_unavailable = {
        "searches/discovery/sentinel-topic-cubesats.NON_MERGEABLE_FAILURE.json",
        "searches/discovery/sentinel-topic-nanosatellites.NON_MERGEABLE_FAILURE.json",
        "searches/discovery/bg1-topic-cubesats.NON_MERGEABLE_FAILURE.json",
        "searches/discovery/bg1-topic-nanosatellites.NON_MERGEABLE_FAILURE.json",
    }
    transient = {
        "searches/corpus/corpus-01-topic-systems-engineering.NON_MERGEABLE_FAILURE.json",
        "searches/corpus-title/corpus-04-topic-satellites.NON_MERGEABLE_FAILURE.json",
        "searches/corpus-projected/corpus-06-topic-satellites.NON_MERGEABLE_FAILURE.json",
    }
    observed_failures = {rel(path, pilot_root) for path in failure_paths}
    if observed_failures != expected_unavailable | transient:
        raise RuntimeError("Unexpected Pilot 008 failure ledger")

    discovery_success_count = discovery["screenshots"]["successful_json_count"]
    successful_json_count = discovery_success_count + sum(
        execution["event_count"] for execution in plan_executions.values()
    )
    if len(all_screenshots) != successful_json_count * 2:
        raise RuntimeError("Successful screenshot count does not reconcile")
    all_pngs = set(pilot_root.rglob("*.png"))

    topic_union = projected["at_least_one_promoted_topic_union"]
    return {
        "schema_version": "aiaa-arc-pilot008-topic-yield-assessment/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "008",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Exercise exact ARC Topic selections and quantify their yield effect on a complete "
            "partition, a known eligible sentinel, and the accepted 119-DOI screening corpus."
        ),
        "discovery": {
            "assessment": rel(discovery_assessment_path, pilot_root),
            "assessment_sha256": sha256(discovery_assessment_path),
            "summary": discovery["summary"],
            "identifier_groups": discovery["identifier_groups"],
            "promoted_distinct_selections": discovery["extension_trigger"]["promoted_distinct_selections"],
        },
        "execution": {
            "successful_source_json_count": successful_json_count,
            "corpus_plan_executions": plan_executions,
            "all_successful_source_events_complete": True,
            "all_successful_source_events_at_most_100": True,
        },
        "accepted_corpus_yield": projected,
        "main_findings": {
            "single_broadest_tested_topic": {
                "label": "Space Systems and Vehicles",
                "concept_id": "135236",
                "retained": projected["per_topic"]["135236"]["retained_canonical_doi_count"],
                "of": 119,
                "retention_percent": projected["per_topic"]["135236"]["retention_percent"],
                "removed": projected["per_topic"]["135236"]["removed_canonical_doi_count"],
            },
            "least_restrictive_tested_topic_union": {
                "labels": [entry["label"] for entry in projected_plan["topic_selections"]],
                "retained": topic_union["retained_canonical_doi_count"],
                "of": 119,
                "retention_percent": topic_union["retention_percent"],
                "removed": topic_union["removed_canonical_doi_count"],
                "reduction_percent": topic_union["reduction_percent"],
            },
            "known_eligible_sentinel": {
                "doi": KNOWN_DOI,
                "retrieved_by_all_four_promoted_topic_identities": all(
                    value["known_eligible_sentinel_retrieved"]
                    for value in projected["per_topic"].values()
                ),
            },
            "bg1_discovery": {
                "baseline_canonical_dois": discovery["summary"]["bg1_baseline_canonical_dois"],
                "sentinel_retaining_topic_union_retained": discovery["summary"]["sentinel_retaining_topic_union_canonical_dois"],
                "sentinel_retaining_topic_union_removed": discovery["summary"]["sentinel_retaining_topic_union_removed"],
                "retention_percent": discovery["summary"]["sentinel_retaining_topic_union_retention_percent"],
            },
        },
        "decision": {
            "topic_as_required_and_filter": "reject",
            "topic_as_canonical_route_supplement": "not_established_do_not_add",
            "reason": (
                f"The least restrictive offline union of all four sentinel-retaining Topic identities "
                f"retained {topic_union['retained_canonical_doi_count']} of 119 accepted corpus DOIs and "
                f"removed {topic_union['removed_canonical_doi_count']} records with unclassified eligibility."
            ),
            "source_translation": "keep_pilot007_hybrid_route_without_topic",
            "topic_evidence_use": "retain_as_nonexcluding_sensitivity_evidence_only",
            "final_search": "not_executed",
        },
        "screenshots": {
            "successful_json_count": successful_json_count,
            "required_screenshot_count": successful_json_count * 2,
            "verified_success_screenshot_count": len(all_screenshots),
            "all_png_count_including_failed_attempts": len(all_pngs),
            "failed_attempt_png_count": len(all_pngs - all_screenshots),
            "ignored_by_project_git": True,
            "no_opt_out": True,
        },
        "adapter_provenance": [
            {"adapter_version": version, "script_sha256": script_hash, "event_count": count}
            for (version, script_hash), count in sorted(all_adapters.items())
        ],
        "retained_failures": {
            "count": len(failure_paths),
            "exact_label_not_offered_count": len(expected_unavailable),
            "exact_label_not_offered_artifacts": sorted(expected_unavailable),
            "transient_source_or_control_failure_count": len(transient),
            "transient_source_or_control_failure_artifacts": sorted(transient),
            "all_transient_failures_recovered": True,
            "converted_to_zero": False,
        },
        "limits": [
            "ARC exposes no Topic vocabulary version, hierarchy, scope note, preferred-term flag, or explosion semantics.",
            "Shared ConceptIDs between labels show source identity collisions. They do not establish synonym or preferred-term relations.",
            "Topic assignments were measured within the accepted 119-DOI pilot corpus. They do not classify the 42 excluded-by-union records as ineligible.",
            "The DOI and title anchor diagnostics admitted outside records. The final paired source calls used a canonical-DOI projection declared before execution and retained every outside source match in the audit ledger.",
            "Pilot cards cannot enter the final corpus.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot007-root", type=Path, required=True)
    parser.add_argument("--discovery-assessment", type=Path, required=True)
    parser.add_argument("--doi-plan", type=Path, required=True)
    parser.add_argument("--title-plan", type=Path, required=True)
    parser.add_argument("--projected-plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(
        args.pilot_root,
        args.pilot007_root,
        args.discovery_assessment,
        args.doi_plan,
        args.title_plan,
        args.projected_plan,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
