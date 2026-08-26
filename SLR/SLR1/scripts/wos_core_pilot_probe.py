#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Bounded, aggregate-only Web of Science Core Collection P01 probe.

This is a review-specific interface diagnostic, not a retrieval adapter.  The
normal execution path attaches to the shared CfT endpoint, creates one owned
page, verifies the Basic Search controls, submits one exact Topic query, and
classifies only a native zero or a summary-page aggregate.  It never opens a
record, exports, enumerates identifiers, or retains source text.

The command is dry-run unless ``--execute`` is supplied.  A live invocation is
intended to be wrapped by the shared browser lease controller; the probe itself
accepts only the controller's fixed loopback endpoint.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
BASIC_SEARCH_URL = "https://www.webofscience.com/wos/woscc/basic-search"
EXPECTED_HOST = "www.webofscience.com"
EXPECTED_PATH = "/wos/woscc/basic-search"
SUMMARY_PATH_PREFIX = "/wos/woscc/summary/"
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_POLL_INTERVAL_SECONDS = 0.25
CLEANUP_TIMEOUT_SECONDS = 5.0
CLEANUP_POLL_INTERVAL_SECONDS = 0.05
MAX_QUERY_CHARACTERS = 100_000
MAX_DATE_UPPER = 50


class InputValidationError(ValueError):
    """Raised before any browser lifecycle for invalid local input."""


class ProbeAbort(RuntimeError):
    """A fixed safe terminal classification without source text."""

    def __init__(self, classification: str) -> None:
        super().__init__(classification)
        self.classification = classification


SAFE_ABORT_CLASSIFICATIONS = frozenset(
    {
        "unexpected_browser_context_count",
        "baseline_target_inventory_unavailable",
        "owned_page_not_distinct",
        "owned_target_not_verified",
        "owned_page_cleanup_handoff_required",
        "source_route_not_verified",
        "source_access_blocked",
        "challenge_detected",
        "busy_detected",
        "basic_controls_not_ready",
        "all_editions_not_checked",
        "edition_picker_not_observed",
        "language_control_setup_failed",
        "date_control_setup_failed",
        "query_control_readback_failed",
        "native_submit_not_unique",
        "native_submit_interaction_failed",
        "post_submit_state_timeout",
        "native_zero_controls_unverified",
        "summary_controls_unverified",
        "summary_card_hydration_failed",
        "summary_page_identity_failed",
        "summary_total_unavailable",
        "cleanup_verification_failed",
    }
)


def safe_abort_classification(error: ProbeAbort) -> str:
    """Never allow an arbitrary exception/classification into a receipt."""
    if type(error.classification) is str and error.classification in SAFE_ABORT_CLASSIFICATIONS:
        return error.classification
    return "owned_page_operation_failed"


@dataclass(frozen=True)
class ProbeConfig:
    execute: bool
    cdp_url: str
    query: str
    query_file_name: str
    query_sha256: str
    date_upper: str
    timeout_seconds: float
    poll_interval_seconds: float
    receipt_path: Path


@dataclass
class OutputReservation:
    path: Path
    descriptor: int


@dataclass(frozen=True)
class EditionState:
    dialog_present: bool
    select_all_present: bool
    select_all_checked: bool
    individual_count: int
    individual_checked_count: int

    @property
    def all_current_editions_checked(self) -> bool:
        return bool(
            self.dialog_present
            and self.select_all_present
            and self.select_all_checked
            and self.individual_count > 0
            and self.individual_checked_count == self.individual_count
        )


@dataclass(frozen=True)
class BasicControlState:
    core_collection: bool
    all_editions_button: bool
    topic_field: bool
    publication_date_button: bool
    date_start_input: bool
    date_end_input: bool
    language_english: bool
    document_type_absent: bool
    query_input: bool
    submit_button: bool

    @property
    def ready(self) -> bool:
        return all(
            (
                self.core_collection,
                self.all_editions_button,
                self.topic_field,
                self.publication_date_button,
                self.date_start_input,
                self.date_end_input,
                self.language_english,
                self.document_type_absent,
                self.query_input,
                self.submit_button,
            )
        )


@dataclass(frozen=True)
class SubmittedControls:
    topic: bool
    english: bool
    publication_date: bool
    document_type_absent: bool

    @property
    def verified(self) -> bool:
        return bool(
            self.topic
            and self.english
            and self.publication_date
            and self.document_type_absent
        )


@dataclass(frozen=True)
class ResultState:
    classification: str
    submitted_controls: SubmittedControls
    zero_alert: bool
    summary_route: bool
    source_total: int | None
    route_page: int | None
    current_page: int | None
    relevance: bool
    page_size_50: bool
    card_count: int
    expected_card_count: int | None
    stable_id_status: str
    export_control_present: bool
    challenge: bool
    busy: bool
    access: bool
    syntax_error: bool

    @property
    def summary_aggregate_ready(self) -> bool:
        return bool(
            self.classification == "summary"
            and self.submitted_controls.verified
            and self.source_total is not None
            and self.source_total > 0
            and self.summary_route
            and self.route_page == self.current_page == 1
            and self.relevance
            and self.page_size_50
            and self.expected_card_count is not None
            and self.card_count == self.expected_card_count
        )


@dataclass(frozen=True)
class HydrationOutcome:
    state: ResultState | None
    classification: str
    polls: int
    scrolls: int
    timed_out: bool


