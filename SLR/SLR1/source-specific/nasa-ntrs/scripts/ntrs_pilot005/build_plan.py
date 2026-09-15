#!/usr/bin/env python3
"""Build the predeclared NASA NTRS Pilot 005 repair-validation plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

SCHEMA = "ntrs-repaired-post-proximity-wildcard-pilot-plan/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ntrs.py"
PILOT004_ROOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/nasa-ntrs/pilots/004"
PILOT004_EVIDENCE = (
    PILOT004_ROOT / "searches/event-plan.json",
    PILOT004_ROOT / "searches/run-receipt.json",
    PILOT004_ROOT / "searches/continuation-plan.json",
    PILOT004_ROOT / "searches/continuation-run-receipt.json",
)
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot005/queries.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot005/build_plan.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot005/run_pilot.py"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def repository_head() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT,
        check=False, capture_output=True, text=True,
    )
    value = completed.stdout.strip()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def adapter_version() -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"), flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot read the NTRS adapter version")
    return match.group(1)


def event(partition: str, variant: str, query: str) -> dict[str, Any]:
    event_id = f"{partition}-{variant}"
    return {
        "event_id": event_id,
        "partition_id": partition,
        "variant": variant,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "wildcard_count": query.count("*"),
        "maximum_attempts": 3,
        "attempt_outputs": [
            f"{variant}/{partition}.attempt-{attempt:02d}.json"
            for attempt in range(1, 4)
        ],
        "require_complete": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    for path in (*PILOT004_EVIDENCE, ADAPTER):
        if not path.is_file():
            raise FileNotFoundError(path)
    events = []
    for partition in queries.SCHEDULE_IDS:
        events.extend(
            (
                event(partition, "literal", queries.LITERAL_SCHEDULE[partition]),
                event(partition, "wildcard", queries.WILDCARD_SCHEDULE[partition]),
            )
        )
    replacements = [
        {
            "block_id": block_id,
            "candidate": candidate,
            "replaced_literals": list(literals),
        }
        for block_id, group in queries.WILDCARD_REPLACEMENTS.items()
        for candidate, literals in group
    ]
    return {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "NASA Technical Reports Server (NTRS)",
        "platform": "NASA",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Validate adapter v13's stable pre-submit and result-state waits, then "
            "complete every literal and standalone-wildcard main partition."
        ),
        "supersedes_failed_execution": {
            "pilot": "004",
            "finding": (
                "Four strict literal A1 attempts returned null. Three reached result "
                "reconciliation. Diagnostics found an intermediate date-only total of "
                "90395 accepted before the requested zero-result state."
            ),
            "repair": (
                "Require a stable rendered pre-submit baseline and a stable changed "
                "post-submit result state. An unchanged baseline always remains stale."
            ),
            "evidence": [
                {"path": str(path.relative_to(REPOSITORY_ROOT)), "sha256": digest(path)}
                for path in PILOT004_EVIDENCE
            ],
        },
        "date_window": {
            "publication_date_start": "2011-01-01",
            "publication_date_end": "2026-08-29",
            "inclusive": True,
        },
        "controls": {
            "field": "general q over metadata and indexed full text",
            "sort": "Publication Date (Oldest)",
            "page_size": 100,
            "limit": 10000,
            "max_pages": 100,
            "timeout_seconds": 240,
            "strict_complete_passes_per_event": 2,
            "full_abstracts": False,
            "language": None,
            "document_type": None,
            "all_other_filters": None,
            "automatic_screenshots": {
                "required": True,
                "opt_out": False,
                "search_page_suffix": ".search-page.png",
                "results_page_suffix": ".results-page.png",
                "same_directory_as_json": True,
                "schema_version": "ntrs-automatic-screenshots/v1",
            },
        },
        "translation": {
            "literal": "one straight-double-quoted ordinary token or ordered phrase",
            "boolean": "+ for AND, | for OR, with explicit parentheses",
            "proximity": False,
            "pair_expansion": False,
            "compound_blocks": {
                "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
                "G_structure": (
                    "G_structure_fixed OR G_product_exact OR G_variation OR "
                    "(G_product AND M_B)"
                ),
                "C1": "C1_fixed OR G_DSL",
                "T_precise": "ordinary OR block",
            },
        },
        "wildcard_candidate": {
            "operator": "one unquoted standalone term ending in *",
            "candidate_count": queries.WILDCARD_ATOM_COUNT,
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "replacements": replacements,
            "phrase_wildcards_used": False,
            "acronym_wildcards_used": False,
            "preferred_if_safe": True,
        },
        "acceptance_checks": [
            "All 18 semantic events have a valid strict success.",
            "Each success contains two matching mandatory sibling screenshots.",
            "Every failed attempt is null, empty, nonmergeable, and retained.",
            "Every query and source control matches the predeclared event.",
            "Each wildcard set contains its fresh literal partition set.",
            "Adoption requires exact partition-level set equality.",
        ],
        "retry_policy": {
            "maximum_attempts_per_event": 3,
            "retry_only_null_nonmergeable_failure": True,
            "same_query_and_controls": True,
            "retain_every_attempt": True,
            "stop_after_first_event_without_a_valid_success": True,
        },
        "adapter": {
            "id": "search_ntrs",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "query_snapshot": {
            "path": str(queries.QUERY_MODULE_PATH.relative_to(REPOSITORY_ROOT)),
            "sha256": queries.EXPECTED_QUERY_MODULE_SHA256,
            "term_snapshot_path": str(queries.TERM_SNAPSHOT_PATH.relative_to(REPOSITORY_ROOT)),
            "term_snapshot_sha256": queries.TERM_SNAPSHOT_SHA256,
        },
        "source_affecting_scripts": {
            str(path): digest(REPOSITORY_ROOT / path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = plan.get("events", [])
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if not isinstance(events, list) or len(events) != 18:
        return [*errors, "event_count"]
    expected = [
        f"{partition}-{variant}"
        for partition in queries.SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    ]
    if [item.get("event_id") for item in events] != expected:
        errors.append("event_order")
    for item in events:
        query = item.get("query")
        variant = item.get("variant")
        partition = item.get("partition_id")
        canonical = (
            queries.LITERAL_SCHEDULE if variant == "literal" else queries.WILDCARD_SCHEDULE
        ).get(partition)
        if query != canonical:
            errors.append(f"canonical_query:{item.get('event_id')}")
            continue
        if item.get("query_sha256") != digest_text(query):
            errors.append(f"query_hash:{item.get('event_id')}")
        if "~" in query or "NEAR" in query.upper():
            errors.append(f"proximity:{item.get('event_id')}")
        outputs = item.get("attempt_outputs")
        if not isinstance(outputs, list) or len(outputs) != 3 or len(set(outputs)) != 3:
            errors.append(f"attempt_outputs:{item.get('event_id')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        plan = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate(plan)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 1 if errors else 0
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    plan = build()
    errors = validate(plan)
    if errors:
        raise RuntimeError("Invalid generated plan: " + ", ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
