#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Sequential source-specific launch runner for the ProQuest P01 bundles.

The runner is intentionally small: it composes the existing trusted adapter
and the read-only field probe, never launches a browser, never retries a
source operation, and refuses fresh-browser/profile/port options.  The
controller must wrap the complete ``--execute`` invocation in the shared
browser-lease command.  ``--dry-run`` is fully offline and prints the exact
bounded operation ledger without creating source artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit

DEFAULT_CDP_URL = "http://127.0.0.1:9222"
ADAPTER_ROOT = Path("~/agent-tools/academic-research/skills/academic-search/scripts")
PROBE_SCRIPT = Path("SLR/SLR1/scripts/proquest_field_thesaurus_probe.py")
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
QUERY_SUFFIX = ".proquest-noft.txt"
COMMAND_TIMEOUT_SECONDS = 120


class RunnerInputError(Exception):
    pass


@dataclass(frozen=True)
class Operation:
    operation_id: str
    purpose: str
    kind: str
    query: str | None = None
    query_file: str | None = None
    count_only: bool = False
    bounded_limit: int = 1


def validate_cdp_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port != 9222
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise RunnerInputError("only http://127.0.0.1:9222 is permitted")
    return value


def validate_pilot_date(value: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as error:
        raise RunnerInputError("pilot-date must be YYYY-MM-DD") from error
    if parsed < dt.date(2011, 1, 1):
        raise RunnerInputError("pilot-date must be on or after 2011-01-01")
    return parsed


def packet_query_path(packet_root: Path, partition_id: str) -> Path:
    path = packet_root / "queries" / f"{partition_id}{QUERY_SUFFIX}"
    if not path.is_file():
        raise RunnerInputError(f"missing exact query file: {path}")
    return path


def read_query(packet_root: Path, partition_id: str) -> tuple[str, str]:
    path = packet_query_path(packet_root, partition_id)
    query = path.read_text(encoding="utf-8")
    if not query.endswith("\n") or not query[:-1].strip():
        raise RunnerInputError(f"query file must be nonempty UTF-8 with terminal LF: {path}")
    return query[:-1], str(path)


def field_operations(source: str) -> list[Operation]:
    if source == "proquest-atai":
        fields = (
            ("NOFT", 'NOFT("CubeSat")'),
            ("SU", 'SU("CubeSat")'),
            ("IF", 'IF("CubeSat")'),
        )
    else:
        fields = (
            ("TI", 'TI("CubeSat")'),
            ("AB", 'AB("CubeSat")'),
            ("SU", 'SU("CubeSat")'),
            ("IF", 'IF("CubeSat")'),
            ("NOFT", 'NOFT("CubeSat")'),
        )
    return [
        Operation(
            operation_id=f"O{index + 2:02d}-FIELD-{name}",
            purpose=f"source-native {name} field diagnostic",
            kind="field",
            query=query,
            count_only=source == "proquest-atai",
        )
        for index, (name, query) in enumerate(fields)
    ]


def build_operations(source: str, *, packet_root: Path, pilot_date: dt.date) -> list[Operation]:
    if source not in {"proquest-atai", "proquest-pqdt"}:
        raise RunnerInputError(f"unsupported source: {source}")
    operations = [
        Operation(
            operation_id="O01-FIELD-THESAURUS-UI",
            purpose="one owned-page visible subject/index/thesaurus UI inventory",
            kind="probe",
        )
    ]
    operations.extend(field_operations(source))
    for partition_id in PARTITIONS:
        query, query_file = read_query(packet_root, partition_id)
        operations.append(
            Operation(
                operation_id=f"O{len(operations) + 1:02d}-PARTITION-{partition_id}",
                purpose=f"diagnostic translation cell {partition_id}",
                kind="partition",
                query=query,
                query_file=query_file,
                count_only=source == "proquest-atai",
            )
        )
    query, query_file = read_query(packet_root, "A1")
    operations.append(
        Operation(
            operation_id=f"O{len(operations) + 1:02d}-RECORD-A1",
            purpose="one bounded record/detail and stable-ID diagnostic",
            kind="record",
            query=query,
            query_file=query_file,
            count_only=False,
            bounded_limit=1,
        )
    )
    # Keep the date argument in the operation builder so dry-run output proves
    # the pilot date was parsed even though the adapter command composes it.
    _ = pilot_date
    return operations


def operation_arguments(
    source: str,
    operation: Operation,
    *,
    adapter_path: Path,
    output_path: Path,
    cdp_url: str,
    pilot_date: dt.date,
) -> list[str]:
    if operation.query is None:
        raise RunnerInputError("probe operations do not use adapter arguments")
    query = operation.query
    base = [
        "uv",
        "run",
        str(adapter_path),
        "--query",
        query,
        "--cdp-url",
        cdp_url,
        "--output-path",
        str(output_path),
    ]
    if source == "proquest-atai":
        base.extend(
            [
                "--language",
                "English",
                "--timeout",
                "30",
                "--year-start",
                "2011",
                "--year-end",
                str(pilot_date.year),
                "--limit",
                str(operation.bounded_limit),
                "--max-pages",
                "1",
                "--page-delay-seconds",
                "0.2",
            ]
        )
    else:
        base[base.index("--query") + 1] = (
            f"{query} AND YR(2011-{pilot_date.year}) AND LA(English)"
        )
        base.extend(
            [
                "--limit",
                str(operation.bounded_limit),
                "--max-pages",
                "1",
                "--timeout",
                "30",
                "--page-delay-seconds",
                "0.2",
                "--detail-delay-seconds",
                "0.2",
            ]
        )
    if operation.count_only:
        base.append("--count-only")
    return base


def probe_arguments(
    source: str, *, probe_path: Path, output_path: Path, cdp_url: str
) -> list[str]:
    return [
        "uv",
        "run",
        str(probe_path),
        "--source",
        source,
        "--cdp-url",
        cdp_url,
        "--execute",
        "--output-path",
        str(output_path),
    ]


def _ensure_new_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.exists():
            raise RunnerInputError(f"create-only output already exists: {path}")


def _safe_output_path(root: Path, name: str) -> Path:
    candidate = (root / name).resolve(strict=False)
    resolved_root = root.resolve(strict=False)
    if candidate.parent != resolved_root or candidate.name != name:
        raise RunnerInputError("operation output escaped its output namespace")
    return candidate


def render_plan(
    source: str,
    *,
    operations: list[Operation],
    packet_root: Path,
    adapter_path: Path,
    probe_path: Path,
    output_dir: Path,
    pilot_date: dt.date,
    cdp_url: str,
) -> dict:
    planned = []
    for operation in operations:
        output_path = _safe_output_path(output_dir, f"{operation.operation_id}.json")
        if operation.kind == "probe":
            command = probe_arguments(
                source, probe_path=probe_path, output_path=output_path, cdp_url=cdp_url
            )
        else:
            command = operation_arguments(
                source,
                operation,
                adapter_path=adapter_path,
                output_path=output_path,
                cdp_url=cdp_url,
                pilot_date=pilot_date,
            )
        planned.append(
            {
                "operation_id": operation.operation_id,
                "purpose": operation.purpose,
                "kind": operation.kind,
                "query_file": operation.query_file,
                "query_present": operation.query is not None,
                "count_only": operation.count_only,
                "command": command,
                "output_path": str(output_path),
            }
        )
    return {
        "schema_version": "slr1-proquest-pilot-runner-plan/v1",
        "source_id": source,
        "cdp_url": cdp_url,
        "pilot_date": pilot_date.isoformat(),
        "date_suffix": f"YR(2011-{pilot_date.year}) AND LA(English)",
        "packet_root": str(packet_root),
        "adapter_path": str(adapter_path),
        "probe_path": str(probe_path),
        "predeclared_operation_cap": len(operations),
        "operations": planned,
        "retry_policy": {
            "maximum_source_reissues": 0,
            "challenge_reissue": False,
            "busy_reissue": False,
        },
    }


def run_plan(plan: dict, *, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = _safe_output_path(output_dir, "runner-ledger.json")
    paths = [Path(item["output_path"]) for item in plan["operations"]] + [ledger_path]
    _ensure_new_paths(paths)
    completed: list[dict] = []
    for item in plan["operations"]:
        command = item["command"]
        try:
            completed_process = subprocess.run(
                command,
                check=False,
                text=True,
                capture_output=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            outcome = {
                "operation_id": item["operation_id"],
                "status": "failed",
                "returncode": None,
                "stdout_present": False,
                "stderr_present": False,
                "reason": "trusted local command exceeded its finite runner timeout",
            }
            completed.append(outcome)
            _write_ledger(ledger_path, plan, completed, "failed")
            return 1
        except OSError as error:
            outcome = {
                "operation_id": item["operation_id"],
                "status": "failed",
                "returncode": None,
                "stdout_present": False,
                "stderr_present": False,
                "reason": "trusted local command could not be started",
            }
            completed.append(outcome)
            _write_ledger(ledger_path, plan, completed, "failed")
            print(f"proquest runner failed: {error}", file=sys.stderr)
            return 1
        outcome = {
            "operation_id": item["operation_id"],
            "status": "completed" if completed_process.returncode == 0 else "failed",
            "returncode": completed_process.returncode,
            "stdout_present": bool(completed_process.stdout),
            "stderr_present": bool(completed_process.stderr),
        }
        completed.append(outcome)
        # Do not print adapter output: it may contain result text. The adapter
        # owns the JSON artifact; this ledger retains only safe presence bits.
        if completed_process.returncode != 0:
            _write_ledger(ledger_path, plan, completed, "failed")
            return completed_process.returncode or 1
    _write_ledger(ledger_path, plan, completed, "completed")
    return 0


def _write_ledger(path: Path, plan: dict, completed: list[dict], status: str) -> None:
    payload = {
        "schema_version": "slr1-proquest-pilot-runner-ledger/v1",
        "source_id": plan["source_id"],
        "status": status,
        "predeclared_operation_cap": plan["predeclared_operation_cap"],
        "performed_operations": len(completed),
        "operations": completed,
        "retry_policy": plan["retry_policy"],
    }
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            json.dump(payload, handle, indent=2)
            handle.write("\n")
    finally:
        if descriptor != -1:
            os.close(descriptor)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the bounded, sequential ProQuest P01 plan using the existing "
            "adapter and one-owned-page field probe; never launches a browser."
        )
    )
    parser.add_argument("--source", choices=("proquest-atai", "proquest-pqdt"), required=True)
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pilot-date", required=True, help="Actual P01 execution date, YYYY-MM-DD")
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--adapter-root", type=Path, default=ADAPTER_ROOT)
    parser.add_argument("--probe-script", type=Path, default=PROBE_SCRIPT)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Invoke the trusted local commands; otherwise print the offline plan only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        cdp_url = validate_cdp_url(args.cdp_url)
        pilot_date = validate_pilot_date(args.pilot_date)
        packet_root = args.packet_root.expanduser().resolve(strict=True)
        adapter_root = args.adapter_root.expanduser().resolve(strict=True)
        probe_path = args.probe_script.expanduser().resolve(strict=True)
        adapter_name = (
            "search_proquest_aerospace.py"
            if args.source == "proquest-atai"
            else "search_pqdt.py"
        )
        adapter_path = (adapter_root / adapter_name).resolve(strict=True)
        if not probe_path.is_file() or not adapter_path.is_file():
            raise RunnerInputError("trusted adapter/probe path is missing")
        output_dir = args.output_dir.expanduser().resolve(strict=False)
        operations = build_operations(
            args.source, packet_root=packet_root, pilot_date=pilot_date
        )
        plan = render_plan(
            args.source,
            operations=operations,
            packet_root=packet_root,
            adapter_path=adapter_path,
            probe_path=probe_path,
            output_dir=output_dir,
            pilot_date=pilot_date,
            cdp_url=cdp_url,
        )
        if not args.execute:
            print(json.dumps(plan, indent=2))
            return 0
        return run_plan(plan, output_dir=output_dir)
    except (RunnerInputError, OSError) as error:
        print(f"proquest runner input failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
