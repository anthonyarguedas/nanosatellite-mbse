#!/usr/bin/env python3
"""Offline integrity checks for the paired Compendex/Inspec Pilot 003 bundle."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

from build_assessment import (  # type: ignore[import-not-found]
    OVER_100_PATH,
    RECONCILIATION_PATH,
    SOURCE_TO_DATABASE,
    build_payloads,
)
from preflight import (  # type: ignore[import-not-found]
    DEFAULT_OUTPUT as PREFLIGHT_PATH,
    PILOT_DIR,
    SCHEDULE_IDS,
    build_payload,
    raw_query,
    validate_partition,
)
from run_pilot import (  # type: ignore[import-not-found]
    DEFAULT_LIMIT,
    DEFAULT_MAX_PAGES,
    DEFAULT_PRIVATE_RIS_DIR,
    DEFAULT_TIMEOUT,
    adapter_arguments,
    validate_adapter_preflight,
)

SEARCH_DIR = PILOT_DIR / "searches"
SLR1_ROOT = Path(__file__).resolve().parents[2]
FIXED_ENGINE = Path.home() / "agent-tools/internet/skills/browser/scripts/_engineering_village_search.py"
DOCS = (
    PILOT_DIR / "pilot.md",
    SLR1_ROOT / "source-specific" / "inspec" / "pilots" / "003" / "pilot.md",
    SLR1_ROOT / "source-specific" / "compendex" / "source-specific-guidelines.md",
    SLR1_ROOT / "source-specific" / "inspec" / "source-specific-guidelines.md",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def fixed_engine_module():
    spec = importlib.util.spec_from_file_location("slr1_fixed_ev_engine_validator", FIXED_ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Fixed Engineering Village validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def local_markdown_targets(markdown: Path, errors: list[str]) -> None:
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        require((markdown.parent / target).resolve().exists(), f"{markdown}: broken local link {target}", errors)


def check_success(partition_id: str, engine: Any, errors: list[str]) -> None:
    json_path = SEARCH_DIR / f"{partition_id}.json"
    csv_path = SEARCH_DIR / f"{partition_id}.csv"
    marker = SEARCH_DIR / f".{partition_id}.json.commit.json"
    require(json_path.is_file() and csv_path.is_file() and marker.is_file(), f"{partition_id}: missing strict JSON/CSV/marker", errors)
    if not (json_path.is_file() and csv_path.is_file() and marker.is_file()):
        return
    require(engine.committed_result_pair_is_usable(json_path, csv_path), f"{partition_id}: fixed adapter rejects marker-gated pair", errors)
    data = load(json_path)
    metadata = data.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {}) if isinstance(metadata, dict) else {}
    strategy = run.get("strategy", {}) if isinstance(run, dict) else {}
    staged = run.get("staged_counts", {}) if isinstance(run, dict) else {}
    require(data.get("schema_version") == "academic-search-result/v1", f"{partition_id}: unexpected output schema", errors)
    require(strategy.get("requested_query") == raw_query(partition_id), f"{partition_id}: raw query changed", errors)
    require("*" not in str(strategy.get("requested_query", "")) and "?" not in str(strategy.get("requested_query", "")), f"{partition_id}: wildcard entered query", errors)
    require(strategy.get("databases") == ["compendex", "inspec"], f"{partition_id}: database pair changed", errors)
    require(strategy.get("query_fields") == ["ALL", "LA"], f"{partition_id}: Expert fields are not ALL plus raw LA", errors)
    require(strategy.get("query_syntax", {}).get("autostemming") == "off", f"{partition_id}: autostemming was not off", errors)
    require(strategy.get("limits", {}).get("published", {}).get("value") == {"start": "2011", "end": "2026"}, f"{partition_id}: Published bounds changed", errors)
    require(strategy.get("limits", {}).get("updates", {}).get("state") == "not_applied", f"{partition_id}: Updates control changed", errors)
    require(strategy.get("limits", {}).get("document_type_filter") is None and strategy.get("limits", {}).get("result_facets") == [], f"{partition_id}: lossy DT/Open Access filter present", errors)
    require(strategy.get("sort", {}).get("value") == {"label": "Date (Oldest)", "value": "sort=yr&sortdir=up"}, f"{partition_id}: Date (Oldest) changed", errors)
    require(run.get("completion_status") == "complete" and run.get("report_ready") is True, f"{partition_id}: strict run not complete", errors)
    require(staged.get("source_reported_total_exact") is True, f"{partition_id}: source total is not exact", errors)
    require(staged.get("source_reported_total") == data.get("total") == staged.get("records_exported"), f"{partition_id}: total/export reconciliation failed", errors)
    results = data.get("results", [])
    require(isinstance(results, list) and len(results) == data.get("total"), f"{partition_id}: retained record count differs", errors)
    observed = {"compendex": [], "inspec": []}
    if isinstance(results, list):
        for record in results:
            database = SOURCE_TO_DATABASE.get(record.get("source")) if isinstance(record, dict) else None
            accession = record.get("paperId") if isinstance(record, dict) else None
            require(database is not None and isinstance(accession, str) and bool(accession.strip()), f"{partition_id}: missing database-scoped accession", errors)
            if database and isinstance(accession, str) and accession.strip():
                observed[database].append(accession.strip())
    expected = staged.get("records_exported_by_database")
    require(expected == {database: len(ids) for database, ids in observed.items()}, f"{partition_id}: separate database totals disagree", errors)
    for database, ids in observed.items():
        require(len(ids) == len(set(ids)), f"{partition_id}: duplicate accession in {database} projection", errors)
    require(metadata.get("publication_state") == "pending_nonmergeable" and metadata.get("merge_eligible") is True, f"{partition_id}: missing marker-gated publication state", errors)

    # This validates the exact command shape used before browser work, without
    # making another source request.
    try:
        adapter = validate_adapter_preflight(
            adapter_arguments(
                partition_id,
                native_export_dir=DEFAULT_PRIVATE_RIS_DIR / partition_id,
                limit=DEFAULT_LIMIT,
                max_pages=DEFAULT_MAX_PAGES,
                timeout=DEFAULT_TIMEOUT,
            )
        )
        require(adapter.get("databases") == ["compendex", "inspec"], f"{partition_id}: paired adapter preflight changed", errors)
    except Exception as error:  # noqa: BLE001
        errors.append(f"{partition_id}: offline fixed-adapter validation failed: {error}")

    try:
        with csv_path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        require(len(rows) == data.get("total"), f"{partition_id}: CSV record count differs", errors)
    except Exception as error:  # noqa: BLE001
        errors.append(f"{partition_id}: unreadable CSV: {error}")


def check_failure(partition_id: str, errors: list[str]) -> None:
    path = SEARCH_DIR / f"{partition_id}.NON_MERGEABLE_FAILURE.json"
    require(path.is_file(), f"{partition_id}: missing explicit null-failure receipt", errors)
    if not path.is_file():
        return
    data = load(path)
    request = data.get("request", {})
    execution = data.get("execution", {})
    require(data.get("do_not_merge") is True and data.get("merge_eligible") is False, f"{partition_id}: failure receipt can be merged", errors)
    require(request.get("query_requested_raw") == raw_query(partition_id), f"{partition_id}: failure query changed", errors)
    require(request.get("published_year_bounds") == {"start": 2011, "end": 2026}, f"{partition_id}: failure year bounds changed", errors)
    require(request.get("language_raw_clause") == "(English WN LA)", f"{partition_id}: failure language clause changed", errors)
    require(request.get("wildcard") == "not_used_or_accepted", f"{partition_id}: failure wildcard state changed", errors)
    require(execution.get("source_total") is None and execution.get("compendex_accession_ids") is None and execution.get("inspec_accession_ids") is None and execution.get("native_ris_capture") is None, f"{partition_id}: failure receipt infers a partial capture", errors)
    require(isinstance(execution.get("private_partial_capture_disposition"), str), f"{partition_id}: failure receipt does not quarantine private partial capture", errors)
    require(execution.get("public_output_presence") == {"json": False, "csv": False, "terminal_marker": False}, f"{partition_id}: failure receipt has an unexpected public output", errors)


def main() -> int:
    errors: list[str] = []
    # Every JSON artifact must parse before any individual assertion is trusted.
    for path in sorted(SEARCH_DIR.glob("*.json")):
        try:
            load(path)
        except Exception as error:  # noqa: BLE001
            errors.append(f"{path.name}: invalid JSON: {error}")

    try:
        require(load(PREFLIGHT_PATH) == build_payload(), "preflight.json differs from central schedule", errors)
        for partition_id in SCHEDULE_IDS:
            validate_partition(partition_id)
    except Exception as error:  # noqa: BLE001
        errors.append(f"membership validation failed: {error}")

    try:
        engine = fixed_engine_module()
    except Exception as error:  # noqa: BLE001
        errors.append(f"fixed adapter cannot be loaded for marker validation: {error}")
        engine = None
    for partition_id in SCHEDULE_IDS:
        success = SEARCH_DIR / f"{partition_id}.json"
        failure = SEARCH_DIR / f"{partition_id}.NON_MERGEABLE_FAILURE.json"
        require(success.exists() != failure.exists(), f"{partition_id}: need exactly one success or explicit failure artifact", errors)
        if success.exists() and engine is not None:
            check_success(partition_id, engine, errors)
        elif failure.exists():
            check_failure(partition_id, errors)

    try:
        expected_reconciliation, expected_over_100 = build_payloads()
        require(load(RECONCILIATION_PATH) == expected_reconciliation, "reconciliation.json is stale or inconsistent", errors)
        require(load(OVER_100_PATH) == expected_over_100, "over-100 investigation is stale or inconsistent", errors)
        for investigation in expected_over_100["investigations"]:
            require(investigation["threshold_exceeded"] is True, f"{investigation['database']}: >100 union was not investigated", errors)
            require(len(investigation["record_ledger"]) == investigation["unique_database_scoped_accessions"], f"{investigation['database']}: >100 record ledger is incomplete", errors)
    except Exception as error:  # noqa: BLE001
        errors.append(f"assessment validation failed: {error}")

    for markdown in DOCS:
        require(markdown.is_file(), f"missing documentation: {markdown}", errors)
        if markdown.is_file():
            local_markdown_targets(markdown, errors)
    for guideline in DOCS[2:]:
        if guideline.is_file():
            text = guideline.read_text(encoding="utf-8")
            require("Last pilot saved in commit: NA" in text, f"{guideline}: completion state changed", errors)
            require("Final searches saved in commit: NA" in text, f"{guideline}: final-search completion state changed", errors)
    inspec_pilot_dir = SLR1_ROOT / "source-specific" / "inspec" / "pilots" / "003"
    require(not any(inspec_pilot_dir.glob("*.json")), "Inspec Pilot 003 duplicates the paired Compendex event artifacts", errors)
    for final_dir in (
        SLR1_ROOT / "source-specific" / "compendex" / "final-searches",
        SLR1_ROOT / "source-specific" / "inspec" / "final-searches",
    ):
        require(sorted(path.name for path in final_dir.iterdir()) == [".gitkeep"], f"{final_dir}: Pilot 003 wrote a final search", errors)

    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(json.dumps({"status": "ok", "partitions": list(SCHEDULE_IDS), "successes": 8, "explicit_null_failures": ["B2"], "over_100_unions": {"compendex": 206, "inspec": 116}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
