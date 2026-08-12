#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests==2.34.2"]
# ///
"""Reconcile complete, ordered Scopus or IEEE Xplore API result pages.

The script deliberately serializes neither credentials nor cookies.  It writes
source responses and ordered ID/rank reconciliations only to an explicitly
selected, access-controlled output directory.  Its default classification is
``pilot_not_candidate_search``; those outputs must never be screened or merged
into the review corpus.

A run succeeds only when every expected page is present, source IDs are unique,
the source total remains unchanged, and retrieved records equal the first-page
source total.  A two-pass run additionally requires an identical global ordered
source-ID sequence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote_plus, urlsplit, urlunsplit

import requests


SCOPUS_ENDPOINT = "https://api.elsevier.com/content/search/scopus"
IEEE_ENDPOINT = "https://ieeexplore.ieee.org/rest/search"
SCOPUS_VIEW = "COMPLETE"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 1.0
DEFAULT_PAGE_DELAY_SECONDS = 0.5
MAX_RETRY_DELAY_SECONDS = 60.0
RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}
ACCESS_STATUS_CODES = {401, 403, 418}
# Compare normalized names so API/header spelling variants such as ``apiKey``,
# ``api_key``, and ``X-ELS-APIKey`` cannot reach a private raw artifact.
# These are exact normalized names, not substring matches: bibliographic fields
# such as ``keywords`` must remain intact.
SENSITIVE_NAME_NORMALIZATIONS = {
    "apikey",
    "authorization",
    "proxyauthorization",
    "accesstoken",
    "token",
    "idtoken",
    "refreshtoken",
    "cookie",
    "setcookie",
    "xelsapikey",
    "password",
    "passwd",
    "secret",
    "clientsecret",
    "privatekey",
    "accesskey",
    "accountid",
    "csrf",
    "csrftoken",
    "jsessionid",
    "searchid",
    "searchsession",
    "session",
    "sessionid",
    "sessiontoken",
    "sid",
    "xsrf",
    "xsrftoken",
    "bearertoken",
    "credential",
    "credentials",
    "userinfo",
}
IEEE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://ieeexplore.ieee.org",
    "Referer": "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
SCOPUS_PUBLIC_HEADERS = {"Accept": "application/json"}


class ReconciliationError(RuntimeError):
    """A response cannot safely be used as a complete search result."""


class TotalChangedError(ReconciliationError):
    """The API-reported total changed inside one logical snapshot."""


class OrderingChangedError(ReconciliationError):
    """Two complete passes did not return the same ordered ID sequence."""


def normalized_sensitive_name(value: Any) -> str:
    """Normalize an object or URL-query key before sensitive-key comparison."""
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def is_sensitive_name(value: Any) -> bool:
    """Return whether a key is unsafe to serialize in a private raw artifact."""
    return normalized_sensitive_name(value) in SENSITIVE_NAME_NORMALIZATIONS


def ensure_private_directory(path: Path) -> None:
    """Create an artifact directory and restrict it to its owner on POSIX."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            os.chmod(path, 0o700)
    except OSError as error:
        raise ReconciliationError(f"could not create/restrict private artifact directory {path}") from error


