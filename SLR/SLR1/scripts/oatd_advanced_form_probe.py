#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""One owned-page OATD advanced-form diagnostic.

The probe is intentionally narrower than a search adapter.  It attaches only
through an explicit loopback CDP endpoint, creates one sibling page, passively
waits through one finite transient challenge window when needed, submits one
normal nonblank advanced GET form, and retains only a safe aggregate receipt.
It never visits record/detail/full-text routes, serializes browser URLs or
target IDs, or interacts with access controls. An explicit exploration-only
``--pre-submit-busy-wait-seconds`` value enables a bounded same-page DOM wait
for an ordinary pre-submit busy state; the default is off and the wait never
reissues or navigates.

Source action is opt-in with ``--execute``.  This makes the default CLI path
safe for offline validation and for tests run by a browser-lease controller.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import secrets
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
SOURCE_ORIGIN = "https://oatd.org"
SOURCE_HOST = "oatd.org"
HOME_PATH = "/"
HOME_URL = f"{SOURCE_ORIGIN}{HOME_PATH}"
ADVANCED_ENTRY_LABEL = "Advanced search options"
ADVANCED_PATH = "/oatd/search-composer"
ADVANCED_ACTION = f"{SOURCE_ORIGIN}{ADVANCED_PATH}"
RESULT_PATH = "/oatd/search"

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_POLL_INTERVAL_SECONDS = 0.2
DEFAULT_BUSY_RETRIES = 2
DEFAULT_BUSY_RETRY_DELAY_SECONDS = 30.0
MAX_BUSY_RETRIES = 2
MIN_BUSY_RETRY_DELAY_SECONDS = 1.0
MAX_BUSY_RETRY_DELAY_SECONDS = 3_600.0
# Exploration-only opt-in for an ordinary pre-submit busy page.  Zero keeps
# the held P05 behavior unchanged; a positive value only adds same-page DOM
# projections and never consumes a source-operation slot.
DEFAULT_PRE_SUBMIT_BUSY_WAIT_SECONDS = 0.0
DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS = 2.0
MAX_PRE_SUBMIT_BUSY_WAIT_SECONDS = 180.0
MAX_PRE_SUBMIT_BUSY_OBSERVATIONS = (
    int(MAX_PRE_SUBMIT_BUSY_WAIT_SECONDS / DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS)
    + 1
)
SAFE_PRE_SUBMIT_BUSY_OBSERVATION_STATES = frozenset(
    {"busy", "clear", "challenge", "access", "syntax"}
)
# A challenge is given one finite, passive-only window before the one native
# submission.  This is deliberately separate from the post-submit busy
# reissue budget: challenge polls never consume a source-operation slot.
DEFAULT_CHALLENGE_WAIT_SECONDS = 30.0
DEFAULT_CHALLENGE_POLL_INTERVAL_SECONDS = 0.2
MAX_CHALLENGE_WAIT_SECONDS = 30.0
CLEANUP_TIMEOUT_SECONDS = 3.0
CLEANUP_POLL_INTERVAL_SECONDS = 0.05
MAX_QUERY_CHARACTERS = 50_000
MAX_FIELD_LABEL_CHARACTERS = 512
MAX_CONTROL_VALUE_CHARACTERS = 50_000

# These are the only successful GET controls that may be reconstructed for a
# finite same-tab busy retry.  Values remain in memory and are never copied to
# the receipt.  A changed/unknown successful control fails closed instead of
# being copied from an observed URL or generic FormData payload.
RETRY_CONTROL_NAMES = (
    "form",
    "box1",
    "field1",
    "joiner1",
    "op12",
    "box2",
    "field2",
    "joiner2",
    "op23",
    "box3",
    "field3",
    "joiner3",
    "op34",
    "box4",
    "field4",
    "joiner4",
    "language",
    "country",
    "earliest",
    "latest",
    "sortby",
    "pagesize",
    "cc_only",
)
NATIVE_SUBMIT_SELECTOR = (
    "button:not([type]), button[type=''], button[type='submit' i], "
    "input[type='submit' i]"
)


class InputValidationError(ValueError):
    """Raised before any browser connection for an unsafe CLI value."""


class ProbeAbort(RuntimeError):
    """A fixed safe terminal classification; it never carries source text."""

    def __init__(self, classification: str) -> None:
        super().__init__(classification)
        self.classification = classification


@dataclass(frozen=True)
class PreClickSafety:
    """Boolean-only proof required immediately before native submission."""

    current_canonical_composer_route: bool
    source_identity: bool
    exact_https_origin: bool
    canonical_effective_get_action: bool
    form_target_self: bool
    submitter_no_override: bool

    @property
    def verified(self) -> bool:
        return bool(
            self.current_canonical_composer_route
            and self.source_identity
            and self.exact_https_origin
            and self.canonical_effective_get_action
            and self.form_target_self
            and self.submitter_no_override
        )


class PreClickSafetyFailure(ProbeAbort):
    """Carries only safe boolean proof facts to the receipt layer."""

    def __init__(self, safety: PreClickSafety) -> None:
        super().__init__("pre_click_safety_not_verified")
        self.safety = safety


