#!/usr/bin/env python3
"""Find model-diagram images in caption chunks and extract them with Pi subagents."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
LOG_DIR = SCRIPT_DIR / "logs/diagram-subagents"
CANDIDATES_PATH = DATA_DIR / "diagram-candidates.jsonl"
ANALYSES_PATH = DATA_DIR / "diagram-analyses.jsonl"
MODEL = "openai-codex/gpt-5.6-luna"

LANGUAGE_RE = re.compile(r"\b(?:SysML|Capella|Arcadia)\b", re.IGNORECASE)
SYSML_RE = re.compile(
    r"\b(?:BDD|IBD|UCD|block definition diagram|internal block diagram|"
    r"requirements? diagram|activity diagram|sequence diagram|"
    r"state machine(?: diagram)?|parametric diagram|use case diagram|"
    r"package diagram|REQ diagram)\b",
    re.IGNORECASE,
)
ARCADIA_RE = re.compile(
    r"(?<![A-Za-z])(?:OCB|OAB|OAIB|OES|MCB|SAB|SFBD|SDFB|LAB|LFBD|"
    r"LCBD|LES|PAB|PFBD|PES|MSM)(?![A-Za-z])|"
    r"\b(?:operational architecture blank|system architecture blank|"
    r"logical architecture blank|physical architecture blank|"
    r"system function(?:al)? breakdown|logical function(?:al)? breakdown|"
    r"physical function(?:al)? breakdown)\b",
    re.IGNORECASE,
)
MODEL_REPRESENTATION_RE = re.compile(
    r"\b(?:model view|model(?:ing)? diagram|system architecture|"
    r"logical architecture|physical architecture|operational architecture|"
    r"functional hierarchy|functional decomposition|functional breakdown|"
    r"(?:system|logical|physical|operational)?\s*"
    r"(?:exchange|entity|functional|operational) scenario|"
    r"(?:functional )?allocation)\b",
    re.IGNORECASE,
)
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^]]*)]\(([^)]+)\)")
PAGE_MARKER_RE = re.compile(r"<!--\s*PDF_PAGE:\s*([1-9][0-9]*)\s*-->")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


EXTRACTION_INSTRUCTIONS = """You are extracting one candidate MBSE figure for search indexing. Inspect the attached image itself. Caption context may identify the language or representation type. Never report an element or relationship unless it is visible in the image.

Decide whether the image contains an actual SysML diagram or an actual Capella/Arcadia model diagram. Screenshots of model diagrams count. Exclude photos, plots, tables, ordinary flowcharts, methodology graphics, taxonomies, and prose even when their captions discuss SysML or Capella.

Return exactly one valid JSON object without Markdown or commentary:
{
  "contains_target_diagram": true,
  "diagram_family": "sysml | capella_arcadia | both | uncertain | none",
  "modeling_language": "verbatim language or null",
  "representation_name": "visible title or caption name, or null",
  "representation_type": "native diagram type or null",
  "summary": "one factual sentence based on visible content",
  "elements": [{
    "name": "verbatim visible label",
    "native_type": "notation type or unknown",
    "semantic_class": "external_actor | external_system_or_subsystem | capability | function_or_behavior | activity_or_action | exchanged_item_or_signal | interface | port_or_connector | block_component_part_or_instance | state_or_mode | scenario | use_case | hazard_fault_failure | requirement | property_parameter_constraint | test_setup_or_equipment | objective | pass_fail_criterion | unknown",
    "logical_or_physical": "logical | physical | unspecified",
    "eps_boundary": "inside | outside | unknown"
  }],
  "relationships": [{
    "source": "verbatim endpoint or unknown",
    "target": "verbatim endpoint or unknown",
    "name": "verbatim visible label or null",
    "native_type": "notation type or unknown",
    "semantic_class": "data_or_resource_flow_or_exchange | allocation_or_mapping | connection_or_link | state_or_mode_transition | decomposition_or_containment | sequence | trace_satisfy_verify | unknown",
    "direction": "source_to_target | target_to_source | bidirectional | undirected | unknown"
  }],
  "other_visible_labels": ["meaningful verbatim labels not captured above"],
  "uncertainties": ["short uncertainty"],
  "confidence": 0.0
}

