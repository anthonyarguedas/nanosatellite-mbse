#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.48,<2",
# ]
# ///
"""Run one frozen PQDT Global aggregate-only validation query.

This pilot-only wrapper proves an already-selected exact PQDT Global source and
returns only source-total/control evidence. It cannot select an arbitrary
ProQuest database, accept an arbitrary query, retrieve records, paginate,
export RIS, normalize output, or create merge input.
"""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import math
import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SOURCE_KEY = "proquest_dissertations_theses_global"
SOURCE_NAME = "ProQuest Dissertations & Theses Global"
PLATFORM_NAME = "ProQuest Platform"
ORIGIN = "https://www.proquest.com"
PRODUCT_ROUTE = "pqdtglobal"
DATABASE_SELECTION_URL = f"{ORIGIN}/{PRODUCT_ROUTE}/databases/advanced"
COMMAND_LINE_URL = f"{ORIGIN}/{PRODUCT_ROUTE}/commandline"
ALLOWED_DATABASE_LABELS = (
    "ProQuest Dissertations & Theses Global",
    "ProQuest Dissertations & Theses Global Full Text Included",
)
QUERY_MANIFEST_PATH = Path(__file__).resolve().parents[1] / "thesis-source-query-manifest-v1.6.json"
QUERY_MANIFEST_SHA256 = "df1fbc09d8fa88f7d02564445c9fb8644b40cdbeabf58fd7d57bf6a28ce23040"
QUERY_IDS = (
    "PQDT-A1", "PQDT-A2", "PQDT-A3", "PQDT-B1", "PQDT-B2", "PQDT-BG1",
    "PQDT-BG2", "PQDT-BC1", "PQDT-BT2", "PQDT-V1", "PQDT-O1",
)
DEFAULT_TIMEOUT_SECONDS = 30.0
LOCK_PATH = Path.home() / ".cache" / "eps-mbse-slr" / "proquest-platform-count-gate.lock"
TOTAL_PATTERN = re.compile(r"^(\d[\d,]*)\s+results?$", re.IGNORECASE)

# Source-selection evidence only: semantic checkbox labels and checked state.
# No result/card fields, IDs, URLs, cookies, storage, or raw HTML are read.
PQDT_DATABASE_STATE_SCRIPT = r"""
(payload) => {
  const normalize = value => String(value || "")
    .replace(/[\s\u200e\u200f]+/g, " ").trim();
  const options = Array.from(document.querySelectorAll("input[type='checkbox'][id^='dbcb_']"))
    .map(input => {
      const label = input.id ? document.querySelector(`label[for="${CSS.escape(input.id)}"]`) : null;
      return { label: normalize(label && label.textContent), checked: Boolean(input.checked) };
    });
  const targets = options.filter(option => payload.allowedLabels.includes(option.label));
  const selected = options.filter(option => option.checked);
  const titleText = normalize(document.title);
  const challenge = /just a moment|attention required|verify you are human/i.test(titleText) ||
    Boolean(document.querySelector("#challenge-running, iframe[src*='challenges.cloudflare.com']"));
  return {
    protocol: window.location.protocol,
    host: window.location.hostname,
    path: window.location.pathname,
    targetCount: targets.length,
    selectedCount: selected.length,
    exactTargetOnly: targets.length === 1 && selected.length === 1 && targets[0].checked,
    selectedTargetLabelAllowed: targets.length === 1 && payload.allowedLabels.includes(targets[0].label),
    challenge,
    loginRoute: /\/(?:login|signin)(?:\/|$)/i.test(window.location.pathname),
    ready: challenge || options.length > 0
  };
}
"""

