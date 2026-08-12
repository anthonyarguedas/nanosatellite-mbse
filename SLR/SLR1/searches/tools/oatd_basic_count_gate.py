#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.48,<2",
# ]
# ///
"""Run one frozen OATD basic-interface count gate without reading result cards.

This is a validation-only wrapper. It accepts one version-1.6 OATD query ID,
returns only aggregate/interface evidence, and is never merge eligible. It does
not validate native zero, pagination, source-record identity, record capture,
or date/language screening.
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
from urllib.parse import urlencode, urlsplit

SOURCE_KEY = "oatd"
SOURCE_NAME = "Open Access Theses and Dissertations (OATD)"
SEARCH_URL = "https://oatd.org/oatd/search"
QUERY_MANIFEST_PATH = Path(__file__).resolve().parents[1] / "thesis-source-query-manifest-v1.6.json"
QUERY_MANIFEST_SHA256 = "df1fbc09d8fa88f7d02564445c9fb8644b40cdbeabf58fd7d57bf6a28ce23040"
QUERY_IDS = (
    "OATD-A1", "OATD-A2", "OATD-A3", "OATD-B1", "OATD-B2", "OATD-BG1",
    "OATD-BG2", "OATD-BC1", "OATD-BT2", "OATD-V1", "OATD-O1",
)
DEFAULT_TIMEOUT_SECONDS = 30.0
LOCK_PATH = Path.home() / ".cache" / "eps-mbse-slr" / "oatd-basic-count-gate.lock"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# This script deliberately reads no result-card content, links, IDs, storage,
# cookies, HTML, or broad body text. It returns a fixed allowlist of page-level
# aggregate/control booleans and integers.
OATD_COUNT_STATE_SCRIPT = r"""
(payload) => {
  const normalize = value => String(value || "")
    .replace(/[\s\u2009\u202f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const reports = Array.from(document.querySelectorAll("p.matchesReport")).filter(visible);
  const report = reports.length === 1 ? reports[0] : null;
  const reportText = normalize(report && report.textContent);
  const expectedPrefix = `You searched for ${normalize(payload.query)}.`;
  const rangeMatch = reportText.match(
    /Showing records\s+(\d+)\s*[\-–]\s*(\d+)\s+of\s+(\d+)\s+total matches?\.?$/i
  );
  const parent = report ? report.parentElement : null;
  const rowCount = parent
    ? Array.from(parent.children).filter(element => element.matches(".result") && visible(element)).length
    : 0;
  const selectedValue = name => {
    const elements = Array.from(document.querySelectorAll(`select[name="${name}"]`)).filter(visible);
    return { count: elements.length, value: elements.length === 1 ? String(elements[0].value || "") : "" };
  };
  const inputValue = name => {
    const elements = Array.from(document.querySelectorAll(`input[name="${name}"]`)).filter(visible);
    return { count: elements.length, value: elements.length === 1 ? String(elements[0].value || "") : "" };
  };
  const cc = Array.from(document.querySelectorAll("input[name='cc_only']")).filter(visible);
  const titleText = normalize(document.title);
  const pageStatusText = Array.from(
    document.querySelectorAll(".error, .error_message, [role='alert']")
  ).filter(visible).map(element => normalize(element.textContent)).join(" ");
  const statusText = normalize(`${titleText} ${pageStatusText}`);
  const challenge = /just a moment|attention required|verify you are human/i.test(titleText) ||
    Boolean(document.querySelector("#challenge-running, iframe[src*='challenges.cloudflare.com']"));
  const busy = /server too busy|please slow down/i.test(statusText);
  const syntaxError = /syntax|could not parse|invalid query|search error/i.test(statusText);
  return {
    host: window.location.hostname,
    path: window.location.pathname,
    protocol: window.location.protocol,
    urlQueryExact: new URL(window.location.href).searchParams.get("q") === payload.query,
    urlFormExact: new URL(window.location.href).searchParams.get("form") === "basic",
    urlParameterNames: Array.from(new URL(window.location.href).searchParams.keys()).sort(),
    reportCount: reports.length,
    queryEchoExact: Boolean(report) && reportText.startsWith(expectedPrefix),
    rangeParsed: Boolean(rangeMatch),
    rangeStart: rangeMatch ? Number(rangeMatch[1]) : null,
    rangeEnd: rangeMatch ? Number(rangeMatch[2]) : null,
    total: rangeMatch ? Number(rangeMatch[3]) : null,
    rowCount,
    sort: selectedValue("sortby"),
    pageSize: selectedValue("pagesize"),
    language: selectedValue("language"),
    country: selectedValue("country"),
    earliest: inputValue("earliest"),
    latest: inputValue("latest"),
    ccCount: cc.length,
    ccChecked: cc.length === 1 ? Boolean(cc[0].checked) : null,
    challenge,
    busy,
    syntaxError,
    ready: challenge || busy || syntaxError || Boolean(rangeMatch)
  };
}
"""


class GateError(Exception):
    """Expected fail-closed gate error with a fixed serializable code."""

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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if manifest.get("protocol_version") != "1.6" or manifest.get("artifact_class") != "frozen_validation_contract_not_search_output":
        raise InputGateError("The pinned query manifest has the wrong protocol boundary.")
    sources = manifest.get("sources")
    if not isinstance(sources, dict):
        raise InputGateError("The pinned query manifest has an invalid source registry type.")
    source = sources.get(SOURCE_KEY)
    if not isinstance(source, dict):
        raise InputGateError("The pinned query manifest has an invalid OATD source type.")
    controls = source.get("controls")
    if not isinstance(controls, dict):
        raise InputGateError("The OATD source/control contract differs from the wrapper.")
    if source.get("fixed_search_url") != SEARCH_URL or controls != {
        "form": "basic",
        "sort": "Relevance",
        "page_size": 30,
        "native_date_filter": False,
        "native_language_filter": False,
        "country_filter": False,
        "institution_filter": False,
        "creative_commons_only": False,
        "access_limiter": False,
        "wildcards_permitted": False,
    }:
        raise InputGateError("The OATD source/control contract differs from the wrapper.")
    entries = source.get("queries")
    if not isinstance(entries, list):
        raise InputGateError("The OATD query registry is not a list.")
    indexed: dict[str, dict[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise InputGateError("The OATD query registry contains a malformed entry.")
        query_id = entry.get("query_id")
        query = entry.get("query")
        digest = entry.get("query_sha256")
        if (
            query_id not in QUERY_IDS
            or entry.get("source_body_id") != query_id
            or not isinstance(query, str)
            or not query.strip()
            or "*" in query
            or "?" in query
            or not isinstance(digest, str)
            or hashlib.sha256(query.encode("utf-8")).hexdigest() != digest
            or query_id in indexed
        ):
            raise InputGateError("The OATD query registry differs from the finite frozen contract.")
        indexed[query_id] = {"query": query, "query_sha256": digest}
    if tuple(indexed) != QUERY_IDS:
        raise InputGateError("The OATD query registry ID/order contract differs.")
    return indexed


def build_search_url(query: str) -> str:
    return f"{SEARCH_URL}?{urlencode({'q': query, 'form': 'basic'})}"


def parse_count_state(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProtocolGateError("invalid_state")
    required_bools = (
        "urlQueryExact", "urlFormExact", "queryEchoExact", "rangeParsed",
        "challenge", "busy", "syntaxError", "ready",
    )
    if any(not isinstance(payload.get(key), bool) for key in required_bools):
        raise ProtocolGateError("invalid_boolean_state")
    if payload["challenge"] or payload["busy"]:
        raise AccessGateError("busy_or_challenge")
    if payload["syntaxError"]:
        raise ProtocolGateError("syntax_error")
    if payload.get("protocol") != "https:" or str(payload.get("host", "")).casefold() != "oatd.org" or payload.get("path") != "/oatd/search":
        raise ProtocolGateError("route_mismatch")
    if payload.get("urlParameterNames") != ["form", "q"] or not payload["urlQueryExact"] or not payload["urlFormExact"]:
        raise ProtocolGateError("query_or_form_rewrite")
    if payload.get("reportCount") != 1 or not payload["queryEchoExact"] or not payload["rangeParsed"]:
        raise ProtocolGateError("aggregate_or_echo_missing")
    integers = ("rangeStart", "rangeEnd", "total", "rowCount")
    if any(isinstance(payload.get(key), bool) or not isinstance(payload.get(key), int) for key in integers):
        raise ProtocolGateError("invalid_aggregate_state")
    total = payload["total"]
    start = payload["rangeStart"]
    end = payload["rangeEnd"]
    rows = payload["rowCount"]
    if total < 1:  # native zero remains deliberately unvalidated in this wrapper
        raise ProtocolGateError("native_zero_unvalidated")
    if start != 1 or end != min(total, 30) or rows != end:
        raise ProtocolGateError("range_row_mismatch")

    def exact_control(name: str, value: str) -> None:
        state = payload.get(name)
        if not isinstance(state, dict) or state.get("count") != 1 or state.get("value") != value:
            raise ProtocolGateError(f"{name}_control_mismatch")

    exact_control("sort", "relevanace")
    exact_control("pageSize", "30")
    exact_control("language", "")
    exact_control("country", "")
    exact_control("earliest", "")
    exact_control("latest", "")
    if payload.get("ccCount") != 1 or payload.get("ccChecked") is not False:
        raise ProtocolGateError("cc_control_mismatch")
    return {
        "source_total": total,
        "displayed_range_start": start,
        "displayed_range_end": end,
        "result_container_count": rows,
        "observed": {
            "basic_get": True,
            "query_echo_exact": True,
            "sort": "Relevance",
            "page_size": 30,
            "native_date_filter": False,
            "native_language_filter": False,
            "country_filter": False,
            "creative_commons_only": False,
        },
    }


def success_artifact(query_id: str, query_sha256: str, state: dict[str, Any], *, started_at: str, completed_at: str) -> dict[str, Any]:
    return {
        "artifact_kind": "oatd_basic_count_gate",
        "artifact_class": "pilot_not_candidate_search",
        "protocol_version": "1.6",
        "source": SOURCE_NAME,
        "canonical_source": SOURCE_KEY,
        "query_id": query_id,
        "query_manifest_sha256": QUERY_MANIFEST_SHA256,
        "query_body_sha256": query_sha256,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "status": "success",
        "failure_code": None,
        "source_total": state["source_total"],
        "displayed_range_start": state["displayed_range_start"],
        "displayed_range_end": state["displayed_range_end"],
        "result_container_count": state["result_container_count"],
        "observed": state["observed"],
        "candidate_records_serialized": 0,
        "results_retrieved": 0,
        "merge_input": False,
        "candidate_import_allowed": False,
        "automatic_retries": 0,
        "unvalidated": [
            "native_zero", "pagination", "source_record_identity", "record_capture",
            "normalization", "date_language_cutoff",
        ],
    }


def failure_artifact(query_id: str, query_sha256: str, error: GateError, *, started_at: str | None, completed_at: str) -> dict[str, Any]:
    return {
        "artifact_kind": "oatd_basic_count_gate",
        "artifact_class": "pilot_not_candidate_search",
        "protocol_version": "1.6",
        "source": SOURCE_NAME,
        "canonical_source": SOURCE_KEY,
        "query_id": query_id,
        "query_manifest_sha256": QUERY_MANIFEST_SHA256,
        "query_body_sha256": query_sha256,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "status": "error",
        "failure_code": error.code,
        "source_total": None,
        "candidate_records_serialized": 0,
        "results_retrieved": 0,
        "merge_input": False,
        "candidate_import_allowed": False,
        "automatic_retries": 0,
    }


def validate_artifact_allowlist(artifact: dict[str, Any]) -> None:
    forbidden = {
        "title", "author", "authors", "abstract", "snippet", "recordid", "record_id",
        "repository", "url", "href", "results", "records", "cookie", "token", "session",
        "csrf", "accountid", "cdp_url", "raw_error",
    }
    for key in artifact:
        if key.casefold() in forbidden:
            raise ProtocolGateError("forbidden_output_field")
    serialized = json.dumps(artifact, sort_keys=True).casefold()
    for marker in ("?token=", "searchid", "sessionid", "accountid=", "cookie="):
        if marker in serialized:
            raise ProtocolGateError("sensitive_output_marker")


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
            # The final link is already immutable; only the owned temp leaked.


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
            raise LockGateError("Another OATD count gate owns the source lock.") from error
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


async def run_browser_gate(query: str, *, cdp_url: str, timeout_seconds: float) -> dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:  # pragma: no cover
        raise ProtocolGateError("playwright_unavailable") from error
    browser = None
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
            try:
                await page.goto(build_search_url(query), wait_until="domcontentloaded", timeout=int(timeout_seconds * 1000))
            except Exception as error:  # Navigation failures map to the bounded timeout state.
                raise TimeoutGateError("navigation_timeout") from error
            deadline = asyncio.get_running_loop().time() + timeout_seconds
            while True:
                try:
                    payload = await page.evaluate(OATD_COUNT_STATE_SCRIPT, {"query": query})
                    if isinstance(payload, dict) and payload.get("ready") is True:
                        return parse_count_state(payload)
                except GateError:
                    raise
                except Exception:  # noqa: BLE001 - transient DOM polling can race page hydration; retry to deadline.
                    payload = None
                if asyncio.get_running_loop().time() >= deadline:
                    raise TimeoutGateError("state_timeout")
                await asyncio.sleep(0.1)
    finally:
        if page is not None:
            try:
                await page.close()
            except Exception:  # noqa: BLE001 - suppress only cleanup failure for this wrapper-owned page.
                page = None
        # The wrapper always attaches to the user's authorized local Chrome.
        # Closing the owned page is sufficient; the shared browser and context
        # remain open for their owner.


def valid_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be numeric") from error
    if not math.isfinite(parsed) or parsed <= 0 or parsed > 300:
        raise argparse.ArgumentTypeError("timeout must be finite and in (0, 300]")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate one frozen OATD query's basic-interface aggregate only.")
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
        artifact = failure_artifact(
            query_id,
            query_sha256,
            error,
            started_at=started_at,
            completed_at=utc_now(),
        )
        validate_artifact_allowlist(artifact)
        atomic_write_json(Path(output_path), artifact)
    except Exception:  # noqa: BLE001, S110 - a failed artifact destination must not expose an exception or overwrite it.
        pass
    try:
        print(f"OATD count gate failed closed: {error.code}")
    except OSError:
        pass
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    started_at: str | None = None
    query_sha256 = ""
    try:
        queries = load_frozen_queries()
        entry = queries[args.query_id]
        query_sha256 = entry["query_sha256"]
        cdp_url = validate_local_cdp_url(args.cdp_url)
        with exclusive_source_lock():
            started_at = utc_now()
            state = asyncio.run(run_browser_gate(entry["query"], cdp_url=cdp_url, timeout_seconds=args.timeout_seconds))
        artifact = success_artifact(
            args.query_id,
            query_sha256,
            state,
            started_at=started_at,
            completed_at=utc_now(),
        )
        validate_artifact_allowlist(artifact)
        atomic_write_json(Path(args.output_path), artifact)
    except GateError as error:
        return _fail_closed_exit(
            query_id=args.query_id,
            query_sha256=query_sha256,
            output_path=args.output_path,
            error=error,
            started_at=started_at,
        )
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:  # noqa: BLE001 - every ordinary browser, CDP, or filesystem failure exits fail-closed.
        return _fail_closed_exit(
            query_id=args.query_id,
            query_sha256=query_sha256,
            output_path=args.output_path,
            error=GateError(),
            started_at=started_at,
        )
    try:
        print(f"OATD count gate passed for {args.query_id}; aggregate only, no records serialized.")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
