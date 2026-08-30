#!/usr/bin/env python3
"""Validate saved OATD Pilot 003 plan, union status, and local documentation."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
RUNNER_PATH = SCRIPT_DIR / "run_pilot.py"
SLR1_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_SEARCH_DIR = SLR1_ROOT / "source-specific" / "oatd" / "pilots" / "003" / "searches"


def load_runner():
    spec = importlib.util.spec_from_file_location("oatd_pilot003_validator_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - setup guard
        raise RuntimeError("could not load Pilot 003 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return value


def add(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate_links(markdown: Path, errors: list[str]) -> None:
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        add(errors, (markdown.parent / target).resolve().exists(), f"{markdown}: broken local link {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-dir", type=Path, default=DEFAULT_SEARCH_DIR)
    args = parser.parse_args()
    root = args.search_dir.expanduser().resolve()
    errors: list[str] = []
    required = {
        "plan": root / "lossless-cell-plan.json",
        "preflight": root / "browser-preflight.json",
        "assessment": root / "execution-assessment.json",
    }
    for path in required.values():
        add(errors, path.is_file() and not path.is_symlink(), f"missing regular artifact {path.name}")
    if errors:
        print("FAILED\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    try:
        plan = load(required["plan"])
        preflight = load(required["preflight"])
        assessment = load(required["assessment"])
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAILED\n- invalid JSON: {error}")
        return 1

    runner = load_runner()
    modules = runner.load_modules()
    regenerated = runner.build_plan(modules)
    add(errors, plan.get("schema_version") == runner.PLAN_SCHEMA, "plan schema differs")
    add(errors, plan.get("partition_order") == list(runner.PARTITION_FACTORS), "plan omits/reorders a partition")
    add(errors, plan.get("total_planned_cells") == regenerated.get("total_planned_cells"), "total planned cells differs from regenerated plan")
    # The timestamp is intentionally volatile. Every cell, query, hash,
    # route length, coverage value, and control must otherwise reproduce.
    for partition_id in runner.PARTITION_FACTORS:
        saved = plan.get("partitions", {}).get(partition_id)
        expected = regenerated.get("partitions", {}).get(partition_id)
        add(errors, isinstance(saved, dict), f"{partition_id}: missing saved partition")
        if not isinstance(saved, dict) or not isinstance(expected, dict):
            continue
        for key in (
            "protocol_boolean_form",
            "factor_labels",
            "factor_alternative_counts",
            "distributive_grid_group_counts",
            "planned_cell_count",
            "complete_expression",
            "coverage",
            "cells",
        ):
            add(errors, saved.get(key) == expected.get(key), f"{partition_id}: saved {key} differs from exact regenerated plan")
        for cell in saved.get("cells", []):
            add(errors, cell.get("encoded_route_characters", runner.CELL_TARGET + 1) <= runner.CELL_TARGET, f"{partition_id}: cell exceeds 1,500-character target")
            add(errors, cell.get("adapter_planner_rechecked_as_identity") is True, f"{partition_id}: cell lacks planner identity recheck")
            query = cell.get("query", "")
            add(errors, isinstance(query, str) and "*" not in query and "?" not in query, f"{partition_id}: wildcard in a cell")

    add(errors, assessment.get("schema_version") == runner.ASSESSMENT_SCHEMA, "assessment schema differs")
    add(errors, assessment.get("plan_total_cells") == plan.get("total_planned_cells"), "assessment total cells does not bind plan")
    add(errors, preflight.get("source_requests_attempted") == 0, "browser preflight made a source request")
    add(errors, isinstance(assessment.get("source_requests_attempted"), int) and assessment.get("source_requests_attempted") >= 0, "assessment has an invalid source-request count")
    add(errors, "/Users/" not in json.dumps(preflight), "preflight retained a local path")
    source_requests = assessment.get("source_requests_attempted")
    health_evidence = assessment.get("health_route_evidence")
    if isinstance(source_requests, int) and source_requests > 0:
        add(errors, preflight.get("healthy") is True, "source run lacks a healthy browser preflight")
        add(
            errors,
            preflight.get("launcher") == "canonical_main_shared_browser_runner_status",
            "source run did not use the canonical main browser runner",
        )
        add(errors, assessment.get("source_route_attempted") is True, "source run is not marked attempted")
        add(errors, isinstance(health_evidence, dict), "source run lacks health-route evidence")
        if isinstance(health_evidence, dict):
            add(
                errors,
                health_evidence.get("status") == "healthy_route_then_exact_english_readback_confirmed",
                "health route and exact English readback were not both accepted",
            )
            health_artifacts = health_evidence.get("artifacts")
            add(errors, isinstance(health_artifacts, list) and len(health_artifacts) == 2, "health evidence lacks plain and English artifacts")
            if isinstance(health_artifacts, list) and len(health_artifacts) == 2:
                plain, english = health_artifacts
                expected_plain = "title:(microRNA) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
                expected_english = "title:(microRNA) AND language:(en OR eng OR english) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
                add(errors, plain.get("kind") == "plain" and plain.get("status") == "accepted", "plain health route was not accepted")
                add(errors, plain.get("exact_source_rendered_query") == expected_plain, "plain health route lacks exact readback")
                add(errors, english.get("kind") == "english" and english.get("status") == "accepted", "English health route was not accepted")
                add(errors, english.get("exact_source_rendered_query") == expected_english, "English health route lacks exact native clause")
                add(errors, english.get("observed_exact_query_echo") is True, "English health route lacks exact source echo")
                language = english.get("language_filter")
                add(errors, isinstance(language, dict) and language.get("display_label") == "English" and language.get("source_value") == "(en OR eng OR english)", "English health route lacks native language readback")
        budget = assessment.get("source_budget")
        add(errors, isinstance(budget, dict), "source run lacks rate-safe budget evidence")
        if isinstance(budget, dict):
            add(errors, isinstance(budget.get("configured_adapter_invocation_budget"), int), "source budget is not numeric")
            add(errors, budget.get("round_robin_policy"), "source budget lacks round-robin policy")
    for partition_id, partition in plan.get("partitions", {}).items():
        observed = assessment.get("partitions", {}).get(partition_id)
        add(errors, isinstance(observed, dict), f"{partition_id}: assessment missing partition")
        if not isinstance(observed, dict):
            continue
        cells = observed.get("cells", [])
        expected_cells = partition.get("cells", [])
        add(errors, observed.get("planned_cell_count") == len(expected_cells), f"{partition_id}: assessment planned count mismatch")
        add(errors, [item.get("cell_id") for item in cells] == [item.get("cell_id") for item in expected_cells], f"{partition_id}: assessment cell membership/order mismatch")
        add(errors, [item.get("query_sha256") for item in cells] == [item.get("query_sha256") for item in expected_cells], f"{partition_id}: assessment query bindings mismatch")
        strict_complete = observed.get("strict_complete_cell_count")
        union = observed.get("union", {})
        if strict_complete != len(expected_cells):
            add(errors, observed.get("total") is None, f"{partition_id}: incomplete partition reported a total")
            add(errors, union.get("lossless") is False and union.get("union_total") is None, f"{partition_id}: incomplete partition reported a Record-ID union")
        else:
            add(errors, union.get("lossless") is True, f"{partition_id}: all strict cells lack a lossless union")
            add(errors, observed.get("total") == union.get("union_total"), f"{partition_id}: total does not bind union")
        for cell in cells:
            if cell.get("status") != "strict_complete":
                add(errors, cell.get("total") is None, f"{partition_id}: non-strict cell was reported as a source total")
        if isinstance(health_evidence, dict) and health_evidence.get("status") == "healthy_route_then_exact_english_readback_confirmed":
            add(errors, bool(cells) and cells[0].get("status") != "not_attempted", f"{partition_id}: round-robin run did not attempt the first cell")

    pilot_md = root.parent / "pilot.md"
    guideline = SLR1_ROOT / "source-specific" / "oatd" / "source-specific-guidelines.md"
    for markdown in (pilot_md, guideline):
        add(errors, markdown.is_file(), f"missing documentation {markdown}")
        if markdown.is_file():
            validate_links(markdown, errors)
    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(json.dumps({
        "status": "ok",
        "planned_cells": plan["total_planned_cells"],
        "browser_status": preflight.get("status"),
        "partition_outcomes": {key: value.get("total") for key, value in assessment["partitions"].items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
