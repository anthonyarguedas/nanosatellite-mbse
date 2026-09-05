#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.60.0"]
# ///

"""Plan, execute, and assess final AIAA ARC direct searches."""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py"
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
PILOT009_PLAN = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/aiaa-arc/pilots/009/searches/event-plan.json"
)
PILOT009_ASSESSMENT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/aiaa-arc/pilots/009/searches/assessment.json"
)
PILOT009_VALIDATION = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/aiaa-arc/pilots/009/searches/validation-report.json"
)
PINNED_RUNTIME_DIAGNOSTIC = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/aiaa-arc/final-searches/diagnostics/post-failure-pinned-target-count-smoke.json"
)
ABSTRACT_READINESS_DIAGNOSTIC = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/aiaa-arc/final-searches/diagnostics/rendered-abstract-readiness.json"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/aiaa-arc/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

SOURCE = "AIAA Aerospace Research Central (ARC)"
SOURCE_ID = "aiaa_arc"
REVIEW_NAMESPACE = "main"
REVIEW_ID = "slr1-1.1-restart"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-aiaa-arc-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
CUTOFF = "2026-08-24"
LIMIT = 100
MAX_PAGES = 5
MAX_SOURCE_TOTAL = 100
PASSES = 2
TIMEOUT_SECONDS = 20.0
PROCESS_TIMEOUT_SECONDS = 900.0
INTER_EVENT_DELAY_SECONDS = 4.0
EXPECTED_ADAPTER_ID = "search_aiaa_arc"
EXPECTED_ADAPTER_VERSION = "6"
PLAYWRIGHT_VERSION = "1.60.0"
SCREENSHOT_SCHEMA = "aiaa-arc-automatic-screenshots/v1"
NATIVE_ABSTRACT_SOURCE = "native AIAA ARC RIS AB/N2"
NATIVE_PUBLICATION_TYPE_SOURCE = "native AIAA ARC RIS TY"

PLAN_SCHEMA = "slr1-aiaa-arc-final-direct-plan/v1"
RUN_SCHEMA = "slr1-aiaa-arc-final-direct-run/v1"
FAILURE_SCHEMA = "slr1-aiaa-arc-final-direct-runner-failure/v1"
CAPTURE_SCHEMA = "slr1-aiaa-arc-final-direct-cell-capture/v1"
CELL_DECLARATIONS_SCHEMA = "slr1-aiaa-arc-final-direct-cell-declarations/v1"
RECORD_UNION_SCHEMA = "slr1-aiaa-arc-final-direct-record-union/v1"
ASSESSMENT_SCHEMA = "slr1-aiaa-arc-final-direct-assessment/v1"
ABSTRACT_PLAN_SCHEMA = "slr1-aiaa-arc-final-abstract-follow-up-plan/v1"
ABSTRACT_RUN_SCHEMA = "slr1-aiaa-arc-final-abstract-follow-up-run/v1"
ABSTRACT_CAPTURE_SCHEMA = "slr1-aiaa-arc-final-abstract-capture/v1"
ABSTRACT_SOURCE_HTML = "native AIAA ARC rendered abstract page"
ABSTRACT_SOURCE_READER = "native AIAA ARC visible reader opening abstract block"
ABSTRACT_SOURCE_UNAVAILABLE = "not available after AIAA ARC RIS and rendered detail checks"

FIELD_TO_SOURCE_FIELD = {
    "Title": "Title",
    "Keywords": "Keyword",
    "Abstract": "Abstract",
    "Anywhere": "AllField",
}


