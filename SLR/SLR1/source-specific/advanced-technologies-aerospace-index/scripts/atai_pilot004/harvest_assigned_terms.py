#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Harvest source-rendered indexing terms from selected ATAI Pilot 003 records."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)
SOURCE_NAME = "Advanced Technologies & Aerospace Index"
SOURCE_SITE = "ataindex"
SELECTED_RECORDS = (
    {
        "reading_aid_entry": "02",
        "paper_id": "3371247439",
        "title": "A Novel MBSE-Driven Integrated Modeling and Simulation Methodology for Small Satellites Development, (IM3S)",
    },
    {
        "reading_aid_entry": "03",
        "paper_id": "3062738113",
        "title": "A Tailored Systems Engineering Process for Developing Student-Built CubeSat Class Satellites",
    },
    {
        "reading_aid_entry": "07",
        "paper_id": "2035264195",
        "title": "Application of model-based systems engineering in small satellite conceptual design-A SysML approach",
    },
    {
        "reading_aid_entry": "11",
        "paper_id": "1825532815",
        "title": "Developing a CubeSat Model-Based System Engineering (MBSE) reference model - Interim status #2",
    },
    {
        "reading_aid_entry": "14",
        "paper_id": "3110716244",
        "title": "Effective Model-Based Systems Engineering framework for academic nanosatellite project management and design",
    },
    {
        "reading_aid_entry": "18",
        "paper_id": "3181339955",
        "title": "Integrating Model-Based Systems Engineering into CubeSat Development: A Case Study of the BOREALIS Mission",
    },
    {
        "reading_aid_entry": "37",
        "paper_id": "1709719593",
        "title": "Small satellite systems design methodology: A formal and agile design process",
    },
)

