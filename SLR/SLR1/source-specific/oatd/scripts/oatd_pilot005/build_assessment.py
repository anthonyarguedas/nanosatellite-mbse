#!/usr/bin/env python3
"""Build the OATD Pilot 005 count assessment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_pilot as base
import split_queries

SCHEMA = "oatd-pilot-005-gate-count-assessment/v1"
RUN_SCHEMA = "oatd-pilot-005-split-gate-count-run/v1"
PILOT_ROOT = Path(__file__).resolve().parents[4] / "source-specific/oatd/pilots/005"
DEFAULT_PLAN = PILOT_ROOT / "searches/split-continuation-plan.json"
DEFAULT_RUN = PILOT_ROOT / "searches/split-continuation-run-receipt.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/assessment.json"
BASELINE_TOTAL = 1249


def build(plan_path: Path, run_path: Path) -> dict[str, Any]:
    plan = base.load(plan_path)
    run = base.load(run_path)
    outcomes = run.get("outcomes")
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("success") is not True
        or not isinstance(outcomes, list)
        or len(outcomes) != 8
    ):
        raise RuntimeError("OATD Pilot 005 lacks eight complete gate counts")
    expected_ids = ["G1-MH", *split_queries.SPLIT_GATE_IDS]
    if [item.get("event_id") for item in outcomes] != expected_ids:
        raise RuntimeError("OATD Pilot 005 gate order changed")
    counts: dict[str, int] = {}
    evidence: list[dict[str, Any]] = []
    for outcome in outcomes:
        total = outcome.get("total")
        output = PILOT_ROOT / outcome["output"]
        if (
            outcome.get("valid_count_artifact") is not True
            or not isinstance(total, int)
            or isinstance(total, bool)
            or not 0 <= total < BASELINE_TOTAL
            or not output.is_file()
        ):
            raise RuntimeError(f"Invalid OATD gate outcome: {outcome.get('event_id')}")
        counts[outcome["event_id"]] = total
        evidence.append(
            {
                "event_id": outcome["event_id"],
                "artifact": outcome["output"],
                "sha256": base.digest(output),
                "total": total,
                "reduction_from_p_count": BASELINE_TOTAL - total,
                "reduction_percent": round(
                    (BASELINE_TOTAL - total) * 100 / BASELINE_TOTAL, 4
                ),
            }
        )
    occurrence_total = sum(counts.values())
    largest = max(counts.values())
    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "pilot": "005",
        "protocol_commit": split_queries.PROTOCOL_COMMIT,
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
        "algebraic_candidate_union": plan["algebraic_candidate_union"],
        "baseline": {
            "P_only_source_total": BASELINE_TOTAL,
            "partially_hydrated_P_records": 338,
        },
        "gate_counts": counts,
        "gate_evidence": evidence,
        "accounting": {
            "complete_gate_count": len(counts),
            "largest_gate_total": largest,
            "gate_occurrence_total": occurrence_total,
            "candidate_union_upper_bound": occurrence_total,
            "candidate_union_exact_total": None,
            "candidate_union_exact_total_reason": (
                "Count-only events do not expose stable IDs for cross-gate deduplication."
            ),
            "minimum_candidate_reduction_from_P": BASELINE_TOTAL - occurrence_total,
            "minimum_candidate_reduction_percent": round(
                (BASELINE_TOTAL - occurrence_total) * 100 / BASELINE_TOTAL, 4
            ),
        },
        "superseded_combined_gate": {
            "event_id": "G2-MB",
            "total": None,
            "failure": "OATD page did not become ready in time.",
            "interpretation": (
                "The four exact split branches replace this null event. The null is "
                "not a zero and contributes no count evidence."
            ),
        },
        "conclusion": {
            "decision": "accept_eight_exact_gates_for_card_id_union_pilot",
            "broad_P_detail_harvest": "retire",
            "reason": (
                "All eight exact gates completed count-only source readback. Their "
                "largest total was 16 and their summed upper bound was 34, compared "
                "with 1,249 records for P alone."
            ),
            "final_search_ready": False,
            "next_required_evidence": (
                "Collect and reconcile complete stable-ID snapshots for every gate, "
                "deduplicate the union, and hydrate each union ID once."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    assessment = build(args.plan, args.run)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"saved": str(args.output), "status": "complete"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
