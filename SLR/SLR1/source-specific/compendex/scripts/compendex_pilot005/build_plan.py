#!/usr/bin/env python3
"""Build the predeclared Compendex Pilot 005 wildcard event plan."""

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

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER_DIR = Path.home() / "agent-tools/internet/skills/browser/scripts"
ADAPTER_ENTRYPOINT = ADAPTER_DIR / "search_compendex_inspec.py"
ADAPTER_IMPLEMENTATION = ADAPTER_DIR / "_engineering_village_search.py"
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/queries.py"),
    Path("SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/build_plan.py"),
    Path("SLR/SLR1/source-specific/compendex/scripts/compendex_pilot005/run_pilot.py"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_head() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", value) else None


def adapter_version() -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER_IMPLEMENTATION.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot read the Engineering Village adapter version")
    return match.group(1)


def event(event_id: str, variant: str, query: str, output: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "schedule_id": "A1",
        "variant": variant,
        "purpose": (
            f"Strict paired two-pass complete {variant} A1 capture for the bounded "
            "wildcard set comparison."
        ),
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "year_start": 2011,
        "year_end": 2026,
        "limit": 1000,
        "max_pages": 40,
        "timeout_seconds": 90.0,
        "page_delay_seconds": 0.5,
        "require_complete": True,
        "output": output,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    scripts = {
        str(path): digest_file(REPOSITORY_ROOT / path)
        for path in SOURCE_AFFECTING_SCRIPTS
    }
    replacements = []
    for item in queries.WILDCARD_REPLACEMENTS:
        replacements.append(
            {
                "candidate": item["candidate"],
                "source_native_atom": f"({item['candidate']} WN ALL)",
                "replaced_literals": list(item["replaced_literals"]),
                "possible_extra_completions": list(item["possible_extra_completions"]),
                "coverage_basis": (
                    "Engineering Village documents trailing * as zero or more characters. "
                    "The live set comparison remains required before adoption."
                ),
            }
        )
    events = [
        event("literal-A1", "literal", queries.A1_LITERAL, "cells/literal-A1.json"),
        event(
            "wildcard-A1",
            "three-family trailing-wildcard candidate",
            queries.A1_WILDCARD,
            "cells/wildcard-A1.json",
        ),
    ]
    return {
        "schema_version": "engineering-village-wildcard-pilot-plan/v1",
        "source": "Compendex with retained paired Inspec projection",
        "platform": "Elsevier Engineering Village",
        "pilot": "005",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Complete the deferred Pilot 002 comparison of current literal A1 against "
            "one conservative three-family trailing-wildcard candidate. Preserve the "
            "Compendex and Inspec totals and stable accessions separately."
        ),
        "scope": {
            "decision_target": "Compendex A1 source translation only",
            "paired_event": True,
            "inspec_projection": (
                "Retained because the fixed Engineering Village route selects both databases. "
                "It is reported separately and never combined with Compendex."
            ),
            "extrapolation": (
                "No result is extrapolated to another partition. A later partition requires "
                "its own predeclared complete set comparison."
            ),
        },
        "date_window": {
            "control": "Published",
            "start_year": 2011,
            "end_year": 2026,
            "inclusive": True,
            "source_precision": "year",
            "common_evidence_cutoff": "TBD",
            "cutoff_handling": (
                "Screen records in the cutoff year against the later exact common cutoff."
            ),
        },
        "controls": {
            "database_selection": ["compendex", "inspec"],
            "database_mask": "3",
            "search_mode": "Expert",
            "field": "ALL",
            "language_clause": "(English WN LA)",
            "autostemming": "off",
            "sort": "Date (Oldest)",
            "page_size": 25,
            "document_type": None,
            "open_access": None,
            "controlled_vocabulary": None,
            "strict_passes_per_event": 2,
            "native_ris": "required for every retained record in each strict pass",
            "raw_ris_persistence": False,
        },
        "adapter": {
            "id": "engineering_village_search",
            "version": adapter_version(),
            "entrypoint": "search_compendex_inspec.py",
            "entrypoint_sha256": digest_file(ADAPTER_ENTRYPOINT),
            "implementation": "_engineering_village_search.py",
            "implementation_sha256": digest_file(ADAPTER_IMPLEMENTATION),
            "source_affecting_dependency_closure": (
                "The two named adapter files are pinned. The adapter version identifies its "
                "reviewed sibling dependencies."
            ),
        },
        "source_affecting_scripts": scripts,
        "term_snapshot": {
            "path": "SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot007/queries.py",
            "sha256": queries.TERM_SNAPSHOT_SHA256,
            "term_counts": queries.TERM_COUNTS,
        },
        "comparison": {
            "schedule_id": "A1",
            "literal_query_characters": len(queries.A1_LITERAL),
            "wildcard_query_characters": len(queries.A1_WILDCARD),
            "character_reduction": queries.CHARACTER_REDUCTION,
            "wildcard_count": len(queries.WILDCARD_REPLACEMENTS),
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "replacements": replacements,
            "unchanged_elements": [
                "Every other P literal",
                "Every E_H literal",
                "Every M_H literal",
                "All phrase order and punctuation",
                "All field wrappers and Boolean relationships",
                "English, Published, database, sort, page-size, and no-facet controls",
            ],
        },
        "source_contract": {
            "asterisk": "zero or more characters anywhere in a word; terminal * is truncation",
            "minimum_prefix": "two non-wildcard characters in ordinary fields",
            "operators_per_term_limit": 3,
            "autostemming": "visibly off and verified by the adapter",
            "known_live_boundary": (
                "The reviewed adapter semantics audit found a positive Compendex "
                "nanosatellit* known-item contrast with an unstemmed plural negative."
            ),
        },
        "acceptance_checks": [
            "The literal event completes two independent source-exhaustive paired passes before the candidate is submitted.",
            "The wildcard event completes the same strict two-pass contract with identical controls.",
            "Each event has an exact source query echo, native RIS reconciliation, and separate Compendex and Inspec stable-accession projections.",
            "The candidate Compendex projection contains every literal Compendex accession.",
            "A zero candidate-only Compendex set permits A1-only adoption. Any candidate-only record requires explicit assessment before adoption.",
            "A missing literal accession, incomplete event, control mismatch, or source failure rejects the candidate.",
            "No count equality alone is treated as set evidence.",
            "No wildcard is adopted for another partition from this A1 comparison.",
        ],
        "stop_rules": [
            "Stop without submitting the wildcard event if the literal strict event fails.",
            "Stop after any source failure. Do not retry, narrow, infer a count, or reuse partial records.",
            "Retain every failure as an explicit non-mergeable null receipt.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
