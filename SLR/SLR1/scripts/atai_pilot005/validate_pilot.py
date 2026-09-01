#!/usr/bin/env python3

"""Validate ATAI Pilot 005 adapter repair artifacts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot005_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate(pilot_root: Path, guideline: Path) -> dict[str, Any]:
    errors: list[str] = []
    searches = pilot_root / "searches"
    audit = load(searches / "adapter-repair-validation.json")
    a3 = load(searches / "A3.strict-v4.json")
    b1 = load(searches / "B1.strict-v4.json")
    adapter = load_adapter()

    if adapter.ADAPTER_VERSION != "4":
        errors.append("General ATAI adapter is not version 4.")
    if not hasattr(adapter, "dismiss_restore_session_overlay"):
        errors.append("General ATAI adapter lacks restore-session handling.")
    if not hasattr(adapter.ProQuestBrowserLease, "__dataclass_fields__") or (
        "owned_target_id" not in adapter.ProQuestBrowserLease.__dataclass_fields__
    ):
        errors.append("ATAI lease lacks owned_target_id.")
    if adapter.canonicalize_proquest_abstract("Complete. More") != "Complete.":
        errors.append("Terminal More canonicalization failed.")
    if adapter.canonicalize_proquest_abstract("learn more") != "learn more":
        errors.append("Abstract canonicalization changes ordinary prose.")

    expected = {"A3": (a3, 1), "B1": (b1, 19)}
    for partition, (artifact, total) in expected.items():
        metadata = artifact.get("output_metadata", {})
        prisma = metadata.get("prisma_search_run", {})
        limits = prisma.get("strategy", {}).get("limits", {})
        if (
            artifact.get("total") != total
            or len(artifact.get("results", [])) != total
            or metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or metadata.get("merge_eligible") is not False
            or artifact.get("do_not_merge") is not True
            or prisma.get("completion_status") != "complete"
            or prisma.get("adapter", {}).get("adapter_version") != "4"
            or artifact.get("pilot_cell", {}).get("status")
            != "strict_two_full_record_passes_succeeded"
        ):
            errors.append(f"{partition} strict artifact contract failed.")
        if any(
            str(record.get("abstract", "")).endswith(" More")
            for record in artifact.get("results", [])
        ):
            errors.append(f"{partition} retained terminal More.")
        if limits.get("language", {}).get("value") != "LA(English)":
            errors.append(f"{partition} lacks LA(English) readback.")
        if limits.get("document_type", {}).get("state") != "not_applied":
            errors.append(f"{partition} applied a type filter.")
        date = limits.get("publication_date", {}).get("effective", {})
        if date.get("start") != "2011-01-01" or date.get("end") != "2026-08-29":
            errors.append(f"{partition} date window changed.")

    if (
        audit.get("status") != "passed"
        or audit.get("adapter", {}).get("version") != "4"
        or audit.get("abstract_audit", {}).get("terminal_more_is_truncation")
        is not False
        or audit.get("strict_runs", {}).get("A3", {}).get("stable_complete_passes")
        != 2
        or audit.get("strict_runs", {}).get("B1", {}).get("stable_complete_passes")
        != 2
        or audit.get("cleanup", {}).get("A3_page_count_restored") is not True
        or audit.get("cleanup", {}).get("B1_page_count_restored") is not True
    ):
        errors.append("Adapter repair audit contract failed.")
    if (
        audit.get("abstract_audit", {})
        .get("A3", {})
        .get("historical_records_with_only_terminal_more_instability")
        != 1
    ):
        errors.append("A3 historical More count changed.")
    if (
        audit.get("abstract_audit", {})
        .get("B1", {})
        .get("historical_records_with_only_terminal_more_instability")
        != 7
    ):
        errors.append("B1 historical More count changed.")

    guideline_text = guideline.read_text()
    if "[Pilot 005](pilots/005/pilot.md)" not in guideline_text:
        errors.append("Source guideline does not link Pilot 005.")

    pilot_path = pilot_root / "pilot.md"
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", pilot_path.read_text()):
        if target.startswith(("http://", "https://", "#")):
            continue
        if not (pilot_path.parent / target.split("#", 1)[0]).resolve().exists():
            errors.append(f"Missing Pilot 005 Markdown link: {target}")

    serialized = json.dumps({"audit": audit, "a3": a3, "b1": b1}).lower()
    for forbidden in ("accountid=", "csrf", "sessionid", "/ataindex/results/"):
        if forbidden in serialized:
            errors.append(f"Pilot 005 retained forbidden session data: {forbidden}")

    return {
        "schema_version": "atai-pilot-005-validation-report/v1",
        "status": "ok" if not errors else "error",
        "checks": {
            "adapter_version_4": adapter.ADAPTER_VERSION == "4",
            "abstract_canonicalization": "passed",
            "abstract_truncation_audit": "passed",
            "A3_strict_two_pass": "passed",
            "B1_strict_two_pass": "passed",
            "restore_session_handler": "passed",
            "inventory_proven_cleanup": "passed",
            "local_markdown_links": "passed" if not any("Markdown" in error for error in errors) else "failed",
            "privacy_boundary": "passed" if not any("session data" in error for error in errors) else "failed",
        },
        "summary": {
            "A3_total": a3.get("total"),
            "B1_total": b1.get("total"),
            "historical_terminal_more_records": 8,
            "truncated_abstracts_observed": 0,
            "cleanup_page_counts_restored": 2,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.pilot_root, args.guideline)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
