#!/usr/bin/env python3
"""Build the predeclared Compendex Pilot 008 readiness plan."""

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

SCHEMA = "engineering-village-readiness-pilot-plan/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER_DIR = Path.home() / "agent-tools/internet/skills/browser/scripts"
ADAPTER_ENTRYPOINT = ADAPTER_DIR / "search_compendex_inspec.py"
ADAPTER_IMPLEMENTATION = ADAPTER_DIR / "_engineering_village_search.py"
PILOT006_FAILURE = Path(
    "SLR/SLR1/source-specific/compendex/pilots/006/searches/cells/"
    "B2.NON_MERGEABLE_FAILURE.json"
)
PILOT006_RUN_RECEIPT = Path(
    "SLR/SLR1/source-specific/compendex/pilots/006/searches/run-receipt.json"
)
PILOT007_FAILURE = Path(
    "SLR/SLR1/source-specific/compendex/pilots/007/searches/cells/"
    "BC1.NON_MERGEABLE_FAILURE.json"
)
PILOT007_RUN_RECEIPT = Path(
    "SLR/SLR1/source-specific/compendex/pilots/007/searches/run-receipt.json"
)
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/compendex/scripts/compendex_pilot008/queries.py"),
    Path("SLR/SLR1/source-specific/compendex/scripts/compendex_pilot008/build_plan.py"),
    Path("SLR/SLR1/source-specific/compendex/scripts/compendex_pilot008/run_pilot.py"),
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
        ADAPTER_IMPLEMENTATION.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot read the Engineering Village adapter version")
    return match.group(1)


