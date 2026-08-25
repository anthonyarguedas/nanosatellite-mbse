#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

"""Public-only, failure-closed local-harvest utilities for ESA Indico.

This is intentionally a review-specific helper, not a replacement for the
shared academic-search adapter.  It has no query-language implementation and
never treats Indico's one-box search as a Boolean source.  It works from the
public category/event exports plus public event/contribution HTML pages, keeps
PDF bytes outside a Git worktree, and writes only safe ledgers by default.

The commands require explicit bounded inputs.  They do not discover or import
final candidates and do not run an unbounded harvest by default.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import (
    parse_qsl,
    quote,
    unquote,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)
from urllib.request import HTTPRedirectHandler, Request, build_opener

ORIGIN = "https://indico.esa.int"
HOST = "indico.esa.int"
SEARCH_ENDPOINT_PATH = "/search/api/search"
USER_AGENT = (
    "SLR1-ESA-Indico-local-harvest/0.1 "
    "(public-only; contact review operator through documented review materials)"
)
DEFAULT_TIMEOUT_SECONDS = 45.0
DEFAULT_MIN_REQUEST_INTERVAL = 0.5
DEFAULT_RETRIES = 2
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}
ACCESS_HTTP = {401, 403, 418}
EVENT_EXPORT_DETAIL = "subcontributions"
ACCESS_STATUSES = {
    "public_pdf",
    "public_non_pdf",
    "access_unverified",
    "access_restricted_or_login",
    "other_failure",
    "export_listed_public",
    "protected_not_public",
}
SENSITIVE_QUERY_KEYS = {
    "apikey",
    "auth",
    "authorization",
    "token",
    "access_token",
    "session",
    "sessionid",
    "searchid",
    "searchsession",
    "cookie",
    "csrf",
    "password",
    "secret",
    "signature",
    "sig",
}
ATTACHMENT_PATH = re.compile(
    r"(?P<path>/event/(?P<event_id>\d+)/"
    r"(?:(?:contributions/(?P<contribution_id>\d+)/))?"
    r"attachments/(?P<folder_id>\d+)/(?P<attachment_id>\d+)/(?P<filename>[^\s\"'<>?#]+))",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
WHITESPACE_RE = re.compile(r"\s+")
HTML_TAG_RE = re.compile(r"<[^>]+>")
HYPHEN_FAMILY = "‐‑‒–—―−"


class HarvestError(RuntimeError):
    """Base class for expected, non-zero ESA harvest outcomes."""


class InputError(HarvestError):
    """The requested bounded operation is unsafe or malformed."""


class AccessError(HarvestError):
    """A public route redirected to, or returned, an access-control response."""


class TransportError(HarvestError):
    """A public route did not return an acceptable transport response."""


class ParseError(HarvestError):
    """A returned public representation did not match the validated shape."""


class CoverageError(HarvestError):
    """A ledger could not prove complete coverage for its stated bounded input."""


class IdentityError(HarvestError):
    """A source object lacked a stable identity or conflicted with a duplicate."""


class PdfError(HarvestError):
    """A public PDF could not be safely downloaded or text-extracted."""


def now_iso() -> str:
    """Return an ISO timestamp with the local explicit offset, to seconds."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def write_json(path: Path, payload: Mapping[str, Any] | Sequence[Any]) -> None:
    """Atomically persist UTF-8 JSON without exposing a partially written ledger."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalized_query_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", unquote(value).casefold())


def canonical_public_url(value: str) -> str:
    """Return a strict public ESA URL or raise before any request is made."""
    if not isinstance(value, str) or not value.strip():
        raise InputError("A non-empty public ESA URL is required")
    resolved = urljoin(f"{ORIGIN}/", value)
    parsed = urlsplit(resolved)
    if (
        parsed.scheme != "https"
        or parsed.hostname != HOST
        or parsed.username
        or parsed.password
    ):
        raise InputError("Only public https://indico.esa.int routes are permitted")
    if parsed.fragment:
        raise InputError("Fragments are not permitted in public harvest routes")
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if normalized_query_key(key) in {
            normalized_query_key(item) for item in SENSITIVE_QUERY_KEYS
        }:
            raise InputError(
                "A route contained a sensitive or state-bearing query parameter"
            )
    return urlunsplit(("https", HOST, parsed.path, parsed.query, ""))


def route_path(url: str) -> str:
    """Return the safe public path and benign query, never a browser/session URL."""
    parsed = urlsplit(canonical_public_url(url))
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def event_export_url(event_id: str, *, detail: str = EVENT_EXPORT_DETAIL) -> str:
    """Return a documented event-export detail route without accepting arbitrary syntax."""
    if detail not in {"contributions", "subcontributions", "sessions"}:
        raise InputError("Unsupported ESA event-export detail level")
    return canonical_public_url(
        f"/export/event/{quote(event_id, safe='')}.json?detail={quote(detail, safe='')}"
    )


def category_export_url(category_id: str, from_date: str, to_date: str) -> str:
    query = urlencode({"from": from_date, "to": to_date})
    return canonical_public_url(
        f"/export/categ/{quote(category_id, safe='')}.json?{query}"
    )


def event_page_url(event_id: str) -> str:
    return canonical_public_url(f"/event/{quote(event_id, safe='')}/")


def contribution_page_url(event_id: str, contribution_id: str) -> str:
    return canonical_public_url(
        f"/event/{quote(event_id, safe='')}/contributions/{quote(contribution_id, safe='')}/"
    )


def require_identifier(value: Any, label: str) -> str:
    if value is None or isinstance(value, bool):
        raise IdentityError(f"Missing {label}")
    result = str(value).strip()
    if not result:
        raise IdentityError(f"Missing {label}")
    return result


def as_list(value: Any, label: str, *, allow_null: bool = True) -> list[Any]:
    if value is None and allow_null:
        return []
    if isinstance(value, list):
        return value
    raise ParseError(f"ESA export field {label!r} was not a list")


def clean_source_text(value: Any) -> str:
    """Normalize source text only for local deterministic matching, not display."""
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = HTML_TAG_RE.sub(" ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def metadata_fields(record: Mapping[str, Any]) -> dict[str, str]:
    """Use only one source object's fields without joining keyword-value boundaries."""
    fields = {
        "title": clean_source_text(record.get("title")),
        "description": clean_source_text(record.get("description")),
    }
    keywords = record.get("keywords")
    if keywords is None:
        fields["keywords"] = ""
    elif isinstance(keywords, list):
        for index, value in enumerate(keywords):
            if value is not None:
                fields[f"keywords[{index}]"] = clean_source_text(value)
    else:
        fields["keywords"] = clean_source_text(keywords)
    return fields


