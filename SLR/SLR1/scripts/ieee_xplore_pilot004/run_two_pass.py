#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""Capture IEEE Pilot 004 cells twice through fresh native Year-Apply passes.

This is the pilot fallback when the fixed adapter's built-in strict verifier
rejects two equivalent Year readback *representations*: the first native Apply
can expose only a contained result-refinement interval, whereas its own second
route echoes the requested range token.  Each pass here starts from the normal
rendered source query, visibly applies the native Year control, exhausts the
source, and is independently saved.  The local receipt then requires matching
source totals and ordered IEEE Article Numbers while preserving—not erasing—
the two readback forms.

The fixed integration remains read-only.  As in ``run_strict.py``, only URL
component encoding is changed from form-style ``+`` to percent encoding after
the fixed adapter has generated the route; all decoded source values and
adapter control logic remain unchanged.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEDULE = ROOT / "source-specific/ieee-xplore/pilots/004/searches/schedule.json"
DEFAULT_OUTPUT_DIR = ROOT / "source-specific/ieee-xplore/pilots/004/searches/two-pass"
FIXED_ADAPTER_DIR = Path(
    "/Users/antho/agent-tools-worktrees/slr-integration/internet/skills/browser/scripts"
)


def _load_adapter() -> Any:
    sys.path.insert(0, str(FIXED_ADAPTER_DIR))
    return importlib.import_module("search_ieee_xplore")


def percent_component_url(url: str) -> str:
    split = urlsplit(url)
    encoded = "&".join(
        f"{quote(key, safe='')}={quote(value, safe='')}"
        for key, value in parse_qsl(split.query, keep_blank_values=True)
    )
    return urlunsplit((split.scheme, split.netloc, split.path, encoded, split.fragment))


def _transport_metadata() -> dict[str, Any]:
    return {
        "schema_version": "slr1-ieee-xplore-pilot004-transport/v1",
        "adapter": "fixed read-only search_ieee_xplore.py",
        "route": "normal IEEE Xplore rendered search UI",
        "url_component_encoding": "percent-encoded components after fixed-adapter route generation",
        "query_semantics_changed": False,
        "source_api_used": False,
        "native_year_apply_required": True,
    }


def _article_ids(result: dict[str, Any]) -> list[str]:
    ids = []
    for record in result.get("results", []):
        value = record.get("paperId") if isinstance(record, dict) else None
        if not isinstance(value, str) or not value.isdigit():
            raise ValueError("A complete pilot record did not retain a numeric IEEE Article Number.")
        ids.append(value)
    if len(ids) != len(set(ids)):
        raise ValueError("A pilot pass retained duplicate IEEE Article Numbers.")
    if result.get("total") != len(ids):
        raise ValueError("A pilot pass did not exhaust the exact source total.")
    return ids


def _id_hash(ids: list[str]) -> str:
    digest = hashlib.sha256()
    for value in ids:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _year_observation(result: dict[str, Any]) -> dict[str, Any]:
    readback = result.get("output_metadata", {}).get("publication_year_readback", {})
    return {
        "state": readback.get("state"),
        "requested_search_window": readback.get("requested_search_window"),
        "native_range_echo": readback.get("native_range_echo"),
        "result_refinement_range": readback.get("result_refinement_range"),
        "result_refinement_range_within_requested_window": readback.get(
            "result_refinement_range_within_requested_window"
        ),
    }


def _year_is_valid(observation: dict[str, Any], *, source_total: int) -> bool:
    if observation.get("requested_search_window") != "2011_2026_Year":
        return False
    state = observation.get("state")
    # An explicit native zero has no dependent Year controls to click. The
    # adapter records this separately rather than pretending an unapplied
    # control is a zero-result filter.
    if source_total == 0:
        return state == "not_needed_source_zero"
    if state == "exact_source_echo":
        return observation.get("native_range_echo") == "2011_2026_Year"
    if state == "result_refinement_range_within_requested_window":
        return observation.get("result_refinement_range_within_requested_window") is True
    return False


def _save_success(adapter: Any, output: Path, result: dict[str, Any], pass_number: int) -> None:
    plan = adapter.validate_marker_gated_output_destinations(
        str(output), None, protocol=adapter.IEEE_OUTPUT_COMMIT_SCHEMA, marker_tag=adapter.IEEE_OUTPUT_MARKER_TAG
    )
    metadata = result.setdefault("output_metadata", {})
    metadata["pilot_transport"] = _transport_metadata()
    metadata["pilot_capture_pass"] = {
        "schema_version": "slr1-ieee-xplore-pilot004-fresh-pass/v1",
        "pass_number": pass_number,
        "capture_method": "independent complete native-Year-Apply traversal",
        "full_abstracts": "not fetched; Article Number is the pilot capture unit",
    }
    adapter.bind_marker_gated_publication(result, plan)
    result = adapter._finalize_for_save(result, prisma_context=None)
    adapter.publish_marker_gated_outputs(plan, result)


def _save_failure(adapter: Any, output: Path, query: str, error: Exception, pass_number: int, limit: int, max_pages: int, page_size: int) -> None:
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
            require_complete=False,
            timeout_seconds=90,
            page_delay_seconds=0,
            fetch_full_abstracts=False,
            detail_delay_seconds=0,
        ),
        source=adapter.SOURCE_NAME,
        prisma_context=adapter._error_prisma_context(None),
    )
    failure.setdefault("output_metadata", {})["pilot_transport"] = _transport_metadata()
    failure["output_metadata"]["pilot_capture_pass"] = {
        "schema_version": "slr1-ieee-xplore-pilot004-fresh-pass/v1",
        "pass_number": pass_number,
        "capture_method": "independent complete native-Year-Apply traversal",
    }
    adapter.publish_marker_gated_failure_artifact(plan, failure)


