#!/usr/bin/env python3
"""Retrieve metadata for citation candidates still needing full text.

The collector uses public OpenAlex, Crossref, and NASA NTRS endpoints. It keeps
normalized API response ledgers separate from the compact enrichment ledger.
Scopus and Web of Science are deliberately outside this follow-up.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import math
import os
import re
import tempfile
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import quote, urlencode

import requests


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SLR1_DIR = REPOSITORY_ROOT / "SLR/SLR1"
DEFAULT_CANDIDATE_PATH = SLR1_DIR / "citation-candidates.json"
DEFAULT_SCOPE_PATH = (
    SLR1_DIR
    / "citation-chasing/backward/cycle-1/metadata/"
    "full-text-needed-metadata-follow-up/lookup-scope.json"
)
DEFAULT_PRIOR_FOLLOW_UP_PATH = (
    SLR1_DIR
    / "citation-chasing/backward/cycle-1/metadata/"
    "full-text-needed-metadata-follow-up/metadata-follow-up.json"
)
DEFAULT_OUTPUT_DIR = (
    SLR1_DIR
    / "citation-chasing/backward/cycle-1/metadata/"
    "non-scopus-wos-metadata-enrichment"
)
PLATFORMS = ("openalex", "crossref", "ntrs")
SOURCE_SCHEMA = "slr1-non-scopus-wos-normalized-api-ledger/v1"
ENRICHMENT_SCHEMA = "slr1-non-scopus-wos-metadata-enrichment/v1"
USER_AGENT = (
    "nanosatellite-mbse-metadata-follow-up/1.0 "
    "(systematic-review metadata reconciliation)"
)
OPENALEX_SELECT = ",".join(
    (
        "id",
        "doi",
        "title",
        "display_name",
        "publication_year",
        "publication_date",
        "type",
        "language",
        "authorships",
        "primary_location",
        "locations",
        "abstract_inverted_index",
        "keywords",
        "ids",
    )
)
REQUEST_TIMEOUT = 45
MAX_RESULTS = 10
MAX_ABSTRACT_LENGTH = 200_000
MAX_TEXT_LENGTH = 20_000


class TextExtractor(HTMLParser):
    """Extract readable text from Crossref JATS or HTML fragments."""

    BLOCK_TAGS = frozenset(
        {
            "p",
            "title",
            "sec",
            "br",
            "li",
            "div",
            "abstract",
            "jats:p",
            "jats:title",
            "jats:sec",
        }
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(value: Any, *, maximum: int = MAX_TEXT_LENGTH) -> str | None:
    if not isinstance(value, str):
        return None
    value = html.unescape(value)
    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        return None
    return value[:maximum]


def clean_markup(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parser = TextExtractor()
    try:
        parser.feed(value)
        parser.close()
        text = " ".join(parser.parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", value)
    text = clean_text(text, maximum=MAX_ABSTRACT_LENGTH)
    if text and re.match(r"^abstract\s+", text, flags=re.IGNORECASE):
        text = re.sub(r"^abstract\s+", "", text, count=1, flags=re.IGNORECASE)
    return text


def normalized_doi(value: Any) -> str | None:
    value = clean_text(value)
    if not value:
        return None
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I)
    value = value.rstrip(".,; ").lower()
    return value if value.startswith("10.") and "/" in value else None


def canonical_title(value: Any) -> str:
    value = clean_text(value) or ""
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = value.replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def title_tokens(value: Any) -> list[str]:
    return canonical_title(value).split()


def title_scores(candidate_title: Any, result_title: Any) -> dict[str, Any]:
    candidate = canonical_title(candidate_title)
    result = canonical_title(result_title)
    candidate_tokens = candidate.split()
    result_tokens = result.split()
    candidate_set = set(candidate_tokens)
    result_set = set(result_tokens)
    intersection = candidate_set & result_set
    union = candidate_set | result_set
    return {
        "sequence": round(SequenceMatcher(None, candidate, result).ratio(), 6)
        if candidate and result
        else 0.0,
        "token_jaccard": round(len(intersection) / len(union), 6) if union else 0.0,
        "token_containment": round(
            len(intersection) / min(len(candidate_set), len(result_set)), 6
        )
        if candidate_set and result_set
        else 0.0,
        "candidate_token_count": len(candidate_tokens),
        "result_token_count": len(result_tokens),
        "exact": bool(candidate and candidate == result),
    }


def author_terms(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    ignored = {
        "and",
        "authors",
        "author",
        "dr",
        "et",
        "al",
        "the",
        "university",
        "national",
        "space",
        "administration",
        "nasa",
        "inc",
        "ltd",
    }
    terms: set[str] = set()
    for item in values:
        if isinstance(item, Mapping):
            item = item.get("name")
        text = canonical_title(item)
        terms.update(
            token
            for token in text.split()
            if len(token) >= 3 and token not in ignored and not token.isdigit()
        )
    return terms


def author_overlap(candidate_authors: Any, result_authors: Any) -> dict[str, Any]:
    candidate = author_terms(candidate_authors)
    result = author_terms(result_authors)
    shared = sorted(candidate & result)
    return {
        "shared_terms": shared,
        "shared_term_count": len(shared),
        "candidate_term_count": len(candidate),
        "result_term_count": len(result),
    }


def first_date_parts(value: Any) -> list[int]:
    if not isinstance(value, Mapping):
        return []
    date_parts = value.get("date-parts")
    if not isinstance(date_parts, list) or not date_parts or not isinstance(date_parts[0], list):
        return []
    result: list[int] = []
    for part in date_parts[0][:3]:
        if isinstance(part, int) and not isinstance(part, bool):
            result.append(part)
        else:
            break
    return result


def date_from_parts(parts: list[int]) -> str | None:
    if not parts:
        return None
    if len(parts) == 1:
        return f"{parts[0]:04d}"
    if len(parts) == 2:
        return f"{parts[0]:04d}-{parts[1]:02d}"
    return f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}"


def unique_texts(values: Iterable[Any], *, limit: int = 100) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = clean_text(value)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def openalex_abstract(index: Any) -> str | None:
    if not isinstance(index, Mapping):
        return None
    positioned: dict[int, str] = {}
    for word, positions in index.items():
        word = clean_text(word, maximum=1_000)
        if not word or not isinstance(positions, list):
            continue
        for position in positions:
            if (
                isinstance(position, int)
                and not isinstance(position, bool)
                and 0 <= position <= 100_000
                and position not in positioned
            ):
                positioned[position] = word
    if not positioned:
        return None
    maximum = max(positioned)
    if maximum + 1 != len(positioned):
        return None
    text = clean_text(
        " ".join(positioned[position] for position in range(maximum + 1)),
        maximum=MAX_ABSTRACT_LENGTH,
    )
    if text and re.match(r"^abstract\s+", text, flags=re.IGNORECASE):
        text = re.sub(r"^abstract\s+", "", text, count=1, flags=re.IGNORECASE)
    return text


def normalize_openalex_autocomplete(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, Mapping):
        return None
    title = clean_text(item.get("display_name"))
    source_id = clean_text(item.get("id"))
    if not title or not source_id or item.get("entity_type") != "work":
        return None
    hint = clean_text(item.get("hint")) or ""
    hint = re.sub(r",?\s+et\s+al\.?$", "", hint, flags=re.IGNORECASE)
    authors = unique_texts(part.strip() for part in hint.split(","))
    doi = normalized_doi(item.get("external_id"))
    return {
        "source_record_id": source_id,
        "title": title,
        "authors": authors,
        "publication_year": None,
        "publication_date": None,
        "publication_title": None,
        "document_type": "work",
        "doi": doi,
        "abstract": None,
        "keywords": [],
        "language": None,
        "stable_urls": unique_texts((source_id, item.get("external_id")), limit=20),
    }


def normalize_openalex(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, Mapping):
        return None
    title = clean_text(item.get("title") or item.get("display_name"))
    source_id = clean_text(item.get("id"))
    if not title or not source_id:
        return None
    authors: list[str] = []
    for authorship in item.get("authorships") or []:
        if not isinstance(authorship, Mapping):
            continue
        author = authorship.get("author")
        if isinstance(author, Mapping):
            name = clean_text(author.get("display_name"))
            if name:
                authors.append(name)
    location = item.get("primary_location")
    location = location if isinstance(location, Mapping) else {}
    source = location.get("source")
    source = source if isinstance(source, Mapping) else {}
    urls: list[Any] = [source_id, item.get("doi")]
    for candidate_location in [location, *(item.get("locations") or [])]:
        if isinstance(candidate_location, Mapping):
            urls.extend(
                (candidate_location.get("landing_page_url"), candidate_location.get("pdf_url"))
            )
    keywords = []
    for keyword in item.get("keywords") or []:
        if isinstance(keyword, Mapping):
            keywords.append(keyword.get("display_name"))
    year = item.get("publication_year")
    if isinstance(year, bool) or not isinstance(year, int):
        year = None
    return {
        "source_record_id": source_id,
        "title": title,
        "authors": unique_texts(authors),
        "publication_year": year,
        "publication_date": clean_text(item.get("publication_date")),
        "publication_title": clean_text(source.get("display_name")),
        "document_type": clean_text(item.get("type")),
        "doi": normalized_doi(item.get("doi")),
        "abstract": openalex_abstract(item.get("abstract_inverted_index")),
        "keywords": unique_texts(keywords),
        "language": clean_text(item.get("language")),
        "stable_urls": unique_texts(urls, limit=20),
    }


def normalize_crossref(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, Mapping):
        return None
    titles = item.get("title")
    title = clean_text(titles[0] if isinstance(titles, list) and titles else titles)
    doi = normalized_doi(item.get("DOI"))
    source_id = doi or clean_text(item.get("URL"))
    if not title or not source_id:
        return None
    authors: list[str] = []
    for author in item.get("author") or []:
        if not isinstance(author, Mapping):
            continue
        literal = clean_text(author.get("name"))
        if literal:
            authors.append(literal)
            continue
        authors.append(
            " ".join(
                part
                for part in (
                    clean_text(author.get("given")),
                    clean_text(author.get("family")),
                )
                if part
            )
        )
    parts: list[int] = []
    for date_field in ("published", "published-print", "published-online", "issued"):
        parts = first_date_parts(item.get(date_field))
        if parts:
            break
    containers = item.get("container-title")
    publication_title = clean_text(
        containers[0] if isinstance(containers, list) and containers else containers
    )
    urls: list[Any] = [item.get("URL")]
    for link in item.get("link") or []:
        if isinstance(link, Mapping):
            urls.append(link.get("URL"))
    return {
        "source_record_id": source_id,
        "title": title,
        "authors": unique_texts(authors),
        "publication_year": parts[0] if parts else None,
        "publication_date": date_from_parts(parts),
        "publication_title": publication_title,
        "document_type": clean_text(item.get("type")),
        "doi": doi,
        "abstract": clean_markup(item.get("abstract")),
        "keywords": unique_texts(item.get("subject") or []),
        "language": clean_text(item.get("language")),
        "stable_urls": unique_texts(urls, limit=20),
    }


def ntrs_publication(item: Mapping[str, Any]) -> Mapping[str, Any]:
    publications = item.get("publications")
    if not isinstance(publications, list):
        return {}
    for publication in publications:
        if isinstance(publication, Mapping) and publication.get("doi"):
            return publication
    for publication in publications:
        if isinstance(publication, Mapping):
            return publication
    return {}


def normalize_ntrs(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, Mapping):
        return None
    title = clean_text(item.get("title"))
    identifier = item.get("id")
    source_id = clean_text(str(identifier)) if identifier is not None else None
    if not title or not source_id:
        return None
    publication = ntrs_publication(item)
    authors: list[str] = []
    for affiliation in item.get("authorAffiliations") or []:
        if not isinstance(affiliation, Mapping):
            continue
        metadata = affiliation.get("meta")
        metadata = metadata if isinstance(metadata, Mapping) else {}
        author = metadata.get("author")
        author = author if isinstance(author, Mapping) else {}
        authors.append(author.get("name"))
    publication_date = clean_text(publication.get("publicationDate"))
    if not publication_date:
        publication_date = clean_text(item.get("distributionDate"))
    year = None
    if publication_date:
        match = re.match(r"^(\d{4})", publication_date)
        if match:
            year = int(match.group(1))
    doi = normalized_doi(publication.get("doi"))
    urls: list[Any] = [f"https://ntrs.nasa.gov/citations/{source_id}"]
    for download in item.get("downloads") or []:
        if isinstance(download, Mapping):
            location = download.get("links") or download.get("url") or download.get("href")
            if isinstance(location, Mapping):
                urls.extend(location.values())
            else:
                urls.append(location)
    return {
        "source_record_id": source_id,
        "title": title,
        "authors": unique_texts(authors),
        "publication_year": year,
        "publication_date": publication_date,
        "publication_title": clean_text(publication.get("publicationName")),
        "document_type": clean_text(item.get("stiType")),
        "doi": doi,
        "abstract": clean_text(item.get("abstract"), maximum=MAX_ABSTRACT_LENGTH),
        "keywords": unique_texts(item.get("subjectCategories") or []),
        "language": None,
        "stable_urls": unique_texts(urls, limit=20),
    }


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_name, 0o644)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def source_receipt(path: Path, source: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    status_counts = Counter(
        attempt.get("status") for attempt in payload.get("attempts", []) if isinstance(attempt, Mapping)
    )
    return {
        "source": source,
        "path": path.relative_to(REPOSITORY_ROOT).as_posix(),
        "sha256": sha256(path),
        "byte_count": path.stat().st_size,
        "candidate_coverage": len(payload.get("attempts", [])),
        "request_count": sum(
            len(attempt.get("queries", []))
            for attempt in payload.get("attempts", [])
            if isinstance(attempt, Mapping)
        ),
        "status_counts": dict(sorted(status_counts.items())),
    }


def selected_candidates(
    candidate_path: Path,
    scope_path: Path,
    prior_follow_up_path: Path,
) -> tuple[list[dict[str, Any]], str]:
    payload = load_json(candidate_path)
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("The candidate file has no records list")
    by_id = {
        record.get("candidate_id"): record
        for record in records
        if isinstance(record, Mapping) and isinstance(record.get("candidate_id"), str)
    }
    scope = load_json(scope_path)
    candidate_ids = scope.get("candidate_ids")
    if not isinstance(candidate_ids, list) or len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("The lookup scope has an invalid candidate ID ledger")
    selected: list[dict[str, Any]] = []
    for candidate_id in candidate_ids:
        record = by_id.get(candidate_id)
        if not isinstance(record, Mapping):
            raise ValueError(f"The scoped candidate is missing: {candidate_id}")
        if record.get("screening_decision") != "full_text_needed":
            raise ValueError(f"The scoped decision changed: {candidate_id}")
        if clean_text(record.get("title")) and clean_text(record.get("abstract")):
            raise ValueError(f"The scoped candidate no longer lacks title or abstract: {candidate_id}")
        selected.append(copy.deepcopy(dict(record)))
    selection = scope.get("selection")
    if not isinstance(selection, Mapping) or selection.get("candidate_count") != len(selected):
        raise ValueError("The lookup scope count changed")

    prior_follow_up = load_json(prior_follow_up_path)
    prior_records = prior_follow_up.get("records")
    if not isinstance(prior_records, list):
        raise ValueError("The prior follow-up artifact has no records list")
    aliases: dict[str, dict[str, Any]] = {}
    for item in prior_records:
        if not isinstance(item, Mapping):
            continue
        lookup = item.get("prior_portal_lookup")
        if not isinstance(lookup, Mapping) or lookup.get("status") != "matched_no_abstract":
            continue
        candidate_id = item.get("candidate_id")
        title = clean_text(lookup.get("matched_title"))
        if candidate_id not in by_id or not title:
            raise ValueError("A prior confirmed identity alias is outside the candidate scope")
        aliases[candidate_id] = {
            "title": title,
            "authors": unique_texts(lookup.get("matched_authors") or []),
            "publication_year": lookup.get("matched_publication_year")
            if isinstance(lookup.get("matched_publication_year"), int)
            and not isinstance(lookup.get("matched_publication_year"), bool)
            else None,
            "doi": normalized_doi(lookup.get("matched_doi")),
            "basis": "prior_portal_matched_no_abstract_identity",
        }
    for candidate in selected:
        alias = aliases.get(candidate["candidate_id"])
        if alias:
            candidate["_prior_confirmed_identity"] = alias
    return selected, sha256(candidate_path)


def response_headers(response: requests.Response) -> dict[str, str]:
    allowed = {
        "date",
        "content-type",
        "etag",
        "last-modified",
        "retry-after",
        "x-rate-limit-limit",
        "x-rate-limit-interval",
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-credits-used",
        "x-ratelimit-limit-usd",
    }
    return {
        key.lower(): clean_text(value, maximum=1_000) or ""
        for key, value in response.headers.items()
        if key.lower() in allowed
    }


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    payload: Mapping[str, Any] | None = None,
    retries: int = 3,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    errors: list[str] = []
    for attempt_number in range(1, retries + 2):
        started = utc_now()
        try:
            response = session.request(
                method,
                url,
                json=payload,
                timeout=REQUEST_TIMEOUT,
                headers={"Accept": "application/json"},
            )
            receipt = {
                "requested_at_utc": started,
                "completed_at_utc": utc_now(),
                "http_status": response.status_code,
                "response_headers": response_headers(response),
                "attempt_number": attempt_number,
            }
            if response.status_code == 404:
                receipt["outcome"] = "not_found"
                return None, receipt
            if response.status_code == 429 or 500 <= response.status_code <= 599:
                errors.append(f"HTTP {response.status_code}")
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else 2 ** (attempt_number - 1)
                except ValueError:
                    delay = 2 ** (attempt_number - 1)
                if response.status_code == 429 and delay > 300:
                    receipt["outcome"] = "rate_limited_for_daily_budget"
                    receipt["errors"] = errors
                    return None, receipt
                if attempt_number <= retries:
                    time.sleep(min(max(delay, 0.5), 60.0))
                    continue
            response.raise_for_status()
            decoded = response.json()
            if not isinstance(decoded, dict):
                raise ValueError("The response root is not an object")
            receipt["outcome"] = "success"
            return decoded, receipt
        except (requests.RequestException, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{type(error).__name__}: {str(error)[:500]}")
            if attempt_number <= retries:
                time.sleep(min(2 ** (attempt_number - 1), 30))
                continue
    return None, {
        "requested_at_utc": started,
        "completed_at_utc": utc_now(),
        "http_status": None,
        "response_headers": {},
        "attempt_number": retries + 1,
        "outcome": "error",
        "errors": errors,
    }


def lookup_identity(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    alias = candidate.get("_prior_confirmed_identity")
    return alias if isinstance(alias, Mapping) else candidate


def lookup_dois(candidate: Mapping[str, Any]) -> list[str]:
    identity = lookup_identity(candidate)
    return unique_texts(
        (
            normalized_doi(identity.get("doi")),
            normalized_doi(candidate.get("doi")),
        ),
        limit=2,
    )


def query_openalex(session: requests.Session, candidate: Mapping[str, Any]) -> dict[str, Any]:
    title = clean_text(lookup_identity(candidate).get("title"))
    url = "https://api.openalex.org/autocomplete/works?" + urlencode({"q": title})
    decoded, receipt = request_json(session, "GET", url)
    results: list[dict[str, Any]] = []
    source_total = None
    if decoded:
        metadata = decoded.get("meta")
        if isinstance(metadata, Mapping):
            count = metadata.get("count")
            if isinstance(count, int) and not isinstance(count, bool):
                source_total = count
        for item in decoded.get("results") or []:
            normalized = normalize_openalex_autocomplete(item)
            if normalized:
                results.append(normalized)
    queries = [
        {
            "mode": "title_autocomplete",
            "request": {"method": "GET", "url": url, "title": title},
            "receipt": receipt,
            "source_reported_total": source_total,
            "results": results,
        }
    ]
    return {
        "candidate_id": candidate["candidate_id"],
        "status": "success"
        if all(query["receipt"]["outcome"] in {"success", "not_found"} for query in queries)
        else "partial_or_error",
        "queries": queries,
    }


def crossref_bibliographic_query(candidate: Mapping[str, Any]) -> str:
    identity = lookup_identity(candidate)
    parts = [clean_text(identity.get("title"))]
    authors = identity.get("authors")
    if isinstance(authors, list):
        parts.extend(clean_text(author) for author in authors[:3])
    year = identity.get("publication_year")
    if isinstance(year, int) and not isinstance(year, bool):
        parts.append(str(year))
    return " ".join(part for part in parts if part)[:2_000]


def query_crossref(session: requests.Session, candidate: Mapping[str, Any]) -> dict[str, Any]:
    queries: list[dict[str, Any]] = []
    for doi in lookup_dois(candidate):
        url = "https://api.crossref.org/works/" + quote(doi, safe="")
        decoded, receipt = request_json(session, "GET", url)
        message = decoded.get("message") if isinstance(decoded, Mapping) else None
        normalized = normalize_crossref(message) if isinstance(message, Mapping) else None
        queries.append(
            {
                "mode": "doi",
                "request": {"method": "GET", "url": url, "doi": doi},
                "receipt": receipt,
                "source_reported_total": 1 if normalized else 0,
                "results": [normalized] if normalized else [],
            }
        )

    bibliographic = crossref_bibliographic_query(candidate)
    url = "https://api.crossref.org/works?" + urlencode(
        (("query.bibliographic", bibliographic), ("rows", str(MAX_RESULTS)))
    )
    decoded, receipt = request_json(session, "GET", url)
    results: list[dict[str, Any]] = []
    source_total = None
    message = decoded.get("message") if isinstance(decoded, Mapping) else None
    if isinstance(message, Mapping):
        count = message.get("total-results")
        if isinstance(count, int) and not isinstance(count, bool):
            source_total = count
        for item in message.get("items") or []:
            normalized = normalize_crossref(item)
            if normalized:
                results.append(normalized)
    queries.append(
        {
            "mode": "bibliographic",
            "request": {
                "method": "GET",
                "url": url,
                "query_bibliographic": bibliographic,
            },
            "receipt": receipt,
            "source_reported_total": source_total,
            "results": results,
        }
    )
    return {
        "candidate_id": candidate["candidate_id"],
        "status": "success"
        if all(query["receipt"]["outcome"] in {"success", "not_found"} for query in queries)
        else "partial_or_error",
        "queries": queries,
    }


def ntrs_exact_query(title: str) -> str:
    escaped = title.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def query_ntrs(session: requests.Session, candidate: Mapping[str, Any]) -> dict[str, Any]:
    title = clean_text(lookup_identity(candidate).get("title")) or ""
    query = ntrs_exact_query(title)
    payload = {"q": query, "page": {"from": 0, "size": MAX_RESULTS}, "highlight": False}
    url = "https://ntrs.nasa.gov/api/citations/search"
    decoded, receipt = request_json(session, "POST", url, payload=payload)
    results: list[dict[str, Any]] = []
    source_total = None
    if decoded:
        statistics = decoded.get("stats")
        if isinstance(statistics, Mapping):
            count = statistics.get("total")
            if isinstance(count, int) and not isinstance(count, bool):
                source_total = count
        for item in decoded.get("results") or []:
            normalized = normalize_ntrs(item)
            if normalized:
                results.append(normalized)
    return {
        "candidate_id": candidate["candidate_id"],
        "status": "success" if receipt["outcome"] == "success" else "partial_or_error",
        "queries": [
            {
                "mode": "exact_title",
                "request": {"method": "POST", "url": url, "json": payload},
                "receipt": receipt,
                "source_reported_total": source_total,
                "results": results,
            }
        ],
    }


QUERY_FUNCTIONS = {
    "openalex": query_openalex,
    "crossref": query_crossref,
    "ntrs": query_ntrs,
}


def candidates_from_source_ledger(
    output_dir: Path,
) -> tuple[list[dict[str, Any]], str] | None:
    for source in ("crossref", "ntrs", "openalex"):
        path = output_dir / "source-events" / f"{source}.json"
        if not path.is_file():
            continue
        ledger = load_json(path)
        snapshot = ledger.get("candidate_scope")
        candidate_file = ledger.get("candidate_file")
        if not isinstance(snapshot, list) or not isinstance(candidate_file, Mapping):
            continue
        candidate_hash = candidate_file.get("sha256_at_selection")
        if not isinstance(candidate_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", candidate_hash):
            raise ValueError("An existing source ledger has an invalid candidate hash")
        candidates: list[dict[str, Any]] = []
        for item in snapshot:
            if not isinstance(item, Mapping) or not isinstance(item.get("candidate_id"), str):
                raise ValueError("An existing source ledger has an invalid candidate scope")
            candidate = {
                "candidate_id": item["candidate_id"],
                "title": item.get("title"),
                "authors": copy.deepcopy(item.get("authors"))
                if isinstance(item.get("authors"), list)
                else [],
                "publication_year": item.get("publication_year"),
                "doi": item.get("doi"),
                "abstract": None,
                "screening_decision": "full_text_needed",
            }
            alias = item.get("prior_confirmed_identity")
            if isinstance(alias, Mapping):
                candidate["_prior_confirmed_identity"] = copy.deepcopy(dict(alias))
            candidates.append(candidate)
        return candidates, candidate_hash
    return None


def scope_snapshot(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": candidate.get("candidate_id"),
            "title": clean_text(candidate.get("title")),
            "authors": copy.deepcopy(candidate.get("authors"))
            if isinstance(candidate.get("authors"), list)
            else [],
            "publication_year": candidate.get("publication_year")
            if isinstance(candidate.get("publication_year"), int)
            and not isinstance(candidate.get("publication_year"), bool)
            else None,
            "doi": normalized_doi(candidate.get("doi")),
            "prior_confirmed_identity": copy.deepcopy(
                candidate.get("_prior_confirmed_identity")
            )
            if isinstance(candidate.get("_prior_confirmed_identity"), Mapping)
            else None,
            "missing_fields": [
                field for field in ("title", "abstract") if not clean_text(candidate.get(field))
            ],
        }
        for candidate in candidates
    ]


def collect_platform(
    source: str,
    candidates: list[dict[str, Any]],
    candidate_path: Path,
    candidate_hash: str,
    scope_path: Path,
    prior_follow_up_path: Path,
    output_dir: Path,
    *,
    resume: bool,
    checkpoint_every: int,
    delay_seconds: float,
) -> Path:
    source_path = output_dir / "source-events" / f"{source}.json"
    snapshot = scope_snapshot(candidates)
    if source_path.exists():
        if not resume:
            raise FileExistsError(f"Refusing to overwrite {source_path}; pass --resume")
        ledger = load_json(source_path)
        if (
            ledger.get("schema_version") != SOURCE_SCHEMA
            or ledger.get("source") != source
            or ledger.get("candidate_scope") != snapshot
        ):
            raise ValueError(f"The existing {source} ledger has a different scope")
        attempts = ledger.get("attempts")
        if not isinstance(attempts, list):
            raise ValueError(f"The existing {source} ledger has no attempts")
    else:
        ledger = {
            "schema_version": SOURCE_SCHEMA,
            "source": source,
            "platform": {
                "openalex": "OpenAlex",
                "crossref": "Crossref REST API",
                "ntrs": "NASA Technical Reports Server",
            }[source],
            "purpose": "candidate_metadata_follow_up_only",
            "candidate_file": {
                "path": candidate_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256_at_selection": candidate_hash,
            },
            "scope_file": {
                "path": scope_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": sha256(scope_path),
            },
            "prior_identity_evidence": {
                "path": prior_follow_up_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": sha256(prior_follow_up_path),
                "alias_count": sum(
                    isinstance(candidate.get("_prior_confirmed_identity"), Mapping)
                    for candidate in candidates
                ),
            },
            "candidate_scope": snapshot,
            "started_at_utc": utc_now(),
            "completed_at_utc": None,
            "attempts": [],
        }
        attempts = ledger["attempts"]

    completed_ids = {
        attempt.get("candidate_id")
        for attempt in attempts
        if isinstance(attempt, Mapping) and isinstance(attempt.get("candidate_id"), str)
    }
    if len(completed_ids) != len(attempts):
        raise ValueError(f"The existing {source} ledger repeats candidate IDs")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    query = QUERY_FUNCTIONS[source]
    additions = 0
    for position, candidate in enumerate(candidates, start=1):
        candidate_id = candidate["candidate_id"]
        if candidate_id in completed_ids:
            continue
        attempt = query(session, candidate)
        attempt["scope_position"] = position
        attempts.append(attempt)
        completed_ids.add(candidate_id)
        additions += 1
        if additions % checkpoint_every == 0:
            atomic_json(source_path, ledger)
            print(
                json.dumps(
                    {
                        "source": source,
                        "completed": len(attempts),
                        "total": len(candidates),
                    }
                ),
                flush=True,
            )
        if delay_seconds:
            time.sleep(delay_seconds)

    if [attempt.get("candidate_id") for attempt in attempts] != [
        candidate["candidate_id"] for candidate in candidates
    ]:
        by_id = {attempt.get("candidate_id"): attempt for attempt in attempts}
        if set(by_id) != {candidate["candidate_id"] for candidate in candidates}:
            raise ValueError(f"The {source} candidate coverage is incomplete")
        ledger["attempts"] = [by_id[candidate["candidate_id"]] for candidate in candidates]
    ledger["completed_at_utc"] = utc_now()
    atomic_json(source_path, ledger)
    return source_path


def result_identity_once(
    identity_source: str,
    identity_record: Mapping[str, Any],
    result: Mapping[str, Any],
    query_mode: str,
) -> dict[str, Any]:
    scores = title_scores(identity_record.get("title"), result.get("title"))
    overlap = author_overlap(identity_record.get("authors"), result.get("authors"))
    candidate_year = identity_record.get("publication_year")
    result_year = result.get("publication_year")
    year_delta = (
        abs(candidate_year - result_year)
        if isinstance(candidate_year, int)
        and not isinstance(candidate_year, bool)
        and isinstance(result_year, int)
        and not isinstance(result_year, bool)
        else None
    )
    candidate_doi = normalized_doi(identity_record.get("doi"))
    result_doi = normalized_doi(result.get("doi"))
    doi_exact = bool(candidate_doi and result_doi and candidate_doi == result_doi)
    doi_conflict = bool(candidate_doi and result_doi and candidate_doi != result_doi)
    shared_author = overlap["shared_term_count"] > 0
    year_close = year_delta is None or year_delta <= 2
    token_minimum = min(scores["candidate_token_count"], scores["result_token_count"])
    generic_short = scores["candidate_token_count"] < 4

    accepted = False
    basis = None
    if doi_exact:
        compatible_title = (
            scores["exact"]
            or scores["sequence"] >= 0.72
            or (scores["token_containment"] >= 0.8 and token_minimum >= 3)
        )
        if compatible_title and (year_close or shared_author):
            accepted = True
            basis = "exact_doi_with_compatible_title_and_year_or_author"
    if not accepted and not doi_conflict:
        if scores["exact"]:
            if not generic_short and (year_close or shared_author):
                accepted = True
                basis = "exact_normalized_title_with_compatible_year_or_author"
            elif generic_short and year_delta is not None and year_delta <= 1 and shared_author:
                accepted = True
                basis = "short_exact_title_with_year_and_author"
        elif (
            token_minimum >= 5
            and scores["sequence"] >= 0.92
            and scores["token_containment"] >= 0.85
            and (year_close or shared_author)
        ):
            accepted = True
            basis = "high_title_similarity_with_compatible_year_or_author"
        elif (
            token_minimum >= 6
            and scores["token_containment"] >= 0.95
            and (year_close or shared_author)
        ):
            accepted = True
            basis = "title_token_containment_with_compatible_year_or_author"
        elif (
            token_minimum >= 7
            and scores["sequence"] >= 0.83
            and scores["token_jaccard"] >= 0.75
            and year_close
            and shared_author
        ):
            accepted = True
            basis = "fuzzy_title_with_year_and_author"

    quality = max(
        scores["sequence"],
        scores["token_jaccard"],
        scores["token_containment"] * 0.98,
    )
    if doi_exact:
        quality += 0.08
    if shared_author:
        quality += 0.03
    if year_delta == 0:
        quality += 0.02
    if query_mode == "doi":
        quality += 0.01
    return {
        "identity_source": identity_source,
        "accepted": accepted,
        "match_basis": basis,
        "title_scores": scores,
        "author_overlap": overlap,
        "candidate_doi": candidate_doi,
        "result_doi": result_doi,
        "doi_exact": doi_exact,
        "doi_conflict": doi_conflict,
        "year_delta": year_delta,
        "quality_score": round(quality, 6),
    }


def result_identity(
    candidate: Mapping[str, Any], result: Mapping[str, Any], query_mode: str
) -> dict[str, Any]:
    comparisons = [
        result_identity_once("candidate_metadata", candidate, result, query_mode)
    ]
    alias = candidate.get("_prior_confirmed_identity")
    if isinstance(alias, Mapping):
        comparisons.append(
            result_identity_once(
                "prior_confirmed_portal_identity", alias, result, query_mode
            )
        )
    comparisons.sort(
        key=lambda comparison: (
            comparison["accepted"], comparison["quality_score"]
        ),
        reverse=True,
    )
    selected = copy.deepcopy(comparisons[0])
    selected["comparisons"] = copy.deepcopy(comparisons)
    return selected


def source_candidates(
    source: str,
    candidate: Mapping[str, Any],
    attempt: Mapping[str, Any],
) -> list[dict[str, Any]]:
    evaluated: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for query in attempt.get("queries") or []:
        if not isinstance(query, Mapping):
            continue
        mode = clean_text(query.get("mode")) or "unknown"
        for rank, result in enumerate(query.get("results") or [], start=1):
            if not isinstance(result, Mapping):
                continue
            source_id = clean_text(result.get("source_record_id"))
            title = clean_text(result.get("title"))
            if not source_id or not title:
                continue
            key = (source_id, canonical_title(title))
            identity = result_identity(candidate, result, mode)
            row = {
                "source": source,
                "query_mode": mode,
                "rank": rank,
                "identity": identity,
                "metadata": copy.deepcopy(dict(result)),
            }
            existing_position = next(
                (
                    position
                    for position, existing in enumerate(evaluated)
                    if (
                        existing["metadata"]["source_record_id"],
                        canonical_title(existing["metadata"]["title"]),
                    )
                    == key
                ),
                None,
            )
            if existing_position is None:
                seen.add(key)
                evaluated.append(row)
            elif identity["quality_score"] > evaluated[existing_position]["identity"]["quality_score"]:
                evaluated[existing_position] = row
    return sorted(
        evaluated,
        key=lambda row: (
            row["identity"]["accepted"],
            row["identity"]["quality_score"],
            bool(row["metadata"].get("abstract")),
            -row["rank"],
        ),
        reverse=True,
    )


def same_work(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_metadata = left["metadata"]
    right_metadata = right["metadata"]
    left_doi = normalized_doi(left_metadata.get("doi"))
    right_doi = normalized_doi(right_metadata.get("doi"))
    if left_doi and right_doi:
        return left_doi == right_doi
    scores = title_scores(left_metadata.get("title"), right_metadata.get("title"))
    left_year = left_metadata.get("publication_year")
    right_year = right_metadata.get("publication_year")
    years_compatible = (
        left_year is None or right_year is None or abs(left_year - right_year) <= 2
    )
    return years_compatible and (
        scores["exact"]
        or (scores["sequence"] >= 0.94 and scores["token_containment"] >= 0.9)
    )


def choose_match(matches: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, list[dict[str, Any]], bool]:
    accepted = [match for match in matches if match["identity"]["accepted"]]
    if not accepted:
        return None, [], False
    accepted.sort(
        key=lambda match: (
            match["identity"]["quality_score"],
            bool(match["metadata"].get("abstract")),
            {"crossref": 3, "ntrs": 2, "openalex": 1}.get(match["source"], 0),
        ),
        reverse=True,
    )
    anchor = accepted[0]
    compatible = [match for match in accepted if same_work(anchor, match)]
    incompatible = [match for match in accepted if not same_work(anchor, match)]
    ambiguous = bool(
        incompatible
        and incompatible[0]["identity"]["quality_score"]
        >= anchor["identity"]["quality_score"] - 0.03
    )
    if ambiguous:
        return None, accepted, True

    abstract_matches = [match for match in compatible if clean_text(match["metadata"].get("abstract"))]
    if abstract_matches:
        abstract_matches.sort(
            key=lambda match: (
                {"crossref": 3, "ntrs": 2, "openalex": 1}.get(match["source"], 0),
                match["identity"]["quality_score"],
                len(match["metadata"].get("abstract") or ""),
            ),
            reverse=True,
        )
        selected = abstract_matches[0]
    else:
        selected = anchor
    return selected, compatible, False


def compact_match(match: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": match["source"],
        "source_record_id": match["metadata"]["source_record_id"],
        "query_mode": match["query_mode"],
        "rank": match["rank"],
        "match_basis": match["identity"]["match_basis"],
        "identity": copy.deepcopy(match["identity"]),
        "metadata": copy.deepcopy(match["metadata"]),
    }


def finalize(
    candidates: list[dict[str, Any]],
    candidate_path: Path,
    candidate_hash: str,
    scope_path: Path,
    prior_follow_up_path: Path,
    output_dir: Path,
) -> Path:
    source_paths = {source: output_dir / "source-events" / f"{source}.json" for source in PLATFORMS}
    ledgers: dict[str, dict[str, Any]] = {}
    attempts_by_source: dict[str, dict[str, Mapping[str, Any]]] = {}
    receipts: list[dict[str, Any]] = []
    snapshot = scope_snapshot(candidates)
    for source, path in source_paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"The {source} source ledger is missing: {path}")
        ledger = load_json(path)
        if (
            ledger.get("schema_version") != SOURCE_SCHEMA
            or ledger.get("source") != source
            or ledger.get("candidate_scope") != snapshot
            or not ledger.get("completed_at_utc")
        ):
            raise ValueError(f"The {source} source ledger is incomplete or has a different scope")
        attempts = ledger.get("attempts")
        if not isinstance(attempts, list) or len(attempts) != len(candidates):
            raise ValueError(f"The {source} source ledger has incomplete coverage")
        by_id = {
            attempt.get("candidate_id"): attempt
            for attempt in attempts
            if isinstance(attempt, Mapping)
        }
        if set(by_id) != {candidate["candidate_id"] for candidate in candidates}:
            raise ValueError(f"The {source} source ledger candidate IDs changed")
        ledgers[source] = ledger
        attempts_by_source[source] = by_id
        receipts.append(source_receipt(path, source, ledger))

    records: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        matches: list[dict[str, Any]] = []
        source_outcomes: dict[str, Any] = {}
        for source in PLATFORMS:
            attempt = attempts_by_source[source][candidate_id]
            evaluated = source_candidates(source, candidate, attempt)
            matches.extend(evaluated)
            accepted = [match for match in evaluated if match["identity"]["accepted"]]
            queries = attempt.get("queries") or []
            source_outcomes[source] = {
                "request_status": attempt.get("status"),
                "query_count": len(queries),
                "result_count": sum(len(query.get("results") or []) for query in queries),
                "accepted_match_count": len(accepted),
                "best_result": compact_match(evaluated[0]) if evaluated else None,
            }

        selected, compatible, ambiguous = choose_match(matches)
        if ambiguous:
            status = "identity_ambiguous"
        elif selected and clean_text(selected["metadata"].get("abstract")):
            status = "abstract_found"
        elif selected:
            status = "metadata_found_no_abstract"
        elif all(
            source_outcomes[source]["request_status"] != "success" for source in PLATFORMS
        ):
            status = "source_failure"
        else:
            status = "no_confirmed_match"
        records.append(
            {
                "candidate_id": candidate_id,
                "missing_fields_at_selection": [
                    field
                    for field in ("title", "abstract")
                    if not clean_text(candidate.get(field))
                ],
                "status": status,
                "selected_match": compact_match(selected) if selected else None,
                "corroborating_matches": [compact_match(match) for match in compatible],
                "source_outcomes": source_outcomes,
                "evidence_note": (
                    "A conservative DOI, title, year, and author identity check accepted the selected metadata."
                    if selected
                    else (
                        "Multiple similarly strong results represented incompatible identities, so no metadata was selected."
                        if ambiguous
                        else "No returned result met the conservative identity threshold."
                    )
                ),
            }
        )

    status_counts = Counter(record["status"] for record in records)
    source_selected_counts = Counter(
        record["selected_match"]["source"]
        for record in records
        if record["selected_match"] is not None
    )
    enrichment = {
        "schema_version": ENRICHMENT_SCHEMA,
        "generated_at": utc_now(),
        "scope": {
            "candidate_file_path": candidate_path.relative_to(REPOSITORY_ROOT).as_posix(),
            "candidate_file_sha256_at_selection": candidate_hash,
            "scope_file_path": scope_path.relative_to(REPOSITORY_ROOT).as_posix(),
            "scope_file_sha256": sha256(scope_path),
            "prior_identity_evidence_path": prior_follow_up_path.relative_to(
                REPOSITORY_ROOT
            ).as_posix(),
            "prior_identity_evidence_sha256": sha256(prior_follow_up_path),
            "prior_confirmed_identity_alias_count": sum(
                isinstance(candidate.get("_prior_confirmed_identity"), Mapping)
                for candidate in candidates
            ),
            "selection_predicate": (
                "screening_decision == full_text_needed and "
                "(title is empty or abstract is empty)"
            ),
            "candidate_count": len(candidates),
            "missing_title_count": sum(not clean_text(candidate.get("title")) for candidate in candidates),
            "missing_abstract_count": sum(
                not clean_text(candidate.get("abstract")) for candidate in candidates
            ),
        },
        "method": {
            "excluded_platforms": ["Scopus", "Web of Science Core Collection"],
            "queried_platforms": ["OpenAlex", "Crossref REST API", "NASA Technical Reports Server"],
            "query_policy": (
                "Every scoped candidate received an OpenAlex work-autocomplete title query, a Crossref "
                "bibliographic query, and an exact-title NASA NTRS query. DOI-bearing candidates also "
                "received direct Crossref DOI queries."
            ),
            "identity_policy": (
                "Metadata is selected only after conservative DOI, normalized-title, publication-year, "
                "and author compatibility checks. A DOI response with conflicting bibliographic identity "
                "is rejected. Near-tied incompatible identities remain ambiguous."
            ),
            "abstract_priority": ["crossref", "ntrs", "openalex"],
            "application_policy": (
                "The reproducible candidate builder may fill absent metadata only. It must not replace "
                "existing nonempty candidate fields or reviewer screening decisions."
            ),
        },
        "source_ledgers": receipts,
        "records": records,
        "summary": {
            "candidate_coverage": len(records),
            "status_counts": dict(sorted(status_counts.items())),
            "selected_source_counts": dict(sorted(source_selected_counts.items())),
            "selected_metadata_count": sum(record["selected_match"] is not None for record in records),
            "new_abstract_count": status_counts["abstract_found"],
            "remaining_missing_title_count": sum(
                not clean_text(candidate.get("title"))
                and not (
                    record["selected_match"]
                    and clean_text(record["selected_match"]["metadata"].get("title"))
                )
                for candidate, record in zip(candidates, records, strict=True)
            ),
            "remaining_missing_abstract_count": len(records) - status_counts["abstract_found"],
        },
    }
    path = output_dir / "metadata-enrichment.json"
    atomic_json(path, enrichment)
    return path


def validate_nonnegative_finite(value: float, name: str) -> float:
    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError(f"{name} must be finite and nonnegative")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-path", type=Path, default=DEFAULT_CANDIDATE_PATH)
    parser.add_argument("--scope-path", type=Path, default=DEFAULT_SCOPE_PATH)
    parser.add_argument(
        "--prior-follow-up-path",
        type=Path,
        default=DEFAULT_PRIOR_FOLLOW_UP_PATH,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--platform",
        choices=(*PLATFORMS, "all", "finalize"),
        default="all",
        help="collect one platform, collect all platforms, or only finalize existing ledgers",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=10)
    parser.add_argument("--delay-seconds", type=float, default=0.08)
    args = parser.parse_args()
    args.candidate_path = args.candidate_path.resolve(strict=True)
    args.scope_path = args.scope_path.resolve(strict=True)
    args.prior_follow_up_path = args.prior_follow_up_path.resolve(strict=True)
    args.output_dir = args.output_dir.resolve(strict=False)
    try:
        args.output_dir.relative_to(REPOSITORY_ROOT)
    except ValueError:
        parser.error("--output-dir must resolve inside the repository")
    if args.output_dir.exists() and args.output_dir.is_symlink():
        parser.error("--output-dir cannot be a symlink")
    if args.checkpoint_every < 1:
        parser.error("--checkpoint-every must be positive")
    try:
        args.delay_seconds = validate_nonnegative_finite(args.delay_seconds, "--delay-seconds")
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))
    return args


def main() -> int:
    args = parse_args()
    existing_scope = candidates_from_source_ledger(args.output_dir)
    if existing_scope:
        candidates, candidate_hash = existing_scope
    else:
        candidates, candidate_hash = selected_candidates(
            args.candidate_path,
            args.scope_path,
            args.prior_follow_up_path,
        )
    sources = PLATFORMS if args.platform == "all" else (args.platform,)
    if args.platform != "finalize":
        for source in sources:
            path = collect_platform(
                source,
                candidates,
                args.candidate_path,
                candidate_hash,
                args.scope_path,
                args.prior_follow_up_path,
                args.output_dir,
                resume=args.resume,
                checkpoint_every=args.checkpoint_every,
                delay_seconds=args.delay_seconds,
            )
            print(json.dumps({"status": "collected", "source": source, "path": str(path)}))
    if args.platform in {"all", "finalize"}:
        path = finalize(
            candidates,
            args.candidate_path,
            candidate_hash,
            args.scope_path,
            args.prior_follow_up_path,
            args.output_dir,
        )
        print(json.dumps({"status": "finalized", "path": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
