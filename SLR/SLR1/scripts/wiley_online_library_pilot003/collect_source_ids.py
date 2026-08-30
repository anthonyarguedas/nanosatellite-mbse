#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Collect a two-pass Wiley DOI ledger when native RIS export is unavailable.

This is intentionally a diagnostic identifier/date-card collector, not a
replacement for the Wiley adapter's native-RIS final-run contract.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any
import urllib.request


ADAPTER_PATH = Path.home() / "agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py"
SOURCE_NAME = "Wiley Online Library"
SOURCE_ID = "wiley_online_library"
PAGE_SIZE = 20


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("wiley_pilot_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sequence_digest(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def clean_error(error: BaseException) -> str:
    return " ".join(str(error).split())[:700]


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
    """Capture the CDP identity of this invocation's newly created page only."""
    session = await page.context.new_cdp_session(page)
    try:
        details = await session.send("Target.getTargetInfo")
    finally:
        await session.detach()
    target_id = details.get("targetInfo", {}).get("targetId")
    if not isinstance(target_id, str) or not target_id:
        raise RuntimeError("Could not determine the collector-owned Chrome target")
    return target_id


async def close_owned_page(cdp_url: str, target_id: str) -> tuple[bool, str]:
    """Close exactly the previously identified owned target through local CDP."""
    root = cdp_url.rstrip("/")

    def target_ids() -> set[str]:
        with urllib.request.urlopen(f"{root}/json/list", timeout=15) as response:
            values = json.load(response)
        return {
            value["id"]
            for value in values
            if isinstance(value, dict) and isinstance(value.get("id"), str)
        }

    try:
        if target_id not in await asyncio.to_thread(target_ids):
            return True, "already_absent"
        await asyncio.to_thread(
            lambda: urllib.request.urlopen(
                f"{root}/json/close/{target_id}", timeout=15
            ).read()
        )
        for _ in range(20):
            await asyncio.sleep(0.1)
            if target_id not in await asyncio.to_thread(target_ids):
                return True, "local_cdp_target_close"
    except Exception as error:  # cleanup must be explicit in the failure receipt
        return False, f"local_cdp_cleanup_error:{type(error).__name__}"
    return False, "local_cdp_target_still_present"


def card_projection(card: dict[str, Any], *, source_id: str, rank: int, source_date: str, date_status: str) -> dict[str, Any]:
    """Keep only validated rendered-card metadata; never call a card description an abstract."""
    if card.get("id") != source_id or card.get("kind") != "doi":
        raise RuntimeError("Wiley rendered-card identity did not match the DOI ledger")
    return {
        "source_id": source_id,
        "doi": source_id,
        "rank": rank,
        "title": card.get("title", ""),
        "source_publication_date": source_date,
        "source_publication_date_basis": "Wiley rendered result-card First published",
        "exact_date_filter_status": date_status,
        "rendered_card_description": card.get("description", ""),
        "rendered_card_description_status": "not_assumed_to_be_an_abstract",
    }


async def collect(
    adapter: Any,
    *,
    query: str,
    date_start: date,
    date_end: date,
    timeout_seconds: float,
    page_delay_seconds: float,
) -> dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:  # pragma: no cover - installation contract
        raise RuntimeError("Playwright is unavailable under uv") from error

    bounds = adapter.resolve_date_bounds(
        year_start=None,
        year_end=None,
        date_start=date_start,
        date_end=date_end,
        relative_date=None,
    )
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    lease: Any | None = None
    owned_target_id: str | None = None
    cleanup_verified = False
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
            owned_target_id = await target_id_for_page(page)
            baseline_total: int | None = None
            baseline_ids: list[str] = []
            baseline_records: list[dict[str, Any]] = []
            baseline_pages: list[dict[str, Any]] = []
            pass_reports: list[dict[str, Any]] = []
            first_page_readback: dict[str, Any] | None = None

            for pass_number in range(1, 3):
                pass_ids: list[str] = []
                page_number = 0
                page_reports: list[dict[str, Any]] = []
                while True:
                    source_url = adapter.build_search_url(
                        query,
                        page_number=page_number,
                        date_bounds=bounds,
                        content="articlesChapters",
                        sort="Earliest",
                    )
                    # Commit is enough to expose a possible Cloudflare shell to
                    # the adapter's same-page passive readiness poll.  Do not
                    # reload, click, solve, or replay any access challenge.
                    await page.goto(
                        source_url,
                        wait_until="commit",
                        timeout=int(timeout_seconds * 1000),
                    )
                    state = await adapter.wait_for_ready_page(
                        page,
                        query=query,
                        page_number=page_number,
                        date_bounds=bounds,
                        content="articlesChapters",
                        sort="Earliest",
                        expected_total=baseline_total,
                        timeout_seconds=timeout_seconds,
                        require_export=False,
                    )
                    if state.total is None:
                        raise RuntimeError("Wiley did not expose an exact source total")
                    if baseline_total is None:
                        baseline_total = state.total
                    if state.total != baseline_total:
                        raise RuntimeError("Wiley source total changed between pages or passes")
                    ids = list(state.ordered_ids)
                    dates = list(state.publication_dates)
                    cards = list(state.result_cards)
                    if len(ids) != len(dates) or len(ids) != len(cards):
                        raise RuntimeError("Wiley page did not align DOI, date, and rendered-card metadata")
                    if len(set(ids)) != len(ids) or set(pass_ids).intersection(ids):
                        raise RuntimeError("Wiley repeated DOI IDs within a collection pass")
                    if pass_number == 1:
                        page_records: list[dict[str, Any]] = []
                        for offset, (source_id, source_date, card) in enumerate(
                            zip(ids, dates, cards), start=1
                        ):
                            date_status = adapter.exact_date_filter_status(
                                {}, bounds, source_date
                            )
                            page_records.append(
                                card_projection(
                                    card,
                                    source_id=source_id,
                                    rank=page_number * PAGE_SIZE + offset,
                                    source_date=source_date,
                                    date_status=date_status,
                                )
                            )
                        baseline_records.extend(page_records)
                    card_fingerprint = digest(
                        [
                            {
                                "source_id": source_id,
                                "source_publication_date": source_date,
                                "title": card.get("title", ""),
                                "rendered_card_description": card.get("description", ""),
                            }
                            for source_id, source_date, card in zip(ids, dates, cards)
                        ]
                    )
                    report = {
                        "page": page_number,
                        "source_total": state.total,
                        "rendered_cards": state.card_count,
                        "ordered_source_ids": ids,
                        "ordered_source_ids_sha256": sequence_digest(ids),
                        "rendered_metadata_sha256": card_fingerprint,
                        "active_page": state.active_page,
                        "source_query_readback": list(state.query_readbacks),
                        "normalized_date_range": state.normalized_date_range,
                        "sort_displays": list(state.sort_displays),
                    }
                    if pass_number == 1:
                        baseline_pages.append(report)
                        if first_page_readback is None:
                            first_page_readback = {
                                "source_query_readback": list(state.query_readbacks),
                                "normalized_date_range": state.normalized_date_range,
                                "sort_displays": list(state.sort_displays),
                                "sort_options": list(state.sort_options),
                                "applied_filter_labels": list(state.applied_filter_labels),
                            }
                    else:
                        previous = baseline_pages[page_number]
                        if (
                            ids != previous["ordered_source_ids"]
                            or card_fingerprint != previous["rendered_metadata_sha256"]
                            or state.active_page != page_number
                        ):
                            raise RuntimeError("Wiley ordered DOI or rendered-card metadata changed between passes")
                    pass_ids.extend(ids)
                    page_reports.append(report)
                    if len(pass_ids) > baseline_total:
                        raise RuntimeError("Wiley DOI ledger exceeded its source total")
                    if len(pass_ids) == baseline_total:
                        break
                    if not ids:
                        raise RuntimeError("Wiley returned an empty non-final source page")
                    page_number += 1
                    if page_delay_seconds:
                        await asyncio.sleep(page_delay_seconds)
                if len(pass_ids) != baseline_total:
                    raise RuntimeError("Wiley DOI ledger did not reconcile to its source total")
                if pass_number == 1:
                    baseline_ids = pass_ids
                elif pass_ids != baseline_ids:
                    raise RuntimeError("Wiley complete ordered DOI sequence changed between passes")
                pass_reports.append(
                    {
                        "pass_number": pass_number,
                        "source_total": baseline_total,
                        "pages": page_reports,
                        "ordered_source_ids_sha256": sequence_digest(pass_ids),
                    }
                )
            # This must run while the shared Playwright CDP connection is still
            # alive; after its context manager exits, page identity cannot be
            # independently verified.
            cleanup_verified, cleanup_mode = await close_owned_page(
                cdp_url, owned_target_id
            )
            if not cleanup_verified:
                raise RuntimeError(
                    f"Wiley collector-owned page cleanup could not be verified: {cleanup_mode}"
                )
            lease = None
            owned_target_id = None
    finally:
        if owned_target_id is not None:
            cleanup_verified, cleanup_mode = await close_owned_page(
                cdp_url, owned_target_id
            )
            if not cleanup_verified:
                raise RuntimeError(
                    f"Wiley collector-owned page cleanup could not be verified: {cleanup_mode}"
                )

    if baseline_total is None:  # pragma: no cover - guarded by page contract
        raise RuntimeError("Wiley collection did not produce a source total")
    counts = {"included": 0, "excluded": 0, "unresolved": 0}
    for record in baseline_records:
        counts[record["exact_date_filter_status"]] += 1
    retained = [
        record["source_id"]
        for record in baseline_records
        if record["exact_date_filter_status"] != "excluded"
    ]
    return {
        "source_total": baseline_total,
        "ordered_source_ids": baseline_ids,
        "ordered_source_ids_sha256": sequence_digest(baseline_ids),
        "records": baseline_records,
        "passes": pass_reports,
        "first_page_readback": first_page_readback,
        "client_exact_date_counts": counts,
        "ordered_client_retained_source_ids": retained,
        "ordered_client_retained_source_ids_sha256": sequence_digest(retained),
        "owned_page_cleanup_verified": cleanup_verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-plan", type=Path, required=True)
    parser.add_argument("--partition-id", required=True)
    parser.add_argument(
        "--query-id",
        help="Optional lossless source-cell ID from query-plan.json; partition ID remains semantic.",
    )
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.25)
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    plan = json.loads(args.query_plan.read_text(encoding="utf-8"))
    source_query_id = args.query_id or args.partition_id
    queries = {**plan["queries"], **plan.get("query_cells", {})}
    query = queries[source_query_id]
    base = {
        "schema_version": "wiley-online-library-pilot-source-id-ledger/v1",
        "pilot": "003",
        "source": SOURCE_NAME,
        "source_id": SOURCE_ID,
        "partition_id": args.partition_id,
        "source_query_id": source_query_id,
        "do_not_merge": True,
        "purpose": (
            "Two-pass rendered Articles & Chapters DOI ledger after the paired "
            "adapter's native RIS export failure; not a final bibliographic export."
        ),
        "query": query,
        "query_plan": args.query_plan.name,
        "controls": {
            "field": "Anywhere / AllField",
            "content": "articlesChapters",
            "sort": "Earliest (visible Date control; observed newest-to-oldest)",
            "date_start": "2011-01-01",
            "date_end": "2026-08-29",
            "source_month_start": "2011-01",
            "source_month_end": "2026-08",
            "source_date_basis": "Wiley rendered result-card First published",
            "language_filter": None,
            "publication_type_filter": None,
            "access_filter": None,
            "peer_review_filter": None,
            "full_text_filter": None,
        },
        "started_at_utc": started.isoformat(),
    }
    try:
        adapter = load_adapter()
        result = asyncio.run(
            collect(
                adapter,
                query=query,
                date_start=date(2011, 1, 1),
                date_end=date(2026, 8, 29),
                timeout_seconds=args.timeout_seconds,
                page_delay_seconds=args.page_delay_seconds,
            )
        )
        payload = {
            **base,
            "status": "success",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            **result,
            "limitations": [
                "The source applies inclusive source-month bounds; the visible First published date supplies the logged client exact-day reconciliation.",
                "This ledger retains only DOI identity and validated rendered-card title/date/description fields. It does not claim native RIS capture or complete bibliographic metadata.",
            ],
        }
    except BaseException as error:  # preserve a null source total on every failure
        payload = {
            **base,
            "status": "error",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_total": None,
            "ordered_source_ids": [],
            "records": [],
            "failure": {"error_type": type(error).__name__, "error": clean_error(error)},
        }
    atomic_json(args.output_path, payload)
    print(
        json.dumps(
            {
                "output": str(args.output_path),
                "partition_id": args.partition_id,
                "source_query_id": source_query_id,
                "status": payload["status"],
                "source_total": payload["source_total"],
            }
        )
    )
    return 0 if payload["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
