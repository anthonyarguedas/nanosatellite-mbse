#!/usr/bin/env python3
"""Build the predeclared Scopus tied-order diagnostic plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "scopus-tied-order-diagnostic-plan/v1"
PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
PAPER_IDS = (
    "SCOPUS-PUBLICATION:85137554950",
    "SCOPUS-PUBLICATION:105005251801",
    "SCOPUS-PUBLICATION:105002219161",
    "SCOPUS-PUBLICATION:105033917858",
)
EIDS = tuple(value.replace("SCOPUS-PUBLICATION:", "2-s2.0-") for value in PAPER_IDS)
QUERY = "EID(" + " OR ".join(EIDS) + ")"
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot010/build_plan.py"),
    Path("SLR/SLR1/source-specific/scopus/scripts/scopus_pilot010/run_pilot.py"),
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


def build() -> dict:
    events = [
        {
            "event_id": f"swapping-papers-pass{number}",
            "pass_number": number,
            "protocol_commit": PROTOCOL_COMMIT,
            "query": QUERY,
            "query_sha256": digest_text(QUERY),
            "query_characters": len(QUERY),
            "output": f"passes/pass{number}.json",
            "require_complete": False,
            "do_not_merge": True,
        }
        for number in range(1, 7)
    ]
    return {
        "schema_version": SCHEMA,
        "pilot": "010",
        "source": "Scopus",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Repeat an exact four-EID query for the two same-year pairs that changed "
            "position under Date (oldest). Record whether a stable tie-break pattern exists."
        ),
        "prior_observation": {
            "pilot008_swaps": [
                {
                    "year": 2022,
                    "ranks": [90, 91],
                    "paper_ids": list(PAPER_IDS[:2]),
                },
                {
                    "year": 2025,
                    "ranks": [142, 143],
                    "paper_ids": list(PAPER_IDS[2:]),
                },
            ],
            "pilot009_swap": {
                "year": 2025,
                "ranks": [142, 143],
                "paper_ids": list(PAPER_IDS[2:]),
            },
            "exact_publication_date_retained": False,
        },
        "identity_query": {
            "query": QUERY,
            "paper_ids": list(PAPER_IDS),
            "eids": list(EIDS),
            "discovery_translation": False,
        },
        "controls": {
            "year_start": 2011,
            "year_end": 2026,
            "result_scope": "Documents",
            "language_facet": "English",
            "sort": "Date (oldest)",
            "page_size": 10,
            "limit": 10,
            "max_pages": 1,
            "full_abstracts": False,
            "independent_owned_page_per_event": True,
            "automatic_screenshots_required": True,
        },
        "acceptance_checks": [
            "All six events complete one exhaustive four-record traversal.",
            "Every event returns exactly the four requested stable IDs without duplicates.",
            "Every event retains Date (oldest), Documents, years, English, and page size 10 readback.",
            "Every successful JSON has both mandatory sibling screenshots.",
            "Every observed order is reported. No order pattern is inferred from equal sets alone.",
        ],
        "stop_rules": [
            "Stop after the first failed or invalid event.",
            "Do not retry, replace, or reinterpret a failed event as source zero.",
        ],
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
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
    if not isinstance(events, list) or len(events) != 6:
        return [*errors, "event_count"]
    if [event.get("pass_number") for event in events] != list(range(1, 7)):
        errors.append("pass_order")
    for event in events:
        if event.get("query") != QUERY:
            errors.append(f"query:{event.get('event_id')}")
        if event.get("query_sha256") != digest_text(QUERY):
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
