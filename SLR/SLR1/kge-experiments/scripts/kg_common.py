"""Shared helpers for SLR1 KG construction and controlled-code analyses."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"
KG_DIR = BASE_DIR / "kg"
OUTPUT_DIR = BASE_DIR / "outputs"
TABLES_DIR = OUTPUT_DIR / "tables"
REPORTS_DIR = OUTPUT_DIR / "reports"
GRAPH_EXPORTS_DIR = OUTPUT_DIR / "graph_exports"
FIGURES_DIR = OUTPUT_DIR / "figures"

REQUIRED_JSONL = [
    "studies.jsonl",
    "study_codes.jsonl",
    "claims.jsonl",
    "limitations.jsonl",
    "emergent_codes.jsonl",
    "evidence_quotes.jsonl",
    "gap_mappings.jsonl",
]

NONE_LIKE = {
    "",
    "none",
    "not reported",
    "none/not reported",
    "not_reported",
    "not applicable",
    "n/a",
    "na",
    "null",
}

EVIDENCE_CONFIDENCE_ORDER = {
    "Unsupported": 0,
    "Weak": 1,
    "Moderate": 2,
    "Strong": 3,
}


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def ensure_issue001_outputs() -> None:
    """Run the ISSUE-001 flattening script only if expected JSONL files are missing."""
    missing = [name for name in REQUIRED_JSONL if not (DATA_DIR / name).exists()]
    if not missing:
        return
    flatten_script = SCRIPT_DIR / "01_flatten_extraction.py"
    if not flatten_script.exists():
        raise FileNotFoundError(f"Missing flatten script: {flatten_script}")
    subprocess.run([sys.executable, str(flatten_script)], check=True)
    still_missing = [name for name in REQUIRED_JSONL if not (DATA_DIR / name).exists()]
    if still_missing:
        raise FileNotFoundError(f"Flattening did not produce: {', '.join(still_missing)}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows_list = list(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows_list:
            writer.writerow({name: csv_value(row.get(name)) for name in fieldnames})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_generated_at_utc() -> str:
    """Return a deterministic UTC timestamp derived from the flattened source extraction."""
    studies_path = DATA_DIR / "studies.jsonl"
    if not studies_path.exists():
        return "unknown"
    with studies_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            raw_value = clean_text(json.loads(line).get("source_generated_at"))
            if not raw_value:
                return "unknown"
            try:
                parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
            except ValueError:
                return raw_value
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
    return "unknown"


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = " ".join(value.split())
        return text or None
    text = str(value)
    return text if text else None


def csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def slugify(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "blank"


def node_id(node_type: str, value: Any) -> str:
    return f"{slugify(node_type)}::{slugify(value)}"


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def values(value: Any) -> list[str]:
    out: list[str] = []
    for item in ensure_list(value):
        text = clean_text(item)
        if text is not None:
            out.append(text)
    return out


def unique_preserve(items: Iterable[Any]) -> list[Any]:
    seen: set[str] = set()
    out: list[Any] = []
    for item in items:
        key = csv_value(item).strip().lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def sorted_unique_text(items: Iterable[Any]) -> list[str]:
    return sorted((str(item) for item in unique_preserve(items) if clean_text(item)), key=lambda x: x.lower())


def join_values(items: Iterable[Any], sep: str = "; ") -> str:
    return sep.join(sorted_unique_text(items))


def first_nonempty(*items: Any) -> Any:
    for item in items:
        if item is None:
            continue
        if isinstance(item, str) and not item.strip():
            continue
        if isinstance(item, list) and not item:
            continue
        return item
    return None


def is_none_like(value: Any) -> bool:
    text = (clean_text(value) or "").strip().lower()
    return text in NONE_LIKE


def evidence_confidence_rank(value: Any) -> int:
    return EVIDENCE_CONFIDENCE_ORDER.get(str(value), -1)


def quote_by_claim(evidence_quotes: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for record in evidence_quotes:
        claim_id = record.get("claim_id")
        quote = clean_text(record.get("evidence_quote"))
        if claim_id and quote and claim_id not in out:
            out[claim_id] = quote
    return out


def merge_text(existing: str | None, new_value: Any, max_parts: int = 3) -> str | None:
    new_text = clean_text(new_value)
    if not new_text:
        return existing
    if not existing:
        return new_text
    parts = [part.strip() for part in existing.split(" | ") if part.strip()]
    lower_parts = {part.lower() for part in parts}
    if new_text.lower() not in lower_parts and len(parts) < max_parts:
        parts.append(new_text)
    return " | ".join(parts)


def dedupe_study_codes(
    study_codes: Iterable[dict[str, Any]],
    field_paths: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Deduplicate structured/extraction duplicates by study, field_path, and value.

    ISSUE-001 intentionally flattens both structured_code_summary and extraction.
    This helper collapses exact duplicate coded values while preserving source ids,
    paths, source sections, rationale, evidence quote, confidence, and status.
    """
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in study_codes:
        field_path = record.get("field_path")
        if field_paths is not None and field_path not in field_paths:
            continue
        value = clean_text(record.get("value"))
        if value is None:
            continue
        study_id = str(record.get("study_id"))
        key = (study_id, str(field_path), value.lower())
        merged = grouped.get(key)
        if merged is None:
            merged = {
                "study_id": study_id,
                "field_path": field_path,
                "value": value,
                "value_index": record.get("value_index"),
                "status": clean_text(record.get("status")),
                "rationale": clean_text(record.get("rationale")),
                "evidence_quote": clean_text(record.get("evidence_quote")),
                "confidence": clean_text(record.get("confidence")),
                "study_code_ids": [],
                "source_paths": [],
                "source_sections": [],
                "statuses": [],
                "confidences": [],
            }
            grouped[key] = merged
        merged["rationale"] = merge_text(merged.get("rationale"), record.get("rationale"))
        merged["evidence_quote"] = merge_text(merged.get("evidence_quote"), record.get("evidence_quote"), max_parts=2)
        merged["confidence"] = first_nonempty(merged.get("confidence"), clean_text(record.get("confidence")))
        for target_key, source_key in [
            ("study_code_ids", "study_code_id"),
            ("source_paths", "source_path"),
            ("source_sections", "source_section"),
            ("statuses", "status"),
            ("confidences", "confidence"),
        ]:
            text = clean_text(record.get(source_key))
            if text and text not in merged[target_key]:
                merged[target_key].append(text)
        if merged.get("value_index") is None or (
            record.get("value_index") is not None and record.get("value_index") < merged.get("value_index")
        ):
            merged["value_index"] = record.get("value_index")
    return sorted(
        grouped.values(),
        key=lambda row: (
            str(row.get("study_id")),
            str(row.get("field_path")),
            row.get("value_index") if row.get("value_index") is not None else 999999,
            str(row.get("value")).lower(),
        ),
    )


