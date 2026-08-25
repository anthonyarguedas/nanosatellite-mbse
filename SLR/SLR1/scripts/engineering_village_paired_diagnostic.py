#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Run the single bounded P03/P04 paired Compendex/Inspec diagnostic event.

This is a bounded attached diagnostic, not a final-search runner.  It is
intentionally separate from the route projection: operation 1 is performed by
``engineering_village_route_probe.py`` and this utility is operation 2.  The
one logical paired event contains exactly two explicitly counted component
requests, one to Compendex and one to Inspec.  Existing Engineering Village
adapter calls are made sequentially so that only one adapter-owned page exists
at a time.  The attempt ID selects the matching immutable operation label;
only the controller-authorized P03/P04 identities are accepted.

The adapter results are inspected only for safe count, selection, control, and
provenance metadata.  Bibliographic records are never written.  A successful
component request is capped at one rendered page and one record; this event
must stop after count/control evidence and must never become full retrieval.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
DEFAULT_TIMEOUT_SECONDS = 45.0
DEFAULT_ADAPTER_PAGE_DELAY_SECONDS = 0.25
DEFAULT_INTER_DATABASE_DELAY_SECONDS = 2.0
DIAGNOSTIC_LIMIT = 1
DIAGNOSTIC_MAX_PAGES = 1
DIAGNOSTIC_YEAR_START = 2011
OPERATION_ID = "P03-OP02-PAIRED-DIAGNOSTIC"
OPERATION_ID_SUFFIX = "-OP02-PAIRED-DIAGNOSTIC"
DATABASES = ("compendex", "inspec")
DATABASE_MASKS = {"compendex": "1", "inspec": "2"}
ADAPTER_DIRECTORY = Path(
    "/Users/antho/agent-tools/academic-research/skills/academic-search/scripts"
)


class InputValidationError(ValueError):
    """Raised for invalid runtime input before an adapter can be loaded."""


@dataclass(frozen=True)
class QueryEvidence:
    path: Path
    sha256: str
    utf8_bytes: int
    terminal_lf: bool
    text: str


@dataclass(frozen=True)
class PairedDiagnosticConfig:
    execute: bool
    attempt_id: str
    cdp_url: str
    query_file: Path
    pilot_date: date
    output_path: Path
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    adapter_page_delay_seconds: float = DEFAULT_ADAPTER_PAGE_DELAY_SECONDS
    inter_database_delay_seconds: float = DEFAULT_INTER_DATABASE_DELAY_SECONDS
    adapter_directory: Path = ADAPTER_DIRECTORY


@dataclass
class OutputReservation:
    path: Path
    descriptor: int


AdapterCall = Callable[..., Mapping[str, Any]]
Sleeper = Callable[[float], None]


_ATTEMPT_ID_PATTERN = re.compile(
    r"^S-D04-P(?P<attempt_number>03|04)-[A-Za-z0-9][A-Za-z0-9._+:-]*$"
)


def operation_id_for_attempt(attempt_id: str) -> str:
    """Bind operation metadata to the validated immutable P03/P04 identity."""
    match = _ATTEMPT_ID_PATTERN.fullmatch(attempt_id)
    if match is None:
        raise InputValidationError(
            "--attempt-id must be a runtime S-D04-P03 or S-D04-P04 timestamp identifier"
        )
    return f"P{match.group('attempt_number')}{OPERATION_ID_SUFFIX}"


def _finite_nonnegative(value: Any, option: str) -> float:
    if isinstance(value, bool):
        raise InputValidationError(f"{option} must be a finite non-negative number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(
            f"{option} must be a finite non-negative number"
        ) from error
    if not math.isfinite(parsed) or parsed < 0:
        raise InputValidationError(f"{option} must be a finite non-negative number")
    return parsed


def _finite_positive(value: Any, option: str) -> float:
    parsed = _finite_nonnegative(value, option)
    if parsed <= 0:
        raise InputValidationError(f"{option} must be a finite positive number")
    return parsed


