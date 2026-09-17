#!/usr/bin/env python3
"""Build the IEEE Xplore Pilot 005 artifact ledger and assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from queries import CHANGED_IDS, SCHEDULE_IDS


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.IEEE_COMMIT.json")


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == sha256(path)
        and evidence.get("bytes") == path.stat().st_size
    )


def requested_query(artifact: dict[str, Any]) -> str:
    metadata = artifact.get("output_metadata", {})
    return (
        artifact.get("requested_query")
        or metadata.get("requested_query")
        or artifact.get("query")
        or artifact.get("executed_query")
        or ""
    )


def query_echo_exact(artifact: dict[str, Any], expected: str) -> bool:
    if artifact.get("executed_query") == expected:
        return True
    receipt = artifact.get("output_metadata", {}).get("ieee_observation_receipt", {})
    return receipt.get("rendered_state", {}).get("query_echo") == "exact"


def artifact_entry(
    pilot_root: Path, event: dict[str, Any], path: Path
) -> dict[str, Any]:
    artifact = load(path)
    metadata = artifact.get("output_metadata", {})
    status = metadata.get("status")
    receipt = metadata.get("ieee_observation_receipt", {})
    year = metadata.get("publication_year_readback", {})
    marker = marker_path(path)
    return {
        "event_id": event["event_id"],
        "schedule_id": event["schedule_id"],
        "mode": event["mode"],
        "path": str(path.relative_to(pilot_root)),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "status": status,
        "total": artifact.get("total"),
        "record_count": len(artifact.get("results", [])),
        "do_not_merge": artifact.get("do_not_merge") is True,
        "requested_query_matches_plan": requested_query(artifact) == event["query"],
        "exact_query_echo_observed": query_echo_exact(artifact, event["query"]),
        "year_readback_state": year.get("state"),
        "year_native_range_echo": year.get("native_range_echo"),
        "year_result_refinement_range": year.get("result_refinement_range"),
        "error_stage": metadata.get("error_stage"),
        "year_control_state": receipt.get("year_control", {}).get("state"),
        "year_start_fill": receipt.get("year_control", {}).get("start_fill"),
        "year_end_fill": receipt.get("year_control", {}).get("end_fill"),
        "year_apply_enabled_after_fill": receipt.get("year_control", {}).get(
            "apply_enabled_after_fill"
        ),
        "strict_passes_completed": receipt.get("strict_completion", {}).get(
            "passes_completed", 0
        ),
        "commit_marker": str(marker.relative_to(pilot_root)) if marker.exists() else None,
        "commit_marker_valid": marker_valid(path),
    }


def old_partition_map(old_union: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["partition_id"]: item
        for item in old_union.get("partitions", [])
        if isinstance(item, dict) and isinstance(item.get("partition_id"), str)
    }


def build(
    pilot_root: Path,
    plan_path: Path,
    raw_receipt_path: Path,
    reconciled_receipt_path: Path,
    old_union_path: Path,
) -> dict[str, Any]:
    plan = load(plan_path)
    raw_receipt = load(raw_receipt_path)
    reconciled_receipt = load(reconciled_receipt_path)
    old = old_partition_map(load(old_union_path))
    events = plan["events"]
    entries = []
    by_event: dict[str, dict[str, Any]] = {}
    for event in events:
        path = pilot_root / "searches" / event["output"]
        entry = artifact_entry(pilot_root, event, path)
        entries.append(entry)
        by_event[event["event_id"]] = entry

    partitions: dict[str, Any] = {}
    for schedule_id in SCHEDULE_IDS:
        pass1 = by_event[f"count-{schedule_id}-pass1"]
        pass2 = by_event[f"count-{schedule_id}-pass2"]
        totals = [pass1["total"], pass2["total"]]
        repeated = (
            totals[0]
            if isinstance(totals[0], int) and totals[0] == totals[1]
            else None
        )
        direct_events = [entry for entry in entries if entry["schedule_id"] == schedule_id]
        strict = by_event.get(f"records-{schedule_id}")
        stable_ids = None
        if strict and strict["status"] == "success":
            strict_artifact = load(pilot_root / strict["path"])
            stable_ids = [row["paperId"] for row in strict_artifact.get("results", [])]
        partitions[schedule_id] = {
            "query_characters": plan["translation"]["query_lengths"][schedule_id],
            "query_sha256": plan["translation"]["query_sha256"][schedule_id],
            "direct_query_echo_observed": any(
                entry["exact_query_echo_observed"] for entry in direct_events
            ),
            "count_passes": [
                {
                    "status": pass1["status"],
                    "total": pass1["total"],
                    "error_stage": pass1["error_stage"],
                },
                {
                    "status": pass2["status"],
                    "total": pass2["total"],
                    "error_stage": pass2["error_stage"],
                },
            ],
            "repeated_source_total": repeated,
            "strict_capture": (
                {
                    "status": strict["status"],
                    "total": strict["total"],
                    "stable_article_numbers": stable_ids,
                    "strict_passes_completed_before_failure": strict[
                        "strict_passes_completed"
                    ],
                    "error_stage": strict["error_stage"],
                }
                if strict
                else None
            ),
        }

    comparisons = {}
    for schedule_id in CHANGED_IDS:
        historical = old[schedule_id]
        current = partitions[schedule_id]
        comparisons[schedule_id] = {
            "pilot_004_definition": "superseded pair-based construction",
            "pilot_004_union_status": historical.get("union_status"),
            "pilot_004_complete_total": historical.get(
                "deduplicated_article_number_count"
            ),
            "pilot_004_complete_article_numbers": historical.get(
                "deduplicated_article_number_union"
            ),
            "pilot_004_partial_article_numbers_not_a_union": historical.get(
                "partial_reconciled_article_numbers_not_a_union"
            ),
            "pilot_005_definition": "post-proximity Boolean construction",
            "pilot_005_repeated_total": current["repeated_source_total"],
            "pilot_005_strict_article_numbers": current["strict_capture"][
                "stable_article_numbers"
            ],
            "comparison_status": (
                "descriptive_total_only_no_current_stable_id_capture"
                if current["repeated_source_total"] is not None
                else "not_comparable_current_total_null"
            ),
        }

    successful_entries = [entry for entry in entries if entry["status"] in {"count_only", "success"}]
    failed_entries = [entry for entry in entries if entry["status"] == "error"]
    return {
        "schema_version": "ieee-xplore-pilot-005-assessment/v1",
        "source": "IEEE Xplore",
        "pilot": "005",
        "protocol_commit": plan["protocol_commit"],
        "diagnostic_only": True,
        "do_not_merge": True,
        "controls": plan["date_window"] | plan["controls"],
        "execution": {
            "predeclared_event_count": len(events),
            "retained_artifact_count": len(entries),
            "successful_source_event_count": len(successful_entries),
            "failed_source_event_count": len(failed_entries),
            "successful_commit_marker_count": sum(
                entry["commit_marker_valid"] for entry in successful_entries
            ),
            "failed_artifact_commit_marker_count": sum(
                entry["commit_marker_valid"] for entry in failed_entries
            ),
            "raw_run_receipt": str(raw_receipt_path.relative_to(pilot_root)),
            "raw_run_receipt_sha256": sha256(raw_receipt_path),
            "raw_receipt_classifier_result": {
                "successful_source_event_count": raw_receipt.get(
                    "successful_source_event_count"
                ),
                "failed_source_event_count": raw_receipt.get(
                    "failed_source_event_count"
                ),
                "limitation": (
                    "The initial local classifier expected full query metadata and a terminal marker "
                    "on failed artifacts. It did not affect any adapter event."
                ),
            },
            "reconciled_run_receipt": str(
                reconciled_receipt_path.relative_to(pilot_root)
            ),
            "reconciled_run_receipt_sha256": sha256(reconciled_receipt_path),
            "reconciled_receipt_status": reconciled_receipt.get("status"),
            "reconciled_receipt_reused_only": all(
                outcome.get("reused_existing") is True
                for outcome in reconciled_receipt.get("outcomes", [])
            ),
            "source_reruns_after_initial_plan": 0,
        },
        "artifact_ledger": entries,
        "partitions": partitions,
        "changed_partition_comparison": comparisons,
        "findings": {
            "all_nine_direct_queries_echoed_exactly_at_least_once": all(
                partitions[schedule_id]["direct_query_echo_observed"]
                for schedule_id in SCHEDULE_IDS
            ),
            "repeated_totals": {
                schedule_id: partitions[schedule_id]["repeated_source_total"]
                for schedule_id in SCHEDULE_IDS
            },
            "repeated_nonnull_totals": {
                schedule_id: partitions[schedule_id]["repeated_source_total"]
                for schedule_id in SCHEDULE_IDS
                if partitions[schedule_id]["repeated_source_total"] is not None
            },
            "changed_strict_capture_success_count": sum(
                partitions[schedule_id]["strict_capture"]["status"] == "success"
                for schedule_id in CHANGED_IDS
            ),
            "changed_strict_capture_failure_count": sum(
                partitions[schedule_id]["strict_capture"]["status"] == "error"
                for schedule_id in CHANGED_IDS
            ),
            "year_fill_or_enable_failures": sum(
                entry["error_stage"] == "year_fill_readback" for entry in entries
            ),
            "initial_form_readiness_failures": sum(
                entry["error_stage"] == "initial_form_readiness" for entry in entries
            ),
            "rendered_state_failures": sum(
                entry["error_stage"] == "rendered_state" for entry in entries
            ),
        },
        "conclusion": {
            "source_translation": (
                "The source echoed every complete direct post-proximity expression. "
                "No query split is indicated by the observed query readback."
            ),
            "source_controls": (
                "The native Publication Year control remained unstable. Only A3, B2, and BG1 "
                "produced equal totals twice. All four changed strict captures ended with total null."
            ),
            "completion": (
                "Pilot 005 validates direct query acceptance but does not validate a complete "
                "date-controlled schedule or authorize a final search."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--raw-run-receipt", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--pilot004-union", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(
        args.pilot_root,
        args.plan,
        args.raw_run_receipt,
        args.run_receipt,
        args.pilot004_union,
    )
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