class NoRedirect(HTTPRedirectHandler):
    """Fail rather than following a public route into another context."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


@dataclass
class PublicResponse:
    url: str
    path: str
    content_type: str
    body: bytes
    receipt: dict[str, Any]


class PublicClient:
    """Anonymous, rate-limited, no-redirect HTTP client for public ESA routes."""

    def __init__(
        self,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
        retries: int = DEFAULT_RETRIES,
        sleep=time.sleep,
        opener: Any | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise InputError("timeout_seconds must be positive")
        if min_request_interval < 0:
            raise InputError("min_request_interval cannot be negative")
        if retries < 0:
            raise InputError("retries cannot be negative")
        self.timeout_seconds = timeout_seconds
        self.min_request_interval = min_request_interval
        self.retries = retries
        self.sleep = sleep
        self.opener = opener or build_opener(NoRedirect())
        self._last_request_finished: float | None = None

    def _throttle(self) -> None:
        if self._last_request_finished is None:
            return
        remaining = self.min_request_interval - (
            time.monotonic() - self._last_request_finished
        )
        if remaining > 0:
            self.sleep(remaining)

    @staticmethod
    def _close_quietly(response: Any | None) -> None:
        """Close a successful or HTTP-error response without inspecting its body."""
        if response is None:
            return
        close = getattr(response, "close", None)
        if callable(close):
            close()

    @staticmethod
    def _is_access_handoff_status(status: int) -> bool:
        return 300 <= status < 400 or status in ACCESS_HTTP

    @staticmethod
    def _looks_like_access_wall(prefix: bytes) -> bool:
        lowered = prefix.lower()
        markers = (
            b"login",
            b"log in",
            b"sign in",
            b"access denied",
            b"captcha",
            b"challenge",
        )
        return any(marker in lowered for marker in markers)

    def _safe_access_receipt(
        self,
        canonical: str,
        *,
        http_status: int | None,
        access_status: str,
        observed_content_type: str | None = None,
    ) -> dict[str, Any]:
        if access_status not in ACCESS_STATUSES:
            raise AssertionError("Unexpected public-material access status")
        receipt = {
            "request_method": "GET",
            "request_path": route_path(canonical),
            "http_status": http_status,
            "redirects_followed": 0,
            "access_status": access_status,
            "observed_at": now_iso(),
            "response_headers_retained": False,
            "response_body_retained": False,
            "redirect_target_retained": False,
        }
        if observed_content_type:
            # This is a derived media-type classification, not a retained header.
            receipt["observed_content_type"] = observed_content_type
        return receipt

    def get(self, url: str, *, accept: str) -> PublicResponse:
        canonical = canonical_public_url(url)
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            self._throttle()
            request = Request(
                canonical,
                method="GET",
                headers={
                    "Accept": accept,
                    "Accept-Language": "en-US,en;q=0.9",
                    "User-Agent": USER_AGENT,
                },
            )
            response: Any | None = None
            error_response: Any | None = None
            try:
                response = self.opener.open(request, timeout=self.timeout_seconds)
                status = int(getattr(response, "status", response.getcode()))
                final_url = str(response.geturl())
                if final_url != canonical or self._is_access_handoff_status(status):
                    raise AccessError(
                        "A public ESA route redirected or entered an access handoff"
                    )
                if not 200 <= status < 300:
                    raise TransportError(f"Public ESA route returned HTTP {status}")
                body = response.read()
                headers = getattr(response, "headers", {})
                content_type = str(headers.get("Content-Type", ""))
                observed_at = now_iso()
                receipt = {
                    "request_method": "GET",
                    "request_path": route_path(canonical),
                    "http_status": status,
                    "content_type": content_type,
                    "response_bytes": len(body),
                    "response_sha256": sha256_bytes(body),
                    "observed_at": observed_at,
                    "redirects_followed": 0,
                }
                return PublicResponse(
                    url=canonical,
                    path=route_path(canonical),
                    content_type=content_type,
                    body=body,
                    receipt=receipt,
                )
            except HTTPError as error:
                error_response = error
                status = int(error.code)
                last_error = error
                if self._is_access_handoff_status(status):
                    raise AccessError(
                        f"Public ESA route entered an access handoff at HTTP {status}"
                    ) from error
                if status in RETRYABLE_HTTP and attempt < self.retries:
                    self.sleep(min(60.0, 2.0**attempt))
                    continue
                raise TransportError(
                    f"Public ESA route returned HTTP {status}"
                ) from error
            except (URLError, TimeoutError, OSError) as error:
                last_error = error
                if attempt < self.retries:
                    self.sleep(min(60.0, 2.0**attempt))
                    continue
                raise TransportError(
                    "Could not retrieve the public ESA route"
                ) from error
            finally:
                self._last_request_finished = time.monotonic()
                self._close_quietly(response)
                if error_response is not response:
                    self._close_quietly(error_response)
        raise TransportError(
            "Public ESA route did not return a response"
        ) from last_error

    def probe_access_status(self, url: str) -> dict[str, Any]:
        """Safely classify one direct material GET without retaining headers or body."""
        canonical = canonical_public_url(url)
        for attempt in range(self.retries + 1):
            self._throttle()
            request = Request(
                canonical,
                method="GET",
                headers={
                    "Accept": "application/pdf,*/*;q=0.1",
                    "Accept-Language": "en-US,en;q=0.9",
                    "User-Agent": USER_AGENT,
                },
            )
            response: Any | None = None
            error_response: Any | None = None
            try:
                response = self.opener.open(request, timeout=self.timeout_seconds)
                status = int(getattr(response, "status", response.getcode()))
                final_url = str(response.geturl())
                if final_url != canonical or self._is_access_handoff_status(status):
                    return self._safe_access_receipt(
                        canonical,
                        http_status=status,
                        access_status="access_restricted_or_login",
                    )
                if not 200 <= status < 300:
                    return self._safe_access_receipt(
                        canonical, http_status=status, access_status="other_failure"
                    )
                content_type = str(
                    getattr(response, "headers", {}).get("Content-Type", "")
                ).casefold()
                prefix = response.read(4096)
                if self._looks_like_access_wall(prefix):
                    access_status = "access_restricted_or_login"
                elif "application/pdf" in content_type:
                    access_status = (
                        "public_pdf" if prefix.startswith(b"%PDF-") else "other_failure"
                    )
                elif prefix.startswith(b"%PDF-"):
                    # A PDF magic header with a non-PDF media type is not a valid
                    # public-PDF confirmation and must be investigated, not guessed.
                    access_status = "other_failure"
                else:
                    access_status = "public_non_pdf"
                return self._safe_access_receipt(
                    canonical,
                    http_status=status,
                    access_status=access_status,
                    observed_content_type=content_type or None,
                )
            except HTTPError as error:
                error_response = error
                status = int(error.code)
                if self._is_access_handoff_status(status):
                    return self._safe_access_receipt(
                        canonical,
                        http_status=status,
                        access_status="access_restricted_or_login",
                    )
                if status in RETRYABLE_HTTP and attempt < self.retries:
                    self.sleep(min(60.0, 2.0**attempt))
                    continue
                return self._safe_access_receipt(
                    canonical, http_status=status, access_status="other_failure"
                )
            except (URLError, TimeoutError, OSError):
                if attempt < self.retries:
                    self.sleep(min(60.0, 2.0**attempt))
                    continue
                return self._safe_access_receipt(
                    canonical, http_status=None, access_status="other_failure"
                )
            finally:
                self._last_request_finished = time.monotonic()
                self._close_quietly(response)
                if error_response is not response:
                    self._close_quietly(error_response)
        raise AssertionError("Access-status probe exhausted without a terminal receipt")

    def get_json(self, url: str) -> tuple[Any, dict[str, Any]]:
        response = self.get(url, accept="application/json, text/plain, */*")
        if "json" not in response.content_type.casefold():
            raise ParseError("A public ESA export did not identify itself as JSON")
        try:
            return json.loads(response.body.decode("utf-8")), response.receipt
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ParseError(
                "A public ESA export did not contain valid UTF-8 JSON"
            ) from error

    def get_html(self, url: str) -> tuple[str, dict[str, Any]]:
        response = self.get(
            url, accept="text/html,application/xhtml+xml;q=0.9,*/*;q=0.1"
        )
        if "html" not in response.content_type.casefold():
            raise ParseError("A public ESA event page did not identify itself as HTML")
        return response.body.decode("utf-8", errors="replace"), response.receipt

    def download_pdf(self, url: str, secure_dir: Path) -> dict[str, Any]:
        """Download/checkpoint one public PDF outside Git, keyed by its public route."""
        ensure_secure_directory(secure_dir)
        canonical = canonical_public_url(url)
        source_key = route_path(canonical)
        index_path = secure_dir / "pdf-source-index.json"
        index: dict[str, Any] = {}
        if index_path.exists():
            loaded = load_json(index_path)
            if not isinstance(loaded, dict) or not isinstance(
                loaded.get("sources", {}), dict
            ):
                raise PdfError("Secure PDF checkpoint index had an invalid shape")
            index = loaded
        sources = index.setdefault("sources", {})
        previous = sources.get(source_key)
        if isinstance(previous, Mapping) and isinstance(
            previous.get("pdf_sha256"), str
        ):
            digest = previous["pdf_sha256"]
            existing_path = secure_dir / f"sha256-{digest}.pdf"
            if existing_path.exists() and sha256_file(existing_path) == digest:
                return {
                    "download_state": "reused_checkpoint",
                    "pdf_sha256": digest,
                    "pdf_bytes": existing_path.stat().st_size,
                    "secure_location_reference": f"sha256:{digest}",
                    "receipt": None,
                    "_secure_path": existing_path,
                }
            raise PdfError("Secure PDF checkpoint did not reconcile to its hashed PDF")

        response = self.get(canonical, accept="application/pdf")
        if "application/pdf" not in response.content_type.casefold():
            raise PdfError(
                "A direct material route did not identify itself as application/pdf"
            )
        if not response.body.startswith(b"%PDF-"):
            raise PdfError("A direct material route did not begin with a PDF signature")
        digest = sha256_bytes(response.body)
        final_path = secure_dir / f"sha256-{digest}.pdf"
        if final_path.exists():
            existing_digest = sha256_file(final_path)
            if existing_digest != digest:
                raise PdfError("An existing secure PDF path had a conflicting checksum")
        else:
            temporary = secure_dir / f".{final_path.name}.part"
            with temporary.open("wb") as handle:
                handle.write(response.body)
            os.replace(temporary, final_path)
        sources[source_key] = {
            "pdf_sha256": digest,
            "pdf_bytes": len(response.body),
            "updated_at": now_iso(),
        }
        index["checkpoint_schema_version"] = "esa-indico-secure-pdf-checkpoint/v1"
        write_json(index_path, index)
        return {
            "download_state": "downloaded",
            "pdf_sha256": digest,
            "pdf_bytes": len(response.body),
            "secure_location_reference": f"sha256:{digest}",
            "receipt": response.receipt,
            "_secure_path": final_path,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_ancestor(path: Path) -> Path | None:
    current = path.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def ensure_secure_directory(path: Path) -> None:
    """Reject PDF/source-text retention beneath a Git checkout."""
    if git_ancestor(path) is not None:
        raise InputError("Secure PDF/text storage must be outside a Git worktree")
    path.mkdir(parents=True, exist_ok=True)


def parse_date_argument(value: str, label: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise InputError(f"{label} must be ISO date YYYY-MM-DD") from error


def probe_public_search(
    client: PublicClient,
    *,
    query: str,
    result_type: str,
) -> dict[str, Any]:
    """Capture a bounded, non-screening one-box route observation without titles/text."""
    if not isinstance(query, str) or not query.strip():
        raise InputError("Search probe query must be non-empty")
    source_types = {
        "events": ["event"],
        "contributions": ["contribution", "subcontribution"],
        "materials": ["attachment"],
    }.get(result_type)
    if source_types is None:
        raise InputError(
            "Search probe result_type must be events, contributions, or materials"
        )
    params: list[tuple[str, str]] = [("q", query)] + [
        ("type", item) for item in source_types
    ]
    payload, receipt = client.get_json(
        canonical_public_url(f"{SEARCH_ENDPOINT_PATH}?{urlencode(params)}")
    )
    if not isinstance(payload, Mapping):
        raise ParseError("Public search did not return an object")
    total = payload.get("total")
    results = payload.get("results")
    pagenav = payload.get("pagenav")
    if isinstance(total, bool) or not isinstance(total, int) or total < -1:
        raise ParseError("Public search total was not an accepted integer/-1")
    if not isinstance(results, list) or not isinstance(pagenav, Mapping):
        raise ParseError("Public search lacked results or pagination metadata")
    rows: list[dict[str, Any]] = []
    for raw in results:
        if not isinstance(raw, Mapping):
            raise ParseError("Public search contained a non-object result")
        source_type = clean_source_text(raw.get("type")).casefold()
        if source_type not in source_types:
            raise ParseError("Public search returned an unexpected source result type")
        event_id = require_identifier(raw.get("event_id"), "search result event id")
        row: dict[str, Any] = {"source_type": source_type, "event_id": event_id}
        if source_type == "event":
            row["stable_result_id"] = f"event:{event_id}"
        elif source_type == "contribution":
            contribution_id = require_identifier(
                raw.get("contribution_id"), "search contribution id"
            )
            row["contribution_id"] = contribution_id
            row["stable_result_id"] = f"event:{event_id}:contribution:{contribution_id}"
        elif source_type == "subcontribution":
            contribution_id = require_identifier(
                raw.get("contribution_id"), "search contribution id"
            )
            sub_id = require_identifier(
                raw.get("subcontribution_id"), "search subcontribution id"
            )
            row["contribution_id"] = contribution_id
            row["subcontribution_id"] = sub_id
            row["stable_result_id"] = (
                f"event:{event_id}:contribution:{contribution_id}:subcontribution:{sub_id}"
            )
        else:
            attachment_id = require_identifier(
                raw.get("attachment_id"), "search attachment id"
            )
            row["attachment_id"] = attachment_id
            row["stable_result_id"] = f"event:{event_id}:attachment:{attachment_id}"
        rows.append(row)
    return {
        "probe_schema_version": "esa-indico-one-box-search-probe/v1",
        "operation": "bounded_non_screening_public_search_probe",
        "query": query,
        "result_type": result_type,
        "source_search_types": source_types,
        "source_reported_total": total if total >= 0 else None,
        "source_reported_total_status": "exact"
        if total >= 0
        else "unavailable_minus_one",
        "retrieved_first_page_rows": len(rows),
        "next_page_present": pagenav.get("next") is not None,
        "rows": rows,
        "receipt": receipt,
    }


def enumerate_category_window(
    client: PublicClient,
    *,
    category_id: str,
    from_date: str,
    to_date: str,
) -> dict[str, Any]:
    """Enumerate one bounded root-category window and reconcile count to rows."""
    start = parse_date_argument(from_date, "from_date")
    end = parse_date_argument(to_date, "to_date")
    if start > end:
        raise InputError("from_date cannot be later than to_date")
    payload, receipt = client.get_json(category_export_url(category_id, start, end))
    if not isinstance(payload, Mapping):
        raise ParseError("Category export did not return an object")
    count = payload.get("count")
    results = payload.get("results")
    complete_flag = payload.get("complete")
    if complete_flag is not None and not isinstance(complete_flag, bool):
        raise ParseError("Category export complete flag was not boolean/null")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ParseError("Category export count was not a non-negative integer")
    if not isinstance(results, list):
        raise ParseError("Category export results was not a list")
    if count != len(results):
        raise CoverageError(
            f"Category export reported {count} event(s) but returned {len(results)} row(s)"
        )

    event_rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in results:
        if not isinstance(raw, Mapping):
            raise ParseError("Category export contained a non-object event row")
        event_id = require_identifier(raw.get("id"), "category-export event id")
        if event_id in seen_ids:
            raise IdentityError(f"Category export repeated event id {event_id}")
        seen_ids.add(event_id)
        source_url = canonical_public_url(
            str(raw.get("url") or event_page_url(event_id))
        )
        expected_path = f"/event/{event_id}/"
        if urlsplit(source_url).path != expected_path:
            raise IdentityError(
                "Category export event URL did not match its stable event id"
            )
        event_rows.append(
            {
                "event_id": event_id,
                "category_id": require_identifier(raw.get("categoryId"), "category id"),
                "start_date": raw.get("startDate"),
                "end_date": raw.get("endDate"),
                "source_route_path": route_path(source_url),
            }
        )

    return {
        "ledger_schema_version": "esa-indico-category-window/v1",
        "operation": "bounded_public_category_export",
        "source_boundary": f"public ESA Indico category-{category_id} export only",
        "category_id": str(category_id),
        "from_date": start,
        "to_date": end,
        "source_reported_total": count,
        "retrieved_total": len(event_rows),
        "totals_reconciled": True,
        "source_complete_flag": complete_flag,
        "source_complete_flag_status": (
            "reported_true" if complete_flag is True else "reported_false" if complete_flag is False else "absent_or_null"
        ),
        "event_rows": event_rows,
        "receipt": receipt,
    }


def direct_attachment_from_url(url: str) -> dict[str, str]:
    """Parse one public direct attachment path into stable components."""
    canonical = canonical_public_url(url)
    match = ATTACHMENT_PATH.search(urlsplit(canonical).path)
    if not match:
        raise ParseError(
            "A material URL did not use the observed public attachment path shape"
        )
    parsed = match.groupdict()
    if match.group("path") != urlsplit(canonical).path:
        raise ParseError("A material URL contained unvalidated trailing path content")
    return {
        "event_id": parsed["event_id"],
        "contribution_id": parsed.get("contribution_id") or "",
        "folder_id": parsed["folder_id"],
        "attachment_id": parsed["attachment_id"],
        "filename": unquote(parsed["filename"]),
        "download_url": canonical,
        "route_path": route_path(canonical),
    }


def extract_attachment_links(
    page_html: str, expected_event_id: str
) -> list[dict[str, str]]:
    """Extract direct attachment links from one public static event/contribution page."""
    decoded = html.unescape(page_html)
    found: dict[str, dict[str, str]] = {}
    for match in ATTACHMENT_PATH.finditer(decoded):
        path = match.group("path")
        parsed = direct_attachment_from_url(path)
        if parsed["event_id"] != str(expected_event_id):
            continue
        previous = found.get(parsed["attachment_id"])
        if previous is not None and previous["download_url"] != parsed["download_url"]:
            raise IdentityError(
                "The same static attachment id had conflicting direct URLs"
            )
        found[parsed["attachment_id"]] = parsed
    return [
        found[key]
        for key in sorted(found, key=lambda item: int(item) if item.isdigit() else item)
    ]


def collect_attachment_mappings(value: Any) -> list[Mapping[str, Any]]:
    """Traverse documented material containers, including legacy material.resources."""
    collected: list[Mapping[str, Any]] = []

    def resource_mapping(
        resource: Mapping[str, Any], material: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Attach safe legacy-material metadata to a resource without changing its ID."""
        enriched = dict(resource)
        enriched["_legacy_material_resource"] = True
        if not enriched.get("filename"):
            enriched["filename"] = resource.get("name")
        if not enriched.get("title"):
            enriched["title"] = (
                resource.get("title") or material.get("title") or resource.get("name")
            )
        if not enriched.get("description"):
            enriched["description"] = material.get("description")
        if not enriched.get("content_type"):
            enriched["content_type"] = material.get("content_type")
        for key in ("is_protected", "size"):
            if enriched.get(key) is None and material.get(key) is not None:
                enriched[key] = material.get(key)
        return enriched

    def walk(item: Any) -> None:
        if item is None:
            return
        if isinstance(item, list):
            for child in item:
                walk(child)
            return
        if not isinstance(item, Mapping):
            raise ParseError("A material container contained a non-object value")
        if "resources" in item:
            resources = as_list(
                item.get("resources"), "material.resources", allow_null=False
            )
            for resource in resources:
                if not isinstance(resource, Mapping):
                    raise ParseError("A legacy material resource was not an object")
                collected.append(resource_mapping(resource, item))
            # A legacy material wrapper has its own ID/title but each resource,
            # not the wrapper, is the attachment.  Do not create a duplicate
            # irregular attachment from the wrapper itself.
            for key in ("attachments", "folders", "material", "children", "items"):
                if key in item and item[key] is not None:
                    walk(item[key])
            return
        if "download_url" in item or (
            "id" in item and ("filename" in item or "name" in item or "type" in item)
        ):
            collected.append(item)
            return
        for key in ("attachments", "folders", "material", "children", "items"):
            if key in item and item[key] is not None:
                walk(item[key])

    if isinstance(value, Mapping):
        for key in ("attachments", "folders", "material"):
            if key in value and value[key] is not None:
                walk(value[key])
    else:
        walk(value)
    return collected


def normalize_export_attachment(
    raw: Mapping[str, Any],
    *,
    event_id: str,
    owner_kind: str,
    owner_id: str,
) -> dict[str, Any]:
    """Normalize an export material while retaining an irregular route for a queue."""
    attachment_id = require_identifier(raw.get("id"), "attachment id")
    protected = raw.get("is_protected")
    if protected is not None and not isinstance(protected, bool):
        raise ParseError("Export attachment is_protected was not boolean/null")
    direct_url = raw.get("download_url") or raw.get("url")
    parsed: dict[str, str] | None = None
    route_status = "missing_direct_attachment_url"
    if isinstance(direct_url, str) and direct_url:
        try:
            parsed = direct_attachment_from_url(direct_url)
        except (InputError, ParseError):
            route_status = "external_or_irregular_route"
        else:
            if (
                parsed["event_id"] != event_id
                or parsed["attachment_id"] != attachment_id
            ):
                raise IdentityError(
                    "Export attachment URL conflicted with its event or attachment id"
                )
            expected_contribution = owner_id if owner_kind == "contribution" else ""
            if parsed["contribution_id"] != expected_contribution:
                raise IdentityError("Export attachment URL conflicted with its owner")
            route_status = "validated_direct_attachment"
    elif direct_url is not None:
        route_status = "external_or_irregular_route"

    if protected is True:
        access_status = "protected_not_public"
    elif parsed is None:
        access_status = "other_failure"
    elif protected is False:
        access_status = "export_listed_public"
    else:
        access_status = "access_unverified"
    provenance = ["event_export"]
    if raw.get("_legacy_material_resource") is True:
        provenance.append("legacy_material_resource")
    return {
        "attachment_id": attachment_id,
        "event_id": event_id,
        "owner_kind": owner_kind,
        "owner_id": owner_id,
        "download_url": parsed["download_url"] if parsed else None,
        "route_path": parsed["route_path"] if parsed else None,
        "route_status": route_status,
        "access_status": access_status,
        "filename": clean_source_text(
            raw.get("filename")
            or raw.get("name")
            or (parsed["filename"] if parsed else "")
        ),
        "title": clean_source_text(raw.get("title") or raw.get("name")),
        "description": clean_source_text(raw.get("description")),
        "content_type": clean_source_text(raw.get("content_type")),
        "source_size_bytes": raw.get("size"),
        "is_protected": protected,
        "provenance": provenance,
    }


def merge_attachment(
    collection: dict[str, dict[str, Any]],
    incoming: Mapping[str, Any],
) -> None:
    key = str(incoming["attachment_id"])
    current = collection.get(key)
    if current is None:
        collection[key] = dict(incoming)
        return
    for field in ("event_id", "owner_kind", "owner_id"):
        if current[field] != incoming[field]:
            raise IdentityError(f"Attachment {key} had conflicting {field}")
    current_url = current.get("download_url")
    incoming_url = incoming.get("download_url")
    if current_url and incoming_url and current_url != incoming_url:
        raise IdentityError(f"Attachment {key} had conflicting download_url")
    if not current_url and incoming_url:
        current["download_url"] = incoming_url
        current["route_path"] = incoming.get("route_path")
        current["route_status"] = incoming.get("route_status")
    elif current_url and incoming_url:
        if current.get("route_path") != incoming.get("route_path"):
            raise IdentityError(f"Attachment {key} had conflicting route_path")
    for field in (
        "filename",
        "title",
        "description",
        "content_type",
        "source_size_bytes",
        "is_protected",
    ):
        if not current.get(field) and incoming.get(field):
            current[field] = incoming[field]
        elif (
            current.get(field)
            and incoming.get(field)
            and current[field] != incoming[field]
        ):
            raise IdentityError(f"Attachment {key} had conflicting {field}")

    current_access = str(current.get("access_status"))
    incoming_access = str(incoming.get("access_status"))
    # A direct observed access result outranks exporter declarations and an
    # unverified static link.  Conversely, merging a static page must never
    # downgrade an export declaration before a separate anonymous GET probes it.
    for terminal_status in (
        "access_restricted_or_login",
        "protected_not_public",
        "public_pdf",
        "public_non_pdf",
        "other_failure",
        "export_listed_public",
        "access_unverified",
    ):
        if terminal_status in {current_access, incoming_access}:
            current["access_status"] = terminal_status
            break
    else:
        current["access_status"] = current_access
    if (
        current.get("route_status") != "validated_direct_attachment"
        and incoming.get("route_status") == "validated_direct_attachment"
    ):
        current["route_status"] = "validated_direct_attachment"
    current["provenance"] = sorted(
        set(current["provenance"]) | set(incoming["provenance"])
    )


