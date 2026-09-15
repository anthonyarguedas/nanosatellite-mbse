"""Shared validation and matching helpers for ESA Indico Pilot 007."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from queries import QUERY_SHA256, SCHEDULE

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
PILOT006_ROOT = SLR1_ROOT / "source-specific" / "esa-indico" / "pilots" / "006"
PILOT007_ROOT = SLR1_ROOT / "source-specific" / "esa-indico" / "pilots" / "007"
SEARCH_ROOT = PILOT007_ROOT / "searches"
SOURCE_ARTIFACT = PILOT006_ROOT / "searches" / "A1-r15.json"
SOURCE_MARKER = (
    PILOT006_ROOT / "searches" / ".A1-r15.json.ESA_INDICO_HARVEST_COMMIT.json"
)
SOURCE_LEDGER = (
    PILOT006_ROOT / "searches" / ".A1-r15.json.ESA_INDICO_METADATA_LEDGER.json"
)
ADAPTER_PATH = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/search_esa_indico.py"
)
MERGE_ENTRYPOINT = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/merge_search_results.py"
)
SOURCE_NAME = "ESA Indico"
PILOT = "007"
EXPECTED_ADAPTER_ID = "search_esa_indico"
EXPECTED_ADAPTER_VERSION = "8"
EXPECTED_MATCHER_SCHEMA = "esa-indico-local-concept-matcher/v3"
EXPECTED_LEDGER_SCHEMA = "esa-indico-v8-metadata-ledger/v1"
MAX_JSON_BYTES = 100_000_000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def relative_to_repository(path: Path) -> str:
    return str(path.resolve().relative_to(REPOSITORY_ROOT.resolve()))


def relative_to_pilot(path: Path) -> str:
    return str(path.resolve().relative_to(PILOT007_ROOT.resolve()))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_regular_file(path: Path, *, maximum_bytes: int = MAX_JSON_BYTES) -> None:
    try:
        value = path.lstat()
    except OSError as error:
        raise RuntimeError(f"Required evidence is unavailable: {path}") from error
    require(stat.S_ISREG(value.st_mode), f"Evidence must be a regular file: {path}")
    require(value.st_size <= maximum_bytes, f"Evidence exceeds its byte bound: {path}")


def load_json(path: Path, *, maximum_bytes: int = MAX_JSON_BYTES) -> dict[str, Any]:
    _require_regular_file(path, maximum_bytes=maximum_bytes)
    try:
        raw = path.read_bytes()
        require(len(raw) <= maximum_bytes, f"JSON exceeds its byte bound: {path}")
        value = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read JSON evidence: {path}") from error
    require(isinstance(value, dict), f"Expected a JSON object in {path}")
    return value


def write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
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


def _load_module(path: Path, name: str) -> Any:
    _require_regular_file(path, maximum_bytes=2_000_000)
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_adapter() -> Any:
    adapter = _load_module(ADAPTER_PATH, "esa_indico_pilot007_adapter")
    require(adapter.ADAPTER_ID == EXPECTED_ADAPTER_ID, "Unexpected ESA adapter ID")
    require(
        adapter.ADAPTER_VERSION == EXPECTED_ADAPTER_VERSION,
        "ESA Pilot 007 requires adapter v8",
    )
    require(
        adapter.LOCAL_MATCHER_SCHEMA == EXPECTED_MATCHER_SCHEMA,
        "Unexpected ESA local matcher schema",
    )
    return adapter


def load_merge_entrypoint() -> Any:
    module = _load_module(MERGE_ENTRYPOINT, "esa_indico_pilot007_merge_entrypoint")
    require(
        callable(getattr(module, "verify_esa_indico_v8_metadata_harvest", None)),
        "The shared ESA v8 harvest gate is unavailable",
    )
    return module


def _receipt_adapter(source: Mapping[str, Any]) -> Mapping[str, Any]:
    metadata = source.get("output_metadata")
    receipt = (
        metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    )
    adapter = receipt.get("adapter") if isinstance(receipt, Mapping) else None
    require(isinstance(adapter, Mapping), "The source corpus lacks adapter provenance")
    return adapter


def corpus_binding(
    source: Mapping[str, Any],
    marker: Mapping[str, Any],
    ledger: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = source.get("output_metadata")
    require(isinstance(metadata, Mapping), "The source corpus lacks output metadata")
    descriptor = metadata.get("esa_metadata_ledger")
    require(
        isinstance(descriptor, Mapping), "The source corpus lacks a ledger descriptor"
    )
    receipt = metadata.get("prisma_search_run")
    require(isinstance(receipt, Mapping), "The source corpus lacks a PRISMA receipt")
    snapshots = ledger.get("root_snapshots")
    require(isinstance(snapshots, Mapping), "The source ledger lacks root snapshots")
    first = snapshots.get("first")
    second = snapshots.get("second")
    require(
        isinstance(first, Mapping) and first == second, "Root snapshots do not match"
    )
    counts = ledger.get("counts")
    require(isinstance(counts, Mapping), "The source ledger lacks counts")
    source_adapter = _receipt_adapter(source)
    return {
        "compact_artifact": relative_to_repository(SOURCE_ARTIFACT),
        "compact_artifact_sha256": file_sha256(SOURCE_ARTIFACT),
        "terminal_marker": relative_to_repository(SOURCE_MARKER),
        "terminal_marker_sha256": file_sha256(SOURCE_MARKER),
        "metadata_ledger": relative_to_repository(SOURCE_LEDGER),
        "metadata_ledger_file_sha256": file_sha256(SOURCE_LEDGER),
        "metadata_ledger_payload_sha256": descriptor.get("payload_sha256"),
        "records_sha256": descriptor.get("records_sha256"),
        "anchor_query_sha256": descriptor.get("query_sha256"),
        "transaction_id": descriptor.get("transaction_id"),
        "adapter": {
            "id": source_adapter.get("adapter_id"),
            "version": source_adapter.get("adapter_version"),
            "script_sha256": source_adapter.get("script_sha256"),
        },
        "matcher_schema": ledger.get("matcher_scope", {}).get("schema"),
        "category_id": first.get("category_id"),
        "root_snapshot_count": first.get("reported_count"),
        "ordered_event_ids_sha256": first.get("ordered_event_ids_sha256"),
        "root_snapshots_equal": first == second,
        "event_export_witness_count": len(ledger.get("event_export_witnesses", [])),
        "counts": dict(counts),
        "source_completed_at_utc": receipt.get("completed_at_utc"),
        "marker_bound_harvest_verified": True,
        "attachment_bodies_persisted": ledger.get("attachment_bodies_persisted"),
    }


def load_validated_corpus() -> tuple[
    Any, dict[str, Any], dict[str, Any], dict[str, Any]
]:
    """Validate the Pilot 006 transaction, then return its immutable metadata view."""
    adapter = load_adapter()
    source = load_json(SOURCE_ARTIFACT, maximum_bytes=1_000_000)
    marker = load_json(SOURCE_MARKER, maximum_bytes=1_000_000)
    merge = load_merge_entrypoint()
    require(
        merge.verify_esa_indico_v8_metadata_harvest(SOURCE_ARTIFACT, source),
        "Pilot 006 did not pass the shared marker-bound ESA v8 harvest gate",
    )
    source_adapter = _receipt_adapter(source)
    adapter_hash = file_sha256(ADAPTER_PATH)
    require(
        source_adapter.get("adapter_id") == EXPECTED_ADAPTER_ID
        and source_adapter.get("adapter_version") == EXPECTED_ADAPTER_VERSION
        and source_adapter.get("script_sha256") == adapter_hash,
        "The current matcher is not the exact adapter that produced Pilot 006",
    )
    ledger_hash_before = file_sha256(SOURCE_LEDGER)
    ledger = load_json(SOURCE_LEDGER)
    require(
        ledger_hash_before == file_sha256(SOURCE_LEDGER),
        "The source ledger changed while it was read",
    )
    require(ledger.get("schema") == EXPECTED_LEDGER_SCHEMA, "Unexpected ledger schema")
    records = ledger.get("records")
    identities = ledger.get("record_identities")
    require(
        isinstance(records, list)
        and isinstance(identities, list)
        and len(records) == len(identities),
        "The source ledger record arrays do not reconcile",
    )
    binding = corpus_binding(source, marker, ledger)
    require(binding["counts"].get("records") == len(records), "Ledger count mismatch")
    require(binding["root_snapshot_count"] == 440, "Unexpected category-0 event count")
    require(len(records) == 16_517, "Unexpected category-0 metadata record count")
    require(
        binding["event_export_witness_count"] == 440, "Event witness count mismatch"
    )
    require(
        binding["attachment_bodies_persisted"] is False,
        "Ledger retained attachment bodies",
    )
    require(
        binding["metadata_ledger_file_sha256"] == ledger_hash_before,
        "Ledger file digest changed",
    )
    return adapter, source, ledger, binding


def operation_for(adapter: Any, query: str, ledger: Mapping[str, Any]) -> str:
    snapshots = ledger["root_snapshots"]
    first = snapshots["first"]
    universe = {
        "kind": "global_root_category_event_universe",
        "event_ids": list(first["event_ids"]),
        "enumerated_count": first["reported_count"],
        "reported_count": first["reported_count"],
        "ordered_event_ids_sha256": first["ordered_event_ids_sha256"],
        "completeness_proof": "two_matching_native_category_export_snapshots",
        "global_coverage": "proven_two_matching_root_snapshots",
    }
    category_scope = {"category_id": 0, "id_path": [0], "path": "0"}
    return adapter.build_local_matching_operation(
        query, category_scope=category_scope, universe=universe
    )


def match_partition(
    adapter: Any,
    ledger: Mapping[str, Any],
    partition_id: str,
) -> tuple[list[str], list[dict[str, Any]], int]:
    require(partition_id in SCHEDULE, f"Unknown partition {partition_id}")
    query = SCHEDULE[partition_id]
    require(text_sha256(query) == QUERY_SHA256[partition_id], "Query digest mismatch")
    expression = adapter.parse_local_concept_expression(query)
    budget = adapter._LocalMatchBudget()
    compiled = adapter._compile_local_query(expression, budget)
    records = ledger["records"]
    identities = ledger["record_identities"]
    matched_identities: list[str] = []
    matched_records: list[Mapping[str, Any]] = []
    for identity, record in zip(identities, records):
        budget.charge()
        if adapter.local_concept_match(
            record,
            expression,
            _compiled=compiled,
            _budget=budget,
        ):
            matched_identities.append(identity)
            matched_records.append(record)
    normalized = []
    for rank, (identity, record) in enumerate(
        zip(matched_identities, matched_records), start=1
    ):
        row = adapter._normalize_local_record(record, rank=rank)
        row["query"] = query
        row["ledgerRecordIdentity"] = identity
        normalized.append(row)
    return matched_identities, normalized, budget.operations


def compact_corpus_binding(binding: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(binding[key])
        for key in (
            "compact_artifact",
            "compact_artifact_sha256",
            "terminal_marker",
            "terminal_marker_sha256",
            "metadata_ledger",
            "metadata_ledger_file_sha256",
            "metadata_ledger_payload_sha256",
            "records_sha256",
            "anchor_query_sha256",
            "transaction_id",
            "adapter",
            "matcher_schema",
            "category_id",
            "root_snapshot_count",
            "ordered_event_ids_sha256",
            "root_snapshots_equal",
            "event_export_witness_count",
            "counts",
            "source_completed_at_utc",
            "marker_bound_harvest_verified",
            "attachment_bodies_persisted",
        )
    }