@dataclass
class ParsedPage:
    """Validated source-native position and records for one page."""

    total: int
    start: int
    end_exclusive: int
    server_page_size: int
    records: list[dict[str, Any]]
    identifiers: list[str]
    normalized_records: list[dict[str, Any]]
    response_details: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def atomic_write_json(path: Path, value: Any) -> None:
    ensure_private_directory(path.parent)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(value, temporary, indent=2, ensure_ascii=False)
            temporary.write("\n")
        if os.name != "nt":
            os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
    except OSError:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def parse_nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ReconciliationError(f"{field} was boolean rather than an integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
    else:
        raise ReconciliationError(f"{field} was not a non-negative integer")
    if parsed < 0:
        raise ReconciliationError(f"{field} was negative")
    return parsed


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def year_from_text(value: Any) -> int | None:
    match = re.search(r"(?:19|20)\d{2}", clean_text(value))
    return int(match.group(0)) if match else None


def decoded_url_component(value: str) -> str | None:
    """Decode a bounded URL context, treating deeper nesting as unsafe."""
    decoded = value
    for _ in range(8):
        next_value = unquote_plus(decoded)
        if next_value == decoded:
            return decoded
        decoded = next_value
    # Do not retain a component whose remaining encoding cannot be inspected.
    return decoded if unquote_plus(decoded) == decoded else None


def contains_sensitive_parameter(value: str) -> bool:
    """Detect direct or encoded sensitive URL context, failing closed."""
    decoded = decoded_url_component(value)
    if decoded is None:
        return True
    pieces = re.split(r"[?&;#]", decoded)
    if any(is_sensitive_name(item.split("=", 1)[0]) for item in pieces):
        return True
    for item in pieces:
        if "=" not in item:
            continue
        try:
            nested = urlsplit(item.split("=", 1)[1])
            _ = nested.port
            if "@" in nested.netloc:
                return True
        except ValueError:
            return True
    return False


def redacted_query(query: str) -> str:
    """Remove sensitive query pieces while preserving benign pieces verbatim."""
    retained: list[str] = []
    pieces = re.split(r"([&;])", query)
    for index in range(0, len(pieces), 2):
        item = pieces[index]
        separator = pieces[index - 1] if index else ""
        if contains_sensitive_parameter(item):
            continue
        if retained:
            retained.append(separator or "&")
        retained.append(item)
    return "".join(retained)


def redacted_url(value: str) -> str:
    """Redact URL context and fail closed when a URL cannot be parsed."""
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        return ""
    filtered_query = redacted_query(parsed.query)
    fragment_contains_sensitive_parameter = contains_sensitive_parameter(parsed.fragment)
    safe_netloc = parsed.netloc.rsplit("@", 1)[-1]
    decoded_netloc = decoded_url_component(parsed.netloc)
    if decoded_netloc is None:
        return ""
    encoded_authority_userinfo = safe_netloc == parsed.netloc and "@" in decoded_netloc
    if (
        filtered_query == parsed.query
        and not fragment_contains_sensitive_parameter
        and safe_netloc == parsed.netloc
        and not encoded_authority_userinfo
    ):
        return value
    if encoded_authority_userinfo:
        return ""
    return urlunsplit(
        (
            parsed.scheme,
            safe_netloc,
            parsed.path,
            filtered_query,
            "" if fragment_contains_sensitive_parameter else parsed.fragment,
        )
    )


def scrub_sensitive(value: Any) -> Any:
    """Drop known secret/context fields from a source response before persistence."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if is_sensitive_name(key):
                continue
            cleaned[str(key)] = scrub_sensitive(item)
        return cleaned
    if isinstance(value, list):
        return [scrub_sensitive(item) for item in value]
    if isinstance(value, str):
        return redacted_url(value)
    return value


def retry_delay_seconds(response: requests.Response | None, attempt: int, backoff_seconds: float) -> float:
    """Honor Retry-After if parseable without persisting response headers."""
    retry_after = ""
    if response is not None:
        retry_after = str(response.headers.get("Retry-After", "")).strip()
    if retry_after:
        try:
            return min(MAX_RETRY_DELAY_SECONDS, max(0.0, float(retry_after)))
        except ValueError:
            try:
                retry_time = parsedate_to_datetime(retry_after)
                if retry_time.tzinfo is None:
                    retry_time = retry_time.replace(tzinfo=timezone.utc)
                delay = (retry_time - datetime.now(timezone.utc)).total_seconds()
                return min(MAX_RETRY_DELAY_SECONDS, max(0.0, delay))
            except (IndexError, OverflowError, TypeError, ValueError):
                pass
    return min(MAX_RETRY_DELAY_SECONDS, max(0.0, backoff_seconds * (2**attempt)))


def looks_like_html_or_challenge(response: requests.Response) -> bool:
    content_type = str(response.headers.get("Content-Type", "")).casefold()
    preview = response.text[:8_000].lstrip().casefold()
    if "text/html" in content_type or "application/xhtml" in content_type:
        return True
    if preview.startswith(("<html", "<!doctype html")):
        return True
    markers = ("captcha", "access denied", "unusual traffic", "challenge-platform", "imperva")
    return "json" not in content_type and any(marker in preview for marker in markers)


def fetch_json(
    *,
    source: str,
    method: str,
    endpoint: str,
    headers: dict[str, str],
    params: dict[str, str] | None,
    payload: dict[str, Any] | None,
    timeout_seconds: float,
    retries: int,
    backoff_seconds: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fetch one page with bounded retries and no persisted response headers."""
    retry_events: list[dict[str, Any]] = []
    for attempt in range(retries + 1):
        response: requests.Response | None = None
        try:
            if method == "GET":
                response = requests.get(
                    endpoint,
                    params=params,
                    headers=headers,
                    timeout=timeout_seconds,
                    allow_redirects=False,
                )
            else:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=timeout_seconds,
                    allow_redirects=False,
                )
        except requests.RequestException as error:
            if attempt >= retries:
                raise ReconciliationError(
                    f"{source} network request failed after {attempt + 1} attempt(s) ({type(error).__name__})"
                ) from error
            delay = retry_delay_seconds(None, attempt, backoff_seconds)
            retry_events.append(
                {
                    "attempt": attempt + 1,
                    "event": "network_error",
                    "error_type": type(error).__name__,
                    "retry_delay_seconds": delay,
                }
            )
            time.sleep(delay)
            continue

        status = int(response.status_code)
        if 300 <= status < 400:
            raise ReconciliationError(f"{source} redirected page retrieval (HTTP {status})")
        if source == "ieee" and looks_like_html_or_challenge(response):
            raise ReconciliationError("IEEE Xplore returned an HTML/challenge page rather than JSON")
        if status in ACCESS_STATUS_CODES:
            raise ReconciliationError(f"{source} access/authentication response (HTTP {status})")
        if status in RETRYABLE_STATUS_CODES:
            if attempt >= retries:
                raise ReconciliationError(
                    f"{source} retryable response persisted after {attempt + 1} attempt(s) (HTTP {status})"
                )
            delay = retry_delay_seconds(response, attempt, backoff_seconds)
            retry_events.append(
                {
                    "attempt": attempt + 1,
                    "event": f"http_{status}",
                    "retry_delay_seconds": delay,
                }
            )
            time.sleep(delay)
            continue
        if status >= 400:
            raise ReconciliationError(f"{source} rejected page retrieval (HTTP {status})")

        try:
            data = response.json()
        except ValueError as error:
            raise ReconciliationError(f"{source} returned non-JSON content") from error
        if not isinstance(data, dict):
            raise ReconciliationError(f"{source} returned JSON that was not an object")
        return data, retry_events

    raise ReconciliationError(f"{source} request exhausted without a response")  # pragma: no cover


