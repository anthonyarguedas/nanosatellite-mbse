#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.48",
# ]
# ///

"""Collect one strict IAF cell and retain its complete stable-ID ledger.

The maintained adapter deliberately persists a compact PRISMA-S result.  Its
in-memory strict result also contains the two-pass raw ordered paper-ID ledger;
this wrapper writes a small create-only identity sidecar from that result and
then asks the adapter itself to publish its normal compact, marker-gated JSON.
It does not implement source interaction, parsing, pagination, or metadata
normalization.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


ADAPTER_PATH = Path.home() / "agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py"
LEDGER_SCHEMA = "iaf-digital-library-complete-identity-ledger/v1"


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("iaf_pilot003_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load maintained IAF adapter")
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
            raise OSError("identity ledger destination has a symlinked directory")
        current = current.parent
    if path.exists() or path.is_symlink():
        raise OSError("refusing to overwrite identity ledger")
    body = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8") + b"\n"
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


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{label} is not a nonempty stable-ID list")
    if len({item.casefold() for item in value}) != len(value):
        raise ValueError(f"{label} contains duplicate stable IDs")
    return list(value)


def _identity_payload(
    result: Mapping[str, Any],
    *,
    query: str,
    output_path: Path,
    compact_digest: str,
    compact_bytes: int,
    provenance: str,
) -> dict[str, Any]:
    metadata = result.get("output_metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("strict adapter result lacks output metadata")
    total = result.get("total")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("strict adapter result lacks an exact source total")
    raw_ids = _string_list(metadata.get("ordered_paper_ids"), "raw ordered paper IDs")
    retained_ids = _string_list(
        metadata.get("in_scope_ordered_paper_ids"), "diagnostic-window ordered paper IDs"
    )
    if len(raw_ids) != total:
        raise ValueError("raw stable-ID ledger does not reconcile to source total")
    date = metadata.get("date_filter_accounting")
    if not isinstance(date, Mapping):
        raise ValueError("strict adapter result lacks local date accounting")
    for key, expected in (
        ("raw_total", total),
        ("source_total", total),
        ("source_entries_retrieved", total),
        ("retained", len(retained_ids)),
        ("retained_written", len(retained_ids)),
    ):
        if date.get(key) != expected:
            raise ValueError(f"date accounting {key} does not reconcile")
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
        raise ValueError("strict adapter result lacks a complete rendered proof")
    if metadata.get("status") != "success" or metadata.get("count_only") is not False:
        raise ValueError("strict adapter result is not a successful record run")
    raw_hash = metadata.get("ordered_paper_ids_sha256")
    retained_hash = metadata.get("in_scope_ordered_paper_ids_sha256")
    if not isinstance(raw_hash, str) or not isinstance(retained_hash, str):
        raise ValueError("strict adapter result lacks stable-ID sequence hashes")
    return {
        "schema_version": LEDGER_SCHEMA,
        "source": "IAF Digital Library",
        "query": query,
        "provenance": provenance,
        "compact_artifact": {
            "file_name": output_path.name,
            "sha256": compact_digest,
            "bytes": compact_bytes,
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


def _backfill_payload_from_compact(
    compact: Mapping[str, Any], *, output_path: Path, digest: str, byte_count: int
) -> dict[str, Any]:
    """Backfill only when compact rows already equal the exact raw total."""

    metadata = compact.get("output_metadata")
    receipt = metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    counts = receipt.get("staged_counts") if isinstance(receipt, Mapping) else None
    strategy = receipt.get("strategy") if isinstance(receipt, Mapping) else None
    total = compact.get("total")
    rows = compact.get("results")
    if (
        not isinstance(total, int)
        or isinstance(total, bool)
        or total < 0
        or not isinstance(rows, list)
        or len(rows) != total
        or not isinstance(counts, Mapping)
        or counts.get("source_reported_total") != total
        or counts.get("raw_source_records") != total
        or counts.get("records_exported") != total
        or counts.get("client_side_exclusions") != 0
        or counts.get("local_match_count") != total
        or not isinstance(strategy, Mapping)
        or not isinstance(strategy.get("executed_query"), str)
        or receipt.get("completion_status") != "complete"
        or receipt.get("report_ready") is not True
    ):
        raise ValueError("compact artifact cannot prove every raw stable identity for backfill")
    raw_ids = _string_list(
        [row.get("paperId") if isinstance(row, Mapping) else None for row in rows],
        "compact result paper IDs",
    )
    hash_value = hashlib.sha256("\n".join(raw_ids).encode("utf-8")).hexdigest()
    return {
        "schema_version": LEDGER_SCHEMA,
        "source": "IAF Digital Library",
        "query": strategy["executed_query"],
        "provenance": "postpublication_compact_projection_all_rows_retained",
        "compact_artifact": {
            "file_name": output_path.name,
            "sha256": digest,
            "bytes": byte_count,
            "commit_marker": marker_path(output_path).name,
        },
        "completion": {
            "source_total": total,
            "source_entries_retrieved": total,
            "two_pass_order_verified": True,
            "two_pass_capture_verified": True,
            "detail_capture_complete": True,
            "local_date_filter_complete": True,
            "complete_source_total_cap": 5000,
            "proof": "attested by the compact marker-gated complete receipt; backfill is allowed only when compact rows equal the full exact raw total",
        },
        "raw_ordered_paper_ids": raw_ids,
        "raw_ordered_paper_ids_sha256": hash_value,
        "diagnostic_window_ordered_paper_ids": raw_ids,
        "diagnostic_window_ordered_paper_ids_sha256": hash_value,
        "date_filter_accounting": {
            "raw_total": total,
            "source_total": total,
            "source_entries_retrieved": total,
            "included": total,
            "excluded": 0,
            "unresolved": 0,
            "retained": total,
            "retained_written": total,
            "complete": True,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query")
    parser.add_argument("--output-path", required=True, type=Path)
    parser.add_argument("--identity-ledger-path", required=True, type=Path)
    parser.add_argument("--date-start", required=True)
    parser.add_argument("--date-end", required=True)
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--page-size", type=int, choices=(10, 50, 100, 200, 500), default=500)
    parser.add_argument("--passes", type=int, choices=(1, 2), default=2)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--page-delay-seconds", type=float, default=0.05)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--prisma-run-id", required=True)
    parser.add_argument("--prisma-review-id", required=True)
    parser.add_argument("--prisma-strategy-reference", required=True)
    parser.add_argument("--prisma-strategy-version")
    parser.add_argument("--prisma-phase", required=True)
    parser.add_argument("--prisma-coverage-scope", required=True)
    parser.add_argument("--prisma-partition-id", required=True)
    parser.add_argument("--prisma-partition-label", required=True)
    parser.add_argument("--prisma-partition-description", required=True)
    parser.add_argument("--backfill-existing", action="store_true")
    return parser


def _adapter_namespace(adapter: Any, args: argparse.Namespace) -> argparse.Namespace:
    values = [
        "--query", args.query,
        "--output-path", str(args.output_path),
        "--limit", str(args.limit),
        "--max-pages", str(args.max_pages),
        "--page-size", str(args.page_size),
        "--passes", str(args.passes),
        "--timeout", str(args.timeout),
        "--page-delay-seconds", str(args.page_delay_seconds),
        "--retries", str(args.retries),
        "--require-complete",
        "--date-start", args.date_start,
        "--date-end", args.date_end,
        "--prisma-run-id", args.prisma_run_id,
        "--prisma-review-id", args.prisma_review_id,
        "--prisma-strategy-reference", args.prisma_strategy_reference,
        "--prisma-phase", args.prisma_phase,
        "--prisma-coverage-scope", args.prisma_coverage_scope,
        "--prisma-partition-id", args.prisma_partition_id,
        "--prisma-partition-label", args.prisma_partition_label,
        "--prisma-partition-description", args.prisma_partition_description,
    ]
    if args.prisma_strategy_version:
        values.extend(("--prisma-strategy-version", args.prisma_strategy_version))
    return adapter.build_parser().parse_args(values)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = args.output_path.expanduser().resolve()
    ledger_path = args.identity_ledger_path.expanduser().resolve()
    if args.backfill_existing:
        try:
            if not output.is_file() or output.is_symlink():
                raise ValueError("compact artifact is unavailable for backfill")
            compact = json.loads(output.read_text(encoding="utf-8"))
            digest, byte_count = sha256_file(output)
            payload = _backfill_payload_from_compact(
                compact, output_path=output, digest=digest, byte_count=byte_count
            )
            write_create_only(ledger_path, payload)
            print(json.dumps({"status": "backfilled", "ledger": ledger_path.name}))
            return 0
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"identity_ledger_backfill_failed:{type(error).__name__}")
            return 1
    if not isinstance(args.query, str) or not args.query:
        print("identity_ledger_collection_failed:missing_query")
        return 2
    if output.exists() or output.is_symlink() or ledger_path.exists() or ledger_path.is_symlink():
        print("identity_ledger_collection_failed:output_exists")
        return 2
    adapter = load_adapter()
    adapter_args = _adapter_namespace(adapter, args)
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
            raise ValueError("adapter execution query differs from the planned raw cell")
        adapter.assert_complete_iaf_result(result)
        # Capture the complete in-memory identity proof before the maintained
        # writer deliberately compacts its persisted metadata.
        identity = _identity_payload(
            result,
            query=args.query,
            output_path=output,
            compact_digest="pending",
            compact_bytes=0,
            provenance="adapter_in_memory_complete_result_before_compact_publication",
        )
        adapter._save_search_result(output, result)
        digest, byte_count = sha256_file(output)
        identity["compact_artifact"]["sha256"] = digest
        identity["compact_artifact"]["bytes"] = byte_count
        if not marker_path(output).is_file():
            raise ValueError("maintained adapter did not publish its terminal commit marker")
        write_create_only(ledger_path, identity)
        print(json.dumps({"status": "complete", "artifact": output.name, "ledger": ledger_path.name}))
        return 0
    except (adapter.IAFDigitalLibraryError, adapter.PrismaSearchRunError, ValueError) as error:
        try:
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
            adapter._save_search_result(
                output,
                adapter.mark_non_mergeable(
                    failure,
                    source=adapter.SOURCE_NAME,
                    prisma_context=adapter._error_prisma_context(prisma_context),
                ),
            )
        except Exception:  # noqa: BLE001 - preserve the source failure artifact when possible
            pass
        print(f"identity_ledger_collection_failed:{type(error).__name__}")
        return 1
    except Exception:  # noqa: BLE001 - source error detail is intentionally not persisted here
        print("identity_ledger_collection_failed:unexpected")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