def validate_cdp_url(value: Any) -> str:
    """Use only the one controller-shared CfT endpoint."""
    if type(value) is not str or value != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    return DEFAULT_CDP_URL


def validate_attempt_id(value: Any) -> str:
    if type(value) is not str or not _ATTEMPT_ID_PATTERN.fullmatch(value):
        raise InputValidationError(
            "--attempt-id must be a runtime S-D04-P03 or S-D04-P04 timestamp identifier"
        )
    return value


def validate_pilot_date(value: Any) -> date:
    if type(value) is not str:
        raise InputValidationError("--pilot-date must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise InputValidationError("--pilot-date must be YYYY-MM-DD") from error


def validate_query_file(value: Any) -> Path:
    if not isinstance(value, Path):
        value = Path(value)
    path = value.expanduser()
    if not path.is_file():
        raise InputValidationError("--query-file must name an existing regular file")
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise InputValidationError("--query-file must be readable UTF-8") from error
    if not text.strip():
        raise InputValidationError("--query-file must not be blank")
    if not data.endswith(b"\n"):
        raise InputValidationError("--query-file must end with one terminal LF")
    return path.resolve()


def read_query_evidence(path: Path) -> QueryEvidence:
    path = validate_query_file(path)
    data = path.read_bytes()
    text = data.decode("utf-8")
    return QueryEvidence(
        path=path,
        sha256=hashlib.sha256(data).hexdigest(),
        utf8_bytes=len(data),
        terminal_lf=data.endswith(b"\n"),
        text=text,
    )


def validate_output_path(value: Any) -> Path:
    if not isinstance(value, Path):
        value = Path(value)
    if not str(value).strip():
        raise InputValidationError("--output-path must be nonblank")
    candidate = value.expanduser()
    if candidate.exists():
        raise InputValidationError("--output-path must be create-only and absent")
    path = candidate.resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.is_dir():
        raise InputValidationError("--output-path parent must be a directory")
    return path


def validate_adapter_directory(value: Any) -> Path:
    if not isinstance(value, Path):
        value = Path(value)
    path = value.expanduser().resolve(strict=False)
    if not path.is_dir():
        raise InputValidationError("--adapter-dir must name the local adapter directory")
    return path


def validate_config(config: Any) -> PairedDiagnosticConfig:
    if not isinstance(config, PairedDiagnosticConfig):
        raise InputValidationError("runtime paired-diagnostic configuration is invalid")
    if type(config.execute) is not bool:
        raise InputValidationError("runtime paired-diagnostic configuration is invalid")
    return PairedDiagnosticConfig(
        execute=config.execute,
        attempt_id=validate_attempt_id(config.attempt_id),
        cdp_url=validate_cdp_url(config.cdp_url),
        query_file=validate_query_file(config.query_file),
        pilot_date=validate_pilot_date(config.pilot_date.isoformat() if isinstance(config.pilot_date, date) else config.pilot_date),
        output_path=validate_output_path(config.output_path),
        timeout_seconds=_finite_positive(
            config.timeout_seconds, "--timeout-seconds"
        ),
        adapter_page_delay_seconds=_finite_nonnegative(
            config.adapter_page_delay_seconds, "--adapter-page-delay-seconds"
        ),
        inter_database_delay_seconds=_finite_nonnegative(
            config.inter_database_delay_seconds, "--inter-database-delay-seconds"
        ),
        adapter_directory=validate_adapter_directory(config.adapter_directory),
    )


def reserve_output_path(path: Path) -> OutputReservation:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    return OutputReservation(path=path, descriptor=descriptor)


def write_reserved_json(
    reservation: OutputReservation, payload: Mapping[str, Any]
) -> None:
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("receipt reservation is no longer writable")
    reservation.descriptor = -1
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def _empty_control_evidence() -> dict[str, Any]:
    return {
        "selected_database": None,
        "database_mask": None,
        "selection_mode": None,
        "selected_database_scope": None,
        "selection_observed": False,
        "adapter_control_gate_passed": False,
    }


def _planned_request(
    attempt_id: str, database: str, operation_id: str = OPERATION_ID
) -> dict[str, Any]:
    return {
        "request_id": f"{attempt_id}:{operation_id}:{database}",
        "database": database,
        "adapter_entry_point": (
            "search_compendex.search_compendex"
            if database == "compendex"
            else "search_inspec.search_inspec"
        ),
        "status": "not_run",
        "classification": "not_run",
        "total": None,
        "total_is_exact": False,
        "explicit_native_zero": False,
        "records_retrieved_by_adapter": 0,
        "records_retained": 0,
        "controls": _empty_control_evidence(),
        "provenance": {
            "source": None,
            "database": database,
            "selected_databases": [database],
            "row_provenance_retained": False,
            "row_provenance_summary": None,
        },
    }


def new_receipt(config: PairedDiagnosticConfig, query: QueryEvidence) -> dict[str, Any]:
    operation_id = operation_id_for_attempt(config.attempt_id)
    return {
        "schema_version": "slr1-engineering-village-paired-diagnostic/v1",
        "mode": "source_action" if config.execute else "dry_run",
        "attempt_id": config.attempt_id,
        "operation_id": operation_id,
        "endpoint_class": "explicit_loopback_cdp",
        "cdp_endpoint": DEFAULT_CDP_URL,
        "paired_event": True,
        "retention_exclusions": [
            "query_text",
            "record",
            "RIS_body",
            "raw_exception",
            "credential",
            "cookie",
            "session_or_search_identifier",
            "browser_target_identifier",
        ],
        "query_reference": {
            "path": str(query.path),
            "sha256": query.sha256,
            "utf8_bytes": query.utf8_bytes,
            "terminal_lf": query.terminal_lf,
        },
        "diagnostic_bounds": {
            "publication_date_lower_inclusive": "2011-01-01",
            "publication_date_upper_inclusive": config.pilot_date.isoformat(),
            "adapter_year_start": DIAGNOSTIC_YEAR_START,
            "adapter_year_end": config.pilot_date.year,
            "day_precision_source_validation": "untested",
            "limit_per_database_request": DIAGNOSTIC_LIMIT,
            "max_pages_per_database_request": DIAGNOSTIC_MAX_PAGES,
            "full_retrieval": False,
        },
        "accounting": {
            "campaign_source_operation_count": 0,
            "campaign_source_operation_maximum": 1,
            "database_requests_planned": 2,
            "database_requests_performed": 0,
            "selected_databases": list(DATABASES),
            "paired_event_semantics": (
                "one_logical_paired_event_with_two_explicit_component_requests"
            ),
        },
        "database_requests": [
            _planned_request(
                config.attempt_id, database, operation_id
            )
            for database in DATABASES
        ],
        "totals": {
            "paired": None,
            "compendex": None,
            "inspec": None,
            "paired_total_basis": "not_inferred_from_separate_database_requests",
        },
        "result": {
            "status": "not_run" if not config.execute else "pending",
            "classification": "not_run" if not config.execute else "pending",
            "count_control_evidence_complete": False,
            "records_retained": 0,
            "source_writing_stopped": True,
        },
    }


def _nonnegative_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _safe_result_status(metadata: Mapping[str, Any]) -> str:
    value = metadata.get("status")
    return value if isinstance(value, str) and value in {
        "success",
        "partial",
        "count_only",
        "error",
    } else "unknown"


def _control_evidence(
    database: str, metadata: Mapping[str, Any]
) -> tuple[dict[str, Any], bool]:
    selected = metadata.get("databases")
    selected_safe = list(selected) if isinstance(selected, list) and all(
        isinstance(value, str) for value in selected
    ) else None
    mask = metadata.get("database_mask")
    mask_safe = mask if isinstance(mask, str) and mask in {"1", "2", "3"} else None
    mode = metadata.get("database_selection_mode")
    mode_safe = mode if isinstance(mode, str) else None
    scope = metadata.get("selected_database_scope")
    scope_safe = scope if isinstance(scope, str) else None
    observed = selected_safe == [database] and mask_safe == DATABASE_MASKS[database]
    evidence = {
        "selected_database": selected_safe,
        "database_mask": mask_safe,
        "selection_mode": mode_safe,
        "selected_database_scope": scope_safe,
        "selection_observed": observed,
        "adapter_control_gate_passed": observed,
    }
    return evidence, observed


def _provenance_summary(
    database: str, metadata: Mapping[str, Any], records_retrieved: int
) -> dict[str, Any]:
    source = metadata.get("source")
    source_safe = source if isinstance(source, str) else None
    raw_by_database = metadata.get("source_entries_retrieved_by_database")
    row_count = None
    if isinstance(raw_by_database, Mapping):
        row_count = _nonnegative_int(raw_by_database.get(database))
    return {
        "source": source_safe,
        "database": database,
        "selected_databases": [database],
        "row_provenance_retained": row_count is not None,
        "row_provenance_summary": {
            "database": database,
            "rows_seen_by_adapter": row_count,
            "records_retrieved_by_adapter": records_retrieved,
        }
        if row_count is not None
        else None,
    }


def _failure_classification(error: BaseException) -> str:
    name = type(error).__name__.casefold()
    if "access" in name or "challenge" in name:
        return "adapter_access_or_challenge"
    if "protocol" in name or "input" in name:
        return "adapter_protocol_or_control_failure"
    if "browser" in name or "request" in name:
        return "adapter_browser_or_request_failure"
    return "adapter_call_failed"


def _summarize_adapter_result(
    database: str, result: Any
) -> tuple[dict[str, Any], bool]:
    """Keep only bounded metadata from one existing adapter return value."""
    if not isinstance(result, Mapping):
        request = _planned_request("unbound", database)
        request.update(
            {
                "status": "blocked",
                "classification": "adapter_return_invalid",
            }
        )
        return request, False

    metadata = result.get("output_metadata")
    if not isinstance(metadata, Mapping):
        request = _planned_request("unbound", database)
        request.update(
            {
                "status": "blocked",
                "classification": "adapter_metadata_missing",
            }
        )
        return request, False

    adapter_status = _safe_result_status(metadata)
    total_raw = result.get("total")
    total = _nonnegative_int(total_raw)
    total_is_exact = metadata.get("total_is_exact") is True and total is not None
    records_retrieved = _nonnegative_int(result.get("results_retrieved"))
    if records_retrieved is None:
        records_retrieved = 0
    controls, controls_ok = _control_evidence(database, metadata)
    provenance = _provenance_summary(database, metadata, records_retrieved)
    explicit_zero = bool(
        total_is_exact
        and total == 0
        and adapter_status in {"success", "partial", "count_only"}
        and metadata.get("stopped_reason") == "zero_results"
    )
    accepted = bool(
        adapter_status in {"success", "partial", "count_only"}
        and total_is_exact
        and controls_ok
        and (total > 0 or explicit_zero)
    )
    request = _planned_request("unbound", database)
    request.update(
        {
            "status": "completed" if accepted else "blocked",
            "classification": "count_and_control_observed"
            if accepted
            else "missing_exact_count_or_selection_evidence",
            "adapter_status": adapter_status,
            "total": total if total_is_exact else None,
            "total_is_exact": total_is_exact,
            "explicit_native_zero": explicit_zero,
            "records_retrieved_by_adapter": records_retrieved,
            "records_retained": 0,
            "controls": controls,
            "provenance": provenance,
        }
    )
    return request, accepted


def _failure_request(
    attempt_id: str,
    database: str,
    error: BaseException,
    operation_id: str = OPERATION_ID,
) -> dict[str, Any]:
    request = _planned_request(attempt_id, database, operation_id)
    request.update(
        {
            "status": "blocked",
            "classification": _failure_classification(error),
            "error_type": type(error).__name__
            if type(error).__name__ in {
                "CompendexAccessError",
                "CompendexBrowserError",
                "CompendexInputError",
                "CompendexProtocolError",
                "CompendexRequestError",
                "InspecAccessError",
                "InspecBrowserError",
                "InspecInputError",
                "InspecProtocolError",
                "InspecRequestError",
            }
            else "adapter_error",
        }
    )
    return request


def _not_run_request(
    attempt_id: str,
    database: str,
    reason: str,
    operation_id: str = OPERATION_ID,
) -> dict[str, Any]:
    request = _planned_request(attempt_id, database, operation_id)
    request["classification"] = reason
    return request


def _call_kwargs(config: PairedDiagnosticConfig) -> dict[str, Any]:
    return {
        "limit": DIAGNOSTIC_LIMIT,
        "year_start": DIAGNOSTIC_YEAR_START,
        "year_end": config.pilot_date.year,
        "max_pages": DIAGNOSTIC_MAX_PAGES,
        "timeout_seconds": config.timeout_seconds,
        "page_delay_seconds": config.adapter_page_delay_seconds,
        "cdp_url": config.cdp_url,
        "target_id": None,
        "result_url": None,
        "headless": False,
        "chrome_executable": None,
        "require_complete": False,
        "prisma_context": None,
    }


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("adapter entry point could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_default_adapters(adapter_directory: Path) -> dict[str, AdapterCall]:
    """Load the pinned local wrappers without starting a browser."""
    implementation_path = adapter_directory / "_engineering_village_search.py"
    compendex_path = adapter_directory / "search_compendex.py"
    inspec_path = adapter_directory / "search_inspec.py"
    if not all(path.is_file() for path in (implementation_path, compendex_path, inspec_path)):
        raise RuntimeError("Engineering Village adapter entry point is unavailable")
    _load_module("_engineering_village_search", implementation_path)
    compendex = _load_module("_p03_search_compendex", compendex_path)
    inspec = _load_module("_p03_search_inspec", inspec_path)
    return {
        "compendex": compendex.search_compendex,
        "inspec": inspec.search_inspec,
    }


def run_paired_diagnostic(
    config: PairedDiagnosticConfig,
    *,
    adapter_calls: Mapping[str, AdapterCall] | None = None,
    sleeper: Sleeper = time.sleep,
) -> tuple[int, dict[str, Any]]:
    """Run one logical paired event with two explicitly counted requests."""
    try:
        config = validate_config(config)
        query = read_query_evidence(config.query_file)
    except Exception:
        return 1, {
            "schema_version": "slr1-engineering-village-paired-diagnostic/v1",
            "mode": "not_run",
            "result": {
                "status": "blocked",
                "classification": "invalid_runtime_config",
            },
        }

    operation_id = operation_id_for_attempt(config.attempt_id)
    receipt = new_receipt(config, query)
    try:
        reservation = reserve_output_path(config.output_path)
    except OSError:
        receipt["result"] = {
            "status": "blocked",
            "classification": "output_reservation_failed",
            "count_control_evidence_complete": False,
            "records_retained": 0,
            "source_writing_stopped": True,
        }
        return 1, receipt

    output_write_failed = False
    try:
        if not config.execute:
            receipt["accounting"]["campaign_source_operation_count"] = 0
            receipt["result"] = {
                "status": "not_run",
                "classification": "dry_run",
                "count_control_evidence_complete": False,
                "records_retained": 0,
                "source_writing_stopped": True,
            }
        else:
            receipt["accounting"]["campaign_source_operation_count"] = 1
            try:
                calls = dict(adapter_calls) if adapter_calls is not None else load_default_adapters(config.adapter_directory)
                if set(calls) != set(DATABASES) or any(
                    not callable(calls[database]) for database in DATABASES
                ):
                    raise RuntimeError("paired adapter call set is invalid")
            except Exception:
                receipt["result"] = {
                    "status": "blocked",
                    "classification": "adapter_entrypoint_unavailable",
                    "count_control_evidence_complete": False,
                    "records_retained": 0,
                    "source_writing_stopped": True,
                }
            else:
                all_accepted = True
                for index, database in enumerate(DATABASES):
                    if index:
                        try:
                            sleeper(config.inter_database_delay_seconds)
                        except Exception:
                            receipt["database_requests"][index] = _not_run_request(
                                config.attempt_id,
                                database,
                                "pacing_failed_before_request",
                                operation_id,
                            )
                            all_accepted = False
                            break
                    receipt["accounting"]["database_requests_performed"] += 1
                    try:
                        adapter_result = calls[database](
                            query.text,
                            **_call_kwargs(config),
                        )
                        request, accepted = _summarize_adapter_result(
                            database, adapter_result
                        )
                    except Exception as error:
                        request = _failure_request(
                            config.attempt_id, database, error, operation_id
                        )
                        accepted = False
                    request["request_id"] = (
                        f"{config.attempt_id}:{operation_id}:{database}"
                    )
                    receipt["database_requests"][index] = request
                    receipt["totals"][database] = request.get("total")
                    if not accepted:
                        all_accepted = False
                        if index == 0:
                            receipt["database_requests"][1] = _not_run_request(
                                config.attempt_id,
                                DATABASES[1],
                                "paired_event_stopped_after_first_request",
                                operation_id,
                            )
                        break

                receipt["result"] = {
                    "status": "complete" if all_accepted else "blocked",
                    "classification": "paired_count_control_diagnostic_complete"
                    if all_accepted
                    else "paired_count_control_diagnostic_blocked",
                    "count_control_evidence_complete": all_accepted,
                    "records_retained": 0,
                    "source_writing_stopped": True,
                }
    finally:
        try:
            write_reserved_json(reservation, receipt)
        except Exception:
            output_write_failed = True

    if output_write_failed:
        return 2, receipt
    return (0 if receipt["result"]["status"] in {"complete", "not_run"} else 1), receipt


def parse_args(argv: list[str] | None = None) -> PairedDiagnosticConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="permit the two diagnostic adapter requests"
    )
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--query-file", required=True)
    parser.add_argument("--pilot-date", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument(
        "--adapter-page-delay-seconds",
        type=float,
        default=DEFAULT_ADAPTER_PAGE_DELAY_SECONDS,
    )
    parser.add_argument(
        "--inter-database-delay-seconds",
        type=float,
        default=DEFAULT_INTER_DATABASE_DELAY_SECONDS,
    )
    parser.add_argument("--adapter-dir", default=str(ADAPTER_DIRECTORY))
    args = parser.parse_args(argv)
    try:
        return validate_config(
            PairedDiagnosticConfig(
                execute=args.execute,
                attempt_id=args.attempt_id,
                cdp_url=args.cdp_url,
                query_file=Path(args.query_file),
                pilot_date=validate_pilot_date(args.pilot_date),
                output_path=Path(args.output_path),
                timeout_seconds=args.timeout_seconds,
                adapter_page_delay_seconds=args.adapter_page_delay_seconds,
                inter_database_delay_seconds=args.inter_database_delay_seconds,
                adapter_directory=Path(args.adapter_dir),
            )
        )
    except InputValidationError as error:
        parser.error(str(error))
    raise AssertionError("argparse.error did not exit")


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    try:
        status, _ = run_paired_diagnostic(config)
    except Exception:
        return 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
