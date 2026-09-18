"""Render validated visual diagram extractions as retrieval chunks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
ANALYSES_PATH = SCRIPT_DIR / "data/diagram-analyses.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def clean(value: Any, fallback: str = "unknown") -> str:
    if value is None:
        return fallback
    text = " ".join(str(value).split()).strip()
    return text or fallback


def quoted(value: Any) -> str:
    return json.dumps(clean(value), ensure_ascii=False)


def element_sentence(element: dict[str, Any]) -> str:
    return (
        f"Model element {quoted(element.get('name'))}. "
        f"Native type: {clean(element.get('native_type'))}. "
        f"Language-neutral semantic class: "
        f"{clean(element.get('semantic_class')).replace('_', ' ')}. "
        f"Logical or physical classification: "
        f"{clean(element.get('logical_or_physical'), 'unspecified')}. "
        f"EPS boundary: {clean(element.get('eps_boundary'))}."
    )


def relationship_sentence(relationship: dict[str, Any]) -> str:
    name = relationship.get("name")
    name_text = f" named {quoted(name)}" if name else ""
    return (
        f"Model relationship from {quoted(relationship.get('source'))} to "
        f"{quoted(relationship.get('target'))}{name_text}. "
        f"Native type: {clean(relationship.get('native_type'))}. "
        f"Language-neutral semantic class: "
        f"{clean(relationship.get('semantic_class')).replace('_', ' ')}. "
        f"Direction: {clean(relationship.get('direction')).replace('_', ' ')}."
    )


def groups(
    prefix: list[str], statements: Iterable[str], target_words: int, max_words: int
) -> list[str]:
    prefix_text = "\n".join(prefix)
    prefix_words = len(prefix_text.split())
    output: list[str] = []
    current: list[str] = []
    current_words = prefix_words
    for statement in statements:
        words = len(statement.split())
        if current and current_words + words > max_words:
            output.append(prefix_text + "\n" + "\n".join(current))
            current = []
            current_words = prefix_words
        current.append(statement)
        current_words += words
        if current_words >= target_words:
            output.append(prefix_text + "\n" + "\n".join(current))
            current = []
            current_words = prefix_words
    if current:
        output.append(prefix_text + "\n" + "\n".join(current))
    return output


def common_lines(row: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    captions = [
        clean(item.get("caption"), "")
        for item in row.get("caption_chunks", [])
        if clean(item.get("caption"), "")
    ]
    diagram_kind = (
        "formal automaton"
        if analysis.get("diagram_family") == "formal_automata"
        else "MBSE model"
    )
    lines = [
        f"Visually extracted {diagram_kind} diagram.",
        f"Modeling language: {clean(analysis.get('modeling_language'))}.",
        f"Diagram family: {clean(analysis.get('diagram_family')).replace('_', ' ')}.",
        f"Representation name: {clean(analysis.get('representation_name'))}.",
        f"Representation type: {clean(analysis.get('representation_type'))}.",
    ]
    if captions:
        lines.append(f"Source caption: {captions[0]}")
    return lines


def build_diagram_chunks(
    reports: dict[str, dict[str, Any]],
    target_words: int = 180,
    max_words: int = 300,
    analyses_path: Path = ANALYSES_PATH,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    analyses = read_jsonl(analyses_path)
    accepted = [
        row
        for row in analyses
        if row.get("status") == "ok"
        and isinstance(row.get("analysis"), dict)
        and row["analysis"].get("contains_target_diagram") is True
        and row.get("report_id") in reports
    ]
    for row in accepted:
        analysis = row["analysis"]
        report = reports[row["report_id"]]
        common = common_lines(row, analysis)
        parts: list[tuple[str, str]] = []

        overview = common + [f"Visible-content summary: {clean(analysis.get('summary'))}"]
        uncertainties = [clean(value, "") for value in analysis.get("uncertainties", [])]
        uncertainties = [value for value in uncertainties if value]
        if uncertainties:
            overview.append("Extraction uncertainty: " + " ".join(uncertainties))
        parts.append(("overview", "\n".join(overview)))

        element_texts = [
            element_sentence(element)
            for element in analysis.get("elements", [])
            if isinstance(element, dict)
        ]
        parts.extend(
            ("elements", text)
            for text in groups(common, element_texts, target_words, max_words)
        )

        relationship_texts = [
            relationship_sentence(relationship)
            for relationship in analysis.get("relationships", [])
            if isinstance(relationship, dict)
        ]
        parts.extend(
            ("relationships", text)
            for text in groups(common, relationship_texts, target_words, max_words)
        )

        labels = [
            clean(value, "") for value in analysis.get("other_visible_labels", [])
        ]
        labels = [value for value in labels if value]
        label_sentences = [f"Other visible model label: {quoted(value)}." for value in labels]
        parts.extend(
            ("labels", text)
            for text in groups(common, label_sentences, target_words, max_words)
        )

        for part_index, (part_name, text) in enumerate(parts, start=1):
            chunk_id = f"{row['diagram_id']}:chunk-{part_index:03d}"
            section = row.get("section") or "Model diagrams"
            embedding_text = (
                f"Document: {report['title']}\n"
                f"Section: {section}\n"
                f"Type: diagram {part_name}\n\n{text}"
            )
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "report_id": row["report_id"],
                    "screening_record_id": report["screening_record_id"],
                    "title": report["title"],
                    "year": report.get("publication_year"),
                    "section": section,
                    "section_key": row.get("section_key") or "model diagrams",
                    "chunk_type": "diagram",
                    "diagram_part": part_name,
                    "diagram_id": row["diagram_id"],
                    "modeling_language": analysis.get("modeling_language"),
                    "representation_type": analysis.get("representation_type"),
                    "diagram_confidence": analysis.get("confidence"),
                    "page_start": row.get("page_start"),
                    "page_end": row.get("page_end"),
                    "source_unit_ids": [],
                    "source_caption_chunk_ids": [
                        item["chunk_id"]
                        for item in row.get("caption_chunks", [])
                        if item.get("chunk_id")
                    ],
                    "image_refs": [row["source_image"]],
                    "text": text,
                    "embedding_text": embedding_text,
                    "word_count": len(text.split()),
                    "character_count": len(text),
                }
            )
    return chunks
