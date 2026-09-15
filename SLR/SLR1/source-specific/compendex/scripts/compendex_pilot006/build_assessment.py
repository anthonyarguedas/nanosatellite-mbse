#!/usr/bin/env python3
"""Build the Compendex Pilot 006 assessment and paired reconciliation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

ASSESSMENT_SCHEMA = "engineering-village-readiness-pilot-assessment/v1"
RECONCILIATION_SCHEMA = "engineering-village-readiness-pilot-reconciliation/v1"
PLAN_SCHEMA = "engineering-village-readiness-pilot-plan/v1"
RUN_SCHEMA = "engineering-village-readiness-pilot-run/v1"
CELL_SCHEMA = "engineering-village-readiness-pilot-cell/v1"
SCREENSHOT_SCHEMA = "engineering-village-automatic-screenshots/v1"
SOURCE_LABELS = {
    "compendex": "Compendex (Engineering Village)",
    "inspec": "Inspec (Engineering Village)",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def png_dimensions(path: Path) -> dict[str, int] | None:
    if not path.is_file():
        return None
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    if width < 1 or height < 1:
        return None
    return {"width": width, "height": height}


def projected_ids(results: list[Any]) -> tuple[dict[str, list[str]], list[str]]:
    projected = {key: [] for key in SOURCE_LABELS}
    errors: list[str] = []
    by_label = {label: key for key, label in SOURCE_LABELS.items()}
    for index, record in enumerate(results):
        if not isinstance(record, dict):
            errors.append(f"record_{index}_not_object")
            continue
        database = by_label.get(record.get("source"))
        accession = record.get("paperId")
        if database is None:
            errors.append(f"record_{index}_source")
            continue
        if not isinstance(accession, str) or not accession.strip():
            errors.append(f"record_{index}_accession")
            continue
        projected[database].append(accession)
    for database, ids in projected.items():
        if len(ids) != len(set(ids)):
            errors.append(f"{database}_duplicate_accession")
    return projected, errors


def screenshot_check(
    output: Path, metadata: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    screenshots = metadata.get("screenshots")
    errors: list[str] = []
    if not isinstance(screenshots, dict):
        return {"valid": False}, ["screenshot_receipt_missing"]
    if screenshots.get("schema_version") != SCREENSHOT_SCHEMA:
        errors.append("screenshot_schema")
    if screenshots.get("automatic") is not True:
        errors.append("screenshots_not_automatic")
    if screenshots.get("opt_out_available") is not False:
        errors.append("screenshot_opt_out")
    if screenshots.get("same_directory_as_json") is not True:
        errors.append("screenshot_directory")
    if screenshots.get("capture_pass") != "pass-1":
        errors.append("screenshot_capture_pass")
    checks: dict[str, Any] = {}
    for key, suffix, page_kind in (
        ("search_page", ".search-page.png", "configured_search_page"),
        ("results_page", ".results-page.png", "verified_first_results_page"),
    ):
        path = output.with_name(f"{output.stem}{suffix}")
        evidence = screenshots.get(key)
        dimensions = png_dimensions(path)
        exists = path.is_file()
        digest = digest_file(path) if exists else None
        valid = bool(
            isinstance(evidence, dict)
            and exists
            and dimensions is not None
            and evidence.get("page") == page_kind
            and evidence.get("file_name") == path.name
            and evidence.get("sha256") == digest
            and evidence.get("width") == dimensions["width"]
            and evidence.get("height") == dimensions["height"]
            and evidence.get("full_page") is True
            and evidence.get("complete_page_url_retained") is False
            and evidence.get("session_identifiers_retained") is False
            and isinstance(evidence.get("account_elements_masked"), int)
            and not isinstance(evidence.get("account_elements_masked"), bool)
            and evidence.get("account_elements_masked") >= 0
            and isinstance(evidence.get("email_elements_masked"), int)
            and not isinstance(evidence.get("email_elements_masked"), bool)
            and evidence.get("email_elements_masked") >= 0
        )
        if not valid:
            errors.append(f"{key}_invalid")
        checks[key] = {
            "file_name": path.name,
            "exists": exists,
            "sha256": digest,
            "dimensions": dimensions,
            "receipt_matches": valid,
        }
    return {
        "valid": not errors,
        "capture_pass": screenshots.get("capture_pass"),
        **checks,
    }, errors


def historical_query_hashes(repository_root: Path) -> dict[str, Any]:
    base = repository_root / "SLR/SLR1/source-specific/compendex/pilots/003/searches"
    result: dict[str, Any] = {}
    b2 = load(base / "B2.NON_MERGEABLE_FAILURE.json")
    result["B2"] = {
        "artifact": str(
            (base / "B2.NON_MERGEABLE_FAILURE.json").relative_to(repository_root)
        ),
        "status": "explicit_null_failure",
        "query_sha256": b2.get("request", {}).get("query_sha256"),
    }
    for partition in queries.CHANGED_IDS:
        path = base / f"{partition}.json"
        value = load(path)
        old_query = value.get("requested_query")
        result[partition] = {
            "artifact": str(path.relative_to(repository_root)),
            "status": "historical_strict_complete",
            "query_sha256": digest_text(old_query)
            if isinstance(old_query, str)
            else None,
        }
    return result


def build(
    pilot_root: Path,
    plan_path: Path,
    run_receipt_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = load(plan_path)
    run_receipt = load(run_receipt_path)
    errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("plan_schema")
    if run_receipt.get("schema_version") != RUN_SCHEMA:
        errors.append("run_schema")
    if plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        errors.append("protocol_commit")
    if run_receipt.get("event_plan_sha256") != digest_file(plan_path):
        errors.append("plan_hash")
    events = plan.get("events")
    outcomes = run_receipt.get("outcomes")
    if not isinstance(events, list) or len(events) != 9:
        raise RuntimeError("The readiness plan does not contain nine events")
    if not isinstance(outcomes, list):
        raise RuntimeError("The readiness run receipt has no outcomes")
    outcome_by_id = {
        item.get("event_id"): item for item in outcomes if isinstance(item, dict)
    }
    if set(outcome_by_id) != set(queries.SCHEDULE_IDS):
        errors.append("run_event_coverage")
    if (
        run_receipt.get("status") != "complete"
        or run_receipt.get("success") is not True
    ):
        errors.append("run_incomplete")

    summaries: list[dict[str, Any]] = []
    reconciliation_partitions: dict[str, Any] = {}
    union_maps: dict[str, OrderedDict[str, list[str]]] = {
        key: OrderedDict() for key in SOURCE_LABELS
    }
    event_occurrences = {key: 0 for key in SOURCE_LABELS}
    screenshot_count = 0
    strict_pass_count = 0

    for event in events:
        partition = event["partition_id"]
        output = pilot_root / "searches" / event["output"]
        event_errors: list[str] = []
        if not output.is_file():
            event_errors.append("artifact_missing")
            summaries.append(
                {
                    "partition_id": partition,
                    "status": "missing",
                    "errors": event_errors,
                }
            )
            errors.extend(f"{partition}:{item}" for item in event_errors)
            continue
        value = load(output)
        metadata = value.get("output_metadata")
        context = value.get("pilot_context")
        results = value.get("results")
        if not isinstance(metadata, dict):
            metadata = {}
            event_errors.append("metadata")
        if not isinstance(context, dict):
            context = {}
            event_errors.append("pilot_context")
        if not isinstance(results, list):
            results = []
            event_errors.append("results")
        if value.get("schema_version") != "academic-search-result/v1":
            event_errors.append("artifact_schema")
        if (
            value.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
        ):
            event_errors.append("merge_boundary")
        if context.get("schema_version") != CELL_SCHEMA:
            event_errors.append("cell_schema")
        if context.get("status") != "strict_two_pass_complete":
            event_errors.append("strict_status")
        if context.get("adapter", {}).get("version") != "16":
            event_errors.append("adapter_version")
        if context.get("partition_id") != partition:
            event_errors.append("partition")
        query = event["query"]
        if value.get("requested_query") != query:
            event_errors.append("query")
        if context.get("query_sha256") != digest_text(query):
            event_errors.append("query_hash")
        if query.count("*") != 3 or queries.PROXIMITY_OPERATOR_RE.search(query):
            event_errors.append("translation")
        if (
            context.get("wildcard_count") != 3
            or context.get("proximity_operator_count") != 0
        ):
            event_errors.append("translation_receipt")
        if context.get("boolean_form") != queries.BOOLEAN_FORMS[partition]:
            event_errors.append("boolean_form")
        if context.get("changed_definition_since_pilot003") is not (
            partition in queries.CHANGED_IDS
        ):
            event_errors.append("changed_definition_flag")
        total = value.get("total")
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            event_errors.append("total")
            total = None
        elif total != len(results):
            event_errors.append("record_count")
        projected, projection_errors = projected_ids(results)
        event_errors.extend(projection_errors)
        projections = context.get("projections")
        if not isinstance(projections, dict):
            projections = {}
            event_errors.append("projection_receipt")
        for database, ids in projected.items():
            expected = projections.get(database, {})
            if expected.get("ordered_stable_accessions") != ids:
                event_errors.append(f"{database}_projection_ids")
            if expected.get("source_total") != len(ids):
                event_errors.append(f"{database}_projection_total")
            if expected.get("ordered_stable_accessions_sha256") != digest_text(
                "\n".join(ids)
            ):
                event_errors.append(f"{database}_projection_hash")
        if total is not None and total != sum(len(ids) for ids in projected.values()):
            event_errors.append("paired_projection_sum")
        strict = context.get("strict_complete_comparison_receipt")
        if not isinstance(strict, dict) or strict.get("sequence_match") is not True:
            event_errors.append("strict_receipt")
        else:
            strict_pass_count += 2
            stable_counts = strict.get("stable_counts", {})
            expected_counts = {
                database: len(ids) for database, ids in projected.items()
            }
            if stable_counts.get("portal_total") != total:
                event_errors.append("strict_portal_total")
            if (
                stable_counts.get("source_export_ids_seen_by_database")
                != expected_counts
            ):
                event_errors.append("strict_projection_counts")
        screenshots, screenshot_errors = screenshot_check(output, metadata)
        event_errors.extend(screenshot_errors)
        if screenshots.get("valid") is True:
            screenshot_count += 2
        outcome = outcome_by_id.get(partition, {})
        if outcome.get("status") != "strict_two_pass_complete":
            event_errors.append("run_outcome")
        if outcome.get("output_sha256") != digest_file(output):
            event_errors.append("artifact_hash")

        for database, ids in projected.items():
            event_occurrences[database] += len(ids)
            for accession in ids:
                union_maps[database].setdefault(accession, []).append(partition)
        reconciliation_partitions[partition] = {
            "paired_source_total": total,
            "query_sha256": event["query_sha256"],
            "boolean_form": event["boolean_form"],
            "strict_two_pass_complete": not any(
                item.startswith("strict") for item in event_errors
            ),
            "projections": {
                database: {
                    "source_total": len(ids),
                    "ordered_stable_accessions": ids,
                    "ordered_stable_accessions_sha256": digest_text("\n".join(ids)),
                }
                for database, ids in projected.items()
            },
        }
        status = "passed" if not event_errors else "failed"
        summaries.append(
            {
                "partition_id": partition,
                "status": status,
                "boolean_form": event["boolean_form"],
                "changed_definition_since_pilot003": partition in queries.CHANGED_IDS,
                "query_sha256": event["query_sha256"],
                "paired_source_total": total,
                "compendex_total": len(projected["compendex"]),
                "inspec_total": len(projected["inspec"]),
                "strict_passes": 2
                if strict and strict.get("sequence_match") is True
                else 0,
                "mandatory_screenshots": 2 if screenshots.get("valid") is True else 0,
                "errors": event_errors,
            }
        )
        errors.extend(f"{partition}:{item}" for item in event_errors)

    repository_root = plan_path.resolve().parents[7]
    historical = historical_query_hashes(repository_root)
    b2_summary = next(
        (item for item in summaries if item.get("partition_id") == "B2"), {}
    )
    b2_resolution = {
        "historical_pilot003": historical["B2"],
        "current_pilot006": {
            "query_sha256": queries.digest_text(queries.EVENT_QUERIES["B2"]),
            "status": b2_summary.get("status"),
            "paired_source_total": b2_summary.get("paired_source_total"),
            "compendex_total": b2_summary.get("compendex_total"),
            "inspec_total": b2_summary.get("inspec_total"),
            "strict_passes": b2_summary.get("strict_passes"),
            "mandatory_screenshots": b2_summary.get("mandatory_screenshots"),
        },
        "resolved_for_current_readiness": b2_summary.get("status") == "passed",
        "historical_artifact_changed": False,
    }
    changed_checks: dict[str, Any] = {}
    for partition in queries.CHANGED_IDS:
        summary = next(
            (item for item in summaries if item.get("partition_id") == partition), {}
        )
        old_hash = historical[partition]["query_sha256"]
        current_hash = queries.digest_text(queries.EVENT_QUERIES[partition])
        changed_checks[partition] = {
            "boolean_form": queries.BOOLEAN_FORMS[partition],
            "compound_definition": (
                queries.COMPOUND_DEFINITIONS["F(G_model)"]
                if partition == "BG1"
                else queries.COMPOUND_DEFINITIONS["F(G_structure)"]
                if partition == "BG2"
                else queries.COMPOUND_DEFINITIONS["F(C1)"]
                if partition == "BC1"
                else queries.COMPOUND_DEFINITIONS["F(T_precise)"]
            ),
            "pilot003_query_sha256": old_hash,
            "pilot006_query_sha256": current_hash,
            "query_changed": old_hash != current_hash,
            "live_status": summary.get("status"),
            "paired_source_total": summary.get("paired_source_total"),
            "compendex_total": summary.get("compendex_total"),
            "inspec_total": summary.get("inspec_total"),
            "strict_passes": summary.get("strict_passes"),
            "mandatory_screenshots": summary.get("mandatory_screenshots"),
        }
        if old_hash == current_hash:
            errors.append(f"{partition}:historical_query_not_changed")
        if summary.get("status") != "passed":
            errors.append(f"{partition}:live_validation")

    union_payload: dict[str, Any] = {}
    for database, mapping in union_maps.items():
        union_payload[database] = {
            "source_label": SOURCE_LABELS[database],
            "event_occurrences": event_occurrences[database],
            "unique_stable_accession_count": len(mapping),
            "exceeds_100": len(mapping) > 100,
            "ordered_union_sha256": digest_text("\n".join(mapping)),
            "stable_accessions": [
                {"stable_accession": accession, "partitions": partitions}
                for accession, partitions in mapping.items()
            ],
        }

    all_passed = not errors
    reconciliation = {
        "schema_version": RECONCILIATION_SCHEMA,
        "pilot": "006",
        "source": "Compendex with a retained paired Inspec projection",
        "created_at_utc": now(),
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "database_scope_rule": (
            "Accessions, totals, and unions are database-scoped. No Compendex and "
            "Inspec cross-database merge is performed."
        ),
        "partition_order": list(queries.SCHEDULE_IDS),
        "partitions": reconciliation_partitions,
        "database_unions": union_payload,
    }
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "pilot": "006",
        "source": "Compendex with a retained paired Inspec projection",
        "created_at_utc": now(),
        "status": "passed" if all_passed else "failed",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "plan": {
            "path": str(plan_path),
            "sha256": digest_file(plan_path),
        },
        "run_receipt": {
            "path": str(run_receipt_path),
            "sha256": digest_file(run_receipt_path),
        },
        "checks": {
            "all_nine_current_partitions": len(summaries) == 9
            and all(item.get("status") == "passed" for item in summaries),
            "approved_population_wildcards_in_every_query": all(
                event["query"].count("*") == 3 for event in events
            ),
            "no_proximity_operator_in_any_query": all(
                queries.PROXIMITY_OPERATOR_RE.search(event["query"]) is None
                for event in events
            ),
            "adapter_v16": plan.get("adapter", {}).get("version") == "16",
            "strict_paired_source_passes": strict_pass_count,
            "expected_strict_paired_source_passes": 18,
            "mandatory_screenshots": screenshot_count,
            "expected_mandatory_screenshots": 18,
            "B2_current_strict_capture": b2_resolution[
                "resolved_for_current_readiness"
            ],
            "changed_definitions_live": all(
                item["query_changed"] and item["live_status"] == "passed"
                for item in changed_checks.values()
            ),
            "separate_database_reconciliation": True,
        },
        "events": summaries,
        "B2_resolution": b2_resolution,
        "changed_definition_checks": changed_checks,
        "database_unions": {
            database: {
                key: value
                for key, value in payload.items()
                if key != "stable_accessions"
            }
            for database, payload in union_payload.items()
        },
        "inspec_boundary": (
            "The paired Inspec projection is retained separately. This Compendex "
            "readiness pilot does not approve the wildcard translation for Inspec."
        ),
        "decision": (
            "The current Compendex translation and adapter route are ready for a "
            "separate final search. This pilot is not a final search."
            if all_passed
            else "Compendex is not ready for a final search from this pilot."
        ),
        "errors": errors,
    }
    return assessment, reconciliation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--assessment-output", type=Path, required=True)
    parser.add_argument("--reconciliation-output", type=Path, required=True)
    args = parser.parse_args()
    assessment, reconciliation = build(args.pilot_root, args.plan, args.run_receipt)
    write_new(args.reconciliation_output, reconciliation)
    write_new(args.assessment_output, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "events": len(assessment["events"]),
                "compendex_unique": reconciliation["database_unions"]["compendex"][
                    "unique_stable_accession_count"
                ],
                "inspec_unique": reconciliation["database_unions"]["inspec"][
                    "unique_stable_accession_count"
                ],
                "errors": assessment["errors"],
            }
        )
    )
    return 0 if assessment["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
