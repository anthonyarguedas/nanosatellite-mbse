#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Run two-pass terminal-page Compendex controlled-vocabulary value cells."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/_engineering_village_search.py"
)
NEXT_STATE_SCRIPT = r"""
() => {
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const controls = Array.from(document.querySelectorAll(
    "a#next-page-top[aria-label='Next Page']"
  ));
  return {
    connected: controls.filter(element => element.isConnected).length,
    visible: controls.filter(visible).length,
    visible_enabled: controls.filter(element =>
      visible(element) && !element.matches(":disabled") &&
      element.getAttribute("aria-disabled") !== "true" &&
      !element.closest("[aria-disabled='true'], .disabled")
    ).length,
  };
}
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "compendex_pilot004_value_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load the Engineering Village adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_inputs(assignments: Any, candidates: Any) -> None:
    if assignments.get("status") != "complete_two_pass_assignment_readback":
        raise RuntimeError("The controlled-term assignment harvest is incomplete")
    if candidates.get("status") != "complete_two_pass_readback":
        raise RuntimeError("The Ei Thesaurus candidate validation is incomplete")
    if assignments.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        raise RuntimeError("The assignment harvest uses a different protocol commit")
    if candidates.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        raise RuntimeError("The candidate validation uses a different protocol commit")
    exact = {
        candidate["term"]: candidate
        for candidate in candidates.get("candidates", [])
        if candidate.get("status") == "verified_exact_preferred_ei_thesaurus_term"
    }
    required = {"Nanosatellites", "Small satellites", "Systems engineering", "Modeling languages"}
    if not required.issubset(exact):
        raise RuntimeError("The value comparison lacks exact identities for all candidate descriptors")
    if any(exact[term].get("selected_record_assignment_count", 0) < 1 for term in required):
        raise RuntimeError("A value-test descriptor lacks selected-record assignment evidence")


def assert_common_controls(adapter: Any, state: Any, *, zero: bool) -> None:
    adapter.raise_for_portal_access(state)
    expected = {
        "database_mask": state.database == "1",
        "Compendex_selected": state.compendex_selected is True,
        "Inspec_unselected": state.inspec_selected is False,
        "All_unselected": state.all_selected is False,
        "Knovel_unselected": state.knovel_selected is False,
        "database_observed": state.database_independently_observed is True or zero,
        "autostemming_off": state.autostemming_off is True,
        "autostemming_label": state.autostemming_label_confirms_off is True,
        "expert_mode": state.expert_mode is True,
        "Published_active": state.year_range_selected is True,
        "Updates_inactive": state.last_update_selected is False,
        "start_year": state.start_year_value == "2011",
        "end_year": state.end_year_value == "2026",
        "no_document_type_refinement": state.query_has_document_type_clause is not True,
        "no_active_result_facets": not state.active_result_facets,
    }
    if not zero:
        expected.update(
            {
                "source_scope": state.reported_database_scope == "Compendex",
                "source_date_echo": ("2011", "2026") in state.reported_date_ranges,
                "page_size": state.page_size == 25,
                "sort_value": state.sort_value == adapter.SORT_OLDEST_VALUE,
                "sort_label": state.sort_label == adapter.SORT_OLDEST_LABEL,
                "facet_inventory": state.facet_control_inventory_observed is True,
            }
        )
    failed = [name for name, passed in expected.items() if not passed]
    if failed:
        raise RuntimeError("Compendex control readback failed: " + ", ".join(failed))


async def wait_for_terminal_controls(
    adapter: Any,
    page: Any,
    timeout_seconds: float,
    ownership_guard: Any,
) -> Any:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    last_state = None
    while True:
        remaining = max(0.001, deadline - asyncio.get_running_loop().time())
        state = await adapter.wait_for_results_page(
            page,
            remaining,
            ownership_reassertion=ownership_guard,
        )
        last_state = state
        if state.zero_results:
            return state
        if (
            state.page_size == 25
            and state.sort_value == adapter.SORT_OLDEST_VALUE
            and state.sort_label == adapter.SORT_OLDEST_LABEL
        ):
            return state
        if asyncio.get_running_loop().time() >= deadline:
            break
        await asyncio.sleep(min(0.2, remaining))
    raise RuntimeError(
        "Compendex did not retain terminal page controls"
        if last_state is not None
        else "Compendex returned no terminal page state"
    )


def assert_terminal_page_without_required_interval(adapter: Any, state: Any) -> dict[str, Any]:
    if state.zero_results:
        adapter.assert_page_reconciliation(
            state, expected_total=None, expected_page_number=1
        )
        return {
            "state": "explicit_source_zero",
            "fixed_adapter_outcome": "accepted_zero_without_numeric_interval",
            "rendered_interval": None,
        }
    if not isinstance(state.total, int) or isinstance(state.total, bool) or not 1 <= state.total <= 25:
        raise RuntimeError("The pilot-local terminal-page contract accepts only totals from 1 through 25")
    if state.page_number != 1 or state.page_count != 1:
        raise RuntimeError("The pilot-local contract refuses pagination or a nonterminal page")
    expected_page_count = math.ceil(state.total / 25)
    if expected_page_count != 1:
        raise RuntimeError("The source total does not reconcile to one 25-row page")
    if state.rendered_count != state.total:
        raise RuntimeError("The terminal rendered row count did not equal the source total")
    if len(state.document_ids) != state.total or len(state.export_ids) != state.total:
        raise RuntimeError("The terminal source identifiers did not equal the source total")
    if len(set(state.document_ids)) != state.total or len(set(state.export_ids)) != state.total:
        raise RuntimeError("The terminal page repeated a source identifier")
    if state.missing_document_id_rows not in {None, 0}:
        raise RuntimeError("The terminal page omitted a request identifier")
    if state.missing_export_id_rows not in {None, 0}:
        raise RuntimeError("The terminal page omitted a stable accession")
    if state.missing_database_rows not in {None, 0}:
        raise RuntimeError("The terminal page omitted row database provenance")
    row_databases = adapter.effective_row_databases(state)
    if row_databases != ["compendex"] * state.total:
        raise RuntimeError("The terminal page did not retain Compendex row provenance")
    interval = (
        [state.result_range_start, state.result_range_end]
        if state.result_range_start is not None and state.result_range_end is not None
        else None
    )
    if interval is not None and interval != [1, state.total]:
        raise RuntimeError("The optional rendered interval conflicted with the terminal page")
    fixed_outcome = "accepted"
    try:
        adapter.assert_page_reconciliation(
            state, expected_total=state.total, expected_page_number=1
        )
    except adapter.CompendexProtocolError as error:
        if clean(error) != "Engineering Village did not expose a rendered result interval for a nonzero page":
            raise
        if interval is not None:
            raise RuntimeError("The fixed adapter rejected a source interval that was present") from error
        fixed_outcome = "rejected_missing_rendered_result_interval"
    return {
        "state": "complete_terminal_single_page",
        "fixed_adapter_outcome": fixed_outcome,
        "rendered_interval": interval,
    }


async def collect_cell(
    adapter: Any,
    connection: Any,
    cell_id: str,
    query: str,
    pass_number: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    page = None
    started_at = now()
    try:
        page = await adapter.new_owned_chrome_page(
            connection.context,
            timeout_seconds=timeout_seconds,
            authorization=None,
            validate_authorization=adapter._validate_engineering_village_authorized_target,
        )
        ownership_guard = adapter._OwnedPageGuard(
            connection.browser, connection.context, page
        )
        await adapter.navigate_to_portal(
            page,
            adapter.build_search_url("expert", ("compendex",)),
            timeout_seconds,
            ownership_reassertion=ownership_guard,
        )
        await adapter.wait_for_portal_state(
            page, timeout_seconds, ownership_reassertion=ownership_guard
        )
        await adapter.configure_expert_search_controls(
            page,
            ("compendex",),
            year_start=2011,
            year_end=2026,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=ownership_guard,
        )
        await adapter.submit_portal_query(
            page,
            query,
            "expert",
            ownership_reassertion=ownership_guard,
        )
        state = await adapter.wait_for_results_page(
            page, timeout_seconds, ownership_reassertion=ownership_guard
        )
        if not state.zero_results:
            await adapter.configure_result_controls(
                page, timeout_seconds, ownership_reassertion=ownership_guard
            )
        state = await wait_for_terminal_controls(
            adapter, page, timeout_seconds, ownership_guard
        )
        if not await adapter.page_echoes_query(
            page,
            query,
            source_query=query,
            effective_query=adapter.source_native_query(query),
            ownership_reassertion=ownership_guard,
        ):
            raise RuntimeError("Compendex did not echo the exact value-cell query")
        assert_common_controls(adapter, state, zero=state.zero_results)
        terminal_contract = assert_terminal_page_without_required_interval(
            adapter, state
        )
        next_state = await page.evaluate(NEXT_STATE_SCRIPT)
        if not isinstance(next_state, dict) or next_state.get("visible_enabled") != 0:
            raise RuntimeError("The terminal one-page cell exposed an enabled visible Next control")

        results: list[dict[str, Any]] = []
        if not state.zero_results:
            row_databases = adapter.effective_row_databases(state)
            raw_records = await adapter.download_ris_records(
                page,
                state.document_ids,
                state.database,
                timeout_seconds,
                ownership_reassertion=ownership_guard,
            )
            results = adapter.reconcile_ris_batch(
                raw_records,
                state.document_ids,
                state.database,
                export_ids=state.export_ids,
                row_databases=row_databases,
            )
            if [record.get("paperId") for record in results] != state.export_ids:
                raise RuntimeError("Native RIS accessions did not retain source order")
            if any(record.get("source") != "Compendex (Engineering Village)" for record in results):
                raise RuntimeError("Native RIS normalization changed source identity")
            if any(
                not isinstance(record.get("year"), int)
                or not 2011 <= record["year"] <= 2026
                for record in results
            ):
                raise RuntimeError("A native RIS record fell outside the source year controls")
        total = 0 if state.zero_results else state.total
        return {
            "schema_version": "compendex-controlled-vocabulary-terminal-cell/v1",
            "source": "Compendex",
            "platform": "Engineering Village",
            "pilot": "004",
            "cell_id": cell_id,
            "pass": pass_number,
            "status": terminal_contract["state"],
            "do_not_merge": True,
            "merge_eligible": False,
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "started_at_utc": started_at,
            "completed_at_utc": now(),
            "adapter": {
                "id": adapter.ADAPTER_ID,
                "version": adapter.ADAPTER_VERSION,
            },
            "query": query,
            "query_sha256": sha256_text(query),
            "query_echo": "observed_exact_source_query",
            "total": total,
            "ordered_stable_accessions": list(state.export_ids),
            "results": results,
            "controls": {
                "database": "Compendex",
                "database_mask": "1",
                "Published": {"start": 2011, "end": 2026},
                "Updates": "inactive",
                "language": "English WN LA",
                "autostemming": "off",
                "sort": "Date (Oldest)" if not state.zero_results else "not_rendered_on_zero_page",
                "page_size": 25 if not state.zero_results else "not_rendered_on_zero_page",
                "document_type": "not_applied",
                "open_access": "not_applied",
            },
            "terminal_page_contract": {
                **terminal_contract,
                "page_number": state.page_number,
                "page_count": state.page_count,
                "rendered_row_count": state.rendered_count,
                "source_total": total,
                "enabled_visible_next_controls": next_state["visible_enabled"],
                "boundary": (
                    "This pilot-local contract accepts only an explicit source zero or a "
                    "fully reconciled terminal one-page result. It cannot traverse a second page."
                ),
            },
            "native_ris": {
                "requested": bool(results),
                "record_count": len(results),
                "stable_accessions_reconciled": [
                    record.get("paperId") for record in results
                ],
                "raw_ris_persisted": False,
                "private_path_persisted": False,
            },
        }
    finally:
        await adapter.close_owned_chrome_page_only(page)


def stable_projection(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "cell_id": artifact["cell_id"],
        "status": artifact["status"],
        "query": artifact["query"],
        "total": artifact["total"],
        "ordered_stable_accessions": artifact["ordered_stable_accessions"],
        "results": artifact["results"],
        "controls": artifact["controls"],
        "terminal_page_contract": artifact["terminal_page_contract"],
        "native_ris": artifact["native_ris"],
    }


async def run(
    assignment_path: Path,
    candidate_path: Path,
    output_dir: Path,
    reconciliation_path: Path,
    failure_path: Path,
    timeout_seconds: float,
) -> None:
    assignments = json.loads(assignment_path.read_text(encoding="utf-8"))
    candidates = json.loads(candidate_path.read_text(encoding="utf-8"))
    validate_inputs(assignments, candidates)
    expected_known = {
        "known-P-controlled": set(
            assignments["candidate_assignments"]["Nanosatellites"]["assigned_accessions"]
        )
        | set(
            assignments["candidate_assignments"]["Small satellites"]["assigned_accessions"]
        ),
        "known-MH-controlled": set(
            assignments["context_qualified_M_H_assignment"]["assigned_accessions"]
        ),
        "known-SysML-controlled": set(
            assignments["candidate_assignments"]["SysML"]["assigned_accessions"]
        ),
    }
    adapter = load_adapter()
    from playwright.async_api import async_playwright

    started_at = now()
    pass_artifacts: dict[str, list[dict[str, Any]]] = {
        cell_id: [] for cell_id in queries.VALUE_CELLS
    }
    current_cell: str | None = None
    current_pass: int | None = None
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as playwright:
            connection = None
            try:
                connection = await adapter.open_chrome_connection(
                    playwright,
                    cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                    headless=False,
                    timeout_seconds=timeout_seconds,
                    chrome_executable=None,
                    require_single_cdp_context=True,
                )
                for pass_number in (1, 2):
                    current_pass = pass_number
                    for cell_id, query in queries.VALUE_CELLS.items():
                        current_cell = cell_id
                        artifact = await collect_cell(
                            adapter,
                            connection,
                            cell_id,
                            query,
                            pass_number,
                            timeout_seconds,
                        )
                        path = output_dir / f"{cell_id}-pass{pass_number}.json"
                        path.write_text(
                            json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"
                        )
                        pass_artifacts[cell_id].append(artifact)
            finally:
                await adapter.close_chrome_connection(connection)
    except Exception as error:
        failure = {
            "schema_version": "compendex-controlled-vocabulary-value-failure/v1",
            "source": "Compendex",
            "pilot": "004",
            "status": "error",
            "do_not_merge": True,
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "started_at_utc": started_at,
            "failed_at_utc": now(),
            "stage": "terminal_single_page_value_cells",
            "cell_id": current_cell,
            "pass": current_pass,
            "error_type": type(error).__name__,
            "error": clean(error),
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False) + "\n")
        raise

    cells: dict[str, Any] = {}
    for cell_id, artifacts in pass_artifacts.items():
        if len(artifacts) != 2 or stable_projection(artifacts[0]) != stable_projection(artifacts[1]):
            raise RuntimeError(f"Compendex value cell {cell_id} changed across passes")
        active = artifacts[1]
        if cell_id in expected_known and set(active["ordered_stable_accessions"]) != expected_known[cell_id]:
            raise RuntimeError(f"Compendex known-set assignment cell {cell_id} disagreed with RIS assignments")
        cells[cell_id] = {
            "query": active["query"],
            "query_sha256": active["query_sha256"],
            "total": active["total"],
            "ordered_stable_accessions": active["ordered_stable_accessions"],
            "pass_artifacts": [
                f"cells/{cell_id}-pass1.json",
                f"cells/{cell_id}-pass2.json",
            ],
            "passes_equal": True,
            "terminal_page_contract": active["terminal_page_contract"],
        }
    candidate_only_ids: list[str] = []
    for cell_id in ("B1-MH-candidate-only", "B1-P-candidate-only"):
        for accession in cells[cell_id]["ordered_stable_accessions"]:
            if accession not in candidate_only_ids:
                candidate_only_ids.append(accession)
    reconciliation = {
        "schema_version": "compendex-controlled-vocabulary-value-comparison/v1",
        "source": "Compendex",
        "platform": "Engineering Village",
        "pilot": "004",
        "status": "complete_two_pass_terminal_cell_comparison",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "adapter": {"id": adapter.ADAPTER_ID, "version": adapter.ADAPTER_VERSION},
        "method": {
            "passes_per_cell": 2,
            "source_window": "Published 2011-2026",
            "common_evidence_cutoff": {
                "state": "TBD",
                "source_precision": "year",
                "handling": "Screen records in the cutoff year against the later exact common cutoff.",
            },
            "candidate_only_logic": (
                "Lossless two-route decomposition of descriptor-augmented B1 minus current "
                "post-proximity literal B1."
            ),
            "positive_control_contract": (
                "Exact source total, page 1 of 1, total-matching rows and stable accessions, "
                "no enabled Next, and complete native RIS reconciliation."
            ),
            "adapter_repair_state": (
                "Adapter v15 accepts the current omitted numeric interval as optional "
                "corroboration while retaining exact total, page, row, control, stable-ID, "
                "and native RIS checks. Separate bounded live checks validated a guarded "
                "two-page transition and strict two-pass publication."
            ),
        },
        "cells": cells,
        "known_set_mapping": {
            "selected_record_count": len(queries.SELECTED_KNOWN_RECORDS),
            "P_controlled_matched_count": cells["known-P-controlled"]["total"],
            "M_H_controlled_matched_count": cells["known-MH-controlled"]["total"],
            "SysML_controlled_matched_count": cells["known-SysML-controlled"]["total"],
        },
        "comparison": {
            "literal_B1_query_sha256": sha256_text(queries.B1_LITERAL),
            "augmented_B1_query_sha256": sha256_text(queries.B1_AUGMENTED),
            "candidate_only_route_totals": {
                "M_H": cells["B1-MH-candidate-only"]["total"],
                "P": cells["B1-P-candidate-only"]["total"],
            },
            "candidate_only_union_count": len(candidate_only_ids),
            "candidate_only_accessions": candidate_only_ids,
        },
        "boundaries": [
            "This is a diagnostic pilot and no artifact is merge eligible.",
            "No Pilot 003 changed-partition set is treated as current schedule evidence.",
            "No full B1 traversal was attempted under the missing-interval source state.",
        ],
    }
    reconciliation_path.parent.mkdir(parents=True, exist_ok=True)
    reconciliation_path.write_text(
        json.dumps(reconciliation, indent=2, ensure_ascii=False) + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assignments", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--failure-output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    asyncio.run(
        run(
            args.assignments,
            args.candidates,
            args.output_dir,
            args.reconciliation,
            args.failure_output,
            args.timeout,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
