#!/usr/bin/env python3
"""Create a post-freeze, metadata-only retained-cache recall audit.

Only cache filenames, Markdown YAML/frontmatter and headings, and PDF document
metadata are inspected.  No cache body text, old extraction, prior screen, or
legacy ID is read or used to create candidates or change screening.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "eps-mbse-slr-2026"
NON_ALNUM = re.compile(r"[^a-z0-9]+")
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", re.I)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_doi(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", text)
    return text.rstrip(".,;:)]}")


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    return NON_ALNUM.sub(" ", text).strip()


def compact(value: Any) -> str:
    return NON_ALNUM.sub("", normalize_title(value))


def metadata_from_markdown(path: Path) -> dict[str, Any]:
    """Read only YAML/frontmatter keys and Markdown headings, never body text."""
    frontmatter: dict[str, str] = {}
    headings: list[str] = []
    in_frontmatter = False
    frontmatter_closed = False
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line_number, raw_line in enumerate(fh, start=1):
                line = raw_line.rstrip("\r\n")
                if line_number == 1 and line.strip() == "---":
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    if line.strip() in {"---", "..."}:
                        in_frontmatter = False
                        frontmatter_closed = True
                        continue
                    match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
                    if match and match.group(1).lower() in {"title", "doi", "year", "date", "author", "authors"}:
                        frontmatter[match.group(1).lower()] = match.group(2).strip(" '\"")
                    continue
                # Scanning retains headings only; non-heading text is discarded.
                if re.match(r"^#{1,6}\s+", line) and len(headings) < 5:
                    headings.append(re.sub(r"^#{1,6}\s+", "", line).strip())
    except OSError as exc:
        return {"read_error": str(exc), "frontmatter": {}, "headings": []}
    return {"frontmatter": frontmatter, "headings": headings, "frontmatter_closed": frontmatter_closed}


def metadata_from_pdf(path: Path) -> dict[str, Any]:
    """Use pdfinfo document metadata only; no text/page extraction is performed."""
    allowed = {"Title", "Author", "Subject", "Keywords", "Creator", "Producer", "CreationDate", "ModDate", "Pages"}
    try:
        completed = subprocess.run(
            ["pdfinfo", str(path)], text=True, capture_output=True, timeout=20, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"pdfinfo_error": str(exc)}
    if completed.returncode != 0:
        return {"pdfinfo_error": (completed.stderr or "pdfinfo failed").strip()[:300]}
    metadata: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() in allowed:
            metadata[key.strip()] = value.strip()
    return metadata


def title_from_filename(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"^paper-\d+[_-]\d{4}[_-]", "", stem, flags=re.I)
    stem = re.sub(r"^\d{4}IEEE[A-Za-z]+-", "", stem)
    return stem.replace("_", " ")


def candidate_match(item: dict[str, Any], doi_index: dict[str, list[dict[str, Any]]], title_index: dict[str, list[dict[str, Any]]], candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, list[str]]:
    doi_candidates: list[str] = []
    raw_doi_values = item.get("doi_values", [])
    for value in raw_doi_values:
        normalized = normalize_doi(value)
        if normalized in doi_index:
            doi_candidates.extend(candidate["report_id"] for candidate in doi_index[normalized])
    if doi_candidates:
        unique = sorted(set(doi_candidates))
        if len(unique) == 1:
            return next(candidate for candidate in candidates if candidate["report_id"] == unique[0]), "normalized_doi", unique
        return None, "ambiguous_doi", unique

    title_values = item.get("title_values", [])
    for value in title_values:
        key = normalize_title(value)
        matches = title_index.get(key, [])
        if len(matches) == 1:
            return matches[0], "normalized_metadata_or_heading_title", [matches[0]["report_id"]]
        if len(matches) > 1:
            return None, "ambiguous_normalized_title", [candidate["report_id"] for candidate in matches]

    filename_key = normalize_title(title_from_filename(Path(item["cache_path"])))
    matches = title_index.get(filename_key, [])
    if len(matches) == 1:
        return matches[0], "normalized_filename_title", [matches[0]["report_id"]]
    if len(matches) > 1:
        return None, "ambiguous_normalized_filename_title", [candidate["report_id"] for candidate in matches]

    # A filename may be deliberately truncated.  Use only a unique, long title
    # prefix as a cache-retrieval check, never as a candidate identity source.
    if len(filename_key) >= 35 and not filename_key.startswith("10 "):
        prefix_matches = [
            candidate for candidate in candidates
            if normalize_title(candidate.get("title", "")).startswith(filename_key)
        ]
        if len(prefix_matches) == 1:
            return prefix_matches[0], "unique_long_filename_title_prefix", [prefix_matches[0]["report_id"]]
    return None, "no_independent_match", []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown-dir", type=Path, required=True)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--merged-candidates", type=Path, required=True)
    parser.add_argument("--screening-decisions", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--register-output", type=Path, required=True)
    args = parser.parse_args()

    with args.merged_candidates.open(encoding="utf-8") as fh:
        merged = json.load(fh)
    with args.screening_decisions.open(encoding="utf-8") as fh:
        decisions_payload = json.load(fh)
    with args.freeze.open(encoding="utf-8") as fh:
        freeze = json.load(fh)
    candidate_hash = sha256(args.merged_candidates)
    if candidate_hash != freeze["candidate_set"]["sha256"]:
        raise RuntimeError("Cache audit must use the independently frozen candidate set.")

    candidates = merged["results"]
    decision_by_id = {decision["report_id"]: decision for decision in decisions_payload["decisions"]}
    doi_index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    title_index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if candidate.get("doi"):
            doi_index[normalize_doi(candidate["doi"])].append(candidate)
        title_index[normalize_title(candidate.get("title", ""))].append(candidate)

    control_basenames = {"conversion-manifest.json", "match-report.json", "README.html"}
    cache_items: list[dict[str, Any]] = []
    item_counter = 0
    for cache_type, directory in [("markdown", args.markdown_dir), ("pdf", args.pdf_dir)]:
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            item_counter += 1
            relative_path = str(path)
            suffix = path.suffix.lower()
            item: dict[str, Any] = {
                "cache_item_id": f"cache-{cache_type[:2]}-{item_counter:04d}",
                "cache_type": cache_type,
                "cache_path": relative_path,
                "file_name": path.name,
                "file_extension": suffix,
                "inspection_scope": "filename_only",
                "metadata": {},
                "title_values": [],
                "doi_values": [],
            }
            if path.name in control_basenames:
                item["classification"] = "cache_control_file_not_bibliographic"
                item["match_status"] = "not_assessed"
                cache_items.append(item)
                continue
            if cache_type == "markdown" and suffix == ".md":
                parsed = metadata_from_markdown(path)
                item["metadata"] = parsed
                item["inspection_scope"] = "filename + Markdown frontmatter + headings only"
                frontmatter = parsed.get("frontmatter", {})
                item["title_values"] = [value for value in [frontmatter.get("title"), *(parsed.get("headings", [])[:1])] if value]
                item["doi_values"] = [frontmatter["doi"]] if frontmatter.get("doi") else []
            elif cache_type == "pdf" and suffix == ".pdf":
                parsed = metadata_from_pdf(path)
                item["metadata"] = parsed
                item["inspection_scope"] = "filename + PDF document metadata only (pdfinfo); no pages/text read"
                item["title_values"] = [parsed["Title"]] if parsed.get("Title") else []
                metadata_text = " ".join(str(parsed.get(key, "")) for key in ["Title", "Subject", "Keywords"])
                item["doi_values"] = DOI_RE.findall(metadata_text)
            else:
                # .html/.md in the PDF cache are intentionally not opened.
                item["classification"] = "non_pdf_file_in_pdf_cache_filename_only"
            # DOI-shaped cache filenames are metadata/filenames, not source content.
            filename_doi_compact = compact(path.stem)
            for candidate_doi in doi_index:
                if filename_doi_compact == compact(candidate_doi):
                    item["doi_values"].append(candidate_doi)
            candidate, method, candidates_considered = candidate_match(item, doi_index, title_index, candidates)
            item["match_status"] = method
            item["candidate_ids_considered"] = candidates_considered
            if candidate is not None:
                decision = decision_by_id[candidate["report_id"]]
                item["independent_match"] = {
                    "report_id": candidate["report_id"],
                    "title": candidate["title"],
                    "doi": candidate.get("doi"),
                    "screening_tier": decision["screening_tier"],
                    "screening_outcome_source": "independent title/abstract decision made before cache audit",
                }
            cache_items.append(item)

    bibliographic_items = [item for item in cache_items if item.get("match_status") != "not_assessed"]
    matched_items = [item for item in bibliographic_items if item.get("independent_match")]
    unmatched_items = [item for item in bibliographic_items if not item.get("independent_match")]
    matched_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in matched_items:
        matched_by_id[item["independent_match"]["report_id"]].append(item)
    unique_match_ids = sorted(matched_by_id)
    tier_counts = Counter(decision_by_id[report_id]["screening_tier"] for report_id in unique_match_ids)
    match_method_counts = Counter(item["match_status"] for item in matched_items)

    # Metadata-only signals from cache filenames/frontmatter/headings.  They are
    # explicitly not added to candidate set and do not reopen search decisions.
    potential_eps_gap_items = []
    for item in unmatched_items:
        label = " ".join([item["file_name"], *item.get("title_values", [])]).lower()
        if any(term in label for term in ["electrical power", " eps", "battery", "power system", "power architecture", "converter"]):
            potential_eps_gap_items.append({
                "cache_item_id": item["cache_item_id"], "cache_path": item["cache_path"],
                "label_from_filename_or_metadata": (item.get("title_values") or [item["file_name"]])[0],
            })

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summary = {
        "cache_files_seen": len(cache_items),
        "cache_control_files_not_assessed": sum(item.get("match_status") == "not_assessed" for item in cache_items),
        "bibliographic_or_possible_bibliographic_cache_files": len(bibliographic_items),
        "matched_cache_files": len(matched_items),
        "unmatched_or_ambiguous_cache_files": len(unmatched_items),
        "unique_independently_rediscovered_reports_matched": len(unique_match_ids),
        "unique_matches_by_independent_screening_tier": dict(sorted(tier_counts.items())),
        "match_methods": dict(sorted(match_method_counts.items())),
        "unique_kept_reports_with_cache_match": sum(decision_by_id[report_id]["screening_tier"] in {"core", "supporting"} for report_id in unique_match_ids),
        "unique_rejected_reports_with_cache_match": sum(decision_by_id[report_id]["screening_tier"] == "rejected" for report_id in unique_match_ids),
    }
    payload = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "anti_anchoring": {
            "independent_candidate_freeze": str(args.freeze),
            "independent_candidate_set_sha256": candidate_hash,
            "cache_inspection_order": "post-freeze and post-independent title/abstract screen only",
            "permitted_cache_data": "filenames; Markdown frontmatter/headings; PDF document metadata",
            "prohibited_cache_use": "no cache item supplied a candidate, screening decision, report ID, evidence extraction, or full-text eligibility decision",
        },
        "summary": summary,
        "match_scope": "Matches are retrieval/known-item recall checks against the independently rediscovered set only; a cache filename's historical paper number is opaque and was never used as an identifier.",
        "metadata_only_recall_signals": {
            "unmatched_eps_or_electrical_power_named_cache_items": potential_eps_gap_items,
            "interpretation": "These are cache-only metadata/filename signals, not candidates. They may indicate an EPS-primary terminology/indexing recall diagnostic, but cannot be assessed for MBSE qualification without a protocol-compliant new discovery route. No query was silently added and no record was imported.",
        },
        "items": cache_items,
    }
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    with args.audit_output.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    lines = [
        "# Read-Only Retained-File / Known-Item Register",
        "",
        f"Review run: `{RUN_ID}`",
        f"Independent candidate freeze: `searches/independent-candidate-freeze.json` (candidate SHA-256 `{candidate_hash}`)",
        "",
        "## Anti-anchoring boundary",
        "- This register was produced only after the independent 17-file new-run merge was frozen and the independent title/abstract screen was recorded.",
        "- Inspection was limited to cache filenames, Markdown frontmatter/headings, and PDF document metadata. No body text, old extraction, legacy screen, or full-text evidence was read.",
        "- Cache entries did not create candidates, alter screening, supply evidence, or provide report IDs. `cache-*` labels below are new audit-local labels; any historical filename number is only part of an opaque path.",
        "",
        "## Cache match summary",
        f"- Cache files seen: {summary['cache_files_seen']} ({summary['cache_control_files_not_assessed']} control files not assessed as bibliographic).",
        f"- Metadata/filename cache files matched to independently rediscovered reports: {summary['matched_cache_files']} files / {summary['unique_independently_rediscovered_reports_matched']} unique reports.",
        f"- Independently matched reports by already-recorded screening tier: {', '.join(f'{key}={value}' for key, value in summary['unique_matches_by_independent_screening_tier'].items()) or 'none'}.",
        f"- Unmatched or ambiguous cache files: {summary['unmatched_or_ambiguous_cache_files']}; they remain cache-only and are not candidates.",
        "",
        "## Matched retained files (retrieval/recall checks only)",
        "| Cache label | Cache path | Metadata/filename title | Match method | Independently rediscovered report | Existing screen tier |",
        "|---|---|---|---|---|---|",
    ]
    for item in matched_items:
        match = item["independent_match"]
        label = (item.get("title_values") or [item["file_name"]])[0].replace("|", "\\|")
        lines.append(f"| {item['cache_item_id']} | `{item['cache_path']}` | {label} | {item['match_status']} | {match['report_id']} — {match['title'].replace('|', '\\|')} | {match['screening_tier']} |")
    lines += ["", "## Unmatched/ambiguous retained files (cache-only; no candidate action)", "| Cache label | Cache path | Metadata/filename title | Match status |", "|---|---|---|---|"]
    for item in unmatched_items:
        label = (item.get("title_values") or [item["file_name"]])[0].replace("|", "\\|")
        lines.append(f"| {item['cache_item_id']} | `{item['cache_path']}` | {label} | {item['match_status']} |")
    lines += [
        "",
        "## Recall-audit observations",
        "- Matched entries demonstrate retrieval-cache overlap with the independently rediscovered set only; they are not evidence of final eligibility.",
        "- Cache-only EPS/electrical-power filename/metadata signals are listed in `searches/retained-file-recall-audit.json`. They suggest a terminology/indexing diagnostic for a future logged update, but may be non-MBSE or excluded platforms. They were not added to this corpus.",
        "- Citation chasing remains deferred until protocol-defined full-text inclusions exist.",
        "",
    ]
    args.register_output.parent.mkdir(parents=True, exist_ok=True)
    args.register_output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "success", **summary, "eps_gap_signals": len(potential_eps_gap_items)}, indent=2))


if __name__ == "__main__":
    main()
