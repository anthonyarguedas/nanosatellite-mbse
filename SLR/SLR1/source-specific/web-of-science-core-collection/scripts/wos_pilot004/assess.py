#!/usr/bin/env python3
"""Validate and assess Web of Science Pilot 004 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from build_plan import (
    DEFAULT_OUTPUT,
    PILOT_ROOT,
    PROTOCOL_COMMIT,
    SCHEDULE_IDS,
    load,
    validate,
)

SCHEMA = "wos-current-schedule-wildcard-pilot-assessment/v1"
SCREENSHOT_SCHEMA = "web-of-science-automatic-screenshots/v1"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
DEFAULT_RECOVERY_RECEIPT = PILOT_ROOT / "searches" / "recovery-run-receipt.json"
INITIAL_VALIDATION_RECEIPT = (
    PILOT_ROOT / "searches" / "run-receipt-initial-local-validation-failure.json"
)
DEFAULT_ASSESSMENT = PILOT_ROOT / "searches" / "assessment.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def ordered_union(sequences: list[list[str]]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for sequence in sequences:
        for value in sequence:
            if value not in seen:
                seen.add(value)
                result.append(value)
    return result


def screenshot_paths(output: Path) -> dict[str, Path]:
    stem = output.name[:-5] if output.name.lower().endswith(".json") else output.name
    return {
        "search_page": output.with_name(f"{stem}.search-page.png"),
        "results_page": output.with_name(f"{stem}.results-page.png"),
    }


def validate_screenshots(
    output: Path, receipt: Any
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    if not isinstance(receipt, Mapping):
        return [f"Missing screenshot receipt in {output.name}"], rows
    if (
        receipt.get("schema_version") != SCREENSHOT_SCHEMA
        or receipt.get("automatic") is not True
        or receipt.get("no_opt_out") is not True
        or receipt.get("same_directory_as_json") is not True
        or receipt.get("complete") is not True
    ):
        errors.append(f"Screenshot contract changed in {output.name}")
    for key, image in screenshot_paths(output).items():
        evidence = receipt.get(key)
        if not isinstance(evidence, Mapping):
            errors.append(f"Missing {key} receipt in {output.name}")
            continue
        try:
            data = image.read_bytes()
        except OSError as error:
            errors.append(f"Could not read {image}: {error}")
            continue
        valid = bool(
            data.startswith(b"\x89PNG\r\n\x1a\n")
            and evidence.get("path") == image.name
            and evidence.get("sha256") == hashlib.sha256(data).hexdigest()
            and isinstance(evidence.get("width"), int)
            and evidence.get("width") > 0
            and isinstance(evidence.get("height"), int)
            and evidence.get("height") > 0
            and isinstance(evidence.get("email_elements_masked"), int)
            and evidence.get("email_elements_masked") >= 0
            and evidence.get("browser_chrome_captured") is False
            and evidence.get("complete_page_url_retained") is False
            and evidence.get("session_identifiers_retained") is False
        )
        if not valid:
            errors.append(f"Invalid {key} PNG receipt in {output.name}")
        rows.append(
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
    return errors, rows


def validate_event(
    event: Mapping[str, Any], output: Path
) -> tuple[list[str], dict[str, Any], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    artifact = load(output)
    metadata = artifact.get("output_metadata")
    results = artifact.get("results")
    if not isinstance(metadata, Mapping) or not isinstance(results, list):
        raise TypeError(f"Malformed source artifact {output}")
    ids = [
        row.get("paperId")
        for row in results
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ]
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("source") != "Web of Science Core Collection"
        or artifact.get("executed_query") != event.get("query")
        or not isinstance(artifact.get("total"), int)
        or artifact.get("total") != len(results)
        or len(ids) != len(results)
        or len(ids) != len(set(ids))
    ):
        errors.append(f"Source result binding changed for {event.get('event_id')}")
    prisma = metadata.get("prisma_search_run")
    staged = prisma.get("staged_counts", {}) if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy", {}) if isinstance(prisma, Mapping) else {}
    native = prisma.get("native_artifact", {}) if isinstance(prisma, Mapping) else {}
    if (
        metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or not isinstance(prisma, Mapping)
        or prisma.get("completion_status") != "complete"
        or prisma.get("report_ready") is not True
        or prisma.get("report_readiness_reasons") != []
        or staged.get("source_reported_total") != artifact.get("total")
        or staged.get("source_reported_total_exact") is not True
        or staged.get("raw_source_records") != len(ids)
        or staged.get("records_exported") != len(ids)
        or native.get("format") != "RIS"
        or native.get("record_count") != len(ids)
    ):
        errors.append(f"Strict completion changed for {event.get('event_id')}")
    scope = strategy.get("search_scope") if isinstance(strategy, Mapping) else None
    scope_controls = scope.get("controls") if isinstance(scope, Mapping) else None
    editions = scope_controls.get("editions") if isinstance(scope_controls, Mapping) else None
    if (
        strategy.get("executed_query") != event.get("query")
        or strategy.get("query_fields") != ["TS", "PY", "LA"]
        or not isinstance(scope, Mapping)
        or scope.get("database") != "Web of Science Core Collection"
        or not isinstance(editions, Mapping)
        or editions.get("state") != "applied"
        or editions.get("requested") != ["All"]
        or not editions.get("effective")
        or strategy.get("sort", {}).get("value") != "Date: oldest first"
        or strategy.get("limits", {}).get("document_types", {}).get("state")
        != "not_applied"
    ):
        errors.append(f"Source controls changed for {event.get('event_id')}")
    if (
        prisma.get("adapter", {}).get("adapter_id") != "search_web_of_science"
        or prisma.get("adapter", {}).get("adapter_version") != "2"
        or prisma.get("phase") != "pilot"
    ):
        errors.append(f"Adapter provenance changed for {event.get('event_id')}")
    screenshot_errors, screenshot_rows = validate_screenshots(
        output, metadata.get("screenshots")
    )
    errors.extend(screenshot_errors)
    records = {
        row["paperId"]: {
            "paper_id": row["paperId"],
            "title": row.get("title", ""),
            "snippet": row.get("snippet", ""),
            "publication_date": row.get("publicationDate", ""),
            "doi": row.get("doi"),
        }
        for row in results
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    }
    return errors, {
        "event_id": event.get("event_id"),
        "partition_id": event.get("partition_id"),
        "variant": event.get("variant"),
        "artifact": str(output.relative_to(PILOT_ROOT)),
        "query_characters": event.get("query_characters"),
        "total": artifact.get("total"),
        "ordered_wos_ids": ids,
        "ordered_wos_ids_sha256": sequence_sha256(ids),
        "screenshots": screenshot_rows,
    }, records


def build(
    root: Path,
    plan_path: Path,
    receipt_path: Path,
    recovery_receipt_path: Path,
) -> dict[str, Any]:
    plan = load(plan_path)
    errors = validate(plan)
    receipt = load(receipt_path)
    recovery = load(recovery_receipt_path)
    initial_validation = load(INITIAL_VALIDATION_RECEIPT)
    outcomes = receipt.get("outcomes", [])
    selected_recovery = recovery.get("selected_artifacts", {})
    if (
        receipt.get("schema_version") != "wos-current-schedule-wildcard-pilot-run/v1"
        or receipt.get("success") is not False
        or receipt.get("planned_event_count") != 18
        or receipt.get("completed_event_count") != 12
        or receipt.get("stopped_after_failure") is not True
        or len(outcomes) != 12
        or any(item.get("valid") is not True for item in outcomes[:-1])
        or outcomes[-1].get("event_id") != "wildcard-BG1"
        or outcomes[-1].get("status") != "error"
        or outcomes[-1].get("total") is not None
    ):
        errors.append("Primary run receipt does not preserve the expected connection failure")
    if (
        recovery.get("schema_version")
        != "wos-current-schedule-wildcard-pilot-recovery-run/v1"
        or recovery.get("success") is not True
        or recovery.get("retry_succeeded") is not True
        or recovery.get("stopped_after_failure") is not False
        or set(selected_recovery)
        != {"wildcard-BG1", "literal-BG2", "wildcard-BG2", "literal-BC1", "wildcard-BC1", "literal-BT2", "wildcard-BT2"}
        or any(item.get("valid") is not True for item in recovery.get("outcomes", []))
    ):
        errors.append("Recovery run receipt is incomplete")
    if (
        initial_validation.get("schema_version")
        != "wos-current-schedule-wildcard-pilot-run/v1"
        or initial_validation.get("completed_event_count") != 1
        or initial_validation.get("outcomes", [{}])[0].get("event_id") != "literal-A1"
        or initial_validation.get("outcomes", [{}])[0].get("exit_code") != 0
        or initial_validation.get("outcomes", [{}])[0].get("status") != "success"
    ):
        errors.append("Initial local validation stop receipt changed")

    event_results: dict[str, dict[str, Any]] = {}
    record_catalog: dict[str, dict[str, Any]] = {}
    all_screenshots: list[dict[str, Any]] = []
    for event in plan.get("events", []):
        recovered = selected_recovery.get(event["event_id"])
        output = (
            root / str(recovered)
            if isinstance(recovered, str)
            else root / "searches" / str(event["output"])
        )
        try:
            event_errors, summary, records = validate_event(event, output)
            errors.extend(event_errors)
            event_results[str(event["event_id"])] = summary
            all_screenshots.extend(summary["screenshots"])
            record_catalog.update(records)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate {event.get('event_id')}: {error}")

    partitions: dict[str, Any] = {}
    for partition_id in SCHEDULE_IDS:
        literal = event_results.get(f"literal-{partition_id}", {})
        wildcard = event_results.get(f"wildcard-{partition_id}", {})
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
            errors.append(f"Wildcard translation lost literal IDs in {partition_id}")

    wildcard_only_ids = sorted(
        {
            identifier
            for value in partitions.values()
            for identifier in value["comparison"]["wildcard_only_wos_ids"]
        }
    )
    wildcard_only_records = [record_catalog[value] for value in wildcard_only_ids]
    if wildcard_only_ids:
        errors.append("Wildcard-only records require a documented population review")
    if len(all_screenshots) != 36 or len({item["file"] for item in all_screenshots}) != 36:
        errors.append("The pilot does not retain 36 unique mandatory screenshots")

    literal_sequences = {
        key: partitions[key]["literal"].get("ordered_wos_ids", []) for key in SCHEDULE_IDS
    }
    wildcard_sequences = {
        key: partitions[key]["wildcard"].get("ordered_wos_ids", []) for key in SCHEDULE_IDS
    }
    literal_main_union = ordered_union([literal_sequences[key] for key in SCHEDULE_IDS])
    wildcard_main_union = ordered_union([wildcard_sequences[key] for key in SCHEDULE_IDS])
    all_equal = all(value["comparison"]["sets_equal"] for value in partitions.values())
    all_supersets = all(
        value["comparison"]["wildcard_is_superset"] for value in partitions.values()
    )
    passed = not errors and all_equal and all_supersets
    return {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Web of Science Core Collection",
        "status": "passed" if passed else "failed",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": PROTOCOL_COMMIT,
        "decisions": {
            "current_no_proximity_schedule": (
                "accepted_for_all_nine_main_partitions" if passed else "unresolved"
            ),
            "population_wildcards": (
                "accepted_and_preferred_for_all_nine_main_partitions"
                if passed
                else "unresolved"
            ),
            "mandatory_screenshots": (
                "accepted_adapter_v2_no_opt_out" if passed else "unresolved"
            ),
            "final_search_authorization": "not_granted_by_this_diagnostic_pilot",
        },
        "wildcard_acceptance": {
            "candidate_count": 10,
            "replaced_literal_count": 22,
            "population_atoms_after_compression": 14,
            "query_character_reduction": 255,
            "all_nine_sets_equal": all_equal,
            "all_literal_ids_retained": all_supersets,
            "wildcard_only_wos_ids": wildcard_only_ids,
            "wildcard_only_records": wildcard_only_records,
            "adopt_for_partitions": list(SCHEDULE_IDS) if passed else [],
        },
        "partition_results": partitions,
        "schedule_reconciliation": {
            "literal_main_union_count": len(literal_main_union),
            "wildcard_main_union_count": len(wildcard_main_union),
            "main_union_sets_equal": set(literal_main_union) == set(wildcard_main_union),
            "literal_main_union_ordered_wos_ids": literal_main_union,
            "wildcard_main_union_ordered_wos_ids": wildcard_main_union,
            "literal_stream_a_union_count": len(
                ordered_union([literal_sequences[key] for key in ("A1", "A2", "A3")])
            ),
            "literal_core_stream_b_union_count": len(
                ordered_union([literal_sequences[key] for key in ("B1", "B2")])
            ),
            "literal_expanded_stream_b_union_count": len(
                ordered_union(
                    [literal_sequences[key] for key in ("BG1", "BG2", "BC1", "BT2")]
                )
            ),
        },
        "retained_failures": [
            {
                "artifact": "searches/events/wildcard-BG1.json",
                "event_id": "wildcard-BG1",
                "attempt": 1,
                "error_stage": "connection",
                "total": None,
                "screenshots_complete": False,
                "recovered_by": selected_recovery.get("wildcard-BG1"),
            },
            {
                "artifact": "searches/run-receipt-initial-local-validation-failure.json",
                "event_id": "literal-A1",
                "source_exit_code": 0,
                "source_status": "success",
                "reason": "superseded local compact-receipt validator expected private fields removed by the shared output compactor",
            },
        ],
        "screenshots": {
            "schema_version": SCREENSHOT_SCHEMA,
            "event_count": len(event_results),
            "required_file_count": 36,
            "verified_file_count": len(all_screenshots),
            "files": all_screenshots,
        },
        "controls": {
            "year": "PY=(2011-2026)",
            "language": "LA=(English)",
            "all_current_editions": True,
            "sort": "Date: oldest first",
            "native_page_size": 50,
            "strict_passes": 2,
            "native_ris": True,
            "proximity": False,
            "pair_expansion": False,
            "publication_type": None,
            "controlled_vocabulary": None,
        },
        "errors": errors,
    }


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument(
        "--recovery-receipt", type=Path, default=DEFAULT_RECOVERY_RECEIPT
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_ASSESSMENT)
    args = parser.parse_args()
    assessment = build(
        args.root, args.plan, args.receipt, args.recovery_receipt
    )
    write_create_only(args.output, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "errors": assessment["errors"],
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0 if assessment["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
