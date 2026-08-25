#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""Diagnose the rendered IEEE Xplore Language facet on one owned page.

This is a review-specific, diagnostic-only companion to the IEEE Xplore
adapter.  It attaches to the controller's existing loopback Chrome, creates
one page, applies only the already-authorized year and content controls, and
returns a value-free structural inventory of the rendered Language facet.  It
does not select English, read records, screen, import, download, or use a
REST/API route.

The surrounding live phase must hold the shared browser lease.  The probe
itself intentionally has no fresh-browser, profile, or alternate-port mode.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import math
import os
import sys
from collections.abc import Awaitable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
SOURCE_HOST = "ieeexplore.ieee.org"
SEARCH_PATH = "/search/searchresult.jsp"
DEFAULT_TIMEOUT_SECONDS = 45.0
DEFAULT_POLL_INTERVAL_SECONDS = 0.2
MAX_QUERY_CHARACTERS = 50_000

# The adapter remains the owner of the normal IEEE search route, query echo,
# year application, content application, and owned-page cleanup contracts.
DEFAULT_ADAPTER_PATH = (
    Path.home()
    / "agent-tools"
    / "academic-research"
    / "skills"
    / "academic-search"
    / "scripts"
    / "search_ieee_xplore.py"
)
_ADAPTER: Any | None = None


class InputValidationError(ValueError):
    """Raised before Playwright or source activity for invalid input."""


class ProbeFailure(RuntimeError):
    """A fixed, safe diagnostic classification."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ProbeConfig:
    """Validated runtime configuration; query and paths are never persisted."""

    execute: bool
    query: str
    year_start: int
    year_end: int
    content_types: tuple[str, ...]
    cdp_url: str
    timeout_seconds: float
    poll_interval_seconds: float
    output_path: Path


@dataclass(frozen=True)
class LanguageInventory:
    """Allowlisted counts and booleans from the rendered Language controls."""

    ready: bool
    expected_route: bool
    challenge_detected: bool
    access_detected: bool
    login_detected: bool
    source_error_detected: bool
    busy_detected: bool
    language_facet_count: int
    language_option_count: int
    english_option_count: int
    apply_control_count: int
    selected_option_count: int


@dataclass(frozen=True)
class ProjectionOutcome:
    """Bounded passive projection result."""

    inventory: LanguageInventory | None
    attempts: int
    failure_code: str | None
    timed_out: bool


@dataclass
class OutputReservation:
    """A create-only output inode held through the diagnostic."""

    path: Path
    descriptor: int


LANGUAGE_CONTROL_STATE_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/[\s\u00a0]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const descriptor = element => [
    element && element.id,
    element && element.getAttribute("aria-label"),
    element && element.getAttribute("data-facet"),
    element && element.getAttribute("data-testid"),
    element && element.className
  ].map(value => String(value || "")).join(" ");
  const bodyText = normalize(document.body && document.body.innerText).slice(0, 12000);
  const title = normalize(document.title);
  const parsed = new URL(window.location.href);
  const sourceRoot = document.querySelector("xpl-search-results");
  const header = Array.from(document.querySelectorAll("h1.Dashboard-header")).filter(visible);
  const challenge = Boolean(document.querySelector(
    "#challenge-form, [id*='challenge' i], iframe[src*='challenge' i], [class*='captcha' i]"
  )) || /unusual traffic detected|error\s*418|captcha|verify you are human|just a moment/i.test(
    `${title} ${bodyText}`
  );
  const login = Boolean(document.querySelector("input[type='password']")) ||
    /\/(?:login|signin)(?:\/|$)/i.test(parsed.pathname) ||
    /sign in|log in|institutional access/i.test(`${title} ${bodyText}`);
  const access = /access denied|unable to access|not authorized/i.test(`${title} ${bodyText}`);
  const sourceError = /unable to load page|service unavailable|unexpected error|system error/i.test(
    `${title} ${bodyText}`
  );
  const busy = /too many requests|rate limit|temporarily busy|please wait|try again later/i.test(
    `${title} ${bodyText}`
  );

  // Inspect labels and attributes only to derive fixed counts.  No label,
  // option, query, URL, body, or HTML text is returned to Python.
  const candidateElements = Array.from(document.querySelectorAll(
    "xpl-facet-language, xpl-facet-refinement, [data-facet], [id*='language' i], [aria-label*='language' i], [class*='language' i]"
  )).filter(visible).filter(element => /language/i.test(descriptor(element)) ||
    /\blanguages?\b/i.test(normalize(element.innerText || element.textContent)));
  const languageRoots = candidateElements.filter(element =>
    !candidateElements.some(other => other !== element && other.contains(element))
  );
  const labels = Array.from(document.querySelectorAll("label, option, [role='option']"));
  const labelTextFor = input => {
    const own = [];
    if (input.id) {
      labels.forEach(label => {
        if (label.htmlFor === input.id) own.push(label.innerText || label.textContent || "");
      });
    }
    const parent = input.closest("label");
    if (parent) own.push(parent.innerText || parent.textContent || "");
    return normalize(own.join(" "));
  };
  const inputs = Array.from(document.querySelectorAll("input[type='checkbox'], input[type='radio']"))
    .filter(visible)
    .filter(input => {
      const insideRoot = languageRoots.some(root => root.contains(input));
      const descriptorText = `${descriptor(input)} ${labelTextFor(input)}`;
      return insideRoot || /\blanguages?\b/i.test(descriptorText);
    });
  const englishInputs = inputs.filter(input => {
    const text = `${labelTextFor(input)} ${String(input.value || "")}`;
    return /(^|\s)english(\s|$)/i.test(normalize(text));
  });
  const applyControls = languageRoots.flatMap(root =>
    Array.from(root.querySelectorAll("button, input[type='button'], input[type='submit']"))
      .filter(visible)
      .filter(button => /^apply$/i.test(normalize(button.innerText || button.value)))
  );

  return {
    ready: Boolean(sourceRoot && header.length === 1),
    expected_route: parsed.protocol === "https:" &&
      parsed.hostname.toLowerCase() === "ieeexplore.ieee.org" &&
      parsed.pathname === "/search/searchresult.jsp",
    challenge_detected: challenge,
    access_detected: access,
    login_detected: login,
    source_error_detected: sourceError,
    busy_detected: busy,
    language: {
      language_facet_count: new Set(languageRoots).size,
      language_option_count: inputs.length,
      english_option_count: englishInputs.length,
      apply_control_count: new Set(applyControls).size,
      selected_option_count: inputs.filter(input => Boolean(input.checked)).length
    }
  };
}
"""