def scopus_public_request(query: str, start: int, page_size: int, sort: str) -> dict[str, Any]:
    return {
        "method": "GET",
        "endpoint": SCOPUS_ENDPOINT,
        "headers": {
            **SCOPUS_PUBLIC_HEADERS,
            "X-ELS-APIKey": "not_serialized; supplied only from secure runtime environment",
        },
        "query_parameters": {
            "query": query,
            "count": str(page_size),
            "start": str(start),
            "view": SCOPUS_VIEW,
            "sort": sort,
            "httpAccept": "application/json",
        },
    }


def ieee_public_request(
    query: str,
    page_number: int,
    page_size: int,
    year_start: int,
    year_end: int,
    content_types: list[str],
    language: str,
    sort_type: str,
) -> dict[str, Any]:
    refinements = [f"ContentType:{value}" for value in content_types]
    refinements.append(f"Language:{language}")
    return {
        "method": "POST",
        "endpoint": IEEE_ENDPOINT,
        "headers": IEEE_HEADERS,
        "json_body": {
            "action": "search",
            "newsearch": True,
            "matchBoolean": True,
            "matchPubs": True,
            "queryText": query,
            "highlight": False,
            "returnType": "SEARCH",
            "rowsPerPage": page_size,
            "pageNumber": page_number,
            "sortType": sort_type,
            "ranges": [f"{year_start}_{year_end}_Year"],
            "refinements": refinements,
        },
    }


def scopus_auth_headers(key_env: str) -> dict[str, str]:
    api_key = os.environ.get(key_env, "")
    if not api_key:
        raise ReconciliationError(
            f"Scopus credential is absent from secure runtime environment variable {key_env!r}"
        )
    return {**SCOPUS_PUBLIC_HEADERS, "X-ELS-APIKey": api_key}


def scopus_authors(entry: dict[str, Any]) -> list[dict[str, str]]:
    source_authors = entry.get("author") or []
    if isinstance(source_authors, dict):
        source_authors = [source_authors]
    authors: list[dict[str, str]] = []
    if not isinstance(source_authors, list):
        return authors
    for raw_author in source_authors:
        if not isinstance(raw_author, dict):
            continue
        name = clean_text(
            " ".join(
                item
                for item in (raw_author.get("given-name"), raw_author.get("surname"))
                if clean_text(item)
            )
            or raw_author.get("authname")
            or raw_author.get("ce:indexed-name")
        )
        if name:
            authors.append({"name": name})
    return authors


def normalize_scopus(entry: dict[str, Any]) -> dict[str, Any]:
    identifier = clean_text(entry.get("eid"))
    return {
        "paperId": identifier,
        "doi": clean_text(entry.get("prism:doi")),
        "title": clean_text(entry.get("dc:title")),
        "authors": scopus_authors(entry),
        "year": year_from_text(entry.get("prism:coverDate")),
        "abstract": clean_text(entry.get("dc:description")),
        "citationCount": parse_nonnegative_int(entry.get("citedby-count", 0) or 0, "citedby-count"),
        "openAccess_pdf": {},
        "url": redacted_url(clean_text(entry.get("prism:url"))),
        "source": "Scopus",
    }


