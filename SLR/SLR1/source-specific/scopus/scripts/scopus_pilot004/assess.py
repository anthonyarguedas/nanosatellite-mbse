#!/usr/bin/env python3
"""Assess complete Scopus Pilot 004 literal and wildcard stable-ID sets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "scopus-post-proximity-wildcard-pilot-assessment/v1"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CHANGED_IDS = ("BG1", "BG2", "BC1", "BT2")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_evidence(path: Path, expected_query: str) -> dict[str, Any]:
    value = load(path)
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    ids = [record.get("paperId") for record in records if isinstance(record, dict)]
    if not all(isinstance(value, str) and value for value in ids):
        raise ValueError(f"{path} has an invalid stable ID")
    screenshots = metadata.get("screenshots", {})
    image_rows = []
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        image = path.with_name(f"{path.stem}{suffix}")
        receipt = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        image_rows.append(
            {
                "kind": key,
                "path": str(image),
                "sha256": digest_file(image),
                "receipt_sha256": receipt.get("sha256"),
                "receipt_path": receipt.get("path"),
                "width": receipt.get("width"),
                "height": receipt.get("height"),
            }
        )
    errors = []
    if value.get("schema_version") != "academic-search-result/v1":
        errors.append("schema")
    if value.get("query") != expected_query:
        errors.append("query")
    if not isinstance(value.get("total"), int) or value.get("total") != len(records):
        errors.append("total")
    if len(ids) != len(set(ids)):
        errors.append("duplicate_stable_id")
    if metadata.get("status") != "success":
        errors.append("status")
    if metadata.get("strict_completion") is not True:
        errors.append("strict_completion")
    if metadata.get("retrieval_complete") is not True:
        errors.append("retrieval_complete")
    if metadata.get("passes_completed") != 2:
        errors.append("passes_completed")
    if metadata.get("two_pass_order_verified") is not True:
        errors.append("two_pass_order")
    if metadata.get("prisma_search_run", {}).get("phase") != "pilot":
        errors.append("pilot_phase")
    if screenshots.get("schema_version") != SCREENSHOT_SCHEMA:
        errors.append("screenshot_schema")
    if screenshots.get("automatic") is not True:
        errors.append("screenshot_automatic")
    if screenshots.get("same_directory_as_json") is not True:
        errors.append("screenshot_directory")
    for image in image_rows:
        if image["receipt_sha256"] != image["sha256"]:
            errors.append(f"{image['kind']}_hash")
        if image["receipt_path"] != Path(image["path"]).name:
            errors.append(f"{image['kind']}_path")
        if not isinstance(image["width"], int) or image["width"] <= 0:
            errors.append(f"{image['kind']}_width")
        if not isinstance(image["height"], int) or image["height"] <= 0:
            errors.append(f"{image['kind']}_height")
    return {
        "path": str(path),
        "sha256": digest_file(path),
        "total": value.get("total"),
        "ids": ids,
        "records": records,
        "ordered_stable_ids_sha256": metadata.get("ordered_stable_ids_sha256"),
        "screenshots": image_rows,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    plan = load(args.plan)
    events = plan.get("events", [])
    event_map = {
        (event["partition_id"], event["variant"]): event
        for event in events
        if isinstance(event, dict)
    }
    comparisons = []
    errors = []
    screenshot_paths: set[str] = set()
    for partition in SCHEDULE_IDS:
        pair: dict[str, dict[str, Any]] = {}
        for variant in ("literal", "wildcard"):
            event = event_map.get((partition, variant))
            if event is None:
                errors.append(f"missing_plan_event:{partition}:{variant}")
                continue
            path = args.pilot_root / "searches" / event["output"]
            try:
                evidence = artifact_evidence(path, event["query"])
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"artifact:{partition}:{variant}:{type(error).__name__}")
                continue
            pair[variant] = evidence
            errors.extend(
                f"artifact:{partition}:{variant}:{item}" for item in evidence["errors"]
            )
            screenshot_paths.update(
                image["path"] for image in evidence["screenshots"]
            )
        if set(pair) != {"literal", "wildcard"}:
            continue
        literal_ids = pair["literal"]["ids"]
        wildcard_ids = pair["wildcard"]["ids"]
        literal_set = set(literal_ids)
        wildcard_set = set(wildcard_ids)
        missing = [value for value in literal_ids if value not in wildcard_set]
        extra = [value for value in wildcard_ids if value not in literal_set]
        wildcard_record_by_id = {
            record["paperId"]: record
            for record in pair["wildcard"]["records"]
            if isinstance(record, dict) and isinstance(record.get("paperId"), str)
        }
        comparisons.append(
            {
                "partition_id": partition,
                "protocol_changed_partition": partition in CHANGED_IDS,
                "literal_artifact": pair["literal"]["path"],
                "wildcard_artifact": pair["wildcard"]["path"],
                "literal_total": pair["literal"]["total"],
                "wildcard_total": pair["wildcard"]["total"],
                "literal_ordered_stable_ids_sha256": pair["literal"][
                    "ordered_stable_ids_sha256"
                ],
                "wildcard_ordered_stable_ids_sha256": pair["wildcard"][
                    "ordered_stable_ids_sha256"
                ],
                "missing_from_wildcard": missing,
                "wildcard_only": extra,
                "wildcard_only_records": [
                    {
                        "paperId": value,
                        "title": wildcard_record_by_id[value].get("title"),
                        "year": wildcard_record_by_id[value].get("year"),
                    }
                    for value in extra
                    if value in wildcard_record_by_id
                ],
                "literal_is_subset": not missing,
                "exact_set_equality": not missing and not extra,
            }
        )

    all_complete = len(comparisons) == len(SCHEDULE_IDS) and not errors
    all_supersets = all(item["literal_is_subset"] for item in comparisons)
    all_equal = all(item["exact_set_equality"] for item in comparisons)
    safe = all_complete and all_supersets and all_equal
    assessment = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Scopus",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest_file(args.plan),
        "protocol_commit": plan.get("protocol_commit"),
        "event_count": len(events),
        "successful_partition_comparison_count": len(comparisons),
        "screenshot_file_count": len(screenshot_paths),
        "required_screenshot_file_count": len(events) * 2,
        "schedule": {
            "all_nine_current_literal_partitions_completed": all_complete,
            "changed_partitions_completed": all(
                any(
                    item["partition_id"] == partition
                    and item["protocol_changed_partition"]
                    for item in comparisons
                )
                for partition in CHANGED_IDS
            ) and all_complete,
            "proximity_operators_used": False,
            "pair_expansions_used": False,
        },
        "wildcard": {
            "candidate_count": plan.get("wildcard_candidate", {}).get(
                "wildcard_count"
            ),
            "replaced_literal_count": plan.get("wildcard_candidate", {}).get(
                "replaced_literal_count"
            ),
            "every_literal_set_is_subset": all_complete and all_supersets,
            "every_partition_has_exact_set_equality": all_complete and all_equal,
            "safe_for_all_main_partitions": safe,
            "preferred_when_safe": True,
            "decision": (
                "adopt_ten_population_wildcards_for_all_main_partitions"
                if safe
                else "retain_literals_pending_safe_complete_comparison"
            ),
        },
        "comparisons": comparisons,
        "errors": errors,
        "status": "passed" if all_complete else "failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "partitions": len(comparisons),
                "screenshots": len(screenshot_paths),
                "wildcard_decision": assessment["wildcard"]["decision"],
                "errors": len(errors),
            }
        )
    )
    return 0 if all_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
