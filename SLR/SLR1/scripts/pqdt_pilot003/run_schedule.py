#!/usr/bin/env python3
"""Run the predeclared PQDT Global Pilot 003 cells sequentially.

Each adapter invocation owns one browser tab and its own ProQuest scope
snapshot.  The adapter must prove the exact PQDT-only scope and restore the
pre-event selection before this runner accepts a cell.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
PILOT_ROOT = ROOT / "source-specific/pqdt-global/pilots/003"
SEARCH_DIR = PILOT_ROOT / "searches"
PLAN_PATH = SEARCH_DIR / "event-plan.json"
SCHEDULE_DIR = ROOT / "scripts/pilot_schedule"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_pqdt.py"
SOURCE_ID = "proquest_dissertations_theses_global"
SOURCE_LABEL = "ProQuest Dissertations & Theses Global"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
SOURCE_YEAR_START = 2011
SOURCE_YEAR_END = 2026
DIAGNOSTIC_CUTOFF = "2026-08-29"
MAX_QUERY_CHARACTERS = 50_000
MAX_COMPLETE_RESULTS = 10_000
MAX_PAGES = 500
ALLOWED_DATABASE_LABELS = {
    "ProQuest Dissertations & Theses Global",
    "ProQuest Dissertations & Theses Global Full Text Included",
}
FROZEN_ADAPTER_ARGS = (
    "--year-start=2011",
    "--year-end=2026",
    "--language=English",
    "--no-full-text",
    "--no-exclude-duplicates",
    "--no-spelling-variants",
    "--no-form-variants",
    "--no-show-variants",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def ordered_id_digest(ids: list[str]) -> str:
    """Match the adapter's length-framed ordered document-ID digest."""
    digest = hashlib.sha256()
    for document_id in ids:
        encoded = document_id.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} is not a JSON object.")
    return value


