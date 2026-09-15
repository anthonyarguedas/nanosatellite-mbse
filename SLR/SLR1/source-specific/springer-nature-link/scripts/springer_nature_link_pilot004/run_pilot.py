#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Run Springer Pilot 004 complete rendered card-path comparisons."""

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
    LANGUAGE,
    PILOT_ROOT,
    PROTOCOL_COMMIT,
    REVISED_SCHEMA,
    SCHEMA,
    SNAPSHOT_RETEST_SCHEMA,
    SORT,
    STABLE_PAGINATION_SCHEMA,
    YEAR_PARTITION_SCHEMA,
)

DEFAULT_ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_springer_link.py"
)
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
PAGE_SIZE = 20
MAX_ATTEMPTS = 3


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


def write_json_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_adapter(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("springer_p004_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Springer adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    try:
        version = int(module.ADAPTER_VERSION)
    except (AttributeError, TypeError, ValueError) as error:
        raise RuntimeError("Springer adapter has no numeric version") from error
    required = (
        "open_springer_owned_page",
        "close_springer_owned_page",
        "configure_springer_advanced_search_for_screenshot",
        "_capture_springer_full_page_screenshot_payload",
        "_publish_springer_screenshot_bundle",
        "validate_springer_screenshot_destinations",
        "navigate_to_search",
        "wait_for_springer_page",
        "build_search_url",
        "resolve_date_bounds",
        "_springer_canonical_order_evidence",
        "canonicalize_springer_rows",
        "parse_springer_publication_date",
        "SpringerSnapshotChangedError",
    )
    capabilities = getattr(module, "SPRINGER_AUTOMATIC_SCREENSHOT_CAPABILITIES", None)
    if (
        version < ADAPTER_MIN_VERSION
        or any(not hasattr(module, name) for name in required)
        or not isinstance(capabilities, Mapping)
        or capabilities.get("adapter_id") != "search_springer_link"
        or int(capabilities.get("adapter_version", "0")) < ADAPTER_MIN_VERSION
        or capabilities.get("automatic") is not True
        or capabilities.get("no_opt_out") is not True
    ):
        raise RuntimeError(
            f"Springer adapter version {ADAPTER_MIN_VERSION}+ with mandatory screenshots is required"
        )
    return module


def validate_plan(plan: dict[str, Any]) -> None:
    if (
        plan.get("schema_version")
        not in {
            SCHEMA,
            REVISED_SCHEMA,
            STABLE_PAGINATION_SCHEMA,
            YEAR_PARTITION_SCHEMA,
            SNAPSHOT_RETEST_SCHEMA,
        }
        or plan.get("protocol_commit") != PROTOCOL_COMMIT
        or plan.get("event_count") not in {8, 18, 20, 26, 74}
        or not isinstance(plan.get("events"), list)
        or len(plan["events"]) != plan.get("event_count")
    ):
        raise RuntimeError("Springer Pilot 004 plan is invalid")
    for event in plan["events"]:
        query = event.get("query")
        if (
            not isinstance(query, str)
            or not query
            or event.get("query_characters") != len(query)
            or event.get("query_sha256") != text_sha256(query)
            or event.get("diagnostic_only") is not True
            or event.get("do_not_merge") is not True
        ):
            raise RuntimeError(f"Invalid planned event {event.get('event_id')}")


def _date_group_fingerprint(evidence: Mapping[str, Any]) -> str:
    groups = [
        [item[0].isoformat(), item[1], item[2]] for item in evidence["group_signature"]
    ]
    return canonical_sha256(groups)


async def collect_pass(
    adapter: Any,
    page: Any,
    event: Mapping[str, Any],
    *,
    pass_number: int,
    date_bounds: Any,
    screenshot_paths: Any,
    screenshot_payloads: dict[str, Any],
) -> dict[str, Any]:
    query = event["query"]
    rows: list[dict[str, Any]] = []
    native_paths: list[str] = []
    seen: set[str] = set()
    page_reports: list[dict[str, Any]] = []
    source_total: int | None = None
    page_count: int | None = None
    page_number = 1
    while True:
        url = adapter.build_search_url(
            query,
            year_start=date_bounds.source_year_start,
            year_end=date_bounds.source_year_end,
            language=LANGUAGE,
            sort=SORT,
            page_number=page_number,
        )
        retries = 0
        while True:
            await adapter.navigate_to_search(page, url, 60.0)
            state = await adapter.wait_for_springer_page(
                page,
                query=query,
                include_records=True,
                year_start=date_bounds.source_year_start,
                year_end=date_bounds.source_year_end,
                language=LANGUAGE,
                sort=SORT,
                expected_page_number=page_number,
                timeout_seconds=60.0,
            )
            duplicate_ids = [
                source_id
                for source_id in state.record_ids
                if source_id.casefold() in seen
            ]
            if not duplicate_ids:
                break
            if retries >= adapter.MAX_PAGINATION_RETRIES:
                raise adapter.SpringerProtocolError(
                    "Springer repeated a card path across pages in the pilot collector"
                )
            retries += 1
            await asyncio.sleep(adapter.PAGINATION_RETRY_DELAY_SECONDS)

        if source_total is None:
            source_total = state.total
            page_count = state.page_count
        elif state.total != source_total or state.page_count != page_count:
            raise adapter.SpringerSnapshotChangedError(
                "Springer total or page count changed during a pilot pass"
            )
        if (
            pass_number == 1
            and page_number == 1
            and "results_page" not in screenshot_payloads
        ):
            screenshot_payloads[
                "results_page"
            ] = await adapter._capture_springer_full_page_screenshot_payload(
                page,
                screenshot_paths.results_page,
                page_kind="hydrated_first_results_page",
            )
        ids = list(state.record_ids)
        seen.update(source_id.casefold() for source_id in ids)
        native_paths.extend(ids)
        rows.extend(state.rows)
        page_reports.append(
            {
                "page": page_number,
                "source_total": state.total,
                "rendered_rows": len(ids),
                "pagination_retries": retries,
                "ordered_card_paths_sha256": sequence_sha256(ids),
            }
        )
        if state.zero_results or page_number >= state.page_count:
            break
        page_number += 1

    if source_total is None or page_count is None:
        raise adapter.SpringerProtocolError("Pilot pass did not observe a source page")
    if (
        len(native_paths) != source_total
        or len(rows) != source_total
        or len(seen) != source_total
        or len(page_reports) != page_count
        or page_count != max(1, math.ceil(source_total / PAGE_SIZE))
    ):
        raise adapter.SpringerProtocolError(
            "Pilot card ledger did not reconcile to source pagination"
        )
    evidence = adapter._springer_canonical_order_evidence(rows)
    canonical_rows = adapter.canonicalize_springer_rows(rows)
    canonical_paths = [row["canonicalPath"] for row in canonical_rows]
    if canonical_paths != list(evidence["ordered_paths"]):
        raise adapter.SpringerProtocolError(
            "Pilot canonical rows disagreed with adapter order evidence"
        )
    return {
        "pass_number": pass_number,
        "source_total": source_total,
        "page_count": page_count,
        "native_ordered_card_paths": native_paths,
        "native_ordered_card_paths_sha256": sequence_sha256(native_paths),
        "ordered_card_paths": canonical_paths,
        "ordered_card_paths_sha256": sequence_sha256(canonical_paths),
        "date_group_sha256": _date_group_fingerprint(evidence),
        "sort_key_sha256": evidence["sort_key_fingerprint"],
        "date_groups_by_identity": evidence["group_by_identity"],
        "canonical_rows": canonical_rows,
        "pages": page_reports,
    }


def card_date_disposition(adapter: Any, value: str) -> str:
    observed_date, precision = adapter.parse_springer_publication_date(value)
    if observed_date is None or precision not in {"day", "month", "year"}:
        return "unresolved"
    start = date.fromisoformat(DATE_START)
    end = date.fromisoformat(DATE_END)
    if observed_date < start:
        return "excluded_before_start"
    if observed_date > end:
        return "excluded_after_cutoff"
    return "included_day" if precision == "day" else f"included_{precision}_unresolved"


def public_records(adapter: Any, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for row in rows:
        published = adapter.clean_text(row.get("published"))
        records.append(
            {
                "source_id": adapter.clean_text(row.get("canonicalPath")),
                "title": adapter.remove_email_addresses(row.get("title")),
                "description": adapter.remove_email_addresses(row.get("description")),
                "source_publication_date": published,
                "source_publication_date_disposition": card_date_disposition(
                    adapter, published
                ),
                "content_type": adapter.clean_text(row.get("contentType")),
            }
        )
    return records


async def run_event_attempt(
    adapter: Any,
    playwright: Any,
    event: Mapping[str, Any],
    output: Path,
    *,
    adapter_path: Path,
    cdp_url: str,
) -> dict[str, Any]:
    started = now()
    screenshot_paths = adapter.validate_springer_screenshot_destinations(output)
    source_year_start = event.get("source_year_start")
    source_year_end = event.get("source_year_end")
    if source_year_start is None and source_year_end is None:
        event_start = date.fromisoformat(DATE_START)
        event_end = date.fromisoformat(DATE_END)
    elif (
        isinstance(source_year_start, int)
        and not isinstance(source_year_start, bool)
        and source_year_start == source_year_end
        and 2011 <= source_year_start <= 2026
    ):
        event_start = max(date.fromisoformat(DATE_START), date(source_year_start, 1, 1))
        event_end = min(date.fromisoformat(DATE_END), date(source_year_start, 12, 31))
    else:
        raise RuntimeError("Pilot event has invalid source-year controls")
    date_bounds = adapter.resolve_date_bounds(
        year_start=None,
        year_end=None,
        date_start=event_start,
        date_end=event_end,
    )
    if date_bounds is None:
        raise RuntimeError("Pilot exact date bounds were not created")
    screenshot_payloads: dict[str, Any] = {}
    lease = None
    try:
        lease = await adapter.open_springer_owned_page(
            playwright,
            cdp_url=cdp_url,
            headless=False,
            timeout_seconds=60.0,
            chrome_executable=None,
        )
        page = lease.page
        configuration = await adapter.configure_springer_advanced_search_for_screenshot(
            page,
            query=event["query"],
            date_bounds=date_bounds,
            sort=SORT,
            timeout_seconds=60.0,
        )
        screenshot_payloads[
            "search_page"
        ] = await adapter._capture_springer_full_page_screenshot_payload(
            page,
            screenshot_paths.search_page,
            page_kind="configured_advanced_search_page",
            configuration_evidence=configuration,
        )
        first = await collect_pass(
            adapter,
            page,
            event,
            pass_number=1,
            date_bounds=date_bounds,
            screenshot_paths=screenshot_paths,
            screenshot_payloads=screenshot_payloads,
        )
        second = await collect_pass(
            adapter,
            page,
            event,
            pass_number=2,
            date_bounds=date_bounds,
            screenshot_paths=screenshot_paths,
            screenshot_payloads=screenshot_payloads,
        )
    finally:
        await adapter.close_springer_owned_page(lease)

    if (
        first["source_total"] != second["source_total"]
        or set(path.casefold() for path in first["ordered_card_paths"])
        != set(path.casefold() for path in second["ordered_card_paths"])
        or first["ordered_card_paths"] != second["ordered_card_paths"]
        or first["date_groups_by_identity"] != second["date_groups_by_identity"]
        or first["date_group_sha256"] != second["date_group_sha256"]
    ):
        raise adapter.SpringerSnapshotChangedError(
            "Springer pilot passes did not reconcile after equal-date tie normalization"
        )
    if set(screenshot_payloads) != {"search_page", "results_page"}:
        raise adapter.SpringerProtocolError(
            "Springer pilot did not capture both mandatory screenshots"
        )
    records = public_records(adapter, first["canonical_rows"])
    ordered_ids = [record["source_id"] for record in records]
    raw_diagnostic_ids = [
        record["source_id"]
        for record in records
        if record["source_publication_date_disposition"]
        not in {"excluded_before_start", "excluded_after_cutoff"}
    ]
    screenshot_receipt = {
        "schema_version": adapter.SPRINGER_SCREENSHOT_SCHEMA,
        "automatic": True,
        "no_opt_out": True,
        "search_page": dict(screenshot_payloads["search_page"].evidence),
        "results_page": dict(screenshot_payloads["results_page"].evidence),
    }
    payload = {
        "schema_version": "springer-nature-link-pilot004-source-event/v1",
        "pilot": "004",
        "event_id": event["event_id"],
        "variant": event["variant"],
        "partition_id": event["partition_id"],
        "cell_id": event.get("cell_id", "direct"),
        "branch": event.get("branch", event["partition_id"]),
        "status": "success",
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
        "protocol_commit": PROTOCOL_COMMIT,
        "query": event["query"],
        "query_characters": event["query_characters"],
        "query_sha256": event["query_sha256"],
        "source_total": first["source_total"],
        "ordered_source_ids": ordered_ids,
        "ordered_source_ids_sha256": sequence_sha256(ordered_ids),
        "diagnostic_window_ordered_source_ids": raw_diagnostic_ids,
        "diagnostic_window_ordered_source_ids_sha256": sequence_sha256(
            raw_diagnostic_ids
        ),
        "records": records,
        "passes": [
            {
                key: value
                for key, value in item.items()
                if key
                not in {
                    "native_ordered_card_paths",
                    "ordered_card_paths",
                    "date_groups_by_identity",
                    "canonical_rows",
                }
            }
            for item in (first, second)
        ],
        "output_metadata": {
            "source": "Springer Nature Link",
            "source_url": "https://link.springer.com/search",
            "access_method": "rendered_source_search_ui",
            "field": "raw Keywords over title, abstract, and body text",
            "date_start": event_start.isoformat(),
            "date_end": event_end.isoformat(),
            "main_window_start": DATE_START,
            "main_window_end": DATE_END,
            "source_year_start": date_bounds.source_year_start,
            "source_year_end": date_bounds.source_year_end,
            "source_date_precision": "year",
            "language_filter": LANGUAGE,
            "sort": SORT,
            "sort_native_label": "Date published (old to new)",
            "page_size": PAGE_SIZE,
            "passes_completed": 2,
            "retrieval_complete": True,
            "source_total_reconciled": True,
            "proximity_operator": None,
            "pair_expansion": False,
            "content_type_filter": None,
            "access_filter": None,
            "controlled_vocabulary_supplement": None,
            "taxonomy_filter": None,
            "exact_day_detail_navigation": False,
            "exact_day_scope_note": (
                "Raw wildcard comparison uses every complete source-year card path. "
                "The diagnostic window removes only card dates proved outside the "
                "requested days and does not claim complete detail-date resolution."
            ),
            "screenshots": screenshot_receipt,
            "adapter": {
                "adapter_id": adapter.ADAPTER_ID,
                "adapter_version": adapter.ADAPTER_VERSION,
                "script_sha256": file_sha256(adapter_path),
            },
            "started_at": started,
            "completed_at": now(),
        },
    }
    adapter._publish_springer_screenshot_bundle(
        screenshot_payloads,
        screenshot_paths,
    )
    write_json_create_only(output, payload)
    return payload


def failure_payload(
    adapter: Any,
    event: Mapping[str, Any],
    attempt: int,
    error: BaseException,
) -> dict[str, Any]:
    return {
        "schema_version": "springer-nature-link-pilot004-failure/v1",
        "pilot": "004",
        "event_id": event["event_id"],
        "attempt": attempt,
        "status": "failure",
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
        "query_sha256": event["query_sha256"],
        "source_total": None,
        "source_ids": [],
        "error_type": type(error).__name__,
        "error": adapter.safe_error_message(error),
        "recorded_at": now(),
    }


def existing_event_is_valid(path: Path, event: Mapping[str, Any]) -> bool:
    try:
        payload = load_json(path)
        metadata = payload["output_metadata"]
        screenshots = metadata["screenshots"]
        return bool(
            payload.get("status") == "success"
            and payload.get("event_id") == event.get("event_id")
            and payload.get("query_sha256") == event.get("query_sha256")
            and metadata.get("retrieval_complete") is True
            and metadata.get("passes_completed") == 2
            and screenshots.get("automatic") is True
            and screenshots.get("no_opt_out") is True
            and all(
                path.with_name(screenshots[key]["path"]).is_file()
                for key in ("search_page", "results_page")
            )
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


async def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = load_json(args.event_plan)
    validate_plan(plan)
    adapter = load_adapter(args.adapter)
    from playwright.async_api import async_playwright

    started = now()
    completed: list[dict[str, Any]] = []
    async with async_playwright() as playwright:
        for event in plan["events"]:
            output = args.pilot_root / "searches" / event["output"]
            if (
                args.resume
                and output.exists()
                and existing_event_is_valid(output, event)
            ):
                completed.append(
                    {
                        "event_id": event["event_id"],
                        "output": event["output"],
                        "status": "existing_valid",
                        "sha256": file_sha256(output),
                    }
                )
                print(f"existing {event['event_id']}", flush=True)
                continue
            last_error: BaseException | None = None
            for attempt in range(1, args.max_attempts + 1):
                try:
                    print(f"running {event['event_id']} attempt {attempt}", flush=True)
                    payload = await run_event_attempt(
                        adapter,
                        playwright,
                        event,
                        output,
                        adapter_path=args.adapter,
                        cdp_url=args.cdp_url,
                    )
                    completed.append(
                        {
                            "event_id": event["event_id"],
                            "output": event["output"],
                            "status": "success",
                            "source_total": payload["source_total"],
                            "sha256": file_sha256(output),
                        }
                    )
                    print(
                        f"completed {event['event_id']} total={payload['source_total']}",
                        flush=True,
                    )
                    last_error = None
                    break
                except BaseException as error:
                    last_error = error
                    failure = (
                        args.pilot_root
                        / "searches"
                        / "failures"
                        / f"{event['event_id']}.attempt-{attempt:02d}.json"
                    )
                    write_json_create_only(
                        failure,
                        failure_payload(adapter, event, attempt, error),
                    )
                    print(
                        f"failed {event['event_id']} attempt {attempt}: "
                        f"{adapter.safe_error_message(error)}",
                        file=sys.stderr,
                        flush=True,
                    )
            if last_error is not None:
                raise RuntimeError(
                    f"Event {event['event_id']} failed after {args.max_attempts} attempts"
                ) from last_error

    return {
        "schema_version": "springer-nature-link-pilot004-run-receipt/v1",
        "pilot": "004",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": PROTOCOL_COMMIT,
        "adapter": {
            "path_basename": args.adapter.name,
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": file_sha256(args.adapter),
        },
        "event_plan": str(
            args.event_plan.resolve().relative_to(args.pilot_root.resolve())
        ),
        "event_plan_sha256": file_sha256(args.event_plan),
        "predeclared_event_count": len(plan["events"]),
        "completed_event_count": len(completed),
        "events": completed,
        "started_at": started,
        "completed_at": now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    parser.add_argument("--max-attempts", type=int, default=MAX_ATTEMPTS)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.max_attempts < 1 or args.max_attempts > MAX_ATTEMPTS:
        parser.error(f"--max-attempts must be between 1 and {MAX_ATTEMPTS}")
    if args.receipt.exists() or args.receipt.is_symlink():
        parser.error(f"Refusing to overwrite {args.receipt}")
    receipt = asyncio.run(run(args))
    write_json_create_only(args.receipt, receipt)
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
