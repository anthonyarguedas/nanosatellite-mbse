#!/usr/bin/env python3
"""Build the predeclared OATD Pilot 007 hydration plan."""

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

SCHEMA = "oatd-pilot-007-hydration-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[1]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/007"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/event-plan.json"
PILOT006_ROOT = SLR1_ROOT / "source-specific/oatd/pilots/006"
PILOT006_EVIDENCE = {
    "plan": PILOT006_ROOT / "searches/event-plan.json",
    "run": PILOT006_ROOT / "searches/run-receipt.json",
    "reconciliation": PILOT006_ROOT / "searches/reconciliation.json",
    "assessment": PILOT006_ROOT / "searches/assessment.json",
    "validation": PILOT006_ROOT / "searches/validation-report.json",
}
PILOT004_LOCAL_PLAN = (
    SLR1_ROOT / "source-specific/oatd/pilots/004/searches/local-matching-plan.json"
)
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
        "oatd_pilot007_plan_adapter", ADAPTER_PATH
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
        raise RuntimeError("OATD Pilot 007 requires adapter v10")
    evidence = {key: load(path) for key, path in PILOT006_EVIDENCE.items()}
    reconciliation = evidence["reconciliation"]
    if (
        evidence["run"].get("success") is not True
        or evidence["validation"].get("status") != "valid"
        or reconciliation.get("exact_deduplicated_union_total") != 26
        or len(reconciliation.get("records", [])) != 26
    ):
        raise RuntimeError("The prerequisite OATD Pilot 006 evidence changed")
    local_plan = adapter.load_local_matching_plan(PILOT004_LOCAL_PLAN)
    not_before = parse_utc(evidence["run"]["completed_at_utc"]) + timedelta(
        seconds=MINIMUM_COOLDOWN_SECONDS
    )
    pilot006_plan = evidence["plan"]
    pilot006_events = {event["event_id"]: event for event in pilot006_plan["events"]}
    pilot006_outcomes = {
        outcome["event_id"]: outcome for outcome in evidence["run"]["outcomes"]
    }

    events: list[dict[str, Any]] = []
    for event_id, query in queries.GATE_QUERIES.items():
        prior_event = pilot006_events[event_id]
        prior_outcome = pilot006_outcomes[event_id]
        prior_artifact_path = PILOT006_ROOT / prior_outcome["artifact"]
        prior_artifact = load(prior_artifact_path)
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
                    "Obtain an initial stable-ID snapshot and a post-hydration "
                    "confirming snapshot for one exact OATD gate."
                ),
                "query": query,
                "query_characters": len(query),
                "query_sha256": text_digest(query),
                "effective_query": configuration.effective_query,
                "effective_query_sha256": text_digest(configuration.effective_query),
                "navigation_route_characters": len(route),
                "expected_source_total": queries.EXPECTED_COUNTS[event_id],
                "expected_stable_record_ids_sha256": prior_artifact["first_pass"][
                    "stable_record_ids_sha256"
                ],
                "pilot006_gate_artifact": {
                    "path": relative(prior_artifact_path),
                    "sha256": digest(prior_artifact_path),
                },
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
                "busy_retries": 1,
                "busy_retry_delay_seconds": 120.0,
                "output": output,
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
        if (
            prior_event["query"] != query
            or len(route) > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS
        ):
            raise RuntimeError(f"The OATD Pilot 007 gate changed: {event_id}")

    return {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "platform": "OATD",
        "pilot": "007",
        "created_at_utc": now(),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Hydrate each of the 26 accepted stable OATD IDs once, checkpoint every "
            "record, and confirm all eight gate sets before pilot publication."
        ),
        "algebraic_candidate_union": {
            "identity": queries.ALGEBRAIC_IDENTITY,
            "relationship_to_original_schedule": "exact_union_equality",
            "partition_branch_coverage": {
                key: list(value)
                for key, value in queries.PARTITION_BRANCH_COVERAGE.items()
            },
        },
        "target_union": {
            "record_count": 26,
            "stable_record_ids_sha256": reconciliation["stable_union_ids_sha256"],
            "ordered_record_ids_sha256": reconciliation["ordered_union_ids_sha256"],
            "pilot006_gate_occurrences": 34,
        },
        "pilot006_evidence": {
            key: {"path": relative(path), "sha256": digest(path)}
            for key, path in PILOT006_EVIDENCE.items()
        },
        "local_matching_plan": {
            "path": relative(PILOT004_LOCAL_PLAN),
            "sha256": digest(PILOT004_LOCAL_PLAN),
            "schema_version": local_plan.schema_version,
            "matcher_version": local_plan.matcher_version,
            "plan_sha256": local_plan.plan_sha256,
        },
        "source_safety": {
            "minimum_cooldown_after_pilot006_seconds": MINIMUM_COOLDOWN_SECONDS,
            "first_source_request_not_before_utc": not_before.isoformat().replace(
                "+00:00", "Z"
            ),
            "search_timeout_seconds": 180.0,
            "inter_gate_delay_seconds": 120.0,
            "page_delay_seconds": 6.0,
            "pre_detail_delay_seconds": 180.0,
            "detail_timeout_seconds": 180.0,
            "detail_delay_seconds": 15.0,
            "detail_batch_size": 8,
            "detail_batch_cooldown_seconds": 180.0,
            "detail_busy_retries": 2,
            "detail_busy_retry_delay_seconds": 120.0,
            "pre_confirmation_delay_seconds": 300.0,
            "stop_after_first_failure": True,
            "pilot004_records_reused": 0,
            "record_details_requested_once_per_target": True,
            "http_504_retry": False,
        },
        "checkpoint_contract": {
            "schema_version": "oatd-pilot-007-hydration-checkpoint/v1",
            "path_free": True,
            "public_normalized_metadata_only": True,
            "write_after_each_completed_detail": True,
            "validate_every_record_before_resume_skip": True,
        },
        "output_contract": {
            "gate_schema": "oatd-pilot-007-confirmed-gate/v1",
            "gate_marker_schema": "oatd-pilot-007-confirmed-gate-commit/v1",
            "union_schema": "oatd-pilot-007-hydrated-union/v1",
            "union_marker_schema": "oatd-pilot-007-hydrated-union-commit/v1",
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
            "Every initial gate snapshot equals its accepted Pilot 006 stable-ID set.",
            "Every one of the 26 stable IDs has one validated normalized detail record.",
            "No Pilot 004 detail record is reused.",
            "Every checkpointed record is validated before a resume skip.",
            "Every confirming gate snapshot equals its initial stable-ID set.",
            "Every gate retains both mandatory screenshots and a terminal marker.",
            "The hydrated union retains gate provenance and removes no local negative.",
            "A source, detail, checkpoint, or confirmation failure leaves the union unpublished.",
        ],
        "checkpoint": "searches/checkpoint/hydrated-union.checkpoint.json",
        "union_output": "searches/hydrated-union.json",
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
    print(json.dumps({"saved": str(args.output), "events": 8, "records": 26}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
