#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""One bounded, aggregate-only X exploration of the ProQuest ATAI surface.

The script is an exploration client, not a search adapter or a pilot.  It is
safe to run without a browser: the default is a create-only dry-run receipt.
The only live mode is intended to be the child of the canonical shared lease:

    caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \\
      --owner "$X_OWNER" --source proquest-atai --receipt "$LEASE_RECEIPT" \\
      --lease-timeout 900 -- uv run SLR/SLR1/scripts/proquest_atai_exploration.py \\
      --execute --timeout-seconds 30 --output-path "$RESTRICTED/atai-x-receipt.json"

The runner never launches a browser, chooses a profile, accepts a target ID,
or changes the endpoint.  Live mode attaches to the already-leased loopback
Chrome, creates exactly one distinct page, uses only normal visible ProQuest
controls, and permits one native query submit.  It retains no record, page
text, URL, target ID, session value, or exception string.  The receipt contains
only fixed-stage status, control booleans, aggregate counts, and hashes of the
fixed query/database-state projections.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_CDP_URL = "http://127.0.0.1:9222"
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_TIMEOUT_SECONDS = 30.0

SOURCE_ID = "proquest-atai"
SOURCE_LABEL = "Advanced Technologies & Aerospace Index"
ENTRY_SITE = "advancedtechaerospace"
SOURCE_SITE = "ataindex"
TARGET_DATABASE_LABEL = SOURCE_LABEL
DATABASE_SELECTION_ROUTE = "/advancedtechaerospace/databases/advanced"
COMMAND_LINE_ROUTES = frozenset({
    "/ataindex/commandline",
    "/ataindex/commandline/advanced",
})
DATABASE_SELECTION_URL = (
    "https://www.proquest.com/advancedtechaerospace/databases/advanced"
)
COMMAND_LINE_URL = "https://www.proquest.com/ataindex/commandline"
EXPECTED_HOST = "www.proquest.com"

BASE_QUERY = 'NOFT("CubeSat")'
SENTINEL_QUERY = BASE_QUERY
FIXED_COMMAND_QUERY = 'NOFT("CubeSat") AND YR(2011-2026) AND LA(English)'
EXECUTED_QUERY = FIXED_COMMAND_QUERY
QUERY_BYTES = FIXED_COMMAND_QUERY.encode("utf-8")
QUERY_SHA256 = hashlib.sha256(QUERY_BYTES).hexdigest()
QUERY_BASE_SHA256 = hashlib.sha256(BASE_QUERY.encode("utf-8")).hexdigest()
TOTAL_PATTERN = re.compile(r"^(\d[\d,]*)\s+results?$", re.IGNORECASE)
YR_PATTERN = re.compile(r"\bYR\(\s*(\d{4})\s*-\s*(\d{4})\s*\)", re.IGNORECASE)
LA_PATTERN = re.compile(r"\bLA\(\s*([^()]+?)\s*\)", re.IGNORECASE)

# These are intentionally finite and closed.  No exception text is permitted
# to become a source receipt value.
STAGES = frozenset(
    {
        "input_validation",
        "output_reservation",
        "adapter_load",
        "adapter_contract",
        "browser_attach",
        "baseline_inventory",
        "owned_page_creation",
        "database_route",
        "database_snapshot",
        "database_selection",
        "database_selection_submit",
        "product_route",
        "command_line_route",
        "form_controls",
        "native_submit",
        "result_state",
        "restoration",
        "cleanup",
        "cancellation",
        "output_write",
    }
)

# The hash constants are an additional guard against accidental query drift.
if (
    BASE_QUERY.count('NOFT("CubeSat")') != 1
    or FIXED_COMMAND_QUERY.count('NOFT("CubeSat")') != 1
    or len(YR_PATTERN.findall(FIXED_COMMAND_QUERY)) != 1
    or len(LA_PATTERN.findall(FIXED_COMMAND_QUERY)) != 1
    or QUERY_SHA256 != "28c39d7a26216eb6965afd78d198e4a8b8e2f88efc7383287695554cd6b78257"
):
    raise RuntimeError("fixed ProQuest ATAI exploration query invariant failed")


class InputValidationError(ValueError):
    """Raised before any browser or source operation."""


class StageFailure(RuntimeError):
    """Internal failure carrying only one closed stage name."""

    def __init__(self, stage: str):
        if stage not in STAGES:
            stage = "adapter_contract"
        self.stage = stage
        super().__init__(stage)


@dataclass(frozen=True)
class ExplorationConfig:
    execute: bool
    cdp_url: str
    timeout_seconds: float
    output_path: Path


@dataclass(frozen=True)
class DatabaseLabelState:
    """Complete visible database-label/check state, with no element IDs."""

    entries: tuple[tuple[str, bool], ...]

    @property
    def labels(self) -> frozenset[str]:
        return frozenset(label for label, _ in self.entries)

    @property
    def selected_labels(self) -> frozenset[str]:
        return frozenset(label for label, checked in self.entries if checked)

    @property
    def complete(self) -> bool:
        return bool(self.entries) and len(self.labels) == len(self.entries)


@dataclass
class OutputReservation:
    path: Path
    descriptor: int


def _validate_fixed_query(value: str) -> str:
    if value != FIXED_COMMAND_QUERY:
        raise InputValidationError("fixed ATAI command query invariant failed")
    if value.count('NOFT("CubeSat")') != 1:
        raise InputValidationError("fixed ATAI sentinel must occur once")
    years = YR_PATTERN.findall(value)
    languages = LA_PATTERN.findall(value)
    if years != [("2011", "2026")] or languages != ["English"]:
        raise InputValidationError("fixed ATAI date/language clauses must occur once")
    return value


