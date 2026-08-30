#!/usr/bin/env python3
"""Validate ATAI Pilot 003 artifacts, schedule membership, and ID unions offline."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PILOT_ROOT = ROOT / "source-specific/advanced-technologies-aerospace-index/pilots/003"
SEARCH_DIR = PILOT_ROOT / "searches"
PLAN_PATH = SEARCH_DIR / "event-plan.json"
ASSESSMENT_PATH = SEARCH_DIR / "stable-id-union-reconciliation.json"
NOISE_PATH = SEARCH_DIR / "noise-investigation.json"
DOCUMENTATION_PATH = SEARCH_DIR / "source-documentation-verification.json"
REPORT_PATH = SEARCH_DIR / "validation-report.json"
SCHEDULE_DIR = ROOT / "scripts/pilot_schedule"
PRISMA_SCRIPTS = Path.home() / "agent-tools/academic-api-search/skills/academic-api-search/scripts"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"


def has_generic_stable_id_pair(partition: str) -> bool:
    return (SEARCH_DIR / f"{partition}-stable-id-reconciliation.json").exists()


def source_cell_path(partition: str) -> Path:
    if partition == "A3":
        return SEARCH_DIR / "A3-repaired-pass2.json"
    if has_generic_stable_id_pair(partition):
        return SEARCH_DIR / f"{partition}-stable-id-pass2.json"
    return SEARCH_DIR / f"{partition}.json"


def load(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path.name}: invalid JSON ({error})")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.name}: root is not an object")
        return None
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def expected_schedule(errors: list[str]) -> tuple[dict[str, Any], Any, Any] | None:
    if str(SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(SCHEDULE_DIR))
    try:
        from queries import CONCEPTS, MAIN_FACTORS, RENDERERS, partition_query
    except Exception as error:  # noqa: BLE001
        errors.append(f"Cannot import shared pilot schedule: {error}")
        return None
    plan = load(PLAN_PATH, errors)
    if plan is None:
        return None
    require(
        plan.get("schema_version") == "academic-search-event-schedule/v1",
        "event-plan.json: unsupported schema",
        errors,
    )
    events = plan.get("events")
    require(isinstance(events, list), "event-plan.json: missing event list", errors)
    if not isinstance(events, list):
        return None
    by_partition = {
        event.get("partition_id"): event
        for event in events
        if isinstance(event, dict) and isinstance(event.get("partition_id"), str)
    }
    require(tuple(by_partition) == PARTITIONS, "event-plan.json: incomplete or reordered schedule", errors)
    renderer = RENDERERS["proquest_aerospace_index"]
    for partition in PARTITIONS:
        event = by_partition.get(partition)
        if not isinstance(event, dict):
            continue
        query = partition_query("proquest_aerospace_index", partition)
        require(event.get("source") == "proquest_aerospace_index", f"{partition}: wrong source in plan", errors)
        require(event.get("event_kind") == "pilot", f"{partition}: plan is not a pilot event", errors)
        require(event.get("pilot_mode") == "strict", f"{partition}: plan does not use the standard strict pilot mode", errors)
        require("query_cells" not in event, f"{partition}: unexpected query-cell split", errors)
        require(event.get("query") == query, f"{partition}: plan query differs from shared schedule", errors)
        require("*" not in query and "?" not in query, f"{partition}: wildcard present", errors)
        for factor in MAIN_FACTORS[partition]:
            for atom in renderer.alternatives(factor):
                require(atom in query, f"{partition}: missing source atom {atom}", errors)
        # Equality with the shared renderer additionally proves every literal,
        # declared pair, parenthesis, and Boolean relationship is retained.
    return by_partition, CONCEPTS, partition_query


def validate_prisma_receipt(receipt: Any, partition: str, errors: list[str]) -> None:
    if not isinstance(receipt, dict):
        errors.append(f"{partition}: no compact PRISMA receipt")
        return
    require(
        receipt.get("schema_version") == "academic-search-prisma-search-run/v2",
        f"{partition}: unsupported PRISMA receipt schema",
        errors,
    )
    require(receipt.get("review_id") == "slr1-atai-pilot-003", f"{partition}: review ID changed", errors)
    require(receipt.get("strategy_reference") == "slr1-direct-query-schedule-v1", f"{partition}: strategy reference changed", errors)
    require(receipt.get("phase") == "pilot_complete", f"{partition}: phase is not pilot_complete", errors)
    coverage = receipt.get("coverage")
    require(isinstance(coverage, dict), f"{partition}: missing coverage", errors)
    if isinstance(coverage, dict):
        require(coverage.get("coverage_scope") == "partition", f"{partition}: coverage is not partition", errors)
        require(coverage.get("partition_id") == partition, f"{partition}: wrong receipt partition", errors)
        require(coverage.get("is_full_source_coverage") is False, f"{partition}: incorrectly claims full source coverage", errors)
    descriptor = receipt.get("source_descriptor")
    require(isinstance(descriptor, dict), f"{partition}: missing source descriptor", errors)
    if isinstance(descriptor, dict):
        require(descriptor.get("source_id") == "proquest_aerospace_index", f"{partition}: wrong source ID", errors)
        require(descriptor.get("source_label") == "Advanced Technologies & Aerospace Index", f"{partition}: wrong source label", errors)
    strategy = receipt.get("strategy")
    require(isinstance(strategy, dict), f"{partition}: missing strategy", errors)
    if not isinstance(strategy, dict):
        return
    limits = strategy.get("limits")
    require(isinstance(limits, dict), f"{partition}: missing limits", errors)
    if isinstance(limits, dict):
        language = limits.get("language")
        date = limits.get("publication_date")
        require(isinstance(language, dict) and language.get("state") == "applied" and language.get("value") == "LA(English)", f"{partition}: LA(English) not source-recorded", errors)
        require(isinstance(date, dict) and date.get("state") == "applied", f"{partition}: publication date not applied", errors)
        if isinstance(date, dict):
            effective = date.get("effective")
            require(isinstance(effective, dict), f"{partition}: missing exact date readback", errors)
            if isinstance(effective, dict):
                require(effective.get("start") == DATE_START and effective.get("end") == DATE_END and effective.get("inclusive") == "both", f"{partition}: diagnostic date bounds differ", errors)
        for key, state in (
            ("document_type", "not_applied"),
            ("peer_reviewed", "not_applied"),
            ("full_text", "unavailable"),
            ("access", "unavailable"),
            ("spelling_variants", "not_applied"),
            ("form_variants", "not_applied"),
            ("show_expansions", "not_applied"),
        ):
            entry = limits.get(key)
            require(isinstance(entry, dict) and entry.get("state") == state, f"{partition}: {key} is not {state}", errors)
    query_syntax = strategy.get("query_syntax")
    require(isinstance(query_syntax, dict), f"{partition}: missing query syntax", errors)
    if isinstance(query_syntax, dict):
        require(query_syntax.get("spelling_variants") is False, f"{partition}: spelling variants not frozen off", errors)
        require(query_syntax.get("form_variants") is False, f"{partition}: form variants not frozen off", errors)
        require(query_syntax.get("show_variants") is False, f"{partition}: display variants not frozen off", errors)
    sort = strategy.get("sort")
    require(isinstance(sort, dict) and sort.get("state") == "applied" and sort.get("value") == "DateAsc", f"{partition}: Oldest-first sort not source-recorded", errors)


def validate_cell(
    partition: str,
    event: dict[str, Any],
    query: str,
    errors: list[str],
) -> dict[str, Any] | None:
    path = source_cell_path(partition)
    payload = load(path, errors)
    if payload is None:
        return None
    metadata = payload.get("output_metadata")
    require(payload.get("schema_version") == "academic-search-result/v1", f"{partition}: wrong result schema", errors)
    require(isinstance(metadata, dict), f"{partition}: missing output metadata", errors)
    if not isinstance(metadata, dict):
        return None
    require(payload.get("source") == "Advanced Technologies & Aerospace Index", f"{partition}: wrong source", errors)
    require(payload.get("requested_query", payload.get("query")) == query, f"{partition}: raw source query changed", errors)
    require(payload.get("executed_query") == f"{query} AND LA(English)", f"{partition}: source executed-query readback changed", errors)
    require(payload.get("do_not_merge") is True, f"{partition}: not marked pilot-only", errors)
    require(metadata.get("merge_eligible") is False, f"{partition}: merge eligibility not disabled", errors)
    require(metadata.get("normalized_merge_eligible") is False, f"{partition}: normalized merge gate not disabled", errors)
    require(metadata.get("status") == "success", f"{partition}: source status not success", errors)
    require(metadata.get("retrieval_complete") is True, f"{partition}: complete capture not proven", errors)
    cell = payload.get("pilot_cell")
    require(isinstance(cell, dict), f"{partition}: missing pilot-cell declaration", errors)
    if isinstance(cell, dict):
        expected_cell_id = (
            "A3-full-expression-repaired-pass-2"
            if partition == "A3"
            else f"{partition}-full-expression-stable-id-pass-2"
            if has_generic_stable_id_pair(partition)
            else f"{partition}-full-expression"
        )
        require(cell.get("semantic_partition") == partition and cell.get("cell_id") == expected_cell_id, f"{partition}: pilot cell identity differs", errors)
        require(cell.get("lossless_cell_split") is False, f"{partition}: unexpected split state", errors)
        require(cell.get("source_native_query_characters") == len(query), f"{partition}: query length differs", errors)
        require(cell.get("source_native_query_sha256") == hashlib.sha256(query.encode()).hexdigest(), f"{partition}: query hash differs", errors)
        require(cell.get("source_total") == payload.get("total"), f"{partition}: pilot cell total differs", errors)
    total = payload.get("total")
    rows = payload.get("results")
    require(isinstance(total, int) and not isinstance(total, bool) and total >= 0, f"{partition}: source total is not an exact nonnegative integer", errors)
    require(isinstance(rows, list), f"{partition}: results are not a list", errors)
    if isinstance(total, int) and isinstance(rows, list):
        require(len(rows) == total, f"{partition}: stable rows do not reconcile to total", errors)
        seen: set[str] = set()
        for ordinal, row in enumerate(rows, start=1):
            require(isinstance(row, dict), f"{partition}: row {ordinal} is not an object", errors)
            if not isinstance(row, dict):
                continue
            identifier = row.get("paperId")
            require(isinstance(identifier, str) and identifier.isascii() and identifier.isdigit(), f"{partition}: row {ordinal} has no numeric stable ID", errors)
            if isinstance(identifier, str) and identifier.isascii() and identifier.isdigit():
                seen.add(identifier)
            url = row.get("url")
            require(url == f"https://www.proquest.com/ataindex/docview/{identifier}", f"{partition}: row {ordinal} has noncanonical stable URL", errors)
        require(len(seen) <= total, f"{partition}: invalid stable-ID accounting", errors)
    receipt = metadata.get("prisma_search_run")
    validate_prisma_receipt(receipt, partition, errors)
    if isinstance(receipt, dict) and isinstance(total, int):
        counts = receipt.get("staged_counts")
        require(isinstance(counts, dict), f"{partition}: missing staged counts", errors)
        if isinstance(counts, dict):
            require(counts.get("source_reported_total") == total, f"{partition}: receipt source total differs", errors)
            require(counts.get("records_exported") == total, f"{partition}: receipt exported count differs", errors)
            require(counts.get("source_reported_total_exact") is True, f"{partition}: total exactness is not recorded", errors)
        if partition == "A3" or has_generic_stable_id_pair(partition):
            require(receipt.get("completion_status") in {"complete", "partial"}, f"{partition}: stable-ID-pair receipt has an invalid completion state", errors)
        else:
            require(receipt.get("completion_status") == "complete", f"{partition}: receipt is not complete", errors)
        if str(PRISMA_SCRIPTS) not in sys.path:
            sys.path.insert(0, str(PRISMA_SCRIPTS))
        try:
            from _prisma_search_run import validate_prisma_search_run  # noqa: PLC0415
            validate_prisma_search_run(receipt)
        except Exception as error:  # noqa: BLE001
            errors.append(f"{partition}: PRISMA receipt validation failed ({error})")
    return payload


def stable_ids(payload: dict[str, Any], name: str, errors: list[str]) -> list[str]:
    rows = payload.get("results")
    total = payload.get("total")
    require(isinstance(rows, list) and isinstance(total, int) and len(rows) == total, f"{name}: stable-ID rows do not reconcile", errors)
    if not isinstance(rows, list):
        return []
    values = [row.get("paperId") for row in rows if isinstance(row, dict)]
    require(all(isinstance(value, str) and value.isascii() and value.isdigit() for value in values), f"{name}: nonnumeric stable ID", errors)
    return values


def validate_a3_repair(cells: dict[str, dict[str, Any]], query: str, errors: list[str]) -> None:
    failure = load(SEARCH_DIR / "A3.strict-complete.NON_MERGEABLE_FAILURE.json", errors)
    first = load(SEARCH_DIR / "A3-repaired-pass1.json", errors)
    repair = load(SEARCH_DIR / "A3-repair-reconciliation.json", errors)
    active = cells.get("A3")
    if failure is not None:
        require(failure.get("total") is None and failure.get("do_not_merge") is True, "A3 initial strict failure was not retained as null-total non-mergeable evidence", errors)
        failure_detail = failure.get("pilot_failure")
        require(isinstance(failure_detail, dict) and failure_detail.get("error") == "ProQuest did not return two stable complete rendered-result passes.", "A3 initial strict failure lacks its source error", errors)
    if first is None or active is None or repair is None:
        return
    first_ids = stable_ids(first, "A3 repaired pass 1", errors)
    active_ids = stable_ids(active, "A3 repaired pass 2", errors)
    require(first.get("requested_query") == query and active.get("requested_query") == query, "A3 repair changed the source query", errors)
    require(first.get("executed_query") == f"{query} AND LA(English)" and active.get("executed_query") == f"{query} AND LA(English)", "A3 repair changed the executed query", errors)
    require(first_ids == active_ids, "A3 repair passes have different ordered stable IDs", errors)
    require(repair.get("schema_version") == "atai-pilot-003-a3-stable-id-repair/v1", "A3 repair has wrong schema", errors)
    require(repair.get("do_not_merge") is True, "A3 repair is not pilot-only", errors)
    repair_data = repair.get("repair")
    require(isinstance(repair_data, dict), "A3 repair lacks repair data", errors)
    if isinstance(repair_data, dict):
        require(repair_data.get("ordered_stable_ids") == active_ids and repair_data.get("stable_id_equality") is True, "A3 repair ledger differs from active stable IDs", errors)


def validate_generic_stable_id_pair(partition: str, active: dict[str, Any] | None, query: str, errors: list[str]) -> None:
    receipt_path = SEARCH_DIR / f"{partition}-stable-id-reconciliation.json"
    receipt = load(receipt_path, errors)
    first = load(SEARCH_DIR / f"{partition}-stable-id-pass1.json", errors)
    if receipt is None or first is None or active is None:
        return
    require(receipt.get("schema_version") == "atai-pilot-003-stable-id-pair/v1", f"{partition}: stable-ID pair has wrong schema", errors)
    require(receipt.get("do_not_merge") is True, f"{partition}: stable-ID pair is not pilot-only", errors)
    require(receipt.get("partition_id") == partition, f"{partition}: stable-ID pair has wrong partition", errors)
    first_ids = stable_ids(first, f"{partition} stable-ID pass 1", errors)
    active_ids = stable_ids(active, f"{partition} stable-ID pass 2", errors)
    require(first.get("requested_query") == query and active.get("requested_query") == query, f"{partition}: stable-ID pair changed the raw query", errors)
    require(first.get("executed_query") == f"{query} AND LA(English)" and active.get("executed_query") == f"{query} AND LA(English)", f"{partition}: stable-ID pair changed the executed query", errors)
    require(first_ids == active_ids, f"{partition}: stable-ID passes differ", errors)
    require(receipt.get("ordered_stable_ids") == active_ids and receipt.get("stable_id_equality") is True, f"{partition}: stable-ID receipt differs from active cell", errors)
    strict_failure = receipt.get("initial_strict_failure")
    if strict_failure is not None:
        failure = load(SEARCH_DIR / f"{partition}.strict-complete.NON_MERGEABLE_FAILURE.json", errors)
        require(isinstance(strict_failure, dict), f"{partition}: invalid strict-failure linkage", errors)
        if failure is not None:
            require(failure.get("total") is None and failure.get("do_not_merge") is True, f"{partition}: strict failure was not retained", errors)
            failure_detail = failure.get("pilot_failure")
            require(isinstance(failure_detail, dict) and failure_detail.get("error") == "ProQuest did not return two stable complete rendered-result passes.", f"{partition}: strict failure error not retained", errors)


def validate_unions(cells: dict[str, dict[str, Any]], errors: list[str]) -> dict[str, Any] | None:
    assessment = load(ASSESSMENT_PATH, errors)
    if assessment is None:
        return None
    require(assessment.get("schema_version") == "atai-pilot-003-stable-id-union-reconciliation/v1", "stable-id union: wrong schema", errors)
    require(assessment.get("do_not_merge") is True, "stable-id union: not pilot-only", errors)
    require(assessment.get("event_plan", {}).get("sha256") == sha256(PLAN_PATH), "stable-id union: event plan hash differs", errors)
    repaired = assessment.get("a3_repaired_capture")
    require(isinstance(repaired, dict), "stable-id union: missing A3 repair linkage", errors)
    if isinstance(repaired, dict):
        require(repaired.get("active_artifact") == "A3-repaired-pass2.json", "stable-id union: wrong A3 active artifact", errors)
        require(repaired.get("initial_failure_artifact") == "A3.strict-complete.NON_MERGEABLE_FAILURE.json", "stable-id union: initial A3 failure is not linked", errors)
    generic_captures = assessment.get("stable_id_pair_captures")
    expected_generic = {partition for partition in PARTITIONS if partition != "A3" and has_generic_stable_id_pair(partition)}
    require(isinstance(generic_captures, dict) and set(generic_captures) == expected_generic, "stable-id union: generic stable-ID capture links differ", errors)
    if isinstance(generic_captures, dict):
        for partition in expected_generic:
            entry = generic_captures.get(partition)
            require(isinstance(entry, dict) and entry.get("active_artifact") == source_cell_path(partition).name and entry.get("reconciliation") == f"{partition}-stable-id-reconciliation.json", f"stable-id union: {partition} stable-ID capture link differs", errors)
    ledger = assessment.get("cells")
    require(isinstance(ledger, dict), "stable-id union: missing cell ledger", errors)
    if not isinstance(ledger, dict):
        return assessment
    source_event_total = 0
    all_ids: list[str] = []
    for partition in PARTITIONS:
        payload = cells.get(partition)
        entry = ledger.get(partition)
        require(isinstance(entry, dict), f"stable-id union: missing {partition} ledger", errors)
        if not isinstance(payload, dict) or not isinstance(entry, dict):
            continue
        expected_ids = [row.get("paperId") for row in payload["results"]]
        require(entry.get("stable_ids_in_source_order") == expected_ids, f"stable-id union: {partition} IDs differ from source cell", errors)
        require(entry.get("source_total") == payload.get("total"), f"stable-id union: {partition} total differs", errors)
        require(entry.get("artifact_sha256") == sha256(source_cell_path(partition)), f"stable-id union: {partition} artifact hash differs", errors)
        partition_union = assessment.get("partition_unions", {}).get(partition)
        unique = list(dict.fromkeys(expected_ids))
        require(isinstance(partition_union, dict) and partition_union.get("deduplicated_stable_ids") == unique and partition_union.get("deduplicated_union_total") == len(unique), f"stable-id union: {partition} union does not reconcile", errors)
        source_event_total += len(expected_ids)
        all_ids.extend(expected_ids)
    require(assessment.get("source_event_total") == source_event_total, "stable-id union: source event total differs", errors)
    all_unique = list(dict.fromkeys(all_ids))
    require(assessment.get("all_schedule_deduplicated_total") == len(all_unique), "stable-id union: all-schedule total differs", errors)
    stream = assessment.get("stream_unions")
    require(isinstance(stream, dict), "stable-id union: missing stream unions", errors)
    if isinstance(stream, dict):
        expected_groups = {
            "stream_A": ("A1", "A2", "A3"),
            "core_stream_B": ("B1", "B2"),
            "expanded_stream_B": ("BG1", "BG2", "BC1", "BT2"),
            "all_schedule": PARTITIONS,
        }
        for name, partitions in expected_groups.items():
            entry = stream.get(name)
            ids = list(dict.fromkeys(identifier for partition in partitions for identifier in ledger[partition]["stable_ids_in_source_order"]))
            require(isinstance(entry, dict) and entry.get("partitions") == list(partitions) and entry.get("deduplicated_stable_ids") == ids and entry.get("deduplicated_union_total") == len(ids), f"stable-id union: {name} does not reconcile", errors)
    return assessment


def validate_noise(assessment: dict[str, Any] | None, errors: list[str]) -> None:
    noise = load(NOISE_PATH, errors)
    if noise is None or assessment is None:
        return
    require(noise.get("schema_version") == "atai-pilot-003-noise-investigation/v1", "noise investigation: wrong schema", errors)
    require(noise.get("do_not_merge") is True, "noise investigation: not pilot-only", errors)
    expected_names: set[str] = {
        f"partition:{partition}"
        for partition, entry in assessment.get("partition_unions", {}).items()
        if isinstance(entry, dict) and entry.get("deduplicated_union_total", 0) > 100
    }
    expected_names.update(
        name
        for name, entry in assessment.get("stream_unions", {}).items()
        if isinstance(entry, dict) and entry.get("deduplicated_union_total", 0) > 100
    )
    observed_names = {
        entry.get("union")
        for entry in noise.get("triggered_unions", [])
        if isinstance(entry, dict)
    }
    require(observed_names == expected_names, "noise investigation: threshold unions differ", errors)
    require("No noise refinement was applied" in str(noise.get("outcome")), "noise investigation: outcome permits an unvalidated refinement", errors)


def validate_markdown_links(errors: list[str]) -> None:
    for markdown in (
        PILOT_ROOT / "pilot.md",
        ROOT / "source-specific/advanced-technologies-aerospace-index/source-specific-guidelines.md",
    ):
        try:
            text = markdown.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{markdown.name}: cannot read Markdown ({error})")
            continue
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            candidate = (markdown.parent / target).resolve()
            # This report is written only after its own link check completes.
            if candidate == REPORT_PATH.resolve():
                continue
            require(candidate.exists(), f"{markdown.name}: broken local link {target}", errors)


def validate_documentation(errors: list[str]) -> None:
    report = load(DOCUMENTATION_PATH, errors)
    if report is None:
        return
    require(report.get("schema") == "academic-source-documentation-verification/v1", "source documentation report: wrong schema", errors)
    require(report.get("ok") is True and report.get("errors") == [], "source documentation report: verifier did not pass", errors)
    verified = report.get("verified")
    require(isinstance(verified, list) and any(isinstance(item, dict) and item.get("source") == "atai" for item in verified), "source documentation report: ATAI is absent", errors)


def write_report(errors: list[str], cell_totals: dict[str, Any]) -> None:
    if REPORT_PATH.exists():
        raise RuntimeError(f"Refusing to overwrite {REPORT_PATH}")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=REPORT_PATH.parent, delete=False) as stream:
        json.dump(
            {
                "schema_version": "atai-pilot-003-validation-report/v1",
                "status": "ok" if not errors else "failed",
                "checks": {
                    "json_artifacts": "parsed",
                    "shared_schedule_query_membership": "passed" if not errors else "see errors",
                    "source_controls_and_receipts": "passed" if not errors else "see errors",
                    "stable_id_unions": "passed" if not errors else "see errors",
                    "noise_investigation_threshold": "passed" if not errors else "see errors",
                    "source_documentation": "passed" if not errors else "see errors",
                    "local_markdown_links": "passed" if not errors else "see errors",
                },
                "cell_totals": cell_totals,
                "errors": errors,
            },
            stream,
            ensure_ascii=False,
            indent=2,
        )
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(REPORT_PATH)


def main() -> int:
    errors: list[str] = []
    # Parse every source-specific JSON artifact before semantic validation.
    for path in sorted(SEARCH_DIR.glob("*.json")):
        load(path, errors)
    schedule = expected_schedule(errors)
    cells: dict[str, dict[str, Any]] = {}
    if schedule is not None:
        events, _, partition_query = schedule
        for partition in PARTITIONS:
            payload = validate_cell(partition, events[partition], partition_query("proquest_aerospace_index", partition), errors)
            if payload is not None:
                cells[partition] = payload
    if schedule is not None:
        validate_a3_repair(cells, partition_query("proquest_aerospace_index", "A3"), errors)
        for partition in PARTITIONS:
            if partition != "A3" and has_generic_stable_id_pair(partition):
                validate_generic_stable_id_pair(
                    partition,
                    cells.get(partition),
                    partition_query("proquest_aerospace_index", partition),
                    errors,
                )
    assessment = validate_unions(cells, errors)
    validate_noise(assessment, errors)
    validate_documentation(errors)
    validate_markdown_links(errors)
    totals = {partition: payload.get("total") for partition, payload in cells.items()}
    write_report(errors, totals)
    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(json.dumps({"status": "ok", "cells": len(cells), "cell_totals": totals}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