def parse_scopus_page(data: dict[str, Any], expected_start: int) -> ParsedPage:
    search = data.get("search-results")
    if not isinstance(search, dict):
        raise ReconciliationError("Scopus response lacked a search-results object")
    total = parse_nonnegative_int(search.get("opensearch:totalResults"), "opensearch:totalResults")
    start = parse_nonnegative_int(search.get("opensearch:startIndex"), "opensearch:startIndex")
    server_page_size = parse_nonnegative_int(search.get("opensearch:itemsPerPage"), "opensearch:itemsPerPage")
    if start != expected_start:
        raise ReconciliationError(
            f"Scopus returned startIndex {start}, expected requested offset {expected_start}"
        )
    entries = search.get("entry")
    if entries is None and total == 0:
        entries = []
    if not isinstance(entries, list):
        raise ReconciliationError("Scopus response entry field was not a list")
    identifiers = [clean_text(entry.get("eid")) for entry in entries if isinstance(entry, dict)]
    if len(identifiers) != len(entries) or any(not identifier for identifier in identifiers):
        raise ReconciliationError("Scopus page lacked a stable EID for one or more returned entries")
    if any(not isinstance(entry, dict) for entry in entries):
        raise ReconciliationError("Scopus page included a non-object entry")
    return ParsedPage(
        total=total,
        start=start,
        end_exclusive=start + len(entries),
        server_page_size=server_page_size,
        records=entries,
        identifiers=identifiers,
        normalized_records=[normalize_scopus(entry) for entry in entries],
        response_details={
            "reported_start_index": start,
            "reported_items_per_page": server_page_size,
        },
    )


def ieee_authors(record: dict[str, Any]) -> list[dict[str, str]]:
    source_authors = record.get("authors") or []
    authors: list[dict[str, str]] = []
    if not isinstance(source_authors, list):
        return authors
    for raw_author in source_authors:
        if isinstance(raw_author, str):
            name = clean_text(raw_author)
        elif isinstance(raw_author, dict):
            name = clean_text(
                raw_author.get("preferredName")
                or raw_author.get("normalizedName")
                or " ".join(
                    item
                    for item in (raw_author.get("firstName"), raw_author.get("lastName"))
                    if clean_text(item)
                )
            )
        else:
            name = ""
        if name:
            authors.append({"name": name})
    return authors


def ieee_document_url(record: dict[str, Any]) -> str:
    identifier = clean_text(record.get("articleNumber"))
    document_link = clean_text(record.get("documentLink"))
    if document_link.startswith("https://ieeexplore.ieee.org/"):
        return redacted_url(document_link)
    if document_link.startswith("/"):
        return redacted_url(f"https://ieeexplore.ieee.org{document_link}")
    return f"https://ieeexplore.ieee.org/document/{identifier}/" if identifier else ""


def normalize_ieee(record: dict[str, Any]) -> dict[str, Any]:
    citation_count = record.get("citationCount", 0) or 0
    return {
        "paperId": clean_text(record.get("articleNumber")),
        "doi": clean_text(record.get("doi")),
        "title": clean_text(record.get("articleTitle")),
        "authors": ieee_authors(record),
        "year": year_from_text(record.get("publicationYear")),
        "abstract": clean_text(record.get("abstract")),
        "citationCount": parse_nonnegative_int(citation_count, "citationCount"),
        "openAccess_pdf": {},
        "url": ieee_document_url(record),
        "source": "IEEE Xplore",
    }


def parse_ieee_page(data: dict[str, Any], expected_start: int, expected_page_size: int) -> ParsedPage:
    total = parse_nonnegative_int(data.get("totalRecords"), "totalRecords")
    start = parse_nonnegative_int(data.get("startRecord"), "startRecord")
    end = parse_nonnegative_int(data.get("endRecord"), "endRecord")
    server_page_size = parse_nonnegative_int(data.get("recordsPerPage"), "recordsPerPage")
    total_pages = parse_nonnegative_int(data.get("totalPages"), "totalPages")
    if start != expected_start:
        raise ReconciliationError(
            f"IEEE Xplore returned startRecord {start}, expected source position {expected_start}"
        )
    if server_page_size != expected_page_size:
        raise ReconciliationError(
            f"IEEE Xplore returned recordsPerPage {server_page_size}, expected {expected_page_size}"
        )
    expected_total_pages = math.ceil(total / expected_page_size) if total else 0
    # IEEE may report one empty result page for a valid zero-record snapshot.
    # Accept that documented convention while still requiring one fetched empty
    # page, two-pass agreement, and retrieved == source total.
    accepted_total_pages = {expected_total_pages}
    if total == 0:
        accepted_total_pages.add(1)
    if total_pages not in accepted_total_pages:
        raise ReconciliationError(
            f"IEEE Xplore returned totalPages {total_pages}, expected one of {sorted(accepted_total_pages)}"
        )
    records = data.get("records")
    if records is None and total == 0:
        records = []
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ReconciliationError("IEEE Xplore response records field was not a list of objects")
    identifiers = [clean_text(record.get("articleNumber")) for record in records]
    if any(not identifier for identifier in identifiers):
        raise ReconciliationError("IEEE Xplore page lacked articleNumber for one or more returned records")
    if end != start + len(records):
        raise ReconciliationError(
            f"IEEE Xplore returned endRecord {end}, expected {start + len(records)} from its record count"
        )
    return ParsedPage(
        total=total,
        start=start,
        end_exclusive=end,
        server_page_size=server_page_size,
        records=records,
        identifiers=identifiers,
        normalized_records=[normalize_ieee(record) for record in records],
        response_details={
            "reported_start_record": start,
            "reported_end_record": end,
            "reported_records_per_page": server_page_size,
            "reported_total_pages": total_pages,
        },
    )