INDEXING_STATE_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/[\s\u200e\u200f]+/g, " ").trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const bodyText = document.body && document.body.innerText ? document.body.innerText : "";
  const lower = bodyText.toLowerCase();
  const pathMatch = window.location.pathname.match(/^\/ataindex\/docview\/(\d+)(?:\/|$)/i);
  const titleNodes = Array.from(document.querySelectorAll("#documentTitle, h1.documentTitle"))
    .filter(visible);
  const productLinks = Array.from(document.querySelectorAll(
    "a[aria-label='Advanced Technologies & Aerospace Index Product Home page']"
  )).filter(visible);
  const panels = Array.from(document.querySelectorAll("#indexSearchTermsPanel")).filter(visible);
  const panel = panels.length === 1 ? panels[0] : null;
  const groups = [];
  if (panel) {
    let current = null;
    for (const item of Array.from(panel.querySelectorAll("li")).filter(visible)) {
      if (item.classList.contains("indexFieldSubHeader")) {
        const field = normalize(item.textContent);
        if (field) {
          current = {field, terms: []};
          groups.push(current);
        }
        continue;
      }
      const checkboxes = Array.from(item.querySelectorAll("input[type='checkbox']")).filter(visible);
      if (!current || checkboxes.length !== 1) continue;
      const labels = Array.from(checkboxes[0].labels || [])
        .filter(visible)
        .map(label => normalize(label.textContent))
        .filter(Boolean);
      if (labels.length === 1) current.terms.push(labels[0]);
    }
  }
  return {
    host: window.location.hostname,
    path: window.location.pathname,
    paperId: pathMatch ? pathMatch[1] : "",
    titleHasExactSource: document.title.includes("Advanced Technologies & Aerospace Index"),
    productLinkExact: productLinks.length === 1,
    titleCount: titleNodes.length,
    title: titleNodes.length === 1 ? normalize(titleNodes[0].textContent) : "",
    panelCount: panels.length,
    indexingPanelLabel: normalize(document.querySelector("#indexSearchTermsLink")?.textContent),
    indexingGroups: groups,
    blocked: ["captcha", "verify you are human", "access denied", "unusual traffic"]
      .some(marker => lower.includes(marker)),
    requiresAccess: /authentication error|institutional access required|session has expired/i.test(bodyText) ||
      /\/(?:login|signin)(?:\/|$)/i.test(window.location.pathname),
  };
}
"""


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot004_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load ATAI adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_indexing_state(payload: Any, expected: dict[str, str]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise RuntimeError("ATAI returned malformed indexing-term evidence.")
    if payload.get("blocked") is True or payload.get("requiresAccess") is True:
        raise RuntimeError("ATAI record indexing was blocked or required renewed access.")
    if clean_text(payload.get("host")).casefold() != "www.proquest.com":
        raise RuntimeError("ATAI record indexing left www.proquest.com.")
    paper_id = clean_text(payload.get("paperId"))
    if paper_id != expected["paper_id"]:
        raise RuntimeError(f"ATAI returned the wrong record ID for {expected['paper_id']}.")
    if payload.get("path") != f"/{SOURCE_SITE}/docview/{paper_id}":
        raise RuntimeError(f"ATAI did not retain the canonical record path for {paper_id}.")
    if payload.get("titleHasExactSource") is not True or payload.get("productLinkExact") is not True:
        raise RuntimeError(f"ATAI did not prove exact Index scope for {paper_id}.")
    title = clean_text(payload.get("title"))
    if payload.get("titleCount") != 1 or title.casefold() != expected["title"].casefold():
        raise RuntimeError(f"ATAI title readback disagreed for {paper_id}.")
    if payload.get("panelCount") != 1 or clean_text(payload.get("indexingPanelLabel")) != "Search with indexing terms":
        raise RuntimeError(f"ATAI indexing panel was missing or ambiguous for {paper_id}.")
    raw_groups = payload.get("indexingGroups")
    if not isinstance(raw_groups, list) or not raw_groups:
        raise RuntimeError(f"ATAI exposed no indexing groups for {paper_id}.")
    normalized_groups: list[dict[str, Any]] = []
    seen_fields: set[str] = set()
    for raw_group in raw_groups:
        if not isinstance(raw_group, dict):
            raise RuntimeError(f"ATAI exposed a malformed indexing group for {paper_id}.")
        field = clean_text(raw_group.get("field")).upper()
        terms = raw_group.get("terms")
        if not field or field in seen_fields or not isinstance(terms, list) or not terms:
            raise RuntimeError(f"ATAI exposed an invalid indexing group for {paper_id}.")
        normalized_terms = [clean_text(term) for term in terms]
        if (
            any(not term or len(term) > 512 for term in normalized_terms)
            or len(set(normalized_terms)) != len(normalized_terms)
        ):
            raise RuntimeError(f"ATAI exposed invalid or duplicate indexing terms for {paper_id}.")
        seen_fields.add(field)
        normalized_groups.append({"field": field, "terms": normalized_terms})
    subject_groups = [group for group in normalized_groups if group["field"] == "SUBJECT"]
    if len(subject_groups) != 1:
        raise RuntimeError(f"ATAI exposed no unique SUBJECT indexing group for {paper_id}.")
    normalized_terms = subject_groups[0]["terms"]
    return {
        "reading_aid_entry": expected["reading_aid_entry"],
        "paper_id": paper_id,
        "title": title,
        "canonical_url": f"https://www.proquest.com/{SOURCE_SITE}/docview/{paper_id}",
        "source_scope_proof": "exact_atai_product_title_and_product_link",
        "rendered_indexing_field": "SUBJECT",
        "rendered_indexing_terms": normalized_terms,
        "rendered_indexing_term_count": len(normalized_terms),
        "other_rendered_indexing_fields": [
            group for group in normalized_groups if group["field"] != "SUBJECT"
        ],
    }


async def harvest(output_path: Path, failure_path: Path, timeout_seconds: float) -> None:
    adapter = load_adapter()
    from playwright.async_api import async_playwright

    started_at = adapter.utc_now()
    lease = None
    passes: list[list[dict[str, Any]]] = []
    try:
        async with async_playwright() as playwright:
            try:
                lease = await adapter.open_proquest_owned_page(
                    playwright,
                    cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                    target_id=None,
                    headless=False,
                    timeout_seconds=timeout_seconds,
                    chrome_executable=None,
                )
                for _pass_number in (1, 2):
                    pass_records: list[dict[str, Any]] = []
                    for expected in SELECTED_RECORDS:
                        await adapter.navigate(
                            lease.page,
                            f"https://www.proquest.com/{SOURCE_SITE}/docview/{expected['paper_id']}",
                            timeout_seconds,
                        )
                        await adapter.wait_for_proquest_detail(
                            lease.page,
                            timeout_seconds=timeout_seconds,
                        )
                        payload = await lease.page.evaluate(INDEXING_STATE_SCRIPT)
                        pass_records.append(parse_indexing_state(payload, expected))
                    passes.append(pass_records)
            finally:
                await adapter.close_proquest_owned_page(lease)
    except Exception as error:
        failure = {
            "schema_version": "atai-controlled-vocabulary-assignment-failure/v1",
            "source": SOURCE_NAME,
            "pilot": "004",
            "status": "error",
            "do_not_merge": True,
            "started_at_utc": started_at,
            "failed_at_utc": adapter.utc_now(),
            "stage": "source_rendered_indexing_term_harvest",
            "error_type": type(error).__name__,
            "error": clean_text(error),
            "selected_record_ids": [record["paper_id"] for record in SELECTED_RECORDS],
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False) + "\n")
        raise

    if len(passes) != 2 or passes[0] != passes[1]:
        raise RuntimeError("ATAI indexing assignments changed across two complete passes.")

    active_records = passes[1]
    frequencies = Counter(
        term
        for record in active_records
        for term in record["rendered_indexing_terms"]
    )
    artifact = {
        "schema_version": "atai-controlled-vocabulary-assignment-harvest/v1",
        "source": SOURCE_NAME,
        "source_id": "proquest_aerospace_index",
        "platform": "ProQuest",
        "pilot": "004",
        "purpose": "Harvest source-rendered indexing terms from seven user-selected Pilot 003 records before testing Technology Thesaurus inclusion.",
        "status": "complete_two_pass_readback",
        "do_not_merge": True,
        "started_at_utc": started_at,
        "completed_at_utc": adapter.utc_now(),
        "method": {
            "route": "canonical ATAI record detail pages",
            "record_selection": "User-selected entries 02, 03, 07, 11, 14, 18, and 37 from the temporary reading aid, resolved to Pilot 003 stable IDs.",
            "passes": 2,
            "stable_assignment_readback": True,
            "captured_surface": "Search with indexing terms",
            "rendered_field": "SUBJECT",
            "scope_proof": "Exact ATAI document title and product-home link on every record page.",
            "privacy_boundary": "Only canonical numeric record IDs, public titles, rendered field labels, and rendered indexing terms are retained.",
        },
        "interpretation_boundary": {
            "assignment_evidence": "The terms are visibly assigned under the record-level SUBJECT indexing field.",
            "controlled_vocabulary_state": "These assignments are not yet proved to be exact Technology Thesaurus MAINSUBJECT descriptors.",
            "eligibility_state": "User selection supplies known-item relevance for this vocabulary pilot only. It is not final review screening.",
        },
        "selected_record_count": len(active_records),
        "records": active_records,
        "term_frequency": [
            {"term": term, "assigned_record_count": count}
            for term, count in sorted(frequencies.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "unique_rendered_indexing_term_count": len(frequencies),
        "pass_reconciliation": {
            "pass_1_record_ids": [record["paper_id"] for record in passes[0]],
            "pass_2_record_ids": [record["paper_id"] for record in passes[1]],
            "ordered_records_equal": passes[0] == passes[1],
            "ordered_assignments_equal": passes[0] == passes[1],
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--failure-output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    asyncio.run(harvest(args.output, args.failure_output, args.timeout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
