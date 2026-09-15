#!/usr/bin/env python3
"""Build the OATD Pilot 006 card-ID union assessment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-006-card-id-assessment/v1"
PILOT_ROOT = Path(__file__).resolve().parents[4] / "source-specific/oatd/pilots/006"
DEFAULT_PLAN = PILOT_ROOT / "searches/event-plan.json"
DEFAULT_RUN = PILOT_ROOT / "searches/run-receipt.json"
DEFAULT_RECONCILIATION = PILOT_ROOT / "searches/reconciliation.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/assessment.json"


def build(plan_path: Path, run_path: Path, reconciliation_path: Path) -> dict[str, Any]:
    plan = base.load(plan_path)
    run = base.load(run_path)
    reconciliation = base.load(reconciliation_path)
    outcomes = run.get("outcomes")
    if (
        plan.get("schema_version") != base.PLAN_SCHEMA
        or plan.get("event_count") != 8
        or run.get("schema_version") != base.RUN_SCHEMA
        or run.get("success") is not True
        or run.get("completed_gate_count") != 8
        or not isinstance(outcomes, list)
        or len(outcomes) != 8
        or reconciliation.get("schema_version") != base.RECONCILIATION_SCHEMA
    ):
        raise RuntimeError("OATD Pilot 006 is incomplete")
    gate_totals = reconciliation.get("gate_totals")
    if gate_totals != queries.EXPECTED_PILOT005_COUNTS:
        raise RuntimeError("OATD Pilot 006 gate totals drifted")
    union_total = reconciliation.get("exact_deduplicated_union_total")
    occurrence_total = reconciliation.get("gate_occurrence_total")
    duplicates = reconciliation.get("cross_gate_duplicate_occurrences")
    reuse = reconciliation.get("pilot004_checkpoint_reuse")
    if (
        union_total != 26
        or occurrence_total != 34
        or duplicates != 8
        or not isinstance(reuse, dict)
        or reuse.get("validated_detail_records_available") != 9
        or reuse.get("remaining_unique_details_to_hydrate") != 17
    ):
        raise RuntimeError("OATD Pilot 006 union accounting is invalid")
    gate_evidence = []
    for outcome in outcomes:
        output = PILOT_ROOT / outcome["artifact"]
        gate_evidence.append(
            {
                "event_id": outcome["event_id"],
                "artifact": outcome["artifact"],
                "sha256": base.digest(output),
                "source_total": outcome["source_total"],
                "two_pass_set_reconciled": True,
                "native_order_drift_observed": outcome["native_order_drift_observed"],
                "busy_retries_performed": outcome["busy_retries_performed"],
            }
        )
    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "pilot": "006",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": {
            "path": str(plan_path.relative_to(PILOT_ROOT)),
            "sha256": base.digest(plan_path),
        },
        "run": {
            "path": str(run_path.relative_to(PILOT_ROOT)),
            "sha256": base.digest(run_path),
        },
        "reconciliation": {
            "path": str(reconciliation_path.relative_to(PILOT_ROOT)),
            "sha256": base.digest(reconciliation_path),
        },
        "gate_evidence": gate_evidence,
        "accounting": {
            "complete_gate_count": 8,
            "complete_source_pass_count": 16,
            "source_detail_requests": 0,
            "gate_occurrence_total": occurrence_total,
            "exact_deduplicated_union_total": union_total,
            "cross_gate_duplicate_occurrences": duplicates,
            "P_only_baseline_total": 1249,
            "candidate_reduction_from_P": 1249 - union_total,
            "candidate_reduction_percent": round((1249 - union_total) * 100 / 1249, 4),
            "pilot004_validated_details_in_union": reuse[
                "validated_detail_records_available"
            ],
            "union_ids_without_pilot004_details": reuse[
                "remaining_unique_details_to_hydrate"
            ],
        },
        "stability": {
            "all_gate_totals_equal_pilot005": True,
            "all_two_pass_stable_id_sets_equal": True,
            "native_order_drift_gate_count": sum(
                bool(item["native_order_drift_observed"]) for item in gate_evidence
            ),
            "busy_retry_count": sum(
                item["busy_retries_performed"] for item in gate_evidence
            ),
        },
        "conclusion": {
            "decision": "accept_exact_gate_id_union_for_detail_hydration_pilot",
            "exact_source_candidate_total": union_total,
            "reason": (
                "All eight gates completed two source-rendered card-ID passes with "
                "equal stable-ID sets. Their 34 occurrences deduplicated to 26 IDs "
                "without requesting any Record Details page."
            ),
            "final_search_ready": False,
            "next_required_evidence": (
                "Hydrate each of the 26 stable IDs once under a predeclared bounded "
                "detail route, then obtain fresh confirming gate snapshots."
            ),
            "pilot004_detail_reuse_approved_for_final_search": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--reconciliation", type=Path, default=DEFAULT_RECONCILIATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    assessment = build(args.plan, args.run, args.reconciliation)
    base.write_exclusive_json(args.output, assessment)
    print(json.dumps({"saved": str(args.output), "union_total": 26}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
