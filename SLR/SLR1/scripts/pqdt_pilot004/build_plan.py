#!/usr/bin/env python3
"""Build the predeclared PQDT Global Pilot 004 wildcard comparison plan."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

from queries import (
    EXPECTED_SHARED_DECLARATION_SHA256,
    FAMILY_COUNT,
    FAMILY_RECEIPTS,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    QUERY_LIMIT,
    REPLACED_TERM_COUNT,
    SCHEDULE_IDS,
    SHARED_DECLARATION_PATH,
    TERM_COUNTS,
    WILDCARD_OPERATOR_COUNT_BY_BLOCK,
    WILDCARD_SCHEDULE,
)

PILOT = "004"
SOURCE = "ProQuest Dissertations & Theses Global"
SOURCE_ID = "proquest_dissertations_theses_global"
YEAR_START = 2011
YEAR_END = 2026
DIAGNOSTIC_CUTOFF = "2026-08-29"
ADAPTER_VERSION = "5"
SCHEMA = "pqdt-global-pilot004-event-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
REPOSITORY_ROOT = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific" / "pqdt-global" / "pilots" / PILOT
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"
ADAPTER_PATH = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_pqdt.py"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
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
    return value if completed.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", value) else None


def adapter_version(path: Path) -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Could not read the PQDT adapter version")
    return match.group(1)


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.name
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def event(variant: str, partition_id: str, query: str) -> dict[str, Any]:
    event_id = f"{variant}-{partition_id}"
    output = f"events/{event_id}.json"
    return {
        "event_id": event_id,
        "partition_id": partition_id,
        "variant": variant,
        "purpose": (
            f"Strict complete two-pass {variant} capture for the {partition_id} "
            "bounded-wildcard comparison."
        ),
        "query": query,
        "query_characters": len(query),
        "query_sha256": text_sha256(query),
        "year_start": YEAR_START,
        "year_end": YEAR_END,
        "language": "English",
        "mode": "strict_complete_two_pass",
        "output": output,
        "screenshots": screenshot_names(output),
        "diagnostic_only": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    if adapter_version(ADAPTER_PATH) != ADAPTER_VERSION:
        raise RuntimeError(f"PQDT adapter version {ADAPTER_VERSION} is required")
    events: list[dict[str, Any]] = []
    for partition_id in SCHEDULE_IDS:
        events.append(event("literal", partition_id, LITERAL_SCHEDULE[partition_id]))
        events.append(event("wildcard", partition_id, WILDCARD_SCHEDULE[partition_id]))

    literal_lengths = {key: len(value) for key, value in LITERAL_SCHEDULE.items()}
    wildcard_lengths = {key: len(value) for key, value in WILDCARD_SCHEDULE.items()}
    reductions = {
        key: literal_lengths[key] - wildcard_lengths[key] for key in SCHEDULE_IDS
    }
    wildcard_counts = {
        key: WILDCARD_SCHEDULE[key].count("[*") for key in SCHEDULE_IDS
    }
    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "platform": "ProQuest",
        "protocol_commit": PROTOCOL_COMMIT,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Compare strict complete literal and maximally bounded-wildcard "
            "translations of all nine schedule partitions after proximity removal."
        ),
        "adapter": {
            "id": "search_pqdt",
            "version": ADAPTER_VERSION,
            "sha256": file_sha256(ADAPTER_PATH),
            "mandatory_automatic_screenshots": True,
            "screenshot_schema": "pqdt-automatic-screenshots/v1",
            "screenshot_opt_out": False,
            "screenshot_files_per_event": 2,
        },
        "source_window": {
            "year_start": YEAR_START,
            "year_end": YEAR_END,
            "source_precision": "year",
            "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
            "cutoff_handling": (
                "Retain 2026 records for later screening against the exact diagnostic cutoff."
            ),
        },
        "controls": {
            "database": "exactly one allowed PQDT Global database label",
            "field": "NOFT",
            "language": "LA(English)",
            "sort": "DateAsc / Oldest first",
            "page_size": 20,
            "passes_per_event": 2,
            "full_text": False,
            "exclude_duplicates": False,
            "spelling_variants": False,
            "form_variants": False,
            "show_variants": False,
            "degree_or_document_type": None,
            "access": None,
            "controlled_vocabulary": None,
            "proximity": False,
            "pair_expansion": False,
            "screenshots": (
                "automatic configured search-page and first results-page PNGs beside every JSON"
            ),
        },
        "translation": {
            "literal_atom": "NOFT(quoted literal)",
            "wildcard_atom": (
                "NOFT(token or ordered phrase using the smallest safe bounded [*n])"
            ),
            "wildcard_scope": (
                "Every declared variant family with one safe common source stem. "
                "Singleton, punctuation, and unsafe-stem alternatives remain literal."
            ),
            "compound_blocks": {
                "G_model": "G_model_fixed OR G_mission_exact OR (G_mission AND M_B)",
                "G_structure": (
                    "G_structure_fixed OR G_product_exact OR G_variation OR "
                    "(G_product AND M_B)"
                ),
                "C1": "C1_fixed OR G_DSL",
                "BT2": "P AND M_B AND T_precise",
            },
            "term_counts": TERM_COUNTS,
            "wildcard_family_count": FAMILY_COUNT,
            "replaced_literal_occurrence_count_across_blocks": REPLACED_TERM_COUNT,
            "wildcard_operators_by_block": WILDCARD_OPERATOR_COUNT_BY_BLOCK,
            "wildcard_families": FAMILY_RECEIPTS,
            "literal_query_lengths": literal_lengths,
            "wildcard_query_lengths": wildcard_lengths,
            "character_reductions": reductions,
            "wildcard_operators_by_partition": wildcard_counts,
            "literal_query_sha256": {
                key: text_sha256(value) for key, value in LITERAL_SCHEDULE.items()
            },
            "wildcard_query_sha256": {
                key: text_sha256(value) for key, value in WILDCARD_SCHEDULE.items()
            },
            "validated_character_limit": QUERY_LIMIT,
            "shared_declaration_snapshot": {
                "path": str(SHARED_DECLARATION_PATH.relative_to(REPOSITORY_ROOT)),
                "sha256": EXPECTED_SHARED_DECLARATION_SHA256,
            },
        },
        "acceptance_checks": [
            "Every event receives exact source query, scope, year, language, variant, and sort readback.",
            "Every event completes two full record passes with the same total and ordered numeric document IDs.",
            "Every event saves both mandatory sibling screenshots with matching JSON receipts.",
            "Every wildcard partition contains every stable ID from its fresh adjacent literal partition.",
            "Every wildcard-only record is inspected against the intended protocol concepts before adoption.",
            "No proximity, pair expansion, result-driven split, type, access, or vocabulary restriction is introduced.",
        ],
        "stop_rules": [
            "Stop on the first source, access, challenge, control, screenshot, cleanup, or output failure.",
            "Retain a failed adapter JSON and any screenshots already captured.",
            "Never replace an event JSON, marker, screenshot, assessment, or validation report.",
        ],
        "schedule_ids": list(SCHEDULE_IDS),
        "event_count": len(events),
        "events": events,
    }


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def validate(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA:
        errors.append("Plan schema changed")
    if payload.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Protocol commit changed")
    adapter = payload.get("adapter")
    if not isinstance(adapter, Mapping) or adapter.get("version") != ADAPTER_VERSION:
        errors.append("Adapter declaration changed")
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != 18:
        return [*errors, "Plan must contain eighteen events"]
    expected_ids = [
        f"{variant}-{partition}"
        for partition in SCHEDULE_IDS
        for variant in ("literal", "wildcard")
    ]
    if [item.get("event_id") for item in events] != expected_ids:
        errors.append("Event order or identity changed")
    for item in events:
        partition = item.get("partition_id")
        variant = item.get("variant")
        schedule = LITERAL_SCHEDULE if variant == "literal" else WILDCARD_SCHEDULE
        query = item.get("query")
        if partition not in schedule or query != schedule[partition]:
            errors.append(f"Canonical query changed for {item.get('event_id')}")
            continue
        if item.get("query_sha256") != text_sha256(query) or item.get(
            "query_characters"
        ) != len(query):
            errors.append(f"Query receipt changed for {item.get('event_id')}")
        if "NEAR" in query.upper() or " PRE/" in query.upper():
            errors.append(f"Proximity syntax found for {item.get('event_id')}")
        if variant == "literal" and ("*" in query or "?" in query):
            errors.append(f"Wildcard found in literal event {item.get('event_id')}")
        if variant == "wildcard" and ("[*" not in query or "?" in query):
            errors.append(f"Bounded wildcard missing for {item.get('event_id')}")
        if len(query) >= QUERY_LIMIT:
            errors.append(f"Query reaches source limit for {item.get('event_id')}")
        if item.get("screenshots") != screenshot_names(str(item.get("output"))):
            errors.append(f"Screenshot names changed for {item.get('event_id')}")
        if item.get("diagnostic_only") is not True or item.get("do_not_merge") is not True:
            errors.append(f"Diagnostic boundary changed for {item.get('event_id')}")
    return errors


def write_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = validate(load(args.output))
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}, indent=2))
        return 1 if errors else 0
    payload = build()
    errors = validate(payload)
    if errors:
        raise RuntimeError("Generated plan is invalid: " + "; ".join(errors))
    write_create_only(args.output, payload)
    print(json.dumps({"saved": str(args.output), "events": len(payload["events"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
