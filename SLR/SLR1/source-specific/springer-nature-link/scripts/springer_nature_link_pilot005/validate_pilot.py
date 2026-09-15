#!/usr/bin/env python3
"""Validate Springer Pilot 005 mapping evidence and guidance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from validate_mapping import (
    DEFAULT_ADAPTER,
    DEFAULT_PLAN,
    DEFAULT_OUTPUT as LIVE_OUTPUT,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific" / "springer-nature-link" / "pilots" / "005"
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


def validate(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[str] = []
    plan = load(args.plan)
    evidence = load(args.evidence)
    if (
        plan.get("schema_version") != "springer-nature-link-pilot005-event-plan/v1"
        or plan.get("adapter_minimum_version") != 11
        or plan.get("check_final_response_status") is not False
        or plan.get("navigate_to_nature") is not False
    ):
        errors.append("Event plan changed")
    observed = evidence.get("observed", {})
    if (
        evidence.get("status") != "pass"
        or evidence.get("errors") != []
        or evidence.get("plan_sha256") != file_sha256(args.plan)
        or evidence.get("adapter", {}).get("adapter_version") != "11"
        or observed.get("source_card_path") != plan.get("source_card_path")
        or observed.get("final_url") != plan.get("expected_link_url")
        or observed.get("redirect_count") != 0
        or observed.get("canonical_link") != plan.get("expected_canonical_link")
        or observed.get("abstract_available") is not True
        or observed.get("final_response_status_checked") is not False
        or observed.get("nature_url_navigated") is not False
        or observed.get("owned_page_closed") is not True
    ):
        errors.append("Live mapping evidence changed")
    guideline = args.guideline.read_text(encoding="utf-8")
    pilot_document = args.pilot_document.read_text(encoding="utf-8")
    for text in (
        "[Pilot 005](pilots/005/pilot.md)",
        "Final response status is not an acceptance condition",
        "Do not navigate to Nature",
        "external canonical-link and exact-day readiness blockers are resolved",
    ):
        if text not in guideline:
            errors.append(f"Guideline lacks required text: {text}")
    for text in (
        "Adapter version 11 allows this exact mapping",
        "does not navigate to Nature",
        "no longer uses the final navigation response status",
        "external canonical-link blocker from Pilot 004 is resolved",
    ):
        if text not in pilot_document:
            errors.append(f"Pilot document lacks required text: {text}")
    adapter_text = args.adapter.read_text(encoding="utf-8")
    for text in (
        'ADAPTER_VERSION = "12"',
        "validated_springer_detail_canonical_link",
        'NATURE_CANONICAL_HOST = "www.nature.com"',
    ):
        if text not in adapter_text:
            errors.append(f"Adapter lacks required contract: {text}")
    return {
        "schema_version": "springer-nature-link-pilot005-validation/v1",
        "pilot": "005",
        "status": "pass" if not errors else "fail",
        "checks": {
            "adapter_version": evidence.get("adapter", {}).get("adapter_version"),
            "redirect_count": observed.get("redirect_count"),
            "abstract_available": observed.get("abstract_available"),
            "final_response_status_checked": observed.get(
                "final_response_status_checked"
            ),
            "nature_url_navigated": observed.get("nature_url_navigated"),
            "owned_page_closed": observed.get("owned_page_closed"),
        },
        "artifacts": {
            "plan": {
                "path": str(args.plan.relative_to(PILOT_ROOT)),
                "sha256": file_sha256(args.plan),
            },
            "evidence": {
                "path": str(args.evidence.relative_to(PILOT_ROOT)),
                "sha256": file_sha256(args.evidence),
            },
            "pilot_document": {
                "path": str(args.pilot_document),
                "sha256": file_sha256(args.pilot_document),
            },
            "guideline": {
                "path": str(args.guideline),
                "sha256": file_sha256(args.guideline),
            },
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--evidence", type=Path, default=LIVE_OUTPUT)
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
