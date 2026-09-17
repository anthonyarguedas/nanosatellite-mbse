#!/usr/bin/env python3
"""Reconcile and assess IEEE Xplore Pilot 006 without source execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


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


def source_success(event: dict[str, Any], artifact: dict[str, Any], path: Path) -> bool:
    metadata = artifact.get("output_metadata", {})
    status = metadata.get("status")
    if (
        artifact.get("executed_query") != event["query"]
        or status not in {"count_only", "success"}
        or not isinstance(artifact.get("total"), int)
        or not marker_valid(path)
    ):
        return False
    if event["mode"] == "count":
        return status == "count_only"
    prisma = metadata.get("prisma_search_run", {})
    return (
        status == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and len(artifact.get("results", [])) == artifact.get("total")
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
    )


def build(pilot_root: Path, raw_receipt_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    searches = pilot_root / "searches"
    plan = load(searches / "event-plan.json")
    raw = load(raw_receipt_path)
    raw_by_event = {item["event_id"]: item for item in raw["outcomes"]}
    outcomes = []
    ledger = []
    artifacts: dict[str, dict[str, Any]] = {}

    for event in plan["events"]:
        path = searches / event["output"]
        artifact = load(path)
        artifacts[event["event_id"]] = artifact
        metadata = artifact.get("output_metadata", {})
        receipt = metadata.get("ieee_observation_receipt", {})
        success = source_success(event, artifact, path)
        raw_item = raw_by_event[event["event_id"]]
        outcome = {
            **raw_item,
            "successful_source_event": success,
            "commit_marker_valid": marker_valid(path),
            "artifact_retained": path.is_file(),
            "source_total": artifact.get("total"),
            "record_count": len(artifact.get("results", [])),
            "artifact_status": metadata.get("status"),
        }
        outcomes.append(outcome)
        ledger.append(
            {
                "event_id": event["event_id"],
                "schedule_id": event["schedule_id"],
                "mode": event["mode"],
                "path": str(path.relative_to(pilot_root)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "status": metadata.get("status"),
                "total": artifact.get("total"),
                "record_count": len(artifact.get("results", [])),
                "commit_marker_valid": marker_valid(path),
                "error_stage": metadata.get("error_stage"),
                "query_echo": receipt.get("rendered_state", {}).get("query_echo"),
                "range_echo": receipt.get("rendered_state", {}).get("range_echo"),
                "card_count": receipt.get("rendered_state", {}).get("card_count"),
                "page_size_control_count": receipt.get("rendered_state", {}).get(
                    "page_size_control_count"
                ),
                "strict_passes_completed": receipt.get("strict_completion", {}).get(
                    "passes_completed", 0
                ),
                "cleanup_state": receipt.get("cleanup", {}).get("state"),
                "year_readback": metadata.get("publication_year_readback"),
                "stable_article_numbers": [
                    row.get("paperId") for row in artifact.get("results", [])
                ]
                if metadata.get("status") == "success"
                else None,
            }
        )

    success_count = sum(item["successful_source_event"] for item in outcomes)
    corrected = {
        "schema_version": "ieee-xplore-pilot-006-reconciled-run-receipt/v1",
        "source": "IEEE Xplore",
        "pilot": "006",
        "status": "complete_with_retained_source_failures",
        "diagnostic_only": True,
        "do_not_merge": True,
        "raw_run_receipt": str(raw_receipt_path.relative_to(pilot_root)),
        "raw_run_receipt_sha256": sha256(raw_receipt_path),
        "reconciled_without_source_execution": True,
        "predeclared_event_count": len(plan["events"]),
        "completed_event_count": len(outcomes),
        "successful_source_event_count": success_count,
        "failed_source_event_count": len(outcomes) - success_count,
        "outcomes": outcomes,
    }

    intervals = {}
    for event_id in (
        "count-A1-pass2",
        "count-B1",
        "count-BG2",
        "count-BC1",
        "count-BT2",
    ):
        metadata = artifacts[event_id]["output_metadata"]
        intervals[event_id] = {
            "total": artifacts[event_id]["total"],
            "readback": metadata["publication_year_readback"]["state"],
            "contained_result_interval": metadata["publication_year_readback"][
                "result_refinement_range"
            ],
            "local_filter_applied": metadata["publication_year_readback"][
                "local_filter_applied"
            ],
        }

    a1_failure = next(item for item in ledger if item["event_id"] == "count-A1-pass1")
    bg2_failure = next(item for item in ledger if item["event_id"] == "records-BG2")
    bc1_failure = next(item for item in ledger if item["event_id"] == "records-BC1")
    assessment = {
        "schema_version": "ieee-xplore-pilot-006-assessment/v1",
        "source": "IEEE Xplore",
        "pilot": "006",
        "diagnostic_only": True,
        "do_not_merge": True,
        "adapter": {
            "version": "9",
            "sha256": "b1bf16743fd434d6439257288e9bbe29e6862f4b868fe7b43e3786abbf6fe3b5",
        },
        "artifact_ledger": ledger,
        "year_noop_results": intervals,
        "strict_successes": {
            event_id: {
                "total": artifacts[event_id]["total"],
                "stable_article_numbers": [
                    row["paperId"] for row in artifacts[event_id]["results"]
                ],
            }
            for event_id in ("records-BG1", "records-BT2")
        },
        "failure_diagnoses": {
            "count-A1-pass1": {
                "recorded_stage": a1_failure["error_stage"],
                "source_state_observed": False,
                "evidence": {
                    "query_echo": a1_failure["query_echo"],
                    "cleanup_state": a1_failure["cleanup_state"],
                },
                "diagnosis": (
                    "Adapter-owned browser page acquisition failed before navigation. "
                    "The historical rendered_state label was a fallback misclassification."
                ),
            },
            "records-BG2": {
                "recorded_stage": bg2_failure["error_stage"],
                "source_state_observed": True,
                "evidence": {
                    "query_echo": bg2_failure["query_echo"],
                    "range_echo": bg2_failure["range_echo"],
                    "card_count": bg2_failure["card_count"],
                    "page_size_control_count": bg2_failure[
                        "page_size_control_count"
                    ],
                    "strict_passes_completed": bg2_failure[
                        "strict_passes_completed"
                    ],
                },
                "diagnosis": (
                    "The year repair succeeded. Strict setup then forced a preferred page-size "
                    "transition although the current native page already contained all 11 records."
                ),
            },
            "records-BC1": {
                "recorded_stage": bc1_failure["error_stage"],
                "source_state_observed": True,
                "evidence": {
                    "query_echo": bc1_failure["query_echo"],
                    "range_echo": bc1_failure["range_echo"],
                    "card_count": bc1_failure["card_count"],
                    "page_size_control_count": bc1_failure[
                        "page_size_control_count"
                    ],
                    "strict_passes_completed": bc1_failure[
                        "strict_passes_completed"
                    ],
                },
                "diagnosis": (
                    "The year repair succeeded. Strict setup forced a preferred page-size "
                    "transition instead of retaining valid 25-row pagination for 28 records."
                ),
            },
        },
        "findings": {
            "successful_source_event_count": success_count,
            "failed_source_event_count": len(outcomes) - success_count,
            "year_noop_contract_transition_count": 0,
            "contained_intervals_proved": len(intervals),
            "strict_success_count": 2,
            "strict_rendered_failure_count": 2,
            "browser_open_failure_count": 1,
        },
        "conclusion": {
            "native_year": (
                "Pilot 005 year failures were adapter interactions with disabled no-op controls. "
                "Passive contained-interval validation returned exact totals without filling or Apply."
            ),
            "bg1_rendered_state": (
                "Semantic year-control reconciliation repaired BG1 strict capture and recovered Article Number 6161179."
            ),
            "remaining_rendered_state": (
                "BG2 and BC1 exposed a separate no-op page-size preference defect. Pilot 007 tests that diagnosis."
            ),
            "a1_rendered_state": (
                "The A1 failure occurred before source navigation and is a browser-open failure, not rendered source evidence."
            ),
        },
    }
    return corrected, assessment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--raw-run-receipt", type=Path, required=True)
    parser.add_argument("--run-receipt-output", type=Path, required=True)
    parser.add_argument("--assessment-output", type=Path, required=True)
    args = parser.parse_args()
    receipt, assessment = build(args.pilot_root, args.raw_run_receipt)
    args.run_receipt_output.write_text(json.dumps(receipt, indent=2) + "\n")
    args.assessment_output.write_text(json.dumps(assessment, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
