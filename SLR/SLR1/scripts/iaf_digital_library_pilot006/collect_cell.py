#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.48",
# ]
# ///

"""Collect one strict IAF Pilot 006 cell and its complete identity ledger."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py"
)
LEDGER_SCHEMA = "iaf-digital-library-pilot006-complete-identity-ledger/v1"
NON_MERGEABLE_REASON = (
    "Diagnostic IAF Pilot 006 source cell. Do not merge into the review corpus."
)


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("iaf_pilot006_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the maintained IAF adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> tuple[str, int]:
    body = path.read_bytes()
    return hashlib.sha256(body).hexdigest(), len(body)


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def write_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.parent
    while current != current.parent:
        if current.is_symlink():
            raise OSError("The identity-ledger destination has a symlinked directory")
        current = current.parent
    if path.exists() or path.is_symlink():
        raise OSError(f"Refusing to overwrite {path}")
    body = (
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False).encode(
            "utf-8"
        )
        + b"\n"
    )
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.link(temporary, path)
        temporary.unlink()
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ValueError(f"{label} is not a stable-ID list")
    if len({item.casefold() for item in value}) != len(value):
        raise ValueError(f"{label} contains duplicate stable IDs")
    return list(value)


def identity_payload(
    result: Mapping[str, Any],
    *,
    query: str,
    output_path: Path,
) -> dict[str, Any]:
    metadata = result.get("output_metadata")
    if not isinstance(metadata, Mapping):
        raise TypeError("The strict adapter result lacks output metadata")
    total = result.get("total")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("The strict adapter result lacks an exact source total")
    raw_ids = string_list(metadata.get("ordered_paper_ids"), "Raw ordered paper IDs")
    retained_ids = string_list(
        metadata.get("in_scope_ordered_paper_ids"),
        "Diagnostic-window ordered paper IDs",
    )
    if len(raw_ids) != total:
        raise ValueError(
            "The raw stable-ID ledger does not reconcile to the source total"
        )
    date = metadata.get("date_filter_accounting")
    if not isinstance(date, Mapping):
        raise TypeError("The strict adapter result lacks local date accounting")
    for key, expected in (
        ("raw_total", total),
        ("source_total", total),
        ("source_entries_retrieved", total),
        ("retained", len(retained_ids)),
        ("retained_written", len(retained_ids)),
    ):
        if date.get(key) != expected:
            raise ValueError(f"Date accounting {key} does not reconcile")
    expected_true = (
        "observed_exact_query_echo",
        "source_controls_verified",
        "require_complete",
        "retrieval_complete",
        "source_traversal_complete",
        "two_pass_order_verified",
        "two_pass_capture_verified",
        "detail_capture_complete",
        "local_date_filter_applied",
        "local_date_filter_complete",
        "normalized_merge_eligible",
    )
    if any(metadata.get(key) is not True for key in expected_true):
        raise ValueError("The strict adapter result lacks a complete rendered proof")
    if metadata.get("status") != "success" or metadata.get("count_only") is not False:
        raise ValueError("The strict adapter result is not a successful record run")
    raw_hash = metadata.get("ordered_paper_ids_sha256")
    retained_hash = metadata.get("in_scope_ordered_paper_ids_sha256")
    if not isinstance(raw_hash, str) or not isinstance(retained_hash, str):
        raise TypeError("The strict adapter result lacks stable-ID sequence hashes")
    return {
        "schema_version": LEDGER_SCHEMA,
        "source": "IAF Digital Library",
        "pilot": "006",
        "diagnostic_only": True,
        "do_not_merge": True,
        "query": query,
        "provenance": "adapter in-memory complete result before compact publication",
        "compact_artifact": {
            "file_name": output_path.name,
            "sha256": "pending",
            "bytes": 0,
            "commit_marker": marker_path(output_path).name,
        },
        "completion": {
            "source_total": total,
            "source_entries_retrieved": metadata.get("source_entries_retrieved"),
            "two_pass_order_verified": metadata.get("two_pass_order_verified"),
            "two_pass_capture_verified": metadata.get("two_pass_capture_verified"),
            "detail_capture_complete": metadata.get("detail_capture_complete"),
            "local_date_filter_complete": metadata.get("local_date_filter_complete"),
            "complete_source_total_cap": metadata.get("complete_source_total_cap"),
        },
        "raw_ordered_paper_ids": raw_ids,
        "raw_ordered_paper_ids_sha256": raw_hash,
        "diagnostic_window_ordered_paper_ids": retained_ids,
        "diagnostic_window_ordered_paper_ids_sha256": retained_hash,
        "date_filter_accounting": {
            key: date.get(key)
            for key in (
                "raw_total",
                "source_total",
                "source_entries_retrieved",
                "included",
                "excluded",
                "unresolved",
                "retained",
                "retained_written",
                "complete",
            )
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--output-path", required=True, type=Path)
    parser.add_argument("--identity-ledger-path", required=True, type=Path)
    parser.add_argument("--failure-path", required=True, type=Path)
    parser.add_argument("--date-start", required=True)
    parser.add_argument("--date-end", required=True)
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument(
        "--page-size", type=int, choices=(10, 50, 100, 200, 500), default=500
    )
    parser.add_argument("--passes", type=int, choices=(1, 2), default=2)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--prisma-run-id", required=True)
    parser.add_argument("--prisma-review-id", required=True)
    parser.add_argument("--prisma-strategy-reference", required=True)
    parser.add_argument("--prisma-strategy-version", required=True)
    parser.add_argument("--prisma-phase", required=True)
    parser.add_argument("--prisma-coverage-scope", required=True)
    parser.add_argument("--prisma-partition-id", required=True)
    parser.add_argument("--prisma-partition-label", required=True)
    parser.add_argument("--prisma-partition-description", required=True)
    return parser


def adapter_namespace(adapter: Any, args: argparse.Namespace) -> argparse.Namespace:
    values = [
        "--query",
        args.query,
        "--output-path",
        str(args.output_path),
        "--limit",
        str(args.limit),
        "--max-pages",
        str(args.max_pages),
        "--page-size",
        str(args.page_size),
        "--passes",
        str(args.passes),
        "--timeout",
        str(args.timeout),
        "--page-delay-seconds",
        str(args.page_delay_seconds),
        "--retries",
        str(args.retries),
        "--require-complete",
        "--date-start",
        args.date_start,
        "--date-end",
        args.date_end,
        "--prisma-run-id",
        args.prisma_run_id,
        "--prisma-review-id",
        args.prisma_review_id,
        "--prisma-strategy-reference",
        args.prisma_strategy_reference,
        "--prisma-strategy-version",
        args.prisma_strategy_version,
        "--prisma-phase",
        args.prisma_phase,
        "--prisma-coverage-scope",
        args.prisma_coverage_scope,
        "--prisma-partition-id",
        args.prisma_partition_id,
        "--prisma-partition-label",
        args.prisma_partition_label,
        "--prisma-partition-description",
        args.prisma_partition_description,
    ]
    return adapter.build_parser().parse_args(values)


def save_failure(
    adapter: Any,
    args: argparse.Namespace,
    error: Exception,
    prisma_context: Mapping[str, Any] | None,
) -> None:
    failure_path = args.failure_path.expanduser().resolve()
    failure_path.parent.mkdir(parents=True, exist_ok=True)
    failure = adapter.error_result(
        args.query,
        error,
        query_mode="raw_query",
        limit=args.limit,
        year_start=None,
        year_end=None,
        date_start=args.date_start,
        date_end=args.date_end,
        max_pages=args.max_pages,
        page_size=args.page_size,
        passes=args.passes,
        timeout_seconds=args.timeout,
        page_delay_seconds=args.page_delay_seconds,
        retries=args.retries,
        count_only=False,
        require_complete=True,
    )
    marked = adapter.mark_non_mergeable(
        failure,
        source=adapter.SOURCE_NAME,
        reason=NON_MERGEABLE_REASON,
        prisma_context=adapter._error_prisma_context(prisma_context),
    )
    marked.setdefault("output_metadata", {})["pilot_only"] = True
    adapter._save_search_result(failure_path, marked)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = args.output_path.expanduser().resolve()
    ledger_path = args.identity_ledger_path.expanduser().resolve()
    failure_path = args.failure_path.expanduser().resolve()
    if any(
        path.exists() or path.is_symlink()
        for path in (output, ledger_path, failure_path)
    ):
        print("iaf_pilot006_cell_failed:output_exists")
        return 2
    adapter = load_adapter()
    adapter_args = adapter_namespace(adapter, args)
    prisma_context: Mapping[str, Any] | None = None
    try:
        prisma_context = adapter.configure_prisma_search_run_from_args(
            adapter_args,
            adapter_id=adapter.ADAPTER_ID,
            adapter_version=adapter.ADAPTER_VERSION,
            adapter_script=ADAPTER_PATH,
        )
        executed, query_mode, rows, operators = adapter.validate_cli_args(adapter_args)
        result = adapter.search_iaf_digital_library(
            adapter_args.query,
            wizard_rows=rows if query_mode == "typed_wizard" else None,
            operators=operators if query_mode == "typed_wizard" else None,
            limit=adapter_args.limit,
            max_pages=adapter_args.max_pages,
            page_size=adapter_args.page_size,
            passes=adapter_args.passes,
            partition_by=adapter_args.partition_by,
            year_start=adapter_args.year_start,
            year_end=adapter_args.year_end,
            date_start=adapter_args.date_start,
            date_end=adapter_args.date_end,
            timeout_seconds=adapter_args.timeout_seconds,
            page_delay_seconds=adapter_args.page_delay_seconds,
            retries=adapter_args.retries,
            count_only=adapter_args.count_only,
            require_complete=adapter_args.require_complete,
            cdp_url=adapter_args.cdp_url,
            target_id=adapter_args.target_id,
            headless=adapter_args.headless,
            chrome_executable=adapter_args.chrome_executable,
            prisma_context=prisma_context,
        )
        if executed != args.query:
            raise ValueError("Adapter execution differs from the planned raw cell")
        adapter.assert_complete_iaf_result(result)
        identity = identity_payload(result, query=args.query, output_path=output)
        marked = adapter.mark_non_mergeable(
            result,
            source=adapter.SOURCE_NAME,
            reason=NON_MERGEABLE_REASON,
            prisma_context=prisma_context,
        )
        marked.setdefault("output_metadata", {})["pilot_only"] = True
        adapter._save_search_result(output, marked)
        digest, byte_count = sha256_file(output)
        identity["compact_artifact"]["sha256"] = digest
        identity["compact_artifact"]["bytes"] = byte_count
        if not marker_path(output).is_file():
            raise ValueError("The maintained adapter did not publish a commit marker")
        write_create_only(ledger_path, identity)
        print(
            json.dumps(
                {
                    "status": "complete",
                    "artifact": output.name,
                    "ledger": ledger_path.name,
                    "source_total": result.get("total"),
                }
            )
        )
        return 0
    except (
        adapter.IAFDigitalLibraryError,
        adapter.PrismaSearchRunError,
        TypeError,
        ValueError,
    ) as error:
        try:
            save_failure(adapter, args, error, prisma_context)
        except Exception as save_error:  # noqa: BLE001
            print(
                f"iaf_pilot006_failure_artifact_failed:{type(save_error).__name__}",
                file=sys.stderr,
            )
        print(f"iaf_pilot006_cell_failed:{type(error).__name__}")
        return 1
    except Exception as error:  # noqa: BLE001
        try:
            wrapped = adapter.IAFDigitalLibraryBrowserError(
                "Unexpected IAF Pilot 006 browser workflow failure"
            )
            wrapped.__cause__ = error
            save_failure(adapter, args, wrapped, prisma_context)
        except Exception as save_error:  # noqa: BLE001
            print(
                f"iaf_pilot006_failure_artifact_failed:{type(save_error).__name__}",
                file=sys.stderr,
            )
        print("iaf_pilot006_cell_failed:unexpected")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
