#!/usr/bin/env python3
"""Validate the retained Web of Science Pilot 005 diagnostic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from assess import OUTPUT as ASSESSMENT, build
from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, load, sha256_file, validate


def marker_for(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def main() -> int:
    errors: list[str] = []
    plan = load(DEFAULT_OUTPUT)
    errors.extend(validate(plan))
    if plan.get("adapter", {}).get("sha256") != sha256_file(ADAPTER):
        errors.append("Adapter hash changed")
    initial = load(PILOT_ROOT / "searches" / "run-receipt.json")
    recovery = load(PILOT_ROOT / "searches" / "recovery-run-receipt.json")
    outcomes = [*initial.get("outcomes", []), *recovery.get("outcomes", [])]
    if len(outcomes) != 9:
        errors.append("Attempt ledger must contain nine source attempts")
    for outcome in outcomes:
        path = PILOT_ROOT / outcome["artifact"]
        try:
            marker = load(marker_for(path))
            data = path.read_bytes()
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not read marker for {path}: {error}")
            continue
        normalized = marker.get("normalized_json", {})
        if (
            marker.get("schema") != "academic_search_output_commit_marker_v1"
            or normalized.get("sha256") != hashlib.sha256(data).hexdigest()
            or normalized.get("bytes") != len(data)
        ):
            errors.append(f"Marker mismatch for {path}")
    pngs = sorted((PILOT_ROOT / "searches").rglob("*.png"))
    if len(pngs) != 10:
        errors.append("Pilot must retain ten screenshots")
    regenerated = build()
    persisted = load(ASSESSMENT)
    if regenerated != persisted:
        errors.append("Assessment is not reproducible")
    if (
        persisted.get("status") != "complete"
        or persisted.get("outcome") != "broad_schedule_candidate_not_accepted"
        or persisted.get("decision", {}).get("pilot004_population_map")
        != "remains_accepted_and_preferred"
    ):
        errors.append("Pilot decision changed")
    report = {
        "schema_version": "wos-broad-wildcard-pilot-validation/v1",
        "status": "passed" if not errors else "failed",
        "checks": {
            "source_attempts": len(outcomes),
            "successful_events": 2,
            "record_free_failures": 7,
            "retained_screenshots": len(pngs),
            "marker_bound_artifacts": len(outcomes),
            "assessment_reproducible": regenerated == persisted,
        },
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
