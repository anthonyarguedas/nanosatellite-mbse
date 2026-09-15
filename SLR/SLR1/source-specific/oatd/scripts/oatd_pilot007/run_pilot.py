#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "playwright>=1.48,<2",
# ]
# ///
"""Hydrate and confirm the OATD Pilot 007 exact gate union."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import secrets
import sys
import tempfile
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import queries

PLAN_SCHEMA = "oatd-pilot-007-hydration-plan/v1"
RUN_SCHEMA = "oatd-pilot-007-hydration-run/v1"
CHECKPOINT_SCHEMA = "oatd-pilot-007-hydration-checkpoint/v1"
GATE_SCHEMA = "oatd-pilot-007-confirmed-gate/v1"
GATE_MARKER_SCHEMA = "oatd-pilot-007-confirmed-gate-commit/v1"
UNION_SCHEMA = "oatd-pilot-007-hydrated-union/v1"
UNION_MARKER_SCHEMA = "oatd-pilot-007-hydrated-union-commit/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
ADAPTER_ROOT = Path.home() / "agent-tools"
ADAPTER_PATH = ADAPTER_ROOT / "internet/skills/browser/scripts/search_oatd.py"
ADAPTER_FILES = {
    "entrypoint": ADAPTER_PATH,
    "browser_helpers": ADAPTER_PATH.with_name("_browser_search_utils.py"),
    "output_loader": ADAPTER_PATH.with_name("_output_utils.py"),
    "output_implementation": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_output_utils.py"
    ),
    "merge_contract": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_merge_contract.py"
    ),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise RuntimeError("A source timestamp lacked a timezone")
    return parsed.astimezone(timezone.utc)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "oatd_pilot007_execution_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_exclusive_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error
    try:
        view = memoryview(payload)
        while view:
            view = view[os.write(descriptor, view) :]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_exclusive_json(path: Path, value: Mapping[str, Any]) -> None:
    write_exclusive_bytes(
        path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )


def write_atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError("Refusing to replace a symlink checkpoint")
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
        fsync_parent(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def fsync_parent(path: Path) -> None:
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def gate_marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.OATD_CONFIRMED_GATE_COMMIT.json")


def union_marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.OATD_HYDRATED_UNION_COMMIT.json")


def screenshot_paths(adapter: Any, output: Path) -> dict[str, Path]:
    paths = adapter.screenshot_paths_for_output(output)
    return {"search_page": paths.search_page, "results_page": paths.results_page}


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[
    Any,
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    Path,
    Path,
    Path,
]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != "007"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or [event.get("event_id") for event in events] != list(queries.GATE_IDS)
    ):
        raise RuntimeError("Unexpected OATD Pilot 007 plan")
    safety = plan.get("source_safety")
    if (
        not isinstance(safety, dict)
        or safety.get("inter_gate_delay_seconds") != 120.0
        or safety.get("pre_detail_delay_seconds") != 180.0
        or safety.get("detail_delay_seconds") != 15.0
        or safety.get("detail_batch_size") != 8
        or safety.get("detail_batch_cooldown_seconds") != 180.0
        or safety.get("pre_confirmation_delay_seconds") != 300.0
        or safety.get("stop_after_first_failure") is not True
    ):
        raise RuntimeError("The OATD Pilot 007 source safety policy changed")
    adapter = load_adapter()
    adapter_plan = plan.get("adapter")
    files = adapter_plan.get("files") if isinstance(adapter_plan, dict) else None
    if (
        not isinstance(adapter_plan, dict)
        or adapter_plan.get("id") != adapter.ADAPTER_ID
        or adapter_plan.get("version") != adapter.ADAPTER_VERSION
        or adapter.ADAPTER_VERSION != "10"
        or not isinstance(files, dict)
    ):
        raise RuntimeError("The OATD Pilot 007 adapter identity changed")
    for name, path in ADAPTER_FILES.items():
        descriptor = files.get(name)
        if not isinstance(descriptor, dict) or descriptor.get("sha256") != digest(path):
            raise RuntimeError(f"The OATD Pilot 007 adapter changed: {name}")
    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("The OATD Pilot 007 script bindings are missing")
    for relative, expected in scripts.items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"An OATD Pilot 007 source script changed: {relative}")
    prior = plan.get("pilot006_evidence")
    if not isinstance(prior, dict):
        raise RuntimeError("The OATD Pilot 006 evidence bindings are missing")
    loaded_prior: dict[str, dict[str, Any]] = {}
    for key in ("plan", "run", "reconciliation", "assessment", "validation"):
        descriptor = prior.get(key)
        if not isinstance(descriptor, dict):
            raise RuntimeError(f"The OATD Pilot 006 {key} binding is missing")
        path = REPOSITORY_ROOT / descriptor.get("path", "")
        if not path.is_file() or digest(path) != descriptor.get("sha256"):
            raise RuntimeError(f"The OATD Pilot 006 {key} evidence changed")
        loaded_prior[key] = load(path)
    reconciliation = loaded_prior["reconciliation"]
    if (
        reconciliation.get("exact_deduplicated_union_total") != 26
        or reconciliation.get("stable_union_ids_sha256")
        != plan.get("target_union", {}).get("stable_record_ids_sha256")
        or len(reconciliation.get("records", [])) != 26
    ):
        raise RuntimeError("The OATD Pilot 007 target union changed")
    local_descriptor = plan.get("local_matching_plan")
    if not isinstance(local_descriptor, dict):
        raise RuntimeError("The OATD Pilot 007 local plan binding is missing")
    local_path = REPOSITORY_ROOT / local_descriptor.get("path", "")
    if not local_path.is_file() or digest(local_path) != local_descriptor.get("sha256"):
        raise RuntimeError("The OATD Pilot 007 local matching plan changed")
    local_plan = adapter.load_local_matching_plan(local_path)
    if local_plan.plan_sha256 != local_descriptor.get("plan_sha256"):
        raise RuntimeError("The OATD Pilot 007 local plan semantics changed")

    occupied = {plan_path.resolve()}
    for event in events:
        event_id = event["event_id"]
        query = queries.GATE_QUERIES[event_id]
        output = pilot_root / event.get("output", "")
        configuration = adapter.build_oatd_search_configuration(
            query,
            language="English",
            year_start=2011,
            year_end=2026,
            page_size=30,
        )
        prior_artifact_descriptor = event.get("pilot006_gate_artifact")
        if not isinstance(prior_artifact_descriptor, dict):
            raise RuntimeError(f"The prior OATD gate binding is missing: {event_id}")
        prior_artifact_path = REPOSITORY_ROOT / prior_artifact_descriptor.get(
            "path", ""
        )
        if not prior_artifact_path.is_file() or digest(
            prior_artifact_path
        ) != prior_artifact_descriptor.get("sha256"):
            raise RuntimeError(f"The prior OATD gate changed: {event_id}")
        prior_artifact = load(prior_artifact_path)
        if (
            event.get("query") != query
            or event.get("query_sha256") != text_digest(query)
            or event.get("effective_query") != configuration.effective_query
            or event.get("effective_query_sha256")
            != text_digest(configuration.effective_query)
            or event.get("expected_source_total") != queries.EXPECTED_COUNTS[event_id]
            or event.get("expected_stable_record_ids_sha256")
            != prior_artifact.get("first_pass", {}).get("stable_record_ids_sha256")
            or event.get("page_size") != 30
            or event.get("limit") != 100
            or event.get("max_pages") != 4
            or output.parent != pilot_root / "searches/gates"
        ):
            raise RuntimeError(f"The OATD Pilot 007 event changed: {event_id}")
        expected_screenshots = {
            key: str(path.relative_to(pilot_root))
            for key, path in screenshot_paths(adapter, output).items()
        }
        if event.get("screenshots") != expected_screenshots:
            raise RuntimeError(f"The OATD Pilot 007 screenshots changed: {event_id}")
        for path in (
            output,
            gate_marker_path(output),
            *screenshot_paths(adapter, output).values(),
        ):
            if path.resolve() in occupied or os.path.lexists(path):
                raise RuntimeError(f"An OATD Pilot 007 gate output is occupied: {path}")
            occupied.add(path.resolve())
    checkpoint = pilot_root / plan.get("checkpoint", "")
    union_output = pilot_root / plan.get("union_output", "")
    if (
        checkpoint.parent != pilot_root / "searches/checkpoint"
        or union_output.parent != pilot_root / "searches"
        or os.path.lexists(union_output)
        or os.path.lexists(union_marker_path(union_output))
        or checkpoint.resolve() in occupied
        or union_output.resolve() in occupied
    ):
        raise RuntimeError("An OATD Pilot 007 union path is unsafe")
    return (
        adapter,
        events,
        reconciliation,
        local_plan,
        local_path,
        checkpoint,
        union_output,
    )


def snapshot_payload(adapter: Any, snapshot: Any) -> dict[str, Any]:
    return {
        "source_reported_total": snapshot.total,
        "pages_retrieved": snapshot.pages_retrieved,
        "source_card_rows_seen": snapshot.source_card_rows_seen,
        "page_size": snapshot.page_size,
        "ordered_record_ids_sha256": adapter._ordered_record_ids_sha256(
            snapshot.ordered_record_ids
        ),
        "stable_record_ids_sha256": adapter._stable_record_ids_sha256(
            snapshot.ordered_record_ids
        ),
        "cards": [
            {"rank": card.rank, "paperId": card.record_id, "title": card.title}
            for card in snapshot.cards
        ],
        "complete": True,
    }


def validate_snapshot_against_plan(
    adapter: Any, event: dict[str, Any], snapshot: Any
) -> None:
    if (
        snapshot.total != event["expected_source_total"]
        or adapter._stable_record_ids_sha256(snapshot.ordered_record_ids)
        != event["expected_stable_record_ids_sha256"]
    ):
        raise adapter.OATDMetadataProtocolError(
            f"OATD {event['event_id']} changed since the accepted card-ID pilot."
        )


async def capture_initial_snapshot(
    adapter: Any,
    page: Any,
    event: dict[str, Any],
    output: Path,
) -> tuple[Any, Any, dict[str, Any], int]:
    configuration = adapter.build_oatd_search_configuration(
        event["query"],
        language=event["language"],
        year_start=event["year_start"],
        year_end=event["year_end"],
        page_size=event["page_size"],
    )
    paths = adapter.screenshot_paths_for_output(output)
    payloads: dict[str, Any] = {}
    budget = adapter.OATDBusyRetryBudget(
        max_retries=event["busy_retries"],
        initial_delay_seconds=event["busy_retry_delay_seconds"],
    )
    configured = await adapter.configure_oatd_search_page_for_screenshot(
        page,
        configuration=configuration,
        timeout_seconds=event["timeout_seconds"],
    )
    payloads["search_page"] = await adapter._capture_oatd_screenshot_payload(
        page,
        paths.search_page,
        page_kind="configured_search_page",
        configuration_evidence=configured,
    )
    snapshot = await adapter.collect_shared_population_snapshot(
        page,
        query=event["query"],
        limit=event["limit"],
        max_pages=event["max_pages"],
        timeout_seconds=event["timeout_seconds"],
        page_delay_seconds=event["page_delay_seconds"],
        busy_retry_budget=budget,
        configuration=configuration,
        screenshot_paths=paths,
        screenshot_payloads=payloads,
    )
    validate_snapshot_against_plan(adapter, event, snapshot)
    return snapshot, configuration, payloads, budget.performed_retries


async def capture_confirmation_snapshot(
    adapter: Any,
    page: Any,
    event: dict[str, Any],
    configuration: Any,
) -> tuple[Any, int]:
    budget = adapter.OATDBusyRetryBudget(
        max_retries=event["busy_retries"],
        initial_delay_seconds=event["busy_retry_delay_seconds"],
    )
    snapshot = await adapter.collect_shared_population_snapshot(
        page,
        query=event["query"],
        limit=event["limit"],
        max_pages=event["max_pages"],
        timeout_seconds=event["timeout_seconds"],
        page_delay_seconds=event["page_delay_seconds"],
        busy_retry_budget=budget,
        configuration=configuration,
    )
    validate_snapshot_against_plan(adapter, event, snapshot)
    return snapshot, budget.performed_retries


def new_checkpoint(
    plan_sha256: str, target_ids: list[str], stable_hash: str
) -> dict[str, Any]:
    return {
        "schema_version": CHECKPOINT_SCHEMA,
        "adapter": {"id": "search_oatd", "version": "10"},
        "pilot": "007",
        "plan_sha256": plan_sha256,
        "source_union": {
            "record_count": len(target_ids),
            "stable_record_ids_sha256": stable_hash,
        },
        "completed_ids": [],
        "records": [],
    }


def validate_checkpoint(
    adapter: Any,
    value: dict[str, Any],
    *,
    plan_sha256: str,
    target_ids: list[str],
    stable_hash: str,
    local_plan: Any,
    configuration: Any,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if (
        set(value)
        != {
            "schema_version",
            "adapter",
            "pilot",
            "plan_sha256",
            "source_union",
            "completed_ids",
            "records",
        }
        or value.get("schema_version") != CHECKPOINT_SCHEMA
        or value.get("adapter") != {"id": "search_oatd", "version": "10"}
        or value.get("pilot") != "007"
        or value.get("plan_sha256") != plan_sha256
        or value.get("source_union")
        != {
            "record_count": len(target_ids),
            "stable_record_ids_sha256": stable_hash,
        }
    ):
        raise RuntimeError("The OATD Pilot 007 checkpoint binding is invalid")
    completed = value.get("completed_ids")
    records = value.get("records")
    if (
        not isinstance(completed, list)
        or not isinstance(records, list)
        or len(completed) != len(records)
        or completed != target_ids[: len(completed)]
        or len(set(completed)) != len(completed)
    ):
        raise RuntimeError("The OATD Pilot 007 checkpoint order is invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for record_id, record in zip(completed, records, strict=True):
        if not isinstance(record, Mapping):
            raise RuntimeError("The OATD Pilot 007 checkpoint record is invalid")
        safe = adapter._checkpoint_safe_public_record(record)
        validated = adapter._validate_shared_population_checkpoint_record(
            safe, configuration=configuration, plan=local_plan
        )
        if validated.get("paperId") != record_id:
            raise RuntimeError("The OATD Pilot 007 checkpoint IDs do not match")
        by_id[record_id] = validated
    if adapter._checkpoint_has_unsafe_content(value):
        raise RuntimeError("The OATD Pilot 007 checkpoint retained unsafe context")
    return list(completed), by_id


def checkpoint_with_records(
    base: dict[str, Any],
    target_ids: list[str],
    records_by_id: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    completed = [record_id for record_id in target_ids if record_id in records_by_id]
    if completed != target_ids[: len(completed)]:
        raise RuntimeError("OATD Pilot 007 hydration must follow union order")
    value = deepcopy(base)
    value["completed_ids"] = completed
    value["records"] = [records_by_id[record_id] for record_id in completed]
    return value


async def hydrate_missing_records(
    adapter: Any,
    detail_page: Any,
    *,
    target_ids: list[str],
    cards_by_id: Mapping[str, Any],
    configurations_by_id: Mapping[str, Any],
    records_by_id: dict[str, dict[str, Any]],
    checkpoint: dict[str, Any],
    checkpoint_path: Path,
    local_plan: Any,
    safety: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], int]:
    budget = adapter.OATDBusyRetryBudget(
        max_retries=safety["detail_busy_retries"],
        initial_delay_seconds=safety["detail_busy_retry_delay_seconds"],
    )
    new_requests = 0
    for record_id in target_ids:
        if record_id in records_by_id:
            continue
        record = await adapter.read_shared_population_detail(
            detail_page,
            card=cards_by_id[record_id],
            configuration=configurations_by_id[record_id],
            timeout_seconds=safety["detail_timeout_seconds"],
            busy_retry_budget=budget,
        )
        annotation, _counts = adapter.annotate_local_matching_plan(record, local_plan)
        record["localMatching"] = annotation
        record = adapter._validate_shared_population_checkpoint_record(
            record,
            configuration=configurations_by_id[record_id],
            plan=local_plan,
        )
        records_by_id[record_id] = record
        new_requests += 1
        checkpoint = checkpoint_with_records(checkpoint, target_ids, records_by_id)
        if adapter._checkpoint_has_unsafe_content(checkpoint):
            raise RuntimeError("The OATD Pilot 007 checkpoint became unsafe")
        write_atomic_json(checkpoint_path, checkpoint)
        print(
            json.dumps(
                {
                    "stage": "detail_hydration",
                    "completed_records": len(records_by_id),
                    "target_records": len(target_ids),
                }
            ),
            flush=True,
        )
        remaining = len(target_ids) - len(records_by_id)
        if remaining:
            if new_requests % safety["detail_batch_size"] == 0:
                await asyncio.sleep(safety["detail_batch_cooldown_seconds"])
            else:
                await asyncio.sleep(safety["detail_delay_seconds"])
    return records_by_id, checkpoint, budget.performed_retries


def gate_membership(
    reconciliation: Mapping[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for record in reconciliation["records"]:
        result[record["paperId"]] = deepcopy(record["gate_membership"])
    return result


def build_gate_artifact(
    adapter: Any,
    event: dict[str, Any],
    initial: Any,
    confirmation: Any,
    payloads: dict[str, Any],
    *,
    initial_retries: int,
    confirmation_retries: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    output = Path(event["absolute_output"])
    paths = adapter.screenshot_paths_for_output(output)
    search = adapter._validate_oatd_screenshot_payload(
        payloads.get("search_page"),
        paths.search_page,
        page_kind="configured_search_page",
    )
    results = adapter._validate_oatd_screenshot_payload(
        payloads.get("results_page"),
        paths.results_page,
        page_kind="verified_first_results_page",
    )
    transaction_id = secrets.token_hex(32)
    artifact = {
        "schema_version": GATE_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_endpoint": "https://oatd.org/oatd/search",
        "pilot": "007",
        "event_id": event["event_id"],
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "requested_query": event["query"],
        "executed_query": event["effective_query"],
        "controls": {
            "language": "English",
            "language_source_value": "(en OR eng OR english)",
            "year_start": 2011,
            "year_end": 2026,
            "page_size": 30,
            "sort": "source_rendered_relevance_not_oldest_first",
        },
        "source_total": initial.total,
        "initial_pass": snapshot_payload(adapter, initial),
        "confirmation_pass": snapshot_payload(adapter, confirmation),
        "stable_record_id_sets_reconciled": True,
        "native_order_drift_observed": (
            initial.ordered_record_ids != confirmation.ordered_record_ids
        ),
        "record_details_requested_by_gate_passes": False,
        "busy_retries_performed": initial_retries + confirmation_retries,
        "screenshots": {
            "schema_version": "oatd-pilot-007-screenshots/v1",
            "search_page": dict(search.evidence),
            "results_page": dict(results.evidence),
        },
        "publication": {
            "schema_version": GATE_MARKER_SCHEMA,
            "state": "terminal_marker_required",
            "transaction_id": transaction_id,
            "marker_path_persisted": False,
        },
    }
    return artifact, {"search_page": search, "results_page": results}


def publish_gate(
    adapter: Any,
    output: Path,
    artifact: dict[str, Any],
    payloads: dict[str, Any],
) -> None:
    paths = screenshot_paths(adapter, output)
    artifact_bytes = (json.dumps(artifact, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
    marker = {
        "schema_version": GATE_MARKER_SCHEMA,
        "transaction_id": artifact["publication"]["transaction_id"],
        "files": {
            "json": {
                "file_name": output.name,
                "sha256": bytes_digest(artifact_bytes),
                "bytes": len(artifact_bytes),
            },
            "search_page": {
                "file_name": paths["search_page"].name,
                "sha256": bytes_digest(payloads["search_page"].data),
                "bytes": len(payloads["search_page"].data),
            },
            "results_page": {
                "file_name": paths["results_page"].name,
                "sha256": bytes_digest(payloads["results_page"].data),
                "bytes": len(payloads["results_page"].data),
            },
        },
        "paths_persisted": False,
    }
    write_exclusive_bytes(paths["search_page"], payloads["search_page"].data)
    write_exclusive_bytes(paths["results_page"], payloads["results_page"].data)
    write_exclusive_bytes(output, artifact_bytes)
    write_exclusive_json(gate_marker_path(output), marker)
    fsync_parent(output)
    validate_gate_artifact(adapter, output, artifact["event_id"])


def validate_bound_files(
    marker: Mapping[str, Any], paths: Mapping[str, Path], schema: str
) -> None:
    if (
        marker.get("schema_version") != schema
        or marker.get("paths_persisted") is not False
    ):
        raise RuntimeError("An OATD Pilot 007 terminal marker is invalid")
    files = marker.get("files")
    if not isinstance(files, Mapping) or set(files) != set(paths):
        raise RuntimeError("An OATD Pilot 007 terminal marker file set is invalid")
    for key, path in paths.items():
        evidence = files.get(key)
        if (
            not path.is_file()
            or not isinstance(evidence, Mapping)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != digest(path)
            or evidence.get("bytes") != path.stat().st_size
        ):
            raise RuntimeError("An OATD Pilot 007 terminal marker digest is invalid")


def validate_gate_artifact(adapter: Any, output: Path, event_id: str) -> dict[str, Any]:
    artifact = load(output)
    marker = load(gate_marker_path(output))
    paths = {"json": output, **screenshot_paths(adapter, output)}
    validate_bound_files(marker, paths, GATE_MARKER_SCHEMA)
    if (
        artifact.get("schema_version") != GATE_SCHEMA
        or artifact.get("event_id") != event_id
        or artifact.get("diagnostic_only") is not True
        or artifact.get("do_not_merge") is not True
        or artifact.get("stable_record_id_sets_reconciled") is not True
        or marker.get("transaction_id")
        != artifact.get("publication", {}).get("transaction_id")
    ):
        raise RuntimeError(f"The OATD Pilot 007 gate is invalid: {event_id}")
    initial = artifact.get("initial_pass")
    confirmation = artifact.get("confirmation_pass")
    if not isinstance(initial, Mapping) or not isinstance(confirmation, Mapping):
        raise RuntimeError(f"The OATD Pilot 007 gate passes are absent: {event_id}")
    initial_ids = [card.get("paperId") for card in initial.get("cards", [])]
    confirmation_ids = [card.get("paperId") for card in confirmation.get("cards", [])]
    total = artifact.get("source_total")
    if (
        not isinstance(total, int)
        or isinstance(total, bool)
        or len(initial_ids) != total
        or len(confirmation_ids) != total
        or len(set(initial_ids)) != total
        or set(initial_ids) != set(confirmation_ids)
        or initial.get("stable_record_ids_sha256")
        != confirmation.get("stable_record_ids_sha256")
    ):
        raise RuntimeError(f"The OATD Pilot 007 gate did not reconcile: {event_id}")
    receipt = artifact.get("screenshots")
    for key, path in screenshot_paths(adapter, output).items():
        evidence = receipt.get(key) if isinstance(receipt, Mapping) else None
        if (
            not isinstance(evidence, Mapping)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != digest(path)
            or evidence.get("full_page") is not True
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            raise RuntimeError(
                f"The OATD Pilot 007 gate screenshot is invalid: {event_id}"
            )
    return artifact


def local_matching_summary(
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    expression_ids = tuple(
        item["id"] for item in records[0]["localMatching"]["expressions"]
    )
    summary = []
    for expression_id in expression_ids:
        counts = {
            "matched": 0,
            "visible_fields_nonmatch": 0,
            "unresolved_missing_required_field": 0,
        }
        for record in records:
            expression = next(
                item
                for item in record["localMatching"]["expressions"]
                if item["id"] == expression_id
            )
            counts[expression["status"]] += 1
        summary.append({"id": expression_id, **counts})
    return summary


def build_union_artifact(
    adapter: Any,
    plan: dict[str, Any],
    reconciliation: dict[str, Any],
    checkpoint: dict[str, Any],
    events: list[dict[str, Any]],
    gate_artifacts: Mapping[str, dict[str, Any]],
    *,
    plan_sha256: str,
    checkpoint_path: Path,
    detail_requests_this_attempt: int,
    detail_busy_retries: int,
) -> dict[str, Any]:
    target_ids = [record["paperId"] for record in reconciliation["records"]]
    records_by_id = {
        record["paperId"]: record for record in checkpoint.get("records", [])
    }
    if set(records_by_id) != set(target_ids):
        raise RuntimeError("The OATD Pilot 007 checkpoint is not complete")
    memberships = gate_membership(reconciliation)
    results = []
    for union_rank, record_id in enumerate(target_ids, start=1):
        record = deepcopy(records_by_id[record_id])
        record["unionRank"] = union_rank
        record["gateProvenance"] = memberships[record_id]
        results.append(record)
    gate_evidence = {
        event["event_id"]: {
            "artifact": event["output"],
            "sha256": digest(Path(event["absolute_output"])),
            "source_total": gate_artifacts[event["event_id"]]["source_total"],
            "stable_record_ids_sha256": gate_artifacts[event["event_id"]][
                "initial_pass"
            ]["stable_record_ids_sha256"],
        }
        for event in events
    }
    transaction_id = secrets.token_hex(32)
    publication_statuses: dict[str, int] = {}
    for record in results:
        status = record.get("publicationDateReadback", {}).get("status", "missing")
        publication_statuses[status] = publication_statuses.get(status, 0) + 1
    return {
        "schema_version": UNION_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_endpoint": "https://oatd.org/oatd/search",
        "pilot": "007",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan_sha256": plan_sha256,
        "candidate_route": plan["algebraic_candidate_union"],
        "controls": {
            "language": "English",
            "language_source_value": "(en OR eng OR english)",
            "year_start": 2011,
            "year_end": 2026,
            "diagnostic_exact_cutoff": "2026-08-29",
            "sort": "source_rendered_relevance_not_oldest_first",
        },
        "total": len(results),
        "results": results,
        "gate_evidence": gate_evidence,
        "gate_occurrence_total": sum(
            artifact["source_total"] for artifact in gate_artifacts.values()
        ),
        "exact_deduplicated_union_total": len(results),
        "stable_union_ids_sha256": adapter._stable_record_ids_sha256(target_ids),
        "ordered_union_ids_sha256": adapter._ordered_record_ids_sha256(target_ids),
        "hydration": {
            "unique_detail_records_hydrated": len(results),
            "one_record_per_stable_union_id": True,
            "pilot004_records_reused": 0,
            "detail_requests_this_attempt": detail_requests_this_attempt,
            "detail_busy_retries_performed": detail_busy_retries,
            "checkpoint_schema": CHECKPOINT_SCHEMA,
            "checkpoint_path_persisted": False,
            "checkpoint_sha256_before_publication": digest(checkpoint_path),
        },
        "confirmation": {
            "all_eight_gate_sets_reconciled": True,
            "complete_gate_count": len(gate_artifacts),
            "complete_source_pass_count": len(gate_artifacts) * 2,
            "record_details_requested_by_gate_passes": False,
        },
        "local_matching": {
            "mode": "annotation_only_no_source_record_exclusion",
            "expressions": local_matching_summary(results),
            "local_negative_records_removed": 0,
        },
        "publication_date_readback_statuses": publication_statuses,
        "publication": {
            "schema_version": UNION_MARKER_SCHEMA,
            "state": "terminal_marker_required",
            "transaction_id": transaction_id,
            "marker_path_persisted": False,
        },
    }


def publish_union(output: Path, artifact: dict[str, Any]) -> None:
    artifact_bytes = (json.dumps(artifact, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
    marker = {
        "schema_version": UNION_MARKER_SCHEMA,
        "transaction_id": artifact["publication"]["transaction_id"],
        "files": {
            "json": {
                "file_name": output.name,
                "sha256": bytes_digest(artifact_bytes),
                "bytes": len(artifact_bytes),
            }
        },
        "paths_persisted": False,
    }
    write_exclusive_bytes(output, artifact_bytes)
    write_exclusive_json(union_marker_path(output), marker)
    fsync_parent(output)
    validate_union_artifact(output)


def validate_union_artifact(output: Path) -> dict[str, Any]:
    artifact = load(output)
    marker = load(union_marker_path(output))
    validate_bound_files(marker, {"json": output}, UNION_MARKER_SCHEMA)
    results = artifact.get("results")
    if (
        artifact.get("schema_version") != UNION_SCHEMA
        or artifact.get("diagnostic_only") is not True
        or artifact.get("do_not_merge") is not True
        or artifact.get("total") != 26
        or artifact.get("exact_deduplicated_union_total") != 26
        or not isinstance(results, list)
        or len(results) != 26
        or len({record.get("paperId") for record in results}) != 26
        or artifact.get("confirmation", {}).get("all_eight_gate_sets_reconciled")
        is not True
        or artifact.get("hydration", {}).get("unique_detail_records_hydrated") != 26
        or artifact.get("hydration", {}).get("pilot004_records_reused") != 0
        or marker.get("transaction_id")
        != artifact.get("publication", {}).get("transaction_id")
    ):
        raise RuntimeError("The OATD Pilot 007 hydrated union is invalid")
    return artifact


async def execute_source_workflow(
    adapter: Any,
    plan: dict[str, Any],
    events: list[dict[str, Any]],
    reconciliation: dict[str, Any],
    local_plan: Any,
    checkpoint_path: Path,
    plan_sha256: str,
    cdp_url: str,
) -> dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is unavailable. Run through uv.") from error
    safety = plan["source_safety"]
    target_ids = [record["paperId"] for record in reconciliation["records"]]
    stable_hash = reconciliation["stable_union_ids_sha256"]
    snapshots: dict[str, Any] = {}
    confirmations: dict[str, Any] = {}
    configurations: dict[str, Any] = {}
    screenshot_payloads: dict[str, dict[str, Any]] = {}
    initial_retries: dict[str, int] = {}
    confirmation_retries: dict[str, int] = {}
    cards_by_id: dict[str, Any] = {}
    configurations_by_id: dict[str, Any] = {}
    stage = "initial_gate_snapshots"
    detail_requests_before = 0
    detail_requests_after = 0
    detail_busy_retries = 0

    async with async_playwright() as playwright, adapter._LeaseCleanup() as cleanup:
        lease = await adapter.open_owned_chrome_page(
            playwright,
            cdp_url=cdp_url,
            headless=False,
            timeout_seconds=safety["search_timeout_seconds"],
            chrome_executable=None,
        )
        cleanup.lease = lease
        page = lease.page
        for index, event in enumerate(events):
            if index:
                await asyncio.sleep(safety["inter_gate_delay_seconds"])
            output = Path(event["absolute_output"])
            snapshot, configuration, payloads, retries = await capture_initial_snapshot(
                adapter, page, event, output
            )
            snapshots[event["event_id"]] = snapshot
            configurations[event["event_id"]] = configuration
            screenshot_payloads[event["event_id"]] = payloads
            initial_retries[event["event_id"]] = retries
            print(
                json.dumps(
                    {
                        "stage": "initial_gate_snapshot",
                        "event": event["event_id"],
                        "total": snapshot.total,
                    }
                ),
                flush=True,
            )
            for card in snapshot.cards:
                if card.record_id not in cards_by_id:
                    cards_by_id[card.record_id] = card
                    configurations_by_id[card.record_id] = configuration
        if set(cards_by_id) != set(target_ids):
            raise adapter.OATDMetadataProtocolError(
                "The fresh OATD gate union changed before detail hydration."
            )

        first_configuration = configurations[events[0]["event_id"]]
        checkpoint = (
            load(checkpoint_path)
            if checkpoint_path.is_file()
            else new_checkpoint(plan_sha256, target_ids, stable_hash)
        )
        completed, records_by_id = validate_checkpoint(
            adapter,
            checkpoint,
            plan_sha256=plan_sha256,
            target_ids=target_ids,
            stable_hash=stable_hash,
            local_plan=local_plan,
            configuration=first_configuration,
        )
        detail_requests_before = len(completed)
        write_atomic_json(checkpoint_path, checkpoint)

        stage = "detail_hydration"
        await asyncio.sleep(safety["pre_detail_delay_seconds"])
        detail_page = None
        try:
            detail_page = await adapter.new_owned_chrome_page(
                lease.context, timeout_seconds=safety["detail_timeout_seconds"]
            )
            (
                records_by_id,
                checkpoint,
                detail_busy_retries,
            ) = await hydrate_missing_records(
                adapter,
                detail_page,
                target_ids=target_ids,
                cards_by_id=cards_by_id,
                configurations_by_id=configurations_by_id,
                records_by_id=records_by_id,
                checkpoint=checkpoint,
                checkpoint_path=checkpoint_path,
                local_plan=local_plan,
                safety=safety,
            )
        finally:
            outcome = await adapter.close_owned_chrome_page_only_verified(detail_page)
            if outcome is None or not outcome.verified:
                raise adapter.OATDMetadataBrowserError(
                    "OATD Pilot 007 detail-page cleanup could not be verified."
                )
        detail_requests_after = len(records_by_id)

        stage = "confirming_gate_snapshots"
        await asyncio.sleep(safety["pre_confirmation_delay_seconds"])
        for index, event in enumerate(events):
            if index:
                await asyncio.sleep(safety["inter_gate_delay_seconds"])
            confirmation, retries = await capture_confirmation_snapshot(
                adapter,
                page,
                event,
                configurations[event["event_id"]],
            )
            adapter.reconcile_shared_population_snapshots(
                snapshots[event["event_id"]], confirmation
            )
            confirmations[event["event_id"]] = confirmation
            confirmation_retries[event["event_id"]] = retries
            print(
                json.dumps(
                    {
                        "stage": "confirming_gate_snapshot",
                        "event": event["event_id"],
                        "total": confirmation.total,
                    }
                ),
                flush=True,
            )

    return {
        "stage": "complete",
        "snapshots": snapshots,
        "confirmations": confirmations,
        "screenshot_payloads": screenshot_payloads,
        "initial_retries": initial_retries,
        "confirmation_retries": confirmation_retries,
        "checkpoint": checkpoint,
        "detail_records_before": detail_requests_before,
        "detail_records_after": detail_requests_after,
        "detail_requests_this_attempt": detail_requests_after - detail_requests_before,
        "detail_busy_retries": detail_busy_retries,
        "last_stage": stage,
    }


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> int:
    if os.path.lexists(receipt_path):
        raise RuntimeError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    (
        adapter,
        events,
        reconciliation,
        local_plan,
        _local_path,
        checkpoint_path,
        union_output,
    ) = validate_plan(plan, plan_path, pilot_root)
    for event in events:
        event["absolute_output"] = str(pilot_root / event["output"])
    cdp_url = adapter.validate_local_cdp_url(
        os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL)
    )
    not_before = parse_utc(plan["source_safety"]["first_source_request_not_before_utc"])
    wait_seconds = max(0.0, (not_before - datetime.now(timezone.utc)).total_seconds())
    if wait_seconds:
        print(f"Waiting {wait_seconds:.1f} seconds for the OATD cooldown.", flush=True)
        time.sleep(wait_seconds)
    started = now()
    completed_before = (
        len(load(checkpoint_path).get("completed_ids", []))
        if checkpoint_path.is_file()
        else 0
    )
    try:
        workflow = asyncio.run(
            execute_source_workflow(
                adapter,
                plan,
                events,
                reconciliation,
                local_plan,
                checkpoint_path,
                digest(plan_path),
                cdp_url,
            )
        )
    except Exception as error:
        completed_after = (
            len(load(checkpoint_path).get("completed_ids", []))
            if checkpoint_path.is_file()
            else 0
        )
        safe_message = (
            adapter.safe_error_message(error)
            if isinstance(error, adapter.OATDMetadataError)
            else "Unexpected OATD Pilot 007 hydration workflow failure."
        )
        receipt = {
            "schema_version": RUN_SCHEMA,
            "source": plan["source"],
            "pilot": "007",
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "diagnostic_only": True,
            "do_not_merge": True,
            "plan": str(plan_path.relative_to(pilot_root)),
            "plan_sha256": digest(plan_path),
            "started_at_utc": started,
            "completed_at_utc": now(),
            "status": "stopped_on_source_or_adapter_failure",
            "success": False,
            "checkpoint_completed_ids_before": completed_before,
            "checkpoint_completed_ids_after": completed_after,
            "error_type": type(error).__name__,
            "error": safe_message,
            "union_output_created": union_output.is_file(),
        }
        write_exclusive_json(receipt_path, receipt)
        fsync_parent(receipt_path)
        print(
            json.dumps(
                {
                    "success": False,
                    "completed_ids": completed_after,
                    "error": safe_message,
                }
            ),
            flush=True,
        )
        return 1

    gate_artifacts: dict[str, dict[str, Any]] = {}
    for event in events:
        event_id = event["event_id"]
        artifact, payloads = build_gate_artifact(
            adapter,
            event,
            workflow["snapshots"][event_id],
            workflow["confirmations"][event_id],
            workflow["screenshot_payloads"][event_id],
            initial_retries=workflow["initial_retries"][event_id],
            confirmation_retries=workflow["confirmation_retries"][event_id],
        )
        output = Path(event["absolute_output"])
        publish_gate(adapter, output, artifact, payloads)
        gate_artifacts[event_id] = validate_gate_artifact(adapter, output, event_id)
    union_artifact = build_union_artifact(
        adapter,
        plan,
        reconciliation,
        workflow["checkpoint"],
        events,
        gate_artifacts,
        plan_sha256=digest(plan_path),
        checkpoint_path=checkpoint_path,
        detail_requests_this_attempt=workflow["detail_requests_this_attempt"],
        detail_busy_retries=workflow["detail_busy_retries"],
    )
    publish_union(union_output, union_artifact)
    persisted_union = validate_union_artifact(union_output)
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": plan["source"],
        "pilot": "007",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(plan_path.relative_to(pilot_root)),
        "plan_sha256": digest(plan_path),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "status": "complete",
        "success": True,
        "target_union_total": 26,
        "checkpoint_completed_ids_before": completed_before,
        "checkpoint_completed_ids_after": len(workflow["checkpoint"]["completed_ids"]),
        "detail_requests_this_attempt": workflow["detail_requests_this_attempt"],
        "detail_busy_retries_performed": workflow["detail_busy_retries"],
        "complete_gate_count": 8,
        "complete_source_pass_count": 16,
        "gate_artifacts": {
            event_id: {
                "path": next(
                    event["output"] for event in events if event["event_id"] == event_id
                ),
                "sha256": digest(
                    Path(
                        next(
                            event["absolute_output"]
                            for event in events
                            if event["event_id"] == event_id
                        )
                    )
                ),
                "marker_sha256": digest(
                    gate_marker_path(
                        Path(
                            next(
                                event["absolute_output"]
                                for event in events
                                if event["event_id"] == event_id
                            )
                        )
                    )
                ),
            }
            for event_id in queries.GATE_IDS
        },
        "union_artifact": {
            "path": str(union_output.relative_to(pilot_root)),
            "sha256": digest(union_output),
            "marker_sha256": digest(union_marker_path(union_output)),
            "records": persisted_union["total"],
        },
        "checkpoint": {
            "path_persisted_in_public_artifact": False,
            "sha256": digest(checkpoint_path),
            "completed_ids": len(workflow["checkpoint"]["completed_ids"]),
        },
    }
    write_exclusive_json(receipt_path, receipt)
    fsync_parent(receipt_path)
    print(
        json.dumps(
            {
                "success": True,
                "records": persisted_union["total"],
                "detail_requests": workflow["detail_requests_this_attempt"],
                "confirmed_gates": 8,
            }
        ),
        flush=True,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args.plan, args.pilot_root, args.receipt)
    except Exception as error:
        print(" ".join(str(error).split())[:1000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
