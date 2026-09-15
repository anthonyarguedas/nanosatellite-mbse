#!/usr/bin/env python3
"""Validate the unchanged direct IEEE A2 readiness retest."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"


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


def module_from(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(
    pilot_root: Path, pilot005_root: Path, guideline: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    searches = pilot_root / "searches"
    plan_path = searches / "event-plan.json"
    plan = load(plan_path)
    run = load(searches / "run-receipt.json")
    assessment = load(searches / "assessment.json")
    p005_plan = load(pilot005_root / "searches" / "event-plan.json")
    p005_a2 = next(
        event for event in p005_plan["events"] if event["event_id"] == "count-A2-pass1"
    )
    builder = module_from(SCRIPT_DIR / "build_plan.py", "p008_plan")
    assessor = module_from(SCRIPT_DIR / "build_assessment.py", "p008_assessment")

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, observed: Any = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    check("plan_matches_builder", plan == builder.build())
    check("event_count", len(plan["events"]) == 2)
    check(
        "plan_precedes_artifacts",
        all(
            plan_path.stat().st_mtime <= (searches / event["output"]).stat().st_mtime
            for event in plan["events"]
        ),
    )
    check(
        "query_byte_identity",
        all(event["query"] == p005_a2["query"] for event in plan["events"])
        and plan["query_identity"]["sha256"] == p005_a2["query_sha256"]
        and plan["query_identity"]["characters"] == 5947,
    )
    check(
        "query_unchanged_controls",
        plan["query_identity"]["source_cells"] == 1
        and plan["controls"]["wildcard"] is False
        and plan["controls"]["proximity"] is False
        and plan["controls"]["publication_year"] == "2011_2026_Year inclusive",
    )
    check(
        "adapter_binding",
        ADAPTER.is_file() and sha256(ADAPTER) == plan["adapter"]["sha256"],
    )

    signatures = []
    for event in plan["events"]:
        path = searches / event["output"]
        artifact = load(path)
        metadata = artifact["output_metadata"]
        receipt = metadata["ieee_observation_receipt"]
        rendered = receipt["rendered_state"]
        signature = {
            "error_stage": metadata.get("error_stage"),
            "initial_form_state": receipt["initial_form_readiness"]["state"],
            "query_echo": rendered["query_echo"],
            "summary": rendered["summary"],
            "loading": rendered["loading"],
            "card_count": rendered["card_count"],
            "sort": rendered["sort"],
            "route": receipt["syntax_access_state"]["route"],
            "access": receipt["syntax_access_state"]["access"],
            "ready": receipt["syntax_access_state"]["ready"],
            "year_attempt_count": receipt["year_control"]["attempt_count"],
        }
        signatures.append(signature)
        check(
            f"{event['event_id']}_explicit_null",
            metadata["status"] == "error"
            and metadata["error_stage"] == "initial_form_readiness"
            and artifact["total"] is None
            and artifact["results"] == []
            and artifact.get("do_not_merge") is True,
        )
        check(
            f"{event['event_id']}_exact_query_echo",
            artifact["executed_query"] == event["query"]
            and rendered["query_echo"] == "exact",
        )
        check(
            f"{event['event_id']}_unready_shell",
            receipt["initial_form_readiness"]["state"] == "not_ready"
            and rendered["summary"] == "missing_or_ambiguous"
            and rendered["loading"] is False
            and rendered["card_count"] == 0
            and rendered["sort"] == "not_observed"
            and receipt["syntax_access_state"]
            == {"route": "expected", "access": "none", "ready": False},
        )
        check(
            f"{event['event_id']}_year_not_attempted",
            receipt["year_control"]["attempt_count"] == 0
            and receipt["year_control"]["apply_transition_count"] == 0,
        )
        check(
            f"{event['event_id']}_failure_has_no_terminal_marker",
            not path.with_name(f".{path.name}.IEEE_COMMIT.json").exists(),
        )

    check("failure_signatures_identical", signatures[0] == signatures[1])
    check(
        "run_receipt",
        run["status"] == "complete_with_retained_source_failures"
        and run["successful_source_event_count"] == 0
        and run["failed_source_event_count"] == 2,
    )
    check(
        "assessment_rebuild",
        assessment == assessor.build(pilot_root, pilot005_root),
    )
    check(
        "four_attempt_comparison",
        assessment["comparison"]["combined_unchanged_attempt_count"] == 4
        and assessment["repeated_failure_signature"] == signatures[0],
    )
    cleanup = list(pilot_root.rglob(".ACADEMIC_SEARCH_OUTPUT_CLEANUP.*"))
    check("no_private_cleanup_residue", not cleanup, len(cleanup))

    guideline_text = guideline.read_text()
    pilot_text = (pilot_root / "pilot.md").read_text()
    check(
        "guideline_documents_direct_a2_limit",
        all(
            fragment in guideline_text
            for fragment in (
                "Pilot 008",
                "four independent null attempts",
                "Do not assign a direct A2 total",
                "pilots/008/pilot.md",
            )
        ),
    )
    check(
        "pilot_keeps_split_boundary",
        "does not authorize a split" in pilot_text
        and "separately predeclared pilot" in pilot_text,
    )

    summary = {
        "query_sha256": plan["query_identity"]["sha256"],
        "query_characters": 5947,
        "pilot008_attempts": 2,
        "pilot008_successes": 0,
        "pilot008_failures": 2,
        "combined_unchanged_attempts": 4,
        "source_total": None,
    }
    return checks, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot005-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks, summary = validate(args.pilot_root, args.pilot005_root, args.guideline)
    failures = [item["check"] for item in checks if not item["passed"]]
    value = {
        "schema_version": "ieee-xplore-pilot-008-validation/v1",
        "source": "IEEE Xplore",
        "pilot": "008",
        "status": "passed" if not failures else "failed",
        "diagnostic_only": True,
        "do_not_merge": True,
        "check_count": len(checks),
        "failure_count": len(failures),
        "failures": failures,
        "summary": summary,
        "checks": checks,
    }
    args.output.write_text(json.dumps(value, indent=2) + "\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
