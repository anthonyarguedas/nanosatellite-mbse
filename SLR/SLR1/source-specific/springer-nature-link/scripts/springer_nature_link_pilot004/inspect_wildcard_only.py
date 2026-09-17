#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Capture bounded visible contexts for Springer Pilot 004 wildcard-only paths."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from build_plan import PILOT_ROOT
from run_pilot import DEFAULT_ADAPTER, load_adapter, write_json_create_only

DEFAULT_PLAN = PILOT_ROOT / "searches" / "wildcard-only-investigation-plan.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "wildcard-only-investigation.json"

INTERPRETATIONS = {
    "/article/10.1038/s44359-026-00173-2": {
        "within_intended_population_meaning": True,
        "basis": (
            "The visible body uses smallsats as aerospace high-specific-power "
            "applications. This is the intended SmallSat meaning."
        ),
    },
    "/chapter/10.1007/978-3-031-96146-5_11": {
        "within_intended_population_meaning": True,
        "basis": (
            "The visible body uses the misspelling cubesates for an inter-satellite "
            "link and also names CubeSat, CubeSats, and NanoSats in the same report."
        ),
    },
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


async def inspect(args: argparse.Namespace) -> dict[str, Any]:
    plan = load_json(args.plan)
    if (
        plan.get("schema_version")
        != "springer-nature-link-pilot004-wildcard-only-plan/v1"
        or not isinstance(plan.get("events"), list)
        or len(plan["events"]) != 2
    ):
        raise RuntimeError("Wildcard-only investigation plan is invalid")
    adapter = load_adapter(args.adapter)
    from playwright.async_api import async_playwright

    findings = []
    async with async_playwright() as playwright:
        for event in plan["events"]:
            lease = None
            try:
                lease = await adapter.open_springer_owned_page(
                    playwright,
                    cdp_url=args.cdp_url,
                    headless=False,
                    timeout_seconds=60.0,
                    chrome_executable=None,
                )
                navigation = await adapter.navigate_to_springer_detail(
                    lease.page,
                    event["source_card_path"],
                    60.0,
                    allow_changed_detail_route=False,
                )
                page_state = await lease.page.evaluate(
                    r"""
                    () => {
                      const normalize = value => String(value || "")
                        .replace(/\s+/g, " ").trim();
                      const titles = Array.from(document.querySelectorAll("h1"))
                        .filter(element => element.offsetWidth || element.offsetHeight)
                        .map(element => normalize(element.innerText || element.textContent))
                        .filter(Boolean);
                      const canonicals = Array.from(document.querySelectorAll(
                        "head link[rel~='canonical']"
                      )).map(element => String(element.href || "")).filter(Boolean);
                      return {titles, canonicals, url: window.location.href};
                    }
                    """
                )
                expected_title = adapter.normalize_springer_visible_title(
                    event["source_card_title"]
                )
                if (
                    not isinstance(page_state, dict)
                    or page_state.get("titles") != [expected_title]
                    or page_state.get("url") != navigation.final_url
                    or not isinstance(page_state.get("canonicals"), list)
                    or len(page_state["canonicals"]) != 1
                ):
                    raise adapter.SpringerProtocolError(
                        "Wildcard-only detail page lacked its expected visible identity"
                    )
                canonical_link = page_state["canonicals"][0]
                matches = await lease.page.evaluate(
                    r"""
                    roots => {
                      const normalize = value => String(value || "")
                        .replace(/\s+/g, " ").trim();
                      const text = normalize(document.body && document.body.innerText);
                      const output = [];
                      for (const root of roots) {
                        const expression = new RegExp(
                          `(^|[^A-Za-z])(${root}[A-Za-z]*)`, "gi"
                        );
                        for (const match of text.matchAll(expression)) {
                          const token = match[2];
                          const start = match.index + match[1].length;
                          output.push({
                            root,
                            token,
                            context: text.slice(
                              Math.max(0, start - 120),
                              Math.min(text.length, start + token.length + 120)
                            )
                          });
                        }
                      }
                      return output;
                    }
                    """,
                    plan["roots"],
                )
                if not isinstance(matches, list) or not matches:
                    raise adapter.SpringerProtocolError(
                        "Wildcard-only detail page exposed no planned root context"
                    )
                unique = []
                seen = set()
                for item in matches:
                    if not isinstance(item, dict):
                        raise adapter.SpringerProtocolError(
                            "Wildcard context evidence was malformed"
                        )
                    root = adapter.clean_text(item.get("root"))
                    token = adapter.clean_text(item.get("token"))
                    context = adapter.remove_email_addresses(item.get("context"))
                    if (
                        root not in plan["roots"]
                        or re.fullmatch(re.escape(root) + r"[A-Za-z]*", token, re.I)
                        is None
                        or not context
                        or len(context) > 300
                    ):
                        raise adapter.SpringerProtocolError(
                            "Wildcard context evidence left its bounded schema"
                        )
                    identity = (root.casefold(), token.casefold(), context)
                    if identity not in seen:
                        seen.add(identity)
                        unique.append(
                            {"root": root, "token": token, "context": context}
                        )
                path = event["source_card_path"]
                interpretation = INTERPRETATIONS[path]
                findings.append(
                    {
                        "source_card_path": path,
                        "source_card_url": adapter.springer_content_url(path),
                        "resolved_detail_url": navigation.final_url,
                        "canonical_link": canonical_link,
                        "canonical_link_matches_link_route": (
                            canonical_link == navigation.final_url
                        ),
                        "adapter_strict_detail_acceptance": (
                            canonical_link == navigation.final_url
                        ),
                        "route_alias": navigation.route_alias,
                        "title": expected_title,
                        "visible_matches": unique,
                        **interpretation,
                    }
                )
            finally:
                await adapter.close_springer_owned_page(lease)
    return {
        "schema_version": "springer-nature-link-pilot004-wildcard-only-investigation/v1",
        "pilot": "004",
        "source": "Springer Nature Link",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
        "plan": str(args.plan.relative_to(PILOT_ROOT)),
        "plan_sha256": file_sha256(args.plan),
        "adapter": {
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": file_sha256(args.adapter),
        },
        "findings": findings,
        "all_within_intended_population_meaning": all(
            item["within_intended_population_meaning"] for item in findings
        ),
        "completed_at": now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    args = parser.parse_args()
    result = asyncio.run(inspect(args))
    write_json_create_only(args.output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