def _load_adapter() -> Any:
    """Load the trusted local adapter only when an execute run is requested."""

    global _ADAPTER
    if _ADAPTER is not None:
        return _ADAPTER
    raw_path = os.environ.get("IEEE_XPLORE_ADAPTER_PATH")
    path = Path(raw_path).expanduser() if raw_path else DEFAULT_ADAPTER_PATH
    spec = importlib.util.spec_from_file_location(
        "ieee_xplore_language_probe_adapter", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("adapter unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _ADAPTER = module
    return module


def validate_loopback_cdp_url(value: Any) -> str:
    """Require the one controller-shared CfT endpoint, without aliases."""

    if type(value) is not str or value != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    return DEFAULT_CDP_URL


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


def validate_year_window(year_start: Any, year_end: Any) -> tuple[int, int]:
    if isinstance(year_start, bool) or isinstance(year_end, bool):
        raise InputValidationError("year bounds must be integers")
    if not isinstance(year_start, int) or not isinstance(year_end, int):
        raise InputValidationError("year bounds must be integers")
    if not (1800 <= year_start <= 2200 and 1800 <= year_end <= 2200):
        raise InputValidationError("year bounds must be between 1800 and 2200")
    if year_start > year_end:
        raise InputValidationError("year-start cannot exceed year-end")
    return year_start, year_end


def validate_query(value: Any) -> str:
    if type(value) is not str:
        raise InputValidationError("--query must be text")
    query = value.strip()
    if not query or not query.replace("*", "").strip():
        raise InputValidationError("--query cannot be empty or wildcard-only")
    if len(query) > MAX_QUERY_CHARACTERS:
        raise InputValidationError("--query is too long")
    return query


def validate_content_types(values: Any) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)) or not values:
        raise InputValidationError("at least one --content-type is required")
    output: list[str] = []
    for value in values:
        if type(value) is not str or not value.strip():
            raise InputValidationError("--content-type values must be nonblank text")
        cleaned = value.strip()
        if cleaned not in output:
            output.append(cleaned)
    return tuple(output)


