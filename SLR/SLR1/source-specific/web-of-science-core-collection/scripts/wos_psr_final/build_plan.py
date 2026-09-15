#!/usr/bin/env python3
"""Predeclare corrective Web of Science prior-secondary-review events."""

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

SCHEMA = "slr1-wos-final-psr-plan/v2"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_ROOT = Path(__file__).resolve().parent
QUERY_SNAPSHOT = SCRIPT_ROOT / "queries.py"
RUNNER = SCRIPT_ROOT / "run_final.py"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_web_of_science.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/web-of-science-core-collection/source-specific-guidelines.md"
)
SUPERSEDED_ASSESSMENT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/web-of-science-core-collection/psr-searches/assessment.json"
)
SUPPORTING_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-prior-secondary-reviews.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
EVENT_ORDER = ("PSR1", "PSR2", "PSR3", "PSR4")
CUTOFF_DATE = "2026-08-24"
CUTOFF_YEAR = 2026
SOURCE_AFFECTING_SCRIPTS = (
    Path("SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_psr_final/queries.py"),
    Path("SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_psr_final/build_plan.py"),
    Path("SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_psr_final/run_final.py"),
)
KNOWN_ITEM = {
    "citation": (
        "Buruso et al. (2026), Model-Based Systems Engineering in Space "
        "Applications: A Comprehensive Literature Review"
    ),
    "doi": "10.1002/sys.70051",
    "stable_id": "WOS:001705529700001",
    "title": "Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review",
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
        raise RuntimeError("Cannot read the Web of Science adapter version")
    return match.group(1)


def load_queries() -> Any:
    spec = importlib.util.spec_from_file_location("wos_final_psr_queries", QUERY_SNAPSHOT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def event(partition_id: str, query: str, strategy_version: str) -> dict[str, Any]:
    return {
        "event_id": f"final-psr-{partition_id}-web-of-science-core-collection-002",
        "partition_id": partition_id,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "output_filename": f"{partition_id}.json",
        "native_ris_filename": f"{partition_id}.ris",
        "limit": 1999,
        "max_pages": 40,
        "timeout_seconds": 300,
        "page_delay_seconds": 0.25,
        "require_complete": True,
        "strict_passes": 2,
        "strategy_version": strategy_version,
    }


def build() -> dict[str, Any]:
    queries = load_queries()
    strategy_version = repository_head()
    if strategy_version is None:
        raise RuntimeError("Cannot determine the repository revision")
    events = [
        event(partition_id, queries.PSR_SCHEDULE[partition_id], strategy_version)
        for partition_id in EVENT_ORDER
    ]
    return {
        "schema_version": SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": strategy_version,
        "source": "Web of Science Core Collection",
        "source_id": "web_of_science_core_collection",
        "review_namespace": "prior_secondary_reviews",
        "review_id": "slr1-1.1-restart",
        "phase": "identification",
        "strategy_reference": "slr1-wos-prior-secondary-review-v2",
        "concept_schedule_commit": queries.CONCEPT_SCHEDULE_COMMIT,
        "corrective_run": {
            "sequence": 2,
            "reason": "The first final run exported RIS without abstract content.",
            "superseded_assessment": str(
                SUPERSEDED_ASSESSMENT.relative_to(REPOSITORY_ROOT)
            ),
            "superseded_assessment_sha256": digest(SUPERSEDED_ASSESSMENT),
        },
        "cutoff": {
            "exact_common_cutoff": CUTOFF_DATE,
            "source_year_upper_bound": CUTOFF_YEAR,
            "source_precision": "year",
            "lower_date_bound": None,
            "native_query_clause": "PY=(1900-2026)",
            "screening_requirement": (
                "Screen every 2026 record against the exact common cutoff. "
                "The Web of Science discovery query can apply only the inclusive year bound."
            ),
        },
        "source_configuration": {
            "database": "Web of Science Core Collection",
            "editions": "All currently exposed editions",
            "field": "TS Topic",
            "query_mode": "raw",
            "sort": "Date: oldest first",
            "page_size": 50,
            "language": "All languages",
            "document_type_controls": [],
            "subject_controls": [],
            "access_controls": [],
            "peer_review_filter": None,
            "full_text_filter": None,
            "controlled_vocabulary": None,
            "native_ris": "RIS (other reference software), persisted for positive final events",
            "native_ris_record_content": "Author, Title, Source, Abstract",
        },
        "translation": {
            "population_wildcards_accepted_for_psr": True,
            "wildcard_count": 10,
            "wildcards_only_replace_population_members": True,
            "x_additions_literal": True,
            "proximity_operators": False,
            "local_pair_filter": False,
            "term_counts": queries.TERM_COUNTS,
            "query_character_counts": queries.QUERY_CHARACTER_COUNTS,
            "query_sha256": queries.QUERY_SHA256,
            "pilot_006_query_hashes_match_current_translation": (
                queries.QUERY_SHA256 == queries.EXPECTED_QUERY_SHA256
            ),
        },
        "strict_contract": {
            "strict_mode": "--require-complete",
            "membership_gate": "equal complete ordered WOS-ID sequences",
            "required_equal_controls": [
                "source total",
                "page count",
                "Web of Science Core Collection scope",
                "all current editions",
                "Date: oldest first",
                "native RIS reconciliation",
                "Author, Title, Source, Abstract export readback",
            ],
            "automatic_screenshots_required": True,
        },
        "known_item": KNOWN_ITEM,
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "fresh_authorized_target_per_partition": True,
            "close_ephemeral_target_after_partition": True,
            "target_identifiers_retained": False,
            "retry_policy": "one user-authorized corrective run after the abstract export defect",
            "native_ris_sidecar_for_positive_event": True,
            "native_ris_record_content": "Author, Title, Source, Abstract",
        },
        "adapter": {
            "id": "search_web_of_science",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "bindings": {
            "query_snapshot": {
                "path": str(QUERY_SNAPSHOT.relative_to(REPOSITORY_ROOT)),
                "sha256": digest(QUERY_SNAPSHOT),
            },
            "source_guideline": {
                "path": str(SOURCE_GUIDELINE.relative_to(REPOSITORY_ROOT)),
                "sha256": digest(SOURCE_GUIDELINE),
            },
            "protocols": {
                str(path.relative_to(REPOSITORY_ROOT)): digest(path)
                for path in (
                    MAIN_PROTOCOL,
                    DISCOVERY_PROTOCOL,
                    SUPPORTING_PROTOCOL,
                )
            },
            "source_affecting_scripts": {
                str(path): digest(REPOSITORY_ROOT / path)
                for path in SOURCE_AFFECTING_SCRIPTS
            },
        },
        "events": events,
    }


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != SCHEMA:
        errors.append("schema")
    if plan.get("source_id") != "web_of_science_core_collection":
        errors.append("source")
    if plan.get("review_namespace") != "prior_secondary_reviews":
        errors.append("namespace")
    cutoff = plan.get("cutoff", {})
    if (
        cutoff.get("exact_common_cutoff") != CUTOFF_DATE
        or cutoff.get("source_year_upper_bound") != CUTOFF_YEAR
        or cutoff.get("lower_date_bound") is not None
        or cutoff.get("native_query_clause") != "PY=(1900-2026)"
    ):
        errors.append("cutoff")
    controls = plan.get("source_configuration", {})
    if (
        controls.get("database") != "Web of Science Core Collection"
        or controls.get("field") != "TS Topic"
        or controls.get("query_mode") != "raw"
        or controls.get("sort") != "Date: oldest first"
        or controls.get("page_size") != 50
        or controls.get("language") != "All languages"
        or controls.get("document_type_controls") != []
        or controls.get("subject_controls") != []
        or controls.get("access_controls") != []
        or controls.get("peer_review_filter") is not None
        or controls.get("full_text_filter") is not None
        or controls.get("controlled_vocabulary") is not None
        or controls.get("native_ris_record_content")
        != "Author, Title, Source, Abstract"
    ):
        errors.append("controls")
    execution = plan.get("execution_policy", {})
    corrective = plan.get("corrective_run", {})
    if (
        plan.get("strategy_reference")
        != "slr1-wos-prior-secondary-review-v2"
        or corrective.get("sequence") != 2
        or execution.get("native_ris_record_content")
        != "Author, Title, Source, Abstract"
    ):
        errors.append("corrective_execution")
    events = plan.get("events")
    if not isinstance(events, list) or [item.get("partition_id") for item in events] != list(EVENT_ORDER):
        errors.append("event_order")
        return errors
    for item in events:
        partition = item["partition_id"]
        query = item.get("query", "")
        if (
            item.get("event_id")
            != f"final-psr-{partition}-web-of-science-core-collection-002"
            or item.get("output_filename") != f"{partition}.json"
            or item.get("native_ris_filename") != f"{partition}.ris"
            or item.get("query_sha256") != digest_text(query)
            or item.get("query_characters") != len(query)
            or item.get("limit") != 1999
            or item.get("max_pages") != 40
            or item.get("timeout_seconds") != 300
            or item.get("require_complete") is not True
            or item.get("strict_passes") != 2
        ):
            errors.append(f"event_contract:{partition}")
        if (
            query.count("*") != 10
            or "?" in query
            or "$" in query
            or not query.endswith(" AND PY=(1900-2026)")
            or any(marker in query.upper() for marker in ("NEAR", " SAME ", "LA=(", "DT=("))
        ):
            errors.append(f"wildcard_query:{partition}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        value = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate(value)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    plan = build()
    errors = validate(plan)
    if errors:
        raise RuntimeError("Invalid final WoS PSR plan: " + ", ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
