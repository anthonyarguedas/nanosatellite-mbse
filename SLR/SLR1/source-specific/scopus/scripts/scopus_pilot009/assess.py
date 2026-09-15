#!/usr/bin/env python3
"""Assess Scopus Pilot 009 repeat stability and wildcard set equality."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "scopus-post-proximity-wildcard-pilot-assessment/v1"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"
RUN_IDS = ("B1",)
CHANGED_IDS = ("BG1", "BG2", "BC1", "BT2")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered_id_hash(ids: list[str]) -> str:
    digest = hashlib.sha256()
    for stable_id in ids:
        encoded = stable_id.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def artifact_evidence(path: Path, expected_query: str) -> dict[str, Any]:
    value = load(path)
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    ids = [
        record.get("paperId")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("paperId"), str)
    ]
    screenshots = metadata.get("screenshots", {}) if isinstance(metadata, dict) else {}
    errors = []
    if value.get("schema_version") != "academic-search-result/v1":
        errors.append("schema")
    if value.get("requested_query") != expected_query:
        errors.append("query")
    if not isinstance(value.get("total"), int) or value.get("total") != len(records):
        errors.append("total")
    if len(ids) != len(records) or len(ids) != len(set(ids)):
        errors.append("stable_ids")
    if metadata.get("status") != "partial":
        errors.append("diagnostic_status")
    if metadata.get("retrieval_complete") is not True:
        errors.append("retrieval_complete")
    if metadata.get("merge_eligible") is not False:
        errors.append("merge_eligible")
    if metadata.get("prisma_search_run", {}).get("phase") != "pilot":
        errors.append("pilot_phase")
    if screenshots.get("schema_version") != SCREENSHOT_SCHEMA:
        errors.append("screenshot_schema")
    if screenshots.get("automatic") is not True:
        errors.append("screenshot_automatic")
    if screenshots.get("same_directory_as_json") is not True:
        errors.append("screenshot_directory")
    image_rows = []
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        image = path.with_name(f"{path.stem}{suffix}")
        receipt = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        if not image.is_file():
            errors.append(f"{key}_missing")
            continue
        digest = digest_file(image)
        if receipt.get("path") != image.name:
            errors.append(f"{key}_path")
        if receipt.get("sha256") != digest:
            errors.append(f"{key}_hash")
        if not isinstance(receipt.get("width"), int) or receipt["width"] <= 0:
            errors.append(f"{key}_width")
        if not isinstance(receipt.get("height"), int) or receipt["height"] <= 0:
            errors.append(f"{key}_height")
        image_rows.append(
            {
                "kind": key,
                "path": str(image),
                "sha256": digest,
                "width": receipt.get("width"),
                "height": receipt.get("height"),
            }
        )
    return {
        "path": str(path),
        "sha256": digest_file(path),
        "total": value.get("total"),
        "ids": ids,
        "records": records,
        "ordered_stable_ids_sha256": ordered_id_hash(ids),
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
        (event["partition_id"], event["variant"], event["pass_number"]): event
        for event in events
        if isinstance(event, dict)
    }
    comparisons = []
    errors = []
    all_screenshots: set[str] = set()
    for partition in RUN_IDS:
        variants: dict[str, dict[str, Any]] = {}
        for variant in ("literal", "wildcard"):
            passes = []
            for pass_number in (1, 2):
                event = event_map.get((partition, variant, pass_number))
                if event is None:
                    errors.append(
                        f"missing_plan_event:{partition}:{variant}:{pass_number}"
                    )
                    continue
                path = args.pilot_root / "searches" / event["output"]
                try:
                    evidence = artifact_evidence(path, event["query"])
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    errors.append(
                        f"artifact:{partition}:{variant}:{pass_number}:{type(error).__name__}"
                    )
                    continue
                passes.append(evidence)
                errors.extend(
                    f"artifact:{partition}:{variant}:{pass_number}:{item}"
                    for item in evidence["errors"]
                )
                all_screenshots.update(
                    image["path"] for image in evidence["screenshots"]
                )
            if len(passes) != 2:
                continue
            repeat_set_stable = bool(
                passes[0]["total"] == passes[1]["total"]
                and set(passes[0]["ids"]) == set(passes[1]["ids"])
            )
            variants[variant] = {
                "passes": passes,
                "repeat_set_stable": repeat_set_stable,
                "repeat_order_stable": passes[0]["ids"] == passes[1]["ids"],
            }
            if not repeat_set_stable:
                errors.append(f"repeat_set_mismatch:{partition}:{variant}")
        if set(variants) != {"literal", "wildcard"}:
            continue
        literal = variants["literal"]["passes"][0]
        wildcard = variants["wildcard"]["passes"][0]
        literal_set = set(literal["ids"])
        wildcard_set = set(wildcard["ids"])
        missing = [value for value in literal["ids"] if value not in wildcard_set]
        extra = [value for value in wildcard["ids"] if value not in literal_set]
        record_by_id = {
            record["paperId"]: record
            for record in wildcard["records"]
            if isinstance(record, dict) and isinstance(record.get("paperId"), str)
        }
        comparisons.append(
            {
                "partition_id": partition,
                "protocol_changed_partition": partition in CHANGED_IDS,
                "literal_total": literal["total"],
                "wildcard_total": wildcard["total"],
                "literal_repeat_set_stable": variants["literal"][
                    "repeat_set_stable"
                ],
                "literal_repeat_order_stable": variants["literal"][
                    "repeat_order_stable"
                ],
                "wildcard_repeat_set_stable": variants["wildcard"][
                    "repeat_set_stable"
                ],
                "wildcard_repeat_order_stable": variants["wildcard"][
                    "repeat_order_stable"
                ],
                "literal_ordered_stable_ids_sha256": literal[
                    "ordered_stable_ids_sha256"
                ],
                "wildcard_ordered_stable_ids_sha256": wildcard[
                    "ordered_stable_ids_sha256"
                ],
                "missing_from_wildcard": missing,
                "wildcard_only": extra,
                "wildcard_only_records": [
                    {
                        "paperId": value,
                        "title": record_by_id[value].get("title"),
                        "year": record_by_id[value].get("year"),
                    }
                    for value in extra
                    if value in record_by_id
                ],
                "literal_is_subset": not missing,
                "exact_set_equality": not missing and not extra,
                "artifacts": {
                    variant: [item["path"] for item in data["passes"]]
                    for variant, data in variants.items()
                },
            }
        )

    complete = len(comparisons) == len(RUN_IDS) and not errors
    equal = complete and all(item["exact_set_equality"] for item in comparisons)
    assessment = {
        "schema_version": SCHEMA,
        "pilot": "009",
        "source": "Scopus",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest_file(args.plan),
        "protocol_commit": plan.get("protocol_commit"),
        "event_count": len(events),
        "successful_partition_comparison_count": len(comparisons),
        "screenshot_file_count": len(all_screenshots),
        "required_screenshot_file_count": len(events) * 2,
        "schedule": {
            "b1_literal_and_wildcard_repeats_completed": complete,
            "changed_partitions_completed": False,
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
            "every_literal_set_is_subset": complete
            and all(item["literal_is_subset"] for item in comparisons),
            "every_partition_has_exact_set_equality": equal,
            "safe_for_all_planned_partitions": equal,
            "preferred_when_safe": True,
            "decision": (
                "accept_for_b1_pending_combined_assessment"
                if equal
                else "retain_literals_pending_safe_complete_comparison"
            ),
        },
        "comparisons": comparisons,
        "errors": errors,
        "status": "passed" if complete else "failed",
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
                "screenshots": len(all_screenshots),
                "wildcard_decision": assessment["wildcard"]["decision"],
                "errors": len(errors),
            }
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
