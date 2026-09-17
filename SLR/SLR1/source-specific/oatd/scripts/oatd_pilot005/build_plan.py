#!/usr/bin/env python3
"""Build the predeclared OATD Pilot 005 five-gate count plan."""

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

SCHEMA = "oatd-pilot-005-gate-count-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/005"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/event-plan.json"
PILOT004_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/004"
FAILURE_RECEIPT = (
    PILOT004_ROOT / "searches/run-receipt.resource-url-repair.record-252.json"
)
P_CHECKPOINT = PILOT004_ROOT / "searches/checkpoint/P-shared.checkpoint.json"
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
BASELINE_TOTAL = 1249
MINIMUM_COOLDOWN_SECONDS = 1800
INTER_EVENT_DELAY_SECONDS = 120.0


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise RuntimeError("A source timestamp lacked a timezone")
    return parsed.astimezone(timezone.utc)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPOSITORY_ROOT.resolve()))


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "oatd_pilot005_plan_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    return {
        "search_page": str(path.with_name(f"{path.stem}.search-page.png")),
        "results_page": str(path.with_name(f"{path.stem}.results-page.png")),
    }


def build() -> dict[str, Any]:
    adapter = load_adapter()
    if adapter.ADAPTER_ID != "search_oatd" or adapter.ADAPTER_VERSION != "10":
        raise RuntimeError("OATD Pilot 005 requires adapter v10")
    failure = load(FAILURE_RECEIPT)
    checkpoint = load(P_CHECKPOINT)
    source = checkpoint.get("source_population")
    completed_ids = checkpoint.get("completed_ids")
    if (
        failure.get("status") != "stopped_on_source_or_adapter_failure"
        or not isinstance(source, dict)
        or source.get("source_reported_total") != BASELINE_TOTAL
        or not isinstance(completed_ids, list)
        or len(completed_ids) != 338
    ):
        raise RuntimeError("The Pilot 004 baseline evidence changed")
    failure_completed = parse_utc(failure["completed_at_utc"])
    source_not_before = failure_completed + timedelta(seconds=MINIMUM_COOLDOWN_SECONDS)

    events: list[dict[str, Any]] = []
    for gate_id, query in queries.GATE_QUERIES.items():
        configuration = adapter.build_oatd_search_configuration(
            query,
            language="English",
            year_start=2011,
            year_end=2026,
            page_size=30,
        )
        route = adapter.build_search_url(query, configuration=configuration)
        output = f"searches/{gate_id}.json"
        if len(route) > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS:
            raise RuntimeError(f"{gate_id} exceeds the OATD navigation ceiling")
        events.append(
            {
                "event_id": gate_id,
                "purpose": "Observe the exact count for one algebraic candidate-union gate.",
                "query": query,
                "query_characters": len(query),
                "query_sha256": text_digest(query),
                "effective_query": configuration.effective_query,
                "effective_query_sha256": text_digest(configuration.effective_query),
                "navigation_route_characters": len(route),
                "language": "English",
                "language_source_value": "(en OR eng OR english)",
                "year_start": 2011,
                "year_end": 2026,
                "diagnostic_exact_cutoff": "2026-08-29",
                "page_size": 30,
                "limit": 1,
                "max_pages": 1,
                "timeout_seconds": 180,
                "page_delay_seconds": 0.0,
                "detail_delay_seconds": 0.0,
                "busy_retries": 1,
                "busy_retry_delay_seconds": 120.0,
                "count_only": True,
                "output": output,
                "screenshots": screenshot_names(output),
                "do_not_merge": True,
            }
        )

    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "platform": "OATD",
        "pilot": "005",
        "created_at_utc": now(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Test five exact P-and-concept gates by count only before replacing "
            "the fragile P-only detail harvest."
        ),
        "algebraic_candidate_union": {
            "identity": queries.ALGEBRAIC_IDENTITY,
            "relationship_to_original_schedule": "exact_union_equality",
            "partition_branch_coverage": {
                key: list(value)
                for key, value in queries.PARTITION_BRANCH_COVERAGE.items()
            },
            "wildcards": False,
            "proximity": False,
            "new_terms": False,
            "source_refinement_from_results": False,
        },
        "pilot004_baseline": {
            "source_reported_total": BASELINE_TOTAL,
            "stable_record_ids_sha256": source.get("stable_record_ids_sha256"),
            "completed_detail_records": len(completed_ids),
            "failure_receipt": {
                "path": relative(FAILURE_RECEIPT),
                "sha256": digest(FAILURE_RECEIPT),
                "completed_at_utc": failure["completed_at_utc"],
                "reported_failure": "HTTP 504 without a ready source state",
            },
            "checkpoint": {
                "path": relative(P_CHECKPOINT),
                "sha256": digest(P_CHECKPOINT),
            },
        },
        "source_safety": {
            "source_requests": "count_only_no_detail_pages",
            "minimum_cooldown_after_pilot004_failure_seconds": MINIMUM_COOLDOWN_SECONDS,
            "first_source_request_not_before_utc": source_not_before.isoformat().replace(
                "+00:00", "Z"
            ),
            "inter_event_delay_seconds": INTER_EVENT_DELAY_SECONDS,
            "stop_after_first_failed_event": True,
            "runner_level_retries": 0,
            "adapter_busy_retry_scope": "one explicit busy response after 120 seconds",
            "http_504_retry": False,
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
            "mandatory_automatic_screenshots": True,
            "screenshot_opt_out": False,
        },
        "source_affecting_scripts": {
            relative(path): digest(path) for path in SOURCE_AFFECTING_SCRIPTS
        },
        "acceptance_checks": [
            "Each successful event has exact rendered query readback.",
            "Each successful event is count only and opens no detail page.",
            "Each successful gate total is a nonnegative integer below 1249.",
            "Each successful artifact remains nonmergeable.",
            "Each successful artifact has both mandatory screenshots and a valid marker.",
            "The five queries retain every original literal and Boolean branch needed for exact union equality.",
        ],
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
