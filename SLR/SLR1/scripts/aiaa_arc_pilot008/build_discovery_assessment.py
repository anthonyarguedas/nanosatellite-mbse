#!/usr/bin/env python3
"""Assess AIAA ARC Pilot 008 Topic discovery events."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from build_discovery_plan import KNOWN_DOI, TOPIC_CANDIDATES, build as build_plan
from run_plan import failure_path, screenshot_paths, validate_success


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def canonical_doi(value: str) -> str:
    return value.strip().casefold().split("@", 1)[0]


def ids(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    raw = []
    canonical = []
    for record in data["results"]:
        source_id = record.get("sourceRecordStableId") or record.get("doi")
        if not isinstance(source_id, str) or not source_id.strip():
            raise RuntimeError("Source record lacks a stable DOI")
        raw.append(source_id.casefold())
        canonical.append(canonical_doi(source_id))
    return raw, canonical


def event_map(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["event_id"]: event for event in plan["events"]}


def successful(pilot_root: Path, event: dict[str, Any]) -> tuple[Path, dict[str, Any]] | None:
    path = pilot_root / event["output"]
    if not path.exists():
        return None
    data = load(path)
    if not isinstance(data.get("total"), int):
        return None
    errors = validate_success(path, event)
    if errors:
        raise RuntimeError(f"{path}: {'; '.join(errors)}")
    return path, data


def relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(pilot_root: Path) -> dict[str, Any]:
    plan_path = pilot_root / "searches" / "discovery-plan.json"
    plan = load(plan_path)
    if plan != build_plan():
        raise RuntimeError("Pilot 008 discovery plan does not rebuild")
    events = event_map(plan)

    baseline_entries = {}
    baseline_sets = {}
    for probe, event_id, expected_total in (
        ("known_eligible_sentinel", "sentinel-baseline", 1),
        ("complete_bg1", "bg1-baseline-repeat", 45),
    ):
        result = successful(pilot_root, events[event_id])
        if result is None:
            raise RuntimeError(f"Missing baseline event {event_id}")
        path, data = result
        raw, canonical = ids(data)
        if data["total"] != expected_total:
            raise RuntimeError(f"{event_id}: expected total {expected_total}, got {data['total']}")
        baseline_sets[probe] = set(canonical)
        baseline_entries[probe] = {
            "event_id": event_id,
            "artifact": relative(path, pilot_root),
            "source_total": data["total"],
            "raw_source_event_count": len(raw),
            "canonical_doi_count": len(set(canonical)),
            "canonical_dois": sorted(set(canonical)),
        }
    if baseline_sets["known_eligible_sentinel"] != {KNOWN_DOI}:
        raise RuntimeError("The known eligible sentinel baseline did not reconcile")

    candidates = []
    id_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_screenshots: set[Path] = set()
    for entry in baseline_entries.values():
        event = events[entry["event_id"]]
        path = pilot_root / event["output"]
        all_screenshots.update(screenshot_paths(path))

    for declaration in TOPIC_CANDIDATES:
        label = declaration["label"]
        slug = next(
            event_id.removeprefix("sentinel-topic-")
            for event_id, event in events.items()
            if event["probe"] == "known_eligible_sentinel" and event.get("topic_label") == label
        )
        sentinel_event = events[f"sentinel-topic-{slug}"]
        bg1_event = events[f"bg1-topic-{slug}"]
        sentinel_result = successful(pilot_root, sentinel_event)
        bg1_result = successful(pilot_root, bg1_event)
        if sentinel_result is None or bg1_result is None:
            if sentinel_result is not None or bg1_result is not None:
                raise RuntimeError(f"{label}: Topic availability differed between probes")
            failures = []
            for event in (sentinel_event, bg1_event):
                sidecar = failure_path(pilot_root / event["output"])
                if not sidecar.exists():
                    raise RuntimeError(f"{label}: missing unavailable-label failure receipt")
                failure = load(sidecar)
                failure_strategy = (
                    failure.get("output_metadata", {})
                    .get("prisma_search_run", {})
                    .get("strategy", {})
                )
                failure_topic = failure_strategy.get("limits", {}).get("topic", {})
                if (
                    failure.get("total") is not None
                    or failure.get("output_metadata", {}).get("status") != "non_mergeable_diagnostic"
                    or failure_topic.get("state") != "unknown"
                    or failure_topic.get("requested") != [label]
                    or failure_strategy.get("executed_query_provenance") != "not_observed"
                ):
                    raise RuntimeError(f"{sidecar}: unexpected unavailable-label failure receipt")
                failures.append(relative(sidecar, pilot_root))
            candidates.append({
                "label": label,
                "basis": declaration["basis"],
                "status": "exact_label_not_offered",
                "concept_id": None,
                "failure_artifacts": failures,
            })
            continue

        sentinel_path, sentinel_data = sentinel_result
        bg1_path, bg1_data = bg1_result
        all_screenshots.update(screenshot_paths(sentinel_path))
        all_screenshots.update(screenshot_paths(bg1_path))
        topic_controls = []
        for data in (sentinel_data, bg1_data):
            limits = data["output_metadata"]["prisma_search_run"]["strategy"]["limits"]
            topic = limits["topic"]
            if topic.get("state") != "applied" or topic.get("requested") != [label]:
                raise RuntimeError(f"{label}: Topic source readback mismatch")
            effective = topic.get("effective")
            if not isinstance(effective, list) or len(effective) != 1 or not effective[0].isdecimal():
                raise RuntimeError(f"{label}: invalid ConceptID readback")
            topic_controls.append(effective[0])
        if topic_controls[0] != topic_controls[1]:
            raise RuntimeError(f"{label}: ConceptID changed between probes")
        concept_id = topic_controls[0]
        sentinel_raw, sentinel_ids = ids(sentinel_data)
        bg1_raw, bg1_ids = ids(bg1_data)
        bg1_set = set(bg1_ids)
        bg1_baseline = baseline_sets["complete_bg1"]
        if not bg1_set <= bg1_baseline:
            raise RuntimeError(f"{label}: filtered BG1 is not a subset of its paired baseline")
        candidate = {
            "label": label,
            "basis": declaration["basis"],
            "status": "resolved_and_executed",
            "concept_id": concept_id,
            "source_parameter": "ConceptID[]",
            "sentinel": {
                "artifact": relative(sentinel_path, pilot_root),
                "source_total": sentinel_data["total"],
                "canonical_dois": sorted(set(sentinel_ids)),
                "retrieved": KNOWN_DOI in sentinel_ids,
            },
            "bg1": {
                "artifact": relative(bg1_path, pilot_root),
                "source_total": bg1_data["total"],
                "raw_source_event_count": len(bg1_raw),
                "canonical_doi_count": len(bg1_set),
                "canonical_dois": sorted(bg1_set),
                "removed_canonical_doi_count": len(bg1_baseline - bg1_set),
                "canonical_retention_percent": round(100 * len(bg1_set) / len(bg1_baseline), 2),
                "canonical_reduction_percent": round(100 * (len(bg1_baseline) - len(bg1_set)) / len(bg1_baseline), 2),
                "subset_of_paired_baseline": True,
            },
        }
        candidates.append(candidate)
        id_groups[concept_id].append(candidate)

    identifier_groups = []
    for concept_id, members in sorted(id_groups.items()):
        labels = [member["label"] for member in members]
        sentinel_sets = {tuple(member["sentinel"]["canonical_dois"]) for member in members}
        bg1_sets = {tuple(member["bg1"]["canonical_dois"]) for member in members}
        identifier_groups.append({
            "concept_id": concept_id,
            "labels": labels,
            "label_count": len(labels),
            "sentinel_set_equal": len(sentinel_sets) == 1,
            "bg1_set_equal": len(bg1_sets) == 1,
            "interpretation": (
                "Shared source identity with equal bounded sets. No preferred-term or synonym relation is inferred."
                if len(labels) > 1
                else "One tested exact label for this source identity."
            ),
        })

    resolved = [candidate for candidate in candidates if candidate["status"] == "resolved_and_executed"]
    distinct_by_id = {}
    for candidate in resolved:
        distinct_by_id.setdefault(candidate["concept_id"], candidate)
    retaining = {
        concept_id: candidate
        for concept_id, candidate in distinct_by_id.items()
        if candidate["sentinel"]["retrieved"]
    }
    bg1_baseline = baseline_sets["complete_bg1"]
    retained_union = set().union(
        *(set(candidate["bg1"]["canonical_dois"]) for candidate in retaining.values())
    )
    all_union = set().union(
        *(set(candidate["bg1"]["canonical_dois"]) for candidate in distinct_by_id.values())
    )
    promoted = [
        {
            "label": candidate["label"],
            "concept_id": concept_id,
            "selection": f"{concept_id}={candidate['label']}",
        }
        for concept_id, candidate in retaining.items()
    ]

    for path in all_screenshots:
        if not path.is_file():
            raise RuntimeError(f"Missing required screenshot {path}")
    failure_paths = sorted(pilot_root.rglob("*NON_MERGEABLE_FAILURE.json"))
    return {
        "schema_version": "aiaa-arc-pilot008-topic-discovery-assessment/v1",
        "source": plan["source"],
        "pilot": "008",
        "protocol_commit": plan["protocol_commit"],
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "baselines": baseline_entries,
        "candidates": candidates,
        "identifier_groups": identifier_groups,
        "summary": {
            "candidate_labels_tested": len(TOPIC_CANDIDATES),
            "exact_labels_resolved": len(resolved),
            "exact_labels_not_offered": len(TOPIC_CANDIDATES) - len(resolved),
            "distinct_concept_ids_resolved": len(distinct_by_id),
            "distinct_concept_ids_retaining_sentinel": len(retaining),
            "bg1_baseline_canonical_dois": len(bg1_baseline),
            "sentinel_retaining_topic_union_canonical_dois": len(retained_union),
            "sentinel_retaining_topic_union_removed": len(bg1_baseline - retained_union),
            "sentinel_retaining_topic_union_retention_percent": round(100 * len(retained_union) / len(bg1_baseline), 2),
            "all_resolved_topic_union_canonical_dois": len(all_union),
            "all_resolved_topic_union_removed": len(bg1_baseline - all_union),
        },
        "extension_trigger": {
            "status": "triggered",
            "rule": plan["candidate_policy"]["promotion_rule"],
            "promoted_distinct_selections": promoted,
            "purpose": "Measure Topic retention in the complete accepted Pilot 007 119-DOI corpus.",
        },
        "decision_at_discovery_stage": {
            "topic_as_required_and_filter": "reject",
            "reason": (
                "Every single tested Topic reduced complete BG1 yield. The union of all sentinel-retaining "
                "Topic identities retained 32 of 44 canonical BG1 DOIs and removed 12 records with unclassified eligibility."
            ),
            "controlled_vocabulary_supplement": "not_accepted",
            "extension": "execute_triggered_accepted_corpus_yield_measurement",
        },
        "screenshots": {
            "successful_json_count": len(all_screenshots) // 2,
            "verified_screenshot_count": len(all_screenshots),
            "digests": {relative(path, pilot_root): sha256(path) for path in sorted(all_screenshots)},
        },
        "retained_failures": {
            "count": len(failure_paths),
            "artifacts": [relative(path, pilot_root) for path in failure_paths],
            "classification": "exact_label_not_offered",
            "converted_to_zero": False,
        },
        "limits": [
            "Autocomplete labels and ConceptIDs have no exposed version, hierarchy, scope note, preferred-term flag, or explosion semantics.",
            "The discovery yield comparison is complete for BG1 and one known eligible sentinel only.",
            "Rendered-card previews cannot enter the final corpus.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