def stable_contribution_id(raw: Mapping[str, Any], *, label: str) -> str:
    for key in ("db_id", "contribution_id", "id"):
        if raw.get(key) is not None:
            return require_identifier(raw.get(key), f"{label} stable id")
    raise IdentityError(
        f"{label} lacked db_id/contribution_id/id needed for its public route"
    )


def export_subcontributions(raw: Mapping[str, Any]) -> list[Any]:
    """Read Indico's documented case-sensitive field with a narrow legacy fallback."""
    if "subContributions" in raw:
        canonical_children = as_list(raw.get("subContributions"), "subContributions")
        if "subcontributions" in raw:
            fallback_children = as_list(raw.get("subcontributions"), "subcontributions")
            if fallback_children != canonical_children:
                raise ParseError(
                    "Conflicting subContributions and legacy subcontributions fields"
                )
        return canonical_children
    # P01's historical detail=contributions payload used this lower-case shape.
    # Retain it only for compatibility with an implementation that omits the
    # documented field; prospective requests use detail=subcontributions.
    return as_list(raw.get("subcontributions"), "legacy subcontributions")


def parse_event_export(
    payload: Any, expected_event_id: str
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
]:
    """Parse detail=subcontributions without assuming it lists every material."""
    if not isinstance(payload, Mapping):
        raise ParseError("Event export did not return an object")
    count = payload.get("count")
    results = payload.get("results")
    if count != 1 or not isinstance(results, list) or len(results) != 1:
        raise CoverageError(
            "Event export detail=subcontributions did not reconcile one event to one result"
        )
    event = results[0]
    if not isinstance(event, Mapping):
        raise ParseError("Event export result was not an object")
    event_id = require_identifier(event.get("id"), "event export event id")
    if event_id != expected_event_id:
        raise IdentityError("Event export result did not match the requested event id")

    documents: list[dict[str, Any]] = [
        {
            "document_id": f"event:{event_id}:metadata",
            "source_object_id": f"event:{event_id}",
            "route_type": "event_metadata",
            "candidate_eligible": False,
            "fields": metadata_fields(event),
        }
    ]
    contribution_rows: list[dict[str, Any]] = []
    subcontribution_rows: list[dict[str, Any]] = []
    attachments: dict[str, dict[str, Any]] = {}

    def add_owner_attachments(
        owner: Mapping[str, Any], owner_kind: str, owner_id: str
    ) -> None:
        for raw_attachment in collect_attachment_mappings(owner):
            normalized = normalize_export_attachment(
                raw_attachment,
                event_id=event_id,
                owner_kind=owner_kind,
                owner_id=owner_id,
            )
            merge_attachment(attachments, normalized)

    add_owner_attachments(event, "event", event_id)

    contributions = as_list(
        event.get("contributions"), "contributions", allow_null=False
    )
    seen_contributions: set[str] = set()
    seen_subcontributions: set[tuple[str, str]] = set()

    def walk_contribution(
        raw: Any, *, parent_contribution_id: str | None = None
    ) -> None:
        if not isinstance(raw, Mapping):
            raise ParseError(
                "Event export contribution/subcontribution was not an object"
            )
        if parent_contribution_id is None:
            contribution_id = stable_contribution_id(raw, label="contribution")
            if contribution_id in seen_contributions:
                raise IdentityError(
                    f"Event export repeated contribution id {contribution_id}"
                )
            seen_contributions.add(contribution_id)
            source_url = raw.get("url")
            if source_url:
                expected = urlsplit(
                    contribution_page_url(event_id, contribution_id)
                ).path
                if urlsplit(canonical_public_url(str(source_url))).path != expected:
                    raise IdentityError(
                        "Contribution URL did not match event/contribution stable ids"
                    )
            contribution_rows.append({"contribution_id": contribution_id})
            owner_kind = "contribution"
            owner_id = contribution_id
            document_id = f"event:{event_id}:contribution:{contribution_id}:metadata"
            source_object_id = f"event:{event_id}:contribution:{contribution_id}"
        else:
            sub_id: str | None = None
            for key in ("db_id", "subcontribution_id", "id"):
                if raw.get(key) is not None:
                    sub_id = require_identifier(raw.get(key), "subcontribution id")
                    break
            if sub_id is None:
                raise IdentityError("Subcontribution lacked a stable/source-local id")
            composite_id = (parent_contribution_id, sub_id)
            if composite_id in seen_subcontributions:
                raise IdentityError(
                    "Event export repeated a subcontribution within the same parent contribution"
                )
            seen_subcontributions.add(composite_id)
            owner_kind = "subcontribution"
            owner_id = f"{parent_contribution_id}:{sub_id}"
            document_id = f"event:{event_id}:contribution:{parent_contribution_id}:subcontribution:{sub_id}:metadata"
            source_object_id = document_id.removesuffix(":metadata")
            subcontribution_rows.append(
                {
                    "parent_contribution_id": parent_contribution_id,
                    "subcontribution_id": sub_id,
                    "stable_id_scope": "event_parent_composite",
                }
            )

        documents.append(
            {
                "document_id": document_id,
                "source_object_id": source_object_id,
                "route_type": f"{owner_kind}_metadata",
                "candidate_eligible": False,
                "fields": metadata_fields(raw),
            }
        )
        # The current pilot validates static attachment enumeration only for true
        # contribution pages.  Subcontribution materials enter the replayable queue.
        if owner_kind == "contribution":
            add_owner_attachments(raw, owner_kind, owner_id)
        children = export_subcontributions(raw)
        if children and owner_kind != "contribution":
            raise CoverageError(
                "Nested subcontribution hierarchy requires a newly validated route"
            )
        for child in children:
            walk_contribution(child, parent_contribution_id=owner_id)

    for contribution in contributions:
        walk_contribution(contribution)

    return (
        dict(event),
        contribution_rows,
        subcontribution_rows,
        attachments,
        documents
        + [
            {
                "document_id": f"event:{item['event_id']}:{item['owner_kind']}:{item['owner_id']}:attachment:{item['attachment_id']}:metadata",
                "source_object_id": f"event:{item['event_id']}:{item['owner_kind']}:{item['owner_id']}:attachment:{item['attachment_id']}",
                "route_type": f"{item['owner_kind']}_attachment_metadata",
                "candidate_eligible": False,
                "fields": {
                    "title": item["title"],
                    "description": item["description"],
                    "filename": item["filename"],
                },
            }
            for item in attachments.values()
        ],
    )


def event_detail_inventory(
    payload: Any, expected_event_id: str, *, detail: str
) -> dict[str, Any]:
    """Return a content-free contribution/subcontribution inventory for one detail."""
    if detail not in {"subcontributions", "sessions"}:
        raise InputError("Inventory supports only documented nested/session details")
    if not isinstance(payload, Mapping):
        raise ParseError("Event-detail export did not return an object")
    results = payload.get("results")
    if payload.get("count") != 1 or not isinstance(results, list) or len(results) != 1:
        raise CoverageError("Event-detail export did not reconcile one event to one result")
    event = results[0]
    if not isinstance(event, Mapping):
        raise ParseError("Event-detail result was not an object")
    event_id = require_identifier(event.get("id"), "event-detail event id")
    if event_id != expected_event_id:
        raise IdentityError("Event-detail result did not match its requested event id")

    contribution_ids: list[str] = []
    seen_contributions: set[str] = set()
    subcontributions: list[dict[str, Any]] = []
    seen_subcontributions: set[tuple[str, str]] = set()

    def append_contribution(raw: Any, *, location: str) -> None:
        if not isinstance(raw, Mapping):
            raise ParseError("Event-detail contribution was not an object")
        contribution_id = stable_contribution_id(raw, label=location)
        if contribution_id in seen_contributions:
            raise IdentityError("Event-detail repeated a contribution stable id")
        seen_contributions.add(contribution_id)
        contribution_ids.append(contribution_id)

        def walk_children(parent_id: str, owner: Mapping[str, Any], depth: int) -> None:
            for child in export_subcontributions(owner):
                if not isinstance(child, Mapping):
                    raise ParseError("Event-detail subcontribution was not an object")
                sub_id = stable_contribution_id(child, label="subcontribution")
                composite = (parent_id, sub_id)
                if composite in seen_subcontributions:
                    raise IdentityError("Event-detail repeated a subcontribution composite id")
                seen_subcontributions.add(composite)
                subcontributions.append(
                    {
                        "parent_contribution_id": parent_id,
                        "subcontribution_id": sub_id,
                        "depth": depth,
                    }
                )
                walk_children(sub_id, child, depth + 1)

        walk_children(contribution_id, raw, 1)

    top_level = as_list(
        event.get("contributions"), "contributions", allow_null=False
    )
    for raw in top_level:
        append_contribution(raw, location="top-level contribution")

    sessions = []
    session_contribution_counts: list[int] = []
    if detail == "sessions":
        sessions = as_list(event.get("sessions"), "sessions", allow_null=False)
        for session in sessions:
            if not isinstance(session, Mapping):
                raise ParseError("Event-detail session was not an object")
            session_contributions = as_list(
                session.get("contributions"), "session.contributions", allow_null=False
            )
            session_contribution_counts.append(len(session_contributions))
            for raw in session_contributions:
                append_contribution(raw, location="session contribution")

    return {
        "event_id": event_id,
        "detail": detail,
        "top_level_contribution_count": len(top_level),
        "session_count": len(sessions),
        "session_contribution_counts": session_contribution_counts,
        "contribution_ids_in_source_order": contribution_ids,
        "subcontribution_records": subcontributions,
    }


def static_attachment_record(
    parsed: Mapping[str, str], *, owner_kind: str, owner_id: str
) -> dict[str, Any]:
    """Record a visible direct link without assuming it is anonymously downloadable."""
    return {
        "attachment_id": parsed["attachment_id"],
        "event_id": parsed["event_id"],
        "owner_kind": owner_kind,
        "owner_id": owner_id,
        "download_url": parsed["download_url"],
        "route_path": parsed["route_path"],
        "route_status": "validated_direct_attachment",
        "access_status": "access_unverified",
        "filename": clean_source_text(parsed["filename"]),
        "title": "",
        "description": "",
        "content_type": "",
        "source_size_bytes": None,
        "is_protected": None,
        "provenance": ["static_owner_page"],
    }