async def _one_pass(adapter: Any, query: str, limit: int, max_pages: int, page_size: int) -> dict[str, Any]:
    original_initial = adapter.build_search_url
    original_paged = adapter.build_rendered_results_url
    adapter.build_search_url = lambda *args, **kwargs: percent_component_url(original_initial(*args, **kwargs))
    adapter.build_rendered_results_url = lambda *args, **kwargs: percent_component_url(original_paged(*args, **kwargs))
    try:
        return await adapter.search_ieee_xplore_in_browser(
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
            require_complete=False,
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
    finally:
        adapter.build_search_url = original_initial
        adapter.build_rendered_results_url = original_paged


def _cells(schedule: dict[str, Any], wanted_partitions: set[str], wanted_cells: set[str]):
    for partition in schedule["partitions"]:
        partition_id = partition["partition_id"]
        if wanted_partitions and partition_id not in wanted_partitions:
            continue
        for cell in partition["cells"]:
            cell_id = cell["cell_id"]
            if wanted_cells and f"{partition_id}:{cell_id}" not in wanted_cells:
                continue
            yield partition_id, cell_id, cell["query"]


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

    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    adapter = _load_adapter()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    events: list[dict[str, Any]] = []
    failures = 0

    for partition_id, cell_id, query in _cells(schedule, set(args.only), set(args.only_cell)):
        prefix = f"{partition_id}-{cell_id}"
        pass_paths = [args.output_dir / f"{prefix}-pass{number}.json" for number in (1, 2)]
        receipt_path = args.output_dir / f"{prefix}-two-pass-receipt.json"
        if any(path.exists() for path in (*pass_paths, receipt_path)):
            raise SystemExit(f"refusing to overwrite an existing two-pass event: {prefix}")
        results: list[dict[str, Any]] = []
        failed = False
        for number, path in enumerate(pass_paths, start=1):
            print(f"Running fresh native pass {number}: {partition_id}/{cell_id}", flush=True)
            try:
                result = asyncio.run(_one_pass(adapter, query, args.limit, args.max_pages, args.page_size))
                _article_ids(result)
                _save_success(adapter, path, result, number)
                results.append(result)
            except (adapter.IEEEXploreError, ValueError) as error:
                if isinstance(error, adapter.IEEEXploreError):
                    _save_failure(adapter, path, query, error, number, args.limit, args.max_pages, args.page_size)
                    stage = getattr(error, "error_stage", "unknown")
                else:
                    stage = "local_stable_id_validation"
                events.append({
                    "partition_id": partition_id,
                    "cell_id": cell_id,
                    "status": "error",
                    "failed_pass": number,
                    "total": None,
                    "error_stage": stage,
                    "artifact": str(path),
                })
                failures += 1
                failed = True
                break
        if failed:
            continue

        first_ids, second_ids = (_article_ids(result) for result in results)
        first_year, second_year = (_year_observation(result) for result in results)
        valid = (
            first_ids == second_ids
            and _year_is_valid(first_year, source_total=results[0].get("total"))
            and _year_is_valid(second_year, source_total=results[1].get("total"))
            and all(result.get("output_metadata", {}).get("retrieval_complete") is True for result in results)
            and all(
                result.get("total") == 0
                or result.get("output_metadata", {}).get("effective_sort") == "Oldest"
                for result in results
            )
        )
        receipt = {
            "schema_version": "slr1-ieee-xplore-pilot004-fresh-two-pass-receipt/v1",
            "source": "IEEE Xplore",
            "partition_id": partition_id,
            "cell_id": cell_id,
            "purpose": "Pilot-only stable Article Number reconciliation; not a final search.",
            "controls": {
                "requested_search_window": "2011_2026_Year",
                "diagnostic_cutoff": "2026-08-29",
                "date_added": "not applied; separate indexing-date control",
                "language": "not applied",
                "publication_type": "not applied",
                "access": "all / not restricted",
                "wildcards": "not used",
            },
            "pass_artifacts": [path.name for path in pass_paths],
            "pass_1_year_readback": first_year,
            "pass_2_year_readback": second_year,
            "source_totals": [result.get("total") for result in results],
            "ordered_article_number_sha256": [_id_hash(first_ids), _id_hash(second_ids)],
            "ordered_article_numbers_identical": first_ids == second_ids,
            "stable_article_number_count": len(first_ids),
            "reconciled": valid,
            "transport": _transport_metadata(),
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if not valid:
            failures += 1
        events.append({
            "partition_id": partition_id,
            "cell_id": cell_id,
            "status": "complete" if valid else "unreconciled",
            "total": results[0].get("total") if valid else None,
            "stable_article_number_count": len(first_ids),
            "receipt": str(receipt_path),
        })

    summary = {
        "schema_version": "slr1-ieee-xplore-pilot004-fresh-two-pass-summary/v1",
        "source": "IEEE Xplore",
        "purpose": "Fresh native Year-Apply two-pass pilot captures; no final-search merge.",
        "events": events,
    }
    summary_path = args.output_dir / "two-pass-summary.json"
    if summary_path.exists():
        raise SystemExit(f"refusing to overwrite existing summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
