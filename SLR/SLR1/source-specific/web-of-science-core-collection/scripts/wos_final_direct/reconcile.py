#!/usr/bin/env python3
"""Reconcile Web of Science native source-abstract omissions after final capture."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import run as base

RECONCILED_RUN_SCHEMA = "slr1-wos-final-direct-run-reconciled/v1"
RECORD_UNION_SCHEMA = "slr1-wos-final-direct-record-union/v2"
ASSESSMENT_SCHEMA = "slr1-wos-final-direct-assessment/v2"
SOURCE_UNION_SCHEMA = "academic-search-source-union-receipt/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_ordered(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def digest_set(values: set[str]) -> str:
    hasher = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
    return hasher.hexdigest()


def source_abstract_state(row: Mapping[str, Any]) -> str | None:
    """Classify a full native abstract or a documented native source omission."""
    abstract = row.get("abstract")
    if not isinstance(abstract, str) or row.get("abstract_detail_verified") is not True:
        return None
    if abstract.strip():
        if (
            row.get("abstract_source")
            == "native_web_of_science_abstract_inclusive_ris"
            and row.get("abstract_not_available") is False
        ):
            return "full_native_abstract"
        return None
    if (
        row.get("abstract_source") == "not_present_in_abstract_inclusive_ris"
        and row.get("abstract_not_available") is True
        and row.get("snippet") in ("", None)
    ):
        return "native_source_omission"
    return None


def record_capture_summary(
    rows: Any, *, enforce_source_rank: bool = True
) -> tuple[bool, dict[str, Any]]:
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": None,
            "full_abstract_count": 0,
            "native_source_omission_count": 0,
            "invalid_abstract_capture_count": 0,
            "publication_type_counts": {},
            "missing_publication_type_count": 0,
        }
    valid = True
    identifiers: set[str] = set()
    full_abstract_count = 0
    source_omission_count = 0
    invalid_abstract_count = 0
    type_counts: Counter[str] = Counter()
    missing_type_count = 0
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            valid = False
            continue
        identifier = row.get("paperId")
        document_type = row.get("documentType")
        if (
            not isinstance(identifier, str)
            or base.WOS_ID.fullmatch(identifier) is None
            or identifier in identifiers
            or row.get("sourceRecordId") != identifier
            or row.get("sourceRecordKind") != base.SOURCE_ID
            or row.get("source") != base.SOURCE
            or (enforce_source_rank and row.get("rank") != position)
        ):
            valid = False
        if isinstance(identifier, str):
            identifiers.add(identifier)
        state = source_abstract_state(row)
        if state == "full_native_abstract":
            full_abstract_count += 1
        elif state == "native_source_omission":
            source_omission_count += 1
        else:
            invalid_abstract_count += 1
            valid = False
        if isinstance(document_type, str) and document_type.strip():
            type_counts[document_type] += 1
        else:
            missing_type_count += 1
            valid = False
    return valid, {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstract_count,
        "native_source_omission_count": source_omission_count,
        "invalid_abstract_capture_count": invalid_abstract_count,
        "publication_type_counts": dict(sorted(type_counts.items())),
        "missing_publication_type_count": missing_type_count,
        "all_retained_rows_have_an_abstract_field": all(
            isinstance(row, Mapping) and isinstance(row.get("abstract"), str)
            for row in rows
        ),
        "all_retained_rows_have_valid_source_abstract_state": invalid_abstract_count
        == 0,
        "all_retained_rows_have_publication_type": missing_type_count == 0,
    }


def native_ris_valid(
    path: Path, value: Mapping[str, Any], event: Mapping[str, Any]
) -> tuple[bool, dict[str, Any] | None]:
    metadata = value.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    native = prisma.get("native_artifact") if isinstance(prisma, Mapping) else None
    total = value.get("total")
    ris_path = path.with_name(str(event["native_ris_filename"]))
    if total == 0:
        return native is None and not ris_path.exists(), None
    rows = value.get("results")
    if not isinstance(total, int) or total < 1 or not isinstance(rows, list):
        return False, None
    identifiers = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ]
    try:
        records = base.parse_ris(ris_path)
        ris_ids = [base.ris_identifier(record) for record in records]
    except (OSError, UnicodeError, ValueError):
        return False, None
    if len(records) != total or ris_ids != identifiers:
        return False, None
    full_abstract_count = 0
    native_source_omission_count = 0
    type_missing = 0
    state_valid = True
    for row, record in zip(rows, records):
        if not isinstance(row, Mapping):
            state_valid = False
            continue
        ris_abstract = " ".join(
            value.strip()
            for tag in ("AB", "N2")
            for value in record.get(tag, [])
            if isinstance(value, str) and value.strip()
        )
        ris_type = " ".join(
            value.strip()
            for value in record.get("TY", [])
            if isinstance(value, str) and value.strip()
        )
        state = source_abstract_state(row)
        if ris_abstract:
            if state != "full_native_abstract":
                state_valid = False
            else:
                full_abstract_count += 1
        elif state == "native_source_omission":
            native_source_omission_count += 1
        else:
            state_valid = False
        if not ris_type or row.get("documentType") != ris_type:
            type_missing += 1
            state_valid = False
    expected_pages = math.ceil(total / base.PAGE_SIZE)
    valid = bool(
        ris_path.is_file()
        and not ris_path.is_symlink()
        and state_valid
        and isinstance(native, Mapping)
        and native.get("schema_version") == "academic-search-native-artifact/v1"
        and native.get("format") == "RIS"
        and native.get("digest_algorithm") == "sha256"
        and native.get("sha256") == digest(ris_path)
        and native.get("byte_count") == ris_path.stat().st_size
        and native.get("record_count") == total
        and native.get("record_count_provenance") == "framed_native_file_parse"
        and native.get("pages_exported") == expected_pages
        and native.get("local_path_persisted") is False
    )
    return valid, {
        "path": ris_path.name,
        "sha256": digest(ris_path),
        "bytes": ris_path.stat().st_size,
        "record_count": len(records),
        "ordered_wos_ids_sha256": digest_ordered(ris_ids),
        "full_abstract_count": full_abstract_count,
        "native_source_omission_count": native_source_omission_count,
        "missing_publication_type_count": type_missing,
        "valid": valid,
    }


def artifact_summary(
    path: Path, event: Mapping[str, Any], plan: Mapping[str, Any]
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"valid": False, "artifact_written": False}
    try:
        value = base.load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }
    metadata = value.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, Mapping) else {}
    staged = prisma.get("staged_counts", {}) if isinstance(prisma, Mapping) else {}
    adapter = prisma.get("adapter", {}) if isinstance(prisma, Mapping) else {}
    rows = value.get("results")
    identifiers = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ] if isinstance(rows, list) else []
    total = value.get("total")
    capture_valid, capture = record_capture_summary(rows)
    native_valid, native_summary = native_ris_valid(path, value, event)
    screenshots_valid, images = base.screenshot_evidence(
        path, metadata.get("screenshots", {}) if isinstance(metadata, Mapping) else {}
    )
    controls_ok = base.controls_valid(value, event, plan)
    completion_ok = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == base.SOURCE
        and isinstance(total, int)
        and total >= 0
        and isinstance(rows, list)
        and total == len(rows) == len(identifiers) == len(set(identifiers))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and prisma.get("report_readiness_reasons") == []
        and staged.get("source_reported_total") == total
        and staged.get("source_reported_total_exact") is True
        and staged.get("raw_source_records") == total
        and staged.get("records_exported") == total
    )
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    marker_ok = base.marker_valid(path)
    return {
        "valid": bool(
            controls_ok
            and completion_ok
            and adapter_ok
            and native_valid
            and screenshots_valid
            and marker_ok
            and capture_valid
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status") if isinstance(metadata, Mapping) else None,
        "total": total,
        "stable_id_count": len(set(identifiers)),
        "ordered_wos_ids_sha256": digest_ordered(identifiers),
        "controls_valid": controls_ok,
        "completion_valid": completion_ok,
        "adapter_binding_valid": adapter_ok,
        "native_ris_valid": native_valid,
        "native_ris": native_summary,
        "screenshots_valid": screenshots_valid,
        "terminal_marker_valid": marker_ok,
        "abstract_capture_valid": capture_valid,
        "full_abstract_count": capture["full_abstract_count"],
        "native_source_omission_count": capture["native_source_omission_count"],
        "invalid_abstract_capture_count": capture["invalid_abstract_capture_count"],
        "publication_type_counts": capture["publication_type_counts"],
        "missing_publication_type_count": capture["missing_publication_type_count"],
        "publication_type_capture_valid": capture[
            "all_retained_rows_have_publication_type"
        ],
        "screenshots": images,
    }


def reconcile(
    plan_path: Path, initial_receipt_path: Path, output_dir: Path, output: Path
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = base.load(plan_path)
    initial = base.load(initial_receipt_path)
    if base.validate_plan(plan, verify_bindings=False):
        raise ValueError("The original final plan is invalid")
    if initial.get("schema_version") != base.RUN_SCHEMA:
        raise ValueError("Unexpected initial final-run receipt schema")
    if initial.get("plan_sha256") != digest(plan_path):
        raise ValueError("The initial receipt does not bind the original plan")
    if (
        initial.get("source_command_attempt_count") != len(base.PARTITIONS)
        or initial.get("all_partitions_attempted") is not True
        or initial.get("target_identifier_retained") is not False
    ):
        raise ValueError("The initial receipt does not cover the complete schedule")
    outcomes_by_partition = {
        item.get("partition_id"): item
        for item in initial.get("outcomes", [])
        if isinstance(item, Mapping) and isinstance(item.get("partition_id"), str)
    }
    if set(outcomes_by_partition) != set(base.PARTITIONS):
        raise ValueError("The initial receipt has incomplete partition coverage")

    outcomes: list[dict[str, Any]] = []
    errors: list[str] = []
    for event in plan["events"]:
        partition = event["partition_id"]
        prior = outcomes_by_partition[partition]
        path = output_dir / event["output_filename"]
        summary = artifact_summary(path, event, plan)
        prior_execution_ok = bool(
            prior.get("exit_code") == 0
            and prior.get("attempt_count") == 1
            and prior.get("artifact") == event.get("output_filename")
            and prior.get("controls_valid") is True
            and prior.get("completion_valid") is True
            and prior.get("adapter_binding_valid") is True
            and prior.get("screenshots_valid") is True
            and prior.get("terminal_marker_valid") is True
            and prior.get("publication_type_capture_valid") is True
        )
        if not prior_execution_ok:
            errors.append(f"initial_source_execution:{partition}")
        if summary.get("valid") is not True:
            errors.append(f"reconciled_capture:{partition}")
        outcomes.append(
            {
                "event_id": event["event_id"],
                "partition_id": partition,
                "source_execution_replayed": False,
                "success": summary.get("valid") is True,
                "attempt_count": 1,
                "initial_outcome_success": prior.get("success"),
                "initial_full_abstract_capture_valid": prior.get(
                    "full_abstract_capture_valid"
                ),
                "initial_missing_full_abstract_count": prior.get(
                    "missing_full_abstract_count"
                ),
                "native_source_omission_reconciled": summary.get(
                    "native_source_omission_count", 0
                )
                > 0,
                "artifact": path.name if path.is_file() else None,
                "native_ris_artifact": event["native_ris_filename"]
                if (output_dir / event["native_ris_filename"]).is_file()
                else None,
                "artifact_sha256": summary.get("artifact_sha256"),
                "artifact_bytes": summary.get("artifact_bytes"),
                "corrected_validation_success": summary.get("valid") is True,
                "total": summary.get("total"),
                "native_ris": summary.get("native_ris"),
                "full_abstract_count": summary.get("full_abstract_count"),
                "native_source_omission_count": summary.get(
                    "native_source_omission_count"
                ),
                "publication_type_counts": summary.get("publication_type_counts"),
                "missing_publication_type_count": summary.get(
                    "missing_publication_type_count"
                ),
                "screenshots": summary.get("screenshots"),
            }
        )
    success = not errors and all(
        outcome.get("corrected_validation_success") is True for outcome in outcomes
    )
    receipt = {
        "schema_version": RECONCILED_RUN_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "event_kind": "final",
        "plan": plan_path.name,
        "plan_sha256": digest(plan_path),
        "initial_run_receipt": initial_receipt_path.name,
        "initial_run_receipt_sha256": digest(initial_receipt_path),
        "source_execution_replayed": False,
        "reconciliation_reason": (
            "The initial local acceptance gate required every Web of Science record "
            "to have a nonempty AB or N2 field. The source guideline requires a "
            "nonempty native AB or N2 when a result-card snippet exists. It permits "
            "a documented native source omission when both are absent."
        ),
        "source_abstract_policy": {
            "full_abstracts_saved_from": "native RIS AB or N2",
            "result_card_snippet_requires_native_abstract": True,
            "native_source_omission_allowed_only_when": [
                "RIS has no AB or N2",
                "normalized abstract is empty",
                "abstract_not_available is true",
                "abstract_source is not_present_in_abstract_inclusive_ris",
                "result-card snippet is empty",
            ],
            "snippet_is_not_used_as_an_abstract": True,
        },
        "publication_type_policy": {
            "normalized_field": "documentType",
            "native_ris_tag": "TY",
            "all_retained_records_require_nonempty_type": True,
            "reviewer_publication_type_coding": "deferred to screening",
        },
        "adapter": plan.get("adapter"),
        "target_identifier_retained": False,
        "source_command_attempt_count": initial.get("source_command_attempt_count"),
        "accepted_event_count": sum(
            outcome.get("corrected_validation_success") is True for outcome in outcomes
        ),
        "all_partitions_attempted": True,
        "success": success,
        "outcomes": outcomes,
        "errors": errors,
        "completed_at_utc": now(),
    }
    base.write_new(output, receipt)
    print(
        json.dumps(
            {
                "status": "passed" if success else "failed",
                "accepted_event_count": receipt["accepted_event_count"],
                "native_source_omissions": sum(
                    outcome.get("native_source_omission_count", 0) for outcome in outcomes
                ),
                "errors": errors,
            }
        )
    )
    return 0 if success else 1


def selected_artifacts(
    plan: Mapping[str, Any], receipt: Mapping[str, Any], output_dir: Path
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]]:
    if receipt.get("schema_version") != RECONCILED_RUN_SCHEMA or receipt.get("success") is not True:
        raise ValueError("The reconciled Web of Science run is incomplete")
    outcomes = {
        item.get("partition_id"): item
        for item in receipt.get("outcomes", [])
        if isinstance(item, Mapping) and isinstance(item.get("partition_id"), str)
    }
    selected = []
    for event in plan.get("events", []):
        if not isinstance(event, Mapping):
            raise ValueError("The final plan has a malformed event")
        outcome = outcomes.get(event.get("partition_id"))
        if (
            not isinstance(outcome, Mapping)
            or outcome.get("success") is not True
            or outcome.get("artifact") != event.get("output_filename")
        ):
            raise ValueError(f"Incomplete reconciled partition: {event.get('partition_id')}")
        path = output_dir / str(event["output_filename"])
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing source artifact: {path}")
        selected.append((event, outcome, path, base.load(path)))
    if len(selected) != len(base.PARTITIONS):
        raise ValueError("The reconciled receipt has incomplete source coverage")
    return selected


def source_union(
    plan_path: Path, receipt_path: Path, output_dir: Path, output: Path
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = base.load(plan_path)
    receipt = base.load(receipt_path)
    selected = selected_artifacts(plan, receipt, output_dir)
    command = [
        "uv",
        "run",
        str(base.SOURCE_UNION_TOOL),
        "--input",
        *(str(path) for _, _, path, _ in selected),
        "--output-path",
        str(output),
        "--expected-partitions",
        *base.PARTITIONS,
        "--expected-sources",
        base.SOURCE_ID,
        "--review-namespace",
        base.REVIEW_NAMESPACE,
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("Could not create the Web of Science source-union receipt")
    return 0


def record_union(
    plan_path: Path, receipt_path: Path, output_dir: Path, output: Path
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = base.load(plan_path)
    receipt = base.load(receipt_path)
    selected = selected_artifacts(plan, receipt, output_dir)
    records: dict[str, dict[str, Any]] = {}
    artifacts: list[dict[str, Any]] = []
    for event, outcome, path, data in selected:
        summary = artifact_summary(path, event, plan)
        if summary.get("valid") is not True:
            raise ValueError(f"Artifact failed reconciled validation: {path}")
        rows = data.get("results")
        if not isinstance(rows, list):
            raise ValueError(f"Source artifact has no results list: {path}")
        artifacts.append(
            {
                "partition_id": event["partition_id"],
                "artifact": base.relative(path),
                "artifact_sha256": outcome.get("artifact_sha256"),
                "record_count": data.get("total"),
                "native_ris": summary.get("native_ris"),
            }
        )
        for row in rows:
            if not isinstance(row, Mapping) or not isinstance(row.get("paperId"), str):
                raise ValueError(f"Malformed source record in {path}")
            identifier = row["paperId"]
            current = records.setdefault(
                identifier,
                {
                    "paperId": identifier,
                    "sourceRecordId": row.get("sourceRecordId"),
                    "discovery_partitions": [],
                    "record": dict(row),
                },
            )
            if event["partition_id"] not in current["discovery_partitions"]:
                current["discovery_partitions"].append(event["partition_id"])
            old = current["record"]
            if len(str(row.get("abstract") or "")) > len(str(old.get("abstract") or "")):
                current["record"] = dict(row)
    rows = []
    for identifier in sorted(records):
        item = records[identifier]
        item["discovery_partitions"].sort(key=base.PARTITIONS.index)
        rows.append(item)
    capture_valid, capture = record_capture_summary(
        [item["record"] for item in rows], enforce_source_rank=False
    )
    if not capture_valid:
        raise ValueError("The record union has an invalid abstract or publication type")
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "purpose": "deduplicated_final_direct_source_records_with_full_native_abstracts_and_source_publication_types",
        "reviewer_publication_type_coding": "not inferred from source metadata",
        "source_abstract_omission_policy": "Retain an empty abstract only when the native RIS has no AB or N2 and the result card has no snippet.",
        "plan": base.relative(plan_path),
        "plan_sha256": digest(plan_path),
        "reconciled_run_receipt": base.relative(receipt_path),
        "reconciled_run_receipt_sha256": digest(receipt_path),
        "input_artifacts": artifacts,
        "source_event_record_count": sum(int(item["record_count"]) for item in artifacts),
        "unique_wos_id_count": len(rows),
        "stable_id_set_sha256": digest_set({item["paperId"] for item in rows}),
        "records_with_full_native_abstract": capture["full_abstract_count"],
        "records_with_native_source_abstract_omission": capture[
            "native_source_omission_count"
        ],
        "records_with_invalid_abstract_capture": capture["invalid_abstract_capture_count"],
        "source_publication_type_field": "documentType",
        "records_with_source_publication_type": sum(
            capture["publication_type_counts"].values()
        ),
        "records_missing_source_publication_type": capture[
            "missing_publication_type_count"
        ],
        "source_publication_type_counts": capture["publication_type_counts"],
        "complete": capture_valid,
        "records": rows,
    }
    base.write_new(output, value)
    return 0


def source_union_valid(
    value: Mapping[str, Any], stable_ids: set[str], raw_count: int, plan: Mapping[str, Any]
) -> bool:
    union = value.get("source_unions", {}).get(base.SOURCE_ID, {})
    return bool(
        value.get("schema_version") == SOURCE_UNION_SCHEMA
        and value.get("review_namespace") == base.REVIEW_NAMESPACE
        and value.get("review_id") == plan.get("review_id")
        and value.get("strategy_reference") == plan.get("strategy_reference")
        and value.get("expected_partitions") == list(base.PARTITIONS)
        and value.get("expected_sources") == [base.SOURCE_ID]
        and value.get("completeness_status") == "complete"
        and value.get("failure_status") == "none"
        and union.get("event_total_sum") == raw_count
        and union.get("raw_record_count") == raw_count
        and set(union.get("stable_record_ids", [])) == stable_ids
    )


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    source_union_path: Path,
    record_union_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = base.load(plan_path)
    receipt = base.load(receipt_path)
    union = base.load(source_union_path)
    records = base.load(record_union_path)
    errors = base.validate_plan(plan, verify_bindings=False)
    if (
        receipt.get("schema_version") != RECONCILED_RUN_SCHEMA
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("success") is not True
        or receipt.get("accepted_event_count") != len(base.PARTITIONS)
        or receipt.get("source_execution_replayed") is not False
        or receipt.get("target_identifier_retained") is not False
    ):
        errors.append("reconciled_receipt")
    try:
        selected = selected_artifacts(plan, receipt, output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"events:{type(error).__name__}")
        selected = []

    evidence: list[dict[str, Any]] = []
    all_ids: set[str] = set()
    raw_count = 0
    raw_types: Counter[str] = Counter()
    unique_types: dict[str, str] = {}
    source_omissions = 0
    cutoff_year_records = 0
    for event, outcome, path, data in selected:
        summary = artifact_summary(path, event, plan)
        rows = data.get("results")
        if not isinstance(rows, list) or summary.get("valid") is not True:
            errors.append(f"event:{event['partition_id']}")
            continue
        ids = {
            row.get("paperId")
            for row in rows
            if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
        }
        if (
            outcome.get("artifact_sha256") != digest(path)
            or outcome.get("artifact_bytes") != path.stat().st_size
            or outcome.get("full_abstract_count") != summary.get("full_abstract_count")
            or outcome.get("native_source_omission_count")
            != summary.get("native_source_omission_count")
            or outcome.get("publication_type_counts")
            != summary.get("publication_type_counts")
            or outcome.get("missing_publication_type_count")
            != summary.get("missing_publication_type_count")
        ):
            errors.append(f"artifact_binding:{event['partition_id']}")
        all_ids.update(identifier for identifier in ids if isinstance(identifier, str))
        raw_count += len(rows)
        raw_types.update(summary["publication_type_counts"])
        for row in rows:
            if (
                isinstance(row, Mapping)
                and isinstance(row.get("paperId"), str)
                and isinstance(row.get("documentType"), str)
            ):
                unique_types.setdefault(row["paperId"], row["documentType"])
        source_omissions += summary["native_source_omission_count"]
        cutoff_year_records += sum(
            isinstance(row, Mapping) and row.get("year") == base.YEAR_END for row in rows
        )
        evidence.append(
            {
                "partition_id": event["partition_id"],
                "artifact": path.name,
                "artifact_sha256": digest(path),
                "source_total": data.get("total"),
                "stable_id_count": len(ids),
                "ordered_wos_ids_sha256": summary["ordered_wos_ids_sha256"],
                "native_ris": summary["native_ris"],
                "full_abstract_count": summary["full_abstract_count"],
                "native_source_omission_count": summary[
                    "native_source_omission_count"
                ],
                "publication_type_counts": summary["publication_type_counts"],
                "missing_publication_type_count": summary[
                    "missing_publication_type_count"
                ],
                "screenshots": summary["screenshots"],
            }
        )
    union_ok = source_union_valid(union, all_ids, raw_count, plan)
    if not union_ok:
        errors.append("source_union")
    record_union_ok = bool(
        records.get("schema_version") == RECORD_UNION_SCHEMA
        and records.get("plan_sha256") == digest(plan_path)
        and records.get("reconciled_run_receipt_sha256") == digest(receipt_path)
        and records.get("source_event_record_count") == raw_count
        and records.get("unique_wos_id_count") == len(all_ids)
        and records.get("stable_id_set_sha256") == digest_set(all_ids)
        and records.get("records_with_full_native_abstract")
        + records.get("records_with_native_source_abstract_omission", -1)
        == len(all_ids)
        and records.get("records_with_invalid_abstract_capture") == 0
        and records.get("source_publication_type_field") == "documentType"
        and records.get("records_with_source_publication_type") == len(all_ids)
        and records.get("records_missing_source_publication_type") == 0
        and records.get("source_publication_type_counts")
        == dict(sorted(Counter(unique_types.values()).items()))
        and records.get("complete") is True
        and isinstance(records.get("records"), list)
        and len(records["records"]) == len(all_ids)
    )
    if not record_union_ok:
        errors.append("record_union")
    screenshot_count = sum(len(item["screenshots"]) for item in evidence)
    if screenshot_count != len(base.PARTITIONS) * 2:
        errors.append("screenshot_count")
    complete = bool(len(evidence) == len(base.PARTITIONS) and not errors)
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "event_kind": "final",
        "complete": complete,
        "status": "passed" if complete else "failed",
        "errors": errors,
        "plan": base.relative(plan_path),
        "plan_sha256": digest(plan_path),
        "reconciled_run_receipt": base.relative(receipt_path),
        "reconciled_run_receipt_sha256": digest(receipt_path),
        "source_union": base.relative(source_union_path),
        "source_union_sha256": digest(source_union_path),
        "record_union": base.relative(record_union_path),
        "record_union_sha256": digest(record_union_path),
        "adapter": plan.get("adapter"),
        "accepted_source_event_count": len(evidence),
        "verified_screenshot_file_count": screenshot_count,
        "events": evidence,
        "stable_id_union": {
            "source_event_record_count": raw_count,
            "unique_wos_id_count": len(all_ids),
            "cross_partition_duplicate_occurrences": raw_count - len(all_ids),
            "stable_id_set_sha256": digest_set(all_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "record_capture": {
            "full_native_abstracts_saved": True,
            "result_card_snippet_replaced_by_abstract": False,
            "native_source_abstract_omission_policy": "AB/N2 and result-card snippet both absent",
            "unique_records_with_full_native_abstract": records.get(
                "records_with_full_native_abstract"
            ),
            "unique_records_with_native_source_abstract_omission": records.get(
                "records_with_native_source_abstract_omission"
            ),
            "unique_records_with_invalid_abstract_capture": records.get(
                "records_with_invalid_abstract_capture"
            ),
            "source_publication_types_saved": True,
            "source_publication_type_field": "documentType",
            "source_publication_type_counts": records.get(
                "source_publication_type_counts"
            ),
            "source_event_publication_type_occurrence_counts": dict(
                sorted(raw_types.items())
            ),
            "records_missing_source_publication_type": records.get(
                "records_missing_source_publication_type"
            ),
            "reviewer_publication_type_coding": "deferred to screening",
        },
        "cutoff_screening": {
            "common_evidence_cutoff": base.CUTOFF_DATE,
            "source_year_upper_bound": base.YEAR_END,
            "source_precision": "year",
            "records_in_cutoff_year_requiring_exact_date_screening": cutoff_year_records,
            "status": "pending_screening",
        },
        "source_union_valid": union_ok,
        "record_union_valid": record_union_ok,
        "final_search_partitions_complete": complete,
    }
    base.write_new(output, assessment)
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "unique_wos_ids": len(all_ids),
                "native_source_omissions": source_omissions,
            }
        )
    )
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    reconcile_parser = commands.add_parser("reconcile-run")
    reconcile_parser.add_argument("--plan", type=Path, required=True)
    reconcile_parser.add_argument("--initial-receipt", type=Path, required=True)
    reconcile_parser.add_argument("--output-dir", type=Path, required=True)
    reconcile_parser.add_argument("--output", type=Path, required=True)

    union_parser = commands.add_parser("source-union")
    union_parser.add_argument("--plan", type=Path, required=True)
    union_parser.add_argument("--receipt", type=Path, required=True)
    union_parser.add_argument("--output-dir", type=Path, required=True)
    union_parser.add_argument("--output", type=Path, required=True)

    records_parser = commands.add_parser("record-union")
    records_parser.add_argument("--plan", type=Path, required=True)
    records_parser.add_argument("--receipt", type=Path, required=True)
    records_parser.add_argument("--output-dir", type=Path, required=True)
    records_parser.add_argument("--output", type=Path, required=True)

    assessment_parser = commands.add_parser("assess")
    assessment_parser.add_argument("--plan", type=Path, required=True)
    assessment_parser.add_argument("--receipt", type=Path, required=True)
    assessment_parser.add_argument("--output-dir", type=Path, required=True)
    assessment_parser.add_argument("--source-union", type=Path, required=True)
    assessment_parser.add_argument("--record-union", type=Path, required=True)
    assessment_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "reconcile-run":
            return reconcile(args.plan, args.initial_receipt, args.output_dir, args.output)
        if args.command == "source-union":
            return source_union(args.plan, args.receipt, args.output_dir, args.output)
        if args.command == "record-union":
            return record_union(args.plan, args.receipt, args.output_dir, args.output)
        if args.command == "assess":
            return assess(
                args.plan,
                args.receipt,
                args.output_dir,
                args.source_union,
                args.record_union,
                args.output,
            )
    except (FileExistsError, OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
