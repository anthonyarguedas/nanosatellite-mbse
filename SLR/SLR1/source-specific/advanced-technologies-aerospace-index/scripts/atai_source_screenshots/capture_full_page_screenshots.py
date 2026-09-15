#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Capture full-page ATAI search-form and result-page screenshots."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_interface_screenshot_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> dict[str, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{path} is not a valid PNG.")
    width, height = struct.unpack(">II", data[16:24])
    return {"width": width, "height": height}


async def mark_sensitive_visible_text(page: Any) -> int:
    """Mark only visible leaf elements containing an email address for masking."""
    value = await page.evaluate(
        r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const email = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i;
  const candidates = Array.from(document.querySelectorAll("body *")).filter(visible);
  const leaves = candidates.filter(element => {
    const text = String(element.innerText || element.textContent || "").trim();
    return email.test(text) && !Array.from(element.children).some(child => {
      const childText = String(child.innerText || child.textContent || "").trim();
      return visible(child) && email.test(childText);
    });
  });
  for (const element of leaves) element.setAttribute("data-interface-screenshot-redact", "true");
  return leaves.length;
}
"""
    )
    if not isinstance(value, int) or value < 0:
        raise RuntimeError("Screenshot redaction scan returned invalid evidence.")
    return value


async def screenshot(page: Any, path: Path) -> int:
    redaction_count = await mark_sensitive_visible_text(page)
    masks = []
    if redaction_count:
        masks.append(page.locator("[data-interface-screenshot-redact='true']"))
    await page.evaluate("() => window.scrollTo(0, 0)")
    await page.screenshot(
        path=str(path),
        full_page=True,
        animations="disabled",
        caret="hide",
        mask=masks,
        mask_color="#000000",
    )
    return redaction_count


async def capture(
    raw_query: str,
    search_screenshot: Path,
    results_screenshot: Path,
    receipt_path: Path,
    timeout_seconds: float,
) -> None:
    adapter = load_adapter()
    command_query = adapter.build_command_query(
        raw_query,
        year_start=None,
        year_end=None,
        language="English",
    )
    date_restriction = adapter.resolve_date_restriction()
    from playwright.async_api import async_playwright

    started_at = adapter.utc_now()
    lease = None
    snapshot: set[str] | None = None
    restore_needed = False
    restoration_verified = False
    result_page = None
    search_redactions = 0
    results_redactions = 0
    primary_error: BaseException | None = None
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
            await lease.page.set_viewport_size({"width": 1440, "height": 1000})

            async def reassert() -> None:
                adapter.assert_owned_proquest_page(lease)
                await adapter.reassert_owned_chrome_page_target(lease)

            snapshot = await adapter.snapshot_database_selection(
                lease.page,
                timeout_seconds=timeout_seconds,
                attached_cdp=True,
                ownership_reassertion=reassert,
            )
            restore_needed = snapshot != {adapter.TARGET_DATABASE_LABEL}
            await adapter.prepare_exact_index_selection(
                lease.page,
                timeout_seconds=timeout_seconds,
                attached_cdp=True,
                snapshot=snapshot,
                ownership_reassertion=reassert,
            )
            await adapter.submit_database_selection(
                lease.page,
                timeout_seconds,
                ownership_reassertion=reassert,
            )
            await adapter.wait_for_exact_index_route(
                lease.page,
                timeout_seconds=timeout_seconds,
                ownership_reassertion=reassert,
            )
            await adapter.navigate(lease.page, adapter.COMMAND_LINE_URL, timeout_seconds)
            await adapter.dismiss_restore_session_overlay(
                lease.page,
                timeout_seconds=timeout_seconds,
                ownership_reassertion=reassert,
            )
            await adapter.wait_for_exact_index_route(
                lease.page,
                timeout_seconds=timeout_seconds,
                ownership_reassertion=reassert,
            )
            await adapter.configure_atai_command_form(
                lease.page,
                query=command_query,
                timeout_seconds=timeout_seconds,
                date_restriction=date_restriction,
                complete_mode=False,
            )
            field = lease.page.locator("#searchTerm:visible")
            submit = lease.page.locator("#submit_7:visible")
            if await field.count() != 1 or await submit.count() != 1:
                raise RuntimeError("ATAI Command Line controls were unavailable.")
            await field.fill(command_query)
            await adapter._wait_for_atai_command_form(
                lease.page,
                timeout_seconds=timeout_seconds,
                expected_query=command_query,
                require_frozen=True,
            )
            search_screenshot.parent.mkdir(parents=True, exist_ok=True)
            search_redactions = await screenshot(lease.page, search_screenshot)

            async with lease.page.expect_navigation(
                wait_until="domcontentloaded",
                timeout=adapter.milliseconds(timeout_seconds),
            ):
                await submit.click()
            result_page = await adapter.wait_for_proquest_page(
                lease.page,
                query=command_query,
                include_records=True,
                expected_page_number=1,
                timeout_seconds=timeout_seconds,
                complete_mode=False,
                ownership_reassertion=reassert,
            )
            expected_rows = min(result_page.total, adapter.REQUIRED_PAGE_SIZE)
            if result_page.total < 1 or len(result_page.rows) != expected_rows:
                raise RuntimeError("ATAI representative screenshot result rows did not reconcile.")
            results_redactions = await screenshot(lease.page, results_screenshot)
        except BaseException as error:
            primary_error = error
        finally:
            if lease is not None and snapshot is not None and restore_needed:
                try:
                    await adapter.restore_database_selection(
                        lease.page,
                        snapshot,
                        timeout_seconds=timeout_seconds,
                    )
                except BaseException as restore_error:
                    primary_error = restore_error
                else:
                    restoration_verified = True
            elif snapshot is not None:
                restoration_verified = True
            try:
                await adapter.close_proquest_owned_page(lease)
            except BaseException as cleanup_error:
                primary_error = cleanup_error
    if primary_error is not None:
        raise primary_error
    if result_page is None or not restoration_verified:
        raise RuntimeError("ATAI screenshot capture did not finish or restore scope.")

    receipt = {
        "schema_version": "atai-interface-screenshot-receipt/v1",
        "source": adapter.SOURCE_NAME,
        "evidence_kind": "general_interface_documentation",
        "status": "complete",
        "started_at_utc": started_at,
        "completed_at_utc": adapter.utc_now(),
        "requested_query": raw_query,
        "executed_query": command_query,
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
        },
        "query_sha256": hashlib.sha256(command_query.encode()).hexdigest(),
        "controls": {
            "database": adapter.TARGET_DATABASE_LABEL,
            "language": "LA(English)",
            "publication_date": "All dates",
            "sort": "DateAsc",
            "page_size": 20,
            "document_type": None,
            "peer_reviewed": False,
            "spelling_variants": False,
            "form_variants": False,
            "show_variants": False,
        },
        "source_total": result_page.total,
        "source_rows_on_page": len(result_page.rows),
        "scope_restoration_verified": restoration_verified,
        "privacy": {
            "browser_chrome_captured": False,
            "complete_result_url_retained": False,
            "session_identifiers_retained": False,
            "email_elements_masked_on_search_page": search_redactions,
            "email_elements_masked_on_results_page": results_redactions,
        },
        "screenshots": [
            {
                "page": "configured_search_form",
                "path": search_screenshot.name,
                "sha256": sha256(search_screenshot),
                **png_dimensions(search_screenshot),
            },
            {
                "page": "first_results_page",
                "path": results_screenshot.name,
                "sha256": sha256(results_screenshot),
                **png_dimensions(results_screenshot),
            },
        ],
        "limitation": "These screenshots document the current general ATAI interface. They are not pilot or final-search artifacts.",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default='NOFT("CubeSat")')
    parser.add_argument("--search-screenshot", type=Path, required=True)
    parser.add_argument("--results-screenshot", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()
    asyncio.run(
        capture(
            args.query,
            args.search_screenshot,
            args.results_screenshot,
            args.receipt,
            args.timeout,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