def probe_direct_attachment_accesses(
    client: PublicClient, attachments: Mapping[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Classify every same-origin direct material by anonymous no-redirect GET.

    The response body is never persisted.  This makes a visible static link or
    exporter ``is_protected=false`` declaration provisional until the direct
    route itself is observed, while allowing a restricted static-only link to
    receive an explicit non-public boundary disposition.
    """
    receipts: list[dict[str, Any]] = []
    for attachment_id in sorted(
        attachments, key=lambda item: int(item) if item.isdigit() else item
    ):
        record = attachments[attachment_id]
        if record.get("is_protected") is True:
            continue
        if record.get("route_status") != "validated_direct_attachment":
            continue
        download_url = record.get("download_url")
        if not isinstance(download_url, str) or not download_url:
            raise CoverageError("Validated direct attachment lacked a download URL")
        receipt = client.probe_access_status(download_url)
        record["access_status"] = receipt["access_status"]
        record["access_probe_receipt"] = receipt
        observed_content_type = receipt.get("observed_content_type")
        if not record.get("content_type") and isinstance(observed_content_type, str):
            record["content_type"] = observed_content_type
        receipts.append(
            {
                "attachment_id": attachment_id,
                "event_id": record["event_id"],
                "owner_kind": record["owner_kind"],
                "owner_id": record["owner_id"],
                "route_path": record["route_path"],
                "receipt": receipt,
            }
        )
    return receipts


def classify_attachment(record: Mapping[str, Any]) -> str:
    """Keep access proof, source-boundary disposition, and text routing distinct."""
    if record.get("is_protected") is True:
        return "protected_not_public_terminal"
    if record.get("route_status") != "validated_direct_attachment":
        return "irregular_or_external_pending_queue"
    access_status = str(record.get("access_status") or "access_unverified")
    if access_status == "public_pdf":
        return "public_pdf_pending_text"
    if access_status == "public_non_pdf":
        return "public_non_pdf_pending_route"
    if access_status == "access_restricted_or_login":
        return (
            "declared_public_access_conflict"
            if record.get("is_protected") is False
            else "restricted_not_public_terminal"
        )
    if access_status == "other_failure":
        return "other_failure"
    # Both a static-only link and an export's unprotected declaration need a
    # direct anonymous GET before they can become public material routes.
    return "direct_material_access_pending"


def attachment_boundary_disposition(
    record: Mapping[str, Any], classification: str
) -> str:
    """State whether a non-public route is excluded or remains a coverage failure."""
    if classification == "protected_not_public_terminal":
        return "excluded_nonpublic_explicitly_protected"
    if classification == "restricted_not_public_terminal":
        return "excluded_nonpublic_restricted_or_login"
    if classification == "declared_public_access_conflict":
        return "coverage_failure_declared_unprotected_but_anonymous_access_failed"
    if classification == "other_failure":
        return "coverage_failure_direct_route_failed"
    if classification == "irregular_or_external_pending_queue":
        return "coverage_pending_irregular_or_external_route"
    if classification == "direct_material_access_pending":
        return "coverage_pending_direct_access_probe"
    if classification == "public_pdf_pending_text":
        return "public_pdf_requires_terminal_text_or_ocr"
    if classification == "public_non_pdf_pending_route":
        return "public_non_pdf_requires_terminal_text_route"
    raise AssertionError("Unexpected attachment classification")


def make_safe_document(document: Mapping[str, Any]) -> dict[str, Any]:
    fields = document["fields"]
    return {
        "document_id": document["document_id"],
        "source_object_id": document["source_object_id"],
        "route_type": document["route_type"],
        "candidate_eligible": bool(document.get("candidate_eligible", False)),
        "field_sha256": {
            key: sha256_text(value) for key, value in sorted(fields.items())
        },
        "field_utf8_bytes": {
            key: len(value.encode("utf-8")) for key, value in sorted(fields.items())
        },
    }


def harvest_event(
    client: PublicClient,
    *,
    event_id: str,
    dictionary: Mapping[str, Any],
    max_contribution_pages: int,
    perform_matching: bool,
    probe_material_access: bool = False,
    max_attachments: int | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build a safe ledger for one explicit event; PDF bytes remain a later stage."""
    requested_event_id = require_identifier(event_id, "event id")
    if max_attachments is not None and max_attachments < 0:
        raise InputError("max_attachments cannot be negative")
    payload, export_receipt = client.get_json(event_export_url(requested_event_id))
    _, contribution_rows, subcontribution_rows, attachments, documents = (
        parse_event_export(payload, requested_event_id)
    )
    if len(contribution_rows) > max_contribution_pages:
        raise CoverageError(
            "Contribution-page safety bound would truncate this event; increase "
            "--max-contribution-pages before starting a complete event pass"
        )
    if max_attachments is not None and len(attachments) > max_attachments:
        raise CoverageError(
            "Attachment safety bound would truncate this event; increase "
            "--max-attachments before starting a complete event pass"
        )

    static_receipts: list[dict[str, Any]] = []
    static_attachments: dict[str, dict[str, Any]] = {}

    event_html, event_receipt = client.get_html(event_page_url(requested_event_id))
    static_receipts.append(
        {"owner_kind": "event", "owner_id": requested_event_id, **event_receipt}
    )
    for parsed in extract_attachment_links(event_html, requested_event_id):
        if parsed["contribution_id"]:
            continue
        merge_attachment(
            static_attachments,
            static_attachment_record(
                parsed, owner_kind="event", owner_id=requested_event_id
            ),
        )

    for row in contribution_rows:
        contribution_id = row["contribution_id"]
        page_html, page_receipt = client.get_html(
            contribution_page_url(requested_event_id, contribution_id)
        )
        static_receipts.append(
            {"owner_kind": "contribution", "owner_id": contribution_id, **page_receipt}
        )
        for parsed in extract_attachment_links(page_html, requested_event_id):
            if parsed["contribution_id"] != contribution_id:
                continue
            merge_attachment(
                static_attachments,
                static_attachment_record(
                    parsed, owner_kind="contribution", owner_id=contribution_id
                ),
            )

    # Preserve this before static merging: it is the true event-export ID set,
    # not the all-route union used for final material accounting.
    export_attachment_ids = set(attachments)
    export_declared_unprotected_attachment_ids = {
        attachment_id
        for attachment_id, record in attachments.items()
        if record.get("access_status") == "export_listed_public"
    }
    export_declared_unprotected_direct_attachment_ids = {
        attachment_id
        for attachment_id, record in attachments.items()
        if attachment_id in export_declared_unprotected_attachment_ids
        and record.get("route_status") == "validated_direct_attachment"
    }
    static_ids = set(static_attachments)
    missing_from_static = sorted(
        export_declared_unprotected_direct_attachment_ids - static_ids,
        key=lambda item: int(item) if item.isdigit() else item,
    )
    if missing_from_static:
        raise CoverageError(
            "Export-declared unprotected attachment(s) were absent from their validated static owner pages: "
            + ", ".join(missing_from_static)
        )

    for record in static_attachments.values():
        merge_attachment(attachments, record)
    if max_attachments is not None and len(attachments) > max_attachments:
        raise CoverageError(
            "All-route attachment safety bound would truncate this event; increase "
            "--max-attachments before starting a complete event pass"
        )
    all_route_attachment_ids = set(attachments)
    material_access_receipts: list[dict[str, Any]] = []
    if probe_material_access:
        material_access_receipts = probe_direct_attachment_accesses(client, attachments)
    for record in attachments.values():
        record["classification"] = classify_attachment(record)
        record["source_boundary_disposition"] = attachment_boundary_disposition(
            record, record["classification"]
        )

    # Add metadata document routes for static-only attachments.  Existing export
    # attachment document routes are retained; equal IDs are not duplicated.
    document_ids = {str(document["document_id"]) for document in documents}
    for attachment in attachments.values():
        document_id = (
            f"event:{attachment['event_id']}:{attachment['owner_kind']}:{attachment['owner_id']}:"
            f"attachment:{attachment['attachment_id']}:metadata"
        )
        if document_id not in document_ids:
            documents.append(
                {
                    "document_id": document_id,
                    "source_object_id": document_id.removesuffix(":metadata"),
                    "route_type": f"{attachment['owner_kind']}_attachment_metadata",
                    "candidate_eligible": False,
                    "fields": {
                        "title": attachment["title"],
                        "description": attachment["description"],
                        "filename": attachment["filename"],
                    },
                }
            )
            document_ids.add(document_id)

    attachment_rows = []
    for attachment_id in sorted(
        attachments, key=lambda item: int(item) if item.isdigit() else item
    ):
        record = attachments[attachment_id]
        row = {
            key: record[key]
            for key in (
                "attachment_id",
                "event_id",
                "owner_kind",
                "owner_id",
                "route_path",
                "route_status",
                "access_status",
                "content_type",
                "source_size_bytes",
                "is_protected",
                "provenance",
                "classification",
                "source_boundary_disposition",
            )
        }
        if isinstance(record.get("access_probe_receipt"), Mapping):
            row["access_probe_receipt"] = record["access_probe_receipt"]
        attachment_rows.append(row)

    pending_pdfs = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "public_pdf_pending_text"
    ]
    pending_direct_access_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "direct_material_access_pending"
    ]
    public_non_pdf_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "public_non_pdf_pending_route"
    ]
    irregular_or_external_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "irregular_or_external_pending_queue"
    ]
    other_failure_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "other_failure"
    ]
    declared_public_access_conflict_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "declared_public_access_conflict"
    ]
    restricted_nonpublic_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "restricted_not_public_terminal"
    ]
    protected_nonpublic_ids = [
        item["attachment_id"]
        for item in attachment_rows
        if item["classification"] == "protected_not_public_terminal"
    ]
    rows_by_id = {item["attachment_id"]: item for item in attachment_rows}
    manual_queue: list[dict[str, Any]] = []
    for attachment_id in pending_pdfs:
        row = rows_by_id[attachment_id]
        manual_queue.append(
            {
                "queue_id": f"ESA-NAV-{requested_event_id}-PDF-{attachment_id}",
                "action": "download_and_extract_public_pdf",
                "reason": "A confirmed public PDF needs its own hash and terminal text/OCR route.",
                "input": {
                    "event_id": requested_event_id,
                    "attachment_id": attachment_id,
                    "owner_kind": row["owner_kind"],
                    "owner_id": row["owner_id"],
                    "route_path": row["route_path"],
                },
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "pdf_sha256",
                    "text_sha256_or_ocr_receipt",
                ],
                "failure_rule": "A missing download, parse, or OCR result makes local coverage incomplete.",
            }
        )
    for attachment_id in pending_direct_access_ids:
        row = rows_by_id[attachment_id]
        manual_queue.append(
            {
                "queue_id": f"ESA-NAV-{requested_event_id}-ACCESS-{attachment_id}",
                "action": "probe_anonymous_public_material_access",
                "reason": "A source declaration or visible link is not proof of public downloadable access.",
                "input": {
                    "event_id": requested_event_id,
                    "attachment_id": attachment_id,
                    "owner_kind": row["owner_kind"],
                    "owner_id": row["owner_id"],
                    "route_path": row["route_path"],
                },
                "required_output": ["access_status", "completed_at", "operator"],
                "failure_rule": (
                    "A successful probe must generate and complete the corresponding PDF or non-PDF "
                    "text route. A restricted static-only item is explicitly non-public; a route "
                    "declared unprotected by the export but inaccessible is a coverage failure."
                ),
            }
        )
    for attachment_id in public_non_pdf_ids:
        row = rows_by_id[attachment_id]
        manual_queue.append(
            {
                "queue_id": f"ESA-NAV-{requested_event_id}-NONPDF-{attachment_id}",
                "action": "route_public_non_pdf_to_text_extractor_or_manual",
                "reason": "A public non-PDF material cannot silently become a no-match.",
                "input": {
                    "event_id": requested_event_id,
                    "attachment_id": attachment_id,
                    "owner_kind": row["owner_kind"],
                    "owner_id": row["owner_id"],
                    "route_path": row["route_path"],
                    "content_type": row["content_type"],
                },
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "text_sha256_or_failure_reason",
                ],
                "failure_rule": (
                    "Only a completed deterministic text route or a replayable manual/LLM text route "
                    "can resolve this item; an access, parse, or unsupported-format failure leaves "
                    "coverage null."
                ),
            }
        )
    for attachment_id in irregular_or_external_ids + other_failure_ids:
        row = rows_by_id[attachment_id]
        manual_queue.append(
            {
                "queue_id": f"ESA-NAV-{requested_event_id}-IRREGULAR-{attachment_id}",
                "action": "resolve_irregular_or_external_material",
                "reason": "The export material did not expose a validated same-origin attachment route.",
                "input": {
                    "event_id": requested_event_id,
                    "attachment_id": attachment_id,
                    "owner_kind": row["owner_kind"],
                    "owner_id": row["owner_id"],
                    "route_path": row["route_path"],
                    "source_export_operation": "detail=subcontributions",
                },
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "text_sha256_or_failure_reason",
                ],
                "failure_rule": (
                    "Do not drop or call an irregular/external material a no-match; an unresolved, "
                    "inaccessible, or unparseable item leaves coverage null."
                ),
            }
        )
    for sub in subcontribution_rows:
        manual_queue.append(
            {
                "queue_id": (
                    f"ESA-NAV-{requested_event_id}-SUB-"
                    f"{sub['parent_contribution_id']}-{sub['subcontribution_id']}"
                ),
                "action": "inspect_public_subcontribution_route",
                "reason": "Nested route is not validated by this pilot.",
                "input": {"event_id": requested_event_id, **sub},
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "coverage_receipt_sha256",
                ],
                "failure_rule": "No validated owner/material receipt leaves source coverage incomplete.",
            }
        )
    queued_attachment_ids = sorted(
        set(
            pending_direct_access_ids
            + public_non_pdf_ids
            + irregular_or_external_ids
            + other_failure_ids
        ),
        key=lambda item: int(item) if item.isdigit() else item,
    )
    material_route_coverage = {
        "direct_material_access_probed": probe_material_access,
        "direct_access_receipts": material_access_receipts,
        "public_non_pdf_attachment_ids": public_non_pdf_ids,
        "direct_access_pending_attachment_ids": pending_direct_access_ids,
        "irregular_or_external_attachment_ids": irregular_or_external_ids,
        "other_failure_attachment_ids": other_failure_ids,
        "declared_public_access_conflict_attachment_ids": declared_public_access_conflict_ids,
        "restricted_nonpublic_terminal_attachment_ids": restricted_nonpublic_ids,
        "protected_nonpublic_terminal_attachment_ids": protected_nonpublic_ids,
        "subcontribution_route_ids_pending": subcontribution_rows,
        "queued_attachment_ids": queued_attachment_ids,
        "coverage_complete": not (
            pending_direct_access_ids
            or public_non_pdf_ids
            or irregular_or_external_ids
            or other_failure_ids
            or declared_public_access_conflict_ids
            or subcontribution_rows
        ),
        "failure_rule": (
            "Every public non-PDF needs a completed deterministic or replayable manual/LLM text route; "
            "an unresolved access probe, declared-public access conflict, irregular/external route, parse, "
            "or manual-route failure leaves coverage null. Explicitly protected or restricted static-only "
            "items are retained as non-public boundary dispositions, not public-PDF zeros."
        ),
    }
    matches: dict[str, Any]
    if (
        perform_matching
        and not pending_pdfs
        and material_route_coverage["coverage_complete"]
    ):
        matches = match_documents(documents, dictionary)
    elif perform_matching:
        matches = {
            "matching_schema_version": "esa-indico-local-matching/v1",
            "performed": False,
            "reason": "PDF or non-PDF material coverage was incomplete; no partial matching was released.",
        }
    else:
        matches = {
            "matching_schema_version": "esa-indico-local-matching/v1",
            "performed": False,
            "reason": "Metadata matching was not requested for this diagnostic topology pass.",
        }

    ledger = {
        "ledger_schema_version": "esa-indico-event-harvest/v1",
        "operation": "bounded_public_event_harvest_without_pdf_download",
        "event_id": requested_event_id,
        "event_export_receipt": export_receipt,
        "contribution_ids": [row["contribution_id"] for row in contribution_rows],
        "subcontribution_ids": subcontribution_rows,
        "documents": [make_safe_document(document) for document in documents],
        "attachment_rows": attachment_rows,
        "static_page_receipts": static_receipts,
        "reconciliation": {
            "export_attachment_ids": sorted(
                export_attachment_ids,
                key=lambda item: int(item) if item.isdigit() else item,
            ),
            "export_declared_unprotected_attachment_ids": sorted(
                export_declared_unprotected_attachment_ids,
                key=lambda item: int(item) if item.isdigit() else item,
            ),
            "all_route_attachment_ids": sorted(
                all_route_attachment_ids,
                key=lambda item: int(item) if item.isdigit() else item,
            ),
            "static_attachment_ids": sorted(
                static_ids, key=lambda item: int(item) if item.isdigit() else item
            ),
            "static_only_attachment_ids": sorted(
                static_ids - export_attachment_ids,
                key=lambda item: int(item) if item.isdigit() else item,
            ),
            "export_declared_unprotected_missing_from_static": missing_from_static,
            "export_declared_unprotected_subset_of_static": not missing_from_static,
        },
        "material_route_coverage": material_route_coverage,
        "pdf_text_coverage": {
            "required_confirmed_public_pdf_attachment_ids": pending_pdfs,
            "completed_public_pdf_attachment_ids": [],
            "coverage_complete": not pending_pdfs,
            "reason": (
                "No confirmed public PDFs required this event stage."
                if not pending_pdfs
                else "This bounded command has not yet downloaded every confirmed public PDF."
            ),
        },
        "matching": matches,
        "matching_is_final_candidate_set": False,
        "manual_navigation_queue": manual_queue,
        "status": "partial_diagnostic",
    }
    return ledger, documents, [attachments[key] for key in attachments]


