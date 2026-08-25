#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Run one record-free, rendered NTRS source-health precheck.

The precheck attaches only to the controller's shared loopback Chrome lease,
opens one distinct adapter-owned page, navigates once to the public NTRS root,
and inspects only a fixed boolean/enum DOM projection.  It never submits a
query, visits a citation, calls the historical JSON API, captures records, or
bypasses a challenge.  ``--execute`` is required for any browser action; the
default CLI path is an offline dry run.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import sys
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
SOURCE_ORIGIN = "https://ntrs.nasa.gov"
SOURCE_ROOT_URL = f"{SOURCE_ORIGIN}/"
SOURCE_HOSTS = frozenset({"ntrs.nasa.gov", "www.ntrs.nasa.gov"})
SOURCE_ROOT_PATHS = frozenset({"/", "/search"})
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_STABILIZATION_INTERVAL_SECONDS = 0.2
CLEANUP_TIMEOUT_SECONDS = 3.0
CLEANUP_POLL_INTERVAL_SECONDS = 0.05


class InputValidationError(ValueError):
    """Raised before any browser/Playwright lifecycle for invalid input."""


class ProbeAbort(RuntimeError):
    """A fixed safe lifecycle classification; no browser text is retained."""

    def __init__(self, classification: str) -> None:
        super().__init__(classification)
        self.classification = classification


class ProjectionFailure(RuntimeError):
    """Base class for fixed safe projection classifications."""

    code = "projection_durable_failure"


class ProjectionContextReplaced(ProjectionFailure):
    """The document execution context was replaced during a passive read."""

    code = "projection_execution_context_replaced"


class ProjectionNavigationInProgress(ProjectionFailure):
    """The document was still being replaced during a passive read."""

    code = "projection_navigation_in_progress"


@dataclass(frozen=True)
class ProbeConfig:
    """Validated runtime input; no value is copied into the receipt."""

    execute: bool
    cdp_url: str
    timeout_seconds: float
    stabilization_interval_seconds: float
    output_path: Path


@dataclass(frozen=True)
class RouteClassification:
    """Safe route facts; the raw page URL remains local to one call."""

    route_class: str
    source_host: bool
    normal_source_route: bool


@dataclass(frozen=True)
class HealthProjection:
    """The fixed allowlist returned by the owned-page DOM projection."""

    route_class: str
    source_identity: bool
    search_control_present: bool
    challenge_detected: bool
    access_detected: bool
    login_detected: bool
    busy_detected: bool
    error_detected: bool
    document_available: bool
    document_ready_state: str


@dataclass(frozen=True)
class HealthSample:
    projection: HealthProjection


@dataclass(frozen=True)
class StabilizationOutcome:
    """Bounded passive observation; no raw browser value is retained."""

    sample: HealthSample | None
    attempts: int
    stable_samples: int
    failure_code: str | None
    timed_out: bool