def write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write a concise owned receipt without replacing prior evidence."""
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    try:
        os.link(temporary, path)
    except FileExistsError as error:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Refusing to overwrite {path}") from error
    else:
        temporary.unlink()


def _expected_query(partition: str) -> str:
    if str(SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(SCHEDULE_DIR))
    from queries import partition_query  # noqa: PLC0415

    return partition_query(SOURCE_ID, partition)


def load_plan() -> list[dict[str, Any]]:
    """Check the standard schedule and its frozen PQDT controls before UI work."""
    plan = load_json(PLAN_PATH)
    if plan.get("schema_version") != "academic-search-event-schedule/v1":
        raise RuntimeError("Pilot plan does not use the standard event-schedule schema.")
    if plan.get("planned_sources") != {"main": [SOURCE_ID]}:
        raise RuntimeError("Pilot plan does not declare PQDT Global as its only source.")
    if plan.get("planned_partitions") != {"main": list(PARTITIONS)}:
        raise RuntimeError("Pilot plan does not declare the complete ordered partition schedule.")
    window = plan.get("requested_window")
    if not isinstance(window, dict) or window.get("start_date") != "2011-01-01" or window.get("cutoff_date") != DIAGNOSTIC_CUTOFF:
        raise RuntimeError("Pilot plan has the wrong diagnostic window.")
    if window.get("source_years") != {"start": SOURCE_YEAR_START, "end": SOURCE_YEAR_END}:
        raise RuntimeError("Pilot plan has the wrong PQDT source-year window.")
    if plan.get("pilot_only") is not True:
        raise RuntimeError("Pilot plan is not marked pilot-only.")
    events = plan.get("events")
    if not isinstance(events, list):
        raise RuntimeError("Pilot plan has no event list.")
    by_partition: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            raise RuntimeError("Pilot plan contains a non-object event.")
        partition = event.get("partition_id")
        if partition not in PARTITIONS or partition in by_partition:
            raise RuntimeError("Pilot plan has an unknown or repeated partition.")
        if event.get("event_kind") != "pilot" or event.get("pilot_mode") != "strict":
            raise RuntimeError(f"{partition}: Pilot 003 must use strict pilot mode.")
        if event.get("review_namespace") != "main" or event.get("source") != SOURCE_ID:
            raise RuntimeError(f"{partition}: wrong source or namespace.")
        if event.get("review_id") != "slr1-pqdt-pilot-003":
            raise RuntimeError(f"{partition}: wrong pilot review identifier.")
        if event.get("strategy_reference") != "slr1-direct-query-schedule-v1":
            raise RuntimeError(f"{partition}: wrong strategy reference.")
        if "query_cells" in event:
            raise RuntimeError(f"{partition}: unexpected lossless-cell split.")
        query = event.get("query")
        if not isinstance(query, str) or query != _expected_query(partition):
            raise RuntimeError(f"{partition}: query differs from the shared literal schedule.")
        if len(query) > MAX_QUERY_CHARACTERS:
            raise RuntimeError(f"{partition}: query exceeds the documented adapter limit.")
        if "*" in query or "?" in query:
            raise RuntimeError(f"{partition}: a wildcard is forbidden.")
        if tuple(event.get("adapter_args", ())) != FROZEN_ADAPTER_ARGS:
            raise RuntimeError(f"{partition}: frozen source controls differ from the plan.")
        by_partition[partition] = event
    if tuple(by_partition) != PARTITIONS:
        raise RuntimeError("Pilot plan does not contain all nine partitions in order.")
    return [by_partition[partition] for partition in PARTITIONS]


def _scope_summary(metadata: Mapping[str, Any]) -> dict[str, Any]:
    scope = metadata.get("scope_restoration")
    if not isinstance(scope, Mapping):
        return {"state": "missing"}
    return {
        "state": scope.get("state"),
        "run_selected_database_label": scope.get("run_selected_database_label"),
        "pre_run_selected_database_labels": scope.get("pre_run_selected_database_labels"),
        "post_run_selected_database_labels": scope.get("post_run_selected_database_labels"),
        "restoration_required": scope.get("restoration_required"),
        "restoration_verified": scope.get("restoration_verified"),
    }


def _control_summary(strategy: Mapping[str, Any], executed_query: str) -> dict[str, Any]:
    """Project compact source-echoed controls retained by the output contract."""
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    sort = strategy.get("sort")
    sort = sort if isinstance(sort, Mapping) else {}
    sort_value = sort.get("value")
    sort_value = sort_value if isinstance(sort_value, Mapping) else {}

    def observed_value(name: str) -> Any:
        value = limits.get(name)
        if isinstance(value, Mapping) and value.get("state") == "applied":
            return value.get("value")
        return None

    return {
        "executed_query_sha256": sha256_bytes(executed_query.encode("utf-8")),
        "source_year_clause_readback": "YR(2011-2026)" in executed_query,
        "language_clause_readback": "LA(English)" in executed_query,
        "oldest_first_readback": (
            sort.get("state") == "applied"
            and sort_value.get("value") == "DateAsc"
            and sort_value.get("label") == "Oldest first"
        ),
        "full_text": observed_value("full_text"),
        "exclude_duplicates": observed_value("exclude_duplicates"),
        "spelling_variants": observed_value("spelling_variants"),
        "form_variants": observed_value("form_variants"),
        "show_variants": observed_value("show_variants"),
    }


def _strict_success_entry(path: Path, event: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one immutable adapter artifact and project safe pilot evidence."""
    payload = load_json(path)
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError(f"{path.name}: missing output metadata.")
    query = event["query"]
    if payload.get("schema_version") != "academic-search-result/v1":
        raise RuntimeError(f"{path.name}: wrong result schema.")
    if payload.get("source") != SOURCE_LABEL or payload.get("requested_query") != query:
        raise RuntimeError(f"{path.name}: source or raw query differs from the plan.")
    executed_query = payload.get("executed_query")
    if not isinstance(executed_query, str) or "YR(2011-2026)" not in executed_query or "LA(English)" not in executed_query:
        raise RuntimeError(f"{path.name}: source did not read back YR(2011-2026) and LA(English).")
    total = payload.get("total")
    rows = payload.get("results")
    if isinstance(total, bool) or not isinstance(total, int) or not 0 <= total <= MAX_COMPLETE_RESULTS:
        raise RuntimeError(f"{path.name}: total is outside the strict complete boundary.")
    if not isinstance(rows, list) or len(rows) != total:
        raise RuntimeError(f"{path.name}: rows do not reconcile to the source total.")
    # The marker-gated public artifact deliberately retains compact PRISMA-S
    # evidence rather than the adapter's private pass internals.  A success
    # marker is published only after the adapter has accepted its strict
    # two-pass document-ID contract.
    if (
        metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("count_only") is not False
        or metadata.get("merge_eligible") is not True
    ):
        raise RuntimeError(f"{path.name}: compact strict-complete status differs.")
    ids: list[str] = []
    for rank, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise RuntimeError(f"{path.name}: result {rank} is not an object.")
        document_id = row.get("paperId")
        if not isinstance(document_id, str) or not document_id.isascii() or not document_id.isdigit():
            raise RuntimeError(f"{path.name}: result {rank} lacks a numeric PQDT document ID.")
        if row.get("rank") != rank:
            raise RuntimeError(f"{path.name}: result ranks are not source order.")
        if row.get("url") != f"https://www.proquest.com/pqdtglobal/docview/{document_id}":
            raise RuntimeError(f"{path.name}: result {rank} lacks the canonical PQDT document route.")
        ids.append(document_id)
    if len(set(ids)) != len(ids):
        raise RuntimeError(f"{path.name}: strict capture retained duplicate document IDs.")
    digest = ordered_id_digest(ids)
    marker = path.with_name(f".{path.name}.PQDT_COMMIT.json")
    marker_payload = load_json(marker)
    normalized = marker_payload.get("normalized_json")
    if not isinstance(normalized, dict) or normalized.get("sha256") != sha256_file(path):
        raise RuntimeError(f"{path.name}: marker does not bind the immutable strict artifact.")
    receipt = metadata.get("prisma_search_run")
    if not isinstance(receipt, dict):
        raise RuntimeError(f"{path.name}: missing PRISMA-S receipt.")
    strategy = receipt.get("strategy")
    counts = receipt.get("staged_counts")
    if not isinstance(strategy, Mapping) or not isinstance(counts, Mapping):
        raise RuntimeError(f"{path.name}: compact receipt lacks source strategy/counts.")
    if (
        strategy.get("executed_query") != executed_query
        or strategy.get("search_scope") != "PQDT Global"
        or counts.get("source_reported_total") != total
        or counts.get("records_exported") != total
        or counts.get("source_reported_total_exact") is not True
        or receipt.get("completion_status") != "complete"
    ):
        raise RuntimeError(f"{path.name}: compact strict receipt does not reconcile source scope/counts.")
    # The source label is retained as a compact readback.  The adapter's
    # marker-bound scope guard snapshots, selects exactly one allowed PQDT
    # label, and restores it; pre/post labels are intentionally not serialized.
    scope = {
        "state": "source_echo_and_marker_bound",
        "source_scope": strategy.get("search_scope"),
        "selected_database_label": "not_serialized_in_compact_output",
        "restoration": "adapter_scope_guard_completed_before_marker_publication",
    }
    controls = _control_summary(strategy, executed_query)
    if controls != {
        **controls,
        "source_year_clause_readback": True,
        "language_clause_readback": True,
        "oldest_first_readback": True,
        "full_text": False,
        "exclude_duplicates": False,
        "spelling_variants": False,
        "form_variants": False,
        "show_variants": False,
    }:
        raise RuntimeError(f"{path.name}: frozen controls were not read back exactly.")
    coverage = receipt.get("coverage")
    descriptor = receipt.get("source_descriptor")
    if (
        receipt.get("review_id") != event.get("review_id")
        or receipt.get("strategy_reference") != event.get("strategy_reference")
        or receipt.get("phase") != "pilot_complete"
        or not isinstance(coverage, dict)
        or coverage.get("coverage_scope") != "partition"
        or coverage.get("partition_id") != event.get("partition_id")
        or not isinstance(descriptor, dict)
        or descriptor.get("source_id") != SOURCE_ID
    ):
        raise RuntimeError(f"{path.name}: PRISMA-S event binding differs from the plan.")
    return {
        "partition_id": event["partition_id"],
        "event_id": event["event_id"],
        "cell_id": f"{event['partition_id']}-full-expression",
        "artifact": path.name,
        "artifact_sha256": sha256_file(path),
        "marker": marker.name,
        "marker_sha256": sha256_file(marker),
        "source_native_query_sha256": sha256_bytes(query.encode("utf-8")),
        "source_native_query_characters": len(query),
        "lossless_cell_split": False,
        "source_total": total,
        "stable_ids_in_source_order": ids,
        "ordered_document_ids_sha256": digest,
        "two_pass_stable_id_reconciliation": True,
        "scope_readback": scope,
        "control_readback": controls,
        "status": "complete",
    }


