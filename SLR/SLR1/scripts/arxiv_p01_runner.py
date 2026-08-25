#!/usr/bin/env python3
"""Bounded source-specific P01 runner for the arXiv browser adapter.

This runner is intentionally a thin, trusted local orchestrator.  The shared
browser-lease wrapper must be its parent; this file never launches Chrome,
selects a browser/profile/port, or performs screening/import.  It executes the
nine count-only cells sequentially, then at most one two-record metadata/
abstract diagnostic and one conditional two-page pagination diagnostic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
METADATA_SELECTION_ORDER = ("B1", "A1", "A2", "A3", "B2", "BG1", "BG2", "BC1", "BT2")
MAX_SOURCE_OPERATIONS = 11
CDP_URL = "http://127.0.0.1:9222"


class RunnerError(RuntimeError):
    """A bounded runner or adapter-output failure."""


def _positive_year(value: str) -> int:
    try:
        year = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer year") from error
    if not 1800 <= year <= 2200:
        raise argparse.ArgumentTypeError("must be between 1800 and 2200")
    return year


def _required_text(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise RunnerError(f"{label} must not be empty")
    return value


def _query(packet: Path, partition: str) -> tuple[str, str]:
    path = packet / "queries" / f"{partition}.arxiv-advanced.txt"
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise RunnerError(f"could not read exact query cell {path}") from error
    if not text.endswith("\n") or "\r" in text or "\x00" in text:
        raise RunnerError(f"query cell is not canonical UTF-8 with one terminal LF: {path}")
    query = text[:-1]
    if not query.strip():
        raise RunnerError(f"query cell is empty: {path}")
    return query, hashlib.sha256(raw).hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _assert_absent(path: Path) -> None:
    if path.exists():
        raise RunnerError(f"refusing to overwrite existing attempt output: {path}")


def adapter_command(
    *,
    adapter: Path,
    query: str,
    output: Path,
    target_id: str | None,
    pilot_year: int,
    limit: int,
    max_pages: int,
    count_only: bool,
    skip_full_abstracts: bool,
    timeout: float,
    page_delay: float,
    uv: str,
) -> list[str]:
    """Build the fixed attached-browser command; no browser override is exposed."""
    command = [
        uv,
        "run",
        str(adapter),
        "--query",
        query,
        "--limit",
        str(limit),
        "--year-start",
        "2011",
        "--year-end",
        str(pilot_year),
        "--max-pages",
        str(max_pages),
        "--timeout",
        str(timeout),
        "--page-delay-seconds",
        str(page_delay),
        "--cdp-url",
        CDP_URL,
        "--output-path",
        str(output),
    ]
    if target_id is not None:
        command.extend(["--target-id", _required_text(target_id, "target_id")])
    if count_only:
        command.append("--count-only")
    if skip_full_abstracts:
        command.append("--skip-full-abstracts")
    return command


def _load_output(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _source_total(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _run_operation(
    *,
    packet: Path,
    output_root: Path,
    partition: str,
    operation_kind: str,
    target_id: str | None,
    pilot_year: int,
    limit: int,
    max_pages: int,
    count_only: bool,
    skip_full_abstracts: bool,
    timeout: float,
    page_delay: float,
    adapter: Path,
    uv: str,
    invoke: Callable[..., subprocess.CompletedProcess[str]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    query, query_sha256 = _query(packet, partition)
    output = output_root / f"{partition}.{operation_kind}.json"
    log_path = output_root / f"{partition}.{operation_kind}.log"
    _assert_absent(output)
    _assert_absent(log_path)
    command = adapter_command(
        adapter=adapter,
        query=query,
        output=output,
        target_id=target_id,
        pilot_year=pilot_year,
        limit=limit,
        max_pages=max_pages,
        count_only=count_only,
        skip_full_abstracts=skip_full_abstracts,
        timeout=timeout,
        page_delay=page_delay,
        uv=uv,
    )
    try:
        with log_path.open("w", encoding="utf-8") as log:
            completed = invoke(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
    except OSError as error:
        completed = subprocess.CompletedProcess(command, 127)
        log_path.write_text(f"runner could not start adapter: {type(error).__name__}\n", encoding="utf-8")

    payload = _load_output(output)
    metadata = payload.get("output_metadata") if isinstance(payload, dict) else None
    total = _source_total(payload.get("total")) if payload else None
    status = str(metadata.get("status")) if isinstance(metadata, dict) else "missing_output"
    if completed.returncode != 0 or payload is None or total is None:
        outcome = "failed"
        total = None
    elif count_only and metadata.get("count_only") is True:
        outcome = "explicit_zero" if total == 0 else "success"
    elif (
        not count_only
        and total >= 1
        and isinstance(payload.get("results"), list)
        and len(payload["results"]) >= 1
    ):
        outcome = "success"
    else:
        outcome = "failed"
        total = None

    operation = {
        "operation_id": f"OP-P01-{partition}-{operation_kind.upper()}",
        "partition_id": partition,
        "kind": operation_kind,
        "query_file": f"queries/{partition}.arxiv-advanced.txt",
        "query_sha256": query_sha256,
        "output_path": _relative(output, output_root),
        "log_path": _relative(log_path, output_root),
        "adapter_returncode": completed.returncode,
        "outcome": outcome,
        "source_reported_total": total,
        "records_retrieved": len(payload.get("results", [])) if payload and isinstance(payload.get("results"), list) else 0,
        "count_only": count_only,
        "limit": limit,
        "max_pages": max_pages,
        "source_status": status,
    }
    return operation, payload


def run_attempt(
    *,
    packet: Path,
    output_root: Path,
    runner_receipt: Path,
    attempt_id: str,
    target_id: str | None,
    pilot_year: int,
    adapter: Path,
    uv: str = "uv",
    timeout: float = 30.0,
    page_delay: float = 0.2,
    invoke: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> int:
    """Run the fixed P01 operation schedule and write one safe runner receipt."""
    _required_text(attempt_id, "attempt_id")
    if target_id is not None:
        _required_text(target_id, "target_id")
    if pilot_year < 1800 or pilot_year > 2200:
        raise RunnerError("pilot_year is outside the bounded year range")
    if not math.isfinite(timeout) or timeout <= 0:
        raise RunnerError("timeout must be finite and greater than zero")
    if not math.isfinite(page_delay) or page_delay < 0:
        raise RunnerError("page_delay must be finite and non-negative")
    if not adapter.is_file():
        raise RunnerError(f"adapter does not exist: {adapter}")
    _assert_absent(runner_receipt)
    output_root.mkdir(parents=True, exist_ok=True)
    operations: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any]] = {}
    terminal = "completed"

    for partition in PARTITIONS:
        operation, payload = _run_operation(
            packet=packet,
            output_root=output_root,
            partition=partition,
            operation_kind="count",
            target_id=target_id,
            pilot_year=pilot_year,
            limit=1,
            max_pages=1,
            count_only=True,
            skip_full_abstracts=True,
            timeout=timeout,
            page_delay=page_delay,
            adapter=adapter,
            uv=uv,
            invoke=invoke,
        )
        operations.append(operation)
        if payload is not None:
            payloads[partition] = payload
        if operation["outcome"] == "failed":
            terminal = "failed"
            break

    selected: str | None = None
    selected_total: int | None = None
    if terminal == "completed":
        for partition in METADATA_SELECTION_ORDER:
            total = _source_total(payloads.get(partition, {}).get("total"))
            if total is not None and total > 0:
                selected, selected_total = partition, total
                break

    if terminal == "completed" and selected is not None:
        operation, payload = _run_operation(
            packet=packet,
            output_root=output_root,
            partition=selected,
            operation_kind="metadata-abstract",
            target_id=target_id,
            pilot_year=pilot_year,
            limit=2,
            max_pages=1,
            count_only=False,
            skip_full_abstracts=False,
            timeout=timeout,
            page_delay=page_delay,
            adapter=adapter,
            uv=uv,
            invoke=invoke,
        )
        operations.append(operation)
        if payload is not None:
            payloads[f"{selected}:metadata-abstract"] = payload
        if operation["outcome"] == "failed":
            terminal = "failed"

    # The adapter chooses page size 100 for a limit above 50.  Only a source
    # total above 100 can therefore force a bounded second rendered page.
    if terminal == "completed" and selected is not None and (selected_total or 0) > 100:
        operation, payload = _run_operation(
            packet=packet,
            output_root=output_root,
            partition=selected,
            operation_kind="pagination",
            target_id=target_id,
            pilot_year=pilot_year,
            limit=101,
            max_pages=2,
            count_only=False,
            skip_full_abstracts=True,
            timeout=timeout,
            page_delay=page_delay,
            adapter=adapter,
            uv=uv,
            invoke=invoke,
        )
        operations.append(operation)
        if payload is not None:
            payloads[f"{selected}:pagination"] = payload
        if operation["outcome"] == "failed":
            terminal = "failed"

    if len(operations) > MAX_SOURCE_OPERATIONS:
        raise RunnerError("internal operation bound exceeded")

    receipt = {
        "schema_version": "slr1-arxiv-p01-runner/v1",
        "attempt_id": attempt_id,
        "source_id": "arxiv",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "source_operations_maximum": MAX_SOURCE_OPERATIONS,
        "source_operations_performed": len(operations),
        "metadata_selection_order": list(METADATA_SELECTION_ORDER),
        "terminal": terminal,
        "operations": operations,
    }
    runner_receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = runner_receipt.with_suffix(runner_receipt.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    temporary.replace(runner_receipt)
    return 0 if terminal == "completed" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--runner-receipt", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument(
        "--target-id",
        help="optional explicit arXiv authorization target; normally omit under the single shared context",
    )
    parser.add_argument("--pilot-year", type=_positive_year, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--uv", default="uv")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.2)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run_attempt(
            packet=args.packet,
            output_root=args.output_root,
            runner_receipt=args.runner_receipt,
            attempt_id=args.attempt_id,
            target_id=args.target_id,
            pilot_year=args.pilot_year,
            adapter=args.adapter,
            uv=args.uv,
            timeout=args.timeout,
            page_delay=args.page_delay_seconds,
        )
    except RunnerError as error:
        print(f"arXiv P01 runner failed before source completion: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
