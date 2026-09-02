#!/usr/bin/env python3
"""Build the predeclared NASA NTRS Pilot 004 event plan."""

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

SCHEMA = "ntrs-post-proximity-wildcard-pilot-plan/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ntrs.py"
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/scripts/ntrs_pilot004/queries.py"),
    Path("SLR/SLR1/scripts/ntrs_pilot004/build_plan.py"),
    Path("SLR/SLR1/scripts/ntrs_pilot004/run_pilot.py"),
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
        raise RuntimeError("Cannot read the NTRS adapter version")
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
        "wildcard_count": query.count("*"),
        "output": f"{variant}/{partition}.json",
        "require_complete": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    if not ADAPTER.is_file():
        raise FileNotFoundError(ADAPTER)
    events = []
    for partition in queries.SCHEDULE_IDS:
        events.extend(
            (
                event(partition, "literal", queries.LITERAL_SCHEDULE[partition]),
                event(partition, "wildcard", queries.WILDCARD_SCHEDULE[partition]),
            )
        )
    replacements = []
    for block_id, block_replacements in queries.WILDCARD_REPLACEMENTS.items():
        for candidate, literals in block_replacements:
            replacements.append(
                {
                    "block_id": block_id,
                    "candidate": candidate,
                    "replaced_literals": list(literals),
                }
            )
    return {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "NASA Technical Reports Server (NTRS)",
        "platform": "NASA",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Run every post-proximity main partition in complete literal and "
            "standalone-wildcard forms, then compare complete canonical citation-ID sets."
        ),
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
            "center": None,
            "subject_category": None,
            "keyword": None,
            "collection": None,
            "source_refinement": None,
            "distribution": None,
            "access": None,
            "peer_review": None,
            "controlled_vocabulary": None,
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
                "G_model": (
                    "F(G_model_fixed) OR F(G_mission_exact) OR "
                    "(F(G_mission) AND F(M_B))"
                ),
                "G_structure": (
                    "F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) "
                    "OR (F(G_product) AND F(M_B))"
                ),
                "C1": "F(C1_fixed) OR F(G_DSL)",
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
            "rationale": (
                "Use every useful standalone-token morphology compression. Keep phrases "
                "literal because NTRS does not document exact-phrase semantics when a "
                "quoted term contains a wildcard. Keep acronyms literal so they remain "
                "standalone lexical tokens."
            ),
        },
        "acceptance_checks": [
            "All 18 events complete two exhaustive ordered canonical-ID passes.",
            "Every event preserves exact query, date, sort, page-size, and empty-filter readback.",
            "Every successful JSON has both mandatory sibling screenshots with matching hashes and dimensions.",
            "Each wildcard set contains the fresh literal set for its partition.",
            "Every wildcard-only record is retained and listed for assessment.",
            "Adopt the complete candidate only if every partition has exact literal-wildcard set equality.",
            "Counts alone never establish wildcard safety.",
        ],
        "stop_rules": [
            "Run each literal event immediately before its wildcard event.",
            "Stop after the first failed or invalid event.",
            "Do not retry, narrow, split, or infer a source set after failure.",
        ],
        "adapter": {
            "id": "search_ntrs",
            "version": adapter_version(),
            "sha256": digest_file(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "term_snapshot": {
            "path": str(queries.TERM_SNAPSHOT_PATH.relative_to(REPOSITORY_ROOT)),
            "sha256": queries.TERM_SNAPSHOT_SHA256,
            "term_counts": {
                key: len(value) for key, value in queries.TERM_BLOCKS.items()
            },
        },
        "source_affecting_scripts": {
            str(path): digest_file(REPOSITORY_ROOT / path)
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
        if not isinstance(query, str) or not query:
            errors.append(f"query:{item.get('event_id')}")
            continue
        if item.get("query_sha256") != digest_text(query):
            errors.append(f"query_hash:{item.get('event_id')}")
        if item.get("query_characters") != len(query):
            errors.append(f"query_length:{item.get('event_id')}")
        if "~" in query or "NEAR" in query.upper():
            errors.append(f"proximity:{item.get('event_id')}")
        expected_query = (
            queries.LITERAL_SCHEDULE
            if item.get("variant") == "literal"
            else queries.WILDCARD_SCHEDULE
        ).get(item.get("partition_id"))
        if query != expected_query:
            errors.append(f"canonical_query:{item.get('event_id')}")
        expected_wildcards = 0 if item.get("variant") == "literal" else query.count("*")
        if item.get("wildcard_count") != expected_wildcards:
            errors.append(f"wildcard_count:{item.get('event_id')}")
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
