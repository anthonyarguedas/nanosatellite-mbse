#!/usr/bin/env python3
"""Build the predeclared Scopus post-proximity and wildcard pilot plan."""

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

SCHEMA = "scopus-post-proximity-wildcard-pilot-plan/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/scripts/scopus_pilot005/queries.py"),
    Path("SLR/SLR1/scripts/scopus_pilot005/build_plan.py"),
    Path("SLR/SLR1/scripts/scopus_pilot005/run_pilot.py"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def repository_head() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
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


def event(partition: str, variant: str, query: str) -> dict[str, Any]:
    return {
        "event_id": f"{partition}-{variant}",
        "partition_id": partition,
        "variant": variant,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output": f"{variant}/{partition}.json",
        "require_complete": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    if not ADAPTER.is_file():
        raise FileNotFoundError(ADAPTER)
    events = []
    for partition in queries.SCHEDULE_IDS:
        events.append(event(partition, "literal", queries.LITERAL_SCHEDULE[partition]))
        events.append(
            event(partition, "wildcard", queries.WILDCARD_SCHEDULE[partition])
        )
    replacements = [
        {
            "candidate": item["candidate"],
            "source_native_atom": f'TITLE-ABS-KEY("{item["candidate"]}")',
            "replaced_literals": list(item["replaced_literals"]),
            "coverage_basis": (
                "The source documents an attached trailing asterisk as truncation. "
                "Adoption still requires complete partition-level stable-ID equality."
            ),
        }
        for item in queries.WILDCARD_REPLACEMENTS
    ]
    return {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "Scopus",
        "platform": "Elsevier Scopus",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Run all nine current direct partitions without proximity operators and "
            "compare each complete literal stable-ID set with the deferred ten-wildcard "
            "population translation."
        ),
        "supersedes": {
            "pilot": "004",
            "reason": (
                "Pilot 004 stopped at its first literal event when thousands of individual "
                "Monaco key events could not produce exact readback. The adapter now uses one "
                "target-scoped browser text-entry event for long queries and still requires "
                "exact EditContext readback before Search."
            ),
            "source_events_reused": False,
        },
        "date_window": {
            "source_year_start": 2011,
            "source_year_end": 2026,
            "inclusive": True,
            "diagnostic_day_cutoff": "2026-08-29",
            "day_cutoff_handling": (
                "The source applies calendar years. Every 2026 record remains unresolved "
                "against the diagnostic day cutoff."
            ),
        },
        "controls": {
            "result_scope": "Documents",
            "language_facet": "English",
            "sort": "Date (oldest)",
            "page_size": 200,
            "limit": 1999,
            "max_pages": 10,
            "full_abstracts": False,
            "document_type": None,
            "subject_area": None,
            "access": None,
            "peer_review": None,
            "controlled_vocabulary": None,
            "strict_passes_per_event": 2,
            "automatic_screenshots": {
                "required": True,
                "opt_out": False,
                "search_page_suffix": ".search-page.png",
                "results_page_suffix": ".results-page.png",
                "same_directory_as_json": True,
                "schema_version": "scopus-automatic-screenshots/v1",
            },
        },
        "translation": {
            "literal": 'TITLE-ABS-KEY("ordinary token or ordered phrase")',
            "boolean": "uppercase AND and OR with explicit parentheses",
            "proximity": False,
            "pair_expansion": False,
            "compound_blocks": {
                "G_model": (
                    "F(G_model_fixed) OR F(G_mission_exact) OR "
                    "(F(G_mission) AND F(M_B))"
                ),
                "G_structure": (
                    "F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) "
                    "OR (F(G_product) AND F(M_B))"
                ),
                "C1": "F(C1_fixed) OR F(G_DSL)",
                "BT2": "F(P) AND F(M_B) AND F(T_precise)",
            },
        },
        "wildcard_candidate": {
            "operator": "attached trailing * in a loose quoted Scopus term or phrase",
            "wildcard_count": len(queries.WILDCARD_REPLACEMENTS),
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "unchanged_population_literal_count": (
                queries.TERM_COUNTS["P"] - queries.REPLACED_LITERAL_COUNT
            ),
            "character_reduction_per_partition": 375,
            "replacements": replacements,
            "preferred_if_safe": True,
        },
        "acceptance_checks": [
            "All 18 events complete two independent exhaustive ordered stable-ID passes.",
            "Every event preserves exact query, year, language, scope, sort, and page-size readback.",
            "Every successful JSON has both mandatory sibling screenshots with matching hashes and dimensions.",
            "Each wildcard stable-ID set contains its fresh literal set for the same partition.",
            "Adoption requires exact set equality in every main partition. Any wildcard-only record keeps the literal translation pending explicit assessment.",
            "No count equality alone establishes wildcard safety.",
        ],
        "stop_rules": [
            "Run each literal event immediately before its wildcard event.",
            "Stop after the first failed or invalid event. Do not retry or infer a set.",
            "Retain a failed adapter JSON and any screenshots that were captured before failure.",
        ],
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest_file(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "term_snapshot": {
            "path": str(queries.TERM_SNAPSHOT_PATH.relative_to(REPOSITORY_ROOT)),
            "sha256": queries.TERM_SNAPSHOT_SHA256,
            "term_counts": queries.TERM_COUNTS,
        },
        "source_affecting_scripts": {
            str(path): digest_file(REPOSITORY_ROOT / path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors = []
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
        if not isinstance(query, str) or not query:
            errors.append(f"query:{item.get('event_id')}")
            continue
        if item.get("query_sha256") != digest_text(query):
            errors.append(f"query_hash:{item.get('event_id')}")
        if item.get("query_characters") != len(query):
            errors.append(f"query_length:{item.get('event_id')}")
        if " W/" in query.upper() or " PRE/" in query.upper():
            errors.append(f"proximity:{item.get('event_id')}")
        expected_wildcards = 0 if item.get("variant") == "literal" else 10
        if query.count("*") != expected_wildcards:
            errors.append(f"wildcards:{item.get('event_id')}")
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
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
