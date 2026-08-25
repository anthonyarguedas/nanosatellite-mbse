#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""One-shot safe Engineering Village owned-page route probe for S-D04 P02.

This script intentionally connects only to the dedicated P02 endpoint.  It
uses a private anchor identifier only in process memory and writes a safe
boolean/count projection; it never serializes target IDs, URLs, page text,
HTML, cookies, credentials, or session/search values.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_CDP_URL = "http://127.0.0.1:9237"
EXPERT_ROUTE = "https://www.engineeringvillage.com/search/expert.url?database=3"
EXPECTED_HOST = "www.engineeringvillage.com"


SAFE_PROJECTION = r"""
() => {
  const visible = (element) => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const control = (selector) => {
    const element = document.querySelector(selector);
    return { present: Boolean(element), checked: element ? Boolean(element.checked) : null };
  };
  const querySelectors = [
    "textarea[name='searchWord1']",
    "textarea[name='query']",
    "input[name='searchWord1']",
    "input[name='query']"
  ];
  const queryFieldPresent = querySelectors.some((selector) => {
    const element = document.querySelector(selector);
    return Boolean(element && visible(element) && !element.disabled && !element.readOnly);
  });
  const bodyText = String(document.body && document.body.innerText ? document.body.innerText : "").toLowerCase();
  const title = String(document.title || "").toLowerCase();
  let parsed;
  try { parsed = new URL(window.location.href); } catch (_) { parsed = null; }
  const expectedHost = Boolean(parsed && parsed.hostname.toLowerCase() === "www.engineeringvillage.com");
  let urlClass = "unclassified";
  if (parsed && parsed.hostname.toLowerCase() === "www.engineeringvillage.com" && parsed.pathname === "/search/expert.url") {
    urlClass = "engineering_village_expert_route";
  } else if (parsed && parsed.hostname.toLowerCase() === "www.engineeringvillage.com") {
    urlClass = "engineering_village_other_route";
  } else if (parsed) {
    urlClass = "off_expected_host";
  }
  const syntaxDetected = Array.from(document.querySelectorAll("*")).some((element) =>
    visible(element) && String(element.textContent || "").replace(/\s+/g, " ").trim() === "This search contains a syntax error."
  );
  const accessDetected = ["access currently limited", "access denied"].some((marker) => bodyText.includes(marker));
  const loginDetected = bodyText.includes("trouble signing in") ||
    (bodyText.includes("check to see if you have access") && bodyText.includes("institution"));
  const challengeDetected = ["suspicious activity", "captcha", "verify you are human", "unusual traffic"].some(
    (marker) => bodyText.includes(marker)
  );
  const controls = {
    compendex: control("#chkb-cpx"),
    inspec: control("#chkb-ins"),
    all: control("#all-checkb"),
    knovel: control("#chkb-kna"),
    autostemming: control("#chkb-autostem"),
    relevance: control("#radio-relevance")
  };
  return {
    response_safe_url_class: urlClass,
    expected_host: expectedHost,
    expected_expert_title: title.includes("engineering village") && (title.includes("expert") || title.includes("search")),
    access_detected: accessDetected,
    login_detected: loginDetected,
    challenge_detected: challengeDetected,
    syntax_detected: syntaxDetected,
    controls,
    expected_expert_controls_present: Object.values(controls).every((value) => value.present),
    query_field_present: queryFieldPresent
  };
}
"""


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def is_new_tab_url(url: str) -> bool:
    value = (url or "").strip().lower()
    return value in {"", "about:blank", "chrome://newtab/", "chrome://new-tab-page/"} or value.startswith(
        "chrome-search://local-ntp/"
    )


async def target_id_for(context: Any, page: Any) -> str | None:
    """Read one target ID transiently for an in-memory equality check only."""
    session = await context.new_cdp_session(page)
    try:
        payload = await session.send("Target.getTargetInfo")
        target_info = payload.get("targetInfo") if isinstance(payload, dict) else None
        target_id = target_info.get("targetId") if isinstance(target_info, dict) else None
        return target_id if isinstance(target_id, str) else None
    finally:
        try:
            await session.detach()
        except Exception:
            pass


def checked_bool(value: Any) -> bool:
    return value is True