def values_by_study(records: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for record in records:
        value = clean_text(record.get("value"))
        if value is not None and value.lower() not in {v.lower() for v in out[record["study_id"]]}:
            out[record["study_id"]].append(value)
    return dict(out)


def field_values_by_study(study_codes: Iterable[dict[str, Any]], field_path: str) -> dict[str, list[str]]:
    return values_by_study(dedupe_study_codes(study_codes, {field_path}))


def scalarize_graph_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def write_graphml(graph: Any, path: Path) -> None:
    """Write GraphML after converting list/dict/None attributes to scalars."""
    import networkx as nx

    path.parent.mkdir(parents=True, exist_ok=True)
    graph_class = graph.__class__
    safe_graph = graph_class()
    safe_graph.graph.update({k: scalarize_graph_value(v) for k, v in graph.graph.items()})
    for node, attrs in graph.nodes(data=True):
        safe_graph.add_node(str(node), **{k: scalarize_graph_value(v) for k, v in attrs.items()})
    if graph.is_multigraph():
        for source, target, key, attrs in graph.edges(keys=True, data=True):
            safe_graph.add_edge(
                str(source),
                str(target),
                key=str(key),
                **{k: scalarize_graph_value(v) for k, v in attrs.items()},
            )
    else:
        for source, target, attrs in graph.edges(data=True):
            safe_graph.add_edge(
                str(source),
                str(target),
                **{k: scalarize_graph_value(v) for k, v in attrs.items()},
            )
    nx.write_graphml(safe_graph, path)


def markdown_table(rows: list[dict[str, Any]], columns: list[str], max_rows: int = 10) -> str:
    if not rows:
        return "_(none)_\n"
    shown = rows[:max_rows]
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, sep]
    for row in shown:
        cells = []
        for column in columns:
            cell = csv_value(row.get(column)).replace("\n", " ")
            cells.append(cell)
        lines.append("| " + " | ".join(cells) + " |")
    if len(rows) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(rows)} rows._")
    return "\n".join(lines) + "\n"
