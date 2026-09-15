#!/usr/bin/env python3
"""Validate AIAA ARC Pilot 008 plans, artifacts, assessment, and prose."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_assessment import build


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate(args: argparse.Namespace) -> dict[str, Any]:
    observed = load(args.assessment)
    rebuilt = build(
        args.pilot_root,
        args.pilot007_root,
        args.discovery_assessment,
        args.doi_plan,
        args.title_plan,
        args.projected_plan,
    )
    require(observed == rebuilt, "Assessment does not rebuild exactly")
    require(observed["status"] == "complete", "Pilot status is incomplete")
    require(observed["execution"]["successful_source_json_count"] == 106, "Unexpected successful source count")
    require(observed["screenshots"]["verified_success_screenshot_count"] == 212, "Screenshot count mismatch")
    require(observed["screenshots"]["required_screenshot_count"] == 212, "Required screenshot count mismatch")
    require(sum(entry["event_count"] for entry in observed["adapter_provenance"]) == 106, "Adapter provenance count mismatch")
    require(observed["retained_failures"]["count"] == 7, "Failure ledger count mismatch")
    require(observed["retained_failures"]["all_transient_failures_recovered"] is True, "Transient failure remains unresolved")
    require(observed["retained_failures"]["converted_to_zero"] is False, "A failure was converted to zero")

    expected_yields = {
        "135111": ("Satellites", 55, 64),
        "134410": ("Spacecrafts", 64, 55),
        "135236": ("Space Systems and Vehicles", 73, 46),
        "138491": ("Systems Engineering", 16, 103),
    }
    per_topic = observed["accepted_corpus_yield"]["per_topic"]
    require(set(per_topic) == set(expected_yields), "Topic identity set mismatch")
    for concept_id, (label, retained, removed) in expected_yields.items():
        value = per_topic[concept_id]
        require(value["label"] == label, f"{concept_id}: label mismatch")
        require(value["retained_canonical_doi_count"] == retained, f"{concept_id}: retained count mismatch")
        require(value["removed_canonical_doi_count"] == removed, f"{concept_id}: removed count mismatch")
        require(value["known_eligible_sentinel_retrieved"] is True, f"{concept_id}: sentinel missing")
    union = observed["accepted_corpus_yield"]["at_least_one_promoted_topic_union"]
    require(union["retained_canonical_doi_count"] == 77, "Topic union retained count mismatch")
    require(union["removed_canonical_doi_count"] == 42, "Topic union removed count mismatch")
    require(union["retention_percent"] == 64.71, "Topic union retention percentage mismatch")
    require(observed["decision"]["topic_as_required_and_filter"] == "reject", "Topic filter decision mismatch")
    require(observed["decision"]["source_translation"] == "keep_pilot007_hybrid_route_without_topic", "Source route decision mismatch")

    pilot_text = args.pilot_document.read_text()
    guideline_text = args.guideline.read_text()
    for text, name in ((pilot_text, "pilot"), (guideline_text, "guideline")):
        require("77 of 119" in text, f"{name} omits accepted-corpus Topic union yield")
        require("removed 42" in text, f"{name} omits Topic union loss")
        require("Pilot 008" in text, f"{name} omits Pilot 008")
    require("Apply no Topic restriction" in guideline_text, "Guideline does not preserve the no-Topic decision")
    require("[Pilot 008](pilots/008/pilot.md)" in guideline_text, "Guideline does not link Pilot 008")
    require("106 successful source" in pilot_text, "Pilot prose omits successful source count")
    require("212 mandatory screenshots" in pilot_text, "Pilot prose omits screenshot count")

    return {
        "schema_version": "aiaa-arc-pilot008-validation/v1",
        "source": observed["source"],
        "pilot": "008",
        "status": "pass",
        "assessment": {
            "path": str(args.assessment),
            "sha256": sha256(args.assessment),
            "rebuild_equal": True,
        },
        "checks": {
            "successful_source_json_count": 106,
            "verified_screenshot_count": 212,
            "topic_yields": expected_yields,
            "least_restrictive_union_retained": 77,
            "least_restrictive_union_removed": 42,
            "known_eligible_sentinel_retained_by_each_promoted_topic": True,
            "topic_filter_rejected": True,
            "all_transient_failures_recovered": True,
            "no_failure_converted_to_zero": True,
            "pilot_and_guideline_updated": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot007-root", type=Path, required=True)
    parser.add_argument("--discovery-assessment", type=Path, required=True)
    parser.add_argument("--doi-plan", type=Path, required=True)
    parser.add_argument("--title-plan", type=Path, required=True)
    parser.add_argument("--projected-plan", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--pilot-document", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = validate(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