def _failure_entry(path: Path, event: Mapping[str, Any], return_code: int | None) -> dict[str, Any]:
    """Keep a strict failure explicit and null-total; never turn it into zero."""
    payload = load_json(path)
    total = payload.get("total")
    if total is not None:
        raise RuntimeError(f"{path.name}: strict failure did not preserve a null total.")
    metadata = payload.get("output_metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    return {
        "partition_id": event["partition_id"],
        "event_id": event["event_id"],
        "cell_id": f"{event['partition_id']}-full-expression",
        "artifact": path.name,
        "artifact_sha256": sha256_file(path),
        "source_native_query_sha256": sha256_bytes(event["query"].encode("utf-8")),
        "source_native_query_characters": len(event["query"]),
        "lossless_cell_split": False,
        "source_total": None,
        "stable_ids_in_source_order": None,
        "two_pass_stable_id_reconciliation": False,
        "scope_readback": _scope_summary(metadata),
        "control_readback": {
            "executed_query_sha256": (
                sha256_bytes(payload["executed_query"].encode("utf-8"))
                if isinstance(payload.get("executed_query"), str)
                else None
            )
        },
        "status": "strict_failure",
        "return_code": return_code,
    }


def _missing_failure_entry(event: Mapping[str, Any], return_code: int | None) -> dict[str, Any]:
    path = SEARCH_DIR / f"{event['partition_id']}.strict-complete.NON_MERGEABLE_FAILURE.json"
    write_new_json(
        path,
        {
            "schema_version": "pqdt-global-pilot-003-source-failure/v1",
            "source": SOURCE_LABEL,
            "total": None,
            "results": [],
            "do_not_merge": True,
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "failure": {
                "return_code": return_code,
                "message": "The strict adapter returned no artifact; no replacement query was run.",
            },
        },
    )
    return {
        "partition_id": event["partition_id"],
        "event_id": event["event_id"],
        "cell_id": f"{event['partition_id']}-full-expression",
        "artifact": path.name,
        "artifact_sha256": sha256_file(path),
        "source_native_query_sha256": sha256_bytes(event["query"].encode("utf-8")),
        "source_native_query_characters": len(event["query"]),
        "lossless_cell_split": False,
        "source_total": None,
        "stable_ids_in_source_order": None,
        "two_pass_stable_id_reconciliation": False,
        "scope_readback": {"state": "not_available"},
        "control_readback": {},
        "status": "strict_failure",
        "return_code": return_code,
    }