def normalize_for_matching(value: str) -> str:
    """NFKC/casefold then preserve lexical-token semantics with hyphens as separators."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    translation = str.maketrans({character: "-" for character in HYPHEN_FAMILY})
    return normalized.translate(translation)


def lexical_tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(normalize_for_matching(value))


@dataclass(frozen=True)
class TokenHit:
    term: str
    field: str
    start: int
    end: int

    def as_json(self) -> dict[str, Any]:
        return {
            "term": self.term,
            "field": self.field,
            "token_start": self.start,
            "token_end": self.end,
        }


@dataclass(frozen=True)
class PairHit:
    left: TokenHit
    right: TokenHit
    intervening_tokens: int

    def as_json(self) -> dict[str, Any]:
        return {
            "left": self.left.as_json(),
            "right": self.right.as_json(),
            "intervening_tokens": self.intervening_tokens,
        }


def phrase_hits(fields: Mapping[str, str], term: str) -> list[TokenHit]:
    phrase = lexical_tokens(term)
    if not phrase:
        return []
    hits: list[TokenHit] = []
    cursor = 0
    for field, raw_text in fields.items():
        values = lexical_tokens(raw_text)
        for index in range(len(values) - len(phrase) + 1):
            if values[index : index + len(phrase)] == phrase:
                hits.append(
                    TokenHit(
                        term=term,
                        field=field,
                        start=cursor + index,
                        end=cursor + index + len(phrase),
                    )
                )
        # The boundary cursor gap prevents a phrase crossing fields while still
        # allowing independent required concepts to co-occur in the defined metadata route.
        cursor += len(values) + 1
    return hits


def find_term_hits(fields: Mapping[str, str], terms: Iterable[str]) -> list[TokenHit]:
    seen: set[tuple[str, str, int, int]] = set()
    output: list[TokenHit] = []
    for term in terms:
        for hit in phrase_hits(fields, term):
            key = (hit.term, hit.field, hit.start, hit.end)
            if key not in seen:
                seen.add(key)
                output.append(hit)
    return sorted(output, key=lambda hit: (hit.field, hit.start, hit.end, hit.term))


def nonoverlapping_pair(left: TokenHit, right: TokenHit) -> int | None:
    if left.field != right.field:
        return None
    if left.end <= right.start:
        return right.start - left.end
    if right.end <= left.start:
        return left.start - right.end
    return None


def pair_hits(
    fields: Mapping[str, str],
    left_terms: Iterable[str],
    right_terms: Iterable[str],
    *,
    maximum_intervening_tokens: int = 5,
) -> list[PairHit]:
    output: list[PairHit] = []
    seen: set[tuple[str, int, int, str, int, int]] = set()
    for left in find_term_hits(fields, left_terms):
        for right in find_term_hits(fields, right_terms):
            gap = nonoverlapping_pair(left, right)
            if gap is None or gap > maximum_intervening_tokens:
                continue
            key = (left.field, left.start, left.end, right.term, right.start, right.end)
            if key not in seen:
                seen.add(key)
                output.append(PairHit(left=left, right=right, intervening_tokens=gap))
    return sorted(
        output,
        key=lambda hit: (
            hit.left.field,
            min(hit.left.start, hit.right.start),
            max(hit.left.end, hit.right.end),
            hit.left.term,
            hit.right.term,
        ),
    )


def concept_match(
    fields: Mapping[str, str],
    concept_id: str,
    concepts: Mapping[str, Any],
    memo: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if concept_id in memo:
        return memo[concept_id]
    definition = concepts.get(concept_id)
    if not isinstance(definition, Mapping):
        raise InputError(f"Concept dictionary did not define {concept_id}")
    kind = definition.get("kind")
    if kind == "finite_terms":
        terms = definition.get("terms")
        if not isinstance(terms, list) or not all(
            isinstance(term, str) for term in terms
        ):
            raise InputError(f"Concept {concept_id} had invalid finite terms")
        result = {
            "matched": bool(find_term_hits(fields, terms)),
            "term_hits": find_term_hits(fields, terms),
            "pair_hits": [],
        }
    elif kind == "union":
        members = definition.get("members")
        if not isinstance(members, list) or not all(
            isinstance(member, str) for member in members
        ):
            raise InputError(f"Concept {concept_id} had invalid union members")
        member_results = [
            concept_match(fields, member, concepts, memo) for member in members
        ]
        result = {
            "matched": any(member["matched"] for member in member_results),
            "term_hits": [
                hit for member in member_results for hit in member["term_hits"]
            ],
            "pair_hits": [
                hit for member in member_results for hit in member["pair_hits"]
            ],
            "members": {
                member: member_result["matched"]
                for member, member_result in zip(members, member_results)
            },
        }
    elif kind in {"union_of_terms_and_pairs", "paired_terms"}:
        direct_terms = definition.get("terms", [])
        if not isinstance(direct_terms, list) or not all(
            isinstance(term, str) for term in direct_terms
        ):
            raise InputError(f"Concept {concept_id} had invalid direct terms")
        direct_hits = find_term_hits(fields, direct_terms)
        found_pairs: list[PairHit] = []
        pair_rules = definition.get("pair_rules", [])
        if kind == "paired_terms":
            pair_rules = [
                {"left": definition.get("left"), "right": definition.get("right")}
            ]
        if not isinstance(pair_rules, list):
            raise InputError(f"Concept {concept_id} had malformed pair rules")
        for pair in pair_rules:
            if not isinstance(pair, Mapping):
                raise InputError(f"Concept {concept_id} had a malformed pair rule")
            left = pair.get("left")
            right = pair.get("right")
            if not isinstance(left, list) or not isinstance(right, list):
                raise InputError(
                    f"Concept {concept_id} had a malformed pair vocabulary"
                )
            found_pairs.extend(pair_hits(fields, left, right))
        result = {
            "matched": bool(direct_hits or found_pairs),
            "term_hits": direct_hits,
            "pair_hits": found_pairs,
        }
    else:
        raise InputError(f"Concept {concept_id} had unsupported kind {kind!r}")
    memo[concept_id] = result
    return result


def hit_contains_architecture(hit: TokenHit) -> bool:
    return any(
        token in {"architecture", "architectures"} for token in lexical_tokens(hit.term)
    )


def independent_r_match(
    raw_r: Mapping[str, Any], artifact_matches: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    """Suppress only an R architecture token consumed inside an artifact expression."""
    artifact_hits: list[TokenHit] = []
    for match in artifact_matches:
        artifact_hits.extend(
            hit for hit in match.get("term_hits", []) if hit_contains_architecture(hit)
        )
        for paired in match.get("pair_hits", []):
            if hit_contains_architecture(paired.left):
                artifact_hits.append(paired.left)
            if hit_contains_architecture(paired.right):
                artifact_hits.append(paired.right)
    independent: list[TokenHit] = []
    suppressed: list[TokenHit] = []
    for r_hit in raw_r["term_hits"]:
        is_arch = lexical_tokens(r_hit.term) in (["architecture"], ["architectures"])
        overlaps_artifact = any(
            r_hit.field == artifact.field
            and r_hit.start < artifact.end
            and artifact.start < r_hit.end
            for artifact in artifact_hits
        )
        if is_arch and overlaps_artifact:
            suppressed.append(r_hit)
        else:
            independent.append(r_hit)
    return {
        "matched": bool(independent),
        "term_hits": independent,
        "pair_hits": [],
        "suppressed_architecture_hits": suppressed,
    }


def serialise_match(match: Mapping[str, Any]) -> dict[str, Any]:
    payload = {
        "matched": bool(match["matched"]),
        "term_hits": [hit.as_json() for hit in match.get("term_hits", [])],
        "pair_hits": [hit.as_json() for hit in match.get("pair_hits", [])],
    }
    if "members" in match:
        payload["members"] = match["members"]
    if "suppressed_architecture_hits" in match:
        payload["suppressed_architecture_hits"] = [
            hit.as_json() for hit in match["suppressed_architecture_hits"]
        ]
    return payload


def match_one_document(
    document: Mapping[str, Any], dictionary: Mapping[str, Any]
) -> dict[str, Any]:
    concepts = dictionary.get("concepts")
    if not isinstance(concepts, Mapping):
        raise InputError("Concept dictionary did not contain concepts")
    fields = document.get("fields")
    if not isinstance(fields, Mapping) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in fields.items()
    ):
        raise InputError("A local document did not contain string fields")
    # Only an explicitly marked terminal full-text route may emit a candidate.
    # Metadata and filenames remain auditable local routes but are never enough.
    candidate_eligible = document.get("candidate_eligible", False)
    if not isinstance(candidate_eligible, bool):
        raise InputError("Local document candidate_eligible flag was not boolean")
    memo: dict[str, dict[str, Any]] = {}
    needed = (
        "P",
        "E_H",
        "E_F",
        "E",
        "M_H",
        "M_B",
        "M",
        "G_model",
        "G_structure",
        "C1",
        "R",
        "T2",
    )
    for concept_id in needed:
        concept_match(fields, concept_id, concepts, memo)
    memo["R"] = independent_r_match(
        memo["R"],
        (memo["G_model"], memo["G_structure"], memo["C1"], memo["T2"]),
    )

    partition_truth = {
        "core_B": memo["P"]["matched"] and memo["M"]["matched"],
        "stream_A_tag": memo["P"]["matched"]
        and memo["E"]["matched"]
        and memo["M"]["matched"],
        "BG1": memo["P"]["matched"] and memo["G_model"]["matched"],
        "BG2": memo["P"]["matched"] and memo["G_structure"]["matched"],
        "BC1": memo["P"]["matched"] and memo["C1"]["matched"],
        "B2_equivalent_tag": memo["P"]["matched"]
        and memo["M_B"]["matched"]
        and memo["R"]["matched"],
        "BT2_equivalent_tag": memo["P"]["matched"]
        and memo["M_B"]["matched"]
        and memo["T2"]["matched"],
        "R_tag": memo["R"]["matched"],
        "T2_tag": memo["T2"]["matched"],
    }
    candidate_partitions = [
        key for key in ("core_B", "BG1", "BG2", "BC1") if partition_truth[key]
    ]
    invariants = {
        "stream_A_implies_core_B": not partition_truth["stream_A_tag"]
        or partition_truth["core_B"],
        "B2_implies_core_B": not partition_truth["B2_equivalent_tag"]
        or partition_truth["core_B"],
        "BT2_implies_core_B": not partition_truth["BT2_equivalent_tag"]
        or partition_truth["core_B"],
        "candidate_union_exact": bool(candidate_partitions)
        == any(partition_truth[key] for key in ("core_B", "BG1", "BG2", "BC1")),
    }
    if not all(invariants.values()):
        raise CoverageError("Local matching invariant failed")
    return {
        "document_id": str(document["document_id"]),
        "source_object_id": str(document["source_object_id"]),
        "route_type": str(document["route_type"]),
        "candidate_eligible": candidate_eligible,
        "field_sha256": {
            key: sha256_text(value) for key, value in sorted(fields.items())
        },
        "concepts": {
            concept_id: serialise_match(memo[concept_id]) for concept_id in needed
        },
        "raw_candidate_partitions": candidate_partitions,
        "candidate_partitions": candidate_partitions if candidate_eligible else [],
        "tags": partition_truth,
        "invariants": invariants,
    }


def match_documents(
    documents: Iterable[Mapping[str, Any]], dictionary: Mapping[str, Any]
) -> dict[str, Any]:
    matches = [match_one_document(document, dictionary) for document in documents]
    document_ids = [match["document_id"] for match in matches]
    if len(document_ids) != len(set(document_ids)):
        raise IdentityError("Local matching input repeated a document route id")
    candidate_keys = ("core_B", "BG1", "BG2", "BC1")
    counts = {
        key: sum(key in match["candidate_partitions"] for match in matches)
        for key in candidate_keys
    }
    overlap: dict[str, int] = {}
    for index, left in enumerate(candidate_keys):
        for right in candidate_keys[index + 1 :]:
            overlap[f"{left}__{right}"] = sum(
                left in match["candidate_partitions"]
                and right in match["candidate_partitions"]
                for match in matches
            )
    source_objects = {
        match["source_object_id"] for match in matches if match["candidate_partitions"]
    }
    return {
        "matching_schema_version": "esa-indico-local-matching/v1",
        "performed": True,
        "dictionary_version": dictionary.get("artifact_version"),
        "document_route_count": len(matches),
        "candidate_document_route_count": sum(
            bool(match["candidate_partitions"]) for match in matches
        ),
        "raw_matching_document_route_count": sum(
            bool(match["raw_candidate_partitions"]) for match in matches
        ),
        "noncandidate_metadata_match_count": sum(
            not match["candidate_eligible"]
            and bool(match["raw_candidate_partitions"])
            for match in matches
        ),
        "candidate_source_object_count": len(source_objects),
        "partition_document_route_counts": counts,
        "pairwise_document_route_overlap": overlap,
        "documents": matches,
    }


def extract_pdf_text(pdf_path: Path, secure_dir: Path) -> dict[str, Any]:
    """Run deterministic Poppler text extraction outside Git; enqueue OCR if empty."""
    ensure_secure_directory(secure_dir)
    executable = shutil.which("pdftotext")
    if not executable:
        raise PdfError(
            "pdftotext is unavailable; do not substitute a silent empty parse"
        )
    pdf_digest = sha256_file(pdf_path)
    text_path = secure_dir / f"sha256-{pdf_digest}.txt"
    temporary = secure_dir / f".{text_path.name}.part"
    completed = subprocess.run(
        [executable, "-enc", "UTF-8", str(pdf_path), str(temporary)],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if completed.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise PdfError("pdftotext returned non-zero; local PDF coverage is incomplete")
    os.replace(temporary, text_path)
    text = text_path.read_text(encoding="utf-8", errors="strict")
    version = subprocess.run(
        [executable, "-v"], capture_output=True, text=True, check=False
    )
    version_line = (
        (version.stderr or version.stdout).splitlines()[0]
        if (version.stderr or version.stdout)
        else "unknown"
    )
    state = "text_extracted" if text.strip() else "ocr_required"
    return {
        "parse_state": state,
        "pdf_sha256": pdf_digest,
        "text_sha256": sha256_text(text),
        "text_utf8_bytes": len(text.encode("utf-8")),
        "parser": version_line,
        "secure_location_reference": f"sha256:{pdf_digest}",
        "_text_path": text_path,
    }


def attachment_looks_like_pdf(record: Mapping[str, Any]) -> bool:
    """Use only a route hint to identify a PDF that still needs an access probe."""
    content_type = str(record.get("content_type") or "").casefold()
    filename = str(record.get("filename") or "").casefold()
    route = str(record.get("route_path") or "").casefold()
    return "application/pdf" in content_type or filename.endswith(".pdf") or route.endswith(".pdf")


def ocr_handoff_command_template() -> str:
    """The mandated external OCR command, represented without a source path."""
    return (
        "uv run ~/agent-tools/processing/skills/pdf-to-markdown/scripts/"
        "pdf_to_markdown.py --input <secure-pdf-path> "
        "--output-path <outside-git-ocr-output-dir> --image-mode keep"
    )


def process_public_pdf_routes(
    client: PublicClient,
    attachments: Sequence[Mapping[str, Any]],
    *,
    secure_dir: Path,
    max_pdf_downloads: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Download/hash/parse every confirmed public PDF in an explicit event ledger.

    The caller must first resolve direct access for every PDF-shaped route.  The
    function refuses a smaller limit before the first download; failures are
    retained as coverage failures and no partial candidate set is released.
    """
    unresolved_pdf_access = [
        require_identifier(item.get("attachment_id"), "pending PDF attachment id")
        for item in attachments
        if attachment_looks_like_pdf(item)
        and item.get("classification") == "direct_material_access_pending"
    ]
    if unresolved_pdf_access:
        raise CoverageError(
            "PDF-shaped attachment(s) lacked an anonymous direct-access result: "
            + ", ".join(sorted(unresolved_pdf_access))
        )
    pdfs = [
        dict(item)
        for item in attachments
        if item.get("classification") == "public_pdf_pending_text"
    ]
    if max_pdf_downloads < len(pdfs):
        raise InputError(
            "--max-pdf-downloads is below the complete public-PDF ledger; refuse a partial prefix"
        )
    ensure_secure_directory(secure_dir)
    rows: list[dict[str, Any]] = []
    text_documents: list[dict[str, Any]] = []
    queue: list[dict[str, Any]] = []
    failures: list[str] = []
    for attachment in pdfs:
        attachment_id = require_identifier(
            attachment.get("attachment_id"), "PDF attachment id"
        )
        event_id = require_identifier(attachment.get("event_id"), "PDF event id")
        try:
            downloaded = client.download_pdf(
                str(attachment["download_url"]), secure_dir
            )
            parsed = extract_pdf_text(downloaded["_secure_path"], secure_dir)
            row = {
                "attachment_id": attachment_id,
                "event_id": event_id,
                "owner_kind": attachment["owner_kind"],
                "owner_id": attachment["owner_id"],
                "route_path": attachment["route_path"],
                "download_state": downloaded["download_state"],
                "pdf_sha256": downloaded["pdf_sha256"],
                "pdf_bytes": downloaded["pdf_bytes"],
                "secure_location_reference": downloaded["secure_location_reference"],
                "parse_state": parsed["parse_state"],
                "text_sha256": parsed["text_sha256"],
                "text_utf8_bytes": parsed["text_utf8_bytes"],
                "parser": parsed["parser"],
                "download_receipt": downloaded["receipt"],
            }
            rows.append(row)
            if parsed["parse_state"] == "text_extracted":
                text_documents.append(
                    {
                        "document_id": (
                            f"event:{event_id}:{attachment['owner_kind']}:{attachment['owner_id']}:"
                            f"attachment:{attachment_id}:pdf_text"
                        ),
                        "source_object_id": (
                            f"event:{event_id}:{attachment['owner_kind']}:{attachment['owner_id']}:"
                            f"attachment:{attachment_id}"
                        ),
                        "route_type": "public_pdf_full_text",
                        "candidate_eligible": True,
                        "fields": {
                            "full_text": Path(parsed["_text_path"]).read_text(
                                encoding="utf-8", errors="strict"
                            )
                        },
                    }
                )
            else:
                queue.append(
                    {
                        "queue_id": f"ESA-OCR-{event_id}-{attachment_id}",
                        "action": "ocr_public_pdf_from_secure_checksum",
                        "input": {
                            "event_id": event_id,
                            "attachment_id": attachment_id,
                            "pdf_sha256": downloaded["pdf_sha256"],
                        },
                        "reason": "Deterministic text extraction was empty.",
                        "required_output": [
                            "text_sha256",
                            "parser_or_ocr_route",
                            "completed_at",
                            "operator",
                        ],
                        "required_command": ocr_handoff_command_template(),
                        "failure_rule": "An absent/failed OCR receipt makes local PDF coverage incomplete.",
                    }
                )
        except HarvestError as error:
            failures.append(attachment_id)
            row = {
                "attachment_id": attachment_id,
                "event_id": event_id,
                "owner_kind": attachment["owner_kind"],
                "owner_id": attachment["owner_id"],
                "route_path": attachment["route_path"],
                "download_state": "failed",
                "parse_state": "not_attempted_or_failed",
                "error_type": type(error).__name__,
            }
            if isinstance(error, AccessError):
                row["access_status"] = "access_restricted_or_login"
            rows.append(row)
    completed = [
        row["attachment_id"]
        for row in rows
        if row.get("parse_state") == "text_extracted"
    ]
    coverage_complete = not failures and len(completed) == len(pdfs)
    return (
        {
            "required_confirmed_public_pdf_attachment_ids": [
                item["attachment_id"] for item in pdfs
            ],
            "completed_public_pdf_attachment_ids": completed,
            "failed_public_pdf_attachment_ids": failures,
            "coverage_complete": coverage_complete,
            "rows": rows,
            "failure_rule": "No partial PDF/text prefix is a final matching result.",
        },
        text_documents,
        queue,
    )


