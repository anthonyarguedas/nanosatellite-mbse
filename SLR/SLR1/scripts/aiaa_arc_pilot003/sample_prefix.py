#!/usr/bin/env python3
"""Capture a deterministic, non-mergeable manifestation prefix.

The source order is fixed by the field-cell order below, then ARC's rendered
Date/Earliest order within each cell. The prefix stops at 100 distinct raw ARC
DOI-like manifestation IDs. A separate audit applies DOI-first identity before
reporting the investigation-record count. The current A2 and BT2 runs exhausted
all cells before this manifestation cap. The script then reads only visible
record-page title, abstract, keywords, and type metadata.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from datetime import date
from typing import Any

from playwright.async_api import async_playwright
from queries import (
    BLOCKS,
    EF_TERMS,
    MB_TERMS,
    METADATA_FIELDS,
    MH_TERMS,
    P_TERMS,
    T2_PAIRS,
    T2_SUBBLOCKS,
    refinement_rows,
)
from run_fielded_count import load_adapter, write_full_json
from run_stage1 import DATE_END, DATE_START, SEARCH_DIR

MAX_PREFIX = 100
TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.casefold())


def phrase_spans(text: str, phrase: str) -> list[tuple[int, int]]:
    haystack, needle = tokens(text), tokens(phrase)
    if not needle:
        return []
    return [
        (index, index + len(needle))
        for index in range(len(haystack) - len(needle) + 1)
        if haystack[index:index + len(needle)] == needle
    ]


def hits_by_field(fields: dict[str, str], alternatives: tuple[str, ...]) -> dict[str, list[str]]:
    return {
        name: [term for term in alternatives if phrase_spans(text, term)]
        for name, text in fields.items()
        if any(phrase_spans(text, term) for term in alternatives)
    }


def pair_hits_by_field(fields: dict[str, str], pairs: tuple[tuple[str, str], ...]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for name, text in fields.items():
        matched = []
        for left, right in pairs:
            left_spans = phrase_spans(text, left)
            right_spans = phrase_spans(text, right)
            if any(
                max(left_start, right_start) - min(left_end, right_end) <= 5
                for left_start, left_end in left_spans
                for right_start, right_end in right_spans
            ):
                matched.append({"left": left, "right": right})
        if matched:
            output[name] = matched
    return output


def cell_configs(schedule_id: str) -> list[dict[str, Any]]:
    output = []
    if schedule_id == "A2":
        for population_field in METADATA_FIELDS:
            for defining_field in METADATA_FIELDS:
                output.append(
                    {
                        "cell_id": f"A2-P-{population_field.lower()}-MH-or-MB-{defining_field.lower()}",
                        "rows": refinement_rows("A2", population_field, defining_field),
                        "population_field": population_field,
                        "defining_field": defining_field,
                        "target": "M_H_OR_M_B",
                        "third": "E_F",
                    }
                )
    elif schedule_id == "BT2":
        for population_field in METADATA_FIELDS:
            for defining_field in METADATA_FIELDS:
                for index, subblock in enumerate(T2_SUBBLOCKS):
                    output.append(
                        {
                            "cell_id": f"BT2-P-{population_field.lower()}-MB-{defining_field.lower()}-T2-{index + 1:02d}-of-{len(T2_SUBBLOCKS):02d}",
                            "rows": (
                                (population_field, BLOCKS["P"]),
                                (defining_field, BLOCKS["M_B"]),
                                ("Anywhere", subblock),
                            ),
                            "population_field": population_field,
                            "defining_field": defining_field,
                            "target": "M_B",
                            "third": "T2",
                            "t2_pair_range": [index * 56 + 1, index * 56 + 56],
                            "t2_pairs": tuple(T2_PAIRS[index * 56:(index + 1) * 56]),
                        }
                    )
    else:  # pragma: no cover - argparse protects this
        raise ValueError(schedule_id)
    return output


def expected_rows(adapter, rows: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [
        {
            "field": adapter.normalize_arc_field(name),
            "label": adapter.ARC_FIELD_LABELS[adapter.normalize_arc_field(name)],
            "text": text,
        }
        for name, text in rows
    ]


def serialize_source_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record.get(key)
        for key in ("paperId", "doi", "rank", "title", "year", "abstract", "publicationTitle", "publicationDate", "documentType", "url")
    }


async def scrape_record_pages(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Read visible bibliographic fields in a page created and closed by this call."""
    output: list[dict[str, Any]] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(os.environ["BH_CDP_URL"])
        page = await browser.contexts[0].new_page()
        try:
            for index, record in enumerate(records, start=1):
                observation: dict[str, Any] = {"doi": record["doi"], "sample_rank": index}
                try:
                    await page.goto(record["url"], wait_until="domcontentloaded", timeout=60_000)
                    await page.wait_for_timeout(350)
                    title = ""
                    if await page.locator("h1").count():
                        title = (await page.locator("h1").first.inner_text()).strip()
                    abstract = ""
                    for selector in (".abstractSection", ".hlFld-Abstract"):
                        if await page.locator(selector).count():
                            abstract = (await page.locator(selector).first.inner_text()).strip()
                            if abstract:
                                abstract = re.sub(r"^Abstract\s*", "", abstract, flags=re.IGNORECASE).strip()
                                break
                    keyword_values = []
                    for value in await page.locator(".article__keyword").all_inner_texts():
                        cleaned = re.sub(r"\s+", " ", value).strip()
                        if cleaned and cleaned not in keyword_values:
                            keyword_values.append(cleaned)
                    article_type = ""
                    selector = ".citation__top__item.article__tocHeading"
                    if await page.locator(selector).count():
                        article_type = re.sub(r"\s+", " ", await page.locator(selector).first.inner_text()).strip()
                    meta_values = await page.locator("meta").evaluate_all(
                        "els => els.map(e => ({name: e.getAttribute('name'), property: e.getAttribute('property'), content: e.getAttribute('content')}))"
                    )
                    og_type = next(
                        (item.get("content") for item in meta_values if item.get("property") == "og:type" and item.get("content")),
                        None,
                    )
                    pb_context = next(
                        (item.get("content") for item in meta_values if item.get("name") == "pbContext" and item.get("content")),
                        "",
                    )
                    context_content_type = None
                    context_subtype = None
                    if isinstance(pb_context, str):
                        content_match = re.search(r"(?:^|;)ctype:string:([^;]+)", pb_context)
                        subtype_match = re.search(r"(?:^|;)csubtype:string:([^;]+)", pb_context)
                        if content_match:
                            context_content_type = content_match.group(1).strip() or None
                        if subtype_match:
                            context_subtype = subtype_match.group(1).strip() or None
                    observation.update(
                        {
                            "status": "observed",
                            "title": title or record.get("title", ""),
                            "abstract": abstract or record.get("abstract", ""),
                            "keywords": keyword_values,
                            "publication_type_visible": article_type or None,
                            "publication_type_og": og_type,
                            "publication_content_type_context": context_content_type,
                            "publication_subtype_context": context_subtype,
                            "publication_type_context": context_subtype or context_content_type,
                            "document_type_ris": record.get("documentType"),
                        }
                    )
                except Exception as error:  # noqa: BLE001 - metadata absence is not a false match.
                    observation.update({"status": "metadata_unavailable", "error_type": type(error).__name__, "error": str(error)})
                output.append(observation)
        finally:
            await page.close()
            await browser.close()
    return output


