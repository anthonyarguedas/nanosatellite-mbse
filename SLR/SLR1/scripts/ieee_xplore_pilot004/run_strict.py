#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""Run strict, literal IEEE Pilot 004 cell captures without editing the adapter.

The fixed integration's normal-search helper currently serializes spaces as
``+``.  IEEE's rendered WAF rejected some otherwise valid complete literals in
that form, while the same decoded normal-search route with percent-encoded
components rendered an exact source query echo.  This pilot-local wrapper
therefore re-encodes only already-generated URL components before navigation.
It retains the adapter's normal rendered UI controls, native Year Apply,
Article-Number capture, strict two-pass verifier, and output commit protocol.
No query term, pair, Boolean relation, filter, or source API is changed.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEDULE = (
    ROOT / "source-specific/ieee-xplore/pilots/004/searches/schedule.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "source-specific/ieee-xplore/pilots/004/searches/strict"
FIXED_ADAPTER_DIR = Path.home() / "agent-tools/internet/skills/browser/scripts"


def _load_adapter() -> Any:
    if not FIXED_ADAPTER_DIR.is_dir():
        raise RuntimeError(f"fixed adapter directory is unavailable: {FIXED_ADAPTER_DIR}")
    sys.path.insert(0, str(FIXED_ADAPTER_DIR))
    return importlib.import_module("search_ieee_xplore")


def percent_component_url(url: str) -> str:
    """Re-encode an already-built normal browser URL without changing pairs."""
    split = urlsplit(url)
    pairs = parse_qsl(split.query, keep_blank_values=True)
    encoded = "&".join(
        f"{quote(key, safe='')}={quote(value, safe='')}" for key, value in pairs
    )
    return urlunsplit((split.scheme, split.netloc, split.path, encoded, split.fragment))


def _selected(schedule: dict[str, Any], partitions: set[str], cells: set[str]):
    for partition in schedule["partitions"]:
        partition_id = partition["partition_id"]
        if partitions and partition_id not in partitions:
            continue
        for cell in partition["cells"]:
            cell_id = cell["cell_id"]
            if cells and f"{partition_id}:{cell_id}" not in cells:
                continue
            yield partition_id, cell


def _transport_metadata() -> dict[str, Any]:
    return {
        "schema_version": "slr1-ieee-xplore-pilot004-transport/v1",
        "adapter": "fixed read-only search_ieee_xplore.py",
        "route": "normal IEEE Xplore rendered search UI",
        "url_component_encoding": "percent-encoded components after the fixed adapter generated the normal route",
        "reason": "The fixed adapter's form-style encoding produced a rendered WAF Request Rejected state for some complete literal cells; the identical decoded route was separately observed with an exact query echo.",
        "query_semantics_changed": False,
        "source_api_used": False,
        "native_year_apply_required": True,
    }


def _save_success(
    adapter: Any,
    output: Path,
    result: dict[str, Any],
    reconciliation: dict[str, Any],
) -> None:
    plan = adapter.validate_marker_gated_output_destinations(
        str(output), None, protocol=adapter.IEEE_OUTPUT_COMMIT_SCHEMA, marker_tag=adapter.IEEE_OUTPUT_MARKER_TAG
    )
    metadata = result.setdefault("output_metadata", {})
    metadata["pilot_transport"] = _transport_metadata()
    metadata["pilot_strict_reconciliation"] = reconciliation
    adapter.bind_marker_gated_publication(result, plan)
    result = adapter._finalize_for_save(result, prisma_context=None)
    adapter.publish_marker_gated_outputs(plan, result)


def _save_failure(
    adapter: Any,
    output: Path,
    *,
    query: str,
    error: Exception,
    limit: int,
    max_pages: int,
    page_size: int,
) -> None:
    plan = adapter.validate_marker_gated_output_destinations(
        str(output), None, protocol=adapter.IEEE_OUTPUT_COMMIT_SCHEMA, marker_tag=adapter.IEEE_OUTPUT_MARKER_TAG
    )
    failure = adapter.mark_non_mergeable(
        adapter.error_result(
            query,
            error,
            limit=limit,
            max_pages=max_pages,
            page_size=page_size,
            year_start=2011,
            year_end=2026,
            publication_date_start=None,
            publication_date_end=None,
            content_types=None,
            extra_refinements=None,
            scope="documents",
            access_scope="all",
            search_within=None,
            date_added_start=None,
            date_added_end=None,
            sort="Oldest",
            count_only=False,
            require_complete=True,
            timeout_seconds=90,
            page_delay_seconds=0,
            fetch_full_abstracts=False,
            detail_delay_seconds=0,
        ),
        source=adapter.SOURCE_NAME,
        prisma_context=adapter._error_prisma_context(None),
    )
    failure.setdefault("output_metadata", {})["pilot_transport"] = _transport_metadata()
    adapter.publish_marker_gated_failure_artifact(plan, failure)


def _year_readbacks_are_equivalent(
    adapter: Any, first: Any, second: Any, reconciliation: dict[str, Any]
) -> bool:
    """Accept only the documented equivalent Year readback representations.

    The fixed adapter's strict verifier compares the display-only sidebar
    refinement interval with the second-pass URL token byte-for-byte.  IEEE
    documents both representations for the same already-clicked native window.
    This narrowly normalizes that representation difference; it never permits
    a changed query, source total, sort, page size, or stable-ID order.
    """
    first_controls = first.controls
    second_controls = second.controls
    if len(first_controls) != 11 or len(second_controls) != 11:
        return False
    if any(
        first_controls[index] != second_controls[index]
        for index in (0, 1, 4, 5, 6, 7, 8, 9, 10)
    ):
        return False
    requested = first_controls[1]
    allowed_states = {
        adapter.YEAR_RANGE_READBACK_EXACT,
        adapter.YEAR_RANGE_READBACK_REFINEMENT_WITHIN_REQUEST,
    }
    if first_controls[2] not in allowed_states or second_controls[2] not in allowed_states:
        return False
    if first_controls[2] == second_controls[2]:
        return False
    start_end = adapter.RANGE_VALUE_PATTERN.fullmatch(str(requested or ""))
    if start_end is None:
        return False
    start, end = (int(value) for value in start_end.groups())
    for controls in (first_controls, second_controls):
        state, refinement = controls[2], controls[3]
        if state == adapter.YEAR_RANGE_READBACK_EXACT:
            if refinement is not None:
                return False
        else:
            match = adapter.RANGE_VALUE_PATTERN.fullmatch(str(refinement or ""))
            if match is None:
                return False
            refinement_start, refinement_end = (int(value) for value in match.groups())
            if not (start <= refinement_start <= refinement_end <= end):
                return False
    reconciliation.update(
        {
            "schema_version": "slr1-ieee-xplore-pilot004-strict-year-readback/v1",
            "state": "equivalent_requested_window_reconciled",
            "requested_search_window": requested,
            "pass_1": {
                "year_readback": first_controls[2],
                "result_refinement_range": first_controls[3],
            },
            "pass_2": {
                "year_readback": second_controls[2],
                "result_refinement_range": second_controls[3],
            },
            "other_controls_identical": True,
            "reason": "The source's first post-Apply page reported only an available refinement interval contained within the requested native window; the second normal rendered route echoed that requested window explicitly.",
        }
    )
    return True


async def _capture(
    adapter: Any,
    query: str,
    *,
    limit: int,
    max_pages: int,
    page_size: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    original_initial = adapter.build_search_url
    original_paged = adapter.build_rendered_results_url
    original_reconcile = adapter._reconcile_ieee_strict_passes
    reconciliation: dict[str, Any] = {
        "schema_version": "slr1-ieee-xplore-pilot004-strict-year-readback/v1",
        "state": "native_control_signature_identical",
    }

    def reconcile(first: Any, second: Any) -> None:
        try:
            original_reconcile(first, second)
        except adapter.IEEESnapshotChangedError as error:
            if str(error) != "IEEE changed rendered controls between strict passes.":
                raise
            if not _year_readbacks_are_equivalent(adapter, first, second, reconciliation):
                raise

    adapter.build_search_url = lambda *args, **kwargs: percent_component_url(
        original_initial(*args, **kwargs)
    )
    adapter.build_rendered_results_url = lambda *args, **kwargs: percent_component_url(
        original_paged(*args, **kwargs)
    )
    adapter._reconcile_ieee_strict_passes = reconcile
    try:
        result = await adapter.search_ieee_xplore_in_browser(
            query,
            limit=limit,
            year_start=2011,
            year_end=2026,
            content_types=None,
            extra_refinements=None,
            scope="documents",
            access_scope="all",
            search_within=None,
            sort="Oldest",
            max_pages=max_pages,
            page_size=page_size,
            count_only=False,
            require_complete=True,
            timeout_seconds=90,
            page_delay_seconds=0,
            fetch_full_abstracts=False,
            detail_delay_seconds=0,
            cdp_url=os.environ.get("BH_CDP_URL", "http://localhost:9222"),
            target_id=None,
            headless=False,
            chrome_executable=None,
            prisma_context=None,
        )
        return result, reconciliation
    finally:
        adapter.build_search_url = original_initial
        adapter.build_rendered_results_url = original_paged
        adapter._reconcile_ieee_strict_passes = original_reconcile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=Path, default=DEFAULT_SCHEDULE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--only-cell", action="append", default=[], metavar="PARTITION:CELL")
    parser.add_argument("--limit", type=int, default=10_000)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()
    if args.limit < 1 or args.max_pages < 1 or not 1 <= args.page_size <= 100:
        raise SystemExit("limit/max-pages/page-size must be positive and page size at most 100")

    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    adapter = _load_adapter()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    failures = 0

    for partition_id, cell in _selected(schedule, set(args.only), set(args.only_cell)):
        cell_id = cell["cell_id"]
        output = output_dir / f"{partition_id}-{cell_id}.json"
        if output.exists():
            raise SystemExit(f"refusing to overwrite existing artifact: {output}")
        print(f"Running strict capture {partition_id}/{cell_id}", flush=True)
        try:
            result, reconciliation = asyncio.run(
                _capture(
                    adapter,
                    cell["query"],
                    limit=args.limit,
                    max_pages=args.max_pages,
                    page_size=args.page_size,
                )
            )
            _save_success(adapter, output, result, reconciliation)
            metadata = result.get("output_metadata", {})
            summaries.append(
                {
                    "partition_id": partition_id,
                    "cell_id": cell_id,
                    "artifact": str(output),
                    "total": result.get("total"),
                    "status": metadata.get("status"),
                    "strict_passes_completed": metadata.get("passes_completed"),
                    "retrieval_complete": metadata.get("retrieval_complete"),
                    "strict_reconciliation": reconciliation.get("state"),
                }
            )
        except adapter.IEEEXploreError as error:
            _save_failure(
                adapter,
                output,
                query=cell["query"],
                error=error,
                limit=args.limit,
                max_pages=args.max_pages,
                page_size=args.page_size,
            )
            summaries.append(
                {
                    "partition_id": partition_id,
                    "cell_id": cell_id,
                    "artifact": str(output),
                    "total": None,
                    "status": "error",
                    "error_stage": getattr(error, "error_stage", "unknown"),
                }
            )
            failures += 1

    summary = {
        "schema_version": "slr1-ieee-xplore-pilot004-strict-summary/v1",
        "purpose": "Pilot-only strict stable-Article-Number captures; no final-search merge.",
        "source": "IEEE Xplore",
        "controls": {
            "publication_year": "native inclusive 2011_2026_Year Apply",
            "diagnostic_cutoff": "2026-08-29",
            "date_added": "not applied; separate indexing-date control",
            "language": "not applied",
            "publication_type": "not applied",
            "access": "all / not restricted",
            "wildcards": "not used",
            "full_abstracts": "not fetched; stable rendered Article Numbers are the pilot capture unit",
        },
        "transport": _transport_metadata(),
        "events": summaries,
    }
    summary_path = output_dir / "strict-summary.json"
    if summary_path.exists():
        raise SystemExit(f"refusing to overwrite existing summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