def validate_output_path(value: Any) -> Path:
    """Validate a prospective create-only output destination."""

    if type(value) is not str or not value.strip():
        raise InputValidationError("--output-path must be nonblank")
    candidate = Path(value).expanduser()
    path = candidate.resolve(strict=False)
    if path.exists():
        raise InputValidationError("--output-path must not already exist")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError("--output-path parent must be a directory")
    return path


def validate_config(config: Any) -> ProbeConfig:
    if not isinstance(config, ProbeConfig) or type(config.execute) is not bool:
        raise InputValidationError("invalid probe configuration")
    query = validate_query(config.query)
    year_start, year_end = validate_year_window(config.year_start, config.year_end)
    content_types = validate_content_types(config.content_types)
    cdp_url = validate_loopback_cdp_url(config.cdp_url)
    timeout = _finite_positive(config.timeout_seconds, "--timeout")
    interval = _finite_positive(config.poll_interval_seconds, "--poll-interval")
    if interval > timeout:
        raise InputValidationError("--poll-interval cannot exceed --timeout")
    if not isinstance(config.output_path, Path):
        raise InputValidationError("output path must be a Path")
    output_path = validate_output_path(str(config.output_path))
    return ProbeConfig(
        execute=config.execute,
        query=query,
        year_start=year_start,
        year_end=year_end,
        content_types=content_types,
        cdp_url=cdp_url,
        timeout_seconds=timeout,
        poll_interval_seconds=interval,
        output_path=output_path,
    )


def _count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProbeFailure("malformed_language_projection")
    return value


def _bool(value: Any) -> bool:
    if type(value) is not bool:
        raise ProbeFailure("malformed_language_projection")
    return value


def projection_from_payload(payload: Any) -> LanguageInventory:
    """Validate the fixed projection; source strings never cross this boundary."""

    if not isinstance(payload, Mapping):
        raise ProbeFailure("malformed_language_projection")
    language = payload.get("language")
    if not isinstance(language, Mapping):
        raise ProbeFailure("malformed_language_projection")
    return LanguageInventory(
        ready=_bool(payload.get("ready")),
        expected_route=_bool(payload.get("expected_route")),
        challenge_detected=_bool(payload.get("challenge_detected")),
        access_detected=_bool(payload.get("access_detected")),
        login_detected=_bool(payload.get("login_detected")),
        source_error_detected=_bool(payload.get("source_error_detected")),
        busy_detected=_bool(payload.get("busy_detected")),
        language_facet_count=_count(language.get("language_facet_count")),
        language_option_count=_count(language.get("language_option_count")),
        english_option_count=_count(language.get("english_option_count")),
        apply_control_count=_count(language.get("apply_control_count")),
        selected_option_count=_count(language.get("selected_option_count")),
    )


def new_receipt(execute: bool) -> dict[str, Any]:
    """Build a rights-safe receipt with null totals until a stage succeeds."""

    stage = lambda: {
        "status": "not_attempted",
        "query_echo_exact": False,
        "source_reported_total": None,
        "total_is_exact": False,
    }
    return {
        "schema_version": "slr1-ieee-language-control-probe/v1",
        "mode": "source_action" if execute else "dry_run",
        "operation": "one_owned_page_language_control_inventory",
        "endpoint_class": "shared_loopback_cdp_127_0_0_1_9222",
        "navigation_attempt_count": 0,
        "records_retrieved": 0,
        "records_imported": 0,
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "retention_exclusions": [
            "query_text",
            "query_echo_text",
            "raw_url",
            "body_text",
            "html",
            "source_records",
            "target_id",
            "cookie",
            "credential",
            "exception_string",
        ],
        "ownership": {
            "owned_page_created": False,
            "owned_page_distinct": False,
            "cleanup_state": "not_attempted",
            "cleanup_verified": None,
        },
        "controls": {
            "initial_query": stage(),
            "year_control": stage(),
            "content_type_control": stage(),
        },
        "language": {
            "status": "not_observed",
            "language_facet_count": None,
            "language_option_count": None,
            "english_option_count": None,
            "apply_control_count": None,
            "selected_option_count": None,
            "language_selection_attempted": False,
            "english_limit_applied": False,
            "challenge_detected": False,
            "access_detected": False,
            "login_detected": False,
            "source_error_detected": False,
            "busy_detected": False,
        },
        "source_reported_total": None,
        "source_total_status": "null",
        "result": {
            "status": "not_run",
            "classification": "not_run",
            "healthy": False,
            "observations_accepted": False,
        },
    }