def parse_ocr_text_route(value: str) -> tuple[str, Path]:
    """Parse one explicit attachment-ID-to-external-OCR-text mapping."""
    attachment_id, separator, raw_path = value.partition("=")
    if not separator:
        raise InputError("--ocr-text-route must be ATTACHMENT_ID=OUTSIDE_GIT_TEXT_PATH")
    attachment_id = require_identifier(attachment_id, "OCR attachment id")
    text_path = Path(raw_path).expanduser()
    if not text_path.is_file():
        raise InputError("An OCR text route did not name an existing regular file")
    if git_ancestor(text_path) is not None:
        raise InputError("OCR text route must remain outside a Git worktree")
    return attachment_id, text_path


def strip_ocr_frontmatter(value: str) -> str:
    """Exclude converter provenance/path frontmatter from local source matching."""
    if not value.startswith("---"):
        return value
    marker = value.find("\n---", 3)
    if marker < 0:
        raise PdfError("OCR Markdown frontmatter was not terminated")
    body_start = value.find("\n", marker + 4)
    return "" if body_start < 0 else value[body_start + 1 :]


def load_ocr_completion_receipts(
    path: Path,
) -> tuple[dict[str, Mapping[str, Any]], str]:
    """Load content-safe OCR completion receipts keyed by attachment ID."""
    payload = load_json(path)
    if not isinstance(payload, Mapping):
        raise ParseError("OCR completion receipt bundle was not an object")
    if payload.get("receipt_schema_version") != "esa-indico-ocr-completion-receipts/v1":
        raise ParseError("OCR completion receipt bundle schema version was invalid")
    receipts = payload.get("receipts")
    if not isinstance(receipts, list):
        raise ParseError("OCR completion receipt bundle lacked a receipts list")
    by_attachment: dict[str, Mapping[str, Any]] = {}
    for receipt in receipts:
        if not isinstance(receipt, Mapping):
            raise ParseError("OCR completion receipt was not an object")
        attachment_id = require_identifier(receipt.get("attachment_id"), "OCR receipt attachment id")
        if attachment_id in by_attachment:
            raise IdentityError("OCR completion receipt repeated an attachment id")
        require_identifier(receipt.get("queue_id"), "OCR receipt queue id")
        require_identifier(receipt.get("pdf_sha256"), "OCR receipt PDF checksum")
        if receipt.get("terminal_outcome") != "ocr_text_extracted":
            raise CoverageError("OCR receipt did not report terminal OCR text extraction")
        if not isinstance(receipt.get("completed_at"), str) or not receipt["completed_at"].strip():
            raise ParseError("OCR completion receipt lacked a timestamp")
        operator = receipt.get("operator")
        if (
            not isinstance(operator, Mapping)
            or not isinstance(operator.get("type"), str)
            or not operator.get("type").strip()
            or not isinstance(operator.get("identifier"), str)
            or not operator.get("identifier").strip()
        ):
            raise ParseError("OCR completion receipt lacked an identified operator")
        for field in ("matched_ocr_body_sha256", "parser_or_ocr_route"):
            if not isinstance(receipt.get(field), str) or not receipt[field].strip():
                raise ParseError(f"OCR completion receipt lacked {field}")
        if (
            isinstance(receipt.get("matched_ocr_body_utf8_bytes"), bool)
            or not isinstance(receipt.get("matched_ocr_body_utf8_bytes"), int)
            or receipt["matched_ocr_body_utf8_bytes"] < 1
        ):
            raise ParseError("OCR completion receipt had invalid OCR body byte count")
        by_attachment[attachment_id] = receipt
    return by_attachment, sha256_file(path)


def apply_ocr_text_routes(
    pdf_coverage: Mapping[str, Any],
    text_documents: Sequence[Mapping[str, Any]],
    ocr_queue: Sequence[Mapping[str, Any]],
    ocr_text_routes: Mapping[str, Path],
    ocr_completion_receipts: Mapping[str, Mapping[str, Any]] | None,
    *,
    receipt_bundle_sha256: str | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Attach externally stored OCR text only for every pending OCR checksum.

    The source OCR Markdown is read only from the declared external workspace.
    The returned Git-safe ledger contains its hash/count and matching output, not
    the Markdown, images, path, or source snippets.
    """
    expected: dict[str, Mapping[str, Any]] = {}
    for queue_item in ocr_queue:
        if queue_item.get("action") != "ocr_public_pdf_from_secure_checksum":
            raise ParseError("Unexpected item in the PDF OCR queue")
        attachment_id = require_identifier(
            queue_item.get("input", {}).get("attachment_id"), "OCR queue attachment id"
        )
        if attachment_id in expected:
            raise IdentityError("OCR queue repeated an attachment id")
        expected[attachment_id] = queue_item
    if not ocr_text_routes:
        return dict(pdf_coverage), [dict(item) for item in text_documents], list(ocr_queue)
    if set(ocr_text_routes) != set(expected):
        raise CoverageError(
            "OCR text-route IDs did not reconcile exactly to the pending OCR queue"
        )
    if ocr_completion_receipts is None or receipt_bundle_sha256 is None:
        raise CoverageError(
            "OCR text routes require a content-safe completion receipt bundle"
        )
    if set(ocr_completion_receipts) != set(expected):
        raise CoverageError(
            "OCR completion receipt IDs did not reconcile exactly to the pending OCR queue"
        )

    coverage = dict(pdf_coverage)
    rows = [dict(row) for row in coverage.get("rows", [])]
    rows_by_id = {
        require_identifier(row.get("attachment_id"), "PDF coverage attachment id"): row
        for row in rows
    }
    documents = [dict(item) for item in text_documents]
    for attachment_id, text_path in sorted(ocr_text_routes.items()):
        queue_item = expected[attachment_id]
        row = rows_by_id.get(attachment_id)
        if row is None or row.get("parse_state") != "ocr_required":
            raise CoverageError("OCR route did not correspond to an OCR-required PDF")
        expected_pdf_sha256 = require_identifier(
            queue_item.get("input", {}).get("pdf_sha256"), "OCR queue PDF checksum"
        )
        if row.get("pdf_sha256") != expected_pdf_sha256:
            raise IdentityError("OCR route PDF checksum did not reconcile to its queue")
        completion_receipt = ocr_completion_receipts[attachment_id]
        if completion_receipt.get("queue_id") != queue_item.get("queue_id"):
            raise IdentityError("OCR completion receipt queue id did not reconcile")
        if completion_receipt.get("pdf_sha256") != expected_pdf_sha256:
            raise IdentityError("OCR completion receipt PDF checksum did not reconcile")
        raw_text = text_path.read_text(encoding="utf-8", errors="strict")
        text = strip_ocr_frontmatter(raw_text)
        if not text.strip():
            raise PdfError("OCR output contained no matchable text")
        text_digest = sha256_text(text)
        text_bytes = len(text.encode("utf-8"))
        if completion_receipt.get("matched_ocr_body_sha256") != text_digest:
            raise IdentityError("OCR completion receipt text checksum did not reconcile")
        if completion_receipt.get("matched_ocr_body_utf8_bytes") != text_bytes:
            raise IdentityError("OCR completion receipt text byte count did not reconcile")
        if completion_receipt.get("parser_or_ocr_route") != "pdf_to_markdown.py --image-mode keep":
            raise CoverageError("OCR completion receipt did not use the required OCR route")
        row["parse_state"] = "ocr_text_extracted"
        row["ocr_text_sha256"] = text_digest
        row["ocr_text_utf8_bytes"] = text_bytes
        row["ocr_parser_or_route"] = completion_receipt["parser_or_ocr_route"]
        row["ocr_secure_location_reference"] = f"sha256:{text_digest}"
        row["ocr_completion_receipt_bundle_sha256"] = receipt_bundle_sha256
        documents.append(
            {
                "document_id": (
                    f"event:{row['event_id']}:{row['owner_kind']}:{row['owner_id']}:"
                    f"attachment:{attachment_id}:pdf_ocr_text"
                ),
                "source_object_id": (
                    f"event:{row['event_id']}:{row['owner_kind']}:{row['owner_id']}:"
                    f"attachment:{attachment_id}"
                ),
                "route_type": "public_pdf_full_text_ocr",
                "candidate_eligible": True,
                "fields": {"full_text": text},
            }
        )
    completed = [
        row["attachment_id"]
        for row in rows
        if row.get("parse_state") in {"text_extracted", "ocr_text_extracted"}
    ]
    required = [
        require_identifier(value, "required confirmed public PDF attachment id")
        for value in coverage.get("required_confirmed_public_pdf_attachment_ids", [])
    ]
    coverage["rows"] = rows
    coverage["completed_public_pdf_attachment_ids"] = completed
    coverage["coverage_complete"] = (
        not coverage.get("failed_public_pdf_attachment_ids")
        and set(completed) == set(required)
        and len(completed) == len(required)
    )
    coverage["ocr_resolved_attachment_ids"] = sorted(ocr_text_routes)
    return coverage, documents, []


def build_manual_receipt_template(queue_item: Mapping[str, Any]) -> dict[str, Any]:
    """Return the strict, content-free receipt contract for one navigation item."""
    return {
        "receipt_schema_version": "esa-indico-manual-navigation-receipt/v1",
        "queue_id": queue_item["queue_id"],
        "completed_at": None,
        "operator": {"type": "human_or_llm", "identifier": None},
        "outcome": "pending",
        "input_echo": queue_item.get("input", {}),
        "observed_contribution_ids": [],
        "observed_attachment_ids": [],
        "observed_attachment_paths": [],
        "notes": "Record no source text, cookies, session identifiers, browser-tab URLs, or private data.",
    }


def validate_manual_receipts(
    queue: Sequence[Mapping[str, Any]], receipts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    expected = {str(item["queue_id"]): item for item in queue}
    seen: set[str] = set()
    resolved: list[str] = []
    unresolved: list[str] = []
    for receipt in receipts:
        if not isinstance(receipt, Mapping):
            raise ParseError("A manual receipt was not an object")
        if (
            receipt.get("receipt_schema_version")
            != "esa-indico-manual-navigation-receipt/v1"
        ):
            raise ParseError("Manual receipt schema version was invalid")
        queue_id = require_identifier(receipt.get("queue_id"), "receipt queue id")
        if queue_id not in expected or queue_id in seen:
            raise IdentityError("Manual receipt queue ids did not reconcile one-to-one")
        seen.add(queue_id)
        outcome = receipt.get("outcome")
        if outcome != "resolved":
            unresolved.append(queue_id)
            continue
        completed_at = receipt.get("completed_at")
        operator = receipt.get("operator")
        if (
            not isinstance(completed_at, str)
            or not completed_at.strip()
            or not isinstance(operator, Mapping)
            or not isinstance(operator.get("type"), str)
            or not operator.get("type").strip()
            or not isinstance(operator.get("identifier"), str)
            or not operator.get("identifier").strip()
        ):
            unresolved.append(queue_id)
            continue
        required_output = expected[queue_id].get("required_output", [])
        if not isinstance(required_output, list) or not all(
            isinstance(value, str) for value in required_output
        ):
            raise ParseError("Manual queue required_output was malformed")
        if any(
            receipt.get(field) is None or receipt.get(field) == ""
            for field in required_output
        ):
            unresolved.append(queue_id)
            continue
        input_event = str(expected[queue_id].get("input", {}).get("event_id", ""))
        observed_ids: set[str] = set()
        for attachment_id in receipt.get("observed_attachment_ids", []):
            observed_ids.add(
                require_identifier(attachment_id, "manual receipt attachment id")
            )
        for path in receipt.get("observed_attachment_paths", []):
            if not isinstance(path, str):
                raise ParseError("Manual receipt attachment path was not a string")
            parsed = direct_attachment_from_url(path)
            if parsed["event_id"] != input_event:
                raise IdentityError(
                    "Manual receipt attachment path had the wrong event id"
                )
            observed_ids.add(parsed["attachment_id"])
        expected_ids = {
            require_identifier(value, "expected attachment id")
            for value in expected[queue_id].get("expected_attachment_ids", [])
        }
        input_attachment_id = expected[queue_id].get("input", {}).get("attachment_id")
        if input_attachment_id is not None:
            expected_ids.add(
                require_identifier(input_attachment_id, "queue attachment id")
            )
        if not expected_ids.issubset(observed_ids):
            unresolved.append(queue_id)
            continue
        action = str(expected[queue_id].get("action", ""))
        if action in {
            "route_public_non_pdf_to_text_extractor_or_manual",
            "resolve_irregular_or_external_material",
        } and receipt.get("terminal_outcome") not in {
            "text_extracted",
            "manual_text_extracted",
        }:
            unresolved.append(queue_id)
            continue
        if action in {"download_and_extract_public_pdf", "ocr_public_pdf_from_secure_checksum"}:
            if receipt.get("terminal_outcome") not in {
                "text_extracted",
                "ocr_text_extracted",
            }:
                unresolved.append(queue_id)
                continue
        if action == "inspect_public_subcontribution_route":
            if receipt.get("terminal_outcome") != "route_enumerated_and_all_materials_terminal":
                unresolved.append(queue_id)
                continue
            observed_attachment_ids = receipt.get("observed_attachment_ids", [])
            observed_attachment_paths = receipt.get("observed_attachment_paths", [])
            if not observed_attachment_ids and not observed_attachment_paths:
                unresolved.append(queue_id)
                continue
            coverage_receipt = receipt.get("coverage_receipt_sha256")
            if not isinstance(coverage_receipt, str) or not re.fullmatch(
                r"[0-9a-f]{64}", coverage_receipt
            ):
                unresolved.append(queue_id)
                continue
        if action == "probe_anonymous_public_material_access":
            # A successful access probe must generate the appropriate PDF or
            # non-PDF terminal route; a receipt for the probe alone cannot
            # complete the document route.
            unresolved.append(queue_id)
            continue
        resolved.append(queue_id)
    unresolved.extend(sorted(set(expected) - seen))
    return {
        "receipt_validation_schema_version": "esa-indico-manual-receipt-validation/v1",
        "queue_item_count": len(expected),
        "receipt_count": len(receipts),
        "resolved_queue_ids": sorted(resolved),
        "unresolved_queue_ids": sorted(set(unresolved)),
        "coverage_complete": not unresolved and len(receipts) == len(expected),
    }


def default_dictionary_path() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "searches"
        / "search-concept-dictionary.json"
    )


def load_dictionary(
    path: Path, *, expected_sha256: str | None = None
) -> dict[str, Any]:
    if expected_sha256 is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise InputError("Expected concept-dictionary SHA-256 must be lowercase hex")
        actual_sha256 = sha256_file(path)
        if actual_sha256 != expected_sha256:
            raise CoverageError(
                "Loaded concept dictionary did not match the required SHA-256 lock"
            )
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("concepts"), dict):
        raise InputError("Concept dictionary was not an SLR1 concept dictionary object")
    required = {
        "P",
        "E_H",
        "E_F",
        "E",
        "M_H",
        "M_B",
        "M",
        "R",
        "G_model",
        "G_structure",
        "C1",
        "T2",
    }
    missing = required - set(data["concepts"])
    if missing:
        raise InputError(
            f"Concept dictionary was missing required concepts: {sorted(missing)}"
        )
    return data


def cmd_probe_search(args: argparse.Namespace) -> int:
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    probes = [
        probe_public_search(client, query=query, result_type=args.result_type)
        for query in args.query
    ]
    payload = {
        "probe_bundle_schema_version": "esa-indico-one-box-search-probes/v1",
        "created_at": now_iso(),
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "probes": probes,
    }
    write_json(Path(args.output_path), payload)
    print(
        json.dumps(
            {
                "status": "success",
                "output_path": args.output_path,
                "probe_count": len(probes),
            }
        )
    )
    return 0


def cmd_probe_access_status(args: argparse.Namespace) -> int:
    """Write only safe direct-material access observations for explicit URLs."""
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    checks: list[dict[str, Any]] = []
    for raw_url in args.attachment_url:
        parsed = direct_attachment_from_url(raw_url)
        receipt = client.probe_access_status(parsed["download_url"])
        checks.append(
            {
                "event_id": parsed["event_id"],
                "contribution_id": parsed["contribution_id"] or None,
                "attachment_id": parsed["attachment_id"],
                "route_path": parsed["route_path"],
                "access_status": receipt["access_status"],
                "receipt": receipt,
            }
        )
    status_counts = {
        status: sum(item["access_status"] == status for item in checks)
        for status in sorted({str(item["access_status"]) for item in checks})
    }
    payload = {
        "receipt_schema_version": "esa-indico-material-access-status-probe/v1",
        "created_at": now_iso(),
        "basis": "observed",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "checks": checks,
        "access_status_counts": status_counts,
        "privacy": {
            "response_headers_retained": False,
            "response_bodies_retained": False,
            "cookies_retained": False,
            "redirect_targets_retained": False,
            "session_identifiers_retained": False,
        },
        "scope_limit": (
            "This proves only the listed anonymous no-redirect direct-material checks; "
            "it does not enumerate or download an event corpus."
        ),
    }
    write_json(Path(args.output_path), payload)
    print(
        json.dumps(
            {
                "status": "success",
                "output_path": args.output_path,
                "check_count": len(checks),
                "access_status_counts": status_counts,
            }
        )
    )
    return 0


def cmd_probe_legacy_material_shape(args: argparse.Namespace) -> int:
    """Record a bounded export-shape check without retaining source material text."""
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    event_id = require_identifier(args.event_id, "event id")
    payload, receipt = client.get_json(event_export_url(event_id))
    _, contributions, subcontributions, attachments, _ = parse_event_export(
        payload, event_id
    )
    legacy_rows = [
        record
        for record in attachments.values()
        if "legacy_material_resource" in record.get("provenance", [])
    ]
    classifications = [classify_attachment(record) for record in legacy_rows]
    classification_counts = {
        classification: classifications.count(classification)
        for classification in sorted(set(classifications))
    }
    result = {
        "receipt_schema_version": "esa-indico-legacy-material-shape-probe/v1",
        "created_at": now_iso(),
        "basis": "observed",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "event_id": event_id,
        "event_export": {
            "detail": EVENT_EXPORT_DETAIL,
            "receipt": receipt,
            "contribution_count": len(contributions),
            "subcontribution_count": len(subcontributions),
            "recognized_attachment_count": len(attachments),
            "legacy_material_resource_count": len(legacy_rows),
            "legacy_material_resource_attachment_ids": sorted(
                (record["attachment_id"] for record in legacy_rows),
                key=lambda item: int(item) if item.isdigit() else item,
            ),
            "legacy_material_resource_owner_kinds": sorted(
                {str(record["owner_kind"]) for record in legacy_rows}
            ),
            "legacy_material_resource_classification_counts": classification_counts,
        },
        "scope_limit": (
            "This bounded export-shape check retains only route-safe identifiers, counts, and a response "
            "hash; it does not traverse owner pages, download material, or screen records."
        ),
    }
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "success",
                "output_path": args.output_path,
                "legacy_resource_count": len(legacy_rows),
            }
        )
    )
    return 0


def probe_event_material_shape(
    client: PublicClient, event_id: str
) -> dict[str, Any]:
    """Return either a safe shape inventory or an explicit event-local failure."""
    receipt: Mapping[str, Any] | None = None
    try:
        payload, receipt = client.get_json(event_export_url(event_id))
        _, contributions, subcontributions, attachments, _ = parse_event_export(
            payload, event_id
        )
        rows = []
        for attachment_id in sorted(
            attachments, key=lambda item: int(item) if item.isdigit() else item
        ):
            record = attachments[attachment_id]
            classification = classify_attachment(record)
            rows.append(
                {
                    "attachment_id": attachment_id,
                    "owner_kind": record["owner_kind"],
                    "owner_id": record["owner_id"],
                    "route_path": record["route_path"],
                    "route_status": record["route_status"],
                    "access_status": record["access_status"],
                    "classification": classification,
                    "provenance": record["provenance"],
                }
            )
        route_status_counts = {
            status: sum(row["route_status"] == status for row in rows)
            for status in sorted({str(row["route_status"]) for row in rows})
        }
        return {
            "event_id": event_id,
            "status": "success",
            "event_export_receipt": receipt,
            "contribution_count": len(contributions),
            "subcontribution_count": len(subcontributions),
            "attachment_count": len(rows),
            "route_status_counts": route_status_counts,
            "irregular_or_external_attachment_ids": [
                row["attachment_id"]
                for row in rows
                if row["route_status"] != "validated_direct_attachment"
            ],
            "legacy_material_resource_attachment_ids": [
                row["attachment_id"]
                for row in rows
                if "legacy_material_resource" in row["provenance"]
            ],
            "attachment_rows": rows,
        }
    except HarvestError as error:
        failure = {
            "event_id": event_id,
            "status": "failed",
            "error_type": type(error).__name__,
            "failure_rule": (
                "An export parse/identity failure is coverage null for this bounded event; "
                "do not infer a zero or continue from a partial material ledger."
            ),
        }
        if isinstance(error, IdentityError):
            conflict = re.fullmatch(
                r"Attachment (?P<attachment_id>[^ ]+) had conflicting (?P<field>[a-z_]+)",
                str(error),
            )
            if conflict:
                failure["safe_identity_conflict"] = conflict.groupdict()
        if receipt is not None:
            failure["event_export_receipt"] = receipt
        return failure


def cmd_probe_event_material_shapes(args: argparse.Namespace) -> int:
    """Inspect explicit event-export material route shapes without owner-page traversal."""
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    event_ids = [require_identifier(value, "event id") for value in args.event_id]
    if len(event_ids) != len(set(event_ids)):
        raise InputError("Repeat event ids are not allowed")
    if len(event_ids) > args.max_events:
        raise InputError("Explicit event count exceeds --max-events")
    events = [probe_event_material_shape(client, event_id) for event_id in event_ids]
    result = {
        "receipt_schema_version": "esa-indico-event-material-shape-probe/v1",
        "created_at": now_iso(),
        "basis": "observed",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "events": events,
        "failed_event_ids": [
            event["event_id"] for event in events if event.get("status") == "failed"
        ],
        "scope_limit": (
            "This reads only explicit event exports. It does not prove owner-page material reconciliation, "
            "direct public access, PDF text coverage, or terminal non-PDF routing."
        ),
    }
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "partial_diagnostic"
                if any(event.get("status") == "failed" for event in events)
                else "success",
                "output_path": args.output_path,
                "event_count": len(events),
                "failed_event_count": sum(
                    event.get("status") == "failed" for event in events
                ),
                "irregular_or_external_attachment_count": sum(
                    len(event.get("irregular_or_external_attachment_ids", []))
                    for event in events
                ),
            }
        )
    )
    return 0


def cmd_compare_event_details(args: argparse.Namespace) -> int:
    """Compare ESA's documented nested and sessions contribution inventories."""
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    event_id = require_identifier(args.event_id, "event id")
    nested_payload, nested_receipt = client.get_json(
        event_export_url(event_id, detail="subcontributions")
    )
    sessions_payload, sessions_receipt = client.get_json(
        event_export_url(event_id, detail="sessions")
    )
    nested = event_detail_inventory(
        nested_payload, event_id, detail="subcontributions"
    )
    sessions = event_detail_inventory(sessions_payload, event_id, detail="sessions")
    nested_ids = nested["contribution_ids_in_source_order"]
    session_ids = sessions["contribution_ids_in_source_order"]
    same_ids = set(nested_ids) == set(session_ids)
    result = {
        "receipt_schema_version": "esa-indico-event-detail-coverage-probe/v1",
        "created_at": now_iso(),
        "basis": "observed",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "event_id": event_id,
        "official_documentation": {
            "url": "https://docs.getindico.io/en/stable/http-api/exporters/event/",
            "documented_nested_detail": "subcontributions",
            "documented_nested_field": "subContributions",
            "documented_sessions_detail": "sessions",
        },
        "subcontributions_detail": {"receipt": nested_receipt, **nested},
        "sessions_detail": {"receipt": sessions_receipt, **sessions},
        "invariants": {
            "same_contribution_id_set": same_ids,
            "nested_detail_has_no_duplicate_contribution_ids": len(nested_ids)
            == len(set(nested_ids)),
            "sessions_detail_has_no_duplicate_contribution_ids": len(session_ids)
            == len(set(session_ids)),
        },
        "scope_limit": (
            "This compares one event's documented export detail routes. It does not prove an "
            "all-source census or a material-owner route for a non-empty subcontribution record."
        ),
    }
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "success" if same_ids else "failed",
                "output_path": args.output_path,
                "event_id": event_id,
                "same_contribution_id_set": same_ids,
            }
        )
    )
    return 0 if same_ids else 2


