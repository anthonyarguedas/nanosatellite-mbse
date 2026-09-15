#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Run the predeclared Wiley Pilot 004 stable-ID and screenshot events."""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping

from build_plan import (
    ADAPTER_MIN_VERSION,
    DATE_END,
    DATE_START,
    DEFAULT_OUTPUT,
    PILOT_ROOT,
    PROTOCOL_COMMIT,
    SCHEMA,
    load,
    validate,
)

DEFAULT_ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_wiley_online_library.py"
)
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
PAGE_SIZE = 20
MAX_SOURCE_TOTAL = 5000


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_adapter(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("wiley_p004_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Wiley adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    try:
        version = int(module.ADAPTER_VERSION)
    except (AttributeError, TypeError, ValueError) as error:
        raise RuntimeError("Wiley adapter has no numeric version") from error
    required = (
        "open_authorized_wiley_attached_page",
        "reassert_authorized_wiley_target",
        "close_owned_chrome_page_verified",
        "establish_wiley_access",
        "configure_wiley_advanced_search_for_screenshot",
        "_capture_wiley_full_page_screenshot_payload",
        "_publish_wiley_screenshot_bundle",
        "build_search_url",
        "navigate",
        "wait_for_ready_page",
        "exact_date_filter_status",
        "WileySnapshotChangedError",
    )
    if version < ADAPTER_MIN_VERSION or any(not hasattr(module, name) for name in required):
        raise RuntimeError(
            f"Wiley adapter version {ADAPTER_MIN_VERSION}+ with automatic screenshots is required"
        )
    capabilities = getattr(module, "WILEY_PILOT003_COLLECTOR_CAPABILITIES", None)
    if (
        not isinstance(capabilities, Mapping)
        or capabilities.get("adapter_id") != "search_wiley_online_library"
        or int(capabilities.get("adapter_version", "0")) < ADAPTER_MIN_VERSION
    ):
        raise RuntimeError("Wiley adapter capability declaration is incompatible")
    return module


def write_json_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise FileExistsError(f"Refusing to overwrite {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def write_json_replace(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def event_output(root: Path, event: Mapping[str, Any]) -> Path:
    return root / "searches" / str(event["output"])


def event_complete(adapter: Any, root: Path, event: Mapping[str, Any]) -> bool:
    output = event_output(root, event)
    paths = adapter.screenshot_paths_for_output(output)
    try:
        artifact = load(output)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False
    metadata = artifact.get("output_metadata")
    screenshots = metadata.get("screenshots") if isinstance(metadata, Mapping) else None
    ids = artifact.get("ordered_source_ids")
    passes = artifact.get("passes")
    return bool(
        artifact.get("schema_version") == "wiley-online-library-pilot004-source-event/v1"
        and artifact.get("event_id") == event.get("event_id")
        and artifact.get("query") == event.get("query")
        and artifact.get("query_sha256") == event.get("query_sha256")
        and artifact.get("status") == "success"
        and artifact.get("diagnostic_only") is True
        and artifact.get("do_not_merge") is True
        and isinstance(ids, list)
        and artifact.get("source_total") == len(ids)
        and artifact.get("ordered_source_ids_sha256") == sequence_sha256(ids)
        and isinstance(passes, list)
        and len(passes) == 2
        and passes[0].get("ordered_source_ids") == passes[1].get("ordered_source_ids")
        and isinstance(screenshots, Mapping)
        and screenshots.get("schema_version") == "wiley-automatic-screenshots/v1"
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
        and screenshots.get("search_page", {}).get("path") == paths.search_page.name
        and screenshots.get("results_page", {}).get("path") == paths.results_page.name
        and paths.search_page.is_file()
        and paths.results_page.is_file()
        and hashlib.sha256(paths.search_page.read_bytes()).hexdigest()
        == screenshots.get("search_page", {}).get("sha256")
        and hashlib.sha256(paths.results_page.read_bytes()).hexdigest()
        == screenshots.get("results_page", {}).get("sha256")
    )


def _tab_totals(state: Any) -> dict[str, int | None]:
    return {
        "articlesChapters": state.articles_total,
        "journalTitle": state.publications_total,
        "collections": state.collections_total,
        "sponsored-content": state.industry_insights_total,
    }


def _card_projection(
    adapter: Any,
    state: Any,
    *,
    rank_start: int,
    bounds: Any,
) -> list[dict[str, Any]]:
    if not (
        len(state.ordered_ids)
        == len(state.publication_dates)
        == len(state.result_cards)
    ):
        raise adapter.WileyProtocolError(
            "Wiley DOI, date, and rendered-card ledgers did not align"
        )
    records = []
    for offset, (source_id, source_date, card) in enumerate(
        zip(state.ordered_ids, state.publication_dates, state.result_cards)
    ):
        if card.get("id") != source_id or card.get("kind") != "doi":
            raise adapter.WileyProtocolError(
                "Wiley rendered-card identity changed from its DOI ledger"
            )
        records.append(
            {
                "source_id": source_id,
                "doi": source_id,
                "rank": rank_start + offset,
                "title": card.get("title", ""),
                "rendered_card_description": card.get("description", ""),
                "rendered_card_description_status": "not_assumed_to_be_an_abstract",
                "source_publication_date": source_date,
                "source_publication_date_basis": "Wiley rendered First published",
                "exact_date_filter_status": adapter.exact_date_filter_status(
                    {}, bounds, source_date
                ),
            }
        )
    return records


async def collect_on_page(
    adapter: Any,
    page: Any,
    event: Mapping[str, Any],
    output: Path,
    *,
    timeout_seconds: float,
    page_delay_seconds: float,
    authorization_reassertion: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    query = str(event["query"])
    bounds = adapter.resolve_date_bounds(
        year_start=None,
        year_end=None,
        date_start=date.fromisoformat(DATE_START),
        date_end=date.fromisoformat(DATE_END),
        relative_date=None,
    )
    screenshot_paths = adapter.screenshot_paths_for_output(output)
    screenshot_payloads: dict[str, Any] = {}

    await authorization_reassertion()
    await adapter.establish_wiley_access(page, timeout_seconds)
    configuration = await adapter.configure_wiley_advanced_search_for_screenshot(
        page,
        query=query,
        date_bounds=bounds,
        field1="AllField",
    )
    screenshot_payloads["search_page"] = (
        await adapter._capture_wiley_full_page_screenshot_payload(
            page,
            screenshot_paths.search_page,
            page_kind="configured_advanced_search_page",
            configuration_evidence=configuration,
        )
    )
    await authorization_reassertion()

    baseline_total: int | None = None
    baseline_pages: list[list[str]] = []
    baseline_card_hashes: list[str] = []
    baseline_tab_totals: dict[str, int | None] | None = None
    baseline_readback: dict[str, Any] | None = None
    records: list[dict[str, Any]] = []
    pass_reports: list[dict[str, Any]] = []

    for pass_index in range(2):
        pass_ids: list[str] = []
        pass_seen: set[str] = set()
        page_reports: list[dict[str, Any]] = []
        expected_pages: int | None = None
        page_number = 0
        while expected_pages is None or page_number < expected_pages:
            await authorization_reassertion()
            url = adapter.build_search_url(
                query,
                page_number=page_number,
                date_bounds=bounds,
                content="articlesChapters",
                sort="Earliest",
                field1="AllField",
            )
            await adapter.navigate(page, url, timeout_seconds)
            state = await adapter.wait_for_ready_page(
                page,
                query=query,
                page_number=page_number,
                date_bounds=bounds,
                content="articlesChapters",
                sort="Earliest",
                expected_total=baseline_total,
                timeout_seconds=timeout_seconds,
                require_export=False,
                field1="AllField",
                snapshot_pass_ordinal=pass_index + 1,
            )
            if state.total is None:
                raise adapter.WileyProtocolError("Wiley exposed no exact source total")
            if baseline_total is None:
                baseline_total = state.total
                if baseline_total > MAX_SOURCE_TOTAL:
                    raise adapter.WileyInputError(
                        f"Wiley source total {baseline_total} exceeds pilot cap {MAX_SOURCE_TOTAL}"
                    )
            if state.total != baseline_total:
                raise adapter.WileySnapshotChangedError(
                    "Wiley source total changed during the pilot event",
                    phase_code="result_page",
                    page_ordinal=page_number + 1,
                    pass_ordinal=pass_index + 1,
                    baseline_total=baseline_total,
                    observed_total=state.total,
                    reason_code="source_total_changed",
                )
            expected_pages = max(1, math.ceil(baseline_total / PAGE_SIZE))
            tabs = _tab_totals(state)
            if baseline_tab_totals is None:
                baseline_tab_totals = tabs
            elif tabs != baseline_tab_totals:
                raise adapter.WileySnapshotChangedError(
                    "Wiley result tab totals changed during the pilot event",
                    phase_code="result_tabs",
                    page_ordinal=page_number + 1,
                    pass_ordinal=pass_index + 1,
                    baseline_total=baseline_total,
                    observed_total=state.total,
                    reason_code="tab_totals_changed",
                )
            readback = {
                "server_normalized_search_title": state.server_normalized_title,
                "server_normalized_date_range": state.normalized_date_range,
                "query_readbacks": list(state.query_readbacks),
                "applied_filter_labels": list(state.applied_filter_labels),
                "sort_displays": list(state.sort_displays),
                "sort_options": list(state.sort_options),
            }
            if baseline_readback is None:
                baseline_readback = readback
            elif readback != baseline_readback:
                raise adapter.WileySnapshotChangedError(
                    "Wiley visible query/date/sort readback changed during the pilot event",
                    phase_code="result_readback",
                    page_ordinal=page_number + 1,
                    pass_ordinal=pass_index + 1,
                    baseline_total=baseline_total,
                    observed_total=state.total,
                    reason_code="readback_changed",
                )

            ids = list(state.ordered_ids)
            if pass_seen.intersection(ids):
                raise adapter.WileyProtocolError("Wiley repeated a DOI across pages")
            pass_seen.update(ids)
            pass_ids.extend(ids)
            card_hash = canonical_sha256(state.result_cards)
            page_reports.append(
                {
                    "page": page_number,
                    "source_total": state.total,
                    "rendered_cards": state.card_count,
                    "ordered_source_ids_sha256": sequence_sha256(ids),
                    "result_card_metadata_sha256": card_hash,
                }
            )
            if pass_index == 0:
                baseline_pages.append(ids)
                baseline_card_hashes.append(card_hash)
                records.extend(
                    _card_projection(
                        adapter,
                        state,
                        rank_start=page_number * PAGE_SIZE + 1,
                        bounds=bounds,
                    )
                )
                if page_number == 0:
                    screenshot_payloads["results_page"] = (
                        await adapter._capture_wiley_full_page_screenshot_payload(
                            page,
                            screenshot_paths.results_page,
                            page_kind="first_results_page",
                        )
                    )
            else:
                if ids != baseline_pages[page_number]:
                    raise adapter.WileySnapshotChangedError(
                        "Wiley ordered DOI page changed between passes",
                        phase_code="verification_page",
                        page_ordinal=page_number + 1,
                        pass_ordinal=pass_index + 1,
                        baseline_total=baseline_total,
                        observed_total=state.total,
                        reason_code="ordered_ids_changed",
                    )
                if card_hash != baseline_card_hashes[page_number]:
                    raise adapter.WileySnapshotChangedError(
                        "Wiley rendered-card metadata changed between passes",
                        phase_code="verification_page",
                        page_ordinal=page_number + 1,
                        pass_ordinal=pass_index + 1,
                        baseline_total=baseline_total,
                        observed_total=state.total,
                        reason_code="card_metadata_changed",
                    )
            page_number += 1
            if page_delay_seconds and page_number < expected_pages:
                await asyncio.sleep(page_delay_seconds)

        if len(pass_ids) != baseline_total:
            raise adapter.WileyProtocolError(
                "Wiley complete pass did not reconcile the source total"
            )
        if pass_index == 1 and pass_ids != [item for page_ids in baseline_pages for item in page_ids]:
            raise adapter.WileySnapshotChangedError(
                "Wiley complete ordered DOI pass changed",
                phase_code="verification_pass",
                page_ordinal=len(baseline_pages),
                pass_ordinal=2,
                baseline_total=baseline_total,
                observed_total=baseline_total,
                reason_code="ordered_ids_changed",
            )
        pass_reports.append(
            {
                "pass_number": pass_index + 1,
                "pages": page_reports,
                "ordered_source_ids": pass_ids,
                "ordered_source_ids_sha256": sequence_sha256(pass_ids),
            }
        )

    if baseline_total is None or len(records) != baseline_total:
        raise adapter.WileyProtocolError("Wiley event did not retain every rendered card")
    ordered_ids = pass_reports[0]["ordered_source_ids"]
    retained_ids = [
        record["source_id"]
        for record in records
        if record["exact_date_filter_status"] != "excluded"
    ]
    excluded_ids = [
        record["source_id"]
        for record in records
        if record["exact_date_filter_status"] == "excluded"
    ]
    unresolved_ids = [
        record["source_id"]
        for record in records
        if record["exact_date_filter_status"] == "unresolved"
    ]
    screenshot_receipt = {
        "schema_version": "wiley-automatic-screenshots/v1",
        "automatic": True,
        "no_opt_out": True,
        "search_page": dict(screenshot_payloads["search_page"].evidence),
        "results_page": dict(screenshot_payloads["results_page"].evidence),
    }
    artifact = {
        "schema_version": "wiley-online-library-pilot004-source-event/v1",
        "pilot": "004",
        "source": "Wiley Online Library",
        "event_id": event["event_id"],
        "variant": event["variant"],
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "branch": event["branch"],
        "status": "success",
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
        "query": query,
        "query_characters": len(query),
        "query_sha256": text_sha256(query),
        "source_total": baseline_total,
        "ordered_source_ids": ordered_ids,
        "ordered_source_ids_sha256": sequence_sha256(ordered_ids),
        "diagnostic_window_ordered_source_ids": retained_ids,
        "diagnostic_window_ordered_source_ids_sha256": sequence_sha256(retained_ids),
        "excluded_after_diagnostic_cutoff_source_ids": excluded_ids,
        "unresolved_exact_date_source_ids": unresolved_ids,
        "records": records,
        "passes": pass_reports,
        "output_metadata": {
            "adapter": {
                "id": adapter.ADAPTER_ID,
                "version": adapter.ADAPTER_VERSION,
            },
            "protocol_commit": PROTOCOL_COMMIT,
            "source_route": "articlesChapters/default",
            "field": "AllField/Anywhere",
            "date_start": DATE_START,
            "date_end": DATE_END,
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "date_basis": "Wiley visible First published",
            "sort": "Date / sortBy=Earliest (observed newest-first)",
            "page_size": PAGE_SIZE,
            "passes_completed": 2,
            "retrieval_complete": True,
            "source_total_reconciled": True,
            "native_ris_used": False,
            "rendered_card_description_is_abstract": False,
            "language_filter": None,
            "publication_type_facet": None,
            "access_filter": None,
            "controlled_vocabulary_supplement": None,
            "proximity_operator": None,
            "pair_expansion": False,
            "result_type_tab_totals": baseline_tab_totals,
            "source_readback": baseline_readback,
            "screenshots": screenshot_receipt,
            "target_id_retained": False,
            "session_url_retained": False,
            "captured_at_utc": now(),
        },
    }
    return artifact, {
        "paths": screenshot_paths,
        "payloads": screenshot_payloads,
    }


async def run_attempt(
    adapter: Any,
    playwright: Any,
    event: Mapping[str, Any],
    output: Path,
    *,
    cdp_url: str,
    target_id: str | None,
    timeout_seconds: float,
    page_delay_seconds: float,
) -> dict[str, Any]:
    lease: Any | None = None
    setup_lease: Any | None = None

    def retain_setup_lease(created: Any) -> None:
        nonlocal setup_lease
        setup_lease = created

    authorization: Any | None = None
    boundary: Any | None = None
    caught: BaseException | None = None
    result: tuple[dict[str, Any], dict[str, Any]] | None = None
    try:
        lease, authorization = await adapter.open_authorized_wiley_attached_page(
            playwright,
            cdp_url=cdp_url,
            target_id=target_id,
            timeout_seconds=timeout_seconds,
            _lease_handoff=retain_setup_lease,
        )
        boundary = adapter._WileyAttachedPageNetworkBoundary(
            lease.page,
            context=lease.context,
            browser=lease.browser,
            owned_target_id=lease.owned_target_id,
        )
        if not await boundary.arm():
            raise adapter.WileyBrowserError("Could not arm Wiley owned-page boundary")

        async def reassert() -> None:
            await adapter.reassert_authorized_wiley_target(authorization)
            await boundary.assert_clean()

        result = await collect_on_page(
            adapter,
            lease.page,
            event,
            output,
            timeout_seconds=timeout_seconds,
            page_delay_seconds=page_delay_seconds,
            authorization_reassertion=reassert,
        )
        await reassert()
    except BaseException as error:
        caught = error

    cleanup_lease = lease if lease is not None else setup_lease
    cleanup_verified = cleanup_lease is None
    if boundary is not None and boundary.armed:
        try:
            await boundary.assert_clean()
        except BaseException as error:
            if caught is None:
                caught = error
        try:
            await boundary.begin_verified_close()
        except BaseException as error:
            if caught is None:
                caught = error
    if cleanup_lease is not None:
        try:
            outcome = await adapter.close_owned_chrome_page_verified(cleanup_lease)
            cleanup_verified = bool(outcome.verified)
        except BaseException as error:
            if caught is None:
                caught = error
    if boundary is not None and boundary.armed and cleanup_verified:
        try:
            await boundary.disarm_after_verified_close()
        except BaseException as error:
            if caught is None:
                caught = error
    if not cleanup_verified:
        raise adapter.WileyBrowserError(
            "Wiley pilot owned-page cleanup could not be verified"
        ) from caught
    if caught is not None:
        raise caught
    if result is None:
        raise adapter.WileyBrowserError("Wiley pilot attempt returned no result")
    artifact, screenshot_bundle = result
    adapter._publish_wiley_screenshot_bundle(
        screenshot_bundle["payloads"], screenshot_bundle["paths"]
    )
    write_json_create_only(output, artifact)
    return artifact


def failure_artifact(
    root: Path, event_id: str, attempt: int, error: BaseException
) -> Path:
    path = (
        root
        / "searches"
        / "failures"
        / f"{event_id}.attempt-{attempt:02d}.NON_MERGEABLE_FAILURE.json"
    )
    payload = {
        "schema_version": "wiley-online-library-pilot004-failure/v1",
        "pilot": "004",
        "event_id": event_id,
        "attempt": attempt,
        "status": "error",
        "source_total": None,
        "ordered_source_ids": [],
        "diagnostic_only": True,
        "do_not_merge": True,
        "error_type": type(error).__name__,
        "error": " ".join(str(error).split())[:500],
        "target_id_retained": False,
        "captured_at_utc": now(),
    }
    write_json_create_only(path, payload)
    return path


def receipt_payload(
    *,
    plan_path: Path,
    events: list[Mapping[str, Any]],
    outcomes: list[dict[str, Any]],
    status: str,
    started_at: str,
) -> dict[str, Any]:
    completed = {
        item["event_id"]
        for item in outcomes
        if item.get("status") in {"complete", "reused_existing"}
    }
    return {
        "schema_version": "wiley-online-library-pilot004-run-receipt/v1",
        "pilot": "004",
        "source": "Wiley Online Library",
        "status": status,
        "diagnostic_only": True,
        "do_not_merge": True,
        "event_plan": (
            str(plan_path.relative_to(PILOT_ROOT))
            if PILOT_ROOT in plan_path.parents
            else plan_path.name
        ),
        "predeclared_event_count": len(events),
        "completed_event_count": len(completed),
        "started_at_utc": started_at,
        "updated_at_utc": now(),
        "outcomes": outcomes,
    }


async def run(args: argparse.Namespace) -> int:
    plan_path = args.plan.expanduser().resolve()
    root = args.pilot_root.expanduser().resolve()
    receipt_path = args.receipt.expanduser().resolve()
    plan = load(plan_path)
    errors = validate(plan)
    if errors or plan.get("schema_version") != SCHEMA:
        raise RuntimeError("Invalid event plan: " + "; ".join(errors))
    adapter_path = args.adapter_path.expanduser().resolve()
    adapter = load_adapter(adapter_path)
    target_id = args.target_id or os.environ.get("WILEY_AUTHORIZED_TARGET_ID")
    cdp_url = args.cdp_url
    events = plan["events"]
    selected = events[: args.max_events] if args.max_events else events
    outcomes: list[dict[str, Any]] = []
    started_at = now()

    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        for event in selected:
            output = event_output(root, event)
            if event_complete(adapter, root, event):
                outcomes.append(
                    {
                        "event_id": event["event_id"],
                        "status": "reused_existing",
                        "output": str(output.relative_to(root)),
                        "updated_at_utc": now(),
                    }
                )
                print(f"{event['event_id']}: reused existing", flush=True)
                continue
            paths = adapter.screenshot_paths_for_output(output)
            if any(os.path.lexists(path) for path in (output, paths.search_page, paths.results_page)):
                raise RuntimeError(
                    f"Incomplete existing output or screenshot blocks {event['event_id']}"
                )
            completed = False
            prior_failures = len(
                list(
                    (root / "searches" / "failures").glob(
                        f"{event['event_id']}.attempt-*.NON_MERGEABLE_FAILURE.json"
                    )
                )
            )
            for offset in range(args.max_attempts):
                attempt = prior_failures + offset + 1
                print(f"{event['event_id']}: attempt {attempt}", flush=True)
                started_event = now()
                try:
                    artifact = await run_attempt(
                        adapter,
                        playwright,
                        event,
                        output,
                        cdp_url=cdp_url,
                        target_id=target_id,
                        timeout_seconds=args.timeout,
                        page_delay_seconds=args.page_delay_seconds,
                    )
                    outcomes.append(
                        {
                            "event_id": event["event_id"],
                            "attempt": attempt,
                            "status": "complete",
                            "source_total": artifact["source_total"],
                            "output": str(output.relative_to(root)),
                            "started_at_utc": started_event,
                            "updated_at_utc": now(),
                        }
                    )
                    completed = True
                    print(
                        f"{event['event_id']}: complete ({artifact['source_total']})",
                        flush=True,
                    )
                    break
                except BaseException as error:
                    failure = failure_artifact(root, event["event_id"], attempt, error)
                    retryable = adapter.is_retryable_wiley_snapshot_error(error)
                    outcomes.append(
                        {
                            "event_id": event["event_id"],
                            "attempt": attempt,
                            "status": "failed",
                            "retryable_snapshot_change": retryable,
                            "failure_artifact": str(failure.relative_to(root)),
                            "started_at_utc": started_event,
                            "updated_at_utc": now(),
                        }
                    )
                    write_json_replace(
                        receipt_path,
                        receipt_payload(
                            plan_path=plan_path,
                            events=events,
                            outcomes=outcomes,
                            status="running",
                            started_at=started_at,
                        ),
                    )
                    if not retryable or offset + 1 >= args.max_attempts:
                        print(
                            f"{event['event_id']}: stopped on {type(error).__name__}: {error}",
                            file=sys.stderr,
                            flush=True,
                        )
                        write_json_replace(
                            receipt_path,
                            receipt_payload(
                                plan_path=plan_path,
                                events=events,
                                outcomes=outcomes,
                                status="stopped_on_source_or_adapter_failure",
                                started_at=started_at,
                            ),
                        )
                        return 1
            if not completed:
                return 1
            write_json_replace(
                receipt_path,
                receipt_payload(
                    plan_path=plan_path,
                    events=events,
                    outcomes=outcomes,
                    status="running",
                    started_at=started_at,
                ),
            )

    status = "complete" if len(selected) == len(events) else "bounded_stop"
    write_json_replace(
        receipt_path,
        receipt_payload(
            plan_path=plan_path,
            events=events,
            outcomes=outcomes,
            status=status,
            started_at=started_at,
        ),
    )
    print(json.dumps({"status": status, "completed_events": len(selected)}))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=Path(os.environ.get("WILEY_ADAPTER_PATH", DEFAULT_ADAPTER)),
    )
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    parser.add_argument("--target-id")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--max-events", type=int)
    args = parser.parse_args()
    if args.max_attempts < 1 or args.max_attempts > 3:
        parser.error("--max-attempts must be 1 through 3")
    if args.max_events is not None and args.max_events < 1:
        parser.error("--max-events must be positive")
    return args


def main() -> int:
    return asyncio.run(run(parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
