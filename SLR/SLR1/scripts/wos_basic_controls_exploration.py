#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Bounded, aggregate-only Web of Science Basic Search exploration.

This X-only utility is a source-interface diagnostic, not a pilot or retrieval
adapter.  It attaches only to the shared loopback CfT endpoint, creates one
owned page, navigates once to the normal Core Collection Basic Search route,
waits passively for the current controls to hydrate, and permits at most one
native submit of the fixed quoted ``"CubeSat"`` sentinel.  It never opens a
record, exports, enumerates identifier values, retains source text, or writes
anything except its newly reserved aggregate receipt.

The default command is a create-only dry run.  ``--execute`` is opt-in and is
intended to be run only as an attached child of the shared browser-lease
wrapper.  No browser, profile, endpoint, or port override is supported.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import math
import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
BASIC_SEARCH_URL = "https://www.webofscience.com/wos/woscc/basic-search"
EXPECTED_HOST = "www.webofscience.com"
EXPECTED_PATH = "/wos/woscc/basic-search"
SENTINEL = '"CubeSat"'
SENTINEL_BYTES = SENTINEL.encode("utf-8")
SENTINEL_SHA256 = "1e53fd60a662c036456114dde907b19e3a607c9859dbe35e292c219105c741a1"
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_POLL_INTERVAL_SECONDS = 0.25
MAX_TIMEOUT_SECONDS = 60.0
MAX_POLL_INTERVAL_SECONDS = 0.25
if len(SENTINEL_BYTES) != 9 or hashlib.sha256(SENTINEL_BYTES).hexdigest() != SENTINEL_SHA256:
    raise RuntimeError("fixed sentinel invariant failed")


class InputValidationError(ValueError):
    """Raised before any browser lifecycle for invalid local input."""


@dataclass(frozen=True)
class ExplorationConfig:
    execute: bool
    cdp_url: str
    date_upper: str
    timeout_seconds: float
    poll_interval_seconds: float
    output_path: Path


@dataclass
class OutputReservation:
    path: Path
    descriptor: int