@dataclass(frozen=True)
class CleanupReport:
    close_attempted: bool
    page_closed: bool
    target_disappeared: bool
    baseline_pages_preserved: bool
    baseline_target_set_preserved: bool

    @property
    def verified(self) -> bool:
        return bool(
            self.close_attempted
            and self.page_closed
            and self.target_disappeared
            and self.baseline_pages_preserved
            and self.baseline_target_set_preserved
        )


# These scripts inspect only fixed, aggregate DOM facts.  They intentionally
# derive booleans/counts in the page and never return labels, query text, URLs,
# card text, identifiers, or HTML.
BASIC_CONTROL_PROJECTION_SCRIPT = r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const oneVisible = selector => {
    const values = Array.from(document.querySelectorAll(selector)).filter(visible);
    return values.length === 1;
  };
  const aria = selector => Array.from(document.querySelectorAll(selector)).filter(visible)
    .map(element => String(element.getAttribute("aria-label") || ""));
  const languageEnglish = aria("[aria-label]").some(value =>
    /Language,\s*English/i.test(value)
  );
  const controls = aria("button[role='combobox'], [role='button'], button, [role='combobox']");
  const hasDocumentType = controls.some(value => /Document Type/i.test(value)) ||
    aria("[aria-label*='Document Type' i]").length > 0;
  return {
    core_collection: oneVisible("button[role='combobox'][aria-label^='Select database, Web of Science Core Collection']"),
    all_editions_button: oneVisible("button[role='combobox'][aria-label^='selectEdition, All']"),
    topic_field: oneVisible("button[role='combobox'][aria-label^='Select search field, Topic']"),
    publication_date_button: oneVisible("button[aria-label='Publication Date']"),
    date_start_input: oneVisible("input[data-ta='search-timespan-start-input']"),
    date_end_input: oneVisible("input[data-ta='search-timespan-end-input']"),
    language_english: languageEnglish,
    document_type_absent: !hasDocumentType,
    query_input: oneVisible("input[data-ta='search-criteria-input'][name='search-main-box'][aria-label^='Search box 1 Topic']"),
    submit_button: oneVisible("button[data-ta='run-search'][type='submit']")
  };
}
"""

EDITION_DIALOG_PROJECTION_SCRIPT = r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const dialogs = Array.from(document.querySelectorAll("[role='dialog'][aria-label='selectEdition']"))
    .filter(visible);
  const dialog = dialogs.length === 1 ? dialogs[0] : null;
  if (!dialog) return {
    dialog_present: false,
    select_all_present: false,
    select_all_checked: false,
    individual_count: 0,
    individual_checked_count: 0
  };
  const text = element => String(
    element.getAttribute("aria-label") || element.textContent || ""
  ).replace(/\s+/g, " ").trim();
  const all = Array.from(dialog.querySelectorAll("input[type='checkbox'], [role='checkbox']"))
    .filter(visible).filter(element => /Select All/i.test(text(element)));
  const boxes = Array.from(dialog.querySelectorAll("input[type='checkbox'], [role='checkbox']"))
    .filter(visible);
  const individuals = boxes.filter(element => !/Select All/i.test(text(element)));
  const checked = element => element.getAttribute("aria-checked") === "true" ||
    Boolean(element.checked);
  return {
    dialog_present: true,
    select_all_present: all.length === 1,
    select_all_checked: all.length === 1 && checked(all[0]),
    individual_count: individuals.length,
    individual_checked_count: individuals.filter(checked).length
  };
}
"""

