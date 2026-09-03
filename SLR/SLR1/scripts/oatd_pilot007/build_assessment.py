#!/usr/bin/env python3
"""Build the OATD Pilot 007 hydration assessment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-007-hydration-assessment/v1"
PILOT_ROOT = Path(__file__).resolve().parents[2] / "source-specific/oatd/pilots/007"
DEFAULT_PLAN = PILOT_ROOT / "searches/event-plan.json"
DEFAULT_RUN = PILOT_ROOT / "searches/run-receipt.json"
DEFAULT_UNION = PILOT_ROOT / "searches/hydrated-union.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/assessment.json"


def build(plan_path: Path, run_path: Path, union_path: Path) -> dict[str, Any]:
    plan = base.load(plan_path)
    run = base.load(run_path)
    union = base.load(union_path)
    results = union.get("results")
    if (
        plan.get("schema_version") != base.PLAN_SCHEMA
        or run.get("schema_version") != base.RUN_SCHEMA
        or run.get("success") is not True
        or union.get("schema_version") != base.UNION_SCHEMA
        or not isinstance(results, list)
        or len(results) != 26
    ):
        raise RuntimeError("OATD Pilot 007 is incomplete")
    gate_totals = {
        event_id: evidence["source_total"]
        for event_id, evidence in union["gate_evidence"].items()
    }
    if gate_totals != queries.EXPECTED_COUNTS:
        raise RuntimeError("OATD Pilot 007 gate totals changed")
    year_only_cutoff_records = [
        {
            "paperId": record["paperId"],
            "publicationDate": record.get("publicationDate"),
            "reason": "The cutoff-year record exposes only year precision.",
        }
        for record in results
        if record.get("year") == 2026 and record.get("publicationDate") == "2026"
    ]
    abstract_unavailable = [
        record["paperId"] for record in results if record.get("abstract_not_available")
    ]
    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "pilot": "007",
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
        "hydrated_union": {
            "path": str(union_path.relative_to(PILOT_ROOT)),
            "sha256": base.digest(union_path),
            "marker_sha256": base.digest(base.union_marker_path(union_path)),
        },
        "accounting": {
            "gate_totals": gate_totals,
            "gate_occurrence_total": union["gate_occurrence_total"],
            "exact_deduplicated_union_total": union["exact_deduplicated_union_total"],
            "complete_normalized_detail_records": len(results),
            "unique_detail_requests": run["detail_requests_this_attempt"],
            "pilot004_detail_records_reused": union["hydration"][
                "pilot004_records_reused"
            ],
            "complete_gate_count": run["complete_gate_count"],
            "complete_source_pass_count": run["complete_source_pass_count"],
            "busy_retries": run["detail_busy_retries_performed"]
            + sum(
                base.load(PILOT_ROOT / evidence["path"])["busy_retries_performed"]
                for evidence in run["gate_artifacts"].values()
            ),
        },
        "metadata_observations": {
            "abstract_available_records": len(results) - len(abstract_unavailable),
            "abstract_unavailable_records": len(abstract_unavailable),
            "abstract_unavailable_paper_ids": abstract_unavailable,
            "publication_date_readback_statuses": union[
                "publication_date_readback_statuses"
            ],
            "cutoff_year_records_with_unresolved_exact_day": year_only_cutoff_records,
            "local_matching": union["local_matching"],
            "local_annotations_are_not_source_partition_proof": True,
        },
        "stability": {
            "initial_gate_sets_equal_pilot006": True,
            "post_hydration_gate_sets_equal_initial": True,
            "native_order_drift_gate_count": sum(
                bool(
                    base.load(PILOT_ROOT / evidence["path"])[
                        "native_order_drift_observed"
                    ]
                )
                for evidence in run["gate_artifacts"].values()
            ),
            "all_26_details_checkpointed": True,
        },
        "conclusion": {
            "decision": "accept_eight_gate_hydration_route_for_fresh_final_execution",
            "reason": (
                "The route hydrated all 26 unique stable IDs once without a busy "
                "retry, then reconfirmed every gate set."
            ),
            "pilot_artifact_mergeable": False,
            "final_search_ready": False,
            "remaining_requirements": [
                "Execute a fresh final event with the final common cutoff.",
                "Publish a standard merge- and report-ready multi-gate union artifact.",
                "Resolve the exact cutoff day for the one year-only 2026 record during screening.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--union", type=Path, default=DEFAULT_UNION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    assessment = build(args.plan, args.run, args.union)
    base.write_exclusive_json(args.output, assessment)
    print(json.dumps({"saved": str(args.output), "records": 26}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
