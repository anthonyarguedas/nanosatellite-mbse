#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Capture stable card IDs excluded by LA(English) in the full schedule union."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = Path.home() / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot006_language_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    async def card_only(
        page: Any,
        *,
        row_index: int,
        row: dict[str, Any],
        query: str,
        expected_page_number: int,
        timeout_seconds: float,
        complete_mode: bool = False,
        ownership_reassertion: Any | None = None,
        structured_restrictions: dict[str, Any] | None = None,
        facet_evidence: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], Any]:
        del row_index
        record = module.normalize_proquest_record(row, detail=None)
        state = await module.wait_for_proquest_page(
            page,
            query=query,
            include_records=True,
            expected_page_number=expected_page_number,
            timeout_seconds=timeout_seconds,
            complete_mode=complete_mode,
            ownership_reassertion=ownership_reassertion,
        )
        return record, module.replace(
            state,
            structured_restrictions=structured_restrictions,
            facet_evidence=facet_evidence,
        )

    module.read_detail_for_proquest_row = card_only
    return module


def save(adapter: Any, path: Path, result: dict[str, Any], pass_number: int) -> None:
    artifact = adapter.mark_non_mergeable(result)
    compact = adapter.compact_search_result_for_output(artifact)
    compact["pilot_context"] = {
        "pilot": "006",
        "attempt": "retry5",
        "pass": pass_number,
        "capture": "card_level_language_exclusion_ids_without_detail_pages",
        "do_not_merge": True,
    }
    path.write_text(json.dumps(compact, indent=2, ensure_ascii=False) + "\n")


def run(plan_path: Path, output_dir: Path, reconciliation_path: Path) -> None:
    plan = json.loads(plan_path.read_text())
    if plan.get("schema_version") != "atai-pilot-006-retry3-plan/v1":
        raise RuntimeError("Unexpected retry 3 plan.")
    event = next(
        event for event in plan["events"]
        if event["event_id"] == "language-union-not-english-count-pass1"
    )
    adapter = load_adapter()
    passes = []
    for pass_number in (1, 2):
        result = adapter.search_proquest_aerospace(
            event["query"],
            limit=10_000,
            max_pages=500,
            timeout_seconds=180,
            page_delay_seconds=0.25,
            count_only=False,
            require_complete=False,
            date_start="2011-01-01",
            date_end="2026-08-29",
            cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
            prisma_context={
                "run_id": f"atai-p006-language-exclusions-card-pass{pass_number}",
                "review_id": "slr1-atai-pilot-006",
                "strategy_reference": "slr1-atai-language-exclusion-id-diagnostic-v1",
                "strategy_version": event["query_sha256"],
                "phase": "identification",
                "coverage_scope": "partition",
                "is_full_source_coverage": False,
                "partition_id": "language-union-not-english",
                "partition_label": "language-union-not-english",
                "partition_description": "Pilot-only card-level IDs excluded by LA(English).",
            },
        )
        ids = [str(record.get("paperId", "")) for record in result.get("results", [])]
        if result.get("total") != 2 or len(ids) != 2 or len(set(ids)) != 2:
            raise RuntimeError("Language-exclusion card capture did not reconcile to two IDs.")
        path = output_dir / f"language-exclusions-card-pass{pass_number}.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        save(adapter, path, result, pass_number)
        passes.append({"ids": ids, "records": result["results"], "artifact": path.name})
    if passes[0]["ids"] != passes[1]["ids"]:
        raise RuntimeError("Language-exclusion ordered IDs changed across passes.")
    reconciliation = {
        "schema_version": "atai-pilot-006-language-exclusion-id-reconciliation/v1",
        "source": plan["source"],
        "pilot": "006",
        "attempt": "retry5",
        "status": "complete_two_pass_card_id_reconciliation",
        "do_not_merge": True,
        "query": event["query"],
        "source_total": 2,
        "stable_ids_in_source_order": passes[1]["ids"],
        "records": [
            {
                "paper_id": record["paperId"],
                "title": record["title"],
                "year": record["year"],
                "document_type": record["documentType"],
                "snippet": record["snippet"],
                "canonical_url": record["url"],
            }
            for record in passes[1]["records"]
        ],
        "passes": 2,
        "ordered_ids_equal": True,
        "artifacts": [passes[0]["artifact"], passes[1]["artifact"]],
        "interpretation": "These are the complete schedule-union records outside source metadata LA(English). Their report languages remain to be checked.",
    }
    reconciliation_path.write_text(json.dumps(reconciliation, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry3-plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    args = parser.parse_args()
    run(args.retry3_plan, args.output_dir, args.reconciliation)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
