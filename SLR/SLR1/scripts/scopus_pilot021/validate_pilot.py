#!/usr/bin/env python3
"""Validate the clean current-literal Scopus PSR pilot and repair evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_TOTALS = {"PSR1": 53, "PSR2": 237, "PSR3": 1, "PSR4": 68}
EXPECTED_PAGES = {"PSR1": [2, 2], "PSR2": [5, 5], "PSR3": [1, 1], "PSR4": [2, 2]}
KNOWN_ID = "SCOPUS-PUBLICATION:105032155734"
KNOWN_TITLE = "Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review"
STRICT_SCHEMA = "academic-search-scopus-strict-two-pass/v2"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
DOMAIN_GUIDE = Path.home() / "agent-tools/internet/skills/browser/domain-skills/scopus/search.md"


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
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--test-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    errors: list[str] = []
    searches = args.pilot_root / "searches"
    plan_path = searches / "event-plan.json"
    run_path = searches / "run-receipt.json"
    assessment_path = searches / "assessment.json"
    plan = load(plan_path)
    run = load(run_path)
    assessment = load(assessment_path)
    test_report = load(args.test_report)
    if (
        plan.get("schema_version")
        != "scopus-current-literal-psr-post-pagination-fix-plan/v1"
        or run.get("schema_version")
        != "scopus-current-literal-psr-post-pagination-fix-run/v1"
        or assessment.get("schema_version")
        != "scopus-current-literal-psr-post-pagination-fix-assessment/v1"
    ):
        errors.append("schema")
    if run.get("plan_sha256") != digest(plan_path):
        errors.append("run_plan_binding")
    if assessment.get("plan_sha256") != digest(plan_path):
        errors.append("assessment_plan_binding")
    if assessment.get("run_receipt_sha256") != digest(run_path):
        errors.append("assessment_run_binding")
    if plan.get("adapter", {}).get("sha256") != digest(ADAPTER):
        errors.append("adapter_binding")
    for relative, expected in plan.get("source_affecting_scripts", {}).items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest(path) != expected:
            errors.append(f"source_script_binding:{relative}")

    events = {event["partition_id"]: event for event in plan.get("events", [])}
    outcomes = {
        outcome["partition_id"]: outcome for outcome in run.get("outcomes", [])
    }
    if set(events) != set(EXPECTED_TOTALS) or set(outcomes) != set(EXPECTED_TOTALS):
        errors.append("partition_coverage")
    screenshot_count = 0
    known_partitions: list[str] = []
    artifact_rows: list[dict[str, Any]] = []
    for partition, expected_total in EXPECTED_TOTALS.items():
        event = events.get(partition, {})
        outcome = outcomes.get(partition, {})
        accepted = outcome.get("accepted_artifact")
        if (
            outcome.get("success") is not True
            or outcome.get("attempt_count") != 1
            or not isinstance(accepted, str)
        ):
            errors.append(f"accepted_outcome:{partition}")
            continue
        path = args.pilot_root / accepted
        value = load(path)
        metadata = value.get("output_metadata", {})
        receipt = metadata.get("strict_two_pass_receipt", {})
        results = value.get("results", [])
        ids = [row.get("paperId") for row in results if isinstance(row, dict)]
        reports = receipt.get("pass_reports", [])
        if (
            value.get("requested_query") != event.get("query")
            or value.get("total") != expected_total
            or len(results) != expected_total
            or len(ids) != len(set(ids))
            or metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or metadata.get("merge_eligible") is not True
            or receipt.get("schema_version") != STRICT_SCHEMA
            or receipt.get("strict_completion") is not True
            or receipt.get("strict_stable_id_sets_reconciled") is not True
            or receipt.get("two_pass_set_verified") is not True
            or receipt.get("two_pass_total_verified") is not True
            or receipt.get("two_pass_order_verified") is not True
            or receipt.get("order_difference_count") != 0
            or receipt.get("stable_id_set_sha256")
            != receipt.get("record_id_set_sha256")
            or [item.get("pages_retrieved") for item in reports]
            != EXPECTED_PAGES[partition]
            or [item.get("source_reported_total") for item in reports]
            != [expected_total, expected_total]
            or [item.get("page_size") for item in reports] != [50, 50]
        ):
            errors.append(f"strict_artifact:{partition}")
        strategy = metadata.get("prisma_search_run", {}).get("strategy", {})
        limits = strategy.get("limits", {})
        year = limits.get("year_interval", {})
        facets = limits.get("result_facets", {})
        if (
            year.get("state") != "applied"
            or year.get("value", {}).get("start") is not None
            or year.get("value", {}).get("end") != 2026
            or facets.get("state") != "not_applied"
            or facets.get("requested") != []
            or limits.get("search_within", {}).get("state") != "not_applied"
            or "PUBYEAR >" in value.get("executed_query", "").upper()
        ):
            errors.append(f"restriction_audit:{partition}")
        query = event.get("query", "")
        if (
            any(
                marker in query.upper()
                for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR")
            )
            or "*" in query
            or "?" in query
        ):
            errors.append(f"literal_query:{partition}")
        screenshots = metadata.get("screenshots", {})
        if (
            screenshots.get("schema_version") != SCREENSHOT_SCHEMA
            or screenshots.get("automatic") is not True
            or screenshots.get("same_directory_as_json") is not True
        ):
            errors.append(f"screenshot_receipt:{partition}")
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
                or evidence.get("browser_chrome_captured") is not False
                or evidence.get("complete_page_url_retained") is not False
                or evidence.get("session_identifiers_retained") is not False
            ):
                errors.append(f"screenshot:{partition}:{key}")
            screenshot_count += 1
        commit_path = marker_path(path)
        commit = load(commit_path)
        if (
            commit.get("normalized_json", {}).get("sha256") != digest(path)
            or commit.get("normalized_json", {}).get("bytes") != path.stat().st_size
        ):
            errors.append(f"terminal_marker:{partition}")
        known = [row for row in results if row.get("paperId") == KNOWN_ID]
        if known:
            known_partitions.append(partition)
            if any(
                row.get("title") != KNOWN_TITLE or row.get("year") != 2026
                for row in known
            ):
                errors.append(f"known_item_identity:{partition}")
        artifact_rows.append(
            {
                "partition_id": partition,
                "path": str(path),
                "sha256": digest(path),
                "source_total": expected_total,
                "strict_receipt_schema": receipt.get("schema_version"),
                "pass_page_counts": [item.get("pages_retrieved") for item in reports],
            }
        )

    if screenshot_count != 8:
        errors.append("screenshot_count")
    if set(known_partitions) != {"PSR1", "PSR2"}:
        errors.append("known_item_recall")
    if (
        run.get("success") is not True
        or run.get("accepted_event_count") != 4
        or run.get("source_command_attempt_count") != 4
        or run.get("safe_preexecution_retry_count") != 0
    ):
        errors.append("run_summary")
    if (
        assessment.get("status") != "passed"
        or assessment.get("all_four_current_literal_partitions_strictly_complete")
        is not True
        or assessment.get("psr2_and_psr4_strict_completion_confirmed") is not True
        or assessment.get("verified_screenshot_file_count") != 8
        or assessment.get("stable_id_union", {}).get("unique_stable_id_count")
        != 326
        or assessment.get("known_item", {}).get(
            "stable_id_and_title_recall_confirmed"
        )
        is not True
        or assessment.get("wildcard_comparisons_run") is not False
    ):
        errors.append("assessment")

    diagnostic_path = (
        REPOSITORY_ROOT
        / "SLR/SLR1/source-specific/scopus/pilots/020/searches/run-receipt.json"
    )
    diagnostic = load(diagnostic_path)
    candidates = [
        item
        for group in diagnostic.get("next_control_diagnostics", [])
        for item in group
        if isinstance(item, dict)
    ]
    if (
        len(candidates) != 2
        or not any(
            item.get("tag") == "A"
            and "Next Generation of Space Software Engineers" in item.get("text", "")
            and item.get("disabled") is False
            for item in candidates
        )
        or not any(
            item.get("tag") == "BUTTON"
            and item.get("text", "").startswith("NextCannot select next page")
            and item.get("disabled") is True
            for item in candidates
        )
        or any("href" in item for item in candidates)
    ):
        errors.append("pagination_diagnostic")
    adapter_source = ADAPTER.read_text(encoding="utf-8")
    if (
        "excluding arbitrary result links" not in adapter_source
        or r"/next\s+page|\bnext\b/i.test(hint)" in adapter_source
    ):
        errors.append("adapter_repair")
    if (
        test_report.get("status") != "passed"
        or test_report.get("targeted", {}).get("passed") != 16
        or test_report.get("broader", {}).get("passed") != 82
    ):
        errors.append("adapter_tests")
    guideline = args.guideline.read_text(encoding="utf-8")
    tasks = args.tasks.read_text(encoding="utf-8")
    domain = DOMAIN_GUIDE.read_text(encoding="utf-8")
    if (
        "Pilot 021" not in guideline
        or "326 IDs" not in guideline
        or "SCOPUS-014/021" not in tasks
        or "exact control semantics" not in domain
    ):
        errors.append("documentation")

    report = {
        "schema_version": "scopus-pilot-021-validation/v1",
        "status": "passed" if not errors else "failed",
        "pilot": "021",
        "adapter_sha256": digest(ADAPTER),
        "plan_sha256": digest(plan_path),
        "run_receipt_sha256": digest(run_path),
        "assessment_sha256": digest(assessment_path),
        "artifact_count": len(artifact_rows),
        "verified_screenshot_file_count": screenshot_count,
        "source_totals": EXPECTED_TOTALS,
        "stable_id_union_count": assessment.get("stable_id_union", {}).get(
            "unique_stable_id_count"
        ),
        "known_item_partitions": known_partitions,
        "strict_receipt_schema": STRICT_SCHEMA,
        "artifacts": artifact_rows,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors)}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
