#!/usr/bin/env python3
"""Validate the IEEE Xplore Pilot 006 and 007 investigation bundle."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
ADAPTER_DOC = (
    Path.home()
    / "agent-tools/internet/skills/browser/domain-skills/academic-publishers/ieee-xplore-search.md"
)


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


def ordered_ids_sha256(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode()
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def module_from(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def marker_valid(path: Path) -> bool:
    marker = path.with_name(f".{path.name}.IEEE_COMMIT.json")
    if not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == sha256(path)
        and evidence.get("bytes") == path.stat().st_size
    )


def validate(
    pilot006_root: Path, pilot007_root: Path, guideline: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p006_searches = pilot006_root / "searches"
    p007_searches = pilot007_root / "searches"
    p006_plan = load(p006_searches / "event-plan.json")
    p007_plan = load(p007_searches / "event-plan.json")
    p006_run = load(p006_searches / "run-receipt.json")
    p006_assessment = load(p006_searches / "assessment.json")
    p007_run = load(p007_searches / "run-receipt.json")
    p007_assessment = load(p007_searches / "assessment.json")
    adapter_validation = load(p007_searches / "adapter-validation.json")

    p006_builder = module_from(
        SLR1_ROOT / "source-specific/ieee-xplore/scripts/ieee_xplore_pilot006/build_plan.py", "p006_plan"
    )
    p006_assessor = module_from(
        SLR1_ROOT / "source-specific/ieee-xplore/scripts/ieee_xplore_pilot006/build_assessment.py",
        "p006_assessment",
    )
    p007_builder = module_from(SCRIPT_DIR / "build_plan.py", "p007_plan")
    p007_assessor = module_from(SCRIPT_DIR / "build_assessment.py", "p007_assessment")

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, observed: Any = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    check("pilot006_plan_matches_builder", p006_plan == p006_builder.build())
    check("pilot007_plan_matches_builder", p007_plan == p007_builder.build())
    check("pilot006_event_count", len(p006_plan["events"]) == 10)
    check("pilot007_event_count", len(p007_plan["events"]) == 3)
    check(
        "plans_precede_source_artifacts",
        all(
            (p006_searches / "event-plan.json").stat().st_mtime
            <= (p006_searches / event["output"]).stat().st_mtime
            for event in p006_plan["events"]
        )
        and all(
            (p007_searches / "event-plan.json").stat().st_mtime
            <= (p007_searches / event["output"]).stat().st_mtime
            for event in p007_plan["events"]
        ),
    )

    rebuilt_receipt, rebuilt_p006 = p006_assessor.build(
        pilot006_root, p006_searches / "run-receipt-raw.json"
    )
    check("pilot006_reconciled_receipt_rebuild", p006_run == rebuilt_receipt)
    check("pilot006_assessment_rebuild", p006_assessment == rebuilt_p006)
    check(
        "pilot006_source_accounting",
        p006_run["successful_source_event_count"] == 7
        and p006_run["failed_source_event_count"] == 3,
    )
    check(
        "pilot006_noop_totals",
        {
            key: value["total"]
            for key, value in p006_assessment["year_noop_results"].items()
        }
        == {
            "count-A1-pass2": 5,
            "count-B1": 74,
            "count-BG2": 11,
            "count-BC1": 28,
            "count-BT2": 9,
        },
    )
    check(
        "pilot006_all_year_intervals_contained",
        all(
            value["readback"]
            == "result_refinement_range_within_requested_window"
            for value in p006_assessment["year_noop_results"].values()
        ),
    )
    check(
        "pilot006_a1_was_pre_source_browser_failure",
        p006_assessment["failure_diagnoses"]["count-A1-pass1"][
            "source_state_observed"
        ]
        is False
        and p006_assessment["failure_diagnoses"]["count-A1-pass1"]["evidence"]
        == {"query_echo": "not_observed", "cleanup_state": "not_needed"},
    )
    check(
        "pilot006_strict_success_ids",
        p006_assessment["strict_successes"]["records-BG1"][
            "stable_article_numbers"
        ]
        == ["6161179"]
        and len(
            p006_assessment["strict_successes"]["records-BT2"][
                "stable_article_numbers"
            ]
        )
        == 9,
    )

    rebuilt_p007 = p007_assessor.build(pilot007_root, pilot006_root)
    check("pilot007_assessment_rebuild", p007_assessment == rebuilt_p007)
    check(
        "pilot007_source_accounting",
        p007_run["status"] == "complete"
        and p007_run["successful_source_event_count"] == 3
        and p007_run["failed_source_event_count"] == 0,
    )

    expected = {
        "BG2": (11, [1, 1], [25, 25]),
        "BC1": (28, [2, 2], [25, 25]),
        "B2": (131, [6, 6], [25, 25]),
    }
    for schedule_id, (total, pages, sizes) in expected.items():
        event = next(
            event for event in p007_plan["events"] if event["schedule_id"] == schedule_id
        )
        path = p007_searches / event["output"]
        artifact = load(path)
        metadata = artifact["output_metadata"]
        receipt = metadata["ieee_strict_completion_receipt"]
        reports = receipt["pass_reports"]
        ids = [row["paperId"] for row in artifact["results"]]
        check(f"{schedule_id}_marker_valid", marker_valid(path))
        check(
            f"{schedule_id}_strict_total_and_records",
            artifact["total"] == total
            and len(ids) == total
            and len(set(ids)) == total
            and [row["rank"] for row in artifact["results"]]
            == list(range(1, total + 1)),
        )
        check(
            f"{schedule_id}_strict_receipt",
            receipt["schema_version"] == "ieee-xplore-strict-two-pass-receipt/v1"
            and receipt["passes_completed"] == 2
            and receipt["controls_reconciled"] is True
            and receipt["ordered_ids_reconciled"] is True
            and receipt["export_reconciled"] is True,
        )
        check(
            f"{schedule_id}_native_pagination",
            [report["pages_retrieved"] for report in reports] == pages
            and [report["page_size"] for report in reports] == sizes
            and all(report["source_rows_rendered"] == total for report in reports),
        )
        digest = ordered_ids_sha256(ids)
        check(
            f"{schedule_id}_ordered_ids_reconcile",
            receipt["ordered_document_ids_sha256"] == digest
            and all(report["ordered_document_ids_sha256"] == digest for report in reports)
            and all(report["exported_result_ids_sha256"] == digest for report in reports),
        )
        adapter = metadata["prisma_search_run"]["adapter"]
        check(
            f"{schedule_id}_adapter_binding",
            adapter["adapter_version"] == "9"
            and adapter["script_sha256"] == p007_plan["adapter"]["sha256"],
        )

    check(
        "live_equivalent_year_representations",
        p007_assessment["partitions"]["BG2"]["pass_year_readbacks"]
        == ["result_refinement_range_within_requested_window", "exact_source_echo"]
        and p007_assessment["partitions"]["BC1"]["pass_year_readbacks"]
        == ["result_refinement_range_within_requested_window", "exact_source_echo"],
    )
    check(
        "pilot_artifacts_declared_nonmergeable",
        p006_assessment["do_not_merge"] is True
        and p007_assessment["do_not_merge"] is True
        and all(
            item["pilot_declaration"] == "diagnostic only; do not merge"
            for item in p007_assessment["artifact_ledger"]
        ),
    )
    cleanup = list(pilot006_root.rglob(".ACADEMIC_SEARCH_OUTPUT_CLEANUP.*")) + list(
        pilot007_root.rglob(".ACADEMIC_SEARCH_OUTPUT_CLEANUP.*")
    )
    check("no_private_cleanup_residue", not cleanup, len(cleanup))

    check(
        "adapter_validation_receipt",
        adapter_validation["test_result"]
        == {"status": "passed", "tests_passed": 139, "subtests_passed": 102, "failures": 0}
        and adapter_validation["lint_result"] == "passed"
        and adapter_validation["pilot007_source_run_sha256"]
        == p007_plan["adapter"]["sha256"],
    )
    check(
        "current_adapter_hash",
        ADAPTER.is_file()
        and sha256(ADAPTER) == adapter_validation["post_run_adapter_sha256"],
    )
    adapter_doc = ADAPTER_DOC.read_text() if ADAPTER_DOC.is_file() else ""
    check(
        "adapter_documentation_updated",
        "disables Year Apply" in adapter_doc
        and "semantic controls" in adapter_doc
        and "browser_open" in adapter_doc,
    )

    guideline_text = guideline.read_text()
    p006_text = (pilot006_root / "pilot.md").read_text()
    p007_text = (pilot007_root / "pilot.md").read_text()
    check(
        "guideline_documents_repairs",
        all(
            fragment in guideline_text
            for fragment in (
                "disabled widget",
                "Page size is a preference",
                "pilots/006/pilot.md",
                "pilots/007/pilot.md",
                "six contiguous 25-row pages",
                "browser_open",
            )
        ),
    )
    check(
        "pilot_documents_keep_final_boundary",
        "does not authorize a final search" in p006_text
        and "still lacks final-search authorization" in p007_text,
    )

    summary = {
        "pilot006_successes": 7,
        "pilot006_failures": 3,
        "pilot007_successes": 3,
        "pilot007_failures": 0,
        "recovered_strict_totals": {"BG1": 1, "BG2": 11, "BC1": 28, "BT2": 9},
        "b2_strict_total": 131,
        "b2_pages_per_pass": 6,
    }
    return checks, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot006-root", type=Path, required=True)
    parser.add_argument("--pilot007-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks, summary = validate(args.pilot006_root, args.pilot007_root, args.guideline)
    failures = [item["check"] for item in checks if not item["passed"]]
    value = {
        "schema_version": "ieee-xplore-pilots-006-007-validation/v1",
        "source": "IEEE Xplore",
        "status": "passed" if not failures else "failed",
        "diagnostic_only": True,
        "do_not_merge": True,
        "check_count": len(checks),
        "failure_count": len(failures),
        "failures": failures,
        "summary": summary,
        "checks": checks,
    }
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
