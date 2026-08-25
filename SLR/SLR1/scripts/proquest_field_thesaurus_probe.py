#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Bounded, read-only ProQuest field/thesaurus UI probe for SLR1 P01 plans.

This helper is a client of the existing ProQuest adapters.  It does not launch
Chrome, select a fresh profile, submit a query, or retain page text.  In live
mode the caller must already be inside the shared CfT lease; the helper creates
one adapter-owned page, projects only allowlisted counts/booleans, and closes
that page before returning.  The default mode is a source-free dry-run.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

DEFAULT_CDP_URL = "http://127.0.0.1:9222"
DEFAULT_TIMEOUT_SECONDS = 30.0
EXPECTED_HOST = "www.proquest.com"

PROBE_STATE_SCRIPT = r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const normalize = value => String(value || "").replace(/[\s\u200e\u200f]+/g, " ").trim();
  const labelText = element => {
    if (!element) return "";
    const id = String(element.id || "");
    const label = id ? document.querySelector(`label[for="${CSS.escape(id)}"]`) : null;
    return normalize([
      element.getAttribute("aria-label"),
      element.getAttribute("name"),
      element.getAttribute("id"),
      label && label.textContent
    ].filter(Boolean).join(" "));
  };
  const controls = Array.from(document.querySelectorAll("input, select, textarea, button, a"))
    .filter(visible).map(labelText);
  const count = pattern => controls.filter(value => pattern.test(value)).length;
  const body = normalize(document.body && document.body.innerText);
  const title = normalize(document.title);
  return {
    protocol: window.location.protocol,
    host: window.location.hostname,
    path: window.location.pathname,
    titleHasProQuest: /ProQuest/i.test(title),
    subjectControlCount: count(/subject|keyword/i),
    indexControlCount: count(/index|descriptor|term/i),
    thesaurusControlCount: count(/thesaurus/i),
    titleFieldCount: count(/(^|[ _-])title([ _-]|$)/i),
    abstractFieldCount: count(/abstract/i),
    queryFieldCount: count(/searchterm|query/i),
    visibleResultOrRecordFieldCount: count(/subject|keyword|index|descriptor|thesaurus/i),
    accessMarker: /captcha|verify you are human|access denied|institutional access required|session has expired/i.test(body)
  };
}
"""


class ProbeError(Exception):
    """Expected source-free probe failure."""


class ProbeInputError(ProbeError):
    pass


class ProbeBrowserError(ProbeError):
    pass


class ProbeProtocolError(ProbeError):
    pass


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ProbeInputError(f"Could not load the local adapter: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


def _adapter_path(source: str, adapter_root: Path) -> Path:
    filename = {
        "proquest-atai": "search_proquest_aerospace.py",
        "proquest-pqdt": "search_pqdt.py",
    }[source]
    path = adapter_root.expanduser() / filename
    if not path.is_file():
        raise ProbeInputError(f"The trusted local adapter is missing: {path}")
    return path


def _validate_cdp_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port != 9222
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ProbeInputError("The probe only permits http://127.0.0.1:9222.")
    return value


def _validate_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise ProbeInputError("timeout must be a finite positive number") from error
    if parsed <= 0 or parsed != parsed or parsed in (float("inf"), float("-inf")):
        raise ProbeInputError("timeout must be a finite positive number")
    return parsed


def parse_probe_state(payload: Any, *, source: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProbeProtocolError("ProQuest returned an invalid field/thesaurus probe state.")
    if payload.get("protocol") != "https:" or payload.get("host") != EXPECTED_HOST:
        raise ProbeProtocolError("The probe left HTTPS www.proquest.com.")
    expected_path = {
        "proquest-atai": "/ataindex/commandline",
        "proquest-pqdt": "/pqdtglobal/commandline",
    }[source]
    if payload.get("path") not in {expected_path, f"{expected_path}/advanced"}:
        raise ProbeProtocolError("The probe left the authorized Command Line route.")
    for key in (
        "titleHasProQuest",
        "accessMarker",
    ):
        if not isinstance(payload.get(key), bool):
            raise ProbeProtocolError(f"ProQuest returned invalid {key} evidence.")
    if payload["titleHasProQuest"] is not True:
        raise ProbeProtocolError("ProQuest did not prove the expected product title.")
    if payload["accessMarker"] is True:
        raise ProbeProtocolError("ProQuest exposed an access or challenge marker.")
    counts: dict[str, int] = {}
    for key in (
        "subjectControlCount",
        "indexControlCount",
        "thesaurusControlCount",
        "titleFieldCount",
        "abstractFieldCount",
        "queryFieldCount",
        "visibleResultOrRecordFieldCount",
    ):
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ProbeProtocolError(f"ProQuest returned invalid {key} evidence.")
        counts[key] = value
    return {
        "source_id": source,
        "route": expected_path,
        "title_proof": payload["titleHasProQuest"],
        "access_marker": payload["accessMarker"],
        "visible_allowlisted_counts": counts,
        "current_behavior_status": "observed_only_if_live_execution_is_completed",
    }


async def _close_owned_page_verified(adapter: Any, lease: Any) -> None:
    common = getattr(adapter, "_common", None)
    closer = getattr(common, "close_owned_chrome_page_verified", None)
    if not callable(closer):
        raise ProbeProtocolError("The trusted adapter exposed no verified owned-page closer.")
    outcome = await closer(lease)
    if not getattr(outcome, "verified", False):
        raise ProbeProtocolError("The ProQuest probe could not verify owned-page cleanup.")


def dry_run_receipt(source: str, *, adapter_path: Path, cdp_url: str) -> dict[str, Any]:
    return {
        "schema_version": "slr1-proquest-field-thesaurus-probe/v1",
        "source_id": source,
        "status": "dry_run",
        "browser_action_performed": False,
        "adapter": adapter_path.name,
        "endpoint": cdp_url,
        "planned_route": {
            "proquest-atai": "https://www.proquest.com/ataindex/commandline",
            "proquest-pqdt": "https://www.proquest.com/pqdtglobal/commandline",
        }[source],
        "planned_observations": [
            "visible subject/keyword controls",
            "visible index/descriptor/term controls",
            "visible thesaurus control",
            "visible title/abstract/query controls",
        ],
        "observations": None,
    }


def _write_new(path: Path, payload: dict[str, Any]) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    finally:
        if descriptor != -1:
            os.close(descriptor)


async def _live_probe(
    source: str,
    *,
    adapter_path: Path,
    cdp_url: str,
    timeout_seconds: float,
    playwright_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    adapter = _load_module(adapter_path, f"slr1_probe_{source.replace('-', '_')}")
    try:
        if playwright_factory is None:
            from playwright.async_api import async_playwright

            playwright_factory = async_playwright
    except ImportError as error:  # pragma: no cover - uv supplies live dependency
        raise ProbeBrowserError("Playwright is unavailable; run this helper through uv.") from error

    lease: Any | None = None
    snapshot: set[str] | None = None
    selection_mutation_started = False
    selected_database: str | None = None
    try:
        async with playwright_factory() as playwright:
            if source == "proquest-atai":
                lease = await adapter.open_proquest_owned_page(
                    playwright,
                    cdp_url=cdp_url,
                    target_id=None,
                    headless=False,
                    timeout_seconds=timeout_seconds,
                    chrome_executable=None,
                )
                try:
                    snapshot = await adapter.snapshot_database_selection(
                        lease.page,
                        timeout_seconds=timeout_seconds,
                        attached_cdp=lease.attached_cdp,
                    )
                    selection_mutation_started = True
                    await adapter.prepare_exact_index_selection(
                        lease.page,
                        timeout_seconds=timeout_seconds,
                        attached_cdp=lease.attached_cdp,
                        snapshot=snapshot,
                    )
                    await adapter.navigate(
                        lease.page, adapter.COMMAND_LINE_URL, timeout_seconds
                    )
                    await adapter.wait_for_exact_index_route(
                        lease.page, timeout_seconds=timeout_seconds
                    )
                    payload = await lease.page.evaluate(PROBE_STATE_SCRIPT)
                finally:
                    try:
                        if selection_mutation_started and snapshot is not None:
                            await adapter.restore_database_selection(
                                lease.page, snapshot, timeout_seconds=timeout_seconds
                            )
                    finally:
                        await _close_owned_page_verified(adapter, lease)
            else:
                lease = await adapter.open_owned_chrome_page(
                    playwright,
                    cdp_url=cdp_url,
                    headless=False,
                    timeout_seconds=timeout_seconds,
                    chrome_executable=None,
                )
                try:
                    await adapter.navigate(
                        lease.page, adapter.DATABASE_SELECTION_URL, timeout_seconds
                    )
                    database_payload = await adapter.wait_ready(
                        lease.page, adapter.PQDT_DATABASE_STATE_SCRIPT, None, timeout_seconds
                    )
                    selected_database = adapter.parse_database_state(database_payload)
                    await adapter.navigate(
                        lease.page, adapter.COMMAND_LINE_URL, timeout_seconds
                    )
                    form_payload = await adapter.wait_ready(
                        lease.page, adapter.PQDT_FORM_STATE_SCRIPT, None, timeout_seconds
                    )
                    adapter.parse_form_state(form_payload)
                    payload = await lease.page.evaluate(PROBE_STATE_SCRIPT)
                finally:
                    await _close_owned_page_verified(adapter, lease)
    except ProbeError:
        raise
    except Exception as error:
        raise ProbeBrowserError("The ProQuest field/thesaurus probe did not complete.") from error

    result = parse_probe_state(payload, source=source)
    if source == "proquest-pqdt":
        result["selected_database"] = selected_database
    else:
        result["selected_database"] = "Advanced Technologies & Aerospace Index"
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only source-free or one-owned-page ProQuest field/thesaurus probe."
    )
    parser.add_argument("--source", choices=("proquest-atai", "proquest-pqdt"), required=True)
    parser.add_argument("--output-path", required=True, help="New JSON receipt path")
    parser.add_argument(
        "--adapter-root",
        default="~/agent-tools/academic-research/skills/academic-search/scripts",
        help="Trusted local adapter directory (offline path override for tests only).",
    )
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--timeout", type=_validate_timeout, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Use the already-leased shared browser; without this flag only a dry-run receipt is written.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        cdp_url = _validate_cdp_url(args.cdp_url)
        adapter_path = _adapter_path(args.source, Path(args.adapter_root))
        output_path = Path(args.output_path).expanduser()
        if output_path.exists():
            raise ProbeInputError(f"output path already exists: {output_path}")
        if args.execute:
            receipt = {
                "schema_version": "slr1-proquest-field-thesaurus-probe/v1",
                "source_id": args.source,
                "status": "completed",
                "browser_action_performed": True,
                "adapter": adapter_path.name,
                "endpoint": cdp_url,
                "observations": asyncio.run(
                    _live_probe(
                        args.source,
                        adapter_path=adapter_path,
                        cdp_url=cdp_url,
                        timeout_seconds=args.timeout,
                    )
                ),
            }
        else:
            receipt = dry_run_receipt(
                args.source, adapter_path=adapter_path, cdp_url=cdp_url
            )
        _write_new(output_path, receipt)
    except (ProbeError, OSError) as error:
        print(f"proquest field probe failed: {error}", file=sys.stderr)
        return 1
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
