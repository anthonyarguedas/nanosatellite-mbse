#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""One-owned-page Engineering Village public paired-Expert route probe.

The utility is a route/DOM diagnostic, not a search.  It attaches only to an
explicit loopback CDP endpoint, opens one distinct sibling page, makes one
normal navigation to the public paired Expert route, and returns a
rights-safe boolean/count receipt.  It never retains a raw URL, page body,
target ID, credential, cookie, query text, or source record.

``--execute`` is deliberately opt-in so ordinary offline tests and parser
checks make no source action.  A browser-lease wrapper can pass the explicit
CDP endpoint and opt in only after its own preflight has completed.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
EXPECTED_HOST = "www.engineeringvillage.com"
EXPECTED_PATH = "/search/expert.url"
PUBLIC_PAIRED_EXPERT_ROUTE = (
    "https://www.engineeringvillage.com/search/expert.url?database=3"
)
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_STABILIZATION_INTERVAL_SECONDS = 0.2
CLEANUP_TIMEOUT_SECONDS = 3.0
CLEANUP_POLL_INTERVAL_SECONDS = 0.05


class InputValidationError(ValueError):
    """Raised before any browser/Playwright use for invalid CLI input."""


class ProbeAbort(RuntimeError):
    """A fixed safe lifecycle classification; no browser text is retained."""

    def __init__(self, classification: str) -> None:
        super().__init__(classification)
        self.classification = classification


class SafeProjectionFailure(RuntimeError):
    """Base class for fixed safe post-navigation projection failures."""

    code = "projection_durable_failure"


class ExecutionContextReplaced(SafeProjectionFailure):
    """A transient browser execution context replacement."""

    code = "projection_execution_context_replaced"


class OngoingNavigation(SafeProjectionFailure):
    """A transient browser navigation still replacing the document."""

    code = "projection_ongoing_navigation"


class DurableProjectionFailure(SafeProjectionFailure):
    """A durable safe-projection or URL-classification failure."""

    code = "projection_durable_failure"


SAFE_PROBE_ABORT_CLASSIFICATIONS = frozenset(
    {
        "unexpected_browser_context_count",
        "baseline_target_inventory_unavailable",
        "owned_page_not_distinct",
        "owned_target_not_verified",
    }
)


def safe_probe_abort_classification(error: ProbeAbort) -> str:
    """Do not let an externally raised ProbeAbort inject receipt content."""
    classification = error.classification
    if (
        type(classification) is str
        and classification in SAFE_PROBE_ABORT_CLASSIFICATIONS
    ):
        return classification
    return "owned_page_operation_failed"


@dataclass(frozen=True)
class ProbeConfig:
    """Validated runtime input; it is deliberately not copied to output."""

    execute: bool
    cdp_url: str
    timeout_seconds: float
    stabilization_interval_seconds: float
    output_path: Path


@dataclass(frozen=True)
class RouteClassification:
    """Safe Python-only route facts; the raw URL remains local to this call."""

    route_class: str
    expected_host: bool
    expected_path: bool
    public_paired_expert_route: bool


@dataclass(frozen=True)
class ControlState:
    """One safe control-presence/check-state projection."""

    present: bool
    checked: bool | None


@dataclass(frozen=True)
class SafeProjection:
    """The strict allowlist of Engineering Village DOM facts."""

    expected_expert_title: bool
    access_detected: bool
    login_detected: bool
    challenge_detected: bool
    syntax_detected: bool
    controls: dict[str, ControlState]
    query_field_present: bool

    @property
    def paired_controls_present(self) -> bool:
        return bool(
            self.controls["compendex"].present and self.controls["inspec"].present
        )

    @property
    def paired_controls_checked(self) -> bool:
        return bool(
            self.controls["compendex"].checked is True
            and self.controls["inspec"].checked is True
        )


@dataclass(frozen=True)
class ProjectionSample:
    """One safe DOM snapshot and Python route classification."""

    route: RouteClassification
    projection: SafeProjection


@dataclass(frozen=True)
class StabilizationOutcome:
    """Bounded passive stabilization result without raw browser failures."""

    sample: ProjectionSample | None
    attempts: int
    stable_samples: int
    failure_code: str | None
    timed_out: bool


