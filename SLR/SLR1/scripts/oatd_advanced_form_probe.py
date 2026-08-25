#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""One owned-page OATD advanced-form diagnostic.

The probe is intentionally narrower than a search adapter.  It attaches only
through an explicit loopback CDP endpoint, creates one sibling page, submits
one normal nonblank advanced GET form, and retains only a safe aggregate
receipt.  It never visits record/detail/full-text routes, serializes browser
URLs or target IDs, or interacts with access controls.

Source action is opt-in with ``--execute``.  This makes the default CLI path
safe for offline validation and for tests run by a browser-lease controller.
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
from urllib.parse import urlencode


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
SOURCE_ORIGIN = "https://oatd.org"
SOURCE_HOST = "oatd.org"
HOME_URL = f"{SOURCE_ORIGIN}/"
ADVANCED_PATH = "/oatd/search-composer"
ADVANCED_ACTION = f"{SOURCE_ORIGIN}{ADVANCED_PATH}"

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_POLL_INTERVAL_SECONDS = 0.2
DEFAULT_BUSY_RETRIES = 2
DEFAULT_BUSY_RETRY_DELAY_SECONDS = 30.0
MAX_BUSY_RETRIES = 5
MIN_BUSY_RETRY_DELAY_SECONDS = 1.0
MAX_BUSY_RETRY_DELAY_SECONDS = 3_600.0
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
    "box2",
    "field2",
    "joiner2",
    "box3",
    "field3",
    "joiner3",
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

    current_canonical_home_route: bool
    source_identity: bool
    exact_https_origin: bool
    canonical_effective_get_action: bool
    form_target_self: bool
    submitter_no_override: bool

    @property
    def verified(self) -> bool:
        return bool(
            self.current_canonical_home_route
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


@dataclass
class OutputReservation:
    """One atomically claimed receipt inode held through source activity."""

    path: Path
    descriptor: int


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
  const access = /access denied|forbidden|captcha|enable javascript and cookies/i.test(errors);
  const syntaxError = /syntax|could not parse|invalid query|search error/i.test(errors);
  const sourceState = challenge ? "challenge" : busy ? "busy" : access ? "access" :
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
    current_canonical_home_route: false,
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
    result.current_canonical_home_route = result.exact_https_origin &&
      current.pathname === "/" && current.search === "" && current.hash === "";

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
    current_canonical_home_route: false,
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
      result.current_canonical_home_route = result.exact_https_origin &&
        current.pathname === "/" && current.search === "" && current.hash === "";

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
  const blockUnsafeDefault = event => {
    if (event.type === "submit" && event.target !== form) return;
    const stillSafe = safetyFor();
    const exactSubmitter = event.type !== "submit" || event.submitter === submitter;
    if (!exactSubmitter || !Object.values(stillSafe).every(Boolean)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      return;
    }
    // Stop later page submit handlers from changing action/target after this
    // final proof while preserving the browser's native default submission.
    if (event.type === "submit") event.stopImmediatePropagation();
  };
  // Pin the exact node and recheck at both native default-action boundaries.
  // A changed action, target, or submitter therefore cancels rather than submits.
  submitter.addEventListener("click", blockUnsafeDefault, { capture: true, once: true });
  window.addEventListener("submit", blockUnsafeDefault, true);
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
    const element = elements.length === 1 ? elements[0] : null;
    return {
      name,
      count: elements.length,
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
      location.pathname === "/oatd/search-composer" && location.hash === "";
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
  const access = /access denied|forbidden|captcha|enable javascript and cookies/i.test(errors);
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


def validate_output_path(value: str) -> Path:
    """Validate a prospective create-only destination before atomic reservation."""
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


def reserve_output_path(path: Path) -> OutputReservation:
    """Atomically claim the final receipt name before any source activity."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return OutputReservation(path=path, descriptor=os.open(path, flags, 0o600))


def write_reserved_json(
    reservation: OutputReservation, payload: Mapping[str, Any]
) -> None:
    """Write through a claimed descriptor without ever reopening its pathname."""
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("receipt reservation is no longer writable")
    reservation.descriptor = -1
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
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
        output_path=validate_output_path(str(config.output_path)),
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
    "current_canonical_home_route",
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
        current_canonical_home_route=payload["current_canonical_home_route"],
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
    page: Any, inspection: FormInspection, query: str
) -> PreparedSubmission:
    """Fill, read back, and click exactly one visible native submit control."""
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
        # unsafe destination or a second form submission.
        await submitter.click()
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
) -> PostClickOutcome:
    """Poll and retry under one absolute post-click deadline.

    Every evaluation, respectful wait, recheck, and retry navigation consumes
    the same deadline. A busy response is reissued only after a fresh safe
    recheck and never after that deadline has elapsed.
    """
    if clock is None:
        clock = asyncio.get_running_loop().time
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
        if state.challenge:
            # A challenge is passive-only. It never reaches busy retry.
            challenge_seen = True
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue
        if state.access:
            return _outcome(
                "access_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
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
        if rechecked.challenge:
            challenge_seen = True
            await _sleep_to_deadline(deadline, poll_interval_seconds, clock, sleeper)
            continue
        if rechecked.access:
            return _outcome(
                "access_after_submission",
                source_total=None,
                polls=polls,
                budget=busy_budget,
            )
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
        # Account before the await: transport failure can follow dispatch.
        busy_budget.record_retry_attempt()
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
        "schema_version": "slr1-oatd-advanced-form-probe/v2",
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
            "current_canonical_home_route": False,
            "current_source_identity": False,
            "current_exact_https_origin": False,
            "canonical_effective_get_action": False,
            "form_target_self": False,
            "submitter_no_override": False,
            "pre_click_safety_verified": False,
            "native_submit_clicked": False,
            "post_click_polls": 0,
            "busy_recovery_attempts": 0,
            "busy_retries_attempted": 0,
            "busy_retries_completed": 0,
            "busy_retries_performed": 0,
        },
        "result": {
            "status": "not_run",
            "classification": "not_run",
            "source_reported_total": None,
            "observations_accepted": False,
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
    submission["current_canonical_home_route"] = safety.current_canonical_home_route
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


async def run_probe(
    config: ProbeConfig,
    *,
    playwright_factory: Callable[[], Any] | None = None,
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
    try:
        # Claim the final name before importing or constructing Playwright so a
        # concurrent winner prevents every source action, not merely the write.
        reservation = reserve_output_path(config.output_path)
    except OSError:
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
    output_write_failed = False

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

                        await owned_page.goto(
                            HOME_URL,
                            wait_until="domcontentloaded",
                            timeout=_milliseconds(config.timeout_seconds),
                        )
                        inspection = await inspect_advanced_form(
                            owned_page, config.field_label
                        )
                        submission = receipt["submission"]
                        submission["canonical_form_count"] = (
                            inspection.canonical_form_count
                        )
                        submission["canonical_get_form"] = (
                            inspection.canonical_form_count == 1
                            and inspection.method_get
                        )
                        submission["box1_count"] = inspection.box1_count
                        submission["field1_count"] = inspection.field1_count
                        submission["exact_field_mapping"] = (
                            inspection.matching_field_option_count == 1
                            and inspection.field_value is not None
                        )
                        submission["visible_native_submit_count"] = (
                            inspection.visible_native_submit_count
                        )
                        pre_submit_abort = _pre_submit_abort(inspection)
                        if pre_submit_abort is not None:
                            raise ProbeAbort(pre_submit_abort)

                        prepared = await prepare_native_submission(
                            owned_page, inspection, config.query
                        )
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
        _set_result(receipt, primary_classification, primary_total)
        if not config.execute:
            receipt["result"]["status"] = "not_run"
        try:
            write_reserved_json(reservation, receipt)
        except Exception:
            output_write_failed = True

    if output_write_failed:
        return 2, receipt
    return (
        0 if not config.execute or receipt["result"]["observations_accepted"] else 1,
        receipt,
    )


def write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write one UTF-8 receipt with O_EXCL; never overwrite a prior artifact."""
    write_reserved_json(reserve_output_path(path), payload)


def parse_args(argv: list[str] | None = None) -> ProbeConfig:
    """Validate every input and a prospective receipt destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="permit one source action"
    )
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--query", required=True)
    parser.add_argument("--field-label", required=True)
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
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args(argv)
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
            output_path=validate_output_path(args.output_path),
        )
    except InputValidationError as error:
        parser.error(str(error))
    raise AssertionError("argparse.error did not exit")  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    try:
        status, _ = asyncio.run(run_probe(config))
    except Exception:
        # run_probe owns the pre-source reservation and its safe final write.
        return 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