def cmd_ocr_handoff_readiness(args: argparse.Namespace) -> int:
    """Check the mandated OCR handoff interface without claiming OCR success."""
    ocr_output_dir = Path(args.ocr_output_dir)
    ensure_secure_directory(ocr_output_dir)
    script = (
        Path.home()
        / "agent-tools"
        / "processing"
        / "skills"
        / "pdf-to-markdown"
        / "scripts"
        / "pdf_to_markdown.py"
    )
    if not script.is_file():
        raise InputError("The mandated PDF-to-Markdown OCR script was not available")
    completed = subprocess.run(
        ["uv", "run", str(script), "--help"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    result = {
        "receipt_schema_version": "esa-indico-ocr-handoff-readiness/v1",
        "created_at": now_iso(),
        "basis": "observed_interface_check",
        "diagnostic_only": True,
        "ocr_invoked_on_source_pdf": False,
        "ocr_success_claimed": False,
        "tool_path_sha256": sha256_file(script),
        "help_exit_status": completed.returncode,
        "outside_git_ocr_output_directory_validated": True,
        "required_command": ocr_handoff_command_template(),
        "scope_limit": (
            "This checks only the local handoff interface. It is not an OCR execution, "
            "does not retain PDF/text/image content, and cannot resolve an empty PDF parse."
        ),
    }
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "success" if completed.returncode == 0 else "failed",
                "output_path": args.output_path,
                "ocr_success_claimed": False,
            }
        )
    )
    return 0 if completed.returncode == 0 else 2


def cmd_enumerate_window(args: argparse.Namespace) -> int:
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    ledger = enumerate_category_window(
        client,
        category_id=args.category_id,
        from_date=args.from_date,
        to_date=args.to_date,
    )
    ledger["created_at"] = now_iso()
    write_json(Path(args.output_path), ledger)
    print(
        json.dumps(
            {
                "status": "success",
                "output_path": args.output_path,
                "event_count": ledger["retrieved_total"],
            }
        )
    )
    return 0


def load_category_window_ledger(path: Path) -> dict[str, Any]:
    """Validate the safe shape needed to reconcile already recorded windows."""
    payload = load_json(path)
    if not isinstance(payload, Mapping):
        raise ParseError("Category-window ledger was not an object")
    if payload.get("ledger_schema_version") != "esa-indico-category-window/v1":
        raise ParseError("Category-window ledger schema version was invalid")
    category_id = require_identifier(payload.get("category_id"), "category ledger id")
    from_date = parse_date_argument(str(payload.get("from_date")), "ledger from_date")
    to_date = parse_date_argument(str(payload.get("to_date")), "ledger to_date")
    count = payload.get("source_reported_total")
    retrieved = payload.get("retrieved_total")
    rows = payload.get("event_rows")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        or isinstance(retrieved, bool)
        or not isinstance(retrieved, int)
        or not isinstance(rows, list)
        or count != retrieved
        or count != len(rows)
        or payload.get("totals_reconciled") is not True
    ):
        raise CoverageError("Category-window ledger totals did not reconcile")
    event_ids: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ParseError("Category-window ledger contained a non-object row")
        event_ids.append(require_identifier(row.get("event_id"), "ledger event id"))
    if len(event_ids) != len(set(event_ids)):
        raise IdentityError("Category-window ledger repeated an event id")
    receipt = payload.get("receipt")
    if not isinstance(receipt, Mapping) or not isinstance(
        receipt.get("response_sha256"), str
    ):
        raise ParseError("Category-window ledger lacked a safe response checksum")
    return {
        "artifact": path.name,
        "category_id": category_id,
        "from_date": from_date,
        "to_date": to_date,
        "source_reported_total": count,
        "retrieved_total": retrieved,
        "source_complete_flag_status": payload.get("source_complete_flag_status"),
        "response_sha256": receipt["response_sha256"],
        "event_ids_in_source_order": event_ids,
    }


def cmd_reconcile_category_windows(args: argparse.Namespace) -> int:
    """Reconcile explicit, safe category-window ledgers without fetching source data."""
    ledgers = [load_category_window_ledger(Path(value)) for value in args.ledger_path]
    categories = {ledger["category_id"] for ledger in ledgers}
    if len(categories) != 1:
        raise InputError("Category-window reconciliation requires exactly one category id")
    occurrences: dict[str, list[str]] = {}
    union_ids: list[str] = []
    for ledger in ledgers:
        for event_id in ledger["event_ids_in_source_order"]:
            if event_id not in occurrences:
                union_ids.append(event_id)
                occurrences[event_id] = []
            occurrences[event_id].append(ledger["artifact"])
    duplicate_occurrences = {
        event_id: artifacts
        for event_id, artifacts in occurrences.items()
        if len(artifacts) > 1
    }
    same_input_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for ledger in ledgers:
        key = (ledger["category_id"], ledger["from_date"], ledger["to_date"])
        same_input_groups.setdefault(key, []).append(ledger)
    repeated_input_passes = []
    repeated_inputs_match = True
    for key, group in sorted(same_input_groups.items()):
        if len(group) < 2:
            continue
        baseline = group[0]
        match = all(
            item["source_reported_total"] == baseline["source_reported_total"]
            and item["event_ids_in_source_order"]
            == baseline["event_ids_in_source_order"]
            and item["response_sha256"] == baseline["response_sha256"]
            and item["source_complete_flag_status"]
            == baseline["source_complete_flag_status"]
            for item in group[1:]
        )
        repeated_inputs_match = repeated_inputs_match and match
        repeated_input_passes.append(
            {
                "category_id": key[0],
                "from_date": key[1],
                "to_date": key[2],
                "artifacts": [item["artifact"] for item in group],
                "identical_count_order_hash_and_complete_flag": match,
            }
        )
    result = {
        "receipt_schema_version": "esa-indico-category-window-reconciliation/v1",
        "created_at": now_iso(),
        "basis": "observed",
        "diagnostic_only": True,
        "category_id": next(iter(categories)),
        "input_windows": ledgers,
        "event_id_union_in_first_occurrence_order": union_ids,
        "duplicate_event_occurrences": duplicate_occurrences,
        "repeated_input_passes": repeated_input_passes,
        "invariants": {
            "all_input_totals_reconciled": True,
            "all_input_category_ids_match": True,
            "all_input_event_ids_unique_within_window": True,
            "repeated_input_count_order_hash_and_complete_flag_match": repeated_inputs_match,
        },
        "scope_limit": (
            "This reconciles only the explicitly supplied bounded ledgers. It does not establish "
            "an all-time root-category boundary, recursive-category semantics, or absence of a cap."
        ),
    }
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "success" if repeated_inputs_match else "failed",
                "output_path": args.output_path,
                "window_count": len(ledgers),
                "event_id_union_count": len(union_ids),
                "repeated_input_passes_match": repeated_inputs_match,
            }
        )
    )
    return 0 if repeated_inputs_match else 2


