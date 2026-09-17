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

from diagram_corpus import build_diagram_chunks


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
INCLUDED_REPORTS_PATH = REPO_ROOT / "SLR/SLR1/included_reports.json"
REPORT_MARKDOWN_RE = re.compile(r"^(review|citation)-report-([0-9]+)\.md$")
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
DISPLAY_MATH_ENV_RE = re.compile(
    r"\\begin\{(?:equation|align|aligned|gather|multline|split|array)\*?\}",
    re.IGNORECASE,
)
SINGLE_LINE_MATH_RE = re.compile(r"^\s*\$(?!\$).+\$\s*$", re.DOTALL)
EQUATION_CUE_RE = re.compile(
    r"\b(?:equations?|eqs?|eqns?)\.?\b|"
    r"\b(?:following|preceding)\s+(?:formula|expression|relationship)\b|"
    r"\b(?:formula|expression|relationship)\s+(?:below|above|as follows)\b",
    re.IGNORECASE,
)
EQUATION_RANGE_RE = re.compile(
    r"\b(?:equations?|eqs?|eqns?)\.?\s*[([]?\s*(\d+)\s*"
    r"(?:-|–|—|to|through|until)\s*(?:equations?\s*)?[([]?\s*(\d+)",
    re.IGNORECASE,
)
EQUATION_NUMBER_RE = re.compile(
    r"\b(?:equation|eq)\.?\s*[([]?\s*(\d+[a-z]?)", re.IGNORECASE
)
EQUATION_TAG_RE = re.compile(r"\\tag\*?\{([^{}]+)\}")


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


def is_display_equation(lines: list[str]) -> bool:
    raw = "\n".join(lines).strip()
    if not raw:
        return False
    if raw.startswith("$$") and raw.endswith("$$"):
        return True
    if raw.startswith(r"\[") and raw.endswith(r"\]"):
        return True
    if DISPLAY_MATH_ENV_RE.search(raw):
        return True
    if len(lines) == 1 and SINGLE_LINE_MATH_RE.fullmatch(raw):
        inner = raw[1:-1]
        return bool(
            re.search(
                r"=|\\(?:leq?|geq?|sum|int|prod|frac|left|right|begin)\b",
                inner,
            )
        )
    return False


def classify_block(lines: list[str], text: str) -> str:
    if CAPTION_RE.match(text):
        return "caption"
    if is_display_equation(lines):
        return "equation"
    nonempty = [line for line in lines if line.strip()]
    if (
        nonempty
        and sum(bool(LIST_LINE_RE.match(line)) for line in nonempty)
        >= len(nonempty) / 2
    ):
        return "list"
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


def word_excerpt(text: str, limit: int) -> str:
    words = text.split()
    excerpt = " ".join(words[:limit])
    return excerpt + ("…" if len(words) > limit else "")


def equation_labels(text: str) -> list[str]:
    matches: list[tuple[int, list[str]]] = []
    range_spans: list[tuple[int, int]] = []
    for match in EQUATION_RANGE_RE.finditer(text):
        start, end = int(match.group(1)), int(match.group(2))
        if end >= start and end - start <= 100:
            matches.append((match.start(), [str(value) for value in range(start, end + 1)]))
            range_spans.append(match.span())
    for match in EQUATION_NUMBER_RE.finditer(text):
        if any(start <= match.start() < end for start, end in range_spans):
            continue
        matches.append((match.start(), [match.group(1)]))
    labels: list[str] = []
    for _, values in sorted(matches):
        for value in values:
            if value not in labels:
                labels.append(value)
    return labels


def is_equation_caption(text: str) -> bool:
    return bool(
        EQUATION_CUE_RE.search(text)
        or (len(text.split()) <= 20 and text.rstrip().endswith(":"))
    )


def equation_neighbor(
    units: list[Unit], start: int, direction: int, max_distance: int = 4
) -> Unit | None:
    origin = units[start]
    fallback = None
    for distance in range(1, max_distance + 1):
        index = start + direction * distance
        if not 0 <= index < len(units):
            break
        candidate = units[index]
        if candidate.section_key != origin.section_key:
            break
        if candidate.kind not in {"prose", "list"}:
            continue
        pages = [
            page
            for page in (
                origin.page_start,
                origin.page_end,
                candidate.page_start,
                candidate.page_end,
            )
            if page is not None
        ]
        if pages and max(pages) - min(pages) > 1:
            continue
        fallback = fallback or candidate
        if len(candidate.text.split()) >= 4 or is_equation_caption(candidate.text):
            return candidate
    return fallback


