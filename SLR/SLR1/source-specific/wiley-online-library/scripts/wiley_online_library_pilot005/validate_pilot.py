#!/usr/bin/env python3
"""Validate Wiley Pilot 005 artifacts, documentation, and adapter contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from build_assessment import DEFAULT_ASSESSMENT, DEFAULT_RECEIPT, build
from build_plan import DEFAULT_OUTPUT, PILOT_ROOT, load, validate

SCHEMA = "wiley-online-library-pilot005-validation/v1"
DEFAULT_GUIDELINE = PILOT_ROOT.parents[1] / "source-specific-guidelines.md"
DEFAULT_PILOT = PILOT_ROOT / "pilot.md"
DEFAULT_REPORT = PILOT_ROOT / "searches" / "validation-report.json"
DEFAULT_ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_wiley_online_library.py"
)
EXPECTED_TOTALS = {
    "A1": 21,
    "A2-mh": 34,
    "A2-mb": 106,
    "A3": 60,
    "B1": 86,
    "B2": 236,
    "BG1": 8,
    "BG2": 32,
    "BC1": 60,
    "BT2": 137,
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--guideline", type=Path, default=DEFAULT_GUIDELINE)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument(
        "--adapter",
        type=Path,
        default=Path(os.environ.get("WILEY_ADAPTER_PATH", DEFAULT_ADAPTER)),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    plan = load(args.plan)
    plan_errors = validate(plan)
    check("event_plan_valid", not plan_errors, plan_errors)
    check(
        "event_plan_uses_current_adapter",
        plan.get("adapter", {}).get("sha256") == file_sha256(args.adapter),
    )

    receipt = load(args.receipt)
    check(
        "run_receipt_complete",
        receipt.get("status") == "complete"
        and receipt.get("predeclared_event_count") == 10
        and receipt.get("completed_event_count") == 10
        and receipt.get("target_id_retained") is False,
    )

    saved_assessment = load(args.assessment)
    rebuilt_assessment = build(args.pilot_root, args.plan, args.receipt)
    check("assessment_rebuild_exact", saved_assessment == rebuilt_assessment)
    check("assessment_complete", saved_assessment.get("status") == "complete")

    events = saved_assessment.get("events", {})
    observed_totals = {
        event_id: summary.get("source_total") for event_id, summary in events.items()
    }
    check(
        "all_ten_expected_totals", observed_totals == EXPECTED_TOTALS, observed_totals
    )
    check(
        "all_totals_match_pilot004",
        all(
            summary.get("source_total_change_from_pilot004") == 0
            for summary in events.values()
        ),
    )
    check(
        "native_ris_complete",
        saved_assessment.get("native_ris_source_records_reconciled") == 780
        and saved_assessment.get("native_ris_download_count") == 53
        and saved_assessment.get("two_pass_source_doi_observations") == 1560,
    )
    check(
        "a2_union_complete",
        saved_assessment.get("A2_union", {}).get("cell_totals") == [34, 106]
        and saved_assessment.get("A2_union", {}).get("union_count") == 129,
    )
    larger = saved_assessment.get("larger_sets", {})
    check(
        "larger_sets_complete",
        larger.get("B2", {}).get("source_total") == 236
        and larger.get("B2", {}).get("pages_per_pass") == 12
        and larger.get("BT2", {}).get("source_total") == 137
        and larger.get("BT2", {}).get("pages_per_pass") == 7,
    )
    dates = saved_assessment.get("exact_date_accounting", {})
    check(
        "exact_dates_complete",
        dates.get("complete") is True
        and dates.get("excluded_source_ids") == []
        and dates.get("unresolved_source_ids") == ["10.1049/el.2013.1237"],
    )
    screenshots = saved_assessment.get("screenshots", {})
    check(
        "twenty_screenshots_valid",
        screenshots.get("validated_png_count") == 20
        and screenshots.get("all_sibling_paths") is True,
    )
    failures = saved_assessment.get("retained_failure_attempts", [])
    check(
        "failed_attempts_are_null_and_separate_from_plan_snapshots",
        len(failures) == 14
        and all(item.get("source_total") is None for item in failures),
    )

    guideline = args.guideline.read_text(encoding="utf-8")
    pilot_text = args.pilot.read_text(encoding="utf-8")
    check(
        "guideline_synchronized",
        all(
            text in guideline
            for text in (
                "Pilot 005 establishes native RIS readiness",
                "780 source records from 53 page-scoped native RIS downloads",
                "unmatched page-worker wrappers as telemetry",
                "caps the private fallback at five seconds",
            )
        ),
    )
    check(
        "pilot_report_synchronized",
        all(
            text in pilot_text
            for text in (
                "Pilot 005: native RIS final readiness",
                "The ten cells contain 780 source records.",
                "The assessment validates 20 mandatory PNGs.",
                "Fourteen failed event attempts",
                "completed in about 14 minutes",
            )
        ),
    )

    adapter_text = args.adapter.read_text(encoding="utf-8")
    check(
        "relaxed_fast_adapter_contract_present",
        all(
            text in adapter_text
            for text in (
                'ADAPTER_VERSION = "12"',
                "_wait_for_captured_wiley_download_body",
                "allowed_background_subresource_requests",
                "unmatched_page_worker_events_tolerated",
                "min(timeout_seconds, 5.0)",
                "stable IDs below take precedence over that stale shell",
            )
        ),
    )

    failed = [item["name"] for item in checks if not item["passed"]]
    report = {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "Wiley Online Library",
        "status": "ok" if not failed else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": {
            "artifact": str(args.plan.relative_to(args.pilot_root)),
            "sha256": file_sha256(args.plan),
        },
        "run_receipt": {
            "artifact": str(args.receipt.relative_to(args.pilot_root)),
            "sha256": file_sha256(args.receipt),
        },
        "assessment": {
            "artifact": str(args.assessment.relative_to(args.pilot_root)),
            "sha256": file_sha256(args.assessment),
        },
        "adapter": {
            "id": "search_wiley_online_library",
            "version": "12",
            "sha256": file_sha256(args.adapter),
            "local_path_retained": False,
        },
        "checks": checks,
        "failed_checks": failed,
    }
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "failed_checks": failed}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