class FinalAiaaArcError(RuntimeError):
    """A final AIAA ARC artifact does not meet its declared contract."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_ids(values: Sequence[str] | set[str]) -> str:
    hasher = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
    return hasher.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve(strict=False).relative_to(REPOSITORY_ROOT))


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise FinalAiaaArcError(f"Expected a regular file: {path}")


def load(path: Path) -> dict[str, Any]:
    require_regular(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalAiaaArcError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Any) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:  # pragma: no cover - operating-system invariant
                raise OSError(f"Could not write {path}")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def repository_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise FinalAiaaArcError("Cannot determine the repository revision")
    return value


def adapter_identity() -> dict[str, str]:
    require_regular(ADAPTER)
    source = ADAPTER.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for name in ("ADAPTER_ID", "ADAPTER_VERSION"):
        match = re.search(
            rf'^\s*{name}\s*=\s*["\']([^"\']+)["\']', source, re.MULTILINE
        )
        if match is None:
            raise FinalAiaaArcError(f"Could not read {name} from the AIAA ARC adapter")
        values[name] = match.group(1)
    if values["ADAPTER_ID"] != EXPECTED_ADAPTER_ID:
        raise FinalAiaaArcError("Unexpected AIAA ARC adapter identity")
    if values["ADAPTER_VERSION"] != EXPECTED_ADAPTER_VERSION:
        raise FinalAiaaArcError("The final AIAA ARC plan requires adapter v6")
    return {
        "id": values["ADAPTER_ID"],
        "version": values["ADAPTER_VERSION"],
        "sha256": digest(ADAPTER),
        "entrypoint": str(ADAPTER),
    }


def load_adapter() -> Any:
    require_regular(ADAPTER)
    name = "slr1_aiaa_arc_final_adapter"
    spec = importlib.util.spec_from_file_location(name, ADAPTER)
    if spec is None or spec.loader is None:
        raise FinalAiaaArcError("Could not load the AIAA ARC adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical_doi(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FinalAiaaArcError("AIAA ARC record lacks a DOI")
    return value.strip().casefold().split("@", 1)[0]


def serialized_rows(rows: Sequence[Mapping[str, Any]]) -> str:
    return " AND ".join(f"{row['field']}={row['text']}" for row in rows)


def accepted_wildcard_events() -> list[dict[str, Any]]:
    """Load and validate the 94 accepted Pilot 009 wildcard cells."""
    for path in (PILOT009_PLAN, PILOT009_ASSESSMENT, PILOT009_VALIDATION):
        require_regular(path)
    source_plan = load(PILOT009_PLAN)
    assessment = load(PILOT009_ASSESSMENT)
    validation = load(PILOT009_VALIDATION)
    candidate = source_plan.get("candidate", {})
    if (
        source_plan.get("schema_version") != "aiaa-arc-pilot009-wildcard-plan/v1"
        or source_plan.get("source") != SOURCE
        or source_plan.get("pair_count") != 94
        or source_plan.get("event_count") != 188
        or candidate.get("literal_fragment")
        != '"nanosatellite" OR "nanosatellites"'
        or candidate.get("wildcard_fragment") != "nanosatellit*"
        or candidate.get("wildcard_position") != "unquoted trailing asterisk"
        or candidate.get("replacement_scope")
        != (
            "Replace only the two unhyphenated nanosatellite singular/plural literals inside P. "
            "Keep nanosat, hyphenated, spaced, CubeSat, SmallSat, and small-satellite forms literal."
        )
    ):
        raise FinalAiaaArcError("The accepted Pilot 009 wildcard plan changed")
    if (
        assessment.get("schema_version")
        != "aiaa-arc-pilot009-wildcard-assessment/v1"
        or assessment.get("status") != "complete"
        or assessment.get("acceptance", {}).get("status") != "accepted"
        or assessment.get("acceptance", {}).get("accepted_wildcard") != "nanosatellit*"
        or assessment.get("overall_comparison", {}).get("sets_equal") is not True
        or assessment.get("overall_comparison", {}).get("wildcard_canonical_doi_count")
        != 119
        or validation.get("schema_version") != "aiaa-arc-pilot009-validation/v1"
        or validation.get("status") != "pass"
    ):
        raise FinalAiaaArcError("Pilot 009 acceptance evidence is incomplete")

    events = source_plan.get("events")
    pairs = source_plan.get("pair_ledger")
    if not isinstance(events, list) or not isinstance(pairs, list) or len(pairs) != 94:
        raise FinalAiaaArcError("Pilot 009 event declarations are incomplete")
    pair_ids = {
        item.get("pair_id")
        for item in pairs
        if isinstance(item, Mapping) and isinstance(item.get("pair_id"), str)
    }
    selected = [
        copy.deepcopy(item)
        for item in events
        if isinstance(item, Mapping) and item.get("variant") == "wildcard"
    ]
    if len(selected) != 94 or len({item.get("event_id") for item in selected}) != 94:
        raise FinalAiaaArcError("Pilot 009 lacks 94 unique wildcard cells")
    if {item.get("pair_id") for item in selected} != pair_ids:
        raise FinalAiaaArcError("Pilot 009 wildcard cells do not match its pair ledger")

    for item in selected:
        partition = item.get("partition")
        rows = item.get("field_rows")
        pair_id = item.get("pair_id")
        if partition not in PARTITIONS or not isinstance(pair_id, str) or not isinstance(rows, list):
            raise FinalAiaaArcError("Pilot 009 wildcard cell is malformed")
        wildcard_count = 0
        for row in rows:
            if not isinstance(row, Mapping):
                raise FinalAiaaArcError("Pilot 009 field row is malformed")
            field = row.get("field")
            source_field = row.get("source_field")
            text = row.get("text")
            if (
                field not in FIELD_TO_SOURCE_FIELD
                or source_field != FIELD_TO_SOURCE_FIELD[field]
                or not isinstance(text, str)
                or not text
            ):
                raise FinalAiaaArcError("Pilot 009 field-row mapping changed")
            wildcard_count += text.count("nanosatellit*")
            if '"nanosatellite" OR "nanosatellites"' in text:
                raise FinalAiaaArcError("Pilot 009 wildcard cell retained literal nanosatellites")
        if wildcard_count != 1:
            raise FinalAiaaArcError("Pilot 009 wildcard replacement is not isolated")
    return selected


def strategy_reference(sequence: int) -> str:
    if sequence < 1:
        raise ValueError("Final-run sequence must be positive")
    return f"slr1-aiaa-arc-main-direct-v{sequence}"


def expected_events(strategy_version: str, *, sequence: int = 1) -> list[dict[str, Any]]:
    source_events = accepted_wildcard_events()
    cell_counts = Counter(str(item["partition"]) for item in source_events)
    if dict(cell_counts) != {
        "A1": 9,
        "A2": 9,
        "A3": 9,
        "B1": 9,
        "B2": 9,
        "BG1": 1,
        "BG2": 36,
        "BC1": 3,
        "BT2": 9,
    }:
        raise FinalAiaaArcError("Accepted AIAA ARC cell counts changed")
    positions: Counter[str] = Counter()
    result: list[dict[str, Any]] = []
    for event_number, source_event in enumerate(source_events, start=1):
        partition = str(source_event["partition"])
        cell_id = str(source_event["pair_id"])
        positions[partition] += 1
        rows = [
            {
                "field": str(row["field"]),
                "source_field": str(row["source_field"]),
                "text": str(row["text"]),
            }
            for row in source_event["field_rows"]
        ]
        serialized = serialized_rows(rows)
        event_prefix = "final-main-aiaa-arc" if sequence == 1 else f"final-main-aiaa-arc-r{sequence:03d}"
        event = {
            "event_id": f"{event_prefix}-{event_number:03d}-{cell_id}",
            "parent_event_id": f"{event_prefix}-{partition}",
            "event_kind": "final",
            "review_namespace": REVIEW_NAMESPACE,
            "source_id": SOURCE_ID,
            "partition_id": partition,
            "cell_id": cell_id,
            "cell_number": positions[partition],
            "cell_count": cell_counts[partition],
            "route": source_event["route"],
            "accepted_pilot_event_id": source_event["event_id"],
            "accepted_pilot_pair_id": source_event["pair_id"],
            "field_rows": rows,
            "serialized_query": serialized,
            "serialized_query_sha256": digest_text(serialized),
            "wildcard": "nanosatellit*",
            "wildcard_occurrences": sum(row["text"].count("nanosatellit*") for row in rows),
            "output_filename": f"{cell_id}.json",
            "native_ris_directory": f"native-ris/{cell_id}",
            "capture_receipt": f"captures/{cell_id}.capture-receipt.json",
            "limit": LIMIT,
            "max_pages": MAX_PAGES,
            "max_source_total": MAX_SOURCE_TOTAL,
            "passes": PASSES,
            "timeout_seconds": TIMEOUT_SECONDS,
            "strategy_version": strategy_version,
        }
        result.append(event)
    return result


def binding_paths() -> tuple[Path, ...]:
    return (
        SCRIPT_PATH,
        PILOT009_PLAN,
        PILOT009_ASSESSMENT,
        PILOT009_VALIDATION,
        PINNED_RUNTIME_DIAGNOSTIC,
        ABSTRACT_READINESS_DIAGNOSTIC,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )


def build_plan(
    *,
    sequence: int = 1,
    superseded_plan: Path | None = None,
    superseded_receipt: Path | None = None,
) -> dict[str, Any]:
    if sequence < 1:
        raise ValueError("Final-run sequence must be positive")
    if sequence > 1 and (superseded_plan is None or superseded_receipt is None):
        raise ValueError("A corrective final plan requires the superseded plan and receipt")
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        require_regular(superseded_plan)
        require_regular(superseded_receipt)
    strategy_version = repository_head()
    adapter = adapter_identity()
    for path in binding_paths():
        require_regular(path)
    events = expected_events(strategy_version, sequence=sequence)
    plan = {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "final_run_sequence": sequence,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": REVIEW_ID,
        "event_kind": "final",
        "phase": PHASE,
        "strategy_reference": strategy_reference(sequence),
        "strategy_version": strategy_version,
        "cutoff": {
            "exact_common_cutoff": CUTOFF,
            "source_date_start": DATE_START,
            "source_date_end_inclusive": CUTOFF,
            "source_precision": "whole source months plus RIS exact-day validation",
            "boundary_policy": (
                "Query the inclusive source months, then retain only RIS records with a complete "
                "publication date from 2011-01-01 through 2026-08-24."
            ),
        },
        "accepted_translation": {
            "pilot": "009",
            "plan": relative(PILOT009_PLAN),
            "plan_sha256": digest(PILOT009_PLAN),
            "assessment": relative(PILOT009_ASSESSMENT),
            "assessment_sha256": digest(PILOT009_ASSESSMENT),
            "validation": relative(PILOT009_VALIDATION),
            "validation_sha256": digest(PILOT009_VALIDATION),
            "parent_route": "Pilot 007 hybrid metadata-anchored route",
            "cell_count": len(events),
            "partition_cell_counts": {
                partition: sum(event["partition_id"] == partition for event in events)
                for partition in PARTITIONS
            },
            "accepted_wildcard": {
                "literal_fragment": '"nanosatellite" OR "nanosatellites"',
                "replacement": "nanosatellit*",
                "scope": (
                    "One unquoted trailing wildcard replaces only the two unhyphenated "
                    "nanosatellite literals in each population block."
                ),
                "paired_current_route_cells": 94,
                "equal_pilot_schedule_doi_union": 119,
                "other_wildcards": False,
            },
        },
        "corrective_runtime_readiness": {
            "playwright_version": PLAYWRIGHT_VERSION,
            "execution": "uv run --with playwright==1.60.0 python <adapter>",
            "diagnostic": relative(PINNED_RUNTIME_DIAGNOSTIC),
            "diagnostic_sha256": digest(PINNED_RUNTIME_DIAGNOSTIC),
            "result": "source-observed count-only success with both mandatory screenshots",
            "source_total": load(PINNED_RUNTIME_DIAGNOSTIC).get("total"),
            "reason": (
                "Playwright 1.62.0 timed out after connecting its browser WebSocket while "
                "pinned releases through 1.60.0 initialized the same shared Chrome session."
            ),
        },
        "source_configuration": {
            "source_or_collection": "full AIAA Aerospace Research Central collection",
            "platform": "AIAA Aerospace Research Central",
            "url": "https://arc.aiaa.org/search/advanced",
            "field_route": (
                "Pilot 007 hybrid field-assignment cells using Title, Keywords, Abstract, "
                "and selected Anywhere rows"
            ),
            "access": "all",
            "language_filter": None,
            "publication_type_filter": None,
            "topic_filter": None,
            "publication_filter": None,
            "peer_review_filter": None,
            "full_text_filter": None,
            "controlled_vocabulary_supplement": None,
            "sort": "Date (ARC native control)",
            "source_month_partition_cap": MAX_SOURCE_TOTAL,
            "browser_authorization": "one explicit visibly loaded ARC Advanced Search target per cell",
        },
        "record_capture_contract": {
            "full_abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "native_source": NATIVE_ABSTRACT_SOURCE,
                "native_ris_field_required_for_every_retained_record": True,
                "source_omissions_allowed_only_with_rendered_detail_follow_up": True,
                "final_record_state": "full source abstract or explicit source-unavailable evidence",
                "snippet_substitution": False,
            },
            "source_publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "native_source": NATIVE_PUBLICATION_TYPE_SOURCE,
                "require_nonempty_for_every_retained_record": True,
                "source_filter_applied": None,
                "reviewer_coding": "Do not infer screening publication_type from source metadata.",
            },
            "native_ris": {
                "required": True,
                "visible_export": "per-record visible Citation and Abstract RIS form",
                "strict_passes": PASSES,
                "private_preservation": True,
                "raw_ris_publication": "native-ris/<query-id>/",
            },
            "source_stable_identifiers": {
                "required": True,
                "native_ids_retained": True,
                "canonical_doi_alias_reconciliation": (
                    "ARC @virtual_collection stable IDs map to the publication DOI "
                    "exported by both visible RIS forms"
                ),
                "within_source_duplicates_accounted": True,
            },
            "rendered_abstract_follow_up": {
                "required_for_blank_native_ris_abstracts": True,
                "readiness_diagnostic": relative(ABSTRACT_READINESS_DIAGNOSTIC),
                "readiness_diagnostic_sha256": digest(ABSTRACT_READINESS_DIAGNOSTIC),
                "routes": [
                    "normal rendered DOI abstract/full page",
                    "visible Read Now reader source abstract block",
                ],
                "one_capture_per_unique_canonical_doi": True,
                "source_unavailable_state_allowed": True,
                "summary_generation": False,
            },
        },
        "strict_contract": {
            "require_complete": True,
            "source_month_partitioning": True,
            "complete_passes": PASSES,
            "ordered_doi_passes_reconciled": True,
            "exact_source_control_readback": True,
            "automatic_screenshots_required": True,
            "terminal_arc_commit_marker_required": True,
            "native_ris_manifest_bound_to_marker": True,
            "canonical_doi_alias_reconciliation_required": True,
            "full_abstract_and_source_publication_type_capture_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_cell": True,
            "continue_after_cell_failure": True,
            "first_cell_runtime_and_capture_gate": sequence > 1,
            "retry_policy": "none after final-plan execution begins",
            "corrective_run_required_after_any_failure": True,
            "skip_full_abstracts": False,
            "source_publication_type_capture": True,
            "native_ris_retention": True,
            "inter_event_delay_seconds": INTER_EVENT_DELAY_SECONDS,
        },
        "adapter": adapter,
        "bindings": {"files": {relative(path): digest(path) for path in binding_paths()}},
        "partition_ids": list(PARTITIONS),
        "source_cell_count": len(events),
        "events": events,
    }
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        plan["supersession"] = {
            "superseded_plan": relative(superseded_plan),
            "superseded_plan_sha256": digest(superseded_plan),
            "superseded_run_receipt": relative(superseded_receipt),
            "superseded_run_receipt_sha256": digest(superseded_receipt),
            "reason": (
                (
                    "The initial final run failed before ARC executed a query because Playwright "
                    "could not initialize its browser-level CDP session under Playwright 1.62.0. "
                    "Use pinned Playwright 1.60.0 and an explicit, visibly loaded ARC authorization "
                    "target for every corrective source cell."
                )
                if sequence == 2
                else (
                    (
                        "The preceding corrective run proved complete source and publication-type "
                        "capture, but ARC omitted RIS AB/N2 values despite include=abs. Preserve the "
                        "native omission and require a separate rendered-detail abstract follow-up."
                    )
                    if sequence == 3
                    else (
                        "The preceding corrective run exposed ARC virtual-collection stable IDs "
                        "whose visible RIS forms export the same canonical publication DOI as the "
                        "normal issue card. Retain every source stable ID, collapse only those "
                        "source-proven aliases by canonical DOI, and account for each duplicate."
                    )
                )
            ),
            "prior_results_reused": False,
        }
    return plan


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    sequence = plan.get("final_run_sequence", 1)
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        errors.append("final_run_sequence")
        sequence = 1
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("event_kind") != "final"
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != strategy_reference(sequence)
    ):
        errors.append("identity")
    strategy_version = plan.get("strategy_version")
    if not isinstance(strategy_version, str) or re.fullmatch(r"[0-9a-f]{40}", strategy_version) is None:
        errors.append("strategy_version")
        strategy_version = ""
    if plan.get("repository_head_at_predeclaration") != strategy_version:
        errors.append("predeclaration_head")
    cutoff = plan.get("cutoff", {})
    if (
        cutoff.get("exact_common_cutoff") != CUTOFF
        or cutoff.get("source_date_start") != DATE_START
        or cutoff.get("source_date_end_inclusive") != CUTOFF
        or cutoff.get("source_precision") != "whole source months plus RIS exact-day validation"
    ):
        errors.append("cutoff")
    accepted = plan.get("accepted_translation", {})
    if (
        accepted.get("pilot") != "009"
        or accepted.get("plan") != relative(PILOT009_PLAN)
        or accepted.get("plan_sha256") != digest(PILOT009_PLAN)
        or accepted.get("assessment") != relative(PILOT009_ASSESSMENT)
        or accepted.get("assessment_sha256") != digest(PILOT009_ASSESSMENT)
        or accepted.get("validation") != relative(PILOT009_VALIDATION)
        or accepted.get("validation_sha256") != digest(PILOT009_VALIDATION)
        or accepted.get("cell_count") != 94
        or accepted.get("accepted_wildcard", {}).get("replacement") != "nanosatellit*"
        or accepted.get("accepted_wildcard", {}).get("other_wildcards") is not False
    ):
        errors.append("accepted_translation")
    readiness = plan.get("corrective_runtime_readiness", {})
    if (
        readiness.get("playwright_version") != PLAYWRIGHT_VERSION
        or readiness.get("diagnostic") != relative(PINNED_RUNTIME_DIAGNOSTIC)
        or readiness.get("diagnostic_sha256") != digest(PINNED_RUNTIME_DIAGNOSTIC)
        or readiness.get("source_total") != load(PINNED_RUNTIME_DIAGNOSTIC).get("total")
    ):
        errors.append("corrective_runtime_readiness")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("access") != "all"
        or configuration.get("language_filter") is not None
        or configuration.get("publication_type_filter") is not None
        or configuration.get("topic_filter") is not None
        or configuration.get("publication_filter") is not None
        or configuration.get("peer_review_filter") is not None
        or configuration.get("full_text_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
        or configuration.get("source_month_partition_cap") != MAX_SOURCE_TOTAL
        or configuration.get("browser_authorization")
        != "one explicit visibly loaded ARC Advanced Search target per cell"
    ):
        errors.append("source_configuration")
    capture = plan.get("record_capture_contract", {})
    if (
        capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("native_source") != NATIVE_ABSTRACT_SOURCE
        or capture.get("full_abstracts", {}).get(
            "native_ris_field_required_for_every_retained_record"
        )
        is not True
        or capture.get("full_abstracts", {}).get(
            "source_omissions_allowed_only_with_rendered_detail_follow_up"
        )
        is not True
        or capture.get("source_publication_types", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("native_source")
        != NATIVE_PUBLICATION_TYPE_SOURCE
        or capture.get("source_publication_types", {}).get("require_nonempty_for_every_retained_record")
        is not True
        or capture.get("native_ris", {}).get("required") is not True
        or capture.get("source_stable_identifiers", {}).get("required") is not True
        or capture.get("source_stable_identifiers", {}).get("native_ids_retained")
        is not True
        or capture.get("source_stable_identifiers", {}).get(
            "within_source_duplicates_accounted"
        )
        is not True
        or capture.get("rendered_abstract_follow_up", {}).get(
            "required_for_blank_native_ris_abstracts"
        )
        is not True
        or capture.get("rendered_abstract_follow_up", {}).get("readiness_diagnostic")
        != relative(ABSTRACT_READINESS_DIAGNOSTIC)
        or capture.get("rendered_abstract_follow_up", {}).get(
            "readiness_diagnostic_sha256"
        )
        != digest(ABSTRACT_READINESS_DIAGNOSTIC)
        or capture.get("rendered_abstract_follow_up", {}).get("summary_generation")
        is not False
    ):
        errors.append("record_capture_contract")
    execution_policy = plan.get("execution_policy", {})
    if (
        execution_policy.get("continue_after_cell_failure") is not True
        or execution_policy.get("first_cell_runtime_and_capture_gate") != (sequence > 1)
        or execution_policy.get("retry_policy")
        != "none after final-plan execution begins"
    ):
        errors.append("execution_policy")
    strict = plan.get("strict_contract", {})
    if any(
        strict.get(name) is not True
        for name in (
            "require_complete",
            "source_month_partitioning",
            "ordered_doi_passes_reconciled",
            "exact_source_control_readback",
            "automatic_screenshots_required",
            "terminal_arc_commit_marker_required",
            "native_ris_manifest_bound_to_marker",
            "canonical_doi_alias_reconciliation_required",
            "full_abstract_and_source_publication_type_capture_required",
        )
    ) or strict.get("complete_passes") != PASSES:
        errors.append("strict_contract")
    if plan.get("partition_ids") != list(PARTITIONS) or plan.get("source_cell_count") != 94:
        errors.append("partition_coverage")
    if sequence > 1:
        supersession = plan.get("supersession")
        if not isinstance(supersession, Mapping):
            errors.append("supersession")
        else:
            superseded_plan = REPOSITORY_ROOT / str(supersession.get("superseded_plan", ""))
            superseded_receipt = REPOSITORY_ROOT / str(
                supersession.get("superseded_run_receipt", "")
            )
            if (
                not superseded_plan.is_file()
                or superseded_plan.is_symlink()
                or supersession.get("superseded_plan_sha256") != digest(superseded_plan)
                or not superseded_receipt.is_file()
                or superseded_receipt.is_symlink()
                or supersession.get("superseded_run_receipt_sha256")
                != digest(superseded_receipt)
                or supersession.get("prior_results_reused") is not False
            ):
                errors.append("supersession")
    elif plan.get("supersession") is not None:
        errors.append("unexpected_supersession")
    if strategy_version:
        try:
            if plan.get("events") != expected_events(strategy_version, sequence=sequence):
                errors.append("events")
        except (OSError, ValueError, FinalAiaaArcError) as error:
            errors.append(f"events:{type(error).__name__}")
    if verify_bindings:
        try:
            if plan.get("adapter") != adapter_identity():
                errors.append("adapter")
        except (OSError, FinalAiaaArcError):
            errors.append("adapter")
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in files.items():
                path = REPOSITORY_ROOT / str(name)
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or not isinstance(expected_hash, str)
                    or digest(path) != expected_hash
                ):
                    errors.append(f"binding:{name}")
    return errors


def canonical_output_dir(output_dir: Path) -> Path:
    return output_dir.expanduser().resolve(strict=False)


def output_path(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return canonical_output_dir(output_dir) / str(event["output_filename"])


def native_ris_path(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return canonical_output_dir(output_dir) / str(event["native_ris_directory"])


def capture_receipt_path(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return canonical_output_dir(output_dir) / str(event["capture_receipt"])


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ARC_COMMIT.json")


def failure_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def runner_failure_path(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return canonical_output_dir(output_dir) / "failures" / f"{event['cell_id']}.runner-failure.json"


def screenshot_evidence(path: Path, screenshots: Any) -> tuple[bool, list[dict[str, Any]]]:
    receipt = screenshots if isinstance(screenshots, Mapping) else {}
    valid = bool(
        receipt.get("schema_version") == SCREENSHOT_SCHEMA
        and receipt.get("automatic") is True
        and receipt.get("same_directory_as_json") is True
    )
    rows: list[dict[str, Any]] = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path), strict=True):
        evidence = receipt.get(key)
        image_valid = False
        image_hash: str | None = None
        if image.is_file() and not image.is_symlink() and isinstance(evidence, Mapping):
            data = image.read_bytes()
            image_hash = hashlib.sha256(data).hexdigest()
            image_valid = bool(
                data.startswith(b"\x89PNG\r\n\x1a\n")
                and evidence.get("path") == image.name
                and evidence.get("sha256") == image_hash
                and isinstance(evidence.get("width"), int)
                and evidence.get("width", 0) > 0
                and isinstance(evidence.get("height"), int)
                and evidence.get("height", 0) > 0
                and evidence.get("browser_chrome_captured") is False
                and evidence.get("complete_page_url_retained") is False
                and evidence.get("session_identifiers_retained") is False
            )
        valid = valid and image_valid
        rows.append(
            {
                "kind": key,
                "path": image.name,
                "sha256": image_hash,
                "valid": image_valid,
            }
        )
    return valid, rows


def observed_rows_valid(strategy: Mapping[str, Any], event: Mapping[str, Any]) -> bool:
    observed = strategy.get("field_rows")
    expected = event.get("field_rows")
    if not isinstance(observed, list) or not isinstance(expected, list) or len(observed) != len(expected):
        return False
    for seen, wanted in zip(observed, expected, strict=True):
        if not isinstance(seen, Mapping) or not isinstance(wanted, Mapping):
            return False
        if (
            seen.get("field") != wanted.get("source_field")
            or seen.get("text") != wanted.get("text")
        ):
            return False
    return True


def record_capture_summary(rows: Any) -> tuple[bool, dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(rows, list):
        return False, {
            "retained_record_count": 0,
            "full_abstract_count": 0,
            "missing_full_abstract_count": 0,
            "source_publication_type_counts": {},
            "missing_source_publication_type_count": 0,
        }, []
    valid = True
    seen: set[str] = set()
    full_abstracts = 0
    missing_abstracts = 0
    missing_types = 0
    types: Counter[str] = Counter()
    captures: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            valid = False
            continue
        try:
            identifier = canonical_doi(row.get("paperId"))
        except FinalAiaaArcError:
            valid = False
            identifier = ""
        try:
            doi = canonical_doi(row.get("doi"))
        except FinalAiaaArcError:
            doi = ""
            valid = False
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if (
            not identifier
            or identifier != doi
            or identifier in seen
            or row.get("exactDateFilterStatus") != "included"
            or "publication_type" in row
        ):
            valid = False
        seen.add(identifier)
        if isinstance(abstract, str):
            if abstract.strip():
                full_abstracts += 1
            else:
                missing_abstracts += 1
        else:
            missing_abstracts += 1
            valid = False
        if isinstance(document_type, str) and document_type.strip():
            type_value = document_type.strip()
            types[type_value] += 1
        else:
            missing_types += 1
            valid = False
            type_value = ""
        if identifier:
            captures.append(
                {
                    "paper_id": identifier,
                    "abstract_characters": len(abstract) if isinstance(abstract, str) else 0,
                    "abstract_sha256": digest_text(abstract) if isinstance(abstract, str) else None,
                    "abstract_source": NATIVE_ABSTRACT_SOURCE,
                    "abstract_capture_status": (
                        "full_native_ris_abstract"
                        if isinstance(abstract, str) and abstract.strip()
                        else "native_ris_abstract_omitted_follow_up_required"
                    ),
                    "source_publication_type": type_value,
                    "source_publication_type_source": NATIVE_PUBLICATION_TYPE_SOURCE,
                    "document_type": type_value,
                }
            )
    summary = {
        "retained_record_count": len(rows),
        "full_abstract_count": full_abstracts,
        "missing_full_abstract_count": missing_abstracts,
        "source_publication_type_counts": dict(sorted(types.items())),
        "missing_source_publication_type_count": missing_types,
    }
    return valid, summary, captures


def inspect_native_ris(
    native_dir: Path,
    *,
    source_total: int,
    within_source_duplicates_removed: int,
    retained_rows: Sequence[Any],
) -> tuple[bool, dict[str, Any]]:
    """Reconcile raw RIS AB/N2 and TY values with the published JSON rows."""
    if native_dir.is_symlink() or not native_dir.is_dir():
        return False, {"error": "native_ris_directory_missing"}
    if (
        isinstance(source_total, bool)
        or not isinstance(source_total, int)
        or source_total < 0
        or isinstance(within_source_duplicates_removed, bool)
        or not isinstance(within_source_duplicates_removed, int)
        or within_source_duplicates_removed < 0
        or within_source_duplicates_removed > source_total
    ):
        return False, {"error": "native_ris_source_accounting_invalid"}
    expected_native_records = source_total - within_source_duplicates_removed
    files = sorted(native_dir.rglob("*"), key=lambda item: item.relative_to(native_dir).as_posix())
    regular_files: list[Path] = []
    for candidate in files:
        details = candidate.lstat()
        if candidate.is_symlink() or not (
            stat.S_ISDIR(details.st_mode) or stat.S_ISREG(details.st_mode)
        ):
            return False, {"error": "native_ris_tree_not_regular"}
        if stat.S_ISREG(details.st_mode):
            if candidate.stat().st_size <= 0:
                return False, {"error": "native_ris_file_invalid"}
            if candidate.suffix.casefold() == ".ris":
                regular_files.append(candidate)
            elif not (candidate.name.startswith(".") and candidate.suffix == ".tmp"):
                return False, {"error": "native_ris_file_invalid"}
    if expected_native_records == 0:
        return (not regular_files), {
            "native_ris_file_count": len(regular_files),
            "expected_native_record_count": expected_native_records,
            "raw_source_record_count": 0,
            "raw_full_abstract_count": 0,
            "raw_missing_full_abstract_count": 0,
            "raw_source_publication_type_counts": {},
            "raw_missing_source_publication_type_count": 0,
            "retained_rows_reconciled_to_native_ris": len(retained_rows) == 0,
            "native_records": {},
        }
    if not regular_files:
        return False, {"error": "native_ris_files_missing"}
    try:
        adapter = load_adapter()
    except Exception as error:  # noqa: BLE001 - preserve artifact assessment.
        return False, {"error": f"adapter_load:{type(error).__name__}"}
    native_records: dict[str, dict[str, Any]] = {}
    raw_full_abstracts = 0
    raw_missing_abstracts = 0
    raw_missing_types = 0
    raw_types: Counter[str] = Counter()
    try:
        for file_path in regular_files:
            for raw in adapter.parse_ris_records(file_path.read_text(encoding="utf-8")):
                doi = canonical_doi(adapter.ris_record_doi(raw))
                if doi in native_records:
                    return False, {"error": "native_ris_duplicate_doi"}
                normalized = adapter.normalize_ris_record(raw, doi)
                abstract = normalized.get("abstract")
                document_type = normalized.get("documentType")
                if isinstance(abstract, str) and abstract.strip():
                    raw_full_abstracts += 1
                else:
                    raw_missing_abstracts += 1
                if isinstance(document_type, str) and document_type.strip():
                    raw_types[document_type.strip()] += 1
                else:
                    raw_missing_types += 1
                native_records[doi] = normalized
    except Exception as error:  # noqa: BLE001 - source evidence must fail closed.
        return False, {"error": f"native_ris_parse:{type(error).__name__}"}
    retained_match = True
    for row in retained_rows:
        if not isinstance(row, Mapping):
            retained_match = False
            continue
        try:
            doi = canonical_doi(row.get("doi"))
        except FinalAiaaArcError:
            retained_match = False
            continue
        native = native_records.get(doi)
        if (
            native is None
            or native.get("abstract") != row.get("abstract")
            or native.get("documentType") != row.get("documentType")
        ):
            retained_match = False
    valid = bool(len(native_records) == expected_native_records and retained_match)
    return valid, {
        "native_ris_file_count": len(regular_files),
        "expected_native_record_count": expected_native_records,
        "raw_source_record_count": len(native_records),
        "raw_full_abstract_count": raw_full_abstracts,
        "raw_missing_full_abstract_count": raw_missing_abstracts,
        "raw_source_publication_type_counts": dict(sorted(raw_types.items())),
        "raw_missing_source_publication_type_count": raw_missing_types,
        "retained_rows_reconciled_to_native_ris": retained_match,
        "native_records": native_records,
    }


def committed_arc_publication_valid(path: Path, native_dir: Path) -> bool:
    try:
        adapter = load_adapter()
        return bool(adapter.is_committed_arc_publication(path, native_export_dir=native_dir))
    except Exception:  # noqa: BLE001 - a changed adapter must fail closed.
        return False


def base_artifact_summary(
    path: Path,
    native_dir: Path,
    event: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None, list[dict[str, Any]]]:
    """Validate one marker-bound source artifact before its capture receipt."""
    if path.is_symlink() or not path.is_file():
        return {"valid": False, "artifact_written": False}, None, []
    try:
        value = load(path)
    except (OSError, ValueError, json.JSONDecodeError, FinalAiaaArcError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }, None, []
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy")
    strategy = strategy if isinstance(strategy, Mapping) else {}
    limits = strategy.get("limits")
    limits = limits if isinstance(limits, Mapping) else {}
    coverage = prisma.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    adapter = prisma.get("adapter")
    adapter = adapter if isinstance(adapter, Mapping) else {}
    rows = value.get("results")
    record_valid, record_summary, captures = record_capture_summary(rows)
    screenshots_valid, screenshot_rows = screenshot_evidence(path, metadata.get("screenshots"))
    source_total = value.get("total")
    retained_count = len(rows) if isinstance(rows, list) else -1
    counts = prisma.get("staged_counts")
    counts = counts if isinstance(counts, Mapping) else {}
    excluded_count = counts.get("client_side_exclusions")
    duplicate_count = counts.get("within_source_duplicates_removed")
    malformed_count = counts.get("malformed_records_dropped")
    source_stable_ids = metadata.get("source_stable_identifiers")
    source_stable_ids_valid = False
    if (
        isinstance(source_total, int)
        and not isinstance(source_total, bool)
        and isinstance(duplicate_count, int)
        and not isinstance(duplicate_count, bool)
        and isinstance(source_stable_ids, list)
        and len(source_stable_ids) == source_total
        and all(isinstance(item, str) and item.strip() for item in source_stable_ids)
        and len({item.casefold() for item in source_stable_ids}) == source_total
    ):
        try:
            source_stable_ids_valid = bool(
                len({canonical_doi(item) for item in source_stable_ids})
                == source_total - duplicate_count
            )
        except FinalAiaaArcError:
            source_stable_ids_valid = False
    publication = limits.get("publication_date")
    publication = publication if isinstance(publication, Mapping) else {}
    expected_date_request = {"exact_start": DATE_START, "exact_end": CUTOFF}
    controls_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == SOURCE
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and prisma.get("run_id") == event.get("event_id")
        and prisma.get("review_id") == plan.get("review_id")
        and prisma.get("strategy_reference") == plan.get("strategy_reference")
        and prisma.get("strategy_version") == event.get("strategy_version")
        and prisma.get("phase") == plan.get("phase")
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and coverage.get("coverage_scope") == "partition"
        and coverage.get("partition_id") == event.get("partition_id")
        and strategy.get("executed_query_provenance") == "source_observed"
        and observed_rows_valid(strategy, event)
        and publication.get("requested") == expected_date_request
        and limits.get("date_input_mode") == "exact_dates"
        and limits.get("date_filter_mode") == "source_month_plus_client_exact_day"
        and limits.get("topic", {}).get("state") == "not_applied"
        and limits.get("published_in", {}).get("state") == "not_applied"
        and limits.get("access", {}).get("effective") == "All content"
        and limits.get("language_filter") is None
        and limits.get("publication_type_filter") is None
        and limits.get("venue_filter") is None
        and limits.get("open_access_filter") is None
        and adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    accounting_valid = bool(
        isinstance(source_total, int)
        and not isinstance(source_total, bool)
        and source_total >= 0
        and isinstance(rows, list)
        and isinstance(excluded_count, int)
        and not isinstance(excluded_count, bool)
        and excluded_count >= 0
        and isinstance(duplicate_count, int)
        and not isinstance(duplicate_count, bool)
        and duplicate_count >= 0
        and isinstance(malformed_count, int)
        and not isinstance(malformed_count, bool)
        and malformed_count == 0
        and source_total
        == retained_count + excluded_count + duplicate_count + malformed_count
        and source_stable_ids_valid
        and counts.get("source_reported_total") == source_total
        and counts.get("source_reported_total_status") == "reported"
        and counts.get("source_reported_total_exact") is True
        and counts.get("raw_source_records") == source_total
        and counts.get("records_exported") == retained_count
        and counts.get("within_source_duplicates_removed") == duplicate_count
        and counts.get("malformed_records_dropped") == malformed_count
    )
    native_valid, native_summary = inspect_native_ris(
        native_dir,
        source_total=source_total if isinstance(source_total, int) else -1,
        within_source_duplicates_removed=(
            duplicate_count if isinstance(duplicate_count, int) else -1
        ),
        retained_rows=rows if isinstance(rows, list) else [],
    )
    marker_valid = committed_arc_publication_valid(path, native_dir)
    manifest_valid = bool(
        isinstance(metadata.get("native_export_manifest_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", metadata["native_export_manifest_sha256"])
        and isinstance(metadata.get("native_export_manifest_entry_count"), int)
        and metadata.get("native_export_manifest_entry_count", -1) >= 0
        and metadata.get("native_export_transaction_state") == "pending_output_commit_marker"
    )
    valid = bool(
        controls_valid
        and accounting_valid
        and record_valid
        and screenshots_valid
        and native_valid
        and marker_valid
        and manifest_valid
    )
    summary = {
        "valid": valid,
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "source_total": source_total,
        "retained_record_count": retained_count if retained_count >= 0 else None,
        "client_exact_date_excluded_count": excluded_count,
        "within_source_duplicates_removed": duplicate_count,
        "source_stable_identifiers_valid": source_stable_ids_valid,
        "controls_valid": controls_valid,
        "accounting_valid": accounting_valid,
        "full_abstract_capture_valid": record_valid,
        "source_publication_type_capture_valid": record_valid,
        "native_ris_valid": native_valid,
        "terminal_marker_valid": marker_valid,
        "native_manifest_valid": manifest_valid,
        "screenshots_valid": screenshots_valid,
        "record_capture": record_summary,
        "native_capture": {
            key: value
            for key, value in native_summary.items()
            if key != "native_records"
        },
        "screenshots": screenshot_rows,
    }
    return summary, value, captures


def capture_receipt_valid(
    receipt_path: Path,
    *,
    output: Path,
    native_dir: Path,
    event: Mapping[str, Any],
    plan_path: Path,
    plan: Mapping[str, Any],
    summary: Mapping[str, Any],
    captures: Sequence[Mapping[str, Any]],
) -> bool:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        return False
    try:
        receipt = load(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError, FinalAiaaArcError):
        return False
    metadata = load(output).get("output_metadata", {})
    return bool(
        receipt.get("schema_version") == CAPTURE_SCHEMA
        and receipt.get("complete") is True
        and receipt.get("source") == SOURCE
        and receipt.get("source_id") == SOURCE_ID
        and receipt.get("event_id") == event.get("event_id")
        and receipt.get("partition_id") == event.get("partition_id")
        and receipt.get("cell_id") == event.get("cell_id")
        and receipt.get("serialized_query") == event.get("serialized_query")
        and receipt.get("serialized_query_sha256") == event.get("serialized_query_sha256")
        and receipt.get("plan") == relative(plan_path)
        and receipt.get("plan_sha256") == digest(plan_path)
        and receipt.get("artifact") == relative(output)
        and receipt.get("artifact_sha256") == digest(output)
        and receipt.get("artifact_bytes") == output.stat().st_size
        and receipt.get("native_ris_directory") == relative(native_dir)
        and receipt.get("source_total") == summary.get("source_total")
        and receipt.get("retained_record_count") == summary.get("retained_record_count")
        and receipt.get("within_source_duplicates_removed")
        == summary.get("within_source_duplicates_removed")
        and receipt.get("source_stable_identifier_count")
        == summary.get("source_total")
        and receipt.get("source_stable_identifier_sequence_sha256")
        == metadata.get("source_stable_identifier_sequence_sha256")
        and receipt.get("canonical_publication_aliases")
        == metadata.get("canonical_publication_aliases")
        and receipt.get("browser_retry_evidence")
        == metadata.get("browser_retry_evidence")
        and receipt.get("ui_retry_evidence")
        == metadata.get("ui_retry_evidence")
        and receipt.get("ris_retry_evidence") == metadata.get("ris_retry_evidence")
        and receipt.get("full_abstract_count")
        == summary.get("record_capture", {}).get("full_abstract_count")
        and receipt.get("missing_full_abstract_count")
        == summary.get("record_capture", {}).get("missing_full_abstract_count")
        and receipt.get("missing_source_publication_type_count") == 0
        and receipt.get("native_ris_manifest_sha256")
        == metadata.get("native_export_manifest_sha256")
        and receipt.get("native_ris_manifest_entry_count")
        == metadata.get("native_export_manifest_entry_count")
        and receipt.get("record_capture") == list(captures)
        and receipt.get("screenshots") == summary.get("screenshots")
        and receipt.get("source_publication_type_source") == NATIVE_PUBLICATION_TYPE_SOURCE
        and receipt.get("abstract_source") == NATIVE_ABSTRACT_SOURCE
        and receipt.get("reviewer_publication_type_coding")
        == "deferred to screening"
    )


def write_capture_receipt(
    output_dir: Path,
    event: Mapping[str, Any],
    plan_path: Path,
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    output = output_path(output_dir, event)
    native_dir = native_ris_path(output_dir, event)
    receipt = capture_receipt_path(output_dir, event)
    if receipt.exists() or receipt.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt}")
    summary, _value, captures = base_artifact_summary(output, native_dir, event, plan)
    if summary.get("valid") is not True:
        raise FinalAiaaArcError("Final AIAA ARC source artifact failed its capture contract")
    metadata = load(output)["output_metadata"]
    payload = {
        "schema_version": CAPTURE_SCHEMA,
        "created_at_utc": now(),
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "event_id": event["event_id"],
        "parent_event_id": event["parent_event_id"],
        "partition_id": event["partition_id"],
        "cell_id": event["cell_id"],
        "serialized_query": event["serialized_query"],
        "serialized_query_sha256": event["serialized_query_sha256"],
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "artifact": relative(output),
        "artifact_sha256": digest(output),
        "artifact_bytes": output.stat().st_size,
        "artifact_commit_marker": {
            "path": marker_path(output).name,
            "sha256": digest(marker_path(output)),
        },
        "native_ris_directory": relative(native_dir),
        "native_ris_manifest_sha256": metadata["native_export_manifest_sha256"],
        "native_ris_manifest_entry_count": metadata["native_export_manifest_entry_count"],
        "source_total": summary["source_total"],
        "retained_record_count": summary["retained_record_count"],
        "client_exact_date_excluded_count": summary["client_exact_date_excluded_count"],
        "within_source_duplicates_removed": summary[
            "within_source_duplicates_removed"
        ],
        "source_stable_identifier_count": len(
            metadata["source_stable_identifiers"]
        ),
        "source_stable_identifier_sequence_sha256": metadata[
            "source_stable_identifier_sequence_sha256"
        ],
        "canonical_publication_aliases": metadata[
            "canonical_publication_aliases"
        ],
        "browser_retry_evidence": metadata["browser_retry_evidence"],
        "ui_retry_evidence": metadata["ui_retry_evidence"],
        "ris_retry_evidence": metadata["ris_retry_evidence"],
        "full_abstract_count": summary["record_capture"]["full_abstract_count"],
        "missing_full_abstract_count": summary["record_capture"]["missing_full_abstract_count"],
        "source_publication_type_counts": summary["record_capture"]["source_publication_type_counts"],
        "missing_source_publication_type_count": summary["record_capture"][
            "missing_source_publication_type_count"
        ],
        "raw_native_capture": summary["native_capture"],
        "abstract_source": NATIVE_ABSTRACT_SOURCE,
        "source_publication_type_source": NATIVE_PUBLICATION_TYPE_SOURCE,
        "record_capture": captures,
        "screenshots": summary["screenshots"],
        "reviewer_publication_type_coding": "deferred to screening",
        "complete": True,
    }
    write_new(receipt, payload)
    return payload


def artifact_summary(
    output_dir: Path,
    event: Mapping[str, Any],
    plan_path: Path,
    plan: Mapping[str, Any],
    *,
    require_capture_receipt: bool,
) -> dict[str, Any]:
    output = output_path(output_dir, event)
    native_dir = native_ris_path(output_dir, event)
    summary, _value, captures = base_artifact_summary(output, native_dir, event, plan)
    if summary.get("artifact_written") is not True:
        return summary
    receipt_valid = False
    if require_capture_receipt and summary.get("valid") is True:
        receipt_valid = capture_receipt_valid(
            capture_receipt_path(output_dir, event),
            output=output,
            native_dir=native_dir,
            event=event,
            plan_path=plan_path,
            plan=plan,
            summary=summary,
            captures=captures,
        )
    summary["capture_receipt_valid"] = receipt_valid if require_capture_receipt else None
    if require_capture_receipt:
        summary["valid"] = bool(summary.get("valid") is True and receipt_valid)
    return summary


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def create_authorized_arc_target(cdp_url: str, timeout_seconds: float = 120.0) -> str:
    """Open one visible ARC page and passively wait for normal Advanced Search."""
    encoded = urllib.parse.quote("https://arc.aiaa.org/search/advanced", safe="")
    created = cdp_json(cdp_url, f"/json/new?{encoded}", method="PUT")
    target_id = created.get("id") if isinstance(created, Mapping) else None
    if not isinstance(target_id, str) or re.fullmatch(r"[A-Fa-f0-9]{32}", target_id) is None:
        raise FinalAiaaArcError("Chrome did not return one explicit ARC target")
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        targets = cdp_json(cdp_url, "/json/list")
        target = next(
            (
                item
                for item in targets
                if isinstance(item, Mapping) and item.get("id") == target_id
            ),
            None,
        )
        if isinstance(target, Mapping):
            parsed = urllib.parse.urlparse(str(target.get("url", "")))
            title = str(target.get("title", ""))
            if (
                target.get("type") == "page"
                and parsed.scheme == "https"
                and parsed.hostname == "arc.aiaa.org"
                and parsed.path == "/search/advanced"
                and "Advanced Search" in title
                and "AIAA Aerospace Research Central" in title
            ):
                return target_id
        time.sleep(0.5)
    close_target(cdp_url, target_id)
    raise FinalAiaaArcError(
        "The visible ARC target did not clear source readiness checks. No challenge was automated."
    )


def close_target(cdp_url: str, target_id: str) -> bool:
    try:
        with urllib.request.urlopen(
            f"{cdp_url.rstrip('/')}/json/close/{target_id}", timeout=15
        ) as response:
            response.read()
    except Exception:
        return False
    return True


def final_command(
    event: Mapping[str, Any],
    output_dir: Path,
    plan: Mapping[str, Any],
    cdp_url: str,
    target_id: str,
) -> list[str]:
    output = output_path(output_dir, event)
    command = [
        "uv",
        "run",
        "--with",
        f"playwright=={PLAYWRIGHT_VERSION}",
        "python",
        str(ADAPTER),
    ]
    for row in event["field_rows"]:
        command.extend(("--field-row", f"{row['field']}={row['text']}"))
    command.extend(
        (
            "--access",
            "all",
            "--date-start",
            DATE_START,
            "--date-end",
            CUTOFF,
            "--limit",
            str(event["limit"]),
            "--max-pages",
            str(event["max_pages"]),
            "--max-source-total",
            str(event["max_source_total"]),
            "--passes",
            str(event["passes"]),
            "--timeout",
            f"{event['timeout_seconds']:g}",
            "--page-delay-seconds",
            "0",
            "--require-complete",
            "--native-export-dir",
            str(native_ris_path(output_dir, event)),
            "--cdp-url",
            cdp_url,
            "--target-id",
            target_id,
            "--output-path",
            str(output),
            "--prisma-run-id",
            str(event["event_id"]),
            "--prisma-review-id",
            str(plan["review_id"]),
            "--prisma-strategy-reference",
            str(plan["strategy_reference"]),
            "--prisma-strategy-version",
            str(event["strategy_version"]),
            "--prisma-phase",
            str(plan["phase"]),
            "--prisma-coverage-scope",
            "partition",
            "--prisma-partition-id",
            str(event["partition_id"]),
            "--prisma-partition-label",
            str(event["partition_id"]),
            "--prisma-partition-description",
            (
                "AIAA ARC final direct discovery partition "
                f"{event['partition_id']} source cell {event['cell_id']}"
            ),
            "--prisma-source-id",
            SOURCE_ID,
        )
    )
    return command


def output_paths_occupied(output_dir: Path, event: Mapping[str, Any]) -> bool:
    output = output_path(output_dir, event)
    paths = (
        output,
        marker_path(output),
        failure_path(output),
        *screenshot_paths(output),
        native_ris_path(output_dir, event),
        capture_receipt_path(output_dir, event),
        runner_failure_path(output_dir, event),
    )
    return any(path.exists() or path.is_symlink() for path in paths)


def compact_process_error(
    completed: subprocess.CompletedProcess[str] | None,
    timeout: bool,
) -> dict[str, Any]:
    stdout = completed.stdout if completed is not None and isinstance(completed.stdout, str) else ""
    stderr = completed.stderr if completed is not None and isinstance(completed.stderr, str) else ""
    return {
        "kind": "subprocess_timeout" if timeout else "source_or_adapter_failure",
        "exit_code": completed.returncode if completed is not None else None,
        "stdout_sha256": digest_text(stdout),
        "stdout_bytes": len(stdout.encode("utf-8")),
        "stderr_sha256": digest_text(stderr),
        "stderr_bytes": len(stderr.encode("utf-8")),
    }


def write_runner_failure(
    output_dir: Path,
    event: Mapping[str, Any],
    plan_path: Path,
    process_error: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> None:
    target = runner_failure_path(output_dir, event)
    if target.exists() or target.is_symlink():
        return
    write_new(
        target,
        {
            "schema_version": FAILURE_SCHEMA,
            "source": SOURCE,
            "source_id": SOURCE_ID,
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "plan": relative(plan_path),
            "plan_sha256": digest(plan_path),
            "status": "error",
            "merge_eligible": False,
            "do_not_merge": True,
            "failed_at_utc": now(),
            "process": dict(process_error),
            "artifact_written": summary.get("artifact_written") is True,
            "artifact_valid": summary.get("valid") is True,
            "adapter_failure_artifact": (
                relative(failure_path(output_path(output_dir, event)))
                if failure_path(output_path(output_dir, event)).is_file()
                else None
            ),
            "disposition": "A corrective final plan and source run are required. Do not reuse this event.",
        },
    )


def shared_browser_url() -> str:
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise FinalAiaaArcError("Run through run_with_browser.py using shared-browser-owned-tabs-v1")
    cdp_url = os.environ.get("BH_CDP_URL")
    if not isinstance(cdp_url, str) or re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url) is None:
        raise FinalAiaaArcError("Final AIAA ARC execution requires a loopback shared-browser endpoint")
    return cdp_url


def run_final(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    *,
    settle_seconds: float,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise FinalAiaaArcError("Invalid final AIAA ARC plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise FinalAiaaArcError("The final AIAA ARC output directory cannot be a symlink")
    if settle_seconds < 0:
        raise ValueError("--settle-seconds must be nonnegative")
    cdp_url = shared_browser_url()
    output_dir.mkdir(parents=True, exist_ok=True)
    for event in plan["events"]:
        if output_paths_occupied(output_dir, event):
            raise FileExistsError(f"Final AIAA ARC cell path is occupied: {event['cell_id']}")

    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_path(output_dir, event)
        output.parent.mkdir(parents=True, exist_ok=True)
        completed: subprocess.CompletedProcess[str] | None = None
        timed_out = False
        runner_exception: str | None = None
        target_id: str | None = None
        target_closed = False
        event_started = now()
        try:
            target_id = create_authorized_arc_target(cdp_url)
            completed = subprocess.run(
                final_command(event, output_dir, plan, cdp_url, target_id),
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            timed_out = True
        except Exception as error:  # noqa: BLE001 - retain a bounded runner outcome.
            runner_exception = type(error).__name__
        finally:
            if target_id is not None:
                target_closed = close_target(cdp_url, target_id)
        summary = artifact_summary(
            output_dir,
            event,
            plan_path,
            plan,
            require_capture_receipt=False,
        )
        capture_error: str | None = None
        if completed is not None and completed.returncode == 0 and summary.get("valid") is True:
            try:
                write_capture_receipt(output_dir, event, plan_path, plan)
                summary = artifact_summary(
                    output_dir,
                    event,
                    plan_path,
                    plan,
                    require_capture_receipt=True,
                )
            except Exception as error:  # noqa: BLE001 - preserve final failure evidence.
                capture_error = type(error).__name__
                summary["valid"] = False
                summary["capture_receipt_valid"] = False
        success = bool(
            completed is not None
            and completed.returncode == 0
            and not timed_out
            and summary.get("valid") is True
        )
        process_error = compact_process_error(completed, timed_out)
        if not success:
            write_runner_failure(output_dir, event, plan_path, process_error, summary)
        outcome = {
            "event_id": event["event_id"],
            "parent_event_id": event["parent_event_id"],
            "partition_id": event["partition_id"],
            "cell_id": event["cell_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "success": success,
            "artifact": relative(output) if output.is_file() else None,
            "capture_receipt": (
                relative(capture_receipt_path(output_dir, event))
                if capture_receipt_path(output_dir, event).is_file()
                else None
            ),
            "adapter_failure_artifact": (
                relative(failure_path(output)) if failure_path(output).is_file() else None
            ),
            "runner_failure_artifact": (
                relative(runner_failure_path(output_dir, event))
                if runner_failure_path(output_dir, event).is_file()
                else None
            ),
            "attempt_count": 1,
            "source_commands_reexecuted": False,
            "authorized_arc_target_created": target_id is not None,
            "authorized_arc_target_close_requested": target_closed,
            "target_identifier_retained": False,
            **process_error,
            **summary,
        }
        if capture_error is not None:
            outcome["capture_receipt_error"] = capture_error
        if runner_exception is not None:
            outcome["runner_exception"] = runner_exception
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "cell": event["cell_id"],
                    "position": position + 1,
                    "planned": len(plan["events"]),
                    "success": success,
                    "source_total": outcome.get("source_total"),
                    "retained": outcome.get("retained_record_count"),
                    "full_abstracts": outcome.get("record_capture", {}).get("full_abstract_count"),
                    "publication_types": outcome.get("record_capture", {}).get(
                        "source_publication_type_counts"
                    ),
                }
            ),
            flush=True,
        )
        if (
            position == 0
            and not success
            and plan.get("execution_policy", {}).get(
                "first_cell_runtime_and_capture_gate"
            )
            is True
        ):
            break
    success = len(outcomes) == len(plan["events"]) and all(
        outcome.get("success") is True for outcome in outcomes
    )
    write_new(
        receipt_path,
        {
            "schema_version": RUN_SCHEMA,
            "source": SOURCE,
            "source_id": SOURCE_ID,
            "review_namespace": REVIEW_NAMESPACE,
            "event_kind": "final",
            "plan": relative(plan_path),
            "plan_sha256": digest(plan_path),
            "adapter": plan["adapter"],
            "target_identifier_retained": False,
            "execution_policy": plan["execution_policy"],
            "started_at_utc": started,
            "completed_at_utc": now(),
            "planned_source_cell_count": len(plan["events"]),
            "attempted_source_cell_count": len(outcomes),
            "accepted_source_cell_count": sum(
                outcome.get("success") is True for outcome in outcomes
            ),
            "all_source_cells_attempted": len(outcomes) == len(plan["events"]),
            "stopped_at_first_cell_gate": bool(
                len(outcomes) == 1
                and outcomes[0].get("success") is not True
                and plan.get("execution_policy", {}).get(
                    "first_cell_runtime_and_capture_gate"
                )
                is True
            ),
            "unattempted_event_ids": [
                event["event_id"] for event in plan["events"][len(outcomes) :]
            ],
            "success": success,
            "outcomes": outcomes,
        },
    )
    return 0 if success else 1


def successful_event_artifacts(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
) -> list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]]:
    plan = load(plan_path)
    receipt = load(receipt_path)
    if validate_plan(plan, verify_bindings=False):
        raise FinalAiaaArcError("The final AIAA ARC plan is invalid")
    if (
        receipt.get("schema_version") != RUN_SCHEMA
        or receipt.get("plan") != relative(plan_path)
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("success") is not True
    ):
        raise FinalAiaaArcError("The final AIAA ARC run is incomplete")
    outcomes = {
        item.get("event_id"): item
        for item in receipt.get("outcomes", [])
        if isinstance(item, Mapping)
    }
    selected: list[tuple[Mapping[str, Any], Mapping[str, Any], Path, dict[str, Any]]] = []
    for event in plan["events"]:
        outcome = outcomes.get(event["event_id"])
        output = output_path(output_dir, event)
        if not isinstance(outcome, Mapping) or outcome.get("success") is not True:
            raise FinalAiaaArcError(f"Incomplete final AIAA ARC cell: {event['cell_id']}")
        summary = artifact_summary(
            output_dir,
            event,
            plan_path,
            plan,
            require_capture_receipt=True,
        )
        if summary.get("valid") is not True:
            raise FinalAiaaArcError(f"Invalid final AIAA ARC artifact: {event['cell_id']}")
        if (
            outcome.get("artifact_sha256") != digest(output)
            or outcome.get("artifact_bytes") != output.stat().st_size
            or outcome.get("capture_receipt") != relative(capture_receipt_path(output_dir, event))
        ):
            raise FinalAiaaArcError(f"AIAA ARC run receipt binding changed: {event['cell_id']}")
        selected.append((event, outcome, output, load(output)))
    return selected


def build_cell_declarations(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    output: Path,
) -> dict[str, Any]:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    selected = successful_event_artifacts(plan_path, receipt_path, output_dir)
    cells: list[dict[str, Any]] = []
    for event, outcome, artifact, data in selected:
        rows = data["results"]
        stable_ids = [row.get("paperId") for row in rows]
        if not all(isinstance(identifier, str) and identifier for identifier in stable_ids):
            raise FinalAiaaArcError(f"AIAA ARC artifact lacks a stable paper ID: {event['cell_id']}")
        source_observed_query = data.get("executed_query")
        if not isinstance(source_observed_query, str) or not source_observed_query:
            raise FinalAiaaArcError(f"AIAA ARC artifact lacks an executed query: {event['cell_id']}")
        cells.append(
            {
                "source_id": SOURCE_ID,
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "parent_event_id": event["parent_event_id"],
                "source_run_id": event["event_id"],
                "query": source_observed_query,
                "requested_query": source_observed_query,
                "executed_query": source_observed_query,
                "artifact": relative(artifact),
                "artifact_sha256": outcome["artifact_sha256"],
                "artifact_byte_count": outcome["artifact_bytes"],
                "stable_ids": stable_ids,
                "status": "complete",
                "report_ready": True,
            }
        )
    value = {
        "schema_version": CELL_DECLARATIONS_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "expected_cells": cells,
    }
    write_new(output, value)
    return value


def run_source_union(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    declarations_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    declarations = load(declarations_path)
    if declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA:
        raise FinalAiaaArcError("Unexpected AIAA ARC source-cell declaration schema")
    selected = successful_event_artifacts(plan_path, receipt_path, output_dir)
    command = [
        "uv",
        "run",
        str(SOURCE_UNION_TOOL),
        "--input",
        *(str(path) for _, _, path, _ in selected),
        "--output-path",
        str(output),
        "--expected-partitions",
        *PARTITIONS,
        "--expected-sources",
        SOURCE_ID,
        "--review-namespace",
        REVIEW_NAMESPACE,
        "--expected-cells",
        str(declarations_path),
    ]
    completed = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not output.is_file():
        raise FinalAiaaArcError("Could not create the AIAA ARC source-union receipt")
    return 0


def raw_unique_records(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    selected = successful_event_artifacts(plan_path, receipt_path, output_dir)
    records: dict[str, dict[str, Any]] = {}
    artifacts: list[dict[str, Any]] = []
    for event, outcome, artifact, data in selected:
        artifacts.append(
            {
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": relative(artifact),
                "artifact_sha256": outcome["artifact_sha256"],
                "artifact_bytes": outcome["artifact_bytes"],
                "source_total": data["total"],
                "retained_record_count": len(data["results"]),
            }
        )
        for row in data["results"]:
            identifier = canonical_doi(row.get("paperId"))
            item = records.setdefault(
                identifier,
                {
                    "paper_id": identifier,
                    "source_record_stable_ids": [],
                    "discovery_cells": [],
                    "discovery_partitions": [],
                    "record": None,
                },
            )
            source_ids = row.get("sourceRecordIds")
            if not isinstance(source_ids, list) or not source_ids:
                source_ids = [row.get("paperId")]
            for source_id_value in source_ids:
                source_id = str(source_id_value)
                if canonical_doi(source_id) != identifier:
                    raise FinalAiaaArcError(
                        "AIAA ARC source stable-ID alias changed canonical DOI"
                    )
                if source_id not in item["source_record_stable_ids"]:
                    item["source_record_stable_ids"].append(source_id)
            if event["cell_id"] not in item["discovery_cells"]:
                item["discovery_cells"].append(event["cell_id"])
            if event["partition_id"] not in item["discovery_partitions"]:
                item["discovery_partitions"].append(event["partition_id"])
            candidate = copy.deepcopy(dict(row))
            current = item["record"]
            if current is None or len(str(candidate.get("abstract") or "")) > len(
                str(current.get("abstract") or "")
            ):
                item["record"] = candidate
    return records, artifacts


def build_abstract_plan(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    source_plan = load(plan_path)
    records, artifacts = raw_unique_records(plan_path, receipt_path, output_dir)
    events: list[dict[str, Any]] = []
    record_ledger: list[dict[str, Any]] = []
    for identifier in sorted(records):
        row = records[identifier]["record"]
        if not isinstance(row, Mapping):
            raise FinalAiaaArcError("AIAA ARC record union contains no selected record")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if not isinstance(abstract, str):
            raise FinalAiaaArcError("AIAA ARC normalized record lacks an abstract field")
        if not isinstance(document_type, str) or not document_type.strip():
            raise FinalAiaaArcError("AIAA ARC normalized record lacks its RIS publication type")
        entry = {
            "paper_id": identifier,
            "title": row.get("title"),
            "document_type": document_type,
            "native_ris_abstract_present": bool(abstract.strip()),
            "native_ris_abstract_characters": len(abstract),
            "native_ris_abstract_sha256": digest_text(abstract),
        }
        if not abstract.strip():
            number = len(events) + 1
            event_id = f"final-main-aiaa-arc-abstract-follow-up-{number:04d}"
            output_name = f"record-{number:04d}.json"
            event = {
                "event_id": event_id,
                "source_id": SOURCE_ID,
                "paper_id": identifier,
                "title": row.get("title"),
                "document_type": document_type,
                "abstract_url": f"https://arc.aiaa.org/doi/abs/{identifier}",
                "output": output_name,
            }
            events.append(event)
            entry["follow_up_event_id"] = event_id
            entry["follow_up_output"] = output_name
        record_ledger.append(entry)
    return {
        "schema_version": ABSTRACT_PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": source_plan["review_id"],
        "phase": source_plan["phase"],
        "strategy_reference": f"{source_plan['strategy_reference']}-abstract-follow-up",
        "strategy_version": source_plan["strategy_version"],
        "source_search_plan": relative(plan_path),
        "source_search_plan_sha256": digest(plan_path),
        "source_search_receipt": relative(receipt_path),
        "source_search_receipt_sha256": digest(receipt_path),
        "source_cell_artifacts": artifacts,
        "unique_record_count": len(records),
        "native_ris_full_abstract_count": sum(
            entry["native_ris_abstract_present"] for entry in record_ledger
        ),
        "rendered_follow_up_count": len(events),
        "capture_contract": {
            "routes": [
                "normal rendered DOI abstract/full page",
                "visible Read Now reader source abstract block",
            ],
            "full_text_summary_generation": False,
            "source_unavailable_state_allowed": True,
            "publication_type_field": "documentType from native RIS TY",
            "one_event_per_unique_canonical_doi_with_blank_native_abstract": True,
        },
        "runtime": {
            "playwright_version": PLAYWRIGHT_VERSION,
            "explicit_arc_authorization_target": True,
            "challenge_automation": False,
        },
        "record_ledger": record_ledger,
        "events": events,
    }


def validate_abstract_plan(
    abstract_plan: Mapping[str, Any],
    *,
    plan_path: Path,
    receipt_path: Path,
) -> list[str]:
    errors: list[str] = []
    if (
        abstract_plan.get("schema_version") != ABSTRACT_PLAN_SCHEMA
        or abstract_plan.get("source") != SOURCE
        or abstract_plan.get("source_id") != SOURCE_ID
        or abstract_plan.get("review_namespace") != REVIEW_NAMESPACE
        or abstract_plan.get("source_search_plan") != relative(plan_path)
        or abstract_plan.get("source_search_plan_sha256") != digest(plan_path)
        or abstract_plan.get("source_search_receipt") != relative(receipt_path)
        or abstract_plan.get("source_search_receipt_sha256") != digest(receipt_path)
    ):
        errors.append("identity")
    events = abstract_plan.get("events")
    ledger = abstract_plan.get("record_ledger")
    if not isinstance(events, list) or not isinstance(ledger, list):
        errors.append("events")
        return errors
    if abstract_plan.get("unique_record_count") != len(ledger):
        errors.append("record_count")
    if abstract_plan.get("rendered_follow_up_count") != len(events):
        errors.append("follow_up_count")
    ids: set[str] = set()
    for number, event in enumerate(events, start=1):
        if not isinstance(event, Mapping):
            errors.append("event_shape")
            continue
        identifier = event.get("paper_id")
        if (
            not isinstance(identifier, str)
            or canonical_doi(identifier) != identifier
            or identifier in ids
            or event.get("event_id")
            != f"final-main-aiaa-arc-abstract-follow-up-{number:04d}"
            or event.get("abstract_url")
            != f"https://arc.aiaa.org/doi/abs/{identifier}"
            or event.get("output") != f"record-{number:04d}.json"
            or not isinstance(event.get("document_type"), str)
            or not event.get("document_type")
        ):
            errors.append(f"event:{number}")
        ids.add(str(identifier))
    contract = abstract_plan.get("capture_contract", {})
    runtime = abstract_plan.get("runtime", {})
    if (
        contract.get("full_text_summary_generation") is not False
        or contract.get("source_unavailable_state_allowed") is not True
        or runtime.get("playwright_version") != PLAYWRIGHT_VERSION
        or runtime.get("explicit_arc_authorization_target") is not True
        or runtime.get("challenge_automation") is not False
    ):
        errors.append("capture_contract")
    return errors


def _clean_detail_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _detail_doi_from_url(adapter: Any, value: str) -> str:
    doi = adapter.doi_from_arc_url(value)
    if doi:
        return canonical_doi(doi)
    parsed = urllib.parse.urlparse(value)
    match = re.match(
        r"^/doi/(?:reader|epub)/(10\..+)$", parsed.path, re.IGNORECASE
    )
    return canonical_doi(urllib.parse.unquote(match.group(1))) if match else ""


def _section_boundary(value: str) -> bool:
    text = _clean_detail_text(value)
    compact = re.sub(r"\s+", "", text).casefold()
    return bool(
        re.fullmatch(r"(?:[ivxlc]+[.)]?)?(?:introduction|nomenclature)", compact)
        or re.fullmatch(r"(?:introduction|nomenclature)(?:[ivxlc]+[.)]?)?", compact)
        or re.match(r"(?i)^keywords?\s*[:.—-]", text)
        or re.match(r"^[A-Z][A-Za-z0-9&/ _-]{1,24}\s*=", text)
        or re.match(r"^(?:[A-Z]\s*){2,10}=", text)
    )


def _section_level(value: str) -> str | None:
    compact = re.sub(r"\s+", "", _clean_detail_text(value)).casefold()
    match = re.fullmatch(
        r"([ivxlc]+)[.)]?(?:introduction|nomenclature)", compact
    )
    if match:
        return match.group(1)
    match = re.fullmatch(
        r"(?:introduction|nomenclature)([ivxlc]+)[.)]?", compact
    )
    return match.group(1) if match else None


def _complete_reader_abstract(value: str) -> bool:
    text = _clean_detail_text(value)
    first = text[:1]
    return bool(
        len(text) >= 120
        and len(text.split()) >= 20
        and first
        and (first.isupper() or first.isdigit())
        and re.search(r"[.!?][\"')\]]?$", text)
    )


def _reader_candidate_text(groups: Sequence[Mapping[str, Any]]) -> str:
    text = _clean_detail_text(" ".join(str(group["text"]) for group in groups))
    text = re.sub(r"^(?:\d+\s+){1,6}(?=[A-Z])", "", text)
    text = re.sub(r"^(?:nd|st|rd|th)\s+(?=[A-Z])", "", text)
    return _clean_detail_text(text)


def _reader_material_blocks(
    groups: Sequence[dict[str, Any]], gap_threshold: float = 8.0
) -> list[list[dict[str, Any]]]:
    blocks: list[list[dict[str, Any]]] = []
    for group in groups:
        if not blocks:
            blocks.append([group])
            continue
        previous = blocks[-1][-1]
        previous_max = previous.get("max_top")
        current_min = group.get("min_top")
        material_gap = bool(
            previous.get("page_number") != group.get("page_number")
            or not isinstance(previous_max, (int, float))
            or not isinstance(current_min, (int, float))
            or current_min - previous_max > gap_threshold
        )
        if material_gap:
            blocks.append([group])
        else:
            blocks[-1].append(group)
    return blocks


def reader_abstract_from_groups(groups: Sequence[Mapping[str, Any]]) -> tuple[str, dict[str, Any]]:
    cleaned = [
        {
            "text": _clean_detail_text(group.get("text")),
            "min_top": group.get("min_top"),
            "max_top": group.get("max_top"),
            "font_size": group.get("font_size"),
            "min_left": group.get("min_left"),
            "max_right": group.get("max_right"),
            "page_number": group.get("page_number"),
        }
        for group in groups
        if isinstance(group, Mapping) and _clean_detail_text(group.get("text"))
    ]
    page_one = [group for group in cleaned if group["page_number"] == 1]
    boundary_index = next(
        (index for index, group in enumerate(page_one) if _section_boundary(group["text"])),
        None,
    )
    explicit_search_end = boundary_index if boundary_index is not None else len(page_one)
    for index, group in enumerate(page_one[:explicit_search_end]):
        text = group["text"]
        match = re.match(r"(?is)^abstract\b\s*[:.—-]?\s*(.*)$", text)
        if match is None:
            continue
        selected: list[dict[str, Any]] = []
        if match.group(1).strip():
            selected.append({**group, "text": match.group(1).strip()})
        for following in page_one[index + 1 : explicit_search_end]:
            selected.append(following)
        abstract = _reader_candidate_text(selected)
        if _complete_reader_abstract(abstract):
            return abstract, {
                "method": "explicit_abstract_heading_in_visible_reader_text_layer",
                "line_count": len(selected),
                "boundary": (
                    page_one[boundary_index]["text"]
                    if boundary_index is not None
                    else "page end"
                ),
                "completeness_checks": "length_words_initial_and_terminal_punctuation",
            }

    content = page_one[:boundary_index] if boundary_index is not None else page_one
    while content and re.fullmatch(r"(?i)[IVXLC]+[.)]?", content[-1]["text"]):
        content.pop()
    blocks = _reader_material_blocks(content)
    selected_block_index: int | None = None
    for index, block in enumerate(blocks):
        block_text = _reader_candidate_text(block)
        if (
            len(block_text) >= 80
            and re.search(r"[.!?]", block_text)
            and _complete_reader_abstract(block_text)
        ):
            selected_block_index = index
            break
    if selected_block_index is None:
        return "", {
            "method": "no_complete_opening_prose_block_detected",
            "material_block_count": len(blocks),
            "boundary": (
                page_one[boundary_index]["text"]
                if boundary_index is not None
                else None
            ),
        }

    selected_blocks = [blocks[selected_block_index]]
    boundary_level = (
        _section_level(page_one[boundary_index]["text"])
        if boundary_index is not None
        else None
    )
    if boundary_index is not None and boundary_level != "ii":
        selected_blocks = blocks[selected_block_index:]
    selected_groups = [group for block in selected_blocks for group in block]
    abstract = _reader_candidate_text(selected_groups)
    if not _complete_reader_abstract(abstract):
        return "", {
            "method": "opening_block_failed_full_abstract_checks",
            "line_count": len(selected_groups),
            "characters": len(abstract),
            "boundary": (
                page_one[boundary_index]["text"]
                if boundary_index is not None
                else None
            ),
        }
    return abstract, {
        "method": "source_unheaded_opening_abstract_block_before_first_major_section",
        "line_count": len(selected_groups),
        "material_block_count": len(selected_blocks),
        "boundary": (
            page_one[boundary_index]["text"]
            if boundary_index is not None
            else "first complete opening prose block"
        ),
        "page_number": 1,
        "min_top": selected_groups[0].get("min_top"),
        "max_top": selected_groups[-1].get("max_top"),
        "completeness_checks": "length_words_initial_and_terminal_punctuation",
    }


async def _wait_for_normal_arc_detail(page: Any, timeout_seconds: float) -> str:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while True:
        body = _clean_detail_text(await page.locator("body").inner_text()).casefold()
        blocked = any(
            marker in body
            for marker in (
                "just a moment",
                "performing security verification",
                "verify you are human",
                "captcha",
                "cloudflare ray id",
            )
        )
        if not blocked:
            return body
        if asyncio.get_running_loop().time() >= deadline:
            raise FinalAiaaArcError(
                "ARC detail page challenge did not clear. No challenge was automated."
            )
        await asyncio.sleep(0.5)


async def _navigate_arc_detail(
    page: Any,
    adapter: Any,
    url: str,
    doi: str,
    timeout_seconds: float,
    *,
    allow_source_unavailable_status: bool = False,
) -> dict[str, Any]:
    response = await page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=max(1, int(timeout_seconds * 1000)),
    )
    await _wait_for_normal_arc_detail(page, timeout_seconds)
    observed_doi = _detail_doi_from_url(adapter, page.url)
    if observed_doi != doi:
        raise FinalAiaaArcError("ARC detail navigation left the requested DOI")
    status = response.status if response is not None else None
    if not isinstance(status, int):
        raise FinalAiaaArcError("ARC detail navigation did not return a normal page")
    source_unavailable = bool(
        allow_source_unavailable_status and status in {401, 403, 404}
    )
    if (status < 200 or status >= 400) and not source_unavailable:
        raise FinalAiaaArcError("ARC detail navigation did not return a normal page")
    return {
        "requested_url": url,
        "observed_url": page.url,
        "http_status": status,
        "title": _clean_detail_text(await page.title()),
        "source_unavailable_status": source_unavailable,
    }


async def _visible_abstract(page: Any) -> tuple[str, str | None]:
    selectors = (
        "#hlFld-Abstract .abstractSection.abstractInFull",
        "#hlFld-Abstract .abstractSection",
        ".abstractSection.abstractInFull",
        ".abstractSection",
    )
    for selector in selectors:
        locator = page.locator(selector)
        visible: list[str] = []
        for index in range(min(await locator.count(), 20)):
            item = locator.nth(index)
            if await item.is_visible():
                text = _clean_detail_text(await item.inner_text())
                if text:
                    visible.append(text)
        unique = list(dict.fromkeys(visible))
        if len(unique) == 1 and len(unique[0]) >= 80:
            return unique[0], selector
        if len(unique) > 1:
            raise FinalAiaaArcError("ARC abstract page exposed ambiguous abstract blocks")
    return "", None


async def _reader_groups(page: Any, timeout_seconds: float) -> list[dict[str, Any]]:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    selector = '.page[data-page-number="1"] .textLayer'
    while asyncio.get_running_loop().time() < deadline:
        if await page.locator(selector).count():
            text = _clean_detail_text(await page.locator(selector).first.inner_text())
            if len(text) >= 200:
                break
        await asyncio.sleep(0.25)
    else:
        return []
    extraction_script = r'''() => {
          const items = [];
          const seenItems = new Set();
          for (const page of Array.from(document.querySelectorAll('.page[data-page-number]')).slice(0, 2)) {
            const layer = page.querySelector('.textLayer');
            if (!layer) continue;
            const pageNumber = Number(page.getAttribute('data-page-number'));
            const pageRect = page.getBoundingClientRect();
            for (const element of Array.from(layer.querySelectorAll('span[role="presentation"]'))) {
              const text = String(element.innerText || element.textContent || '').replace(/\s+/g, ' ').trim();
              if (!text) continue;
              const rect = element.getBoundingClientRect();
              const fontSize = Number.parseFloat(getComputedStyle(element).fontSize);
              const minTop = rect.top - pageRect.top;
              const maxTop = rect.bottom - pageRect.top;
              const left = rect.left - pageRect.left;
              const right = rect.right - pageRect.left;
              const geometryKey = [
                pageNumber,
                Math.round(minTop * 2),
                Math.round(maxTop * 2),
                Math.round(left * 2),
                text
              ].join('|');
              if (seenItems.has(geometryKey)) continue;
              seenItems.add(geometryKey);
              items.push({
                page_number: pageNumber,
                text,
                min_top: minTop,
                max_top: maxTop,
                left,
                right,
                font_size: Number.isFinite(fontSize) ? fontSize : null
              });
            }
          }
          items.sort((a, b) =>
            a.page_number - b.page_number || a.min_top - b.min_top || a.left - b.left
          );
          const lines = [];
          for (const item of items) {
            const prior = lines.at(-1);
            if (
              prior && prior.page_number === item.page_number &&
              Math.abs(prior.anchor_top - item.min_top) <= 2.5 &&
              (
                item.left - prior.max_right <= 20 ||
                /^=/.test(item.text)
              )
            ) {
              prior.parts.push(item.text);
              prior.min_top = Math.min(prior.min_top, item.min_top);
              prior.max_top = Math.max(prior.max_top, item.max_top);
              prior.min_left = Math.min(prior.min_left, item.left);
              prior.max_right = Math.max(prior.max_right, item.right);
              if (Number.isFinite(item.font_size)) prior.font_sizes.push(item.font_size);
              continue;
            }
            lines.push({
              page_number: item.page_number,
              anchor_top: item.min_top,
              min_top: item.min_top,
              max_top: item.max_top,
              min_left: item.left,
              max_right: item.right,
              parts: [item.text],
              font_sizes: Number.isFinite(item.font_size) ? [item.font_size] : []
            });
          }
          return lines.map(line => ({
            page_number: line.page_number,
            text: line.parts.join(' ').replace(/\s+/g, ' ').trim(),
            min_top: line.min_top,
            max_top: line.max_top,
            min_left: line.min_left,
            max_right: line.max_right,
            font_size: line.font_sizes.length
              ? line.font_sizes.reduce((sum, value) => sum + value, 0) / line.font_sizes.length
              : null
          }));
        }'''
    last_groups: list[dict[str, Any]] = []
    last_signature: str | None = None
    stable_polls = 0
    while asyncio.get_running_loop().time() < deadline:
        candidate = await page.evaluate(extraction_script)
        if isinstance(candidate, list) and all(
            isinstance(group, dict) for group in candidate
        ):
            last_groups = candidate
            first_page = [
                group for group in candidate if group.get("page_number") == 1
            ]
            distinct_tops = {
                round(float(group["min_top"]), 1)
                for group in first_page
                if isinstance(group.get("min_top"), (int, float))
            }
            text_characters = sum(
                len(_clean_detail_text(group.get("text"))) for group in first_page
            )
            signature = digest_text(
                json.dumps(candidate, ensure_ascii=False, sort_keys=True)
            )
            hydrated = bool(
                len(first_page) >= 5
                and len(distinct_tops) >= 3
                and text_characters >= 200
            )
            if hydrated and signature == last_signature:
                stable_polls += 1
            elif hydrated:
                stable_polls = 1
            else:
                stable_polls = 0
            last_signature = signature
            if stable_polls >= 2:
                return candidate
        await asyncio.sleep(0.25)
    return last_groups if len(last_groups) >= 5 else []


async def capture_rendered_abstract(
    page: Any,
    adapter: Any,
    event: Mapping[str, Any],
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    doi = canonical_doi(event["paper_id"])
    abstract_page = await _navigate_arc_detail(
        page, adapter, str(event["abstract_url"]), doi, timeout_seconds
    )
    abstract, selector = await _visible_abstract(page)
    if abstract:
        return {
            "status": "full_source_abstract",
            "abstract": abstract,
            "abstract_source": ABSTRACT_SOURCE_HTML,
            "abstract_not_available": False,
            "source_publication_type": event["document_type"],
            "documentType": event["document_type"],
            "abstract_page": {**abstract_page, "selector": selector},
            "reader": {"state": "not_needed"},
        }

    read_links = page.get_by_role("link", name=re.compile(r"^\s*Read\s+Now\s*$", re.I))
    hrefs: list[str] = []
    for index in range(min(await read_links.count(), 10)):
        link = read_links.nth(index)
        if await link.is_visible():
            href = await link.get_attribute("href")
            if isinstance(href, str):
                hrefs.append(urllib.parse.urljoin(page.url, href))
    hrefs = list(dict.fromkeys(hrefs))
    if len(hrefs) > 1:
        raise FinalAiaaArcError("ARC detail page exposed ambiguous Read Now routes")
    reader_evidence: dict[str, Any]
    if hrefs:
        reader_evidence = await _navigate_arc_detail(
            page,
            adapter,
            hrefs[0],
            doi,
            timeout_seconds,
            allow_source_unavailable_status=True,
        )
        if reader_evidence["source_unavailable_status"]:
            reader_evidence["state"] = "source_reader_not_available"
        elif "/doi/epdf/" in page.url or "/doi/pdf/" in page.url:
            groups = await _reader_groups(page, timeout_seconds)
            reader_abstract, derivation = reader_abstract_from_groups(groups)
            reader_evidence.update(
                {
                    "state": "checked",
                    "text_group_count": len(groups),
                    "derivation": derivation,
                }
            )
            if reader_abstract:
                return {
                    "status": "full_source_abstract",
                    "abstract": reader_abstract,
                    "abstract_source": ABSTRACT_SOURCE_READER,
                    "abstract_not_available": False,
                    "source_publication_type": event["document_type"],
                    "documentType": event["document_type"],
                    "abstract_page": {**abstract_page, "selector": None},
                    "reader": reader_evidence,
                }
        else:
            reader_evidence["state"] = "unavailable_or_returned_to_abstract_page"
    else:
        reader_evidence = {"state": "no_visible_read_now_route"}
    return {
        "status": "source_abstract_not_available",
        "abstract": "",
        "abstract_source": ABSTRACT_SOURCE_UNAVAILABLE,
        "abstract_not_available": True,
        "source_publication_type": event["document_type"],
        "documentType": event["document_type"],
        "abstract_page": {**abstract_page, "selector": None},
        "reader": reader_evidence,
    }


async def _run_abstract_events(
    abstract_plan: Mapping[str, Any],
    output_dir: Path,
    cdp_url: str,
    target_id: str,
) -> list[dict[str, Any]]:
    from playwright.async_api import async_playwright

    adapter = load_adapter()
    outcomes: list[dict[str, Any]] = []
    async with async_playwright() as playwright:
        connection = await adapter._browser_utils.open_chrome_connection(
            playwright,
            cdp_url=cdp_url,
            headless=False,
            timeout_seconds=60,
            chrome_executable=None,
            require_single_cdp_context=False,
        )
        owned_target = await adapter.resolve_operator_authorized_cdp_target(
            connection.browser, target_id
        )
        page = await adapter.new_adapter_owned_page(
            owned_target.context,
            timeout_seconds=60,
            ownership_reassertion=None,
        )
        try:
            page.set_default_timeout(60_000)
            page.set_default_navigation_timeout(60_000)
            for event in abstract_plan["events"]:
                output = output_dir / str(event["output"])
                if output.exists() or output.is_symlink():
                    raise FileExistsError(f"Refusing to overwrite {output}")
                started = now()
                try:
                    capture = await capture_rendered_abstract(page, adapter, event)
                    payload = {
                        "schema_version": ABSTRACT_CAPTURE_SCHEMA,
                        "source": SOURCE,
                        "source_id": SOURCE_ID,
                        "event_id": event["event_id"],
                        "paper_id": event["paper_id"],
                        "expected_title": event["title"],
                        "captured_at_utc": now(),
                        **capture,
                    }
                    success = payload["status"] in {
                        "full_source_abstract",
                        "source_abstract_not_available",
                    }
                except Exception as error:  # noqa: BLE001 - retain bounded per-record failure.
                    payload = {
                        "schema_version": ABSTRACT_CAPTURE_SCHEMA,
                        "source": SOURCE,
                        "source_id": SOURCE_ID,
                        "event_id": event["event_id"],
                        "paper_id": event["paper_id"],
                        "expected_title": event["title"],
                        "captured_at_utc": now(),
                        "status": "error",
                        "abstract": "",
                        "abstract_source": None,
                        "abstract_not_available": None,
                        "source_publication_type": event["document_type"],
                        "documentType": event["document_type"],
                        "error_type": type(error).__name__,
                        "do_not_merge": True,
                    }
                    success = False
                write_new(output, payload)
                outcomes.append(
                    {
                        "event_id": event["event_id"],
                        "paper_id": event["paper_id"],
                        "success": success,
                        "status": payload["status"],
                        "artifact": relative(output),
                        "artifact_sha256": digest(output),
                        "artifact_bytes": output.stat().st_size,
                        "abstract_characters": len(payload["abstract"]),
                        "source_publication_type": payload["source_publication_type"],
                        "started_at_utc": started,
                        "completed_at_utc": now(),
                    }
                )
                print(
                    json.dumps(
                        {
                            "abstract_event": event["event_id"],
                            "status": payload["status"],
                            "characters": len(payload["abstract"]),
                            "publication_type": payload["source_publication_type"],
                        }
                    ),
                    flush=True,
                )
        finally:
            await adapter.close_adapter_owned_page(page, "abstract follow-up")
            await adapter._browser_utils.close_chrome_connection(connection)
    return outcomes


def run_abstract_plan(
    abstract_plan_path: Path,
    source_plan_path: Path,
    source_receipt_path: Path,
    output_dir: Path,
    receipt_path: Path,
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    abstract_plan = load(abstract_plan_path)
    errors = validate_abstract_plan(
        abstract_plan,
        plan_path=source_plan_path,
        receipt_path=source_receipt_path,
    )
    if errors:
        raise FinalAiaaArcError("Invalid AIAA ARC abstract plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise FinalAiaaArcError("AIAA ARC abstract output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    for event in abstract_plan["events"]:
        output = output_dir / event["output"]
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {output}")
    started = now()
    target_id: str | None = None
    target_closed = False
    outcomes: list[dict[str, Any]] = []
    if abstract_plan["events"]:
        cdp_url = shared_browser_url()
        try:
            target_id = create_authorized_arc_target(cdp_url)
            outcomes = asyncio.run(
                _run_abstract_events(abstract_plan, output_dir, cdp_url, target_id)
            )
        finally:
            if target_id is not None:
                target_closed = close_target(cdp_url, target_id)
    success = len(outcomes) == len(abstract_plan["events"]) and all(
        outcome["success"] for outcome in outcomes
    )
    receipt = {
        "schema_version": ABSTRACT_RUN_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(abstract_plan_path),
        "plan_sha256": digest(abstract_plan_path),
        "source_search_plan": relative(source_plan_path),
        "source_search_plan_sha256": digest(source_plan_path),
        "source_search_receipt": relative(source_receipt_path),
        "source_search_receipt_sha256": digest(source_receipt_path),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(abstract_plan["events"]),
        "attempted_event_count": len(outcomes),
        "full_source_abstract_count": sum(
            outcome["status"] == "full_source_abstract" for outcome in outcomes
        ),
        "source_abstract_not_available_count": sum(
            outcome["status"] == "source_abstract_not_available"
            for outcome in outcomes
        ),
        "failed_event_count": sum(not outcome["success"] for outcome in outcomes),
        "all_events_attempted": len(outcomes) == len(abstract_plan["events"]),
        "authorized_arc_target_created": target_id is not None,
        "authorized_arc_target_close_requested": target_closed,
        "target_identifier_retained": False,
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def load_abstract_enrichment(
    abstract_plan_path: Path,
    abstract_receipt_path: Path,
    abstract_output_dir: Path,
) -> dict[str, dict[str, Any]]:
    plan = load(abstract_plan_path)
    receipt = load(abstract_receipt_path)
    if (
        receipt.get("schema_version") != ABSTRACT_RUN_SCHEMA
        or receipt.get("plan") != relative(abstract_plan_path)
        or receipt.get("plan_sha256") != digest(abstract_plan_path)
        or receipt.get("success") is not True
        or receipt.get("all_events_attempted") is not True
    ):
        raise FinalAiaaArcError("AIAA ARC abstract follow-up run is incomplete")
    outcome_map = {
        outcome.get("event_id"): outcome
        for outcome in receipt.get("outcomes", [])
        if isinstance(outcome, Mapping)
    }
    records: dict[str, dict[str, Any]] = {}
    for event in plan["events"]:
        outcome = outcome_map.get(event["event_id"])
        path = abstract_output_dir / event["output"]
        capture = load(path)
        if (
            not isinstance(outcome, Mapping)
            or outcome.get("success") is not True
            or outcome.get("artifact_sha256") != digest(path)
            or outcome.get("artifact_bytes") != path.stat().st_size
            or capture.get("schema_version") != ABSTRACT_CAPTURE_SCHEMA
            or capture.get("event_id") != event["event_id"]
            or capture.get("paper_id") != event["paper_id"]
            or capture.get("documentType") != event["document_type"]
            or capture.get("status")
            not in {"full_source_abstract", "source_abstract_not_available"}
        ):
            raise FinalAiaaArcError("AIAA ARC abstract capture is invalid")
        abstract = capture.get("abstract")
        if not isinstance(abstract, str):
            raise FinalAiaaArcError("AIAA ARC abstract capture lacks text")
        if capture["status"] == "full_source_abstract" and not abstract.strip():
            raise FinalAiaaArcError("AIAA ARC full abstract capture is empty")
        if capture["status"] == "source_abstract_not_available" and (
            abstract or capture.get("abstract_not_available") is not True
        ):
            raise FinalAiaaArcError("AIAA ARC unavailable abstract state is invalid")
        records[event["paper_id"]] = capture
    return records


def build_record_union(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    abstract_plan_path: Path,
    abstract_receipt_path: Path,
    abstract_output_dir: Path,
    output: Path,
) -> dict[str, Any]:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    records, artifact_rows = raw_unique_records(plan_path, receipt_path, output_dir)
    abstract_plan = load(abstract_plan_path)
    errors = validate_abstract_plan(
        abstract_plan,
        plan_path=plan_path,
        receipt_path=receipt_path,
    )
    if errors:
        raise FinalAiaaArcError("Invalid AIAA ARC abstract plan: " + ", ".join(errors))
    enrichment = load_abstract_enrichment(
        abstract_plan_path,
        abstract_receipt_path,
        abstract_output_dir,
    )
    retained_occurrences = sum(row["retained_record_count"] for row in artifact_rows)
    source_total_sum = sum(row["source_total"] for row in artifact_rows)
    full_abstracts = 0
    source_unavailable = 0
    publication_types: Counter[str] = Counter()
    union_rows: list[dict[str, Any]] = []
    for identifier in sorted(records):
        item = records[identifier]
        record = item.get("record")
        if not isinstance(record, dict):
            raise FinalAiaaArcError("AIAA ARC record union contains no selected record")
        document_type = record.get("documentType")
        if not isinstance(document_type, str) or not document_type.strip():
            raise FinalAiaaArcError("AIAA ARC record union lost its source publication type")
        publication_types[document_type] += 1
        native_abstract = record.get("abstract")
        if not isinstance(native_abstract, str):
            raise FinalAiaaArcError("AIAA ARC record union lost its abstract field")
        if native_abstract.strip():
            record["abstract_source"] = NATIVE_ABSTRACT_SOURCE
            record["abstract_not_available"] = False
            record["abstract_capture_status"] = "full_source_abstract"
            full_abstracts += 1
        else:
            capture = enrichment.get(identifier)
            if not isinstance(capture, Mapping):
                raise FinalAiaaArcError("AIAA ARC blank native abstract lacks detail follow-up")
            record["abstract"] = capture["abstract"]
            record["abstract_source"] = capture["abstract_source"]
            record["abstract_not_available"] = capture["abstract_not_available"]
            record["abstract_capture_status"] = capture["status"]
            if capture["status"] == "full_source_abstract":
                full_abstracts += 1
            else:
                source_unavailable += 1
        record["sourcePublicationType"] = document_type
        record["sourcePublicationTypeSource"] = NATIVE_PUBLICATION_TYPE_SOURCE
        item["source_record_stable_ids"].sort()
        item["discovery_cells"].sort()
        item["discovery_partitions"].sort(key=PARTITIONS.index)
        union_rows.append(item)
    complete = bool(
        len(union_rows) == len(records)
        and full_abstracts + source_unavailable == len(union_rows)
        and sum(publication_types.values()) == len(union_rows)
        and all(
            isinstance(item["record"].get("abstract"), str)
            and item["record"].get("abstract_capture_status")
            in {"full_source_abstract", "source_abstract_not_available"}
            and isinstance(item["record"].get("documentType"), str)
            and bool(item["record"]["documentType"])
            and item["record"].get("sourcePublicationType")
            == item["record"].get("documentType")
            for item in union_rows
        )
    )
    if not complete:
        raise FinalAiaaArcError("AIAA ARC final record capture did not reconcile")
    value = {
        "schema_version": RECORD_UNION_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "purpose": "deduplicated_final_direct_source_records_with_full_abstracts_and_source_publication_types",
        "reviewer_publication_type_coding": "not inferred from source metadata",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "abstract_follow_up_plan": relative(abstract_plan_path),
        "abstract_follow_up_plan_sha256": digest(abstract_plan_path),
        "abstract_follow_up_receipt": relative(abstract_receipt_path),
        "abstract_follow_up_receipt_sha256": digest(abstract_receipt_path),
        "input_artifacts": artifact_rows,
        "source_event_source_total_sum": source_total_sum,
        "source_event_retained_record_count": retained_occurrences,
        "unique_canonical_doi_count": len(union_rows),
        "cross_cell_duplicate_occurrences": retained_occurrences - len(union_rows),
        "canonical_doi_set_sha256": digest_ids(set(records)),
        "records_with_full_abstract": full_abstracts,
        "records_with_source_abstract_unavailable": source_unavailable,
        "records_with_resolved_abstract_state": full_abstracts + source_unavailable,
        "records_with_source_publication_type": len(union_rows),
        "records_missing_source_publication_type": 0,
        "source_publication_type_counts": dict(sorted(publication_types.items())),
        "abstract_sources": [
            NATIVE_ABSTRACT_SOURCE,
            ABSTRACT_SOURCE_HTML,
            ABSTRACT_SOURCE_READER,
            ABSTRACT_SOURCE_UNAVAILABLE,
        ],
        "source_publication_type_source": NATIVE_PUBLICATION_TYPE_SOURCE,
        "complete": complete,
        "records": union_rows,
    }
    write_new(output, value)
    return value


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    declarations_path: Path,
    source_union_path: Path,
    abstract_plan_path: Path,
    abstract_receipt_path: Path,
    abstract_output_dir: Path,
    record_union_path: Path,
    output: Path,
) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output}")
    plan = load(plan_path)
    receipt = load(receipt_path)
    declarations = load(declarations_path)
    source_union = load(source_union_path)
    abstract_plan = load(abstract_plan_path)
    abstract_receipt = load(abstract_receipt_path)
    record_union = load(record_union_path)
    errors = validate_plan(plan, verify_bindings=False)
    if (
        receipt.get("schema_version") != RUN_SCHEMA
        or receipt.get("plan") != relative(plan_path)
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("success") is not True
        or receipt.get("accepted_source_cell_count") != len(plan["events"])
    ):
        errors.append("run_receipt")
    if (
        declarations.get("schema_version") != CELL_DECLARATIONS_SCHEMA
        or declarations.get("plan_sha256") != digest(plan_path)
        or declarations.get("run_receipt_sha256") != digest(receipt_path)
        or len(declarations.get("expected_cells", [])) != len(plan["events"])
    ):
        errors.append("cell_declarations")
    try:
        selected = successful_event_artifacts(plan_path, receipt_path, output_dir)
    except (OSError, ValueError, json.JSONDecodeError, FinalAiaaArcError) as error:
        errors.append(f"events:{type(error).__name__}")
        selected = []

    event_rows: list[dict[str, Any]] = []
    retained_occurrences = 0
    source_total_sum = 0
    all_ids: set[str] = set()
    for event, outcome, artifact, data in selected:
        summary = artifact_summary(
            output_dir,
            event,
            plan_path,
            plan,
            require_capture_receipt=True,
        )
        if summary.get("valid") is not True or outcome.get("success") is not True:
            errors.append(f"event:{event['cell_id']}")
        if (
            outcome.get("artifact_sha256") != digest(artifact)
            or outcome.get("artifact_bytes") != artifact.stat().st_size
        ):
            errors.append(f"artifact_binding:{event['cell_id']}")
        retained_occurrences += len(data["results"])
        source_total_sum += data["total"]
        ids = [canonical_doi(row["paperId"]) for row in data["results"]]
        all_ids.update(ids)
        event_rows.append(
            {
                "partition_id": event["partition_id"],
                "cell_id": event["cell_id"],
                "artifact": relative(artifact),
                "artifact_sha256": digest(artifact),
                "source_total": data["total"],
                "retained_record_count": len(data["results"]),
                "client_exact_date_excluded_count": summary.get(
                    "client_exact_date_excluded_count"
                ),
                "stable_ids": ids,
                "stable_id_set_sha256": digest_ids(set(ids)),
                "full_abstract_count": summary.get("record_capture", {}).get(
                    "full_abstract_count"
                ),
                "missing_full_abstract_count": summary.get("record_capture", {}).get(
                    "missing_full_abstract_count"
                ),
                "source_publication_type_counts": summary.get("record_capture", {}).get(
                    "source_publication_type_counts"
                ),
                "missing_source_publication_type_count": summary.get(
                    "record_capture", {}
                ).get("missing_source_publication_type_count"),
                "native_ris_valid": summary.get("native_ris_valid"),
                "capture_receipt_valid": summary.get("capture_receipt_valid"),
                "screenshots_valid": summary.get("screenshots_valid"),
                "terminal_marker_valid": summary.get("terminal_marker_valid"),
            }
        )

    union_source = source_union.get("source_unions", {}).get(SOURCE_ID, {})
    union_valid = bool(
        source_union.get("review_namespace") == REVIEW_NAMESPACE
        and source_union.get("review_id") == REVIEW_ID
        and source_union.get("strategy_reference") == plan.get("strategy_reference")
        and source_union.get("expected_partitions") == list(PARTITIONS)
        and source_union.get("expected_sources") == [SOURCE_ID]
        and source_union.get("completeness_status") == "complete"
        and source_union.get("failure_status") == "none"
        and source_union.get("artifact_count") == len(plan["events"])
        and union_source.get("event_total_sum") == retained_occurrences
        and {
            canonical_doi(identifier)
            for identifier in union_source.get("stable_record_ids", [])
            if isinstance(identifier, str)
        }
        == all_ids
    )
    if not union_valid:
        errors.append("source_union")
    cell_unions = source_union.get("cell_unions", {}).get(SOURCE_ID, {})
    for partition in PARTITIONS:
        expected_count = sum(event["partition_id"] == partition for event in plan["events"])
        if cell_unions.get(partition, {}).get("cell_count") != expected_count:
            errors.append(f"source_union_cell:{partition}")

    abstract_plan_errors = validate_abstract_plan(
        abstract_plan,
        plan_path=plan_path,
        receipt_path=receipt_path,
    )
    if abstract_plan_errors:
        errors.extend(f"abstract_plan:{error}" for error in abstract_plan_errors)
    if (
        abstract_receipt.get("schema_version") != ABSTRACT_RUN_SCHEMA
        or abstract_receipt.get("plan") != relative(abstract_plan_path)
        or abstract_receipt.get("plan_sha256") != digest(abstract_plan_path)
        or abstract_receipt.get("success") is not True
        or abstract_receipt.get("all_events_attempted") is not True
    ):
        errors.append("abstract_run")
    try:
        detail_records = load_abstract_enrichment(
            abstract_plan_path,
            abstract_receipt_path,
            abstract_output_dir,
        )
    except (OSError, ValueError, json.JSONDecodeError, FinalAiaaArcError) as error:
        errors.append(f"abstract_captures:{type(error).__name__}")
        detail_records = {}

    record_rows = record_union.get("records")
    full_abstract_count = record_union.get("records_with_full_abstract")
    unavailable_abstract_count = record_union.get(
        "records_with_source_abstract_unavailable"
    )
    record_union_valid = bool(
        record_union.get("schema_version") == RECORD_UNION_SCHEMA
        and record_union.get("plan_sha256") == digest(plan_path)
        and record_union.get("run_receipt_sha256") == digest(receipt_path)
        and record_union.get("source_event_source_total_sum") == source_total_sum
        and record_union.get("source_event_retained_record_count") == retained_occurrences
        and record_union.get("unique_canonical_doi_count") == len(all_ids)
        and record_union.get("canonical_doi_set_sha256") == digest_ids(all_ids)
        and isinstance(full_abstract_count, int)
        and isinstance(unavailable_abstract_count, int)
        and full_abstract_count + unavailable_abstract_count == len(all_ids)
        and record_union.get("records_with_resolved_abstract_state") == len(all_ids)
        and record_union.get("records_with_source_publication_type") == len(all_ids)
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("complete") is True
        and isinstance(record_rows, list)
        and len(record_rows) == len(all_ids)
    )
    if not record_union_valid:
        errors.append("record_union")

    complete = bool(len(event_rows) == len(plan["events"]) and not errors)
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final",
        "complete": complete,
        "errors": errors,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "cell_declarations": relative(declarations_path),
        "cell_declarations_sha256": digest(declarations_path),
        "source_union": relative(source_union_path),
        "source_union_sha256": digest(source_union_path),
        "abstract_follow_up_plan": relative(abstract_plan_path),
        "abstract_follow_up_plan_sha256": digest(abstract_plan_path),
        "abstract_follow_up_receipt": relative(abstract_receipt_path),
        "abstract_follow_up_receipt_sha256": digest(abstract_receipt_path),
        "rendered_abstract_capture_count": len(detail_records),
        "record_union": relative(record_union_path),
        "record_union_sha256": digest(record_union_path),
        "adapter": plan.get("adapter"),
        "cutoff": plan.get("cutoff"),
        "accepted_source_cell_count": len(event_rows),
        "events": event_rows,
        "stable_id_union": {
            "source_event_source_total_sum": source_total_sum,
            "source_event_retained_record_count": retained_occurrences,
            "unique_canonical_doi_count": len(all_ids),
            "cross_cell_duplicate_occurrences": retained_occurrences - len(all_ids),
            "canonical_doi_set_sha256": digest_ids(all_ids),
            "hash_algorithm": "sha256_length_prefixed_utf8_canonical_lexical_set",
        },
        "record_capture": {
            "full_abstracts_required": True,
            "source_publication_types_required": True,
            "abstract_sources": record_union.get("abstract_sources"),
            "source_publication_type_source": NATIVE_PUBLICATION_TYPE_SOURCE,
            "reviewer_publication_type_coding": "deferred to screening",
            "unique_records_with_full_abstract": full_abstract_count,
            "unique_records_with_source_abstract_unavailable": unavailable_abstract_count,
            "unique_records_with_resolved_abstract_state": record_union.get(
                "records_with_resolved_abstract_state"
            ),
            "unique_records_with_source_publication_type": record_union.get(
                "records_with_source_publication_type"
            ),
            "unique_records_without_source_publication_type": record_union.get(
                "records_missing_source_publication_type"
            ),
            "source_publication_type_counts": record_union.get(
                "source_publication_type_counts"
            ),
        },
    }
    write_new(output, assessment)
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--sequence", type=int, default=1)
    plan_parser.add_argument("--superseded-plan", type=Path)
    plan_parser.add_argument("--superseded-receipt", type=Path)

    check_parser = commands.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    check_parser.add_argument("--verify-bindings", action="store_true")

    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=INTER_EVENT_DELAY_SECONDS)

    declarations_parser = commands.add_parser("cell-declarations")
    declarations_parser.add_argument("--plan", type=Path, required=True)
    declarations_parser.add_argument("--receipt", type=Path, required=True)
    declarations_parser.add_argument("--output-dir", type=Path, required=True)
    declarations_parser.add_argument("--output", type=Path, required=True)

    source_union_parser = commands.add_parser("source-union")
    source_union_parser.add_argument("--plan", type=Path, required=True)
    source_union_parser.add_argument("--receipt", type=Path, required=True)
    source_union_parser.add_argument("--output-dir", type=Path, required=True)
    source_union_parser.add_argument("--cell-declarations", type=Path, required=True)
    source_union_parser.add_argument("--output", type=Path, required=True)

    abstract_plan_parser = commands.add_parser("abstract-plan")
    abstract_plan_parser.add_argument("--plan", type=Path, required=True)
    abstract_plan_parser.add_argument("--receipt", type=Path, required=True)
    abstract_plan_parser.add_argument("--output-dir", type=Path, required=True)
    abstract_plan_parser.add_argument("--output", type=Path, required=True)

    abstract_run_parser = commands.add_parser("abstract-run")
    abstract_run_parser.add_argument("--abstract-plan", type=Path, required=True)
    abstract_run_parser.add_argument("--plan", type=Path, required=True)
    abstract_run_parser.add_argument("--receipt", type=Path, required=True)
    abstract_run_parser.add_argument("--output-dir", type=Path, required=True)
    abstract_run_parser.add_argument("--output-receipt", type=Path, required=True)

    record_union_parser = commands.add_parser("record-union")
    record_union_parser.add_argument("--plan", type=Path, required=True)
    record_union_parser.add_argument("--receipt", type=Path, required=True)
    record_union_parser.add_argument("--output-dir", type=Path, required=True)
    record_union_parser.add_argument("--abstract-plan", type=Path, required=True)
    record_union_parser.add_argument("--abstract-receipt", type=Path, required=True)
    record_union_parser.add_argument("--abstract-output-dir", type=Path, required=True)
    record_union_parser.add_argument("--output", type=Path, required=True)

    assessment_parser = commands.add_parser("assess")
    assessment_parser.add_argument("--plan", type=Path, required=True)
    assessment_parser.add_argument("--receipt", type=Path, required=True)
    assessment_parser.add_argument("--output-dir", type=Path, required=True)
    assessment_parser.add_argument("--cell-declarations", type=Path, required=True)
    assessment_parser.add_argument("--source-union", type=Path, required=True)
    assessment_parser.add_argument("--abstract-plan", type=Path, required=True)
    assessment_parser.add_argument("--abstract-receipt", type=Path, required=True)
    assessment_parser.add_argument("--abstract-output-dir", type=Path, required=True)
    assessment_parser.add_argument("--record-union", type=Path, required=True)
    assessment_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "plan":
            plan = build_plan(
                sequence=args.sequence,
                superseded_plan=args.superseded_plan,
                superseded_receipt=args.superseded_receipt,
            )
            errors = validate_plan(plan, verify_bindings=False)
            if errors:
                raise FinalAiaaArcError("Generated an invalid AIAA ARC plan: " + ", ".join(errors))
            write_new(args.output, plan)
            print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
            return 0
        if args.command == "check-plan":
            errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
            print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
            return 0 if not errors else 1
        if args.command == "run":
            return run_final(
                args.plan,
                args.output_dir,
                args.receipt,
                settle_seconds=args.settle_seconds,
            )
        if args.command == "cell-declarations":
            build_cell_declarations(args.plan, args.receipt, args.output_dir, args.output)
            return 0
        if args.command == "source-union":
            return run_source_union(
                args.plan,
                args.receipt,
                args.output_dir,
                args.cell_declarations,
                args.output,
            )
        if args.command == "abstract-plan":
            write_new(
                args.output,
                build_abstract_plan(args.plan, args.receipt, args.output_dir),
            )
            return 0
        if args.command == "abstract-run":
            return run_abstract_plan(
                args.abstract_plan,
                args.plan,
                args.receipt,
                args.output_dir,
                args.output_receipt,
            )
        if args.command == "record-union":
            build_record_union(
                args.plan,
                args.receipt,
                args.output_dir,
                args.abstract_plan,
                args.abstract_receipt,
                args.abstract_output_dir,
                args.output,
            )
            return 0
        if args.command == "assess":
            return assess(
                args.plan,
                args.receipt,
                args.output_dir,
                args.cell_declarations,
                args.source_union,
                args.abstract_plan,
                args.abstract_receipt,
                args.abstract_output_dir,
                args.record_union,
                args.output,
            )
    except Exception as error:  # noqa: BLE001 - command boundary preserves source artifacts.
        print(str(error), file=sys.stderr)
        return 1
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
