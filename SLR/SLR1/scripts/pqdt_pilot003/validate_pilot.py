#!/usr/bin/env python3
"""Validate PQDT Global Pilot 003 artifacts without opening a browser."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

import build_assessment
import run_schedule as runner

SEARCH_DIR = runner.SEARCH_DIR
PILOT_ROOT = runner.PILOT_ROOT
PLAN_PATH = runner.PLAN_PATH
PARTITIONS = runner.PARTITIONS
ASSESSMENT_PATH = SEARCH_DIR / "stable-id-union-reconciliation.json"
NOISE_PATH = SEARCH_DIR / "noise-investigation.json"
DOCUMENTATION_PATH = SEARCH_DIR / "source-documentation-verification.json"
REPORT_PATH = SEARCH_DIR / "validation-report.json"
ORCHESTRATOR = Path.home() / "agent-tools/internet/skills/browser/scripts/run_search_events.py"
REPO_ROOT = Path(__file__).resolve().parents[4]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_all_json(errors: list[str]) -> None:
    for path in sorted(SEARCH_DIR.glob("*.json")) + sorted(SEARCH_DIR.glob(".*.json")):
        try:
            runner.load_json(path)
        except RuntimeError as error:
            errors.append(str(error))


def validate_standard_plan(errors: list[str]) -> dict[str, Any] | None:
    try:
        events = runner.load_plan()
    except RuntimeError as error:
        errors.append(str(error))
        return None
    if not ORCHESTRATOR.is_file():
        errors.append("standard schedule validator is unavailable")
        return {event["partition_id"]: event for event in events}
    command = [
        "uv", "run", str(ORCHESTRATOR), "--plan", str(PLAN_PATH),
        "--start-date", "2011-01-01", "--cutoff-date", runner.DIAGNOSTIC_CUTOFF,
        "--limit", str(runner.MAX_COMPLETE_RESULTS), "--max-pages", str(runner.MAX_PAGES),
        "--timeout", "90", "--dry-run",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    require(completed.returncode == 0, "standard pilot-plan schema dry run failed", errors)
    if completed.returncode:
        return {event["partition_id"]: event for event in events}
    try:
        projection = json.loads(completed.stdout)
    except json.JSONDecodeError:
        errors.append("standard pilot-plan dry run did not return JSON")
        return {event["partition_id"]: event for event in events}
    require(projection.get("status") == "dry_run", "standard pilot-plan dry run did not succeed", errors)
    require(len(projection.get("events", [])) == len(PARTITIONS), "standard pilot-plan dry run has the wrong event count", errors)
    if str(runner.SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(runner.SCHEDULE_DIR))
    from queries import MAIN_FACTORS, RENDERERS, partition_query  # noqa: PLC0415

    renderer = RENDERERS[runner.SOURCE_ID]
    for event in events:
        partition = event["partition_id"]
        query = event["query"]
        require(query == partition_query(runner.SOURCE_ID, partition), f"{partition}: source query differs from shared schedule", errors)
        require("*" not in query and "?" not in query, f"{partition}: wildcard found", errors)
        for factor in MAIN_FACTORS[partition]:
            for atom in renderer.alternatives(factor):
                require(atom in query, f"{partition}: missing literal or unordered pair atom", errors)
    return {event["partition_id"]: event for event in events}


def validate_documentation(errors: list[str]) -> None:
    try:
        receipt = runner.load_json(DOCUMENTATION_PATH)
    except RuntimeError as error:
        errors.append(str(error))
        return
    require(receipt.get("schema") == "academic-source-documentation-verification/v1", "source documentation receipt has the wrong schema", errors)
    require(receipt.get("ok") is True and receipt.get("errors") == [], "source documentation verifier did not pass", errors)
    verified = receipt.get("verified")
    require(isinstance(verified, list) and any(isinstance(item, dict) and item.get("source") == "pqdt" for item in verified), "source documentation receipt lacks PQDT", errors)


def validate_cells(events: Mapping[str, Mapping[str, Any]], errors: list[str]) -> dict[str, dict[str, Any]]:
    try:
        ledger = runner.load_json(SEARCH_DIR / "event-execution-ledger.json")
    except RuntimeError as error:
        errors.append(str(error))
        return {}
    raw_cells = ledger.get("cells")
    if not isinstance(raw_cells, list):
        errors.append("execution ledger has no cell list")
        return {}
    ledger_cells = {
        cell.get("partition_id"): cell
        for cell in raw_cells
        if isinstance(cell, dict) and isinstance(cell.get("partition_id"), str)
    }
    require(tuple(ledger_cells) == PARTITIONS, "execution ledger does not retain the complete ordered schedule", errors)
    cells: dict[str, dict[str, Any]] = {}
    for partition in PARTITIONS:
        event = events.get(partition)
        cell = ledger_cells.get(partition)
        if event is None or cell is None:
            continue
        path = SEARCH_DIR / str(cell.get("artifact"))
        try:
            if cell.get("status") == "complete":
                verified = runner._strict_success_entry(path, event)
                require(cell == verified, f"{partition}: execution ledger differs from immutable strict evidence", errors)
                cells[partition] = verified
            else:
                failure = runner.load_json(path)
                require(failure.get("total") is None and cell.get("source_total") is None, f"{partition}: strict failure total is not null", errors)
                cells[partition] = dict(cell)
        except RuntimeError as error:
            errors.append(str(error))
    return cells


def expected_union(cells: Mapping[str, Mapping[str, Any]], partitions: tuple[str, ...]) -> dict[str, Any]:
    return build_assessment.union_from_cells(cells, partitions)


def validate_assessment(cells: Mapping[str, Mapping[str, Any]], errors: list[str]) -> dict[str, Any] | None:
    try:
        assessment = runner.load_json(ASSESSMENT_PATH)
    except RuntimeError as error:
        errors.append(str(error))
        return None
    require(assessment.get("schema_version") == "pqdt-global-pilot-003-stable-id-union-reconciliation/v1", "stable-ID union has the wrong schema", errors)
    require(assessment.get("do_not_merge") is True, "stable-ID union is not pilot-only", errors)
    require(assessment.get("event_plan", {}).get("sha256") == runner.sha256_file(PLAN_PATH), "stable-ID union event-plan hash differs", errors)
    ledger = assessment.get("cells")
    require(isinstance(ledger, dict) and tuple(ledger) == PARTITIONS, "stable-ID union lacks all nine cell ledgers", errors)
    if not isinstance(ledger, dict):
        return assessment
    for partition in PARTITIONS:
        if partition in cells:
            expected_cell = dict(cells[partition])
            ids = expected_cell.get("stable_ids_in_source_order")
            expected_cell["deduplicated_cell_total"] = len(ids) if isinstance(ids, list) else None
            expected_cell["within_cell_duplicate_stable_ids"] = [] if isinstance(ids, list) else None
            require(ledger.get(partition) == expected_cell, f"stable-ID union: {partition} cell differs from execution evidence", errors)
    partition_unions = assessment.get("partition_unions")
    require(isinstance(partition_unions, dict), "stable-ID union lacks partition unions", errors)
    if isinstance(partition_unions, dict):
        for partition in PARTITIONS:
            expected = {"cell_ids": [f"{partition}-full-expression"], **expected_union(cells, (partition,))}
            require(partition_unions.get(partition) == expected, f"stable-ID union: {partition} union differs", errors)
    stream_unions = assessment.get("stream_unions")
    expected_streams = {
        "stream_A": ("A1", "A2", "A3"),
        "core_stream_B": ("B1", "B2"),
        "expanded_stream_B": ("BG1", "BG2", "BC1", "BT2"),
        "all_schedule": PARTITIONS,
    }
    require(isinstance(stream_unions, dict), "stable-ID union lacks stream unions", errors)
    if isinstance(stream_unions, dict):
        for name, partitions in expected_streams.items():
            require(stream_unions.get(name) == expected_union(cells, partitions), f"stable-ID union: {name} differs", errors)
        all_total = stream_unions.get("all_schedule", {}).get("deduplicated_union_total") if isinstance(stream_unions.get("all_schedule"), dict) else None
        require(assessment.get("all_schedule_deduplicated_total") == all_total, "stable-ID union: all-schedule total differs", errors)
    return assessment


def validate_noise(assessment: Mapping[str, Any] | None, errors: list[str]) -> None:
    if assessment is None:
        return
    try:
        noise = runner.load_json(NOISE_PATH)
    except RuntimeError as error:
        errors.append(str(error))
        return
    require(noise.get("schema_version") == "pqdt-global-pilot-003-noise-investigation/v1", "noise investigation has the wrong schema", errors)
    require(noise.get("do_not_merge") is True, "noise investigation is not pilot-only", errors)
    expected_names: set[str] = set()
    for partition, union in assessment.get("partition_unions", {}).items():
        if isinstance(union, dict) and isinstance(union.get("deduplicated_union_total"), int) and union["deduplicated_union_total"] > build_assessment.THRESHOLD:
            expected_names.add(f"partition:{partition}")
    for name, union in assessment.get("stream_unions", {}).items():
        if isinstance(union, dict) and isinstance(union.get("deduplicated_union_total"), int) and union["deduplicated_union_total"] > build_assessment.THRESHOLD:
            expected_names.add(name)
    observed_names = {
        item.get("union") for item in noise.get("triggered_unions", []) if isinstance(item, dict)
    }
    require(observed_names == expected_names, "noise investigation threshold unions differ", errors)
    require("No query refinement was applied" in str(noise.get("outcome")), "noise investigation permits an unvalidated refinement", errors)


def validate_markdown_links(errors: list[str]) -> None:
    for markdown in (PILOT_ROOT / "pilot.md", runner.ROOT / "source-specific/pqdt-global/source-specific-guidelines.md"):
        try:
            text = markdown.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"Cannot read {markdown}: {error}")
            continue
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            candidate = (markdown.parent / target).resolve()
            if candidate == REPORT_PATH.resolve():
                continue
            require(candidate.exists(), f"{markdown.name}: broken local link {target}", errors)


def validate_focused_diff(errors: list[str]) -> None:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        errors.append("could not inspect the focused Pilot 003 diff")
        return
    allowed = (
        "SLR/SLR1/scripts/pqdt_pilot003/",
        "SLR/SLR1/source-specific/pqdt-global/",
    )
    paths = []
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[-1]
        paths.append(path)
    for path in paths:
        require(path.startswith(allowed), f"unfocused worktree change: {path}", errors)


def main() -> int:
    if REPORT_PATH.exists():
        raise RuntimeError(f"Refusing to overwrite {REPORT_PATH}")
    errors: list[str] = []
    validate_all_json(errors)
    events = validate_standard_plan(errors)
    validate_documentation(errors)
    cells = validate_cells(events or {}, errors)
    assessment = validate_assessment(cells, errors)
    validate_noise(assessment, errors)
    validate_markdown_links(errors)
    validate_focused_diff(errors)
    report = {
        "schema_version": "pqdt-global-pilot-003-validation-report/v1",
        "status": "ok" if not errors else "failed",
        "checks": {
            "json_artifacts": "parsed" if not errors else "see errors",
            "standard_pilot_plan_schema": "passed" if not errors else "see errors",
            "exact_schedule_membership": "passed" if not errors else "see errors",
            "source_controls_scope_and_two_pass_ids": "passed" if not errors else "see errors",
            "stable_id_unions": "passed" if not errors else "see errors",
            "noise_investigation_threshold": "passed" if not errors else "see errors",
            "source_documentation": "passed" if not errors else "see errors",
            "local_markdown_links": "passed" if not errors else "see errors",
            "focused_diff": "passed" if not errors else "see errors",
        },
        "cell_totals": {partition: cells.get(partition, {}).get("source_total") for partition in PARTITIONS},
        "errors": errors,
    }
    runner.write_new_json(REPORT_PATH, report)
    print(json.dumps({"status": report["status"], "cell_totals": report["cell_totals"], "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
