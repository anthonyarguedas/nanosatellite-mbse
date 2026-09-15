#!/usr/bin/env python3
"""Build the predeclared OATD Pilot 006 card-ID union plan."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import queries

SCHEMA = "oatd-pilot-006-card-id-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/006"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/event-plan.json"
PILOT005_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/005"
PILOT004_CHECKPOINT = (
    SLR1_ROOT
    / "source-specific/oatd/pilots/004/searches/checkpoint/P-shared.checkpoint.json"
)
PILOT005_EVIDENCE = {
    "plan": PILOT005_ROOT / "searches/split-continuation-plan.json",
    "run": PILOT005_ROOT / "searches/split-continuation-run-receipt.json",
    "assessment": PILOT005_ROOT / "searches/assessment.json",
    "validation": PILOT005_ROOT / "searches/validation-report.json",
}
ADAPTER_ROOT = Path.home() / "agent-tools"
ADAPTER_PATH = ADAPTER_ROOT / "internet/skills/browser/scripts/search_oatd.py"
ADAPTER_FILES = {
    "entrypoint": ADAPTER_PATH,
    "browser_helpers": ADAPTER_PATH.with_name("_browser_search_utils.py"),
    "output_loader": ADAPTER_PATH.with_name("_output_utils.py"),
    "output_implementation": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_output_utils.py"
    ),
    "merge_contract": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_merge_contract.py"
    ),
}
SOURCE_AFFECTING_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "build_plan.py",
    SCRIPT_DIR / "run_pilot.py",
)
MINIMUM_COOLDOWN_SECONDS = 1800


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise RuntimeError("A source timestamp lacked a timezone")
    return parsed.astimezone(timezone.utc)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPOSITORY_ROOT.resolve()))


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "oatd_pilot006_plan_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build() -> dict[str, Any]:
    adapter = load_adapter()
    if adapter.ADAPTER_ID != "search_oatd" or adapter.ADAPTER_VERSION != "10":
        raise RuntimeError("OATD Pilot 006 requires adapter v10")
    pilot005_run = load(PILOT005_EVIDENCE["run"])
    validation = load(PILOT005_EVIDENCE["validation"])
    checkpoint = load(PILOT004_CHECKPOINT)
    if (
        pilot005_run.get("success") is not True
        or pilot005_run.get("completed_gate_count") != 8
        or validation.get("status") != "valid"
        or validation.get("counts") != queries.EXPECTED_PILOT005_COUNTS
        or len(checkpoint.get("completed_ids", [])) != 338
    ):
        raise RuntimeError("The prerequisite OATD pilot evidence changed")
    not_before = parse_utc(pilot005_run["completed_at_utc"]) + timedelta(
        seconds=MINIMUM_COOLDOWN_SECONDS
    )

    events: list[dict[str, Any]] = []
    for event_id, query in queries.GATE_QUERIES.items():
        configuration = adapter.build_oatd_search_configuration(
            query,
            language="English",
            year_start=2011,
            year_end=2026,
            page_size=30,
        )
        route = adapter.build_search_url(query, configuration=configuration)
        output = f"searches/gates/{event_id}.json"
        output_path = Path(output)
        events.append(
            {
                "event_id": event_id,
                "purpose": (
                    "Collect two complete source-rendered card-ID snapshots for one "
                    "exact candidate-union gate without opening Record Details."
                ),
                "query": query,
                "query_characters": len(query),
                "query_sha256": text_digest(query),
                "effective_query": configuration.effective_query,
                "effective_query_sha256": text_digest(configuration.effective_query),
                "navigation_route_characters": len(route),
                "expected_count_from_pilot005": queries.EXPECTED_PILOT005_COUNTS[
                    event_id
                ],
                "language": "English",
                "language_source_value": "(en OR eng OR english)",
                "year_start": 2011,
                "year_end": 2026,
                "diagnostic_exact_cutoff": "2026-08-29",
                "page_size": 30,
                "limit": 100,
                "max_pages": 4,
                "timeout_seconds": 180.0,
                "page_delay_seconds": 6.0,
                "pass_delay_seconds": 60.0,
                "busy_retries": 1,
                "busy_retry_delay_seconds": 120.0,
                "output": output,
                "failure_output": f"searches/failures/{event_id}.json",
                "screenshots": {
                    "search_page": str(
                        output_path.with_name(f"{event_id}.search-page.png")
                    ),
                    "results_page": str(
                        output_path.with_name(f"{event_id}.results-page.png")
                    ),
                },
                "do_not_merge": True,
            }
        )
    if any(
        event["navigation_route_characters"] > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS
        for event in events
    ):
        raise RuntimeError("An OATD Pilot 006 route exceeds the adapter ceiling")

    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "platform": "OATD",
        "pilot": "006",
        "created_at_utc": now(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Determine the exact deduplicated stable-ID union of the eight accepted "
            "OATD candidate gates before any candidate detail hydration."
        ),
        "algebraic_candidate_union": {
            "identity": queries.ALGEBRAIC_IDENTITY,
            "relationship_to_original_schedule": "exact_union_equality",
            "partition_branch_coverage": {
                key: list(value)
                for key, value in queries.PARTITION_BRANCH_COVERAGE.items()
            },
        },
        "pilot005_evidence": {
            key: {"path": relative(path), "sha256": digest(path)}
            for key, path in PILOT005_EVIDENCE.items()
        },
        "pilot004_checkpoint": {
            "path": relative(PILOT004_CHECKPOINT),
            "sha256": digest(PILOT004_CHECKPOINT),
            "completed_records": 338,
            "reuse_is_not_approved_by_this_plan": True,
        },
        "source_safety": {
            "minimum_cooldown_after_pilot005_seconds": MINIMUM_COOLDOWN_SECONDS,
            "first_source_request_not_before_utc": not_before.isoformat().replace(
                "+00:00", "Z"
            ),
            "pass_delay_seconds": 60.0,
            "inter_gate_delay_seconds": 120.0,
            "page_delay_seconds": 6.0,
            "stop_after_first_failure": True,
            "record_details_requested": False,
            "maximum_gate_total": 100,
            "maximum_pages_per_pass": 4,
            "two_complete_passes_per_gate": True,
            "adapter_busy_retry_scope": "one explicit busy response after 120 seconds",
            "http_504_retry": False,
        },
        "output_contract": {
            "gate_schema": "oatd-pilot-006-card-id-gate/v1",
            "terminal_marker_schema": "oatd-pilot-006-card-id-gate-commit/v1",
            "reconciliation_schema": "oatd-pilot-006-card-id-reconciliation/v1",
            "public_card_fields": ["rank", "paperId", "title"],
            "query_urls_persisted": False,
            "record_detail_parameters_persisted": False,
            "cookies_or_browser_targets_persisted": False,
        },
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
            "files": {
                name: {
                    "path": f"~/agent-tools/{path.relative_to(ADAPTER_ROOT)}",
                    "sha256": digest(path),
                }
                for name, path in ADAPTER_FILES.items()
            },
        },
        "source_affecting_scripts": {
            relative(path): digest(path) for path in SOURCE_AFFECTING_SCRIPTS
        },
        "acceptance_checks": [
            "Every gate has two complete source-rendered card-ID passes.",
            "Each gate has equal stable-ID sets across its two passes.",
            "Every gate has exact query and shared-control readback.",
            "No Record Details page is requested.",
            "Each gate has a configured-search and verified-results screenshot.",
            "Each gate JSON and both screenshots are bound by a terminal marker.",
            "The cross-gate union preserves gate membership and source rank.",
            "A failed gate leaves the exact candidate union null.",
        ],
        "reconciliation_output": "searches/reconciliation.json",
        "event_count": len(events),
        "events": events,
    }


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    plan = build()
    write_new(args.output, plan)
    print(
        json.dumps({"saved": str(args.output), "events": len(plan["events"])}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
