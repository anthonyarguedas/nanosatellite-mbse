#!/usr/bin/env python3
"""Validate Web of Science Pilot 006 PSR wildcard evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from assess import OUTPUT as ASSESSMENT, RUN_RECEIPT, build
from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, load, sha256_file, validate


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def main() -> int:
    errors: list[str] = []
    plan = load(DEFAULT_OUTPUT)
    errors.extend(validate(plan))
    if plan.get("adapter", {}).get("sha256") != sha256_file(ADAPTER):
        errors.append("Installed adapter differs from the predeclared adapter")
    run = load(RUN_RECEIPT)
    selected = run.get("selected_artifacts", {})
    if (
        run.get("success") is not True
        or run.get("attempt_count") != 8
        or run.get("successful_event_count") != 8
        or len(selected) != 8
    ):
        errors.append("Run receipt is incomplete")
    for relative in selected.values():
        path = PILOT_ROOT / relative
        try:
            marker = load(marker_path(path))
            data = path.read_bytes()
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate marker for {path}: {error}")
            continue
        normalized = marker.get("normalized_json", {})
        if (
            marker.get("schema") != "academic_search_output_commit_marker_v1"
            or normalized.get("sha256") != hashlib.sha256(data).hexdigest()
            or normalized.get("bytes") != len(data)
        ):
            errors.append(f"Output marker mismatch for {path}")
    pngs = sorted((PILOT_ROOT / "searches").rglob("*.png"))
    if len(pngs) != 16:
        errors.append("Pilot does not retain 16 screenshots")
    regenerated = build()
    persisted = load(ASSESSMENT)
    if regenerated != persisted:
        errors.append("Assessment is not reproducible")
    totals = [
        persisted.get("partition_results", {}).get(key, {}).get("wildcard", {}).get("total")
        for key in ("PSR1", "PSR2", "PSR3", "PSR4")
    ]
    if (
        persisted.get("status") != "passed"
        or persisted.get("wildcard_acceptance", {}).get("all_four_sets_equal") is not True
        or persisted.get("wildcard_acceptance", {}).get("all_four_orders_equal") is not True
        or persisted.get("wildcard_acceptance", {}).get("wildcard_only_wos_ids") != []
        or persisted.get("union_reconciliation", {}).get("literal_union_count") != 102
        or persisted.get("known_item", {}).get("retrieved_by_successful_wildcard_union") is not True
        or persisted.get("screenshots", {}).get("verified_file_count") != 16
        or totals != [22, 60, 0, 27]
    ):
        errors.append("Accepted pilot conclusions changed")
    report = {
        "schema_version": "wos-psr-population-wildcard-pilot-validation/v1",
        "status": "passed" if not errors else "failed",
        "checks": {
            "plan": "passed" if not validate(plan) else "failed",
            "source_events": len(selected),
            "source_attempts": run.get("attempt_count"),
            "marker_bound_artifacts": len(selected),
            "mandatory_screenshots": len(pngs),
            "assessment_reproducible": regenerated == persisted,
            "known_item_recall": persisted.get("known_item", {}).get("retrieved_by_successful_wildcard_union"),
        },
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