def reserve_output_path(path: Path) -> OutputReservation:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    return OutputReservation(path=path, descriptor=os.open(path, flags, 0o600))


def write_reserved_json(reservation: OutputReservation, payload: Mapping[str, Any]) -> None:
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("output reservation is closed")
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


def _record_search_stage(receipt: dict[str, Any], name: str, state: Any) -> None:
    stage = receipt["controls"][name]
    total = getattr(state, "total", None)
    zero = getattr(state, "zero", False)
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ProbeFailure("unreconciled_source_total")
    stage.update(
        {
            "status": "native_zero" if zero else "success",
            "query_echo_exact": True,
            "source_reported_total": total,
            "total_is_exact": True,
        }
    )


def _record_language_projection(
    receipt: dict[str, Any], inventory: LanguageInventory
) -> None:
    language = receipt["language"]
    language.update(
        {
            "status": "observed" if inventory.ready else "not_ready",
            "language_facet_count": inventory.language_facet_count,
            "language_option_count": inventory.language_option_count,
            "english_option_count": inventory.english_option_count,
            "apply_control_count": inventory.apply_control_count,
            "selected_option_count": inventory.selected_option_count,
            "challenge_detected": inventory.challenge_detected,
            "access_detected": inventory.access_detected,
            "login_detected": inventory.login_detected,
            "source_error_detected": inventory.source_error_detected,
            "busy_detected": inventory.busy_detected,
        }
    )


def classify_inventory(inventory: LanguageInventory) -> tuple[str, bool]:
    """Fail closed without treating absent controls or failures as zero."""

    if inventory.challenge_detected:
        return "challenge_detected", False
    if inventory.login_detected:
        return "login_detected", False
    if inventory.access_detected:
        return "access_detected", False
    if inventory.busy_detected:
        return "busy_detected", False
    if inventory.source_error_detected:
        return "source_error_detected", False
    if not inventory.expected_route:
        return "unexpected_source_route", False
    if not inventory.ready:
        return "rendered_search_not_ready", False
    if inventory.language_facet_count == 0:
        return "language_facet_not_present", False
    if inventory.language_facet_count != 1:
        return "language_facet_ambiguous", False
    if inventory.language_option_count == 0:
        return "language_options_not_present", False
    if inventory.english_option_count != 1:
        return "english_option_not_verified", False
    if inventory.apply_control_count > 1:
        return "language_apply_control_ambiguous", False
    if inventory.selected_option_count != 0:
        return "inherited_language_selection_detected", False
    return "language_control_inventory_healthy", True


def _transient_projection_error(error: BaseException) -> bool:
    """Classify only context replacement/navigation races; retain no text."""

    signal = f"{type(error).__name__} {error}".casefold()
    return any(
        marker in signal
        for marker in (
            "execution context was destroyed",
            "cannot find context",
            "frame was detached",
            "navigation is in progress",
            "navigating",
        )
    )