@dataclass(frozen=True)
class CleanupReport:
    """Ownership/continuity facts verified while the CDP session remains live."""

    close_attempted: bool
    page_closed: bool
    target_disappeared: bool
    baseline_preserved: bool | None
    baseline_target_set_preserved: bool | None = None

    @property
    def verified(self) -> bool:
        return bool(
            self.close_attempted
            and self.page_closed
            and self.target_disappeared
            and self.baseline_preserved is True
            and self.baseline_target_set_preserved is True
        )


CONTROL_NAMES = (
    "compendex",
    "inspec",
    "all",
    "knovel",
    "autostemming",
    "relevance",
)

SAFE_PROJECTION_SCRIPT = r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const control = selector => {
    const element = document.querySelector(selector);
    const present = Boolean(element && visible(element));
    return {
      present,
      checked: present ? Boolean(element.checked) : null
    };
  };
  const querySelectors = [
    "textarea[name='searchWord1']",
    "textarea[name='query']",
    "input[name='searchWord1']",
    "input[name='query']"
  ];
  const queryFieldPresent = querySelectors.some(selector => {
    const element = document.querySelector(selector);
    return Boolean(element && visible(element) && !element.disabled && !element.readOnly);
  });
  // Text is inspected only in the live page to derive booleans.  It is never
  // returned to Python or receipt output.
  const bodyText = String(document.body && document.body.innerText ? document.body.innerText : "").toLowerCase();
  const title = String(document.title || "").toLowerCase();
  const syntaxDetected = Array.from(document.querySelectorAll("*")).some(element =>
    visible(element) && String(element.textContent || "").replace(/\s+/g, " ").trim() ===
      "This search contains a syntax error."
  );
  return {
    expected_expert_title: title.includes("engineering village") &&
      (title.includes("expert") || title.includes("search")),
    access_detected: ["access currently limited", "access denied"].some(marker => bodyText.includes(marker)),
    login_detected: bodyText.includes("trouble signing in") ||
      (bodyText.includes("check to see if you have access") && bodyText.includes("institution")),
    challenge_detected: ["suspicious activity", "captcha", "verify you are human", "unusual traffic"].some(
      marker => bodyText.includes(marker)
    ),
    syntax_detected: syntaxDetected,
    controls: {
      compendex: control("#chkb-cpx"),
      inspec: control("#chkb-ins"),
      all: control("#all-checkb"),
      knovel: control("#chkb-kna"),
      autostemming: control("#chkb-autostem"),
      relevance: control("#radio-relevance")
    },
    query_field_present: queryFieldPresent
  };
}
"""


def compact(value: Any) -> str:
    """Compact local values without emitting source/browser text."""
    return " ".join(str(value or "").split())


def validate_loopback_cdp_endpoint(value: Any) -> str:
    """Require the one controller-shared CDP endpoint, with no overrides."""
    if type(value) is not str or value != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    return DEFAULT_CDP_URL


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


def _milliseconds(seconds: float) -> int:
    return max(1, int(seconds * 1_000))


def validate_output_path(value: str) -> Path:
    """Prepare one non-colliding create-only output destination before CDP use."""
    if not compact(value):
        raise InputValidationError("--output-path must be nonblank")
    candidate = Path(value).expanduser()
    if candidate.is_symlink():
        raise InputValidationError("--output-path must not be a symlink")
    path = candidate.resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise InputValidationError("--output-path must not already exist")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError("--output-path parent must be a directory")
    return path


def validate_runtime_config(config: Any) -> ProbeConfig:
    """Revalidate direct API input before any Playwright lifecycle can start."""
    if not isinstance(config, ProbeConfig) or type(config.execute) is not bool:
        raise InputValidationError("runtime probe configuration is invalid")
    if not isinstance(config.output_path, Path):
        raise InputValidationError("runtime probe configuration is invalid")
    timeout = _finite_positive(config.timeout_seconds, "--timeout-seconds")
    interval = _finite_positive(
        config.stabilization_interval_seconds, "--stabilization-interval-seconds"
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


def classify_public_paired_expert_url(value: Any) -> RouteClassification:
    """Classify a route in Python without returning or serializing the URL."""
    if not isinstance(value, str):
        return RouteClassification("invalid_url", False, False, False)
    try:
        parsed = urlsplit(value)
        # Access validates malformed port syntax without retaining it.
        _ = parsed.port
    except ValueError:
        return RouteClassification("invalid_url", False, False, False)
    hostname = (parsed.hostname or "").casefold()
    safe_https = (
        parsed.scheme.casefold() == "https"
        and not parsed.username
        and not parsed.password
    )
    expected_host = safe_https and hostname == EXPECTED_HOST
    expected_path = expected_host and parsed.path == EXPECTED_PATH
    public_paired = False
    if expected_path:
        try:
            public_paired = parse_qsl(
                parsed.query, keep_blank_values=True, strict_parsing=True
            ) == [("database", "3")]
        except ValueError:
            public_paired = False
    if public_paired:
        route_class = "public_paired_expert_route"
    elif expected_path:
        route_class = "expected_expert_route_nonpublic_or_unpaired"
    elif expected_host:
        route_class = "expected_host_other_route"
    else:
        route_class = "off_expected_host"
    return RouteClassification(route_class, expected_host, expected_path, public_paired)


def _boolean(value: Any) -> bool:
    return value is True


def projection_from_payload(payload: Any) -> SafeProjection:
    """Validate the fixed boolean/control allowlist returned by page.evaluate."""
    if not isinstance(payload, Mapping):
        raise DurableProjectionFailure()
    controls_payload = payload.get("controls")
    if not isinstance(controls_payload, Mapping) or set(controls_payload) != set(
        CONTROL_NAMES
    ):
        raise DurableProjectionFailure()
    controls: dict[str, ControlState] = {}
    for name in CONTROL_NAMES:
        raw = controls_payload.get(name)
        if not isinstance(raw, Mapping):
            raise DurableProjectionFailure()
        present = raw.get("present")
        checked = raw.get("checked")
        if present is not True and present is not False:
            raise DurableProjectionFailure()
        if checked is not None and checked is not True and checked is not False:
            raise DurableProjectionFailure()
        if present is False and checked is not None:
            raise DurableProjectionFailure()
        controls[name] = ControlState(present=present, checked=checked)
    bool_names = (
        "expected_expert_title",
        "access_detected",
        "login_detected",
        "challenge_detected",
        "syntax_detected",
        "query_field_present",
    )
    if any(
        payload.get(name) is not True and payload.get(name) is not False
        for name in bool_names
    ):
        raise DurableProjectionFailure()
    return SafeProjection(
        expected_expert_title=_boolean(payload.get("expected_expert_title")),
        access_detected=_boolean(payload.get("access_detected")),
        login_detected=_boolean(payload.get("login_detected")),
        challenge_detected=_boolean(payload.get("challenge_detected")),
        syntax_detected=_boolean(payload.get("syntax_detected")),
        controls=controls,
        query_field_present=_boolean(payload.get("query_field_present")),
    )


def classify_projection_exception(error: BaseException) -> SafeProjectionFailure:
    """Map browser errors to the only retriable fixed safe subclasses."""
    if isinstance(error, SafeProjectionFailure):
        return error
    message = compact(error).casefold()
    context_markers = (
        "execution context was destroyed",
        "execution context is not available",
        "cannot find context with specified id",
        "cannot find context",
        "context destroyed",
    )
    navigation_markers = (
        "navigation is in progress",
        "navigation in progress",
        "page is navigating",
        "ongoing navigation",
        "frame was detached",
    )
    if any(marker in message for marker in context_markers):
        return ExecutionContextReplaced()
    if any(marker in message for marker in navigation_markers):
        return OngoingNavigation()
    return DurableProjectionFailure()


async def capture_safe_projection(page: Any) -> ProjectionSample:
    """Evaluate only allowlisted DOM facts, then classify the current URL in Python."""
    try:
        payload = await page.evaluate(SAFE_PROJECTION_SCRIPT)
    except Exception as error:
        raise classify_projection_exception(error) from None
    try:
        route = classify_public_paired_expert_url(page.url)
    except Exception:
        raise DurableProjectionFailure() from None
    return ProjectionSample(route=route, projection=projection_from_payload(payload))


async def _sleep_to_deadline(
    deadline: float,
    interval: float,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> None:
    remaining = deadline - clock()
    if remaining > 0:
        await sleeper(min(interval, remaining))


async def stabilize_after_domcontentloaded(
    page: Any,
    *,
    timeout_seconds: float,
    interval_seconds: float,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> StabilizationOutcome:
    """Passively require two equal safe samples under one finite deadline.

    Only the two known browser-transient exception classes are retried.  This
    helper never reloads, clicks, fills, or calls navigation; the caller has
    already spent its one allowed navigation before entering this loop.
    """
    if clock is None:
        clock = asyncio.get_running_loop().time
    deadline = clock() + timeout_seconds
    previous: ProjectionSample | None = None
    last_transient_failure: SafeProjectionFailure | None = None
    attempts = 0

    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return StabilizationOutcome(
                sample=None,
                attempts=attempts,
                stable_samples=0,
                failure_code=(
                    last_transient_failure.code
                    if last_transient_failure is not None
                    else "projection_stabilization_timeout"
                ),
                timed_out=True,
            )
        attempts += 1
        try:
            # The complete evaluate-plus-route snapshot is bounded, not just
            # page.evaluate. A late snapshot is never accepted as stable.
            sample = await asyncio.wait_for(
                capture_safe_projection(page), timeout=remaining
            )
        except asyncio.TimeoutError:
            return StabilizationOutcome(
                sample=None,
                attempts=attempts,
                stable_samples=0,
                failure_code="projection_stabilization_timeout",
                timed_out=True,
            )
        except (ExecutionContextReplaced, OngoingNavigation) as error:
            last_transient_failure = error
            if clock() >= deadline:
                return StabilizationOutcome(
                    sample=None,
                    attempts=attempts,
                    stable_samples=0,
                    failure_code=error.code,
                    timed_out=True,
                )
            await _sleep_to_deadline(deadline, interval_seconds, clock, sleeper)
            continue
        except DurableProjectionFailure as error:
            return StabilizationOutcome(
                sample=None,
                attempts=attempts,
                stable_samples=0,
                failure_code=error.code,
                timed_out=False,
            )

        # Equality is meaningful only while the common deadline still holds.
        # In particular, a second equal sample that arrives late is discarded.
        if clock() >= deadline:
            return StabilizationOutcome(
                sample=None,
                attempts=attempts,
                stable_samples=0,
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


async def target_id_for(context: Any, page: Any) -> str | None:
    """Keep an owned target ID only in memory for exact cleanup verification."""
    session: Any | None = None
    try:
        session = await context.new_cdp_session(page)
        payload = await session.send("Target.getTargetInfo")
        info = payload.get("targetInfo") if isinstance(payload, Mapping) else None
        target_id = info.get("targetId") if isinstance(info, Mapping) else None
        return target_id if type(target_id) is str and target_id else None
    except Exception:
        return None
    finally:
        if session is not None:
            try:
                await session.detach()
            except Exception:
                pass


async def active_target_ids(browser: Any) -> frozenset[str] | None:
    """Read an unambiguous browser-level page-target inventory in memory."""
    session: Any | None = None
    try:
        session = await browser.new_browser_cdp_session()
        payload = await session.send("Target.getTargets")
        infos = payload.get("targetInfos") if isinstance(payload, Mapping) else None
        if not isinstance(infos, list):
            return None
        page_target_ids: list[str] = []
        for item in infos:
            if not isinstance(item, Mapping):
                return None
            if item.get("type") != "page":
                continue
            target_id = item.get("targetId")
            if type(target_id) is not str or not target_id:
                return None
            page_target_ids.append(target_id)
        if len(page_target_ids) != len(set(page_target_ids)):
            return None
        return frozenset(page_target_ids)
    except Exception:
        return None
    finally:
        if session is not None:
            try:
                await session.detach()
            except Exception:
                pass


def baseline_pages_preserved(context: Any, baseline_pages: tuple[Any, ...]) -> bool:
    """Check identity/closure only, never inspect or navigate baseline pages."""
    try:
        current = tuple(context.pages)
        if len(current) != len(baseline_pages):
            return False
        if any(left is not right for left, right in zip(current, baseline_pages)):
            return False
        return not any(page.is_closed() for page in baseline_pages)
    except Exception:
        return False


async def _wait_for_target_disappearance(
    browser: Any,
    target_id: str,
    *,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> bool:
    """Retain the narrow helper for callers that need disappearance alone."""
    deadline = clock() + CLEANUP_TIMEOUT_SECONDS
    while True:
        targets = await active_target_ids(browser)
        if targets is None:
            return False
        if target_id not in targets:
            return True
        if clock() >= deadline:
            return False
        await _sleep_to_deadline(
            deadline, CLEANUP_POLL_INTERVAL_SECONDS, clock, sleeper
        )


async def _wait_for_baseline_target_set(
    browser: Any,
    owned_target_id: str,
    baseline_target_ids: frozenset[str],
    *,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> tuple[bool, bool]:
    """Wait only for the exact pre-create target set to be restored."""
    deadline = clock() + CLEANUP_TIMEOUT_SECONDS
    while True:
        targets = await active_target_ids(browser)
        if targets is None:
            return False, False
        target_disappeared = owned_target_id not in targets
        baseline_target_set_preserved = targets == baseline_target_ids
        if baseline_target_set_preserved:
            return target_disappeared, True
        if clock() >= deadline:
            return target_disappeared, False
        await _sleep_to_deadline(
            deadline, CLEANUP_POLL_INTERVAL_SECONDS, clock, sleeper
        )


async def cleanup_owned_page(
    browser: Any,
    context: Any,
    owned_page: Any,
    owned_target_id: str | None,
    baseline_pages: tuple[Any, ...],
    *,
    baseline_target_ids: frozenset[str] | None = None,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> CleanupReport:
    """Close only a proven new page and restore the exact target baseline live."""
    if clock is None:
        clock = asyncio.get_running_loop().time
    close_attempted = True
    page_closed = False
    target_disappeared = False
    baseline_target_set_preserved: bool | None = None
    try:
        if not owned_page.is_closed():
            await owned_page.close()
        page_closed = bool(owned_page.is_closed())
    except Exception:
        page_closed = False
    if page_closed and owned_target_id is not None and baseline_target_ids is not None:
        (
            target_disappeared,
            baseline_target_set_preserved,
        ) = await _wait_for_baseline_target_set(
            browser,
            owned_target_id,
            baseline_target_ids,
            clock=clock,
            sleeper=sleeper,
        )
    return CleanupReport(
        close_attempted=close_attempted,
        page_closed=page_closed,
        target_disappeared=target_disappeared,
        baseline_preserved=baseline_pages_preserved(context, baseline_pages),
        baseline_target_set_preserved=baseline_target_set_preserved,
    )


def _safe_controls(
    projection: SafeProjection | None,
) -> dict[str, dict[str, bool | None]]:
    if projection is None:
        return {name: {"present": False, "checked": None} for name in CONTROL_NAMES}
    return {
        name: {"present": state.present, "checked": state.checked}
        for name, state in projection.controls.items()
    }


def new_receipt(execute: bool) -> dict[str, Any]:
    """Build a receipt whose schema cannot hold raw source/browser content."""
    return {
        "schema_version": "slr1-engineering-village-route-probe/v2",
        "mode": "source_action" if execute else "dry_run",
        "endpoint_class": "explicit_loopback_cdp",
        "operation": "one_owned_page_one_public_paired_expert_navigation",
        "navigation_attempt_count": 0,
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
            "owned_target_verified": False,
            "owned_page_close_attempted": False,
            "owned_page_closed": False,
            "owned_target_disappeared": False,
            "baseline_pages_preserved": None,
            "baseline_target_set_preserved": None,
        },
        "navigation": {
            "response_status": None,
            "route_class": "not_observed",
            "expected_host": False,
            "expected_path": False,
            "public_paired_expert_route": False,
            "expected_expert_title": False,
            "access_detected": False,
            "login_detected": False,
            "challenge_detected": False,
            "syntax_detected": False,
            "controls": _safe_controls(None),
            "paired_controls_present": False,
            "paired_controls_checked": False,
            "query_field_present": False,
            "stabilization_attempts": 0,
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


def _apply_stabilization(
    receipt: dict[str, Any], outcome: StabilizationOutcome
) -> None:
    navigation = receipt["navigation"]
    navigation["stabilization_attempts"] = outcome.attempts
    navigation["stable_samples"] = outcome.stable_samples
    navigation["projection_failure"] = outcome.failure_code
    navigation["projection_timed_out"] = outcome.timed_out
    if outcome.sample is None:
        return
    route = outcome.sample.route
    projection = outcome.sample.projection
    navigation.update(
        {
            "route_class": route.route_class,
            "expected_host": route.expected_host,
            "expected_path": route.expected_path,
            "public_paired_expert_route": route.public_paired_expert_route,
            "expected_expert_title": projection.expected_expert_title,
            "access_detected": projection.access_detected,
            "login_detected": projection.login_detected,
            "challenge_detected": projection.challenge_detected,
            "syntax_detected": projection.syntax_detected,
            "controls": _safe_controls(projection),
            "paired_controls_present": projection.paired_controls_present,
            "paired_controls_checked": projection.paired_controls_checked,
            "query_field_present": projection.query_field_present,
        }
    )


def classify_route_result(
    receipt: Mapping[str, Any], outcome: StabilizationOutcome
) -> tuple[str, bool]:
    """Fail closed from the safe, stabilized route/control projection."""
    if outcome.failure_code is not None:
        if outcome.timed_out and not outcome.failure_code.endswith("_timeout"):
            return f"{outcome.failure_code}_timeout", False
        return outcome.failure_code, False
    if outcome.timed_out:
        return "projection_stabilization_timeout", False
    navigation = receipt["navigation"]
    if navigation["challenge_detected"] is True:
        return "challenge_detected", False
    if navigation["access_detected"] is True:
        return "access_detected", False
    if navigation["login_detected"] is True:
        return "login_detected", False
    if navigation["syntax_detected"] is True:
        return "syntax_detected", False
    if (
        navigation["response_status"] is None
        or not 200 <= navigation["response_status"] < 400
    ):
        return "navigation_response_not_healthy", False
    if navigation["public_paired_expert_route"] is not True:
        return "public_paired_expert_route_not_verified", False
    if navigation["expected_expert_title"] is not True:
        return "expected_expert_title_not_verified", False
    if navigation["paired_controls_present"] is not True:
        return "paired_controls_not_present", False
    if navigation["paired_controls_checked"] is not True:
        return "paired_controls_not_checked", False
    if navigation["query_field_present"] is not True:
        return "query_field_not_present", False
    return "healthy", True


async def run_probe(
    config: ProbeConfig,
    *,
    playwright_factory: Callable[[], Any] | None = None,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> tuple[int, dict[str, Any]]:
    """Run one opt-in navigation and close it before the live session exits."""
    try:
        config = validate_runtime_config(config)
    except Exception:
        # Direct ProbeConfig construction cannot bypass pre-connection policy.
        receipt = new_receipt(False)
        _set_result(receipt, "invalid_runtime_config")
        return 1, receipt

    receipt = new_receipt(config.execute)
    if not config.execute:
        _set_result(receipt, "dry_run")
        receipt["result"]["status"] = "not_run"
        return 0, receipt

    if clock is None:
        clock = asyncio.get_running_loop().time
    if playwright_factory is None:
        from playwright.async_api import async_playwright

        playwright_factory = async_playwright

    browser: Any | None = None
    context: Any | None = None
    owned_page: Any | None = None
    owned_page_safe_to_close = False
    owned_target_id: str | None = None
    baseline_pages: tuple[Any, ...] = ()
    baseline_target_ids: frozenset[str] | None = None
    classification = "browser_connection_failed"
    healthy = False

    try:
        # The nested finally is intentionally inside this async Playwright
        # context.  It must finish target-disappearance verification before
        # Playwright disconnects from the browser lease.
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
                # Browser-level target ownership is the authority. Snapshot it
                # before creating anything, while retaining IDs only in memory.
                baseline_target_ids = await active_target_ids(browser)
                if baseline_target_ids is None:
                    raise ProbeAbort("baseline_target_inventory_unavailable")

                owned_page = await context.new_page()
                receipt["ownership"]["owned_page_created"] = True
                distinct = all(
                    owned_page is not baseline for baseline in baseline_pages
                )
                receipt["ownership"]["owned_page_distinct_from_baseline"] = distinct
                if not distinct:
                    raise ProbeAbort("owned_page_not_distinct")

                post_create_target_ids = await active_target_ids(browser)
                owned_target_id = await target_id_for(context, owned_page)
                owned_target_is_new = bool(
                    owned_target_id is not None
                    and post_create_target_ids is not None
                    and owned_target_id in post_create_target_ids
                    and owned_target_id not in baseline_target_ids
                )
                # A target that is proven non-baseline is safe to close even if
                # a concurrent target mutation makes the run fail before goto.
                owned_page_safe_to_close = owned_target_is_new
                target_verified = False
                if owned_target_is_new and post_create_target_ids is not None:
                    assert owned_target_id is not None
                    expected_target_ids = baseline_target_ids | frozenset(
                        {owned_target_id}
                    )
                    target_verified = (
                        post_create_target_ids == expected_target_ids
                        and post_create_target_ids - baseline_target_ids
                        == frozenset({owned_target_id})
                    )
                receipt["ownership"]["owned_target_verified"] = target_verified
                if not target_verified:
                    raise ProbeAbort("owned_target_not_verified")

                # This is the only navigation in this probe.  Stabilization
                # below is evaluate/sleep only and has no reload fallback.
                receipt["navigation_attempt_count"] = 1
                response = await owned_page.goto(
                    PUBLIC_PAIRED_EXPERT_ROUTE,
                    wait_until="domcontentloaded",
                    timeout=_milliseconds(config.timeout_seconds),
                )
                status = getattr(response, "status", None)
                receipt["navigation"]["response_status"] = (
                    status
                    if isinstance(status, int)
                    and not isinstance(status, bool)
                    and 100 <= status <= 599
                    else None
                )
                outcome = await stabilize_after_domcontentloaded(
                    owned_page,
                    timeout_seconds=config.timeout_seconds,
                    interval_seconds=config.stabilization_interval_seconds,
                    clock=clock,
                    sleeper=sleeper,
                )
                _apply_stabilization(receipt, outcome)
                classification, healthy = classify_route_result(receipt, outcome)
            except ProbeAbort as error:
                classification = safe_probe_abort_classification(error)
                healthy = False
            except Exception:
                classification = "owned_page_operation_failed"
                healthy = False
            finally:
                if (
                    owned_page is not None
                    and owned_page_safe_to_close
                    and browser is not None
                    and context is not None
                    and baseline_target_ids is not None
                ):
                    try:
                        cleanup = await cleanup_owned_page(
                            browser,
                            context,
                            owned_page,
                            owned_target_id,
                            baseline_pages,
                            baseline_target_ids=baseline_target_ids,
                            clock=clock,
                            sleeper=sleeper,
                        )
                        ownership = receipt["ownership"]
                        ownership["owned_page_close_attempted"] = (
                            cleanup.close_attempted
                        )
                        ownership["owned_page_closed"] = cleanup.page_closed
                        ownership["owned_target_disappeared"] = (
                            cleanup.target_disappeared
                        )
                        ownership["baseline_pages_preserved"] = (
                            cleanup.baseline_preserved
                        )
                        ownership["baseline_target_set_preserved"] = (
                            cleanup.baseline_target_set_preserved
                        )
                        if not cleanup.verified:
                            classification = "cleanup_verification_failed"
                            healthy = False
                    except Exception:
                        receipt["ownership"]["owned_page_close_attempted"] = True
                        receipt["ownership"]["baseline_pages_preserved"] = False
                        receipt["ownership"]["baseline_target_set_preserved"] = False
                        classification = "cleanup_verification_failed"
                        healthy = False
    except Exception:
        if classification != "cleanup_verification_failed":
            classification = "browser_connection_failed"
            healthy = False

    _set_result(receipt, classification, healthy)
    return (0 if healthy else 1), receipt


def write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Create one JSON receipt using O_EXCL; a collision can never overwrite."""
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def parse_args(argv: list[str] | None = None) -> ProbeConfig:
    """Validate endpoint, timing, and output collision before Playwright import."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="permit one source navigation"
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
            args.stabilization_interval_seconds, "--stabilization-interval-seconds"
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
    raise AssertionError("argparse.error did not exit")  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    try:
        status, receipt = asyncio.run(run_probe(config))
    except Exception:
        status, receipt = 1, new_receipt(config.execute)
        _set_result(receipt, "internal_probe_failure")
    try:
        write_new_json(config.output_path, receipt)
    except OSError:
        # Do not echo a controller-private output path.
        return 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
