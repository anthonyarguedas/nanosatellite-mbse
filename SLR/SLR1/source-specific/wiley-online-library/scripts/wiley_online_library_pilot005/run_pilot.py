#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Run the predeclared Wiley Pilot 005 native RIS events."""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping

from build_plan import (
    ADAPTER_PATH,
    ADAPTER_VERSION,
    DATE_END,
    DATE_START,
    DEFAULT_OUTPUT,
    EVENT_SCHEMA,
    PILOT_ROOT,
    REPOSITORY_ROOT,
    SCHEMA,
    file_sha256,
    load,
    validate,
)

DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
FAILURE_SCHEMA = "wiley-online-library-pilot005-failure/v1"
RECEIPT_SCHEMA = "wiley-online-library-pilot005-run-receipt/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def load_adapter(path: Path, plan: Mapping[str, Any]) -> Any:
    declaration = plan.get("adapter")
    if not isinstance(declaration, Mapping):
        raise RuntimeError("The event plan lacks an adapter declaration")
    if declaration.get("sha256") != file_sha256(path):
        raise RuntimeError("The Wiley adapter changed after predeclaration")
    spec = importlib.util.spec_from_file_location("wiley_p005_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Wiley adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if str(getattr(module, "ADAPTER_VERSION", "")) != ADAPTER_VERSION:
        raise RuntimeError(f"Wiley adapter version {ADAPTER_VERSION} is required")
    required = declaration.get("required_interfaces")
    if not isinstance(required, list) or any(
        not isinstance(name, str) or not hasattr(module, name) for name in required
    ):
        raise RuntimeError("The Wiley adapter lacks a predeclared native RIS interface")
    capabilities = getattr(module, "WILEY_PILOT003_COLLECTOR_CAPABILITIES", None)
    if (
        not isinstance(capabilities, Mapping)
        or capabilities.get("adapter_id") != "search_wiley_online_library"
        or str(capabilities.get("adapter_version")) != ADAPTER_VERSION
    ):
        raise RuntimeError("The Wiley adapter capability declaration is incompatible")
    return module


def write_json_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise FileExistsError(f"Refusing to overwrite {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def write_json_replace(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def event_output(root: Path, event: Mapping[str, Any]) -> Path:
    return root / "searches" / str(event["output"])


def screenshot_paths_match(
    adapter: Any, output: Path, metadata: Mapping[str, Any]
) -> bool:
    paths = adapter.screenshot_paths_for_output(output)
    screenshots = metadata.get("screenshots")
    if not isinstance(screenshots, Mapping):
        return False
    return bool(
        screenshots.get("schema_version") == "wiley-automatic-screenshots/v1"
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


def event_complete(adapter: Any, root: Path, event: Mapping[str, Any]) -> bool:
    output = event_output(root, event)
    try:
        artifact = load(output)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False
    metadata = artifact.get("output_metadata")
    ids = artifact.get("ordered_source_ids")
    native = artifact.get("native_ris_reconciliation")
    return bool(
        artifact.get("schema_version") == EVENT_SCHEMA
        and artifact.get("event_id") == event.get("event_id")
        and artifact.get("query") == event.get("query")
        and artifact.get("query_sha256") == event.get("query_sha256")
        and artifact.get("status") == "success"
        and artifact.get("diagnostic_only") is True
        and artifact.get("do_not_merge") is True
        and artifact.get("merge_eligible") is False
        and isinstance(metadata, Mapping)
        and metadata.get("retrieval_complete") is True
        and metadata.get("passes_completed") == 2
        and isinstance(ids, list)
        and artifact.get("source_total") == len(ids)
        and artifact.get("ordered_source_ids_sha256") == sequence_sha256(ids)
        and isinstance(native, Mapping)
        and native.get("every_source_doi_normalized_from_native_ris") is True
        and screenshot_paths_match(adapter, output, metadata)
    )


def exact_date_accounting(result: Mapping[str, Any]) -> dict[str, Any]:
    metadata = result["output_metadata"]
    ordered_ids = list(metadata["ordered_source_ids"])
    records = result["results"]
    status_by_id: dict[str, str] = {}
    source_dates: dict[str, str] = {}
    for record in records:
        doi = str(record["doi"])
        status = str(record.get("exactDateFilterStatus", ""))
        if status not in {"included", "unresolved"}:
            raise RuntimeError(f"Unexpected retained exact-date status for {doi}: {status}")
        if doi in status_by_id:
            raise RuntimeError(f"Repeated retained DOI during exact-date accounting: {doi}")
        status_by_id[doi] = status
        source_dates[doi] = str(record.get("sourcePublicationDate", ""))
    excluded_ids = [source_id for source_id in ordered_ids if source_id not in status_by_id]
    expected_excluded = metadata.get("excluded_by_client_date_filter")
    if expected_excluded != len(excluded_ids):
        raise RuntimeError("Wiley exact-date exclusion count did not reconcile the DOI ledger")
    unresolved_ids = [
        source_id for source_id in ordered_ids if status_by_id.get(source_id) == "unresolved"
    ]
    if metadata.get("unresolved_exact_dates_retained") != len(unresolved_ids):
        raise RuntimeError("Wiley unresolved exact-date count did not reconcile the DOI ledger")
    included_ids = [
        source_id for source_id in ordered_ids if status_by_id.get(source_id) == "included"
    ]
    if len(included_ids) + len(excluded_ids) + len(unresolved_ids) != len(ordered_ids):
        raise RuntimeError("Wiley exact-date dispositions did not cover every source DOI")
    return {
        "basis": "Wiley visible First published",
        "source_month_total": len(ordered_ids),
        "included_count": len(included_ids),
        "excluded_count": len(excluded_ids),
        "unresolved_count": len(unresolved_ids),
        "included_source_ids": included_ids,
        "excluded_source_ids": excluded_ids,
        "unresolved_source_ids": unresolved_ids,
        "retained_source_publication_dates": source_dates,
        "every_source_id_accounted_for": True,
    }


def native_ris_reconciliation(result: Mapping[str, Any]) -> dict[str, Any]:
    metadata = result["output_metadata"]
    source_total = int(result["total"])
    ids = list(metadata["ordered_source_ids"])
    records = result["results"]
    excluded = int(metadata["excluded_by_client_date_filter"])
    diagnostics = metadata.get("ris_export_diagnostics")
    if not isinstance(diagnostics, list) or not diagnostics:
        raise RuntimeError("Wiley returned no native RIS export diagnostics")
    for ordinal, item in enumerate(diagnostics, start=1):
        if not isinstance(item, Mapping) or not (
            item.get("completed_state") == "completed"
            and item.get("selected_doi_count") == item.get("exported_doi_count")
            and item.get("selected_doi_count") == item.get("ty_count")
            and item.get("selected_doi_count") == item.get("er_count")
            and isinstance(item.get("byte_count"), int)
            and item.get("byte_count") > 0
            and isinstance(item.get("sha256"), str)
            and len(item.get("sha256")) == 64
        ):
            raise RuntimeError(f"Native RIS diagnostic {ordinal} did not reconcile")
    if metadata.get("source_entries_retrieved") != source_total:
        raise RuntimeError("Native RIS source entries did not reconcile the source total")
    if len(records) + excluded != source_total:
        raise RuntimeError("Normalized RIS records and date exclusions did not cover the source total")
    normalized_dois = [str(record.get("doi")) for record in records]
    retained_ids = [source_id for source_id in ids if source_id in set(normalized_dois)]
    if normalized_dois != retained_ids or len(normalized_dois) != len(set(normalized_dois)):
        raise RuntimeError("Normalized native RIS DOI order did not match the retained source ledger")
    pages = int(metadata["pages_per_pass"])
    expected_downloads = pages if source_total == 1 else pages + 1
    if len(diagnostics) != expected_downloads:
        raise RuntimeError("Native RIS download count did not match page-scoped export behavior")
    first_pass = metadata["pass_reports"][0]
    page_selected_counts = [
        int(item["rendered_cards"]) for item in first_pass.get("pages", [])
    ]
    if sum(page_selected_counts) != source_total:
        raise RuntimeError("First-pass page counts did not reconcile the source DOI ledger")
    return {
        "route": "visible page scoped native RIS with abstracts",
        "raw_ris_persisted": False,
        "source_total": source_total,
        "source_entries_retrieved": metadata.get("source_entries_retrieved"),
        "normalized_record_count_before_date_exclusions": len(records) + excluded,
        "retained_normalized_record_count": len(records),
        "date_excluded_normalized_record_count": excluded,
        "preflight_export_count": metadata.get("export_preflight_records"),
        "page_export_count": pages,
        "download_count": len(diagnostics),
        "download_record_counts": [item["exported_doi_count"] for item in diagnostics],
        "download_byte_counts": [item["byte_count"] for item in diagnostics],
        "download_sha256": [item["sha256"] for item in diagnostics],
        "first_pass_page_record_counts": page_selected_counts,
        "every_batch_count_reconciled": True,
        "every_batch_ris_markers_reconciled": True,
        "every_source_doi_normalized_from_native_ris": True,
        "normalized_retained_doi_order_matches_source_ledger": True,
    }


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
        query=str(event["query"]),
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

    result = await adapter.collect_wiley_results(
        page,
        query=str(event["query"]),
        limit=int(event["limit"]),
        max_pages=int(event["max_pages"]),
        timeout_seconds=timeout_seconds,
        page_delay_seconds=page_delay_seconds,
        passes=2,
        date_bounds=bounds,
        content="articlesChapters",
        sort="Earliest",
        result_url=None,
        count_only=False,
        native_export_plan=None,
        expected_source_total=None,
        max_source_total=int(event["max_source_total"]),
        authorization_reassertion=authorization_reassertion,
        field1="AllField",
        screenshot_paths=screenshot_paths,
        screenshot_payloads=screenshot_payloads,
    )
    await authorization_reassertion()
    metadata = result.get("output_metadata")
    if not isinstance(metadata, dict):
        raise adapter.WileyProtocolError("Wiley native RIS result lacked metadata")
    if set(screenshot_payloads) != {"search_page", "results_page"}:
        raise adapter.WileyProtocolError("Wiley did not capture both mandatory screenshots")
    metadata["screenshots"] = {
        "schema_version": "wiley-automatic-screenshots/v1",
        "automatic": True,
        "no_opt_out": True,
        "search_page": dict(screenshot_payloads["search_page"].evidence),
        "results_page": dict(screenshot_payloads["results_page"].evidence),
    }
    if not (
        result.get("total") == metadata.get("source_entries_retrieved")
        and metadata.get("retrieval_complete") is True
        and metadata.get("passes_completed") == 2
        and metadata.get("export_method")
        == "visible_page_scoped_normal_ui_ris_with_abstracts"
        and metadata.get("stopped_reason") == "all_available_records"
        and metadata.get("status") == "success"
    ):
        raise adapter.WileyProtocolError("Wiley event did not complete its native RIS contract")
    ids = list(metadata.get("ordered_source_ids", []))
    if len(ids) != result.get("total") or len(ids) != len(set(ids)):
        raise adapter.WileyProtocolError("Wiley complete DOI ledger did not reconcile its total")
    pass_reports = metadata.get("pass_reports")
    if not isinstance(pass_reports, list) or len(pass_reports) != 2:
        raise adapter.WileyProtocolError("Wiley event lacked two complete pass receipts")
    if any(report.get("ordered_ids_sha256") != sequence_sha256(ids) for report in pass_reports):
        raise adapter.WileyProtocolError("Wiley complete ordered DOI pass hashes changed")

    date_accounting = exact_date_accounting(result)
    native_reconciliation = native_ris_reconciliation(result)
    metadata.update(
        {
            "pilot": "005",
            "event_id": event["event_id"],
            "diagnostic_only": True,
            "do_not_merge": True,
            "merge_eligible": False,
            "normalized_merge_eligible": False,
            "raw_native_ris_persisted": False,
            "pilot_native_ris_final_readiness": True,
            "target_id_retained": False,
            "session_url_retained": False,
        }
    )
    artifact = {
        "schema_version": EVENT_SCHEMA,
        "pilot": "005",
        "source": "Wiley Online Library",
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "branch": event["branch"],
        "status": "success",
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
        "query": event["query"],
        "query_characters": event["query_characters"],
        "query_sha256": event["query_sha256"],
        "date_start": DATE_START,
        "date_end": DATE_END,
        "source_total": result["total"],
        "pilot004_reference_total": event["pilot004_reference_total"],
        "source_total_change_from_pilot004": result["total"]
        - event["pilot004_reference_total"],
        "ordered_source_ids": ids,
        "ordered_source_ids_sha256": sequence_sha256(ids),
        "results_retrieved": result["results_retrieved"],
        "records": result["results"],
        "exact_date_accounting": date_accounting,
        "native_ris_reconciliation": native_reconciliation,
        "passes": pass_reports,
        "output_metadata": metadata,
        "captured_at_utc": now(),
    }
    return artifact, {"paths": screenshot_paths, "payloads": screenshot_payloads}


async def run_attempt(
    adapter: Any,
    playwright: Any,
    event: Mapping[str, Any],
    output: Path,
    *,
    cdp_url: str,
    target_id: str,
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
        "schema_version": FAILURE_SCHEMA,
        "pilot": "005",
        "source": "Wiley Online Library",
        "event_id": event_id,
        "attempt": attempt,
        "status": "error",
        "source_total": None,
        "ordered_source_ids": [],
        "native_ris_records": [],
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
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
        "schema_version": RECEIPT_SCHEMA,
        "pilot": "005",
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
        "target_id_retained": False,
        "outcomes": outcomes,
    }


def verify_script_hashes(plan: Mapping[str, Any]) -> None:
    dependencies = plan.get("dependencies")
    scripts = dependencies.get("source_affecting_scripts") if isinstance(dependencies, Mapping) else None
    if not isinstance(scripts, Mapping):
        raise RuntimeError("The event plan lacks source script hashes")
    for relative, expected in scripts.items():
        path = REPOSITORY_ROOT / str(relative)
        if not path.is_file() or file_sha256(path) != expected:
            raise RuntimeError(f"Source script changed after predeclaration: {relative}")


async def run(args: argparse.Namespace) -> int:
    plan_path = args.plan.expanduser().resolve()
    root = args.pilot_root.expanduser().resolve()
    receipt_path = args.receipt.expanduser().resolve()
    plan = load(plan_path)
    errors = validate(plan)
    if errors or plan.get("schema_version") != SCHEMA:
        raise RuntimeError("Invalid event plan: " + "; ".join(errors))
    verify_script_hashes(plan)
    adapter_path = args.adapter_path.expanduser().resolve()
    adapter = load_adapter(adapter_path, plan)
    target_id = args.target_id or os.environ.get("WILEY_AUTHORIZED_TARGET_ID")
    if not target_id:
        raise RuntimeError(
            "Pilot 005 requires --target-id or WILEY_AUTHORIZED_TARGET_ID for an exact authorized Wiley page"
        )
    events = list(plan["events"])
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
                        cdp_url=args.cdp_url,
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
                            "native_ris_download_count": artifact[
                                "native_ris_reconciliation"
                            ]["download_count"],
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
        default=Path(os.environ.get("WILEY_ADAPTER_PATH", ADAPTER_PATH)),
    )
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    parser.add_argument("--target-id")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--max-events", type=int)
    args = parser.parse_args()
    if args.max_attempts < 1 or args.max_attempts > 2:
        parser.error("--max-attempts must be 1 or 2")
    if args.max_events is not None and args.max_events < 1:
        parser.error("--max-events must be positive")
    if not args.timeout > 0 or not args.page_delay_seconds >= 0:
        parser.error("timeout and page delay must be nonnegative, with a positive timeout")
    return args


def main() -> int:
    return asyncio.run(run(parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