def request_for_page(args: argparse.Namespace, source_position: int) -> tuple[dict[str, Any], dict[str, str], dict[str, str] | None, dict[str, Any] | None]:
    """Build public descriptor plus private in-memory authentication for one page."""
    if args.source == "scopus":
        descriptor = scopus_public_request(args.query, source_position, args.page_size, args.scopus_sort)
        return descriptor, scopus_auth_headers(args.scopus_api_key_env), descriptor["query_parameters"], None
    page_number = source_position + 1
    descriptor = ieee_public_request(
        args.query,
        page_number,
        args.page_size,
        args.ieee_year_start,
        args.ieee_year_end,
        args.ieee_content_types,
        args.ieee_language,
        args.ieee_sort_type,
    )
    return descriptor, dict(IEEE_HEADERS), None, descriptor["json_body"]


def parse_page_for_source(
    source: str,
    data: dict[str, Any],
    expected_start: int,
    page_size: int,
) -> ParsedPage:
    if source == "scopus":
        return parse_scopus_page(data, expected_start)
    return parse_ieee_page(data, expected_start, page_size)


def execute_pass(args: argparse.Namespace, pass_dir: Path, pass_number: int) -> dict[str, Any]:
    """Retrieve one complete source snapshot and write private raw/reconciliation artifacts."""
    if pass_dir.exists():
        raise ReconciliationError(f"private pass directory already exists: {pass_dir}")
    ensure_private_directory(pass_dir)
    page_reports: list[dict[str, Any]] = []
    ordered_ids: list[str] = []
    normalized_results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_page_sequences: set[str] = set()
    total: int | None = None
    expected_start = 0
    page_ordinal = 0

    while total is None or expected_start < total:
        page_ordinal += 1
        source_position = expected_start if args.source == "scopus" else page_ordinal - 1
        descriptor, request_headers, params, payload = request_for_page(args, source_position)
        data, retry_events = fetch_json(
            source=args.source,
            method=descriptor["method"],
            endpoint=descriptor["endpoint"],
            headers=request_headers,
            params=params,
            payload=payload,
            timeout_seconds=args.timeout,
            retries=args.retries,
            backoff_seconds=args.backoff_seconds,
        )
        page = parse_page_for_source(args.source, data, expected_start, args.page_size)
        if total is None:
            total = page.total
        elif page.total != total:
            raise TotalChangedError(
                f"{args.source} source total changed from {total} to {page.total} at source position {expected_start}"
            )

        expected_count = min(args.page_size, max(0, total - expected_start))
        # Scopus may echo the actual terminal count in itemsPerPage when the
        # complete result is shorter than the requested page. Accept only the
        # frozen size or the computed terminal count; a short nonterminal page
        # still fails the count/end checks below.
        if page.server_page_size not in {args.page_size, expected_count}:
            raise ReconciliationError(
                f"{args.source} page {page_ordinal} advertised page size {page.server_page_size}, "
                f"expected frozen {args.page_size} or terminal count {expected_count}"
            )
        if len(page.records) != expected_count:
            raise ReconciliationError(
                f"{args.source} page {page_ordinal} returned {len(page.records)} records, expected {expected_count}"
            )
        if page.end_exclusive != expected_start + expected_count:
            raise ReconciliationError(
                f"{args.source} page {page_ordinal} ended at {page.end_exclusive}, expected {expected_start + expected_count}"
            )

        page_sequence_sha = sha256_bytes("\n".join(page.identifiers).encode("utf-8"))
        if page_sequence_sha in seen_page_sequences:
            raise ReconciliationError(
                f"{args.source} page {page_ordinal} repeated a prior ordered page-ID sequence"
            )
        seen_page_sequences.add(page_sequence_sha)
        duplicate_ids = sorted(set(page.identifiers) & seen_ids)
        if duplicate_ids:
            raise ReconciliationError(
                f"{args.source} page {page_ordinal} duplicated source IDs from an earlier page"
            )
        if len(set(page.identifiers)) != len(page.identifiers):
            raise ReconciliationError(
                f"{args.source} page {page_ordinal} contained duplicate source IDs within the page"
            )

        cleaned_response = scrub_sensitive(data)
        raw_path = pass_dir / f"page-{page_ordinal:04d}.response.json"
        request_path = pass_dir / f"page-{page_ordinal:04d}.request.json"
        atomic_write_json(raw_path, cleaned_response)
        atomic_write_json(request_path, descriptor)
        response_sha = sha256_file(raw_path)
        request_sha = sha256_file(request_path)

        for index_within_page, (identifier, normalized) in enumerate(
            zip(page.identifiers, page.normalized_records), start=1
        ):
            global_rank = expected_start + index_within_page
            normalized["query"] = args.query
            normalized["rank"] = global_rank
            normalized_results.append(normalized)
            ordered_ids.append(identifier)
        seen_ids.update(page.identifiers)
        page_reports.append(
            {
                "page_ordinal": page_ordinal,
                "requested_source_position": source_position,
                "requested_native_pagination": {
                    "parameter": "start" if args.source == "scopus" else "pageNumber",
                    "value": source_position if args.source == "scopus" else page_ordinal,
                    "basis": "zero-based offset" if args.source == "scopus" else "one-based page number",
                },
                "expected_start": expected_start,
                "expected_records": expected_count,
                "returned_records": len(page.records),
                "observed": page.response_details,
                "global_rank_start": expected_start + 1 if expected_count else None,
                "global_rank_end": expected_start + expected_count if expected_count else None,
                "ordered_source_ids": page.identifiers,
                "page_id_sequence_sha256": page_sequence_sha,
                "response_path": raw_path.name,
                "response_sha256": response_sha,
                "request_path": request_path.name,
                "request_sha256": request_sha,
                "retry_events": retry_events,
            }
        )

        if total == 0:
            break
        expected_start += expected_count
        if expected_start < total and args.page_delay_seconds:
            time.sleep(args.page_delay_seconds)

    if total is None:  # Defensive: loop always receives a first page.
        raise ReconciliationError(f"{args.source} did not return a source total")
    expected_pages = math.ceil(total / args.page_size) if total else 1
    missing_pages = [
        ordinal
        for ordinal in range(1, expected_pages + 1)
        if ordinal not in {report["page_ordinal"] for report in page_reports}
    ]
    retrieved = len(normalized_results)
    reconciliation = {
        "classification": args.classification,
        "screening_prohibited": args.classification == "pilot_not_candidate_search",
        "source": "Scopus" if args.source == "scopus" else "IEEE Xplore",
        "query": args.query,
        "pass_number": pass_number,
        "completed_at_utc": utc_now(),
        "source_total": total,
        "page_size": args.page_size,
        "expected_pages": expected_pages,
        "pages_retrieved": len(page_reports),
        "missing_pages": missing_pages,
        "retrieved_records": retrieved,
        "unique_source_ids": len(seen_ids),
        "duplicate_source_ids": [],
        "retrieved_equals_source_total": retrieved == total,
        "ordered_source_ids": ordered_ids,
        "global_id_sequence_sha256": sha256_bytes("\n".join(ordered_ids).encode("utf-8")),
        "pages": page_reports,
    }
    if missing_pages:
        raise ReconciliationError(f"{args.source} missing expected page(s): {missing_pages}")
    if len(seen_ids) != retrieved:
        raise ReconciliationError(f"{args.source} ordered source-ID reconciliation found duplicates")
    if retrieved != total:
        raise ReconciliationError(
            f"{args.source} retrieved {retrieved} records but source total was {total}; result is invalid"
        )

    atomic_write_json(pass_dir / "reconciliation.json", reconciliation)
    normalized_output = {
        "source": reconciliation["source"],
        "query": args.query,
        "total": total,
        "results_retrieved": retrieved,
        "results": normalized_results,
        "output_metadata": {
            "classification": args.classification,
            "screening_prohibited": args.classification == "pilot_not_candidate_search",
            "source": reconciliation["source"],
            "source_endpoint": SCOPUS_ENDPOINT if args.source == "scopus" else IEEE_ENDPOINT,
            "pagination_reconciliation": "reconciliation.json",
            "global_id_sequence_sha256": reconciliation["global_id_sequence_sha256"],
            "retrieved_equals_source_total": True,
        },
    }
    atomic_write_json(pass_dir / "normalized-results.json", normalized_output)
    return reconciliation