POST_RESULT_PROJECTION_SCRIPT = r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const normalize = value => String(value || "").replace(/[\s\u2009\u202f]+/g, " ").trim();
  const visibleText = selector => Array.from(document.querySelectorAll(selector))
    .filter(visible).map(element => normalize(element.textContent)).join(" ");
  const alertText = visibleText("[role='alert'], .error, .error-message, .message-error");
  const challenge = Boolean(document.querySelector(
    "iframe[src*='captcha'], iframe[src*='challenge'], [id*='captcha' i], [class*='captcha' i]"
  )) || /verify you are human|unusual traffic|just a moment/i.test(normalize(document.title));
  const access = /^(?:access denied|forbidden|institutional access required)$/i.test(alertText);
  const busy = /^(?:service busy|server busy|please try again later|rate limit)/i.test(alertText);
  const syntaxError = /invalid query|query syntax|search error|unable to process/i.test(alertText);
  const zeroAlert = Array.from(document.querySelectorAll("form[data-ta='search-form'] [role='alert'][aria-atomic='true']"))
    .filter(visible).some(element => normalize(element.textContent) === "Your search found no results");

  let summaryRoute = false;
  let routePage = null;
  try {
    const current = new URL(window.location.href);
    const match = current.hostname === "www.webofscience.com" &&
      current.pathname.match(/^\/wos\/woscc\/summary\/[^/]+\/relevance\/(\d+)$/);
    if (match) {
      summaryRoute = true;
      routePage = Number(match[1]);
    }
  } catch (_) {}

  const friendly = visibleText("app-search-friendly-display");
  const submittedControls = {
    topic: /\bTopic\b/i.test(friendly),
    english: /\bEnglish\b/i.test(friendly),
    publication_date: /Publication Date/i.test(friendly),
    document_type_absent: !/Document Type/i.test(friendly)
  };
  const totalInputs = Array.from(document.querySelectorAll(
    "app-page-controls input[type='checkbox'][aria-label^='Select all records,']"
  )).filter(visible);
  let total = null;
  if (totalInputs.length === 1) {
    const label = String(totalInputs[0].getAttribute("aria-label") || "");
    const match = label.match(/\b0\s+of\s+([0-9][0-9,]*)\b/i);
    if (match) total = Number(match[1].replace(/,/g, ""));
  }
  const pageInputs = Array.from(document.querySelectorAll("input[aria-label^='Top Page Number ']")).filter(visible);
  const currentPage = pageInputs.length === 1 && /^\d+$/.test(String(pageInputs[0].value || ""))
    ? Number(pageInputs[0].value) : null;
  const relevance = Array.from(document.querySelectorAll("button[data-ta='selectSortOption']"))
    .filter(visible).filter(element =>
      String(element.getAttribute("aria-label") || "") === "Sort by Relevance"
    ).length === 1;
  const pageSize = Array.from(document.querySelectorAll("button[role='combobox']"))
    .filter(visible).some(element => /^Page size,\s*50$/i.test(String(element.getAttribute("aria-label") || "")));
  const cards = Array.from(document.querySelectorAll("app-record")).filter(visible);
  const cardCount = cards.length;
  const expected = summaryRoute && total !== null && total > 0 && routePage !== null
    ? Math.min(50, total - 50 * (routePage - 1)) : null;
  const ids = cards.map(card =>
    Boolean(String(card.getAttribute("data-wos-id") || card.getAttribute("docid") || "").trim())
  );
  const stableIdStatus = cardCount === 0 ? "none" :
    ids.every(Boolean) ? "uniform" : ids.some(Boolean) ? "partial" : "none";
  const exportControlPresent = Array.from(document.querySelectorAll(
    "button, [role='button'], [aria-label]"
  )).filter(visible).some(element => /\bExport\b/i.test(
    String(element.getAttribute("aria-label") || element.textContent || "")
  ));
  let classification = "unknown";
  if (zeroAlert) classification = "zero";
  else if (summaryRoute) classification = "summary";
  return {
    classification,
    submitted_controls: submittedControls,
    zero_alert: zeroAlert,
    summary_route: summaryRoute,
    source_total: total,
    route_page: routePage,
    current_page: currentPage,
    relevance,
    page_size_50: pageSize,
    card_count: cardCount,
    expected_card_count: expected,
    stable_id_status: stableIdStatus,
    export_control_present: exportControlPresent,
    challenge,
    busy,
    access,
    syntax_error: syntaxError
  };
}
"""

SCROLL_TO_BOTTOM_SCRIPT = r"""
() => {
  window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));
  return true;
}
"""


def compact(value: Any) -> str:
    return " ".join(str(value or "").split())


def _finite_positive(value: Any, option: str) -> float:
    if isinstance(value, bool):
        raise InputValidationError(f"{option} must be a finite positive number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(f"{option} must be a finite positive number") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise InputValidationError(f"{option} must be a finite positive number")
    return parsed


def validate_loopback_cdp_endpoint(value: Any) -> str:
    if type(value) is not str or value != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    return DEFAULT_CDP_URL


def validate_date_upper(value: Any) -> str:
    if type(value) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise InputValidationError("--date-upper must be YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise InputValidationError("--date-upper must be a valid calendar date") from error
    if value < "2011-01-01":
        raise InputValidationError("--date-upper must not precede 2011-01-01")
    return value


def validate_query(query: Any) -> str:
    if type(query) is not str or not compact(query) or len(query) > MAX_QUERY_CHARACTERS:
        raise InputValidationError("query must be nonblank and within its safe size limit")
    if "\x00" in query:
        raise InputValidationError("query contains an unsafe control character")
    return query


def validate_sha256(value: Any) -> str:
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise InputValidationError("query_sha256 must be a lowercase SHA-256 hash")
    return value


def validate_query_file(path_value: str | Path) -> tuple[str, str, str]:
    path = Path(path_value)
    if path.is_symlink() or not path.is_file():
        raise InputValidationError("--query-file must be a regular file")
    try:
        query = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise InputValidationError("--query-file is not readable UTF-8") from error
    query = query.rstrip("\n")
    validate_query(query)
    return query, path.name, hashlib.sha256(query.encode("utf-8")).hexdigest()


def validate_receipt_path(value: str | Path) -> Path:
    if not compact(value):
        raise InputValidationError("--receipt must be nonblank")
    path = Path(value).expanduser().resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise InputValidationError("--receipt must name a new path")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError("--receipt parent must be a directory")
    return path


def reserve_output_path(path: Path) -> OutputReservation:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return OutputReservation(path=path, descriptor=os.open(path, flags, 0o600))


def write_reserved_json(reservation: OutputReservation, payload: Mapping[str, Any]) -> None:
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("receipt reservation is no longer writable")
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


def validate_runtime_config(config: Any) -> ProbeConfig:
    if not isinstance(config, ProbeConfig) or type(config.execute) is not bool:
        raise InputValidationError("runtime probe configuration is invalid")
    if not isinstance(config.receipt_path, Path):
        raise InputValidationError("runtime probe configuration is invalid")
    query = validate_query(config.query)
    validate_sha256(config.query_sha256)
    if hashlib.sha256(query.encode("utf-8")).hexdigest() != config.query_sha256:
        raise InputValidationError("query hash does not match query")
    timeout = _finite_positive(config.timeout_seconds, "--timeout-seconds")
    interval = _finite_positive(config.poll_interval_seconds, "--poll-interval-seconds")
    if interval > timeout:
        raise InputValidationError("--poll-interval-seconds cannot exceed --timeout-seconds")
    return ProbeConfig(
        execute=config.execute,
        cdp_url=validate_loopback_cdp_endpoint(config.cdp_url),
        query=query,
        query_file_name=compact(config.query_file_name)[:256],
        query_sha256=config.query_sha256,
        date_upper=validate_date_upper(config.date_upper),
        timeout_seconds=timeout,
        poll_interval_seconds=interval,
        receipt_path=validate_receipt_path(config.receipt_path),
    )


def _nonnegative_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def controls_from_payload(payload: Any) -> BasicControlState:
    if not isinstance(payload, Mapping):
        raise ProbeAbort("basic_controls_not_ready")
    names = (
        "core_collection",
        "all_editions_button",
        "topic_field",
        "publication_date_button",
        "date_start_input",
        "date_end_input",
        "language_english",
        "document_type_absent",
        "query_input",
        "submit_button",
    )
    if any(type(payload.get(name)) is not bool for name in names):
        raise ProbeAbort("basic_controls_not_ready")
    return BasicControlState(**{name: payload[name] for name in names})


def edition_state_from_payload(payload: Any) -> EditionState:
    if not isinstance(payload, Mapping):
        raise ProbeAbort("edition_picker_not_observed")
    values = {
        "dialog_present": payload.get("dialog_present"),
        "select_all_present": payload.get("select_all_present"),
        "select_all_checked": payload.get("select_all_checked"),
    }
    if any(type(value) is not bool for value in values.values()):
        raise ProbeAbort("edition_picker_not_observed")
    count = _nonnegative_int(payload.get("individual_count"))
    checked = _nonnegative_int(payload.get("individual_checked_count"))
    if count is None or checked is None or checked > count:
        raise ProbeAbort("edition_picker_not_observed")
    return EditionState(
        dialog_present=values["dialog_present"],
        select_all_present=values["select_all_present"],
        select_all_checked=values["select_all_checked"],
        individual_count=count,
        individual_checked_count=checked,
    )


def submitted_controls_from_payload(payload: Any) -> SubmittedControls:
    if not isinstance(payload, Mapping):
        raise ProbeAbort("summary_controls_unverified")
    raw = payload.get("submitted_controls")
    if not isinstance(raw, Mapping):
        raise ProbeAbort("summary_controls_unverified")
    names = ("topic", "english", "publication_date", "document_type_absent")
    if any(type(raw.get(name)) is not bool for name in names):
        raise ProbeAbort("summary_controls_unverified")
    return SubmittedControls(**{name: raw[name] for name in names})


def _safe_result_total(value: Any) -> int | None:
    value = _nonnegative_int(value)
    return value if value is not None else None


def result_state_from_payload(payload: Any) -> ResultState:
    if not isinstance(payload, Mapping):
        raise ProbeAbort("post_submit_state_timeout")
    classification = payload.get("classification")
    if classification not in {"zero", "summary", "unknown"}:
        classification = "unknown"
    submitted = submitted_controls_from_payload(payload)
    bool_names = (
        "zero_alert",
        "summary_route",
        "relevance",
        "page_size_50",
        "export_control_present",
        "challenge",
        "busy",
        "access",
        "syntax_error",
    )
    if any(type(payload.get(name)) is not bool for name in bool_names):
        raise ProbeAbort("post_submit_state_timeout")
    route_page = _nonnegative_int(payload.get("route_page"))
    current_page = _nonnegative_int(payload.get("current_page"))
    total = _safe_result_total(payload.get("source_total"))
    card_count = _nonnegative_int(payload.get("card_count"))
    expected = _nonnegative_int(payload.get("expected_card_count"))
    stable_id_status = payload.get("stable_id_status")
    if stable_id_status not in {"uniform", "partial", "none"}:
        stable_id_status = "none"
    if card_count is None:
        raise ProbeAbort("post_submit_state_timeout")
    return ResultState(
        classification=classification,
        submitted_controls=submitted,
        zero_alert=payload["zero_alert"],
        summary_route=payload["summary_route"],
        source_total=total,
        route_page=route_page,
        current_page=current_page,
        relevance=payload["relevance"],
        page_size_50=payload["page_size_50"],
        card_count=card_count,
        expected_card_count=expected,
        stable_id_status=stable_id_status,
        export_control_present=payload["export_control_present"],
        challenge=payload["challenge"],
        busy=payload["busy"],
        access=payload["access"],
        syntax_error=payload["syntax_error"],
    )


def _result_classification(state: ResultState) -> str | None:
    if state.challenge:
        return "challenge_detected"
    if state.access:
        return "source_access_blocked"
    if state.busy:
        return "busy_detected"
    if state.syntax_error:
        return "query_syntax_failed"
    if state.classification == "zero" and state.zero_alert:
        if not state.submitted_controls.verified:
            return "native_zero_controls_unverified"
        return "zero_observed"
    if state.classification == "summary":
        if not (state.summary_route and state.route_page == state.current_page == 1):
            return "summary_page_identity_failed"
        if not state.submitted_controls.verified or not state.relevance or not state.page_size_50:
            return "summary_controls_unverified"
        if state.source_total is None or state.source_total < 1:
            return "summary_total_unavailable"
        return None
    return None


def _milliseconds(seconds: float) -> int:
    return max(1, int(seconds * 1_000))


async def _sleep_to_deadline(
    deadline: float,
    interval: float,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> bool:
    remaining = deadline - clock()
    if remaining <= 0:
        return False
    try:
        await asyncio.wait_for(sleeper(min(interval, remaining)), timeout=remaining)
    except asyncio.TimeoutError:
        return False
    return clock() < deadline


async def project_controls(page: Any) -> BasicControlState:
    try:
        payload = await page.evaluate(BASIC_CONTROL_PROJECTION_SCRIPT)
    except Exception as error:
        raise ProbeAbort("basic_controls_not_ready") from error
    return controls_from_payload(payload)


async def project_editions(page: Any) -> EditionState:
    try:
        payload = await page.evaluate(EDITION_DIALOG_PROJECTION_SCRIPT)
    except Exception as error:
        raise ProbeAbort("edition_picker_not_observed") from error
    return edition_state_from_payload(payload)


async def _wait_for_dialog(page: Any, *, timeout: float, interval: float) -> EditionState:
    deadline = asyncio.get_running_loop().time() + timeout
    while True:
        state = await project_editions(page)
        if state.dialog_present:
            return state
        if deadline - asyncio.get_running_loop().time() <= 0:
            raise ProbeAbort("edition_picker_not_observed")
        await asyncio.sleep(min(interval, max(0.0, deadline - asyncio.get_running_loop().time())))


async def _click_unique(locator: Any, classification: str, timeout: float) -> None:
    try:
        count = await locator.count()
        if count != 1 or not await locator.first.is_visible():
            raise ProbeAbort(classification)
        await locator.first.click(timeout=_milliseconds(timeout), no_wait_after=True)
    except ProbeAbort:
        raise
    except Exception as error:
        raise ProbeAbort(classification) from error


async def verify_all_editions(page: Any, timeout: float) -> EditionState:
    button = page.locator(
        "button[role='combobox'][aria-label^='selectEdition, All']"
    )
    await _click_unique(button, "edition_picker_not_observed", timeout)
    state = await _wait_for_dialog(page, timeout=timeout, interval=0.2)
    if not state.select_all_present:
        raise ProbeAbort("edition_picker_not_observed")
    if not state.all_current_editions_checked:
        try:
            checkbox = page.get_by_role("checkbox", name=re.compile(r"^Select All$", re.I))
            await _click_unique(checkbox, "all_editions_not_checked", timeout)
        except AttributeError as error:
            raise ProbeAbort("all_editions_not_checked") from error
        state = await _wait_for_dialog(page, timeout=timeout, interval=0.2)
    if not state.all_current_editions_checked:
        raise ProbeAbort("all_editions_not_checked")
    try:
        await page.keyboard.press("Escape")
    except Exception as error:
        raise ProbeAbort("edition_picker_not_observed") from error
    return state


async def _find_add_row_button(page: Any) -> Any | None:
    """Find one visible add-row control without returning its accessible name."""
    buttons = page.locator("button")
    try:
        count = await buttons.count()
    except Exception:
        return None
    matches = []
    for index in range(count):
        item = buttons.nth(index)
        try:
            if not await item.is_visible():
                continue
            label = compact(await item.get_attribute("aria-label"))
            title = compact(await item.get_attribute("title"))
            text = compact(await item.inner_text())
        except Exception:
            continue
        accessible = f"{label} {title} {text}".casefold()
        if "add" in accessible and any(word in accessible for word in ("search", "row", "field", "criteria")):
            matches.append(item)
    return matches[0] if len(matches) == 1 else None


async def ensure_english_language(page: Any, timeout: float) -> None:
    controls = await project_controls(page)
    if controls.language_english:
        return
    button = await _find_add_row_button(page)
    if button is None:
        raise ProbeAbort("language_control_setup_failed")
    try:
        await button.click(timeout=_milliseconds(timeout), no_wait_after=True)
        language = page.locator("[role='option'][aria-label='Language']")
        await _click_unique(language, "language_control_setup_failed", timeout)
        options = page.locator("[role='option']")
        count = await options.count()
        english = []
        for index in range(count):
            option = options.nth(index)
            if not await option.is_visible():
                continue
            label = compact(await option.get_attribute("aria-label"))
            text = compact(await option.inner_text())
            if label.casefold() == "english" or text.casefold() == "english":
                english.append(option)
        if len(english) != 1:
            raise ProbeAbort("language_control_setup_failed")
        await english[0].click(timeout=_milliseconds(timeout), no_wait_after=True)
    except ProbeAbort:
        raise
    except Exception as error:
        raise ProbeAbort("language_control_setup_failed") from error
    if not (await project_controls(page)).language_english:
        raise ProbeAbort("language_control_setup_failed")


async def ensure_date_range(page: Any, date_upper: str, timeout: float) -> None:
    try:
        start = page.locator("input[data-ta='search-timespan-start-input']")
        end = page.locator("input[data-ta='search-timespan-end-input']")
        if await start.count() != 1 or await end.count() != 1 or not await start.first.is_visible() or not await end.first.is_visible():
            button = page.locator("button[aria-label='Publication Date']")
            await _click_unique(button, "date_control_setup_failed", timeout)
        start = page.locator("input[data-ta='search-timespan-start-input']")
        end = page.locator("input[data-ta='search-timespan-end-input']")
        if await start.count() != 1 or await end.count() != 1:
            raise ProbeAbort("date_control_setup_failed")
        await start.first.fill("2011-01-01")
        await end.first.fill(date_upper)
        if await start.first.input_value() != "2011-01-01" or await end.first.input_value() != date_upper:
            raise ProbeAbort("date_control_setup_failed")
    except ProbeAbort:
        raise
    except Exception as error:
        raise ProbeAbort("date_control_setup_failed") from error


async def prepare_basic_controls(page: Any, config: ProbeConfig) -> tuple[BasicControlState, EditionState]:
    initial = await project_controls(page)
    if not initial.core_collection or not initial.topic_field or not initial.all_editions_button:
        raise ProbeAbort("basic_controls_not_ready")
    editions = await verify_all_editions(page, config.timeout_seconds)
    await ensure_english_language(page, config.timeout_seconds)
    await ensure_date_range(page, config.date_upper, config.timeout_seconds)
    try:
        query = page.locator(
            "input[data-ta='search-criteria-input'][name='search-main-box'][aria-label^='Search box 1 Topic']"
        )
        if await query.count() != 1 or not await query.first.is_visible():
            raise ProbeAbort("query_control_readback_failed")
        await query.first.fill(config.query)
        if await query.first.input_value() != config.query:
            raise ProbeAbort("query_control_readback_failed")
    except ProbeAbort:
        raise
    except Exception as error:
        raise ProbeAbort("query_control_readback_failed") from error
    final = await project_controls(page)
    if not final.ready:
        raise ProbeAbort("basic_controls_not_ready")
    return final, editions


async def submit_one_query(page: Any, config: ProbeConfig) -> None:
    submit = page.locator("button[data-ta='run-search'][type='submit']")
    await _click_unique(submit, "native_submit_not_unique", config.timeout_seconds)


async def project_result(page: Any) -> ResultState:
    try:
        payload = await page.evaluate(POST_RESULT_PROJECTION_SCRIPT)
    except Exception as error:
        raise ProbeAbort("post_submit_state_timeout") from error
    return result_state_from_payload(payload)


async def wait_for_result_and_hydrate(
    page: Any,
    *,
    timeout_seconds: float,
    poll_interval_seconds: float,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> HydrationOutcome:
    if clock is None:
        clock = asyncio.get_running_loop().time
    deadline = clock() + timeout_seconds
    polls = 0
    scrolls = 0
    stable_card_polls = 0
    last: ResultState | None = None
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return HydrationOutcome(None, "post_submit_state_timeout", polls, scrolls, True)
        try:
            state = await asyncio.wait_for(project_result(page), timeout=remaining)
        except asyncio.TimeoutError:
            return HydrationOutcome(None, "post_submit_state_timeout", polls, scrolls, True)
        polls += 1
        immediate = _result_classification(state)
        if immediate is not None:
            if immediate in {"challenge_detected", "source_access_blocked", "busy_detected", "query_syntax_failed"}:
                return HydrationOutcome(None, immediate, polls, scrolls, False)
            if immediate == "zero_observed":
                return HydrationOutcome(state, immediate, polls, scrolls, False)
            if immediate in {"summary_page_identity_failed", "summary_controls_unverified", "summary_total_unavailable"}:
                return HydrationOutcome(None, immediate, polls, scrolls, False)
        if state.classification == "summary":
            if state.summary_aggregate_ready:
                if last == state:
                    stable_card_polls += 1
                else:
                    stable_card_polls = 1
                last = state
                if stable_card_polls >= 2:
                    return HydrationOutcome(state, "summary_observed", polls, scrolls, False)
            else:
                stable_card_polls = 0
                last = state
                try:
                    await page.evaluate(SCROLL_TO_BOTTOM_SCRIPT)
                except Exception:
                    return HydrationOutcome(None, "summary_card_hydration_failed", polls, scrolls, False)
                scrolls += 1
        if clock() >= deadline:
            if state.classification == "summary":
                return HydrationOutcome(None, "summary_card_hydration_failed", polls, scrolls, True)
            return HydrationOutcome(None, "post_submit_state_timeout", polls, scrolls, True)
        if not await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper):
            if state.classification == "summary":
                return HydrationOutcome(None, "summary_card_hydration_failed", polls, scrolls, True)
            return HydrationOutcome(None, "post_submit_state_timeout", polls, scrolls, True)


async def target_id_for(context: Any, page: Any) -> str | None:
    session = None
    try:
        session = await context.new_cdp_session(page)
        payload = await session.send("Target.getTargetInfo")
        info = payload.get("targetInfo") if isinstance(payload, Mapping) else None
        target = info.get("targetId") if isinstance(info, Mapping) else None
        return target if type(target) is str and target else None
    except Exception:
        return None
    finally:
        if session is not None:
            try:
                await session.detach()
            except Exception:
                pass


async def active_target_ids(browser: Any) -> frozenset[str] | None:
    session = None
    try:
        session = await browser.new_browser_cdp_session()
        payload = await session.send("Target.getTargets")
        infos = payload.get("targetInfos") if isinstance(payload, Mapping) else None
        if not isinstance(infos, list):
            return None
        values = []
        for info in infos:
            if not isinstance(info, Mapping) or type(info.get("targetId")) is not str or not info["targetId"]:
                return None
            values.append(info["targetId"])
        if len(values) != len(set(values)):
            return None
        return frozenset(values)
    except Exception:
        return None
    finally:
        if session is not None:
            try:
                await session.detach()
            except Exception:
                pass


async def cleanup_owned_page(
    browser: Any,
    context: Any,
    page: Any,
    target_id: str,
    baseline_pages: tuple[Any, ...],
    baseline_targets: frozenset[str],
    *,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> CleanupReport:
    if clock is None:
        clock = asyncio.get_running_loop().time
    close_attempted = True
    page_closed = False
    try:
        await asyncio.wait_for(page.close(), timeout=CLEANUP_TIMEOUT_SECONDS)
        page_closed = bool(page.is_closed())
    except Exception:
        page_closed = False
    deadline = clock() + CLEANUP_TIMEOUT_SECONDS
    target_disappeared = False
    baseline_target_set_preserved = False
    while clock() < deadline:
        targets = await active_target_ids(browser)
        if targets is not None:
            target_disappeared = target_id not in targets
            baseline_target_set_preserved = targets == baseline_targets
            if target_disappeared and baseline_target_set_preserved:
                break
        await _sleep_to_deadline(deadline, CLEANUP_POLL_INTERVAL_SECONDS, clock, sleeper)
    try:
        current_pages = tuple(context.pages)
        baseline_pages_preserved = (
            current_pages == baseline_pages
            and all(not item.is_closed() for item in baseline_pages)
        )
    except Exception:
        baseline_pages_preserved = False
    return CleanupReport(
        close_attempted=close_attempted,
        page_closed=page_closed,
        target_disappeared=target_disappeared,
        baseline_pages_preserved=baseline_pages_preserved,
        baseline_target_set_preserved=baseline_target_set_preserved,
    )


def new_receipt(config: ProbeConfig) -> dict[str, Any]:
    return {
        "schema_version": "slr1-wos-core-pilot-probe/v1",
        "mode": "source_action" if config.execute else "dry_run",
        "endpoint_class": "explicit_loopback_cdp",
        "operation": "one_owned_page_one_basic_topic_diagnostic",
        "navigation_attempt_count": 0,
        "query": {
            "file_name": config.query_file_name,
            "sha256": config.query_sha256,
            "character_count": len(config.query),
            "text_retained": False,
        },
        "diagnostic_date_bound": {
            "start_inclusive": "2011-01-01",
            "end_inclusive": config.date_upper,
            "pilot_only": True,
            "common_cutoff_selected": False,
        },
        "retention_exclusions": [
            "query_text",
            "browser_url",
            "opaque_summary_route",
            "body_text",
            "html",
            "record",
            "stable_identifier_value",
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
        "controls": {
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
            "query_readback": False,
        },
        "submission": {
            "native_submit_observed": False,
            "source_operation_count": 0,
            "busy_retries": 0,
            "challenge_reissued": False,
            "pacing": "one submission; no busy retry; bounded passive state polling only",
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


def set_result(receipt: dict[str, Any], classification: str, *, accepted: bool = False) -> None:
    current = receipt["result"]
    current.update(
        {
            "status": "healthy" if accepted else "blocked",
            "classification": classification,
            "observations_accepted": accepted,
        }
    )
    if not accepted:
        current["source_reported_total"] = None


def apply_controls(receipt: dict[str, Any], controls: BasicControlState, editions: EditionState) -> None:
    receipt["controls"].update(
        {
            "core_collection": controls.core_collection,
            "all_editions_button": controls.all_editions_button,
            "all_current_editions_checked": editions.all_current_editions_checked,
            "current_edition_count": editions.individual_count,
            "current_edition_checked_count": editions.individual_checked_count,
            "topic_field": controls.topic_field,
            "publication_date": controls.publication_date_button,
            "english": controls.language_english,
            "document_type_absent": controls.document_type_absent,
            "query_readback": controls.query_input,
        }
    )


def apply_result(receipt: dict[str, Any], state: ResultState, outcome: HydrationOutcome) -> None:
    result = receipt["result"]
    result.update(
        {
            "source_reported_total": state.source_total if outcome.classification in {"zero_observed", "summary_observed"} else None,
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


def _safe_failure(receipt: dict[str, Any], classification: str) -> None:
    set_result(receipt, classification, accepted=False)


async def run_probe(
    config: ProbeConfig,
    *,
    playwright_factory: Callable[[], Any] | None = None,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> tuple[int, dict[str, Any]]:
    try:
        config = validate_runtime_config(config)
    except Exception:
        # A direct API caller cannot bypass the same validation as the CLI.
        fallback = config if isinstance(config, ProbeConfig) else ProbeConfig(
            execute=False,
            cdp_url=DEFAULT_CDP_URL,
            query="invalid",
            query_file_name="invalid",
            query_sha256=hashlib.sha256(b"invalid").hexdigest(),
            date_upper="2011-01-01",
            timeout_seconds=1.0,
            poll_interval_seconds=0.1,
            receipt_path=Path("invalid-receipt.json"),
        )
        receipt = new_receipt(fallback)
        _safe_failure(receipt, "invalid_runtime_config")
        return 1, receipt

    receipt = new_receipt(config)
    try:
        reservation = reserve_output_path(config.receipt_path)
    except OSError:
        _safe_failure(receipt, "output_reservation_failed")
        return 1, receipt

    browser = None
    context = None
    owned_page = None
    baseline_pages: tuple[Any, ...] = ()
    baseline_targets: frozenset[str] | None = None
    owned_target: str | None = None
    cleanup: CleanupReport | None = None
    status = 1
    try:
        if not config.execute:
            set_result(receipt, "dry_run", accepted=True)
            status = 0
        else:
            if clock is None:
                clock = asyncio.get_running_loop().time
            if playwright_factory is None:
                from playwright.async_api import async_playwright

                playwright_factory = async_playwright
            async with playwright_factory() as playwright:
                try:
                    browser = await playwright.chromium.connect_over_cdp(
                        config.cdp_url, timeout=_milliseconds(config.timeout_seconds)
                    )
                    contexts = tuple(browser.contexts)
                    receipt["ownership"]["existing_context_count"] = len(contexts)
                    if len(contexts) != 1:
                        raise ProbeAbort("unexpected_browser_context_count")
                    context = contexts[0]
                    baseline_pages = tuple(context.pages)
                    receipt["ownership"]["baseline_page_count"] = len(baseline_pages)
                    baseline_targets = await active_target_ids(browser)
                    if baseline_targets is None:
                        raise ProbeAbort("baseline_target_inventory_unavailable")
                    owned_page = await context.new_page()
                    receipt["ownership"]["owned_page_created"] = True
                    distinct = all(owned_page is not page for page in baseline_pages)
                    receipt["ownership"]["owned_page_distinct_from_baseline"] = distinct
                    if not distinct:
                        raise ProbeAbort("owned_page_not_distinct")
                    owned_target = await target_id_for(context, owned_page)
                    after_create = await active_target_ids(browser)
                    target_verified = bool(
                        owned_target is not None
                        and after_create is not None
                        and owned_target not in baseline_targets
                        and after_create == baseline_targets | {owned_target}
                    )
                    receipt["ownership"]["owned_target_verified"] = target_verified
                    if not target_verified:
                        raise ProbeAbort("owned_target_not_verified")

                    response = await owned_page.goto(
                        BASIC_SEARCH_URL,
                        wait_until="domcontentloaded",
                        timeout=_milliseconds(config.timeout_seconds),
                    )
                    response_status = getattr(response, "status", None)
                    if not isinstance(response_status, int) or not 200 <= response_status < 400:
                        raise ProbeAbort("source_route_not_verified")
                    try:
                        parsed = urlsplit(owned_page.url)
                        if not (
                            parsed.scheme == "https"
                            and parsed.netloc == EXPECTED_HOST
                            and parsed.path == EXPECTED_PATH
                            and not parsed.query
                            and not parsed.fragment
                        ):
                            raise ProbeAbort("source_route_not_verified")
                    except ProbeAbort:
                        raise
                    except Exception as error:
                        raise ProbeAbort("source_route_not_verified") from error

                    controls, editions = await prepare_basic_controls(owned_page, config)
                    apply_controls(receipt, controls, editions)
                    receipt["controls"]["date_start_readback"] = True
                    receipt["controls"]["date_end_readback"] = True
                    await submit_one_query(owned_page, config)
                    receipt["submission"]["native_submit_observed"] = True
                    receipt["submission"]["source_operation_count"] = 1
                    outcome = await wait_for_result_and_hydrate(
                        owned_page,
                        timeout_seconds=config.timeout_seconds,
                        poll_interval_seconds=config.poll_interval_seconds,
                        clock=clock,
                        sleeper=sleeper,
                    )
                    if outcome.state is not None:
                        apply_result(receipt, outcome.state, outcome)
                    if outcome.classification == "summary_observed" and outcome.state is not None:
                        set_result(receipt, outcome.classification, accepted=True)
                        status = 0
                    elif outcome.classification == "zero_observed" and outcome.state is not None:
                        set_result(receipt, outcome.classification, accepted=True)
                        status = 0
                    else:
                        _safe_failure(receipt, outcome.classification)
                except ProbeAbort as error:
                    _safe_failure(receipt, safe_abort_classification(error))
                except Exception:
                    _safe_failure(receipt, "owned_page_operation_failed")
                finally:
                    if (
                        owned_page is not None
                        and owned_target is not None
                        and baseline_targets is not None
                        and context is not None
                        and browser is not None
                        and receipt["ownership"]["owned_page_distinct_from_baseline"]
                        and receipt["ownership"]["owned_target_verified"]
                    ):
                        cleanup = await cleanup_owned_page(
                            browser,
                            context,
                            owned_page,
                            owned_target,
                            baseline_pages,
                            baseline_targets,
                            clock=clock,
                            sleeper=sleeper,
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
                            _safe_failure(receipt, "cleanup_verification_failed")
                            status = 1
                    elif owned_page is not None and receipt["ownership"]["owned_page_distinct_from_baseline"]:
                        # A distinct page whose target was not proven is not
                        # closed under an ambiguous ownership state.
                        _safe_failure(receipt, "owned_page_cleanup_handoff_required")
                        status = 1
    except Exception:
        _safe_failure(receipt, "browser_connection_failed")
        status = 1
    finally:
        try:
            write_reserved_json(reservation, receipt)
        except Exception:
            status = 1
    return status, receipt


def parse_args(argv: list[str] | None = None) -> ProbeConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="perform the one opt-in browser diagnostic")
    parser.add_argument("--query-file", required=True, help="exact UTF-8 Topic query file inside the source packet")
    parser.add_argument("--date-upper", required=True, help="pilot-only inclusive upper date bound, YYYY-MM-DD")
    parser.add_argument("--receipt", required=True, help="new per-attempt aggregate receipt path")
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help=argparse.SUPPRESS)
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-interval-seconds", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS)
    args = parser.parse_args(argv)
    try:
        query, name, digest = validate_query_file(args.query_file)
        return validate_runtime_config(
            ProbeConfig(
                execute=args.execute,
                cdp_url=args.cdp_url,
                query=query,
                query_file_name=name,
                query_sha256=digest,
                date_upper=args.date_upper,
                timeout_seconds=args.timeout_seconds,
                poll_interval_seconds=args.poll_interval_seconds,
                receipt_path=validate_receipt_path(args.receipt),
            )
        )
    except InputValidationError as error:
        parser.error(str(error))
        raise AssertionError("argparse.error exits")


def main(argv: list[str] | None = None) -> int:
    try:
        config = parse_args(argv)
    except SystemExit:
        raise
    status, receipt = asyncio.run(run_probe(config))
    # The receipt is the machine-readable result; stdout contains no source
    # query or browser detail.
    print(json.dumps({"status": status, "classification": receipt["result"]["classification"]}, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
