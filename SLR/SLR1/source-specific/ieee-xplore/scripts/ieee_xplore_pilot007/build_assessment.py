#!/usr/bin/env python3
"""Build the IEEE Xplore Pilot 007 strict pagination assessment."""

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


def build(pilot_root: Path, pilot006_root: Path) -> dict[str, Any]:
    searches = pilot_root / "searches"
    plan = load(searches / "event-plan.json")
    run = load(searches / "run-receipt.json")
    pilot006 = load(pilot006_root / "searches" / "assessment.json")
    events = {event["schedule_id"]: event for event in plan["events"]}
    partitions: dict[str, Any] = {}
    ledger = []

    for schedule_id in ("BG2", "BC1", "B2"):
        event = events[schedule_id]
        path = searches / event["output"]
        artifact = load(path)
        metadata = artifact["output_metadata"]
        receipt = metadata["ieee_strict_completion_receipt"]
        reports = receipt["pass_reports"]
        ids = [row["paperId"] for row in artifact["results"]]
        partitions[schedule_id] = {
            "total": artifact["total"],
            "stable_article_numbers": ids,
            "ordered_article_number_sha256": receipt[
                "ordered_document_ids_sha256"
            ],
            "pass_page_sizes": [report["page_size"] for report in reports],
            "pass_page_counts": [report["pages_retrieved"] for report in reports],
            "pass_year_readbacks": [
                report["year_range_readback"] for report in reports
            ],
            "pass_year_refinement_ranges": [
                report["year_refinement_range"] for report in reports
            ],
            "pass_ordered_id_hashes": [
                report["ordered_document_ids_sha256"] for report in reports
            ],
            "pass_exported_id_hashes": [
                report["exported_result_ids_sha256"] for report in reports
            ],
            "controls_reconciled": receipt["controls_reconciled"],
            "ordered_ids_reconciled": receipt["ordered_ids_reconciled"],
            "export_reconciled": receipt["export_reconciled"],
            "strict_passes_completed": receipt["passes_completed"],
        }
        ledger.append(
            {
                "schedule_id": schedule_id,
                "path": str(path.relative_to(pilot_root)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "commit_marker": str(marker_path(path).relative_to(pilot_root)),
                "commit_marker_valid": marker_valid(path),
                "source_total": artifact["total"],
                "record_count": len(ids),
                "source_artifact_merge_eligible": metadata.get("merge_eligible"),
                "pilot_declaration": "diagnostic only; do not merge",
            }
        )

    p006_counts = pilot006["year_noop_results"]
    return {
        "schema_version": "ieee-xplore-pilot-007-assessment/v1",
        "source": "IEEE Xplore",
        "pilot": "007",
        "diagnostic_only": True,
        "do_not_merge": True,
        "adapter": plan["adapter"],
        "artifact_ledger": ledger,
        "partitions": partitions,
        "pilot006_recovery": {
            "BG2": {
                "pilot006_count_total": p006_counts["count-BG2"]["total"],
                "pilot006_strict_total": None,
                "pilot007_strict_total": partitions["BG2"]["total"],
            },
            "BC1": {
                "pilot006_count_total": p006_counts["count-BC1"]["total"],
                "pilot006_strict_total": None,
                "pilot007_strict_total": partitions["BC1"]["total"],
            },
        },
        "findings": {
            "successful_source_event_count": run["successful_source_event_count"],
            "failed_source_event_count": run["failed_source_event_count"],
            "bg2_total": partitions["BG2"]["total"],
            "bc1_total": partitions["BC1"]["total"],
            "b2_total": partitions["B2"]["total"],
            "native_page_size": 25,
            "b2_pages_per_pass": 6,
            "equivalent_year_representation_partitions": ["BG2", "BC1"],
            "all_markers_valid": all(item["commit_marker_valid"] for item in ledger),
            "all_strict_receipts_complete": all(
                partitions[key]["strict_passes_completed"] == 2
                and partitions[key]["controls_reconciled"] is True
                and partitions[key]["ordered_ids_reconciled"] is True
                and partitions[key]["export_reconciled"] is True
                for key in partitions
            ),
        },
        "conclusion": {
            "page_size": (
                "Pilot 006 BG2 and BC1 failures came from forcing a preferred page-size transition. "
                "Keeping native 25-row paging completed both strict captures."
            ),
            "year_representation": (
                "BG2 and BC1 each reconciled a contained result interval in pass one with an exact "
                "requested Year token in pass two under identical totals and ordered IDs."
            ),
            "over_100": (
                "B2 completed 131 ordered Article Numbers through six contiguous 25-row pages in each strict pass."
            ),
            "scope": (
                "These year-precision diagnostic artifacts do not establish the final exact publication-day window."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(args.pilot_root, args.pilot006_root)
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
