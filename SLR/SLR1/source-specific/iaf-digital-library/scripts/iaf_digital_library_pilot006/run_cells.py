#!/usr/bin/env python3
"""Run the predeclared strict IAF Pilot 006 live cells."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_plan import (
    DATE_END,
    DATE_START,
    DEFAULT_OUTPUT,
    PILOT_ROOT,
    PROTOCOL_COMMIT,
    queries,
    validate,
)

COLLECTOR = Path(__file__).with_name("collect_cell.py")
DEFAULT_SEARCH_DIR = PILOT_ROOT / "searches"
DEFAULT_RECEIPT = DEFAULT_SEARCH_DIR / "run-receipt.json"
REVIEW_ID = "slr1-iaf-pilot-006"
STRATEGY_REFERENCE = "slr1-iaf-all-partition-wildcard-population-v1"
STRATEGY_VERSION = PROTOCOL_COMMIT


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def artifact_path(search_dir: Path, partition_id: str, cell_id: str) -> Path:
    return search_dir / "cells" / partition_id / f"{cell_id}.json"


def ledger_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.identity-ledger.json")


def validate_marker(output: Path) -> bool:
    marker = marker_path(output)
    try:
        value = load_json(marker)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False
    normalized = value.get("normalized_json")
    return bool(
        value.get("schema") == "academic_search_output_commit_marker_v1"
        and isinstance(normalized, Mapping)
        and normalized.get("sha256") == file_sha256(output)
        and normalized.get("bytes") == output.stat().st_size
    )


def existing_status(output: Path, ledger: Path, query: str) -> str:
    try:
        artifact = load_json(output)
        identity = load_json(ledger)
    except FileNotFoundError:
        return "missing_artifact_or_ledger"
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return "unreadable_artifact_or_ledger"
    metadata = artifact.get("output_metadata")
    receipt = (
        metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    )
    compact = identity.get("compact_artifact")
    if not isinstance(metadata, Mapping) or not isinstance(receipt, Mapping):
        return "missing_completion_metadata"
    if not isinstance(compact, Mapping):
        return "missing_identity_binding"
    if (
        artifact.get("executed_query") != query
        or identity.get("schema_version")
        != "iaf-digital-library-pilot006-complete-identity-ledger/v1"
        or identity.get("query") != query
        or compact.get("file_name") != output.name
        or compact.get("sha256") != file_sha256(output)
        or compact.get("bytes") != output.stat().st_size
        or compact.get("commit_marker") != marker_path(output).name
        or not validate_marker(output)
    ):
        return "identity_or_query_mismatch"
    if (
        metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("count_only") is False
        and metadata.get("merge_eligible") is False
        and artifact.get("do_not_merge") is True
        and receipt.get("completion_status") == "complete"
        and identity.get("diagnostic_only") is True
        and identity.get("do_not_merge") is True
    ):
        return "complete_existing"
    return "noncomplete_existing"


def selected_partitions(values: Sequence[str] | None) -> tuple[str, ...]:
    if not values:
        return queries.SCHEDULE_IDS
    selected = tuple(dict.fromkeys(values))
    unknown = [value for value in selected if value not in queries.SCHEDULE_IDS]
    if unknown:
        raise ValueError("Unknown wildcard partition: " + ", ".join(unknown))
    return tuple(value for value in queries.SCHEDULE_IDS if value in selected)


def failure_path(
    search_dir: Path, partition_id: str, cell_id: str, attempt: int
) -> Path:
    return (
        search_dir
        / "failures"
        / partition_id
        / f"{cell_id}.attempt-{attempt:02d}.NON_MERGEABLE_FAILURE.json"
    )


def next_attempt(search_dir: Path, partition_id: str, cell_id: str) -> int:
    folder = search_dir / "failures" / partition_id
    existing = list(folder.glob(f"{cell_id}.attempt-*.NON_MERGEABLE_FAILURE.json"))
    return len(existing) + 1


def collector_command(
    *,
    query: str,
    output: Path,
    failure: Path,
    partition_id: str,
    cell_id: str,
    attempt: int,
    timeout_seconds: float,
    page_delay_seconds: float,
    retries: int,
    page_size: int,
) -> list[str]:
    return [
        "uv",
        "run",
        str(COLLECTOR),
        "--query",
        query,
        "--output-path",
        str(output),
        "--identity-ledger-path",
        str(ledger_path(output)),
        "--failure-path",
        str(failure),
        "--limit",
        "5000",
        "--max-pages",
        "100",
        "--page-size",
        str(page_size),
        "--passes",
        "2",
        "--timeout",
        str(timeout_seconds),
        "--page-delay-seconds",
        str(page_delay_seconds),
        "--retries",
        str(retries),
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--prisma-run-id",
        f"iaf-p006-{partition_id.lower()}-{cell_id}-attempt-{attempt:02d}",
        "--prisma-review-id",
        REVIEW_ID,
        "--prisma-strategy-reference",
        STRATEGY_REFERENCE,
        "--prisma-strategy-version",
        STRATEGY_VERSION,
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition_id,
        "--prisma-partition-label",
        partition_id,
        "--prisma-partition-description",
        f"Pilot 006 diagnostic lossless source cell for {partition_id}",
    ]


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def write_receipt(
    path: Path,
    *,
    plan_path: Path,
    pilot_root: Path,
    started: str,
    selected: Sequence[str],
    planned_cells: int,
    outcomes: Sequence[Mapping[str, Any]],
    status: str,
) -> None:
    failures = sorted(
        path
        for path in (pilot_root / "searches" / "failures").rglob(
            "*.NON_MERGEABLE_FAILURE.json"
        )
        if not path.name.startswith(".")
    )
    value = {
        "schema_version": "iaf-digital-library-pilot006-run-receipt/v1",
        "source": "IAF Digital Library",
        "pilot": "006",
        "status": status,
        "diagnostic_only": True,
        "do_not_merge": True,
        "started_at_utc": started,
        "updated_at_utc": now(),
        "event_plan": relative(plan_path, pilot_root),
        "selected_partitions": list(selected),
        "predeclared_cell_count": planned_cells,
        "completed_cell_count": sum(
            1
            for item in outcomes
            if item.get("status") in ("complete", "reused_existing")
        ),
        "outcome_count": len(outcomes),
        "source_attempt_count": sum(1 for item in outcomes if "attempt" in item),
        "reused_existing_cell_count": sum(
            1 for item in outcomes if item.get("status") == "reused_existing"
        ),
        "retained_failure_artifacts": [relative(item, pilot_root) for item in failures],
        "outcomes": list(outcomes),
    }
    if status == "complete":
        value["completed_at_utc"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--partition", action="append")
    parser.add_argument("--max-cells", type=int)
    parser.add_argument("--max-attempts-per-cell", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--process-timeout", type=float, default=360.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument(
        "--page-size", type=int, choices=(10, 50, 100, 200, 500), default=500
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.max_cells is not None and args.max_cells < 1:
        parser.error("--max-cells must be positive")
    if args.max_attempts_per_cell < 1:
        parser.error("--max-attempts-per-cell must be positive")
    if args.timeout <= 0 or args.process_timeout <= 0:
        parser.error("Timeouts must be positive")
    if args.page_delay_seconds < 0 or args.page_delay_seconds > 1:
        parser.error("Page delay must be between zero and one second")
    if args.retries < 0:
        parser.error("--retries cannot be negative")
    if not COLLECTOR.is_file():
        parser.error("The strict cell collector is unavailable")
    try:
        plan_path = args.plan.expanduser().resolve()
        plan = load_json(plan_path)
        plan_errors = validate(plan)
        if plan_errors:
            raise ValueError("; ".join(plan_errors))
        partitions = selected_partitions(args.partition)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    pilot_root = args.pilot_root.expanduser().resolve()
    search_dir = pilot_root / "searches"
    receipt_path = args.receipt.expanduser().resolve()
    planned_cells = sum(
        len(plan["partitions"][partition_id]["cells"]) for partition_id in partitions
    )
    started = now()
    outcomes: list[dict[str, Any]] = []
    handled_cells = 0
    stopped = False

    for partition_id in partitions:
        if stopped:
            break
        for cell in plan["partitions"][partition_id]["cells"]:
            if args.max_cells is not None and handled_cells >= args.max_cells:
                stopped = True
                break
            handled_cells += 1
            cell_id = cell["cell_id"]
            output = artifact_path(search_dir, partition_id, cell_id)
            ledger = ledger_path(output)
            if output.exists() or ledger.exists():
                status = existing_status(output, ledger, cell["query"])
                outcomes.append(
                    {
                        "partition_id": partition_id,
                        "cell_id": cell_id,
                        "status": "reused_existing"
                        if status == "complete_existing"
                        else status,
                        "output": relative(output, pilot_root),
                        "completed_at_utc": now(),
                    }
                )
                print(f"{partition_id}/{cell_id}: {status}", flush=True)
                if status != "complete_existing":
                    write_receipt(
                        receipt_path,
                        plan_path=plan_path,
                        pilot_root=pilot_root,
                        started=started,
                        selected=partitions,
                        planned_cells=planned_cells,
                        outcomes=outcomes,
                        status="stopped_on_existing_artifact_error",
                    )
                    return 1
                continue

            output.parent.mkdir(parents=True, exist_ok=True)
            completed_cell = False
            first_attempt = next_attempt(search_dir, partition_id, cell_id)
            for attempt_offset in range(args.max_attempts_per_cell):
                attempt = first_attempt + attempt_offset
                failure = failure_path(search_dir, partition_id, cell_id, attempt)
                failure.parent.mkdir(parents=True, exist_ok=True)
                command = collector_command(
                    query=cell["query"],
                    output=output,
                    failure=failure,
                    partition_id=partition_id,
                    cell_id=cell_id,
                    attempt=attempt,
                    timeout_seconds=args.timeout,
                    page_delay_seconds=args.page_delay_seconds,
                    retries=args.retries,
                    page_size=args.page_size,
                )
                if args.dry_run:
                    print(
                        json.dumps(
                            {
                                "partition": partition_id,
                                "cell": cell_id,
                                "command": command,
                            }
                        )
                    )
                    outcomes.append(
                        {
                            "partition_id": partition_id,
                            "cell_id": cell_id,
                            "attempt": attempt,
                            "status": "dry_run",
                        }
                    )
                    completed_cell = True
                    break
                print(
                    f"{partition_id}/{cell_id}: attempt {attempt} "
                    f"({handled_cells}/{planned_cells})",
                    flush=True,
                )
                event_started = now()
                environment = os.environ.copy()
                environment.setdefault("PYTHONUNBUFFERED", "1")
                try:
                    process = subprocess.run(
                        command,
                        cwd=Path.cwd(),
                        env=environment,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=args.process_timeout,
                    )
                    status = existing_status(output, ledger, cell["query"])
                    outcome = {
                        "partition_id": partition_id,
                        "cell_id": cell_id,
                        "attempt": attempt,
                        "started_at_utc": event_started,
                        "completed_at_utc": now(),
                        "return_code": process.returncode,
                        "status": "complete"
                        if process.returncode == 0 and status == "complete_existing"
                        else "failed",
                        "output": relative(output, pilot_root),
                        "failure_artifact": relative(failure, pilot_root)
                        if failure.exists()
                        else None,
                    }
                    if process.returncode != 0:
                        lines = (
                            (process.stderr or process.stdout or "")
                            .strip()
                            .splitlines()
                        )
                        outcome["diagnostic"] = (
                            lines[-1][:240] if lines else "no child diagnostic"
                        )
                    outcomes.append(outcome)
                    if outcome["status"] == "complete":
                        print(f"{partition_id}/{cell_id}: complete", flush=True)
                        completed_cell = True
                        break
                    print(
                        f"{partition_id}/{cell_id}: retained failed attempt", flush=True
                    )
                except subprocess.TimeoutExpired:
                    outcomes.append(
                        {
                            "partition_id": partition_id,
                            "cell_id": cell_id,
                            "attempt": attempt,
                            "started_at_utc": event_started,
                            "completed_at_utc": now(),
                            "status": "process_timeout",
                            "output": relative(output, pilot_root),
                        }
                    )
                    print(f"{partition_id}/{cell_id}: process timeout", flush=True)
                write_receipt(
                    receipt_path,
                    plan_path=plan_path,
                    pilot_root=pilot_root,
                    started=started,
                    selected=partitions,
                    planned_cells=planned_cells,
                    outcomes=outcomes,
                    status="running",
                )
            if not completed_cell:
                write_receipt(
                    receipt_path,
                    plan_path=plan_path,
                    pilot_root=pilot_root,
                    started=started,
                    selected=partitions,
                    planned_cells=planned_cells,
                    outcomes=outcomes,
                    status="stopped_on_source_or_adapter_failure",
                )
                return 1

    final_status = "bounded_stop" if stopped else "complete"
    write_receipt(
        receipt_path,
        plan_path=plan_path,
        pilot_root=pilot_root,
        started=started,
        selected=partitions,
        planned_cells=planned_cells,
        outcomes=outcomes,
        status=final_status,
    )
    print(
        json.dumps(
            {
                "status": final_status,
                "planned_cells": planned_cells,
                "handled_cells": handled_cells,
                "retained_failures": len(
                    [
                        path
                        for path in (search_dir / "failures").rglob(
                            "*.NON_MERGEABLE_FAILURE.json"
                        )
                        if not path.name.startswith(".")
                    ]
                ),
            }
        )
    )
    return 0 if final_status in ("complete", "bounded_stop") else 1


if __name__ == "__main__":
    raise SystemExit(main())