def event(partition: str) -> dict[str, Any]:
    query = queries.EVENT_QUERIES[partition]
    return {
        "event_id": partition,
        "partition_id": partition,
        "boolean_form": queries.BOOLEAN_FORMS[partition],
        "changed_definition_since_pilot003": partition in queries.CHANGED_IDS,
        "purpose": (
            f"Strict paired two-pass complete current {partition} readiness capture "
            "with the approved Compendex population wildcard block."
        ),
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "wildcard_count": query.count("*"),
        "year_start": 2011,
        "year_end": 2026,
        "limit": 5000,
        "max_pages": 200,
        "timeout_seconds": 180.0,
        "page_delay_seconds": 2.0,
        "require_complete": True,
        "max_fresh_attempts": 3,
        "attempts": [
            {
                "attempt_ordinal": attempt,
                "output": f"attempts/{partition}/attempt-{attempt:02d}.json",
                "failure_output": (
                    f"attempts/{partition}/attempt-{attempt:02d}."
                    "NON_MERGEABLE_FAILURE.json"
                ),
                "screenshot_outputs": [
                    f"attempts/{partition}/attempt-{attempt:02d}.search-page.png",
                    f"attempts/{partition}/attempt-{attempt:02d}.results-page.png",
                ],
            }
            for attempt in range(1, 4)
        ],
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    for path in (ADAPTER_ENTRYPOINT, ADAPTER_IMPLEMENTATION):
        if not path.is_file():
            raise FileNotFoundError(path)
    version = adapter_version()
    if version != "16":
        raise RuntimeError(f"Pilot 008 requires adapter v16, found v{version}")
    for path in (
        PILOT006_FAILURE,
        PILOT006_RUN_RECEIPT,
        PILOT007_FAILURE,
        PILOT007_RUN_RECEIPT,
    ):
        if not (REPOSITORY_ROOT / path).is_file():
            raise FileNotFoundError(REPOSITORY_ROOT / path)
    events = [event(partition) for partition in queries.RUN_ORDER]
    return {
        "schema_version": SCHEMA,
        "pilot": "008",
        "source": "Compendex with a retained paired Inspec projection",
        "platform": "Elsevier Engineering Village",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Run one consolidated readiness pilot over all nine current Boolean "
            "partitions with the approved Compendex F(P) wildcard translation, no "
            "proximity, strict paired Compendex and Inspec capture, and both mandatory "
            "adapter v16 screenshots. Confirm current B2 and the changed BG1, BG2, BC1, "
            "and BT2 definitions before any final search."
        ),
        "historical_gaps": {
            "pilot003": {
                "B2": "explicit null strict-capture failure",
                "changed_definitions_not_current": list(queries.CHANGED_IDS),
            },
            "pilot006": {
                "outcome": (
                    "A1, A2, A3, and B1 completed. Current B2 then stopped on one "
                    "unverified next-page transition, so the predeclared stop rule left "
                    "the consolidated run incomplete."
                ),
                "failure_artifact": str(PILOT006_FAILURE),
                "failure_artifact_sha256": digest_file(
                    REPOSITORY_ROOT / PILOT006_FAILURE
                ),
                "run_receipt": str(PILOT006_RUN_RECEIPT),
                "run_receipt_sha256": digest_file(
                    REPOSITORY_ROOT / PILOT006_RUN_RECEIPT
                ),
            },
            "pilot007": {
                "outcome": (
                    "B2, BG1, and BG2 completed. BC1 then stopped during creation of "
                    "an adapter-owned page before source submission, so the predeclared "
                    "stop rule left the second consolidated run incomplete."
                ),
                "failure_artifact": str(PILOT007_FAILURE),
                "failure_artifact_sha256": digest_file(
                    REPOSITORY_ROOT / PILOT007_FAILURE
                ),
                "run_receipt": str(PILOT007_RUN_RECEIPT),
                "run_receipt_sha256": digest_file(
                    REPOSITORY_ROOT / PILOT007_RUN_RECEIPT
                ),
            },
            "source_events_reused": False,
            "interpretation": (
                "Pilots 003, 006, and 007 remain immutable. Pilot 008 starts every "
                "partition again as a fresh source event. The critical gaps run first, "
                "and all nine events must still pass."
            ),
        },
        "scope": {
            "decision_target": "Compendex readiness for a later final search",
            "paired_event": True,
            "inspec_projection": (
                "Retain and validate the Inspec records separately because the fixed paired "
                "route selects both databases. This Compendex pilot does not approve an "
                "Inspec wildcard translation or create an Inspec final search."
            ),
            "final_search": False,
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
            "automatic_screenshots": {
                "required": True,
                "opt_out": False,
                "capture_pass": "pass-1",
                "search_page_suffix": ".search-page.png",
                "results_page_suffix": ".results-page.png",
                "same_directory_as_json": True,
                "schema_version": "engineering-village-automatic-screenshots/v1",
            },
        },
        "translation": {
            "literal": '("ordinary token or ordered phrase" WN ALL)',
            "boolean": "uppercase AND and OR with explicit parentheses",
            "proximity": False,
            "pair_expansion": False,
            "population_block": {
                "status": "approved for all nine Compendex schedule entries",
                "wildcard_atoms": [
                    f"({item['candidate']} WN ALL)"
                    for item in queries.WILDCARD_REPLACEMENTS
                ],
                "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
                "preserved_other_population_terms": True,
            },
            "compound_definitions": queries.COMPOUND_DEFINITIONS,
            "schedule": queries.BOOLEAN_FORMS,
        },
        "critical_live_checks": {
            "B2": (
                "Must complete a fresh strict paired event. A null, partial, inferred, or "
                "reused result fails readiness."
            ),
            "changed_partitions": {
                partition: {
                    "boolean_form": queries.BOOLEAN_FORMS[partition],
                    "must_complete_live": True,
                }
                for partition in queries.CHANGED_IDS
            },
        },
        "acceptance_checks": [
            "All nine fresh events complete two independent source-exhaustive paired passes.",
            "Every event uses exactly three approved trailing population wildcards and no proximity operator.",
            "Every event preserves exact query, database, Published-year, language, autostemming, sort, page-size, and no-facet readback.",
            "Every retained record reconciles against native RIS in both strict passes and has one database-scoped stable accession.",
            "Compendex and Inspec totals, accessions, and unions remain separate.",
            "Every event retains a configured-search screenshot and verified-first-results screenshot whose hashes and dimensions match the JSON receipt.",
            "B2 completes with a non-null strict result.",
            "BG1, BG2, BC1, and BT2 each complete with the current compound definition.",
            "No event or union is treated as a final search.",
        ],
        "execution_order": {
            "partitions": list(queries.RUN_ORDER),
            "basis": (
                "Run B2 and the four changed definitions before repeating the partitions "
                "that already completed in an earlier attempt. This ordering changes no query or "
                "acceptance rule."
            ),
            "page_delay_seconds": 2.0,
            "default_inter_event_delay_seconds": 10.0,
        },
        "fresh_attempt_policy": {
            "maximum_attempts_per_partition": 3,
            "default_delay_between_attempts_seconds": 30.0,
            "basis": (
                "Adapter v16 requires a fresh owned page and a fresh whole attempt after "
                "an unverified page transition. Pilot 007 also observed a pre-submission "
                "owned-page setup failure while another shared-browser task was active."
            ),
            "acceptance": (
                "Only a complete two-pass result with both verified screenshots is accepted. "
                "Each failed attempt remains null and non-mergeable."
            ),
        },
        "stop_rules": [
            "Run partitions in the predeclared critical-first order.",
            "After a failed attempt, wait and start the exact query on a fresh adapter-owned page. Never resume a pass or reuse partial records.",
            "Stop the pilot after three failed fresh attempts for one partition.",
            "Do not narrow a query, infer a count, or reuse any Pilot 003, 006, or 007 source result.",
            "Retain every create-only non-mergeable failure receipt and any screenshots already captured.",
        ],
        "adapter": {
            "id": "engineering_village_search",
            "version": version,
            "entrypoint": "search_compendex_inspec.py",
            "entrypoint_sha256": digest_file(ADAPTER_ENTRYPOINT),
            "implementation": "_engineering_village_search.py",
            "implementation_sha256": digest_file(ADAPTER_IMPLEMENTATION),
            "execution_route": "strict paired Python API with mandatory screenshot paths",
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
    errors: list[str] = []
    events = plan.get("events")
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if plan.get("pilot") != "008":
        errors.append("pilot")
    if plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        errors.append("protocol_commit")
    if plan.get("adapter", {}).get("version") != "16":
        errors.append("adapter_version")
    if not isinstance(events, list) or len(events) != 9:
        return [*errors, "event_count"]
    if [item.get("event_id") for item in events] != list(queries.RUN_ORDER):
        errors.append("event_order")
    for item in events:
        partition = item.get("partition_id")
        query = item.get("query")
        if partition not in queries.EVENT_QUERIES or query != queries.EVENT_QUERIES.get(
            partition
        ):
            errors.append(f"query:{partition}")
            continue
        if item.get("query_sha256") != digest_text(query):
            errors.append(f"query_hash:{partition}")
        if item.get("query_characters") != len(query):
            errors.append(f"query_length:{partition}")
        if item.get("wildcard_count") != 3 or query.count("*") != 3:
            errors.append(f"wildcards:{partition}")
        if queries.PROXIMITY_OPERATOR_RE.search(query):
            errors.append(f"proximity:{partition}")
        if item.get("boolean_form") != queries.BOOLEAN_FORMS[partition]:
            errors.append(f"boolean:{partition}")
        if item.get("changed_definition_since_pilot003") is not (
            partition in queries.CHANGED_IDS
        ):
            errors.append(f"changed_flag:{partition}")
        attempts = item.get("attempts")
        if (
            item.get("max_fresh_attempts") != 3
            or not isinstance(attempts, list)
            or len(attempts) != 3
        ):
            errors.append(f"attempts:{partition}")
            continue
        for ordinal, attempt in enumerate(attempts, start=1):
            prefix = f"attempts/{partition}/attempt-{ordinal:02d}"
            if attempt.get("attempt_ordinal") != ordinal:
                errors.append(f"attempt_ordinal:{partition}:{ordinal}")
            if attempt.get("output") != f"{prefix}.json":
                errors.append(f"attempt_output:{partition}:{ordinal}")
            if attempt.get("failure_output") != f"{prefix}.NON_MERGEABLE_FAILURE.json":
                errors.append(f"attempt_failure:{partition}:{ordinal}")
            if attempt.get("screenshot_outputs") != [
                f"{prefix}.search-page.png",
                f"{prefix}.results-page.png",
            ]:
                errors.append(f"attempt_screenshots:{partition}:{ordinal}")
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
