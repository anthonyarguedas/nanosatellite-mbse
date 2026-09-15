#!/usr/bin/env python3
"""Validate Wiley Pilot 004 artifacts, source guideline, and adapter contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from build_assessment import DEFAULT_ASSESSMENT, DEFAULT_SMOKE, build
from build_plan import DEFAULT_OUTPUT, PILOT_ROOT, load, validate

SCHEMA = "wiley-online-library-pilot004-validation/v1"
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
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--smoke", type=Path, default=DEFAULT_SMOKE)
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
    check("predeclared_plan_valid", not plan_errors, plan_errors)

    saved_assessment = load(args.assessment)
    rebuilt = build(args.pilot_root, args.plan, args.smoke)
    check("assessment_rebuild_exact", saved_assessment == rebuilt)
    check("assessment_complete", saved_assessment.get("status") == "complete")
    acceptance = saved_assessment.get("wildcard_acceptance", {})
    check("all_nine_wildcard_sets_equal", acceptance.get("all_nine_source_sets_equal") is True)
    check("all_nine_wildcard_orders_equal", acceptance.get("all_nine_source_orders_equal") is True)
    check("no_wildcard_only_ids", acceptance.get("wildcard_only_source_ids") == [])
    check(
        "all_nine_wildcards_adopted",
        acceptance.get("adopt_for_partitions")
        == ["A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"],
    )
    screenshots = saved_assessment.get("screenshots", {})
    check("twenty_schedule_jsons", screenshots.get("successful_schedule_event_json_count") == 20)
    check("forty_schedule_pngs", screenshots.get("successful_schedule_png_count") == 40)
    check("two_adapter_smoke_pngs", screenshots.get("adapter_smoke_png_count") == 2)
    check("all_screenshots_are_siblings", screenshots.get("all_sibling_paths") is True)

    guideline = args.guideline.read_text(encoding="utf-8")
    required_guideline_text = (
        "Adapter version 12 always saves `A1.search-page.png` and `A1.results-page.png`",
        "There is no screenshot opt-out.",
        "Prefer this shorter rendering.",
        "Pilot 004 found the same complete source IDs in the same order for all nine",
        "F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))",
        "F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))",
        "F(C1_fixed) OR F(G_DSL)",
        "F(P) AND F(M_B) AND F(T_precise)",
        "lossless union of `F(P) AND F(E_F) AND F(M_H)` and `F(P) AND F(E_F) AND F(M_B)`",
        "Current union totals are A1 21, A2 129, A3 60, B1 86, B2 236, BG1 8, BG2 32, BC1 60, and BT2 137.",
    )
    check(
        "guideline_synchronized",
        all(value in guideline for value in required_guideline_text),
        [value for value in required_guideline_text if value not in guideline],
    )

    pilot_text = args.pilot.read_text(encoding="utf-8")
    check(
        "pilot_report_synchronized",
        all(
            value in pilot_text
            for value in (
                "current schedule and wildcard adoption",
                "The assessment validates 42 PNGs in total.",
                "Accept and prefer `CubeSat*`, `nanosat*`, and `SmallSat*`",
                "It does not provide native RIS",
            )
        ),
    )

    adapter_text = args.adapter.read_text(encoding="utf-8")
    required_adapter_text = (
        'ADAPTER_VERSION = "12"',
        "class WileyScreenshotPaths",
        "def screenshot_paths_for_output",
        "async def configure_wiley_advanced_search_for_screenshot",
        "async def capture_wiley_full_page_screenshot",
        '"no_opt_out": True',
        "_publish_wiley_screenshot_bundle",
    )
    check(
        "adapter_v12_screenshot_contract_present",
        all(value in adapter_text for value in required_adapter_text),
        [value for value in required_adapter_text if value not in adapter_text],
    )
    check("adapter_has_no_screenshot_opt_out", "--no-screenshots" not in adapter_text)

    smoke = load(args.smoke)
    smoke_metadata = smoke.get("output_metadata", {})
    check(
        "live_adapter_smoke_complete",
        smoke.get("total") == 1
        and smoke.get("do_not_merge") is True
        and smoke_metadata.get("status") == "success"
        and smoke_metadata.get("screenshots", {}).get("no_opt_out") is True
        and smoke_metadata.get("prisma_search_run", {}).get("adapter", {}).get(
            "adapter_version"
        )
        == "12",
    )

    failures = saved_assessment.get("retained_failure_attempts", [])
    check(
        "failed_attempts_retained_as_null",
        len(failures) == 5
        and all(item.get("source_total") is None for item in failures),
    )

    failed = [item["name"] for item in checks if not item["passed"]]
    report = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Wiley Online Library",
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
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failed_checks": failed}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
