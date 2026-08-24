#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""One-request-at-a-time, record-free NTRS P02 diagnostic probe.

The tool deliberately writes only compact request/shape/count/ID/lexical
receipts. Response bodies, headers other than content type, cookies, sessions,
and normalized candidate records remain in memory and are never persisted.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urljoin, urlsplit

import requests

USER_AGENT = "SLR1-NTRS-P02/1.0 (public diagnostic metadata; no credentials)"
DEFAULT_TIMEOUT_SECONDS = 45.0
NTRS_ORIGIN = "https://ntrs.nasa.gov"
NTRS_SEARCH_URL = f"{NTRS_ORIGIN}/api/citations/search"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def compact_scalar(value: Any, *, limit: int = 240) -> Any:
    """Keep only compact diagnostic scalar evidence, never arbitrary records."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        clean = " ".join(value.split())
        return clean[:limit] + ("…" if len(clean) > limit else "")
    return {"type": json_type(value)}


def compact_field_value(value: Any, *, depth: int = 0) -> Any:
    """Bound retained field evidence for one explicitly selected public record."""
    if depth > 2:
        return {"type": json_type(value)}
    if value is None or isinstance(value, (bool, int, float, str)):
        return compact_scalar(value)
    if isinstance(value, list):
        return {
            "type": "array",
            "length": len(value),
            "sample": [compact_field_value(item, depth=depth + 1) for item in value[:4]],
        }
    if isinstance(value, dict):
        return {
            "type": "object",
            "keys": sorted(str(key) for key in value)[:30],
            "sample": {
                str(key): compact_field_value(value[key], depth=depth + 1)
                for key in sorted(value, key=str)[:8]
            },
        }
    return {"type": json_type(value)}


def raw_ntrs_id(record: Any) -> str | None:
    if not isinstance(record, Mapping):
        return None
    value = record.get("id")
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    text = str(value).strip()
    return text or None


def ordered_id_digest(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def lexical_hits(records: list[Any], terms: list[str]) -> list[dict[str, Any]]:
    """Find locatable terms only in public lexical metadata surfaces."""
    allowed_top_level = {"title", "abstract", "keywords", "subjectCategories", "keyword", "subjectCategory"}
    hits: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, Mapping):
            continue
        record_id = raw_ntrs_id(record)
        for field in allowed_top_level:
            value = record.get(field)
            values: list[tuple[str, str]] = []
            if isinstance(value, str):
                values.append((field, value))
            elif isinstance(value, list):
                for index, item in enumerate(value[:30]):
                    if isinstance(item, str):
                        values.append((f"{field}[{index}]", item))
                    elif isinstance(item, Mapping):
                        for key in ("name", "value", "label", "term", "title"):
                            nested = item.get(key)
                            if isinstance(nested, str):
                                values.append((f"{field}[{index}].{key}", nested))
            elif isinstance(value, Mapping):
                for key in ("name", "value", "label", "term", "title"):
                    nested = value.get(key)
                    if isinstance(nested, str):
                        values.append((f"{field}.{key}", nested))
            for path, text in values:
                lower = text.casefold()
                for term in terms:
                    if term.casefold() not in lower:
                        continue
                    start = lower.find(term.casefold())
                    snippet = " ".join(text[max(0, start - 80): start + len(term) + 100].split())
                    hits.append(
                        {
                            "record_id": record_id,
                            "field": path,
                            "term": term,
                            "context": snippet[:260] + ("…" if len(snippet) > 260 else ""),
                        }
                    )
                    if len(hits) >= 20:
                        return hits
    return hits


def recursive_named_values(value: Any, names: set[str], path: str = "", depth: int = 0) -> list[dict[str, Any]]:
    """Capture only short q/query echo strings and their source paths."""
    if depth > 7:
        return []
    found: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if str(key).casefold() in names and isinstance(child, (str, int, float, bool)):
                found.append({"path": child_path, "value": compact_scalar(child, limit=500)})
            found.extend(recursive_named_values(child, names, child_path, depth + 1))
            if len(found) >= 20:
                return found[:20]
    elif isinstance(value, list):
        for index, child in enumerate(value[:20]):
            found.extend(recursive_named_values(child, names, f"{path}[{index}]", depth + 1))
            if len(found) >= 20:
                return found[:20]
    return found


def stats_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {"type": json_type(value)}
    output: dict[str, Any] = {
        "type": "object",
        "keys": sorted(str(key) for key in value),
        "total": {"present": "total" in value, "type": json_type(value.get("total")), "value": compact_scalar(value.get("total"))},
    }
    exactness: dict[str, Any] = {}
    for key, item in value.items():
        normalized = str(key).casefold()
        if any(marker in normalized for marker in ("estimate", "exact", "approx", "relation", "lower", "upper")):
            exactness[str(key)] = {"type": json_type(item), "value": compact_scalar(item)}
    output["exactness_or_estimate_signals"] = exactness
    return output


def aggregation_summary(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {
            "type": "object",
            "keys": sorted(str(key) for key in value)[:100],
            "member_types": {str(key): json_type(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))[:30]},
        }
    if isinstance(value, list):
        return {"type": "array", "length": len(value), "member_types": sorted({json_type(item) for item in value[:30]})}
    return {"type": json_type(value)}


def safe_content_type(response: requests.Response) -> str | None:
    value = response.headers.get("Content-Type")
    if not isinstance(value, str):
        return None
    return value.split(";", 1)[0].strip().casefold() or None


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_query(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    if not args.query_file:
        raise ValueError("--query-file is required for search or strict operations")
    query = Path(args.query_file).read_text(encoding="utf-8")
    if "\r" in query or "\n" in query:
        raise ValueError("query file must contain exactly one UTF-8 query without a line ending")
    if not query:
        raise ValueError("query file must not be empty")
    return query, {
        "label": args.query_label or Path(args.query_file).name,
        "utf8_bytes": len(query.encode("utf-8")),
        "sha256": sha256_text(query),
        "executed_query": query,
    }


def parse_extra_payload(args: argparse.Namespace) -> dict[str, Any]:
    if not args.extra_payload_file:
        return {}
    raw = Path(args.extra_payload_file).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("extra payload JSON must be an object")
    return value


def request_once(method: str, url: str, *, json_payload: dict[str, Any] | None, timeout: float) -> tuple[requests.Response | None, dict[str, Any] | None, dict[str, Any]]:
    started = utc_now()
    try:
        response = requests.request(
            method=method,
            url=url,
            json=json_payload,
            headers={"Accept": "application/json" if method == "POST" else "*/*", "User-Agent": USER_AGENT},
            timeout=timeout,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        return None, None, {
            "started_at": started,
            "ended_at": utc_now(),
            "status": "failed",
            "error_type": type(error).__name__,
            "http_status": None,
            "content_type": None,
            "redirects_followed": false_value(),
        }
    ended = utc_now()
    content_type = safe_content_type(response)
    try:
        data = response.json()
        json_error = None
    except (ValueError, TypeError):
        data = None
        json_error = "non_json"
    return response, data, {
        "started_at": started,
        "ended_at": ended,
        "status": "success" if 200 <= response.status_code < 300 and data is not None else "failed",
        "http_status": response.status_code,
        "content_type": content_type,
        "redirects_followed": false_value(),
        "json_parse": "success" if data is not None else json_error,
        "response_body_sha256": sha256_bytes(response.content),
        "response_body_bytes": len(response.content),
    }


def false_value() -> bool:
    return False


def run_health(args: argparse.Namespace) -> dict[str, Any]:
    response, data, base = request_once("GET", args.url or f"{NTRS_ORIGIN}/api/health", json_payload=None, timeout=args.timeout)
    health: dict[str, Any] = {"json_type": json_type(data)}
    if isinstance(data, Mapping):
        health["keys"] = sorted(str(key) for key in data)
        health["status"] = compact_scalar(data.get("status"))
    return {
        "schema_version": "slr1-ntrs-p02-single-request/v1",
        "operation": "health",
        "request": {"method": "GET", "url": args.url or f"{NTRS_ORIGIN}/api/health", "authenticated": False, "automatic_transport_retries": 0, "cookies_or_session_sent": False},
        "response": {**base, "health": health},
        "retention": {"raw_response_body_retained": False, "response_headers_retained": ["content-type"], "cookies_or_session_retained": False, "candidate_rows_retained": False},
    }


def run_search(args: argparse.Namespace) -> dict[str, Any]:
    query, query_meta = read_query(args)
    payload: dict[str, Any] = {"q": query, "page": {"from": args.page_from, "size": args.page_size}, "highlight": False}
    if args.date_start or args.date_end:
        published: dict[str, str] = {}
        if args.date_start:
            published["gte"] = args.date_start
        if args.date_end:
            published["lte"] = args.date_end
        payload["published"] = published
    payload.update(parse_extra_payload(args))
    # q/page/highlight remain authoritative even if an extra control file was malformed.
    payload["q"] = query
    payload["page"] = {"from": args.page_from, "size": args.page_size}
    payload["highlight"] = False
    response, data, base = request_once("POST", args.url or NTRS_SEARCH_URL, json_payload=payload, timeout=args.timeout)
    envelope: dict[str, Any] = {"json_type": json_type(data)}
    ids: list[str] = []
    records: list[Any] = []
    if isinstance(data, Mapping):
        envelope["top_level_keys"] = sorted(str(key) for key in data)
        envelope["stats"] = stats_summary(data.get("stats"))
        envelope["aggregations"] = aggregation_summary(data.get("aggregations")) if "aggregations" in data else {"present": False}
        results_value = data.get("results")
        envelope["results"] = {
            "type": json_type(results_value),
            "count": len(results_value) if isinstance(results_value, list) else None,
        }
        if isinstance(results_value, list):
            records = results_value
            ids = [record_id for record in (raw_ntrs_id(item) for item in results_value) if record_id]
            envelope["results"]["record_object_count"] = sum(isinstance(item, Mapping) for item in results_value)
            if results_value and isinstance(results_value[0], Mapping):
                first = results_value[0]
                selected = {field: compact_field_value(first.get(field)) for field in args.retain_field if field in first}
                envelope["first_record"] = {
                    "id": raw_ntrs_id(first),
                    "top_level_fields": sorted(str(key) for key in first),
                    "selected_public_fields": selected,
                }
            else:
                envelope["first_record"] = None
        echoes = recursive_named_values(data, {"q", "query", "querytext", "searchquery", "executedquery"})
        envelope["query_echo_or_rewrite"] = {
            "visible_values": echoes,
            "exact_query_echo_present": any(item.get("value") == query for item in echoes),
        }
        control_paths = recursive_named_values(data, {"published", "page", "sort", "from", "size"})
        envelope["response_control_visibility"] = {"paths": [item["path"] for item in control_paths]}
    else:
        envelope["stats"] = {"type": "absent"}
        envelope["aggregations"] = {"present": False}
        envelope["results"] = {"type": "absent", "count": None}
        envelope["query_echo_or_rewrite"] = {"visible_values": [], "exact_query_echo_present": False}
        envelope["response_control_visibility"] = {"paths": []}
    return {
        "schema_version": "slr1-ntrs-p02-single-request/v1",
        "operation": "search",
        "query": query_meta,
        "request": {"method": "POST", "url": args.url or NTRS_SEARCH_URL, "payload": payload, "authenticated": False, "automatic_transport_retries": 0, "cookies_or_session_sent": False},
        "response": {**base, "envelope": envelope},
        "stable_id_ledger": {"ids": ids, "count": len(ids), "ordered_sha256_length_prefixed_utf8": ordered_id_digest(ids), "all_ids_nonempty": len(ids) == len(records)},
        "lexical_field_evidence": lexical_hits(records, args.lexical),
        "retention": {"raw_response_body_retained": False, "response_headers_retained": ["content-type"], "cookies_or_session_retained": False, "candidate_rows_retained": False, "retained_public_diagnostic_metadata": ["response shape", "stats", "aggregations shape", "raw NTRS IDs", "explicitly requested lexical snippets only"]},
    }


def same_origin_public_script_urls(root_url: str, html: str) -> list[str]:
    origin = urlsplit(root_url)
    candidates = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", html, flags=re.I)
    urls: list[str] = []
    for candidate in candidates:
        resolved = urljoin(root_url, candidate)
        parsed = urlsplit(resolved)
        if parsed.scheme == "https" and parsed.hostname == origin.hostname and parsed.query == "" and resolved not in urls:
            urls.append(resolved)
    return urls


def text_contexts(text: str, terms: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    lowered = text.casefold()
    for term in terms:
        matches: list[str] = []
        needle = term.casefold()
        start = 0
        while len(matches) < 3:
            position = lowered.find(needle, start)
            if position < 0:
                break
            snippet = " ".join(text[max(0, position - 110): position + len(term) + 150].split())
            matches.append(snippet[:360] + ("…" if len(snippet) > 360 else ""))
            start = position + max(1, len(needle))
        result[term] = matches
    return result


def run_static_client(args: argparse.Namespace) -> dict[str, Any]:
    root_url = args.url or f"{NTRS_ORIGIN}/"
    requests_made: list[dict[str, Any]] = []
    root_response, _, root_base = request_once("GET", root_url, json_payload=None, timeout=args.timeout)
    requests_made.append({"method": "GET", "url": root_url, **root_base})
    if root_response is None or not (200 <= root_response.status_code < 300):
        return {"schema_version": "slr1-ntrs-p02-static-client/v1", "operation": "static_client", "requests": requests_made, "status": "failed", "retention": {"raw_response_bodies_retained": False, "response_headers_retained": ["content-type"], "cookies_or_session_retained": False}}
    root_text = root_response.text
    scripts = same_origin_public_script_urls(root_url, root_text)
    selected = next((url for url in scripts if re.search(r"(?:^|/)main[.-].+\.js$", url)), scripts[0] if scripts else None)
    result: dict[str, Any] = {
        "schema_version": "slr1-ntrs-p02-static-client/v1",
        "operation": "static_client",
        "status": "success",
        "requests": requests_made,
        "root": {"sha256": sha256_text(root_text), "bytes": len(root_response.content), "script_urls": scripts[:20], "term_contexts": text_contexts(root_text, args.static_term)},
        "retention": {"raw_response_bodies_retained": False, "response_headers_retained": ["content-type"], "cookies_or_session_retained": False},
    }
    if selected is None:
        result["static_asset"] = {"status": "not_found"}
        return result
    asset_response, _, asset_base = request_once("GET", selected, json_payload=None, timeout=args.timeout)
    requests_made.append({"method": "GET", "url": selected, **asset_base})
    if asset_response is None or not (200 <= asset_response.status_code < 300):
        result["status"] = "partial"
        result["static_asset"] = {"url": selected, "status": "failed"}
        return result
    asset_text = asset_response.text
    result["static_asset"] = {"url": selected, "sha256": sha256_text(asset_text), "bytes": len(asset_response.content), "term_contexts": text_contexts(asset_text, args.static_term)}
    return result


def run_text_probe(args: argparse.Namespace) -> dict[str, Any]:
    response, _, base = request_once("GET", args.url, json_payload=None, timeout=args.timeout)
    if response is None:
        text_summary = {"status": "failed"}
    else:
        text = response.text
        text_summary = {"sha256": sha256_text(text), "bytes": len(response.content), "term_contexts": text_contexts(text, args.static_term)}
    return {
        "schema_version": "slr1-ntrs-p02-single-request/v1",
        "operation": "text_probe",
        "request": {"method": "GET", "url": args.url, "authenticated": False, "automatic_transport_retries": 0, "cookies_or_session_sent": False},
        "response": {**base, "text_summary": text_summary},
        "retention": {"raw_response_body_retained": False, "response_headers_retained": ["content-type"], "cookies_or_session_retained": False, "candidate_rows_retained": False},
    }


def load_pinned_adapter(adapter_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("p02_pinned_search_ntrs", adapter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load pinned NTRS adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_strict(args: argparse.Namespace) -> dict[str, Any]:
    query, query_meta = read_query(args)
    adapter_path = Path(args.adapter_script)
    started = utc_now()
    try:
        adapter = load_pinned_adapter(adapter_path)
        result = adapter.search_ntrs(
            query,
            limit=args.limit,
            max_pages=args.max_pages,
            date_start=args.date_start,
            date_end=args.date_end,
            require_complete=True,
        )
    except Exception as error:  # Adapter errors are compacted intentionally.
        return {
            "schema_version": "slr1-ntrs-p02-pinned-strict-adapter/v1",
            "operation": "pinned_strict_adapter",
            "query": query_meta,
            "adapter": {"commit": args.adapter_commit, "script_sha256": args.adapter_sha256, "uses_exact_worktree": True, "automatic_transport_retries": 0},
            "controls": {"limit": args.limit, "max_pages": args.max_pages, "date_start": args.date_start, "date_end": args.date_end, "require_complete": True},
            "started_at": started,
            "ended_at": utc_now(),
            "status": "failed",
            "error_type": type(error).__name__,
            "source_reported_total": None,
            "records_retained": 0,
            "retention": {"raw_response_bodies_retained": False, "adapter_normalized_result_persisted": False, "candidate_rows_retained": False},
        }
    metadata = result.get("output_metadata") if isinstance(result, Mapping) else {}
    rows = result.get("results") if isinstance(result, Mapping) else []
    ids = [str(row.get("paperId")).strip() for row in rows if isinstance(row, Mapping) and str(row.get("paperId") or "").strip()]
    strict_receipt = metadata.get("strict_complete_comparison_receipt") if isinstance(metadata, Mapping) else None
    return {
        "schema_version": "slr1-ntrs-p02-pinned-strict-adapter/v1",
        "operation": "pinned_strict_adapter",
        "query": query_meta,
        "adapter": {"commit": args.adapter_commit, "script_sha256": args.adapter_sha256, "uses_exact_worktree": True, "automatic_transport_retries": 0},
        "controls": {"limit": args.limit, "max_pages": args.max_pages, "date_start": args.date_start, "date_end": args.date_end, "require_complete": True},
        "started_at": started,
        "ended_at": utc_now(),
        "status": "success" if metadata.get("strict_completion") is True else "failed",
        "source_reported_total": result.get("total"),
        "total_is_exact_claimed_by_adapter": metadata.get("total_is_exact"),
        "source_ordering": metadata.get("source_ordering"),
        "strict_complete_comparison_receipt": strict_receipt,
        "stable_id_ledger": {"ids": ids, "count": len(ids), "ordered_sha256_length_prefixed_utf8": ordered_id_digest(ids), "all_ids_nonempty": len(ids) == len(rows)},
        "records_retained": 0,
        "retention": {"raw_response_bodies_retained": False, "adapter_normalized_result_persisted": False, "candidate_rows_retained": False, "note": "The pinned adapter result was held only in memory; this receipt retains raw IDs/counts/hashes and no titles, authors, abstracts, links, or candidate corpus."},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("health", "search", "static-client", "text-probe", "strict"))
    parser.add_argument("--receipt", required=True, help="P02 compact receipt path")
    parser.add_argument("--url")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--query-file")
    parser.add_argument("--query-label")
    parser.add_argument("--page-from", type=int, default=0)
    parser.add_argument("--page-size", type=int, default=1)
    parser.add_argument("--date-start")
    parser.add_argument("--date-end")
    parser.add_argument("--extra-payload-file")
    parser.add_argument("--retain-field", action="append", default=[])
    parser.add_argument("--lexical", action="append", default=[])
    parser.add_argument("--static-term", action="append", default=[])
    parser.add_argument("--adapter-script")
    parser.add_argument("--adapter-commit")
    parser.add_argument("--adapter-sha256")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-pages", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    if args.operation == "health":
        payload = run_health(args)
    elif args.operation == "search":
        if args.page_from < 0 or args.page_size < 0:
            raise SystemExit("page controls must be non-negative")
        payload = run_search(args)
    elif args.operation == "static-client":
        if not args.static_term:
            args.static_term = ["NTRS", "Registered", "PubSpace", "subjectCategory", "keywords", "published", "sort", "page.from", "page.size"]
        payload = run_static_client(args)
    elif args.operation == "text-probe":
        if not args.url:
            raise SystemExit("--url is required for text-probe")
        if not args.static_term:
            args.static_term = ["NTRS", "public", "registered", "PubSpace"]
        payload = run_text_probe(args)
    else:
        if not args.adapter_script or not args.adapter_commit or not args.adapter_sha256:
            raise SystemExit("strict requires --adapter-script, --adapter-commit, and --adapter-sha256")
        if args.limit is None or args.max_pages is None or args.limit < 1 or args.max_pages < 1:
            raise SystemExit("strict requires positive --limit and --max-pages")
        payload = run_strict(args)
    atomic_json(Path(args.receipt), payload)
    print(json.dumps({"operation": args.operation, "receipt_written": True, "status": payload.get("status", payload.get("response", {}).get("status"))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
