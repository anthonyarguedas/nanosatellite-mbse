#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["certifi"]
# ///

"""Run the bounded arXiv Atom API Pilot 003 route.

This is a pilot-only runner.  It renders the normative concepts from
``pilot_schedule`` without changing membership, validates the Atom transport,
and writes non-mergeable diagnostic artifacts.  It deliberately keeps the
rendered Advanced Search route separate: Atom syntax is used only here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import certifi

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from pilot_schedule.queries import CONCEPTS, MAIN_FACTORS  # noqa: E402


ATOM_ENDPOINT = "https://export.arxiv.org/api/query"
API_MANUAL_URL = "https://info.arxiv.org/help/api/user-manual.html"
DATE_FROM = "2011-01-01"
DATE_TO = "2026-08-29"
DATE_CLAUSE = "submittedDate:[201101010000 TO 202608292359]"
SORT_BY = "submittedDate"
SORT_ORDER = "ascending"
MAX_RESULTS_PER_CALL = 2000
BT2_PAIR_CHUNK_SIZE = 38
PILOT_SCHEMA = "arxiv-atom-pilot003-event/v1"
UNION_SCHEMA = "arxiv-atom-pilot003-unions/v1"
VALIDATION_SCHEMA = "arxiv-atom-pilot003-transport-validation/v1"
USER_AGENT = "nanosatellite-mbse-pilot/003 (public Atom API validation)"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

ATOM_NS = "http://www.w3.org/2005/Atom"
OPENSEARCH_NS = "http://a9.com/-/spec/opensearch/1.1/"
ARXIV_NS = "http://arxiv.org/schemas/atom"
NS = {"atom": ATOM_NS, "opensearch": OPENSEARCH_NS, "arxiv": ARXIV_NS}
TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
ATOM_VALUE_RE = re.compile(r'all:(?:"([^"]+)"|([A-Za-z0-9-]+))')
DATE_RANGE_RE = re.compile(r"submittedDate:\[([^\]]+)\]")
VERSION_RE = re.compile(r"^(?P<bare>.+?)(?P<version>v\d+)$", re.IGNORECASE)


class PilotError(RuntimeError):
    """A route/capture failure that must never be represented as zero hits."""


@dataclass(frozen=True)
class TransportFailure(PilotError):
    status: int | None
    reason: str
    body_sha256: str | None = None
    body_preview: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "body_sha256": self.body_sha256,
            "body_preview": self.body_preview,
        }


class RateLimitedAtomClient:
    """Small, standard-library-only Atom client with an auditable request pace."""

    def __init__(self, *, pause_seconds: float, timeout_seconds: float) -> None:
        self.pause_seconds = pause_seconds
        self.timeout_seconds = timeout_seconds
        self._last_request_started: float | None = None

    def _wait(self) -> None:
        if self._last_request_started is None:
            return
        remaining = self.pause_seconds - (time.monotonic() - self._last_request_started)
        if remaining > 0:
            time.sleep(remaining)

    def request(self, params: Mapping[str, Any], *, retries: int = 1) -> dict[str, Any]:
        encoded = urllib.parse.urlencode(params)
        url = f"{ATOM_ENDPOINT}?{encoded}"
        attempts: list[dict[str, Any]] = []
        for attempt in range(retries + 1):
            self._wait()
            self._last_request_started = time.monotonic()
            started = utc_now()
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds, context=SSL_CONTEXT) as response:
                    raw = response.read()
                    status = getattr(response, "status", 200)
                    if status != 200:
                        raise TransportFailure(status, f"unexpected HTTP status {status}")
                    return {
                        "url_length": len(url),
                        "params": dict(params),
                        "started_at_utc": started,
                        "completed_at_utc": utc_now(),
                        "status": status,
                        "headers": {
                            key.lower(): value
                            for key, value in response.headers.items()
                            if key.lower() in {"content-type", "date", "content-length"}
                        },
                        "response_sha256": hashlib.sha256(raw).hexdigest(),
                        "raw": raw,
                        "attempt_failures": attempts,
                    }
            except urllib.error.HTTPError as error:
                raw = error.read()
                failure = TransportFailure(
                    error.code,
                    f"HTTP {error.code}",
                    hashlib.sha256(raw).hexdigest(),
                    raw.decode("utf-8", errors="replace")[:500],
                )
            except urllib.error.URLError as error:
                failure = TransportFailure(None, f"URL error: {error.reason}")
            except TimeoutError:
                failure = TransportFailure(None, "request timed out")
            attempts.append({"attempt": attempt + 1, **failure.as_dict()})
            # A URI-too-long response is deterministic for this request; retain it
            # as a null failure instead of hammering the endpoint.
            if failure.status == 414 or attempt == retries:
                raise TransportFailure(
                    failure.status,
                    failure.reason,
                    failure.body_sha256,
                    failure.body_preview,
                )
        raise AssertionError("unreachable")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.split())


def literal_atom(value: str) -> str:
    """Render one protocol literal as a documented Atom all-field atom."""
    if '"' in value:
        raise ValueError(f"Unexpected quote in protocol literal: {value!r}")
    return f'all:"{value}"' if any(character.isspace() for character in value) else f"all:{value}"


def pair_atom(left: str, right: str) -> str:
    """Broader Atom fallback for an unavailable same-field distance predicate."""
    return f"({literal_atom(left)} AND {literal_atom(right)})"


def alternatives(concept_names: Iterable[str]) -> tuple[str, ...]:
    rendered: list[str] = []
    for name in concept_names:
        concept = CONCEPTS[name]
        rendered.extend(literal_atom(value) for value in concept.literals)
        rendered.extend(pair_atom(left, right) for left, right in concept.pairs)
    return tuple(rendered)


def factor_expression(
    concept_names: Sequence[str], *, pair_override: Sequence[tuple[str, str]] | None = None
) -> str:
    if pair_override is not None:
        if tuple(concept_names) != ("T2",):
            raise ValueError("Only the T2 factor may have a pair override")
        values = tuple(pair_atom(left, right) for left, right in pair_override)
    else:
        values = alternatives(concept_names)
    if not values:
        raise ValueError("A factor must have at least one source-native alternative")
    return f"({' OR '.join(values)})"


def partition_query(
    partition_id: str,
    *,
    factor_overrides: Mapping[int, Sequence[str]] | None = None,
) -> str:
    """Render one complete Atom Boolean expression, optionally replacing OR factors.

    An override replaces only the alternatives in one parenthesized factor.  A
    union over its disjoint replacement cells is therefore exactly equivalent
    to the original factor union.
    """
    overrides = factor_overrides or {}
    pieces = []
    for index, factor in enumerate(MAIN_FACTORS[partition_id]):
        values = tuple(overrides[index]) if index in overrides else alternatives(factor)
        if not values:
            raise ValueError("A source-native OR factor cannot be empty")
        pieces.append(f"({' OR '.join(values)})")
    pieces.append(DATE_CLAUSE)
    return " AND ".join(pieces)


def encoded_url_length(query: str, *, start: int = 0, max_results: int = MAX_RESULTS_PER_CALL) -> int:
    return len(
        f"{ATOM_ENDPOINT}?"
        + urllib.parse.urlencode(
            {
                "search_query": query,
                "start": start,
                "max_results": max_results,
                "sortBy": SORT_BY,
                "sortOrder": SORT_ORDER,
            }
        )
    )


def _cell(
    partition_id: str,
    cell_id: str,
    *,
    factor_overrides: Mapping[int, Sequence[str]] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    query = partition_query(partition_id, factor_overrides=factor_overrides)
    return {
        "cell_id": cell_id,
        "query": query,
        "source_native_alternative_counts": factor_counts(partition_id),
        "encoded_url_length": encoded_url_length(query),
        **(dict(extra) if extra else {}),
    }


def partition_cells(partition_id: str) -> tuple[dict[str, Any], ...]:
    """Return a practical, lossless Atom-cell union for one partition.

    The direct endpoint's observed request-line ceiling is below the full A2,
    BC1, and BT2 URI lengths.  Only one parenthesized OR factor is split at a
    time, so the cell union distributes AND over an unchanged, disjoint OR
    union and does not change a term, pair, or Boolean relation.
    """
    if partition_id == "A2":
        # The semantic M_H OR M_B factor is a disjoint two-cell union.
        cells = []
        for index, concept_names in enumerate((("M_H",), ("M_B",)), start=1):
            values = alternatives(concept_names)
            cells.append(
                _cell(
                    "A2",
                    f"M-{index:02d}-of-02",
                    factor_overrides={2: values},
                    extra={
                        "replaced_factor": "M_H OR M_B",
                        "factor_concepts": list(concept_names),
                        "factor_alternative_count": len(values),
                    },
                )
            )
        return tuple(cells)

    if partition_id == "BC1":
        values = alternatives(("C1",))
        chunks = tuple(values[index : index + 31] for index in range(0, len(values), 31))
        return tuple(
            _cell(
                "BC1",
                f"C1-{index:02d}-of-{len(chunks):02d}",
                factor_overrides={1: chunk},
                extra={
                    "replaced_factor": "C1",
                    "factor_alternative_indices": list(
                        range((index - 1) * 31 + 1, (index - 1) * 31 + len(chunk) + 1)
                    ),
                    "factor_alternative_count": len(chunk),
                },
            )
            for index, chunk in enumerate(chunks, start=1)
        )

    if partition_id == "BT2":
        pairs = CONCEPTS["T2"].pairs
        chunks = tuple(
            pairs[index : index + BT2_PAIR_CHUNK_SIZE]
            for index in range(0, len(pairs), BT2_PAIR_CHUNK_SIZE)
        )
        return tuple(
            _cell(
                "BT2",
                f"T2-{index:02d}-of-{len(chunks):02d}",
                factor_overrides={2: tuple(pair_atom(left, right) for left, right in chunk)},
                extra={
                    "replaced_factor": "T2",
                    "t2_pair_indices": list(
                        range(
                            (index - 1) * BT2_PAIR_CHUNK_SIZE + 1,
                            (index - 1) * BT2_PAIR_CHUNK_SIZE + len(chunk) + 1,
                        )
                    ),
                    "t2_pairs": [list(pair) for pair in chunk],
                    "factor_alternative_count": len(chunk),
                },
            )
            for index, chunk in enumerate(chunks, start=1)
        )

    return (_cell(partition_id, "cell-01-of-01"),)


def factor_counts(partition_id: str) -> dict[str, int]:
    return {
        " ∪ ".join(concept_names): sum(
            CONCEPTS[name].alternative_count for name in concept_names
        )
        for concept_names in MAIN_FACTORS[partition_id]
    }


def pairs_for_partition(partition_id: str) -> tuple[tuple[str, str], ...]:
    values: list[tuple[str, str]] = []
    for factor in MAIN_FACTORS[partition_id]:
        for name in factor:
            values.extend(CONCEPTS[name].pairs)
    return tuple(values)


def lexical_tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower())


def local_pair_matches(text: str, left: str, right: str) -> list[dict[str, int]]:
    """Find both-order pair occurrences with no more than five intervening tokens."""
    tokens = lexical_tokens(text)
    left_tokens = lexical_tokens(left)
    right_tokens = lexical_tokens(right)
    matches: list[dict[str, int]] = []
    if not left_tokens or not right_tokens:
        return matches
    left_starts = [
        index
        for index in range(len(tokens) - len(left_tokens) + 1)
        if tokens[index : index + len(left_tokens)] == left_tokens
    ]
    right_starts = [
        index
        for index in range(len(tokens) - len(right_tokens) + 1)
        if tokens[index : index + len(right_tokens)] == right_tokens
    ]
    for left_start in left_starts:
        left_end = left_start + len(left_tokens)
        for right_start in right_starts:
            right_end = right_start + len(right_tokens)
            if left_end <= right_start:
                gap = right_start - left_end
                order = "left_then_right"
            elif right_end <= left_start:
                gap = left_start - right_end
                order = "right_then_left"
            else:
                continue
            if gap <= 5:
                matches.append(
                    {
                        "left_start": left_start,
                        "right_start": right_start,
                        "intervening_lexical_tokens": gap,
                        "order": order,
                    }
                )
    return matches


def add_local_pair_evidence(record: dict[str, Any], pairs: Sequence[tuple[str, str]]) -> None:
    evidence: list[dict[str, Any]] = []
    for left, right in pairs:
        for field in ("title", "abstract"):
            text = record.get(field)
            if not isinstance(text, str):
                continue
            matches = local_pair_matches(text, left, right)
            if matches:
                evidence.append(
                    {
                        "left": left,
                        "right": right,
                        "field": field,
                        "matches": matches,
                    }
                )
    record["local_pair_evidence_title_abstract"] = evidence


def identifier_parts(atom_id: str) -> tuple[str, str | None, str]:
    path = urllib.parse.urlparse(atom_id).path
    marker = "/abs/"
    candidate = path.split(marker, 1)[1] if marker in path else path.lstrip("/")
    candidate = urllib.parse.unquote(candidate)
    match = VERSION_RE.match(candidate)
    if match:
        return match.group("bare"), match.group("version").lower(), candidate
    return candidate, None, candidate


def parse_record(entry: ET.Element, *, pairs: Sequence[tuple[str, str]]) -> dict[str, Any]:
    atom_id = clean_text(entry.findtext("atom:id", namespaces=NS))
    if not atom_id:
        raise PilotError("Atom entry has no id")
    bare, version, versioned = identifier_parts(atom_id)
    record = {
        "source_record_stable_id": bare,
        "source_record_version_id": versioned,
        "source_record_version": version,
        "atom_id": atom_id,
        "title": clean_text(entry.findtext("atom:title", namespaces=NS)),
        "abstract": clean_text(entry.findtext("atom:summary", namespaces=NS)),
        "published": clean_text(entry.findtext("atom:published", namespaces=NS)),
        "updated": clean_text(entry.findtext("atom:updated", namespaces=NS)),
        "authors": [
            clean_text(author.findtext("atom:name", namespaces=NS))
            for author in entry.findall("atom:author", NS)
            if clean_text(author.findtext("atom:name", namespaces=NS))
        ],
        "categories": [
            category.attrib["term"]
            for category in entry.findall("atom:category", NS)
            if category.attrib.get("term")
        ],
        "primary_category": (
            entry.find("arxiv:primary_category", NS).attrib.get("term")
            if entry.find("arxiv:primary_category", NS) is not None
            else None
        ),
        "doi": clean_text(entry.findtext("arxiv:doi", namespaces=NS)),
        "journal_ref": clean_text(entry.findtext("arxiv:journal_ref", namespaces=NS)),
    }
    add_local_pair_evidence(record, pairs)
    return record


def parse_feed(raw: bytes, *, pairs: Sequence[tuple[str, str]]) -> dict[str, Any]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        raise PilotError(f"Atom XML parse failure: {error}") from error
    total_text = root.findtext("opensearch:totalResults", namespaces=NS)
    start_text = root.findtext("opensearch:startIndex", namespaces=NS)
    per_page_text = root.findtext("opensearch:itemsPerPage", namespaces=NS)
    try:
        total = int(total_text) if total_text is not None else None
        start = int(start_text) if start_text is not None else None
        per_page = int(per_page_text) if per_page_text is not None else None
    except ValueError as error:
        raise PilotError(f"Atom OpenSearch numeric field is invalid: {error}") from error
    if total is None or start is None or per_page is None:
        raise PilotError("Atom feed omitted an OpenSearch total, start index, or page size")
    return {
        "source_query_echo": clean_text(root.findtext("atom:title", namespaces=NS)),
        "feed_updated": clean_text(root.findtext("atom:updated", namespaces=NS)),
        "source_reported_total": total,
        "source_start_index": start,
        "source_items_per_page": per_page,
        "records": [parse_record(entry, pairs=pairs) for entry in root.findall("atom:entry", NS)],
    }


def atom_values(expression: str) -> set[str]:
    return {quoted or bare for quoted, bare in ATOM_VALUE_RE.findall(expression)}


def validate_source_echo(
    query: str, source_echo: str | None, pairs: Sequence[tuple[str, str]]
) -> None:
    """Fail closed if the feed's source echo omitted a requested Atom atom/pair."""
    if not isinstance(source_echo, str):
        raise PilotError("Atom feed did not echo its source query")
    missing_atoms = atom_values(query) - atom_values(source_echo)
    if missing_atoms:
        raise PilotError(f"Atom source echo omitted term atoms: {sorted(missing_atoms)!r}")
    date_match = DATE_RANGE_RE.search(query)
    if date_match is None:
        raise PilotError("Atom query omitted submittedDate range")
    canonical_date = f'submittedDate:"{date_match.group(1)}"'
    if canonical_date not in source_echo:
        raise PilotError("Atom source echo omitted or changed the submittedDate range")
    for left, right in pairs:
        fallback = pair_atom(left, right)
        if fallback in query and fallback not in source_echo:
            raise PilotError(f"Atom source echo omitted pair fallback: {fallback}")