def evidence(schedule_id: str, metadata: dict[str, Any], cell: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "Title": metadata.get("title") or "",
        "Keywords": " ".join(metadata.get("keywords") or ()),
        "Abstract": metadata.get("abstract") or "",
    }
    p_hits = hits_by_field(fields, P_TERMS)
    mb_hits = hits_by_field(fields, MB_TERMS)
    mh_hits = hits_by_field(fields, MH_TERMS)
    ef_hits = hits_by_field(fields, EF_TERMS)
    t2_hits = pair_hits_by_field(fields, T2_PAIRS)
    assigned_p_field = {"Title": "Title", "Keyword": "Keywords", "Abstract": "Abstract"}[cell["population_field"]]
    assigned_defining_field = {"Title": "Title", "Keyword": "Keywords", "Abstract": "Abstract"}[cell["defining_field"]]
    if schedule_id == "A2":
        target_hits = {name: sorted(set(mh_hits.get(name, []) + mb_hits.get(name, []))) for name in fields if mh_hits.get(name) or mb_hits.get(name)}
        target_ok = bool(target_hits)
        third_ok = bool(ef_hits)
        likely_scope = (
            "metadata_consistent_stream_A_candidate"
            if p_hits and target_ok and third_ok
            else "metadata_incomplete_or_hidden_match_possible"
        )
        acronym_hits = {
            name: [term for term in values if term in {"MBSE", "SysML", "OPM", "OOSEM", "MBE", "MDE", "MBD", "RFLP"}]
            for name, values in target_hits.items()
        }
        expected_visible = {
            "P_assigned_field": bool(p_hits.get(assigned_p_field)),
            "M_H_or_M_B_assigned_field": bool(target_hits.get(assigned_defining_field)),
            "E_F_any_visible_field": third_ok,
        }
    else:
        target_hits = mb_hits
        target_ok = bool(mb_hits)
        third_ok = bool(t2_hits)
        likely_scope = (
            "metadata_consistent_stream_B_candidate_eps_thread_unresolved"
            if p_hits and target_ok and third_ok
            else "metadata_incomplete_or_hidden_match_possible"
        )
        acronym_hits = {}
        expected_visible = {
            "P_assigned_field": bool(p_hits.get(assigned_p_field)),
            "M_B_assigned_field": bool(mb_hits.get(assigned_defining_field)),
            "T2_pair_any_visible_field": third_ok,
        }
    hidden_risk = [key for key, value in expected_visible.items() if not value]
    return {
        "visible_population_confirmation": p_hits,
        "visible_target_confirmation": target_hits,
        "visible_third_block_confirmation": ef_hits if schedule_id == "A2" else t2_hits,
        "expected_field_confirmation": expected_visible,
        "possible_hidden_or_full_text_match": bool(hidden_risk),
        "missing_visible_evidence": hidden_risk,
        "likely_scope": likely_scope,
        "acronym_hits": acronym_hits,
        "wildcard_noise": "not_applicable_no_accepted_wildcard_was_used",
        "recurring_removable_noise_candidate": (
            "visible_metadata_does_not_confirm_all_source blocks; do not call it a false match without full text"
            if hidden_risk
            else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True, choices=("A2", "BT2"))
    parser.add_argument("--mode", choices=("ris", "preview"), default="ris")
    args = parser.parse_args()
    suffix = "" if args.mode == "ris" else "-preview"
    output_path = SEARCH_DIR / f"{args.schedule}-sampled-prefix{suffix}.json"
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite {output_path}")
    adapter = load_adapter()
    selected: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}
    source_runs: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for cell in cell_configs(args.schedule):
        if len(selected) >= MAX_PREFIX:
            break
        rows = cell["rows"]
        try:
            result = adapter.search_aiaa_arc(
                None,
                field_rows=tuple(adapter.FieldRow(name, text) for name, text in rows),
                date_start=date.fromisoformat(DATE_START),
                date_end=date.fromisoformat(DATE_END),
                limit=100,
                max_pages=5,
                passes=2,
                timeout_seconds=60.0,
                page_delay_seconds=1.0,
                max_source_total=10_000,
                preview_results=args.mode == "preview",
                cdp_url=os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL),
            )
            metadata = result.get("output_metadata", {})
            if metadata.get("field_rows") != expected_rows(adapter, rows):
                raise RuntimeError("ARC sample field-row readback changed")
            if not (
                metadata.get("observed_exact_query_echo") is True
                and metadata.get("exact_date_controls_proven") is True
                and metadata.get("language_filter") is None
                and metadata.get("publication_type_filter") is None
            ):
                raise RuntimeError("ARC sample source controls were not exactly proven")
            run = {
                "cell_id": cell["cell_id"],
                "field_rows": metadata.get("field_rows"),
                "source_total": result.get("total"),
                "results_retrieved": len(result.get("results", [])),
                "records": [serialize_source_record(record) for record in result.get("results", [])],
            }
            source_runs.append(run)
            for record in result.get("results", []):
                doi = record.get("doi")
                if not isinstance(doi, str) or not doi:
                    continue
                if doi not in seen and len(selected) < MAX_PREFIX:
                    entry = serialize_source_record(record)
                    entry["source_cell"] = cell["cell_id"]
                    entry["source_rank"] = record.get("rank")
                    entry["cell"] = cell
                    selected.append(entry)
                    seen[doi] = entry
        except Exception as error:  # noqa: BLE001 - preserve every adapter/source failure.
            failures.append({"cell_id": cell["cell_id"], "error_type": type(error).__name__, "error": adapter.safe_error_message(error)})
            break
    page_metadata = asyncio.run(scrape_record_pages(selected)) if selected else []
    by_doi = {item["doi"]: item for item in page_metadata}
    sampled_records = []
    for source_record in selected:
        observed = by_doi.get(source_record["doi"], {"status": "metadata_unavailable"})
        record = {key: value for key, value in source_record.items() if key != "cell"}
        record["page_metadata"] = observed
        record["diagnostic"] = evidence(args.schedule, observed, source_record["cell"])
        sampled_records.append(record)
    payload = {
        "schema_version": "aiaa-arc-fielded-sampled-prefix/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "003",
        "schedule_id": args.schedule,
        "diagnostic_kind": "non_mergeable_deterministic_manifestation_prefix",
        "capture_mode": args.mode,
        "do_not_merge": True,
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "count_scope": "source-month totals before exact-day exclusions",
        },
        "prefix_contract": {
            "maximum_unique_manifestation_ids": MAX_PREFIX,
            "cell_order": [entry["cell_id"] for entry in cell_configs(args.schedule)],
            "within_cell_order": "ARC rendered Date/Earliest source order, reconciled across two DOI passes",
            "deduplication": "first raw ARC DOI-like manifestation ID wins; DOI-first identity is applied in the separate audit",
            "stopped_after_unique_manifestation_ids": len(selected),
        },
        "source_runs": source_runs,
        "source_failures": failures,
        "sampled_records": sampled_records,
        "limitations": [
            "The prefix is diagnostic and non-mergeable, not a final search.",
            "Visible metadata confirmation cannot establish full-text eligibility or prove a source hit was false.",
            "ARC record pages expose keywords as visible metadata; no source-side language filter exists.",
            "Preview mode retains DOI-bearing rendered cards and then reads only visible record-page metadata; it does not claim RIS capture.",
            "The prior RIS-mode attempt is retained separately when it failed; a failed citation-form route is not a false match.",
        ],
    }
    write_full_json(output_path, payload)
    print(json.dumps({"saved": str(output_path), "unique_manifestation_ids": len(selected), "source_runs": len(source_runs), "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
