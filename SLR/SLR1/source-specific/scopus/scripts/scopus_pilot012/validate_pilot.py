#!/usr/bin/env python3
"""Validate Scopus Pilot 010 and Pilot 012 order-relaxation evidence."""

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
    parser.add_argument("--pilot010-root", type=Path, required=True)
    parser.add_argument("--pilot012-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output-utils", type=Path, required=True)
    parser.add_argument("--merge-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    errors = []
    p010_path = args.pilot010_root / "searches" / "assessment.json"
    p012_path = args.pilot012_root / "searches" / "assessment.json"
    p010 = load(p010_path)
    p012 = load(p012_path)
    if (
        p010.get("status") != "passed"
        or p010.get("unique_full_order_count") != 2
        or p010.get("requested_stable_id_set_reproduced_in_every_event") is not True
        or p010.get("stable_secondary_tie_breaker_observed") is not False
    ):
        errors.append("Pilot 010 order evidence mismatch")
    if (
        p012.get("status") != "passed"
        or p012.get("complete_stable_id_set_reconciliation_validated") is not True
        or p012.get("b1_final_search_readiness") is not True
        or p012.get("decision") != "accept_set_reconciled_strict_contract"
    ):
        errors.append("Pilot 012 strict evidence mismatch")

    artifact_paths = []
    for root in (args.pilot010_root, args.pilot012_root):
        plan = load(root / "searches" / "event-plan.json")
        for event in plan["events"]:
            path = root / "searches" / event["output"]
            if not path.is_file():
                errors.append(f"missing artifact: {path}")
                continue
            value = load(path)
            artifact_paths.append(path)
            screenshots = value.get("output_metadata", {}).get("screenshots", {})
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
                ):
                    errors.append(f"screenshot mismatch: {image}")
            marker_path = path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")
            marker = load(marker_path)
            if (
                marker.get("normalized_json", {}).get("sha256") != digest(path)
                or marker.get("normalized_json", {}).get("bytes") != path.stat().st_size
            ):
                errors.append(f"marker mismatch: {path}")

    adapter = args.adapter.read_text(encoding="utf-8")
    output_utils = args.output_utils.read_text(encoding="utf-8")
    merge_contract = args.merge_contract.read_text(encoding="utf-8")
    guideline = args.guideline.read_text(encoding="utf-8")
    for text in (
        "SCOPUS_NATIVE_EDITOR_INSERT_TEXT_THRESHOLD = 1",
        "strict_stable_id_sets_reconciled",
        "order_difference_count",
        "complete_two_pass_record_id_set_reconciliation",
    ):
        if text not in adapter:
            errors.append(f"adapter contract missing: {text}")
    if "academic-search-scopus-strict-two-pass/v2" not in merge_contract:
        errors.append("shared v2 schema is missing")
    if "stable_id_set_sha256" not in output_utils or "stable_id_set_sha256" not in merge_contract:
        errors.append("shared set-hash contract is missing")
    for text in (
        "Order equality is audit evidence rather than a membership gate.",
        "Pilot 012 establishes current strict readiness",
        "Pilot 010",
    ):
        if text not in guideline:
            errors.append(f"guideline text missing: {text}")

    report = {
        "schema_version": "scopus-pilot-012-validation/v1",
        "status": "passed" if not errors else "failed",
        "pilot010_assessment": {"path": str(p010_path), "sha256": digest(p010_path)},
        "pilot012_assessment": {"path": str(p012_path), "sha256": digest(p012_path)},
        "validated_source_artifact_count": len(artifact_paths),
        "verified_screenshot_file_count": len(artifact_paths) * 2,
        "v1_receipt_compatibility_retained": True,
        "current_receipt_schema": "academic-search-scopus-strict-two-pass/v2",
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors)}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