def runtime_metadata() -> dict[str, Any]:
    try:
        uv_version = subprocess.run(
            ["uv", "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        uv_version = "unavailable"
    return {
        "driver_path": str(Path(__file__).resolve()),
        "driver_sha256": sha256_file(Path(__file__).resolve()),
        "uv_version": uv_version,
        "python_version": sys.version,
        "requests_version": requests.__version__,
    }


def manifest_for(directory: Path) -> dict[str, Any]:
    files = sorted(path for path in directory.rglob("*") if path.is_file() and path.name != "manifest.json")
    return {
        "generated_at_utc": utc_now(),
        "files": [
            {
                "path": str(path.relative_to(directory)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ],
    }


def summary_without_ids(reconciliation: dict[str, Any]) -> dict[str, Any]:
    pages = []
    for page in reconciliation["pages"]:
        pages.append({key: value for key, value in page.items() if key != "ordered_source_ids"})
    return {
        key: value
        for key, value in reconciliation.items()
        if key not in {"ordered_source_ids", "pages"}
    } | {"pages": pages}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve and reconcile all pages from Scopus or IEEE Xplore without serializing secrets."
    )
    parser.add_argument("--source", choices=("scopus", "ieee"), required=True)
    parser.add_argument("--query", required=True, help="Exact source-native query string")
    parser.add_argument("--output-dir", required=True, help="Explicit private output directory")
    parser.add_argument("--page-size", type=int, default=25, help="Validated fixed page size for this protocol (must be 25)")
    parser.add_argument("--passes", type=int, default=2, help="Complete ordered retrieval passes (default: 2)")
    parser.add_argument(
        "--classification",
        choices=("pilot_not_candidate_search", "final_run"),
        default="pilot_not_candidate_search",
        help="Output classification; pilots are never candidates (default: pilot_not_candidate_search)",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument("--backoff-seconds", type=float, default=DEFAULT_BACKOFF_SECONDS)
    parser.add_argument("--page-delay-seconds", type=float, default=DEFAULT_PAGE_DELAY_SECONDS)
    parser.add_argument(
        "--total-change-reruns",
        type=int,
        default=1,
        help="Fresh complete snapshot attempts permitted after an in-pass total change (default: 1)",
    )
    parser.add_argument("--scopus-api-key-env", default="SCOPUS_API_KEY")
    parser.add_argument("--scopus-sort", default="eid")
    parser.add_argument("--ieee-year-start", type=int, default=2011)
    parser.add_argument("--ieee-year-end", type=int, default=2026)
    parser.add_argument(
        "--ieee-content-types",
        nargs="+",
        default=["Journals", "Conferences", "Books"],
        help="IEEE ContentType facet values (pilot default: Journals Conferences Books)",
    )
    parser.add_argument(
        "--ieee-no-content-type-filter",
        action="store_true",
        help="Omit every ContentType facet; use when the prospectively frozen final strategy has no type filter",
    )
    parser.add_argument("--ieee-language", default="English")
    parser.add_argument("--ieee-sort-type", default="newest")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if not args.query.strip():
        raise ReconciliationError("--query must not be empty")
    if args.page_size != 25:
        raise ReconciliationError("--page-size must be 25: this is the empirically validated request shape")
    if args.passes < 2:
        raise ReconciliationError("--passes must be at least 2 to validate reproducible ordering")
    if args.timeout <= 0:
        raise ReconciliationError("--timeout must be positive")
    if args.retries < 0 or args.total_change_reruns < 0:
        raise ReconciliationError("retry counts cannot be negative")
    if args.backoff_seconds < 0 or args.page_delay_seconds < 0:
        raise ReconciliationError("backoff and page delay cannot be negative")
    if args.ieee_year_start > args.ieee_year_end:
        raise ReconciliationError("IEEE start year cannot be later than end year")
    if args.source == "scopus" and clean_text(args.scopus_sort).casefold() != "eid":
        raise ReconciliationError("--scopus-sort must be the empirically validated explicit value 'eid'")
    if args.source == "ieee" and clean_text(args.ieee_sort_type).casefold() != "newest":
        raise ReconciliationError("--ieee-sort-type must be the empirically validated explicit value 'newest'")
    if args.source == "ieee" and not clean_text(args.ieee_language):
        raise ReconciliationError("--ieee-language must not be empty")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.ieee_no_content_type_filter:
        args.ieee_content_types = []
    try:
        validate_args(args)
        output_dir = Path(args.output_dir).expanduser().resolve()
        if output_dir.exists() and any(output_dir.iterdir()):
            raise ReconciliationError(
                f"output directory already contains artifacts: {output_dir}; choose a clean directory"
            )
        ensure_private_directory(output_dir)
        metadata = {
            "status": "running",
            "classification": args.classification,
            "screening_prohibited": args.classification == "pilot_not_candidate_search",
            "credential_policy": "No credential, cookie, token, or response userInfo field is serialized.",
            "started_at_utc": utc_now(),
            "source": args.source,
            "query": args.query,
            "configuration": {
                "page_size": args.page_size,
                "passes": args.passes,
                "timeout_seconds": args.timeout,
                "retries": args.retries,
                "backoff_seconds": args.backoff_seconds,
                "page_delay_seconds": args.page_delay_seconds,
                "total_change_reruns": args.total_change_reruns,
                "scopus_sort": args.scopus_sort if args.source == "scopus" else None,
                "ieee_sort_type": args.ieee_sort_type if args.source == "ieee" else None,
                "ieee_year_start": args.ieee_year_start if args.source == "ieee" else None,
                "ieee_year_end": args.ieee_year_end if args.source == "ieee" else None,
                "ieee_content_types": args.ieee_content_types if args.source == "ieee" else None,
                "ieee_no_content_type_filter": args.ieee_no_content_type_filter if args.source == "ieee" else None,
                "ieee_language": args.ieee_language if args.source == "ieee" else None,
            },
            "runtime": runtime_metadata(),
        }
        atomic_write_json(output_dir / "run-metadata.json", metadata)

        reconciliations: list[dict[str, Any]] | None = None
        invalidated_total_change_attempts: list[int] = []
        successful_snapshot_attempt: int | None = None
        for attempt in range(1, args.total_change_reruns + 2):
            attempt_dir = output_dir / f"snapshot-attempt-{attempt:02d}"
            if attempt_dir.exists():
                raise ReconciliationError(f"private snapshot-attempt directory already exists: {attempt_dir}")
            ensure_private_directory(attempt_dir)
            try:
                trial = [
                    execute_pass(args, attempt_dir / f"pass-{pass_number:02d}", pass_number)
                    for pass_number in range(1, args.passes + 1)
                ]
                baseline = trial[0]
                for candidate in trial[1:]:
                    if candidate["source_total"] != baseline["source_total"]:
                        raise TotalChangedError(
                            f"{args.source} total changed between complete passes "
                            f"({baseline['source_total']} to {candidate['source_total']})"
                        )
                    if candidate["ordered_source_ids"] != baseline["ordered_source_ids"]:
                        raise OrderingChangedError(
                            f"{args.source} ordered source-ID sequence changed between complete passes"
                        )
                reconciliations = trial
                successful_snapshot_attempt = attempt
                break
            except TotalChangedError as error:
                invalidated_total_change_attempts.append(attempt)
                atomic_write_json(
                    attempt_dir / "snapshot-invalidated.json",
                    {
                        "status": "invalidated_total_changed",
                        "classification": args.classification,
                        "error_type": type(error).__name__,
                        "reason": str(error),
                        "at_utc": utc_now(),
                        "next_action": "Restart a complete snapshot from page one; do not merge this attempt.",
                    },
                )
                if attempt > args.total_change_reruns:
                    raise
            except ReconciliationError:
                raise

        if reconciliations is None:
            raise ReconciliationError("no complete stable snapshot was obtained")
        concise_passes = [summary_without_ids(item) for item in reconciliations]
        execution_summary = {
            "status": "success",
            "classification": args.classification,
            "screening_prohibited": args.classification == "pilot_not_candidate_search",
            "completed_at_utc": utc_now(),
            "source": reconciliations[0]["source"],
            "query": args.query,
            "source_total": reconciliations[0]["source_total"],
            "successful_snapshot_attempt": successful_snapshot_attempt,
            "invalidated_total_change_attempts": invalidated_total_change_attempts,
            "retrieved_records_per_pass": [item["retrieved_records"] for item in reconciliations],
            "retrieved_equals_source_total_all_passes": all(
                item["retrieved_equals_source_total"] for item in reconciliations
            ),
            "ordered_passes_identical": True,
            "global_id_sequence_sha256": reconciliations[0]["global_id_sequence_sha256"],
            "passes": concise_passes,
        }
        atomic_write_json(output_dir / "execution-summary.json", execution_summary)
        metadata["status"] = "success"
        metadata["completed_at_utc"] = utc_now()
        metadata["source_total"] = execution_summary["source_total"]
        metadata["successful_snapshot_attempt"] = successful_snapshot_attempt
        metadata["invalidated_total_change_attempts"] = invalidated_total_change_attempts
        metadata["retrieved_equals_source_total_all_passes"] = True
        atomic_write_json(output_dir / "run-metadata.json", metadata)
        atomic_write_json(output_dir / "manifest.json", manifest_for(output_dir))
        print(
            json.dumps(
                {
                    "status": "success",
                    "classification": args.classification,
                    "source": execution_summary["source"],
                    "source_total": execution_summary["source_total"],
                    "retrieved_records_per_pass": execution_summary["retrieved_records_per_pass"],
                    "ordered_passes_identical": True,
                    "output_dir": str(output_dir),
                },
                ensure_ascii=False,
            )
        )
        return 0
    except ReconciliationError as error:
        failure_dir = Path(args.output_dir).expanduser().resolve()
        ensure_private_directory(failure_dir)
        failure = {
            "status": "failure",
            "classification": args.classification,
            "screening_prohibited": args.classification == "pilot_not_candidate_search",
            "source": args.source,
            "error_type": type(error).__name__,
            "reason": str(error),
            "at_utc": utc_now(),
            "rule": "Do not merge or screen a failed/partial snapshot.",
        }
        atomic_write_json(failure_dir / "failure.json", failure)
        metadata_path = failure_dir / "run-metadata.json"
        if metadata_path.is_file():
            try:
                prior_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                prior_metadata = {}
            if isinstance(prior_metadata, dict):
                prior_metadata.update(
                    {
                        "status": "failure",
                        "completed_at_utc": failure["at_utc"],
                        "failure": {
                            "error_type": failure["error_type"],
                            "reason": failure["reason"],
                            "rule": failure["rule"],
                        },
                    }
                )
                atomic_write_json(metadata_path, prior_metadata)
        print(
            json.dumps(
                {
                    "status": "failure",
                    "source": args.source,
                    "error_type": type(error).__name__,
                    "reason": str(error),
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
