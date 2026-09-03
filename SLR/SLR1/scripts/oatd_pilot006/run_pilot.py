#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "playwright>=1.48,<2",
# ]
# ///
"""Collect and reconcile OATD Pilot 006 card-ID gate snapshots."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import queries

PLAN_SCHEMA = "oatd-pilot-006-card-id-plan/v1"
RUN_SCHEMA = "oatd-pilot-006-card-id-run/v1"
GATE_SCHEMA = "oatd-pilot-006-card-id-gate/v1"
GATE_MARKER_SCHEMA = "oatd-pilot-006-card-id-gate-commit/v1"
RECONCILIATION_SCHEMA = "oatd-pilot-006-card-id-reconciliation/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[1]
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
        "oatd_pilot006_execution_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def gate_marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.OATD_CARD_IDS_COMMIT.json")


def screenshot_paths(adapter: Any, output: Path) -> dict[str, Path]:
    value = adapter.screenshot_paths_for_output(output)
    return {"search_page": value.search_page, "results_page": value.results_page}


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
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_exclusive_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    write_exclusive_bytes(path, payload)


def fsync_parent(path: Path) -> None:
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[Any, list[dict[str, Any]], Path, Path]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != "006"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or [event.get("event_id") for event in events] != list(queries.GATE_IDS)
    ):
        raise RuntimeError("Unexpected OATD Pilot 006 plan")
    safety = plan.get("source_safety")
    if (
        not isinstance(safety, dict)
        or safety.get("pass_delay_seconds") != 60.0
        or safety.get("inter_gate_delay_seconds") != 120.0
        or safety.get("stop_after_first_failure") is not True
        or safety.get("record_details_requested") is not False
    ):
        raise RuntimeError("The OATD Pilot 006 source safety policy changed")
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
        raise RuntimeError("The OATD Pilot 006 adapter identity changed")
    for name, path in ADAPTER_FILES.items():
        descriptor = files.get(name)
        if not isinstance(descriptor, dict) or descriptor.get("sha256") != digest(path):
            raise RuntimeError(f"The OATD Pilot 006 adapter changed: {name}")
    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("The OATD Pilot 006 script bindings are missing")
    for relative, expected in scripts.items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"An OATD Pilot 006 source script changed: {relative}")
    prior = plan.get("pilot005_evidence")
    if not isinstance(prior, dict):
        raise RuntimeError("The OATD Pilot 005 evidence bindings are missing")
    for key in ("plan", "run", "assessment", "validation"):
        descriptor = prior.get(key)
        if not isinstance(descriptor, dict):
            raise RuntimeError(f"The OATD Pilot 005 {key} binding is missing")
        path = REPOSITORY_ROOT / descriptor.get("path", "")
        if not path.is_file() or digest(path) != descriptor.get("sha256"):
            raise RuntimeError(f"The OATD Pilot 005 {key} evidence changed")
    checkpoint_descriptor = plan.get("pilot004_checkpoint")
    if not isinstance(checkpoint_descriptor, dict):
        raise RuntimeError("The OATD Pilot 004 checkpoint binding is missing")
    checkpoint = REPOSITORY_ROOT / checkpoint_descriptor.get("path", "")
    if (
        not checkpoint.is_file()
        or digest(checkpoint) != checkpoint_descriptor.get("sha256")
        or checkpoint_descriptor.get("completed_records") != 338
    ):
        raise RuntimeError("The OATD Pilot 004 checkpoint changed")

    occupied = {plan_path.resolve()}
    for event in events:
        event_id = event["event_id"]
        query = queries.GATE_QUERIES[event_id]
        output = pilot_root / event.get("output", "")
        failure_output = pilot_root / event.get("failure_output", "")
        configuration = adapter.build_oatd_search_configuration(
            query,
            language="English",
            year_start=2011,
            year_end=2026,
            page_size=30,
        )
        route = adapter.build_search_url(query, configuration=configuration)
        declared_screenshots = {
            key: str(path.relative_to(pilot_root))
            for key, path in screenshot_paths(adapter, output).items()
        }
        if (
            event.get("query") != query
            or event.get("query_sha256") != text_digest(query)
            or event.get("effective_query") != configuration.effective_query
            or event.get("effective_query_sha256")
            != text_digest(configuration.effective_query)
            or event.get("navigation_route_characters") != len(route)
            or event.get("expected_count_from_pilot005")
            != queries.EXPECTED_PILOT005_COUNTS[event_id]
            or event.get("page_size") != 30
            or event.get("limit") != 100
            or event.get("max_pages") != 4
            or event.get("screenshots") != declared_screenshots
            or output.parent != pilot_root / "searches/gates"
            or failure_output.parent != pilot_root / "searches/failures"
        ):
            raise RuntimeError(f"The OATD Pilot 006 event changed: {event_id}")
        paths = (
            output,
            failure_output,
            gate_marker_path(output),
            *screenshot_paths(adapter, output).values(),
        )
        for path in paths:
            resolved = path.resolve()
            if resolved in occupied:
                raise RuntimeError("An OATD Pilot 006 output path collides")
            occupied.add(resolved)
            if os.path.lexists(path):
                raise RuntimeError(
                    f"Refusing to overwrite OATD Pilot 006 output: {path}"
                )
    reconciliation = pilot_root / plan.get("reconciliation_output", "")
    if reconciliation.parent != pilot_root / "searches" or os.path.lexists(
        reconciliation
    ):
        raise RuntimeError("The OATD Pilot 006 reconciliation path is invalid")
    if reconciliation.resolve() in occupied:
        raise RuntimeError("The OATD Pilot 006 reconciliation path collides")
    return adapter, events, checkpoint, reconciliation


async def collect_gate(
    adapter: Any,
    event: dict[str, Any],
    output: Path,
    *,
    cdp_url: str,
    pass_delay_seconds: float,
) -> tuple[Any, Any, bool, dict[str, Any], dict[str, Any]]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is unavailable. Run through uv.") from error
    configuration = adapter.build_oatd_search_configuration(
        event["query"],
        language=event["language"],
        year_start=event["year_start"],
        year_end=event["year_end"],
        page_size=event["page_size"],
    )
    paths_value = adapter.screenshot_paths_for_output(output)
    payloads: dict[str, Any] = {}
    budget = adapter.OATDBusyRetryBudget(
        max_retries=event["busy_retries"],
        initial_delay_seconds=event["busy_retry_delay_seconds"],
    )
    started = now()
    async with async_playwright() as playwright, adapter._LeaseCleanup() as cleanup:
        lease = await adapter.open_owned_chrome_page(
            playwright,
            cdp_url=cdp_url,
            headless=False,
            timeout_seconds=event["timeout_seconds"],
            chrome_executable=None,
        )
        cleanup.lease = lease
        page = lease.page
        configured = await adapter.configure_oatd_search_page_for_screenshot(
            page,
            configuration=configuration,
            timeout_seconds=event["timeout_seconds"],
        )
        payloads["search_page"] = await adapter._capture_oatd_screenshot_payload(
            page,
            paths_value.search_page,
            page_kind="configured_search_page",
            configuration_evidence=configured,
        )
        first = await adapter.collect_shared_population_snapshot(
            page,
            query=event["query"],
            limit=event["limit"],
            max_pages=event["max_pages"],
            timeout_seconds=event["timeout_seconds"],
            page_delay_seconds=event["page_delay_seconds"],
            busy_retry_budget=budget,
            configuration=configuration,
            screenshot_paths=paths_value,
            screenshot_payloads=payloads,
        )
        if pass_delay_seconds:
            await asyncio.sleep(pass_delay_seconds)
        second = await adapter.collect_shared_population_snapshot(
            page,
            query=event["query"],
            limit=event["limit"],
            max_pages=event["max_pages"],
            timeout_seconds=event["timeout_seconds"],
            page_delay_seconds=event["page_delay_seconds"],
            busy_retry_budget=budget,
            configuration=configuration,
        )
        order_drift = adapter.reconcile_shared_population_snapshots(first, second)
    return (
        first,
        second,
        order_drift,
        payloads,
        {
            "started_at_utc": started,
            "completed_at_utc": now(),
            "busy_retries_performed": budget.performed_retries,
        },
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


def build_gate_artifact(
    adapter: Any,
    event: dict[str, Any],
    first: Any,
    second: Any,
    order_drift: bool,
    payloads: dict[str, Any],
    timing: dict[str, Any],
    output: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
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
        "pilot": "006",
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
            "country": None,
            "creative_commons_only": False,
        },
        "source_total": first.total,
        "pilot005_count": event["expected_count_from_pilot005"],
        "count_drift_from_pilot005": first.total
        - event["expected_count_from_pilot005"],
        "two_complete_id_passes_reconciled": True,
        "native_order_drift_observed": order_drift,
        "first_pass": snapshot_payload(adapter, first),
        "verification_pass": snapshot_payload(adapter, second),
        "record_details_requested": False,
        "records_hydrated": 0,
        "timing": timing,
        "transport": {
            "timeout_seconds": event["timeout_seconds"],
            "page_delay_seconds": event["page_delay_seconds"],
            "pass_delay_seconds": event["pass_delay_seconds"],
            "busy_retries": event["busy_retries"],
            "busy_retry_delay_seconds": event["busy_retry_delay_seconds"],
            "busy_retries_performed": timing["busy_retries_performed"],
        },
        "screenshots": {
            "schema_version": "oatd-pilot-006-screenshots/v1",
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
) -> dict[str, Any]:
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
    return marker


def validate_gate_artifact(adapter: Any, output: Path, event_id: str) -> dict[str, Any]:
    artifact = load(output)
    marker = load(gate_marker_path(output))
    screenshots = screenshot_paths(adapter, output)
    if (
        artifact.get("schema_version") != GATE_SCHEMA
        or artifact.get("event_id") != event_id
        or artifact.get("diagnostic_only") is not True
        or artifact.get("do_not_merge") is not True
        or artifact.get("record_details_requested") is not False
        or artifact.get("records_hydrated") != 0
        or artifact.get("two_complete_id_passes_reconciled") is not True
        or marker.get("schema_version") != GATE_MARKER_SCHEMA
        or marker.get("transaction_id")
        != artifact.get("publication", {}).get("transaction_id")
        or marker.get("paths_persisted") is not False
    ):
        raise RuntimeError(f"The OATD {event_id} card-ID artifact is invalid")
    files = marker.get("files")
    paths = {"json": output, **screenshots}
    if not isinstance(files, dict) or set(files) != set(paths):
        raise RuntimeError(f"The OATD {event_id} card-ID marker is invalid")
    for key, path in paths.items():
        evidence = files.get(key)
        if (
            not path.is_file()
            or not isinstance(evidence, dict)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != digest(path)
            or evidence.get("bytes") != path.stat().st_size
        ):
            raise RuntimeError(f"The OATD {event_id} {key} evidence is invalid")
    first = artifact.get("first_pass")
    second = artifact.get("verification_pass")
    if not isinstance(first, dict) or not isinstance(second, dict):
        raise RuntimeError(f"The OATD {event_id} snapshots are absent")
    first_ids = [card.get("paperId") for card in first.get("cards", [])]
    second_ids = [card.get("paperId") for card in second.get("cards", [])]
    total = artifact.get("source_total")
    if (
        not isinstance(total, int)
        or isinstance(total, bool)
        or total < 0
        or len(first_ids) != total
        or len(second_ids) != total
        or len(set(first_ids)) != total
        or len(set(second_ids)) != total
        or set(first_ids) != set(second_ids)
        or first.get("stable_record_ids_sha256")
        != second.get("stable_record_ids_sha256")
        or first.get("complete") is not True
        or second.get("complete") is not True
    ):
        raise RuntimeError(f"The OATD {event_id} snapshots did not reconcile")
    receipt = artifact.get("screenshots")
    if not isinstance(receipt, dict):
        raise RuntimeError(f"The OATD {event_id} screenshot receipt is absent")
    for key, path in screenshots.items():
        evidence = receipt.get(key)
        if (
            not isinstance(evidence, dict)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != digest(path)
            or evidence.get("full_page") is not True
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            raise RuntimeError(f"The OATD {event_id} screenshot receipt is invalid")
    return artifact


def build_reconciliation(
    adapter: Any,
    plan: dict[str, Any],
    events: list[dict[str, Any]],
    pilot_root: Path,
    checkpoint: Path,
) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    gate_totals: dict[str, int] = {}
    gate_set_hashes: dict[str, str] = {}
    occurrence_total = 0
    for event in events:
        artifact = validate_gate_artifact(
            adapter, pilot_root / event["output"], event["event_id"]
        )
        total = artifact["source_total"]
        gate_totals[event["event_id"]] = total
        gate_set_hashes[event["event_id"]] = artifact["first_pass"][
            "stable_record_ids_sha256"
        ]
        occurrence_total += total
        second_ranks = {
            card["paperId"]: card["rank"]
            for card in artifact["verification_pass"]["cards"]
        }
        for card in artifact["first_pass"]["cards"]:
            paper_id = card["paperId"]
            if paper_id not in by_id:
                ordered_ids.append(paper_id)
                by_id[paper_id] = {
                    "paperId": paper_id,
                    "title": card["title"],
                    "first_seen_gate": event["event_id"],
                    "gate_membership": [],
                }
            entry = by_id[paper_id]
            if card["title"] != entry["title"]:
                raise RuntimeError("OATD changed a card title across accepted gates")
            entry["gate_membership"].append(
                {
                    "gate_id": event["event_id"],
                    "first_pass_rank": card["rank"],
                    "verification_pass_rank": second_ranks[paper_id],
                }
            )
    checkpoint_value = load(checkpoint)
    completed_ids = checkpoint_value.get("completed_ids")
    if not isinstance(completed_ids, list) or len(completed_ids) != 338:
        raise RuntimeError("The Pilot 004 checkpoint records changed")
    reusable = [paper_id for paper_id in ordered_ids if paper_id in set(completed_ids)]
    return {
        "schema_version": RECONCILIATION_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "pilot": "006",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan_sha256": plan["plan_sha256_at_runtime"],
        "algebraic_candidate_union": plan["algebraic_candidate_union"],
        "gate_totals": gate_totals,
        "gate_stable_record_ids_sha256": gate_set_hashes,
        "gate_occurrence_total": occurrence_total,
        "exact_deduplicated_union_total": len(ordered_ids),
        "cross_gate_duplicate_occurrences": occurrence_total - len(ordered_ids),
        "union_order": "first gate occurrence, then source-rendered first-pass rank",
        "ordered_union_ids_sha256": adapter._ordered_record_ids_sha256(ordered_ids),
        "stable_union_ids_sha256": adapter._stable_record_ids_sha256(ordered_ids),
        "records": [by_id[paper_id] for paper_id in ordered_ids],
        "pilot004_checkpoint_reuse": {
            "validated_detail_records_available": len(reusable),
            "paper_ids": reusable,
            "remaining_unique_details_to_hydrate": len(ordered_ids) - len(reusable),
            "reuse_is_approved_for_final_search": False,
        },
        "record_details_requested": False,
        "records_hydrated": 0,
    }


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> int:
    if os.path.lexists(receipt_path):
        raise RuntimeError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    adapter, events, checkpoint, reconciliation_path = validate_plan(
        plan, plan_path, pilot_root
    )
    cdp_url = adapter.validate_local_cdp_url(
        os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL)
    )
    not_before = parse_utc(plan["source_safety"]["first_source_request_not_before_utc"])
    wait_seconds = max(0.0, (not_before - datetime.now(timezone.utc)).total_seconds())
    if wait_seconds:
        print(f"Waiting {wait_seconds:.1f} seconds for the OATD cooldown.", flush=True)
        time.sleep(wait_seconds)

    started = now()
    outcomes: list[dict[str, Any]] = []
    stopped = False
    for index, event in enumerate(events):
        if index:
            time.sleep(float(plan["source_safety"]["inter_gate_delay_seconds"]))
        output = pilot_root / event["output"]
        event_started = now()
        try:
            first, second, order_drift, payloads, timing = asyncio.run(
                collect_gate(
                    adapter,
                    event,
                    output,
                    cdp_url=cdp_url,
                    pass_delay_seconds=event["pass_delay_seconds"],
                )
            )
            artifact, validated_payloads = build_gate_artifact(
                adapter,
                event,
                first,
                second,
                order_drift,
                payloads,
                timing,
                output,
            )
            publish_gate(adapter, output, artifact, validated_payloads)
            outcome = {
                "event_id": event["event_id"],
                "started_at_utc": event_started,
                "completed_at_utc": now(),
                "success": True,
                "source_total": artifact["source_total"],
                "pilot005_count": artifact["pilot005_count"],
                "count_drift_from_pilot005": artifact["count_drift_from_pilot005"],
                "native_order_drift_observed": order_drift,
                "artifact": event["output"],
                "artifact_sha256": digest(output),
                "marker_sha256": digest(gate_marker_path(output)),
                "busy_retries_performed": timing["busy_retries_performed"],
            }
        except Exception as error:
            safe_message = (
                adapter.safe_error_message(error)
                if isinstance(error, adapter.OATDMetadataError)
                else "Unexpected OATD Pilot 006 card-ID workflow failure."
            )
            failure = {
                "schema_version": "oatd-pilot-006-card-id-failure/v1",
                "source": "Open Access Theses and Dissertations (OATD)",
                "pilot": "006",
                "event_id": event["event_id"],
                "protocol_commit": queries.PROTOCOL_COMMIT,
                "diagnostic_only": True,
                "do_not_merge": True,
                "requested_query": event["query"],
                "source_total": None,
                "stable_record_ids": None,
                "error_type": type(error).__name__,
                "error": safe_message,
                "started_at_utc": event_started,
                "completed_at_utc": now(),
            }
            failure_path = pilot_root / event["failure_output"]
            write_exclusive_json(failure_path, failure)
            fsync_parent(failure_path)
            outcome = {
                "event_id": event["event_id"],
                "started_at_utc": event_started,
                "completed_at_utc": now(),
                "success": False,
                "source_total": None,
                "artifact": None,
                "failure_artifact": event["failure_output"],
                "failure_artifact_sha256": digest(failure_path),
                "error_type": type(error).__name__,
                "error": safe_message,
            }
            stopped = True
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "event": event["event_id"],
                    "success": outcome["success"],
                    "total": outcome["source_total"],
                }
            ),
            flush=True,
        )
        if stopped:
            break

    reconciliation: dict[str, Any] | None = None
    if not stopped and len(outcomes) == len(events):
        runtime_plan = dict(plan)
        runtime_plan["plan_sha256_at_runtime"] = digest(plan_path)
        reconciliation = build_reconciliation(
            adapter, runtime_plan, events, pilot_root, checkpoint
        )
        write_exclusive_json(reconciliation_path, reconciliation)
        fsync_parent(reconciliation_path)
    success = reconciliation is not None
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": plan["source"],
        "pilot": "006",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(plan_path.relative_to(pilot_root)),
        "plan_sha256": digest(plan_path),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_gate_count": len(events),
        "completed_gate_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": success,
        "outcomes": outcomes,
        "reconciliation": (
            {
                "path": str(reconciliation_path.relative_to(pilot_root)),
                "sha256": digest(reconciliation_path),
                "exact_deduplicated_union_total": reconciliation[
                    "exact_deduplicated_union_total"
                ],
            }
            if reconciliation is not None
            else None
        ),
    }
    write_exclusive_json(receipt_path, receipt)
    fsync_parent(receipt_path)
    return 0 if success else 1


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
