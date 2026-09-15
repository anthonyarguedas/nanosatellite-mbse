#!/usr/bin/env python3
"""Build the ATAI Pilot 008 literal-to-wildcard set assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from queries import SCHEDULE_IDS

SCHEMA = "atai-pilot-008-assessment/v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_ids(artifact: dict[str, Any]) -> list[str]:
    return [str(record.get("paperId")) for record in artifact.get("results", [])]


def record_profile(record: dict[str, Any], partitions: list[str]) -> dict[str, Any]:
    return {
        "paper_id": str(record.get("paperId")),
        "title": record.get("title"),
        "year": record.get("year"),
        "publication_title": record.get("publicationTitle"),
        "abstract": record.get("abstract"),
        "wildcard_only_in_partitions": partitions,
    }


def screenshot_paths(output: Path) -> dict[str, Path]:
    return {
        "search_page": output.with_name(f"{output.stem}.search-page.png"),
        "results_page": output.with_name(f"{output.stem}.results-page.png"),
    }


def load_review(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return load(path)


def build(root: Path, review_path: Path | None) -> dict[str, Any]:
    searches = root / "searches"
    plan = load(searches / "event-plan.json")
    receipt = load(searches / "run-receipt.json")
    marking = load(searches / "nonmergeable-marking.json")
    failure_history = load(searches / "failure-history.json")
    review = load_review(review_path)
    errors: list[str] = []

    events = plan.get("events", [])
    plan_by_id = {event["event_id"]: event for event in events}
    if (
        plan.get("schema_version") != "atai-pilot-008-event-plan/v1"
        or len(events) != 18
        or receipt.get("status") != "complete"
        or receipt.get("completed_event_count") != 18
    ):
        errors.append("The predeclared eighteen-event run is incomplete")

    artifacts: dict[tuple[str, str], dict[str, Any]] = {}
    artifact_paths: dict[tuple[str, str], Path] = {}
    screenshots: list[dict[str, Any]] = []
    for outcome in receipt.get("outcomes", []):
        event_id = outcome.get("event_id")
        event = plan_by_id.get(event_id)
        if event is None:
            errors.append(f"Run outcome lacks a plan event: {event_id}")
            continue
        output = root / outcome["output"]
        artifact = load(output)
        key = (event["variant"], event["schedule_id"])
        artifacts[key] = artifact
        artifact_paths[key] = output
        metadata = artifact.get("output_metadata", {})
        run = metadata.get("prisma_search_run", {})
        strategy = run.get("strategy", {})
        limits = strategy.get("limits", {})
        date = limits.get("publication_date", {}).get("effective", {})
        ids = stable_ids(artifact)
        if (
            outcome.get("return_code") != 0
            or artifact.get("schema_version") != "academic-search-result/v1"
            or artifact.get("requested_query") != event["query"]
            or metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or not isinstance(artifact.get("total"), int)
            or artifact.get("total") != len(ids)
            or len(ids) != len(set(ids))
            or any(not paper_id.isdigit() for paper_id in ids)
        ):
            errors.append(f"Source artifact is incomplete or unstable: {event_id}")
        adapter = run.get("adapter", {})
        try:
            adapter_version = int(adapter.get("adapter_version", "0"))
        except (TypeError, ValueError):
            adapter_version = 0
        if (
            adapter.get("adapter_id") != "search_proquest_aerospace"
            or adapter_version < 6
            or strategy.get("search_scope") != "Advanced Technologies & Aerospace Index"
            or strategy.get("query_syntax", {}).get("spelling_variants") is not False
            or strategy.get("query_syntax", {}).get("form_variants") is not False
            or limits.get("language", {}).get("value") != "LA(English)"
            or date.get("start") != "2011-01-01"
            or date.get("end") != "2026-08-29"
            or date.get("inclusive") != "both"
            or strategy.get("sort", {}).get("value") != "DateAsc"
            or limits.get("document_type", {}).get("state") != "not_applied"
            or limits.get("peer_reviewed", {}).get("state") != "not_applied"
            or limits.get("full_text", {}).get("state") != "unavailable"
            or limits.get("access", {}).get("state") != "unavailable"
        ):
            errors.append(f"Source controls differ: {event_id}")
        if (
            artifact.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
            or metadata.get("normalized_merge_eligible") is not False
            or metadata.get("pilot_only") is not True
            or run.get("report_ready") is not False
        ):
            errors.append(f"Source artifact remains mergeable: {event_id}")

        screenshot_receipt = metadata.get("screenshots", {})
        screenshot_event = {
            "event_id": event_id,
            "json": str(output.relative_to(root)),
        }
        if (
            screenshot_receipt.get("schema_version") != "atai-automatic-screenshots/v1"
            or screenshot_receipt.get("automatic") is not True
            or screenshot_receipt.get("same_directory_as_json") is not True
        ):
            errors.append(f"Screenshot receipt is missing: {event_id}")
        for kind, path in screenshot_paths(output).items():
            evidence = screenshot_receipt.get(kind, {})
            if (
                not path.is_file()
                or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n"
                or evidence.get("path") != path.name
                or evidence.get("sha256") != file_sha256(path)
                or not isinstance(evidence.get("width"), int)
                or evidence["width"] <= 0
                or not isinstance(evidence.get("height"), int)
                or evidence["height"] <= 0
                or evidence.get("browser_chrome_captured") is not False
                or evidence.get("complete_page_url_retained") is not False
                or evidence.get("session_identifiers_retained") is not False
            ):
                errors.append(f"Screenshot evidence differs: {event_id} {kind}")
            screenshot_event[kind] = {
                **evidence,
                "repository_path": str(path.relative_to(root)),
            }
        screenshots.append(screenshot_event)

    if set(artifacts) != {
        (variant, partition)
        for partition in SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    }:
        errors.append("The run does not contain one literal and wildcard artifact per partition")

    comparisons: dict[str, Any] = {}
    wildcard_only_partitions: dict[str, list[str]] = {}
    wildcard_records: dict[str, dict[str, Any]] = {}
    literal_union: set[str] = set()
    wildcard_union: set[str] = set()
    for partition in SCHEDULE_IDS:
        literal_artifact = artifacts.get(("literal", partition), {})
        wildcard_artifact = artifacts.get(("wildcard", partition), {})
        literal_ids = stable_ids(literal_artifact)
        wildcard_ids = stable_ids(wildcard_artifact)
        literal_set = set(literal_ids)
        wildcard_set = set(wildcard_ids)
        literal_union.update(literal_set)
        wildcard_union.update(wildcard_set)
        missing = [paper_id for paper_id in literal_ids if paper_id not in wildcard_set]
        extra = [paper_id for paper_id in wildcard_ids if paper_id not in literal_set]
        for paper_id in extra:
            wildcard_only_partitions.setdefault(paper_id, []).append(partition)
            record = next(
                item
                for item in wildcard_artifact.get("results", [])
                if str(item.get("paperId")) == paper_id
            )
            wildcard_records.setdefault(paper_id, record)
        comparisons[partition] = {
            "literal_total": literal_artifact.get("total"),
            "wildcard_total": wildcard_artifact.get("total"),
            "literal_stable_ids_in_source_order": literal_ids,
            "wildcard_stable_ids_in_source_order": wildcard_ids,
            "literal_ids_missing_from_wildcard": missing,
            "wildcard_only_ids": extra,
            "sets_equal": literal_set == wildcard_set,
            "orders_equal": literal_ids == wildcard_ids,
            "literal_artifact": str(artifact_paths.get(("literal", partition), Path()).relative_to(root)),
            "wildcard_artifact": str(artifact_paths.get(("wildcard", partition), Path()).relative_to(root)),
        }
        if missing:
            errors.append(f"The wildcard translation loses literal IDs in {partition}")

    wildcard_only_ids = sorted(wildcard_only_partitions, key=lambda value: int(value))
    profiles = [
        record_profile(
            wildcard_records[paper_id], wildcard_only_partitions[paper_id]
        )
        for paper_id in wildcard_only_ids
    ]

    review_decisions: dict[str, dict[str, Any]] = {}
    if wildcard_only_ids:
        if review is None:
            errors.append("Wildcard-only records require a recorded concept review")
        else:
            if review.get("schema_version") != "atai-pilot-008-wildcard-only-review/v1":
                errors.append("Wildcard-only review schema differs")
            values = review.get("records")
            if not isinstance(values, list):
                errors.append("Wildcard-only review records are missing")
            else:
                review_decisions = {
                    str(item.get("paper_id")): item
                    for item in values
                    if isinstance(item, dict)
                }
                if set(review_decisions) != set(wildcard_only_ids):
                    errors.append("Wildcard-only review does not cover the exact extra-ID union")
                for paper_id, item in review_decisions.items():
                    if item.get("within_intended_concepts") is not True:
                        errors.append(
                            f"Wildcard-only record is outside the intended concepts: {paper_id}"
                        )
                    if not str(item.get("basis", "")).strip():
                        errors.append(f"Wildcard-only review lacks a basis: {paper_id}")

    if (
        marking.get("schema_version") != "atai-pilot-008-nonmergeable-marking/v1"
        or marking.get("status") != "complete"
        or marking.get("marked_artifact_count") != 23
    ):
        errors.append(
            "The nonmergeable marking receipt does not cover eighteen successes and five failures"
        )
    if (
        failure_history.get("schema_version") != "atai-pilot-008-failure-history/v1"
        or failure_history.get("status") != "complete"
        or failure_history.get("attempt_count") != 6
        or failure_history.get("retained_source_failure_artifact_count") != 5
        or failure_history.get("retained_failure_screenshot_count") != 2
    ):
        errors.append("The retained failure history is incomplete")
    if len(screenshots) != 18:
        errors.append("The pilot does not index all eighteen successful screenshot pairs")

    accepted = not errors
    return {
        "schema_version": SCHEMA,
        "status": "complete" if accepted else "error",
        "source": plan.get("source"),
        "pilot": "008",
        "protocol_commit": plan.get("protocol_commit"),
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": (
            "accept_bounded_wildcard_translation" if accepted else "do_not_accept_pending_errors"
        ),
        "decision_basis": (
            "Every fresh wildcard partition retained every adjacent literal stable ID under "
            "strict complete capture. Every wildcard-only record, if any, was reviewed as an "
            "intended concept match. All events retained mandatory screenshots."
            if accepted
            else "The acceptance checks listed in errors did not all pass."
        ),
        "translation": plan.get("translation"),
        "partition_comparisons": comparisons,
        "union_comparison": {
            "literal_distinct_ids": len(literal_union),
            "wildcard_distinct_ids": len(wildcard_union),
            "literal_ids_missing_from_wildcard": sorted(
                literal_union - wildcard_union, key=lambda value: int(value)
            ),
            "wildcard_only_ids": wildcard_only_ids,
        },
        "wildcard_only_records": profiles,
        "wildcard_only_review": review,
        "controls": plan.get("controls"),
        "automatic_screenshots": {
            "required_per_event": 2,
            "successful_event_count": len(screenshots),
            "successful_event_screenshot_file_count": len(screenshots) * 2,
            "retained_failure_screenshot_file_count": failure_history.get(
                "retained_failure_screenshot_count"
            ),
            "events": screenshots,
        },
        "retained_failure_history": failure_history,
        "successful_source_artifact_count": len(artifacts),
        "retained_source_failure_artifact_count": failure_history.get(
            "retained_source_failure_artifact_count"
        ),
        "source_artifact_count": marking.get("marked_artifact_count"),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--wildcard-only-review", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assessment = build(args.pilot_root, args.wildcard_only_review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