For a non-target figure, set contains_target_diagram to false and diagram_family to "none". Give a short visible-content summary and leave elements and relationships empty. Transcribe all legible model elements and named exchanges that matter for retrieval. Preserve wording and capitalization. Do not expand acronyms or invent hidden endpoints. Use "unknown" when the image does not establish an EPS boundary or logical/physical classification."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(path)


def split_caption_context(text: str) -> tuple[str, str]:
    parts = text.split("\n\nNearby context:", 1)
    return parts[0].strip(), parts[1].strip() if len(parts) == 2 else ""


def selection_reasons(text: str) -> list[str]:
    reasons = []
    if LANGUAGE_RE.search(text):
        reasons.append("language_name")
    if SYSML_RE.search(text):
        reasons.append("sysml_diagram_type")
    if ARCADIA_RE.search(text):
        reasons.append("arcadia_diagram_type")
    if MODEL_REPRESENTATION_RE.search(text):
        reasons.append("model_representation_term")
    return reasons


def image_path(report: dict[str, Any], image_ref: str) -> Path:
    markdown = REPO_ROOT / report["source_path"]
    return (markdown.parent / image_ref).resolve()


def diagram_id(report_id: str, image_ref: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", Path(image_ref).stem.casefold()).strip("-")
    digest = hashlib.sha1(image_ref.encode("utf-8")).hexdigest()[:8]
    return f"{report_id}--{stem}-{digest}"


def page_image_contexts(report: dict[str, Any]) -> list[dict[str, Any]]:
    markdown = (REPO_ROOT / report["source_path"]).read_text(
        encoding="utf-8", errors="replace"
    )
    current_page: int | None = None
    current_heading = "Document"
    page_text: dict[int | None, list[str]] = {}
    images: list[dict[str, Any]] = []
    for line in markdown.splitlines():
        page_match = PAGE_MARKER_RE.search(line)
        if page_match:
            current_page = int(page_match.group(1))
            continue
        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            current_heading = " ".join(heading_match.group(1).split())
        for match in MARKDOWN_IMAGE_RE.finditer(line):
            images.append(
                {
                    "image_ref": match.group(2),
                    "page": current_page,
                    "section": current_heading,
                }
            )
        text = MARKDOWN_IMAGE_RE.sub(" ", line)
        text = re.sub(r"<[^>]+>|<!--.*?-->", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" #*`|-")
        if text and not text.startswith("---"):
            page_text.setdefault(current_page, []).append(text)

    unique: dict[str, dict[str, Any]] = {}
    for image in images:
        image_ref = image["image_ref"]
        if image_ref in unique:
            continue
        context = " ".join(page_text.get(image["page"], []))
        unique[image_ref] = {**image, "context": context[:5000]}
    return list(unique.values())


def build_candidates() -> list[dict[str, Any]]:
    reports = {row["report_id"]: row for row in read_jsonl(DATA_DIR / "reports.jsonl")}
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for chunk in read_jsonl(DATA_DIR / "chunks.jsonl"):
        if chunk.get("chunk_type") != "caption" or not chunk.get("image_refs"):
            continue
        reasons = selection_reasons(chunk.get("text", ""))
        if not reasons:
            continue
        report_id = chunk["report_id"]
        report = reports[report_id]
        caption, context = split_caption_context(chunk["text"])
        for image_ref in chunk["image_refs"]:
            key = (report_id, image_ref)
            candidate = grouped.setdefault(
                key,
                {
                    "diagram_id": diagram_id(report_id, image_ref),
                    "report_id": report_id,
                    "screening_record_id": report["screening_record_id"],
                    "title": report["title"],
                    "year": report.get("publication_year"),
                    "source_path": report["source_path"],
                    "source_image": str(
                        image_path(report, image_ref).relative_to(REPO_ROOT)
                    ),
                    "image_ref": image_ref,
                    "page_start": chunk.get("page_start"),
                    "page_end": chunk.get("page_end"),
                    "section": chunk.get("section"),
                    "section_key": chunk.get("section_key"),
                    "caption_chunks": [],
                    "selection_reasons": [],
                },
            )
            candidate["caption_chunks"].append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "caption": caption,
                    "context": context,
                    "page_start": chunk.get("page_start"),
                    "page_end": chunk.get("page_end"),
                }
            )
            candidate["selection_reasons"] = sorted(
                set(candidate["selection_reasons"]) | set(reasons)
            )
            starts = [
                value
                for value in (candidate.get("page_start"), chunk.get("page_start"))
                if value is not None
            ]
            ends = [
                value
                for value in (candidate.get("page_end"), chunk.get("page_end"))
                if value is not None
            ]
            candidate["page_start"] = min(starts) if starts else None
            candidate["page_end"] = max(ends) if ends else None

    caption_candidates = sorted(grouped.values(), key=lambda row: row["diagram_id"])
    fallback_candidates = []
    for report in reports.values():
        if not LANGUAGE_RE.search(report["title"]):
            continue
        for image in page_image_contexts(report):
            image_ref = image["image_ref"]
            key = (report["report_id"], image_ref)
            if key in grouped:
                continue
            section = image["section"] or "Document"
            fallback_candidates.append(
                {
                    "diagram_id": diagram_id(report["report_id"], image_ref),
                    "report_id": report["report_id"],
                    "screening_record_id": report["screening_record_id"],
                    "title": report["title"],
                    "year": report.get("publication_year"),
                    "source_path": report["source_path"],
                    "source_image": str(
                        image_path(report, image_ref).relative_to(REPO_ROOT)
                    ),
                    "image_ref": image_ref,
                    "page_start": image["page"],
                    "page_end": image["page"],
                    "section": section,
                    "section_key": re.sub(
                        r"[^a-z0-9]+", " ", section.casefold()
                    ).strip(),
                    "caption_chunks": [
                        {
                            "chunk_id": None,
                            "caption": "",
                            "context": image["context"],
                            "page_start": image["page"],
                            "page_end": image["page"],
                        }
                    ],
                    "selection_reasons": ["language_in_report_title"],
                }
            )
    fallback_candidates.sort(key=lambda row: row["diagram_id"])
    candidates = caption_candidates + fallback_candidates
    for candidate in candidates:
        path = REPO_ROOT / candidate["source_image"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing candidate image: {path}")
        candidate["source_image_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return candidates


def candidate_prompt(candidate: dict[str, Any]) -> str:
    evidence = []
    for row in candidate["caption_chunks"]:
        if row.get("caption"):
            line = f"Caption: {row['caption']}"
            if row.get("context"):
                line += f"\nNearby context: {row['context']}"
        else:
            line = "No source caption is available."
            if row.get("context"):
                line += f"\nText from the same page: {row['context']}"
        evidence.append(line)
    context = "\n\n".join(evidence)
    if len(context) > 5000:
        context = context[:5000] + "…"
    metadata = (
        f"Candidate metadata:\n"
        f"- Report: {candidate['report_id']}\n"
        f"- Page: {candidate.get('page_start')}\n"
        f"- Caption evidence:\n{context}"
    )
    return f"{EXTRACTION_INSTRUCTIONS}\n\n{metadata}"


def final_assistant(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    messages = [
        event.get("message")
        for event in events
        if event.get("type") == "message_end"
        and event.get("message", {}).get("role") == "assistant"
    ]
    return messages[-1] if messages else None


def parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("Subagent response is not a JSON object")
    if not isinstance(value.get("contains_target_diagram"), bool):
        raise ValueError("Subagent response lacks contains_target_diagram boolean")
    for field in ("elements", "relationships", "other_visible_labels", "uncertainties"):
        if not isinstance(value.get(field), list):
            raise ValueError(f"Subagent response lacks {field} array")
    return value


def load_events(path: Path) -> list[dict[str, Any]]:
    events = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def process_candidate(
    candidate: dict[str, Any], thinking: str, timeout_seconds: int
) -> tuple[str, str]:
    item_dir = LOG_DIR / candidate["diagram_id"]
    result_path = item_dir / "result.json"
    if result_path.exists():
        return candidate["diagram_id"], "cached"

    item_dir.mkdir(parents=True, exist_ok=True)
    events_path = item_dir / "events.jsonl"
    stderr_path = item_dir / "stderr.txt"
    command = [
        "pi",
        "--mode",
        "json",
        "--model",
        MODEL,
        "--thinking",
        thinking,
        "--no-session",
        "--no-context-files",
        "--no-skills",
        "--no-tools",
        candidate_prompt(candidate),
        f"@{REPO_ROOT / candidate['source_image']}",
    ]
    started = datetime.now(timezone.utc)
    try:
        with events_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
            "w", encoding="utf-8"
        ) as stderr:
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                stdout=stdout,
                stderr=stderr,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        exit_code = completed.returncode
        error = None
    except subprocess.TimeoutExpired:
        exit_code = None
        error = f"Timed out after {timeout_seconds} seconds"

    finished = datetime.now(timezone.utc)
    events = load_events(events_path) if events_path.exists() else []
    message = final_assistant(events)
    response_text = ""
    if message:
        response_text = "".join(
            part.get("text", "")
            for part in message.get("content", [])
            if part.get("type") == "text"
        )
    try:
        analysis = parse_json_response(response_text) if response_text else None
        if analysis is None and error is None:
            error = "Subagent returned no final JSON"
    except (json.JSONDecodeError, ValueError) as exc:
        analysis = None
        error = f"Invalid subagent JSON: {exc}"

    result = {
        **candidate,
        "status": "ok" if exit_code == 0 and analysis is not None else "error",
        "analysis": analysis,
        "raw_response": response_text if analysis is None else None,
        "error": error or (f"Pi exited with status {exit_code}" if exit_code else None),
        "subagent": {
            "provider": message.get("provider") if message else "openai-codex",
            "model": message.get("model") if message else "gpt-5.6-luna",
            "thinking": thinking,
            "usage": message.get("usage") if message else None,
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "exit_code": exit_code,
        },
    }
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return candidate["diagram_id"], result["status"]


def collect(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for candidate in candidates:
        path = LOG_DIR / candidate["diagram_id"] / "result.json"
        if path.exists():
            results.append(json.loads(path.read_text(encoding="utf-8")))
    write_jsonl(ANALYSES_PATH, results)
    return results


def command_candidates() -> int:
    candidates = build_candidates()
    write_jsonl(CANDIDATES_PATH, candidates)
    reason_counts: dict[str, int] = {}
    for candidate in candidates:
        for reason in candidate["selection_reasons"]:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    print(
        json.dumps(
            {
                "candidates": len(candidates),
                "reports": len({row["report_id"] for row in candidates}),
                "selection_reason_counts": reason_counts,
                "path": str(CANDIDATES_PATH.relative_to(SCRIPT_DIR)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def command_process(args: argparse.Namespace) -> int:
    candidates = read_jsonl(CANDIDATES_PATH)
    if not candidates:
        raise RuntimeError(f"No candidates in {CANDIDATES_PATH}; run candidates first")
    if args.id:
        wanted = set(args.id)
        candidates = [row for row in candidates if row["diagram_id"] in wanted]
    if args.offset:
        candidates = candidates[args.offset :]
    if args.limit is not None:
        candidates = candidates[: args.limit]

    statuses: dict[str, int] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_candidate, candidate, args.thinking, args.timeout_seconds
            ): candidate["diagram_id"]
            for candidate in candidates
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            diagram, status = future.result()
            statuses[status] = statuses.get(status, 0) + 1
            completed += 1
            print(f"[{completed}/{len(futures)}] {status}: {diagram}", flush=True)

    all_candidates = read_jsonl(CANDIDATES_PATH)
    results = collect(all_candidates)
    accepted = sum(
        row.get("status") == "ok"
        and row.get("analysis", {}).get("contains_target_diagram") is True
        for row in results
    )
    print(
        json.dumps(
            {
                "selected": len(candidates),
                "run_statuses": statuses,
                "results_collected": len(results),
                "target_diagrams": accepted,
                "analyses_path": str(ANALYSES_PATH.relative_to(SCRIPT_DIR)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if statuses.get("error", 0) == 0 else 1


def command_collect() -> int:
    candidates = read_jsonl(CANDIDATES_PATH)
    results = collect(candidates)
    print(json.dumps({"results_collected": len(results)}, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("candidates", help="Build candidates from caption chunks")
    process = subparsers.add_parser("process", help="Run one Luna subagent per image")
    process.add_argument("--workers", type=int, default=8)
    process.add_argument("--limit", type=int)
    process.add_argument("--offset", type=int, default=0)
    process.add_argument("--id", action="append")
    process.add_argument(
        "--thinking", choices=("off", "minimal", "low", "medium", "high", "max"), default="minimal"
    )
    process.add_argument("--timeout-seconds", type=int, default=300)
    subparsers.add_parser("collect", help="Collect existing per-image results")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "candidates":
            return command_candidates()
        if args.command == "process":
            return command_process(args)
        return command_collect()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
