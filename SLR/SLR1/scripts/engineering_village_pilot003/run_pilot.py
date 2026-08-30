#!/usr/bin/env python3
"""Run one strict paired Engineering Village Pilot 003 event per partition.

The fixed browser integration is invoked as an external, read-only dependency.
This runner owns only the review-side preflight and explicit null-failure
receipts; it never substitutes a partial result for a failed strict pass.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from preflight import (  # type: ignore[import-not-found]
    DEFAULT_OUTPUT as PREFLIGHT_PATH,
    PILOT_DIR,
    SLR1_ROOT,
    SCHEDULE_IDS,
    build_payload,
    raw_query,
)

SEARCH_DIR = PILOT_DIR / "searches"
FIXED_BROWSER_SCRIPTS = Path("/Users/antho/agent-tools/internet/skills/browser/scripts")
BROWSER_RUNNER = FIXED_BROWSER_SCRIPTS / "run_with_browser.py"
PAIRED_ADAPTER = FIXED_BROWSER_SCRIPTS / "search_compendex_inspec.py"
DEFAULT_PRIVATE_RIS_DIR = Path.home() / ".cache" / "slr1-engineering-village-pilot003-ris"
DEFAULT_LIMIT = 5_000
DEFAULT_MAX_PAGES = 200
DEFAULT_TIMEOUT = 120


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def marker_path(json_path: Path) -> Path:
    return json_path.with_name(f".{json_path.name}.commit.json")


def failure_path(partition_id: str) -> Path:
    return SEARCH_DIR / f"{partition_id}.NON_MERGEABLE_FAILURE.json"


def output_paths(partition_id: str) -> tuple[Path, Path, Path, Path]:
    json_path = SEARCH_DIR / f"{partition_id}.json"
    csv_path = SEARCH_DIR / f"{partition_id}.csv"
    return json_path, csv_path, marker_path(json_path), failure_path(partition_id)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_fixed_adapter():
    """Load only the installed fixed adapter for offline CLI validation."""
    spec = importlib.util.spec_from_file_location("slr1_fixed_ev_adapter", PAIRED_ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load fixed adapter: {PAIRED_ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def adapter_arguments(
    partition_id: str,
    *,
    native_export_dir: Path,
    limit: int,
    max_pages: int,
    timeout: int,
) -> list[str]:
    json_path, csv_path, _, _ = output_paths(partition_id)
    return [
        "--query",
        raw_query(partition_id),
        "--search-mode",
        "expert",
        "--year-start",
        "2011",
        "--year-end",
        "2026",
        "--limit",
        str(limit),
        "--max-pages",
        str(max_pages),
        "--timeout",
        str(timeout),
        "--require-complete",
        "--native-export-dir",
        str(native_export_dir),
        "--output-path",
        str(json_path),
        "--csv-output-path",
        str(csv_path),
        "--prisma-run-id",
        f"slr1-pilot-003-engineering-village-{partition_id}",
        "--prisma-review-id",
        "slr1",
        "--prisma-strategy-reference",
        "slr1-direct-query-schedule-v1",
        "--prisma-strategy-version",
        "8f5dc8e",
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition_id,
        "--prisma-partition-label",
        partition_id,
        "--prisma-partition-description",
        "One literal direct-query schedule partition in the paired Engineering Village pilot.",
    ]


def validate_adapter_preflight(arguments: list[str]) -> dict[str, Any]:
    """Parse and validate the exact CLI without browser or source work."""
    adapter = load_fixed_adapter()
    parser = adapter.build_paired_parser()
    args = parser.parse_args(arguments)
    observed_query = adapter.validate_paired_cli_args(args)
    if observed_query != args.query or tuple(args.databases) != ("compendex", "inspec"):
        raise RuntimeError("The fixed paired adapter did not preserve the exact paired request")
    if args.facets:
        raise RuntimeError("A document-type or Open Access facet entered the paired request")
    if args.controlled_terms or args.classifications:
        raise RuntimeError("A controlled-term supplement entered the free-text pilot")
    return {
        "adapter_id": adapter.ADAPTER_ID,
        "adapter_version": adapter.ADAPTER_VERSION,
        "databases": list(args.databases),
        "query_sha256": sha256_text(observed_query),
    }


def ensure_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    if path.stat().st_mode & 0o077:
        raise RuntimeError("The native RIS directory must be owner-only")


def validate_success_artifact(partition_id: str, adapter_info: dict[str, Any]) -> dict[str, Any]:
    """Check public marker and PRISMA provenance before using a strict result.

    Adapter version 10 deliberately projects private two-pass accession/RIS
    proof into a compact public JSON/CSV/marker envelope.  Its successful CLI
    return and terminal marker are therefore the public proof boundary; raw
    RIS and session-scoped pass manifests stay in the owner-only directory.
    """
    json_path, csv_path, commit_path, _ = output_paths(partition_id)
    if not all(path.is_file() for path in (json_path, csv_path, commit_path)):
        raise RuntimeError(f"{partition_id}: strict publication did not produce JSON, CSV, and terminal marker")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError(f"{partition_id}: output metadata is absent")
    run = metadata.get("prisma_search_run")
    if not isinstance(run, dict) or run.get("completion_status") != "complete" or run.get("report_ready") is not True:
        raise RuntimeError(f"{partition_id}: output lacks a complete source-run receipt")
    strategy = run.get("strategy")
    if not isinstance(strategy, dict) or strategy.get("requested_query") != raw_query(partition_id):
        raise RuntimeError(f"{partition_id}: source request differs from preflight")
    if strategy.get("databases") != ["compendex", "inspec"] or strategy.get("search_scope") != "Compendex & Inspec":
        raise RuntimeError(f"{partition_id}: output is not a paired Compendex+Inspec event")
    syntax = strategy.get("query_syntax")
    if not isinstance(syntax, dict) or syntax.get("autostemming") != "off":
        raise RuntimeError(f"{partition_id}: autostemming-off state was not observed")
    sort = strategy.get("sort")
    if not isinstance(sort, dict) or sort.get("value") != {"label": "Date (Oldest)", "value": "sort=yr&sortdir=up"}:
        raise RuntimeError(f"{partition_id}: Date (Oldest) was not observed")
    limits = strategy.get("limits")
    if not isinstance(limits, dict):
        raise RuntimeError(f"{partition_id}: source-control receipt is absent")
    if limits.get("published", {}).get("value") != {"start": "2011", "end": "2026"} or limits.get("updates", {}).get("state") != "not_applied":
        raise RuntimeError(f"{partition_id}: Published 2011-2026 / inactive Updates controls are not proven")
    if limits.get("document_type_filter") is not None or limits.get("result_facets") != []:
        raise RuntimeError(f"{partition_id}: a document-type or Open Access filter was applied")
    executed_query = strategy.get("executed_query")
    if not isinstance(executed_query, str) or " WN DT" in executed_query or " WN ACT" in executed_query:
        raise RuntimeError(f"{partition_id}: a DT or Open Access Expert suffix was applied")
    if payload.get("total") != len(payload.get("results", [])):
        raise RuntimeError(f"{partition_id}: strict source total does not reconcile to retained records")
    staged = run.get("staged_counts")
    if not isinstance(staged, dict) or staged.get("source_reported_total") != payload.get("total") or staged.get("records_exported") != payload.get("total"):
        raise RuntimeError(f"{partition_id}: source total does not reconcile to exported records")
    database_counts = staged.get("records_exported_by_database")
    if not isinstance(database_counts, dict) or set(database_counts) != {"compendex", "inspec"} or sum(database_counts.values()) != payload.get("total"):
        raise RuntimeError(f"{partition_id}: separate database counts are not reconciled")
    if metadata.get("publication_state") != "pending_nonmergeable" or metadata.get("merge_eligible") is not True:
        raise RuntimeError(f"{partition_id}: output lacks marker-gated publication state")
    return {
        "partition_id": partition_id,
        "adapter": adapter_info,
        "source_total": payload["total"],
        "source_entries_by_database": database_counts,
        "strict_capture": "adapter two-pass proof accepted before compact marker-gated publication",
    }


def safe_failure_message(stdout: str, stderr: str) -> str:
    """Keep a bounded explanation while excluding portal/session values."""
    text = "\n".join(item for item in (stderr, stdout) if item)
    candidates = [line.strip() for line in text.splitlines() if line.strip()]
    diagnostic = next(
        (
            line
            for line in reversed(candidates)
            if any(token in line.casefold() for token in ("error", "failed", "failure", "refus", "strict"))
        ),
        None,
    )
    message = diagnostic or "Fixed strict adapter exited without a safely retainable diagnostic."
    message = re.sub(r"https?://[^\s]+", "[portal-url-redacted]", message)
    message = re.sub(r"/Users/[^\s]+", "[local-path-redacted]", message)
    message = re.sub(r"SEARCHID=[^\s&]+", "SEARCHID=[redacted]", message, flags=re.I)
    return message[:500]


def write_failure_receipt(
    partition_id: str,
    *,
    adapter_info: dict[str, Any],
    started_at: str,
    finished_at: str,
    returncode: int,
    stdout: str,
    stderr: str,
    limit: int,
    max_pages: int,
    private_first_pass_observed: bool,
) -> Path:
    json_path, csv_path, commit_path, destination = output_paths(partition_id)
    if destination.exists():
        raise RuntimeError(f"Refusing to overwrite explicit failure receipt: {destination}")
    query = raw_query(partition_id)
    payload = {
        "schema_version": "slr1-engineering-village-pilot003-strict-null-failure/v1",
        "pilot": "003",
        "partition_id": partition_id,
        "source": "Compendex and Inspec (Engineering Village)",
        "selected_databases": ["compendex", "inspec"],
        "merge_eligible": False,
        "do_not_merge": True,
        "request": {
            "query_requested_raw": query,
            "query_sha256": sha256_text(query),
            "published_year_bounds": {"start": 2011, "end": 2026},
            "language_raw_clause": "(English WN LA)",
            "autostemming": "off_required",
            "sort": "Date (Oldest)_required",
            "document_type_filter": "not_applied",
            "open_access_filter": "not_applied",
            "controlled_vocabulary_supplement": "not_requested",
            "wildcard": "not_used_or_accepted",
            "strict_capacity": {"limit": limit, "max_pages": max_pages},
        },
        "execution": {
            "adapter": adapter_info,
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "exit_code": returncode,
            "source_submission_state": (
                "private_first_pass_started_but_strict_completion_failed"
                if private_first_pass_observed
                else "unknown_not_inferred_after_strict_adapter_failure"
            ),
            "source_total": None,
            "compendex_accession_ids": None,
            "inspec_accession_ids": None,
            "native_ris_capture": None,
            "private_partial_capture_disposition": (
                "Private first-pass material is unusable because strict two-pass reconciliation did not complete; no partial count, accession, hash, or manifest detail is exposed or used."
                if private_first_pass_observed
                else "No accepted private capture exists; strict completion did not produce a usable source result."
            ),
            "public_output_presence": {
                "json": json_path.exists(),
                "csv": csv_path.exists(),
                "terminal_marker": commit_path.exists(),
            },
        },
        "failure": {
            "message": safe_failure_message(stdout, stderr),
            "stdout_sha256": sha256_text(stdout),
            "stderr_sha256": sha256_text(stderr),
            "disposition": "Explicit null failure retained; no count, accession list, partial RIS capture, or source-zero inference is used.",
        },
    }
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return destination


def require_exact_preflight() -> None:
    existing = json.loads(PREFLIGHT_PATH.read_text(encoding="utf-8"))
    if existing != build_payload():
        raise RuntimeError("The saved preflight does not match the current pilot_schedule concepts")


def run_partition(
    partition_id: str,
    *,
    native_export_root: Path,
    limit: int,
    max_pages: int,
    timeout: int,
) -> dict[str, Any]:
    json_path, csv_path, commit_path, failed = output_paths(partition_id)
    if any(path.exists() for path in (json_path, csv_path, commit_path, failed)):
        raise RuntimeError(f"{partition_id}: refusing to overwrite an existing pilot artifact")
    if not BROWSER_RUNNER.is_file() or not PAIRED_ADAPTER.is_file():
        raise RuntimeError("The fixed read-only browser integration is unavailable")

    native_event_dir = native_export_root / partition_id
    ensure_private_directory(native_event_dir)
    arguments = adapter_arguments(
        partition_id,
        native_export_dir=native_event_dir,
        limit=limit,
        max_pages=max_pages,
        timeout=timeout,
    )
    adapter_info = validate_adapter_preflight(arguments)
    command = [
        "caffeinate",
        "-dims",
        "uv",
        "run",
        str(BROWSER_RUNNER),
        "--",
        "uv",
        "run",
        str(PAIRED_ADAPTER),
        *arguments,
    ]
    started_at = utc_now()
    completed = subprocess.run(
        command,
        cwd=SLR1_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    finished_at = utc_now()
    if completed.returncode == 0:
        outcome = validate_success_artifact(partition_id, adapter_info)
        outcome["outcome"] = "strict_two_pass_success"
        return outcome
    receipt = write_failure_receipt(
        partition_id,
        adapter_info=adapter_info,
        started_at=started_at,
        finished_at=finished_at,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        limit=limit,
        max_pages=max_pages,
        private_first_pass_observed=any(native_event_dir.rglob("*.ris")),
    )
    return {
        "partition_id": partition_id,
        "outcome": "explicit_strict_null_failure",
        "failure_receipt": receipt.name,
        "exit_code": completed.returncode,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", choices=SCHEDULE_IDS, action="append")
    parser.add_argument("--native-export-dir", type=Path, default=DEFAULT_PRIVATE_RIS_DIR)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--verify-existing",
        action="store_true",
        help="Validate existing strict output(s) without opening a browser or submitting a query.",
    )
    args = parser.parse_args()
    if args.limit < 1 or args.max_pages < 1 or args.timeout < 1:
        raise SystemExit("limit, max-pages, and timeout must be positive")
    require_exact_preflight()
    ensure_private_directory(args.native_export_dir.expanduser())
    requested = tuple(args.partition or SCHEDULE_IDS)
    outcomes = []
    if args.verify_existing:
        for partition_id in requested:
            json_path, csv_path, commit_path, failed = output_paths(partition_id)
            if failed.exists():
                outcomes.append({"partition_id": partition_id, "outcome": "explicit_strict_null_failure", "failure_receipt": failed.name})
                continue
            if not all(path.is_file() for path in (json_path, csv_path, commit_path)):
                raise RuntimeError(f"{partition_id}: no complete strict output is available to verify")
            native_event_dir = args.native_export_dir.expanduser() / partition_id
            adapter_info = validate_adapter_preflight(
                adapter_arguments(
                    partition_id,
                    native_export_dir=native_event_dir,
                    limit=args.limit,
                    max_pages=args.max_pages,
                    timeout=args.timeout,
                )
            )
            outcome = validate_success_artifact(partition_id, adapter_info)
            outcome["outcome"] = "strict_two_pass_success"
            outcomes.append(outcome)
    else:
        for partition_id in requested:
            outcomes.append(
                run_partition(
                    partition_id,
                    native_export_root=args.native_export_dir.expanduser(),
                    limit=args.limit,
                    max_pages=args.max_pages,
                    timeout=args.timeout,
                )
            )
    print(json.dumps({"pilot": "003", "outcomes": outcomes}, indent=2))
    return 0 if all(item["outcome"] == "strict_two_pass_success" for item in outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