# Only an explicit visible Full text control is asserted. Other limiter states
# remain a live PQDT-02 proof obligation and are never inferred from absence.
PQDT_FORM_STATE_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/\s+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const checkboxLabel = input => {
    const label = input.id ? document.querySelector(`label[for="${CSS.escape(input.id)}"]`) : null;
    return normalize(label && label.textContent);
  };
  const checkedLimiters = Array.from(document.querySelectorAll("input[type='checkbox']"))
    .filter(visible)
    .filter(input => input.checked)
    .map(checkboxLabel)
    .filter(label => /^(?:Full text|Peer reviewed|Source type|Document type|Manuscript type|Degree|Open access)$/i.test(label));
  const fullText = Array.from(document.querySelectorAll("input[type='checkbox']"))
    .filter(visible)
    .filter(input => /^Full text$/i.test(checkboxLabel(input)));
  const one = selector => Array.from(document.querySelectorAll(selector)).filter(visible);
  const sort = one("select[id^='sortType_']");
  const size = one("select[id^='itemsPerPage_']");
  const dedup = one("input[id^='excludeDuplicate_']");
  const spelling = one("#includeVariantsSpelling");
  const forms = one("#includeVariantsPluralsAndAdjectives");
  const query = one("#searchTerm");
  const submit = one("#submit_7");
  const titleText = normalize(document.title);
  const challenge = /just a moment|attention required|verify you are human/i.test(titleText) ||
    Boolean(document.querySelector("#challenge-running, iframe[src*='challenges.cloudflare.com']"));
  return {
    protocol: window.location.protocol,
    host: window.location.hostname,
    path: window.location.pathname,
    titleHasSource: titleText.includes("ProQuest Dissertations & Theses Global"),
    sortCount: sort.length,
    sortValue: sort.length === 1 ? String(sort[0].value || "") : "",
    pageSizeCount: size.length,
    pageSizeValue: size.length === 1 ? String(size[0].value || "") : "",
    dedupCount: dedup.length,
    dedupChecked: dedup.length === 1 ? Boolean(dedup[0].checked) : null,
    spellingCount: spelling.length,
    spellingChecked: spelling.length === 1 ? Boolean(spelling[0].checked) : null,
    formsCount: forms.length,
    formsChecked: forms.length === 1 ? Boolean(forms[0].checked) : null,
    queryFieldCount: query.length,
    submitCount: submit.length,
    fullTextControlCount: fullText.length,
    fullTextChecked: fullText.length === 1 ? Boolean(fullText[0].checked) : null,
    checkedDiscoveryLimiterCount: checkedLimiters.length,
    challenge,
    loginRoute: /\/(?:login|signin)(?:\/|$)/i.test(window.location.pathname),
    ready: challenge || (query.length === 1 && submit.length === 1)
  };
}
"""

# Aggregate/explicit-zero state only. No result rows, links, ranks, IDs, or
# candidate metadata are selected or returned.
PQDT_COUNT_STATE_SCRIPT = r"""
(payload) => {
  const normalize = value => String(value || "").replace(/\s+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const totalNodes = Array.from(document.querySelectorAll("#pqResultsCount")).filter(visible);
  const queryFields = Array.from(document.querySelectorAll("#searchTerm")).filter(visible);
  const zeroNodes = Array.from(document.querySelectorAll(".pagingBoxNoResultMain .error_message, .pagingBoxNoResultMain"))
    .filter(visible)
    .filter(element => /found\s+0\s+results?/i.test(normalize(element.textContent)));
  const errorNodes = Array.from(document.querySelectorAll(".error_message, [role='alert']"))
    .filter(visible)
    .map(element => normalize(element.textContent));
  const syntaxError = errorNodes.some(text =>
    !/found\s+0\s+results?/i.test(text) && /syntax|invalid|could not parse|search error/i.test(text)
  );
  const titleText = normalize(document.title);
  const challenge = /just a moment|attention required|verify you are human/i.test(titleText) ||
    Boolean(document.querySelector("#challenge-running, iframe[src*='challenges.cloudflare.com']"));
  return {
    protocol: window.location.protocol,
    host: window.location.hostname,
    pathStartsProduct: window.location.pathname.startsWith("/pqdtglobal/"),
    titleHasSource: titleText.includes("ProQuest Dissertations & Theses Global"),
    queryFieldCount: queryFields.length,
    queryEchoExact: queryFields.length === 1 && normalize(queryFields[0].value) === normalize(payload.query),
    totalNodeCount: totalNodes.length,
    totalText: totalNodes.length === 1 ? normalize(totalNodes[0].textContent) : "",
    explicitZero: zeroNodes.length === 1,
    zeroNodeCount: zeroNodes.length,
    syntaxError,
    challenge,
    loginRoute: /\/(?:login|signin)(?:\/|$)/i.test(window.location.pathname),
    ready: challenge || syntaxError || zeroNodes.length > 0 || totalNodes.length > 0
  };
}
"""


class GateError(Exception):
    code = "other_fail_closed"


class InputGateError(GateError):
    code = "invalid_input"


class AccessGateError(GateError):
    code = "access_state"


class ProtocolGateError(GateError):
    code = "protocol_mismatch"


class TimeoutGateError(GateError):
    code = "timeout"


class LockGateError(GateError):
    code = "source_lock_unavailable"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def validate_local_cdp_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or (parsed.hostname or "").casefold() not in {
        "127.0.0.1", "localhost", "::1"
    }:
        raise InputGateError("CDP must use a loopback HTTP(S) endpoint.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise InputGateError("CDP URL must not contain credentials or query/fragment data.")
    return value.rstrip("/")


def load_frozen_queries() -> dict[str, dict[str, str]]:
    try:
        manifest_bytes = QUERY_MANIFEST_PATH.read_bytes()
        if not isinstance(manifest_bytes, bytes):
            raise TypeError
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    except (OSError, TypeError):
        raise InputGateError("The pinned thesis-source query manifest is unreadable.") from None
    if manifest_sha256 != QUERY_MANIFEST_SHA256:
        raise InputGateError("The pinned thesis-source query manifest checksum differs.")
    try:
        manifest = json.loads(manifest_bytes)
    except (TypeError, ValueError):
        raise InputGateError("The pinned thesis-source query manifest is unreadable.") from None
    if not isinstance(manifest, dict):
        raise InputGateError("The pinned thesis-source query manifest has an invalid top-level type.")
    if (
        manifest.get("protocol_version") != "1.6"
        or manifest.get("artifact_class") != "frozen_validation_contract_not_search_output"
    ):
        raise InputGateError("The pinned query manifest has the wrong protocol boundary.")
    sources = manifest.get("sources")
    if not isinstance(sources, dict):
        raise InputGateError("The pinned query manifest has an invalid source registry type.")
    source = sources.get(SOURCE_KEY)
    if not isinstance(source, dict):
        raise InputGateError("The pinned query manifest has an invalid PQDT source type.")
    controls = source.get("controls")
    semantic_labels = source.get("semantic_database_labels")
    if not isinstance(controls, dict) or not isinstance(semantic_labels, list):
        raise InputGateError("The PQDT source/control contract differs from the wrapper.")
    if (
        source.get("fixed_product_route") != PRODUCT_ROUTE
        or tuple(semantic_labels) != ALLOWED_DATABASE_LABELS
        or controls != {
            "sort": "Relevance",
            "page_size": 20,
            "source_duplicate_exclusion": False,
            "full_text_limiter": False,
            "peer_reviewed_limiter": False,
            "source_type_limiter": False,
            "document_type_limiter": False,
            "degree_or_manuscript_limiter": False,
            "access_limiter": False,
            "spelling_variants": True,
            "plural_and_adjective_variants": True,
        }
    ):
        raise InputGateError("The PQDT source/control contract differs from the wrapper.")
    entries = source.get("queries")
    if not isinstance(entries, list):
        raise InputGateError("The PQDT query registry is not a list.")
    indexed: dict[str, dict[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise InputGateError("The PQDT query registry contains a malformed entry.")
        query_id = entry.get("query_id")
        query = entry.get("query")
        digest = entry.get("query_sha256")
        expected_body = query_id.replace("PQDT-", "PQ-", 1) if isinstance(query_id, str) else ""
        if (
            query_id not in QUERY_IDS
            or entry.get("source_body_id") != expected_body
            or not isinstance(query, str)
            or not query.startswith("NOFT(")
            or query.count("YR(2011-2026)") != 1
            or query.count("LA(English)") != 1
            or not isinstance(digest, str)
            or hashlib.sha256(query.encode("utf-8")).hexdigest() != digest
            or query_id in indexed
        ):
            raise InputGateError("The PQDT query registry differs from the frozen exact-query contract.")
        indexed[query_id] = {"query": query, "query_sha256": digest}
    if tuple(indexed) != QUERY_IDS:
        raise InputGateError("The PQDT query registry ID/order contract differs.")
    return indexed


def parse_database_state(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProtocolGateError("invalid_database_state")
    for key in ("exactTargetOnly", "selectedTargetLabelAllowed", "challenge", "loginRoute", "ready"):
        if not isinstance(payload.get(key), bool):
            raise ProtocolGateError("invalid_database_boolean")
    if payload["challenge"] or payload["loginRoute"]:
        raise AccessGateError("challenge_or_login")
    if payload.get("protocol") != "https:" or str(payload.get("host", "")).casefold() != "www.proquest.com" or payload.get("path") != f"/{PRODUCT_ROUTE}/databases/advanced":
        raise ProtocolGateError("database_route_mismatch")
    if payload.get("targetCount") != 1 or payload.get("selectedCount") != 1 or not payload["exactTargetOnly"] or not payload["selectedTargetLabelAllowed"]:
        raise ProtocolGateError("exact_pqdt_selection_not_proven")
    return {"exact_database_selection": True}


def parse_form_state(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProtocolGateError("invalid_form_state")
    for key in ("titleHasSource", "dedupChecked", "spellingChecked", "formsChecked", "challenge", "loginRoute", "ready"):
        if not isinstance(payload.get(key), bool):
            raise ProtocolGateError("invalid_form_boolean")
    if payload["challenge"] or payload["loginRoute"]:
        raise AccessGateError("challenge_or_login")
    if payload.get("protocol") != "https:" or str(payload.get("host", "")).casefold() != "www.proquest.com" or payload.get("path") != f"/{PRODUCT_ROUTE}/commandline" or not payload["titleHasSource"]:
        raise ProtocolGateError("product_route_mismatch")
    exact_counts = {
        "sortCount": 1, "pageSizeCount": 1, "dedupCount": 1,
        "spellingCount": 1, "formsCount": 1, "queryFieldCount": 1, "submitCount": 1,
    }
    if any(
        isinstance(payload.get(key), bool)
        or not isinstance(payload.get(key), int)
        or payload.get(key) != value
        for key, value in exact_counts.items()
    ):
        raise ProtocolGateError("form_controls_missing_or_ambiguous")
    if payload.get("sortValue") != "relevance" or payload.get("pageSizeValue") != "20":
        raise ProtocolGateError("sort_or_page_size_mismatch")
    if payload["dedupChecked"] or not payload["spellingChecked"] or not payload["formsChecked"]:
        raise ProtocolGateError("dedup_or_variant_state_mismatch")
    full_text_count = payload.get("fullTextControlCount")
    if isinstance(full_text_count, bool) or not isinstance(full_text_count, int) or full_text_count != 1:
        raise ProtocolGateError("full_text_control_missing_or_ambiguous")
    if payload.get("fullTextChecked") is not False:
        raise ProtocolGateError("full_text_control_checked_or_invalid")
    # A zero count catches observed named visible limiters only. It cannot prove
    # absent, hidden, type, degree, or access limiter state, so that proof is
    # retained as an explicit PQDT-02 live-gate residual rather than output.
    checked_limiter_count = payload.get("checkedDiscoveryLimiterCount")
    if (
        isinstance(checked_limiter_count, bool)
        or not isinstance(checked_limiter_count, int)
        or checked_limiter_count != 0
    ):
        raise ProtocolGateError("discovery_limiter_enabled_or_ambiguous")
    return {
        "exact_product_route": True,
        "sort": "Relevance",
        "page_size": 20,
        "source_duplicate_exclusion": False,
        "spelling_variants": True,
        "plural_and_adjective_variants": True,
        "full_text_control_visible": True,
        "full_text_limiter": False,
    }


def parse_total_text(value: Any) -> int:
    if not isinstance(value, str):
        raise ProtocolGateError("invalid_total_text")
    match = TOTAL_PATTERN.fullmatch(value.strip())
    if not match:
        raise ProtocolGateError("unrecognized_total_text")
    return int(match.group(1).replace(",", ""))


def parse_count_state(payload: Any) -> int:
    if not isinstance(payload, dict):
        raise ProtocolGateError("invalid_count_state")
    for key in ("titleHasSource", "queryEchoExact", "explicitZero", "syntaxError", "challenge", "loginRoute", "ready"):
        if not isinstance(payload.get(key), bool):
            raise ProtocolGateError("invalid_count_boolean")
    if payload["challenge"] or payload["loginRoute"]:
        raise AccessGateError("challenge_or_login")
    if payload["syntaxError"]:
        raise ProtocolGateError("syntax_error")
    if payload.get("protocol") != "https:" or str(payload.get("host", "")).casefold() != "www.proquest.com" or payload.get("pathStartsProduct") is not True or not payload["titleHasSource"]:
        raise ProtocolGateError("result_product_route_mismatch")
    if payload.get("queryFieldCount") != 1 or not payload["queryEchoExact"]:
        raise ProtocolGateError("query_echo_mismatch")
    if payload["explicitZero"] or payload.get("zeroNodeCount"):
        raise ProtocolGateError("native_zero_unvalidated")
    if payload.get("totalNodeCount") != 1:
        raise ProtocolGateError("result_total_missing_or_ambiguous")
    total = parse_total_text(payload.get("totalText"))
    if total < 1:
        raise ProtocolGateError("nonpositive_total_without_validated_zero")
    return total


def validate_artifact_allowlist(artifact: dict[str, Any]) -> None:
    forbidden = {
        "title", "author", "authors", "abstract", "snippet", "paperid", "recordid",
        "record_id", "url", "href", "results", "records", "rank", "cookie", "token",
        "session", "csrf", "accountid", "cdp_url", "raw_error", "checkbox_id",
    }
    for key in artifact:
        if key.casefold() in forbidden:
            raise ProtocolGateError("forbidden_output_field")
    serialized = json.dumps(artifact, sort_keys=True).casefold()
    for marker in ("?token=", "searchid", "sessionid", "accountid=", "cookie=", "/results/"):
        if marker in serialized:
            raise ProtocolGateError("sensitive_output_marker")


def make_artifact(query_id: str, query_sha256: str, *, started_at: str | None, completed_at: str, total: int | None, observed: dict[str, Any] | None = None, error: GateError | None = None) -> dict[str, Any]:
    return {
        "artifact_kind": "pqdt_global_count_gate",
        "artifact_class": "pilot_not_candidate_search",
        "protocol_version": "1.6",
        "source": SOURCE_NAME,
        "canonical_source": SOURCE_KEY,
        "platform": PLATFORM_NAME,
        "query_id": query_id,
        "query_manifest_sha256": QUERY_MANIFEST_SHA256,
        "query_body_sha256": query_sha256,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "status": "success" if error is None else "error",
        "failure_code": None if error is None else error.code,
        "source_total": total if error is None else None,
        "observed": observed or {},
        "candidate_records_serialized": 0,
        "results_retrieved": 0,
        "merge_input": False,
        "candidate_import_allowed": False,
        "native_export_automated": False,
        "unvalidated": [
            "PQDT-02: absent/hidden/type/degree/access limiter proof remains live",
            "PQDT-02: cooperative lock cannot eliminate external ABA",
            "PQDT-02: live authorized-session gate remains open",
            "native_zero", "pagination", "source_record_identity", "pageable_cap",
            "native_ris", "normalization", "date_language_semantics",
        ],
    }


# This advisory lock coordinates cooperating local wrappers only. It cannot
# eliminate an external actor changing shared session state via ABA; that proof
# remains an explicit live PQDT-02 residual in every artifact.
@contextmanager
def exclusive_source_lock(path: Path = LOCK_PATH) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    with path.open("a+", encoding="utf-8") as handle:
        try:
            os.fchmod(handle.fileno(), 0o600)
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise LockGateError("Another ProQuest gate owns the platform lock.") from error
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    expanded_path = path.expanduser()
    path = expanded_path.parent.resolve() / expanded_path.name
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    published = False
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_path, path)
        except FileExistsError:
            raise InputGateError("Output path already exists; pilot artifacts are immutable.") from None
        published = True
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            if not published:
                raise
            # The final hard link is immutable; only the owned temporary leaked.


async def wait_payload(page: Any, script: str, argument: Any, timeout_seconds: float) -> Any:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while True:
        try:
            payload = await page.evaluate(script, argument) if argument is not None else await page.evaluate(script)
            if isinstance(payload, dict) and payload.get("ready") is True:
                return payload
        except GateError:
            raise
        except Exception:  # noqa: BLE001 - transient DOM polling can race page hydration; retry to deadline.
            payload = None
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutGateError("state_timeout")
        await asyncio.sleep(0.1)


async def navigate(page: Any, url: str, timeout_seconds: float) -> None:
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=int(timeout_seconds * 1000))
    except Exception as error:  # Navigation failures map to the bounded timeout state.
        raise TimeoutGateError("navigation_timeout") from error


async def assert_exact_pqdt_only_selection(page: Any, timeout_seconds: float) -> None:
    payload = await wait_payload(
        page,
        PQDT_DATABASE_STATE_SCRIPT,
        {"allowedLabels": list(ALLOWED_DATABASE_LABELS)},
        timeout_seconds,
    )
    parse_database_state(payload)


async def configure_result_options(page: Any) -> None:
    expander = page.locator("#showResultPageOptions")
    if await expander.count() != 1:
        raise ProtocolGateError("result_options_missing")
    if await expander.get_attribute("aria-expanded") != "true":
        await expander.click()
    sort = page.locator("select[id^='sortType_']:visible")
    size = page.locator("select[id^='itemsPerPage_']:visible")
    dedup = page.locator("input[id^='excludeDuplicate_']:visible")
    spelling = page.locator("#includeVariantsSpelling:visible")
    forms = page.locator("#includeVariantsPluralsAndAdjectives:visible")
    controls = (sort, size, dedup, spelling, forms)
    if any(await control.count() != 1 for control in controls):
        raise ProtocolGateError("result_option_controls_ambiguous")
    await sort.select_option(value="relevance")
    await size.select_option(value="20")
    if await dedup.is_checked():
        await dedup.click()
    if not await spelling.is_checked():
        await spelling.click()
    if not await forms.is_checked():
        await forms.click()


async def run_browser_gate(query: str, *, cdp_url: str, timeout_seconds: float) -> tuple[int, dict[str, Any]]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:  # pragma: no cover
        raise ProtocolGateError("playwright_unavailable") from error
    page = None
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(cdp_url, timeout=int(timeout_seconds * 1000))
            if not browser.contexts:
                raise AccessGateError("no_authorized_browser_context")
            context = browser.contexts[0]
            context.set_default_timeout(int(timeout_seconds * 1000))
            context.set_default_navigation_timeout(int(timeout_seconds * 1000))
            page = await context.new_page()

            selection_assertion_count = 0
            await navigate(page, DATABASE_SELECTION_URL, timeout_seconds)
            await assert_exact_pqdt_only_selection(page, timeout_seconds)
            selection_assertion_count += 1

            # Revisit the semantic selector in this same wrapper-owned page.
            # This second check is immediately before the final command-page
            # configuration/submission sequence; the advisory lock cannot rule
            # out external ABA changes between page operations.
            await navigate(page, DATABASE_SELECTION_URL, timeout_seconds)
            await assert_exact_pqdt_only_selection(page, timeout_seconds)
            selection_assertion_count += 1
            if selection_assertion_count != 2:  # Defensive invariant for serialized scope evidence.
                raise ProtocolGateError("pqdt_selection_assertion_count_mismatch")

            await navigate(page, COMMAND_LINE_URL, timeout_seconds)
            await configure_result_options(page)
            field = page.locator("#searchTerm:visible")
            button = page.locator("#submit_7:visible")
            if await field.count() != 1 or await button.count() != 1:
                raise ProtocolGateError("command_line_controls_ambiguous")
            await field.fill(query)

            # This validates the exact command route/title and visible controls
            # immediately before submitting the frozen query.
            form_payload = await wait_payload(page, PQDT_FORM_STATE_SCRIPT, None, timeout_seconds)
            form_observed = parse_form_state(form_payload)
            await button.click()
            count_payload = await wait_payload(
                page, PQDT_COUNT_STATE_SCRIPT, {"query": query}, timeout_seconds,
            )
            total = parse_count_state(count_payload)
            return total, {
                "exact_database_selection": True,
                "database_selection_assertion_count": selection_assertion_count,
                **form_observed,
                "query_echo_exact": True,
            }
    finally:
        if page is not None:
            try:
                await page.close()
            except Exception:  # noqa: BLE001 - suppress only cleanup failure for this wrapper-owned page.
                page = None
        # The attached browser and context remain open for their owner.


def valid_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be numeric") from error
    if not math.isfinite(parsed) or parsed <= 0 or parsed > 300:
        raise argparse.ArgumentTypeError("timeout must be finite and in (0, 300]")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate one frozen exact-PQDT query aggregate without reading records.")
    parser.add_argument("--query-id", required=True, choices=QUERY_IDS)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--cdp-url", required=True, help="Loopback CDP URL for an already-authorized local Chrome.")
    parser.add_argument("--timeout-seconds", type=valid_timeout, default=DEFAULT_TIMEOUT_SECONDS)
    return parser


def _fail_closed_exit(
    *,
    query_id: str,
    query_sha256: str,
    output_path: str,
    error: GateError,
    started_at: str | None,
) -> int:
    try:
        artifact = make_artifact(
            query_id,
            query_sha256,
            started_at=started_at,
            completed_at=utc_now(),
            total=None,
            error=error,
        )
        validate_artifact_allowlist(artifact)
        atomic_write_json(Path(output_path), artifact)
    except Exception:  # noqa: BLE001, S110 - a failed artifact destination must not expose an exception or overwrite it.
        pass
    try:
        print(f"PQDT Global count gate failed closed: {error.code}")
    except OSError:
        pass
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    started_at: str | None = None
    query_sha = ""
    try:
        queries = load_frozen_queries()
        entry = queries[args.query_id]
        query_sha = entry["query_sha256"]
        cdp_url = validate_local_cdp_url(args.cdp_url)
        with exclusive_source_lock():
            started_at = utc_now()
            total, observed = asyncio.run(
                run_browser_gate(entry["query"], cdp_url=cdp_url, timeout_seconds=args.timeout_seconds)
            )
        artifact = make_artifact(
            args.query_id, query_sha, started_at=started_at, completed_at=utc_now(),
            total=total, observed=observed,
        )
        validate_artifact_allowlist(artifact)
        atomic_write_json(Path(args.output_path), artifact)
    except GateError as error:
        return _fail_closed_exit(
            query_id=args.query_id,
            query_sha256=query_sha,
            output_path=args.output_path,
            error=error,
            started_at=started_at,
        )
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:  # noqa: BLE001 - every ordinary browser, CDP, control, or filesystem failure exits fail-closed.
        return _fail_closed_exit(
            query_id=args.query_id,
            query_sha256=query_sha,
            output_path=args.output_path,
            error=GateError(),
            started_at=started_at,
        )
    try:
        print(f"PQDT Global count gate passed for {args.query_id}; aggregate only, no records serialized.")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