def deterministic_run_id(partition: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"slr1-pqdt-pilot-003/{partition}/full"))


def run_event(event: Mapping[str, Any], *, resume: bool) -> dict[str, Any]:
    partition = str(event["partition_id"])
    output = SEARCH_DIR / f"{partition}.json"
    if output.exists():
        if not resume:
            raise RuntimeError(f"Refusing to overwrite existing {output}.")
        payload = load_json(output)
        metadata = payload.get("output_metadata")
        if isinstance(metadata, dict) and metadata.get("status") == "success":
            return _strict_success_entry(output, event)
        return _failure_entry(output, event, None)
    if not ADAPTER.is_file():
        raise RuntimeError(f"PQDT adapter is unavailable: {ADAPTER}")
    command = [
        "uv", "run", str(ADAPTER), "--query", str(event["query"]),
        "--limit", str(MAX_COMPLETE_RESULTS), "--max-pages", str(MAX_PAGES),
        "--timeout", "90", "--require-complete", "--output-path", str(output),
        "--prisma-run-id", deterministic_run_id(partition),
        "--prisma-review-id", str(event["review_id"]),
        "--prisma-strategy-reference", str(event["strategy_reference"]),
        "--prisma-strategy-version", str(event["strategy_version"]),
        "--prisma-phase", "pilot_complete",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", partition,
        "--prisma-partition-label", f"PQDT Global Pilot 003 {partition}",
        "--prisma-partition-description", "Full literal PQDT Global pilot diagnostic cell; not a final search.",
        *FROZEN_ADAPTER_ARGS,
    ]
    print(f"Running PQDT Global Pilot 003 {partition} ({len(event['query'])} query characters).", flush=True)
    completed = subprocess.run(command, check=False)
    if not output.exists():
        return _missing_failure_entry(event, completed.returncode)
    payload = load_json(output)
    metadata = payload.get("output_metadata")
    if completed.returncode == 0 and isinstance(metadata, dict) and metadata.get("status") == "success":
        return _strict_success_entry(output, event)
    return _failure_entry(output, event, completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-plan", action="store_true", help="Validate only; do not open a browser.")
    parser.add_argument("--resume", action="store_true", help="Read existing immutable cell artifacts instead of rerunning them.")
    parser.add_argument("--allow-direct-browser", action="store_true", help="Testing only; normal runs require run_with_browser.py.")
    args = parser.parse_args()
    events = load_plan()
    if args.check_plan:
        print(json.dumps({"status": "ok", "partitions": [event["partition_id"] for event in events]}, indent=2))
        return 0
    if not args.allow_direct_browser and os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise SystemExit("Run this source workflow through the shared browser runner.")
    ledger_path = SEARCH_DIR / "event-execution-ledger.json"
    if ledger_path.exists():
        raise RuntimeError(f"Refusing to overwrite existing {ledger_path}.")
    cells: list[dict[str, Any]] = []
    for event in events:
        try:
            cells.append(run_event(event, resume=args.resume))
        except Exception as error:  # preserve the other independently scoped events
            partition = str(event["partition_id"])
            failure_path = SEARCH_DIR / f"{partition}.strict-complete.NON_MERGEABLE_FAILURE.json"
            if failure_path.exists():
                cells.append(_failure_entry(failure_path, event, None))
                continue
            raise RuntimeError(f"{partition}: runner could not preserve a strict failure") from error
    complete = [cell for cell in cells if cell["status"] == "complete"]
    failures = [cell for cell in cells if cell["status"] != "complete"]
    write_new_json(
        ledger_path,
        {
            "schema_version": "pqdt-global-pilot-003-event-execution-ledger/v1",
            "source": SOURCE_LABEL,
            "source_id": SOURCE_ID,
            "pilot": "003",
            "do_not_merge": True,
            "purpose": "Pilot-only strict rendered-record diagnostic; no final search is created.",
            "event_plan": {"artifact": PLAN_PATH.name, "sha256": sha256_file(PLAN_PATH)},
            "source_window": {
                "year_start": SOURCE_YEAR_START,
                "year_end": SOURCE_YEAR_END,
                "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
                "precision": "PQDT YR is year precision; 2026 records remain for cutoff screening.",
            },
            "query_limit": MAX_QUERY_CHARACTERS,
            "complete_result_boundary": MAX_COMPLETE_RESULTS,
            "cells": cells,
            "complete_cell_count": len(complete),
            "strict_failure_count": len(failures),
        },
    )
    print(json.dumps({
        "complete_cells": len(complete),
        "strict_failures": [cell["partition_id"] for cell in failures],
        "totals": {cell["partition_id"]: cell["source_total"] for cell in cells},
    }, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
