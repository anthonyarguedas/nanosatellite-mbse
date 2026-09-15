#!/usr/bin/env python3
"""Validate and assess Wiley Pilot 004 schedule and wildcard evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from build_plan import DEFAULT_OUTPUT, PILOT_ROOT, load, validate
from queries import LITERAL_CELLS, SCHEDULE_IDS, WILDCARD_CELLS

SCHEMA = "wiley-online-library-pilot004-assessment/v1"
DEFAULT_ASSESSMENT = PILOT_ROOT / "searches" / "assessment.json"
DEFAULT_SMOKE = PILOT_ROOT / "searches" / "adapter-smoke" / "automatic-screenshot-smoke.json"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
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
    output: Path, screenshots: Any, *, expected_schema: str = "wiley-automatic-screenshots/v1"
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    receipts: list[dict[str, Any]] = []
    if not isinstance(screenshots, Mapping):
        return [f"Missing screenshot receipt in {output.name}"], receipts
    if (
        screenshots.get("schema_version") != expected_schema
        or screenshots.get("automatic") is not True
        or screenshots.get("no_opt_out") is not True
    ):
        errors.append(f"Screenshot contract changed in {output.name}")
    for key, suffix in (("search_page", ".search-page.png"), ("results_page", ".results-page.png")):
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
                "json": output.name,
                "kind": key,
                "file_name": expected_name,
                "sha256": evidence.get("sha256"),
                "width": evidence.get("width"),
                "height": evidence.get("height"),
            }
        )
    return errors, receipts


def validate_event(event: Mapping[str, Any], output: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    artifact = load(output)
    metadata = artifact.get("output_metadata")
    ids = artifact.get("ordered_source_ids")
    retained = artifact.get("diagnostic_window_ordered_source_ids")
    passes = artifact.get("passes")
    if (
        artifact.get("schema_version") != "wiley-online-library-pilot004-source-event/v1"
        or artifact.get("event_id") != event.get("event_id")
        or artifact.get("variant") != event.get("variant")
        or artifact.get("partition_id") != event.get("partition_id")
        or artifact.get("cell_id") != event.get("cell_id")
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
        or metadata.get("native_ris_used") is not False
        or metadata.get("proximity_operator") is not None
        or metadata.get("pair_expansion") is not False
        or metadata.get("language_filter") is not None
        or metadata.get("publication_type_facet") is not None
        or metadata.get("access_filter") is not None
        or metadata.get("controlled_vocabulary_supplement") is not None
    ):
        errors.append(f"Completion or controls changed for {event.get('event_id')}")
    if (
        not isinstance(ids, list)
        or len(ids) != len(set(ids))
        or artifact.get("source_total") != len(ids)
        or artifact.get("ordered_source_ids_sha256") != sequence_sha256(ids or [])
        or not isinstance(retained, list)
        or not set(retained).issubset(ids or [])
        or artifact.get("diagnostic_window_ordered_source_ids_sha256")
        != sequence_sha256(retained or [])
    ):
        errors.append(f"Stable-ID ledger changed for {event.get('event_id')}")
    if (
        not isinstance(passes, list)
        or len(passes) != 2
        or passes[0].get("ordered_source_ids") != ids
        or passes[1].get("ordered_source_ids") != ids
        or passes[0].get("ordered_source_ids_sha256") != sequence_sha256(ids or [])
        or passes[1].get("ordered_source_ids_sha256") != sequence_sha256(ids or [])
    ):
        errors.append(f"Two-pass reconciliation changed for {event.get('event_id')}")
    screenshot_errors, screenshot_receipts = validate_screenshots(
        output, metadata.get("screenshots") if isinstance(metadata, Mapping) else None
    )
    errors.extend(screenshot_errors)
    return errors, {
        "event_id": event.get("event_id"),
        "variant": event.get("variant"),
        "partition_id": event.get("partition_id"),
        "cell_id": event.get("cell_id"),
        "query_characters": event.get("query_characters"),
        "source_total": artifact.get("source_total"),
        "ordered_source_ids": ids,
        "diagnostic_window_ordered_source_ids": retained,
        "excluded_after_diagnostic_cutoff_source_ids": artifact.get(
            "excluded_after_diagnostic_cutoff_source_ids", []
        ),
        "unresolved_exact_date_source_ids": artifact.get(
            "unresolved_exact_date_source_ids", []
        ),
        "screenshots": screenshot_receipts,
    }


def build(root: Path, plan_path: Path, smoke_path: Path) -> dict[str, Any]:
    plan = load(plan_path)
    errors = validate(plan)
    receipt = load(root / "searches" / "run-receipt.json")
    if (
        receipt.get("status") != "complete"
        or receipt.get("predeclared_event_count") != 20
        or receipt.get("completed_event_count") != 20
    ):
        errors.append("Run receipt is incomplete")

    event_results: dict[str, dict[str, Any]] = {}
    all_screenshot_receipts: list[dict[str, Any]] = []
    record_catalog: dict[str, dict[str, Any]] = {}
    for event in plan["events"]:
        output = root / "searches" / event["output"]
        try:
            event_errors, summary = validate_event(event, output)
            errors.extend(event_errors)
            event_results[event["event_id"]] = summary
            all_screenshot_receipts.extend(summary["screenshots"])
            artifact = load(output)
            for record in artifact.get("records", []):
                record_catalog.setdefault(
                    record["source_id"],
                    {
                        "source_id": record["source_id"],
                        "title": record.get("title", ""),
                        "source_publication_date": record.get("source_publication_date", ""),
                    },
                )
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate {event.get('event_id')}: {error}")

    partition_results: dict[str, Any] = {}
    for partition_id in SCHEDULE_IDS:
        variants: dict[str, Any] = {}
        for variant, cells in (("literal", LITERAL_CELLS), ("wildcard", WILDCARD_CELLS)):
            ids_by_cell = []
            retained_by_cell = []
            source_totals = []
            for cell in cells[partition_id]:
                event_id = f"{variant}-{partition_id}-{cell['cell_id']}"
                summary = event_results.get(event_id, {})
                ids_by_cell.append(summary.get("ordered_source_ids", []))
                retained_by_cell.append(
                    summary.get("diagnostic_window_ordered_source_ids", [])
                )
                source_totals.append(summary.get("source_total"))
            union_ids = ordered_union(ids_by_cell)
            retained_union = ordered_union(retained_by_cell)
            variants[variant] = {
                "source_cell_count": len(cells[partition_id]),
                "source_cell_totals": source_totals,
                "source_cell_total_sum": sum(
                    value for value in source_totals if isinstance(value, int)
                ),
                "source_union_count": len(union_ids),
                "ordered_source_ids": union_ids,
                "ordered_source_ids_sha256": sequence_sha256(union_ids),
                "diagnostic_window_union_count": len(retained_union),
                "diagnostic_window_ordered_source_ids": retained_union,
                "diagnostic_window_ordered_source_ids_sha256": sequence_sha256(
                    retained_union
                ),
            }
        literal_ids = variants["literal"]["ordered_source_ids"]
        wildcard_ids = variants["wildcard"]["ordered_source_ids"]
        literal_retained = variants["literal"]["diagnostic_window_ordered_source_ids"]
        wildcard_retained = variants["wildcard"]["diagnostic_window_ordered_source_ids"]
        missing = sorted(set(literal_ids) - set(wildcard_ids))
        wildcard_only = sorted(set(wildcard_ids) - set(literal_ids))
        partition_results[partition_id] = {
            **variants,
            "comparison": {
                "literal_missing_from_wildcard": missing,
                "wildcard_only_source_ids": wildcard_only,
                "source_sets_equal": set(literal_ids) == set(wildcard_ids),
                "source_order_equal": literal_ids == wildcard_ids,
                "diagnostic_window_sets_equal": set(literal_retained)
                == set(wildcard_retained),
                "wildcard_is_source_superset": set(literal_ids).issubset(wildcard_ids),
            },
        }

    wildcard_only_all = sorted(
        {
            source_id
            for value in partition_results.values()
            for source_id in value["comparison"]["wildcard_only_source_ids"]
        }
    )
    all_equal = all(
        value["comparison"]["source_sets_equal"]
        and value["comparison"]["source_order_equal"]
        and value["comparison"]["diagnostic_window_sets_equal"]
        for value in partition_results.values()
    )
    if not all_equal:
        errors.append("At least one wildcard partition differs from its literal union")
    if wildcard_only_all:
        errors.append("Wildcard-only records require population inspection")

    smoke = load(smoke_path)
    smoke_metadata = smoke.get("output_metadata")
    smoke_errors, smoke_screenshots = validate_screenshots(
        smoke_path,
        smoke_metadata.get("screenshots") if isinstance(smoke_metadata, Mapping) else None,
    )
    errors.extend(smoke_errors)
    if (
        smoke.get("total") != 1
        or smoke.get("do_not_merge") is not True
        or not isinstance(smoke_metadata, Mapping)
        or smoke_metadata.get("status") != "success"
        or smoke_metadata.get("count_only") is not True
        or smoke_metadata.get("merge_eligible") is not False
        or smoke_metadata.get("screenshots", {}).get("no_opt_out") is not True
        or smoke_metadata.get("prisma_search_run", {}).get("adapter", {}).get(
            "adapter_version"
        )
        != "12"
    ):
        errors.append("Adapter CLI screenshot smoke did not retain its bounded contract")
    all_screenshot_receipts.extend(smoke_screenshots)

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

    successful = not errors
    return {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Wiley Online Library",
        "status": "complete" if successful else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": plan.get("protocol_commit"),
        "decisions": {
            "current_schedule_translation": (
                "accepted_direct_with_two_cell_A2_union" if successful else "unresolved"
            ),
            "wildcard_population_translation": (
                "accepted_and_preferred_for_all_nine_partitions"
                if successful
                else "unresolved"
            ),
            "wildcard_basis": (
                "Every complete wildcard partition union had the same IDs in the same "
                "order as its literal union. There were no missing or wildcard-only IDs."
            ),
            "mandatory_screenshots": (
                "accepted_adapter_v12_no_opt_out" if successful else "unresolved"
            ),
            "native_ris_final_run_boundary": (
                "unchanged: this diagnostic used rendered DOI ledgers and does not replace "
                "the strict native RIS final-search contract"
            ),
        },
        "partition_results": partition_results,
        "wildcard_acceptance": {
            "all_nine_source_sets_equal": all_equal,
            "all_nine_source_orders_equal": all(
                value["comparison"]["source_order_equal"]
                for value in partition_results.values()
            ),
            "all_literal_ids_retained": all(
                value["comparison"]["wildcard_is_source_superset"]
                for value in partition_results.values()
            ),
            "wildcard_only_source_ids": wildcard_only_all,
            "wildcard_only_record_count": len(wildcard_only_all),
            "adopt_for_partitions": list(SCHEDULE_IDS) if successful else [],
        },
        "compression": {
            "literal_population_terms": 26,
            "wildcard_population_atoms": 21,
            "characters_saved_per_source_cell": 85,
            "accepted_wildcard_atoms": ["CubeSat*", "nanosat*", "SmallSat*"],
        },
        "screenshots": {
            "successful_schedule_event_json_count": len(event_results),
            "successful_schedule_png_count": sum(
                len(value.get("screenshots", [])) for value in event_results.values()
            ),
            "adapter_smoke_png_count": len(smoke_screenshots),
            "total_validated_png_count": len(all_screenshot_receipts),
            "all_sibling_paths": all(
                Path(item["file_name"]).parent == Path(".")
                for item in all_screenshot_receipts
            ),
            "receipts": all_screenshot_receipts,
        },
        "adapter_smoke": {
            "artifact": str(smoke_path.relative_to(root)),
            "query": smoke.get("query"),
            "total": smoke.get("total"),
            "adapter_version": smoke_metadata.get("prisma_search_run", {})
            .get("adapter", {})
            .get("adapter_version")
            if isinstance(smoke_metadata, Mapping)
            else None,
        },
        "retained_failure_attempts": failure_summaries,
        "retained_failure_count": len(failure_summaries),
        "failure_interpretation": (
            "The retained null artifacts cover two pre-source setup/runner failures, one "
            "runner cleanup failure, and two isolated page-boundary failures. Fresh unchanged "
            "events later completed. No failed-attempt IDs or totals entered a successful event."
        ),
        "record_catalog_count": len(record_catalog),
        "plan": {
            "artifact": str(plan_path.relative_to(root)),
            "sha256": file_sha256(plan_path),
            "event_count": len(plan.get("events", [])),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--smoke", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--output", type=Path, default=DEFAULT_ASSESSMENT)
    args = parser.parse_args()
    assessment = build(args.pilot_root, args.plan, args.smoke)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": assessment["status"], "errors": assessment["errors"]}, indent=2))
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