def validate_cdp_url(value: Any) -> str:
    if type(value) is not str or value != DEFAULT_CDP_URL:
        raise InputValidationError(f"--cdp-url must be exactly {DEFAULT_CDP_URL}")
    return DEFAULT_CDP_URL


def validate_timeout(value: Any) -> float:
    if isinstance(value, bool):
        raise InputValidationError("--timeout-seconds must be finite and positive")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise InputValidationError(
            "--timeout-seconds must be finite and positive"
        ) from error
    if not math.isfinite(parsed) or parsed <= 0 or parsed > MAX_TIMEOUT_SECONDS:
        raise InputValidationError(
            "--timeout-seconds must be finite and no greater than 30"
        )
    return parsed


def validate_output_path(value: Any) -> Path:
    if isinstance(value, Path):
        candidate = value.expanduser()
    elif type(value) is str and value.strip():
        candidate = Path(value).expanduser()
    else:
        raise InputValidationError("--output-path must be a nonblank path")
    try:
        candidate_exists = candidate.exists() or candidate.is_symlink()
    except OSError as error:
        raise InputValidationError("--output-path cannot be inspected safely") from error
    if candidate_exists:
        raise InputValidationError("--output-path must be new and create-only")
    try:
        resolved = candidate.resolve(strict=False)
        resolved_exists = resolved.exists() or resolved.is_symlink()
    except (OSError, RuntimeError) as error:
        raise InputValidationError("--output-path cannot be resolved safely") from error
    if resolved_exists:
        raise InputValidationError("--output-path must be new and create-only")
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise InputValidationError("--output-path parent is unavailable") from error
    if not resolved.parent.is_dir():
        raise InputValidationError("--output-path parent is not a directory")
    return resolved


def validate_config(config: Any) -> ExplorationConfig:
    if not isinstance(config, ExplorationConfig) or type(config.execute) is not bool:
        raise InputValidationError("runtime exploration configuration is invalid")
    if not isinstance(config.output_path, Path):
        raise InputValidationError("runtime exploration configuration is invalid")
    return ExplorationConfig(
        execute=config.execute,
        cdp_url=validate_cdp_url(config.cdp_url),
        timeout_seconds=validate_timeout(config.timeout_seconds),
        output_path=validate_output_path(config.output_path),
    )


def reserve_output_path(path: Path) -> OutputReservation:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    return OutputReservation(path=path, descriptor=descriptor)


def write_reserved_json(
    reservation: OutputReservation, payload: Mapping[str, Any]
) -> None:
    descriptor = reservation.descriptor
    if descriptor < 0:
        raise OSError("output reservation is closed")
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


def _state_from_option(option: Any) -> tuple[str, bool]:
    label = getattr(option, "label", None)
    checked = getattr(option, "checked", None)
    if type(label) is not str or not label.strip() or type(checked) is not bool:
        raise StageFailure("database_snapshot")
    return label.strip(), checked


def freeze_database_label_state(options: Iterable[Any]) -> DatabaseLabelState:
    """Canonicalize every visible label and its checked state, rejecting gaps."""
    entries = [_state_from_option(option) for option in options]
    labels = [label for label, _ in entries]
    if not entries or len(set(labels)) != len(labels):
        raise StageFailure("database_snapshot")
    return DatabaseLabelState(tuple(sorted(entries, key=lambda item: item[0])))