SAFE_PROBE_ABORT_CLASSIFICATIONS = frozenset(
    {
        "unexpected_browser_context_count",
        "baseline_target_inventory_unavailable",
        "owned_page_not_distinct",
        "owned_target_not_verified",
        "owned_page_cleanup_handoff_required",
        "challenge_before_submission",
        "busy_before_submission",
        "access_before_submission",
        "syntax_before_submission",
        "canonical_advanced_form_not_observed",
        "advanced_form_control_mapping_failed",
        "advanced_field_mapping_failed",
        "native_submit_control_not_unique",
        "advanced_form_projection_failed",
        "advanced_retry_controls_not_prevalidated",
        "advanced_control_readback_failed",
        "native_submit_interaction_failed",
        "pre_click_safety_projection_failed",
        "pre_click_safety_not_verified",
        "post_click_projection_failed",
        "accounting_checkpoint_failed",
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
class FinalizeConfig:
    """No-browser recovery inputs for a previously reserved execution."""

    journal_path: Path
    ledger_path: Path


@dataclass(frozen=True)
class ProbeConfig:
    """Validated invocation data; sensitive values are never serialized."""

    execute: bool
    cdp_url: str
    query: str
    field_label: str
    timeout_seconds: float
    poll_interval_seconds: float
    busy_retries: int
    busy_retry_delay_seconds: float
    output_path: Path
    challenge_wait_seconds: float = DEFAULT_CHALLENGE_WAIT_SECONDS
    challenge_poll_interval_seconds: float = DEFAULT_CHALLENGE_POLL_INTERVAL_SECONDS
    journal_path: Path | None = None
    ledger_path: Path | None = None
    pre_submit_busy_wait_seconds: float = DEFAULT_PRE_SUBMIT_BUSY_WAIT_SECONDS


@dataclass
class OutputReservation:
    """One atomically claimed receipt inode held through source activity."""

    path: Path
    descriptor: int


JOURNAL_SCHEMA_VERSION = "slr1-oatd-advanced-form-journal/v1"
LEDGER_SCHEMA_VERSION = "slr1-oatd-advanced-form-ledger/v1"
ACCOUNTING_OPERATION_IDS = ("O-001", "O-002", "O-003")
ACCOUNTING_OPERATION_KINDS = ("native_submit", "busy_reissue", "busy_reissue")
SAFE_ACCOUNTING_CLASSIFICATIONS = frozenset(
    {
        "not_started",
        "dry_run",
        "browser_connection_failed",
        "guardian_interrupted",
        "journal_unavailable",
        "accounting_checkpoint_failed",
        "accounting_publication_failed",
        "busy_retry_checkpoint_failed",
        "busy_retry_navigation_failed",
        "busy_revalidation_failed",
        "busy_after_submission",
        "challenge_after_submission",
        "post_submit_state_timeout",
        "submission_not_observed_timeout",
        "result_observed",
        "zero_observed",
        "access_after_submission",
        "syntax_after_submission",
        "challenge_before_submission",
        "busy_before_submission",
        "access_before_submission",
        "syntax_before_submission",
        "canonical_advanced_form_not_observed",
        "advanced_form_control_mapping_failed",
        "advanced_field_mapping_failed",
        "native_submit_control_not_unique",
        "advanced_form_projection_failed",
        "advanced_retry_controls_not_prevalidated",
        "advanced_control_readback_failed",
        "native_submit_interaction_failed",
        "pre_click_safety_projection_failed",
        "pre_click_safety_not_verified",
        "post_click_projection_failed",
        "unexpected_browser_context_count",
        "baseline_target_inventory_unavailable",
        "owned_page_not_distinct",
        "owned_target_not_verified",
        "owned_page_cleanup_handoff_required",
        "owned_page_operation_failed",
        "cleanup_verification_failed",
        "output_reservation_failed",
        "accounting_reservation_failed",
        "invalid_runtime_config",
    }
)


def _write_all(descriptor: int, encoded: bytes) -> None:
    """Write all bytes without reopening a reserved path."""
    view = memoryview(encoded)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("reserved accounting file made no progress")
        view = view[written:]


@dataclass
class DurableJournal:
    """Append-only, fsynced safe checkpoints for one execute-mode run."""

    reservation: OutputReservation
    reservation_id: str
    sequence: int = 0

    @property
    def path(self) -> Path:
        return self.reservation.path

    def checkpoint(self, phase: str, snapshot: Mapping[str, Any]) -> None:
        descriptor = self.reservation.descriptor
        if descriptor < 0:
            raise OSError("journal reservation is no longer writable")
        self.sequence += 1
        record = {
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "reservation_id": self.reservation_id,
            "sequence": self.sequence,
            "phase": phase,
            "snapshot": dict(snapshot),
        }
        _write_all(
            descriptor,
            (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode(
                "utf-8"
            ),
        )
        os.fsync(descriptor)

    def close(self) -> None:
        descriptor = self.reservation.descriptor
        if descriptor >= 0:
            self.reservation.descriptor = -1
            os.close(descriptor)


def _safe_accounting_classification(value: Any, default: str) -> str:
    return (
        value
        if type(value) is str and value in SAFE_ACCOUNTING_CLASSIFICATIONS
        else default
    )


def _safe_accounting_total(value: Any) -> int | None:
    return _exact_nonnegative_int(value)


@dataclass
class ExecutionAccounting:
    """In-memory operation state mirrored to the durable journal."""

    reservation_id: str
    operations: list[dict[str, Any]]
    busy_retry_delays: list[float]
    pre_submit_busy_observations: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(cls, reservation_id: str, busy_retry_delay: float) -> "ExecutionAccounting":
        return cls(
            reservation_id=reservation_id,
            operations=[
                {
                    "operation_id": operation_id,
                    "kind": kind,
                    "dispatch_status": "not_dispatched",
                    "dispatched": False,
                    "possibly_dispatched": False,
                    "completed": False,
                    "attempted": False,
                    "wait_seconds": None,
                }
                for operation_id, kind in zip(
                    ACCOUNTING_OPERATION_IDS, ACCOUNTING_OPERATION_KINDS
                )
            ],
            busy_retry_delays=[
                min(busy_retry_delay * (2**index), MAX_BUSY_RETRY_DELAY_SECONDS)
                for index in range(MAX_BUSY_RETRIES)
            ],
        )

    def record_pre_submit_busy_observation(
        self,
        journal: DurableJournal,
        *,
        poll: int,
        state: str,
        waited_seconds: float,
    ) -> None:
        """Fsync one allowlisted passive busy observation without source text."""
        if (
            type(poll) is not int
            or poll < 0
            or poll >= MAX_PRE_SUBMIT_BUSY_OBSERVATIONS
        ):
            raise ValueError("pre-submit busy observation poll is outside the cap")
        if type(state) is not str or state not in SAFE_PRE_SUBMIT_BUSY_OBSERVATION_STATES:
            raise ValueError("pre-submit busy observation state is not allowlisted")
        if (
            isinstance(waited_seconds, bool)
            or not isinstance(waited_seconds, (int, float))
            or not math.isfinite(float(waited_seconds))
            or not 0 <= float(waited_seconds) <= MAX_PRE_SUBMIT_BUSY_WAIT_SECONDS
        ):
            raise ValueError("pre-submit busy observation time is unsafe")
        observation = {
            "poll": poll,
            "state": state,
            "waited_seconds": float(waited_seconds),
        }
        self.pre_submit_busy_observations.append(observation)
        self.checkpoint(journal, f"pre_submit_busy_observation_{poll}")

    def _operation(self, operation_number: int) -> dict[str, Any]:
        if not 1 <= operation_number <= len(self.operations):
            raise ValueError("accounting operation number is outside the fixed cap")
        return self.operations[operation_number - 1]

    def mark_possibly_dispatched(
        self, operation_number: int, *, wait_seconds: float | None = None
    ) -> None:
        operation = self._operation(operation_number)
        operation["dispatch_status"] = "possibly_dispatched"
        operation["possibly_dispatched"] = True
        operation["attempted"] = True
        if wait_seconds is not None:
            operation["wait_seconds"] = wait_seconds

    def mark_dispatched(self, operation_number: int) -> None:
        operation = self._operation(operation_number)
        operation["dispatch_status"] = "dispatched"
        operation["dispatched"] = True
        operation["possibly_dispatched"] = True
        operation["attempted"] = True
        operation["completed"] = True

    def snapshot(
        self,
        *,
        classification: str | None = None,
        source_total: int | None = None,
        interrupted: bool = False,
        terminal: bool = False,
    ) -> dict[str, Any]:
        snapshot: dict[str, Any] = {
            "reservation_id": self.reservation_id,
            "busy_retry_policy": {
                "maximum_retries": MAX_BUSY_RETRIES,
                "wait_delays_seconds": list(self.busy_retry_delays),
            },
            "operations": [dict(operation) for operation in self.operations],
            "interrupted": bool(interrupted),
        }
        if self.pre_submit_busy_observations:
            snapshot["pre_submit_busy_observations"] = [
                dict(observation)
                for observation in self.pre_submit_busy_observations
            ]
        if classification is not None:
            safe_classification = _safe_accounting_classification(
                classification, "owned_page_operation_failed"
            )
            safe_total = _safe_accounting_total(source_total)
            accepted = (
                safe_classification in {"result_observed", "zero_observed"}
                and safe_total is not None
            )
            snapshot["terminal"] = {
                "classification": safe_classification,
                "source_total": safe_total if accepted else None,
                "observations_accepted": accepted,
                "interrupted": bool(interrupted),
                "terminal_checkpoint": bool(terminal),
            }
        return snapshot

    def checkpoint(
        self,
        journal: DurableJournal,
        phase: str,
        *,
        classification: str | None = None,
        source_total: int | None = None,
        interrupted: bool = False,
        terminal: bool = False,
    ) -> None:
        journal.checkpoint(
            phase,
            self.snapshot(
                classification=classification,
                source_total=source_total,
                interrupted=interrupted,
                terminal=terminal,
            ),
        )

    def before_native_click(self, journal: DurableJournal) -> None:
        # This checkpoint is deliberately before the awaitable click.  If a
        # guardian stops the child after fsync, the finalizer must count this
        # operation conservatively as possibly dispatched.
        self.mark_possibly_dispatched(1)
        self.checkpoint(journal, "before_native_click")

    def after_native_click(self, journal: DurableJournal) -> None:
        self.mark_dispatched(1)
        self.checkpoint(journal, "after_native_click")

    def before_busy_retry(
        self, journal: DurableJournal, retry_number: int, delay: float
    ) -> None:
        self.mark_possibly_dispatched(retry_number + 1, wait_seconds=delay)
        self.checkpoint(journal, f"before_busy_reissue_{retry_number}")

    def after_busy_retry(self, journal: DurableJournal, retry_number: int) -> None:
        self.mark_dispatched(retry_number + 1)
        self.checkpoint(journal, f"after_busy_reissue_{retry_number}")

    def terminal_ledger(
        self,
        classification: str,
        source_total: int | None,
        *,
        interrupted: bool = False,
        recovered: bool = False,
    ) -> dict[str, Any]:
        safe_classification = _safe_accounting_classification(
            classification, "owned_page_operation_failed"
        )
        safe_total = _safe_accounting_total(source_total)
        accepted = (
            safe_classification in {"result_observed", "zero_observed"}
            and safe_total is not None
            and not interrupted
            and all(
                operation["completed"]
                for operation in self.operations
                if operation["possibly_dispatched"]
            )
        )
        operations = [dict(operation) for operation in self.operations]
        possibly_dispatched = sum(
            bool(operation["possibly_dispatched"]) for operation in operations
        )
        dispatched = sum(bool(operation["dispatched"]) for operation in operations)
        completed = sum(bool(operation["completed"]) for operation in operations)
        payload = {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "status": "terminal",
            "reservation_id": self.reservation_id,
            "recovered_after_interruption": bool(recovered),
            "busy_retry_policy": {
                "maximum_retries": MAX_BUSY_RETRIES,
                "wait_delays_seconds": list(self.busy_retry_delays),
            },
            "operations": operations,
            "counts": {
                "source_operations_reserved": len(operations),
                "source_operations_possibly_dispatched": possibly_dispatched,
                "source_operations_dispatched": dispatched,
                "source_operations_completed": completed,
                "busy_retries_attempted": sum(
                    operation["attempted"]
                    for operation in operations
                    if operation["kind"] == "busy_reissue"
                ),
                "busy_retries_completed": sum(
                    operation["completed"]
                    for operation in operations
                    if operation["kind"] == "busy_reissue"
                ),
            },
            "terminal": {
                "classification": safe_classification,
                "source_reported_total": safe_total if accepted else None,
                "observations_accepted": accepted,
                "interrupted": bool(interrupted),
                "possibly_dispatched": possibly_dispatched > 0,
            },
        }
        if self.pre_submit_busy_observations:
            payload["pre_submit_busy_observations"] = [
                dict(observation)
                for observation in self.pre_submit_busy_observations
            ]
        return payload


@dataclass(frozen=True)
class FormInspection:
    """Safe form counts plus transient mapping data required for interaction."""

    source_state: str | None
    canonical_form_count: int
    form_index: int
    method_get: bool
    box1_count: int
    field1_count: int
    matching_field_option_count: int
    field_value: str | None
    visible_native_submit_count: int


@dataclass(frozen=True)
class PreparedSubmission:
    """Prevalidated values for a possible same-tab busy retry."""

    retry_parameters: tuple[tuple[str, str], ...]
    visible_native_submit_count: int
    pre_click_safety: PreClickSafety


@dataclass(frozen=True)
class ChallengeWaitOutcome:
    """Passive challenge observation before the single native submission."""

    inspection: FormInspection | None
    classification: str | None
    polls: int
    waited_seconds: float


@dataclass(frozen=True)
class PreSubmitBusyWaitOutcome:
    """Passive ordinary-busy observation before the native submission."""

    inspection: FormInspection | None
    classification: str | None
    polls: int
    waited_seconds: float
    observations: tuple[str, ...]


@dataclass(frozen=True)
class PostClickState:
    """Allowlisted post-click facts only; no text, URL, or record escapes."""

    challenge: bool
    busy: bool
    access: bool
    syntax_error: bool
    canonical_advanced_route: bool
    source_identity: bool
    form_readback_exact: bool
    result_kind: str
    source_total: int | None
    result_observed: bool

    @property
    def submission_observed(self) -> bool:
        return self.result_observed or (
            self.canonical_advanced_route and self.form_readback_exact
        )

    @property
    def busy_retry_safe(self) -> bool:
        return bool(
            self.busy
            and not self.challenge
            and not self.access
            and not self.syntax_error
            and self.canonical_advanced_route
            and self.source_identity
            and self.form_readback_exact
        )


@dataclass(frozen=True)
class PostClickOutcome:
    """The one terminal state from bounded post-click observation."""

    classification: str
    source_total: int | None
    polls: int
    # Retained for compatibility; "performed" means dispatched/attempted.
    busy_retries_performed: int
    busy_recovery_attempts: int
    busy_retries_completed: int = 0

    @property
    def busy_retries_attempted(self) -> int:
        """Retries accounted immediately before their awaitable goto call."""
        return self.busy_retries_performed


@dataclass
class BusyRetryBudget:
    """Adapter-v3-style finite, run-wide extra-request budget."""

    max_retries: int
    initial_delay_seconds: float
    recovery_attempts: int = 0
    attempted_retries: int = 0
    completed_retries: int = 0

    def __post_init__(self) -> None:
        # Keep the internal helper capped even when a direct test/caller does
        # not pass through CLI validation.
        self.max_retries = min(self.max_retries, MAX_BUSY_RETRIES)

    @property
    def performed_retries(self) -> int:
        """Compatibility name for retries dispatched to page.goto."""
        return self.attempted_retries

    def reserve_delay(self) -> float | None:
        """Reserve one finite recovery wait and return its capped delay."""
        if self.recovery_attempts >= self.max_retries:
            return None
        delay = min(
            self.initial_delay_seconds * (2**self.recovery_attempts),
            MAX_BUSY_RETRY_DELAY_SECONDS,
        )
        self.recovery_attempts += 1
        return delay

    def record_retry_attempt(self) -> None:
        """Consume and account a retry immediately before dispatching goto."""
        if self.attempted_retries >= self.recovery_attempts:
            raise RuntimeError("busy retry was not reserved")
        self.attempted_retries += 1

    def record_retry_completion(self) -> None:
        """Account only a goto that returned normally after dispatch."""
        if self.completed_retries >= self.attempted_retries:
            raise RuntimeError("busy retry completion was not attempted")
        self.completed_retries += 1


@dataclass(frozen=True)
class CleanupReport:
    """Safe ownership-continuity facts produced before Playwright disconnects."""

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


ADVANCED_FORM_INSPECTION_SCRIPT = r"""
(fieldLabel) => {
  const normalize = value => String(value || "").replace(/[\s\u2009\u202f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const title = normalize(document.title);
  const sourceTitle = /\bOATD\b/i.test(title);
  const errors = Array.from(document.querySelectorAll(
    ".error, .error_message, .message.error, [role='alert']"
  )).filter(visible).map(element => normalize(element.textContent)).join(" ");
  const challenge = (!sourceTitle && /just a moment|attention required|verify you are human/i.test(title)) ||
    Boolean(document.querySelector(
      "#challenge-running, #challenge-form, iframe[src*='challenges.cloudflare.com'], .cf-challenge-running"
    ));
  const busyPattern = /^(?:🟢\s*)?(?:server too busy(?:\s*[-:,.]\s*please slow down)?|please slow down)[.!]?$/i;
  const busy = busyPattern.test(errors) || (!sourceTitle && busyPattern.test(title));
  const access = /access denied|forbidden|captcha|enable javascript and cookies|log\s*in|sign\s*in|authentication required|verification required/i.test(errors) ||
    (!sourceTitle && /captcha|log\s*in|sign\s*in|authentication required|verification required/i.test(title));
  const syntaxError = /syntax|could not parse|invalid query|search error/i.test(errors);
  // Access/CAPTCHA wins over the challenge marker: a transition to an
  // access-controlled state is terminal and must not receive more waiting.
  const sourceState = access ? "access" : challenge ? "challenge" : busy ? "busy" :
    syntaxError ? "syntax" : null;
  const forms = Array.from(document.forms);
  const canonical = forms.filter(form => {
    try {
      const action = new URL(form.getAttribute("action") || "", document.baseURI);
      return action.protocol === "https:" && action.origin === "https://oatd.org" &&
        action.hostname === "oatd.org" && action.port === "" && action.username === "" &&
        action.password === "" && action.pathname === "/oatd/search-composer" &&
        action.search === "" && action.hash === "" && form.method.toLowerCase() === "get";
    } catch (_) {
      return false;
    }
  });
  const form = canonical.length === 1 ? canonical[0] : null;
  const fields = form ? Array.from(form.querySelectorAll("select[name='field1']")) : [];
  const boxes = form ? Array.from(form.querySelectorAll(
    "input[name='box1'], textarea[name='box1']"
  )) : [];
  const field = fields.length === 1 ? fields[0] : null;
  const options = field ? Array.from(field.options) : [];
  const wanted = normalize(fieldLabel);
  const matches = options.filter(option => normalize(option.textContent) === wanted);
  const nativeSubmits = form ? Array.from(form.querySelectorAll("button, input")).filter(element =>
    visible(element) && ((element.tagName === "BUTTON" && element.type === "submit") ||
      (element.tagName === "INPUT" && element.type === "submit"))
  ) : [];
  return {
    source_state: sourceState,
    canonical_form_count: canonical.length,
    form_index: form ? forms.indexOf(form) : -1,
    method_get: Boolean(form && form.method.toLowerCase() === "get"),
    box1_count: boxes.length,
    field1_count: fields.length,
    matching_field_option_count: matches.length,
    matching_field_value: matches.length === 1 ? String(matches[0].value || "") : null,
    visible_native_submit_count: nativeSubmits.length
  };
}
"""

FORM_SELF_CHECK_SCRIPT = r"""
(form) => {
  const isCanonical = candidate => {
    try {
      const action = new URL(candidate.getAttribute("action") || "", document.baseURI);
      return action.protocol === "https:" && action.origin === "https://oatd.org" &&
        action.hostname === "oatd.org" && action.port === "" && action.username === "" &&
        action.password === "" && action.pathname === "/oatd/search-composer" &&
        action.search === "" && action.hash === "" && candidate.method.toLowerCase() === "get";
    } catch (_) {
      return false;
    }
  };
  const canonical = Array.from(document.forms).filter(isCanonical);
  return {
    canonical_form_count: canonical.length,
    selected_form_is_canonical: canonical.length === 1 && canonical[0] === form
  };
}
"""

PRE_CLICK_SAFETY_SCRIPT = r"""
(form) => {
  const result = {
    current_canonical_composer_route: false,
    source_identity: false,
    exact_https_origin: false,
    canonical_effective_get_action: false,
    form_target_self: false,
    submitter_no_override: false
  };
  const normalize = value => String(value || "").replace(/[\s\u2009\u202f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const formValue = (candidate, name) => {
    const descriptor = Object.getOwnPropertyDescriptor(HTMLFormElement.prototype, name);
    if (!descriptor || typeof descriptor.get !== "function") throw new Error("form getter unavailable");
    return descriptor.get.call(candidate);
  };
  const exactOatdOrigin = value => {
    try {
      const parsed = new URL(String(value));
      return parsed.protocol === "https:" && parsed.origin === "https://oatd.org" &&
        parsed.hostname === "oatd.org" && parsed.port === "" &&
        parsed.username === "" && parsed.password === "" && parsed.hash === "";
    } catch (_) {
      return false;
    }
  };
  try {
    if (!(form instanceof HTMLFormElement)) return result;
    const current = new URL(window.location.href);
    result.exact_https_origin = exactOatdOrigin(current.href);
    result.current_canonical_composer_route = result.exact_https_origin &&
      ["/", "/oatd/search-composer"].includes(current.pathname) &&
      current.search === "" && current.hash === "";

    const sourceTitle = /\bOATD\b/i.test(normalize(document.title));
    const sourceHeading = Array.from(document.querySelectorAll("h3.pageHeader a.inheader"))
      .some(element => normalize(element.textContent) === "Open Access Theses and Dissertations");
    result.source_identity = Boolean(sourceTitle && sourceHeading);

    const isCanonicalEffectiveGet = candidate => {
      if (!(candidate instanceof HTMLFormElement)) return false;
      try {
        const action = new URL(String(formValue(candidate, "action")));
        return exactOatdOrigin(action.href) && action.pathname === "/oatd/search-composer" &&
          action.search === "" && action.hash === "" &&
          String(formValue(candidate, "method")).toLowerCase() === "get";
      } catch (_) {
        return false;
      }
    };
    const canonicalForms = Array.from(document.forms).filter(isCanonicalEffectiveGet);
    result.canonical_effective_get_action = Boolean(
      isCanonicalEffectiveGet(form) && canonicalForms.length === 1 && canonicalForms[0] === form
    );

    const isSelfTarget = target => target === "" || target.toLowerCase() === "_self";
    const effectiveTarget = String(formValue(form, "target") || "");
    // A document-level base target can otherwise turn an omitted form target
    // into a new browsing context, so reject every non-self base target too.
    const baseTargetsAreSelf = Array.from(document.querySelectorAll("base[target]"))
      .every(base => isSelfTarget(String(base.getAttribute("target") || "")));
    result.form_target_self = isSelfTarget(effectiveTarget) && baseTargetsAreSelf;

    const nativeSubmits = Array.from(form.querySelectorAll("button, input")).filter(element =>
      visible(element) && ((element.tagName === "BUTTON" && element.type === "submit") ||
        (element.tagName === "INPUT" && element.type === "submit"))
    );
    const submitter = nativeSubmits.length === 1 ? nativeSubmits[0] : null;
    result.submitter_no_override = Boolean(
      submitter && submitter.form === form &&
      !Element.prototype.hasAttribute.call(submitter, "formaction") &&
      !Element.prototype.hasAttribute.call(submitter, "formmethod") &&
      !Element.prototype.hasAttribute.call(submitter, "formtarget")
    );
  } catch (_) {
    // A malformed or changing document leaves the fixed-safe booleans false.
  }
  return result;
}
"""

NATIVE_SUBMIT_GUARD_SCRIPT = r"""
(submitter) => {
  const empty = () => ({
    current_canonical_composer_route: false,
    source_identity: false,
    exact_https_origin: false,
    canonical_effective_get_action: false,
    form_target_self: false,
    submitter_no_override: false
  });
  const normalize = value => String(value || "").replace(/[\s\u2009\u202f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const formValue = (candidate, name) => {
    const descriptor = Object.getOwnPropertyDescriptor(HTMLFormElement.prototype, name);
    if (!descriptor || typeof descriptor.get !== "function") throw new Error("form getter unavailable");
    return descriptor.get.call(candidate);
  };
  const exactOatdOrigin = value => {
    try {
      const parsed = new URL(String(value));
      return parsed.protocol === "https:" && parsed.origin === "https://oatd.org" &&
        parsed.hostname === "oatd.org" && parsed.port === "" &&
        parsed.username === "" && parsed.password === "" && parsed.hash === "";
    } catch (_) {
      return false;
    }
  };
  const isSelfTarget = target => target === "" || target.toLowerCase() === "_self";
  const safetyFor = () => {
    const result = empty();
    try {
      if (!(submitter instanceof HTMLButtonElement) && !(submitter instanceof HTMLInputElement)) {
        return result;
      }
      const form = submitter.form;
      if (!(form instanceof HTMLFormElement)) return result;
      const current = new URL(window.location.href);
      result.exact_https_origin = exactOatdOrigin(current.href);
      result.current_canonical_composer_route = result.exact_https_origin &&
        ["/", "/oatd/search-composer"].includes(current.pathname) &&
        current.search === "" && current.hash === "";

      const sourceTitle = /\bOATD\b/i.test(normalize(document.title));
      const sourceHeading = Array.from(document.querySelectorAll("h3.pageHeader a.inheader"))
        .some(element => normalize(element.textContent) === "Open Access Theses and Dissertations");
      result.source_identity = Boolean(sourceTitle && sourceHeading);

      const isCanonicalEffectiveGet = candidate => {
        if (!(candidate instanceof HTMLFormElement)) return false;
        try {
          const action = new URL(String(formValue(candidate, "action")));
          return exactOatdOrigin(action.href) && action.pathname === "/oatd/search-composer" &&
            action.search === "" && action.hash === "" &&
            String(formValue(candidate, "method")).toLowerCase() === "get";
        } catch (_) {
          return false;
        }
      };
      const canonicalForms = Array.from(document.forms).filter(isCanonicalEffectiveGet);
      result.canonical_effective_get_action = Boolean(
        isCanonicalEffectiveGet(form) && canonicalForms.length === 1 && canonicalForms[0] === form
      );

      const effectiveTarget = String(formValue(form, "target") || "");
      const baseTargetsAreSelf = Array.from(document.querySelectorAll("base[target]"))
        .every(base => isSelfTarget(String(base.getAttribute("target") || "")));
      result.form_target_self = isSelfTarget(effectiveTarget) && baseTargetsAreSelf;

      const nativeSubmits = Array.from(form.querySelectorAll("button, input")).filter(element =>
        visible(element) && ((element.tagName === "BUTTON" && element.type === "submit") ||
          (element.tagName === "INPUT" && element.type === "submit"))
      );
      result.submitter_no_override = Boolean(
        nativeSubmits.length === 1 && nativeSubmits[0] === submitter && submitter.form === form &&
        !Element.prototype.hasAttribute.call(submitter, "formaction") &&
        !Element.prototype.hasAttribute.call(submitter, "formmethod") &&
        !Element.prototype.hasAttribute.call(submitter, "formtarget")
      );
    } catch (_) {
      return empty();
    }
    return result;
  };
  const safety = safetyFor();
  if (!Object.values(safety).every(Boolean)) return safety;
  const form = submitter.form;
  // submit() bypasses submit events.  Lock its public prototype entry for the
  // short-lived owned page before allowing the click; a nonstandard/unlockable
  // entry fails closed instead of leaving a programmatic-submit bypass open.
  const submitDescriptor = Object.getOwnPropertyDescriptor(
    HTMLFormElement.prototype, "submit"
  );
  if (
    !submitDescriptor ||
    typeof submitDescriptor.value !== "function" ||
    (submitDescriptor.writable !== true && submitDescriptor.configurable !== true)
  ) return empty();
  try {
    Object.defineProperty(HTMLFormElement.prototype, "submit", {
      configurable: false,
      enumerable: submitDescriptor.enumerable,
      value: () => undefined,
      writable: false
    });
  } catch (_) {
    return empty();
  }
  let acceptedClick = false;
  let acceptedSubmit = false;
  const block = event => {
    try {
      if (event.type === "click") {
        const path = event.composedPath();
        const exactClick = Boolean(
          event.isTrusted === true &&
          (event.target === submitter || path.includes(submitter))
        );
        const stillSafe = safetyFor();
        if (
          !exactClick ||
          acceptedClick ||
          !Object.values(stillSafe).every(Boolean)
        ) {
          event.preventDefault();
          event.stopImmediatePropagation();
          return;
        }
        acceptedClick = true;
        // Stop at the first capture boundary.  This prevents every later
        // document/form/control click handler from mutating a form, invoking
        // HTMLFormElement.prototype.submit(), or submitting another form.
        // It does not cancel the one native default action.
        event.stopImmediatePropagation();
        return;
      }

      const exactSubmit = Boolean(
        acceptedClick &&
        !acceptedSubmit &&
        event.isTrusted === true &&
        event.target === form &&
        event.submitter === submitter
      );
      const stillSafe = safetyFor();
      if (!exactSubmit || !Object.values(stillSafe).every(Boolean)) {
        event.preventDefault();
        event.stopImmediatePropagation();
        return;
      }
      acceptedSubmit = true;
      // Keep the proven native default action, but no later submit handler.
      event.stopImmediatePropagation();
    } catch (_) {
      // An unexpected event shape is never allowed to reach a native default.
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  };
  // The window capture listener runs before document/form/control handlers.
  // It permits exactly one pinned click and exactly one matching submit event;
  // every other click or submit is stopped and canceled while the guard lives.
  window.addEventListener("click", block, true);
  window.addEventListener("submit", block, true);
  return safety;
}
"""

FORM_CONTROL_INVENTORY_SCRIPT = r"""
(form, names) => {
  const allowed = new Set(names);
  const isIgnored = element => {
    const type = String(element.type || "").toLowerCase();
    return ["submit", "button", "reset", "image"].includes(type);
  };
  const named = Array.from(form.elements).filter(element => element && element.name && !isIgnored(element));
  const unexpected = named.filter(element => !allowed.has(element.name));
  const entries = names.map(name => {
    const elements = named.filter(element => element.name === name);
    const radios = elements.filter(
      element => String(element.type || "").toLowerCase() === "radio"
    );
    const checkedRadios = radios.filter(element => Boolean(element.checked));
    const radioGroup = radios.length === elements.length && radios.length > 0;
    const element = radioGroup
      ? (checkedRadios.length === 1 ? checkedRadios[0] : null)
      : (elements.length === 1 ? elements[0] : null);
    return {
      name,
      // A valid radio group is one semantic successful control even though it
      // has multiple DOM inputs. Zero marks an ambiguous/unchecked group.
      count: radioGroup ? (checkedRadios.length === 1 ? 1 : 0) : elements.length,
      tag: element ? String(element.tagName || "").toLowerCase() : "",
      type: element ? String(element.type || "").toLowerCase() : "",
      value: element ? String(element.value || "") : "",
      checked: element ? Boolean(element.checked) : false,
      disabled: element ? Boolean(element.disabled) : false
    };
  });
  return { unexpected_data_control_count: unexpected.length, entries };
}
"""

CANONICAL_ADVANCED_ROUTE_SCRIPT = r"""
(value) => {
  try {
    const raw = String(value);
    const authority = raw.match(/^https:\/\/([^/?#]*)/);
    if (!authority || authority[1] !== "oatd.org" || raw.includes("#")) return false;
    const location = new URL(raw);
    return location.protocol === "https:" && location.origin === "https://oatd.org" &&
      location.hostname === "oatd.org" && location.port === "" &&
      location.username === "" && location.password === "" &&
      ["/oatd/search", "/oatd/search-composer"].includes(location.pathname) &&
      location.hash === "";
  } catch (_) {
    return false;
  }
}
"""

POST_CLICK_STATE_SCRIPT = r"""
(payload) => {
  const normalize = value => String(value || "").replace(/[\s\u2009\u202f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const title = normalize(document.title);
  const sourceTitle = /\bOATD\b/i.test(title);
  const sourceHeading = Array.from(document.querySelectorAll("h3.pageHeader a.inheader"))
    .some(element => normalize(element.textContent) === "Open Access Theses and Dissertations");
  const errors = Array.from(document.querySelectorAll(
    ".error, .error_message, .message.error, [role='alert']"
  )).filter(visible).map(element => normalize(element.textContent)).join(" ");
  const challenge = (!sourceTitle && /just a moment|attention required|verify you are human/i.test(title)) ||
    Boolean(document.querySelector(
      "#challenge-running, #challenge-form, iframe[src*='challenges.cloudflare.com'], .cf-challenge-running"
    ));
  const busyPattern = /^(?:🟢\s*)?(?:server too busy(?:\s*[-:,.]\s*please slow down)?|please slow down)[.!]?$/i;
  const busy = busyPattern.test(errors) || (!sourceTitle && busyPattern.test(title));
  const access = /access denied|forbidden|captcha|enable javascript and cookies|log\s*in|sign\s*in|authentication required|verification required/i.test(errors) ||
    (!sourceTitle && /captcha|log\s*in|sign\s*in|authentication required|verification required/i.test(title));
  const syntaxError = /syntax|could not parse|invalid query|search error/i.test(errors);
  const canonicalRoute = (__CANONICAL_ADVANCED_ROUTE__)(window.location.href);
  const forms = Array.from(document.forms).filter(form => {
    try {
      const action = new URL(form.getAttribute("action") || "", document.baseURI);
      return action.protocol === "https:" && action.origin === "https://oatd.org" &&
        action.hostname === "oatd.org" && action.port === "" && action.username === "" &&
        action.password === "" && action.pathname === "/oatd/search-composer" &&
        action.search === "" && action.hash === "" && form.method.toLowerCase() === "get";
    } catch (_) {
      return false;
    }
  });
  const form = forms.length === 1 ? forms[0] : null;
  const boxes = form ? Array.from(form.querySelectorAll(
    "input[name='box1'], textarea[name='box1']"
  )) : [];
  const fields = form ? Array.from(form.querySelectorAll("select[name='field1']")) : [];
  const box = boxes.length === 1 ? boxes[0] : null;
  const field = fields.length === 1 ? fields[0] : null;
  const formReadbackExact = Boolean(box && field && String(box.value || "") === payload.query &&
    String(field.value || "") === payload.fieldValue);
  const reports = Array.from(document.querySelectorAll("p.matchesReport")).filter(visible);
  const report = reports.length === 1 ? reports[0] : null;
  const reportText = normalize(report && report.textContent);
  const expectedPrefix = `You searched for ${normalize(payload.query)}.`;
  const suffix = reportText.startsWith(expectedPrefix) ? reportText.slice(expectedPrefix.length).trim() : "";
  const range = suffix.match(/^Showing records\s+(\d+)\s*[\-–]\s*(\d+)\s+of\s+(\d+)\s+total matches?\.$/i);
  let resultKind = "unknown";
  let total = null;
  if (range) {
    resultKind = "range";
    total = Number(range[3]);
  } else if (/^One record found\.$/i.test(suffix)) {
    resultKind = "singleton";
    total = 1;
  } else if (/^No records match your search\.$/i.test(suffix)) {
    resultKind = "zero";
    total = 0;
  }
  const resultObserved = Boolean(canonicalRoute && sourceTitle && sourceHeading && formReadbackExact &&
    report && ["range", "singleton", "zero"].includes(resultKind));
  return {
    challenge,
    busy,
    access,
    syntax_error: syntaxError,
    canonical_advanced_route: canonicalRoute,
    source_identity: Boolean(sourceTitle && sourceHeading),
    form_readback_exact: formReadbackExact,
    result_kind: resultKind,
    source_total: total,
    result_observed: resultObserved
  };
}
""".replace("__CANONICAL_ADVANCED_ROUTE__", CANONICAL_ADVANCED_ROUTE_SCRIPT)


def compact(value: Any) -> str:
    """Normalize benign whitespace without retaining arbitrary source text."""
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


def _validate_busy_policy(retries: Any, delay: Any) -> tuple[int, float]:
    if (
        not isinstance(retries, int)
        or isinstance(retries, bool)
        or not 0 <= retries <= MAX_BUSY_RETRIES
    ):
        raise InputValidationError(
            f"--busy-retries must be an integer from 0 to {MAX_BUSY_RETRIES}"
        )
    parsed_delay = _finite_positive(delay, "--busy-retry-delay-seconds")
    if not MIN_BUSY_RETRY_DELAY_SECONDS <= parsed_delay <= MAX_BUSY_RETRY_DELAY_SECONDS:
        raise InputValidationError(
            "--busy-retry-delay-seconds is outside the finite safe range"
        )
    return retries, parsed_delay


def _validate_challenge_wait_policy(wait: Any, interval: Any) -> tuple[float, float]:
    """Validate the finite passive-only challenge policy."""
    parsed_wait = _finite_positive(wait, "--challenge-wait-seconds")
    if parsed_wait > MAX_CHALLENGE_WAIT_SECONDS:
        raise InputValidationError(
            "--challenge-wait-seconds exceeds the finite safe challenge bound"
        )
    parsed_interval = _finite_positive(
        interval, "--challenge-poll-interval-seconds"
    )
    if parsed_interval > parsed_wait:
        raise InputValidationError(
            "--challenge-poll-interval-seconds cannot exceed --challenge-wait-seconds"
        )
    return parsed_wait, parsed_interval


def _validate_pre_submit_busy_wait_policy(value: Any) -> float:
    """Validate the default-off exploration-only passive busy wait."""
    if isinstance(value, bool):
        raise InputValidationError(
            "--pre-submit-busy-wait-seconds must be zero or a finite nonnegative number"
        )
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(
            "--pre-submit-busy-wait-seconds must be zero or a finite nonnegative number"
        ) from error
    if not math.isfinite(parsed) or parsed < 0:
        raise InputValidationError(
            "--pre-submit-busy-wait-seconds must be zero or a finite nonnegative number"
        )
    if parsed > MAX_PRE_SUBMIT_BUSY_WAIT_SECONDS:
        raise InputValidationError(
            "--pre-submit-busy-wait-seconds exceeds the finite 180-second bound"
        )
    return parsed


def _validate_pre_submit_busy_poll_interval(value: Any) -> float:
    """Keep the exploration busy observation cadence fixed at two seconds."""
    parsed = _finite_positive(
        value, "--pre-submit-busy-poll-interval-seconds"
    )
    if parsed != DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS:
        raise InputValidationError(
            "--pre-submit-busy-poll-interval-seconds is fixed at 2 seconds"
        )
    return parsed


def _validate_create_only_path(value: Any, option: str) -> Path:
    """Validate a prospective create-only destination before source work."""
    if not compact(value):
        raise InputValidationError(f"{option} must be nonblank")
    candidate = Path(value).expanduser()
    if candidate.is_symlink():
        raise InputValidationError(f"{option} must not be a symlink")
    path = candidate.resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise InputValidationError(f"{option} must not already exist")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError(f"{option} parent must be a directory")
    return path


def validate_output_path(value: str) -> Path:
    """Validate a prospective create-only receipt destination."""
    return _validate_create_only_path(value, "--output-path")


def _derived_accounting_path(output_path: Path, suffix: str) -> Path:
    return output_path.with_name(output_path.name + suffix)


def reserve_output_path(path: Path) -> OutputReservation:
    """Atomically claim one create-only path before any source activity."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return OutputReservation(path=path, descriptor=os.open(path, flags, 0o600))


def reserve_ledger_path(
    path: Path, *, reservation_id: str
) -> OutputReservation:
    """Claim and mark the ledger inode while retaining its descriptor."""
    reservation = reserve_output_path(path)
    marker = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "status": "reserved",
        "reservation_id": reservation_id,
    }
    try:
        _write_all(
            reservation.descriptor,
            (json.dumps(marker, sort_keys=True) + "\n").encode("utf-8"),
        )
        os.fsync(reservation.descriptor)
    except Exception:
        descriptor = reservation.descriptor
        reservation.descriptor = -1
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    return reservation


def write_reserved_json(
    reservation: OutputReservation,
    payload: Mapping[str, Any],
    *,
    truncate: bool = False,
) -> None:
    """Write through a claimed descriptor without reopening its pathname."""
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("receipt reservation is no longer writable")
    reservation.descriptor = -1
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        if truncate:
            os.lseek(descriptor, 0, os.SEEK_SET)
            os.ftruncate(descriptor, 0)
            _write_all(descriptor, encoded)
            os.fsync(descriptor)
            os.close(descriptor)
        else:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(encoded)
    except Exception:
        # A concurrent winner can replace the name after O_EXCL creation.
        # Never unlink the current pathname while unwinding a failed write.
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def _validate_nonblank(value: str, option: str, maximum: int) -> str:
    if type(value) is not str or not compact(value) or len(value) > maximum:
        raise InputValidationError(
            f"{option} must be nonblank and within its safe size limit"
        )
    if "\x00" in value:
        raise InputValidationError(f"{option} contains an unsafe control character")
    return value


def validate_runtime_config(config: Any) -> ProbeConfig:
    """Revalidate direct API input before any Playwright lifecycle can start."""
    if not isinstance(config, ProbeConfig) or type(config.execute) is not bool:
        raise InputValidationError("runtime probe configuration is invalid")
    if not isinstance(config.output_path, Path):
        raise InputValidationError("runtime probe configuration is invalid")
    timeout = _finite_positive(config.timeout_seconds, "--timeout-seconds")
    interval = _finite_positive(config.poll_interval_seconds, "--poll-interval-seconds")
    if interval > timeout:
        raise InputValidationError(
            "--poll-interval-seconds cannot exceed --timeout-seconds"
        )
    retries, retry_delay = _validate_busy_policy(
        config.busy_retries, config.busy_retry_delay_seconds
    )
    challenge_wait, challenge_interval = _validate_challenge_wait_policy(
        config.challenge_wait_seconds, config.challenge_poll_interval_seconds
    )
    pre_submit_busy_wait = _validate_pre_submit_busy_wait_policy(
        config.pre_submit_busy_wait_seconds
    )
    output_path = validate_output_path(str(config.output_path))
    journal_path: Path | None = None
    ledger_path: Path | None = None
    if config.execute:
        journal_value = config.journal_path or _derived_accounting_path(
            output_path, ".journal.jsonl"
        )
        ledger_value = config.ledger_path or _derived_accounting_path(
            output_path, ".ledger.json"
        )
        journal_path = _validate_create_only_path(journal_value, "--journal-path")
        ledger_path = _validate_create_only_path(ledger_value, "--ledger-path")
        if len({output_path, journal_path, ledger_path}) != 3:
            raise InputValidationError(
                "--output-path, --journal-path, and --ledger-path must be distinct"
            )
    return ProbeConfig(
        execute=config.execute,
        cdp_url=validate_loopback_cdp_endpoint(config.cdp_url),
        query=_validate_nonblank(config.query, "--query", MAX_QUERY_CHARACTERS),
        field_label=_validate_nonblank(
            config.field_label, "--field-label", MAX_FIELD_LABEL_CHARACTERS
        ),
        timeout_seconds=timeout,
        poll_interval_seconds=interval,
        busy_retries=retries,
        busy_retry_delay_seconds=retry_delay,
        output_path=output_path,
        challenge_wait_seconds=challenge_wait,
        challenge_poll_interval_seconds=challenge_interval,
        pre_submit_busy_wait_seconds=pre_submit_busy_wait,
        journal_path=journal_path,
        ledger_path=ledger_path,
    )


def _milliseconds(seconds: float) -> int:
    return max(1, int(seconds * 1_000))


def _exact_nonnegative_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def _bool(value: Any) -> bool:
    return value is True


PRE_CLICK_SAFETY_FIELDS = (
    "current_canonical_composer_route",
    "source_identity",
    "exact_https_origin",
    "canonical_effective_get_action",
    "form_target_self",
    "submitter_no_override",
)


def pre_click_safety_from_payload(payload: Any) -> PreClickSafety:
    """Accept only the boolean proof allowlist from the final form check."""
    if not isinstance(payload, Mapping) or any(
        type(payload.get(name)) is not bool for name in PRE_CLICK_SAFETY_FIELDS
    ):
        raise ProbeAbort("pre_click_safety_projection_failed")
    return PreClickSafety(
        current_canonical_composer_route=payload["current_canonical_composer_route"],
        source_identity=payload["source_identity"],
        exact_https_origin=payload["exact_https_origin"],
        canonical_effective_get_action=payload["canonical_effective_get_action"],
        form_target_self=payload["form_target_self"],
        submitter_no_override=payload["submitter_no_override"],
    )


def inspect_form_payload(payload: Any) -> FormInspection:
    """Convert a browser projection to typed facts without returning source text."""
    if not isinstance(payload, Mapping):
        raise ProbeAbort("advanced_form_projection_failed")
    source_state = payload.get("source_state")
    if source_state in {"captcha", "login", "login_required", "verification"}:
        source_state = "access"
    if source_state not in {None, "challenge", "busy", "access", "syntax"}:
        raise ProbeAbort("advanced_form_projection_failed")
    field_value = payload.get("matching_field_value")
    if (
        not isinstance(field_value, str)
        or not field_value
        or len(field_value) > MAX_CONTROL_VALUE_CHARACTERS
        or any(character in field_value for character in ("\x00", "\r", "\n"))
    ):
        field_value = None
    return FormInspection(
        source_state=source_state,
        canonical_form_count=_exact_nonnegative_int(payload.get("canonical_form_count"))
        if _exact_nonnegative_int(payload.get("canonical_form_count")) is not None
        else -1,
        form_index=payload.get("form_index")
        if isinstance(payload.get("form_index"), int)
        and not isinstance(payload.get("form_index"), bool)
        else -1,
        method_get=_bool(payload.get("method_get")),
        box1_count=_exact_nonnegative_int(payload.get("box1_count"))
        if _exact_nonnegative_int(payload.get("box1_count")) is not None
        else -1,
        field1_count=_exact_nonnegative_int(payload.get("field1_count"))
        if _exact_nonnegative_int(payload.get("field1_count")) is not None
        else -1,
        matching_field_option_count=_exact_nonnegative_int(
            payload.get("matching_field_option_count")
        )
        if _exact_nonnegative_int(payload.get("matching_field_option_count"))
        is not None
        else -1,
        field_value=field_value,
        visible_native_submit_count=_exact_nonnegative_int(
            payload.get("visible_native_submit_count")
        )
        if _exact_nonnegative_int(payload.get("visible_native_submit_count"))
        is not None
        else -1,
    )


def _pre_submit_abort(inspection: FormInspection) -> str | None:
    if inspection.source_state is not None:
        return f"{inspection.source_state}_before_submission"
    if (
        inspection.canonical_form_count != 1
        or inspection.form_index < 0
        or not inspection.method_get
    ):
        return "canonical_advanced_form_not_observed"
    if inspection.box1_count != 1 or inspection.field1_count != 1:
        return "advanced_form_control_mapping_failed"
    if inspection.matching_field_option_count != 1 or inspection.field_value is None:
        return "advanced_field_mapping_failed"
    if inspection.visible_native_submit_count != 1:
        return "native_submit_control_not_unique"
    return None


async def open_visible_advanced_search(
    page: Any, *, timeout_seconds: float
) -> None:
    """Open OATD home and activate its visible advanced-search disclosure.

    OATD renders the disclosure label as split/static text rather than a
    dependable link/button accessibility role. Select the smallest visible
    element whose normalized descendant text contains the exact public label,
    then use Playwright's target-scoped visible click. Direct composer
    navigation is intentionally not a fallback because it frequently reaches
    the ordinary overloaded rendering.
    """
    timeout = _finite_positive(timeout_seconds, "advanced entry timeout")
    await page.goto(
        HOME_URL,
        wait_until="domcontentloaded",
        timeout=_milliseconds(timeout),
    )
    deadline = asyncio.get_running_loop().time() + timeout
    selected: Any | None = None
    while asyncio.get_running_loop().time() < deadline:
        candidates = page.locator(
            "xpath=//*[contains(translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            "'advanced search options')]"
        )
        visible_candidates: list[tuple[int, float, Any]] = []
        try:
            count = await candidates.count()
        except Exception:
            count = 0
        for index in range(count):
            item = candidates.nth(index)
            try:
                if not await item.is_visible():
                    continue
                text = compact(await item.inner_text()).casefold()
                if ADVANCED_ENTRY_LABEL.casefold() not in text:
                    continue
                box = await item.bounding_box()
                if not box or box.get("width", 0) <= 0 or box.get("height", 0) <= 0:
                    continue
                visible_candidates.append(
                    (len(text), float(box["width"]) * float(box["height"]), item)
                )
            except Exception:
                continue
        if visible_candidates:
            visible_candidates.sort(key=lambda value: (value[0], value[1]))
            best = visible_candidates[0]
            # An exact tie would make the target ambiguous; wait for the page
            # to settle rather than choosing by DOM position.
            if len(visible_candidates) == 1 or best[:2] != visible_candidates[1][:2]:
                selected = best[2]
                break
        await asyncio.sleep(DEFAULT_POLL_INTERVAL_SECONDS)
    if selected is None:
        raise ProbeAbort("advanced_form_control_mapping_failed")
    try:
        await selected.click(
            timeout=_milliseconds(max(0.001, deadline - asyncio.get_running_loop().time())),
            no_wait_after=True,
        )
    except Exception as error:
        raise ProbeAbort("advanced_form_control_mapping_failed") from error

    forms = page.locator(
        "form[action='/oatd/search-composer'], "
        "form[action='https://oatd.org/oatd/search-composer']"
    )
    while asyncio.get_running_loop().time() < deadline:
        try:
            if (
                await forms.count() == 1
                and await forms.first.is_visible()
            ):
                return
        except Exception:
            pass
        await asyncio.sleep(DEFAULT_POLL_INTERVAL_SECONDS)
    raise ProbeAbort("canonical_advanced_form_not_observed")


async def inspect_advanced_form(page: Any, field_label: str) -> FormInspection:
    """Read only the canonical form inventory from the owned page."""
    try:
        payload = await page.evaluate(ADVANCED_FORM_INSPECTION_SCRIPT, field_label)
    except Exception as error:
        raise ProbeAbort("advanced_form_projection_failed") from error
    return inspect_form_payload(payload)


def _safe_control_value(value: Any) -> str | None:
    if not isinstance(value, str) or len(value) > MAX_CONTROL_VALUE_CHARACTERS:
        return None
    if any(character in value for character in ("\x00", "\r", "\n")):
        return None
    return value


def retry_parameters_from_inventory(
    inventory: Any, *, query: str, field_value: str
) -> tuple[tuple[str, str], ...]:
    """Build a canonical retry query only from the prevalidated form controls."""
    if (
        not isinstance(inventory, Mapping)
        or inventory.get("unexpected_data_control_count") != 0
    ):
        raise ProbeAbort("advanced_retry_controls_not_prevalidated")
    entries = inventory.get("entries")
    if not isinstance(entries, list) or len(entries) != len(RETRY_CONTROL_NAMES):
        raise ProbeAbort("advanced_retry_controls_not_prevalidated")
    by_name: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if (
            not isinstance(entry, Mapping)
            or entry.get("name") not in RETRY_CONTROL_NAMES
        ):
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        name = entry["name"]
        if name in by_name:
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        by_name[name] = entry

    parameters: list[tuple[str, str]] = []
    for name in RETRY_CONTROL_NAMES:
        entry = by_name.get(name)
        if entry is None:
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        count = entry.get("count")
        if not isinstance(count, int) or isinstance(count, bool) or count not in {0, 1}:
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        if count == 0:
            if name in {"box1", "field1"}:
                raise ProbeAbort("advanced_retry_controls_not_prevalidated")
            continue
        if entry.get("disabled") is True:
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        if entry.get("tag") not in {"input", "select", "textarea"}:
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        control_type = entry.get("type")
        if not isinstance(control_type, str):
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        value = _safe_control_value(entry.get("value"))
        if value is None:
            raise ProbeAbort("advanced_retry_controls_not_prevalidated")
        if control_type in {"checkbox", "radio"} and entry.get("checked") is not True:
            continue
        if name == "box1" and value != query:
            raise ProbeAbort("advanced_control_readback_failed")
        if name == "field1" and value != field_value:
            raise ProbeAbort("advanced_control_readback_failed")
        parameters.append((name, value))

    names = {name for name, _ in parameters}
    if "box1" not in names or "field1" not in names:
        raise ProbeAbort("advanced_retry_controls_not_prevalidated")
    return tuple(parameters)


def canonical_retry_url(parameters: tuple[tuple[str, str], ...]) -> str:
    """Construct an in-memory canonical GET URL from prevalidated controls only."""
    if not parameters:
        raise ProbeAbort("advanced_retry_controls_not_prevalidated")
    return f"{ADVANCED_ACTION}?{urlencode(parameters)}"


async def prepare_native_submission(
    page: Any,
    inspection: FormInspection,
    query: str,
    *,
    deadline: float | None = None,
    clock: Callable[[], float] | None = None,
    before_native_click: Callable[[], None] | None = None,
) -> PreparedSubmission:
    """Fill, read back, and click exactly one visible native submit control."""
    if clock is None:
        clock = asyncio.get_running_loop().time
    if deadline is None:
        # Direct callers still get a bounded native action.  run_probe always
        # supplies its shared submission deadline instead.
        deadline = clock() + DEFAULT_TIMEOUT_SECONDS
    abort = _pre_submit_abort(inspection)
    if abort is not None:
        raise ProbeAbort(abort)
    assert inspection.field_value is not None  # narrowed by _pre_submit_abort
    try:
        forms = page.locator("form")
        if await forms.count() <= inspection.form_index:
            raise ProbeAbort("canonical_advanced_form_not_observed")
        form = forms.nth(inspection.form_index)
        self_check = await form.evaluate(FORM_SELF_CHECK_SCRIPT)
        if not (
            isinstance(self_check, Mapping)
            and self_check.get("canonical_form_count") == 1
            and self_check.get("selected_form_is_canonical") is True
        ):
            raise ProbeAbort("canonical_advanced_form_not_observed")
        box = form.locator("input[name='box1'], textarea[name='box1']")
        field = form.locator("select[name='field1']")
        if await box.count() != 1 or await field.count() != 1:
            raise ProbeAbort("advanced_form_control_mapping_failed")
        if not await box.is_visible() or not await field.is_visible():
            raise ProbeAbort("advanced_form_control_mapping_failed")
        await box.fill(query)
        await field.select_option(inspection.field_value)
        if (
            await box.input_value() != query
            or await field.input_value() != inspection.field_value
        ):
            raise ProbeAbort("advanced_control_readback_failed")
        inventory = await form.evaluate(
            FORM_CONTROL_INVENTORY_SCRIPT, list(RETRY_CONTROL_NAMES)
        )
        parameters = retry_parameters_from_inventory(
            inventory, query=query, field_value=inspection.field_value
        )
        native_submit = form.locator(NATIVE_SUBMIT_SELECTOR)
        submit_count = await native_submit.count()
        if submit_count != 1 or not await native_submit.first.is_visible():
            raise ProbeAbort("native_submit_control_not_unique")
        # Pin before any final safety projection. A Locator can otherwise
        # resolve a replacement submitter after a safe form was observed.
        submitter = await native_submit.first.element_handle()
        if submitter is None:
            raise ProbeAbort("native_submit_control_not_unique")
        safety = pre_click_safety_from_payload(
            await form.evaluate(PRE_CLICK_SAFETY_SCRIPT)
        )
        if not safety.verified:
            raise PreClickSafetyFailure(safety)
        safety = pre_click_safety_from_payload(
            await submitter.evaluate(NATIVE_SUBMIT_GUARD_SCRIPT)
        )
        if not safety.verified:
            raise PreClickSafetyFailure(safety)
        # The guard rechecks the pinned submitter and form at click/submit
        # default-action boundaries, so mutation cannot turn this into an
        # unsafe destination or a second form submission.  Do not let click
        # wait through an unbounded navigation before post-click observation.
        remaining = deadline - clock()
        if not math.isfinite(remaining) or remaining <= 0:
            raise ProbeAbort("native_submit_interaction_failed")
        try:
            if before_native_click is not None:
                # The durable callback runs immediately before the one native
                # click and must complete before source dispatch is possible.
                before_native_click()
            await asyncio.wait_for(
                submitter.click(timeout=_milliseconds(remaining), no_wait_after=True),
                timeout=remaining,
            )
        except asyncio.TimeoutError as error:
            raise ProbeAbort("native_submit_interaction_failed") from error
    except ProbeAbort:
        raise
    except Exception as error:
        raise ProbeAbort("native_submit_interaction_failed") from error
    return PreparedSubmission(
        retry_parameters=parameters,
        visible_native_submit_count=submit_count,
        pre_click_safety=safety,
    )


def post_click_state_from_payload(payload: Any) -> PostClickState:
    """Reject malformed state conservatively while keeping only safe fields."""
    if not isinstance(payload, Mapping):
        raise ProbeAbort("post_click_projection_failed")
    kind = payload.get("result_kind")
    if kind not in {"range", "singleton", "zero"}:
        kind = "unknown"
    total = _exact_nonnegative_int(payload.get("source_total"))
    if kind == "zero" and total != 0:
        kind = "unknown"
        total = None
    if kind == "singleton" and total != 1:
        kind = "unknown"
        total = None
    if kind == "range" and (total is None or total < 1):
        kind = "unknown"
        total = None
    return PostClickState(
        challenge=_bool(payload.get("challenge")),
        busy=_bool(payload.get("busy")),
        access=_bool(payload.get("access")),
        syntax_error=_bool(payload.get("syntax_error")),
        canonical_advanced_route=_bool(payload.get("canonical_advanced_route")),
        source_identity=_bool(payload.get("source_identity")),
        form_readback_exact=_bool(payload.get("form_readback_exact")),
        result_kind=kind,
        source_total=total,
        result_observed=(
            _bool(payload.get("result_observed"))
            and _bool(payload.get("canonical_advanced_route"))
            and _bool(payload.get("source_identity"))
            and _bool(payload.get("form_readback_exact"))
            and kind in {"range", "singleton", "zero"}
            and total is not None
        ),
    )


async def _observe_post_click(
    page: Any, query: str, field_value: str
) -> PostClickState:
    payload = await page.evaluate(
        POST_CLICK_STATE_SCRIPT, {"query": query, "fieldValue": field_value}
    )
    return post_click_state_from_payload(payload)


async def _sleep_to_deadline(
    deadline: float,
    interval: float,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> bool:
    """Sleep no longer than the shared deadline, including a custom sleeper."""
    remaining = deadline - clock()
    if remaining <= 0:
        return False
    try:
        await asyncio.wait_for(sleeper(min(interval, remaining)), timeout=remaining)
    except asyncio.TimeoutError:
        return False
    return clock() < deadline


async def wait_for_challenge_clear(
    page: Any,
    *,
    field_label: str,
    timeout_seconds: float = DEFAULT_CHALLENGE_WAIT_SECONDS,
    poll_interval_seconds: float = DEFAULT_CHALLENGE_POLL_INTERVAL_SECONDS,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    deadline: float | None = None,
    initial_inspection: FormInspection | None = None,
) -> ChallengeWaitOutcome:
    """Passively wait for one transient challenge on the same owned page.

    The helper performs DOM projections only.  It never clicks, reloads,
    navigates, submits, or invokes an access-control action.  Its challenge
    budget is separate from the busy reissue budget and is consumed only by
    this fixed-cadence observation window.
    """
    if clock is None:
        clock = asyncio.get_running_loop().time
    wait_seconds, poll_interval = _validate_challenge_wait_policy(
        timeout_seconds, poll_interval_seconds
    )
    started = clock()
    challenge_deadline = started + wait_seconds
    if deadline is not None:
        challenge_deadline = min(challenge_deadline, deadline)

    inspection = initial_inspection
    if inspection is None:
        remaining = challenge_deadline - clock()
        if remaining <= 0:
            return ChallengeWaitOutcome(
                inspection=None,
                classification="challenge_before_submission",
                polls=0,
                waited_seconds=max(0.0, clock() - started),
            )
        try:
            inspection = await asyncio.wait_for(
                inspect_advanced_form(page, field_label), timeout=remaining
            )
        except asyncio.TimeoutError:
            return ChallengeWaitOutcome(
                inspection=None,
                classification="challenge_before_submission",
                polls=0,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
            )

    if inspection.source_state != "challenge":
        return ChallengeWaitOutcome(
            inspection=inspection,
            classification=None,
            polls=0,
            waited_seconds=0.0,
        )

    polls = 0
    while True:
        if not await _sleep_to_deadline(
            challenge_deadline, poll_interval, clock, sleeper
        ):
            return ChallengeWaitOutcome(
                inspection=None,
                classification="challenge_before_submission",
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
            )
        remaining = challenge_deadline - clock()
        if remaining <= 0:
            return ChallengeWaitOutcome(
                inspection=None,
                classification="challenge_before_submission",
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
            )
        try:
            inspection = await asyncio.wait_for(
                inspect_advanced_form(page, field_label), timeout=remaining
            )
        except asyncio.TimeoutError:
            return ChallengeWaitOutcome(
                inspection=None,
                classification="challenge_before_submission",
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
            )
        polls += 1
        state = inspection.source_state
        if state == "challenge":
            continue
        if state == "access":
            classification = "access_before_submission"
        elif state == "busy":
            classification = "busy_before_submission"
        elif state == "syntax":
            classification = "syntax_before_submission"
        else:
            classification = None
        return ChallengeWaitOutcome(
            inspection=inspection if classification is None else None,
            classification=classification,
            polls=polls,
            waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
        )


def _pre_submit_busy_observation_state(inspection: FormInspection) -> str:
    """Map a form projection to a fixed safe journal state."""
    state = inspection.source_state
    return (
        state
        if type(state) is str and state in SAFE_PRE_SUBMIT_BUSY_OBSERVATION_STATES
        else "clear"
    )


async def wait_for_pre_submit_busy_clear(
    page: Any,
    *,
    field_label: str,
    timeout_seconds: float = MAX_PRE_SUBMIT_BUSY_WAIT_SECONDS,
    poll_interval_seconds: float = DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    deadline: float | None = None,
    initial_inspection: FormInspection | None = None,
    on_observation: Callable[[int, str, float], None] | None = None,
) -> PreSubmitBusyWaitOutcome:
    """Passively wait for ordinary pre-submit busy to clear on one owned page.

    This exploration-only window performs only the existing allowlisted DOM
    projection.  It never reloads, navigates, requests, submits, or reissues.
    A challenge or access transition is returned to the caller so the existing
    separate challenge/access policy remains in control.
    """
    if clock is None:
        clock = asyncio.get_running_loop().time
    wait_seconds = _validate_pre_submit_busy_wait_policy(timeout_seconds)
    poll_interval = _validate_pre_submit_busy_poll_interval(poll_interval_seconds)
    started = clock()
    busy_deadline = started + wait_seconds
    if deadline is not None:
        busy_deadline = min(busy_deadline, deadline)

    inspection = initial_inspection
    if inspection is None:
        remaining = busy_deadline - clock()
        if remaining <= 0:
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification="busy_before_submission",
                polls=0,
                waited_seconds=0.0,
                observations=(),
            )
        try:
            inspection = await asyncio.wait_for(
                inspect_advanced_form(page, field_label), timeout=remaining
            )
        except asyncio.TimeoutError:
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification="advanced_form_projection_failed",
                polls=0,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=(),
            )
        except ProbeAbort as error:
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification=safe_probe_abort_classification(error),
                polls=0,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=(),
            )

    if wait_seconds <= 0 or inspection.source_state != "busy":
        return PreSubmitBusyWaitOutcome(
            inspection=inspection,
            classification=None,
            polls=0,
            waited_seconds=0.0,
            observations=(),
        )

    observations: list[str] = []

    def note(current: FormInspection, poll: int) -> None:
        state = _pre_submit_busy_observation_state(current)
        observations.append(state)
        if on_observation is not None:
            on_observation(
                poll,
                state,
                min(wait_seconds, max(0.0, clock() - started)),
            )

    # The initial busy projection is journaled before any passive sleep.  No
    # O-001 operation has been marked possibly dispatched at this point.
    note(inspection, 0)
    polls = 0
    while True:
        if not await _sleep_to_deadline(
            busy_deadline, poll_interval, clock, sleeper
        ):
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification="busy_before_submission",
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=tuple(observations),
            )
        remaining = busy_deadline - clock()
        if remaining <= 0:
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification="busy_before_submission",
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=tuple(observations),
            )
        try:
            inspection = await asyncio.wait_for(
                inspect_advanced_form(page, field_label), timeout=remaining
            )
        except asyncio.TimeoutError:
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification="advanced_form_projection_failed",
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=tuple(observations),
            )
        except ProbeAbort as error:
            return PreSubmitBusyWaitOutcome(
                inspection=None,
                classification=safe_probe_abort_classification(error),
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=tuple(observations),
            )
        polls += 1
        note(inspection, polls)
        if inspection.source_state != "busy":
            return PreSubmitBusyWaitOutcome(
                inspection=inspection,
                classification=None,
                polls=polls,
                waited_seconds=min(wait_seconds, max(0.0, clock() - started)),
                observations=tuple(observations),
            )


def _outcome(
    classification: str,
    *,
    source_total: int | None,
    polls: int,
    budget: BusyRetryBudget,
) -> PostClickOutcome:
    return PostClickOutcome(
        classification=classification,
        source_total=source_total,
        polls=polls,
        busy_retries_performed=budget.attempted_retries,
        busy_recovery_attempts=budget.recovery_attempts,
        busy_retries_completed=budget.completed_retries,
    )


def _post_click_timeout(
    *,
    submission_observed: bool,
    polls: int,
    budget: BusyRetryBudget,
) -> PostClickOutcome:
    """Return the one fixed timeout outcome without retaining browser details."""
    return _outcome(
        "post_submit_state_timeout"
        if submission_observed
        else "submission_not_observed_timeout",
        source_total=None,
        polls=polls,
        budget=budget,
    )


def _observed_result_outcome(
    state: PostClickState, *, polls: int, budget: BusyRetryBudget
) -> PostClickOutcome:
    """Classify a terminal result before any busy/retry decision."""
    return _outcome(
        "zero_observed" if state.result_kind == "zero" else "result_observed",
        source_total=0 if state.result_kind == "zero" else state.source_total,
        polls=polls,
        budget=budget,
    )


async def wait_for_post_click_state(
    page: Any,
    *,
    query: str,
    field_value: str,
    retry_parameters: tuple[tuple[str, str], ...],
    timeout_seconds: float,
    poll_interval_seconds: float,
    busy_budget: BusyRetryBudget,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    deadline: float | None = None,
    before_busy_retry: Callable[[int, float], None] | None = None,
    after_busy_retry: Callable[[int], None] | None = None,
) -> PostClickOutcome:
    """Poll and retry under one absolute post-click deadline.

    Every evaluation, respectful wait, recheck, and retry navigation consumes
    the same deadline. A busy response is reissued only after a fresh safe
    recheck and never after that deadline has elapsed.  A caller that has
    already dispatched the native click supplies its original deadline so the
    post-click window cannot restart after click or navigation time.
    """
    if clock is None:
        clock = asyncio.get_running_loop().time
    if deadline is None:
        deadline = clock() + timeout_seconds
    polls = 0
    submission_observed = False
    challenge_seen = False

    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            if challenge_seen:
                return _outcome(
                    "challenge_after_submission",
                    source_total=None,
                    polls=polls,
                    budget=busy_budget,
                )
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        try:
            state = await asyncio.wait_for(
                _observe_post_click(page, query, field_value), timeout=remaining
            )
            polls += 1
        except asyncio.TimeoutError:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        except Exception:
            if clock() >= deadline:
                return _post_click_timeout(
                    submission_observed=submission_observed,
                    polls=polls,
                    budget=busy_budget,
                )
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue

        if clock() >= deadline:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        submission_observed = submission_observed or state.submission_observed
        if state.access:
            return _outcome(
                "access_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        if state.challenge:
            # A challenge is passive-only. It never reaches busy retry.
            challenge_seen = True
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue
        if state.syntax_error:
            return _outcome(
                "syntax_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        if state.result_observed:
            return _observed_result_outcome(state, polls=polls, budget=busy_budget)
        if not state.busy:
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue
        if not state.busy_retry_safe:
            return _outcome(
                "busy_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )

        delay = busy_budget.reserve_delay()
        if delay is None:
            return _outcome(
                "busy_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        # Respect the requested backoff only up to the common deadline.
        await _sleep_to_deadline(deadline, delay, clock, sleeper)
        remaining = deadline - clock()
        if remaining <= 0:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        try:
            rechecked = await asyncio.wait_for(
                _observe_post_click(page, query, field_value), timeout=remaining
            )
            polls += 1
        except asyncio.TimeoutError:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        except Exception:
            return _outcome(
                "busy_revalidation_failed",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )

        if clock() >= deadline:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        submission_observed = submission_observed or rechecked.submission_observed
        if rechecked.access:
            return _outcome(
                "access_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        if rechecked.challenge:
            challenge_seen = True
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue
        if rechecked.syntax_error:
            return _outcome(
                "syntax_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        # A terminal result wins even if an inconsistent busy marker remains.
        # In particular, it must not cause a canonical retry GET.
        if rechecked.result_observed:
            return _observed_result_outcome(rechecked, polls=polls, budget=busy_budget)
        if not rechecked.busy:
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue
        if not rechecked.busy_retry_safe:
            return _outcome(
                "busy_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )

        # Do not construct or dispatch an extra request once time has expired.
        remaining = deadline - clock()
        if remaining <= 0:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        retry_url = canonical_retry_url(retry_parameters)
        remaining = deadline - clock()
        if remaining <= 0:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        retry_number = busy_budget.attempted_retries + 1
        # The checkpoint callback runs before accounting and before the
        # awaitable goto call.  A guardian that stops the child after its
        # fsync is therefore represented conservatively as possibly dispatched.
        try:
            if before_busy_retry is not None:
                before_busy_retry(retry_number, delay)
            busy_budget.record_retry_attempt()
        except asyncio.CancelledError:
            raise
        except Exception:
            return _outcome(
                "busy_retry_checkpoint_failed",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        try:
            await asyncio.wait_for(
                page.goto(
                    retry_url,
                    wait_until="domcontentloaded",
                    timeout=_milliseconds(remaining),
                ),
                timeout=remaining,
            )
            busy_budget.record_retry_completion()
            if after_busy_retry is not None:
                after_busy_retry(retry_number)
        except asyncio.TimeoutError:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        except Exception:
            return _outcome(
                "busy_retry_navigation_failed",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
        if clock() >= deadline:
            return _post_click_timeout(
                submission_observed=submission_observed,
                polls=polls,
                budget=busy_budget,
            )
        continue


async def target_id_for(context: Any, page: Any) -> str | None:
    """Read one owned target ID transiently for equality/disappearance checks."""
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
    """Read every CDP target identity needed for exact baseline restoration."""
    session: Any | None = None
    try:
        session = await browser.new_browser_cdp_session()
        payload = await session.send("Target.getTargets")
        infos = payload.get("targetInfos") if isinstance(payload, Mapping) else None
        if not isinstance(infos, list):
            return None
        target_ids: list[str] = []
        for item in infos:
            if not isinstance(item, Mapping):
                return None
            target_type = item.get("type")
            target_id = item.get("targetId")
            if (
                type(target_type) is not str
                or not target_type
                or type(target_id) is not str
                or not target_id
            ):
                return None
            # Persistent workers and service workers are part of an exact
            # target baseline; do not silently filter them out.
            target_ids.append(target_id)
        if len(target_ids) != len(set(target_ids)):
            return None
        return frozenset(target_ids)
    except Exception:
        return None
    finally:
        if session is not None:
            try:
                await session.detach()
            except Exception:
                pass


async def _active_target_ids_to_deadline(
    browser: Any, deadline: float, clock: Callable[[], float]
) -> frozenset[str] | None:
    """Bound an inventory request while cleanup ownership remains live."""
    remaining = deadline - clock()
    if remaining <= 0:
        return None
    try:
        return await asyncio.wait_for(active_target_ids(browser), timeout=remaining)
    except asyncio.TimeoutError:
        return None


async def recover_owned_target_for_cleanup(
    browser: Any,
    context: Any,
    owned_page: Any,
    baseline_target_ids: frozenset[str],
    *,
    clock: Callable[[], float],
    sleeper: Callable[[float], Awaitable[None]],
) -> str | None:
    """Boundedly reprove a distinct target before closing an uncertain page."""
    deadline = clock() + CLEANUP_TIMEOUT_SECONDS
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return None
        try:
            target_id = await asyncio.wait_for(
                target_id_for(context, owned_page), timeout=remaining
            )
        except asyncio.TimeoutError:
            return None
        targets = await _active_target_ids_to_deadline(browser, deadline, clock)
        if (
            target_id is not None
            and target_id not in baseline_target_ids
            and targets is not None
            and target_id in targets
        ):
            return target_id
        if clock() >= deadline:
            return None
        await _sleep_to_deadline(
            deadline, CLEANUP_POLL_INTERVAL_SECONDS, clock, sleeper
        )


def baseline_pages_preserved(context: Any, baseline_pages: tuple[Any, ...]) -> bool:
    """Prove no baseline object was closed, replaced, or supplemented."""
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
        targets = await _active_target_ids_to_deadline(browser, deadline, clock)
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
        targets = await _active_target_ids_to_deadline(browser, deadline, clock)
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
    close_deadline = clock() + CLEANUP_TIMEOUT_SECONDS
    try:
        if not owned_page.is_closed():
            remaining = close_deadline - clock()
            if remaining <= 0:
                raise asyncio.TimeoutError
            await asyncio.wait_for(owned_page.close(), timeout=remaining)
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


def new_receipt(execute: bool) -> dict[str, Any]:
    """Create an output-safe receipt with no caller/source/browser identifiers."""
    return {
        "schema_version": "slr1-oatd-advanced-form-probe/v6",
        "mode": "source_action" if execute else "dry_run",
        "endpoint_class": "explicit_loopback_cdp",
        "operation": "one_owned_page_one_native_advanced_get_submission",
        "record_details_opened": False,
        "full_text_opened": False,
        "records_retained": 0,
        "retention_exclusions": [
            "url",
            "target_id",
            "html",
            "record",
            "full_text",
            "cookie",
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
        "submission": {
            "canonical_form_count": None,
            "canonical_get_form": False,
            "box1_count": None,
            "field1_count": None,
            "exact_field_mapping": False,
            "nonblank_control_readback": False,
            "visible_native_submit_count": None,
            "current_canonical_composer_route": False,
            "current_source_identity": False,
            "current_exact_https_origin": False,
            "canonical_effective_get_action": False,
            "form_target_self": False,
            "submitter_no_override": False,
            "pre_click_safety_verified": False,
            "native_submit_clicked": False,
            "challenge_wait_polls": 0,
            "challenge_wait_seconds": 0.0,
            "challenge_wait_outcome": "not_used",
            "pre_submit_busy_wait_polls": 0,
            "pre_submit_busy_wait_seconds": 0.0,
            "pre_submit_busy_wait_outcome": "not_used",
            "post_click_polls": 0,
            "busy_recovery_attempts": 0,
            "busy_retries_attempted": 0,
            "busy_retries_completed": 0,
            "busy_retries_performed": 0,
        },
        "challenge_wait_policy": {
            "maximum_seconds": DEFAULT_CHALLENGE_WAIT_SECONDS,
            "poll_interval_seconds": DEFAULT_CHALLENGE_POLL_INTERVAL_SECONDS,
            "polls": 0,
            "waited_seconds": 0.0,
            "outcome": "not_used",
        },
        "pre_submit_busy_wait_policy": {
            "enabled": False,
            "maximum_seconds": DEFAULT_PRE_SUBMIT_BUSY_WAIT_SECONDS,
            "poll_interval_seconds": DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS,
            "polls": 0,
            "waited_seconds": 0.0,
            "outcome": "not_used",
            "observations": [],
        },
        "result": {
            "status": "not_run",
            "classification": "not_run",
            "source_reported_total": None,
            "observations_accepted": False,
        },
        "accounting": {
            "journal_reserved": False,
            "ledger_reserved": False,
            "terminal_checkpoint_fsynced": False,
            "terminal_ledger_published": False,
            "possibly_dispatched": False,
        },
    }


def _boolean_pre_click_safety(value: Any) -> PreClickSafety:
    """Normalize even an unexpected internal error payload to safe booleans."""
    try:
        values = tuple(getattr(value, name) for name in PRE_CLICK_SAFETY_FIELDS)
    except Exception:
        values = ()
    if len(values) != len(PRE_CLICK_SAFETY_FIELDS) or any(
        type(item) is not bool for item in values
    ):
        return PreClickSafety(False, False, False, False, False, False)
    return PreClickSafety(*values)


def _apply_pre_click_safety(receipt: dict[str, Any], safety: Any) -> None:
    """Copy only final boolean submission-proof facts into the receipt."""
    safety = _boolean_pre_click_safety(safety)
    submission = receipt["submission"]
    submission["current_canonical_composer_route"] = safety.current_canonical_composer_route
    submission["current_source_identity"] = safety.source_identity
    submission["current_exact_https_origin"] = safety.exact_https_origin
    submission["canonical_effective_get_action"] = safety.canonical_effective_get_action
    submission["form_target_self"] = safety.form_target_self
    submission["submitter_no_override"] = safety.submitter_no_override
    submission["pre_click_safety_verified"] = safety.verified


def _set_result(
    receipt: dict[str, Any], classification: str, source_total: int | None = None
) -> None:
    receipt["result"] = {
        "status": "observed"
        if classification in {"result_observed", "zero_observed"}
        else "blocked",
        "classification": classification,
        "source_reported_total": source_total,
        "observations_accepted": classification in {"result_observed", "zero_observed"},
    }


def _record_form_inspection(receipt: dict[str, Any], inspection: FormInspection) -> None:
    """Copy only fixed form-count facts into the safe receipt."""
    submission = receipt["submission"]
    submission["canonical_form_count"] = inspection.canonical_form_count
    submission["canonical_get_form"] = bool(
        inspection.canonical_form_count == 1 and inspection.method_get
    )
    submission["box1_count"] = inspection.box1_count
    submission["field1_count"] = inspection.field1_count
    submission["exact_field_mapping"] = bool(
        inspection.matching_field_option_count == 1
        and inspection.field_value is not None
    )
    submission["visible_native_submit_count"] = (
        inspection.visible_native_submit_count
    )


def _record_challenge_wait(
    receipt: dict[str, Any],
    outcome: ChallengeWaitOutcome,
    *,
    maximum_seconds: float,
    poll_interval_seconds: float,
) -> None:
    """Keep passive challenge polls distinct from busy source reissues."""
    policy = receipt["challenge_wait_policy"]
    policy["maximum_seconds"] = maximum_seconds
    policy["poll_interval_seconds"] = poll_interval_seconds
    policy["polls"] = outcome.polls
    policy["waited_seconds"] = outcome.waited_seconds
    policy["outcome"] = outcome.classification or "cleared"
    submission = receipt["submission"]
    submission["challenge_wait_polls"] = outcome.polls
    submission["challenge_wait_seconds"] = outcome.waited_seconds
    submission["challenge_wait_outcome"] = outcome.classification or "cleared"


def _record_pre_submit_busy_wait(
    receipt: dict[str, Any],
    outcome: PreSubmitBusyWaitOutcome,
    *,
    maximum_seconds: float,
) -> None:
    """Record only fixed safe facts from the exploration busy window."""
    policy = receipt["pre_submit_busy_wait_policy"]
    policy["enabled"] = maximum_seconds > 0
    policy["maximum_seconds"] = maximum_seconds
    policy["poll_interval_seconds"] = DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS
    policy["polls"] = outcome.polls
    policy["waited_seconds"] = outcome.waited_seconds
    policy["observations"] = list(outcome.observations)
    if outcome.classification is not None:
        label = outcome.classification
    elif not outcome.observations:
        label = "not_needed"
    elif outcome.inspection is not None and outcome.inspection.source_state is None:
        label = "cleared"
    else:
        label = "transitioned"
    policy["outcome"] = label
    submission = receipt["submission"]
    submission["pre_submit_busy_wait_polls"] = outcome.polls
    submission["pre_submit_busy_wait_seconds"] = outcome.waited_seconds
    submission["pre_submit_busy_wait_outcome"] = label


def _new_accounting_operations() -> list[dict[str, Any]]:
    return [
        dict(operation)
        for operation in ExecutionAccounting.create(
            "uninitialized", DEFAULT_BUSY_RETRY_DELAY_SECONDS
        ).operations
    ]


def _read_journal_checkpoints(path: Path) -> tuple[list[dict[str, Any]], bool]:
    """Read only complete, schema-valid journal lines; ignore a torn tail."""
    try:
        with path.open("rb") as handle:
            raw_lines = handle.readlines()
    except OSError:
        return [], False
    records: list[dict[str, Any]] = []
    for raw in raw_lines:
        try:
            record = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            break
        if not isinstance(record, Mapping):
            break
        if record.get("schema_version") != JOURNAL_SCHEMA_VERSION:
            continue
        if not isinstance(record.get("snapshot"), Mapping):
            continue
        sequence = record.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            continue
        records.append(dict(record))
    return records, bool(records)


def _merge_journal_accounting(
    records: list[dict[str, Any]],
) -> tuple[ExecutionAccounting, Mapping[str, Any] | None]:
    """Merge durable intent monotonically so interruption cannot erase work."""
    reservation_id = "unknown"
    if records and type(records[0].get("reservation_id")) is str:
        reservation_id = records[0]["reservation_id"][:256]
    accounting = ExecutionAccounting.create(
        reservation_id, DEFAULT_BUSY_RETRY_DELAY_SECONDS
    )
    by_id = {operation["operation_id"]: operation for operation in accounting.operations}
    observations_by_poll: dict[int, dict[str, Any]] = {}
    terminal: Mapping[str, Any] | None = None
    for record in records:
        record_id = record.get("reservation_id")
        if reservation_id == "unknown" and type(record_id) is str:
            reservation_id = record_id[:256]
            accounting.reservation_id = reservation_id
        snapshot = record.get("snapshot")
        if not isinstance(snapshot, Mapping):
            continue
        policy = snapshot.get("busy_retry_policy")
        if isinstance(policy, Mapping):
            delays = policy.get("wait_delays_seconds")
            if isinstance(delays, list) and len(delays) == MAX_BUSY_RETRIES:
                safe_delays: list[float] = []
                for delay in delays:
                    if isinstance(delay, (int, float)) and not isinstance(delay, bool):
                        parsed = float(delay)
                        if math.isfinite(parsed) and 0 < parsed <= MAX_BUSY_RETRY_DELAY_SECONDS:
                            safe_delays.append(parsed)
                if len(safe_delays) == MAX_BUSY_RETRIES:
                    accounting.busy_retry_delays = safe_delays
        operations = snapshot.get("operations")
        if isinstance(operations, list):
            for candidate in operations:
                if not isinstance(candidate, Mapping):
                    continue
                operation = by_id.get(candidate.get("operation_id"))
                if operation is None:
                    continue
                if candidate.get("kind") in {"native_submit", "busy_reissue"}:
                    operation["kind"] = candidate["kind"]
                if candidate.get("possibly_dispatched") is True:
                    operation["possibly_dispatched"] = True
                    operation["attempted"] = True
                    operation["dispatch_status"] = "possibly_dispatched"
                if candidate.get("dispatched") is True:
                    operation["dispatched"] = True
                    operation["possibly_dispatched"] = True
                    operation["attempted"] = True
                    operation["dispatch_status"] = "dispatched"
                if candidate.get("completed") is True:
                    operation["completed"] = True
                    operation["dispatched"] = True
                    operation["possibly_dispatched"] = True
                    operation["attempted"] = True
                    operation["dispatch_status"] = "dispatched"
                wait_seconds = candidate.get("wait_seconds")
                if isinstance(wait_seconds, (int, float)) and not isinstance(
                    wait_seconds, bool
                ):
                    parsed_wait = float(wait_seconds)
                    if math.isfinite(parsed_wait) and 0 < parsed_wait <= MAX_BUSY_RETRY_DELAY_SECONDS:
                        operation["wait_seconds"] = parsed_wait
        observations = snapshot.get("pre_submit_busy_observations")
        if isinstance(observations, list):
            for candidate in observations:
                if not isinstance(candidate, Mapping):
                    continue
                poll = candidate.get("poll")
                state = candidate.get("state")
                waited_seconds = candidate.get("waited_seconds")
                if (
                    type(poll) is not int
                    or not 0 <= poll < MAX_PRE_SUBMIT_BUSY_OBSERVATIONS
                    or type(state) is not str
                    or state not in SAFE_PRE_SUBMIT_BUSY_OBSERVATION_STATES
                    or isinstance(waited_seconds, bool)
                    or not isinstance(waited_seconds, (int, float))
                ):
                    continue
                parsed_waited = float(waited_seconds)
                if not math.isfinite(parsed_waited) or not 0 <= parsed_waited <= MAX_PRE_SUBMIT_BUSY_WAIT_SECONDS:
                    continue
                observations_by_poll[poll] = {
                    "poll": poll,
                    "state": state,
                    "waited_seconds": parsed_waited,
                }
        candidate_terminal = snapshot.get("terminal")
        if isinstance(candidate_terminal, Mapping) and candidate_terminal.get(
            "terminal_checkpoint"
        ) is True:
            terminal = dict(candidate_terminal)
    accounting.pre_submit_busy_observations = [
        observations_by_poll[poll] for poll in sorted(observations_by_poll)
    ]
    accounting.reservation_id = reservation_id
    return accounting, terminal


def _read_existing_json(path: Path) -> Mapping[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def _write_existing_reserved_json(
    path: Path, payload: Mapping[str, Any], *, reservation_id: str
) -> None:
    """Fill a previously reserved ledger inode without creating a replacement."""
    if path.is_symlink() or not path.is_file():
        raise OSError("ledger reservation is not a regular file")
    existing = _read_existing_json(path)
    if existing is not None:
        if existing.get("status") == "terminal":
            if existing.get("schema_version") != LEDGER_SCHEMA_VERSION:
                raise OSError("ledger has an unexpected schema")
            return
        if existing.get("status") != "reserved" or existing.get(
            "reservation_id"
        ) != reservation_id:
            raise OSError("ledger reservation does not match the journal")
    elif path.stat().st_size != 0:
        raise OSError("ledger reservation is not recoverable")
    flags = os.O_WRONLY | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        _write_all(
            descriptor,
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def finalize_ledger(journal_path: Path, ledger_path: Path) -> dict[str, Any]:
    """Reconstruct a terminal accounting ledger without opening a browser."""
    journal_path = Path(journal_path).expanduser()
    ledger_path = Path(ledger_path).expanduser()
    if journal_path.is_symlink() or ledger_path.is_symlink():
        raise OSError("finalizer paths must not be symlinks")
    existing_terminal = _read_existing_json(ledger_path) if ledger_path.exists() else None
    if (
        isinstance(existing_terminal, Mapping)
        and existing_terminal.get("schema_version") == LEDGER_SCHEMA_VERSION
        and existing_terminal.get("status") == "terminal"
    ):
        return dict(existing_terminal)
    records, journal_available = _read_journal_checkpoints(journal_path)
    accounting, terminal = _merge_journal_accounting(records)
    existing_ledger = _read_existing_json(ledger_path) if ledger_path.exists() else None
    if (
        accounting.reservation_id == "unknown"
        and isinstance(existing_ledger, Mapping)
        and type(existing_ledger.get("reservation_id")) is str
    ):
        accounting.reservation_id = existing_ledger["reservation_id"][:256]
    incomplete_possible = any(
        operation["possibly_dispatched"] and not operation["completed"]
        for operation in accounting.operations
    )
    durable_terminal = bool(terminal is not None and not incomplete_possible)
    if durable_terminal and isinstance(terminal, Mapping):
        classification = _safe_accounting_classification(
            terminal.get("classification"), "guardian_interrupted"
        )
        source_total = _safe_accounting_total(terminal.get("source_total"))
        if classification not in {"result_observed", "zero_observed"}:
            source_total = None
        interrupted = False
    else:
        classification = (
            "guardian_interrupted" if journal_available else "journal_unavailable"
        )
        source_total = None
        interrupted = True
    payload = accounting.terminal_ledger(
        classification,
        source_total,
        interrupted=interrupted,
        recovered=True,
    )
    payload["terminal"]["recovery_basis"] = (
        "durable_terminal_checkpoint" if durable_terminal else "last_safe_checkpoint"
    )
    payload["terminal"]["journal_checkpoint_count"] = len(records)
    if not ledger_path.exists():
        reservation = reserve_output_path(ledger_path)
        write_reserved_json(reservation, payload, truncate=True)
    else:
        _write_existing_reserved_json(
            ledger_path, payload, reservation_id=accounting.reservation_id
        )
    return payload


async def run_probe(
    config: ProbeConfig,
    *,
    playwright_factory: Callable[[], Any] | None = None,
    advanced_entry_opener: Callable[[Any, float], Awaitable[None]] | None = None,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> tuple[int, dict[str, Any]]:
    """Reserve a receipt and run the opt-in action with live cleanup."""
    try:
        config = validate_runtime_config(config)
    except Exception:
        # Direct ProbeConfig construction cannot bypass pre-connection policy.
        receipt = new_receipt(False)
        _set_result(receipt, "invalid_runtime_config")
        return 1, receipt

    receipt = new_receipt(config.execute)
    # Record the prospective policy even when the page is not challenged; this
    # makes a passive wait auditable without conflating it with busy reissues.
    receipt["challenge_wait_policy"]["maximum_seconds"] = (
        config.challenge_wait_seconds
    )
    receipt["challenge_wait_policy"]["poll_interval_seconds"] = (
        config.challenge_poll_interval_seconds
    )
    receipt["pre_submit_busy_wait_policy"]["enabled"] = (
        config.pre_submit_busy_wait_seconds > 0
    )
    receipt["pre_submit_busy_wait_policy"]["maximum_seconds"] = (
        config.pre_submit_busy_wait_seconds
    )
    receipt["pre_submit_busy_wait_policy"]["poll_interval_seconds"] = (
        DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS
    )
    reservation: OutputReservation | None = None
    journal_reservation: OutputReservation | None = None
    ledger_reservation: OutputReservation | None = None
    journal: DurableJournal | None = None
    accounting: ExecutionAccounting | None = None
    try:
        # Claim every execute-mode artifact before importing or constructing
        # Playwright.  A collision therefore prevents source activity rather
        # than merely preventing the final write.
        reservation = reserve_output_path(config.output_path)
        if config.execute:
            assert config.journal_path is not None
            assert config.ledger_path is not None
            reservation_id = secrets.token_hex(16)
            journal_reservation = reserve_output_path(config.journal_path)
            ledger_reservation = reserve_ledger_path(
                config.ledger_path, reservation_id=reservation_id
            )
            journal = DurableJournal(journal_reservation, reservation_id)
            accounting = ExecutionAccounting.create(
                reservation_id, config.busy_retry_delay_seconds
            )
            receipt["accounting"]["journal_reserved"] = True
            receipt["accounting"]["ledger_reserved"] = True
            accounting.checkpoint(journal, "reserved")
    except Exception:
        for held in (journal_reservation, ledger_reservation):
            if held is not None and held.descriptor >= 0:
                try:
                    os.close(held.descriptor)
                except OSError:
                    pass
                held.descriptor = -1
        if reservation is not None and reservation.descriptor >= 0:
            _set_result(
                receipt,
                "accounting_reservation_failed"
                if config.execute
                else "output_reservation_failed",
            )
            try:
                write_reserved_json(reservation, receipt)
            except Exception:
                pass
        else:
            _set_result(receipt, "output_reservation_failed")
        return 1, receipt

    browser: Any | None = None
    context: Any | None = None
    owned_page: Any | None = None
    owned_page_distinct = False
    owned_page_safe_to_close = False
    post_create_inventory_failed = False
    post_create_reverification_required = False
    owned_target_id: str | None = None
    baseline_pages: tuple[Any, ...] = ()
    baseline_target_ids: frozenset[str] | None = None
    primary_classification = "browser_connection_failed"
    primary_total: int | None = None
    interrupted = False
    output_write_failed = False
    ledger_write_failed = False

    def journal_pre_submit_busy_observation(
        poll: int, state: str, waited_seconds: float
    ) -> None:
        policy = receipt["pre_submit_busy_wait_policy"]
        policy["observations"].append(state)
        policy["polls"] = poll
        policy["waited_seconds"] = waited_seconds
        policy["outcome"] = "observing"
        submission = receipt["submission"]
        submission["pre_submit_busy_wait_polls"] = poll
        submission["pre_submit_busy_wait_seconds"] = waited_seconds
        submission["pre_submit_busy_wait_outcome"] = "observing"
        if accounting is None or journal is None:
            return
        try:
            accounting.record_pre_submit_busy_observation(
                journal,
                poll=poll,
                state=state,
                waited_seconds=waited_seconds,
            )
        except Exception as error:
            raise ProbeAbort("accounting_checkpoint_failed") from error

    try:
        if not config.execute:
            primary_classification = "dry_run"
        else:
            if clock is None:
                clock = asyncio.get_running_loop().time
            if playwright_factory is None:
                from playwright.async_api import async_playwright

                playwright_factory = async_playwright

            try:
                # Cleanup remains inside this live browser context so target
                # disappearance and every target-type baseline are observable.
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
                        receipt["ownership"]["baseline_page_count"] = len(
                            baseline_pages
                        )
                        baseline_target_ids = await active_target_ids(browser)
                        if baseline_target_ids is None:
                            raise ProbeAbort("baseline_target_inventory_unavailable")

                        owned_page = await context.new_page()
                        receipt["ownership"]["owned_page_created"] = True
                        owned_page_distinct = all(
                            owned_page is not baseline for baseline in baseline_pages
                        )
                        receipt["ownership"]["owned_page_distinct_from_baseline"] = (
                            owned_page_distinct
                        )
                        if not owned_page_distinct:
                            raise ProbeAbort("owned_page_not_distinct")

                        post_create_timeout = min(
                            config.timeout_seconds, CLEANUP_TIMEOUT_SECONDS
                        )
                        try:
                            post_create_target_ids = await asyncio.wait_for(
                                active_target_ids(browser), timeout=post_create_timeout
                            )
                        except asyncio.TimeoutError:
                            post_create_target_ids = None
                        post_create_inventory_failed = post_create_target_ids is None
                        try:
                            owned_target_id = await asyncio.wait_for(
                                target_id_for(context, owned_page),
                                timeout=post_create_timeout,
                            )
                        except asyncio.TimeoutError:
                            owned_target_id = None
                        post_create_reverification_required = bool(
                            post_create_inventory_failed or owned_target_id is None
                        )
                        owned_target_is_new = bool(
                            owned_target_id is not None
                            and post_create_target_ids is not None
                            and owned_target_id in post_create_target_ids
                            and owned_target_id not in baseline_target_ids
                        )
                        # A target proven non-baseline is safe to close even if
                        # concurrent target mutation blocks the home navigation.
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

                        if advanced_entry_opener is None:
                            await open_visible_advanced_search(
                                owned_page, timeout_seconds=config.timeout_seconds
                            )
                        else:
                            await advanced_entry_opener(
                                owned_page, config.timeout_seconds
                            )
                        # The challenge wait, native click, and all post-click
                        # work share one absolute operation deadline.  A
                        # cleared challenge therefore cannot restart the
                        # submission budget.
                        submission_deadline = clock() + config.timeout_seconds
                        inspection = await inspect_advanced_form(
                            owned_page, config.field_label
                        )
                        submission = receipt["submission"]
                        _record_form_inspection(receipt, inspection)
                        if (
                            inspection.source_state == "busy"
                            and config.pre_submit_busy_wait_seconds > 0
                        ):
                            pre_submit_busy_wait = (
                                await wait_for_pre_submit_busy_clear(
                                    owned_page,
                                    field_label=config.field_label,
                                    timeout_seconds=(
                                        config.pre_submit_busy_wait_seconds
                                    ),
                                    poll_interval_seconds=(
                                        DEFAULT_PRE_SUBMIT_BUSY_POLL_INTERVAL_SECONDS
                                    ),
                                    clock=clock,
                                    sleeper=sleeper,
                                    deadline=submission_deadline,
                                    initial_inspection=inspection,
                                    on_observation=(
                                        journal_pre_submit_busy_observation
                                    ),
                                )
                            )
                            _record_pre_submit_busy_wait(
                                receipt,
                                pre_submit_busy_wait,
                                maximum_seconds=config.pre_submit_busy_wait_seconds,
                            )
                            if pre_submit_busy_wait.classification is not None:
                                raise ProbeAbort(
                                    pre_submit_busy_wait.classification
                                )
                            if pre_submit_busy_wait.inspection is None:
                                raise ProbeAbort("busy_before_submission")
                            inspection = pre_submit_busy_wait.inspection
                            _record_form_inspection(receipt, inspection)

                        # A busy page that becomes a challenge enters the
                        # existing separate 30-second challenge policy; an
                        # access transition remains an immediate terminal stop.
                        if inspection.source_state == "challenge":
                            challenge_wait = await wait_for_challenge_clear(
                                owned_page,
                                field_label=config.field_label,
                                timeout_seconds=config.challenge_wait_seconds,
                                poll_interval_seconds=(
                                    config.challenge_poll_interval_seconds
                                ),
                                clock=clock,
                                sleeper=sleeper,
                                deadline=submission_deadline,
                                initial_inspection=inspection,
                            )
                            _record_challenge_wait(
                                receipt,
                                challenge_wait,
                                maximum_seconds=config.challenge_wait_seconds,
                                poll_interval_seconds=(
                                    config.challenge_poll_interval_seconds
                                ),
                            )
                            if challenge_wait.classification is not None:
                                raise ProbeAbort(challenge_wait.classification)
                            if challenge_wait.inspection is None:
                                raise ProbeAbort("challenge_before_submission")
                            inspection = challenge_wait.inspection
                            _record_form_inspection(receipt, inspection)

                        pre_submit_abort = _pre_submit_abort(inspection)
                        if pre_submit_abort is not None:
                            raise ProbeAbort(pre_submit_abort)

                        remaining = submission_deadline - clock()
                        if remaining <= 0:
                            raise ProbeAbort("native_submit_interaction_failed")
                        try:
                            prepared = await asyncio.wait_for(
                                prepare_native_submission(
                                    owned_page,
                                    inspection,
                                    config.query,
                                    deadline=submission_deadline,
                                    clock=clock,
                                    before_native_click=(
                                        (lambda: accounting.before_native_click(journal))
                                        if accounting is not None and journal is not None
                                        else None
                                    ),
                                ),
                                timeout=remaining,
                            )
                        except asyncio.TimeoutError as error:
                            raise ProbeAbort(
                                "native_submit_interaction_failed"
                            ) from error
                        if accounting is not None and journal is not None:
                            accounting.after_native_click(journal)
                        submission["nonblank_control_readback"] = True
                        submission["visible_native_submit_count"] = (
                            prepared.visible_native_submit_count
                        )
                        _apply_pre_click_safety(receipt, prepared.pre_click_safety)
                        submission["native_submit_clicked"] = True
                        assert inspection.field_value is not None
                        outcome = await wait_for_post_click_state(
                            owned_page,
                            query=config.query,
                            field_value=inspection.field_value,
                            retry_parameters=prepared.retry_parameters,
                            timeout_seconds=config.timeout_seconds,
                            poll_interval_seconds=config.poll_interval_seconds,
                            busy_budget=BusyRetryBudget(
                                max_retries=config.busy_retries,
                                initial_delay_seconds=config.busy_retry_delay_seconds,
                            ),
                            clock=clock,
                            sleeper=sleeper,
                            deadline=submission_deadline,
                            before_busy_retry=(
                                (lambda retry_number, delay: accounting.before_busy_retry(
                                    journal, retry_number, delay
                                ))
                                if accounting is not None and journal is not None
                                else None
                            ),
                            after_busy_retry=(
                                (lambda retry_number: accounting.after_busy_retry(
                                    journal, retry_number
                                ))
                                if accounting is not None and journal is not None
                                else None
                            ),
                        )
                        submission["post_click_polls"] = outcome.polls
                        submission["busy_recovery_attempts"] = (
                            outcome.busy_recovery_attempts
                        )
                        submission["busy_retries_attempted"] = (
                            outcome.busy_retries_attempted
                        )
                        submission["busy_retries_completed"] = (
                            outcome.busy_retries_completed
                        )
                        submission["busy_retries_performed"] = (
                            outcome.busy_retries_performed
                        )
                        primary_classification = outcome.classification
                        primary_total = outcome.source_total
                    except PreClickSafetyFailure as error:
                        _apply_pre_click_safety(receipt, error.safety)
                        primary_classification = "pre_click_safety_not_verified"
                    except ProbeAbort as error:
                        primary_classification = safe_probe_abort_classification(error)
                    except asyncio.CancelledError:
                        interrupted = True
                        primary_classification = "guardian_interrupted"
                        primary_total = None
                    except Exception:
                        # Do not serialize browser exceptions: they can carry
                        # source URLs or query values in an implementation.
                        primary_classification = "owned_page_operation_failed"
                    finally:
                        can_attempt_cleanup = bool(
                            owned_page is not None
                            and owned_page_distinct
                            and browser is not None
                            and context is not None
                            and baseline_target_ids is not None
                        )
                        if can_attempt_cleanup and post_create_reverification_required:
                            # An unavailable post-create proof must not strand
                            # a distinct page. Reprove it boundedly or hand off.
                            if not owned_page_safe_to_close:
                                try:
                                    recovered_target_id = (
                                        await recover_owned_target_for_cleanup(
                                            browser,
                                            context,
                                            owned_page,
                                            baseline_target_ids,
                                            clock=clock,
                                            sleeper=sleeper,
                                        )
                                    )
                                except Exception:
                                    recovered_target_id = None
                                if recovered_target_id is None:
                                    receipt["ownership"]["baseline_pages_preserved"] = (
                                        baseline_pages_preserved(
                                            context, baseline_pages
                                        )
                                    )
                                    receipt["ownership"][
                                        "baseline_target_set_preserved"
                                    ] = False
                                    primary_classification = (
                                        "owned_page_cleanup_handoff_required"
                                    )
                                    primary_total = None
                                else:
                                    owned_target_id = recovered_target_id
                                    owned_page_safe_to_close = True
                        if can_attempt_cleanup and owned_page_safe_to_close:
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
                                    primary_classification = (
                                        "cleanup_verification_failed"
                                    )
                                    primary_total = None
                            except Exception:
                                receipt["ownership"]["owned_page_close_attempted"] = (
                                    True
                                )
                                receipt["ownership"]["baseline_pages_preserved"] = False
                                receipt["ownership"][
                                    "baseline_target_set_preserved"
                                ] = False
                                primary_classification = "cleanup_verification_failed"
                                primary_total = None
            except asyncio.CancelledError:
                interrupted = True
                primary_classification = "guardian_interrupted"
                primary_total = None
            except Exception:
                # Do not downgrade a proven cleanup failure or explicit
                # handoff to a transport category if Playwright stops poorly.
                if primary_classification not in {
                    "cleanup_verification_failed",
                    "owned_page_cleanup_handoff_required",
                }:
                    primary_classification = "browser_connection_failed"
                    primary_total = None
    finally:
        if config.execute and accounting is not None and journal is not None:
            try:
                accounting.checkpoint(
                    journal,
                    "terminal",
                    classification=primary_classification,
                    source_total=primary_total,
                    interrupted=interrupted,
                    terminal=True,
                )
                receipt["accounting"]["terminal_checkpoint_fsynced"] = True
            except Exception:
                primary_classification = "accounting_checkpoint_failed"
                primary_total = None
            receipt["accounting"]["possibly_dispatched"] = any(
                operation["possibly_dispatched"]
                for operation in accounting.operations
            )
            if ledger_reservation is not None:
                try:
                    ledger_payload = accounting.terminal_ledger(
                        primary_classification,
                        primary_total,
                        interrupted=interrupted,
                    )
                    write_reserved_json(
                        ledger_reservation, ledger_payload, truncate=True
                    )
                    receipt["accounting"]["terminal_ledger_published"] = True
                except Exception:
                    ledger_write_failed = True
                    primary_classification = "accounting_publication_failed"
                    primary_total = None
        _set_result(receipt, primary_classification, primary_total)
        if not config.execute:
            receipt["result"]["status"] = "not_run"
        if reservation is not None:
            try:
                write_reserved_json(reservation, receipt)
            except Exception:
                output_write_failed = True
        if journal is not None:
            try:
                journal.close()
            except OSError:
                pass
        for held in (journal_reservation, ledger_reservation):
            if held is not None and held.descriptor >= 0:
                try:
                    os.close(held.descriptor)
                except OSError:
                    pass
                held.descriptor = -1

    if output_write_failed or ledger_write_failed:
        return 2, receipt
    return (
        0 if not config.execute or receipt["result"]["observations_accepted"] else 1,
        receipt,
    )


def write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write one UTF-8 receipt with O_EXCL; never overwrite a prior artifact."""
    write_reserved_json(reserve_output_path(path), payload)


def parse_args(argv: list[str] | None = None) -> ProbeConfig | FinalizeConfig:
    """Validate a probe invocation or a no-browser finalizer invocation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="permit one source action"
    )
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="reconstruct a terminal ledger without connecting to a browser",
    )
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--query")
    parser.add_argument("--field-label")
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument(
        "--poll-interval-seconds", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS
    )
    parser.add_argument("--busy-retries", type=int, default=DEFAULT_BUSY_RETRIES)
    parser.add_argument(
        "--busy-retry-delay-seconds",
        type=float,
        default=DEFAULT_BUSY_RETRY_DELAY_SECONDS,
    )
    parser.add_argument(
        "--challenge-wait-seconds",
        type=float,
        default=DEFAULT_CHALLENGE_WAIT_SECONDS,
        help="finite passive challenge wait cap (maximum 30 seconds)",
    )
    parser.add_argument(
        "--challenge-poll-interval-seconds",
        type=float,
        default=DEFAULT_CHALLENGE_POLL_INTERVAL_SECONDS,
        help="fixed passive challenge poll cadence",
    )
    parser.add_argument(
        "--pre-submit-busy-wait-seconds",
        type=float,
        default=DEFAULT_PRE_SUBMIT_BUSY_WAIT_SECONDS,
        help=(
            "exploration-only passive ordinary-busy wait; default 0/off, "
            "maximum 180 seconds, fixed 2-second DOM cadence, no reissue"
        ),
    )
    parser.add_argument("--output-path")
    parser.add_argument("--journal-path")
    parser.add_argument("--ledger-path")
    args = parser.parse_args(argv)
    if args.finalize:
        if args.execute:
            parser.error("--finalize cannot be combined with --execute")
        if not compact(args.journal_path) or not compact(args.ledger_path):
            parser.error("--finalize requires --journal-path and --ledger-path")
        journal_path = Path(args.journal_path).expanduser()
        ledger_path = Path(args.ledger_path).expanduser()
        if journal_path.is_symlink() or ledger_path.is_symlink():
            parser.error("finalizer paths must not be symlinks")
        return FinalizeConfig(journal_path=journal_path, ledger_path=ledger_path)
    if not compact(args.output_path):
        parser.error("--output-path must be provided")
    if not compact(args.query) or not compact(args.field_label):
        parser.error("--query and --field-label must be provided")
    try:
        timeout = _finite_positive(args.timeout_seconds, "--timeout-seconds")
        interval = _finite_positive(
            args.poll_interval_seconds, "--poll-interval-seconds"
        )
        if interval > timeout:
            raise InputValidationError(
                "--poll-interval-seconds cannot exceed --timeout-seconds"
            )
        retries, retry_delay = _validate_busy_policy(
            args.busy_retries, args.busy_retry_delay_seconds
        )
        challenge_wait, challenge_interval = _validate_challenge_wait_policy(
            args.challenge_wait_seconds, args.challenge_poll_interval_seconds
        )
        pre_submit_busy_wait = _validate_pre_submit_busy_wait_policy(
            args.pre_submit_busy_wait_seconds
        )
        output_path = validate_output_path(args.output_path)
        journal_path: Path | None = None
        ledger_path: Path | None = None
        if args.execute:
            journal_value = args.journal_path or _derived_accounting_path(
                output_path, ".journal.jsonl"
            )
            ledger_value = args.ledger_path or _derived_accounting_path(
                output_path, ".ledger.json"
            )
            journal_path = _validate_create_only_path(
                journal_value, "--journal-path"
            )
            ledger_path = _validate_create_only_path(ledger_value, "--ledger-path")
            if len({output_path, journal_path, ledger_path}) != 3:
                raise InputValidationError(
                    "--output-path, --journal-path, and --ledger-path must be distinct"
                )
        return ProbeConfig(
            execute=args.execute,
            cdp_url=validate_loopback_cdp_endpoint(args.cdp_url),
            query=_validate_nonblank(args.query, "--query", MAX_QUERY_CHARACTERS),
            field_label=_validate_nonblank(
                args.field_label, "--field-label", MAX_FIELD_LABEL_CHARACTERS
            ),
            timeout_seconds=timeout,
            poll_interval_seconds=interval,
            busy_retries=retries,
            busy_retry_delay_seconds=retry_delay,
            output_path=output_path,
            challenge_wait_seconds=challenge_wait,
            challenge_poll_interval_seconds=challenge_interval,
            pre_submit_busy_wait_seconds=pre_submit_busy_wait,
            journal_path=journal_path,
            ledger_path=ledger_path,
        )
    except InputValidationError as error:
        parser.error(str(error))
    raise AssertionError("argparse.error did not exit")  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    if isinstance(config, FinalizeConfig):
        try:
            finalize_ledger(config.journal_path, config.ledger_path)
        except Exception:
            return 1
        return 0
    try:
        status, _ = asyncio.run(run_probe(config))
    except Exception:
        # run_probe owns the pre-source reservation and its safe final write.
        return 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
