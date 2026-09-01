#!/usr/bin/env python3
"""Validate arXiv browser Pilot 004 and its synchronized guideline."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from queries import CELLS, PROTOCOL_COMMIT, SCHEDULE_IDS

ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_arxiv.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0
    return struct.unpack(">II", header[16:24])


def validate(pilot_root: Path, guideline: Path) -> dict[str, Any]:
    searches = pilot_root / "searches"
    plan = load(searches / "event-plan.json")
    run_receipt = load(searches / "run-receipt.json")
    marking = load(searches / "nonmergeable-marking.json")
    plan_repair = load(searches / "plan-repair-receipt.json")
    failure_retention = load(searches / "failure-retention-receipt.json")
    union = load(searches / "partition-unions.json")
    assessment = load(searches / "assessment.json")
    errors: list[str] = []
    if not ADAPTER.is_file():
        errors.append(f"Current arXiv adapter is missing: {ADAPTER}")

    events = plan.get("events", [])
    if (
        plan.get("schema_version") != "arxiv-browser-pilot004-event-plan/v1"
        or plan.get("protocol_commit") != PROTOCOL_COMMIT
        or plan.get("partition_ids") != list(SCHEDULE_IDS)
        or len(events) != len(CELLS) != 12
    ):
        errors.append("The predeclared plan does not match the canonical 11 cells.")

    expected_by_id = {cell.cell_id: cell for cell in CELLS}
    screenshot_files: list[Path] = []
    totals: dict[str, list[int]] = {partition_id: [] for partition_id in SCHEDULE_IDS}
    for event in events:
        cell = expected_by_id.get(event.get("event_id"))
        if (
            cell is None
            or event.get("serialized_query") != cell.serialized_query
            or [row.get("term") for row in event.get("rows", [])] != list(cell.rows)
            or any(row.get("operator") != "AND" or row.get("field") != "all" for row in event.get("rows", []))
        ):
            errors.append(f"Plan query mismatch: {event.get('event_id')}")
            continue
        path = searches / event["output"]
        artifact = load(path)
        metadata = artifact.get("output_metadata", {})
        prisma = metadata.get("prisma_search_run", {})
        total = artifact.get("total")
        if (
            artifact.get("schema_version") != "academic-search-result/v1"
            or artifact.get("source") != "arXiv"
            or artifact.get("executed_query") != cell.serialized_query
            or not isinstance(total, int)
            or total < 0
            or len(artifact.get("results", [])) != total
            or metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or artifact.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
            or metadata.get("pilot_only") is not True
            or prisma.get("adapter", {}).get("adapter_version") != "8"
            or prisma.get("coverage", {}).get("partition_id") != event["partition_id"]
            or "pilot_non_mergeable" not in prisma.get("report_readiness_reasons", [])
        ):
            errors.append(f"Source artifact mismatch: {path}")
        else:
            totals[event["partition_id"]].append(total)

        screenshot_receipt = metadata.get("screenshots", {})
        if (
            screenshot_receipt.get("schema_version") != "arxiv-automatic-screenshots/v1"
            or screenshot_receipt.get("automatic") is not True
            or screenshot_receipt.get("same_directory_as_json") is not True
        ):
            errors.append(f"Screenshot receipt missing: {path}")
        for key, suffix in (
            ("search_page", ".search-page.png"),
            ("results_page", ".results-page.png"),
        ):
            image = path.with_name(f"{path.stem}{suffix}")
            evidence = screenshot_receipt.get(key, {})
            width, height = dimensions(image) if image.is_file() else (0, 0)
            if (
                not image.is_file()
                or evidence.get("path") != image.name
                or evidence.get("sha256") != sha256(image)
                or evidence.get("width") != width
                or evidence.get("height") != height
                or width <= 0
                or height <= 0
            ):
                errors.append(f"Screenshot evidence mismatch: {image}")
            screenshot_files.append(image)

    if len(screenshot_files) != 24 or len(set(screenshot_files)) != 24:
        errors.append("The pilot does not contain 24 unique source screenshots.")
    if run_receipt.get("status") != "complete" or run_receipt.get("completed_event_count") != 12:
        errors.append("The run receipt is incomplete.")
    if marking.get("status") != "complete" or marking.get("marked_artifact_count") != 12:
        errors.append("The non-mergeable marking receipt is incomplete.")
    if assessment.get("status") != "passed" or assessment.get("screenshot_file_count") != 24:
        errors.append("The pilot assessment did not pass.")
    retained = failure_retention.get("retained_reproduction", {})
    retained_artifact = searches / retained.get("artifact", "")
    retained_screenshot = searches / retained.get("search_screenshot", "")
    if (
        plan_repair.get("status") != "complete"
        or plan_repair.get("trigger", {}).get("total") is not None
        or failure_retention.get("status") != "complete"
        or not retained_artifact.is_file()
        or not retained_screenshot.is_file()
        or retained.get("artifact_sha256") != sha256(retained_artifact)
        or retained.get("search_screenshot_sha256") != sha256(retained_screenshot)
        or load(retained_artifact).get("total") is not None
    ):
        errors.append("The A2 failure and lossless plan-repair history is incomplete.")

    union_partitions = union.get("partitions", {})
    for partition_id in SCHEDULE_IDS:
        partition = union_partitions.get(partition_id, {})
        if (
            partition.get("outcome") != "complete"
            or partition.get("complete_cells") != len(totals[partition_id])
            or partition.get("cell_total_sum") != sum(totals[partition_id])
            or partition.get("unique_stable_id_count") != len(partition.get("stable_id_union", []))
        ):
            errors.append(f"Partition union mismatch: {partition_id}")

    text = guideline.read_text()
    required_text = (
        "Interface: Web",
        "https://arxiv.org/search/advanced",
        "A1.search-page.png",
        "rendered All-fields row",
        "[x] [Pilot 004](pilots/004/pilot.md)",
    )
    for marker in required_text:
        if marker not in text:
            errors.append(f"Guideline marker missing: {marker}")
    for obsolete in (
        "A future final runner must retain the Atom API route",
        "## Prospective Atom translation",
        "Interface and platform: documented arXiv Atom API",
    ):
        if obsolete in text:
            errors.append(f"Obsolete Atom-route wording remains: {obsolete}")

    return {
        "schema_version": "arxiv-browser-pilot004-validation/v1",
        "source": "arXiv",
        "pilot": "004",
        "status": "passed" if not errors else "failed",
        "do_not_merge": True,
        "checks": {
            "canonical_cell_plan": "passed" if not any("plan" in error.lower() for error in errors) else "failed",
            "strict_complete_artifacts": "passed" if not any("source artifact" in error.lower() for error in errors) else "failed",
            "mandatory_screenshots": "passed" if not any("screenshot" in error.lower() for error in errors) else "failed",
            "partition_unions": "passed" if not any("union" in error.lower() for error in errors) else "failed",
            "failure_and_repair_history": "passed" if not any("repair history" in error.lower() for error in errors) else "failed",
            "guideline_synchronization": "passed" if not any("guideline" in error.lower() or "obsolete" in error.lower() for error in errors) else "failed",
        },
        "source_event_count": len(events),
        "screenshot_file_count": len(screenshot_files),
        "partition_totals_by_cell": totals,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.pilot_root, args.guideline)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
