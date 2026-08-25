#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""Read-only, redacted P02 controller-anchor continuity inspector."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_CDP_URL = "http://127.0.0.1:9237"


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def is_new_tab_url(url: str) -> bool:
    value = (url or "").strip().lower()
    return value in {"", "about:blank", "chrome://newtab/", "chrome://new-tab-page/"} or value.startswith(
        "chrome-search://local-ntp/"
    )


async def target_id_for(context: Any, page: Any) -> str | None:
    session = await context.new_cdp_session(page)
    try:
        payload = await session.send("Target.getTargetInfo")
        info = payload.get("targetInfo") if isinstance(payload, dict) else None
        target_id = info.get("targetId") if isinstance(info, dict) else None
        return target_id if isinstance(target_id, str) else None
    finally:
        try:
            await session.detach()
        except Exception:
            pass


async def inspect(anchor_id_file: Path) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": "slr1-engineering-village-browser-postflight/v1",
        "pilot_id": "S-D04-P02-20260824T130842-0400",
        "endpoint_class": "dedicated_loopback_9237",
        "read_only": True,
        "safe_projection_only": True,
        "retention_exclusions": ["raw_target_id", "url", "title", "page_text", "html", "cookie", "session_or_search_identifier"],
        "browser_context_count": None,
        "page_target_count": None,
        "sole_page_is_private_controller_anchor": False,
        "sole_page_new_tab_class": False,
        "anchor_continuity_verified": False,
        "error_category": None,
        "captured_at": timestamp(),
    }
    try:
        private_anchor_id = anchor_id_file.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"[A-Fa-f0-9]{32}", private_anchor_id):
            raise ValueError
    except Exception:
        receipt["error_category"] = "invalid_anchor_input"
        receipt["ended_at"] = timestamp()
        return receipt

    playwright: Any | None = None
    try:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(ALLOWED_CDP_URL)
        contexts = tuple(browser.contexts)
        receipt["browser_context_count"] = len(contexts)
        if len(contexts) != 1:
            receipt["error_category"] = "ambiguous_browser_context"
            return receipt
        pages = tuple(contexts[0].pages)
        receipt["page_target_count"] = len(pages)
        if len(pages) != 1:
            receipt["error_category"] = "page_count_mismatch"
            return receipt
        target_id = await target_id_for(contexts[0], pages[0])
        receipt["sole_page_is_private_controller_anchor"] = target_id == private_anchor_id
        receipt["sole_page_new_tab_class"] = is_new_tab_url(pages[0].url)
        receipt["anchor_continuity_verified"] = (
            receipt["sole_page_is_private_controller_anchor"] and receipt["sole_page_new_tab_class"]
        )
        if not receipt["anchor_continuity_verified"]:
            receipt["error_category"] = "anchor_continuity_mismatch"
    except Exception:
        receipt["error_category"] = "read_only_inspection_failed"
    finally:
        if playwright is not None:
            try:
                await playwright.stop()
            except Exception:
                pass
        receipt["ended_at"] = timestamp()
    return receipt


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    if path.exists():
        raise SystemExit("refusing to overwrite an existing postflight receipt")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect P02 controller anchor without mutating Chrome.")
    parser.add_argument("--cdp-url", required=True)
    parser.add_argument("--anchor-id-file", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    if args.cdp_url != ALLOWED_CDP_URL:
        raise SystemExit("refusing a non-P02 CDP endpoint")
    write_receipt(Path(args.receipt), asyncio.run(inspect(Path(args.anchor_id_file))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
