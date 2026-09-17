#!/usr/bin/env python3
"""Combine accepted Scopus Pilot 006, 008, and 009 wildcard evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "scopus-main-schedule-wildcard-combined-assessment/v1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
P006_IDS = ("A1", "A2", "A3")
P008_IDS = ("B2", "BG1", "BG2", "BC1", "BT2")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def screenshot_pair_ok(path: Path, value: dict[str, Any]) -> bool:
    screenshots = value.get("output_metadata", {}).get("screenshots", {})
    if (
        screenshots.get("schema_version") != "scopus-automatic-screenshots/v1"
        or screenshots.get("automatic") is not True
        or screenshots.get("same_directory_as_json") is not True
    ):
        return False
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        image = path.with_name(f"{path.stem}{suffix}")
        evidence = screenshots.get(key, {})
        if (
            not image.is_file()
            or evidence.get("path") != image.name
            or evidence.get("sha256") != digest_file(image)
            or not isinstance(evidence.get("width"), int)
            or evidence["width"] <= 0
            or not isinstance(evidence.get("height"), int)
            or evidence["height"] <= 0
        ):
            return False
    return True


def strict_comparison(root: Path, partition: str) -> dict[str, Any]:
    variants = {}
    for variant in ("literal", "wildcard"):
        path = root / "searches" / variant / f"{partition}.json"
        value = load(path)
        metadata = value.get("output_metadata", {})
        receipt = metadata.get("strict_two_pass_receipt", {})
        records = value.get("results", [])
        ids = [record.get("paperId") for record in records if isinstance(record, dict)]
        valid = bool(
            value.get("schema_version") == "academic-search-result/v1"
            and isinstance(value.get("total"), int)
            and value["total"] == len(records) == len(ids) == len(set(ids))
            and metadata.get("status") == "success"
            and metadata.get("retrieval_complete") is True
            and receipt.get("schema_version")
            == "academic-search-scopus-strict-two-pass/v1"
            and receipt.get("strict_completion") is True
            and receipt.get("two_pass_order_verified") is True
            and receipt.get("two_pass_total_verified") is True
            and screenshot_pair_ok(path, value)
        )
        variants[variant] = {
            "path": str(path),
            "sha256": digest_file(path),
            "total": value.get("total"),
            "ids": ids,
            "valid": valid,
        }
    literal_set = set(variants["literal"]["ids"])
    wildcard_set = set(variants["wildcard"]["ids"])
    return {
        "partition_id": partition,
        "evidence_mode": "adapter_strict_two_pass_per_query",
        "literal_total": variants["literal"]["total"],
        "wildcard_total": variants["wildcard"]["total"],
        "literal_is_subset": literal_set <= wildcard_set,
        "exact_set_equality": literal_set == wildcard_set,
        "missing_count": len(literal_set - wildcard_set),
        "wildcard_only_count": len(wildcard_set - literal_set),
        "valid": all(item["valid"] for item in variants.values()),
        "artifacts": {
            key: {name: item[name] for name in ("path", "sha256")}
            for key, item in variants.items()
        },
    }


def assessment_comparison(
    assessment: dict[str, Any], partition: str, *, set_repeat: bool
) -> dict[str, Any]:
    source = next(
        item for item in assessment["comparisons"] if item["partition_id"] == partition
    )
    if set_repeat:
        repeats = bool(
            source.get("literal_repeat_set_stable") is True
            and source.get("wildcard_repeat_set_stable") is True
        )
    else:
        repeats = bool(
            source.get("literal_repeat_stable") is True
            and source.get("wildcard_repeat_stable") is True
        )
    return {
        "partition_id": partition,
        "evidence_mode": "two_independent_complete_one_owner_events_per_query",
        "literal_total": source["literal_total"],
        "wildcard_total": source["wildcard_total"],
        "literal_is_subset": source["literal_is_subset"],
        "exact_set_equality": source["exact_set_equality"],
        "missing_count": len(source["missing_from_wildcard"]),
        "wildcard_only_count": len(source["wildcard_only"]),
        "valid": repeats and source["exact_set_equality"] is True,
        "source_order_repeat_stable": {
            "literal": source.get(
                "literal_repeat_order_stable", source.get("literal_repeat_stable")
            ),
            "wildcard": source.get(
                "wildcard_repeat_order_stable", source.get("wildcard_repeat_stable")
            ),
        },
        "artifacts": source["artifacts"],
    }


def plan_artifact_paths(root: Path, selected: set[str]) -> list[Path]:
    plan = load(root / "searches" / "event-plan.json")
    return [
        root / "searches" / event["output"]
        for event in plan["events"]
        if event["partition_id"] in selected
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--pilot008-root", type=Path, required=True)
    parser.add_argument("--pilot009-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    p008_assessment_path = args.pilot008_root / "searches" / "assessment.json"
    p009_assessment_path = args.pilot009_root / "searches" / "assessment.json"
    p008 = load(p008_assessment_path)
    p009 = load(p009_assessment_path)
    comparisons = [
        *(strict_comparison(args.pilot006_root, partition) for partition in P006_IDS),
        assessment_comparison(p009, "B1", set_repeat=True),
        *(
            assessment_comparison(p008, partition, set_repeat=False)
            for partition in P008_IDS
        ),
    ]
    comparisons.sort(key=lambda item: SCHEDULE_IDS.index(item["partition_id"]))

    evidence_paths = [
        *plan_artifact_paths(args.pilot006_root, set(P006_IDS)),
        *plan_artifact_paths(args.pilot008_root, set(P008_IDS)),
        *plan_artifact_paths(args.pilot009_root, {"B1"}),
    ]
    screenshot_errors = []
    for path in evidence_paths:
        value = load(path)
        if not screenshot_pair_ok(path, value):
            screenshot_errors.append(str(path))
    valid = bool(
        len(comparisons) == len(SCHEDULE_IDS)
        and all(item["valid"] for item in comparisons)
        and all(item["exact_set_equality"] for item in comparisons)
        and not screenshot_errors
    )
    output = {
        "schema_version": SCHEMA,
        "source": "Scopus",
        "protocol_commit": "3194156e90497186664260a8e86435e78d2e2aa1",
        "diagnostic_only": True,
        "do_not_merge": True,
        "evidence_pilots": ["006", "008", "009"],
        "schedule": {
            "all_nine_current_main_partitions_completed": valid,
            "changed_partitions": ["BG1", "BG2", "BC1", "BT2"],
            "proximity_operators_used": False,
            "pair_expansions_used": False,
        },
        "wildcard": {
            "candidate_count": 10,
            "replaced_population_literal_count": 22,
            "character_reduction_per_partition": 375,
            "all_nine_literal_sets_are_subsets": valid,
            "all_nine_literal_and_wildcard_sets_are_equal": valid,
            "missing_record_count": sum(
                item["missing_count"] for item in comparisons
            ),
            "wildcard_only_record_count": sum(
                item["wildcard_only_count"] for item in comparisons
            ),
            "preferred_when_safe": True,
            "safe_for_all_nine_main_partitions": valid,
            "decision": (
                "adopt_ten_population_wildcards_for_all_main_partitions"
                if valid
                else "retain_literal_population_translation"
            ),
        },
        "screenshots": {
            "successful_evidence_event_count": len(evidence_paths),
            "required_screenshot_file_count": len(evidence_paths) * 2,
            "verified_screenshot_file_count": (
                len(evidence_paths) * 2 if not screenshot_errors else None
            ),
            "errors": screenshot_errors,
        },
        "source_limitations": [
            "B1 Date-oldest tie order changed between complete literal runs. Stable-ID sets were equal. This diagnostic does not establish final-search readiness for B1.",
            "Pilot 006 and Pilot 007 strict B1 events failed during result reconciliation. Pilot 008 and Pilot 009 used two predeclared complete one-owner events per query.",
            "The wildcard decision applies to the nine main partitions. No PSR wildcard translation is adopted without a separate comparison.",
        ],
        "comparisons": comparisons,
        "assessment_inputs": {
            "pilot008": {
                "path": str(p008_assessment_path),
                "sha256": digest_file(p008_assessment_path),
            },
            "pilot009": {
                "path": str(p009_assessment_path),
                "sha256": digest_file(p009_assessment_path),
            },
        },
        "status": "passed" if valid else "failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": output["status"],
                "partitions": len(comparisons),
                "screenshots": output["screenshots"][
                    "verified_screenshot_file_count"
                ],
                "decision": output["wildcard"]["decision"],
            }
        )
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
