#!/usr/bin/env python3
"""Build the Wiley Pilot 005 native RIS readiness assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from build_plan import DEFAULT_OUTPUT, EVENT_SCHEMA, PILOT_ROOT, load, validate

SCHEMA = "wiley-online-library-pilot005-assessment/v1"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
DEFAULT_ASSESSMENT = PILOT_ROOT / "searches" / "assessment.json"


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
    output: Path, screenshots: Any
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    receipts: list[dict[str, Any]] = []
    if not isinstance(screenshots, Mapping) or not (
        screenshots.get("schema_version") == "wiley-automatic-screenshots/v1"
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
    ):
        return [f"Screenshot contract changed in {output.name}"], receipts
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        evidence = screenshots.get(key)
        expected_name = output.name.removesuffix(".json") + suffix
        path = output.with_name(expected_name)
        if not isinstance(evidence, Mapping):
            errors.append(f"Missing {key} receipt in {output.name}")
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            errors.append(f"Could not read {path}: {error}")
            continue
        if not (
            evidence.get("path") == expected_name
            and path.parent == output.parent
            and data.startswith(b"\x89PNG\r\n\x1a\n")
            and evidence.get("sha256") == hashlib.sha256(data).hexdigest()
            and isinstance(evidence.get("width"), int)
            and evidence.get("width") > 0
            and isinstance(evidence.get("height"), int)
            and evidence.get("height") > 0
            and evidence.get("browser_chrome_captured") is False
            and evidence.get("complete_page_url_retained") is False
            and evidence.get("session_identifiers_retained") is False
        ):
            errors.append(f"Invalid {key} PNG receipt in {output.name}")
        receipts.append(
            {
                "event_json": output.name,
                "kind": key,
                "file_name": expected_name,
                "sha256": evidence.get("sha256"),
                "width": evidence.get("width"),
                "height": evidence.get("height"),
            }
        )
    return errors, receipts


def validate_event(
    event: Mapping[str, Any], output: Path
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    artifact = load(output)
    metadata = artifact.get("output_metadata")
    ids = artifact.get("ordered_source_ids")
    records = artifact.get("records")
    passes = artifact.get("passes")
    native = artifact.get("native_ris_reconciliation")
    dates = artifact.get("exact_date_accounting")
    if not (
        artifact.get("schema_version") == EVENT_SCHEMA
        and artifact.get("event_id") == event.get("event_id")
        and artifact.get("partition_id") == event.get("partition_id")
        and artifact.get("cell_id") == event.get("cell_id")
        and artifact.get("query") == event.get("query")
        and artifact.get("query_sha256") == event.get("query_sha256")
        and artifact.get("query_characters") == event.get("query_characters")
    ):
        errors.append(f"Plan binding changed for {event.get('event_id')}")
    if not (
        artifact.get("status") == "success"
        and artifact.get("diagnostic_only") is True
        and artifact.get("do_not_merge") is True
        and artifact.get("merge_eligible") is False
        and isinstance(metadata, Mapping)
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("stopped_reason") == "all_available_records"
        and metadata.get("passes_completed") == 2
        and metadata.get("source_entries_retrieved") == artifact.get("source_total")
        and metadata.get("export_method")
        == "visible_page_scoped_normal_ui_ris_with_abstracts"
        and metadata.get("diagnostic_only") is True
        and metadata.get("merge_eligible") is False
        and metadata.get("raw_native_ris_persisted") is False
        and metadata.get("language_filter") is None
        and metadata.get("publication_type_filter") is None
        and metadata.get("open_access_filter") is False
        and metadata.get("subject_facet_ids") == []
    ):
        errors.append(f"Completion or controls changed for {event.get('event_id')}")
    if not (
        isinstance(ids, list)
        and len(ids) == len(set(ids))
        and artifact.get("source_total") == len(ids)
        and artifact.get("ordered_source_ids_sha256") == sequence_sha256(ids)
        and isinstance(records, list)
    ):
        errors.append(f"Complete DOI ledger changed for {event.get('event_id')}")
        ids = ids if isinstance(ids, list) else []
        records = records if isinstance(records, list) else []
    if not (
        isinstance(passes, list)
        and len(passes) == 2
        and all(
            isinstance(report, Mapping)
            and report.get("pass_number") == number
            and report.get("ordered_ids_sha256") == sequence_sha256(ids)
            for number, report in enumerate(passes, start=1)
        )
        and all(
            sum(page.get("rendered_cards", 0) for page in report.get("pages", []))
            == len(ids)
            for report in passes
        )
    ):
        errors.append(
            f"Two-pass DOI reconciliation changed for {event.get('event_id')}"
        )
    if not (
        isinstance(native, Mapping)
        and native.get("route") == "visible page scoped native RIS with abstracts"
        and native.get("raw_ris_persisted") is False
        and native.get("source_total") == len(ids)
        and native.get("source_entries_retrieved") == len(ids)
        and native.get("normalized_record_count_before_date_exclusions") == len(ids)
        and native.get("every_batch_count_reconciled") is True
        and native.get("every_batch_ris_markers_reconciled") is True
        and native.get("every_source_doi_normalized_from_native_ris") is True
        and native.get("normalized_retained_doi_order_matches_source_ledger") is True
        and isinstance(native.get("download_count"), int)
        and native.get("download_count") > 0
        and len(native.get("download_record_counts", []))
        == native.get("download_count")
        and len(native.get("download_byte_counts", [])) == native.get("download_count")
        and len(native.get("download_sha256", [])) == native.get("download_count")
    ):
        errors.append(f"Native RIS reconciliation changed for {event.get('event_id')}")
    if not (
        isinstance(dates, Mapping)
        and dates.get("basis") == "Wiley visible First published"
        and dates.get("source_month_total") == len(ids)
        and dates.get("every_source_id_accounted_for") is True
        and dates.get("included_count", 0)
        + dates.get("excluded_count", 0)
        + dates.get("unresolved_count", 0)
        == len(ids)
        and len(dates.get("included_source_ids", [])) == dates.get("included_count")
        and len(dates.get("excluded_source_ids", [])) == dates.get("excluded_count")
        and len(dates.get("unresolved_source_ids", [])) == dates.get("unresolved_count")
    ):
        errors.append(f"Exact-date accounting changed for {event.get('event_id')}")
    screenshot_errors, screenshot_receipts = validate_screenshots(
        output, metadata.get("screenshots") if isinstance(metadata, Mapping) else None
    )
    errors.extend(screenshot_errors)
    return errors, {
        "event_id": event.get("event_id"),
        "partition_id": event.get("partition_id"),
        "cell_id": event.get("cell_id"),
        "source_total": artifact.get("source_total"),
        "pilot004_reference_total": artifact.get("pilot004_reference_total"),
        "source_total_change_from_pilot004": artifact.get(
            "source_total_change_from_pilot004"
        ),
        "pages_per_pass": metadata.get("pages_per_pass")
        if isinstance(metadata, Mapping)
        else None,
        "ordered_source_ids": ids,
        "ordered_source_ids_sha256": artifact.get("ordered_source_ids_sha256"),
        "native_ris_download_count": native.get("download_count")
        if isinstance(native, Mapping)
        else None,
        "native_ris_download_bytes": sum(native.get("download_byte_counts", []))
        if isinstance(native, Mapping)
        else None,
        "retained_record_count": len(records),
        "exact_date_accounting": dict(dates) if isinstance(dates, Mapping) else dates,
        "screenshots": screenshot_receipts,
        "artifact": str(output.relative_to(PILOT_ROOT)),
        "sha256": file_sha256(output),
    }


def build(root: Path, plan_path: Path, receipt_path: Path) -> dict[str, Any]:
    plan = load(plan_path)
    errors = validate(plan)
    receipt = load(receipt_path)
    if not (
        receipt.get("schema_version") == "wiley-online-library-pilot005-run-receipt/v1"
        and receipt.get("status") == "complete"
        and receipt.get("predeclared_event_count") == 10
        and receipt.get("completed_event_count") == 10
    ):
        errors.append("Run receipt is incomplete")

    events: dict[str, dict[str, Any]] = {}
    screenshot_receipts: list[dict[str, Any]] = []
    for event in plan.get("events", []):
        output = root / "searches" / str(event["output"])
        try:
            event_errors, summary = validate_event(event, output)
            errors.extend(event_errors)
            events[str(event["event_id"])] = summary
            screenshot_receipts.extend(summary["screenshots"])
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate {event.get('event_id')}: {error}")

    a2_ids = ordered_union(
        [
            events.get("A2-mh", {}).get("ordered_source_ids", []),
            events.get("A2-mb", {}).get("ordered_source_ids", []),
        ]
    )
    unresolved_ids = sorted(
        {
            source_id
            for event in events.values()
            for source_id in event.get("exact_date_accounting", {}).get(
                "unresolved_source_ids", []
            )
        }
    )
    excluded_ids = sorted(
        {
            source_id
            for event in events.values()
            for source_id in event.get("exact_date_accounting", {}).get(
                "excluded_source_ids", []
            )
        }
    )
    if events and (
        events.get("B2", {}).get("source_total", 0) <= 200
        or events.get("B2", {}).get("pages_per_pass", 0) <= 10
        or events.get("BT2", {}).get("source_total", 0) <= 100
        or events.get("BT2", {}).get("pages_per_pass", 0) <= 5
    ):
        errors.append("B2 or BT2 did not exercise the declared larger-set boundary")
    if len(screenshot_receipts) != 20:
        errors.append("The ten events did not retain twenty mandatory screenshots")

    failures = []
    for path in sorted(
        (root / "searches" / "failures").glob("*.NON_MERGEABLE_FAILURE.json")
    ):
        failure = load(path)
        failures.append(
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
        "pilot": "005",
        "source": "Wiley Online Library",
        "status": "complete" if successful else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": plan.get("protocol_commit"),
        "date_window": plan.get("date_window"),
        "decision": {
            "native_ris_final_readiness": (
                "passed_for_the_adopted_current_schedule"
                if successful
                else "not_established"
            ),
            "basis": (
                "All ten current source cells completed two matching ordered DOI passes. "
                "Every first-pass source DOI was normalized from a reconciled page-scoped "
                "native RIS record. Exact-date dispositions and both screenshots were complete."
            ),
            "pilot004_boundary": (
                "Pilot 004 remains rendered DOI and wildcard evidence only. Pilot 005 is the "
                "first current-schedule native RIS readiness validation."
            ),
            "raw_ris_persistence": (
                "Raw RIS bytes were validated and hashed in memory, then discarded. "
                "Normalized pilot records remain non-mergeable."
            ),
        },
        "events": events,
        "event_count": len(events),
        "source_cell_total_sum": sum(
            item.get("source_total", 0) for item in events.values()
        ),
        "two_pass_source_doi_observations": 2
        * sum(item.get("source_total", 0) for item in events.values()),
        "native_ris_source_records_reconciled": sum(
            item.get("source_total", 0) for item in events.values()
        ),
        "native_ris_download_count": sum(
            item.get("native_ris_download_count", 0) for item in events.values()
        ),
        "native_ris_download_bytes": sum(
            item.get("native_ris_download_bytes", 0) for item in events.values()
        ),
        "A2_union": {
            "cell_ids": ["A2-mh", "A2-mb"],
            "cell_totals": [
                events.get("A2-mh", {}).get("source_total"),
                events.get("A2-mb", {}).get("source_total"),
            ],
            "union_count": len(a2_ids),
            "ordered_source_ids": a2_ids,
            "ordered_source_ids_sha256": sequence_sha256(a2_ids),
        },
        "larger_sets": {
            "B2": {
                "source_total": events.get("B2", {}).get("source_total"),
                "pages_per_pass": events.get("B2", {}).get("pages_per_pass"),
                "native_ris_download_count": events.get("B2", {}).get(
                    "native_ris_download_count"
                ),
            },
            "BT2": {
                "source_total": events.get("BT2", {}).get("source_total"),
                "pages_per_pass": events.get("BT2", {}).get("pages_per_pass"),
                "native_ris_download_count": events.get("BT2", {}).get(
                    "native_ris_download_count"
                ),
            },
        },
        "exact_date_accounting": {
            "basis": "Wiley visible First published",
            "source_cell_record_dispositions": sum(
                item.get("source_total", 0) for item in events.values()
            ),
            "excluded_source_ids": excluded_ids,
            "unresolved_source_ids": unresolved_ids,
            "unresolved_policy": "retain for later source-locatable clarification",
            "complete": successful,
        },
        "screenshots": {
            "event_json_count": len(events),
            "validated_png_count": len(screenshot_receipts),
            "all_sibling_paths": all(
                Path(item["file_name"]).parent == Path(".")
                for item in screenshot_receipts
            ),
            "receipts": screenshot_receipts,
        },
        "conditional_future_pilots": plan.get("conditional_future_pilots"),
        "retained_failure_attempts": failures,
        "retained_failure_count": len(failures),
        "plan": {
            "artifact": str(plan_path.relative_to(root)),
            "sha256": file_sha256(plan_path),
            "event_count": len(plan.get("events", [])),
        },
        "run_receipt": {
            "artifact": str(receipt_path.relative_to(root)),
            "sha256": file_sha256(receipt_path),
        },
        "errors": errors,
    }


def write_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_ASSESSMENT)
    args = parser.parse_args()
    assessment = build(args.pilot_root, args.plan, args.receipt)
    write_create_only(args.output, assessment)
    print(
        json.dumps(
            {"status": assessment["status"], "errors": assessment["errors"]}, indent=2
        )
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