def safe_exception_category(phase: str) -> str:
    allowed = {
        "anchor_input": "invalid_anchor_input",
        "connect": "connection_failed",
        "precondition": "precondition_failed",
        "ownership": "ownership_proof_failed",
        "navigation": "navigation_failed",
        "inspection": "safe_inspection_failed",
        "cleanup": "cleanup_verification_failed",
    }
    return allowed.get(phase, "unexpected_failure")


async def run_probe(anchor_id_file: Path) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": "slr1-engineering-village-g01-safe-receipt/v1",
        "pilot_id": "S-D04-P02-20260824T130842-0400",
        "gate": "G01",
        "captured_at": timestamp(),
        "endpoint_class": "dedicated_loopback_9237",
        "operation": "one_owned_page_normal_route_navigation_without_query_or_control_interaction",
        "navigation_attempt_count": 0,
        "safe_projection_only": True,
        "retention_exclusions": [
            "body_text",
            "html",
            "screenshot",
            "cookie",
            "credential",
            "private_url_or_query",
            "session_or_search_identifier",
            "websocket_url",
            "raw_target_id",
        ],
        "precondition": {
            "exactly_one_browser_context": False,
            "initial_page_count": None,
            "sole_initial_page": False,
            "anchor_matches_private_input": False,
            "anchor_initial_new_tab_class": False,
        },
        "ownership": {
            "context_new_page_called": False,
            "owned_page_distinct_object": False,
            "owned_target_distinct_from_anchor": False,
            "anchor_never_navigated_by_script": True,
        },
        "navigation": {
            "response_status": None,
            "response_safe_url_class": "not_observed",
            "expected_host": False,
            "expected_expert_title": False,
            "access_detected": False,
            "login_detected": False,
            "challenge_detected": False,
            "syntax_detected": False,
            "controls": {},
            "expected_expert_controls_present": False,
            "query_field_present": False,
        },
        "final_continuity": {
            "owned_page_close_attempted": False,
            "owned_page_closed": False,
            "final_page_count": None,
            "anchor_is_sole_final_page": False,
            "anchor_matches_private_input": False,
            "anchor_final_new_tab_class": False,
            "anchor_unchanged": False,
        },
        "result": {"status": "blocked", "healthy": False, "failure_category": None},
    }

    try:
        private_anchor_id = anchor_id_file.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"[A-Fa-f0-9]{32}", private_anchor_id):
            raise ValueError("anchor input")
    except Exception:
        receipt["result"]["failure_category"] = safe_exception_category("anchor_input")
        receipt["ended_at"] = timestamp()
        return receipt

    playwright: Any | None = None
    context: Any | None = None
    anchor: Any | None = None
    owned_page: Any | None = None
    anchor_target_id: str | None = None
    phase = "connect"
    try:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(ALLOWED_CDP_URL)
        contexts = tuple(browser.contexts)
        receipt["precondition"]["exactly_one_browser_context"] = len(contexts) == 1
        if len(contexts) != 1:
            phase = "precondition"
            raise RuntimeError("precondition")
        context = contexts[0]
        initial_pages = tuple(context.pages)
        receipt["precondition"]["initial_page_count"] = len(initial_pages)
        receipt["precondition"]["sole_initial_page"] = len(initial_pages) == 1
        if len(initial_pages) != 1:
            phase = "precondition"
            raise RuntimeError("precondition")

        anchor = initial_pages[0]
        phase = "ownership"
        anchor_target_id = await target_id_for(context, anchor)
        receipt["precondition"]["anchor_matches_private_input"] = anchor_target_id == private_anchor_id
        receipt["precondition"]["anchor_initial_new_tab_class"] = is_new_tab_url(anchor.url)
        if not (
            receipt["precondition"]["anchor_matches_private_input"]
            and receipt["precondition"]["anchor_initial_new_tab_class"]
        ):
            phase = "precondition"
            raise RuntimeError("precondition")

        phase = "ownership"
        owned_page = await context.new_page()
        receipt["ownership"]["context_new_page_called"] = True
        receipt["ownership"]["owned_page_distinct_object"] = owned_page is not anchor
        owned_target_id = await target_id_for(context, owned_page)
        receipt["ownership"]["owned_target_distinct_from_anchor"] = (
            bool(owned_target_id) and bool(anchor_target_id) and owned_target_id != anchor_target_id
        )
        if not (
            receipt["ownership"]["owned_page_distinct_object"]
            and receipt["ownership"]["owned_target_distinct_from_anchor"]
        ):
            raise RuntimeError("ownership")

        phase = "navigation"
        receipt["navigation_attempt_count"] = 1
        response = await owned_page.goto(EXPERT_ROUTE, wait_until="domcontentloaded", timeout=45_000)
        receipt["navigation"]["response_status"] = response.status if response is not None else None

        phase = "inspection"
        projection = await owned_page.evaluate(SAFE_PROJECTION)
        if not isinstance(projection, dict):
            raise RuntimeError("safe projection")
        receipt["navigation"].update(projection)
    except Exception:
        receipt["result"]["failure_category"] = safe_exception_category(phase)
    finally:
        if owned_page is not None:
            receipt["final_continuity"]["owned_page_close_attempted"] = True
            try:
                if not owned_page.is_closed():
                    await owned_page.close(run_before_unload=False)
                receipt["final_continuity"]["owned_page_closed"] = owned_page.is_closed()
            except Exception:
                if receipt["result"]["failure_category"] is None:
                    receipt["result"]["failure_category"] = safe_exception_category("cleanup")

        if context is not None and anchor is not None:
            try:
                final_pages = tuple(context.pages)
                receipt["final_continuity"]["final_page_count"] = len(final_pages)
                receipt["final_continuity"]["anchor_is_sole_final_page"] = (
                    len(final_pages) == 1 and final_pages[0] is anchor and not anchor.is_closed()
                )
                final_anchor_target_id = await target_id_for(context, anchor)
                receipt["final_continuity"]["anchor_matches_private_input"] = (
                    final_anchor_target_id == private_anchor_id
                )
                receipt["final_continuity"]["anchor_final_new_tab_class"] = is_new_tab_url(anchor.url)
                receipt["final_continuity"]["anchor_unchanged"] = all(
                    [
                        receipt["final_continuity"]["anchor_is_sole_final_page"],
                        receipt["final_continuity"]["anchor_matches_private_input"],
                        receipt["final_continuity"]["anchor_final_new_tab_class"],
                    ]
                )
            except Exception:
                if receipt["result"]["failure_category"] is None:
                    receipt["result"]["failure_category"] = safe_exception_category("cleanup")
        if playwright is not None:
            try:
                await playwright.stop()
            except Exception:
                pass

    navigation = receipt["navigation"]
    healthy = all(
        [
            receipt["result"]["failure_category"] is None,
            receipt["precondition"]["exactly_one_browser_context"],
            receipt["precondition"]["sole_initial_page"],
            receipt["precondition"]["anchor_matches_private_input"],
            receipt["precondition"]["anchor_initial_new_tab_class"],
            receipt["ownership"]["context_new_page_called"],
            receipt["ownership"]["owned_page_distinct_object"],
            receipt["ownership"]["owned_target_distinct_from_anchor"],
            isinstance(navigation["response_status"], int) and 200 <= navigation["response_status"] < 400,
            navigation["response_safe_url_class"] == "engineering_village_expert_route",
            checked_bool(navigation["expected_host"]),
            checked_bool(navigation["expected_expert_title"]),
            not checked_bool(navigation["access_detected"]),
            not checked_bool(navigation["login_detected"]),
            not checked_bool(navigation["challenge_detected"]),
            not checked_bool(navigation["syntax_detected"]),
            checked_bool(navigation["expected_expert_controls_present"]),
            checked_bool(navigation["query_field_present"]),
            receipt["final_continuity"]["owned_page_closed"],
            receipt["final_continuity"]["anchor_unchanged"],
        ]
    )
    receipt["result"]["healthy"] = healthy
    receipt["result"]["status"] = "healthy" if healthy else "blocked"
    if not healthy and receipt["result"]["failure_category"] is None:
        receipt["result"]["failure_category"] = "gate_condition_not_met"
    receipt["ended_at"] = timestamp()
    return receipt


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    if path.exists():
        raise SystemExit("refusing to overwrite an existing G01 receipt")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one safe P02 owned-page route probe.")
    parser.add_argument("--cdp-url", required=True)
    parser.add_argument("--anchor-id-file", required=True)
    parser.add_argument("--receipt", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.cdp_url != ALLOWED_CDP_URL:
        raise SystemExit("refusing a non-P02 CDP endpoint")
    receipt = asyncio.run(run_probe(Path(args.anchor_id_file)))
    write_receipt(Path(args.receipt), receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