def record_date_in_window(record: Mapping[str, Any]) -> bool:
    published = record.get("published")
    if not isinstance(published, str) or len(published) < 10:
        return False
    return DATE_FROM <= published[:10] <= DATE_TO


def capture_once(
    client: RateLimitedAtomClient,
    query: str,
    *,
    page_size: int,
    pairs: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    """Exhaust one Atom query, validating each source page and its stable IDs."""
    records: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    expected_total: int | None = None
    offset = 0
    while True:
        response = client.request(
            {
                "search_query": query,
                "start": offset,
                "max_results": page_size,
                "sortBy": SORT_BY,
                "sortOrder": SORT_ORDER,
            }
        )
        feed = parse_feed(response["raw"], pairs=pairs)
        validate_source_echo(query, feed["source_query_echo"], pairs)
        total = feed["source_reported_total"]
        if expected_total is None:
            expected_total = total
        elif total != expected_total:
            raise PilotError(
                f"Atom total changed during one pass ({expected_total} then {total})"
            )
        if feed["source_start_index"] != offset:
            raise PilotError(
                f"Atom page start mismatch (requested {offset}, observed {feed['source_start_index']})"
            )
        page_records = feed["records"]
        if len(page_records) > page_size:
            raise PilotError("Atom returned more records than the requested page size")
        pages.append(
            {
                "requested_start": offset,
                "requested_max_results": page_size,
                "source_start_index": feed["source_start_index"],
                "source_items_per_page": feed["source_items_per_page"],
                "source_reported_total": total,
                "source_query_echo": feed["source_query_echo"],
                "feed_updated": feed["feed_updated"],
                "response_status": response["status"],
                "response_sha256": response["response_sha256"],
                "url_length": response["url_length"],
                "entry_count": len(page_records),
                "transient_attempt_failures": response["attempt_failures"],
            }
        )
        records.extend(page_records)
        if expected_total == 0:
            break
        if len(records) >= expected_total:
            break
        if not page_records:
            raise PilotError("Atom pagination ended before the source-reported total")
        offset += len(page_records)

    if expected_total is None or len(records) != expected_total:
        raise PilotError("Atom capture did not reconcile record count to source total")
    versioned_ids = [record["source_record_version_id"] for record in records]
    stable_ids = [record["source_record_stable_id"] for record in records]
    if len(versioned_ids) != len(set(versioned_ids)):
        raise PilotError("Atom capture returned a duplicate versioned arXiv identifier")
    if len(stable_ids) != len(set(stable_ids)):
        raise PilotError("Atom current-version capture returned a duplicate bare arXiv identifier")
    if not all(record_date_in_window(record) for record in records):
        raise PilotError("Atom date-filter result fell outside the requested calendar window")
    published = [record["published"] for record in records]
    if published != sorted(published):
        raise PilotError("Atom requested ascending submittedDate order was not observed in published timestamps")
    return {
        "source_reported_total": expected_total,
        "records": records,
        "versioned_ids_in_source_order": versioned_ids,
        "stable_ids_in_source_order": stable_ids,
        "pages": pages,
        "complete": True,
        "date_window_check": {
            "field_checked": "Atom <published> (v1 submission timestamp)",
            "all_records_within_requested_calendar_window": True,
        },
        "ordering_check": {
            "requested": {"sortBy": SORT_BY, "sortOrder": SORT_ORDER},
            "published_timestamps_nondecreasing": True,
        },
    }


def complete_capture(
    client: RateLimitedAtomClient,
    query: str,
    *,
    page_size: int,
    pairs: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    first = capture_once(client, query, page_size=page_size, pairs=pairs)
    second = capture_once(client, query, page_size=page_size, pairs=pairs)
    same_total = first["source_reported_total"] == second["source_reported_total"]
    same_versioned = first["versioned_ids_in_source_order"] == second["versioned_ids_in_source_order"]
    same_stable = first["stable_ids_in_source_order"] == second["stable_ids_in_source_order"]
    if not (same_total and same_versioned and same_stable):
        raise PilotError("Two exhaustive Atom passes did not have the same total and ordered IDs")
    return {
        "source_reported_total": first["source_reported_total"],
        "first_pass": first,
        "second_pass": {
            "source_reported_total": second["source_reported_total"],
            "versioned_ids_in_source_order": second["versioned_ids_in_source_order"],
            "stable_ids_in_source_order": second["stable_ids_in_source_order"],
            "pages": second["pages"],
            "complete": second["complete"],
            "date_window_check": second["date_window_check"],
            "ordering_check": second["ordering_check"],
        },
        "cross_pass_reconciliation": {
            "same_source_reported_total": same_total,
            "same_versioned_ids_in_source_order": same_versioned,
            "same_stable_ids_in_source_order": same_stable,
            "complete_stable_id_capture": True,
        },
    }


def probe(
    client: RateLimitedAtomClient,
    query: str,
    *,
    id_list: Sequence[str] = (),
    max_results: int = 20,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": SORT_BY,
        "sortOrder": SORT_ORDER,
    }
    if id_list:
        params["id_list"] = ",".join(id_list)
    response = client.request(params)
    feed = parse_feed(response["raw"], pairs=())
    return {
        "query": query,
        "id_list": list(id_list),
        "response_status": response["status"],
        "source_query_echo": feed["source_query_echo"],
        "source_reported_total": feed["source_reported_total"],
        "source_start_index": feed["source_start_index"],
        "source_items_per_page": feed["source_items_per_page"],
        "returned_stable_ids": [record["source_record_stable_id"] for record in feed["records"]],
        "returned_versioned_ids": [record["source_record_version_id"] for record in feed["records"]],
        "records": feed["records"],
        "response_sha256": response["response_sha256"],
        "url_length": response["url_length"],
        "transient_attempt_failures": response["attempt_failures"],
    }


def expect_membership(
    observation: Mapping[str, Any], *, present: Iterable[str], absent: Iterable[str]
) -> dict[str, Any]:
    returned = set(observation["returned_stable_ids"])
    present_values = list(present)
    absent_values = list(absent)
    missing = [value for value in present_values if value not in returned]
    unexpected = [value for value in absent_values if value in returned]
    return {
        "known_present": present_values,
        "known_absent": absent_values,
        "missing_known_present": missing,
        "unexpected_known_absent": unexpected,
        "passed": not missing and not unexpected,
    }


def fetch_manual() -> dict[str, Any]:
    request = urllib.request.Request(API_MANUAL_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
            raw = response.read()
            text = raw.decode("utf-8", errors="replace")
            required_fragments = {
                "all_field": "all:</code> searches in each of the fields simultaneously",
                "date_filter": "The API provides one date filter, <code>submittedDate</code>",
                "boolean_grouping": "parentheses for grouping the Boolean expressions",
                "phrase": "entire phrases by enclosing the phrase in double quotes",
                "ordering": "<code>sortBy</code> can be \"relevance\"",
                "pagination": "max_results=2000",
            }
            compact_text = re.sub(r"\s+", " ", text)
            found = {
                name: re.sub(r"\s+", " ", fragment) in compact_text
                for name, fragment in required_fragments.items()
            }
            return {
                "status": "passed" if all(found.values()) else "failed",
                "url": API_MANUAL_URL,
                "response_status": getattr(response, "status", 200),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "required_fragments_found": found,
            }
    except (urllib.error.URLError, TimeoutError) as error:
        return {
            "status": "failed",
            "url": API_MANUAL_URL,
            "failure": {"status": None, "reason": str(error)},
        }


def validation_payload(client: RateLimitedAtomClient, output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Perform independent, bounded checks before accepting the Atom route."""
    manual = fetch_manual()
    if manual["status"] != "passed":
        raise PilotError("Official Atom API manual validation failed")

    known_a = 'all:"Attention Is All You Need"'
    known_b = 'all:"GLU Variants Improve Transformer"'
    known_c = "all:GLU"
    known_ids = ("1706.03762", "2002.05202")

    field_all = probe(client, known_a, id_list=("1706.03762",))
    field_title = probe(client, 'ti:"Attention Is All You Need"', id_list=("1706.03762",))
    field_abstract = probe(client, 'abs:"dominant sequence transduction models"', id_list=("1706.03762",))
    field_checks = [
        expect_membership(field_all, present=("1706.03762",), absent=()),
        expect_membership(field_title, present=("1706.03762",), absent=()),
        expect_membership(field_abstract, present=("1706.03762",), absent=()),
    ]

    boolean_observations = {
        "and_before_or": probe(client, f"{known_a} OR {known_b} AND {known_c}", id_list=known_ids),
        "left_grouped": probe(client, f"({known_a} OR {known_b}) AND {known_c}", id_list=known_ids),
        "right_grouped": probe(client, f"{known_a} OR ({known_b} AND {known_c})", id_list=known_ids),
    }
    boolean_checks = {
        "and_before_or": expect_membership(
            boolean_observations["and_before_or"], present=known_ids, absent=()
        ),
        "left_grouped": expect_membership(
            boolean_observations["left_grouped"], present=("2002.05202",), absent=("1706.03762",)
        ),
        "right_grouped": expect_membership(
            boolean_observations["right_grouped"], present=known_ids, absent=()
        ),
    }

    phrase_positive = probe(client, 'ti:"Attention Is All You Need"', id_list=("1706.03762",))
    phrase_negative = probe(client, 'ti:"Need All Is Attention You"', id_list=("1706.03762",))
    phrase_checks = [
        expect_membership(phrase_positive, present=("1706.03762",), absent=()),
        expect_membership(phrase_negative, present=(), absent=("1706.03762",)),
    ]

    date_positive = probe(
        client,
        'all:"Attention Is All You Need" AND submittedDate:[201706120000 TO 201706122359]',
        id_list=("1706.03762",),
    )
    date_negative = probe(
        client,
        'all:"Attention Is All You Need" AND submittedDate:[201706130000 TO 201706132359]',
        id_list=("1706.03762",),
    )
    date_checks = [
        expect_membership(date_positive, present=("1706.03762",), absent=()),
        expect_membership(date_negative, present=(), absent=("1706.03762",)),
    ]

    pair_observation = probe(
        client,
        "all:reusable AND all:model AND submittedDate:[201101010000 TO 202608292359]",
        id_list=("1102.2933",),
    )
    pair_check = expect_membership(pair_observation, present=("1102.2933",), absent=())
    pair_record = next(
        (record for record in pair_observation["records"] if record["source_record_stable_id"] == "1102.2933"),
        None,
    )
    pair_local_matches = (
        local_pair_matches(pair_record["abstract"], "reusable", "model")
        if isinstance(pair_record, Mapping) and isinstance(pair_record.get("abstract"), str)
        else []
    )
    pair_check["local_title_or_abstract_evidence"] = {
        "declared_pair": ["reusable", "model"],
        "field": "abstract",
        "matches": pair_local_matches,
        "passed": bool(pair_local_matches),
    }

    pagination_query = "all:CubeSat AND submittedDate:[202401010000 TO 202412312359]"
    try:
        pagination_capture = complete_capture(client, pagination_query, page_size=25, pairs=())
        pagination_artifact = {
            "schema_version": PILOT_SCHEMA,
            "event_kind": "pilot_transport_validation",
            "merge_eligible": False,
            "do_not_merge": True,
            "route": "Atom API",
            "endpoint": ATOM_ENDPOINT,
            "query": pagination_query,
            "date_window": {"from": "2024-01-01", "to": "2024-12-31", "basis": "submittedDate"},
            "capture": pagination_capture,
            "outcome": "complete",
        }
    except PilotError as error:
        pagination_artifact = {
            "schema_version": PILOT_SCHEMA,
            "event_kind": "pilot_transport_validation",
            "merge_eligible": False,
            "do_not_merge": True,
            "route": "Atom API",
            "endpoint": ATOM_ENDPOINT,
            "query": pagination_query,
            "total": None,
            "outcome": "failed",
            "failure": {"reason": str(error)},
        }
        raise

    checks = {
        "documentation": manual,
        "transport_fields": {
            "status": "passed" if all(check["passed"] for check in field_checks) else "failed",
            "observations": {"all": field_all, "title": field_title, "abstract": field_abstract},
            "membership": field_checks,
        },
        "boolean_grouping": {
            "status": "passed" if all(check["passed"] for check in boolean_checks.values()) else "failed",
            "observations": boolean_observations,
            "membership": boolean_checks,
            "interpretation": "The direct Atom route observed AND-before-OR and respected explicit parentheses; this finding is not attributed to rendered Advanced Search rows.",
        },
        "phrases": {
            "status": "passed" if all(check["passed"] for check in phrase_checks) else "failed",
            "observations": {"positive": phrase_positive, "reordered_negative": phrase_negative},
            "membership": phrase_checks,
        },
        "dates": {
            "status": "passed" if all(check["passed"] for check in date_checks) else "failed",
            "observations": {"inside": date_positive, "outside": date_negative},
            "membership": date_checks,
            "interpretation": "1706.03762 was retrieved in its 2017 v1 interval although its Atom updated timestamp is later; the pilot therefore records submittedDate as an original-submission/v1 route observation.",
        },
        "ordering_and_complete_stable_id_capture": {
            "status": "passed",
            "artifact": "pagination-capture.json",
            "query": pagination_query,
            "interpretation": "Two complete 25-record-page traversals reconciled source total, ordered versioned IDs, bare stable IDs, and ascending published timestamps.",
        },
        "pair_fallback": {
            "status": "passed" if pair_check["passed"] and pair_check["local_title_or_abstract_evidence"]["passed"] else "failed",
            "observation": pair_observation,
            "membership": pair_check,
            "interpretation": "The Atom conjunction is a deliberately broader candidate fallback for an unavailable same-field ≤5-token predicate. The local abstract check confirms one declared T2 pair without excluding any API candidate.",
        },
    }
    if any(value["status"] != "passed" for value in checks.values()):
        raise PilotError("One or more Atom transport checks failed")
    validation = {
        "schema_version": VALIDATION_SCHEMA,
        "event_kind": "pilot_transport_validation",
        "merge_eligible": False,
        "do_not_merge": True,
        "observed_at_utc": utc_now(),
        "diagnostic_window": {"from": DATE_FROM, "to": DATE_TO},
        "route": {
            "transport": "arXiv Atom API",
            "endpoint": ATOM_ENDPOINT,
            "method": "GET",
            "query_field": "documented all: field atoms with ti:/abs: validation controls",
            "boolean_syntax": "Atom API AND, OR, parentheses; separate from rendered Advanced Search semantics",
            "date_clause": DATE_CLAUSE,
            "sort": {"sortBy": SORT_BY, "sortOrder": SORT_ORDER},
            "capture": "Atom XML parsed locally; start/max_results pagination; bare and versioned arXiv IDs retained",
        },
        "checks": checks,
    }
    return validation, pagination_artifact


def run_full_route_probe(
    client: RateLimitedAtomClient, partition_id: str
) -> dict[str, Any]:
    """Retain the rejected overlong full route as a null, non-mergeable event."""
    full_query = partition_query(partition_id)
    try:
        response = client.request(
            {
                "search_query": full_query,
                "start": 0,
                "max_results": 1,
                "sortBy": SORT_BY,
                "sortOrder": SORT_ORDER,
            },
            retries=0,
        )
        feed = parse_feed(response["raw"], pairs=pairs_for_partition(partition_id))
        return {
            "schema_version": PILOT_SCHEMA,
            "event_kind": "pilot_route_probe",
            "merge_eligible": False,
            "do_not_merge": True,
            "partition_id": partition_id,
            "route": "Atom API full expression",
            "query": full_query,
            "encoded_url_length": response["url_length"],
            "total": feed["source_reported_total"],
            "outcome": "unexpected_success",
            "source_query_echo": feed["source_query_echo"],
            "replacement": "No replacement needed; inspect route selection before final use.",
        }
    except TransportFailure as error:
        cells = partition_cells(partition_id)
        return {
            "schema_version": PILOT_SCHEMA,
            "event_kind": "pilot_route_probe",
            "merge_eligible": False,
            "do_not_merge": True,
            "partition_id": partition_id,
            "route": "Atom API full expression",
            "query": full_query,
            "encoded_url_length": encoded_url_length(full_query, max_results=1),
            "total": None,
            "outcome": "failed",
            "failure": error.as_dict(),
            "replacement": {
                "route": "lossless union of parenthesized-OR Atom cells",
                "cell_count": len(cells),
                "cell_ids": [cell["cell_id"] for cell in cells],
                "maximum_replacement_encoded_url_length": max(
                    cell["encoded_url_length"] for cell in cells
                ),
            },
        }


def partition_event(
    client: RateLimitedAtomClient, partition_id: str, *, page_size: int
) -> dict[str, Any]:
    cells = []
    pairs = pairs_for_partition(partition_id)
    for planned in partition_cells(partition_id):
        try:
            capture = complete_capture(
                client,
                planned["query"],
                page_size=page_size,
                pairs=pairs,
            )
            cells.append(
                {
                    **planned,
                    "status": "complete",
                    "total": capture["source_reported_total"],
                    "capture": capture,
                }
            )
        except (PilotError, TransportFailure) as error:
            failure = error.as_dict() if isinstance(error, TransportFailure) else {"reason": str(error)}
            cells.append({**planned, "status": "failed", "total": None, "failure": failure})
    all_complete = all(cell["status"] == "complete" for cell in cells)
    total = sum(cell["total"] for cell in cells) if all_complete else None
    return {
        "schema_version": PILOT_SCHEMA,
        "event_kind": "pilot",
        "pilot_number": "003",
        "merge_eligible": False,
        "do_not_merge": True,
        "source": "arXiv",
        "platform": "arXiv Atom API",
        "partition_id": partition_id,
        "diagnostic_window": {
            "from": DATE_FROM,
            "to": DATE_TO,
            "basis": "Atom submittedDate; observed v1/original-submission behavior",
            "precision": "minute GMT source syntax with inclusive requested calendar endpoints",
            "source_clause": DATE_CLAUSE,
        },
        "controls": {
            "language": {"state": "unavailable", "applied": None},
            "document_type": {"state": "unavailable", "applied": None},
            "subject_category": {"state": "not_applied", "value": "all arXiv classifications"},
            "cross_list": {"state": "not_applicable_to_Atom_all_field_route", "applied": None},
            "proximity": {
                "state": "unavailable",
                "pair_handling": "broader all:left AND all:right fallback; local title/abstract ≤5-token audit without candidate exclusion",
            },
            "controlled_vocabulary": {
                "state": "not_applied",
                "reason": "arXiv Category Taxonomy is not a content thesaurus supplement for this all-classifications route",
            },
            "wildcard": {"state": "not_used", "accepted": False},
            "sort": {"sortBy": SORT_BY, "sortOrder": SORT_ORDER},
            "export": {
                "state": "Atom XML capture",
                "api_side_export_control": "unavailable",
                "pagination": {"start": "offset", "max_results_per_call": MAX_RESULTS_PER_CALL},
            },
        },
        "route": {
            "transport": "Atom API",
            "endpoint": ATOM_ENDPOINT,
            "literal": "all:<single-token> or all:\"multiword phrase\"",
            "pair_fallback": "(all:left AND all:right)",
            "cell_union": "one complete Atom Boolean expression except BT2's disjoint T2-pair cells",
            "browser_transport_boundary": "No Atom API grammar is attributed to rendered Advanced Search rows.",
        },
        "outcome": "complete" if all_complete else "failed",
        "total": total,
        "cells": cells,
    }


def records_from_event(event: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    records: list[tuple[str, Mapping[str, Any]]] = []
    for cell in event.get("cells", []):
        if cell.get("status") != "complete":
            continue
        for record in cell["capture"]["first_pass"]["records"]:
            records.append((cell["cell_id"], record))
    return records


def build_unions(events: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    partitions: dict[str, Any] = {}
    for partition_id, event in events.items():
        if event.get("outcome") != "complete":
            partitions[partition_id] = {
                "outcome": "failed",
                "total": None,
                "stable_id_union": None,
                "reason": "At least one source cell failed; no zero or partial union is substituted.",
            }
            continue
        members: dict[str, dict[str, Any]] = {}
        raw_events = records_from_event(event)
        for cell_id, record in raw_events:
            stable = record["source_record_stable_id"]
            value = members.setdefault(
                stable,
                {
                    "source_record_stable_id": stable,
                    "source_record_version_ids": [],
                    "cell_ids": [],
                    "published": record["published"],
                    "title": record["title"],
                    "local_pair_evidence_title_abstract": record["local_pair_evidence_title_abstract"],
                },
            )
            if record["source_record_version_id"] not in value["source_record_version_ids"]:
                value["source_record_version_ids"].append(record["source_record_version_id"])
            if cell_id not in value["cell_ids"]:
                value["cell_ids"].append(cell_id)
        ordered = sorted(members.values(), key=lambda value: (value["published"], value["source_record_stable_id"]))
        partitions[partition_id] = {
            "outcome": "complete",
            "raw_source_discovery_events": len(raw_events),
            "cell_total_sum": sum(cell["total"] for cell in event["cells"]),
            "unique_stable_id_count": len(ordered),
            "duplicate_discovery_events": len(raw_events) - len(ordered),
            "stable_id_union": [value["source_record_stable_id"] for value in ordered],
            "records": ordered,
        }
    return {
        "schema_version": UNION_SCHEMA,
        "event_kind": "pilot_union_reconciliation",
        "merge_eligible": False,
        "do_not_merge": True,
        "source": "arXiv",
        "diagnostic_window": {"from": DATE_FROM, "to": DATE_TO},
        "deduplication_key": "bare arXiv identifier (source_record_stable_id); versioned IDs retained as manifestations",
        "partitions": partitions,
    }


def visible_literal_match(record: Mapping[str, Any], concept_names: Sequence[str]) -> bool:
    fields = " ".join(
        value for value in (record.get("title"), record.get("abstract")) if isinstance(value, str)
    )
    tokens = lexical_tokens(fields)
    for name in concept_names:
        for literal in CONCEPTS[name].literals:
            needle = lexical_tokens(literal)
            if any(tokens[index : index + len(needle)] == needle for index in range(len(tokens) - len(needle) + 1)):
                return True
    return False


def build_threshold_investigation(
    events: Mapping[str, Mapping[str, Any]], unions: Mapping[str, Any]
) -> dict[str, Any]:
    investigated: dict[str, Any] = {}
    for partition_id, union in unions["partitions"].items():
        if union.get("unique_stable_id_count", 0) <= 100:
            continue
        event = events[partition_id]
        record_map = {
            record["source_record_stable_id"]: record
            for _, record in records_from_event(event)
        }
        factors = MAIN_FACTORS[partition_id]
        visible_counts = []
        for union_record in union["records"]:
            record = record_map[union_record["source_record_stable_id"]]
            visible_counts.append(
                {
                    "source_record_stable_id": record["source_record_stable_id"],
                    "published": record["published"],
                    "title": record["title"],
                    "visible_title_or_abstract_factor_hits": [
                        visible_literal_match(record, factor) for factor in factors
                    ],
                    "local_pair_evidence_title_abstract": record["local_pair_evidence_title_abstract"],
                }
            )
        factor_hit_counts = [
            sum(1 for record in visible_counts if record["visible_title_or_abstract_factor_hits"][index])
            for index in range(len(factors))
        ]
        investigated[partition_id] = {
            "deduplicated_union_count": union["unique_stable_id_count"],
            "raw_source_discovery_events": union["raw_source_discovery_events"],
            "inspection": {
                "method": "All retained public Atom title and abstract fields were audited locally for visible literal evidence and declared-pair evidence. This is a diagnostic, not a source-match override.",
                "visible_factor_hit_counts": factor_hit_counts,
                "records": visible_counts,
            },
            "no_loss_precision_controls_adopted": [
                "exact normative Boolean partition expression",
                "2011-01-01 through 2026-08-29 submittedDate bound",
                "BT2 disjoint pair-cell union where needed",
            ],
            "controls_rejected_as_not_proven_lossless": [
                "language filter (unavailable)",
                "document-type filter (unavailable)",
                "proximity restriction (unavailable; would discard broader pair-fallback candidates)",
                "category restriction (would narrow all-classifications coverage)",
                "local title/abstract evidence as a filter (Atom all: can match other indexed metadata)",
                "wildcard compression (not accepted partition-specifically by stable-set evidence)",
            ],
            "decision": "No additional precision restriction was applied. The complete source-native union remains the pilot candidate set so no potentially eligible record is lost.",
        }
    return {
        "schema_version": "arxiv-atom-pilot003-threshold-investigation/v1",
        "event_kind": "pilot_threshold_investigation",
        "merge_eligible": False,
        "do_not_merge": True,
        "threshold": "strictly more than 100 deduplicated bare arXiv IDs in one partition union",
        "status": "investigated" if investigated else "not_triggered",
        "partitions": investigated,
    }


def write_json(path: Path, payload: Mapping[str, Any], *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite {path}; pass --overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def dry_run_payload() -> dict[str, Any]:
    full_bt2 = partition_query("BT2")
    return {
        "concept_counts": {
            name: {
                "literals": len(concept.literals),
                "pairs": len(concept.pairs),
                "alternatives": concept.alternative_count,
            }
            for name, concept in CONCEPTS.items()
            if name in {"P", "E_H", "E_F", "M_H", "M_B", "R", "G_model", "G_structure", "C1", "T2"}
        },
        "partitions": {
            partition_id: {
                "full_query_length": len(partition_query(partition_id)),
                "full_encoded_url_length": encoded_url_length(partition_query(partition_id)),
                "cells": [
                    {
                        "cell_id": cell["cell_id"],
                        "encoded_url_length": cell["encoded_url_length"],
                        "t2_pair_indices": cell.get("t2_pair_indices"),
                    }
                    for cell in partition_cells(partition_id)
                ],
            }
            for partition_id in MAIN_FACTORS
        },
        "bt2_full_encoded_url_length": encoded_url_length(full_bt2),
        "date_clause": DATE_CLAUSE,
    }


def validate_renderer() -> None:
    expected_counts = {
        "P": (26, 0),
        "E_H": (38, 0),
        "E_F": (37, 0),
        "M_H": (54, 0),
        "M_B": (31, 0),
        "R": (55, 0),
        "G_model": (14, 16),
        "G_structure": (8, 16),
        "C1": (26, 36),
        "T2": (0, 224),
    }
    observed = {name: (len(CONCEPTS[name].literals), len(CONCEPTS[name].pairs)) for name in expected_counts}
    if observed != expected_counts:
        raise PilotError(f"pilot_schedule concept membership mismatch: {observed}")
    if tuple(MAIN_FACTORS) != ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"):
        raise PilotError("pilot_schedule main partition order changed")
    for partition_id in MAIN_FACTORS:
        query = partition_query(partition_id)
        if "*" in query or "?" in query:
            raise PilotError(f"Unaccepted wildcard rendered in {partition_id}")
        for factor in MAIN_FACTORS[partition_id]:
            for name in factor:
                for value in CONCEPTS[name].literals:
                    if literal_atom(value) not in query:
                        raise PilotError(f"Missing {name} literal in {partition_id}: {value}")
                for pair in CONCEPTS[name].pairs:
                    if pair_atom(*pair) not in query:
                        raise PilotError(f"Missing {name} pair in {partition_id}: {pair}")
    bt2_cells = partition_cells("BT2")
    reconstructed = [
        tuple(pair)
        for cell in bt2_cells
        for pair in cell["t2_pairs"]
    ]
    if tuple(reconstructed) != CONCEPTS["T2"].pairs:
        raise PilotError("BT2 cell union did not preserve all T2 pairs in order")
    if len(bt2_cells) != 6 or [len(cell["t2_pairs"]) for cell in bt2_cells] != [38, 38, 38, 38, 38, 34]:
        raise PilotError("BT2 is not the expected six disjoint 38/34-pair source-native cells")
    if any(cell["encoded_url_length"] >= 3800 for cell in bt2_cells):
        raise PilotError("BT2 replacement URI does not stay below the 3,800-character safety budget")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("all", "dry-run"), default="all")
    parser.add_argument("--pause-seconds", type=float, default=3.1)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--page-size", type=int, default=MAX_RESULTS_PER_CALL)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    if args.pause_seconds < 0:
        parser.error("--pause-seconds must be non-negative")
    if not 1 <= args.page_size <= MAX_RESULTS_PER_CALL:
        parser.error(f"--page-size must be 1 through {MAX_RESULTS_PER_CALL}")

    validate_renderer()
    if args.mode == "dry-run":
        print(json.dumps(dry_run_payload(), ensure_ascii=False, indent=2))
        return 0

    output_dir = args.output_dir.resolve()
    client = RateLimitedAtomClient(
        pause_seconds=args.pause_seconds,
        timeout_seconds=args.timeout_seconds,
    )
    validation, pagination = validation_payload(client, output_dir)
    write_json(output_dir / "transport-validation.json", validation, overwrite=args.overwrite)
    write_json(output_dir / "pagination-capture.json", pagination, overwrite=args.overwrite)

    for partition_id in ("A2", "BC1", "BT2"):
        rejected_full_route = run_full_route_probe(client, partition_id)
        write_json(
            output_dir / f"{partition_id}-full.NON_MERGEABLE_FAILURE.json",
            rejected_full_route,
            overwrite=args.overwrite,
        )
        if rejected_full_route["outcome"] != "failed" or rejected_full_route.get("total") is not None:
            raise PilotError(
                f"The full {partition_id} route did not preserve its transport outcome as a null failure"
            )

    events: dict[str, dict[str, Any]] = {}
    for partition_id in MAIN_FACTORS:
        event = partition_event(client, partition_id, page_size=args.page_size)
        events[partition_id] = event
        write_json(output_dir / f"{partition_id}.json", event, overwrite=args.overwrite)
        if event["outcome"] != "complete":
            raise PilotError(f"{partition_id} did not complete; retained null failure artifact")

    unions = build_unions(events)
    write_json(output_dir / "partition-unions.json", unions, overwrite=args.overwrite)
    investigation = build_threshold_investigation(events, unions)
    write_json(output_dir / "threshold-investigation.json", investigation, overwrite=args.overwrite)
    print(
        json.dumps(
            {
                "status": "complete",
                "output_dir": str(output_dir),
                "partition_unions": {
                    partition_id: payload.get("unique_stable_id_count")
                    for partition_id, payload in unions["partitions"].items()
                },
                "threshold_investigation": investigation["status"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PilotError, FileExistsError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
