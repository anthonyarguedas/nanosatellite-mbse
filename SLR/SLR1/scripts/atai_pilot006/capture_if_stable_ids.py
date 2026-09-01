#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Capture two-pass card-level stable IDs for IF-affected ATAI partitions."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = Path.home() / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
PARTITIONS = ("B1", "B2", "BC1", "BT2")


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot006_if_adapter", ADAPTER_PATH)
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
        state = module.replace(
            state,
            structured_restrictions=structured_restrictions,
            facet_evidence=facet_evidence,
        )
        return record, state

    module.read_detail_for_proquest_row = card_only
    return module


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def save(adapter: Any, path: Path, result: dict[str, Any], context: dict[str, Any]) -> None:
    artifact = adapter.mark_non_mergeable(result)
    compact = adapter.compact_search_result_for_output(artifact)
    compact["pilot_context"] = context
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(compact, indent=2, ensure_ascii=False) + "\n")


def run(plan_path: Path, output_dir: Path, reconciliation_path: Path) -> None:
    plan = json.loads(plan_path.read_text())
    if plan.get("schema_version") != "atai-pilot-006-retry3-plan/v1":
        raise RuntimeError("Unexpected retry 3 plan.")
    adapter = load_adapter()
    by_id = {event["event_id"]: event for event in plan["events"]}
    reconciliation: dict[str, Any] = {
        "schema_version": "atai-pilot-006-if-stable-id-reconciliation/v1",
        "source": plan["source"],
        "pilot": "006",
        "attempt": "retry4",
        "status": "running",
        "do_not_merge": True,
        "method": "Two ordinary exhaustive card-level passes per cell. No Abstract/Details route is used. This is stable-ID evidence only.",
        "cells": {},
    }
    for partition in PARTITIONS:
        forms: dict[str, list[str]] = {}
        for form in ("literal", "augmented"):
            event = by_id[f"if-{partition}-{form}-count-pass1"]
            passes = []
            for pass_number in (1, 2):
                path = output_dir / f"{partition}-{form}-card-pass{pass_number}.json"
                if path.exists():
                    raise RuntimeError(f"Refusing to overwrite {path}")
                result = adapter.search_proquest_aerospace(
                    event["query"],
                    limit=10_000,
                    language="English",
                    max_pages=500,
                    timeout_seconds=180,
                    page_delay_seconds=0.25,
                    count_only=False,
                    require_complete=False,
                    date_start="2011-01-01",
                    date_end="2026-08-29",
                    cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                    prisma_context={
                        "run_id": f"atai-p006-if-{partition}-{form}-card-pass{pass_number}",
                        "review_id": "slr1-atai-pilot-006",
                        "strategy_reference": "slr1-atai-if-stable-id-diagnostic-v1",
                        "strategy_version": event["query_sha256"],
                        "phase": "identification",
                        "coverage_scope": "partition",
                        "is_full_source_coverage": False,
                        "partition_id": f"if-{partition}-{form}",
                        "partition_label": f"if-{partition}-{form}",
                        "partition_description": "Pilot-only card-level stable-ID capture.",
                    },
                )
                save(
                    adapter,
                    path,
                    result,
                    {
                        "pilot": "006",
                        "attempt": "retry4",
                        "partition": partition,
                        "form": form,
                        "pass": pass_number,
                        "capture": "card_level_stable_ids_without_detail_pages",
                        "do_not_merge": True,
                    },
                )
                ids = [clean(record.get("paperId")) for record in result.get("results", [])]
                if result.get("total") != len(ids) or len(ids) != len(set(ids)):
                    raise RuntimeError(f"{partition} {form} pass {pass_number} did not reconcile.")
                passes.append({"total": result["total"], "ids": ids, "artifact": path.name})
            if passes[0]["total"] != passes[1]["total"] or passes[0]["ids"] != passes[1]["ids"]:
                raise RuntimeError(f"{partition} {form} card passes changed.")
            forms[form] = passes[1]["ids"]
            reconciliation["cells"][f"{partition}-{form}"] = {
                "source_total": passes[1]["total"],
                "stable_ids_in_source_order": passes[1]["ids"],
                "passes": 2,
                "ordered_ids_equal": True,
                "artifacts": [passes[0]["artifact"], passes[1]["artifact"]],
            }
        literal = set(forms["literal"])
        augmented = forms["augmented"]
        if not literal.issubset(set(augmented)):
            raise RuntimeError(f"{partition} IF augmentation lost literal IDs.")
        reconciliation["cells"][partition] = {
            "literal_total": len(forms["literal"]),
            "augmented_total": len(augmented),
            "candidate_only_ids": [paper_id for paper_id in augmented if paper_id not in literal],
        }
        reconciliation_path.parent.mkdir(parents=True, exist_ok=True)
        reconciliation_path.write_text(json.dumps(reconciliation, indent=2) + "\n")
    candidate_union = []
    for partition in PARTITIONS:
        for paper_id in reconciliation["cells"][partition]["candidate_only_ids"]:
            if paper_id not in candidate_union:
                candidate_union.append(paper_id)
    reconciliation["candidate_only_union_ids"] = candidate_union
    reconciliation["candidate_only_union_total"] = len(candidate_union)
    reconciliation["status"] = "complete_two_pass_card_id_reconciliation"
    reconciliation_path.write_text(json.dumps(reconciliation, indent=2) + "\n")


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
