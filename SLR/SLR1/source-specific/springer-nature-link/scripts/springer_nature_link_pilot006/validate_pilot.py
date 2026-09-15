#!/usr/bin/env python3
"""Validate Springer Pilot 006 evidence and synchronized guidance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_assessment import DEFAULT_OUTPUT as DEFAULT_ASSESSMENT
from run_pilot import DEFAULT_ADAPTER, DEFAULT_PLAN, DEFAULT_RECEIPT, PILOT_ROOT

DEFAULT_GUIDELINE = PILOT_ROOT.parents[1] / "source-specific-guidelines.md"
DEFAULT_PILOT_DOCUMENT = PILOT_ROOT / "pilot.md"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "validation-report.json"
CONCURRENT_HELPER = DEFAULT_ADAPTER.with_name("_springer_concurrent_cdp.py")


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


def validate(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[str] = []
    plan = load(args.plan)
    receipt = load(args.receipt)
    assessment = load(args.assessment)
    if (
        plan.get("schema_version") != "springer-nature-link-pilot006-event-plan/v4"
        or plan.get("adapter_minimum_version") != 12
        or plan.get("shared_controls", {}).get("browser_mode")
        != "target_scoped_shared_cdp"
        or len(plan.get("events", [])) != 3
    ):
        errors.append("Final plan changed")
    if (
        receipt.get("status") != "complete"
        or receipt.get("plan_sha256") != file_sha256(args.plan)
        or receipt.get("event_count") != 3
        or receipt.get("adapter", {}).get("adapter_version") != "12"
    ):
        errors.append("Run receipt changed")
    decisions = assessment.get("decisions", {})
    if (
        assessment.get("status") != "complete"
        or assessment.get("errors") != []
        or assessment.get("screenshots", {}).get("validated_png_count") != 6
        or assessment.get("screenshots", {}).get("all_sibling_paths") is not True
        or assessment.get("retained_failed_attempt_count") != 4
        or any(value in {None, "unresolved"} for value in decisions.values())
        or decisions.get("source_final_search_readiness") != "accepted"
    ):
        errors.append("Assessment changed")
    expected = {
        "nature-included-shared": (1, 1, "included", "2026-05-26"),
        "unresolved-retained-shared": (1, 1, "unresolved", None),
        "post-cutoff-excluded-shared": (1, 0, "excluded", "2026-09-01"),
    }
    for event_id, values in expected.items():
        event = assessment.get("events", {}).get(event_id, {})
        if (
            event.get("source_total") != values[0]
            or event.get("results_retrieved") != values[1]
            or event.get("date_status") != values[2]
            or event.get("resolved_date") != values[3]
            or event.get("browser_transport") != "target_scoped_shared_cdp"
            or event.get("prisma_report_ready") is not True
        ):
            errors.append(f"Event assessment changed for {event_id}")
    if assessment.get("adapter", {}).get("adapter_script_sha256") != file_sha256(
        args.adapter
    ):
        errors.append("Adapter script changed after the pilot")
    if assessment.get("adapter", {}).get("concurrent_helper_sha256") != file_sha256(
        CONCURRENT_HELPER
    ):
        errors.append("Concurrent helper changed after the pilot")

    guideline = args.guideline.read_text(encoding="utf-8")
    pilot_document = args.pilot_document.read_text(encoding="utf-8")
    for text in (
        "[Pilot 006](pilots/006/pilot.md)",
        "target-scoped shared-browser transport",
        "no pending source pilot",
        "ready for final rendered searches",
    ):
        if text not in guideline:
            errors.append(f"Guideline lacks required text: {text}")
    for text in (
        "Playwright connected to Chrome's browser WebSocket",
        "target-scoped CDP transport",
        "six sibling PNGs",
        "Springer has no pending source pilot",
    ):
        if text not in pilot_document:
            errors.append(f"Pilot document lacks required text: {text}")

    artifacts = {
        "plan": args.plan,
        "receipt": args.receipt,
        "assessment": args.assessment,
        "pilot_document": args.pilot_document,
        "guideline": args.guideline,
    }
    artifact_receipts = {}
    for name, path in artifacts.items():
        if not path.is_file():
            errors.append(f"Missing artifact: {path}")
            continue
        try:
            display = path.relative_to(PILOT_ROOT)
        except ValueError:
            display = path
        artifact_receipts[name] = {
            "path": str(display),
            "sha256": file_sha256(path),
        }
    return {
        "schema_version": "springer-nature-link-pilot006-validation/v1",
        "pilot": "006",
        "status": "pass" if not errors else "fail",
        "checks": {
            "strict_complete_events": len(assessment.get("events", {})),
            "validated_png": assessment.get("screenshots", {}).get(
                "validated_png_count"
            ),
            "retained_null_failures": assessment.get("retained_failed_attempt_count"),
            "adapter_version": assessment.get("adapter", {}).get("adapter_version"),
            "source_final_search_readiness": decisions.get(
                "source_final_search_readiness"
            ),
        },
        "artifacts": artifact_receipts,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--assessment", type=Path, default=DEFAULT_ASSESSMENT)
    parser.add_argument("--guideline", type=Path, default=DEFAULT_GUIDELINE)
    parser.add_argument("--pilot-document", type=Path, default=DEFAULT_PILOT_DOCUMENT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = validate(args)
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
