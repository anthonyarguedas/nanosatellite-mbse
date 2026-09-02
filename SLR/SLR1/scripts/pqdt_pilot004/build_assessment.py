#!/usr/bin/env python3
"""Build the PQDT Global Pilot 004 wildcard and screenshot assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from build_plan import DEFAULT_OUTPUT, PILOT_ROOT, PROTOCOL_COMMIT, SCHEDULE_IDS, load, validate
from run_pilot import SCREENSHOT_SCHEMA, strict_artifact_summary

SCHEMA = "pqdt-global-pilot004-assessment/v1"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
DEFAULT_REVIEW = PILOT_ROOT / "searches" / "wildcard-only-review.json"
DEFAULT_OUTPUT_PATH = PILOT_ROOT / "searches" / "assessment.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered_unique(sequences: Iterable[Iterable[str]]) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for sequence in sequences:
        for value in sequence:
            if value not in seen:
                seen.add(value)
                values.append(value)
    return values


def load_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return load(path)


def safe_record(record: Mapping[str, Any], partitions: list[str]) -> dict[str, Any]:
    return {
        "paper_id": record.get("paperId"),
        "title": record.get("title"),
        "year": record.get("year"),
        "publication_title": record.get("publicationTitle"),
        "abstract": record.get("abstract"),
        "wildcard_only_in_partitions": partitions,
    }


def build(
    root: Path,
    plan_path: Path,
    receipt_path: Path,
    review_path: Path | None,
) -> dict[str, Any]:
    plan = load(plan_path)
    receipt = load(receipt_path)
    errors = validate(plan)
    events = plan.get("events", [])
    if (
        receipt.get("schema_version") != "pqdt-global-pilot004-run-receipt/v1"
        or receipt.get("status") != "complete"
        or receipt.get("predeclared_event_count") != 18
        or receipt.get("completed_event_count") != 18
        or receipt.get("event_plan_sha256") != file_sha256(plan_path)
    ):
        errors.append("The predeclared eighteen-event run is incomplete")

    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    paths: dict[tuple[str, str], Path] = {}
    records: dict[str, dict[str, Any]] = {}
    screenshot_events: list[dict[str, Any]] = []
    for event in events:
        output = root / "searches" / str(event["output"])
        try:
            summary = strict_artifact_summary(event, output, plan)
        except (OSError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate {event.get('event_id')}: {error}")
            continue
        key = (str(event["variant"]), str(event["partition_id"]))
        summaries[key] = summary
        paths[key] = output
        artifact = load(output)
        for record in artifact.get("results", []):
            if isinstance(record, dict) and isinstance(record.get("paperId"), str):
                records.setdefault(record["paperId"], record)
        metadata = artifact.get("output_metadata", {})
        screenshot_events.append(
            {
                "event_id": event["event_id"],
                "json": str(output.relative_to(root)),
                "schema_version": metadata.get("screenshots", {}).get("schema_version"),
                **summary["screenshots"],
            }
        )

    expected_keys = {
        (variant, partition)
        for partition in SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    }
    if set(summaries) != expected_keys:
        errors.append("The run lacks one literal and wildcard result per partition")

    comparisons: dict[str, Any] = {}
    wildcard_only_partitions: dict[str, list[str]] = {}
    literal_union_sequences: list[list[str]] = []
    wildcard_union_sequences: list[list[str]] = []
    for partition in SCHEDULE_IDS:
        literal = summaries.get(("literal", partition), {})
        wildcard = summaries.get(("wildcard", partition), {})
        literal_ids = list(literal.get("stable_ids_in_source_order", []))
        wildcard_ids = list(wildcard.get("stable_ids_in_source_order", []))
        literal_set = set(literal_ids)
        wildcard_set = set(wildcard_ids)
        missing = [value for value in literal_ids if value not in wildcard_set]
        extra = [value for value in wildcard_ids if value not in literal_set]
        for paper_id in extra:
            wildcard_only_partitions.setdefault(paper_id, []).append(partition)
        if missing:
            errors.append(f"The wildcard translation loses literal IDs in {partition}")
        comparisons[partition] = {
            "literal_total": literal.get("source_total"),
            "wildcard_total": wildcard.get("source_total"),
            "literal_stable_ids_in_source_order": literal_ids,
            "wildcard_stable_ids_in_source_order": wildcard_ids,
            "literal_ids_missing_from_wildcard": missing,
            "wildcard_only_ids": extra,
            "sets_equal": literal_set == wildcard_set,
            "orders_equal": literal_ids == wildcard_ids,
            "wildcard_is_superset": literal_set.issubset(wildcard_set),
            "literal_artifact": (
                str(paths[("literal", partition)].relative_to(root))
                if ("literal", partition) in paths
                else None
            ),
            "wildcard_artifact": (
                str(paths[("wildcard", partition)].relative_to(root))
                if ("wildcard", partition) in paths
                else None
            ),
        }
        literal_union_sequences.append(literal_ids)
        wildcard_union_sequences.append(wildcard_ids)

    wildcard_only_ids = sorted(wildcard_only_partitions, key=lambda value: int(value))
    wildcard_only_records = [
        safe_record(records.get(paper_id, {"paperId": paper_id}), wildcard_only_partitions[paper_id])
        for paper_id in wildcard_only_ids
    ]
    review = load_optional(review_path)
    review_by_id: dict[str, Mapping[str, Any]] = {}
    if wildcard_only_ids:
        if review is None:
            errors.append("Wildcard-only records require a recorded concept review")
        else:
            if review.get("schema_version") != "pqdt-global-pilot004-wildcard-only-review/v1":
                errors.append("Wildcard-only review schema changed")
            review_rows = review.get("records")
            if not isinstance(review_rows, list):
                errors.append("Wildcard-only review records are missing")
            else:
                review_by_id = {
                    str(item.get("paper_id")): item
                    for item in review_rows
                    if isinstance(item, Mapping)
                }
                if set(review_by_id) != set(wildcard_only_ids):
                    errors.append("Wildcard-only review does not cover the exact extra-ID union")
                for paper_id, row in review_by_id.items():
                    if row.get("within_intended_concepts") is not True:
                        errors.append(
                            f"Wildcard-only record is outside the intended concepts: {paper_id}"
                        )
                    if not str(row.get("basis", "")).strip():
                        errors.append(f"Wildcard-only review lacks a basis: {paper_id}")

    screenshot_count = sum(len(summary.get("screenshots", {})) for summary in summaries.values())
    if len(screenshot_events) != 18 or screenshot_count != 36:
        errors.append("The mandatory screenshot ledger does not contain 18 pairs")
    accepted = not errors
    literal_union = ordered_unique(literal_union_sequences)
    wildcard_union = ordered_unique(wildcard_union_sequences)
    return {
        "schema_version": SCHEMA,
        "status": "complete" if accepted else "error",
        "source": plan.get("source"),
        "pilot": "004",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": (
            "accept_and_prefer_bounded_wildcard_translation"
            if accepted
            else "do_not_accept_pending_errors"
        ),
        "decision_basis": (
            "Every bounded-wildcard partition retained every fresh adjacent literal stable ID under strict two-pass complete capture. Every wildcard-only record, if any, passed an intended-concept review. Every event retained both mandatory screenshots."
            if accepted
            else "The acceptance checks listed in errors did not all pass."
        ),
        "translation": plan.get("translation"),
        "partition_comparisons": comparisons,
        "union_comparison": {
            "literal_distinct_ids": len(literal_union),
            "wildcard_distinct_ids": len(wildcard_union),
            "literal_ids_missing_from_wildcard": [
                value for value in literal_union if value not in set(wildcard_union)
            ],
            "wildcard_only_ids": [
                value for value in wildcard_union if value not in set(literal_union)
            ],
        },
        "wildcard_only_records": wildcard_only_records,
        "wildcard_only_review": review,
        "accepted_for_partitions": list(SCHEDULE_IDS) if accepted else [],
        "controls": plan.get("controls"),
        "automatic_screenshots": {
            "schema_version": SCREENSHOT_SCHEMA,
            "required_per_event": 2,
            "successful_event_count": len(screenshot_events),
            "screenshot_file_count": screenshot_count,
            "events": screenshot_events,
        },
        "source_artifact_count": len(summaries),
        "source_artifact_boundary": (
            "Marker-bound strict adapter artifacts remain isolated pilot evidence. The pilot assessment and all derived unions are nonmergeable and are not final-search inputs."
        ),
        "source_window": plan.get("source_window"),
        "limitations": [
            "PQDT YR has year precision. Records dated 2026 still require screening against the exact 2026-08-29 diagnostic cutoff.",
            "LA(English) is metadata evidence. Full-report language remains a screening decision.",
            "Degree subtype, completion, access, and full-text availability remain screening decisions.",
            "The source wildcard may match suffixes within each declared bound. Wildcard-only records require explicit intended-concept review.",
        ],
        "plan": {
            "artifact": str(plan_path.relative_to(root)),
            "sha256": file_sha256(plan_path),
            "event_count": len(events),
        },
        "run_receipt": {
            "artifact": str(receipt_path.relative_to(root)),
            "sha256": file_sha256(receipt_path),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--wildcard-only-review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    assessment = build(
        args.pilot_root,
        args.plan,
        args.receipt,
        args.wildcard_only_review,
    )
    if args.inspect:
        print(
            json.dumps(
                {
                    "status": assessment["status"],
                    "wildcard_only_records": assessment["wildcard_only_records"],
                    "errors": assessment["errors"],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0 if assessment["status"] == "complete" else 1
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": assessment["status"], "errors": assessment["errors"]}, indent=2))
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
