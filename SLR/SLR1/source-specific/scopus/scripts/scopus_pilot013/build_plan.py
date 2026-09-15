#!/usr/bin/env python3
"""Build the Scopus set-reconciled strict validation plan."""

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

SCHEMA = "scopus-set-reconciled-strict-validation-plan/v1"
PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/scopus/scripts/scopus_pilot009/queries.py"
EXPECTED_QUERY_SNAPSHOT_SHA256 = "8d741bb5dac62d13027f0c07b5199b5d923f64addd177c8d19e0fbfcd24f4bac"
TIED_QUERY = (
    "EID(2-s2.0-85137554950 OR 2-s2.0-105005251801 OR "
    "2-s2.0-105002219161 OR 2-s2.0-105033917858)"
)
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot013/build_plan.py"),
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot013/run_pilot.py"),
)


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
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted Pilot 009 query snapshot changed")
    spec = importlib.util.spec_from_file_location("scopus_pilot013_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the accepted Scopus query snapshot")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def event(event_id: str, query: str, output: str, page_size: int, limit: int, max_pages: int) -> dict:
    return {
        "event_id": event_id,
        "protocol_commit": PROTOCOL_COMMIT,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output": output,
        "page_size": page_size,
        "limit": limit,
        "max_pages": max_pages,
        "require_complete": True,
        "do_not_merge": True,
    }


def build() -> dict:
    queries = load_queries()
    events = [
        event("B1-wildcard-strict-retry", queries.WILDCARD_SCHEDULE["B1"], "B1-wildcard-retry.json", 50, 1999, 10),
    ]
    return {
        "schema_version": SCHEMA,
        "pilot": "013",
        "source": "Scopus",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Retry the accepted wildcard B1 query once under the validated v2 "
            "complete-set strict contract."
        ),
        "continuation_of": {
            "pilot": "012",
            "prior_b1_total": 165,
            "prior_b1_strict_status": "success",
            "source_events_reused": False,
        },
        "pilot010_finding": {
            "complete_event_count": 6,
            "unique_order_count": 2,
            "all_stable_id_sets_equal": True,
            "stable_secondary_tie_breaker_observed": False,
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
                "Retain both ordered hashes and the changed-position count. Order equality "
                "is audit evidence and is not a membership-completeness gate."
            ),
        },
        "controls": {
            "year_start": 2011,
            "year_end": 2026,
            "result_scope": "Documents",
            "language_facet": "English",
            "sort": "Date (oldest)",
            "full_abstracts": False,
            "automatic_screenshots_required": True,
            "strict_passes_per_event": 2,
        },
        "acceptance_checks": [
            "The event completes two exhaustive passes with equal stable-ID sets.",
            "The v2 receipt retains both pass-order hashes and an order-difference count.",
            "The B1 event returns 165 unique IDs unless the live source total has changed explicitly.",
            "The successful JSON has both mandatory sibling screenshots.",
        ],
        "stop_rules": [
            "Stop after the first failed or invalid event.",
            "Do not retry or infer a set from a null-total failure.",
        ],
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "query_snapshot": {
            "path": str(QUERY_SNAPSHOT.relative_to(REPOSITORY_ROOT)),
            "sha256": digest(QUERY_SNAPSHOT),
        },
        "source_affecting_scripts": {
            str(path): digest(REPOSITORY_ROOT / path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "events": events,
    }


def validate(plan: dict) -> list[str]:
    errors = []
    events = plan.get("events")
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if not isinstance(events, list) or len(events) != 1:
        return [*errors, "event_count"]
    if [event.get("event_id") for event in events] != [
        "B1-wildcard-strict-retry",
    ]:
        errors.append("event_order")
    for event in events:
        if event.get("query_sha256") != digest_text(event.get("query", "")):
            errors.append(f"query_hash:{event.get('event_id')}")
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