# This projection deliberately returns no title, body, URL, HTML, form value,
# query text, or record field.  Text is used in the page only to derive fixed
# classifications.  The source route is independently classified in Python.
NTRS_HEALTH_PROJECTION_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/[\s\u00a0]+/g, " ").trim();
  const visible = element => Boolean(element &&
    (element.offsetWidth || element.offsetHeight || element.getClientRects().length) &&
    window.getComputedStyle(element).display !== "none" &&
    window.getComputedStyle(element).visibility !== "hidden");
  const host = String(location.hostname || "").toLowerCase();
  const sourceRoute = ["ntrs.nasa.gov", "www.ntrs.nasa.gov"].includes(host) &&
    ["/", "/search"].includes(location.pathname) && !location.search && !location.hash;
  const title = normalize(document.title).toLowerCase();
  const body = normalize(document.body && document.body.innerText).slice(0, 12000).toLowerCase();
  const combined = `${title} ${body}`;
  const challenge = Boolean(document.querySelector(
    "#challenge-form, #challenge-running, [id*='challenge' i], [class*='captcha' i], iframe[src*='challenge' i]"
  )) || [
    "attention required", "just a moment", "verify you are human", "captcha",
    "unusual traffic", "access denied"
  ].some(marker => combined.includes(marker));
  const access = /access denied|forbidden|enable javascript and cookies/.test(combined);
  const login = /\/(?:login|signin|auth)(?:\/|$)/i.test(location.pathname) ||
    Array.from(document.querySelectorAll("input[type='password']")).some(visible);
  const busy = /server too busy|please slow down|too many requests|rate limit/.test(combined);
  const error = /bad gateway|gateway timeout|proxy error|service unavailable|temporarily unavailable|unable to load|unexpected error|internal server error|error\s*5\d\d/.test(combined);
  const queryInputs = Array.from(document.querySelectorAll(
    "input, textarea, [contenteditable='true']"
  )).filter(visible).filter(element => {
    const type = String(element.getAttribute("type") || "text").toLowerCase();
    const key = ["name", "id", "aria-label", "placeholder", "data-testid"]
      .map(name => String(element.getAttribute(name) || "")).join(" ").toLowerCase();
    return !["hidden", "password", "date", "checkbox", "radio", "submit", "button"].includes(type) &&
      /(?:^|[-_\s])(search|query|q)(?:$|[-_\s])/.test(key);
  });
  return {
    sourceIdentity: sourceRoute,
    searchControlPresent: queryInputs.length > 0,
    challengeDetected: challenge,
    accessDetected: access,
    loginDetected: login,
    busyDetected: busy,
    errorDetected: error,
    documentAvailable: Boolean(document.documentElement),
    documentReadyState: ["loading", "interactive", "complete"].includes(document.readyState)
      ? document.readyState : "unresolved"
  };
}
"""

SAFE_PROBE_ABORT_CLASSIFICATIONS = frozenset(
    {
        "unexpected_browser_context_count",
        "owned_page_not_distinct",
        "owned_page_not_verified",
        "owned_page_cleanup_handoff_required",
        "cleanup_verification_failed",
    }
)


def safe_probe_abort_classification(error: ProbeAbort) -> str:
    """Prevent arbitrary raised text from entering a receipt."""

    value = error.classification
    if type(value) is str and value in SAFE_PROBE_ABORT_CLASSIFICATIONS:
        return value
    return "owned_page_operation_failed"


def _finite_positive(value: Any, option: str) -> float:
    if isinstance(value, bool):
        raise InputValidationError(f"{option} must be a finite positive number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(
            f"{option} must be a finite positive number"
        ) from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise InputValidationError(f"{option} must be a finite positive number")
    return parsed


def validate_loopback_cdp_endpoint(value: Any) -> str:
    """Require the one controller-shared CfT endpoint."""

    if type(value) is not str or value != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    return DEFAULT_CDP_URL


def validate_output_path(value: Any) -> Path:
    """Validate a create-only receipt destination before source activity."""

    if type(value) is not str or not value.strip():
        raise InputValidationError("--output-path must be nonblank")
    candidate = Path(value).expanduser()
    if candidate.exists() or candidate.is_symlink():
        raise InputValidationError("--output-path must not already exist")
    path = candidate.resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise InputValidationError("--output-path must not already exist")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError("--output-path parent must be a directory")
    return path


def validate_runtime_config(config: Any) -> ProbeConfig:
    """Revalidate direct API input before importing Playwright."""

    if not isinstance(config, ProbeConfig) or type(config.execute) is not bool:
        raise InputValidationError("runtime probe configuration is invalid")
    if not isinstance(config.output_path, Path):
        raise InputValidationError("runtime probe configuration is invalid")
    timeout = _finite_positive(config.timeout_seconds, "--timeout-seconds")
    interval = _finite_positive(
        config.stabilization_interval_seconds,
        "--stabilization-interval-seconds",
    )
    if interval > timeout:
        raise InputValidationError(
            "--stabilization-interval-seconds cannot exceed --timeout-seconds"
        )
    return ProbeConfig(
        execute=config.execute,
        cdp_url=validate_loopback_cdp_endpoint(config.cdp_url),
        timeout_seconds=timeout,
        stabilization_interval_seconds=interval,
        output_path=validate_output_path(str(config.output_path)),
    )


def _milliseconds(seconds: float) -> int:
    return max(1, int(seconds * 1_000))


def classify_ntrs_url(value: Any) -> RouteClassification:
    """Classify only the public source route; never return the URL."""

    if not isinstance(value, str):
        return RouteClassification("invalid_url", False, False)
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return RouteClassification("invalid_url", False, False)
    hostname = (parsed.hostname or "").casefold()
    source_host = bool(
        parsed.scheme == "https"
        and hostname in SOURCE_HOSTS
        and parsed.port is None
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )
    normal = bool(source_host and parsed.path in SOURCE_ROOT_PATHS)
    if normal:
        route_class = "normal_source_route"
    elif source_host:
        route_class = "expected_source_other_route"
    else:
        route_class = "off_source_route"
    return RouteClassification(route_class, source_host, normal)


def _bool_field(payload: Mapping[str, Any], key: str) -> bool:
    value = payload.get(key)
    if type(value) is not bool:
        raise ProjectionFailure()
    return value


def projection_from_payload(payload: Any, route: RouteClassification) -> HealthProjection:
    """Validate the fixed safe projection returned from the page."""

    if not isinstance(payload, Mapping):
        raise ProjectionFailure()
    ready_state = payload.get("documentReadyState")
    if ready_state not in {"loading", "interactive", "complete", "unresolved"}:
        raise ProjectionFailure()
    return HealthProjection(
        route_class=route.route_class,
        source_identity=_bool_field(payload, "sourceIdentity"),
        search_control_present=_bool_field(payload, "searchControlPresent"),
        challenge_detected=_bool_field(payload, "challengeDetected"),
        access_detected=_bool_field(payload, "accessDetected"),
        login_detected=_bool_field(payload, "loginDetected"),
        busy_detected=_bool_field(payload, "busyDetected"),
        error_detected=_bool_field(payload, "errorDetected"),
        document_available=_bool_field(payload, "documentAvailable"),
        document_ready_state=ready_state,
    )


def classify_projection_exception(error: BaseException) -> ProjectionFailure:
    """Map only known browser-transient wording to fixed safe categories."""

    message = f"{type(error).__name__} {error}".casefold()
    if any(
        marker in message
        for marker in (
            "execution context was destroyed",
            "execution context is not available",
            "cannot find context",
            "context destroyed",
        )
    ):
        return ProjectionContextReplaced()
    if any(
        marker in message
        for marker in (
            "navigation is in progress",
            "navigation in progress",
            "page is navigating",
            "frame was detached",
        )
    ):
        return ProjectionNavigationInProgress()
    return ProjectionFailure()


async def capture_health_projection(page: Any) -> HealthSample:
    """Read only the fixed DOM projection and classify the final route locally."""

    try:
        route = classify_ntrs_url(page.url)
        payload = await page.evaluate(NTRS_HEALTH_PROJECTION_SCRIPT)
        return HealthSample(projection=projection_from_payload(payload, route))
    except ProjectionFailure:
        raise
    except Exception as error:
        raise classify_projection_exception(error) from None


def _terminal_projection(projection: HealthProjection) -> bool:
    return bool(
        projection.challenge_detected
        or projection.access_detected
        or projection.login_detected
        or projection.busy_detected
        or projection.error_detected
    )


async def _sleep_to_deadline(
    deadline: float,
    interval: float,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> None:
    remaining = deadline - clock()
    if remaining <= 0:
        return
    try:
        await asyncio.wait_for(sleeper(min(interval, remaining)), timeout=remaining)
    except asyncio.TimeoutError:
        return


async def stabilize_health(
    page: Any,
    *,
    timeout_seconds: float,
    interval_seconds: float,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> StabilizationOutcome:
    """Require two equal healthy projections under one finite passive deadline."""

    if clock is None:
        clock = asyncio.get_running_loop().time
    deadline = clock() + timeout_seconds
    previous: HealthSample | None = None
    last_transient: ProjectionFailure | None = None
    attempts = 0
    last_sample: HealthSample | None = None

    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return StabilizationOutcome(
                sample=last_sample,
                attempts=attempts,
                stable_samples=0 if previous is None else 1,
                failure_code=(
                    last_transient.code
                    if last_transient is not None
                    else "projection_stabilization_timeout"
                ),
                timed_out=True,
            )
        attempts += 1
        try:
            sample = await asyncio.wait_for(
                capture_health_projection(page), timeout=remaining
            )
        except asyncio.TimeoutError:
            return StabilizationOutcome(
                sample=last_sample,
                attempts=attempts,
                stable_samples=0,
                failure_code="projection_stabilization_timeout",
                timed_out=True,
            )
        except (ProjectionContextReplaced, ProjectionNavigationInProgress) as error:
            last_transient = error
            await _sleep_to_deadline(
                deadline, interval_seconds, clock, sleeper
            )
            continue
        except ProjectionFailure as error:
            return StabilizationOutcome(
                sample=last_sample,
                attempts=attempts,
                stable_samples=0,
                failure_code=error.code,
                timed_out=False,
            )

        last_sample = sample
        if _terminal_projection(sample.projection):
            # A challenge, access page, busy page, login, or source error is a
            # terminal diagnostic state.  No passive retry is a bypass.
            return StabilizationOutcome(
                sample=sample,
                attempts=attempts,
                stable_samples=1,
                failure_code=None,
                timed_out=False,
            )
        if clock() >= deadline:
            return StabilizationOutcome(
                sample=sample,
                attempts=attempts,
                stable_samples=1,
                failure_code="projection_stabilization_timeout",
                timed_out=True,
            )
        if previous == sample:
            return StabilizationOutcome(
                sample=sample,
                attempts=attempts,
                stable_samples=2,
                failure_code=None,
                timed_out=False,
            )
        previous = sample
        await _sleep_to_deadline(deadline, interval_seconds, clock, sleeper)


def _status_class(response: Any) -> str | None:
    if response is None:
        return None
    status = getattr(response, "status", None)
    if isinstance(status, bool) or not isinstance(status, int):
        return "other"
    if status < 100 or status > 999:
        return "other"
    return f"{status // 100}xx" if status < 600 else "other"


def new_receipt(execute: bool) -> dict[str, Any]:
    """Build a record-free receipt with no raw browser/source fields."""

    return {
        "schema_version": "slr1-ntrs-source-health/v1",
        "mode": "source_action" if execute else "dry_run",
        "operation": "one_owned_page_one_public_root_navigation",
        "endpoint_class": "shared_cft_loopback",
        "navigation_attempt_count": 0,
        "record_free": True,
        "source_total": None,
        "records_observed": 0,
        "retention_exclusions": [
            "url",
            "body_text",
            "html",
            "target_id",
            "cookie",
            "credential",
            "query_text",
            "record",
            "exception_string",
        ],
        "ownership": {
            "existing_context_count": None,
            "baseline_page_count": None,
            "owned_page_created": False,
            "owned_page_distinct_from_baseline": False,
            "owned_page_verified": False,
            "owned_page_close_attempted": False,
            "owned_page_closed": False,
            "owned_page_absent_after_close": False,
            "baseline_pages_preserved": None,
        },
        "navigation": {
            "response_status_class": None,
            "route_class": "not_observed",
            "source_identity": False,
            "search_control_present": False,
            "challenge_detected": False,
            "access_detected": False,
            "login_detected": False,
            "busy_detected": False,
            "error_detected": False,
            "document_available": False,
            "document_ready_state": "not_observed",
            "projection_attempts": 0,
            "stable_samples": 0,
            "projection_failure": None,
            "projection_timed_out": False,
        },
        "result": {
            "status": "not_run",
            "classification": "not_run",
            "healthy": False,
            "observations_accepted": False,
        },
    }


def _set_result(
    receipt: dict[str, Any], classification: str, healthy: bool = False
) -> None:
    receipt["result"] = {
        "status": "healthy" if healthy else "blocked",
        "classification": classification,
        "healthy": healthy,
        "observations_accepted": healthy,
    }


def _apply_outcome(receipt: dict[str, Any], outcome: StabilizationOutcome) -> None:
    navigation = receipt["navigation"]
    navigation["projection_attempts"] = outcome.attempts
    navigation["stable_samples"] = outcome.stable_samples
    navigation["projection_failure"] = outcome.failure_code
    navigation["projection_timed_out"] = outcome.timed_out
    if outcome.sample is None:
        return
    projection = outcome.sample.projection
    navigation.update(
        {
            "route_class": projection.route_class,
            "source_identity": projection.source_identity,
            "search_control_present": projection.search_control_present,
            "challenge_detected": projection.challenge_detected,
            "access_detected": projection.access_detected,
            "login_detected": projection.login_detected,
            "busy_detected": projection.busy_detected,
            "error_detected": projection.error_detected,
            "document_available": projection.document_available,
            "document_ready_state": projection.document_ready_state,
        }
    )


def classify_health_result(
    receipt: Mapping[str, Any], outcome: StabilizationOutcome | None
) -> tuple[str, bool]:
    """Fail closed from status and the fixed stabilized projection."""

    if outcome is None:
        return "navigation_failed", False
    if outcome.sample is not None:
        projection = outcome.sample.projection
        if projection.challenge_detected:
            return "challenge_detected", False
        if projection.access_detected:
            return "access_detected", False
        if projection.login_detected:
            return "login_detected", False
        if projection.busy_detected:
            return "busy_detected", False
        if projection.error_detected:
            return "source_error_detected", False
    if outcome.failure_code is not None or outcome.timed_out:
        return "source_health_not_stable", False
    navigation = receipt["navigation"]
    if navigation.get("response_status_class") != "2xx":
        return "navigation_response_not_healthy", False
    if navigation.get("route_class") != "normal_source_route":
        return "normal_source_route_not_verified", False
    if navigation.get("source_identity") is not True:
        return "source_identity_not_verified", False
    if navigation.get("document_available") is not True:
        return "document_not_available", False
    if navigation.get("search_control_present") is not True:
        return "search_surface_not_ready", False
    if outcome.stable_samples < 2:
        return "source_health_not_stable", False
    return "healthy", True


def _page_is_closed(page: Any) -> bool:
    checker = getattr(page, "is_closed", None)
    try:
        return bool(checker()) if callable(checker) else False
    except Exception:
        return False


def _page_absent(context: Any, page: Any) -> bool:
    try:
        return all(candidate is not page for candidate in tuple(context.pages))
    except Exception:
        return False


def _baseline_preserved(context: Any, baseline: tuple[Any, ...]) -> bool:
    try:
        current = tuple(context.pages)
        if len(current) != len(baseline):
            return False
        if any(left is not right for left, right in zip(current, baseline)):
            return False
        return all(not _page_is_closed(page) for page in baseline)
    except Exception:
        return False


async def _close_owned_page(
    context: Any,
    page: Any,
    baseline: tuple[Any, ...],
) -> bool:
    try:
        await asyncio.wait_for(page.close(), timeout=CLEANUP_TIMEOUT_SECONDS)
    except Exception:
        return False
    return bool(
        _page_is_closed(page)
        and _page_absent(context, page)
        and _baseline_preserved(context, baseline)
    )


async def run_probe(
    config: ProbeConfig,
    *,
    playwright_factory: Callable[[], Any] | None = None,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> tuple[int, dict[str, Any]]:
    """Reserve one receipt, optionally navigate once, and close only its page."""

    try:
        config = validate_runtime_config(config)
    except Exception:
        receipt = new_receipt(False)
        _set_result(receipt, "invalid_runtime_config")
        return 1, receipt

    receipt = new_receipt(config.execute)
    try:
        # Create-only reservation happens before importing or starting
        # Playwright.  A collision therefore cannot trigger source activity.
        handle = config.output_path.open("x", encoding="utf-8")
    except OSError:
        _set_result(receipt, "output_reservation_failed")
        return 1, receipt

    classification = "browser_connection_failed"
    healthy = False
    browser: Any | None = None
    context: Any | None = None
    owned_page: Any | None = None
    baseline_pages: tuple[Any, ...] = ()
    owned_page_distinct = False
    owned_page_verified = False
    output_write_failed = False

    try:
        if not config.execute:
            classification = "dry_run"
        else:
            if clock is None:
                clock = asyncio.get_running_loop().time
            if playwright_factory is None:
                from playwright.async_api import async_playwright

                playwright_factory = async_playwright
            async with playwright_factory() as playwright:
                try:
                    browser = await playwright.chromium.connect_over_cdp(
                        config.cdp_url,
                        timeout=_milliseconds(config.timeout_seconds),
                    )
                    contexts = tuple(browser.contexts)
                    receipt["ownership"]["existing_context_count"] = len(contexts)
                    if len(contexts) != 1:
                        raise ProbeAbort("unexpected_browser_context_count")
                    context = contexts[0]
                    baseline_pages = tuple(context.pages)
                    receipt["ownership"]["baseline_page_count"] = len(baseline_pages)
                    owned_page = await context.new_page()
                    receipt["ownership"]["owned_page_created"] = True
                    owned_page_distinct = all(
                        owned_page is not baseline for baseline in baseline_pages
                    )
                    receipt["ownership"][
                        "owned_page_distinct_from_baseline"
                    ] = owned_page_distinct
                    try:
                        current_pages = tuple(context.pages)
                    except Exception:
                        current_pages = ()
                    owned_page_verified = bool(
                        owned_page_distinct
                        and any(owned_page is page for page in current_pages)
                    )
                    receipt["ownership"]["owned_page_verified"] = (
                        owned_page_verified
                    )
                    if not owned_page_distinct:
                        raise ProbeAbort("owned_page_not_distinct")
                    if not owned_page_verified:
                        raise ProbeAbort("owned_page_not_verified")

                    receipt["navigation_attempt_count"] = 1
                    deadline = clock() + config.timeout_seconds
                    outcome: StabilizationOutcome | None = None
                    try:
                        remaining = deadline - clock()
                        if remaining <= 0:
                            raise asyncio.TimeoutError
                        response = await asyncio.wait_for(
                            owned_page.goto(
                                SOURCE_ROOT_URL,
                                wait_until="domcontentloaded",
                                timeout=_milliseconds(remaining),
                            ),
                            timeout=remaining,
                        )
                        receipt["navigation"]["response_status_class"] = _status_class(
                            response
                        )
                        remaining = deadline - clock()
                        if remaining <= 0:
                            outcome = StabilizationOutcome(
                                None, 0, 0, "projection_stabilization_timeout", True
                            )
                        else:
                            outcome = await stabilize_health(
                                owned_page,
                                timeout_seconds=remaining,
                                interval_seconds=min(
                                    config.stabilization_interval_seconds,
                                    remaining,
                                ),
                                clock=clock,
                                sleeper=sleeper,
                            )
                        _apply_outcome(receipt, outcome)
                        classification, healthy = classify_health_result(
                            receipt, outcome
                        )
                    except asyncio.TimeoutError:
                        receipt["navigation"]["projection_failure"] = (
                            "navigation_timeout"
                        )
                        classification = "navigation_timeout"
                        healthy = False
                    except Exception:
                        classification = "navigation_failed"
                        healthy = False
                except ProbeAbort as error:
                    classification = safe_probe_abort_classification(error)
                    healthy = False
                except Exception:
                    classification = "browser_connection_failed"
                    healthy = False
                finally:
                    if (
                        context is not None
                        and owned_page is not None
                        and owned_page_distinct
                        and owned_page_verified
                    ):
                        receipt["ownership"]["owned_page_close_attempted"] = True
                        cleanup_ok = await _close_owned_page(
                            context, owned_page, baseline_pages
                        )
                        receipt["ownership"]["owned_page_closed"] = _page_is_closed(
                            owned_page
                        )
                        receipt["ownership"][
                            "owned_page_absent_after_close"
                        ] = _page_absent(context, owned_page)
                        receipt["ownership"]["baseline_pages_preserved"] = (
                            _baseline_preserved(context, baseline_pages)
                        )
                        if not cleanup_ok:
                            classification = "cleanup_verification_failed"
                            healthy = False
                    elif context is not None:
                        receipt["ownership"]["baseline_pages_preserved"] = (
                            _baseline_preserved(context, baseline_pages)
                        )
                        if owned_page is not None and owned_page_distinct:
                            classification = "owned_page_cleanup_handoff_required"
                            healthy = False
    finally:
        _set_result(receipt, classification, healthy)
        if not config.execute:
            receipt["result"]["status"] = "not_run"
        try:
            handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            handle.close()
        except Exception:
            output_write_failed = True
            try:
                handle.close()
            except Exception:
                pass

    if output_write_failed:
        return 2, receipt
    return (0 if not config.execute or healthy else 1), receipt


def parse_args(argv: Sequence[str] | None = None) -> ProbeConfig:
    """Parse and validate the offline-safe CLI contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="permit the one root navigation"
    )
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument(
        "--stabilization-interval-seconds",
        type=float,
        default=DEFAULT_STABILIZATION_INTERVAL_SECONDS,
    )
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args(argv)
    try:
        timeout = _finite_positive(args.timeout_seconds, "--timeout-seconds")
        interval = _finite_positive(
            args.stabilization_interval_seconds,
            "--stabilization-interval-seconds",
        )
        if interval > timeout:
            raise InputValidationError(
                "--stabilization-interval-seconds cannot exceed --timeout-seconds"
            )
        return ProbeConfig(
            execute=args.execute,
            cdp_url=validate_loopback_cdp_endpoint(args.cdp_url),
            timeout_seconds=timeout,
            stabilization_interval_seconds=interval,
            output_path=validate_output_path(args.output_path),
        )
    except InputValidationError as error:
        parser.error(str(error))
    raise AssertionError("argparse.error did not exit")


def main(argv: Sequence[str] | None = None) -> int:
    config = parse_args(argv)
    try:
        status, _ = asyncio.run(run_probe(config))
    except Exception:
        # The source activity and receipt write are owned by run_probe.  This
        # final boundary emits only a status, never an exception string.
        return 2
    return status


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
