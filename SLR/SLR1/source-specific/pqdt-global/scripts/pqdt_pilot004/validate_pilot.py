#!/usr/bin/env python3
"""Validate PQDT Global Pilot 004 artifacts and source decisions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, Mapping

from build_assessment import DEFAULT_OUTPUT_PATH as DEFAULT_ASSESSMENT, build
from build_plan import ADAPTER_PATH, ADAPTER_VERSION, DEFAULT_OUTPUT, PILOT_ROOT, load, validate
from run_pilot import DEFAULT_RECEIPT, screenshot_receipt_is_complete, strict_artifact_summary

SCHEMA = "pqdt-global-pilot004-validation/v1"
DEFAULT_GUIDELINE = PILOT_ROOT.parents[1] / "source-specific-guidelines.md"
DEFAULT_PILOT = PILOT_ROOT / "pilot.md"
DEFAULT_SMOKE = PILOT_ROOT / "searches" / "adapter-smoke" / "automatic-screenshot-smoke.json"
DEFAULT_REPORT = PILOT_ROOT / "searches" / "validation-report.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int] | None:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--guideline", type=Path, default=DEFAULT_GUIDELINE)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--smoke", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--adapter", type=Path, default=ADAPTER_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    plan = load(args.plan)
    plan_errors = validate(plan)
    check("predeclared_plan_valid", not plan_errors, plan_errors)
    check(
        "adapter_snapshot_unchanged",
        args.adapter.is_file()
        and plan.get("adapter", {}).get("version") == ADAPTER_VERSION
        and plan.get("adapter", {}).get("sha256") == file_sha256(args.adapter),
    )

    receipt = load(args.receipt)
    check(
        "run_receipt_complete",
        receipt.get("status") == "complete"
        and receipt.get("predeclared_event_count") == 18
        and receipt.get("completed_event_count") == 18
        and receipt.get("retained_failure_count") == 3,
    )

    event_errors: list[str] = []
    summaries: list[dict[str, Any]] = []
    for event in plan.get("events", []):
        output = args.pilot_root / "searches" / str(event["output"])
        try:
            summaries.append(strict_artifact_summary(event, output, plan))
        except (OSError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
            event_errors.append(f"{event.get('event_id')}: {error}")
    check("eighteen_strict_source_events", len(summaries) == 18 and not event_errors, event_errors)
    check(
        "thirty_six_event_screenshots",
        sum(len(item.get("screenshots", {})) for item in summaries) == 36,
    )

    saved_assessment = load(args.assessment)
    rebuilt = build(args.pilot_root, args.plan, args.receipt, None)
    check("assessment_rebuild_exact", saved_assessment == rebuilt)
    check(
        "wildcard_decision_complete",
        saved_assessment.get("status") == "complete"
        and saved_assessment.get("decision")
        == "accept_and_prefer_bounded_wildcard_translation"
        and saved_assessment.get("accepted_for_partitions")
        == ["A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"],
    )
    comparison = saved_assessment.get("partition_comparisons", {})
    check(
        "all_partition_sets_and_orders_equal",
        isinstance(comparison, Mapping)
        and len(comparison) == 9
        and all(
            isinstance(value, Mapping)
            and value.get("sets_equal") is True
            and value.get("orders_equal") is True
            and value.get("literal_ids_missing_from_wildcard") == []
            and value.get("wildcard_only_ids") == []
            for value in comparison.values()
        ),
    )
    check(
        "all_schedule_union_equal",
        saved_assessment.get("union_comparison")
        == {
            "literal_distinct_ids": 29,
            "wildcard_distinct_ids": 29,
            "literal_ids_missing_from_wildcard": [],
            "wildcard_only_ids": [],
        },
    )

    smoke = load(args.smoke)
    smoke_metadata = smoke.get("output_metadata")
    smoke_adapter = (
        smoke_metadata.get("prisma_search_run", {}).get("adapter", {})
        if isinstance(smoke_metadata, Mapping)
        else {}
    )
    check(
        "live_adapter_screenshot_smoke",
        smoke.get("total") == 1
        and smoke.get("do_not_merge") is True
        and isinstance(smoke_metadata, Mapping)
        and smoke_metadata.get("status") == "count_only"
        and smoke_metadata.get("merge_eligible") is False
        and smoke_adapter.get("adapter_id") == "search_pqdt"
        and smoke_adapter.get("adapter_version") == ADAPTER_VERSION
        and smoke_adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
        and screenshot_receipt_is_complete(smoke, args.smoke),
    )

    failure_dir = args.pilot_root / "searches" / "failures"
    failure_jsons = sorted(failure_dir.glob("*.NON_MERGEABLE_FAILURE.json"))
    failure_pngs = sorted(failure_dir.glob("*.NON_MERGEABLE_FAILURE.*-page.png"))
    failure_values = [load(path) for path in failure_jsons]
    check(
        "three_failed_attempts_retained_as_null",
        len(failure_jsons) == 3
        and all(
            value.get("total") is None
            and value.get("do_not_merge") is True
            and value.get("output_metadata", {}).get("status") == "error"
            for value in failure_values
        ),
    )
    check(
        "four_failed_attempt_screenshots_retained",
        len(failure_pngs) == 4
        and all(
            (dimensions := png_dimensions(path)) is not None
            and dimensions[0] > 0
            and dimensions[1] > 0
            for path in failure_pngs
        ),
    )

    adapter_text = args.adapter.read_text(encoding="utf-8")
    required_adapter_text = (
        'ADAPTER_VERSION = "5"',
        "class PQDTScreenshotPaths",
        "def screenshot_paths_for_output",
        "async def capture_pqdt_full_page_screenshot",
        '"schema_version": "pqdt-automatic-screenshots/v1"',
        '"no_opt_out": True',
        "screenshot_paths=args.screenshot_paths",
    )
    check(
        "adapter_v5_screenshot_contract_present",
        all(value in adapter_text for value in required_adapter_text),
        [value for value in required_adapter_text if value not in adapter_text],
    )
    check("adapter_has_no_screenshot_opt_out", "--no-screenshots" not in adapter_text)

    guideline = args.guideline.read_text(encoding="utf-8")
    required_guideline_text = (
        "Adapter version 5 always saves `A1.search-page.png` and `A1.results-page.png`",
        "The adapter has no screenshot opt-out.",
        "Prefer this shorter bounded wildcard rendering in every partition.",
        "Pilot 004 accepted 128 bounded wildcard families",
        "F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))",
        "F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))",
        "F(P) AND F(M_B) AND F(T_precise)",
        "The all-schedule union contained 29 IDs.",
    )
    check(
        "guideline_synchronized",
        all(value in guideline for value in required_guideline_text)
        and "NEAR/5" not in guideline
        and "F(T2)" not in guideline,
        [value for value in required_guideline_text if value not in guideline],
    )

    pilot_text = args.pilot.read_text(encoding="utf-8")
    required_pilot_text = (
        "current schedule and bounded wildcard adoption",
        "The candidate uses 128 bounded wildcard families.",
        "There were no wildcard-only IDs to review.",
        "The pilot validates 38 successful-run PNGs in total",
        "Three null-total failure JSONs remain",
        "It does not create a final search.",
    )
    check(
        "pilot_report_synchronized",
        all(value in pilot_text for value in required_pilot_text),
        [value for value in required_pilot_text if value not in pilot_text],
    )

    failed = [item["name"] for item in checks if not item["passed"]]
    report = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "ProQuest Dissertations & Theses Global",
        "status": "ok" if not failed else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": {
            "artifact": str(args.plan.relative_to(args.pilot_root)),
            "sha256": file_sha256(args.plan),
        },
        "assessment": {
            "artifact": str(args.assessment.relative_to(args.pilot_root)),
            "sha256": file_sha256(args.assessment),
        },
        "adapter": {
            "id": "search_pqdt",
            "version": ADAPTER_VERSION,
            "sha256": file_sha256(args.adapter),
            "local_path_retained": False,
        },
        "successful_screenshot_count": 38,
        "retained_failed_attempt_screenshot_count": len(failure_pngs),
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