def _load_core_probe() -> Any:
    path = Path(__file__).with_name("wos_core_pilot_probe.py")
    spec = importlib.util.spec_from_file_location("wos_basic_controls_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("core probe unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _finite_positive(value: Any, option: str) -> float:
    if isinstance(value, bool):
        raise InputValidationError(f"{option} must be finite and positive")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(f"{option} must be finite and positive") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise InputValidationError(f"{option} must be finite and positive")
    return parsed


def _validate_date_upper(value: Any) -> str:
    if type(value) is not str:
        raise InputValidationError("--date-upper must be YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise InputValidationError("--date-upper must be a valid calendar date") from error
    if len(value) != 10 or value < "2011-01-01":
        raise InputValidationError("--date-upper must be YYYY-MM-DD on or after 2011-01-01")
    return value


def _validate_output_path(value: Any) -> Path:
    if type(value) is not str or not value.strip():
        raise InputValidationError("--output-path must be nonblank")
    candidate = Path(value).expanduser()
    if candidate.exists() or candidate.is_symlink():
        raise InputValidationError("--output-path must name a new path")
    path = candidate.resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise InputValidationError("--output-path must name a new path")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError("--output-path parent must be a directory")
    return path


def validate_config(config: Any) -> ExplorationConfig:
    if not isinstance(config, ExplorationConfig) or type(config.execute) is not bool:
        raise InputValidationError("runtime exploration configuration is invalid")
    if not isinstance(config.output_path, Path):
        raise InputValidationError("runtime exploration configuration is invalid")
    if type(config.cdp_url) is not str or config.cdp_url != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    timeout = _finite_positive(config.timeout_seconds, "--timeout-seconds")
    if timeout > MAX_TIMEOUT_SECONDS:
        raise InputValidationError("--timeout-seconds must not exceed 60")
    interval = _finite_positive(config.poll_interval_seconds, "--poll-interval-seconds")
    if interval > MAX_POLL_INTERVAL_SECONDS:
        raise InputValidationError("--poll-interval-seconds must not exceed 0.25")
    if interval > timeout:
        raise InputValidationError("--poll-interval-seconds cannot exceed --timeout-seconds")
    return ExplorationConfig(
        execute=config.execute,
        cdp_url=DEFAULT_CDP_URL,
        date_upper=_validate_date_upper(config.date_upper),
        timeout_seconds=timeout,
        poll_interval_seconds=interval,
        output_path=_validate_output_path(str(config.output_path)),
    )


def reserve_output_path(path: Path) -> OutputReservation:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return OutputReservation(path=path, descriptor=os.open(path, flags, 0o600))


def write_reserved_json(reservation: OutputReservation, payload: Mapping[str, Any]) -> None:
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("output reservation is no longer writable")
    reservation.descriptor = -1
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def new_receipt(config: ExplorationConfig) -> dict[str, Any]:
    return {
        "schema_version": "slr1-wos-basic-controls-exploration/v1",
        "mode": "x_exploration" if config.execute else "dry_run",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "endpoint_class": "explicit_loopback_cdp",
        "operation": "x_one_owned_page_basic_controls_one_submit_max",
        "navigation_attempt_count": 0,
        "records_retrieved": 0,
        "records_imported": 0,
        "query": {
            "byte_count": len(SENTINEL_BYTES),
            "sha256": SENTINEL_SHA256,
            "text_retained": False,
        },
        "retention_exclusions": [
            "query_text",
            "browser_url",
            "opaque_summary_route",
            "body_text",
            "html",
            "record",
            "record_text",
            "stable_identifier_value",
            "target_id",
            "cookie",
            "credential",
            "exception_string",
        ],
        "ownership": {
            "existing_context_count": None,
            "baseline_page_count": None,
            "owned_page_created": False,
            "owned_page_distinct_from_baseline": False,
            "owned_target_verified": False,
            "owned_page_close_attempted": False,
            "owned_page_closed": False,
            "owned_target_disappeared": False,
            "baseline_pages_preserved": None,
            "baseline_target_set_preserved": None,
        },
        "navigation": {
            "route_verified": False,
        },
        "controls": {
            "basic_hydration_polls": 0,
            "basic_hydration_timed_out": False,
            "core_collection": False,
            "all_editions_button": False,
            "all_current_editions_checked": False,
            "current_edition_count": None,
            "current_edition_checked_count": None,
            "topic_field": False,
            "publication_date": False,
            "date_start_readback": False,
            "date_end_readback": False,
            "english": False,
            "document_type_absent": False,
            "query_readback_sha256_match": False,
            "submit_button": False,
        },
        "submission": {
            "native_submit_count": 0,
            "source_operation_count": 0,
            "reissued": False,
            "reloaded": False,
            "one_submit_max": True,
        },
        "result": {
            "status": "not_run",
            "classification": "not_run",
            "observations_accepted": False,
            "source_reported_total": None,
            "summary_route_observed": False,
            "route_page": None,
            "current_page": None,
            "relevance": False,
            "page_size_50": False,
            "card_count": None,
            "expected_card_count": None,
            "lazy_cardinality": "not_observed",
            "stable_id_status": "not_observed",
            "export_control_present": None,
            "polls": 0,
            "scrolls": 0,
        },
    }


def _set_result(receipt: dict[str, Any], classification: str, accepted: bool = False) -> None:
    result = receipt["result"]
    result.update(
        {
            "status": "healthy" if accepted else "blocked",
            "classification": classification,
            "observations_accepted": accepted,
        }
    )
    if not accepted:
        result.update(
            {
                "source_reported_total": None,
                "route_page": None,
                "current_page": None,
                "card_count": None,
                "expected_card_count": None,
                "lazy_cardinality": "not_observed",
                "stable_id_status": "not_observed",
                "export_control_present": None,
            }
        )


def _apply_basic_controls(
    receipt: dict[str, Any], controls: Any, editions: Any, query_match: bool, start_match: bool, end_match: bool
) -> None:
    receipt["controls"].update(
        {
            "core_collection": controls.core_collection,
            "all_editions_button": controls.all_editions_button,
            "all_current_editions_checked": editions.all_current_editions_checked,
            "current_edition_count": editions.individual_count,
            "current_edition_checked_count": editions.individual_checked_count,
            "topic_field": controls.topic_field,
            "publication_date": controls.publication_date_button,
            "date_start_readback": start_match,
            "date_end_readback": end_match,
            "english": controls.language_english,
            "document_type_absent": controls.document_type_absent,
            "query_readback_sha256_match": query_match,
            "submit_button": controls.submit_button,
        }
    )


def _apply_result(receipt: dict[str, Any], state: Any, outcome: Any) -> None:
    result = receipt["result"]
    accepted = outcome.classification in {"zero_observed", "summary_observed"}
    result.update(
        {
            "source_reported_total": state.source_total if accepted else None,
            "summary_route_observed": state.summary_route,
            "route_page": state.route_page,
            "current_page": state.current_page,
            "relevance": state.relevance,
            "page_size_50": state.page_size_50,
            "card_count": state.card_count,
            "expected_card_count": state.expected_card_count,
            "lazy_cardinality": (
                "not_applicable_zero" if outcome.classification == "zero_observed"
                else "complete" if outcome.classification == "summary_observed"
                else "incomplete"
            ),
            "stable_id_status": state.stable_id_status,
            "export_control_present": state.export_control_present,
            "polls": outcome.polls,
            "scrolls": outcome.scrolls,
        }
    )


def _route_is_basic_search(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
    except Exception:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc == EXPECTED_HOST
        and parsed.path == EXPECTED_PATH
        and not parsed.query
        and not parsed.fragment
    )


async def _exact_input_value(page: Any, selector: str, expected: str) -> bool:
    try:
        locator = page.locator(selector)
        return bool(
            await locator.count() == 1
            and await locator.first.is_visible()
            and await locator.first.input_value() == expected
        )
    except Exception:
        return False


async def _execute(config: ExplorationConfig, receipt: dict[str, Any]) -> tuple[int, str]:
    core = _load_core_probe()
    from playwright.async_api import async_playwright

    core_config = core.ProbeConfig(
        execute=True,
        cdp_url=DEFAULT_CDP_URL,
        query=SENTINEL,
        query_file_name="wos_basic_controls_exploration_sentinel",
        query_sha256=SENTINEL_SHA256,
        date_upper=config.date_upper,
        timeout_seconds=config.timeout_seconds,
        poll_interval_seconds=config.poll_interval_seconds,
        receipt_path=Path("wos-basic-controls-exploration-receipt.json"),
    )
    browser = None
    context = None
    page = None
    baseline_pages: tuple[Any, ...] = ()
    baseline_targets: frozenset[str] | None = None
    owned_target: str | None = None
    owned_distinct = False
    target_verified = False
    classification = "browser_connection_failed"
    status = 1
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.connect_over_cdp(
                DEFAULT_CDP_URL,
                timeout=max(1, int(config.timeout_seconds * 1_000)),
            )
            contexts = tuple(browser.contexts)
            receipt["ownership"]["existing_context_count"] = len(contexts)
            if len(contexts) != 1:
                raise core.ProbeAbort("unexpected_browser_context_count")
            context = contexts[0]
            baseline_pages = tuple(context.pages)
            receipt["ownership"]["baseline_page_count"] = len(baseline_pages)
            baseline_targets = await core.active_target_ids(browser)
            if baseline_targets is None:
                raise core.ProbeAbort("baseline_target_inventory_unavailable")

            page = await context.new_page()
            receipt["ownership"]["owned_page_created"] = True
            owned_distinct = all(page is not item for item in baseline_pages)
            receipt["ownership"]["owned_page_distinct_from_baseline"] = owned_distinct
            if not owned_distinct:
                raise core.ProbeAbort("owned_page_not_distinct")
            owned_target = await core.target_id_for(context, page)
            after_create = await core.active_target_ids(browser)
            target_verified = bool(
                owned_target is not None
                and after_create is not None
                and owned_target not in baseline_targets
                and after_create == baseline_targets | {owned_target}
            )
            receipt["ownership"]["owned_target_verified"] = target_verified
            if not target_verified:
                raise core.ProbeAbort("owned_target_not_verified")

            receipt["navigation_attempt_count"] = 1
            response = await page.goto(
                BASIC_SEARCH_URL,
                wait_until="domcontentloaded",
                timeout=max(1, int(config.timeout_seconds * 1_000)),
            )
            route_verified = bool(
                isinstance(getattr(response, "status", None), int)
                and not isinstance(getattr(response, "status", None), bool)
                and 200 <= response.status < 400
                and _route_is_basic_search(page.url)
            )
            receipt["navigation"]["route_verified"] = route_verified
            if not route_verified:
                raise core.ProbeAbort("source_route_not_verified")

            hydration = await core.wait_for_basic_controls(
                page,
                timeout_seconds=config.timeout_seconds,
                poll_interval_seconds=config.poll_interval_seconds,
            )
            receipt["controls"].update(
                {
                    "basic_hydration_polls": hydration.polls,
                    "basic_hydration_timed_out": hydration.timed_out,
                }
            )
            if hydration.controls is None:
                raise core.ProbeAbort("basic_controls_not_ready")

            controls, editions = await core.prepare_basic_controls(page, core_config)
            query_match = False
            try:
                query = page.locator(
                    "input[data-ta='search-criteria-input'][name='search-main-box'][aria-label^='Search box 1 Topic']"
                )
                if await query.count() == 1 and await query.first.is_visible():
                    value = await query.first.input_value()
                    query_match = (
                        value.encode("utf-8") == SENTINEL_BYTES
                        and hashlib.sha256(value.encode("utf-8")).hexdigest() == SENTINEL_SHA256
                    )
            except Exception:
                query_match = False
            start_match = await _exact_input_value(
                page, "input[data-ta='search-timespan-start-input']", "2011-01-01"
            )
            end_match = await _exact_input_value(
                page, "input[data-ta='search-timespan-end-input']", config.date_upper
            )
            _apply_basic_controls(receipt, controls, editions, query_match, start_match, end_match)
            if not (controls.ready and query_match and start_match and end_match):
                raise core.ProbeAbort("basic_controls_not_ready")

            if receipt["submission"]["native_submit_count"] >= 1:
                raise core.ProbeAbort("native_submit_not_unique")
            await core.submit_one_query(page, core_config)
            receipt["submission"]["native_submit_count"] = 1
            receipt["submission"]["source_operation_count"] = 1

            outcome = await core.wait_for_result_and_hydrate(
                page,
                timeout_seconds=config.timeout_seconds,
                poll_interval_seconds=config.poll_interval_seconds,
            )
            if outcome.state is not None:
                _apply_result(receipt, outcome.state, outcome)
            if outcome.classification not in {"zero_observed", "summary_observed"}:
                safe_results = core.SAFE_ABORT_CLASSIFICATIONS | {"query_syntax_failed"}
                classification = (
                    outcome.classification
                    if outcome.classification in safe_results
                    else "owned_page_operation_failed"
                )
            else:
                _set_result(receipt, outcome.classification, accepted=True)
                status = 0
                classification = outcome.classification
        except core.ProbeAbort as error:
            classification = core.safe_abort_classification(error)
        except Exception:
            classification = "owned_page_operation_failed"
        finally:
            if (
                browser is not None
                and context is not None
                and page is not None
                and owned_distinct
                and target_verified
                and owned_target is not None
                and baseline_targets is not None
            ):
                try:
                    cleanup = await core.cleanup_owned_page(
                        browser,
                        context,
                        page,
                        owned_target,
                        baseline_pages,
                        baseline_targets,
                    )
                    receipt["ownership"].update(
                        {
                            "owned_page_close_attempted": cleanup.close_attempted,
                            "owned_page_closed": cleanup.page_closed,
                            "owned_target_disappeared": cleanup.target_disappeared,
                            "baseline_pages_preserved": cleanup.baseline_pages_preserved,
                            "baseline_target_set_preserved": cleanup.baseline_target_set_preserved,
                        }
                    )
                    if not cleanup.verified:
                        classification = "cleanup_verification_failed"
                        status = 1
                except Exception:
                    classification = "cleanup_verification_failed"
                    status = 1
            elif page is not None and owned_distinct:
                classification = "owned_page_cleanup_handoff_required"
                status = 1

    _set_result(receipt, classification, accepted=(status == 0))
    return status, classification


async def run_exploration(config: ExplorationConfig) -> tuple[int, dict[str, Any]]:
    try:
        config = validate_config(config)
    except Exception:
        fallback = config if isinstance(config, ExplorationConfig) else ExplorationConfig(
            execute=False,
            cdp_url=DEFAULT_CDP_URL,
            date_upper="2011-01-01",
            timeout_seconds=1.0,
            poll_interval_seconds=0.25,
            output_path=Path("invalid-exploration-receipt.json"),
        )
        receipt = new_receipt(fallback)
        _set_result(receipt, "invalid_runtime_config")
        return 1, receipt

    receipt = new_receipt(config)
    try:
        reservation = reserve_output_path(config.output_path)
    except OSError:
        _set_result(receipt, "output_reservation_failed")
        return 1, receipt

    status = 0
    classification = "dry_run"
    try:
        if config.execute:
            status, classification = await _execute(config, receipt)
        _set_result(receipt, classification, accepted=(status == 0 and config.execute))
        if not config.execute:
            receipt["result"]["status"] = "not_run"
    except Exception:
        status = 1
        classification = "owned_page_operation_failed"
        _set_result(receipt, classification)
    try:
        write_reserved_json(reservation, receipt)
    except Exception:
        return 2, receipt
    return status, receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="permit one live owned-page exploration")
    parser.add_argument("--date-upper", required=True, help="inclusive diagnostic date bound, YYYY-MM-DD")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-interval-seconds", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS)
    parser.add_argument("--output-path", required=True, help="new aggregate receipt path")
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help=argparse.SUPPRESS)
    return parser


def config_from_args(args: argparse.Namespace) -> ExplorationConfig:
    return ExplorationConfig(
        execute=args.execute,
        cdp_url=args.cdp_url,
        date_upper=args.date_upper,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
        output_path=Path(args.output_path).expanduser(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = validate_config(config_from_args(args))
    except InputValidationError as error:
        parser.error(str(error))
    status, receipt = asyncio.run(run_exploration(config))
    print(json.dumps({"status": status, "classification": receipt["result"]["classification"]}, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