def cmd_compare_category_scopes(args: argparse.Namespace) -> int:
    """Compare one root-category window with explicit component-category windows."""
    root = load_category_window_ledger(Path(args.root_ledger_path))
    components = [
        load_category_window_ledger(Path(value)) for value in args.component_ledger_path
    ]
    if root["category_id"] != "0":
        raise InputError("Root scope comparison requires a category-0 root ledger")
    if not components:
        raise InputError("At least one component-category ledger is required")
    if any(
        component["from_date"] != root["from_date"]
        or component["to_date"] != root["to_date"]
        for component in components
    ):
        raise InputError("Category scope ledgers must have identical date inputs")
    component_ids = [
        event_id
        for component in components
        for event_id in component["event_ids_in_source_order"]
    ]
    if len(component_ids) != len(set(component_ids)):
        raise IdentityError("Component category ledgers overlapped on an event id")
    root_ids = set(root["event_ids_in_source_order"])
    component_id_set = set(component_ids)
    same_union = root_ids == component_id_set
    result = {
        "receipt_schema_version": "esa-indico-category-scope-comparison/v1",
        "created_at": now_iso(),
        "basis": "observed",
        "diagnostic_only": True,
        "root_window": root,
        "component_windows": components,
        "invariants": {
            "root_event_ids_equal_component_union": same_union,
            "component_event_ids_disjoint": True,
            "date_inputs_match": True,
        },
        "scope_limit": (
            "A matching bounded union shows that category 0 returned the tested nonzero category IDs "
            "for this window. It does not prove that these are all descendants or that category 0 is "
            "an all-time exhaustive public universe."
        ),
    }
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "success" if same_union else "failed",
                "output_path": args.output_path,
                "root_event_ids_equal_component_union": same_union,
            }
        )
    )
    return 0 if same_union else 2


def cmd_harvest_event(args: argparse.Namespace) -> int:
    event_ids = [require_identifier(value, "event id") for value in args.event_id]
    if len(event_ids) != len(set(event_ids)):
        raise InputError("Repeat event ids are not allowed")
    if len(event_ids) > args.max_events:
        raise InputError(
            "Explicit event count exceeds --max-events; refuse a possible partial prefix"
        )
    dictionary_path = Path(args.dictionary)
    if args.match_metadata and not args.expected_dictionary_sha256:
        raise InputError(
            "--match-metadata requires --expected-dictionary-sha256 from local-method-spec.json"
        )
    dictionary = load_dictionary(
        dictionary_path, expected_sha256=args.expected_dictionary_sha256
    )
    dictionary_sha256 = sha256_file(dictionary_path)
    client = PublicClient(
        timeout_seconds=args.timeout,
        min_request_interval=args.min_request_interval,
        retries=args.retries,
    )
    ledgers = []
    pdf_download_count = 0
    secure_dir = (
        Path(args.secure_material_dir)
        if args.download_pdfs and args.secure_material_dir
        else None
    )
    if args.download_pdfs and secure_dir is None:
        raise InputError("--download-pdfs requires --secure-material-dir outside Git")
    if args.download_pdfs and not args.probe_material_access:
        raise InputError(
            "--download-pdfs requires --probe-material-access so every PDF-shaped route has a direct public-access result"
        )
    if args.ocr_text_route and not args.download_pdfs:
        raise InputError("--ocr-text-route requires --download-pdfs")
    if args.ocr_text_route and len(event_ids) != 1:
        raise InputError("--ocr-text-route is bounded to exactly one event per invocation")
    if args.ocr_text_route and not args.ocr_completion_receipt_path:
        raise InputError(
            "--ocr-text-route requires --ocr-completion-receipt-path with content-safe OCR receipts"
        )
    if args.ocr_completion_receipt_path and not args.ocr_text_route:
        raise InputError("--ocr-completion-receipt-path requires --ocr-text-route")
    ocr_completion_receipts: dict[str, Mapping[str, Any]] | None = None
    ocr_receipt_bundle_sha256: str | None = None
    if args.ocr_completion_receipt_path:
        ocr_completion_receipts, ocr_receipt_bundle_sha256 = load_ocr_completion_receipts(
            Path(args.ocr_completion_receipt_path)
        )
    ocr_text_routes: dict[str, Path] = {}
    for route_spec in args.ocr_text_route:
        attachment_id, text_path = parse_ocr_text_route(route_spec)
        if attachment_id in ocr_text_routes:
            raise InputError("An OCR attachment id was supplied more than once")
        ocr_text_routes[attachment_id] = text_path
    for event_id in event_ids:
        ledger, documents, attachments = harvest_event(
            client,
            event_id=event_id,
            dictionary=dictionary,
            max_contribution_pages=args.max_contribution_pages,
            perform_matching=args.match_metadata and not args.download_pdfs,
            probe_material_access=args.probe_material_access,
            max_attachments=args.max_attachments,
        )
        if args.download_pdfs:
            assert secure_dir is not None
            pdf_coverage, pdf_documents, ocr_queue = process_public_pdf_routes(
                client,
                attachments,
                secure_dir=secure_dir,
                max_pdf_downloads=args.max_pdf_downloads,
            )
            pdf_download_count += sum(
                row.get("download_state") in {"downloaded", "reused_checkpoint"}
                for row in pdf_coverage["rows"]
            )
            if ocr_text_routes:
                pdf_coverage, pdf_documents, ocr_queue = apply_ocr_text_routes(
                    pdf_coverage,
                    pdf_documents,
                    ocr_queue,
                    ocr_text_routes,
                    ocr_completion_receipts,
                    receipt_bundle_sha256=ocr_receipt_bundle_sha256,
                )
            pdf_rows_by_id = {
                str(row["attachment_id"]): row for row in pdf_coverage["rows"]
            }
            for attachment_row in ledger["attachment_rows"]:
                pdf_row = pdf_rows_by_id.get(str(attachment_row["attachment_id"]))
                if pdf_row is None:
                    continue
                terminal_text_status = pdf_row.get("parse_state")
                attachment_row["terminal_text_status"] = terminal_text_status
                if terminal_text_status == "text_extracted":
                    attachment_row["source_boundary_disposition"] = "public_pdf_text_extracted"
                elif terminal_text_status == "ocr_text_extracted":
                    attachment_row["source_boundary_disposition"] = "public_pdf_ocr_text_extracted"
                else:
                    attachment_row["source_boundary_disposition"] = "public_pdf_text_coverage_incomplete"
            ledger["pdf_text_coverage"] = pdf_coverage
            ledger["manual_navigation_queue"] = [
                item
                for item in ledger["manual_navigation_queue"]
                if not str(item.get("queue_id", "")).startswith(
                    f"ESA-NAV-{event_id}-PDF-"
                )
            ] + ocr_queue
            material_coverage_complete = bool(
                ledger.get("material_route_coverage", {}).get("coverage_complete")
            )
            if (
                pdf_coverage["coverage_complete"]
                and material_coverage_complete
                and args.match_metadata
            ):
                ledger["matching"] = match_documents(
                    documents + pdf_documents, dictionary
                )
                ledger["matching_is_final_candidate_set"] = False
            elif args.match_metadata:
                ledger["matching"] = {
                    "matching_schema_version": "esa-indico-local-matching/v1",
                    "performed": False,
                    "reason": (
                        "PDF or non-PDF material coverage was incomplete; no partial candidate "
                        "matching was released."
                    ),
                }
                ledger["matching_is_final_candidate_set"] = False
        ledgers.append(ledger)
    payload = {
        "run_schema_version": "esa-indico-bounded-event-run/v1",
        "created_at": now_iso(),
        "protocol_commit": args.protocol_commit,
        "concept_dictionary": {
            "artifact_version": dictionary.get("artifact_version"),
            "sha256": dictionary_sha256,
            "lock_required_for_matching": True,
        },
        "diagnostic_only": True,
        "candidate_import_permitted": False,
        "event_ledgers": ledgers,
    }
    write_json(Path(args.output_path), payload)
    if args.queue_output_path:
        queue = {
            "queue_schema_version": "esa-indico-manual-navigation-queue/v1",
            "created_at": now_iso(),
            "protocol_commit": args.protocol_commit,
            "diagnostic_only": True,
            "items": [
                item
                for ledger in ledgers
                for item in ledger.get("manual_navigation_queue", [])
            ],
        }
        write_json(Path(args.queue_output_path), queue)
    print(
        json.dumps(
            {
                "status": "partial_diagnostic",
                "output_path": args.output_path,
                "event_count": len(ledgers),
                "pdfs_downloaded": pdf_download_count,
            }
        )
    )
    return 0


def cmd_receipt_templates(args: argparse.Namespace) -> int:
    queue_payload = load_json(Path(args.queue_path))
    queue = queue_payload.get("items") if isinstance(queue_payload, Mapping) else None
    if not isinstance(queue, list):
        raise InputError("Queue input must contain an items list")
    payload = {
        "template_bundle_schema_version": "esa-indico-manual-navigation-templates/v1",
        "created_at": now_iso(),
        "templates": [build_manual_receipt_template(item) for item in queue],
    }
    write_json(Path(args.output_path), payload)
    print(
        json.dumps(
            {
                "status": "success",
                "output_path": args.output_path,
                "template_count": len(queue),
            }
        )
    )
    return 0


def cmd_validate_receipts(args: argparse.Namespace) -> int:
    queue_payload = load_json(Path(args.queue_path))
    queue = queue_payload.get("items") if isinstance(queue_payload, Mapping) else None
    if not isinstance(queue, list):
        raise InputError("Queue input must contain an items list")
    receipts: list[Mapping[str, Any]] = []
    for path_string in args.receipt_path:
        payload = load_json(Path(path_string))
        if isinstance(payload, list):
            receipts.extend(payload)
        else:
            receipts.append(payload)
    result = validate_manual_receipts(queue, receipts)
    result["validated_at"] = now_iso()
    write_json(Path(args.output_path), result)
    print(
        json.dumps(
            {
                "status": "success" if result["coverage_complete"] else "incomplete",
                **result,
            }
        )
    )
    return 0 if result["coverage_complete"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bounded, public-only ESA Indico local-harvest helper for SLR1"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def http_options(target: argparse.ArgumentParser) -> None:
        target.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
        target.add_argument(
            "--min-request-interval", type=float, default=DEFAULT_MIN_REQUEST_INTERVAL
        )
        target.add_argument("--retries", type=int, default=DEFAULT_RETRIES)

    search = subparsers.add_parser(
        "probe-search", help="record bounded one-box search behavior without screening"
    )
    search.add_argument("--query", action="append", required=True)
    search.add_argument(
        "--result-type", choices=("events", "contributions", "materials"), required=True
    )
    search.add_argument("--output-path", required=True)
    http_options(search)
    search.set_defaults(handler=cmd_probe_search)

    access_probe = subparsers.add_parser(
        "probe-access-status",
        help="safely classify explicit direct-material URLs without retaining response headers or bodies",
    )
    access_probe.add_argument("--attachment-url", action="append", required=True)
    access_probe.add_argument("--output-path", required=True)
    http_options(access_probe)
    access_probe.set_defaults(handler=cmd_probe_access_status)

    legacy_shape = subparsers.add_parser(
        "probe-legacy-material-shape",
        help="inspect one explicit event export for legacy material.resources topology",
    )
    legacy_shape.add_argument("--event-id", required=True)
    legacy_shape.add_argument("--output-path", required=True)
    http_options(legacy_shape)
    legacy_shape.set_defaults(handler=cmd_probe_legacy_material_shape)

    material_shapes = subparsers.add_parser(
        "probe-event-material-shapes",
        help="inspect explicit event-export material route shapes without owner-page traversal",
    )
    material_shapes.add_argument("--event-id", action="append", required=True)
    material_shapes.add_argument("--max-events", type=int, default=12)
    material_shapes.add_argument("--output-path", required=True)
    http_options(material_shapes)
    material_shapes.set_defaults(handler=cmd_probe_event_material_shapes)

    details = subparsers.add_parser(
        "compare-event-details",
        help="compare documented subcontributions and sessions contribution inventories",
    )
    details.add_argument("--event-id", required=True)
    details.add_argument("--output-path", required=True)
    http_options(details)
    details.set_defaults(handler=cmd_compare_event_details)

    ocr_handoff = subparsers.add_parser(
        "ocr-handoff-readiness",
        help="safely check the mandated OCR handoff without processing a source PDF",
    )
    ocr_handoff.add_argument("--ocr-output-dir", required=True)
    ocr_handoff.add_argument("--output-path", required=True)
    ocr_handoff.set_defaults(handler=cmd_ocr_handoff_readiness)

    category = subparsers.add_parser(
        "enumerate-window", help="enumerate one explicit category date window"
    )
    category.add_argument("--category-id", default="0")
    category.add_argument("--from-date", required=True)
    category.add_argument("--to-date", required=True)
    category.add_argument("--output-path", required=True)
    http_options(category)
    category.set_defaults(handler=cmd_enumerate_window)

    reconcile_category = subparsers.add_parser(
        "reconcile-category-windows",
        help="reconcile explicit safe ledgers for one category without fetching source data",
    )
    reconcile_category.add_argument("--ledger-path", action="append", required=True)
    reconcile_category.add_argument("--output-path", required=True)
    reconcile_category.set_defaults(handler=cmd_reconcile_category_windows)

    compare_category = subparsers.add_parser(
        "compare-category-scopes",
        help="compare one category-0 window to explicit component-category windows",
    )
    compare_category.add_argument("--root-ledger-path", required=True)
    compare_category.add_argument("--component-ledger-path", action="append", required=True)
    compare_category.add_argument("--output-path", required=True)
    compare_category.set_defaults(handler=cmd_compare_category_scopes)

    event = subparsers.add_parser(
        "harvest-event", help="harvest explicit event IDs without downloading PDFs"
    )
    event.add_argument("--event-id", action="append", required=True)
    event.add_argument("--max-events", type=int, default=3)
    event.add_argument("--max-contribution-pages", type=int, default=25)
    event.add_argument(
        "--max-attachments",
        type=int,
        default=None,
        help="Optional fail-closed bound before material probes for the explicit event/all-route attachment ledger.",
    )
    event.add_argument("--dictionary", default=str(default_dictionary_path()))
    event.add_argument(
        "--expected-dictionary-sha256",
        help="Required SHA-256 lock from local-method-spec.json whenever --match-metadata is used.",
    )
    event.add_argument(
        "--match-metadata",
        action="store_true",
        help="Run deterministic matching only after the requested route coverage is complete; never imports candidates.",
    )
    event.add_argument(
        "--download-pdfs",
        action="store_true",
        help="Download/hash/extract every explicit public PDF to --secure-material-dir outside Git.",
    )
    event.add_argument("--secure-material-dir")
    event.add_argument(
        "--probe-material-access",
        action="store_true",
        help="Anonymous no-redirect GET-classify every same-origin direct material before routing it.",
    )
    event.add_argument(
        "--max-pdf-downloads",
        type=int,
        default=0,
        help="Must be at least the complete public-PDF ledger before downloads start.",
    )
    event.add_argument(
        "--ocr-text-route",
        action="append",
        default=[],
        metavar="ATTACHMENT_ID=OUTSIDE_GIT_TEXT_PATH",
        help="Complete every pending OCR item with external OCR Markdown; never stores that text in Git.",
    )
    event.add_argument(
        "--ocr-completion-receipt-path",
        help="Content-safe OCR completion receipt bundle that must reconcile to every --ocr-text-route.",
    )
    event.add_argument("--protocol-commit", required=True)
    event.add_argument("--output-path", required=True)
    event.add_argument(
        "--queue-output-path",
        help="Optional content-free queue for manual/browser/OCR fallback receipts.",
    )
    http_options(event)
    event.set_defaults(handler=cmd_harvest_event)

    templates = subparsers.add_parser(
        "receipt-templates", help="create content-free manual receipt templates"
    )
    templates.add_argument("--queue-path", required=True)
    templates.add_argument("--output-path", required=True)
    templates.set_defaults(handler=cmd_receipt_templates)

    receipts = subparsers.add_parser(
        "validate-receipts", help="validate manual-navigation receipts"
    )
    receipts.add_argument("--queue-path", required=True)
    receipts.add_argument("--receipt-path", action="append", required=True)
    receipts.add_argument("--output-path", required=True)
    receipts.set_defaults(handler=cmd_validate_receipts)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except HarvestError as error:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error_type": type(error).__name__,
                    "message": str(error),
                }
            ),
            file=sys.stderr,
        )
        return 1
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error_type": type(error).__name__,
                    "message": "Local harvest operation failed.",
                }
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
