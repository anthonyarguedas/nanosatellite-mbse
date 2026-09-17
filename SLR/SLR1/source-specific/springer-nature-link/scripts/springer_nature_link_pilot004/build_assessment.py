#!/usr/bin/env python3
"""Validate and assess Springer Pilot 004 schedule and wildcard evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from build_plan import PILOT_ROOT, SNAPSHOT_RETEST_SCHEMA, YEAR_PARTITION_SCHEMA
from queries import SCHEDULE_IDS

SCHEMA = "springer-nature-link-pilot004-assessment/v1"
DEFAULT_PLAN = PILOT_ROOT / "searches" / "event-plan-v4.json"
DEFAULT_RETEST_PLAN = PILOT_ROOT / "searches" / "snapshot-retest-plan.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "assessment.json"
DEFAULT_SMOKE = (
    PILOT_ROOT
    / "searches"
    / "adapter-smoke"
    / "automatic-screenshot-smoke.NON_MERGEABLE_DIAGNOSTIC.json"
)
DEFAULT_INVESTIGATION = PILOT_ROOT / "searches" / "wildcard-only-investigation.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def ordered_union(sequences: list[list[str]]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for sequence in sequences:
        for value in sequence:
            if value not in seen:
                seen.add(value)
                output.append(value)
    return output


def validate_screenshots(
    output: Path,
    screenshots: Any,
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    receipts: list[dict[str, Any]] = []
    if not isinstance(screenshots, Mapping):
        return [f"Missing screenshot receipt in {output.name}"], receipts
    if (
        screenshots.get("schema_version") != "springer-automatic-screenshots/v1"
        or screenshots.get("automatic") is not True
        or screenshots.get("no_opt_out") is not True
    ):
        errors.append(f"Screenshot contract changed in {output.name}")
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        evidence = screenshots.get(key)
        if not isinstance(evidence, Mapping):
            errors.append(f"Missing {key} receipt in {output.name}")
            continue
        expected_name = output.name.removesuffix(".json") + suffix
        path = output.with_name(expected_name)
        if evidence.get("path") != expected_name or path.parent != output.parent:
            errors.append(f"{key} is not beside {output.name}")
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            errors.append(f"Could not read {path}: {error}")
            continue
        if (
            not data.startswith(b"\x89PNG\r\n\x1a\n")
            or evidence.get("sha256") != hashlib.sha256(data).hexdigest()
            or not isinstance(evidence.get("width"), int)
            or evidence.get("width") < 1
            or not isinstance(evidence.get("height"), int)
            or evidence.get("height") < 1
            or evidence.get("browser_chrome_captured") is not False
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            errors.append(f"Invalid {key} PNG receipt in {output.name}")
        receipts.append(
            {
                "json": str(output.relative_to(PILOT_ROOT)),
                "kind": key,
                "file_name": expected_name,
                "sha256": evidence.get("sha256"),
                "width": evidence.get("width"),
                "height": evidence.get("height"),
            }
        )
    return errors, receipts


def validate_event(
    event: Mapping[str, Any],
    output: Path,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    artifact = load(output)
    metadata = artifact.get("output_metadata")
    ids = artifact.get("ordered_source_ids")
    diagnostic_ids = artifact.get("diagnostic_window_ordered_source_ids")
    passes = artifact.get("passes")
    if (
        artifact.get("schema_version")
        != "springer-nature-link-pilot004-source-event/v1"
        or artifact.get("event_id") != event.get("event_id")
        or artifact.get("variant") != event.get("variant")
        or artifact.get("partition_id") != event.get("partition_id")
        or artifact.get("query") != event.get("query")
        or artifact.get("query_sha256") != event.get("query_sha256")
        or artifact.get("query_characters") != event.get("query_characters")
    ):
        errors.append(f"Plan binding changed for {event.get('event_id')}")
    if (
        artifact.get("status") != "success"
        or artifact.get("diagnostic_only") is not True
        or artifact.get("do_not_merge") is not True
        or artifact.get("merge_eligible") is not False
        or not isinstance(metadata, Mapping)
        or metadata.get("retrieval_complete") is not True
        or metadata.get("source_total_reconciled") is not True
        or metadata.get("passes_completed") != 2
        or metadata.get("proximity_operator") is not None
        or metadata.get("pair_expansion") is not False
        or metadata.get("language_filter") != "En"
        or metadata.get("content_type_filter") is not None
        or metadata.get("access_filter") is not None
        or metadata.get("controlled_vocabulary_supplement") is not None
        or metadata.get("taxonomy_filter") is not None
    ):
        errors.append(f"Completion or controls changed for {event.get('event_id')}")
    if (
        not isinstance(ids, list)
        or len(ids) != len(set(ids))
        or artifact.get("source_total") != len(ids)
        or artifact.get("ordered_source_ids_sha256") != sequence_sha256(ids or [])
        or not isinstance(diagnostic_ids, list)
        or not set(diagnostic_ids).issubset(ids or [])
        or artifact.get("diagnostic_window_ordered_source_ids_sha256")
        != sequence_sha256(diagnostic_ids or [])
    ):
        errors.append(f"Stable card-path ledger changed for {event.get('event_id')}")
    if (
        not isinstance(passes, list)
        or len(passes) != 2
        or any(
            item.get("source_total") != artifact.get("source_total") for item in passes
        )
        or any(
            item.get("ordered_card_paths_sha256")
            != artifact.get("ordered_source_ids_sha256")
            for item in passes
        )
        or passes[0].get("date_group_sha256") != passes[1].get("date_group_sha256")
    ):
        errors.append(f"Two-pass reconciliation changed for {event.get('event_id')}")
    screenshot_errors, screenshot_receipts = validate_screenshots(
        output,
        metadata.get("screenshots") if isinstance(metadata, Mapping) else None,
    )
    errors.extend(screenshot_errors)
    return errors, {
        "event_id": event.get("event_id"),
        "variant": event.get("variant"),
        "partition_id": event.get("partition_id"),
        "cell_id": artifact.get("cell_id"),
        "source_year_start": metadata.get("source_year_start")
        if isinstance(metadata, Mapping)
        else None,
        "source_total": artifact.get("source_total"),
        "ordered_source_ids": ids,
        "diagnostic_window_ordered_source_ids": diagnostic_ids,
        "records": artifact.get("records", []),
        "screenshots": screenshot_receipts,
    }


def selected_events(
    plan: Mapping[str, Any],
    retest_plan: Mapping[str, Any],
    partition_id: str,
    variant: str,
) -> list[Mapping[str, Any]]:
    base = [
        event
        for event in plan["events"]
        if event["partition_id"] == partition_id and event["variant"] == variant
    ]
    retests = [
        event
        for event in retest_plan["events"]
        if event["partition_id"] == partition_id and event["variant"] == variant
    ]
    if partition_id in {"A3", "BT2"}:
        return retests
    if partition_id == "B2":
        return [
            event
            for event in base
            if event.get("source_year_start") not in {2025, 2026}
        ] + retests
    return base


def build(
    root: Path,
    plan_path: Path,
    retest_plan_path: Path,
    smoke_path: Path,
    investigation_path: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    plan = load(plan_path)
    retest_plan = load(retest_plan_path)
    if (
        plan.get("schema_version") != YEAR_PARTITION_SCHEMA
        or plan.get("event_count") != 74
    ):
        errors.append("Main event plan is invalid")
    if (
        retest_plan.get("schema_version") != SNAPSHOT_RETEST_SCHEMA
        or retest_plan.get("event_count") != 8
    ):
        errors.append("Snapshot retest plan is invalid")
    for receipt_name, expected in (
        ("run-receipt.json", 74),
        ("snapshot-retest-run-receipt.json", 8),
    ):
        receipt = load(root / "searches" / receipt_name)
        if (
            receipt.get("status") != "complete"
            or receipt.get("predeclared_event_count") != expected
            or receipt.get("completed_event_count") != expected
        ):
            errors.append(f"{receipt_name} is incomplete")

    summaries: dict[str, dict[str, Any]] = {}
    screenshot_receipts: list[dict[str, Any]] = []
    record_catalog: dict[str, dict[str, Any]] = {}
    all_events = [*plan["events"], *retest_plan["events"]]
    for event in all_events:
        output = root / "searches" / event["output"]
        try:
            event_errors, summary = validate_event(event, output)
            errors.extend(event_errors)
            summaries[event["event_id"]] = summary
            screenshot_receipts.extend(summary["screenshots"])
            for record in summary["records"]:
                if isinstance(record, Mapping) and isinstance(
                    record.get("source_id"), str
                ):
                    record_catalog.setdefault(record["source_id"], dict(record))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate {event.get('event_id')}: {error}")

    partition_results: dict[str, Any] = {}
    all_wildcard_only: set[str] = set()
    all_literal_missing: set[str] = set()
    for partition_id in SCHEDULE_IDS:
        variants: dict[str, Any] = {}
        for variant in ("literal", "wildcard"):
            events = selected_events(plan, retest_plan, partition_id, variant)
            event_summaries = [summaries.get(event["event_id"], {}) for event in events]
            ids = ordered_union(
                [item.get("ordered_source_ids", []) for item in event_summaries]
            )
            diagnostic_ids = ordered_union(
                [
                    item.get("diagnostic_window_ordered_source_ids", [])
                    for item in event_summaries
                ]
            )
            totals = [item.get("source_total") for item in event_summaries]
            variants[variant] = {
                "source_cell_count": len(events),
                "source_cell_totals": totals,
                "source_cell_total_sum": sum(
                    value for value in totals if isinstance(value, int)
                ),
                "source_union_count": len(ids),
                "ordered_source_ids": ids,
                "ordered_source_ids_sha256": sequence_sha256(ids),
                "diagnostic_window_union_count": len(diagnostic_ids),
                "diagnostic_window_ordered_source_ids": diagnostic_ids,
                "diagnostic_window_ordered_source_ids_sha256": sequence_sha256(
                    diagnostic_ids
                ),
                "selected_event_ids": [event["event_id"] for event in events],
            }
        literal_ids = variants["literal"]["ordered_source_ids"]
        wildcard_ids = variants["wildcard"]["ordered_source_ids"]
        missing = sorted(set(literal_ids) - set(wildcard_ids))
        wildcard_only = sorted(set(wildcard_ids) - set(literal_ids))
        all_literal_missing.update(missing)
        all_wildcard_only.update(wildcard_only)
        partition_results[partition_id] = {
            **variants,
            "comparison": {
                "literal_missing_from_wildcard": missing,
                "wildcard_only_source_ids": wildcard_only,
                "source_sets_equal": set(literal_ids) == set(wildcard_ids),
                "wildcard_is_source_superset": set(literal_ids).issubset(wildcard_ids),
                "diagnostic_window_wildcard_is_superset": set(
                    variants["literal"]["diagnostic_window_ordered_source_ids"]
                ).issubset(
                    variants["wildcard"]["diagnostic_window_ordered_source_ids"]
                ),
            },
        }

    investigation = load(investigation_path)
    finding_by_path = {
        item["source_card_path"]: item
        for item in investigation.get("findings", [])
        if isinstance(item, Mapping) and isinstance(item.get("source_card_path"), str)
    }
    wildcard_only_findings = []
    for source_id in sorted(all_wildcard_only):
        finding = finding_by_path.get(source_id)
        if finding is None:
            errors.append(f"Wildcard-only path lacks investigation: {source_id}")
            continue
        wildcard_only_findings.append(finding)
        if finding.get("within_intended_population_meaning") is not True:
            errors.append(f"Wildcard-only path left population meaning: {source_id}")
    if all_literal_missing:
        errors.append(
            "At least one literal card path is missing from the wildcard union"
        )

    smoke = load(smoke_path)
    smoke_metadata = smoke.get("output_metadata")
    smoke_errors, smoke_screenshots = validate_screenshots(
        smoke_path.with_name("automatic-screenshot-smoke.json"),
        smoke_metadata.get("screenshots")
        if isinstance(smoke_metadata, Mapping)
        else None,
    )
    errors.extend(smoke_errors)
    adapter_receipt = (
        smoke_metadata.get("prisma_search_run", {}).get("adapter", {})
        if isinstance(smoke_metadata, Mapping)
        else {}
    )
    if (
        smoke.get("total") != 1
        or smoke.get("do_not_merge") is not True
        or not isinstance(smoke_metadata, Mapping)
        or smoke_metadata.get("count_only") is not True
        or smoke_metadata.get("merge_eligible") is not False
        or adapter_receipt.get("adapter_version") != "10"
    ):
        errors.append("Adapter CLI screenshot smoke changed")
    screenshot_receipts.extend(smoke_screenshots)

    failures = sorted((root / "searches" / "failures").glob("*.json"))
    failure_summaries = []
    for path in failures:
        failure = load(path)
        failure_summaries.append(
            {
                "artifact": str(path.relative_to(root)),
                "event_id": failure.get("event_id"),
                "attempt": failure.get("attempt"),
                "error_type": failure.get("error_type"),
                "error": failure.get("error"),
                "source_total": failure.get("source_total"),
            }
        )

    accepted = not errors
    strict_detail_failures = sorted(
        item["source_card_path"]
        for item in wildcard_only_findings
        if item.get("adapter_strict_detail_acceptance") is not True
    )
    return {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Springer Nature Link",
        "status": "complete" if accepted else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": plan.get("protocol_commit"),
        "decisions": {
            "current_schedule_translation": (
                "accepted_with_five_cell_A2_and_twenty_five_cell_B2_unions"
                if accepted
                else "unresolved"
            ),
            "wildcard_population_translation": (
                "accepted_and_preferred_for_all_nine_partitions"
                if accepted
                else "unresolved"
            ),
            "wildcard_basis": (
                "Every complete wildcard partition was a stable-card-path superset "
                "of its literal comparison. Six sets were equal. The two unique "
                "wildcard-only paths remained within the intended population meaning."
            ),
            "mandatory_screenshots": (
                "accepted_adapter_v10_no_opt_out" if accepted else "unresolved"
            ),
            "strict_detail_route": (
                "follow_up_required_for_external_nature_canonical_link"
                if strict_detail_failures
                else "no_new_limitation"
            ),
            "final_search_status": (
                "not_ready_due_to_strict_detail_route_and_exact_day_boundaries"
            ),
        },
        "partition_results": partition_results,
        "wildcard_acceptance": {
            "all_nine_wildcard_supersets": all(
                item["comparison"]["wildcard_is_source_superset"]
                for item in partition_results.values()
            ),
            "all_nine_diagnostic_window_wildcard_supersets": all(
                item["comparison"]["diagnostic_window_wildcard_is_superset"]
                for item in partition_results.values()
            ),
            "literal_missing_source_ids": sorted(all_literal_missing),
            "wildcard_only_source_ids": sorted(all_wildcard_only),
            "wildcard_only_record_count": len(all_wildcard_only),
            "wildcard_only_findings": wildcard_only_findings,
            "adopt_for_partitions": list(SCHEDULE_IDS) if accepted else [],
        },
        "compression": {
            "literal_population_terms": 26,
            "wildcard_population_atoms": 21,
            "characters_saved_per_source_cell": 85,
            "accepted_wildcard_atoms": ["CubeSat*", "nanosat*", "SmallSat*"],
        },
        "source_cell_plan": {
            "A2": ("P AND E_F AND M_H plus four fixed contiguous M_B term cells"),
            "B2": (
                "one complete query per source year, with a fixed two-by-two "
                "M_B/R Boolean union for 2021, 2022, and 2024"
            ),
            "other_partitions": "one direct query each",
            "lossless": True,
        },
        "screenshots": {
            "successful_schedule_event_json_count": len(all_events),
            "successful_schedule_png_count": len(all_events) * 2,
            "adapter_smoke_png_count": len(smoke_screenshots),
            "total_validated_png_count": len(screenshot_receipts),
            "all_sibling_paths": len(screenshot_receipts) == len(all_events) * 2 + 2,
            "receipts": screenshot_receipts,
        },
        "adapter_smoke": {
            "artifact": str(smoke_path.relative_to(root)),
            "query": smoke.get("executed_query"),
            "total": smoke.get("total"),
            "adapter_version": adapter_receipt.get("adapter_version"),
        },
        "detail_route_limitation": {
            "strict_adapter_failure_source_ids": strict_detail_failures,
            "finding": (
                "The Link article route for the Nature Reviews Clean Technology "
                "wildcard-only record exposes a www.nature.com canonical link. Adapter "
                "version 10 correctly rejects it under the current same-route detail "
                "contract. A separate repair pilot is required before final execution."
                if strict_detail_failures
                else None
            ),
        },
        "retained_failure_attempts": failure_summaries,
        "retained_failure_count": len(failure_summaries),
        "failure_interpretation": (
            "Nine null attempts established the superseded direct A2, A2 M_B, and "
            "direct B2 route failures. Nine transient page, screenshot, or browser "
            "attempts later completed unchanged. Failed attempts contributed no IDs "
            "or totals."
        ),
        "record_catalog_count": len(record_catalog),
        "plans": {
            "main": {
                "artifact": str(plan_path.relative_to(root)),
                "sha256": file_sha256(plan_path),
                "event_count": len(plan.get("events", [])),
            },
            "retest": {
                "artifact": str(retest_plan_path.relative_to(root)),
                "sha256": file_sha256(retest_plan_path),
                "event_count": len(retest_plan.get("events", [])),
            },
            "investigation": {
                "artifact": str(investigation_path.relative_to(root)),
                "sha256": file_sha256(investigation_path),
            },
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--retest-plan", type=Path, default=DEFAULT_RETEST_PLAN)
    parser.add_argument("--smoke", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--investigation", type=Path, default=DEFAULT_INVESTIGATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    assessment = build(
        args.pilot_root,
        args.plan,
        args.retest_plan,
        args.smoke,
        args.investigation,
    )
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"status": assessment["status"], "errors": assessment["errors"]}, indent=2
        )
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