async def wait_for_language_inventory(
    page: Any,
    *,
    timeout_seconds: float,
    poll_interval_seconds: float,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> ProjectionOutcome:
    """Passively poll one owned page; never click or reissue a source action."""

    if clock is None:
        clock = asyncio.get_running_loop().time
    deadline = clock() + timeout_seconds
    attempts = 0
    last_failure: str | None = None
    while True:
        attempts += 1
        try:
            payload = await page.evaluate(LANGUAGE_CONTROL_STATE_SCRIPT)
            inventory = projection_from_payload(payload)
        except ProbeFailure as error:
            return ProjectionOutcome(None, attempts, error.code, False)
        except Exception as error:  # noqa: BLE001 - fixed safe classification only
            if _transient_projection_error(error):
                last_failure = "execution_context_replaced"
            else:
                return ProjectionOutcome(None, attempts, "projection_failed", False)
        else:
            if (
                inventory.challenge_detected
                or inventory.access_detected
                or inventory.login_detected
                or inventory.source_error_detected
                or inventory.busy_detected
                or inventory.ready
            ):
                return ProjectionOutcome(inventory, attempts, None, False)
            last_failure = "rendered_search_not_ready"
        if clock() >= deadline:
            return ProjectionOutcome(None, attempts, last_failure or "projection_timeout", True)
        await sleeper(min(poll_interval_seconds, max(0.0, deadline - clock())))


def _classify_exception(error: BaseException) -> str:
    if isinstance(error, ProbeFailure):
        return error.code
    if isinstance(error, asyncio.TimeoutError):
        return "timeout"
    name = type(error).__name__
    if name in {"IEEEAccessError"}:
        return "access_detected"
    if name in {"IEEEYearControlError"}:
        return "year_control_failed"
    if name in {"IEEEProtocolError"}:
        return "protocol_failure"
    if name in {"IEEERequestError", "IEEEExecutionContextReplacementError"}:
        return "source_request_failed"
    if name in {"IEEEBrowserError"}:
        return "browser_failure"
    if isinstance(error, ImportError):
        return "playwright_unavailable"
    return "browser_or_adapter_failure"


def _safe_adapter_receipt(adapter: Any, value: Any) -> dict[str, Any] | None:
    projector = getattr(adapter, "_safe_ieee_observation_receipt", None)
    if not callable(projector):
        return None
    try:
        projected = projector(value)
    except Exception:
        return None
    return projected if isinstance(projected, dict) else None


async def _execute_probe(
    config: ProbeConfig,
    receipt: dict[str, Any],
    *,
    adapter: Any,
    playwright_factory: Callable[[], Any] | None,
) -> str:
    if playwright_factory is None:
        from playwright.async_api import async_playwright

        playwright_factory = async_playwright

    adapter_receipt = (
        adapter._new_ieee_observation_receipt()
        if callable(getattr(adapter, "_new_ieee_observation_receipt", None))
        else None
    )
    cleanup_context = adapter._LeaseCleanup(adapter_receipt)
    try:
        async with playwright_factory() as playwright, cleanup_context as cleanup:
            lease, _authorization, _mode = await adapter.open_ieee_owned_page(
                playwright,
                cdp_url=config.cdp_url,
                target_id=None,
                headless=False,
                timeout_seconds=config.timeout_seconds,
                chrome_executable=None,
            )
            cleanup.lease = lease
            receipt["ownership"].update(
                {"owned_page_created": True, "owned_page_distinct": True}
            )
            page = lease.page
            receipt["navigation_attempt_count"] = 1

            await adapter.navigate(
                page,
                adapter.build_search_url(config.query),
                config.timeout_seconds,
                target="search",
            )
            state = await adapter.wait_for_search_page(
                page,
                query=config.query,
                year_range=None,
                refinements=(),
                expected_page_number=1,
                require_relevance=False,
                timeout_seconds=config.timeout_seconds,
                receipt=adapter_receipt,
                receipt_phase="initial_form",
            )
            _record_search_stage(receipt, "initial_query", state)
            if state.zero:
                raise ProbeFailure("native_zero_before_visible_controls")
            state = await adapter.ensure_relevance_sort(
                page,
                state,
                query=config.query,
                year_range=None,
                refinements=(),
                timeout_seconds=config.timeout_seconds,
                receipt=adapter_receipt,
            )

            year_range = adapter.requested_year_range(config.year_start, config.year_end)
            state = await adapter.apply_year_range(
                page,
                query=config.query,
                year_range=year_range,
                refinements=(),
                current_page_size=state.page_size,
                timeout_seconds=config.timeout_seconds,
                receipt=adapter_receipt,
            )
            _record_search_stage(receipt, "year_control", state)
            if state.zero:
                raise ProbeFailure("native_zero_after_year_control")

            refinements = adapter.content_type_refinements(config.content_types)
            state = await adapter.apply_content_type_refinements(
                page,
                query=config.query,
                year_range=year_range,
                refinements=refinements,
                current_page_size=state.page_size,
                timeout_seconds=config.timeout_seconds,
                receipt=adapter_receipt,
            )
            _record_search_stage(receipt, "content_type_control", state)
            if state.zero:
                raise ProbeFailure("native_zero_before_language_inventory")

            outcome = await wait_for_language_inventory(
                page,
                timeout_seconds=config.timeout_seconds,
                poll_interval_seconds=config.poll_interval_seconds,
            )
            if outcome.inventory is None:
                raise ProbeFailure(
                    outcome.failure_code or "language_projection_unavailable"
                )
            _record_language_projection(receipt, outcome.inventory)
            classification, healthy = classify_inventory(outcome.inventory)
            if not healthy:
                raise ProbeFailure(classification)
            receipt["source_reported_total"] = state.total
            receipt["source_total_status"] = "native_zero" if state.zero else "exact"
            return classification
    finally:
        safe_adapter_receipt = _safe_adapter_receipt(adapter, adapter_receipt)
        if isinstance(safe_adapter_receipt, dict):
            cleanup_section = safe_adapter_receipt.get("cleanup")
            cleanup_state = (
                cleanup_section.get("state")
                if isinstance(cleanup_section, Mapping)
                else None
            )
            if isinstance(cleanup_state, str):
                receipt["ownership"]["cleanup_state"] = cleanup_state
        if receipt["ownership"]["owned_page_created"]:
            receipt["ownership"]["cleanup_verified"] = (
                receipt["ownership"]["cleanup_state"] == "completed"
            )
        else:
            receipt["ownership"]["cleanup_verified"] = (
                receipt["ownership"]["cleanup_state"] == "not_needed"
            )


def _finish_receipt(receipt: dict[str, Any], classification: str, healthy: bool) -> None:
    receipt["result"] = {
        "status": "healthy" if healthy else "blocked",
        "classification": classification,
        "healthy": healthy,
        "observations_accepted": healthy,
    }


async def run_probe(
    config: ProbeConfig,
    *,
    playwright_factory: Callable[[], Any] | None = None,
    adapter_module: Any | None = None,
) -> tuple[int, dict[str, Any]]:
    """Run an opt-in one-page diagnostic and publish a create-only receipt."""

    try:
        config = validate_config(config)
    except Exception:
        receipt = new_receipt(False)
        _finish_receipt(receipt, "invalid_runtime_config", False)
        return 1, receipt

    receipt = new_receipt(config.execute)
    try:
        reservation = reserve_output_path(config.output_path)
    except OSError:
        _finish_receipt(receipt, "output_reservation_failed", False)
        return 1, receipt

    classification = "dry_run" if not config.execute else "browser_failure"
    healthy = False
    try:
        if config.execute:
            adapter = adapter_module if adapter_module is not None else _load_adapter()
            # The adapter's cleanup context owns only the page created below;
            # keep its safe structural receipt local until cleanup is verified.
            try:
                classification = await _execute_probe(
                    config,
                    receipt,
                    adapter=adapter,
                    playwright_factory=playwright_factory,
                )
                healthy = classification == "language_control_inventory_healthy"
            except Exception as error:  # noqa: BLE001 - fixed output boundary
                classification = _classify_exception(error)
                healthy = False
        else:
            receipt["ownership"]["cleanup_state"] = "not_needed"
            receipt["ownership"]["cleanup_verified"] = True
    except Exception as error:  # noqa: BLE001 - never expose browser text
        classification = _classify_exception(error)
        healthy = False

    if receipt["ownership"]["owned_page_created"] and not receipt["ownership"]["cleanup_verified"]:
        classification = "cleanup_verification_failed"
        healthy = False
    _finish_receipt(receipt, classification, healthy)
    try:
        write_reserved_json(reservation, receipt)
    except Exception:
        return 2, receipt
    return (0 if not config.execute or healthy else 1), receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="permit one live owned-page diagnostic")
    parser.add_argument("--query", required=True, help="exact IEEE Xplore query text")
    parser.add_argument("--year-start", type=int, required=True)
    parser.add_argument("--year-end", type=int, required=True)
    parser.add_argument(
        "--content-type",
        action="append",
        required=True,
        metavar="TYPE",
        help="visible content type passed through the current adapter; repeat for multiple types",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS)
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--output-path", required=True)
    return parser


def config_from_args(args: argparse.Namespace) -> ProbeConfig:
    return ProbeConfig(
        execute=args.execute,
        query=args.query,
        year_start=args.year_start,
        year_end=args.year_end,
        content_types=tuple(args.content_type),
        cdp_url=args.cdp_url,
        timeout_seconds=args.timeout,
        poll_interval_seconds=args.poll_interval,
        output_path=Path(args.output_path).expanduser(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = validate_config(config_from_args(args))
    except InputValidationError as error:
        parser.error(str(error))
    status, receipt = asyncio.run(run_probe(config))
    print(receipt["result"]["classification"], file=sys.stderr)
    return status


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
