#!/usr/bin/env python3
"""Offline integrity checks for IAF Digital Library Pilot 003."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from assess import (
    DEFAULT_ASSESSMENT_PATH,
    DEFAULT_INVESTIGATION_PATH,
    DEFAULT_PAIR_CHECK_PATH,
    DEFAULT_SEARCH_DIR,
    build_assessment,
)
from plan import (
    DEFAULT_PLAN_PATH,
    MAIN_FACTORS,
    PILOT_DIR,
    validate_plan_payload,
)


GUIDELINE_PATH = PILOT_DIR.parents[1] / "source-specific-guidelines.md"
FINAL_SEARCH_DIR = PILOT_DIR.parents[1] / "final-searches"
PILOT_MARKDOWN = PILOT_DIR / "pilot.md"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_markdown_links(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing documentation file {path}")
        return
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("https://", "http://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        require(resolved.exists(), f"{path.name}: broken local link {target}", errors)


def check_guideline_state(errors: list[str]) -> None:
    if not GUIDELINE_PATH.is_file():
        errors.append("missing IAF source guideline")
        return
    text = GUIDELINE_PATH.read_text(encoding="utf-8")
    for line in (
        "Last pilot saved in commit: NA",
        "Final searches saved in commit: NA",
        "Citation chasing searches saved in commit: NA (not applicable)",
        "Source excluded from review due to search failure in commit: NA",
    ):
        require(line in text, f"completion state changed or missing: {line}", errors)
    require(
        "Do not treat it as an exhaustive source restriction" in text,
        "guideline no longer preserves the language limitation",
        errors,
    )
    require(
        "Apply no additional type, peer-review, access, or full-text-availability filter." in text,
        "guideline no longer preserves the conference-paper/type control decision",
        errors,
    )
    if not FINAL_SEARCH_DIR.is_dir():
        errors.append("missing final-searches directory")
    else:
        contents = sorted(item.name for item in FINAL_SEARCH_DIR.iterdir())
        require(contents == [".gitkeep"], "pilot wrote a final-search artifact", errors)


def check_json_files(search_dir: Path, errors: list[str]) -> int:
    paths = sorted(search_dir.rglob("*.json"))
    for path in paths:
        try:
            load(path)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(search_dir)}: invalid JSON: {error}")
    return len(paths)


def check_assessment_failure_policy(assessment: Mapping[str, Any], errors: list[str]) -> None:
    entries = assessment.get("entries")
    if not isinstance(entries, Mapping):
        errors.append("assessment entries are missing")
        return
    for partition_id in MAIN_FACTORS:
        entry = entries.get(partition_id)
        if not isinstance(entry, Mapping):
            errors.append(f"assessment missing {partition_id}")
            continue
        if entry.get("status") == "failure":
            for key in (
                "source_event_counts",
                "raw_paper_id_union",
                "diagnostic_window_paper_id_union",
                "paper_id_membership",
            ):
                require(entry.get(key) is None, f"{partition_id}: failed aggregate {key} is not null", errors)
            for failed in entry.get("failed_cells", []):
                if isinstance(failed, Mapping):
                    require(failed.get("total") is None, f"{partition_id}: failure cell total is not null", errors)
        elif entry.get("status") == "complete":
            raw = entry.get("raw_paper_id_union")
            retained = entry.get("diagnostic_window_paper_id_union")
            require(isinstance(raw, Mapping), f"{partition_id}: raw union missing", errors)
            require(isinstance(retained, Mapping), f"{partition_id}: retained union missing", errors)
            if isinstance(raw, Mapping):
                require(raw.get("deduplicated_count") == len(raw.get("paper_ids", [])), f"{partition_id}: raw union count does not reconcile", errors)
            if isinstance(retained, Mapping):
                require(retained.get("deduplicated_count") == len(retained.get("paper_ids", [])), f"{partition_id}: retained union count does not reconcile", errors)
        else:
            errors.append(f"{partition_id}: unknown assessment status")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--search-dir", type=Path, default=DEFAULT_SEARCH_DIR)
    parser.add_argument("--assessment-path", type=Path, default=DEFAULT_ASSESSMENT_PATH)
    parser.add_argument("--pair-check-path", type=Path, default=DEFAULT_PAIR_CHECK_PATH)
    parser.add_argument("--investigation-path", type=Path, default=DEFAULT_INVESTIGATION_PATH)
    args = parser.parse_args(argv)
    errors: list[str] = []
    plan_path = args.plan.expanduser()
    search_dir = args.search_dir.expanduser().resolve()
    try:
        plan = load(plan_path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAILED\n- cannot load plan: {error}")
        return 1
    errors.extend(validate_plan_payload(plan))
    json_count = check_json_files(search_dir, errors) if search_dir.exists() else 0
    if not search_dir.exists():
        errors.append("missing pilot search directory")
    for path in (
        args.assessment_path.expanduser(),
        args.pair_check_path.expanduser(),
        args.investigation_path.expanduser(),
    ):
        require(path.is_file(), f"missing derived artifact {path.name}", errors)
    assessment: Mapping[str, Any] | None = None
    pair_checks: Mapping[str, Any] | None = None
    investigations: Mapping[str, Any] | None = None
    if not errors:
        try:
            assessment = load(args.assessment_path.expanduser())
            pair_checks = load(args.pair_check_path.expanduser())
            investigations = load(args.investigation_path.expanduser())
            regenerated = build_assessment(plan, search_dir, plan_path)
            require(assessment == regenerated[0], "assessment is not the deterministic reconciliation of cell artifacts", errors)
            require(pair_checks == regenerated[1], "pair checks are not the deterministic local result", errors)
            require(investigations == regenerated[2], "investigations are not the deterministic threshold result", errors)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            errors.append(f"could not regenerate pilot assessment: {error}")
    if isinstance(assessment, Mapping):
        check_assessment_failure_policy(assessment, errors)
    check_guideline_state(errors)
    check_markdown_links(PILOT_MARKDOWN, errors)
    check_markdown_links(GUIDELINE_PATH, errors)
    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    assert assessment is not None
    entries = assessment["entries"]
    union_counts = {
        partition_id: {
            "raw": entry["raw_paper_id_union"]["deduplicated_count"]
            if entry["status"] == "complete"
            else None,
            "diagnostic_window": entry["diagnostic_window_paper_id_union"]["deduplicated_count"]
            if entry["status"] == "complete"
            else None,
        }
        for partition_id, entry in entries.items()
    }
    print(
        json.dumps(
            {
                "status": "ok",
                "json_files": json_count,
                "partitions": list(MAIN_FACTORS),
                "packed_cells": plan["packing"]["packed_cells"],
                "summary": assessment["summary"],
                "unions": union_counts,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
