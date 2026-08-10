#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.34.2"]
# ///
"""Whole-instance ESA Indico census, material inventory, extraction, and match.

The operation inventories materials *before* candidate gating.  It matches the
frozen P/E/M/G/C1/R/T dictionary independently against joined metadata and each
extractable attachment, then unions the routes.  Pilot mode is the default and
its output is explicitly prohibited from screening or evidence use.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit, urlunsplit
import zipfile
import xml.etree.ElementTree as ET

import requests

from concept_matcher import ConceptMatcher, MatcherError, atomic_write_json, load_json, normalize_text, run_fixtures, sha256_file


ROOT_URL = "https://indico.esa.int/export/categ/0.json"
CATEGORY_URL = "https://indico.esa.int/export/categ/{category_id}.json"
EVENT_URL = "https://indico.esa.int/export/event/{event_id}.json?detail=contributions"
CHILD_CATEGORY_IDS = (5, 6, 7, 9)
RETRYABLE = {408, 425, 429, 500, 502, 503, 504}
ACCESS_FAILURES = {401, 403, 418}
DOCUMENT_EXTENSIONS = {
    ".pdf", ".txt", ".text", ".md", ".markdown", ".html", ".htm", ".xml", ".json",
    ".csv", ".tsv", ".tex", ".log", ".rtf", ".doc", ".docx", ".odt", ".ppt", ".pptx",
    ".odp", ".xls", ".xlsx", ".ods", ".ps", ".eps"
}
DOCUMENT_MIME_PREFIXES = ("text/",)
DOCUMENT_MIME_TYPES = {
    "application/pdf", "application/rtf", "application/msword", "application/json", "application/xml",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.oasis.opendocument.text", "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.spreadsheet", "application/postscript"
}
SLIDE_MARKERS = ("slide", "presentation", "poster", "briefing")


class HarvestError(RuntimeError):
    """The source census or reproducibility contract cannot be completed."""


@dataclass
class Attachment:
    key: str
    association_type: str
    event_id: str
    contribution_id: str | None
    folder_id: str
    folder_title: str
    attachment_id: str
    title: str
    description: str
    filename: str
    content_type: str
    size: int | None
    url: str
    protected: bool
    document_like: bool
    lead_only_hint: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_url(value: str) -> str:
    parsed = urlsplit(value)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def safe_name(value: str, fallback: str) -> str:
    value = unquote(value or "").replace("\x00", "")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(value).name).strip(".-")
    return value[:180] or fallback


def scalar_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(scalar_text(item) for item in value)
    if isinstance(value, dict):
        preferred = [
            value.get("title"), value.get("name"), value.get("fullName"), value.get("affiliation"),
            value.get("description"), value.get("label"), value.get("code")
        ]
        text = " ".join(scalar_text(item) for item in preferred if item not in (None, "", [], {}))
        return text or " ".join(scalar_text(item) for item in value.values())
    return str(value)


def response_json(session: requests.Session, url: str, timeout: float, retries: int, delay: float) -> tuple[dict[str, Any], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=timeout, allow_redirects=True)
        except requests.RequestException as error:
            if attempt >= retries:
                raise HarvestError(f"network failure for {safe_url(url)} after {attempt + 1} attempts: {type(error).__name__}") from error
            wait = min(30.0, delay * (2**attempt))
            events.append({"attempt": attempt + 1, "event": "network_error", "error_type": type(error).__name__, "wait": wait})
            time.sleep(wait)
            continue
        if response.status_code in RETRYABLE and attempt < retries:
            retry_after = response.headers.get("Retry-After", "")
            try:
                wait = min(60.0, max(0.0, float(retry_after))) if retry_after else min(30.0, delay * (2**attempt))
            except ValueError:
                wait = min(30.0, delay * (2**attempt))
            events.append({"attempt": attempt + 1, "event": f"http_{response.status_code}", "wait": wait})
            time.sleep(wait)
            continue
        if response.status_code in ACCESS_FAILURES or response.status_code >= 400:
            raise HarvestError(f"HTTP {response.status_code} for {safe_url(url)}")
        content_type = response.headers.get("Content-Type", "").casefold()
        if "json" not in content_type and response.text.lstrip().casefold().startswith(("<html", "<!doctype html")):
            raise HarvestError(f"non-JSON HTML/challenge response for {safe_url(url)}")
        try:
            payload = response.json()
        except ValueError as error:
            raise HarvestError(f"malformed JSON for {safe_url(url)}") from error
        if not isinstance(payload, dict):
            raise HarvestError(f"JSON root is not an object for {safe_url(url)}")
        raw = response.content
        return payload, {
            "url": safe_url(response.url), "status": response.status_code, "retrieved_at_utc": utc_now(),
            "bytes": len(raw), "sha256": sha256_bytes(raw), "retry_events": events, "raw_bytes": raw
        }
    raise HarvestError(f"request exhausted for {safe_url(url)}")


def parse_event_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    results = payload.get("results")
    if not isinstance(results, list) or any(not isinstance(item, dict) for item in results):
        raise HarvestError("category export lacks an object results array")
    return results


def event_date(event: dict[str, Any]) -> date | None:
    value = event.get("startDate")
    candidate = value.get("date") if isinstance(value, dict) else value
    try:
        return date.fromisoformat(str(candidate)[:10])
    except (TypeError, ValueError):
        return None


def attachment_extension(filename: str, url: str) -> str:
    suffix = Path(filename or urlsplit(url).path).suffix.casefold()
    return suffix


def document_like(filename: str, url: str, content_type: str) -> bool:
    mime = content_type.split(";", 1)[0].strip().casefold()
    return attachment_extension(filename, url) in DOCUMENT_EXTENSIONS or mime.startswith(DOCUMENT_MIME_PREFIXES) or mime in DOCUMENT_MIME_TYPES


def iter_materials(owner: dict[str, Any], association_type: str, event_id: str, contribution_id: str | None) -> Iterable[Attachment]:
    seen: set[str] = set()
    folders = owner.get("folders") if isinstance(owner.get("folders"), list) else []
    for folder in folders:
        if not isinstance(folder, dict):
            continue
        folder_id = str(folder.get("id", ""))
        folder_title = scalar_text(folder.get("title"))
        for item in folder.get("attachments") or []:
            if not isinstance(item, dict):
                continue
            url = str(item.get("download_url") or item.get("url") or "").strip()
            attachment_id = str(item.get("id", ""))
            key = url or f"{association_type}:{event_id}:{contribution_id}:{folder_id}:{attachment_id}"
            if not url or key in seen:
                continue
            seen.add(key)
            filename = str(item.get("filename") or item.get("title") or Path(urlsplit(url).path).name)
            content_type = str(item.get("content_type") or mimetypes.guess_type(filename)[0] or "")
            size = item.get("size") if isinstance(item.get("size"), int) else None
            title = scalar_text(item.get("title"))
            description = scalar_text(item.get("description"))
            hint_text = f"{folder_title} {title} {filename}".casefold()
            yield Attachment(
                key=key, association_type=association_type, event_id=event_id, contribution_id=contribution_id,
                folder_id=folder_id, folder_title=folder_title, attachment_id=attachment_id, title=title,
                description=description, filename=filename, content_type=content_type, size=size, url=safe_url(url),
                protected=bool(item.get("is_protected") or folder.get("is_protected")),
                document_like=document_like(filename, url, content_type),
                lead_only_hint=any(marker in hint_text for marker in SLIDE_MARKERS) or attachment_extension(filename, url) in {".ppt", ".pptx", ".odp"}
            )

    materials = owner.get("material") if isinstance(owner.get("material"), list) else []
    for material in materials:
        if not isinstance(material, dict):
            continue
        folder_id = str(material.get("id", ""))
        folder_title = scalar_text(material.get("title"))
        for resource in material.get("resources") or []:
            if not isinstance(resource, dict):
                continue
            url = str(resource.get("url") or "").strip()
            attachment_id = str(resource.get("id", ""))
            key = url or f"{association_type}:{event_id}:{contribution_id}:{folder_id}:{attachment_id}"
            if not url or key in seen:
                continue
            seen.add(key)
            filename = str(resource.get("fileName") or resource.get("name") or Path(urlsplit(url).path).name)
            content_type = str(resource.get("content_type") or mimetypes.guess_type(filename)[0] or "")
            title = scalar_text(resource.get("name"))
            description = scalar_text(resource.get("description"))
            hint_text = f"{folder_title} {title} {filename}".casefold()
            yield Attachment(
                key=key, association_type=association_type, event_id=event_id, contribution_id=contribution_id,
                folder_id=folder_id, folder_title=folder_title, attachment_id=attachment_id, title=title,
                description=description, filename=filename, content_type=content_type, size=None, url=safe_url(url),
                protected=bool(resource.get("is_protected")), document_like=document_like(filename, url, content_type),
                lead_only_hint=any(marker in hint_text for marker in SLIDE_MARKERS) or attachment_extension(filename, url) in {".ppt", ".pptx", ".odp"}
            )


def material_metadata(attachments: Iterable[Attachment]) -> str:
    return " ".join(
        f"{item.folder_title} {item.title} {item.description} {item.filename} {item.content_type}"
        for item in attachments
    )


def metadata_fields(event: dict[str, Any], contribution: dict[str, Any] | None, attachments: list[Attachment]) -> dict[str, str]:
    fields = {
        "event.title": scalar_text(event.get("title")),
        "event.description": scalar_text(event.get("description")),
        "event.category": scalar_text(event.get("category")),
        "event.label": scalar_text(event.get("label")),
        "event.keywords": scalar_text(event.get("keywords")),
        "event.type": scalar_text(event.get("type")),
        "event.material_metadata": material_metadata([item for item in attachments if item.association_type == "event"]),
    }
    if contribution is not None:
        participants = []
        for key in ("primaryauthors", "coauthors", "speakers"):
            if isinstance(contribution.get(key), list):
                participants.extend(item for item in contribution[key] if isinstance(item, dict))
        fields.update({
            "contribution.title": scalar_text(contribution.get("title")),
            "contribution.description": scalar_text(contribution.get("description")),
            "contribution.keywords": scalar_text(contribution.get("keywords")),
            "contribution.session": scalar_text(contribution.get("session")),
            "contribution.track": scalar_text(contribution.get("track")),
            "contribution.type": scalar_text(contribution.get("type")),
            "contribution.code": scalar_text(contribution.get("code")),
            "contribution.author_names": " ".join(scalar_text(item.get("fullName") or f"{item.get('first_name', '')} {item.get('last_name', '')}") for item in participants),
            "contribution.author_affiliations": " ".join(scalar_text(item.get("affiliation")) for item in participants),
            "contribution.material_metadata": material_metadata([item for item in attachments if item.association_type == "contribution"]),
        })
    return fields


def download_attachment(session: requests.Session, attachment: Attachment, destination: Path, timeout: float, retries: int, delay: float) -> dict[str, Any]:
    if attachment.protected:
        return {"status": "inaccessible_protected", "retrieved": False}
    destination.parent.mkdir(parents=True, exist_ok=True)
    events: list[dict[str, Any]] = []
    for attempt in range(retries + 1):
        response: requests.Response | None = None
        try:
            response = session.get(attachment.url, timeout=timeout, stream=True, allow_redirects=True)
        except requests.RequestException as error:
            if attempt >= retries:
                return {"status": "network_failure", "retrieved": False, "error_type": type(error).__name__, "retry_events": events}
            wait = min(30.0, delay * (2**attempt)); events.append({"attempt": attempt + 1, "event": "network_error", "wait": wait}); time.sleep(wait); continue
        if response.status_code in RETRYABLE and attempt < retries:
            wait = min(30.0, delay * (2**attempt)); events.append({"attempt": attempt + 1, "event": f"http_{response.status_code}", "wait": wait}); time.sleep(wait); continue
        if response.status_code >= 400:
            return {"status": f"http_{response.status_code}", "retrieved": False, "retry_events": events}
        content_type = response.headers.get("Content-Type", attachment.content_type).split(";", 1)[0]
        with tempfile.NamedTemporaryFile("wb", dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp", delete=False) as target:
            temporary = Path(target.name)
            digest = hashlib.sha256(); size = 0
            try:
                for block in response.iter_content(1024 * 1024):
                    if block:
                        target.write(block); digest.update(block); size += len(block)
            except requests.RequestException as error:
                temporary.unlink(missing_ok=True)
                return {"status": "stream_failure", "retrieved": False, "error_type": type(error).__name__, "retry_events": events}
        temporary.replace(destination)
        return {"status": "retrieved", "retrieved": True, "path": str(destination), "bytes": size, "sha256": digest.hexdigest(), "content_type": content_type, "final_url": safe_url(response.url), "retry_events": events}
    return {"status": "network_failure", "retrieved": False, "retry_events": events}


def decode_text_bytes(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def extract_zip_xml(path: Path) -> str:
    parts: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.endswith(".xml") and (
                name.startswith(("word/", "ppt/slides/", "xl/sharedStrings", "xl/worksheets/"))
                or name in {"content.xml"}
            )
        )
        for name in names:
            try:
                root = ET.fromstring(archive.read(name))
            except (ET.ParseError, KeyError):
                continue
            parts.extend(text.strip() for text in root.itertext() if text and text.strip())
    return " ".join(parts)


def tool_version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
        return (result.stdout or result.stderr).strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError, IndexError):
        return "unavailable"


def extract_text(path: Path, attachment: Attachment) -> tuple[str, dict[str, Any]]:
    extension = attachment_extension(attachment.filename, attachment.url) or path.suffix.casefold()
    try:
        if extension == ".pdf" or attachment.content_type.casefold().startswith("application/pdf"):
            pdftotext = shutil.which("pdftotext")
            if not pdftotext:
                return "", {"status": "unparseable", "reason": "pdftotext_unavailable"}
            result = subprocess.run([pdftotext, "-enc", "UTF-8", str(path), "-"], capture_output=True, timeout=180, check=False)
            if result.returncode != 0:
                return "", {"status": "unparseable", "reason": "pdftotext_failed", "returncode": result.returncode}
            text = result.stdout.decode("utf-8", errors="replace")
            return text, {"status": "parsed" if normalize_text(text) else "unparseable", "extractor": "pdftotext"}
        if extension in {".docx", ".pptx", ".xlsx", ".odt", ".odp", ".ods"}:
            text = extract_zip_xml(path)
            return text, {"status": "parsed" if normalize_text(text) else "unparseable", "extractor": "zip_xml"}
        if extension in {".doc", ".ppt", ".xls", ".rtf"} and shutil.which("textutil"):
            result = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)], capture_output=True, timeout=180, check=False)
            text = result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""
            return text, {"status": "parsed" if normalize_text(text) else "unparseable", "extractor": "textutil", "returncode": result.returncode}
        raw = path.read_bytes()
        text = decode_text_bytes(raw)
        return text, {"status": "parsed" if normalize_text(text) else "unparseable", "extractor": "text_decode"}
    except (OSError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        return "", {"status": "unparseable", "reason": type(error).__name__}


def concise_match(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "concepts_present": result["concepts_present"],
        "concept_term_ids": result["concept_term_ids"],
        "stream_a": result["stream_a"],
        "stream_b": result["stream_b"],
        "stream_b_core": result["stream_b_core"],
        "stream_b_g": result["stream_b_g"],
        "stream_b_c1": result["stream_b_c1"],
        "stream_b_genericity": result["stream_b_genericity"],
        "stream_b_genericity_relation_qualified": result["stream_b_genericity_relation_qualified"],
        "stream_b_tailoring_tag": result["stream_b_tailoring_tag"],
        "g_eps_explicit": result["g_eps_explicit"],
        "c1_eps_explicit": result["c1_eps_explicit"],
        "genericity_eps_explicit": result["genericity_eps_explicit"],
        "genericity_artifact_matches": result["genericity_artifact_matches"],
        "active_genericity_artifact_ids": result["active_genericity_artifact_ids"],
        "active_g_artifact_ids": result["active_g_artifact_ids"],
        "active_c1_artifact_ids": result["active_c1_artifact_ids"],
        "relation_qualified_genericity_artifact_ids": result["relation_qualified_genericity_artifact_ids"],
        "field_hits": result["field_hits"],
    }


def manifest(directory: Path) -> dict[str, Any]:
    files = sorted(path for path in directory.rglob("*") if path.is_file() and path.name != "manifest.json")
    return {"generated_at_utc": utc_now(), "files": [{"path": str(path.relative_to(directory)), "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in files]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Whole-instance ESA Indico attachment-first deterministic matcher")
    parser.add_argument("--dictionary", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--date-start", default="2011-01-01")
    parser.add_argument("--date-end", required=True, help="inclusive source-harvest date, YYYY-MM-DD")
    parser.add_argument("--classification", choices=("pilot_not_candidate_search", "final_run"), default="pilot_not_candidate_search")
    parser.add_argument("--event-workers", type=int, default=8)
    parser.add_argument("--attachment-workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--backoff-seconds", type=float, default=1.0)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir.expanduser().resolve()
    try:
        start = date.fromisoformat(args.date_start); end = date.fromisoformat(args.date_end)
        if start > end:
            raise HarvestError("date-start is after date-end")
        if args.event_workers < 1 or args.attachment_workers < 1 or args.timeout <= 0 or args.retries < 0:
            raise HarvestError("worker, timeout, or retry values are invalid")
        if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
            raise HarvestError(f"output directory is not empty: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True); os.chmod(output_dir, 0o700)
        dictionary_path = args.dictionary.expanduser().resolve(); fixture_path = args.fixtures.expanduser().resolve()
        matcher = ConceptMatcher.from_path(dictionary_path)
        fixture_report = run_fixtures(matcher, fixture_path)
        if fixture_report["status"] != "passed":
            raise HarvestError("synthetic matcher regression failed; harvest prohibited")
        atomic_write_json(output_dir / "matcher-regression.json", fixture_report)
        metadata = {
            "status": "running", "classification": args.classification,
            "screening_prohibited": args.classification == "pilot_not_candidate_search",
            "started_at_utc": utc_now(), "date_start": str(start), "date_end": str(end),
            "dictionary_sha256": sha256_file(dictionary_path), "matcher_sha256": sha256_file(Path(__file__).with_name("concept_matcher.py")),
            "harvester_sha256": sha256_file(Path(__file__).resolve()), "fixtures_sha256": sha256_file(fixture_path),
            "runtime": {"python": sys.version, "requests": requests.__version__, "pdftotext": tool_version(["pdftotext", "-v"]), "textutil": tool_version(["textutil", "-help"])},
            "candidate_policy": "No pilot record may be screened or used as evidence. Materials are inventoried before core P/M or relation-free complete G/C1 gating; R/T are separate tags."
        }
        atomic_write_json(output_dir / "run-metadata.json", metadata)
        session = requests.Session(); session.headers.update({"Accept": "application/json", "User-Agent": "eps-mbse-slr-2026-esa-census/1.0"})

        root_payload, root_info = response_json(session, ROOT_URL, args.timeout, args.retries, args.backoff_seconds)
        (output_dir / "raw" / "categories").mkdir(parents=True, exist_ok=True)
        (output_dir / "raw" / "categories" / "0.json").write_bytes(root_info.pop("raw_bytes"))
        root_events = parse_event_list(root_payload)
        child_sets: dict[str, set[str]] = {}; child_info: dict[str, Any] = {}
        for category_id in CHILD_CATEGORY_IDS:
            payload, info = response_json(session, CATEGORY_URL.format(category_id=category_id), args.timeout, args.retries, args.backoff_seconds)
            (output_dir / "raw" / "categories" / f"{category_id}.json").write_bytes(info.pop("raw_bytes"))
            events = parse_event_list(payload); child_sets[str(category_id)] = {str(item.get("id")) for item in events}; child_info[str(category_id)] = info | {"returned_events": len(events)}
        root_by_id = {str(item.get("id")): item for item in root_events if str(item.get("id", ""))}
        root_ids = set(root_by_id); top_union = child_sets.get("5", set()) | child_sets.get("6", set()) | child_sets.get("7", set())
        category_reconciliation = {
            "root_reported_count": root_payload.get("count"), "root_returned": len(root_events), "root_unique_ids": len(root_ids),
            "top_level_union_unique_ids": len(top_union), "root_equals_top_level_union": root_ids == top_union,
            "root_only_ids": sorted(root_ids - top_union), "top_level_only_ids": sorted(top_union - root_ids),
            "category_9_subset_of_6": child_sets.get("9", set()).issubset(child_sets.get("6", set())),
            "root_request": root_info, "child_requests": child_info
        }
        atomic_write_json(output_dir / "category-reconciliation.json", category_reconciliation)
        in_window: list[dict[str, Any]] = []; missing_dates: list[str] = []
        for event_id, event in sorted(root_by_id.items(), key=lambda item: int(item[0]) if item[0].isdigit() else item[0]):
            parsed_date = event_date(event)
            if parsed_date is None:
                missing_dates.append(event_id)
            elif start <= parsed_date <= end:
                in_window.append(event)

        event_raw_dir = output_dir / "raw" / "events"; event_raw_dir.mkdir(parents=True, exist_ok=True)
        event_exports: dict[str, dict[str, Any]] = {}; event_failures: dict[str, dict[str, Any]] = {}
        def fetch_event(event: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
            event_id = str(event["id"]); local_session = requests.Session(); local_session.headers.update(session.headers)
            payload, info = response_json(local_session, EVENT_URL.format(event_id=event_id), args.timeout, args.retries, args.backoff_seconds)
            return event_id, payload, info
        with ThreadPoolExecutor(max_workers=args.event_workers) as executor:
            futures = {executor.submit(fetch_event, event): str(event["id"]) for event in in_window}
            for future in as_completed(futures):
                event_id = futures[future]
                try:
                    returned_id, payload, info = future.result(); raw = info.pop("raw_bytes"); (event_raw_dir / f"{returned_id}.json").write_bytes(raw)
                    results = payload.get("results")
                    if not isinstance(results, list) or len(results) != 1 or not isinstance(results[0], dict):
                        raise HarvestError("event export did not contain exactly one event object")
                    contributions = results[0].get("contributions")
                    if not isinstance(contributions, list) or any(not isinstance(item, dict) for item in contributions):
                        raise HarvestError("event export lacked a contribution array")
                    event_exports[returned_id] = {"event": results[0], "info": info, "contributions": contributions}
                except Exception as error:  # retain each source coverage failure and continue census
                    event_failures[event_id] = {"error_type": type(error).__name__, "reason": str(error), "at_utc": utc_now()}

        subjects: list[dict[str, Any]] = []; all_attachments: list[Attachment] = []
        for event_id, export in sorted(event_exports.items(), key=lambda item: int(item[0]) if item[0].isdigit() else item[0]):
            event = export["event"]
            event_attachments = list(iter_materials(event, "event", event_id, None)); all_attachments.extend(event_attachments)
            if event_attachments:
                subjects.append({
                    "subject_id": f"event:{event_id}", "event_id": event_id, "contribution_id": None,
                    "event": event, "contribution": None, "metadata_attachments": event_attachments,
                    "route_attachments": event_attachments,
                })
            for contribution in export["contributions"]:
                contribution_id = str(contribution.get("db_id") or contribution.get("id") or "")
                attachments = list(iter_materials(contribution, "contribution", event_id, contribution_id)); all_attachments.extend(attachments)
                subjects.append({
                    "subject_id": f"event:{event_id}:contribution:{contribution_id}", "event_id": event_id,
                    "contribution_id": contribution_id, "event": event, "contribution": contribution,
                    "metadata_attachments": event_attachments + attachments,
                    "route_attachments": attachments,
                })

        inventory = [asdict(item) for item in all_attachments]
        atomic_write_json(output_dir / "material-inventory.json", {"count": len(inventory), "attachments": inventory})
        unique_downloads: dict[str, Attachment] = {}
        for attachment in all_attachments:
            if attachment.document_like:
                unique_downloads.setdefault(attachment.url, attachment)
        attachment_dir = output_dir / "raw" / "attachments"; extraction_dir = output_dir / "derived" / "attachment-text"
        download_results: dict[str, dict[str, Any]] = {}
        def retrieve(item: Attachment) -> tuple[str, dict[str, Any]]:
            extension = attachment_extension(item.filename, item.url)
            filename = safe_name(item.filename, f"attachment-{item.attachment_id}{extension}")
            destination = attachment_dir / item.event_id / (item.contribution_id or "event") / f"{safe_name(item.attachment_id, 'unknown')}-{filename}"
            local_session = requests.Session(); local_session.headers.update({"User-Agent": session.headers["User-Agent"], "Accept": "*/*"})
            result = download_attachment(local_session, item, destination, args.timeout, args.retries, args.backoff_seconds)
            if result.get("retrieved"):
                text, extraction = extract_text(destination, item); normalized = normalize_text(text)
                extraction_path = extraction_dir / f"{sha256_bytes(item.url.encode('utf-8'))}.txt"
                if normalized:
                    extraction_path.parent.mkdir(parents=True, exist_ok=True); extraction_path.write_text(normalized + "\n", encoding="utf-8")
                    extraction["text_path"] = str(extraction_path); extraction["text_sha256"] = sha256_file(extraction_path); extraction["normalized_characters"] = len(normalized)
                result["extraction"] = extraction
            return item.url, result
        with ThreadPoolExecutor(max_workers=args.attachment_workers) as executor:
            futures = {executor.submit(retrieve, item): url for url, item in unique_downloads.items()}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    returned_url, result = future.result(); download_results[returned_url] = result
                except Exception as error:
                    download_results[url] = {"status": "processing_failure", "retrieved": False, "error_type": type(error).__name__, "reason": str(error)}
        atomic_write_json(output_dir / "attachment-coverage.json", {"unique_document_like_urls": len(unique_downloads), "results": download_results})

        subject_matches: list[dict[str, Any]] = []
        for subject in subjects:
            fields = metadata_fields(subject["event"], subject["contribution"], subject["metadata_attachments"])
            metadata_match = matcher.match_fields(fields)
            attachment_matches: list[dict[str, Any]] = []
            # Event-level files are matched once as event-material subjects. A contribution's
            # attachment route contains only files actually associated with that contribution;
            # event material metadata may still appear in the joined-metadata route.
            association_urls = {item.url for item in subject["route_attachments"] if item.document_like}
            for url in sorted(association_urls):
                coverage = download_results.get(url, {})
                extraction = coverage.get("extraction") if isinstance(coverage, dict) else None
                text_path = extraction.get("text_path") if isinstance(extraction, dict) else None
                if not text_path:
                    continue
                text = Path(text_path).read_text(encoding="utf-8")
                matched = matcher.match_fields({"attachment.extracted_text": text})
                attachment_matches.append({"url_sha256": sha256_bytes(url.encode("utf-8")), "match": concise_match(matched)})
            attachment_b = any(item["match"]["stream_b"] for item in attachment_matches)
            attachment_b_core = any(item["match"]["stream_b_core"] for item in attachment_matches)
            attachment_b_g = any(item["match"]["stream_b_g"] for item in attachment_matches)
            attachment_b_c1 = any(item["match"]["stream_b_c1"] for item in attachment_matches)
            attachment_b_genericity = any(item["match"]["stream_b_genericity"] for item in attachment_matches)
            attachment_b_genericity_relation = any(
                item["match"]["stream_b_genericity_relation_qualified"] for item in attachment_matches
            )
            attachment_tailoring = any(item["match"]["stream_b_tailoring_tag"] for item in attachment_matches)
            attachment_a = any(item["match"]["stream_a"] for item in attachment_matches)
            attachment_g_eps = any(item["match"]["g_eps_explicit"] for item in attachment_matches)
            attachment_c1_eps = any(item["match"]["c1_eps_explicit"] for item in attachment_matches)
            attachment_genericity_eps = any(item["match"]["genericity_eps_explicit"] for item in attachment_matches)
            stream_b_core = metadata_match["stream_b_core"] or attachment_b_core
            stream_b_g = metadata_match["stream_b_g"] or attachment_b_g
            stream_b_c1 = metadata_match["stream_b_c1"] or attachment_b_c1
            stream_b_genericity = stream_b_g or stream_b_c1
            stream_b_genericity_relation = (
                metadata_match["stream_b_genericity_relation_qualified"] or attachment_b_genericity_relation
            )
            stream_b = stream_b_core or stream_b_genericity
            stream_a = metadata_match["stream_a"] or attachment_a
            g_eps_explicit = metadata_match["g_eps_explicit"] or attachment_g_eps
            c1_eps_explicit = metadata_match["c1_eps_explicit"] or attachment_c1_eps
            genericity_eps_explicit = metadata_match["genericity_eps_explicit"] or attachment_genericity_eps
            tailoring_tag = metadata_match["stream_b_tailoring_tag"] or attachment_tailoring
            subject_matches.append({
                "subject_id": subject["subject_id"], "event_id": subject["event_id"], "contribution_id": subject["contribution_id"],
                "metadata_match": concise_match(metadata_match), "attachment_matches": attachment_matches,
                "stream_a": stream_a, "stream_b": stream_b,
                "stream_b_core": stream_b_core, "stream_b_g": stream_b_g, "stream_b_c1": stream_b_c1,
                "stream_b_genericity": stream_b_genericity,
                "stream_b_genericity_relation_qualified": stream_b_genericity_relation,
                "stream_b_tailoring_tag": tailoring_tag,
                "g_eps_explicit": g_eps_explicit, "c1_eps_explicit": c1_eps_explicit,
                "genericity_eps_explicit": genericity_eps_explicit,
                "routes": {
                    "joined_metadata": metadata_match["stream_b"], "attachment_text": attachment_b,
                    "joined_metadata_core": metadata_match["stream_b_core"], "attachment_text_core": attachment_b_core,
                    "joined_metadata_g": metadata_match["stream_b_g"], "attachment_text_g": attachment_b_g,
                    "joined_metadata_c1": metadata_match["stream_b_c1"], "attachment_text_c1": attachment_b_c1,
                    "joined_metadata_genericity": metadata_match["stream_b_genericity"],
                    "attachment_text_genericity": attachment_b_genericity,
                    "joined_metadata_genericity_relation_qualified": metadata_match[
                        "stream_b_genericity_relation_qualified"
                    ],
                    "attachment_text_genericity_relation_qualified": attachment_b_genericity_relation,
                    "joined_metadata_tailoring_tag": metadata_match["stream_b_tailoring_tag"],
                    "attachment_text_tailoring_tag": attachment_tailoring,
                }
            })
        atomic_write_json(output_dir / "match-results.json", {"subjects": subject_matches})

        b_subjects = [item for item in subject_matches if item["stream_b"]]; a_subjects = [item for item in subject_matches if item["stream_a"]]
        g_eps_subjects = {item["subject_id"] for item in subject_matches if item["g_eps_explicit"]}
        c1_eps_subjects = {item["subject_id"] for item in subject_matches if item["c1_eps_explicit"]}
        genericity_eps_subjects = {item["subject_id"] for item in subject_matches if item["genericity_eps_explicit"]}
        core_b_subjects = {item["subject_id"] for item in subject_matches if item["stream_b_core"]}
        g_b_subjects = {item["subject_id"] for item in subject_matches if item["stream_b_g"]}
        c1_b_subjects = {item["subject_id"] for item in subject_matches if item["stream_b_c1"]}
        genericity_b_subjects = {item["subject_id"] for item in subject_matches if item["stream_b_genericity"]}
        relation_qualified_g_subjects = {
            item["subject_id"] for item in subject_matches if item["stream_b_genericity_relation_qualified"]
        }
        tailoring_subjects = {item["subject_id"] for item in subject_matches if item["stream_b_tailoring_tag"]}
        metadata_b = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata"]}
        attachment_b = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text"]}
        metadata_g = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata_g"]}
        attachment_g = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text_g"]}
        metadata_c1 = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata_c1"]}
        attachment_c1 = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text_c1"]}
        retrieved = sum(1 for item in download_results.values() if item.get("retrieved")); parsed = sum(1 for item in download_results.values() if item.get("extraction", {}).get("status") == "parsed")
        summary = {
            "status": "success_with_coverage_failures" if event_failures or retrieved < len(unique_downloads) or parsed < retrieved else "success",
            "classification": args.classification, "screening_prohibited": args.classification == "pilot_not_candidate_search",
            "completed_at_utc": utc_now(), "root_events_returned": len(root_events), "root_unique_events": len(root_ids),
            "events_missing_or_unparseable_date": len(missing_dates), "in_window_events": len(in_window),
            "contribution_exports_attempted": len(in_window), "contribution_exports_retrieved": len(event_exports),
            "contribution_exports_failed": len(event_failures), "contributions_parsed": sum(len(item["contributions"]) for item in event_exports.values()),
            "material_attachments_inventoried": len(all_attachments), "unique_document_like_attachments": len(unique_downloads),
            "document_like_retrieved": retrieved, "document_like_inaccessible_or_failed": len(unique_downloads) - retrieved,
            "document_like_text_parsed": parsed, "document_like_unparseable": retrieved - parsed,
            "subjects_matched": len(subject_matches), "stream_a_eps_explicit_tag": len(a_subjects), "stream_b_union": len(b_subjects),
            "g_eps_explicit_tag": len(g_eps_subjects), "c1_eps_explicit_tag": len(c1_eps_subjects),
            "genericity_eps_explicit_tag": len(genericity_eps_subjects),
            "stream_b_core": len(core_b_subjects), "stream_b_g": len(g_b_subjects),
            "stream_b_c1": len(c1_b_subjects), "stream_b_genericity": len(genericity_b_subjects),
            "stream_b_genericity_relation_qualified": len(relation_qualified_g_subjects),
            "stream_b_tailoring_tag": len(tailoring_subjects),
            "core_intersection_g": len(core_b_subjects & g_b_subjects),
            "core_intersection_c1": len(core_b_subjects & c1_b_subjects),
            "g_intersection_c1": len(g_b_subjects & c1_b_subjects),
            "core_intersection_genericity": len(core_b_subjects & genericity_b_subjects),
            "core_only": len(core_b_subjects - genericity_b_subjects),
            "g_only_vs_core_c1": len(g_b_subjects - core_b_subjects - c1_b_subjects),
            "c1_only_vs_core_g": len(c1_b_subjects - core_b_subjects - g_b_subjects),
            "genericity_only": len(genericity_b_subjects - core_b_subjects),
            "a_intersection_b": len({item['subject_id'] for item in a_subjects} & {item['subject_id'] for item in b_subjects}),
            "a_only_structural_error": len({item['subject_id'] for item in a_subjects} - {item['subject_id'] for item in b_subjects}),
            "b_only": len({item['subject_id'] for item in b_subjects} - {item['subject_id'] for item in a_subjects}),
            "metadata_route_b": len(metadata_b), "attachment_route_b": len(attachment_b),
            "metadata_and_attachment_route_b": len(metadata_b & attachment_b), "metadata_only_route_b": len(metadata_b - attachment_b),
            "attachment_only_route_b": len(attachment_b - metadata_b),
            "metadata_route_g": len(metadata_g), "attachment_route_g": len(attachment_g),
            "metadata_and_attachment_route_g": len(metadata_g & attachment_g),
            "metadata_route_c1": len(metadata_c1), "attachment_route_c1": len(attachment_c1),
            "metadata_and_attachment_route_c1": len(metadata_c1 & attachment_c1),
            "coverage_event_ids_present": {event_id: event_id in root_ids for event_id in ("161", "329", "386", "407", "472")},
            "category_reconciliation": {key: category_reconciliation[key] for key in ("root_equals_top_level_union", "category_9_subset_of_6")},
            "event_export_failures": event_failures, "missing_date_event_ids": missing_dates,
            "dictionary_sha256": metadata["dictionary_sha256"], "matcher_sha256": metadata["matcher_sha256"], "harvester_sha256": metadata["harvester_sha256"]
        }
        if summary["a_only_structural_error"]:
            raise HarvestError("Stream A was not a subset of Stream B")
        atomic_write_json(output_dir / "dry-run-summary.json", summary)
        metadata.update({"status": summary["status"], "completed_at_utc": utc_now()}); atomic_write_json(output_dir / "run-metadata.json", metadata)
        atomic_write_json(output_dir / "manifest.json", manifest(output_dir))
        print(json.dumps(summary, indent=2, ensure_ascii=False)); return 0
    except (HarvestError, MatcherError, ValueError) as error:
        output_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(output_dir / "failure.json", {"status": "failure", "classification": args.classification, "screening_prohibited": args.classification == "pilot_not_candidate_search", "error_type": type(error).__name__, "reason": str(error), "at_utc": utc_now()})
        print(json.dumps({"status": "failure", "error": str(error)}, ensure_ascii=False), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
