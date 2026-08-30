#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Capture visible Wiley title/abstract metadata for a fixed DOI ledger.

This is a non-final local metadata check.  It never removes a source ID when a
field is absent or when a detail page cannot be read.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any
from urllib.parse import quote
import urllib.request


ADAPTER_PATH = Path(
    "/Users/antho/agent-tools/internet/skills/browser/scripts/"
    "search_wiley_online_library.py"
)

DETAIL_SNAPSHOT_JS = r"""
() => {
  const compact = value => String(value || '').replace(/\s+/g, ' ').trim();
  const metas = {};
  for (const node of document.querySelectorAll('meta[name], meta[property]')) {
    const key = (node.getAttribute('name') || node.getAttribute('property') || '').toLowerCase();
    const value = compact(node.getAttribute('content'));
    if (key && value && !metas[key]) metas[key] = value;
  }
  const body = compact(document.body?.innerText || '');
  const lower = body.toLowerCase();
  const blocked = ['just a moment', 'performing security verification', 'verify you are human',
    'captcha', 'access denied'].some(marker => lower.includes(marker));
  const selectors = [
    '.article-section__abstract',
    '.article-section__content .abstract',
    'section.abstract',
    '#abstract',
    '.abstract'
  ];
  let abstract = '';
  let abstractSelector = '';
  for (const selector of selectors) {
    const node = document.querySelector(selector);
    const value = compact(node?.innerText || node?.textContent || '');
    if (value) { abstract = value; abstractSelector = selector; break; }
  }
  let abstractSource = abstract ? 'visible_detail_dom' : 'not_exposed';
  if (!abstract && metas['citation_abstract']) {
    abstract = metas['citation_abstract'];
    abstractSource = 'citation_abstract_meta';
  }
  const title = metas['citation_title'] || compact(document.querySelector('h1')?.textContent || document.title);
  const doi = metas['citation_doi'] || metas['dc.identifier'] || '';
  return {
    blocked,
    title,
    detail_doi: doi,
    abstract,
    abstract_source: abstractSource,
    abstract_selector: abstractSelector,
    ready: Boolean(title || doi || abstract),
  };
}
"""


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("wiley_pilot_detail_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, staged_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    staged = Path(staged_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staged, path)
    except BaseException:
        staged.unlink(missing_ok=True)
        raise


async def target_id_for_page(page: Any) -> str:
    session = await page.context.new_cdp_session(page)
    try:
        value = await session.send("Target.getTargetInfo")
    finally:
        await session.detach()
    target_id = value.get("targetInfo", {}).get("targetId")
    if not isinstance(target_id, str) or not target_id:
        raise RuntimeError("Could not identify the metadata collector's owned page")
    return target_id


async def close_target(cdp_url: str, target_id: str) -> bool:
    root = cdp_url.rstrip("/")

    def ids() -> set[str]:
        with urllib.request.urlopen(f"{root}/json/list", timeout=15) as response:
            values = json.load(response)
        return {
            item["id"]
            for item in values
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    try:
        if target_id not in await asyncio.to_thread(ids):
            return True
        await asyncio.to_thread(
            lambda: urllib.request.urlopen(
                f"{root}/json/close/{target_id}", timeout=15
            ).read()
        )
        for _ in range(20):
            await asyncio.sleep(0.1)
            if target_id not in await asyncio.to_thread(ids):
                return True
    except Exception:
        return False
    return False


def source_records(paths: list[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    names: list[str] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") != "success":
            raise RuntimeError(f"Input ledger is not successful: {path}")
        names.append(path.name)
        for record in payload.get("records", []):
            doi = record.get("doi")
            if not isinstance(doi, str) or not doi or doi in seen:
                continue
            seen.add(doi)
            output.append(
                {
                    "doi": doi,
                    "source_card_title": record.get("title", ""),
                    "source_card_title_status": "two_pass_rendered_card",
                    "source_card_date": record.get("source_publication_date", ""),
                }
            )
    return output, names


async def wait_for_detail(page: Any, *, timeout_seconds: float) -> dict[str, Any]:
    started = asyncio.get_running_loop().time()
    deadline = started + timeout_seconds
    challenge_deadline = started + max(timeout_seconds, 90.0)
    last: dict[str, Any] = {}
    while asyncio.get_running_loop().time() < deadline:
        value = await page.evaluate(DETAIL_SNAPSHOT_JS)
        last = value if isinstance(value, dict) else {}
        if last.get("blocked"):
            deadline = max(deadline, challenge_deadline)
        elif last.get("ready"):
            return last
        await asyncio.sleep(0.25)
    if last.get("blocked"):
        raise RuntimeError("Wiley detail page retained a Cloudflare/CAPTCHA/access challenge")
    raise RuntimeError("Wiley detail page did not expose a readable metadata state")


async def capture(
    adapter: Any, records: list[dict[str, Any]], *, timeout_seconds: float
) -> tuple[list[dict[str, Any]], bool]:
    from playwright.async_api import async_playwright

    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    lease: Any | None = None
    target_id: str | None = None
    results: list[dict[str, Any]] = []
    complete = True
    try:
        async with async_playwright() as playwright:
            lease = await adapter.open_owned_chrome_page(
                playwright,
                cdp_url=cdp_url,
                headless=False,
                timeout_seconds=timeout_seconds,
                chrome_executable=None,
            )
            page = lease.page
            target_id = await target_id_for_page(page)
            for index, seed in enumerate(records, start=1):
                doi = seed["doi"]
                try:
                    response = await page.goto(
                        "https://onlinelibrary.wiley.com/doi/" + quote(doi, safe="/"),
                        wait_until="commit",
                        timeout=int(timeout_seconds * 1000),
                    )
                    snapshot = await wait_for_detail(page, timeout_seconds=timeout_seconds)
                    results.append(
                        {
                            **seed,
                            "rank": index,
                            "detail_status": "success",
                            "detail_http_status": response.status if response else None,
                            "detail_title": snapshot.get("title", ""),
                            "detail_doi": snapshot.get("detail_doi", ""),
                            "abstract": snapshot.get("abstract", ""),
                            "abstract_status": snapshot.get("abstract_source", "not_exposed"),
                            "abstract_selector": snapshot.get("abstract_selector", ""),
                        }
                    )
                except Exception as error:
                    text = " ".join(str(error).split())[:500]
                    results.append(
                        {
                            **seed,
                            "rank": index,
                            "detail_status": "error",
                            "detail_http_status": None,
                            "detail_title": "",
                            "detail_doi": "",
                            "abstract": "",
                            "abstract_status": "not_available",
                            "abstract_selector": "",
                            "error_type": type(error).__name__,
                            "error": text,
                        }
                    )
                    # A persistent access challenge is a source route blocker,
                    # not an invitation to keep replaying detail requests.
                    if "Cloudflare/CAPTCHA/access challenge" in text:
                        complete = False
                        for pending in records[index:]:
                            results.append(
                                {
                                    **pending,
                                    "rank": len(results) + 1,
                                    "detail_status": "not_attempted_after_access_blocker",
                                    "detail_http_status": None,
                                    "detail_title": "",
                                    "detail_doi": "",
                                    "abstract": "",
                                    "abstract_status": "not_available",
                                    "abstract_selector": "",
                                }
                            )
                        break
            if not await close_target(cdp_url, target_id):
                raise RuntimeError("Could not verify closure of the metadata collector's owned page")
            target_id = None
    finally:
        if target_id is not None and not await close_target(cdp_url, target_id):
            raise RuntimeError("Could not verify closure of the metadata collector's owned page")
    return results, complete


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", action="append", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    args = parser.parse_args()
    records, input_names = source_records(args.ledger)
    base = {
        "schema_version": "wiley-online-library-pilot-detail-metadata/v1",
        "pilot": "003",
        "source": "Wiley Online Library",
        "do_not_merge": True,
        "purpose": (
            "Local title/abstract confirmation for exact-pair diagnostics. "
            "No missing or nonmatching field excludes a DOI from its source ledger."
        ),
        "input_ledgers": input_names,
        "requested_records": len(records),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    try:
        adapter = load_adapter()
        captured, complete = asyncio.run(
            capture(adapter, records, timeout_seconds=args.timeout_seconds)
        )
        payload = {
            **base,
            "status": "success" if complete else "partial_access_blocked",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "records": captured,
            "record_sequence_sha256": sha256([record["doi"] for record in captured]),
            "abstracts_exposed": sum(bool(record.get("abstract")) for record in captured),
            "detail_errors": sum(record.get("detail_status") == "error" for record in captured),
        }
    except BaseException as error:
        payload = {
            **base,
            "status": "error",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "records": [],
            "failure": {
                "error_type": type(error).__name__,
                "error": " ".join(str(error).split())[:700],
            },
        }
    atomic_json(args.output_path, payload)
    print(
        json.dumps(
            {
                "output": str(args.output_path),
                "status": payload["status"],
                "records": len(payload["records"]),
                "abstracts_exposed": payload.get("abstracts_exposed"),
            }
        )
    )
    return 0 if payload["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
