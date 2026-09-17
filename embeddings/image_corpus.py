"""Build metadata for every image referenced by an included report."""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable


IMAGE_RE = re.compile(r"!\[([^]]*)]\(([^)]+)\)")
PAGE_RE = re.compile(r"<!--\s*PDF_PAGE:\s*([1-9][0-9]*)\s*-->")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SPACE_RE = re.compile(r"\s+")
HTML_RE = re.compile(r"<[^>]+>")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFC", html.unescape(value))
    value = IMAGE_RE.sub(" ", value)
    value = HTML_RE.sub(" ", value)
    value = value.replace("\u00ad", "")
    return SPACE_RE.sub(" ", value).strip(" #*`|-")


def normalize_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def resolve_report_image(
    repository_root: Path, source_path: Path, image_ref: str
) -> Path:
    """Resolve one local Markdown image reference inside the repository."""
    reference = image_ref.strip().strip("<>")
    if not reference or "://" in reference or reference.startswith("data:"):
        raise ValueError(f"Image reference is not a local file: {image_ref}")
    candidate = (source_path.parent / reference).resolve()
    try:
        candidate.relative_to(repository_root.resolve())
    except (OSError, ValueError) as error:
        raise ValueError(
            f"Image reference leaves the repository: {image_ref}"
        ) from error
    if not candidate.is_file() or candidate.suffix.casefold() not in IMAGE_SUFFIXES:
        raise FileNotFoundError(
            f"Referenced image is missing or unsupported: {candidate}"
        )
    return candidate


def stable_image_id(report_id: str, source_image: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", Path(source_image).stem.casefold()).strip("-")
    digest = hashlib.sha1(source_image.encode("utf-8")).hexdigest()[:10]
    return f"{report_id}--image-{stem}-{digest}"


def scan_markdown_images(markdown: str) -> list[dict[str, Any]]:
    """Return image mentions with their page, section, and page text."""
    headings: list[tuple[int, str]] = []
    current_page: int | None = None
    mentions: list[dict[str, Any]] = []
    page_text: dict[int | None, list[str]] = {}

    for line in markdown.splitlines():
        page_match = PAGE_RE.search(line)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            level = len(heading_match.group(1))
            heading = clean_text(heading_match.group(2).strip("# "))
            while headings and headings[-1][0] >= level:
                headings.pop()
            if heading:
                headings.append((level, heading))
            continue

        section = " > ".join(name for _, name in headings) or "Document"
        for match in IMAGE_RE.finditer(line):
            mentions.append(
                {
                    "image_ref": match.group(2).strip(),
                    "alt_text": clean_text(match.group(1)),
                    "page_start": current_page,
                    "page_end": current_page,
                    "section": section,
                    "section_key": normalize_key(section) or "document",
                }
            )

        text = clean_text(line)
        if text and not text.startswith("---"):
            page_text.setdefault(current_page, []).append(text)

    rendered_page_text = {
        page: " ".join(parts)[:1600] for page, parts in page_text.items()
    }
    for mention in mentions:
        mention["page_context"] = rendered_page_text.get(mention["page_start"], "")
    return mentions


def useful_alt_text(alt_text: str, image_ref: str) -> str:
    normalized_alt = normalize_key(alt_text)
    normalized_name = normalize_key(Path(image_ref).name)
    normalized_stem = normalize_key(Path(image_ref).stem)
    if normalized_alt in {"", normalized_name, normalized_stem}:
        return ""
    return alt_text


def diagram_metadata(analyses: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for row in analyses:
        analysis = row.get("analysis")
        if (
            row.get("status") != "ok"
            or not isinstance(analysis, dict)
            or analysis.get("contains_target_diagram") is not True
        ):
            continue
        source_image = row.get("source_image")
        if not isinstance(source_image, str) or not source_image:
            continue
        metadata[source_image] = {
            "diagram_id": row.get("diagram_id"),
            "modeling_language": analysis.get("modeling_language"),
            "representation_type": analysis.get("representation_type"),
            "visual_summary": analysis.get("summary"),
        }
    return metadata


def build_image_records(
    reports: Iterable[dict[str, Any]],
    units: Iterable[dict[str, Any]],
    analyses: Iterable[dict[str, Any]],
    repository_root: Path,
) -> list[dict[str, Any]]:
    """Build deterministic metadata for all report images, including diagrams."""
    repository_root = repository_root.resolve()
    units = list(units)
    unit_lookup = {unit["unit_id"]: unit for unit in units}
    caption_by_ref: dict[tuple[str, str], dict[str, Any]] = {}
    for unit in units:
        for image_ref in unit.get("image_refs", []):
            caption_by_ref[(unit["report_id"], image_ref)] = unit
    diagrams = diagram_metadata(analyses)

    records: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for report in reports:
        source_path = (repository_root / report["source_path"]).resolve()
        markdown = source_path.read_text(encoding="utf-8", errors="replace")
        for mention in scan_markdown_images(markdown):
            image_ref = mention["image_ref"]
            image_path = resolve_report_image(repository_root, source_path, image_ref)
            source_image = image_path.relative_to(repository_root).as_posix()
            if source_image in seen_paths:
                raise ValueError(f"Image is referenced more than once: {source_image}")
            seen_paths.add(source_image)

            caption_unit = caption_by_ref.get((report["report_id"], image_ref))
            context = ""
            if caption_unit is not None:
                context_parts = [
                    unit_lookup[unit_id]["text"]
                    for unit_id in caption_unit.get("context_unit_ids", [])
                    if unit_id in unit_lookup
                ]
                context = " ".join(context_parts)[:1600]

            caption = (
                caption_unit["text"]
                if caption_unit is not None
                else useful_alt_text(mention["alt_text"], image_ref)
            )
            image_details = diagrams.get(source_image, {})
            record = {
                "image_id": stable_image_id(report["report_id"], source_image),
                "report_id": report["report_id"],
                "screening_record_id": report.get("screening_record_id"),
                "title": report["title"],
                "year": report.get("publication_year"),
                "source_path": report["source_path"],
                "source_image": source_image,
                "source_image_sha256": file_sha256(image_path),
                "image_ref": image_ref,
                "page_start": (
                    caption_unit.get("page_start")
                    if caption_unit is not None
                    else mention["page_start"]
                ),
                "page_end": (
                    caption_unit.get("page_end")
                    if caption_unit is not None
                    else mention["page_end"]
                ),
                "section": (
                    caption_unit.get("section")
                    if caption_unit is not None
                    else mention["section"]
                ),
                "section_key": (
                    caption_unit.get("section_key")
                    if caption_unit is not None
                    else mention["section_key"]
                ),
                "caption": caption,
                "nearby_context": context or mention["page_context"],
                "is_mbse_diagram": bool(image_details),
                **image_details,
            }
            records.append(record)
    return records


def image_search_text(record: dict[str, Any]) -> str:
    """Render image metadata as text for reranking and result display."""
    parts = [
        f"Document: {record['title']}",
        f"Section: {record.get('section') or 'Document'}",
    ]
    if record.get("caption"):
        parts.append(f"Image caption: {record['caption']}")
    if record.get("visual_summary"):
        parts.append(f"Visual analysis: {record['visual_summary']}")
    if record.get("representation_type"):
        parts.append(f"Representation type: {record['representation_type']}")
    if record.get("modeling_language"):
        parts.append(f"Modeling language: {record['modeling_language']}")
    if record.get("nearby_context"):
        parts.append(f"Nearby context: {record['nearby_context']}")
    return "\n".join(parts)