def split_long_equation(text: str, max_words: int) -> list[str]:
    if len(text.split()) <= max_words:
        return [text]
    rows = text.split(r"\\")
    if len(rows) == 1:
        return split_long_text(text, max_words)

    parts: list[str] = []
    current: list[str] = []
    current_words = 0
    for index, row in enumerate(rows):
        row = row + (r"\\" if index < len(rows) - 1 else "")
        row_words = len(row.split())
        if row_words > max_words:
            if current:
                parts.append(" ".join(current))
                current = []
                current_words = 0
            parts.extend(split_long_text(row, max_words))
            continue
        if current and current_words + row_words > max_words:
            parts.append(" ".join(current))
            current = []
            current_words = 0
        current.append(row)
        current_words += row_words
    if current:
        parts.append(" ".join(current))
    return parts


def build_equation_chunks(
    report: dict,
    units: list[Unit],
    max_words: int,
    context_words: int = 120,
) -> list[dict]:
    """Create dedicated equation chunks with captions or nearby prose."""
    report_id = report["report_id"]
    title = report["title"]
    chunks: list[dict] = []
    equation_number = 0
    index = 0

    while index < len(units):
        if units[index].kind != "equation":
            index += 1
            continue
        run_start = index
        run_section_key = units[run_start].section_key
        while (
            index < len(units)
            and units[index].kind == "equation"
            and units[index].section_key == run_section_key
        ):
            index += 1
        run_end = index
        before = equation_neighbor(units, run_start, -1)
        after = equation_neighbor(units, run_end - 1, 1)
        caption = next(
            (
                unit
                for unit in (before, after)
                if unit is not None and is_equation_caption(unit.text)
            ),
            None,
        )
        run_labels = equation_labels(caption.text) if caption is not None else []
        assigned_labels: list[str] = []
        if len(run_labels) == run_end - run_start:
            assigned_labels = run_labels
        elif run_end - run_start == 1 and len(run_labels) == 1:
            assigned_labels = run_labels

        for run_offset, unit in enumerate(units[run_start:run_end]):
            equation_number += 1
            equation_id = f"{report_id}:equation-{equation_number:05d}"
            tag_match = EQUATION_TAG_RE.search(unit.text)
            label = (
                tag_match.group(1).strip()
                if tag_match
                else assigned_labels[run_offset]
                if run_offset < len(assigned_labels)
                else None
            )

            context_limit = max(20, min(context_words, max_words // 2))
            context_lines: list[str] = []
            context_units: list[Unit] = []
            context_source = "none"
            equation_caption = None
            if caption is not None:
                equation_caption = word_excerpt(caption.text, context_limit)
                context_lines.append(f"Equation caption: {equation_caption}")
                context_units.append(caption)
                context_source = "caption"
            else:
                context_source = "surrounding_context"
                per_side = max(10, context_limit // 2)
                if before is not None:
                    context_lines.append(
                        "Context before equation: "
                        + word_excerpt(before.text, per_side)
                    )
                    context_units.append(before)
                if after is not None:
                    context_lines.append(
                        "Context after equation: " + word_excerpt(after.text, per_side)
                    )
                    context_units.append(after)
                if not context_units:
                    context_source = "none"

            label_line = f"Equation label: Equation ({label})." if label else ""
            prefix_lines = [line for line in (label_line, *context_lines) if line]
            prefix_words = len(" ".join(prefix_lines).split())
            formula_budget = max(50, max_words - prefix_words - 10)
            formula_parts = split_long_equation(unit.text, formula_budget)
            source_units = [unit, *context_units]
            pages = [
                page
                for source_unit in source_units
                for page in (source_unit.page_start, source_unit.page_end)
                if page is not None
            ]

            for part_index, formula_part in enumerate(formula_parts, start=1):
                part_line = (
                    f"Equation part: {part_index} of {len(formula_parts)}."
                    if len(formula_parts) > 1
                    else ""
                )
                body_lines = [
                    *prefix_lines,
                    part_line,
                    f"Formula: {formula_part}",
                ]
                body = "\n".join(line for line in body_lines if line)
                chunk_id = (
                    equation_id
                    if len(formula_parts) == 1
                    else f"{equation_id}:part-{part_index:03d}"
                )
                embedding_text = (
                    f"Document: {title}\n"
                    f"Section: {unit.section}\n"
                    f"Type: equation\n\n{body}"
                )
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "report_id": report_id,
                        "screening_record_id": report["screening_record_id"],
                        "title": title,
                        "year": report.get("publication_year"),
                        "section": unit.section,
                        "section_key": unit.section_key,
                        "chunk_type": "equation",
                        "equation_id": equation_id,
                        "equation_label": label,
                        "equation_caption": equation_caption,
                        "equation_context_source": context_source,
                        "equation_part": part_index,
                        "equation_parts": len(formula_parts),
                        "page_start": min(pages) if pages else unit.page_start,
                        "page_end": max(pages) if pages else unit.page_end,
                        "source_unit_ids": list(
                            dict.fromkeys(
                                source_unit.unit_id for source_unit in source_units
                            )
                        ),
                        "image_refs": [],
                        "text": body,
                        "embedding_text": embedding_text,
                        "word_count": len(body.split()),
                        "character_count": len(body),
                    }
                )
    return chunks


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


def included_report_sources() -> dict[str, Path]:
    """Return the report files selected by the authoritative included list."""
    records = json.loads(INCLUDED_REPORTS_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(f"Expected a JSON array in {INCLUDED_REPORTS_PATH}")

    sources: dict[str, Path] = {}
    repository_root = REPO_ROOT.resolve()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"Included report {index} must be a JSON object")
        source_value = record.get("full_text_markdown")
        if not isinstance(source_value, str) or not source_value.strip():
            raise ValueError(
                f"Included report {index} lacks a full_text_markdown path"
            )
        relative_path = Path(source_value)
        if relative_path.is_absolute():
            raise ValueError(
                f"Included report path must be repository relative: {source_value}"
            )
        try:
            source_path = (REPO_ROOT / relative_path).resolve()
            source_path.relative_to(repository_root)
        except (OSError, ValueError) as error:
            raise ValueError(
                f"Included report path leaves the repository: {source_value}"
            ) from error

        match = REPORT_MARKDOWN_RE.fullmatch(source_path.name)
        if match is None:
            raise ValueError(f"Cannot derive a report ID from {source_value}")
        namespace, suffix = match.groups()
        report_id = f"{namespace}-{suffix}"
        if report_id in sources:
            raise ValueError(f"Duplicate included report ID: {report_id}")
        sources[report_id] = source_path
    return sources


def expected_sources() -> Iterator[tuple[dict, Path | None, str]]:
    selected_sources = included_report_sources()
    unmatched_report_ids = set(selected_sources)
    configurations = [
        {
            "namespace": "review",
            "json_path": REPO_ROOT / "SLR/SLR1/review-candidates.json",
            "id_prefix": "review-candidate-",
        },
        {
            "namespace": "citation",
            "json_path": REPO_ROOT / "SLR/SLR1/citation-candidates.json",
            "id_prefix": "citation-candidate-",
        },
    ]
    for config in configurations:
        source_data = json.loads(config["json_path"].read_text(encoding="utf-8"))
        for candidate in source_data["records"]:
            suffix = candidate["candidate_id"].removeprefix(config["id_prefix"])
            report_id = f"{config['namespace']}-{suffix}"
            source_path = selected_sources.get(report_id)
            if source_path is None:
                continue
            unmatched_report_ids.remove(report_id)
            path = source_path if source_path.is_file() else None
            source_kind = "preferred_markdown" if path is not None else "missing"
            report = {
                "report_id": report_id,
                "namespace": config["namespace"],
                "screening_record_id": candidate["candidate_id"],
                "screening_decision": candidate.get("screening_decision"),
                "title": candidate.get("title") or candidate["candidate_id"],
                "authors": candidate.get("authors") or [],
                "publication_year": candidate.get("publication_year"),
                "doi": candidate.get("doi") or None,
            }
            yield report, path, source_kind

    if unmatched_report_ids:
        identifiers = ", ".join(sorted(unmatched_report_ids))
        raise ValueError(f"Included reports lack candidate records: {identifiers}")


def build(args: argparse.Namespace) -> dict:
    reports: list[dict] = []
    all_units: list[Unit] = []
    all_chunks: list[dict] = []
    all_equation_chunks: list[dict] = []
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
        equation_chunks = build_equation_chunks(
            report,
            units,
            max_words=args.max_words,
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
                "equation_count": len(
                    {chunk["equation_id"] for chunk in equation_chunks}
                ),
                "equation_chunk_count": len(equation_chunks),
                "source_word_count": len(markdown.split()),
            }
        )
        reports.append(report)
        all_units.extend(units)
        all_chunks.extend(chunks)
        all_equation_chunks.extend(equation_chunks)

    if missing and not args.allow_missing:
        identifiers = ", ".join(item["screening_record_id"] for item in missing)
        raise RuntimeError(f"Included reports lack Markdown: {identifiers}")

    report_lookup = {report["report_id"]: report for report in reports}
    diagram_chunks = build_diagram_chunks(
        report_lookup,
        target_words=args.target_words,
        max_words=args.max_words,
    )
    diagram_chunk_counts: dict[str, int] = defaultdict(int)
    diagram_ids: dict[str, set[str]] = defaultdict(set)
    for chunk in diagram_chunks:
        report_id = chunk["report_id"]
        diagram_chunk_counts[report_id] += 1
        diagram_ids[report_id].add(chunk["diagram_id"])
    for report in reports:
        report_id = report["report_id"]
        base_text_chunks = report["chunk_count"]
        report["base_text_chunk_count"] = base_text_chunks
        report["text_chunk_count"] = (
            base_text_chunks + report["equation_chunk_count"]
        )
        report["diagram_count"] = len(diagram_ids[report_id])
        report["diagram_chunk_count"] = diagram_chunk_counts[report_id]
        report["chunk_count"] = (
            report["text_chunk_count"] + report["diagram_chunk_count"]
        )
    all_chunks.extend(diagram_chunks)
    all_chunks.extend(all_equation_chunks)

    exact_duplicates = [ids for ids in content_hashes.values() if len(ids) > 1]
    manifest = {
        "schema_version": "slr1-embedding-corpus/v2",
        "selection_rule": "listed in SLR/SLR1/included_reports.json",
        "selection_source": {
            "path": str(INCLUDED_REPORTS_PATH.relative_to(REPO_ROOT)),
            "sha256": hashlib.sha256(INCLUDED_REPORTS_PATH.read_bytes()).hexdigest(),
        },
        "chunking": {
            "strategy": "section bounded paragraph groups, grouped atomic table rows, contextual captions, dedicated equations with captions or surrounding context, page context for uncaptioned images, and visually extracted model diagrams",
            "target_words": args.target_words,
            "max_words": args.max_words,
            "overlap_words": args.overlap_words,
            "title_and_section_prefix": True,
            "caption_and_table_neighbor_context_words": 120,
            "equation_context_words": 120,
            "equation_detection": "display math blocks and standalone mathematical expressions",
            "references_excluded": True,
        },
        "diagram_extraction": {
            "analyses_path": "data/diagram-analyses.jsonl",
            "candidate_rule": "matching caption evidence, captioned images in Simulink sections, plus uncaptioned images from reports whose title names SysML, Capella, Arcadia, or Simulink",
            "acceptance_rule": "status is ok and contains_target_diagram is true",
            "parts": ["overview", "elements", "relationships", "labels"],
        },
        "counts": {
            "directly_included_records": len(reports) + len(missing),
            "reports_indexed": len(reports),
            "reports_missing": len(missing),
            "units": len(all_units),
            "text_chunks": len(all_chunks) - len(diagram_chunks),
            "diagrams_indexed": len(
                {chunk["diagram_id"] for chunk in diagram_chunks}
            ),
            "diagram_chunks": len(diagram_chunks),
            "equations_indexed": len(
                {chunk["equation_id"] for chunk in all_equation_chunks}
            ),
            "equation_chunks": len(all_equation_chunks),
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
