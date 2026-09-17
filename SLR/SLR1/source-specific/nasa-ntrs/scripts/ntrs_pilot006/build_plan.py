#!/usr/bin/env python3
"""Build the maximal wildcard continuation plan for NASA NTRS Pilot 006."""

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

SCHEMA = "ntrs-maximal-wildcard-pilot-plan/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ntrs.py"
BASELINE_ROOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/nasa-ntrs/pilots/005"
BASELINE_PLAN = BASELINE_ROOT / "searches/event-plan.json"
BASELINE_RUN = BASELINE_ROOT / "searches/run-receipt.json"
BASELINE_ASSESSMENT = BASELINE_ROOT / "searches/assessment.json"
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot006/queries.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot006/build_plan.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot006/run_pilot.py"),
    Path("SLR/SLR1/source-specific/nasa-ntrs/scripts/ntrs_pilot005/run_pilot.py"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


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


def stable_ids(path: Path) -> list[str]:
    value = load(path)
    return [row["paperId"] for row in value["results"]]


def sequence_hash(values: list[str]) -> str:
    result = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


def build() -> dict[str, Any]:
    baseline_plan = load(BASELINE_PLAN)
    baseline_run = load(BASELINE_RUN)
    baseline_assessment = load(BASELINE_ASSESSMENT)
    if baseline_assessment.get("status") != "passed":
        raise RuntimeError("Pilot 005 is not an accepted fresh literal baseline")
    if baseline_assessment.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        raise RuntimeError("Pilot 005 uses a different protocol commit")
    if digest(ADAPTER) != baseline_plan.get("adapter", {}).get("sha256"):
        raise RuntimeError("The adapter changed after Pilot 005")

    run_events = {event["event_id"]: event for event in baseline_run["events"]}
    baselines = {}
    events = []
    for partition in queries.SCHEDULE_IDS:
        outcome = run_events[f"{partition}-literal"]
        path = BASELINE_ROOT / outcome["accepted_artifact"]
        ids = stable_ids(path)
        baselines[partition] = {
            "path": str(path.relative_to(REPOSITORY_ROOT)),
            "sha256": digest(path),
            "source_total": len(ids),
            "ordered_stable_ids_sha256": sequence_hash(ids),
        }
        query = queries.WILDCARD_SCHEDULE[partition]
        events.append(
            {
                "event_id": f"{partition}-maximal-wildcard",
                "partition_id": partition,
                "variant": "maximal_wildcard",
                "protocol_commit": queries.PROTOCOL_COMMIT,
                "query": query,
                "query_sha256": digest_text(query),
                "query_characters": len(query),
                "wildcard_count": query.count("*"),
                "maximum_attempts": 3,
                "attempt_outputs": [
                    f"maximal-wildcard/{partition}.attempt-{attempt:02d}.json"
                    for attempt in range(1, 4)
                ],
                "require_complete": True,
                "do_not_merge": True,
            }
        )
    replacements = [
        {"block_id": block, "candidate": candidate, "replaced_literals": list(literals)}
        for block, group in queries.WILDCARD_REPLACEMENTS.items()
        for candidate, literals in group
    ]
    return {
        "schema_version": SCHEMA,
        "pilot": "006",
        "source": "NASA Technical Reports Server (NTRS)",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test wildcard compression for every compatible term morphology family "
            "against Pilot 005's fresh complete literal partition sets."
        ),
        "baseline": {
            "pilot": "005",
            "plan": {"path": str(BASELINE_PLAN.relative_to(REPOSITORY_ROOT)), "sha256": digest(BASELINE_PLAN)},
            "run": {"path": str(BASELINE_RUN.relative_to(REPOSITORY_ROOT)), "sha256": digest(BASELINE_RUN)},
            "assessment": {"path": str(BASELINE_ASSESSMENT.relative_to(REPOSITORY_ROOT)), "sha256": digest(BASELINE_ASSESSMENT)},
            "partitions": baselines,
        },
        "date_window": {
            "publication_date_start": "2011-01-01",
            "publication_date_end": "2026-08-29",
            "inclusive": True,
        },
        "controls": dict(baseline_plan.get("controls", {})),
        "translation": {
            "boolean": "+ for AND, | for OR, with explicit parentheses",
            "proximity": False,
            "pair_expansion": False,
            "wildcard_atom_count": queries.WILDCARD_ATOM_COUNT,
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "phrase_term_wildcards": True,
            "acronym_wildcards": False,
            "replacements": replacements,
        },
        "acceptance_checks": [
            "All nine maximal wildcard events have a valid strict success.",
            "Every success contains both mandatory sibling screenshots.",
            "Every failed attempt remains null, empty, and nonmergeable.",
            "Every maximal wildcard set contains its pinned Pilot 005 literal set.",
            "Adoption requires exact set equality in every partition.",
        ],
        "retry_policy": dict(baseline_plan.get("retry_policy", {})),
        "adapter": {
            "id": "search_ntrs",
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


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = plan.get("events", [])
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if not isinstance(events, list) or len(events) != 9:
        return [*errors, "event_count"]
    if [event.get("partition_id") for event in events] != list(queries.SCHEDULE_IDS):
        errors.append("event_order")
    for event in events:
        query = event.get("query")
        partition = event.get("partition_id")
        if query != queries.WILDCARD_SCHEDULE.get(partition):
            errors.append(f"query:{partition}")
        if event.get("query_sha256") != digest_text(query):
            errors.append(f"query_hash:{partition}")
        if "~" in query or "NEAR" in query.upper():
            errors.append(f"proximity:{partition}")
        if event.get("wildcard_count") != query.count("*"):
            errors.append(f"wildcard_count:{partition}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        plan = load(args.output)
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
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
