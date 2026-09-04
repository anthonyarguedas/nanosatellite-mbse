#!/usr/bin/env python3
"""Reconcile and assess the completed Wiley final search events."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping, Sequence

import adapter_repair as repair
import corrective
import run as base


SCRIPT_PATH = Path(__file__).resolve()
FINAL_ROOT = (
    base.REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/wiley-online-library/final-searches"
)
INITIAL_PLAN_PATH = FINAL_ROOT / "final-event-plan.json"
INITIAL_RECEIPT_PATH = FINAL_ROOT / "run-receipt.json"
REPAIR_ROOT = FINAL_ROOT / "corrective-004"
REPAIR_PLAN_PATH = REPAIR_ROOT / "final-event-plan.json"
REPAIR_RECEIPT_PATH = REPAIR_ROOT / "run-receipt.json"
REPAIR_EVENTS_ROOT = REPAIR_ROOT / "events"
MANIFEST_SCHEMA = base.UNION_MANIFEST_SCHEMA
ASSESSMENT_SCHEMA = "slr1-wiley-online-library-final-direct-assessment/v1"
FINAL_SELECTION_SCHEMA = "slr1-wiley-online-library-final-selection/v1"
RIS_TAG_PATTERN = re.compile(r"^([A-Z0-9]{2})\s{0,2}-\s?(.*)$")
WHITESPACE = re.compile(r"\s+")
EMAIL_PATTERN = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
REPAIRED_KEYS = frozenset(repair.EVENT_KEYS)


def clean_text(value: Any) -> str:
    return WHITESPACE.sub(" ", str(value or "").replace("\xa0", " ")).strip()


def remove_email_addresses(value: Any) -> str:
    return clean_text(EMAIL_PATTERN.sub("", clean_text(value)))


def normalize_doi(value: Any) -> str:
    doi = clean_text(value)
    folded = doi.casefold()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ):
        if folded.startswith(prefix):
            doi = doi[len(prefix) :]
            break
    return doi.strip().rstrip(".,;)").casefold()


def parse_ris_records(text: str) -> list[dict[str, list[str]]]:
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    last_tag: str | None = None
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        match = RIS_TAG_PATTERN.match(raw_line)
        if match:
            tag, value = match.groups()
            if tag == "TY":
                if current is not None:
                    raise ValueError("RIS record started before the prior record ended")
                current = {"TY": [value.strip()]}
                last_tag = "TY"
                continue
            if tag == "ER":
                if current is None:
                    raise ValueError("RIS end marker has no record")
                records.append(current)
                current = None
                last_tag = None
                continue
            if current is None:
                raise ValueError("RIS field is outside a record")
            current.setdefault(tag, []).append(value.strip())
            last_tag = tag
            continue
        if not raw_line.strip():
            continue
        if current is not None and last_tag and raw_line[:1].isspace():
            current[last_tag][-1] = (
                f"{current[last_tag][-1]} {raw_line.strip()}".strip()
            )
            continue
        raise ValueError("RIS contains an unrecognized line")
    if current is not None:
        raise ValueError("RIS record has no end marker")
    return records


def ris_values(record: Mapping[str, list[str]], *tags: str) -> list[str]:
    values: list[str] = []
    for tag in tags:
        for value in record.get(tag, []):
            cleaned = clean_text(value)
            if cleaned:
                values.append(cleaned)
    return values


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def selected_artifacts(
    initial_plan: Mapping[str, Any], repair_plan: Mapping[str, Any]
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path, str]]:
    repaired = {
        (event["partition_id"], event["cell_id"]): event
        for event in repair_plan["events"]
    }
    selected: list[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path, str]] = []
    for initial_event in initial_plan["events"]:
        key = (initial_event["partition_id"], initial_event["cell_id"])
        if key in REPAIRED_KEYS:
            event = repaired[key]
            plan = repair_plan
            root = REPAIR_EVENTS_ROOT
            selection_basis = "corrective_004_adapter_repair"
        else:
            event = initial_event
            plan = initial_plan
            root = FINAL_ROOT
            selection_basis = "initial_complete_source_event"
        selected.append(
            (
                event,
                plan,
                root / event["output_filename"],
                root / event["native_ris_directory"],
                selection_basis,
            )
        )
    return selected


def validate_lineage(
    initial_plan: Mapping[str, Any], repair_plan: Mapping[str, Any]
) -> list[str]:
    errors = [f"initial_plan:{value}" for value in base.validate_plan(initial_plan)]
    errors.extend(f"repair_plan:{value}" for value in repair.validate_plan(repair_plan))
    initial_receipt = base.load(INITIAL_RECEIPT_PATH)
    if not (
        initial_receipt.get("schema_version") == base.RUN_SCHEMA
        and initial_receipt.get("plan_sha256") == base.digest(INITIAL_PLAN_PATH)
        and initial_receipt.get("all_source_cells_attempted") is True
        and initial_receipt.get("attempted_source_cell_count")
        == len(initial_plan["events"])
    ):
        errors.append("initial_run_receipt")
    initial_outcomes = {
        (item.get("partition_id"), item.get("cell_id")): item
        for item in initial_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    for event in initial_plan["events"]:
        key = (event["partition_id"], event["cell_id"])
        if key in REPAIRED_KEYS:
            continue
        outcome = initial_outcomes.get(key)
        if not (
            isinstance(outcome, Mapping)
            and outcome.get("exit_code") == 0
            and outcome.get("artifact_written") is True
            and outcome.get("status") == "success"
        ):
            errors.append(f"initial_event_receipt:{event['event_id']}")

    repair_receipt = base.load(REPAIR_RECEIPT_PATH)
    if not (
        repair_receipt.get("schema_version") == repair.RUN_RECEIPT_SCHEMA
        and repair_receipt.get("plan_sha256") == base.digest(REPAIR_PLAN_PATH)
        and repair_receipt.get("success") is True
        and repair_receipt.get("accepted_source_cell_count")
        == len(repair_plan["events"])
    ):
        errors.append("repair_run_receipt")
    repair_outcomes = {
        item.get("event_id"): item
        for item in repair_receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    for event in repair_plan["events"]:
        outcome = repair_outcomes.get(event["event_id"])
        if not (
            isinstance(outcome, Mapping)
            and outcome.get("success") is True
            and outcome.get("artifact_sha256")
            == base.digest(REPAIR_EVENTS_ROOT / event["output_filename"])
        ):
            errors.append(f"repair_event_receipt:{event['event_id']}")
    return errors


def validate_native_commit_chain(path: Path, native_dir: Path) -> bool:
    marker_path = base.marker_path(path)
    if not marker_path.is_file() or not native_dir.is_dir():
        return False
    marker = base.load(marker_path)
    transaction_id = marker.get("transaction_id")
    native = marker.get("native_ris")
    normalized = marker.get("normalized_json")
    if not (
        marker.get("schema") == base.WILEY_MARKER_SCHEMA
        and isinstance(transaction_id, str)
        and re.fullmatch(r"[0-9a-f]{64}", transaction_id)
        and isinstance(native, Mapping)
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == base.digest(path)
        and normalized.get("bytes") == path.stat().st_size
    ):
        return False
    declarations = native.get("artifacts")
    if not isinstance(declarations, list):
        return False
    declared_names: set[str] = set()
    for declaration in declarations:
        if not isinstance(declaration, Mapping):
            return False
        name = declaration.get("file_name")
        if not isinstance(name, str) or name in declared_names:
            return False
        declared_names.add(name)
        artifact = native_dir / name
        if not (
            artifact.is_file()
            and not artifact.is_symlink()
            and declaration.get("bytes") == artifact.stat().st_size
            and declaration.get("sha256") == base.digest(artifact)
        ):
            return False
    actual_names = {
        item.name
        for item in native_dir.glob("*.ris")
        if item.is_file() and not item.is_symlink()
    }
    if actual_names != declared_names:
        return False
    native_marker_name = native.get("commit_marker_file_name")
    native_marker_path = (
        native_dir / native_marker_name
        if isinstance(native_marker_name, str)
        else Path()
    )
    if not native_marker_path.is_file() or native_marker_path.is_symlink():
        return False
    native_marker = base.load(native_marker_path)
    if not (
        native_marker.get("schema") == "wiley_native_ris_commit_v2"
        and native_marker.get("transaction_id") == transaction_id
        and native_marker.get("native_ris") == native
    ):
        return False
    acknowledgements = []
    for candidate in path.parent.glob(".WILEY_NATIVE_ACK.*.json"):
        try:
            value = base.load(candidate)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if value.get("transaction_id") == transaction_id:
            acknowledgements.append((candidate, value))
    if len(acknowledgements) != 1:
        return False
    acknowledgement_path, acknowledgement = acknowledgements[0]
    normalized_marker = acknowledgement.get("normalized_marker")
    acknowledged_native_marker = acknowledgement.get("native_terminal_marker")
    return bool(
        acknowledgement.get("schema") == "wiley_normalized_native_completion_ack_v2"
        and acknowledgement.get("acknowledgement_file_name")
        == acknowledgement_path.name
        and acknowledgement.get("acknowledgement_commitment")
        == native.get("acknowledgement_commitment")
        and acknowledgement.get("native_ris") == native
        and isinstance(normalized_marker, Mapping)
        and normalized_marker.get("file_name") == marker_path.name
        and normalized_marker.get("sha256") == base.digest(marker_path)
        and normalized_marker.get("bytes") == marker_path.stat().st_size
        and isinstance(acknowledged_native_marker, Mapping)
        and acknowledged_native_marker.get("file_name") == native_marker_path.name
        and acknowledged_native_marker.get("sha256") == base.digest(native_marker_path)
        and acknowledged_native_marker.get("bytes") == native_marker_path.stat().st_size
        and acknowledged_native_marker.get("payload") == native_marker
    )


def validate_native_projection(
    path: Path, native_dir: Path
) -> tuple[bool, dict[str, Any]]:
    artifact = base.load(path)
    rows = artifact.get("results")
    rows = rows if isinstance(rows, list) else []
    native_records: list[dict[str, list[str]]] = []
    page_files = sorted(native_dir.glob("page-*.ris"))
    try:
        for page_file in page_files:
            native_records.extend(
                parse_ris_records(page_file.read_text(encoding="utf-8-sig"))
            )
    except (OSError, UnicodeError, ValueError):
        return False, {"native_source_record_count": None}
    by_doi: dict[str, dict[str, list[str]]] = {}
    duplicate_dois: set[str] = set()
    for record in native_records:
        doi_values = ris_values(record, "DO", "M3")
        doi = normalize_doi(doi_values[0]) if doi_values else ""
        if not doi or doi in by_doi:
            duplicate_dois.add(doi)
        else:
            by_doi[doi] = record
    full_abstracts = 0
    omitted_abstracts = 0
    projection_valid = not duplicate_dois
    for row in rows:
        if not isinstance(row, Mapping):
            projection_valid = False
            continue
        record = by_doi.get(normalize_doi(row.get("doi")))
        if record is None:
            projection_valid = False
            continue
        abstract = remove_email_addresses(" ".join(ris_values(record, "N2", "AB")))
        document_types = ris_values(record, "TY")
        document_type = (
            remove_email_addresses(document_types[0]) if document_types else ""
        )
        if row.get("abstract") != abstract or row.get("documentType") != document_type:
            projection_valid = False
        if abstract:
            full_abstracts += 1
        else:
            omitted_abstracts += 1
    source_total = artifact.get("total")
    projection_valid = bool(
        projection_valid
        and isinstance(source_total, int)
        and len(native_records) == source_total
        and len(by_doi) == source_total
        and full_abstracts + omitted_abstracts == len(rows)
    )
    return projection_valid, {
        "native_page_file_count": len(page_files),
        "native_source_record_count": len(native_records),
        "retained_projection_count": len(rows),
        "full_native_abstract_count": full_abstracts,
        "native_abstract_omission_count": omitted_abstracts,
        "publication_type_projection_count": sum(
            isinstance(row, Mapping)
            and isinstance(row.get("documentType"), str)
            and bool(row["documentType"].strip())
            for row in rows
        ),
    }


def summarize_selected(
    selected: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path, str]],
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    evidence: list[dict[str, Any]] = []
    for event, plan, path, native_dir, selection_basis in selected:
        summary = corrective.normalized_summary(path, event, plan, native_dir)
        projection_valid, projection = validate_native_projection(path, native_dir)
        commit_chain_valid = validate_native_commit_chain(path, native_dir)
        valid = bool(
            summary.get("valid") is True and projection_valid and commit_chain_valid
        )
        if not valid:
            errors.append(f"event:{event['event_id']}")
        evidence.append(
            {
                "event_id": event["event_id"],
                "parent_event_id": event["parent_event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "selection_basis": selection_basis,
                "artifact": base.relative(path),
                "native_ris_directory": base.relative(native_dir),
                "adapter_version": plan["adapter"]["version"],
                "valid": valid,
                "native_commit_chain_valid": commit_chain_valid,
                "native_projection_valid": projection_valid,
                **summary,
                **projection,
            }
        )
    return errors, evidence


def build_manifest(
    initial_plan: Mapping[str, Any],
    repair_plan: Mapping[str, Any],
    selected: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], Path, Path, str]],
) -> dict[str, Any]:
    by_partition: dict[str, list[dict[str, Any]]] = {}
    selection: list[dict[str, Any]] = []
    for event, plan, path, native_dir, selection_basis in selected:
        summary = corrective.normalized_summary(path, event, plan, native_dir)
        if summary.get("valid") is not True:
            raise ValueError(f"Cannot bind incomplete Wiley event {event['event_id']}")
        cell = {
            "cell_id": event["cell_id"],
            "source_id": base.SOURCE_ID,
            "partition_id": event["partition_id"],
            "parent_event_id": event["parent_event_id"],
            "source_run_id": event["event_id"],
            "query": event["query"],
            "requested_query": event["query"],
            "artifact_sha256": base.digest(path),
            "artifact_byte_count": path.stat().st_size,
            "status": "final_complete",
            "report_ready": True,
        }
        by_partition.setdefault(event["partition_id"], []).append(cell)
        selection.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "selection_basis": selection_basis,
                "artifact": base.relative(path),
                "artifact_sha256": base.digest(path),
                "native_ris_directory": base.relative(native_dir),
            }
        )
    events: list[dict[str, Any]] = []
    for partition_id in base.PARTITIONS:
        cells = sorted(
            by_partition.get(partition_id, []), key=lambda item: item["cell_id"]
        )
        if not cells:
            raise ValueError(f"Missing Wiley partition {partition_id}")
        events.append(
            {
                "event_id": base.parent_event_id(partition_id),
                "event_kind": "final",
                "review_namespace": base.REVIEW_NAMESPACE,
                "source_id": base.SOURCE_ID,
                "partition_id": partition_id,
                "status": "final_complete",
                "query_cells": cells,
            }
        )
    return {
        "schema_version": MANIFEST_SCHEMA,
        "created_at_utc": base.now(),
        "review_namespace": base.REVIEW_NAMESPACE,
        "review": {
            "review_id": initial_plan["review_id"],
            "strategy_reference": initial_plan["strategy_reference"],
            "strategy_version": initial_plan["repository_head_at_predeclaration"],
            "phase": initial_plan["phase"],
        },
        "source_union_expected_partitions": list(base.PARTITIONS),
        "source_union_expected_sources": [base.SOURCE_ID],
        "initial_final_plan": {
            "artifact": base.relative(INITIAL_PLAN_PATH),
            "sha256": base.digest(INITIAL_PLAN_PATH),
        },
        "adapter_repair_final_plan": {
            "artifact": base.relative(REPAIR_PLAN_PATH),
            "sha256": base.digest(REPAIR_PLAN_PATH),
        },
        "final_selection": {
            "schema_version": FINAL_SELECTION_SCHEMA,
            "source_cell_count": len(selection),
            "events": selection,
        },
        "events": events,
    }


def source_union(manifest_path: Path, output_path: Path) -> int:
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {manifest_path}")
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    initial_plan = base.load(INITIAL_PLAN_PATH)
    repair_plan = base.load(REPAIR_PLAN_PATH)
    errors = validate_lineage(initial_plan, repair_plan)
    selected = selected_artifacts(initial_plan, repair_plan)
    selected_errors, _evidence = summarize_selected(selected)
    errors.extend(selected_errors)
    if errors:
        raise ValueError("Cannot create Wiley source union: " + ", ".join(errors))
    manifest = build_manifest(initial_plan, repair_plan, selected)
    base.write_new(manifest_path, manifest)
    command = [
        "uv",
        "run",
        str(base.SOURCE_UNION_TOOL),
        "--input",
        *(str(path) for _event, _plan, path, _native, _basis in selected),
        "--output-path",
        str(output_path),
        "--review-namespace",
        base.REVIEW_NAMESPACE,
        "--campaign-manifest",
        str(manifest_path),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "Wiley source union creation failed: "
            + " ".join(completed.stderr.split())[-700:]
        )
    print(json.dumps({"status": "saved", "source_cells": len(selected)}))
    return 0


def assess(manifest_path: Path, source_union_path: Path, output_path: Path) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    initial_plan = base.load(INITIAL_PLAN_PATH)
    repair_plan = base.load(REPAIR_PLAN_PATH)
    errors = validate_lineage(initial_plan, repair_plan)
    selected = selected_artifacts(initial_plan, repair_plan)
    selected_errors, evidence = summarize_selected(selected)
    errors.extend(selected_errors)
    manifest = base.load(manifest_path)
    expected_manifest = build_manifest(initial_plan, repair_plan, selected)
    comparable_saved = dict(manifest)
    comparable_expected = dict(expected_manifest)
    comparable_saved.pop("created_at_utc", None)
    comparable_expected.pop("created_at_utc", None)
    if comparable_saved != comparable_expected:
        errors.append("source_union_manifest")

    union = base.load(source_union_path)
    retained_ids: set[str] = set()
    source_total = 0
    retained_total = 0
    excluded_total = 0
    unresolved_total = 0
    full_abstract_total = 0
    omitted_abstract_total = 0
    publication_types: dict[str, int] = {}
    native_ris_artifacts = 0
    native_ris_bytes = 0
    screenshot_count = 0
    adapter_versions: dict[str, int] = {}
    for item, selected_item in zip(evidence, selected):
        _event, _plan, path, _native_dir, _basis = selected_item
        artifact = base.load(path)
        rows = artifact.get("results")
        rows = rows if isinstance(rows, list) else []
        retained_ids.update(
            row["paperId"]
            for row in rows
            if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
        )
        source_total += item.get("source_total", 0)
        retained_total += item.get("retained_record_count", 0)
        excluded_total += item.get("client_date_excluded_count", 0)
        unresolved_total += item.get("unresolved_exact_date_count", 0)
        full_abstract_total += item.get("full_abstract_count", 0)
        omitted_abstract_total += item.get("source_omitted_abstract_count", 0)
        native_ris_artifacts += item.get("native_ris_artifact_count", 0)
        native_ris_bytes += item.get("native_ris_total_bytes", 0)
        screenshot_count += sum(
            screenshot.get("valid") is True
            for screenshot in item.get("screenshots", [])
            if isinstance(screenshot, Mapping)
        )
        version = str(item.get("adapter_version"))
        adapter_versions[version] = adapter_versions.get(version, 0) + 1
        for document_type, count in item.get("publication_type_counts", {}).items():
            publication_types[document_type] = (
                publication_types.get(document_type, 0) + count
            )

    source_section = union.get("source_unions", {}).get(base.SOURCE_ID, {})
    union_valid = bool(
        union.get("schema_version") == "academic-search-source-union-receipt/v1"
        and union.get("review_namespace") == base.REVIEW_NAMESPACE
        and union.get("review_id") == initial_plan["review_id"]
        and union.get("strategy_reference") == initial_plan["strategy_reference"]
        and union.get("strategy_version")
        == initial_plan["repository_head_at_predeclaration"]
        and union.get("expected_partitions") == list(base.PARTITIONS)
        and union.get("expected_sources") == [base.SOURCE_ID]
        and union.get("completeness_status") == "complete"
        and union.get("failure_status") == "none"
        and source_section.get("raw_record_count") == retained_total
        and source_section.get("event_total_sum") == retained_total
        and set(source_section.get("stable_record_ids", [])) == retained_ids
    )
    if not union_valid:
        errors.append("source_union")
    capture_complete = bool(
        len(evidence) == len(initial_plan["events"])
        and source_total == retained_total + excluded_total
        and full_abstract_total + omitted_abstract_total == retained_total
        and sum(publication_types.values()) == retained_total
        and screenshot_count == 2 * len(evidence)
        and all(
            item.get("valid") is True
            and item.get("all_retained_rows_have_abstract_field") is True
            and item.get("all_retained_rows_have_publication_type") is True
            and item.get("native_projection_valid") is True
            and item.get("native_commit_chain_valid") is True
            for item in evidence
        )
    )
    if not capture_complete:
        errors.append("capture_contract")
    status = "passed" if not errors else "failed"
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": status,
        "source": base.SOURCE,
        "source_id": base.SOURCE_ID,
        "review_namespace": base.REVIEW_NAMESPACE,
        "final_search_partitions_complete": not errors,
        "partition_count": len(base.PARTITIONS),
        "accepted_source_cell_count": len(evidence),
        "lineage": {
            "initial_final_plan": {
                "path": base.relative(INITIAL_PLAN_PATH),
                "sha256": base.digest(INITIAL_PLAN_PATH),
            },
            "initial_run_receipt": {
                "path": base.relative(INITIAL_RECEIPT_PATH),
                "sha256": base.digest(INITIAL_RECEIPT_PATH),
            },
            "adapter_repair_plan": {
                "path": base.relative(REPAIR_PLAN_PATH),
                "sha256": base.digest(REPAIR_PLAN_PATH),
            },
            "adapter_repair_run_receipt": {
                "path": base.relative(REPAIR_RECEIPT_PATH),
                "sha256": base.digest(REPAIR_RECEIPT_PATH),
            },
            "source_union_manifest": {
                "path": base.relative(manifest_path),
                "sha256": base.digest(manifest_path),
            },
            "source_union_receipt": {
                "path": base.relative(source_union_path),
                "sha256": base.digest(source_union_path),
                "valid": union_valid,
            },
            "finalizer": {
                "path": base.relative(SCRIPT_PATH),
                "sha256": base.digest(SCRIPT_PATH),
            },
        },
        "adapter_versions_by_selected_source_cell": dict(
            sorted(adapter_versions.items())
        ),
        "events": evidence,
        "cutoff_accounting": {
            "common_evidence_cutoff": base.DATE_END,
            "source_record_count_before_client_exact_day_filter": source_total,
            "retained_record_count": retained_total,
            "excluded_after_exact_cutoff_count": excluded_total,
            "unresolved_exact_date_count": unresolved_total,
            "complete": source_total == retained_total + excluded_total,
        },
        "abstract_and_publication_type_capture": {
            "source_export": "visible page scoped native RIS export with abstracts",
            "abstract_field": "abstract",
            "abstract_source_tags": ["N2", "AB"],
            "publication_type_field": "documentType",
            "publication_type_source_tag": "TY",
            "retained_rows": retained_total,
            "rows_with_full_native_abstract": full_abstract_total,
            "rows_where_native_ris_omitted_an_abstract": omitted_abstract_total,
            "all_retained_rows_preserve_an_abstract_field": all(
                item.get("all_retained_rows_have_abstract_field") is True
                for item in evidence
            ),
            "all_retained_rows_preserve_a_publication_type": all(
                item.get("all_retained_rows_have_publication_type") is True
                for item in evidence
            ),
            "all_values_match_preserved_native_ris": all(
                item.get("native_projection_valid") is True for item in evidence
            ),
            "publication_type_counts": dict(sorted(publication_types.items())),
            "source_omission_policy": (
                "An empty abstract records Wiley native RIS omission. No result card "
                "description substitutes for a full abstract."
            ),
            "complete": capture_complete,
        },
        "native_ris": {
            "artifact_count": native_ris_artifacts,
            "total_bytes": native_ris_bytes,
            "all_commit_chains_valid": all(
                item.get("native_commit_chain_valid") is True for item in evidence
            ),
        },
        "stable_id_union": {
            "source_event_retained_record_count": retained_total,
            "unique_stable_id_count": len(retained_ids),
            "cross_partition_duplicate_occurrences": retained_total - len(retained_ids),
            "stable_id_set_sha256": base.digest_set(retained_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "screenshots": {
            "expected_png_count": 2 * len(evidence),
            "validated_png_count": screenshot_count,
        },
        "validation_errors": errors,
        "completed_at_utc": base.now(),
    }
    base.write_new(output_path, assessment)
    print(
        json.dumps(
            {
                "status": status,
                "source_records": source_total,
                "retained_records": retained_total,
                "unique_records": len(retained_ids),
                "full_abstract_rows": full_abstract_total,
                "native_abstract_omissions": omitted_abstract_total,
                "publication_type_counts": publication_types,
                "errors": errors,
            }
        )
    )
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    union_parser = commands.add_parser("source-union")
    union_parser.add_argument("--manifest", type=Path, required=True)
    union_parser.add_argument("--output", type=Path, required=True)
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--manifest", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "source-union":
        return source_union(
            args.manifest.resolve(strict=False), args.output.resolve(strict=False)
        )
    return assess(
        args.manifest.resolve(strict=True),
        args.source_union.resolve(strict=True),
        args.output.resolve(strict=False),
    )


if __name__ == "__main__":
    raise SystemExit(main())
