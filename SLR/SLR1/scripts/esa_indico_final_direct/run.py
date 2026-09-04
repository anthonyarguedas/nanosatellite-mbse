#!/usr/bin/env python3
"""Plan, execute, derive, and validate final ESA Indico direct searches."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER_PATH = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/search_esa_indico.py"
)
QUERY_PATH = REPOSITORY_ROOT / "SLR/SLR1/scripts/esa_indico_pilot007/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/esa-indico/source-specific-guidelines.md"
)
CONTRACT_NOTE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/esa-indico/metadata-only-contract-supersession.md"
)
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
FINAL_SEARCH_ROOT = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/esa-indico/final-searches"
)
DEFAULT_OUTPUT_DIR = FINAL_SEARCH_ROOT / "corrective-006"
RESUME_FAILURE_ARTIFACT = FINAL_SEARCH_ROOT / "A1.json"

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
PLAN_SCHEMA = "slr1-esa-indico-final-direct-plan/v1"
RUN_SCHEMA = "slr1-esa-indico-final-direct-run/v1"
VALIDATION_SCHEMA = "slr1-esa-indico-final-direct-validation/v1"
REVIEW_ID = "slr1-1.1-restart"
STRATEGY_REFERENCE = "slr1-esa-indico-main-direct-v6"
CORRECTIVE_SEQUENCE = 6
CUTOFF_DATE = "2026-08-24"
LIMIT = 1000
TIMEOUT_SECONDS = 120.0
MAX_HARVEST_SECONDS = 1800.0
MAX_HARVEST_EVENTS = 10000
REQUEST_RETRIES = 4
REQUEST_INTERVAL_SECONDS = 0.0
EXPECTED_ADAPTER_ID = "search_esa_indico"
EXPECTED_ADAPTER_VERSION = "9"
EXPECTED_MATCHER_SCHEMA = "esa-indico-local-concept-matcher/v3"
DOCUMENT_TYPES = {
    "event": "Event",
    "contribution": "Contribution",
    "subcontribution": "Contribution",
    "attachment": "Material",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def framed_sha256(values: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve(strict=False).relative_to(REPOSITORY_ROOT))


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Required regular file is unavailable: {path}")


def load_json(path: Path) -> dict[str, Any]:
    require_regular(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def copy_new(source: Path, destination: Path) -> None:
    require_regular(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {destination}") from error
    try:
        with source.open("rb") as input_handle, os.fdopen(descriptor, "wb") as output_handle:
            shutil.copyfileobj(input_handle, output_handle, 1024 * 1024)
            output_handle.flush()
            os.fsync(output_handle.fileno())
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def repository_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise RuntimeError("Cannot determine the repository revision")
    return value


def load_module(path: Path, name: str) -> Any:
    require_regular(path)
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_adapter() -> Any:
    adapter = load_module(ADAPTER_PATH, "esa_indico_final_adapter")
    if (
        adapter.ADAPTER_ID != EXPECTED_ADAPTER_ID
        or adapter.ADAPTER_VERSION != EXPECTED_ADAPTER_VERSION
        or adapter.LOCAL_MATCHER_SCHEMA != EXPECTED_MATCHER_SCHEMA
    ):
        raise RuntimeError("The accepted ESA Indico adapter identity changed")
    return adapter


def load_queries() -> Any:
    queries = load_module(QUERY_PATH, "esa_indico_final_queries")
    if tuple(queries.SCHEDULE) != PARTITIONS:
        raise RuntimeError("The accepted ESA Indico partition schedule changed")
    return queries


def marker_path(adapter: Any, output: Path) -> Path:
    return output.with_name(
        f".{output.name}.{adapter.ESA_LOCAL_HARVEST_OUTPUT_MARKER_TAG}.json"
    )


def ledger_path(adapter: Any, output: Path) -> Path:
    return output.with_name(adapter.local_harvest_metadata_ledger_basename(output))


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    return (
        output.with_name(f"{output.stem}.search-page.png"),
        output.with_name(f"{output.stem}.results-page.png"),
    )


def source_bindings() -> dict[str, str]:
    return {
        relative(path): sha256(path)
        for path in (
            SCRIPT_PATH,
            QUERY_PATH,
            SOURCE_GUIDELINE,
            CONTRACT_NOTE,
            DISCOVERY_PROTOCOL,
            MAIN_PROTOCOL,
        )
    }


def build_plan() -> dict[str, Any]:
    adapter = load_adapter()
    queries = load_queries()
    strategy_version = repository_head()
    events = []
    for partition in PARTITIONS:
        query = queries.SCHEDULE[partition]
        events.append(
            {
                "event_id": (
                    f"final-main-{partition}-esa-indico-{CORRECTIVE_SEQUENCE:03d}"
                ),
                "partition_id": partition,
                "semantic_form": queries.SEMANTIC_FORMS[partition],
                "source_construction": queries.SOURCE_CONSTRUCTIONS[partition],
                "query": query,
                "query_sha256": text_sha256(query),
                "query_characters": len(query),
                "output_filename": f"{partition}.json",
                "execution": (
                    "complete_category_0_metadata_harvest_and_local_match"
                    if partition == "A1"
                    else "fixed_A1_ledger_local_match"
                ),
            }
        )
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "source": "ESA Indico",
        "review_namespace": "main",
        "review_id": REVIEW_ID,
        "phase": "identification",
        "strategy_reference": STRATEGY_REFERENCE,
        "corrective_run": {
            "sequence": CORRECTIVE_SEQUENCE,
            "superseded_plan": "../corrective-005/final-event-plan.json",
            "superseded_plan_sha256": sha256(
                FINAL_SEARCH_ROOT / "corrective-005/final-event-plan.json"
            ),
            "failure_receipt": "../corrective-005/failed-run-receipt.json",
            "failure_receipt_sha256": sha256(
                FINAL_SEARCH_ROOT / "corrective-005/failed-run-receipt.json"
            ),
            "resume_failure_artifact": "../A1.json",
            "resume_failure_artifact_sha256": sha256(RESUME_FAILURE_ARTIFACT),
            "resume_terminal_marker": "../.A1.json.ESA_INDICO_HARVEST_COMMIT.json",
            "resume_terminal_marker_sha256": sha256(
                FINAL_SEARCH_ROOT / ".A1.json.ESA_INDICO_HARVEST_COMMIT.json"
            ),
            "reason": (
                "Revalidate the marker-bound 441-event prefix whose ordered root "
                "snapshot again matches the live root, then require a matching final snapshot."
            ),
        },
        "cutoff": {
            "exact_common_cutoff": CUTOFF_DATE,
            "source_filter": None,
            "handling": "Apply the evidence window during candidate screening.",
        },
        "source_configuration": {
            "category_id": 0,
            "category_scope": "selected category and descendants",
            "result_types": ["events", "contributions", "materials"],
            "covered_native_record_types": [
                "event",
                "contribution",
                "subcontribution",
                "attachment",
            ],
            "date_filter": None,
            "language_filter": None,
            "publication_type_filter": None,
            "access_filter": None,
            "full_text_filter": None,
            "attachment_body_requests": False,
        },
        "capture_contract": {
            "one_complete_source_harvest": True,
            "anchor_partition": "A1",
            "two_equal_ordered_root_snapshots": True,
            "every_event_export_required": True,
            "full_metadata_ledger_required": True,
            "recompute_anchor_gate_before_each_derivative": True,
            "derivative_sidecars_are_query_bound_seals_of_the_same_fixed_records": True,
            "full_abstract_field": "abstract",
            "full_abstract_source": "complete event-export description metadata",
            "publication_type_field": "documentType",
            "publication_type_semantics": "source record class, without reviewer coding",
            "screenshots_required": True,
        },
        "controls": {
            "limit": LIMIT,
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_harvest_seconds": MAX_HARVEST_SECONDS,
            "max_harvest_events": MAX_HARVEST_EVENTS,
            "local_request_retries": REQUEST_RETRIES,
            "minimum_request_start_interval_seconds": REQUEST_INTERVAL_SECONDS,
        },
        "translation": {
            "literal": "one straight-double-quoted lexical literal",
            "boolean": "uppercase AND and OR with explicit parentheses",
            "wildcard": False,
            "controlled_vocabulary_supplement": False,
            "matching_fields": {
                "event": ["title", "description", "keywords"],
                "contribution": ["title", "description", "keywords"],
                "subcontribution": ["title", "description", "keywords"],
                "attachment": ["title", "filename", "description"],
            },
        },
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
            "sha256": sha256(ADAPTER_PATH),
            "matcher_schema": adapter.LOCAL_MATCHER_SCHEMA,
            "entrypoint": "~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py",
        },
        "bindings": {"files": source_bindings()},
        "event_count": len(events),
        "events": events,
    }


def validate_plan(plan: Mapping[str, Any]) -> None:
    adapter = load_adapter()
    queries = load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise RuntimeError("Unexpected ESA final plan schema")
    if plan.get("event_count") != len(PARTITIONS):
        raise RuntimeError("ESA final plan is incomplete")
    events = plan.get("events")
    if not isinstance(events, list) or [event.get("partition_id") for event in events] != list(PARTITIONS):
        raise RuntimeError("ESA final plan partition order changed")
    for event in events:
        partition = event["partition_id"]
        query = queries.SCHEDULE[partition]
        if event.get("query") != query or event.get("query_sha256") != text_sha256(query):
            raise RuntimeError(f"{partition}: predeclared query changed")
    declared_adapter = plan.get("adapter")
    if not isinstance(declared_adapter, Mapping) or declared_adapter.get("id") != adapter.ADAPTER_ID:
        raise RuntimeError("ESA final plan adapter ID changed")
    if declared_adapter.get("version") != adapter.ADAPTER_VERSION or declared_adapter.get("sha256") != sha256(ADAPTER_PATH):
        raise RuntimeError("ESA final plan adapter changed")
    if plan.get("bindings", {}).get("files") != source_bindings():
        raise RuntimeError("A source-affecting file changed after predeclaration")


def anchor_command(plan: Mapping[str, Any], output_dir: Path) -> list[str]:
    event = plan["events"][0]
    return [
        "uv",
        "run",
        str(ADAPTER_PATH),
        "--query",
        event["query"],
        "--limit",
        str(LIMIT),
        "--category-id",
        "0",
        "--timeout",
        str(TIMEOUT_SECONDS),
        "--max-harvest-seconds",
        str(MAX_HARVEST_SECONDS),
        "--max-harvest-events",
        str(MAX_HARVEST_EVENTS),
        "--local-request-retries",
        str(REQUEST_RETRIES),
        "--min-request-start-interval-seconds",
        str(REQUEST_INTERVAL_SECONDS),
        "--require-complete",
        "--resume-state-path",
        str(RESUME_FAILURE_ARTIFACT),
        "--fresh-browser",
        "--headless",
        "--output-path",
        str(output_dir / event["output_filename"]),
        "--prisma-run-id",
        event["event_id"],
        "--prisma-review-id",
        REVIEW_ID,
        "--prisma-strategy-reference",
        STRATEGY_REFERENCE,
        "--prisma-strategy-version",
        str(plan["repository_head_at_predeclaration"]),
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        "A1",
        "--prisma-partition-label",
        "ESA Indico final A1",
        "--prisma-partition-description",
        "Exact A1 expression over the complete category 0 public metadata harvest.",
        "--prisma-source-total-not-reported",
        "--prisma-source-total-not-exact",
    ]


def execute_anchor(plan: Mapping[str, Any], output_dir: Path) -> None:
    validate_plan(plan)
    output = output_dir / "A1.json"
    adapter = load_adapter()
    reserved = [output, marker_path(adapter, output), ledger_path(adapter, output), *screenshot_paths(output)]
    if any(path.exists() or path.is_symlink() for path in reserved):
        raise RuntimeError("Refusing to overwrite an existing A1 transaction")
    command = anchor_command(plan, output_dir)
    completed = subprocess.run(command, cwd=REPOSITORY_ROOT, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ESA A1 complete harvest failed with exit code {completed.returncode}")


def _screenshot_receipt_is_valid(adapter: Any, output: Path, data: Mapping[str, Any]) -> bool:
    metadata = data.get("output_metadata")
    screenshots = metadata.get("screenshots") if isinstance(metadata, Mapping) else None
    if not isinstance(screenshots, Mapping):
        return False
    search_path, results_path = screenshot_paths(output)
    for key, expected_path in (("search_page", search_path), ("results_page", results_path)):
        entry = screenshots.get(key)
        if not isinstance(entry, Mapping) or entry.get("path") != expected_path.name:
            return False
        try:
            require_regular(expected_path)
            dimensions = adapter._png_dimensions(expected_path)
        except (OSError, RuntimeError, Exception):
            return False
        if entry.get("sha256") != sha256(expected_path) or any(
            entry.get(name) != value for name, value in dimensions.items()
        ):
            return False
    return True


def _match_identities(adapter: Any, ledger: Mapping[str, Any], query: str) -> list[str]:
    expression = adapter.parse_local_concept_expression(query)
    budget = adapter._LocalMatchBudget()
    compiled = adapter._compile_local_query(expression, budget)
    identities = ledger.get("record_identities")
    records = ledger.get("records")
    if not isinstance(identities, list) or not isinstance(records, list) or len(identities) != len(records):
        raise RuntimeError("ESA ledger record arrays do not reconcile")
    matched: list[str] = []
    for identity, record in zip(identities, records):
        budget.charge()
        if adapter.local_concept_match(record, expression, _compiled=compiled, _budget=budget):
            matched.append(identity)
    return matched


def validate_transaction(
    adapter: Any,
    output: Path,
    expected_query: str,
    *,
    expected_partition: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    data = load_json(output)
    marker = load_json(marker_path(adapter, output))
    ledger = load_json(ledger_path(adapter, output))
    metadata = data.get("output_metadata")
    receipt = metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    descriptor = metadata.get("esa_metadata_ledger") if isinstance(metadata, Mapping) else None
    if (
        data.get("schema_version") != "academic-search-result/v1"
        or not isinstance(metadata, Mapping)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("merge_eligible") is not True
        or not isinstance(receipt, Mapping)
        or receipt.get("completion_status") != "complete"
        or receipt.get("report_ready") is not True
        or not isinstance(descriptor, Mapping)
    ):
        raise RuntimeError(f"{expected_partition}: compact transaction is incomplete")
    if data.get("requested_query") != expected_query or data.get("query") != expected_query:
        raise RuntimeError(f"{expected_partition}: requested query changed")
    if receipt.get("coverage", {}).get("partition_id") != expected_partition:
        raise RuntimeError(f"{expected_partition}: PRISMA partition binding changed")
    if receipt.get("adapter", {}).get("adapter_version") != adapter.ADAPTER_VERSION:
        raise RuntimeError(f"{expected_partition}: adapter version binding changed")
    if descriptor.get("sidecar_basename") != ledger_path(adapter, output).name:
        raise RuntimeError(f"{expected_partition}: ledger basename binding changed")
    if marker.get("schema") != adapter.ESA_LOCAL_HARVEST_OUTPUT_COMMIT_SCHEMA:
        raise RuntimeError(f"{expected_partition}: terminal marker schema changed")
    if marker.get("esa_metadata_ledger") != descriptor:
        raise RuntimeError(f"{expected_partition}: marker ledger binding changed")
    normalized_json = marker.get("normalized_json")
    if not isinstance(normalized_json, Mapping) or normalized_json.get("sha256") != sha256(output) or normalized_json.get("bytes") != output.stat().st_size:
        raise RuntimeError(f"{expected_partition}: compact artifact marker digest changed")
    if descriptor.get("payload_sha256") != adapter._checkpoint_canonical_sha256(ledger):
        raise RuntimeError(f"{expected_partition}: ledger payload digest changed")
    if ledger.get("adapter") != {"id": adapter.ADAPTER_ID, "version": adapter.ADAPTER_VERSION}:
        raise RuntimeError(f"{expected_partition}: ledger adapter binding changed")
    publication = ledger.get("publication")
    if not isinstance(publication, Mapping) or publication.get("requested_query") != expected_query:
        raise RuntimeError(f"{expected_partition}: ledger query binding changed")
    if publication.get("requested_query_sha256") != text_sha256(expected_query):
        raise RuntimeError(f"{expected_partition}: ledger query digest changed")
    if publication.get("executed_expression") != data.get("executed_query"):
        raise RuntimeError(f"{expected_partition}: executed expression changed")
    controls = publication.get("effective_controls")
    if not isinstance(controls, Mapping) or controls.get("year_start") is not None or controls.get("year_end") is not None:
        raise RuntimeError(f"{expected_partition}: an undeclared date filter was applied")
    if controls.get("category_id") != 0 or controls.get("result_types") != ["events", "contributions", "materials"]:
        raise RuntimeError(f"{expected_partition}: source controls changed")
    snapshots = ledger.get("root_snapshots")
    first = snapshots.get("first") if isinstance(snapshots, Mapping) else None
    second = snapshots.get("second") if isinstance(snapshots, Mapping) else None
    if not isinstance(first, Mapping) or first != second or first.get("category_id") != 0:
        raise RuntimeError(f"{expected_partition}: root snapshots do not match")
    event_ids = first.get("event_ids")
    if not isinstance(event_ids, list) or first.get("reported_count") != len(event_ids) or first.get("ordered_event_ids_sha256") != framed_sha256(event_ids):
        raise RuntimeError(f"{expected_partition}: root event ledger changed")
    records = ledger.get("records")
    identities = ledger.get("record_identities")
    if not isinstance(records, list) or not isinstance(identities, list) or len(records) != len(identities):
        raise RuntimeError(f"{expected_partition}: ledger records changed")
    observed_identities = [f"{row['source_type']}:{row['event_id']}:{row['source_id']}" for row in records]
    if identities != observed_identities or len(set(identities)) != len(identities):
        raise RuntimeError(f"{expected_partition}: stable record identities changed")
    if ledger.get("records_sha256") != adapter._checkpoint_canonical_sha256(records) or descriptor.get("records_sha256") != ledger.get("records_sha256"):
        raise RuntimeError(f"{expected_partition}: fixed-record digest changed")
    witnesses = ledger.get("event_export_witnesses")
    if not isinstance(witnesses, list) or len(witnesses) != len(event_ids):
        raise RuntimeError(f"{expected_partition}: event witness coverage changed")
    if ledger.get("attachment_bodies_persisted") is not False:
        raise RuntimeError(f"{expected_partition}: attachment body boundary changed")
    recomputed_matches = _match_identities(adapter, ledger, expected_query)
    matches = ledger.get("matches")
    if not isinstance(matches, Mapping) or matches.get("matched_record_identities") != recomputed_matches:
        raise RuntimeError(f"{expected_partition}: local matches do not rebuild")
    rows = data.get("results")
    if not isinstance(rows, list) or data.get("total") != len(rows) or len(rows) != len(recomputed_matches):
        raise RuntimeError(f"{expected_partition}: compact result count changed")
    records_by_identity = dict(zip(identities, records))
    for row, identity in zip(rows, recomputed_matches):
        source = records_by_identity[identity]
        expected_abstract = adapter.clean_text(source.get("description"))
        if (
            row.get("paperId") != source.get("paper_id")
            or row.get("title") != source.get("title")
            or row.get("abstract") != expected_abstract
            or row.get("documentType") != DOCUMENT_TYPES[source["source_type"]]
        ):
            raise RuntimeError(f"{expected_partition}: abstract or publication type projection changed")
    if not _screenshot_receipt_is_valid(adapter, output, data):
        raise RuntimeError(f"{expected_partition}: screenshot evidence changed")
    return data, marker, ledger


def _source_records(ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    records = []
    for value in ledger["records"]:
        record = dict(value)
        record.pop("paper_id", None)
        records.append(record)
    return records


def _universe(adapter: Any, ledger: Mapping[str, Any]) -> dict[str, Any]:
    first = ledger["root_snapshots"]["first"]
    second = ledger["root_snapshots"]["second"]
    event_ids = list(first["event_ids"])
    return {
        "schema": adapter.LOCAL_SOURCE_UNIVERSE_SCHEMA,
        "kind": "global_root_category_event_universe",
        "category_id": 0,
        "scope_kind": "global",
        "endpoint_path": "/export/categ/0.json",
        "reported_count": len(event_ids),
        "enumerated_count": len(event_ids),
        "complete_marker": None,
        "snapshot_reconciled": True,
        "complete": True,
        "completeness_proof": "two_matching_native_category_export_snapshots",
        "global_coverage": "proven_two_matching_root_snapshots",
        "event_ids": event_ids,
        "events": [{"event_id": event_id} for event_id in event_ids],
        "ordered_event_ids_sha256": first["ordered_event_ids_sha256"],
        "root_snapshot_ledgers": {"first": copy.deepcopy(first), "second": copy.deepcopy(second)},
    }


def _prisma_context(
    adapter: Any,
    plan: Mapping[str, Any],
    event: Mapping[str, Any],
    started_at_utc: str,
) -> dict[str, Any]:
    return {
        "run_id": event["event_id"],
        "run_id_provenance": "explicitly_supplied",
        "review_id": REVIEW_ID,
        "strategy_reference": STRATEGY_REFERENCE,
        "strategy_version": plan["repository_head_at_predeclaration"],
        "phase": "identification",
        "coverage": {
            "coverage_scope": "partition",
            "partition_id": event["partition_id"],
            "partition_label": f"ESA Indico final {event['partition_id']}",
            "partition_description": (
                f"Exact {event['partition_id']} expression evaluated over the fixed complete "
                "category 0 metadata ledger."
            ),
        },
        "started_at_utc": started_at_utc,
        "started_at_provenance": "shared_complete_harvest_observation",
        "adapter": {
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": sha256(ADAPTER_PATH),
            "script_hash_provenance": "sha256_regular_file",
        },
    }


def _clone_screenshot_evidence(
    adapter: Any,
    anchor_data: Mapping[str, Any],
    anchor_output: Path,
    output: Path,
) -> dict[str, Any]:
    anchor_screens = anchor_data["output_metadata"]["screenshots"]
    anchor_paths = screenshot_paths(anchor_output)
    output_paths = screenshot_paths(output)
    copied: list[Path] = []
    try:
        for source, destination in zip(anchor_paths, output_paths):
            copy_new(source, destination)
            copied.append(destination)
        evidence: dict[str, Any] = {}
        for key, destination in zip(("search_page", "results_page"), output_paths):
            source_entry = anchor_screens[key]
            entry = dict(source_entry)
            entry["path"] = destination.name
            entry["sha256"] = sha256(destination)
            entry.update(adapter._png_dimensions(destination))
            evidence[key] = entry
        return evidence
    except Exception:
        for path in copied:
            path.unlink(missing_ok=True)
        raise


def derive_partition(
    adapter: Any,
    plan: Mapping[str, Any],
    event: Mapping[str, Any],
    output_dir: Path,
) -> None:
    partition = event["partition_id"]
    output = output_dir / event["output_filename"]
    anchor_output = output_dir / "A1.json"
    anchor_data, _anchor_marker, anchor_ledger = validate_transaction(
        adapter,
        anchor_output,
        plan["events"][0]["query"],
        expected_partition="A1",
    )
    if any(
        path.exists() or path.is_symlink()
        for path in (output, marker_path(adapter, output), ledger_path(adapter, output), *screenshot_paths(output))
    ):
        raise RuntimeError(f"Refusing to overwrite the {partition} transaction")
    records = _source_records(anchor_ledger)
    universe = _universe(adapter, anchor_ledger)
    settings = anchor_ledger["publication"]["effective_controls"]["effective_harvest_settings"]
    query = event["query"]
    checkpoint = adapter._local_checkpoint(
        query=query,
        category_id=0,
        universe=universe,
        next_event_index=len(universe["event_ids"]),
        completed_event_ids=universe["event_ids"],
        records=records,
        source_states=[],
        state="exhausted",
        settings=settings,
    )
    harvested = adapter._local_match_harvested_records(
        records,
        query=query,
        limit=LIMIT,
        year_start=None,
        year_end=None,
        count_only=False,
        universe=universe,
        checkpoint=checkpoint,
    )
    anchor_receipt = anchor_data["output_metadata"]["prisma_search_run"]
    completed_at = anchor_receipt.get("completed_at_utc") or now()
    started_at = completed_at
    metadata = adapter._local_harvest_metadata(
        harvested,
        query=query,
        requested_groups=adapter.LOCAL_RESULT_GROUPS,
        category_scope={"category_id": 0, "id_path": [0], "path": "0"},
        limit=LIMIT,
        year_start=None,
        year_end=None,
        timeout_seconds=float(settings["timeout_seconds"]),
        page_delay_seconds=float(settings["page_delay_seconds"]),
        count_only=False,
        max_events=int(settings["max_events"]),
        max_harvest_seconds=float(settings["max_harvest_seconds"]),
        request_retries=int(settings["request_retries"]),
        request_start_interval_seconds=float(settings["request_start_interval_seconds"]),
        retry_telemetry=[],
        started_at_utc=started_at,
        completed_at_utc=completed_at,
    )
    metadata["fixed_metadata_ledger_derivation"] = {
        "schema": "esa-indico-fixed-ledger-derivation/v1",
        "anchor_partition": "A1",
        "anchor_transaction_id": anchor_ledger["publication"]["transaction_id"],
        "anchor_records_sha256": anchor_ledger["records_sha256"],
        "anchor_event_ids_sha256": anchor_ledger["root_snapshots"]["first"]["ordered_event_ids_sha256"],
        "source_requests": 0,
        "browser_requests": 0,
        "attachment_body_requests": 0,
    }
    context = adapter._local_prisma_context(
        _prisma_context(adapter, plan, event, started_at),
        record_count=harvested["record_count"],
        local_match_count=harvested["matched_count"],
        year_excluded=0,
        client_side_exclusions=harvested["client_side_exclusions"],
        within_source_duplicates_removed=0,
        malformed_records_dropped=0,
        source_total_scope=(
            "not_reported_by_source; local match count is separate from the complete "
            "harvested export universe"
        ),
        normalized_rows_written=harvested["normalized_rows_written"],
        attachment_metadata=harvested["attachment_metadata"],
    )
    result = adapter.finalize_search_result(
        {
            "query": query,
            "total": harvested["matched_count"],
            "pages_retrieved": harvested["event_count"] + 3,
            "results_retrieved": len(harvested["records"]),
            "results": harvested["records"],
            "output_metadata": metadata,
        },
        source=adapter.SOURCE_NAME,
        executed_query=metadata["matching_operation_text"],
        merge_eligible=True,
        prisma_context=context,
    )
    result_metadata = result["output_metadata"]
    result_metadata["local_harvest"]["resume"] = copy.deepcopy(checkpoint)
    result_metadata["require_complete"] = True
    result_metadata["local_harvest_requested"] = False
    screenshot_evidence = _clone_screenshot_evidence(
        adapter, anchor_data, anchor_output, output
    )
    adapter._attach_automatic_screenshot_evidence(
        result, screenshot_evidence, route="complete_local_harvest_fixed_ledger_derivative"
    )
    result_metadata["fixed_ledger_screenshot_provenance"] = {
        "schema": "esa-indico-fixed-ledger-screenshot-provenance/v1",
        "anchor_partition": "A1",
        "same_complete_harvest": True,
    }
    try:
        adapter._save_search_result(
            result,
            output,
            prisma_context=context,
        )
    except Exception:
        for path in screenshot_paths(output):
            path.unlink(missing_ok=True)
        raise


def derive_all(plan: Mapping[str, Any], output_dir: Path) -> None:
    validate_plan(plan)
    adapter = load_adapter()
    validate_transaction(
        adapter,
        output_dir / "A1.json",
        plan["events"][0]["query"],
        expected_partition="A1",
    )
    for event in plan["events"][1:]:
        derive_partition(adapter, plan, event, output_dir)
        validate_transaction(
            adapter,
            output_dir / event["output_filename"],
            event["query"],
            expected_partition=event["partition_id"],
        )
        print(f"Completed fixed-ledger derivative {event['partition_id']}")


def _artifact_summary(
    adapter: Any,
    output: Path,
    data: Mapping[str, Any],
    ledger: Mapping[str, Any],
) -> dict[str, Any]:
    rows = data["results"]
    type_counts = Counter(str(row.get("documentType")) for row in rows)
    source_type_counts = Counter(str(row.get("sourceType")) for row in rows)
    full_abstracts = sum(bool(row.get("abstract")) for row in rows)
    blank_abstracts = len(rows) - full_abstracts
    search_page, results_page = screenshot_paths(output)
    return {
        "partition_id": data["output_metadata"]["prisma_search_run"]["coverage"]["partition_id"],
        "artifact": output.name,
        "artifact_sha256": sha256(output),
        "terminal_marker": marker_path(adapter, output).name,
        "terminal_marker_sha256": sha256(marker_path(adapter, output)),
        "metadata_ledger": ledger_path(adapter, output).name,
        "metadata_ledger_sha256": sha256(ledger_path(adapter, output)),
        "records_sha256": ledger["records_sha256"],
        "root_event_ids_sha256": ledger["root_snapshots"]["first"]["ordered_event_ids_sha256"],
        "total": data["total"],
        "source_types": dict(sorted(source_type_counts.items())),
        "publication_types": dict(sorted(type_counts.items())),
        "publication_type_field": "documentType",
        "abstract_capture": {
            "field": "abstract",
            "full_source_description_count": full_abstracts,
            "source_description_not_available_count": blank_abstracts,
            "projection_mismatch_count": 0,
        },
        "screenshots": {
            "search_page": {"path": search_page.name, "sha256": sha256(search_page)},
            "results_page": {"path": results_page.name, "sha256": sha256(results_page)},
        },
        "status": "complete",
    }


def build_receipts(plan: Mapping[str, Any], output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_plan(plan)
    adapter = load_adapter()
    events: list[dict[str, Any]] = []
    matched_memberships: dict[str, list[str]] = {}
    source_order: list[str] | None = None
    fixed_records_sha: str | None = None
    fixed_root_sha: str | None = None
    ledger_record_count: int | None = None
    event_count: int | None = None
    for event in plan["events"]:
        partition = event["partition_id"]
        output = output_dir / event["output_filename"]
        data, _marker, ledger = validate_transaction(
            adapter, output, event["query"], expected_partition=partition
        )
        events.append(_artifact_summary(adapter, output, data, ledger))
        records_sha = ledger["records_sha256"]
        root_sha = ledger["root_snapshots"]["first"]["ordered_event_ids_sha256"]
        if fixed_records_sha is None:
            fixed_records_sha = records_sha
            fixed_root_sha = root_sha
            source_order = list(ledger["record_identities"])
            ledger_record_count = len(source_order)
            event_count = ledger["root_snapshots"]["first"]["reported_count"]
        elif records_sha != fixed_records_sha or root_sha != fixed_root_sha or ledger["record_identities"] != source_order:
            raise RuntimeError(f"{partition}: derivative did not retain the fixed ledger")
        for identity in ledger["matches"]["matched_record_identities"]:
            matched_memberships.setdefault(identity, []).append(partition)
    assert source_order is not None and fixed_records_sha is not None and fixed_root_sha is not None
    union = [identity for identity in source_order if identity in matched_memberships]
    completed_at = now()
    run_receipt = {
        "schema_version": RUN_SCHEMA,
        "source": "ESA Indico",
        "status": "complete",
        "completed_at_utc": completed_at,
        "plan": "final-event-plan.json",
        "plan_sha256": sha256(output_dir / "final-event-plan.json"),
        "adapter": plan["adapter"],
        "execution": {
            "complete_source_harvest_count": 1,
            "anchor_partition": "A1",
            "fixed_ledger_derivative_count": len(PARTITIONS) - 1,
            "anchor_gate_recomputed_before_every_derivative": True,
            "attachment_body_requests": 0,
            "date_filter_applied": False,
            "language_filter_applied": False,
            "publication_type_filter_applied": False,
        },
        "fixed_source_corpus": {
            "category_id": 0,
            "root_event_count": event_count,
            "normalized_metadata_record_count": ledger_record_count,
            "records_sha256": fixed_records_sha,
            "ordered_event_ids_sha256": fixed_root_sha,
            "root_snapshots_equal": True,
        },
        "event_count": len(events),
        "completed_event_count": len(events),
        "failed_event_count": 0,
        "events": events,
        "schedule_union": {
            "matched_record_count": len(union),
            "matched_record_identities": union,
            "partition_memberships": {identity: matched_memberships[identity] for identity in union},
        },
        "metadata_capture": {
            "full_abstracts_saved": True,
            "abstract_field": "abstract",
            "abstract_source": "full normalized ESA event-export description",
            "blank_abstracts_mean_source_description_not_available": True,
            "publication_types_saved": True,
            "publication_type_field": "documentType",
            "publication_type_is_source_record_class": True,
            "reviewer_publication_type_not_inferred": True,
        },
    }
    validation = {
        "schema_version": VALIDATION_SCHEMA,
        "source": "ESA Indico",
        "status": "pass",
        "validated_at_utc": completed_at,
        "checks": {
            "plan_and_file_bindings": "pass",
            "adapter_identity": "pass",
            "nine_partition_transactions": "pass",
            "nine_terminal_markers": "pass",
            "nine_full_metadata_ledgers": "pass",
            "mandatory_screenshot_pairs": "pass",
            "equal_root_snapshots": "pass",
            "all_event_export_witnesses": "pass",
            "fixed_record_order_and_digest": "pass",
            "exact_local_match_rebuilds": "pass",
            "full_abstract_projection": "pass",
            "publication_type_projection": "pass",
            "no_attachment_bodies": "pass",
            "no_search_date_filter": "pass",
        },
        "partition_totals": {event["partition_id"]: event["total"] for event in events},
        "schedule_union_records": len(union),
        "fixed_source_corpus": run_receipt["fixed_source_corpus"],
        "artifacts": {
            event["artifact"]: event["artifact_sha256"] for event in events
        },
    }
    return run_receipt, validation


def write_receipts(plan: Mapping[str, Any], output_dir: Path) -> None:
    receipt_path = output_dir / "run-receipt.json"
    validation_path = output_dir / "validation-report.json"
    if receipt_path.exists() or validation_path.exists():
        raise RuntimeError("Refusing to overwrite final ESA receipts")
    run_receipt, validation = build_receipts(plan, output_dir)
    write_new_json(receipt_path, run_receipt)
    write_new_json(validation_path, validation)


def validate_persisted(plan: Mapping[str, Any], output_dir: Path) -> None:
    expected_receipt, expected_validation = build_receipts(plan, output_dir)
    observed_receipt = load_json(output_dir / "run-receipt.json")
    observed_validation = load_json(output_dir / "validation-report.json")
    expected_receipt["completed_at_utc"] = observed_receipt.get("completed_at_utc")
    expected_validation["validated_at_utc"] = observed_validation.get("validated_at_utc")
    if observed_receipt != expected_receipt:
        raise RuntimeError("ESA final run receipt does not rebuild")
    if observed_validation != expected_validation:
        raise RuntimeError("ESA final validation report does not rebuild")
    print(
        "Validated ESA Indico final searches: "
        f"{observed_receipt['schedule_union']['matched_record_count']} union records"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("plan", "harvest", "derive", "receipt", "validate", "run")
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve(strict=False)
    plan_path = output_dir / "final-event-plan.json"

    if args.action in {"plan", "run"}:
        write_new_json(plan_path, build_plan())
        print(f"Wrote {plan_path}")
    plan = load_json(plan_path)
    if args.action in {"harvest", "run"}:
        execute_anchor(plan, output_dir)
        print("Completed ESA Indico category 0 harvest and A1")
    if args.action in {"derive", "run"}:
        derive_all(plan, output_dir)
    if args.action in {"receipt", "run"}:
        write_receipts(plan, output_dir)
    if args.action in {"validate", "run"}:
        validate_persisted(plan, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
