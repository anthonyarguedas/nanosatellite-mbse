#!/usr/bin/env python3
"""Build the predeclared Wiley Pilot 005 native RIS event plan."""

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
    ADOPTED_EVENTS,
    PILOT004_QUERY_PATH,
    PILOT004_QUERY_SHA256,
    PROTOCOL_COMMIT,
    SCHEDULE_IDS,
    WILDCARD_REPLACEMENTS,
)

PILOT = "005"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
ADAPTER_VERSION = "12"
SCHEMA = "wiley-online-library-pilot005-event-plan/v1"
EVENT_SCHEMA = "wiley-online-library-pilot005-native-ris-event/v1"
ADAPTER_PATH = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_wiley_online_library.py"
)
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
REPOSITORY_ROOT = SCRIPT_DIR.parents[3]
PILOT_ROOT = (
    SLR1_DIR / "source-specific" / "wiley-online-library" / "pilots" / PILOT
)
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"
SOURCE_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "build_plan.py",
    SCRIPT_DIR / "run_pilot.py",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def repository_head() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", value) else None


def adapter_version(path: Path) -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        path.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Could not read the Wiley adapter version")
    return match.group(1)


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name.removesuffix(".json")
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def build() -> dict[str, Any]:
    if adapter_version(ADAPTER_PATH) != ADAPTER_VERSION:
        raise RuntimeError(f"Wiley adapter version {ADAPTER_VERSION} is required")
    events: list[dict[str, Any]] = []
    for source in ADOPTED_EVENTS:
        output = f"events/{source['event_id']}.json"
        query = source["query"]
        events.append(
            {
                **source,
                "query_characters": len(query),
                "query_sha256": text_sha256(query),
                "output": output,
                "screenshots": screenshot_names(output),
                "date_start": DATE_START,
                "date_end": DATE_END,
                "limit": 5000,
                "max_pages": 20,
                "max_source_total": 5000,
                "passes": 2,
                "sort": "Earliest",
                "content": "articlesChapters",
                "native_ris": "visible page scoped export with abstracts",
                "raw_ris_persisted": False,
                "diagnostic_only": True,
                "do_not_merge": True,
            }
        )
    return {
        "schema_version": SCHEMA,
        "event_schema_version": EVENT_SCHEMA,
        "pilot": PILOT,
        "source": "Wiley Online Library",
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_head(),
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Validate the adopted ten-cell current Wiley schedule with the production "
            "page-scoped native RIS route, two complete ordered DOI passes, exact-date "
            "accounting, and both mandatory screenshots."
        ),
        "scope": {
            "schedule_partitions": list(SCHEDULE_IDS),
            "source_cell_count": len(events),
            "A2_cells": ["A2-mh", "A2-mb"],
            "larger_set_checks": ["B2", "BT2"],
            "pilot004_boundary": (
                "Pilot 004 supplied rendered DOI ledgers only. No Pilot 004 RIS, page, "
                "browser, screenshot, or attempt state enters this pilot."
            ),
        },
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "inclusive": True,
            "source_control": "enclosing source months",
            "record_accounting": "visible First published exact-day status",
            "common_evidence_cutoff": "TBD",
            "purpose": "fixed diagnostic window, not a final review search",
        },
        "controls": {
            "source_route": "articlesChapters/default",
            "field": "one Anywhere/AllField row",
            "sort": "Date / sortBy=Earliest (observed newest-first)",
            "page_size": 20,
            "passes": 2,
            "language": None,
            "publication_type_facet": None,
            "access_filter": None,
            "controlled_vocabulary": None,
            "proximity": False,
            "pair_expansion": False,
            "population_wildcards": [candidate for _terms, candidate in WILDCARD_REPLACEMENTS],
            "native_ris": (
                "Every first-pass source page is exported through Wiley's visible "
                "page-scoped RIS-with-abstracts flow and reconciled one-to-one and in order."
            ),
            "raw_ris_persistence": False,
            "screenshots": "configured Advanced Search and hydrated first results page",
        },
        "adapter": {
            "id": "search_wiley_online_library",
            "version": ADAPTER_VERSION,
            "sha256": file_sha256(ADAPTER_PATH),
            "required_interfaces": [
                "open_authorized_wiley_attached_page",
                "collect_wiley_results",
                "reconcile_ris_batch",
                "configure_wiley_advanced_search_for_screenshot",
                "_capture_wiley_full_page_screenshot_payload",
                "_publish_wiley_screenshot_bundle",
            ],
        },
        "dependencies": {
            "accepted_pilot004_query_module": {
                "path": str(PILOT004_QUERY_PATH.relative_to(REPOSITORY_ROOT)),
                "sha256": PILOT004_QUERY_SHA256,
            },
            "source_affecting_scripts": {
                str(path.relative_to(REPOSITORY_ROOT)): file_sha256(path)
                for path in SOURCE_SCRIPTS
            },
        },
        "authorization": {
            "mode": "exact caller-authorized Wiley target",
            "target_id_persisted": False,
            "owned_page_per_attempt": True,
            "user_target_navigated_or_closed": False,
        },
        "acceptance_checks": [
            "All ten predeclared source cells complete from fresh page-zero state.",
            "A2-mh and A2-mb both complete and form the adopted lossless A2 union.",
            "B2 and BT2 complete across every native result page.",
            "Each event has two equal complete ordered DOI passes and a stable source total.",
            "Every source DOI has exactly one first-pass normalized native RIS record in the same order.",
            "Every native RIS page batch reconciles its record count and DOI order to that rendered page.",
            "Every source record receives included, excluded, or unresolved exact-date accounting from visible First published evidence.",
            "Every event saves and hashes both mandatory sibling screenshots.",
            "No prior pilot state, source limit, language limit, type facet, access filter, Subject term, proximity operator, or pair expansion is used.",
        ],
        "stop_rules": [
            "Retry only a fresh isolated source-total or ordered-ID snapshot change, up to two attempts.",
            "Stop on access, challenge, query, control, card, RIS, DOI, date, screenshot, output, or cleanup failure.",
            "A failed attempt contributes no DOI, record, count, screenshot, or native export to a successful event.",
            "Never overwrite an event, screenshot, failure receipt, assessment, or validation report.",
        ],
        "conditional_future_pilots": {
            "additional_wildcards": {
                "active": False,
                "trigger": "More than the three accepted wildcard atoms are proposed.",
            },
            "controlled_vocabulary": {
                "active": False,
                "trigger": "A Wiley Subject descriptor is proposed as a free-text supplement.",
            },
        },
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
    if payload.get("event_schema_version") != EVENT_SCHEMA:
        errors.append("Event schema changed")
    if payload.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("Protocol commit changed")
    adapter = payload.get("adapter")
    if not isinstance(adapter, Mapping) or adapter.get("version") != ADAPTER_VERSION:
        errors.append("Adapter declaration changed")
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != len(ADOPTED_EVENTS):
        return [*errors, "Plan must contain ten source events"]
    if [item.get("event_id") for item in events] != [
        item["event_id"] for item in ADOPTED_EVENTS
    ]:
        errors.append("Event order or identity changed")
    expected_by_id = {item["event_id"]: item for item in ADOPTED_EVENTS}
    for event in events:
        event_id = event.get("event_id")
        expected = expected_by_id.get(event_id)
        query = event.get("query")
        if expected is None or query != expected["query"]:
            errors.append(f"Adopted query changed for {event_id}")
            continue
        if event.get("query_characters") != len(query) or event.get(
            "query_sha256"
        ) != text_sha256(query):
            errors.append(f"Query receipt changed for {event_id}")
        if event.get("passes") != 2 or event.get("native_ris") != (
            "visible page scoped export with abstracts"
        ):
            errors.append(f"Native two-pass contract changed for {event_id}")
        if event.get("date_start") != DATE_START or event.get("date_end") != DATE_END:
            errors.append(f"Date window changed for {event_id}")
        if event.get("screenshots") != screenshot_names(str(event.get("output"))):
            errors.append(f"Screenshot paths changed for {event_id}")
        if event.get("diagnostic_only") is not True or event.get("do_not_merge") is not True:
            errors.append(f"Diagnostic boundary changed for {event_id}")
    return errors


def write_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
