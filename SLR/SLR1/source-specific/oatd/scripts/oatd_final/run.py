#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "playwright>=1.48,<2",
# ]
# ///
"""Plan, execute, and validate the final OATD eight-gate source union."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import secrets
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
sys.path.insert(0, str(SCRIPT_DIR))
import record_metadata
import source_native

SLR1_ROOT = SCRIPT_PATH.parents[4]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
DEFAULT_FINAL_ROOT = SLR1_ROOT / "source-specific/oatd/final-searches"
FINAL_ROOT = DEFAULT_FINAL_ROOT
PLAN_PATH = FINAL_ROOT / "final-event-plan.json"
RECEIPT_PATH = FINAL_ROOT / "run-receipt.json"
UNION_PATH = FINAL_ROOT / "hydrated-union.json"
CHECKPOINT_PATH = FINAL_ROOT / "checkpoint/hydrated-union.checkpoint.json"
VALIDATION_PATH = FINAL_ROOT / "validation-report.json"
ASSESSMENT_PATH = FINAL_ROOT / "assessment.json"
GUIDELINE_PATH = SLR1_ROOT / "source-specific/oatd/source-specific-guidelines.md"
DISCOVERY_PROTOCOL_PATH = SLR1_ROOT / "protocol-discovery-and-screening.md"
MAIN_PROTOCOL_PATH = SLR1_ROOT / "protocol.md"
QUERY_PATH = SLR1_ROOT / "source-specific/oatd/scripts/oatd_pilot006/queries.py"
LOCAL_PLAN_PATH = (
    SLR1_ROOT / "source-specific/oatd/pilots/004/searches/local-matching-plan.json"
)
ADAPTER_ROOT = Path.home() / "agent-tools"
ADAPTER_PATH = ADAPTER_ROOT / "internet/skills/browser/scripts/search_oatd.py"
ADAPTER_FILES = {
    "entrypoint": ADAPTER_PATH,
    "browser_helpers": ADAPTER_PATH.with_name("_browser_search_utils.py"),
    "output_loader": ADAPTER_PATH.with_name("_output_utils.py"),
    "output_implementation": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_output_utils.py"
    ),
    "merge_contract": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_merge_contract.py"
    ),
}

PLAN_SCHEMA = "slr1-oatd-final-plan/v1"
RUN_SCHEMA = "slr1-oatd-final-run/v1"
CHECKPOINT_SCHEMA = "slr1-oatd-final-hydration-checkpoint/v2"
GATE_SCHEMA = "slr1-oatd-final-gate/v2"
GATE_MARKER_SCHEMA = "slr1-oatd-final-gate-commit/v1"
VALIDATION_SCHEMA = "slr1-oatd-final-validation/v1"
ASSESSMENT_SCHEMA = "slr1-oatd-final-assessment/v1"

CUTOFF_DATE = "2026-08-24"
YEAR_START = 2011
YEAR_END = 2026
PAGE_SIZE = 30
CARD_LIMIT = 100
MAX_PAGES = 4
REVIEW_ID = "slr1-1.1-restart"
RUN_ID = "final-main-oatd-001"
STRATEGY_REFERENCE = "slr1-oatd-main-direct-v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise RuntimeError("A source timestamp lacked a timezone")
    return parsed.astimezone(timezone.utc)


def configure_final_root(root: Path | None) -> None:
    """Select the initial or an explicitly bounded corrective output root."""
    global FINAL_ROOT, PLAN_PATH, RECEIPT_PATH, UNION_PATH, CHECKPOINT_PATH
    global VALIDATION_PATH, ASSESSMENT_PATH, RUN_ID, STRATEGY_REFERENCE
    selected = (root or DEFAULT_FINAL_ROOT).resolve(strict=False)
    permitted = {
        DEFAULT_FINAL_ROOT.resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-002").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-003").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-004").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-005").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-006").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-007").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-008").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-009").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-010").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-011").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-012").resolve(strict=False),
        (DEFAULT_FINAL_ROOT / "corrective-013").resolve(strict=False),
    }
    if selected not in permitted:
        raise RuntimeError("The OATD final root must be the initial directory or a declared corrective-002 through corrective-013 directory")
    FINAL_ROOT = selected
    PLAN_PATH = FINAL_ROOT / "final-event-plan.json"
    RECEIPT_PATH = FINAL_ROOT / "run-receipt.json"
    UNION_PATH = FINAL_ROOT / "hydrated-union.json"
    CHECKPOINT_PATH = FINAL_ROOT / "checkpoint/hydrated-union.checkpoint.json"
    VALIDATION_PATH = FINAL_ROOT / "validation-report.json"
    ASSESSMENT_PATH = FINAL_ROOT / "assessment.json"
    sequence = 1 if selected == DEFAULT_FINAL_ROOT.resolve(strict=False) else int(selected.name.rsplit("-", 1)[1])
    RUN_ID = f"final-main-oatd-{sequence:03d}"
    STRATEGY_REFERENCE = f"slr1-oatd-main-direct-v{sequence}"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPOSITORY_ROOT.resolve()))


def repository_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise RuntimeError("Could not determine the repository revision")
    return value


def load_queries() -> Any:
    spec = importlib.util.spec_from_file_location("slr1_oatd_final_queries", QUERY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if tuple(module.GATE_QUERIES) != tuple(module.GATE_IDS):
        raise RuntimeError("The OATD final gate declaration order is invalid")
    return module


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("slr1_oatd_final_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module.ADAPTER_ID != "search_oatd" or module.ADAPTER_VERSION != "10":
        raise RuntimeError("The final OATD workflow requires search_oatd adapter v10")
    return module


def write_exclusive_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error
    try:
        view = memoryview(payload)
        while view:
            view = view[os.write(descriptor, view) :]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_exclusive_json(path: Path, value: Mapping[str, Any]) -> None:
    write_exclusive_bytes(
        path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )


def write_atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError("Refusing to replace a symlink checkpoint")
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
        fsync_parent(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def fsync_parent(path: Path) -> None:
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def gate_marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.OATD_FINAL_GATE_COMMIT.json")


def absent(path: Path) -> bool:
    return not os.path.lexists(path)


def source_affecting_bindings() -> dict[str, str]:
    paths = (SCRIPT_PATH, SCRIPT_DIR / "record_metadata.py", SCRIPT_DIR / "source_native.py",
             SCRIPT_DIR / "diagnose.py", SCRIPT_DIR / "native_detail.py", SCRIPT_DIR / "continue_native.py",
             QUERY_PATH, GUIDELINE_PATH, DISCOVERY_PROTOCOL_PATH, MAIN_PROTOCOL_PATH)
    return {relative(path): digest(path) for path in paths}


def build_configuration(adapter: Any, query: str, **controls: Any) -> Any:
    """Keep the native basic form transport while preserving exact typed q clauses.

    The source's basic form submits form=basic even when q contains language and
    date clauses. The 2026-09-05 live comparison returned HTTP 500 for the first
    gate without that parameter and an exact 17-record readback with it.
    """
    configuration = adapter.build_oatd_search_configuration(query, **controls)
    parameters = tuple(pair for pair in configuration.route_parameters if pair[0] != "form")
    return replace(configuration, route_parameters=parameters + (("form", "basic"),),
                   legacy_basic_route=True)


def plan_event(adapter: Any, event_id: str, query: str) -> dict[str, Any]:
    configuration = build_configuration(adapter,
        query,
        language="English",
        year_start=YEAR_START,
        year_end=YEAR_END,
        page_size=PAGE_SIZE,
    )
    route = adapter.build_search_url(query, configuration=configuration)
    output = FINAL_ROOT / "gates" / f"{event_id}.json"
    screenshots = adapter.screenshot_paths_for_output(output)
    if len(route) > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS:
        raise RuntimeError(f"OATD final gate exceeds the reviewed route ceiling: {event_id}")
    return {
        "event_id": event_id,
        "query": query,
        "query_sha256": text_digest(query),
        "query_characters": len(query),
        "effective_query": configuration.effective_query,
        "effective_query_sha256": text_digest(configuration.effective_query),
        "navigation_route_characters": len(route),
        "language": "English",
        "language_source_value": "(en OR eng OR english)",
        "year_start": YEAR_START,
        "year_end": YEAR_END,
        "page_size": PAGE_SIZE,
        "limit": CARD_LIMIT,
        "max_pages": MAX_PAGES,
        "timeout_seconds": 180.0,
        "page_delay_seconds": 6.0,
        "busy_retries": 1,
        "busy_retry_delay_seconds": 120.0,
        "output": str(output.relative_to(FINAL_ROOT)),
        "screenshots": {
            "search_page": str(screenshots.search_page.relative_to(FINAL_ROOT)),
            "results_page": str(screenshots.results_page.relative_to(FINAL_ROOT)),
        },
    }


def corrective_run_context() -> tuple[dict[str, Any] | None, str | None]:
    """Bind each corrective event to the retained immediately prior attempt."""
    initial_root = DEFAULT_FINAL_ROOT.resolve(strict=False)
    if FINAL_ROOT == initial_root:
        return None, None
    if FINAL_ROOT.name == "corrective-002":
        sequence = 2
        prior_root = initial_root
        cooldown_seconds = 1800
        reason = (
            "The initial final attempt completed all eight initial card-ID snapshots "
            "but stopped before any Record Details request because a local checkpoint "
            "field name conflicted with the adapter's safe-content guard. No gate or "
            "hydrated-union artifact was published."
        )
    elif FINAL_ROOT.name == "corrective-003":
        sequence = 3
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-002").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Corrective run 002 stopped before opening any OATD source page because "
            "the shared CDP browser could not verify an adapter-owned target."
        )
    elif FINAL_ROOT.name == "corrective-004":
        sequence = 4
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-003").resolve(strict=False)
        cooldown_seconds = 1800
        reason = (
            "Corrective run 003 was operator-cancelled after its plan selected an "
            "invocation-owned browser. The final workflow requires the shared Chrome "
            "profile to retain its established OATD access state. This run uses only "
            "the shared chrome-automation profile on loopback CDP port 9222."
        )
    elif FINAL_ROOT.name == "corrective-005":
        sequence = 5
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-004").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Corrective run 004 was cancelled during a local pre-source wait for all "
            "shared-browser jobs to finish. Complete quiescence is unnecessary after "
            "an OATD sibling tab has proven ownership. This run uses bounded local "
            "target-acquisition retries, then permits concurrent shared-profile tabs."
        )
    elif FINAL_ROOT.name == "corrective-006":
        sequence = 6
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-005").resolve(strict=False)
        cooldown_seconds = 1800
        reason = (
            "Corrective run 005 acquired a shared-profile owned tab, then OATD returned "
            "HTTP 504 on the first gate before any gate, checkpoint, or union artifact "
            "was published. This clean corrective run follows a 30-minute source cooldown."
        )
    elif FINAL_ROOT.name == "corrective-007":
        sequence = 7
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-006").resolve(strict=False)
        cooldown_seconds = 3600
        reason = (
            "Corrective run 006 received a second HTTP 504 on the first exact gate "
            "after its 30-minute cooldown. No gate, checkpoint, or union artifact was published. "
            "This final clean attempt retains the exact route and waits one hour."
        )
    elif FINAL_ROOT.name == "corrective-008":
        sequence = 8
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-007").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Independent native UI investigation recovered the exact G1 gate with "
            "form=basic and unchanged English/year clauses. The q-only route returned "
            "HTTP 500. This run retains native form transport, takes two initial "
            "passes and one confirmation, persists progress, and records source "
            "abstract truncation plus native degree/type evidence. See code-audit/."
        )
    elif FINAL_ROOT.name == "corrective-009":
        sequence = 9
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-008").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Run 008 captured four initial gate sets, then direct URL navigation "
            "failed on G2D-MB-T. An independent native form submission returned "
            "an exact zero for the unchanged controlled query. This run uses "
            "actual native form submission and the independent rendered-observation "
            "sequence in a directly created owned page for each pass. Live checks "
            "validated zero, multi-record, and singleton gates. The backend cause "
            "of the HTTP errors remains unknown. No earlier gate or detail record is reused."
        )
    elif FINAL_ROOT.name == "corrective-010":
        sequence = 10
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-009").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Run 009 completed all 16 initial gate passes and saved the exact 27-ID "
            "checkpoint, then its first reconstructed direct detail request returned "
            "HTTP 504. Native keyboard activation of the observed Record Details "
            "link retrieved that record. This continuation binds and retains those "
            "16 complete final passes, reuses no hydrated or pilot record, and "
            "requires native detail hydration plus eight equal final confirming sets."
        )
    elif FINAL_ROOT.name == "corrective-011":
        sequence = 11
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-010").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Continuation 010 hydrated and checkpointed one native Record Details "
            "record, then waited for a DOMContentLoaded event that cached browser "
            "Back does not require. This continuation uses the adapter's reviewed "
            "commit-based history restoration and source-state validation. It "
            "retains that validated detail and the 16 complete initial final passes."
        )
    elif FINAL_ROOT.name == "corrective-012":
        sequence = 12
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-011").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Continuation 011 retained nine complete details, then the MIT detail "
            "route failed with the full gate in q. The same observed Record ID "
            "with an empty q display context returned the same MIT metadata. "
            "This continuation separates fixed full-query gate membership from "
            "stable-ID metadata lookup. It retains the 16 initial final passes "
            "and nine validated details, then requires all eight confirming sets."
        )
    elif FINAL_ROOT.name == "corrective-013":
        sequence = 13
        prior_root = (DEFAULT_FINAL_ROOT / "corrective-012").resolve(strict=False)
        cooldown_seconds = 0
        reason = (
            "Continuation 012 retained ten validated details. An empty-q lookup "
            "failed for the next record, while an explicitly awaited native-link "
            "navigation retrieved it. This continuation uses that native navigation "
            "and permits one bounded alternate display-context lookup on HTTP "
            "500/504. It retains all validated final evidence and requires the "
            "same eight complete final confirming gate sets."
        )
    else:  # configure_final_root rejects every other root.
        raise RuntimeError("The OATD corrective sequence is unknown")
    prior_plan = prior_root / "final-event-plan.json"
    failures = sorted(prior_root.glob("failure-receipt-*.json"))
    if not prior_plan.is_file() or not failures:
        raise RuntimeError("A corrective OATD final run requires the retained prior plan and failure receipt")
    prior_failure = failures[-1]
    failure = load(prior_failure)
    completed_at = failure.get("completed_at_utc")
    if failure.get("success") is not False or not isinstance(completed_at, str):
        raise RuntimeError("The retained OATD prior failure receipt is invalid")
    not_before = parse_utc(completed_at).timestamp() + cooldown_seconds
    return (
        {
            "sequence": sequence,
            "reason": reason,
            "superseded_plan": relative(prior_plan),
            "superseded_plan_sha256": digest(prior_plan),
            "superseded_failure_receipt": relative(prior_failure),
            "superseded_failure_receipt_sha256": digest(prior_failure),
            "minimum_cooldown_after_prior_attempt_seconds": cooldown_seconds,
        },
        datetime.fromtimestamp(not_before, timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def build_plan() -> dict[str, Any]:
    adapter = load_adapter()
    queries = load_queries()
    local_plan = adapter.load_local_matching_plan(LOCAL_PLAN_PATH)
    corrective, not_before = corrective_run_context()
    events = [
        plan_event(adapter, event_id, queries.GATE_QUERIES[event_id])
        for event_id in queries.GATE_IDS
    ]
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "output_root": relative(FINAL_ROOT),
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "review_id": REVIEW_ID,
        "run_id": RUN_ID,
        "phase": "identification",
        "strategy_reference": STRATEGY_REFERENCE,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "cutoff": {
            "exact_common_cutoff": CUTOFF_DATE,
            "source_year_start": YEAR_START,
            "source_year_upper_bound": YEAR_END,
            "source_precision": "year",
            "screening_requirement": (
                "Screen every 2026 record against the exact common cutoff. "
                "OATD applies only inclusive calendar-year source bounds."
            ),
        },
        "source_configuration": {
            "collection": "Full OATD index",
            "endpoint": "https://oatd.org/oatd/search",
            "field": "raw basic q over OATD advertised metadata scope",
            "native_form_parameter": "basic",
            "submission_method": "source basic form submission with complete controlled q",
            "language": "English",
            "language_source_value": "(en OR eng OR english)",
            "publication_type_filter": None,
            "publication_type_scope": "OATD ETD index",
            "country_filter": None,
            "creative_commons_filter": None,
            "sort": "source_rendered_relevance_not_oldest_first",
            "page_size": PAGE_SIZE,
            "full_abstracts_required": True,
            "source_publication_type_required": True,
        },
        "candidate_route": {
            "identity": queries.ALGEBRAIC_IDENTITY,
            "implementation": "eight exact source-native gates",
            "gate_ids": list(queries.GATE_IDS),
            "partition_branch_coverage": {
                key: list(value)
                for key, value in queries.PARTITION_BRANCH_COVERAGE.items()
            },
            "no_population_only_detail_route": True,
        },
        "execution_policy": {
            "initial_complete_card_id_passes_per_gate": 2,
            "confirmation_complete_card_id_passes_per_gate": 1,
            "membership_gate": "equal complete unique stable-ID sets per gate",
            "deduplicate_before_record_details": True,
            "detail_hydration": "one owned Record Details page request per unique stable ID",
            "local_negative_removal": 0,
            "stop_after_source_detail_or_confirmation_failure": True,
            "inter_gate_delay_seconds": 120.0,
            "pre_detail_delay_seconds": 180.0,
            "detail_delay_seconds": 15.0,
            "detail_batch_size": 8,
            "detail_batch_cooldown_seconds": 180.0,
            "pre_confirmation_delay_seconds": 300.0,
            "detail_busy_retries": 2,
            "detail_busy_retry_delay_seconds": 120.0,
            "http_504_retry": False,
            "fresh_browser": False,
            "browser_profile": "shared_chrome_automation_cdp_9222",
            "existing_shared_tabs_modified": False,
            "shared_target_acquisition_attempts": 1,
            "shared_target_acquisition_delay_seconds": 0.0,
            "shared_target_retry_scope": "no automatic local retry",
            "gate_page_lifecycle": "one directly created owned page per gate pass",
            "concurrent_shared_profile_tabs_allowed_after_ownership": True,
            "first_source_request_not_before_utc": not_before,
        },
        "checkpoint_contract": {
            "schema_version": CHECKPOINT_SCHEMA,
            "path_free": True,
            "public_normalized_metadata_only": True,
            "write_after_each_completed_detail": True,
            "validate_every_record_before_resume_skip": True,
        },
        "output_contract": {
            "gate_schema": GATE_SCHEMA,
            "gate_marker_schema": GATE_MARKER_SCHEMA,
            "hydrated_union_schema": "academic-search-result/v1",
            "hydrated_union_marker_schema": "oatd_output_commit_marker_v1",
            "gate_artifacts_merge_eligible": False,
            "hydrated_union_merge_eligible": True,
            "full_abstract_field": "results[].abstract",
            "source_publication_type_fields": [
                "results[].documentType",
                "results[].publicationType",
                "results[].sourcePublicationType",
            ],
            "reviewer_publication_type_not_inferred": True,
        },
        "local_matching_plan": {
            "path": relative(LOCAL_PLAN_PATH),
            "sha256": digest(LOCAL_PLAN_PATH),
            "schema_version": local_plan.schema_version,
            "matcher_version": local_plan.matcher_version,
            "plan_sha256": local_plan.plan_sha256,
        },
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
            "files": {
                name: {
                    "path": f"~/agent-tools/{path.relative_to(ADAPTER_ROOT)}",
                    "sha256": digest(path),
                }
                for name, path in ADAPTER_FILES.items()
            },
        },
        "bindings": {"files": source_affecting_bindings()},
        "checkpoint": str(CHECKPOINT_PATH.relative_to(FINAL_ROOT)),
        "union_output": str(UNION_PATH.relative_to(FINAL_ROOT)),
        "events": events,
        "corrective_run": corrective,
    }


def validate_plan(plan: Mapping[str, Any], *, require_empty_outputs: bool) -> tuple[Any, Any, Any]:
    adapter = load_adapter()
    queries = load_queries()
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("output_root") != relative(FINAL_ROOT)
        or plan.get("source_id") != "oatd"
        or plan.get("review_id") != REVIEW_ID
        or plan.get("run_id") != RUN_ID
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
    ):
        raise RuntimeError("The OATD final plan identity is invalid")
    corrective = plan.get("corrective_run")
    policy = plan.get("execution_policy")
    if (
        not isinstance(policy, Mapping)
        or policy.get("initial_complete_card_id_passes_per_gate") != 2
        or policy.get("confirmation_complete_card_id_passes_per_gate") != 1
        or policy.get("fresh_browser") is not False
        or policy.get("browser_profile") != "shared_chrome_automation_cdp_9222"
        or policy.get("existing_shared_tabs_modified") is not False
        or policy.get("shared_target_acquisition_attempts") != 1
        or policy.get("shared_target_acquisition_delay_seconds") != 0.0
        or policy.get("shared_target_retry_scope") != "no automatic local retry"
        or policy.get("gate_page_lifecycle") != "one directly created owned page per gate pass"
        or policy.get("concurrent_shared_profile_tabs_allowed_after_ownership") is not True
    ):
        raise RuntimeError("The OATD final shared-profile execution policy is invalid")
    not_before = policy.get("first_source_request_not_before_utc")
    if FINAL_ROOT == DEFAULT_FINAL_ROOT.resolve(strict=False):
        if corrective is not None or not_before is not None:
            raise RuntimeError("The initial OATD final plan has unexpected corrective provenance")
    else:
        expected_sequence = int(FINAL_ROOT.name.rsplit("-", 1)[1])
        if not isinstance(corrective, Mapping) or corrective.get("sequence") != expected_sequence or not isinstance(not_before, str):
            raise RuntimeError("The corrective OATD final plan lacks its bounded provenance")
        try:
            parse_utc(not_before)
        except Exception as error:
            raise RuntimeError("The corrective OATD final cooldown timestamp is invalid") from error
        for field in (
            "superseded_plan",
            "superseded_plan_sha256",
            "superseded_failure_receipt",
            "superseded_failure_receipt_sha256",
        ):
            if not isinstance(corrective.get(field), str) or not corrective[field]:
                raise RuntimeError("The corrective OATD final plan lacks a supersession binding")
        for path_field, digest_field in (
            ("superseded_plan", "superseded_plan_sha256"),
            ("superseded_failure_receipt", "superseded_failure_receipt_sha256"),
        ):
            path = REPOSITORY_ROOT / corrective[path_field]
            if not path.is_file() or digest(path) != corrective[digest_field]:
                raise RuntimeError("The corrective OATD final supersession evidence changed")
    cutoff = plan.get("cutoff")
    if not isinstance(cutoff, Mapping) or cutoff.get("exact_common_cutoff") != CUTOFF_DATE or cutoff.get(
        "source_year_start"
    ) != YEAR_START or cutoff.get("source_year_upper_bound") != YEAR_END:
        raise RuntimeError("The OATD final cutoff is invalid")
    candidate_route = plan.get("candidate_route")
    if not isinstance(candidate_route, Mapping) or candidate_route.get("identity") != queries.ALGEBRAIC_IDENTITY:
        raise RuntimeError("The OATD final candidate route is invalid")
    events = plan.get("events")
    if not isinstance(events, list) or [event.get("event_id") for event in events] != list(queries.GATE_IDS):
        raise RuntimeError("The OATD final gate schedule is invalid")
    for event in events:
        event_id = event["event_id"]
        query = queries.GATE_QUERIES[event_id]
        configuration = build_configuration(adapter,
            query,
            language="English",
            year_start=YEAR_START,
            year_end=YEAR_END,
            page_size=PAGE_SIZE,
        )
        output = FINAL_ROOT / str(event.get("output", ""))
        screenshots = adapter.screenshot_paths_for_output(output)
        expected_screenshots = {
            "search_page": str(screenshots.search_page.relative_to(FINAL_ROOT)),
            "results_page": str(screenshots.results_page.relative_to(FINAL_ROOT)),
        }
        if (
            event.get("query") != query
            or event.get("query_sha256") != text_digest(query)
            or event.get("query_characters") != len(query)
            or event.get("effective_query") != configuration.effective_query
            or event.get("effective_query_sha256") != text_digest(configuration.effective_query)
            or event.get("language") != "English"
            or event.get("language_source_value") != "(en OR eng OR english)"
            or event.get("year_start") != YEAR_START
            or event.get("year_end") != YEAR_END
            or event.get("page_size") != PAGE_SIZE
            or event.get("limit") != CARD_LIMIT
            or event.get("max_pages") != MAX_PAGES
            or event.get("screenshots") != expected_screenshots
            or output.parent != FINAL_ROOT / "gates"
        ):
            raise RuntimeError(f"The OATD final gate changed: {event_id}")
        if require_empty_outputs:
            for path in (output, gate_marker_path(output), screenshots.search_page, screenshots.results_page):
                if not absent(path):
                    raise RuntimeError(f"An OATD final gate output is occupied: {path}")
    expected_bindings = source_affecting_bindings()
    bindings = plan.get("bindings", {})
    if not isinstance(bindings, Mapping) or bindings.get("files") != expected_bindings:
        raise RuntimeError("An OATD final source-affecting file changed")
    adapter_binding = plan.get("adapter")
    if not isinstance(adapter_binding, Mapping) or adapter_binding.get("id") != adapter.ADAPTER_ID or adapter_binding.get(
        "version"
    ) != adapter.ADAPTER_VERSION:
        raise RuntimeError("The OATD final adapter identity changed")
    adapter_files = adapter_binding.get("files")
    if not isinstance(adapter_files, Mapping):
        raise RuntimeError("The OATD final adapter bindings are missing")
    for name, path in ADAPTER_FILES.items():
        descriptor = adapter_files.get(name)
        if not isinstance(descriptor, Mapping) or descriptor.get("sha256") != digest(path):
            raise RuntimeError(f"The OATD final adapter file changed: {name}")
    continuation = plan.get("continuation")
    if FINAL_ROOT.name in {"corrective-010", "corrective-011", "corrective-012", "corrective-013"}:
        files = continuation.get("source_pass_files") if isinstance(continuation, Mapping) else None
        if not isinstance(files, Mapping) or len(files) != 32:
            raise RuntimeError("The continuation lacks its 16 initial passes and 16 screenshots")
        expected_prefix = relative(DEFAULT_FINAL_ROOT / "corrective-009/progress") + "/"
        for name, expected_digest in files.items():
            path = REPOSITORY_ROOT / name
            if not name.startswith(expected_prefix) or not path.is_file() or digest(path) != expected_digest:
                raise RuntimeError("A retained initial final pass changed")
        retained = continuation.get("retained_checkpoint")
        if retained is not None:
            for path_key, hash_key in (("path", "sha256"), ("plan_path", "plan_sha256")):
                retained_path = REPOSITORY_ROOT / retained[path_key]
                if not retained_path.is_file() or digest(retained_path) != retained[hash_key]:
                    raise RuntimeError("A retained final detail checkpoint binding changed")
    local_descriptor = plan.get("local_matching_plan")
    if not isinstance(local_descriptor, Mapping) or local_descriptor.get("sha256") != digest(LOCAL_PLAN_PATH):
        raise RuntimeError("The OATD local matching plan changed")
    local_plan = adapter.load_local_matching_plan(LOCAL_PLAN_PATH)
    if local_descriptor.get("plan_sha256") != local_plan.plan_sha256:
        raise RuntimeError("The OATD local matching plan semantics changed")
    checkpoint = FINAL_ROOT / str(plan.get("checkpoint", ""))
    union = FINAL_ROOT / str(plan.get("union_output", ""))
    if checkpoint != CHECKPOINT_PATH or union != UNION_PATH:
        raise RuntimeError("The OATD final output locations changed")
    if require_empty_outputs and (not absent(union) or not absent(adapter.oatd_output_commit_marker_path(union))):
        raise RuntimeError("The OATD final hydrated union output is occupied")
    return adapter, queries, local_plan


def snapshot_payload(adapter: Any, snapshot: Any) -> dict[str, Any]:
    return {
        "source_reported_total": snapshot.total,
        "pages_retrieved": snapshot.pages_retrieved,
        "source_card_rows_seen": snapshot.source_card_rows_seen,
        "page_size": snapshot.page_size,
        "ordered_record_ids_sha256": adapter._ordered_record_ids_sha256(snapshot.ordered_record_ids),
        "stable_record_ids_sha256": adapter._stable_record_ids_sha256(snapshot.ordered_record_ids),
        "cards": [
            {"rank": card.rank, "paperId": card.record_id, "title": card.title}
            for card in snapshot.cards
        ],
        "complete": True,
    }


async def save_failed_page(adapter: Any, page: Any, stage: str, error: Exception) -> None:
    root = FINAL_ROOT / "failures" / f"{stage}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    root.mkdir(parents=True, exist_ok=False)
    state = await page.evaluate("""() => ({title: document.title, path: location.pathname,
        status: performance.getEntriesByType('navigation').at(-1)?.responseStatus ?? null})""")
    await page.evaluate(adapter.OATD_SCREENSHOT_REDACTION_SCRIPT)
    png = await page.screenshot(full_page=True, mask=[page.locator('[data-oatd-screenshot-redact]')])
    write_exclusive_bytes(root / "page.png", png)
    write_exclusive_json(root / "evidence.json", {
        "merge_eligible": False, "captured_at_utc": now(), "stage": stage,
        "state": state, "error_type": type(error).__name__,
        "screenshot": {"file": "page.png", "sha256": bytes_digest(png), "bytes": len(png)},
    })


async def capture_snapshot(adapter: Any, page: Any, event: Mapping[str, Any], *,
                           output: Path | None = None, persist_progress: bool = False) -> tuple[Any, Any, dict[str, Any], int]:
    try:
        snapshot, configuration, payloads, retries = await _capture_snapshot(adapter, page, event, output=output)
    except Exception as error:
        if persist_progress:
            try:
                await save_failed_page(adapter, page, event["event_id"], error)
            except Exception:
                pass  # Preserve the original error if evidence capture also fails.
        raise
    if persist_progress:
        parent = FINAL_ROOT / "progress" / event["event_id"]
        number = len(list(parent.glob("pass-*"))) + 1
        root = parent / f"pass-{number:02d}"
        root.mkdir(parents=True, exist_ok=False)
        for payload in payloads.values():
            write_exclusive_bytes(root / payload.evidence["file_name"], payload.data)
        write_exclusive_json(root / "snapshot.json", {
            "merge_eligible": False, "captured_at_utc": now(), "event_id": event["event_id"],
            "pass_number": number, "requested_query": event["query"],
            "executed_query": configuration.effective_query,
            "snapshot": snapshot_payload(adapter, snapshot),
            "screenshots": {key: dict(value.evidence) for key, value in payloads.items()},
        })
    return snapshot, configuration, payloads, retries


async def _capture_snapshot(
    adapter: Any,
    page: Any,
    event: Mapping[str, Any],
    *,
    output: Path | None = None,
) -> tuple[Any, Any, dict[str, Any], int]:
    configuration = build_configuration(adapter,
        event["query"],
        language=event["language"],
        year_start=event["year_start"],
        year_end=event["year_end"],
        page_size=event["page_size"],
    )
    if configuration.effective_query != event["effective_query"]:
        raise RuntimeError("The OATD final effective query changed before browser work")
    budget = adapter.OATDBusyRetryBudget(
        max_retries=event["busy_retries"],
        initial_delay_seconds=event["busy_retry_delay_seconds"],
    )
    screenshot_paths = adapter.screenshot_paths_for_output(output) if output is not None else None
    snapshot, payloads = await source_native.collect(
        adapter, page, configuration=configuration, limit=event["limit"],
        max_pages=event["max_pages"], timeout_seconds=event["timeout_seconds"],
        page_delay_seconds=event["page_delay_seconds"], budget=budget,
        screenshot_paths=screenshot_paths,
    )
    return snapshot, configuration, payloads, budget.performed_retries


def target_union(snapshots: Mapping[str, Any], events: list[Mapping[str, Any]], adapter: Any) -> tuple[list[str], dict[str, Any], dict[str, list[dict[str, Any]]]]:
    target_ids: list[str] = []
    cards_by_id: dict[str, Any] = {}
    membership: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        event_id = event["event_id"]
        snapshot = snapshots[event_id]
        for card in snapshot.cards:
            if card.record_id not in cards_by_id:
                target_ids.append(card.record_id)
                cards_by_id[card.record_id] = card
                membership[card.record_id] = []
            membership[card.record_id].append(
                {
                    "gate_id": event_id,
                    "initial_rank": card.rank,
                    "initial_card_title": card.title,
                }
            )
    if len(target_ids) != len(set(target_ids)):
        raise RuntimeError("The OATD final initial union repeated a stable ID")
    if not target_ids:
        return target_ids, cards_by_id, membership
    if adapter._stable_record_ids_sha256(target_ids) != adapter._stable_record_ids_sha256(
        list(cards_by_id)
    ):
        raise RuntimeError("The OATD final initial union ledger is inconsistent")
    return target_ids, cards_by_id, membership


def confirmation_membership(
    confirmations: Mapping[str, Any], events: list[Mapping[str, Any]], membership: dict[str, list[dict[str, Any]]]
) -> None:
    for event in events:
        event_id = event["event_id"]
        ranks = {
            card.record_id: {"confirmation_rank": card.rank, "confirmation_card_title": card.title}
            for card in confirmations[event_id].cards
        }
        for record_id, gate_rows in membership.items():
            for gate in gate_rows:
                if gate["gate_id"] == event_id:
                    if record_id not in ranks:
                        raise RuntimeError("The OATD confirmation lost a gate member")
                    gate.update(ranks[record_id])


def new_checkpoint(plan_sha256: str, target_ids: list[str], adapter: Any) -> dict[str, Any]:
    return {
        "schema_version": CHECKPOINT_SCHEMA,
        "adapter": {"adapter_id": adapter.ADAPTER_ID, "adapter_version": adapter.ADAPTER_VERSION},
        "plan_sha256": plan_sha256,
        "source_union": {
            "record_count": len(target_ids),
            "stable_record_ids_sha256": adapter._stable_record_ids_sha256(target_ids),
            "ordered_record_ids_sha256": adapter._ordered_record_ids_sha256(target_ids),
        },
        "stable_ids": list(target_ids),
        "completed_ids": [],
        "records": [],
    }


def validate_checkpoint(
    adapter: Any,
    value: Mapping[str, Any],
    *,
    plan_sha256: str,
    fresh_target_ids: list[str],
    configuration: Any,
    local_plan: Any,
) -> tuple[list[str], dict[str, dict[str, Any]], list[str]]:
    required = {
        "schema_version",
        "adapter",
        "plan_sha256",
        "source_union",
        "stable_ids",
        "completed_ids",
        "records",
    }
    if set(value) != required or value.get("schema_version") != CHECKPOINT_SCHEMA or value.get("adapter") != {
        "adapter_id": adapter.ADAPTER_ID,
        "adapter_version": adapter.ADAPTER_VERSION,
    } or value.get("plan_sha256") != plan_sha256:
        raise RuntimeError("The OATD final checkpoint binding is invalid")
    target_ids = value.get("stable_ids")
    if not isinstance(target_ids, list) or any(not isinstance(value, str) for value in target_ids) or len(target_ids) != len(set(target_ids)):
        raise RuntimeError("The OATD final checkpoint target ledger is invalid")
    if set(target_ids) != set(fresh_target_ids):
        raise RuntimeError("The OATD stable union changed since checkpoint creation")
    expected_union = {
        "record_count": len(target_ids),
        "stable_record_ids_sha256": adapter._stable_record_ids_sha256(target_ids),
        "ordered_record_ids_sha256": adapter._ordered_record_ids_sha256(target_ids),
    }
    if value.get("source_union") != expected_union:
        raise RuntimeError("The OATD final checkpoint union hash is invalid")
    completed = value.get("completed_ids")
    records = value.get("records")
    if not isinstance(completed, list) or not isinstance(records, list) or len(completed) != len(records) or completed != target_ids[: len(completed)]:
        raise RuntimeError("The OATD final checkpoint completion order is invalid")
    records_by_id: dict[str, dict[str, Any]] = {}
    for record_id, record in zip(completed, records, strict=True):
        if not isinstance(record_id, str) or not isinstance(record, Mapping):
            raise RuntimeError("The OATD final checkpoint record is invalid")
        validated = validate_record(adapter, record, configuration=configuration, local_plan=local_plan)
        if validated["paperId"] != record_id:
            raise RuntimeError("The OATD final checkpoint record IDs disagree")
        records_by_id[record_id] = validated
    if adapter._checkpoint_has_unsafe_content(value):
        raise RuntimeError("The OATD final checkpoint retained unsafe context")
    return list(completed), records_by_id, list(target_ids)


def checkpoint_with_records(
    checkpoint: Mapping[str, Any], target_ids: list[str], records_by_id: Mapping[str, dict[str, Any]]
) -> dict[str, Any]:
    completed = [record_id for record_id in target_ids if record_id in records_by_id]
    if completed != target_ids[: len(completed)]:
        raise RuntimeError("OATD final hydration must follow its persisted union order")
    value = deepcopy(checkpoint)
    value["completed_ids"] = completed
    value["records"] = [records_by_id[record_id] for record_id in completed]
    return value


def validate_record(adapter: Any, record: Mapping[str, Any], *, configuration: Any, local_plan: Any) -> dict[str, Any]:
    evidence = record_metadata.validate(record.get("oatdDetail"), record.get("abstract", ""))
    base = {key: value for key, value in record.items() if key != "oatdDetail"}
    validated = adapter._validate_shared_population_checkpoint_record(
        base, configuration=configuration, plan=local_plan)
    validated["oatdDetail"] = deepcopy(evidence)
    return validated


async def hydrate_records(
    adapter: Any,
    detail_page: Any,
    *,
    target_ids: list[str],
    cards_by_id: Mapping[str, Any],
    configurations_by_id: Mapping[str, Any],
    records_by_id: dict[str, dict[str, Any]],
    checkpoint: dict[str, Any],
    local_plan: Any,
    policy: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], int]:
    budget = adapter.OATDBusyRetryBudget(
        max_retries=policy["detail_busy_retries"],
        initial_delay_seconds=policy["detail_busy_retry_delay_seconds"],
    )
    requests = 0
    for record_id in target_ids:
        if record_id in records_by_id:
            continue
        record = await adapter.read_shared_population_detail(
            detail_page,
            card=cards_by_id[record_id],
            configuration=configurations_by_id[record_id],
            timeout_seconds=180.0,
            busy_retry_budget=budget,
        )
        evidence = await record_metadata.capture(detail_page, record)
        discipline = evidence["fields"]["discipline"]
        if discipline:
            record["departmentDiscipline"] = discipline[0]["value"]
            record["detailFieldStates"]["discipline"] = "present"
        annotation, _counts = adapter.annotate_local_matching_plan(record, local_plan)
        record["localMatching"] = annotation
        record["oatdDetail"] = evidence
        record = validate_record(adapter, record,
                                 configuration=configurations_by_id[record_id], local_plan=local_plan)
        records_by_id[record_id] = record
        requests += 1
        checkpoint = checkpoint_with_records(checkpoint, target_ids, records_by_id)
        if adapter._checkpoint_has_unsafe_content(checkpoint):
            raise RuntimeError("The OATD final checkpoint became unsafe")
        write_atomic_json(CHECKPOINT_PATH, checkpoint)
        print(
            json.dumps(
                {
                    "stage": "detail_hydration",
                    "completed_records": len(records_by_id),
                    "target_records": len(target_ids),
                }
            ),
            flush=True,
        )
        remaining = len(target_ids) - len(records_by_id)
        if remaining:
            if requests % policy["detail_batch_size"] == 0:
                await asyncio.sleep(policy["detail_batch_cooldown_seconds"])
            else:
                await asyncio.sleep(policy["detail_delay_seconds"])
    return records_by_id, checkpoint, budget.performed_retries


def source_publication_type(record: Mapping[str, Any]) -> str:
    value = record.get("documentType")
    if value != "Thesis or dissertation":
        raise RuntimeError("A final OATD record lacked the source ETD publication type")
    return value


def materialize_record(
    record: Mapping[str, Any],
    *,
    rank: int,
    memberships: list[dict[str, Any]] | None = None,
    gate_rank: int | None = None,
) -> dict[str, Any]:
    value = deepcopy(dict(record))
    publication_type = source_publication_type(value)
    value["rank"] = rank
    value["publicationType"] = publication_type
    value["sourcePublicationType"] = publication_type
    value["sourcePublicationTypeCode"] = "thesis_or_dissertation"
    value["sourcePublicationTypeBasis"] = "OATD ETD index scope"
    evidence = record_metadata.validate(value.get("oatdDetail"), value.get("abstract", ""))
    for output_field, source_field in (("sourceDegree", "degree"), ("sourceDegreeLevel", "degree_level"),
                                       ("sourceLanguage", "language"), ("sourceIssuedDate", "issued_date")):
        fields = evidence["fields"][source_field]
        value[output_field] = fields[0]["value"] if fields else None
    if memberships is not None:
        value["unionRank"] = rank
        value["gateProvenance"] = deepcopy(memberships)
    if gate_rank is not None:
        value["gateRank"] = gate_rank
    if value.get("abstract_not_available") is not (not bool(value.get("abstract"))):
        raise RuntimeError("A final OATD record has inconsistent abstract availability")
    return value


def abstract_summary(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    unavailable = [record["paperId"] for record in records if not record.get("abstract")]
    truncated = [record["paperId"] for record in records
                 if record_metadata.abstract_state(record.get("abstract", "")) == "truncated_in_oatd"]
    return {
        "required": True,
        "capture_method": "entire rendered Record Details Abstract cell with paragraph boundaries preserved",
        "snippet_substitution": False,
        "records_with_full_source_abstract": len(records) - len(unavailable) - len(truncated),
        "records_explicitly_without_source_abstract": len(unavailable),
        "records_with_source_truncated_abstract": len(truncated),
        "source_abstract_unavailable_record_ids": unavailable,
        "source_truncated_abstract_record_ids": truncated,
        "all_available_source_abstract_text_preserved": True,
        "all_records_have_full_abstracts": not unavailable and not truncated,
        "repository_metadata_enrichment_needed": bool(unavailable or truncated),
    }


def publication_type_summary(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    values = {record.get("documentType") for record in records}
    if values not in (set(), {"Thesis or dissertation"}):
        raise RuntimeError("OATD final source publication types are incomplete")
    return {
        "record_fields": ["documentType", "publicationType", "sourcePublicationType"],
        "source_value_counts": {"Thesis or dissertation": len(records)},
        "source_scope": "OATD ETD index",
        "reviewer_publication_type_not_inferred": True,
    }


def screenshot_receipt(adapter: Any, output: Path, payloads: Mapping[str, Any]) -> dict[str, Any]:
    paths = adapter.screenshot_paths_for_output(output)
    search = adapter._validate_oatd_screenshot_payload(
        payloads.get("search_page"), paths.search_page, page_kind="configured_search_page"
    )
    results = adapter._validate_oatd_screenshot_payload(
        payloads.get("results_page"), paths.results_page, page_kind="verified_first_results_page"
    )
    return {
        "schema_version": "slr1-oatd-final-gate-screenshots/v1",
        "search_page": dict(search.evidence),
        "results_page": dict(results.evidence),
    }


def build_gate_artifact(
    adapter: Any,
    event: Mapping[str, Any],
    initial: Any,
    second_initial: Any,
    confirmation: Any,
    payloads: Mapping[str, Any],
    records_by_id: Mapping[str, Mapping[str, Any]],
    membership: Mapping[str, list[dict[str, Any]]],
    *,
    initial_retries: int,
    confirmation_retries: int,
) -> dict[str, Any]:
    output = FINAL_ROOT / event["output"]
    gate_records: list[dict[str, Any]] = []
    for card in initial.cards:
        gate_records.append(
            materialize_record(
                records_by_id[card.record_id],
                rank=card.rank,
                memberships=None,
                gate_rank=card.rank,
            )
        )
        gate_records[-1]["gateProvenance"] = deepcopy(membership[card.record_id])
    transaction_id = secrets.token_hex(32)
    return {
        "schema_version": GATE_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "source_endpoint": "https://oatd.org/oatd/search",
        "run_id": RUN_ID,
        "review_id": REVIEW_ID,
        "protocol_commit": load_queries().PROTOCOL_COMMIT,
        "merge_eligible": False,
        "requested_query": event["query"],
        "executed_query": event["effective_query"],
        "controls": {
            "language": "English",
            "language_source_value": "(en OR eng OR english)",
            "year_start": YEAR_START,
            "year_end": YEAR_END,
            "exact_common_cutoff_for_screening": CUTOFF_DATE,
            "page_size": PAGE_SIZE,
            "sort": "source_rendered_relevance_not_oldest_first",
            "publication_type_filter": None,
        },
        "source_total": initial.total,
        "initial_pass": snapshot_payload(adapter, initial),
        "second_initial_pass": snapshot_payload(adapter, second_initial),
        "confirmation_pass": snapshot_payload(adapter, confirmation),
        "stable_record_id_sets_reconciled": True,
        "native_order_drift_observed": initial.ordered_record_ids != confirmation.ordered_record_ids,
        "record_details_requested_by_gate_passes": False,
        "busy_retries_performed": initial_retries + confirmation_retries,
        "record_details": gate_records,
        "full_abstract_capture": abstract_summary(gate_records),
        "source_publication_type_capture": publication_type_summary(gate_records),
        "screenshots": screenshot_receipt(adapter, output, payloads),
        "publication": {
            "schema_version": GATE_MARKER_SCHEMA,
            "state": "terminal_marker_required",
            "transaction_id": transaction_id,
            "marker_path_persisted": False,
        },
    }


def publish_gate(adapter: Any, output: Path, artifact: Mapping[str, Any], payloads: Mapping[str, Any]) -> None:
    paths = adapter.screenshot_paths_for_output(output)
    artifact_bytes = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    marker = {
        "schema_version": GATE_MARKER_SCHEMA,
        "transaction_id": artifact["publication"]["transaction_id"],
        "files": {
            "json": {"file_name": output.name, "sha256": bytes_digest(artifact_bytes), "bytes": len(artifact_bytes)},
            "search_page": {
                "file_name": paths.search_page.name,
                "sha256": bytes_digest(payloads["search_page"].data),
                "bytes": len(payloads["search_page"].data),
            },
            "results_page": {
                "file_name": paths.results_page.name,
                "sha256": bytes_digest(payloads["results_page"].data),
                "bytes": len(payloads["results_page"].data),
            },
        },
        "paths_persisted": False,
    }
    write_exclusive_bytes(paths.search_page, payloads["search_page"].data)
    write_exclusive_bytes(paths.results_page, payloads["results_page"].data)
    write_exclusive_bytes(output, artifact_bytes)
    write_exclusive_json(gate_marker_path(output), marker)
    fsync_parent(output)
    validate_gate(adapter, output)


def validate_bound_files(marker: Mapping[str, Any], paths: Mapping[str, Path], schema: str) -> None:
    if marker.get("schema_version") != schema or marker.get("paths_persisted") is not False:
        raise RuntimeError("An OATD final terminal marker is invalid")
    files = marker.get("files")
    if not isinstance(files, Mapping) or set(files) != set(paths):
        raise RuntimeError("An OATD final terminal marker file set is invalid")
    for key, path in paths.items():
        item = files.get(key)
        if not path.is_file() or not isinstance(item, Mapping) or item.get("file_name") != path.name or item.get(
            "sha256"
        ) != digest(path) or item.get("bytes") != path.stat().st_size:
            raise RuntimeError("An OATD final terminal marker digest is invalid")


def validate_gate(adapter: Any, output: Path) -> dict[str, Any]:
    artifact = load(output)
    marker = load(gate_marker_path(output))
    paths = {"json": output, **adapter.screenshot_paths_for_output(output).__dict__}
    validate_bound_files(marker, paths, GATE_MARKER_SCHEMA)
    if artifact.get("schema_version") != GATE_SCHEMA or artifact.get("merge_eligible") is not False:
        raise RuntimeError("An OATD final gate artifact has the wrong schema")
    if marker.get("transaction_id") != artifact.get("publication", {}).get("transaction_id"):
        raise RuntimeError("An OATD final gate transaction is not bound")
    initial = artifact.get("initial_pass")
    confirmation = artifact.get("confirmation_pass")
    if not isinstance(initial, Mapping) or not isinstance(confirmation, Mapping):
        raise RuntimeError("An OATD final gate lacks complete passes")
    initial_ids = [card.get("paperId") for card in initial.get("cards", [])]
    confirmation_ids = [card.get("paperId") for card in confirmation.get("cards", [])]
    total = artifact.get("source_total")
    if not isinstance(total, int) or isinstance(total, bool) or len(initial_ids) != total or len(confirmation_ids) != total or len(
        set(initial_ids)
    ) != total or set(initial_ids) != set(confirmation_ids) or initial.get("stable_record_ids_sha256") != confirmation.get(
        "stable_record_ids_sha256"
    ) or artifact.get("stable_record_id_sets_reconciled") is not True:
        raise RuntimeError("An OATD final gate did not reconcile")
    second_initial = artifact.get("second_initial_pass")
    for observation in (initial, second_initial, confirmation):
        if not isinstance(observation, Mapping):
            raise RuntimeError("An OATD final gate lacks all three required passes")
        ids = [card.get("paperId") for card in observation.get("cards", [])]
        if (len(ids) != total or len(set(ids)) != total or set(ids) != set(initial_ids)
                or observation.get("source_reported_total") != total
                or observation.get("complete") is not True
                or observation.get("stable_record_ids_sha256") != adapter._stable_record_ids_sha256(ids)):
            raise RuntimeError("An OATD final gate failed its three-pass reconciliation")
    details = artifact.get("record_details")
    if not isinstance(details, list) or [record.get("paperId") for record in details] != initial_ids:
        raise RuntimeError("An OATD final gate lacks hydrated detail records")
    if any(
        record.get("documentType") != "Thesis or dissertation"
        or record.get("publicationType") != "Thesis or dissertation"
        or record.get("sourcePublicationType") != "Thesis or dissertation"
        or record.get("abstract_not_available") is not (not bool(record.get("abstract")))
        for record in details
    ):
        raise RuntimeError("An OATD final gate lost an abstract or publication type")
    for record in details:
        record_metadata.validate(record.get("oatdDetail"), record.get("abstract", ""))
    screenshots = artifact.get("screenshots")
    if not isinstance(screenshots, Mapping):
        raise RuntimeError("An OATD final gate lacks screenshots")
    for key, path in adapter.screenshot_paths_for_output(output).__dict__.items():
        receipt = screenshots.get(key)
        if not isinstance(receipt, Mapping) or receipt.get("file_name") != path.name or receipt.get("sha256") != digest(path) or receipt.get(
            "full_page"
        ) is not True or receipt.get("complete_page_url_retained") is not False or receipt.get(
            "session_identifiers_retained"
        ) is not False:
            raise RuntimeError("An OATD final gate screenshot is invalid")
    return artifact


def union_query_identity(queries: Any) -> str:
    return " OR ".join(f"{event_id}: {queries.GATE_QUERIES[event_id]}" for event_id in queries.GATE_IDS)


def compact_prisma_receipt(adapter: Any, queries: Any, record_count: int, gate_occurrences: int, completed_at: str) -> dict[str, Any]:
    descriptor = adapter._output._prisma_search_run.source_descriptor_for("oatd")
    query = union_query_identity(queries)
    return {
        "schema_version": "academic-search-prisma-search-run/v2",
        "run_id": RUN_ID,
        "run_id_provenance": "explicitly_supplied",
        "review_id": REVIEW_ID,
        "strategy_reference": STRATEGY_REFERENCE,
        "strategy_version": repository_head(),
        "phase": "identification",
        "coverage": {
            "coverage_scope": "full_source",
            "is_full_source_coverage": True,
            "partition_id": None,
            "partition_label": None,
            "partition_description": "Complete OATD final direct-query schedule, materialized as its exact eight-gate stable-ID union",
        },
        "source_descriptor": descriptor,
        "adapter": {
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": digest(ADAPTER_PATH),
            "script_hash_provenance": "sha256_regular_file",
        },
        "strategy": {
            "executed_query": query,
            "query_fields": ["raw basic q", "language", "pub_dt"],
            "search_scope": {"label": "Full OATD index"},
            "query_syntax": {
                "nativequeryeditor": "OATD rendered basic search",
                "querysyntax": "OATD source-native raw query grammar",
                "searchmode": "normal_rendered_eight_gate_union",
            },
            "limits": {
                "year_interval": {
                    "state": "applied",
                    "value": {"start": YEAR_START, "end": YEAR_END, "inclusive": True},
                    "provenance": "source_echo",
                },
                "language": {
                    "state": "applied",
                    "value": "English (en OR eng OR english)",
                    "provenance": "source_echo",
                },
                "publication_type": {"state": "not_applied", "provenance": "source_echo"},
                "country": {"state": "not_applied", "provenance": "source_echo"},
            },
            "sort": {
                "state": "applied",
                "value": {"label": "OATD source-rendered Relevance order"},
                "provenance": "source_echo",
            },
            "requested_query": queries.ALGEBRAIC_IDENTITY,
            "executed_query_provenance": "source_observed_per_gate",
        },
        "completed_at_utc": completed_at,
        "staged_counts": {
            "source_reported_total": record_count,
            "source_reported_total_status": "reported",
            "source_reported_total_exact": True,
            "source_reported_total_scope": "exact deduplicated stable-ID union computed from all complete source-reported OATD gate totals",
            "source_universe_total": None,
            "source_export_total": None,
            "local_match_count": None,
            "matched_total": None,
            "raw_source_records": gate_occurrences,
            "client_side_exclusions": 0,
            "within_source_duplicates_removed": gate_occurrences - record_count,
            "malformed_records_dropped": 0,
            "records_exported": record_count,
        },
        "completion_status": "complete",
        "report_ready": True,
        "report_readiness_reasons": [],
    }


def build_union_result(
    adapter: Any,
    queries: Any,
    plan: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    membership: Mapping[str, list[dict[str, Any]]],
    gate_artifacts: Mapping[str, Mapping[str, Any]],
    *,
    completed_at: str,
    detail_requests_this_attempt: int,
    detail_busy_retries: int,
) -> dict[str, Any]:
    target_ids = checkpoint["stable_ids"]
    records_by_id = {record["paperId"]: record for record in checkpoint["records"]}
    if set(records_by_id) != set(target_ids):
        raise RuntimeError("The OATD final checkpoint is incomplete")
    results = [
        materialize_record(records_by_id[record_id], rank=index, memberships=membership[record_id])
        for index, record_id in enumerate(target_ids, start=1)
    ]
    gate_occurrences = sum(artifact["source_total"] for artifact in gate_artifacts.values())
    stable_hash = adapter._stable_record_ids_sha256(target_ids)
    ordered_hash = adapter._ordered_record_ids_sha256(target_ids)
    receipt = compact_prisma_receipt(adapter, queries, len(results), gate_occurrences, completed_at)
    receipt_errors = adapter._output._prisma_search_run.prisma_search_run_validation_errors(
        receipt, require_report_ready=True
    )
    if receipt_errors:
        raise RuntimeError("The OATD final compact PRISMA receipt is invalid: " + ", ".join(receipt_errors))
    query = union_query_identity(queries)
    result = {
        "query": query,
        "total": len(results),
        "pages_retrieved": sum(
            artifact["initial_pass"]["pages_retrieved"] for artifact in gate_artifacts.values()
        ),
        "results": results,
        "candidate_route": deepcopy(plan["candidate_route"]),
        "gate_evidence": {
            event_id: {
                "artifact": f"gates/{event_id}.json",
                "source_total": artifact["source_total"],
                "initial_stable_record_ids_sha256": artifact["initial_pass"]["stable_record_ids_sha256"],
                "second_initial_stable_record_ids_sha256": artifact["second_initial_pass"]["stable_record_ids_sha256"],
                "confirmation_stable_record_ids_sha256": artifact["confirmation_pass"]["stable_record_ids_sha256"],
            }
            for event_id, artifact in gate_artifacts.items()
        },
        "gate_occurrence_total": gate_occurrences,
        "exact_deduplicated_union_total": len(results),
        "stable_union_ids_sha256": stable_hash,
        "ordered_union_ids_sha256": ordered_hash,
        "hydration": {
            "unique_detail_records_hydrated": len(results),
            "one_record_per_stable_union_id": True,
            "detail_requests_this_attempt": detail_requests_this_attempt,
            "detail_busy_retries_performed": detail_busy_retries,
            "checkpoint_schema": CHECKPOINT_SCHEMA,
            "checkpoint_path_persisted": False,
            "checkpoint_sha256_before_publication": digest(CHECKPOINT_PATH),
        },
        "confirmation": {
            "all_eight_gate_sets_reconciled": True,
            "complete_gate_count": len(gate_artifacts),
            "complete_source_pass_count": len(gate_artifacts) * 3,
            "record_details_requested_by_gate_passes": False,
        },
        "cutoff_screening": {
            "exact_common_cutoff": CUTOFF_DATE,
            "source_year_bounds": [YEAR_START, YEAR_END],
            "records_in_cutoff_year_requiring_exact_date_screening": [
                record["paperId"] for record in results if record.get("year") == YEAR_END
            ],
        },
        "full_abstract_capture": abstract_summary(results),
        "source_publication_type_capture": publication_type_summary(results),
        "output_metadata": {
            "source": "Open Access Theses and Dissertations (OATD)",
            "source_endpoint": "https://oatd.org/oatd/search",
            "status": "success",
            "count_only": False,
            "retrieval_complete": True,
            "merge_eligible": True,
            "search_mode": "normal_rendered_eight_gate_union_hydrate_once",
            "query_syntax": "OATD source-native raw query grammar per gate",
            "executed_query": query,
            "observed_exact_query_echo": True,
            "full_abstract_capture": abstract_summary(results),
            "source_publication_type_capture": publication_type_summary(results),
            "prisma_search_run": receipt,
        },
    }
    normalized = adapter._output._merge_contract.normalize_search_result(
        result,
        source="Open Access Theses and Dissertations (OATD)",
        executed_query=query,
        merge_eligible=True,
    )
    if not adapter.is_complete_oatd_strict_result(normalized):
        raise RuntimeError("The OATD final hydrated union did not satisfy the strict merge gate")
    return normalized


def publish_union(adapter: Any, result: dict[str, Any]) -> dict[str, Any]:
    plan = adapter.prepare_oatd_output_plan(UNION_PATH, None)
    transaction_id = adapter._prepare_oatd_output_commit(
        result, csv_path=None, marker_path=plan.marker_path
    )
    json_stage = adapter._stage_oatd_json(
        plan.output_path, result, "OATD JSON output", plan.output_directory
    )
    marker = {
        "schema": adapter.OATD_OUTPUT_COMMIT_SCHEMA,
        "transaction_id": transaction_id,
        "lexical_output_binding": adapter.make_lexical_output_binding(
            plan.lexical_output_path,
            secrets.token_bytes(32),
            parent_identity=plan.lexical_output_parent_identity,
            captured_location=plan.lexical_output_location,
        ),
        "normalized_json": {"sha256": json_stage.sha256, "bytes": json_stage.byte_count},
        "normalized_csv": None,
    }
    marker_stage = adapter._stage_oatd_json(
        plan.marker_path, marker, "OATD output commit marker", plan.output_directory
    )
    adapter._publish_staged_oatd_file(json_stage)
    adapter._publish_staged_oatd_file(marker_stage)
    adapter._retire_oatd_staged_outputs([json_stage, marker_stage])
    persisted = adapter._verify_retired_oatd_publication(
        plan.output_path,
        plan.marker_path,
        marker,
        [json_stage, marker_stage],
        plan.output_directory,
    )
    if not adapter.is_complete_oatd_strict_result(persisted) or not adapter.verify_commit_gated_publication(
        UNION_PATH, persisted, artifact_sha256=digest(UNION_PATH)
    ):
        raise RuntimeError("The final OATD hydrated union failed terminal verification")
    return persisted


async def acquire_shared_profile_lease(adapter: Any, playwright: Any, policy: Mapping[str, Any]) -> tuple[Any, int]:
    """Use the same direct owned-page setup as the independent successful UI probe."""
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise RuntimeError("Run OATD through the shared-browser runner")
    cdp_url = adapter.validate_local_cdp_url(os.environ.get("BH_CDP_URL", adapter.DEFAULT_LOCAL_CDP_URL))
    if cdp_url != "http://127.0.0.1:9222":
        raise RuntimeError("The final workflow requires the canonical shared endpoint")
    browser = await playwright.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    page = await context.new_page()
    try:
        identity = await adapter._common._target_id_for_page(page)
        return adapter._common.BrowserLease(browser, context, page, False, identity), 0
    except Exception:
        await page.close()
        raise


async def replace_owned_gate_page(adapter: Any, lease: Any) -> Any:
    """Create one new owned page per gate pass. Leave all unrelated pages alone."""
    outcome = await adapter.close_owned_chrome_page_verified(lease)
    if not outcome.verified:
        raise RuntimeError("The preceding owned OATD gate page did not close")
    lease.page = await lease.context.new_page()
    try:
        lease.owned_target_id = await adapter._common._target_id_for_page(lease.page)
    except Exception:
        await lease.page.close()
        raise
    return lease.page


async def execute_workflow(
    adapter: Any,
    queries: Any,
    plan: Mapping[str, Any],
    local_plan: Any,
    *,
    resume: bool,
) -> dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is unavailable. Run through uv.") from error
    events = [dict(event) for event in plan["events"]]
    policy = plan["execution_policy"]
    plan_sha256 = digest(PLAN_PATH)
    snapshots: dict[str, Any] = {}
    second_initials: dict[str, Any] = {}
    confirmations: dict[str, Any] = {}
    configurations: dict[str, Any] = {}
    screenshot_payloads: dict[str, dict[str, Any]] = {}
    initial_retries: dict[str, int] = {}
    confirmation_retries: dict[str, int] = {}
    detail_busy_retries = 0

    async with async_playwright() as playwright, adapter._LeaseCleanup() as cleanup:
        lease, target_acquisition_retries = await acquire_shared_profile_lease(
            adapter, playwright, policy
        )
        cleanup.lease = lease
        page = lease.page
        for index, event in enumerate(events):
            if index:
                await asyncio.sleep(policy["inter_gate_delay_seconds"])
                page = await replace_owned_gate_page(adapter, lease)
            output = FINAL_ROOT / event["output"]
            snapshot, configuration, payloads, retries = await capture_snapshot(
                adapter, page, event, output=output, persist_progress=True
            )
            snapshots[event["event_id"]] = snapshot
            configurations[event["event_id"]] = configuration
            screenshot_payloads[event["event_id"]] = payloads
            initial_retries[event["event_id"]] = retries
            print(
                json.dumps(
                    {"stage": "initial_gate_snapshot", "event": event["event_id"], "total": snapshot.total}
                ),
                flush=True,
            )

        for event in events:
            await asyncio.sleep(policy["inter_gate_delay_seconds"])
            page = await replace_owned_gate_page(adapter, lease)
            second, _configuration, _payloads, retries = await capture_snapshot(adapter, page, event, persist_progress=True)
            adapter.reconcile_shared_population_snapshots(snapshots[event["event_id"]], second)
            second_initials[event["event_id"]] = second
            initial_retries[event["event_id"]] += retries
            print(json.dumps({"stage": "second_initial_gate_snapshot", "event": event["event_id"],
                              "total": second.total}), flush=True)

        fresh_target_ids, cards_by_id, membership = target_union(snapshots, events, adapter)
        configurations_by_id: dict[str, Any] = {}
        for event in events:
            for card in snapshots[event["event_id"]].cards:
                configurations_by_id.setdefault(card.record_id, configurations[event["event_id"]])
        if set(cards_by_id) != set(fresh_target_ids):
            raise RuntimeError("The OATD final card union is incomplete")

        if CHECKPOINT_PATH.exists():
            if not resume:
                raise RuntimeError("An OATD final checkpoint exists. Re-run with --resume.")
            checkpoint = load(CHECKPOINT_PATH)
        else:
            if resume:
                raise RuntimeError("Cannot resume OATD final hydration without a checkpoint")
            checkpoint = new_checkpoint(plan_sha256, fresh_target_ids, adapter)
        completed, records_by_id, target_ids = validate_checkpoint(
            adapter,
            checkpoint,
            plan_sha256=plan_sha256,
            fresh_target_ids=fresh_target_ids,
            configuration=configurations[events[0]["event_id"]],
            local_plan=local_plan,
        )
        completed_before = len(completed)
        write_atomic_json(CHECKPOINT_PATH, checkpoint)

        if len(records_by_id) < len(target_ids):
            await asyncio.sleep(policy["pre_detail_delay_seconds"])
            detail_page = None
            try:
                detail_page = await lease.context.new_page()
                records_by_id, checkpoint, detail_busy_retries = await hydrate_records(
                    adapter,
                    detail_page,
                    target_ids=target_ids,
                    cards_by_id=cards_by_id,
                    configurations_by_id=configurations_by_id,
                    records_by_id=records_by_id,
                    checkpoint=checkpoint,
                    local_plan=local_plan,
                    policy=policy,
                )
            except Exception as error:
                if detail_page is not None:
                    try:
                        await save_failed_page(adapter, detail_page, "detail-hydration", error)
                    except Exception:
                        pass
                raise
            finally:
                if detail_page is not None:
                    outcome = await adapter.close_owned_chrome_page_only_verified(detail_page)
                    if outcome is None or not outcome.verified:
                        raise RuntimeError("OATD final detail-page cleanup could not be verified")
        completed_after = len(records_by_id)

        await asyncio.sleep(policy["pre_confirmation_delay_seconds"])
        for index, event in enumerate(events):
            if index:
                await asyncio.sleep(policy["inter_gate_delay_seconds"])
            page = await replace_owned_gate_page(adapter, lease)
            confirmation, _configuration, _payloads, retries = await capture_snapshot(adapter, page, event, persist_progress=True)
            adapter.reconcile_shared_population_snapshots(snapshots[event["event_id"]], confirmation)
            confirmations[event["event_id"]] = confirmation
            confirmation_retries[event["event_id"]] = retries
            print(
                json.dumps(
                    {"stage": "confirming_gate_snapshot", "event": event["event_id"], "total": confirmation.total}
                ),
                flush=True,
            )

    confirmation_membership(confirmations, events, membership)
    return {
        "events": events,
        "snapshots": snapshots,
        "second_initials": second_initials,
        "confirmations": confirmations,
        "screenshot_payloads": screenshot_payloads,
        "initial_retries": initial_retries,
        "confirmation_retries": confirmation_retries,
        "checkpoint": checkpoint,
        "membership": membership,
        "records_by_id": records_by_id,
        "completed_before": completed_before,
        "completed_after": completed_after,
        "detail_requests_this_attempt": completed_after - completed_before,
        "detail_busy_retries": detail_busy_retries,
        "shared_target_acquisition_retries": target_acquisition_retries,
    }


def failure_receipt(error: Exception, *, started_at: str, completed_before: int) -> None:
    completed_after = 0
    if CHECKPOINT_PATH.is_file():
        try:
            completed_after = len(load(CHECKPOINT_PATH).get("completed_ids", []))
        except Exception:
            completed_after = -1
    name = f"failure-receipt-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    payload = {
        "schema_version": RUN_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "run_id": RUN_ID,
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "status": "stopped_on_source_or_adapter_failure",
        "success": False,
        "checkpoint_completed_ids_before": completed_before,
        "checkpoint_completed_ids_after": completed_after,
        "error_type": type(error).__name__,
        "error": " ".join(str(error).split())[:1000],
        "hydrated_union_created": UNION_PATH.is_file(),
    }
    write_exclusive_json(FINAL_ROOT / name, payload)


def run(resume: bool) -> int:
    if RECEIPT_PATH.exists() or RECEIPT_PATH.is_symlink():
        raise RuntimeError(f"Refusing to overwrite {RECEIPT_PATH}")
    plan = load(PLAN_PATH)
    adapter, queries, local_plan = validate_plan(plan, require_empty_outputs=True)
    if CHECKPOINT_PATH.exists() and not resume:
        raise RuntimeError("An OATD final checkpoint exists. Re-run with --resume.")
    not_before = plan["execution_policy"].get("first_source_request_not_before_utc")
    if isinstance(not_before, str):
        wait_seconds = max(0.0, (parse_utc(not_before) - datetime.now(timezone.utc)).total_seconds())
        if wait_seconds:
            print(f"Waiting {wait_seconds:.1f} seconds for the OATD corrective cooldown.", flush=True)
            time.sleep(wait_seconds)
    started_at = now()
    completed_before = len(load(CHECKPOINT_PATH).get("completed_ids", [])) if CHECKPOINT_PATH.is_file() else 0
    try:
        workflow = asyncio.run(execute_workflow(adapter, queries, plan, local_plan, resume=resume))
    except Exception as error:
        failure_receipt(error, started_at=started_at, completed_before=completed_before)
        print(json.dumps({"success": False, "error": " ".join(str(error).split())[:1000]}), flush=True)
        return 1

    gate_artifacts: dict[str, dict[str, Any]] = {}
    for event in workflow["events"]:
        event_id = event["event_id"]
        artifact = build_gate_artifact(
            adapter,
            event,
            workflow["snapshots"][event_id],
            workflow["second_initials"][event_id],
            workflow["confirmations"][event_id],
            workflow["screenshot_payloads"][event_id],
            workflow["records_by_id"],
            workflow["membership"],
            initial_retries=workflow["initial_retries"][event_id],
            confirmation_retries=workflow["confirmation_retries"][event_id],
        )
        output = FINAL_ROOT / event["output"]
        publish_gate(adapter, output, artifact, workflow["screenshot_payloads"][event_id])
        gate_artifacts[event_id] = validate_gate(adapter, output)

    completed_at = now()
    union = build_union_result(
        adapter,
        queries,
        plan,
        workflow["checkpoint"],
        workflow["membership"],
        gate_artifacts,
        completed_at=completed_at,
        detail_requests_this_attempt=workflow["detail_requests_this_attempt"],
        detail_busy_retries=workflow["detail_busy_retries"],
    )
    persisted = publish_union(adapter, union)
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "run_id": RUN_ID,
        "review_id": REVIEW_ID,
        "plan": str(PLAN_PATH.relative_to(FINAL_ROOT)),
        "plan_sha256": digest(PLAN_PATH),
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "status": "complete",
        "success": True,
        "checkpoint_completed_ids_before": workflow["completed_before"],
        "checkpoint_completed_ids_after": workflow["completed_after"],
        "detail_requests_this_attempt": workflow["detail_requests_this_attempt"],
        "detail_busy_retries_performed": workflow["detail_busy_retries"],
        "shared_target_acquisition_retries": workflow["shared_target_acquisition_retries"],
        "complete_gate_count": len(gate_artifacts),
        "complete_source_pass_count": len(gate_artifacts) * 3,
        "gate_occurrence_total": sum(artifact["source_total"] for artifact in gate_artifacts.values()),
        "exact_deduplicated_union_total": persisted["total"],
        "gate_artifacts": {
            event_id: {
                "path": f"gates/{event_id}.json",
                "sha256": digest(FINAL_ROOT / f"gates/{event_id}.json"),
                "marker_sha256": digest(gate_marker_path(FINAL_ROOT / f"gates/{event_id}.json")),
            }
            for event_id in gate_artifacts
        },
        "hydrated_union": {
            "path": UNION_PATH.name,
            "sha256": digest(UNION_PATH),
            "marker_sha256": digest(adapter.oatd_output_commit_marker_path(UNION_PATH)),
            "records": persisted["total"],
        },
        "checkpoint": {
            "path_persisted_in_public_artifact": False,
            "sha256": digest(CHECKPOINT_PATH),
            "completed_ids": workflow["completed_after"],
        },
    }
    write_exclusive_json(RECEIPT_PATH, receipt)
    fsync_parent(RECEIPT_PATH)
    print(
        json.dumps(
            {
                "success": True,
                "records": persisted["total"],
                "detail_requests": workflow["detail_requests_this_attempt"],
                "confirmed_gates": len(gate_artifacts),
            }
        ),
        flush=True,
    )
    return 0


def validate() -> dict[str, Any]:
    errors: list[str] = []
    plan = load(PLAN_PATH)
    receipt = load(RECEIPT_PATH)
    adapter, queries, local_plan = validate_plan(plan, require_empty_outputs=False)
    union = load(UNION_PATH)
    if not adapter.is_complete_oatd_strict_result(union):
        errors.append("union_strict_completion")
    if not adapter.verify_commit_gated_publication(UNION_PATH, union, artifact_sha256=digest(UNION_PATH)):
        errors.append("union_terminal_marker")
    receipt_errors = adapter._output._prisma_search_run.prisma_search_run_validation_errors(
        union.get("output_metadata", {}).get("prisma_search_run"), require_report_ready=True
    )
    if receipt_errors:
        errors.append("union_prisma:" + ",".join(receipt_errors))
    results = union.get("results")
    if not isinstance(results, list):
        errors.append("union_results")
        results = []
    result_ids = [record.get("paperId") for record in results]
    if (
        union.get("total") != len(results)
        or union.get("exact_deduplicated_union_total") != len(results)
        or len(set(result_ids)) != len(results)
        or any(record.get("rank") != index for index, record in enumerate(results, start=1))
        or union.get("stable_union_ids_sha256") != adapter._stable_record_ids_sha256(result_ids)
        or union.get("ordered_union_ids_sha256") != adapter._ordered_record_ids_sha256(result_ids)
    ):
        errors.append("union_accounting")
    if any(
        record.get("documentType") != "Thesis or dissertation"
        or record.get("publicationType") != "Thesis or dissertation"
        or record.get("sourcePublicationType") != "Thesis or dissertation"
        or record.get("abstract_not_available") is not (not bool(record.get("abstract")))
        for record in results
    ):
        errors.append("abstract_or_publication_type_capture")

    gate_sets: dict[str, set[str]] = {}
    for event in plan["events"]:
        event_id = event["event_id"]
        output = FINAL_ROOT / event["output"]
        try:
            artifact = validate_gate(adapter, output)
        except Exception as error:
            errors.append(f"gate:{event_id}:{' '.join(str(error).split())[:160]}")
            continue
        if artifact.get("requested_query") != queries.GATE_QUERIES[event_id] or artifact.get("executed_query") != event[
            "effective_query"
        ]:
            errors.append(f"gate_query:{event_id}")
        gate_sets[event_id] = {
            card["paperId"] for card in artifact["initial_pass"]["cards"]
        }
    gate_union = set().union(*gate_sets.values()) if gate_sets else set()
    if set(result_ids) != gate_union or len(gate_sets) != len(queries.GATE_IDS):
        errors.append("gate_union_reconciliation")

    checkpoint = load(CHECKPOINT_PATH)
    first_configuration = build_configuration(adapter,
        queries.GATE_QUERIES[queries.GATE_IDS[0]],
        language="English",
        year_start=YEAR_START,
        year_end=YEAR_END,
        page_size=PAGE_SIZE,
    )
    try:
        _completed, records_by_id, target_ids = validate_checkpoint(
            adapter,
            checkpoint,
            plan_sha256=digest(PLAN_PATH),
            fresh_target_ids=result_ids,
            configuration=first_configuration,
            local_plan=local_plan,
        )
        if target_ids != result_ids or set(records_by_id) != set(result_ids):
            errors.append("checkpoint_records")
    except Exception as error:
        errors.append(f"checkpoint:{' '.join(str(error).split())[:160]}")

    if (
        receipt.get("success") is not True
        or receipt.get("status") != "complete"
        or receipt.get("plan_sha256") != digest(PLAN_PATH)
        or receipt.get("complete_gate_count") != len(queries.GATE_IDS)
        or receipt.get("complete_source_pass_count") != len(queries.GATE_IDS) * 3
        or receipt.get("exact_deduplicated_union_total") != len(results)
    ):
        errors.append("run_receipt")
    cutoff_ids = [record["paperId"] for record in results if record.get("year") == YEAR_END]
    if union.get("cutoff_screening", {}).get("records_in_cutoff_year_requiring_exact_date_screening") != cutoff_ids:
        errors.append("cutoff_screening")
    return {
        "schema_version": VALIDATION_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "run_id": RUN_ID,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "validated_gate_count": len(gate_sets),
        "validated_source_pass_count": len(gate_sets) * 3,
        "retained_initial_source_pass_count": plan.get("continuation", {}).get("retained_complete_initial_passes", 0),
        "new_confirming_source_pass_count": len(gate_sets),
        "validated_normalized_detail_records": len(results),
        "exact_deduplicated_union_total": len(results),
        "records_with_full_source_abstract": abstract_summary(results)["records_with_full_source_abstract"],
        "records_with_source_truncated_abstract": abstract_summary(results)["records_with_source_truncated_abstract"],
        "records_explicitly_without_source_abstract": sum(
            bool(record.get("abstract_not_available")) for record in results
        ),
        "source_publication_type_values": sorted(
            {record.get("documentType") for record in results if record.get("documentType")}
        ),
        "cutoff_year_exact_date_screening_ids": cutoff_ids,
        "merge_eligible_hydrated_union": union.get("output_metadata", {}).get("merge_eligible") is True,
    }


def assessment() -> dict[str, Any]:
    validation = load(VALIDATION_PATH)
    if validation.get("status") != "valid":
        raise RuntimeError("A final OATD assessment requires a valid final artifact")
    union = load(UNION_PATH)
    receipt = load(RECEIPT_PATH)
    results = union["results"]
    return {
        "schema_version": ASSESSMENT_SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "run_id": RUN_ID,
        "status": "passed",
        "plan": {"path": PLAN_PATH.name, "sha256": digest(PLAN_PATH)},
        "run": {"path": RECEIPT_PATH.name, "sha256": digest(RECEIPT_PATH)},
        "hydrated_union": {
            "path": UNION_PATH.name,
            "sha256": digest(UNION_PATH),
            "marker_sha256": digest(load_adapter().oatd_output_commit_marker_path(UNION_PATH)),
        },
        "accounting": {
            "gate_occurrence_total": union["gate_occurrence_total"],
            "exact_deduplicated_union_total": union["exact_deduplicated_union_total"],
            "complete_normalized_detail_records": len(results),
            "unique_detail_requests_this_attempt": receipt["detail_requests_this_attempt"],
            "complete_gate_count": receipt["complete_gate_count"],
            "complete_source_pass_count": receipt["complete_source_pass_count"],
            "busy_retries": receipt["detail_busy_retries_performed"],
        },
        "metadata_capture": {
            "full_abstract_capture": union["full_abstract_capture"],
            "source_publication_type_capture": union["source_publication_type_capture"],
        },
        "cutoff_screening": union["cutoff_screening"],
        "conclusion": {
            "decision": "complete_final_oatd_eight_gate_union",
            "merge_eligible": True,
            "screening_next_step": "Resolve every cutoff-year record against the exact common cutoff during screening.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan", help="Create the final no-clobber event plan")
    run_parser = subparsers.add_parser("run", help="Run the final source workflow")
    validate_parser = subparsers.add_parser("validate", help="Validate completed final artifacts")
    assess_parser = subparsers.add_parser("assess", help="Build the final assessment")
    for command_parser in (plan_parser, run_parser, validate_parser, assess_parser):
        command_parser.add_argument(
            "--root",
            type=Path,
            help="Use one recorded corrective final-searches subdirectory", 
        )
    run_parser.add_argument("--resume", action="store_true", help="Resume a validated checkpoint after a source failure")
    args = parser.parse_args()
    try:
        configure_final_root(args.root)
        if args.command == "plan":
            if PLAN_PATH.exists() or PLAN_PATH.is_symlink():
                raise RuntimeError(f"Refusing to overwrite {PLAN_PATH}")
            plan = build_plan()
            validate_plan(plan, require_empty_outputs=True)
            write_exclusive_json(PLAN_PATH, plan)
            print(json.dumps({"saved": str(PLAN_PATH), "gates": len(plan["events"])}))
            return 0
        if args.command == "run":
            return run(args.resume)
        if args.command == "validate":
            if VALIDATION_PATH.exists() or VALIDATION_PATH.is_symlink():
                raise RuntimeError(f"Refusing to overwrite {VALIDATION_PATH}")
            report = validate()
            write_exclusive_json(VALIDATION_PATH, report)
            print(json.dumps(report))
            return 0 if report["status"] == "valid" else 1
        if args.command == "assess":
            if ASSESSMENT_PATH.exists() or ASSESSMENT_PATH.is_symlink():
                raise RuntimeError(f"Refusing to overwrite {ASSESSMENT_PATH}")
            value = assessment()
            write_exclusive_json(ASSESSMENT_PATH, value)
            print(json.dumps({"saved": str(ASSESSMENT_PATH), "records": value["accounting"]["exact_deduplicated_union_total"]}))
            return 0
    except Exception as error:
        print(" ".join(str(error).split())[:1000], file=sys.stderr)
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
