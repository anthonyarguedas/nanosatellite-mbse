#!/usr/bin/env python3
"""Validate Springer Pilot 004 artifacts and synchronized guidance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_assessment import DEFAULT_OUTPUT as DEFAULT_ASSESSMENT
from build_plan import PILOT_ROOT, validate
from queries import SCHEDULE_IDS
from run_pilot import DEFAULT_ADAPTER, load_adapter

DEFAULT_PLAN = PILOT_ROOT / "searches" / "event-plan-v4.json"
DEFAULT_RETEST_PLAN = PILOT_ROOT / "searches" / "snapshot-retest-plan.json"
DEFAULT_GUIDELINE = PILOT_ROOT.parents[1] / "source-specific-guidelines.md"
DEFAULT_PILOT_DOCUMENT = PILOT_ROOT / "pilot.md"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "validation-report.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_all(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[str] = []
    plan = load(args.plan)
    retest_plan = load(args.retest_plan)
    errors.extend(validate(plan))
    errors.extend(validate(retest_plan))
    assessment = load(args.assessment)
    if (
        assessment.get("status") != "complete"
        or assessment.get("errors") != []
        or tuple(assessment.get("partition_results", {})) != SCHEDULE_IDS
        or assessment.get("wildcard_acceptance", {}).get("all_nine_wildcard_supersets")
        is not True
        or assessment.get("wildcard_acceptance", {}).get("literal_missing_source_ids")
        != []
        or assessment.get("wildcard_acceptance", {}).get("wildcard_only_record_count")
        != 2
        or assessment.get("screenshots", {}).get("total_validated_png_count") != 166
        or assessment.get("screenshots", {}).get("all_sibling_paths") is not True
        or assessment.get("retained_failure_count") != 18
    ):
        errors.append("Assessment decision or accounting changed")
    for partition_id, result in assessment.get("partition_results", {}).items():
        comparison = result.get("comparison", {})
        if (
            comparison.get("wildcard_is_source_superset") is not True
            or comparison.get("diagnostic_window_wildcard_is_superset") is not True
        ):
            errors.append(f"Wildcard acceptance changed for {partition_id}")
    if set(
        assessment.get("wildcard_acceptance", {}).get("adopt_for_partitions", [])
    ) != set(SCHEDULE_IDS):
        errors.append("Wildcard adoption no longer covers all partitions")
    if assessment.get("detail_route_limitation", {}).get(
        "strict_adapter_failure_source_ids"
    ) != ["/article/10.1038/s44359-026-00173-2"]:
        errors.append("Strict detail-route limitation changed")

    guideline = args.guideline.read_text(encoding="utf-8")
    pilot_document = args.pilot_document.read_text(encoding="utf-8")
    required_guideline_text = (
        "Adapter version 12 always saves",
        "There is no screenshot option",
        "Accepted population compression",
        "five A2 cells and 25 B2 cells",
        "[Pilot 004](pilots/004/pilot.md)",
        "www.nature.com/articles/s44359-026-00173-2",
        "Springer has no pending source pilot",
    )
    for value in required_guideline_text:
        if value not in guideline:
            errors.append(f"Guideline lacks required text: {value}")
    required_pilot_text = (
        "166 PNGs",
        "CubeSat*",
        "nanosat*",
        "SmallSat*",
        "five A2 cells and 25 B2 cells",
        "external `www.nature.com` canonical link",
        "not a final search",
    )
    for value in required_pilot_text:
        if value not in pilot_document:
            errors.append(f"Pilot document lacks required text: {value}")

    event_outputs = sorted((PILOT_ROOT / "searches" / "events").glob("*.json"))
    png_outputs = sorted((PILOT_ROOT / "searches" / "events").glob("*.png"))
    if len(event_outputs) != 82 or len(png_outputs) != 164:
        errors.append("Successful event or PNG count changed")
    failure_outputs = sorted((PILOT_ROOT / "searches" / "failures").glob("*.json"))
    if len(failure_outputs) != 18:
        errors.append("Retained failure count changed")

    adapter = load_adapter(args.adapter)
    if (
        int(adapter.ADAPTER_VERSION) < 10
        or adapter.SPRINGER_AUTOMATIC_SCREENSHOT_CAPABILITIES.get("no_opt_out")
        is not True
    ):
        errors.append("Installed adapter lacks mandatory screenshots")

    artifacts = {
        "assessment": args.assessment,
        "main_plan": args.plan,
        "retest_plan": args.retest_plan,
        "main_receipt": PILOT_ROOT / "searches" / "run-receipt.json",
        "retest_receipt": (
            PILOT_ROOT / "searches" / "snapshot-retest-run-receipt.json"
        ),
        "investigation": (PILOT_ROOT / "searches" / "wildcard-only-investigation.json"),
        "adapter_smoke": (
            PILOT_ROOT
            / "searches"
            / "adapter-smoke"
            / "automatic-screenshot-smoke.NON_MERGEABLE_DIAGNOSTIC.json"
        ),
        "guideline": args.guideline,
        "pilot_document": args.pilot_document,
    }
    digests = {}
    for name, path in artifacts.items():
        if not path.is_file():
            errors.append(f"Missing artifact: {path}")
            continue
        try:
            display_path = path.relative_to(PILOT_ROOT)
        except ValueError:
            display_path = path
        digests[name] = {
            "path": str(display_path),
            "sha256": file_sha256(path),
        }
    return {
        "schema_version": "springer-nature-link-pilot004-validation/v1",
        "pilot": "004",
        "status": "pass" if not errors else "fail",
        "checks": {
            "main_plan_events": len(plan.get("events", [])),
            "retest_plan_events": len(retest_plan.get("events", [])),
            "successful_event_json": len(event_outputs),
            "successful_event_png": len(png_outputs),
            "adapter_smoke_png": 2,
            "total_validated_png": assessment.get("screenshots", {}).get(
                "total_validated_png_count"
            ),
            "retained_failures": len(failure_outputs),
            "wildcard_partitions_accepted": len(
                assessment.get("wildcard_acceptance", {}).get(
                    "adopt_for_partitions", []
                )
            ),
            "adapter_version": adapter.ADAPTER_VERSION,
        },
        "artifacts": digests,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--retest-plan", type=Path, default=DEFAULT_RETEST_PLAN)
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--guideline", type=Path, default=DEFAULT_GUIDELINE)
    parser.add_argument("--pilot-document", type=Path, default=DEFAULT_PILOT_DOCUMENT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = validate_all(args)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps({"status": report["status"], "errors": report["errors"]}, indent=2)
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
