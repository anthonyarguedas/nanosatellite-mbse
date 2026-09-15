#!/usr/bin/env python3
"""Build a structure aware retrieval corpus from directly included SLR reports."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Iterator


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
PAGE_RE = re.compile(r"<!--\s*PDF_PAGE:\s*([1-9][0-9]*)\s*-->")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^]]*)]\(([^)]+)\)")
LINK_RE = re.compile(r"\[([^]]+)]\((?:[^()]+|\([^)]*\))+\)")
CAPTION_RE = re.compile(
    r"^(?:fig(?:ure)?\.?|table|chart|diagram|listing)\s*[-.:]?\s*(?:[A-Z]?\d+|[IVXLCDM]+)\b",
    re.IGNORECASE,
)
REFERENCE_HEADING_RE = re.compile(
    r"^(?:(?:\d+|[ivxlcdm]+)[.\s:-]+)?(?:references|bibliography|literature cited|works cited)$",
    re.IGNORECASE,
)
SPACE_RE = re.compile(r"\s+")
SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\[(])")
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")


@dataclass
class Unit:
    unit_id: str
    report_id: str
    text: str
    kind: str
    section: str
    section_key: str
    page_start: int | None
    page_end: int | None
    image_refs: list[str] = field(default_factory=list)
    context_unit_ids: list[str] = field(default_factory=list)


class TableHTMLParser(HTMLParser):
    """Extract rows and cells from Markdown embedded HTML tables."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.header_rows: set[int] = set()
        self._row: list[str] | None = None
        self._cell_parts: list[str] | None = None
        self._cell_is_header = False
        self._row_has_header = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "tr":
            self._row = []
            self._row_has_header = False
        elif tag in {"td", "th"} and self._row is not None:
            self._cell_parts = []
            self._cell_is_header = tag == "th"
        elif tag == "br" and self._cell_parts is not None:
            self._cell_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self._cell_parts is not None:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if (
            tag in {"td", "th"}
            and self._cell_parts is not None
            and self._row is not None
        ):
            self._row.append(clean_inline("".join(self._cell_parts)))
            self._row_has_header = self._row_has_header or self._cell_is_header
            self._cell_parts = None
            self._cell_is_header = False
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                if self._row_has_header:
                    self.header_rows.add(len(self.rows))
                self.rows.append(self._row)
            self._row = None