def database_state_digest(state: DatabaseLabelState) -> str:
    encoded = json.dumps(
        list(state.entries), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _state_summary(state: DatabaseLabelState | None) -> dict[str, Any]:
    if state is None:
        return {
            "complete": False,
            "label_count": None,
            "selected_label_count": None,
            "target_selected": False,
            "state_sha256": None,
        }
    return {
        "complete": state.complete,
        "label_count": len(state.entries),
        "selected_label_count": len(state.selected_labels),
        "target_selected": state.selected_labels == frozenset({TARGET_DATABASE_LABEL}),
        "state_sha256": database_state_digest(state),
    }


def _empty_receipt(config: ExplorationConfig) -> dict[str, Any]:
    return {
        "schema_version": "slr1-proquest-atai-exploration/v1",
        "mode": "x_exploration" if config.execute else "dry_run",
        "diagnostic_only": True,
        "screening_performed": False,
        "candidate_import_permitted": False,
        "source_id": SOURCE_ID,
        "source_label": SOURCE_LABEL,
        "endpoint_class": "explicit_loopback_cdp",
        "operation": "one_owned_page_one_native_submit_max",
        "frozen_blockers": [
            "no_record_retrieval_or_completeness_claim",
            "no_native_export",
            "no_controlled_vocabulary_claim",
            "no_screening_or_candidate_import",
        ],
        "retention_exclusions": [
            "query_text",
            "record",
            "record_text",
            "body_text",
            "html",
            "browser_url",
            "opaque_result_route",
            "target_id",
            "session_or_search_identifier",
            "cookie",
            "credential",
            "exception_string",
        ],
        "query": {
            "base_sha256": QUERY_BASE_SHA256,
            "executed_sha256": QUERY_SHA256,
            "utf8_bytes": len(QUERY_BYTES),
            "text_retained": False,
            "year_start": 2011,
            "year_end": 2026,
            "language": "English",
            "sentinel_occurrences": 1,
            "year_clause_occurrences": 1,
            "language_clause_occurrences": 1,
        },
        "bounds": {
            "owned_pages_maximum": 1,
            "native_query_submits_maximum": 1,
            "source_operations_maximum": 1,
            "records_retrieved": 0,
            "records_retained": 0,
            "native_export": False,
        },
        "ownership": {
            "existing_context_count": None,
            "baseline_page_count": None,
            "owned_page_created": False,
            "owned_page_distinct_from_baseline": False,
            "owned_target_verified": False,
            "owned_page_close_attempted": False,
            "owned_page_closed": False,
            "owned_target_disappeared": False,
            "baseline_pages_preserved": None,
            "baseline_target_set_preserved": None,
            "cleanup_verified": False,
        },
        "selection": {
            "database_route_verified": False,
            "snapshot_captured": False,
            "snapshot_complete": False,
            "snapshot_label_count": None,
            "snapshot_selected_label_count": None,
            "snapshot_state_sha256": None,
            "deliberate_state_captured": False,
            "deliberate_state_complete": False,
            "deliberate_state_sha256": None,
            "exact_target_selected": False,
            "restoration_guard_passed": False,
            "restoration_attempted": False,
            "restoration_verified": False,
            "restoration_status": "not_required",
        },
        "controls": {
            "database_selection_controls_validated": False,
            "database_selection_submit_control": False,
            "product_route_verified": False,
            "command_line_route_verified": False,
            "result_controls_validated": False,
            "result_control_count": 0,
            "limiter_controls_validated": False,
            "query_field_validated": False,
            "query_readback_sha256_match": False,
            "date_clause_exact": False,
            "language_clause_exact": False,
            "native_submit_control_validated": False,
        },
        "submission": {
            "database_selection_submit_count": 0,
            "restoration_selection_submit_count": 0,
            "native_submit_count": 0,
            "source_operation_count": 0,
            "reissued": False,
            "one_native_submit_max": True,
        },
        "result": {
            "status": "not_run",
            "classification": "not_run",
            "total": None,
            "source_reported_total": None,
            "total_is_exact": False,
            "native_zero": None,
            "explicit_native_zero": None,
            "records_retrieved": 0,
            "records_retained": 0,
            "record_text_retained": False,
        },
        "error_stage": None,
        "terminal": {
            "status": "not_run" if not config.execute else "pending",
            "classification": "dry_run" if not config.execute else "pending",
            "failure_stage": None,
        },
    }


def _mark_blocked(receipt: dict[str, Any], stage: str) -> None:
    if stage not in STAGES:
        stage = "adapter_contract"
    receipt["error_stage"] = stage
    receipt["terminal"].update(
        {"status": "blocked", "classification": stage, "failure_stage": stage}
    )
    receipt["result"].update(
        {
            "status": "blocked",
            "classification": stage,
            "total": None,
            "source_reported_total": None,
            "total_is_exact": False,
            "native_zero": None,
            "explicit_native_zero": None,
        }
    )


def _mark_complete(receipt: dict[str, Any], total: int, native_zero: bool) -> None:
    classification = "native_zero_observed" if native_zero else "aggregate_total_observed"
    receipt["result"].update(
        {
            "status": "complete",
            "classification": classification,
            "total": total,
            "source_reported_total": total,
            "total_is_exact": True,
            "native_zero": native_zero,
            "explicit_native_zero": native_zero,
        }
    )
    receipt["error_stage"] = None
    receipt["terminal"].update(
        {"status": "complete", "classification": classification, "failure_stage": None}
    )


def _mark_dry_run(receipt: dict[str, Any]) -> None:
    receipt["terminal"].update(
        {"status": "not_run", "classification": "dry_run", "failure_stage": None}
    )
    receipt["error_stage"] = None
    receipt["result"].update(
        {
            "status": "not_run",
            "classification": "dry_run",
            "total": None,
            "source_reported_total": None,
            "native_zero": None,
            "explicit_native_zero": None,
        }
    )


def load_adapter(path: Path | None = None) -> Any:
    adapter_path = (
        path
        if path is not None
        else Path(
            "~/agent-tools/academic-research/skills/academic-search/scripts/"
            "search_proquest_aerospace.py"
        )
    ).expanduser()
    if not adapter_path.is_file():
        raise StageFailure("adapter_load")
    spec = importlib.util.spec_from_file_location("slr1_atai_exploration_adapter", adapter_path)
    if spec is None or spec.loader is None:
        raise StageFailure("adapter_load")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise StageFailure("adapter_load") from error
    return module


def _validate_adapter_contract(adapter: Any) -> None:
    expected = {
        "SOURCE_NAME": SOURCE_LABEL,
        "ENTRY_SITE": ENTRY_SITE,
        "SOURCE_SITE": SOURCE_SITE,
        "TARGET_DATABASE_LABEL": TARGET_DATABASE_LABEL,
        "DATABASE_SELECTION_URL": DATABASE_SELECTION_URL,
        "COMMAND_LINE_URL": COMMAND_LINE_URL,
    }
    if any(getattr(adapter, key, object()) != value for key, value in expected.items()):
        raise StageFailure("adapter_contract")
    required_callables = (
        "navigate",
        "wait_for_database_selection_route",
        "dismiss_ephemeral_cookie_dialog",
        "ensure_aerospace_hierarchy_expanded",
        "read_database_options",
        "set_database_selection",
        "submit_database_selection",
        "wait_for_exact_index_route",
        "configure_result_options",
        "result_option_snapshot_from_payload",
        "limiter_evidence_from_payload",
    )
    if any(not callable(getattr(adapter, name, None)) for name in required_callables):
        raise StageFailure("adapter_contract")
    if not isinstance(getattr(adapter, "RESULT_OPTIONS_STATE_SCRIPT", None), str):
        raise StageFailure("adapter_contract")
    common = getattr(adapter, "_common", None)
    if common is None or not all(
        callable(getattr(common, name, None))
        for name in (
            "open_chrome_connection",
            "new_owned_chrome_page",
            "close_owned_chrome_page_only_verified",
            "_target_id_for_page",
        )
    ):
        raise StageFailure("adapter_contract")


def _page_is_closed(page: Any) -> bool:
    checker = getattr(page, "is_closed", None)
    if not callable(checker):
        return False
    try:
        return bool(checker())
    except Exception as error:
        raise StageFailure("baseline_inventory") from error


async def _target_id(common: Any, page: Any) -> str:
    try:
        value = await common._target_id_for_page(page)
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("baseline_inventory") from error
    if type(value) is not str or not value:
        raise StageFailure("baseline_inventory")
    return value


async def _inventory(common: Any, browser: Any, context: Any) -> tuple[tuple[Any, ...], frozenset[str]]:
    try:
        contexts = tuple(browser.contexts)
        pages = tuple(context.pages)
    except Exception as error:
        raise StageFailure("baseline_inventory") from error
    if len(contexts) != 1 or contexts[0] is not context:
        raise StageFailure("baseline_inventory")
    if any(_page_is_closed(page) for page in pages):
        raise StageFailure("baseline_inventory")
    target_ids = []
    for page in pages:
        target_ids.append(await _target_id(common, page))
    if len(set(target_ids)) != len(target_ids):
        raise StageFailure("baseline_inventory")
    return pages, frozenset(target_ids)


async def _assert_owned_inventory(
    common: Any,
    browser: Any,
    context: Any,
    page: Any,
    baseline_pages: tuple[Any, ...],
    baseline_targets: frozenset[str],
    owned_target: str,
) -> None:
    pages, target_ids = await _inventory(common, browser, context)
    if not any(candidate is page for candidate in pages):
        raise StageFailure("owned_page_creation")
    if set(id(candidate) for candidate in pages) != {
        *[id(candidate) for candidate in baseline_pages],
        id(page),
    }:
        raise StageFailure("owned_page_creation")
    if target_ids != baseline_targets | {owned_target}:
        raise StageFailure("owned_page_creation")


def _assert_database_selection_route(page: Any) -> None:
    try:
        current = urlsplit(str(page.url))
    except Exception as error:
        raise StageFailure("database_route") from error
    if (
        current.scheme != "https"
        or current.hostname != EXPECTED_HOST
        or current.path != DATABASE_SELECTION_ROUTE
        or current.query
        or current.fragment
    ):
        raise StageFailure("database_route")


def _assert_clean_product_route(page: Any) -> None:
    try:
        current = urlsplit(str(page.url))
    except Exception as error:
        raise StageFailure("product_route") from error
    if (
        current.scheme != "https"
        or current.hostname != EXPECTED_HOST
        or not current.path.startswith(f"/{SOURCE_SITE}/")
        or current.query
        or current.fragment
    ):
        raise StageFailure("product_route")


async def _read_selection_state(
    adapter: Any,
    page: Any,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
) -> DatabaseLabelState:
    try:
        await reassert_owned()
        await adapter.wait_for_database_selection_route(
            page,
            source_site=ENTRY_SITE,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=reassert_owned,
        )
        await adapter.ensure_aerospace_hierarchy_expanded(
            page,
            timeout_seconds=timeout_seconds,
            source_site=ENTRY_SITE,
            ownership_reassertion=reassert_owned,
        )
        _assert_database_selection_route(page)
        await reassert_owned()
        options = await adapter.read_database_options(
            page, timeout_seconds=timeout_seconds
        )
        state = freeze_database_label_state(options)
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("database_snapshot") from error
    if not state.complete or TARGET_DATABASE_LABEL not in state.labels:
        raise StageFailure("database_snapshot")
    if not state.selected_labels:
        raise StageFailure("database_snapshot")
    return state


async def _navigate_and_snapshot_selection(
    adapter: Any,
    page: Any,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
) -> DatabaseLabelState:
    try:
        await reassert_owned()
        await adapter.navigate(page, DATABASE_SELECTION_URL, timeout_seconds)
        await adapter.wait_for_database_selection_route(
            page,
            source_site=ENTRY_SITE,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=reassert_owned,
        )
        await adapter.dismiss_ephemeral_cookie_dialog(page, attached_cdp=True)
        await reassert_owned()
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("database_route") from error
    return await _read_selection_state(
        adapter, page, timeout_seconds, reassert_owned
    )


async def _select_exact_target(
    adapter: Any,
    page: Any,
    snapshot: DatabaseLabelState,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
) -> DatabaseLabelState:
    try:
        before = await _read_selection_state(
            adapter, page, timeout_seconds, reassert_owned
        )
        if before != snapshot:
            raise StageFailure("database_selection")
        options = await adapter.read_database_options(
            page, timeout_seconds=timeout_seconds
        )
        for option in options:
            element_id = getattr(option, "element_id", None)
            if type(element_id) is not str or not element_id.startswith("dbcb_"):
                raise StageFailure("database_selection")
            checkbox = page.locator(f"#{element_id}:visible")
            if await checkbox.count() != 1 or not await checkbox.first.is_visible():
                raise StageFailure("database_selection")
        await adapter.set_database_selection(
            page,
            {TARGET_DATABASE_LABEL},
            timeout_seconds=timeout_seconds,
            source_site=ENTRY_SITE,
            ownership_reassertion=reassert_owned,
        )
        after = await _read_selection_state(
            adapter, page, timeout_seconds, reassert_owned
        )
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("database_selection") from error
    if after.labels != snapshot.labels:
        raise StageFailure("database_selection")
    if after.selected_labels != frozenset({TARGET_DATABASE_LABEL}):
        raise StageFailure("database_selection")
    return after


def _assert_command_line_route(page: Any) -> None:
    try:
        current = urlsplit(str(page.url))
    except Exception as error:
        raise StageFailure("command_line_route") from error
    if (
        current.scheme != "https"
        or current.hostname != EXPECTED_HOST
        or current.path not in COMMAND_LINE_ROUTES
        or current.query
        or current.fragment
    ):
        raise StageFailure("command_line_route")


async def _submit_selection_and_enter_command_line(
    adapter: Any,
    page: Any,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
    receipt: dict[str, Any],
) -> None:
    try:
        selection_button = page.locator("#submit_2:visible, #submit_4:visible")
        if (
            await selection_button.count() != 1
            or not await selection_button.first.is_visible()
            or not await selection_button.first.is_enabled()
        ):
            raise StageFailure("database_selection_submit")
        receipt["submission"]["database_selection_submit_count"] = 1
        await adapter.submit_database_selection(
            page,
            timeout_seconds,
            source_site=ENTRY_SITE,
            ownership_reassertion=reassert_owned,
        )
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("database_selection_submit") from error
    receipt["controls"]["database_selection_submit_control"] = True
    try:
        await reassert_owned()
        await adapter.wait_for_exact_index_route(
            page,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=reassert_owned,
        )
        _assert_clean_product_route(page)
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("product_route") from error
    receipt["controls"]["product_route_verified"] = True
    try:
        await adapter.navigate(page, COMMAND_LINE_URL, timeout_seconds)
        await adapter.wait_for_exact_index_route(
            page,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=reassert_owned,
        )
        _assert_command_line_route(page)
        await reassert_owned()
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("command_line_route") from error
    receipt["controls"]["command_line_route_verified"] = True


async def _read_form_control_state(adapter: Any, page: Any) -> tuple[Any, Any]:
    try:
        payload = await page.evaluate(adapter.RESULT_OPTIONS_STATE_SCRIPT)
        if (
            not isinstance(payload, Mapping)
            or payload.get("host") != EXPECTED_HOST
            or payload.get("blocked") is not False
            or payload.get("requiresAccess") is not False
        ):
            raise StageFailure("form_controls")
        snapshot = adapter.result_option_snapshot_from_payload(payload)
        limiter = adapter.limiter_evidence_from_payload(
            payload.get("limiterState") if isinstance(payload, Mapping) else None,
            complete_mode=True,
        )
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("form_controls") from error
    if not snapshot.is_frozen or len(snapshot.controls) != 6:
        raise StageFailure("form_controls")
    if limiter.residual_categories:
        raise StageFailure("form_controls")
    return snapshot, limiter


async def _validate_controls_and_submit(
    adapter: Any,
    page: Any,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
    receipt: dict[str, Any],
) -> None:
    try:
        await reassert_owned()
        _assert_command_line_route(page)
        command = adapter.build_command_query(
            BASE_QUERY,
            year_start=2011,
            year_end=2026,
            language="English",
        )
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("form_controls") from error
    if command != _validate_fixed_query(FIXED_COMMAND_QUERY):
        raise StageFailure("form_controls")
    receipt["controls"]["date_clause_exact"] = True
    receipt["controls"]["language_clause_exact"] = True

    try:
        await reassert_owned()
        await adapter.configure_result_options(
            page, timeout_seconds=timeout_seconds, complete_mode=True
        )
        await reassert_owned()
        _assert_command_line_route(page)
        snapshot, _limiter = await _read_form_control_state(adapter, page)
        receipt["controls"]["result_controls_validated"] = True
        receipt["controls"]["result_control_count"] = len(snapshot.controls)
        receipt["controls"]["limiter_controls_validated"] = True
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("form_controls") from error

    try:
        field = page.locator("#searchTerm")
        button = page.locator("#submit_7")
        if (
            await field.count() != 1
            or not await field.first.is_visible()
            or await button.count() != 1
            or not await button.first.is_visible()
            or not await button.first.is_enabled()
        ):
            raise StageFailure("form_controls")
        receipt["controls"]["query_field_validated"] = True
        receipt["controls"]["native_submit_control_validated"] = True
        await field.first.fill(command)
        readback = await field.first.input_value()
        if (
            readback != FIXED_COMMAND_QUERY
            or hashlib.sha256(readback.encode("utf-8")).hexdigest() != QUERY_SHA256
        ):
            raise StageFailure("form_controls")
        receipt["controls"]["query_readback_sha256_match"] = True
        await reassert_owned()
        _assert_command_line_route(page)
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("form_controls") from error

    if receipt["submission"]["native_submit_count"] != 0:
        raise StageFailure("native_submit")
    receipt["submission"]["native_submit_count"] = 1
    receipt["submission"]["source_operation_count"] = 1
    try:
        await button.first.click()
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("native_submit") from error


SENTINEL_RESULT_STATE_SCRIPT = r"""
(payload) => {
  const normalize = value => String(value || '').replace(/[\s\u200e\u200f]+/g, ' ').trim();
  const visible = element => Boolean(
    element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length)
  );
  const body = normalize(document.body && document.body.innerText);
  const lower = body.toLowerCase();
  const totalNodes = Array.from(document.querySelectorAll('#pqResultsCount')).filter(visible);
  const zeroNodes = Array.from(document.querySelectorAll('.pagingBoxNoResultMain, .error_message'))
    .filter(visible);
  const errors = Array.from(document.querySelectorAll('.error_message, [role="alert"]'))
    .filter(visible).map(element => normalize(element.textContent)).filter(Boolean);
  const zeroResults = zeroNodes.some(element => /found\s+0\s+results?/i.test(normalize(element.textContent)));
  const syntaxError = errors.some(text =>
    !/found\s+0\s+results?/i.test(text) && /syntax|invalid|could not parse|search error/i.test(text)
  );
  const queryFields = Array.from(document.querySelectorAll('#searchTerm')).filter(visible);
  const productLinks = Array.from(document.querySelectorAll(
    "a[aria-label='Advanced Technologies & Aerospace Index Product Home page']"
  )).filter(visible);
  const rows = Array.from(document.querySelectorAll('#lor_container .item.clearfix')).filter(visible);
  const resultMatch = String(window.location.pathname || '').match(/^\/ataindex\/results\/[^/]+\/(\d+)$/i);
  const blocked = ['captcha', 'verify you are human', 'access denied', 'unusual traffic', 'cloudflare']
    .some(marker => lower.includes(marker));
  const requiresAccess = /authentication error|institutional access required|session has expired/i.test(body) ||
    /\/(?:login|signin)(?:\/|$)/i.test(window.location.pathname);
  const totalText = totalNodes.length === 1 ? normalize(totalNodes[0].textContent) : '';
  return {
    protocol: window.location.protocol,
    host: window.location.hostname,
    titleExact: document.title.includes('Advanced Technologies & Aerospace Index'),
    productLinkExact: productLinks.length === 1,
    queryFieldCount: queryFields.length,
    queryMatches: queryFields.length === 1 && normalize(queryFields[0].value) === normalize(payload.query),
    resultRoute: Boolean(resultMatch),
    routeClean: Boolean(resultMatch) && !window.location.search && !window.location.hash,
    pageOrdinal: resultMatch ? Number(resultMatch[1]) : null,
    totalNodeCount: totalNodes.length,
    totalText,
    zeroResults,
    rowCount: rows.length,
    syntaxError,
    blocked,
    requiresAccess,
    ready: blocked || requiresAccess || zeroResults || syntaxError || (totalNodes.length === 1 && Boolean(totalText))
  };
}
"""


def _parse_aggregate_result(payload: Any) -> tuple[int, bool]:
    if not isinstance(payload, Mapping):
        raise StageFailure("result_state")
    if (
        payload.get("protocol") != "https:"
        or payload.get("host") != EXPECTED_HOST
        or payload.get("titleExact") is not True
        or payload.get("productLinkExact") is not True
        or payload.get("queryFieldCount") != 1
        or payload.get("queryMatches") is not True
        or payload.get("resultRoute") is not True
        or payload.get("routeClean") is not True
        or payload.get("pageOrdinal") != 1
        or payload.get("blocked") is not False
        or payload.get("requiresAccess") is not False
        or payload.get("syntaxError") is not False
    ):
        raise StageFailure("result_state")
    row_count = payload.get("rowCount")
    if isinstance(row_count, bool) or not isinstance(row_count, int) or row_count < 0:
        raise StageFailure("result_state")
    if payload.get("zeroResults") is True:
        if payload.get("totalNodeCount") != 0 or payload.get("totalText") or row_count != 0:
            raise StageFailure("result_state")
        return 0, True
    if payload.get("zeroResults") is not False or payload.get("totalNodeCount") != 1:
        raise StageFailure("result_state")
    total_text = payload.get("totalText")
    if type(total_text) is not str:
        raise StageFailure("result_state")
    match = TOTAL_PATTERN.fullmatch(total_text)
    if match is None:
        raise StageFailure("result_state")
    total = int(match.group(1).replace(",", ""))
    if total < 1 or row_count != min(20, total):
        raise StageFailure("result_state")
    return total, False


async def _wait_for_aggregate_result(
    page: Any,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
) -> tuple[int, bool]:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while True:
        try:
            await reassert_owned()
            payload = await page.evaluate(
                SENTINEL_RESULT_STATE_SCRIPT, {"query": FIXED_COMMAND_QUERY}
            )
            if not isinstance(payload, Mapping):
                raise StageFailure("result_state")
            if payload.get("ready") is True:
                return _parse_aggregate_result(payload)
        except StageFailure:
            raise
        except Exception as error:
            # A document replacement is allowed to settle inside the same
            # bounded observation window; no click, reload, or source reissue
            # is performed here.
            if asyncio.get_running_loop().time() >= deadline:
                raise StageFailure("result_state") from error
        if asyncio.get_running_loop().time() >= deadline:
            raise StageFailure("result_state")
        await asyncio.sleep(min(0.1, deadline - asyncio.get_running_loop().time()))


async def _restore_selection_if_guarded(
    adapter: Any,
    page: Any,
    snapshot: DatabaseLabelState,
    deliberate: DatabaseLabelState,
    timeout_seconds: float,
    reassert_owned: Callable[[], Any],
    receipt: dict[str, Any],
) -> bool:
    """Restore only after complete current state equals our deliberate state."""
    try:
        await adapter.navigate(page, DATABASE_SELECTION_URL, timeout_seconds)
        await adapter.wait_for_database_selection_route(
            page,
            source_site=ENTRY_SITE,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=reassert_owned,
        )
        await adapter.ensure_aerospace_hierarchy_expanded(
            page,
            timeout_seconds=timeout_seconds,
            source_site=ENTRY_SITE,
            ownership_reassertion=reassert_owned,
        )
        current = await _read_selection_state(
            adapter, page, timeout_seconds, reassert_owned
        )
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("restoration") from error
    if current != deliberate:
        receipt["selection"]["restoration_status"] = "not_attempted_state_changed"
        return False
    receipt["selection"]["restoration_guard_passed"] = True
    receipt["selection"]["restoration_attempted"] = True
    try:
        await adapter.set_database_selection(
            page,
            set(snapshot.selected_labels),
            timeout_seconds=timeout_seconds,
            source_site=ENTRY_SITE,
            ownership_reassertion=reassert_owned,
        )
        prepared = await _read_selection_state(
            adapter, page, timeout_seconds, reassert_owned
        )
        if prepared != snapshot:
            raise StageFailure("restoration")
        receipt["submission"]["restoration_selection_submit_count"] = 1
        await adapter.submit_database_selection(
            page,
            timeout_seconds,
            source_site=ENTRY_SITE,
            ownership_reassertion=reassert_owned,
        )
        await adapter.navigate(page, DATABASE_SELECTION_URL, timeout_seconds)
        await adapter.wait_for_database_selection_route(
            page,
            source_site=ENTRY_SITE,
            timeout_seconds=timeout_seconds,
            ownership_reassertion=reassert_owned,
        )
        restored = await _read_selection_state(
            adapter, page, timeout_seconds, reassert_owned
        )
    except StageFailure:
        raise
    except Exception as error:
        raise StageFailure("restoration") from error
    if restored != snapshot:
        raise StageFailure("restoration")
    receipt["selection"]["restoration_verified"] = True
    receipt["selection"]["restoration_status"] = "attempted_verified"
    return True


async def _cleanup_owned_page(
    common: Any,
    browser: Any | None,
    context: Any | None,
    page: Any | None,
    baseline_pages: tuple[Any, ...],
    baseline_targets: frozenset[str] | None,
    owned_target: str | None,
    owned_distinct: bool,
    receipt: dict[str, Any],
) -> bool:
    if browser is None or context is None or baseline_targets is None:
        return False
    if page is not None and owned_distinct:
        receipt["ownership"]["owned_page_close_attempted"] = True
        try:
            outcome = await common.close_owned_chrome_page_only_verified(page)
            receipt["ownership"]["owned_page_closed"] = bool(outcome.verified)
        except Exception:
            outcome = None
    else:
        outcome = None
    try:
        current_pages, current_targets = await _inventory(common, browser, context)
    except Exception:
        return False
    owned_disappeared = page is None or not any(
        candidate is page for candidate in current_pages
    )
    target_disappeared = (
        (page is None and owned_target is None)
        or (owned_target is not None and owned_target not in current_targets)
    )
    baseline_pages_preserved = all(
        any(candidate is baseline for candidate in current_pages)
        for baseline in baseline_pages
    )
    baseline_target_set_preserved = current_targets == baseline_targets
    receipt["ownership"].update(
        {
            "owned_target_disappeared": bool(
                owned_disappeared and target_disappeared
            ),
            "baseline_pages_preserved": baseline_pages_preserved,
            "baseline_target_set_preserved": baseline_target_set_preserved,
            "cleanup_verified": bool(
                owned_disappeared
                and target_disappeared
                and baseline_pages_preserved
                and baseline_target_set_preserved
            ),
        }
    )
    return bool(receipt["ownership"]["cleanup_verified"])


async def _execute_live(
    config: ExplorationConfig,
    receipt: dict[str, Any],
    *,
    adapter: Any,
    playwright_factory: Callable[[], Any] | None = None,
) -> None:
    current_stage = "adapter_contract"
    browser: Any | None = None
    context: Any | None = None
    page: Any | None = None
    connection: Any | None = None
    baseline_pages: tuple[Any, ...] = ()
    baseline_targets: frozenset[str] | None = None
    owned_target: str | None = None
    owned_distinct = False
    snapshot: DatabaseLabelState | None = None
    deliberate: DatabaseLabelState | None = None
    selection_changed = False
    primary_stage: str | None = None
    restoration_failed = False
    cleanup_ok = False
    aggregate: tuple[int, bool] | None = None

    _validate_adapter_contract(adapter)
    common = adapter._common
    if playwright_factory is None:
        try:
            from playwright.async_api import async_playwright

            playwright_factory = async_playwright
        except ImportError as error:  # pragma: no cover - uv supplies live dependency
            raise StageFailure("browser_attach") from error

    try:
        async with playwright_factory() as playwright:
            try:
                current_stage = "browser_attach"
                connection = await common.open_chrome_connection(
                    playwright,
                    cdp_url=DEFAULT_CDP_URL,
                    headless=False,
                    timeout_seconds=config.timeout_seconds,
                    chrome_executable=None,
                    require_single_cdp_context=True,
                )
                browser = connection.browser
                context = connection.context
                if (
                    getattr(connection, "attached_cdp", False) is not True
                    or getattr(connection, "owns_browser", True) is not False
                    or context is None
                ):
                    raise StageFailure("browser_attach")

                current_stage = "baseline_inventory"
                baseline_pages, baseline_targets = await _inventory(
                    common, browser, context
                )
                receipt["ownership"]["existing_context_count"] = 1
                receipt["ownership"]["baseline_page_count"] = len(baseline_pages)
                if not baseline_pages:
                    raise StageFailure("baseline_inventory")

                current_stage = "owned_page_creation"
                page = await common.new_owned_chrome_page(
                    context, timeout_seconds=config.timeout_seconds
                )
                receipt["ownership"]["owned_page_created"] = True
                owned_distinct = not any(candidate is page for candidate in baseline_pages)
                receipt["ownership"]["owned_page_distinct_from_baseline"] = owned_distinct
                if not owned_distinct:
                    raise StageFailure("owned_page_creation")
                owned_target = await _target_id(common, page)
                after_pages, after_targets = await _inventory(common, browser, context)
                if (
                    owned_target in baseline_targets
                    or after_targets != baseline_targets | {owned_target}
                    or set(id(candidate) for candidate in after_pages)
                    != {*[id(candidate) for candidate in baseline_pages], id(page)}
                ):
                    raise StageFailure("owned_page_creation")
                receipt["ownership"]["owned_target_verified"] = True

                async def reassert_owned() -> None:
                    if page is None or owned_target is None:
                        raise StageFailure("owned_page_creation")
                    await _assert_owned_inventory(
                        common,
                        browser,
                        context,
                        page,
                        baseline_pages,
                        baseline_targets,
                        owned_target,
                    )

                current_stage = "database_route"
                snapshot = await _navigate_and_snapshot_selection(
                    adapter, page, config.timeout_seconds, reassert_owned
                )
                receipt["selection"].update(
                    {
                        "database_route_verified": True,
                        "snapshot_captured": True,
                        "snapshot_complete": snapshot.complete,
                        "snapshot_label_count": len(snapshot.entries),
                        "snapshot_selected_label_count": len(snapshot.selected_labels),
                        "snapshot_state_sha256": database_state_digest(snapshot),
                    }
                )
                receipt["controls"]["database_selection_controls_validated"] = True

                current_stage = "database_selection"
                deliberate = await _select_exact_target(
                    adapter,
                    page,
                    snapshot,
                    config.timeout_seconds,
                    reassert_owned,
                )
                selection_changed = deliberate != snapshot
                receipt["selection"].update(
                    {
                        "deliberate_state_captured": True,
                        "deliberate_state_complete": deliberate.complete,
                        "deliberate_state_sha256": database_state_digest(deliberate),
                        "exact_target_selected": deliberate.selected_labels
                        == frozenset({TARGET_DATABASE_LABEL}),
                    }
                )
                if not receipt["selection"]["exact_target_selected"]:
                    raise StageFailure("database_selection")

                current_stage = "database_selection_submit"
                await _submit_selection_and_enter_command_line(
                    adapter,
                    page,
                    config.timeout_seconds,
                    reassert_owned,
                    receipt,
                )

                current_stage = "form_controls"
                await _validate_controls_and_submit(
                    adapter,
                    page,
                    config.timeout_seconds,
                    reassert_owned,
                    receipt,
                )

                current_stage = "result_state"
                aggregate = await _wait_for_aggregate_result(
                    page, config.timeout_seconds, reassert_owned
                )
                _mark_complete(receipt, aggregate[0], aggregate[1])
            except StageFailure as error:
                primary_stage = error.stage
            except asyncio.CancelledError:
                primary_stage = "cancellation"
            except BaseException:
                primary_stage = current_stage

            if selection_changed and snapshot is not None and deliberate is not None:
                current_stage = "restoration"
                try:
                    restored = await _restore_selection_if_guarded(
                        adapter,
                        page,
                        snapshot,
                        deliberate,
                        config.timeout_seconds,
                        reassert_owned,
                        receipt,
                    )
                    if not restored:
                        restoration_failed = True
                except StageFailure:
                    restoration_failed = True
                    receipt["selection"]["restoration_status"] = "attempted_failed"
                except BaseException:
                    restoration_failed = True
                    receipt["selection"]["restoration_status"] = "attempted_failed"
            elif selection_changed:
                restoration_failed = True
                receipt["selection"]["restoration_status"] = "guard_not_proven"
            else:
                receipt["selection"]["restoration_status"] = "not_required"

            current_stage = "cleanup"
            cleanup_ok = await _cleanup_owned_page(
                common,
                browser,
                context,
                page,
                baseline_pages,
                baseline_targets,
                owned_target,
                owned_distinct,
                receipt,
            )
    except asyncio.CancelledError:
        primary_stage = primary_stage or "cancellation"
    except StageFailure as error:
        primary_stage = primary_stage or error.stage
    except BaseException:
        primary_stage = primary_stage or current_stage

    if restoration_failed:
        primary_stage = "restoration"
    if not cleanup_ok:
        primary_stage = primary_stage or "cleanup"
    if primary_stage is not None:
        _mark_blocked(receipt, primary_stage)
    elif aggregate is None:
        _mark_blocked(receipt, "result_state")


def run_exploration(
    config: ExplorationConfig,
    *,
    adapter: Any | None = None,
    playwright_factory: Callable[[], Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Run dry mode or one injected/live exploration and write one receipt."""
    try:
        config = validate_config(config)
    except InputValidationError:
        fallback = config if isinstance(config, ExplorationConfig) else ExplorationConfig(
            execute=False,
            cdp_url=DEFAULT_CDP_URL,
            timeout_seconds=1.0,
            output_path=Path("invalid-atai-exploration-receipt.json"),
        )
        receipt = _empty_receipt(fallback)
        _mark_blocked(receipt, "input_validation")
        return 2, receipt

    receipt = _empty_receipt(config)
    try:
        reservation = reserve_output_path(config.output_path)
    except OSError:
        _mark_blocked(receipt, "output_reservation")
        return 1, receipt

    status = 0
    try:
        if not config.execute:
            _mark_dry_run(receipt)
        else:
            try:
                live_adapter = adapter if adapter is not None else load_adapter()
                asyncio.run(
                    _execute_live(
                        config,
                        receipt,
                        adapter=live_adapter,
                        playwright_factory=playwright_factory,
                    )
                )
            except StageFailure as error:
                _mark_blocked(receipt, error.stage)
            except BaseException:
                _mark_blocked(receipt, "browser_attach")
            status = 0 if receipt["terminal"]["status"] == "complete" else 1
    finally:
        try:
            write_reserved_json(reservation, receipt)
        except Exception:
            _mark_blocked(receipt, "output_write")
            status = 2
    return status, receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="permit one leased live exploration"
    )
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument(
        "--output-path", required=True, help="new aggregate receipt path"
    )
    # Kept hidden so a copied command cannot accidentally select another port.
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = validate_config(
            ExplorationConfig(
                execute=args.execute,
                cdp_url=args.cdp_url,
                timeout_seconds=args.timeout_seconds,
                output_path=Path(args.output_path).expanduser(),
            )
        )
    except InputValidationError as error:
        parser.error(str(error))
    status, receipt = run_exploration(config)
    terminal = receipt["terminal"]
    print(
        json.dumps(
            {
                "status": status,
                "classification": terminal["classification"],
                "failure_stage": terminal["failure_stage"],
            },
            sort_keys=True,
        )
    )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
