#!/usr/bin/env python3
"""Validate the requested Scopus wildcard B1 strict retry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    errors = []
    plan_path = args.pilot_root / "searches" / "event-plan.json"
    artifact_path = args.pilot_root / "searches" / "B1-wildcard-retry.json"
    assessment_path = args.pilot_root / "searches" / "assessment.json"
    plan = load(plan_path)
    artifact = load(artifact_path)
    assessment = load(assessment_path)
    event = plan["events"][0]
    metadata = artifact.get("output_metadata", {})
    receipt = metadata.get("strict_two_pass_receipt", {})
    if (
        event.get("event_id") != "B1-wildcard-strict-retry"
        or artifact.get("requested_query") != event.get("query")
        or artifact.get("total") != 165
        or len(artifact.get("results", [])) != 165
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or receipt.get("schema_version") != "academic-search-scopus-strict-two-pass/v2"
        or receipt.get("strict_stable_id_sets_reconciled") is not True
        or receipt.get("two_pass_set_verified") is not True
        or receipt.get("two_pass_order_verified") is not True
        or receipt.get("order_difference_count") != 0
    ):
        errors.append("strict B1 artifact mismatch")
    screenshots = metadata.get("screenshots", {})
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        image = artifact_path.with_name(f"{artifact_path.stem}{suffix}")
        evidence = screenshots.get(key, {})
        if (
            not image.is_file()
            or evidence.get("path") != image.name
            or evidence.get("sha256") != digest(image)
        ):
            errors.append(f"screenshot mismatch: {image}")
    marker_path = artifact_path.with_name(
        f".{artifact_path.name}.ACADEMIC_SEARCH_COMMIT.json"
    )
    marker = load(marker_path)
    if (
        marker.get("normalized_json", {}).get("sha256") != digest(artifact_path)
        or marker.get("normalized_json", {}).get("bytes")
        != artifact_path.stat().st_size
    ):
        errors.append("terminal marker mismatch")
    if (
        assessment.get("status") != "passed"
        or assessment.get("b1_final_search_readiness") is not True
    ):
        errors.append("assessment mismatch")
    guideline = args.guideline.read_text(encoding="utf-8")
    if "Pilot 013" not in guideline or "Two fresh strict wildcard B1 events" not in Path("SLR/SLR1/TASKS.md").read_text(encoding="utf-8"):
        errors.append("documentation mismatch")

    report = {
        "schema_version": "scopus-pilot-013-validation/v1",
        "status": "passed" if not errors else "failed",
        "artifact": {"path": str(artifact_path), "sha256": digest(artifact_path)},
        "source_total": artifact.get("total"),
        "receipt_schema": receipt.get("schema_version"),
        "two_pass_order_verified": receipt.get("two_pass_order_verified"),
        "order_difference_count": receipt.get("order_difference_count"),
        "verified_screenshot_file_count": 2,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors)}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
