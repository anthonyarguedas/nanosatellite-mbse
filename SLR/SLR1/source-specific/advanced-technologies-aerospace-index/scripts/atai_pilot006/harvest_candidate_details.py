#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Harvest safe detail metadata for IF-only and language-excluded records."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = Path.home() / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
ALLOWED_FIELDS = {
    "Subject",
    "Classification",
    "Title",
    "Publication title",
    "Publication year",
    "Publication date",
    "DOI",
    "Summary language",
    "Language of publication",
    "Document type",
    "Source type",
    "Country of publication",
    "Publication subject",
    "ISSN",
    "Accession number",
    "ProQuest document ID",
}

FIELD_SCRIPT = r"""
() => {
  const normalize = value => String(value || "").replace(/[\s\u200e\u200f]+/g, " ").trim();
  const visible = element => Boolean(element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length));
  const rows = Array.from(document.querySelectorAll(".display_record_indexing_row")).filter(visible);
  const fields = rows.map(row => {
    const name = row.querySelector(".display_record_indexing_fieldname");
    if (!name) return null;
    const field = normalize(name.textContent);
    const clone = row.cloneNode(true);
    for (const node of Array.from(clone.querySelectorAll(".display_record_indexing_fieldname"))) node.remove();
    return {field, value: normalize(clone.innerText || clone.textContent)};
  }).filter(Boolean);
  const productLinks = Array.from(document.querySelectorAll(
    "a[aria-label='Advanced Technologies & Aerospace Index Product Home page']"
  )).filter(visible);
  const match = location.pathname.match(/^\/ataindex\/docview\/(\d+)(?:\/|$)/i);
  return {
    host: location.hostname,
    path: location.pathname,
    paperId: match ? match[1] : "",
    titleHasExactSource: document.title.includes("Advanced Technologies & Aerospace Index"),
    productLinkExact: productLinks.length === 1,
    fields,
  };
}
"""


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot006_detail_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def ids_from_inputs(if_path: Path, language_path: Path) -> tuple[list[str], set[str], set[str]]:
    if_data = json.loads(if_path.read_text())
    language = json.loads(language_path.read_text())
    if_ids = if_data.get("candidate_only_union_ids", [])
    language_ids = language.get("stable_ids_in_source_order", [])
    if not isinstance(if_ids, list) or not isinstance(language_ids, list):
        raise RuntimeError("Candidate ID inputs are malformed.")
    union = []
    for paper_id in [*if_ids, *language_ids]:
        paper_id = clean(paper_id)
        if not paper_id.isdigit():
            raise RuntimeError("Candidate input contains an invalid stable ID.")
        if paper_id not in union:
            union.append(paper_id)
    return union, set(if_ids), set(language_ids)


def parse_fields(payload: Any, paper_id: str) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise RuntimeError(f"Malformed detail fields for {paper_id}.")
    if (
        clean(payload.get("host")).casefold() != "www.proquest.com"
        or payload.get("path") != f"/ataindex/docview/{paper_id}"
        or payload.get("paperId") != paper_id
        or payload.get("titleHasExactSource") is not True
        or payload.get("productLinkExact") is not True
    ):
        raise RuntimeError(f"Exact ATAI detail scope failed for {paper_id}.")
    result = {}
    for item in payload.get("fields", []):
        if not isinstance(item, dict):
            continue
        field = clean(item.get("field"))
        value = clean(item.get("value"))
        if field in ALLOWED_FIELDS and value:
            if field in result and result[field] != value:
                raise RuntimeError(f"Duplicate detail field {field} for {paper_id}.")
            result[field] = value
    return result


async def harvest(if_path: Path, language_path: Path, output_path: Path) -> None:
    ids, if_ids, language_ids = ids_from_inputs(if_path, language_path)
    adapter = load_adapter()
    from playwright.async_api import async_playwright

    passes = []
    async with async_playwright() as playwright:
        lease = None
        try:
            lease = await adapter.open_proquest_owned_page(
                playwright,
                cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                target_id=None,
                headless=False,
                timeout_seconds=180,
                chrome_executable=None,
            )
            for _pass_number in (1, 2):
                records = []
                for paper_id in ids:
                    await adapter.navigate(
                        lease.page,
                        f"https://www.proquest.com/ataindex/docview/{paper_id}",
                        180,
                    )
                    detail = await adapter.wait_for_proquest_detail(
                        lease.page,
                        timeout_seconds=180,
                    )
                    fields = parse_fields(await lease.page.evaluate(FIELD_SCRIPT), paper_id)
                    records.append({
                        "paper_id": paper_id,
                        "routes": [
                            route
                            for route, membership in (
                                ("if_candidate_only", paper_id in if_ids),
                                ("language_excluded", paper_id in language_ids),
                            )
                            if membership
                        ],
                        "title": detail.title,
                        "authors": detail.authors,
                        "publication": detail.publication,
                        "abstract": detail.abstract,
                        "abstract_available": bool(detail.abstract),
                        "fields": fields,
                        "canonical_url": f"https://www.proquest.com/ataindex/docview/{paper_id}",
                    })
                passes.append(records)
        finally:
            if lease is not None:
                await adapter.close_proquest_owned_page(lease)
    if passes[0] != passes[1]:
        raise RuntimeError("Candidate detail metadata changed across two passes.")
    artifact = {
        "schema_version": "atai-pilot-006-candidate-detail-harvest/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "006",
        "attempt": "retry6",
        "status": "complete_two_pass_detail_readback",
        "do_not_merge": True,
        "input_if_reconciliation": str(if_path),
        "input_language_reconciliation": str(language_path),
        "record_count": len(ids),
        "if_candidate_count": len(if_ids),
        "language_excluded_count": len(language_ids),
        "passes": 2,
        "ordered_details_equal": True,
        "records": passes[1],
        "interpretation_boundary": "Source detail metadata and abstracts support search-method decisions. They are not final eligibility or full-text language decisions.",
    }
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--if-reconciliation", type=Path, required=True)
    parser.add_argument("--language-reconciliation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(harvest(args.if_reconciliation, args.language_reconciliation, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
