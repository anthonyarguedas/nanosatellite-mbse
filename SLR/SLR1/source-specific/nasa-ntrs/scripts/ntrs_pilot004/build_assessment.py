#!/usr/bin/env python3
"""Build the NASA NTRS Pilot 004 schedule and wildcard assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import queries

SCHEMA = "ntrs-post-proximity-wildcard-pilot-assessment/v1"
PLAN_SCHEMA = "ntrs-post-proximity-wildcard-pilot-plan/v1"
RUN_SCHEMA = "ntrs-post-proximity-wildcard-pilot-run/v1"
SCREENSHOT_SCHEMA = "ntrs-automatic-screenshots/v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.NTRS_COMMIT.json")


def image_path(path: Path, suffix: str) -> Path:
    return path.with_name(f"{path.stem}{suffix}")


def ordered_hash(values: list[str]) -> str:
    result = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


def event_evidence(
    *, pilot_root: Path, event: dict[str, Any], adapter_hash: str
) -> tuple[dict[str, Any], list[str], set[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    path = pilot_root / "searches" / event["output"]
    value = load(path)
    metadata = value.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, dict) else {}
    records = value.get("results", [])
    ids = [
        row.get("paperId")
        for row in records
        if isinstance(row, dict) and isinstance(row.get("paperId"), str)
    ]
    rows_by_id = {
        row["paperId"]: row
        for row in records
        if isinstance(row, dict) and isinstance(row.get("paperId"), str)
    }
    if value.get("executed_query") != event["query"]:
        errors.append("executed query mismatch")
    if value.get("total") != len(records) or len(records) != len(ids):
        errors.append("total or record count mismatch")
    if len(ids) != len(set(ids)):
        errors.append("duplicate stable ID")
    if metadata.get("status") != "success" or metadata.get("retrieval_complete") is not True:
        errors.append("event is not a complete success")
    if metadata.get("merge_eligible") is not True:
        errors.append("strict event lacks merge eligibility")
    if prisma.get("completion_status") != "complete":
        errors.append("PRISMA completion mismatch")
    if prisma.get("adapter", {}).get("script_sha256") != adapter_hash:
        errors.append("adapter binding mismatch")
    strategy = prisma.get("strategy", {}) if isinstance(prisma, dict) else {}
    limits = strategy.get("limits", {}) if isinstance(strategy, dict) else {}
    publication = limits.get("publication_date", {}) if isinstance(limits, dict) else {}
    if (
        publication.get("state") != "applied"
        or publication.get("value", {}).get("gte") != "2011-01-01"
        or publication.get("value", {}).get("lte") != "2026-08-29"
    ):
        errors.append("publication date mismatch")
    if strategy.get("sort", {}).get("value") != "Publication Date (Oldest)":
        errors.append("sort mismatch")
    for key in (
        "title",
        "author",
        "organization",
        "document_type",
        "center",
        "subject",
        "report_number",
        "funding_number",
        "keyword",
        "collection",
        "source",
        "distribution",
        "subject_category",
        "thesaurus_term",
    ):
        if limits.get(key, {}).get("state") != "not_applied":
            errors.append(f"unexpected applied limiter: {key}")
    marker_file = marker_path(path)
    marker = load(marker_file)
    if (
        marker.get("schema") != "ntrs_output_commit_marker_v1"
        or marker.get("normalized_json", {}).get("sha256") != digest(path)
        or marker.get("normalized_json", {}).get("bytes") != path.stat().st_size
    ):
        errors.append("terminal marker mismatch")
    screenshots = metadata.get("screenshots", {}) if isinstance(metadata, dict) else {}
    images = []
    if (
        screenshots.get("schema_version") != SCREENSHOT_SCHEMA
        or screenshots.get("automatic") is not True
        or screenshots.get("same_directory_as_json") is not True
    ):
        errors.append("screenshot receipt mismatch")
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        image = image_path(path, suffix)
        receipt = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        image_valid = bool(
            image.is_file()
            and receipt.get("path") == image.name
            and receipt.get("sha256") == digest(image)
            and isinstance(receipt.get("width"), int)
            and receipt["width"] > 0
            and isinstance(receipt.get("height"), int)
            and receipt["height"] > 0
            and receipt.get("full_page") is True
            and receipt.get("complete_page_url_retained") is False
            and receipt.get("session_identifiers_retained") is False
        )
        if not image_valid:
            errors.append(f"invalid {key} screenshot")
        images.append(
            {
                "kind": key,
                "path": str(image.relative_to(pilot_root)),
                "sha256": digest(image) if image.is_file() else None,
                "width": receipt.get("width"),
                "height": receipt.get("height"),
                "valid": image_valid,
            }
        )
    return (
        {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "variant": event["variant"],
            "path": str(path.relative_to(pilot_root)),
            "sha256": digest(path),
            "query_sha256": event["query_sha256"],
            "query_characters": len(event["query"]),
            "wildcard_count": event["query"].count("*"),
            "source_total": value.get("total"),
            "stable_id_count": len(ids),
            "ordered_stable_ids_sha256": ordered_hash(ids),
            "screenshots": images,
            "valid": not errors,
            "errors": errors,
        },
        ids,
        set(ids),
        rows_by_id,
    )


def build(
    *, pilot_root: Path, plan_path: Path, run_receipt_path: Path
) -> dict[str, Any]:
    plan = load(plan_path)
    run = load(run_receipt_path)
    errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("plan schema mismatch")
    if run.get("schema_version") != RUN_SCHEMA or run.get("success") is not True:
        errors.append("run receipt is not successful")
    if run.get("plan_sha256") != digest(plan_path):
        errors.append("run plan binding mismatch")
    if plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        errors.append("protocol commit mismatch")
    adapter_hash = plan.get("adapter", {}).get("sha256")
    if not isinstance(adapter_hash, str):
        errors.append("missing adapter hash")
        adapter_hash = ""

    evidence_rows: list[dict[str, Any]] = []
    sets: dict[tuple[str, str], set[str]] = {}
    records: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for event in plan.get("events", []):
        evidence, _ordered, stable_ids, rows = event_evidence(
            pilot_root=pilot_root,
            event=event,
            adapter_hash=adapter_hash,
        )
        evidence_rows.append(evidence)
        sets[(event["partition_id"], event["variant"])] = stable_ids
        records[(event["partition_id"], event["variant"])] = rows
        errors.extend(f"{event['event_id']}: {error}" for error in evidence["errors"])

    comparisons = []
    all_literal: set[str] = set()
    all_wildcard: set[str] = set()
    for partition in queries.SCHEDULE_IDS:
        literal = sets.get((partition, "literal"), set())
        wildcard = sets.get((partition, "wildcard"), set())
        missing = sorted(literal - wildcard)
        added = sorted(wildcard - literal)
        all_literal.update(literal)
        all_wildcard.update(wildcard)
        added_rows = records.get((partition, "wildcard"), {})
        comparisons.append(
            {
                "partition_id": partition,
                "literal_total": len(literal),
                "wildcard_total": len(wildcard),
                "missing_literal_ids": missing,
                "missing_literal_count": len(missing),
                "wildcard_only_ids": added,
                "wildcard_only_count": len(added),
                "wildcard_only_records": [
                    {
                        "paperId": stable_id,
                        "title": added_rows.get(stable_id, {}).get("title"),
                        "year": added_rows.get(stable_id, {}).get("year"),
                    }
                    for stable_id in added
                ],
                "set_relation": (
                    "equal"
                    if literal == wildcard
                    else "wildcard_strict_superset"
                    if literal < wildcard
                    else "missing_literal_records"
                ),
            }
        )
    missing_all = sorted(all_literal - all_wildcard)
    added_all = sorted(all_wildcard - all_literal)
    exact_all = all(item["set_relation"] == "equal" for item in comparisons)
    no_missing = not missing_all and all(
        item["missing_literal_count"] == 0 for item in comparisons
    )
    if not no_missing:
        errors.append("wildcard candidate misses literal records")
    if not exact_all:
        errors.append("complete candidate does not have partition-level set equality")

    screenshot_count = sum(
        image["valid"]
        for item in evidence_rows
        for image in item["screenshots"]
    )
    expected_screenshots = len(evidence_rows) * 2
    if screenshot_count != expected_screenshots:
        errors.append("screenshot count mismatch")
    status = "passed" if not errors else "failed"
    decision = (
        "adopt_standalone_wildcards_for_all_main_partitions"
        if status == "passed"
        else "retain_literal_translation_pending_follow_up"
    )
    return {
        "schema_version": SCHEMA,
        "status": status,
        "pilot": "004",
        "source": "NASA Technical Reports Server (NTRS)",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": {"path": str(plan_path), "sha256": digest(plan_path)},
        "run_receipt": {
            "path": str(run_receipt_path),
            "sha256": digest(run_receipt_path),
        },
        "adapter": dict(plan.get("adapter", {})),
        "accepted_source_event_count": sum(item["valid"] for item in evidence_rows),
        "source_event_count": len(evidence_rows),
        "verified_screenshot_file_count": screenshot_count,
        "required_screenshot_file_count": expected_screenshots,
        "events": evidence_rows,
        "comparisons": comparisons,
        "schedule_union": {
            "literal_unique_ids": len(all_literal),
            "wildcard_unique_ids": len(all_wildcard),
            "missing_literal_ids": missing_all,
            "missing_literal_count": len(missing_all),
            "wildcard_only_ids": added_all,
            "wildcard_only_count": len(added_all),
            "set_relation": "equal" if all_literal == all_wildcard else "different",
        },
        "wildcard": {
            "decision": decision,
            "candidate_count": queries.WILDCARD_ATOM_COUNT,
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "phrase_wildcards_used": False,
            "acronym_wildcards_used": False,
            "partition_level_exact_set_equality": exact_all,
            "literal_records_missing": not no_missing,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    result = build(
        pilot_root=args.pilot_root,
        plan_path=args.plan,
        run_receipt_path=args.run_receipt,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "events": result["source_event_count"],
                "screenshots": result["verified_screenshot_file_count"],
                "decision": result["wildcard"]["decision"],
                "errors": len(result["errors"]),
            }
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
