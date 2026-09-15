#!/usr/bin/env python3
"""Validate the accepted Scopus schedule, wildcard, and screenshot evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--pilot008-root", type=Path, required=True)
    parser.add_argument("--pilot009-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    errors = []
    combined_path = args.pilot009_root / "searches" / "combined-assessment.json"
    combined = load(combined_path)
    if combined.get("status") != "passed":
        errors.append("combined assessment did not pass")
    if combined.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("combined protocol commit mismatch")
    wildcard = combined.get("wildcard", {})
    if wildcard.get("decision") != "adopt_ten_population_wildcards_for_all_main_partitions":
        errors.append("wildcard decision mismatch")
    if wildcard.get("missing_record_count") != 0 or wildcard.get(
        "wildcard_only_record_count"
    ) != 0:
        errors.append("wildcard set difference remains")

    selected = {
        args.pilot006_root: {"A1", "A2", "A3"},
        args.pilot008_root: {"B2", "BG1", "BG2", "BC1", "BT2"},
        args.pilot009_root: {"B1"},
    }
    artifact_rows = []
    screenshot_count = 0
    for root, partitions in selected.items():
        plan_path = root / "searches" / "event-plan.json"
        plan = load(plan_path)
        if plan.get("protocol_commit") != PROTOCOL_COMMIT:
            errors.append(f"protocol commit mismatch: {plan_path}")
        for event in plan.get("events", []):
            if event.get("partition_id") not in partitions:
                continue
            query = event.get("query", "")
            if " W/" in query.upper() or " PRE/" in query.upper():
                errors.append(f"proximity syntax: {event.get('event_id')}")
            expected_wildcards = 10 if event.get("variant") == "wildcard" else 0
            if query.count("*") != expected_wildcards:
                errors.append(f"wildcard count: {event.get('event_id')}")
            path = root / "searches" / event["output"]
            value = load(path)
            metadata = value.get("output_metadata", {})
            if value.get("requested_query") != query:
                errors.append(f"query mismatch: {path}")
            if metadata.get("prisma_search_run", {}).get("adapter", {}).get(
                "script_sha256"
            ) != plan.get("adapter", {}).get("sha256"):
                errors.append(f"adapter binding mismatch: {path}")
            marker_file = marker_path(path)
            marker = load(marker_file)
            if (
                marker.get("normalized_json", {}).get("sha256") != digest(path)
                or marker.get("normalized_json", {}).get("bytes")
                != path.stat().st_size
            ):
                errors.append(f"terminal marker mismatch: {path}")
            screenshots = metadata.get("screenshots", {})
            if (
                screenshots.get("schema_version")
                != "scopus-automatic-screenshots/v1"
                or screenshots.get("automatic") is not True
                or screenshots.get("same_directory_as_json") is not True
            ):
                errors.append(f"screenshot receipt mismatch: {path}")
            for key, suffix in (
                ("search_page", ".search-page.png"),
                ("results_page", ".results-page.png"),
            ):
                image = path.with_name(f"{path.stem}{suffix}")
                evidence = screenshots.get(key, {})
                if (
                    not image.is_file()
                    or evidence.get("path") != image.name
                    or evidence.get("sha256") != digest(image)
                    or not isinstance(evidence.get("width"), int)
                    or evidence["width"] <= 0
                    or not isinstance(evidence.get("height"), int)
                    or evidence["height"] <= 0
                ):
                    errors.append(f"screenshot mismatch: {image}")
                screenshot_count += 1
            artifact_rows.append(
                {
                    "event_id": event["event_id"],
                    "path": str(path),
                    "sha256": digest(path),
                    "total": value.get("total"),
                }
            )

    if len(artifact_rows) != 30:
        errors.append("accepted source event count is not 30")
    if screenshot_count != 60:
        errors.append("accepted screenshot count is not 60")

    guideline = args.guideline.read_text(encoding="utf-8")
    for text in (
        "There is no screenshot opt-out.",
        "commit `3194156e90497186664260a8e86435e78d2e2aa1`",
        "Use `F*(P)` in every main partition.",
        "`BT2` | `F*(P) AND F(M_B) AND F(T_precise)`",
        "Keep `F(P)` and `F(X)` literal in PSR queries.",
        "Pilot 009",
    ):
        if text not in guideline:
            errors.append(f"guideline text missing: {text}")
    adapter = args.adapter.read_text(encoding="utf-8")
    for text in (
        ".search-page.png",
        ".results-page.png",
        "scopus-automatic-screenshots/v1",
        "Input.insertText",
    ):
        if text not in adapter:
            errors.append(f"adapter contract missing: {text}")
    if "--no-screenshot" in adapter:
        errors.append("adapter exposes a screenshot opt-out")

    report = {
        "schema_version": "scopus-pilot-009-validation/v1",
        "status": "passed" if not errors else "failed",
        "protocol_commit": PROTOCOL_COMMIT,
        "accepted_source_event_count": len(artifact_rows),
        "verified_screenshot_file_count": screenshot_count,
        "combined_assessment": {
            "path": str(combined_path),
            "sha256": digest(combined_path),
        },
        "wildcard_decision": wildcard.get("decision"),
        "artifacts": artifact_rows,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "events": len(artifact_rows),
                "screenshots": screenshot_count,
                "errors": len(errors),
            }
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
