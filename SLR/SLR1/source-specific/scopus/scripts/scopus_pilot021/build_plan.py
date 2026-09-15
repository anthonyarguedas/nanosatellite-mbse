#!/usr/bin/env python3
"""Build the clean current-literal PSR pilot after pagination repair."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "scopus-current-literal-psr-post-pagination-fix-plan/v1"
PILOT = "021"
PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_ROOT = Path(__file__).resolve().parent
QUERY_SNAPSHOT = SCRIPT_ROOT / "queries.py"
SUPPORTING_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-prior-secondary-reviews.md"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
EVENT_ORDER = ("PSR2", "PSR4", "PSR1", "PSR3")
CANONICAL_PSR_IDS = ("PSR1", "PSR2", "PSR3", "PSR4")
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot021/queries.py"),
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot021/build_plan.py"),
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot021/run_pilot.py"),
)
KNOWN_ITEM = {
    "citation": (
        "Buruso et al. (2026), Model-Based Systems Engineering in Space "
        "Applications: A Comprehensive Literature Review"
    ),
    "doi": "10.1002/sys.70051",
    "stable_id": "SCOPUS-PUBLICATION:105032155734",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def repository_head() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def adapter_version() -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot read the Scopus adapter version")
    return match.group(1)


def load_queries():
    spec = importlib.util.spec_from_file_location(
        "scopus_pilot021_predeclared_queries", QUERY_SNAPSHOT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def event(partition_id: str, query: str) -> dict[str, Any]:
    return {
        "event_id": f"{partition_id}-current-literal-post-pagination-fix",
        "partition_id": partition_id,
        "protocol_commit": PROTOCOL_COMMIT,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output_template": f"events/{partition_id}.attempt-{{attempt:02d}}.json",
        "page_size": 50,
        "limit": 1999,
        "max_pages": 50,
        "require_complete": True,
        "strict_passes": 2,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    queries = load_queries()
    events = [
        event(partition_id, queries.PSR_SCHEDULE[partition_id])
        for partition_id in EVENT_ORDER
    ]
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": "Scopus",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Run one clean strict v2 result for each current literal PSR "
            "partition after repairing final-page Next-control detection. Keep "
            "PSR2 and PSR4 first because Pilot 003 left them incomplete."
        ),
        "historical_context": {
            "pilot_003_incomplete_partitions": ["PSR2", "PSR4"],
            "pilot_014_complete_partitions": ["PSR4", "PSR1"],
            "pilot_014_failed_partitions": ["PSR2", "PSR3"],
            "pilot_015_complete_partitions": ["PSR3"],
            "pilot_015_failed_partitions": ["PSR2", "PSR4", "PSR1"],
            "pilots_016_020_role": "ID-free adapter diagnosis only",
            "historical_source_events_reused": False,
        },
        "adapter_repair": {
            "base_adapter_sha256": "4889373d405b849e9246168363c0a78dc8e253281c1f3935d54a85dd88d97344",
            "failure": (
                "A result-title link containing the word Next was combined with "
                "the disabled final paginator, causing a false enabled-Next state."
            ),
            "repair": (
                "Recognize exact Next semantics, including the paginator's "
                "disabled screen-reader suffix, without matching arbitrary links."
            ),
            "diagnostic_pilot": "020",
            "offline_regression_checks": {
                "targeted": "16 passed",
                "scopus_suite_excluding_unrelated_existing_key_payload_failure": "82 passed, 2 skipped",
            },
        },
        "schedule": {
            "canonical_partition_ids": list(CANONICAL_PSR_IDS),
            "execution_order": list(EVENT_ORDER),
            "literal_only": True,
            "wildcard_comparisons_included": False,
            "proximity_operators_included": False,
            "current_compound_definitions_used_for_psr4": True,
            "term_counts": queries.TERM_COUNTS,
            "query_character_counts": queries.QUERY_CHARACTER_COUNTS,
        },
        "controls": {
            "year_start": None,
            "year_end": 2026,
            "cutoff_day_handling": (
                "Diagnostic source-year bound only. Any 2026 day-level eligibility "
                "remains unresolved."
            ),
            "result_scope": "Documents",
            "language_facets": [],
            "document_type_facets": [],
            "subject_area_controls": [],
            "access_facets": [],
            "peer_review_filter": None,
            "search_within": None,
            "sort": "Date (oldest)",
            "full_abstracts": False,
            "automatic_screenshots_required": True,
            "strict_passes_per_event": 2,
        },
        "strict_contract": {
            "receipt_schema": "academic-search-scopus-strict-two-pass/v2",
            "membership_gate": "equal complete unique stable-ID sets",
            "required_equal_controls": [
                "source total",
                "page count",
                "page size",
                "scope",
                "Date (oldest) control",
            ],
            "order_handling": (
                "Retain both pass-order hashes and the changed-position count. "
                "Order equality is audit evidence, not a membership gate."
            ),
        },
        "known_item": KNOWN_ITEM,
        "acceptance_checks": [
            "Each of PSR1, PSR2, PSR3, and PSR4 completes two exhaustive passes with equal stable-ID sets.",
            "Every event retains an academic-search-scopus-strict-two-pass/v2 receipt.",
            "Every successful JSON has both mandatory sibling screenshots with matching receipts.",
            "No event has a lower year, language, document type, subject, access, peer-review, or search-within restriction.",
            "Buruso et al. remains in the four-partition stable-ID union.",
        ],
        "execution_policy": {
            "maximum_attempts_per_partition": 3,
            "accepted_source_events_per_partition": 1,
            "continue_after_partition_failure": True,
            "fresh_authorized_target_per_attempt": True,
            "close_ephemeral_target_after_attempt": True,
            "target_identifiers_retained": False,
            "retry_only_after_safe_preexecution_failure": True,
            "safe_retry_stages": ["context", "owned_page", "editor_focus"],
            "safe_retry_requires_executed_query_provenance": "not_observed",
            "reason": (
                "Browser context setup can fail before source execution. Never "
                "repeat a delivered or ambiguous source search in this pilot."
            ),
            "infer_from_failure": False,
        },
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "query_snapshot": {
            "path": str(QUERY_SNAPSHOT.relative_to(REPOSITORY_ROOT)),
            "sha256": digest(QUERY_SNAPSHOT),
            "main_query_snapshot_sha256": (
                queries.EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256
            ),
            "supporting_protocol_sha256": digest(SUPPORTING_PROTOCOL),
        },
        "source_affecting_scripts": {
            str(path): digest(REPOSITORY_ROOT / path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = plan.get("events")
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if not isinstance(events, list) or len(events) != 4:
        return [*errors, "event_count"]
    partition_ids = [item.get("partition_id") for item in events]
    if partition_ids != list(EVENT_ORDER):
        errors.append("event_order")
    if set(partition_ids) != set(CANONICAL_PSR_IDS):
        errors.append("partition_coverage")
    controls = plan.get("controls", {})
    if (
        controls.get("year_start") is not None
        or controls.get("year_end") != 2026
        or controls.get("language_facets") != []
        or controls.get("document_type_facets") != []
        or controls.get("subject_area_controls") != []
        or controls.get("access_facets") != []
        or controls.get("peer_review_filter") is not None
        or controls.get("search_within") is not None
    ):
        errors.append("controls")
    for item in events:
        query = item.get("query", "")
        event_id = item.get("event_id")
        if item.get("query_sha256") != digest_text(query):
            errors.append(f"query_hash:{event_id}")
        if any(marker in query.upper() for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR")):
            errors.append(f"prohibited_query_control:{event_id}")
        if "*" in query or "?" in query:
            errors.append(f"nonliteral_query:{event_id}")
        if (
            item.get("strict_passes") != 2
            or item.get("require_complete") is not True
            or item.get("page_size") != 50
            or item.get("output_template")
            != f"events/{item.get('partition_id')}.attempt-{{attempt:02d}}.json"
        ):
            errors.append(f"strict_contract:{event_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = validate(json.loads(args.output.read_text(encoding="utf-8")))
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 1 if errors else 0
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    plan = build()
    errors = validate(plan)
    if errors:
        raise RuntimeError("Invalid plan: " + ", ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
