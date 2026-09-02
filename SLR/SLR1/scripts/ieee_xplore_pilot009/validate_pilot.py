#!/usr/bin/env python3
"""Validate IEEE Pilot 009 and its synchronized source decision."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.IEEE_COMMIT.json")


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not path.is_file() or not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == sha256(path)
        and evidence.get("bytes") == path.stat().st_size
    )


def validate(
    pilot_root: Path, pilot008_root: Path, guideline: Path
) -> dict[str, Any]:
    searches = pilot_root / "searches"
    plan = load(searches / "event-plan.json")
    run = load(searches / "run-receipt.json")
    assessment = load(searches / "assessment.json")
    adapter_validation = load(searches / "adapter-validation.json")
    transport_investigation = load(searches / "transport-investigation.json")
    pilot008_plan = load(pilot008_root / "searches" / "event-plan.json")
    checks = []

    def check(name: str, condition: bool) -> None:
        checks.append({"check": name, "passed": bool(condition)})

    check(
        "plan_schema",
        plan.get("schema_version") == "ieee-xplore-pilot-009-event-plan/v1",
    )
    check(
        "adapter_binding",
        ADAPTER.is_file() and sha256(ADAPTER) == plan["adapter"]["sha256"],
    )
    check("adapter_v10", plan["adapter"]["version"] == "10")
    check("two_predeclared_events", len(plan.get("events", [])) == 2)
    check("one_source_cell", plan["query_identity"]["source_cells"] == 1)
    check("wildcards_prohibited", plan["query_identity"]["wildcard_count"] == 0)
    check("wildcard_control_false", plan["controls"]["wildcard"] is False)
    check(
        "pilot008_query_identity",
        all(
            event["query"] == pilot008_plan["events"][0]["query"]
            and event["query_sha256"] == pilot008_plan["events"][0]["query_sha256"]
            for event in plan["events"]
        ),
    )
    check(
        "compact_target_within_bound",
        plan["transport"]["repaired_compact_request_target_bytes"]
        <= plan["transport"]["validated_request_target_bound_bytes"]
        < plan["transport"]["former_percent_request_target_bytes"],
    )
    observations = transport_investigation.get("observations", [])
    check(
        "transport_diagnosis",
        transport_investigation.get("diagnosis") == "adapter_transport_failure"
        and len(observations) == 3,
    )
    check(
        "http_414_observed",
        [item.get("document_status") for item in observations[:2]] == [414, 414],
    )
    check(
        "compact_ready_observed",
        observations[2].get("request_target_bytes") == 7477
        and observations[2].get("document_status") == 200
        and observations[2].get("result_header_present") is True,
    )
    check("run_complete", run.get("status") == "complete")
    check("two_successes", run.get("successful_source_event_count") == 2)

    totals = []
    for event in plan["events"]:
        path = searches / event["output"]
        artifact = load(path)
        metadata = artifact.get("output_metadata", {})
        prisma = metadata.get("prisma_search_run", {})
        adapter = prisma.get("adapter", {})
        strategy = prisma.get("strategy", {})
        year = metadata.get("publication_year_readback", {})
        total = artifact.get("total")
        totals.append(total)
        prefix = event["event_id"]
        check(f"{prefix}_status", metadata.get("status") == "count_only")
        check(
            f"{prefix}_integer_total",
            isinstance(total, int) and not isinstance(total, bool),
        )
        check(
            f"{prefix}_exact_query", artifact.get("executed_query") == event["query"]
        )
        check(
            f"{prefix}_source_observed_query",
            strategy.get("executed_query_provenance") == "source_observed",
        )
        check(
            f"{prefix}_year",
            year.get("state") == "exact_source_echo"
            and year.get("native_range_echo") == "2011_2026_Year",
        )
        check(
            f"{prefix}_oldest",
            strategy.get("sort", {}).get("state") == "applied"
            and strategy.get("sort", {}).get("value") == "Oldest",
        )
        check(
            f"{prefix}_adapter",
            adapter.get("adapter_version") == plan["adapter"]["version"]
            and adapter.get("script_sha256") == plan["adapter"]["sha256"],
        )
        check(f"{prefix}_marker", marker_valid(path))
        check(f"{prefix}_nonmergeable", artifact.get("do_not_merge") is True)

    check("repeated_total", len(totals) == 2 and totals[0] == totals[1] == 33)
    check(
        "assessment_classification",
        assessment.get("conclusion", {}).get("classification")
        == "adapter_transport_failure_repaired",
    )
    check(
        "assessment_no_wildcard",
        assessment.get("query_identity", {}).get("wildcard_used") is False,
    )
    check(
        "adapter_validation_binding",
        adapter_validation.get("adapter_version") == plan["adapter"]["version"]
        and adapter_validation.get("adapter_sha256") == plan["adapter"]["sha256"],
    )
    check(
        "focused_adapter_tests",
        adapter_validation.get("focused_test_result", {}).get("status") == "passed"
        and adapter_validation.get("focused_test_result", {}).get("tests_passed")
        == 24,
    )
    check("adapter_lint", adapter_validation.get("lint_result") == "passed")
    check(
        "live_validation_no_wildcards",
        adapter_validation.get("wildcard_used") is False
        and adapter_validation.get("live_validation", {}).get("wildcard_count") == 0,
    )

    guideline_text = guideline.read_text()
    pilot_text = (pilot_root / "pilot.md").read_text()
    pilot008_text = (pilot008_root / "pilot.md").read_text()
    check(
        "guideline_synced",
        "Pilot 009" in guideline_text
        and "wildcard compression is excluded" in guideline_text
        and "7,477" in guideline_text,
    )
    check(
        "pilot_documented",
        "Both predeclared events completed with the same source total of 33"
        in pilot_text,
    )
    check(
        "pilot008_reclassified",
        "Later adapter reclassification" in pilot008_text
        and "diagnosis is superseded" in pilot008_text,
    )

    failures = [item["check"] for item in checks if not item["passed"]]
    return {
        "schema_version": "ieee-xplore-pilot-009-validation/v1",
        "source": "IEEE Xplore",
        "pilot": "009",
        "status": "passed" if not failures else "failed",
        "check_count": len(checks),
        "failed_checks": failures,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot008-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = validate(args.pilot_root, args.pilot008_root, args.guideline)
    args.output.write_text(json.dumps(value, indent=2) + "\n")
    return 0 if value["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