def jsonl_write(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(path)


def normalize_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def clean_inline(value: str) -> str:
    value = unicodedata.normalize("NFC", html.unescape(value))
    value = IMAGE_RE.sub(lambda match: match.group(1), value)
    value = LINK_RE.sub(lambda match: match.group(1), value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(
        r"</?(?:div|span|p|center|font|sub|sup|strong|em|b|i)(?:\s+[^>]*)?>",
        " ",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"<!--.*?-->", " ", value, flags=re.DOTALL)
    value = value.replace("\u00ad", "")
    value = SPACE_RE.sub(" ", value).strip()
    return value


def strip_frontmatter(markdown: str) -> str:
    if not markdown.startswith("---"):
        return markdown
    match = re.match(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", markdown, flags=re.DOTALL)
    return markdown[match.end() :] if match else markdown


def split_markdown_table(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            return []
        rows.append([clean_inline(cell) for cell in stripped[1:-1].split("|")])
    return rows


def likely_header(cells: list[str]) -> bool:
    header_terms = {
        "parameter",
        "variable",
        "function",
        "description",
        "method",
        "tool",
        "value",
        "unit",
        "requirement",
        "component",
        "subsystem",
        "attribute",
        "property",
        "name",
        "phase",
        "activity",
        "input",
        "output",
        "metric",
        "result",
        "risk",
        "failure mode",
        "symbol",
    }
    normalized = {normalize_key(cell) for cell in cells}
    return bool(normalized & header_terms)


def rows_to_table_texts(
    rows: list[list[str]], explicit_header: bool = False
) -> list[str]:
    if not rows:
        return []
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]

    separator_index = None
    if len(rows) > 1 and all(
        TABLE_SEPARATOR_RE.match(cell) for cell in rows[1] if cell
    ):
        separator_index = 1

    has_header = explicit_header or separator_index == 1 or likely_header(rows[0])
    if has_header:
        headers = [cell or f"Column {index + 1}" for index, cell in enumerate(rows[0])]
        data_rows = rows[2:] if separator_index == 1 else rows[1:]
    else:
        headers = [f"Column {index + 1}" for index in range(width)]
        data_rows = rows

    rendered: list[str] = []
    for row in data_rows:
        fields = [f"{header}: {value}" for header, value in zip(headers, row) if value]
        if fields:
            rendered.append("Table row. " + "; ".join(fields) + ".")
    return rendered


def extract_html_table_texts(text: str) -> list[str]:
    parser = TableHTMLParser()
    parser.feed(text)
    return rows_to_table_texts(
        parser.rows,
        explicit_header=bool(parser.header_rows and 0 in parser.header_rows),
    )


def classify_block(lines: list[str], text: str) -> str:
    if CAPTION_RE.match(text):
        return "caption"
    nonempty = [line for line in lines if line.strip()]
    if (
        nonempty
        and sum(bool(LIST_LINE_RE.match(line)) for line in nonempty)
        >= len(nonempty) / 2
    ):
        return "list"
    if re.search(r"\b(?:equation|where)\b", text, re.IGNORECASE) and "$" in text:
        return "equation"
    return "prose"


def parse_markdown(report_id: str, title: str, markdown: str) -> list[Unit]:
    markdown = strip_frontmatter(markdown)
    units: list[Unit] = []
    headings: list[tuple[int, str]] = []
    current_page: int | None = None
    block_lines: list[str] = []
    block_pages: list[int] = []
    pending_images: list[str] = []
    skip_level: int | None = None
    title_key = normalize_key(title)

    def section_values() -> tuple[str, str]:
        names = [name for _, name in headings]
        section = " > ".join(names) if names else "Document"
        key = " / ".join(normalize_key(name) for name in names) if names else "document"
        return section, key

    def append_unit(
        text: str, kind: str, pages: list[int], image_refs: list[str] | None = None
    ) -> None:
        text = clean_inline(text)
        if not text or len(normalize_key(text)) < 2:
            return
        section, section_key = section_values()
        unit = Unit(
            unit_id=f"{report_id}:unit-{len(units) + 1:05d}",
            report_id=report_id,
            text=text,
            kind=kind,
            section=section,
            section_key=section_key,
            page_start=min(pages) if pages else current_page,
            page_end=max(pages) if pages else current_page,
            image_refs=list(image_refs or []),
        )
        units.append(unit)

    def flush_block() -> None:
        nonlocal block_lines, block_pages, pending_images
        if not block_lines:
            return
        raw = "\n".join(block_lines).strip()
        pages = list(block_pages)
        original_lines = block_lines
        block_lines = []
        block_pages = []

        if skip_level is not None:
            return

        if "<table" in raw.casefold():
            for row_text in extract_html_table_texts(raw):
                append_unit(row_text, "table_row", pages)
            return

        markdown_rows = split_markdown_table(raw)
        if markdown_rows:
            for row_text in rows_to_table_texts(markdown_rows):
                append_unit(row_text, "table_row", pages)
            return

        text = clean_inline(raw)
        if not text:
            return
        kind = classify_block(original_lines, text)
        if kind == "caption" and not pending_images and len(text.split()) > 50:
            kind = "prose"
        image_refs = pending_images if kind == "caption" else []
        if image_refs:
            pending_images = []
        append_unit(text, kind, pages, image_refs)

    for line in markdown.splitlines():
        page_match = PAGE_RE.search(line)
        if page_match:
            flush_block()
            current_page = int(page_match.group(1))
            continue

        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            flush_block()
            level = len(heading_match.group(1))
            heading = clean_inline(heading_match.group(2).strip("# "))

            if skip_level is not None and level <= skip_level:
                skip_level = None
            while headings and headings[-1][0] >= level:
                headings.pop()

            heading_key = normalize_key(heading)
            if not headings and (
                heading_key == title_key
                or title_key in heading_key
                or heading_key in title_key
            ):
                continue
            headings.append((level, heading))
            if REFERENCE_HEADING_RE.match(heading):
                skip_level = level
            continue

        image_matches = list(IMAGE_RE.finditer(line))
        if image_matches and clean_inline(IMAGE_RE.sub("", line)) == "":
            flush_block()
            pending_images.extend(match.group(2) for match in image_matches)
            continue

        if not line.strip():
            flush_block()
            continue

        block_lines.append(line)
        if current_page is not None:
            block_pages.append(current_page)

    flush_block()
    attach_neighbor_context(units)
    return units


def attach_neighbor_context(units: list[Unit]) -> None:
    """Link captions and table rows to nearby prose without changing source text."""
    prose_kinds = {"prose", "list", "equation"}
    for index, unit in enumerate(units):
        if unit.kind not in {"caption", "table_row"}:
            continue
        candidates: list[tuple[int, Unit]] = []
        for neighbor_index in range(max(0, index - 2), min(len(units), index + 3)):
            neighbor = units[neighbor_index]
            if (
                neighbor.kind not in prose_kinds
                or neighbor.section_key != unit.section_key
            ):
                continue
            page_distance = 0
            if unit.page_start is not None and neighbor.page_start is not None:
                page_distance = abs(unit.page_start - neighbor.page_start)
            if page_distance <= 1:
                candidates.append((abs(index - neighbor_index), neighbor))
        if candidates:
            candidates.sort(key=lambda pair: pair[0])
            unit.context_unit_ids = [candidates[0][1].unit_id]


def split_long_text(text: str, max_words: int) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    sentences = [
        part.strip() for part in SENTENCE_BOUNDARY_RE.split(text) if part.strip()
    ]
    if len(sentences) == 1:
        return [
            " ".join(words[index : index + max_words])
            for index in range(0, len(words), max_words)
        ]
    parts: list[str] = []
    current: list[str] = []
    count = 0
    for sentence in sentences:
        sentence_words = sentence.split()
        if len(sentence_words) > max_words:
            if current:
                parts.append(" ".join(current))
                current = []
                count = 0
            parts.extend(
                " ".join(sentence_words[index : index + max_words])
                for index in range(0, len(sentence_words), max_words)
            )
            continue
        if current and count + len(sentence_words) > max_words:
            parts.append(" ".join(current))
            current = []
            count = 0
        current.append(sentence)
        count += len(sentence_words)
    if current:
        parts.append(" ".join(current))
    return parts


def overlap_tail(text: str, overlap_words: int) -> str:
    sentences = [
        part.strip() for part in SENTENCE_BOUNDARY_RE.split(text) if part.strip()
    ]
    if len(sentences) > 1 and len(sentences[-1].split()) <= overlap_words * 2:
        return sentences[-1]
    return " ".join(text.split()[-overlap_words:])


def build_chunks(
    report: dict,
    units: list[Unit],
    target_words: int,
    max_words: int,
    overlap_words: int,
) -> list[dict]:
    report_id = report["report_id"]
    title = report["title"]
    chunks: list[dict] = []
    unit_lookup = {unit.unit_id: unit for unit in units}
    ordinary = {"prose", "list", "equation"}
    current_units: list[Unit] = []
    current_parts: list[str] = []
    current_word_count = 0

    def emit(kind: str = "passage") -> None:
        nonlocal current_units, current_parts, current_word_count
        if not current_parts:
            return
        body = "\n\n".join(current_parts).strip()
        source_units = list(dict.fromkeys(unit.unit_id for unit in current_units))
        pages = [
            page
            for unit in current_units
            for page in (unit.page_start, unit.page_end)
            if page is not None
        ]
        section = current_units[0].section
        section_key = current_units[0].section_key
        chunk_id = f"{report_id}:chunk-{len(chunks) + 1:05d}"
        embedding_text = (
            f"Document: {title}\nSection: {section}\nType: {kind}\n\n{body}"
        )
        chunks.append(
            {
                "chunk_id": chunk_id,
                "report_id": report_id,
                "screening_record_id": report["screening_record_id"],
                "title": title,
                "year": report.get("publication_year"),
                "section": section,
                "section_key": section_key,
                "chunk_type": kind,
                "page_start": min(pages) if pages else None,
                "page_end": max(pages) if pages else None,
                "source_unit_ids": source_units,
                "image_refs": list(
                    dict.fromkeys(
                        image for unit in current_units for image in unit.image_refs
                    )
                ),
                "text": body,
                "embedding_text": embedding_text,
                "word_count": len(body.split()),
                "character_count": len(body),
            }
        )
        current_units = []
        current_parts = []
        current_word_count = 0

    unit_index = 0
    while unit_index < len(units):
        unit = units[unit_index]

        if unit.kind == "table_row":
            emit()
            table_units: list[Unit] = []
            table_parts: list[str] = []
            table_words = 0
            first_section_key = unit.section_key
            while unit_index < len(units):
                row = units[unit_index]
                row_words = len(row.text.split())
                if row.kind != "table_row" or row.section_key != first_section_key:
                    break
                if table_parts and table_words + row_words > max_words:
                    break
                table_units.append(row)
                table_parts.append(row.text)
                table_words += row_words
                unit_index += 1
                if table_words >= target_words:
                    break
            context_ids = list(
                dict.fromkeys(
                    unit_id for row in table_units for unit_id in row.context_unit_ids
                )
            )
            context_units = [
                unit_lookup[unit_id]
                for unit_id in context_ids
                if unit_id in unit_lookup
            ]
            context = ""
            if context_units:
                context = "\n\nNearby context: " + " ".join(
                    context_units[0].text.split()[:120]
                )
            current_units = table_units + context_units[:1]
            current_parts = ["\n".join(table_parts) + context]
            current_word_count = len(current_parts[0].split())
            emit("table")
            continue

        if unit.kind not in ordinary:
            emit()
            context_units = [
                unit_lookup[unit_id]
                for unit_id in unit.context_unit_ids
                if unit_id in unit_lookup
            ]
            context = ""
            if context_units:
                context_words = context_units[0].text.split()
                context = "\n\nNearby context: " + " ".join(context_words[:120])
            current_units = [unit] + context_units
            current_parts = [unit.text + context]
            current_word_count = len(current_parts[0].split())
            emit(unit.kind)
            unit_index += 1
            continue

        pieces = split_long_text(unit.text, max_words=max_words)
        for piece_index, piece in enumerate(pieces):
            piece_words = len(piece.split())
            same_section = (
                not current_units or current_units[-1].section_key == unit.section_key
            )
            if current_parts and (
                not same_section or current_word_count + piece_words > max_words
            ):
                previous_body = "\n\n".join(current_parts)
                previous_section_key = current_units[-1].section_key
                emit()
                if (
                    same_section
                    and overlap_words > 0
                    and previous_section_key == unit.section_key
                ):
                    overlap = overlap_tail(previous_body, overlap_words)
                    current_units = [unit]
                    current_parts = [overlap]
                    current_word_count = len(overlap.split())
            current_units.append(unit)
            current_parts.append(piece)
            current_word_count += piece_words
            if current_word_count >= target_words and piece_index == len(pieces) - 1:
                emit()
        unit_index += 1
    emit()
    return chunks


def expected_sources() -> Iterator[tuple[dict, Path | None, str]]:
    configurations = [
        {
            "namespace": "review",
            "json_path": REPO_ROOT / "SLR/SLR1/review-candidates.json",
            "id_prefix": "review-candidate-",
            "preferred": REPO_ROOT / "SLR/SLR1/pdfs/review-reports",
            "preferred_prefix": "review-report-",
            "fallback": REPO_ROOT / "SLR/SLR1/pdfs/review-candidates",
            "fallback_prefix": "review-candidate-",
        },
        {
            "namespace": "citation",
            "json_path": REPO_ROOT / "SLR/SLR1/citation-candidates.json",
            "id_prefix": "citation-candidate-",
            "preferred": REPO_ROOT / "SLR/SLR1/pdfs/citation-chasing-candidates",
            "preferred_prefix": "citation-candidate-",
            "fallback": DATA_DIR / "generated-sources",
            "fallback_prefix": "citation-candidate-",
        },
    ]
    for config in configurations:
        source_data = json.loads(config["json_path"].read_text(encoding="utf-8"))
        for candidate in source_data["records"]:
            decision = str(candidate.get("screening_decision") or "").casefold()
            if not decision.startswith("include_"):
                continue
            suffix = candidate["candidate_id"].removeprefix(config["id_prefix"])
            preferred = config["preferred"] / f"{config['preferred_prefix']}{suffix}.md"
            fallback = config["fallback"] / f"{config['fallback_prefix']}{suffix}.md"
            if preferred.exists():
                path, source_kind = preferred, "preferred_markdown"
            elif fallback.exists():
                path, source_kind = fallback, "fallback_markdown"
            else:
                path, source_kind = None, "missing"
            report = {
                "report_id": f"{config['namespace']}-{suffix}",
                "namespace": config["namespace"],
                "screening_record_id": candidate["candidate_id"],
                "screening_decision": candidate["screening_decision"],
                "title": candidate.get("title") or candidate["candidate_id"],
                "authors": candidate.get("authors") or [],
                "publication_year": candidate.get("publication_year"),
                "doi": candidate.get("doi") or None,
            }
            yield report, path, source_kind


def build(args: argparse.Namespace) -> dict:
    reports: list[dict] = []
    all_units: list[Unit] = []
    all_chunks: list[dict] = []
    missing: list[dict] = []
    content_hashes: dict[str, list[str]] = defaultdict(list)

    for report, path, source_kind in expected_sources():
        if path is None:
            missing.append(report)
            continue
        markdown = path.read_text(encoding="utf-8", errors="replace")
        units = parse_markdown(report["report_id"], report["title"], markdown)
        chunks = build_chunks(
            report,
            units,
            target_words=args.target_words,
            max_words=args.max_words,
            overlap_words=args.overlap_words,
        )
        digest = hashlib.sha256(
            SPACE_RE.sub(" ", strip_frontmatter(markdown)).encode("utf-8")
        ).hexdigest()
        content_hashes[digest].append(report["report_id"])
        report.update(
            {
                "source_path": str(path.relative_to(REPO_ROOT)),
                "source_kind": source_kind,
                "source_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
                "content_sha256": digest,
                "unit_count": len(units),
                "chunk_count": len(chunks),
                "source_word_count": len(markdown.split()),
            }
        )
        reports.append(report)
        all_units.extend(units)
        all_chunks.extend(chunks)

    if missing and not args.allow_missing:
        identifiers = ", ".join(item["screening_record_id"] for item in missing)
        raise RuntimeError(f"Included reports lack Markdown: {identifiers}")

    exact_duplicates = [ids for ids in content_hashes.values() if len(ids) > 1]
    manifest = {
        "schema_version": "slr1-embedding-corpus/v1",
        "selection_rule": "screening_decision starts with include_, case insensitive; already_included is excluded",
        "chunking": {
            "strategy": "section bounded paragraph groups, grouped atomic table rows, and contextual captions",
            "target_words": args.target_words,
            "max_words": args.max_words,
            "overlap_words": args.overlap_words,
            "title_and_section_prefix": True,
            "caption_and_table_neighbor_context_words": 120,
            "references_excluded": True,
        },
        "counts": {
            "directly_included_records": len(reports) + len(missing),
            "reports_indexed": len(reports),
            "reports_missing": len(missing),
            "units": len(all_units),
            "chunks": len(all_chunks),
            "chunk_words": sum(chunk["word_count"] for chunk in all_chunks),
        },
        "missing_reports": missing,
        "exact_duplicate_report_groups": exact_duplicates,
    }

    jsonl_write(DATA_DIR / "reports.jsonl", reports)
    jsonl_write(DATA_DIR / "units.jsonl", (asdict(unit) for unit in all_units))
    jsonl_write(DATA_DIR / "chunks.jsonl", all_chunks)
    (DATA_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-words", type=int, default=180)
    parser.add_argument("--max-words", type=int, default=300)
    parser.add_argument("--overlap-words", type=int, default=30)
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.overlap_words < args.target_words <= args.max_words:
        parser.error("Require 0 <= overlap_words < target_words <= max_words")
    return args


def main() -> int:
    try:
        manifest = build(parse_args())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
