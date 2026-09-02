#!/usr/bin/env python3
"""Assess Web of Science PSR population-wildcard evidence."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from build_plan import DEFAULT_OUTPUT, PILOT_ROOT, PSR_IDS, load, validate
from run_pilot import artifact_summary, sequence_sha256, screenshot_paths

SCHEMA = "wos-psr-population-wildcard-pilot-assessment/v1"
RUN_RECEIPT = PILOT_ROOT / "searches/run-receipt.json"
OUTPUT = PILOT_ROOT / "searches/assessment.json"
KNOWN_DOI = "10.1002/sys.70051"


def ordered_union(sequences: list[list[str]]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for sequence in sequences:
        for value in sequence:
            if value not in seen:
                seen.add(value)
                result.append(value)
    return result


def validate_screenshots(output: Path, artifact: Mapping[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    receipts: list[dict[str, Any]] = []
    screenshots = artifact.get("output_metadata", {}).get("screenshots", {})
    for key, image in zip(("search_page", "results_page"), screenshot_paths(output)):
        evidence = screenshots.get(key, {}) if isinstance(screenshots, Mapping) else {}
        try:
            data = image.read_bytes()
        except OSError as error:
            errors.append(f"Could not read {image}: {error}")
            continue
        if (
            not data.startswith(b"\x89PNG\r\n\x1a\n")
            or evidence.get("path") != image.name
            or evidence.get("sha256") != hashlib.sha256(data).hexdigest()
            or not isinstance(evidence.get("width"), int)
            or evidence.get("width") < 1
            or not isinstance(evidence.get("height"), int)
            or evidence.get("height") < 1
            or evidence.get("browser_chrome_captured") is not False
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            errors.append(f"Invalid screenshot evidence for {image}")
        receipts.append(
            {
                "json": str(output.relative_to(PILOT_ROOT)),
                "kind": key,
                "file": str(image.relative_to(PILOT_ROOT)),
                "sha256": evidence.get("sha256"),
                "width": evidence.get("width"),
                "height": evidence.get("height"),
                "email_elements_masked": evidence.get("email_elements_masked"),
            }
        )
    return errors, receipts


def build() -> dict[str, Any]:
    errors: list[str] = []
    plan = load(DEFAULT_OUTPUT)
    errors.extend(validate(plan))
    run = load(RUN_RECEIPT)
    if (
        run.get("schema_version") != "wos-psr-population-wildcard-pilot-run/v1"
        or run.get("success") is not True
        or run.get("successful_event_count") != 8
        or run.get("attempt_count") != 8
        or run.get("stopped_after_failure") is not False
        or len(run.get("selected_artifacts", {})) != 8
    ):
        errors.append("Run receipt is incomplete")

    event_summaries: dict[str, dict[str, Any]] = {}
    record_catalog: dict[str, dict[str, Any]] = {}
    screenshot_receipts: list[dict[str, Any]] = []
    events_by_id = {item["event_id"]: item for item in plan.get("events", [])}
    for event_id, relative in run.get("selected_artifacts", {}).items():
        event = events_by_id[event_id]
        output = PILOT_ROOT / relative
        artifact = load(output)
        summary = artifact_summary(output, event)
        if summary.get("valid") is not True:
            errors.append(f"Source artifact validation failed for {event_id}")
        rows = artifact.get("results", [])
        ids = [row["paperId"] for row in rows]
        if summary.get("ordered_wos_ids_sha256") != sequence_sha256(ids):
            errors.append(f"Stable-ID hash changed for {event_id}")
        shot_errors, shots = validate_screenshots(output, artifact)
        errors.extend(shot_errors)
        screenshot_receipts.extend(shots)
        event_summaries[event_id] = {
            "event_id": event_id,
            "partition_id": event["partition_id"],
            "variant": event["variant"],
            "artifact": relative,
            "query_characters": event["query_characters"],
            "total": artifact["total"],
            "ordered_wos_ids": ids,
            "ordered_wos_ids_sha256": sequence_sha256(ids),
        }
        for row in rows:
            record_catalog.setdefault(
                row["paperId"],
                {
                    "paper_id": row["paperId"],
                    "doi": row.get("doi"),
                    "title": row.get("title", ""),
                    "snippet": row.get("snippet", ""),
                },
            )

    partitions: dict[str, Any] = {}
    for partition_id in PSR_IDS:
        literal = event_summaries.get(f"literal-{partition_id}", {})
        wildcard = event_summaries.get(f"wildcard-{partition_id}", {})
        literal_ids = literal.get("ordered_wos_ids", [])
        wildcard_ids = wildcard.get("ordered_wos_ids", [])
        missing = sorted(set(literal_ids) - set(wildcard_ids))
        wildcard_only = sorted(set(wildcard_ids) - set(literal_ids))
        partitions[partition_id] = {
            "literal": literal,
            "wildcard": wildcard,
            "comparison": {
                "literal_missing_from_wildcard": missing,
                "wildcard_only_wos_ids": wildcard_only,
                "sets_equal": set(literal_ids) == set(wildcard_ids),
                "orders_equal": literal_ids == wildcard_ids,
                "wildcard_is_superset": set(literal_ids).issubset(wildcard_ids),
            },
        }
        if missing:
            errors.append(f"Wildcard query lost literal IDs in {partition_id}")

    wildcard_only_ids = sorted(
        {
            identifier
            for value in partitions.values()
            for identifier in value["comparison"]["wildcard_only_wos_ids"]
        }
    )
    if wildcard_only_ids:
        errors.append("Wildcard-only records require population review")
    if len(screenshot_receipts) != 16 or len({item["file"] for item in screenshot_receipts}) != 16:
        errors.append("The pilot does not retain 16 unique screenshots")

    literal_union = ordered_union(
        [partitions[key]["literal"].get("ordered_wos_ids", []) for key in PSR_IDS]
    )
    wildcard_union = ordered_union(
        [partitions[key]["wildcard"].get("ordered_wos_ids", []) for key in PSR_IDS]
    )
    known_ids = sorted(
        identifier
        for identifier, row in record_catalog.items()
        if str(row.get("doi") or "").casefold() == KNOWN_DOI
    )
    known_membership = {
        key: {
            "literal": [identifier for identifier in known_ids if identifier in partitions[key]["literal"].get("ordered_wos_ids", [])],
            "wildcard": [identifier for identifier in known_ids if identifier in partitions[key]["wildcard"].get("ordered_wos_ids", [])],
        }
        for key in PSR_IDS
    }
    if not known_ids or not any(value["wildcard"] for value in known_membership.values()):
        errors.append("Buruso known-item recall failed")

    all_equal = all(value["comparison"]["sets_equal"] for value in partitions.values())
    all_orders_equal = all(value["comparison"]["orders_equal"] for value in partitions.values())
    passed = not errors and all_equal and all_orders_equal
    return {
        "schema_version": SCHEMA,
        "pilot": "006",
        "source": "Web of Science Core Collection",
        "namespace": "prior_secondary_review_supporting_search",
        "status": "passed" if passed else "failed",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": plan.get("protocol_commit"),
        "decision": {
            "psr_population_wildcards": (
                "accepted_and_preferred_for_all_four_psr_partitions"
                if passed
                else "unresolved"
            ),
            "x_additions": "remain_literal",
            "broader_pilot005_family_map": "remains_rejected",
            "final_search_authorization": "not_granted_by_this_diagnostic_pilot",
        },
        "wildcard_acceptance": {
            "candidate_count": 10,
            "replaced_population_literal_count": 22,
            "query_character_reduction": 255,
            "all_four_sets_equal": all_equal,
            "all_four_orders_equal": all_orders_equal,
            "all_literal_ids_retained": all(
                value["comparison"]["wildcard_is_superset"]
                for value in partitions.values()
            ),
            "wildcard_only_wos_ids": wildcard_only_ids,
            "wildcard_only_records": [record_catalog[value] for value in wildcard_only_ids],
            "adopt_for_partitions": list(PSR_IDS) if passed else [],
        },
        "partition_results": partitions,
        "union_reconciliation": {
            "literal_union_count": len(literal_union),
            "wildcard_union_count": len(wildcard_union),
            "sets_equal": set(literal_union) == set(wildcard_union),
            "orders_equal": literal_union == wildcard_union,
            "literal_ordered_wos_ids": literal_union,
            "wildcard_ordered_wos_ids": wildcard_union,
        },
        "known_item": {
            "doi": KNOWN_DOI,
            "wos_ids": known_ids,
            "partition_membership": known_membership,
            "retrieved_by_successful_wildcard_union": any(
                value["wildcard"] for value in known_membership.values()
            ),
        },
        "screenshots": {
            "schema_version": "web-of-science-automatic-screenshots/v1",
            "successful_event_count": len(event_summaries),
            "required_file_count": 16,
            "verified_file_count": len(screenshot_receipts),
            "files": screenshot_receipts,
        },
        "attempt_accounting": {
            "attempt_count": run.get("attempt_count"),
            "successful_event_count": run.get("successful_event_count"),
            "failure_count": sum(item.get("valid") is not True for item in run.get("outcomes", [])),
        },
        "controls": plan.get("controls"),
        "errors": errors,
    }


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    assessment = build()
    write_create_only(OUTPUT, assessment)
    print(json.dumps({"status": assessment["status"], "errors": assessment["errors"], "output": str(OUTPUT)}, indent=2))
    return 0 if assessment["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
