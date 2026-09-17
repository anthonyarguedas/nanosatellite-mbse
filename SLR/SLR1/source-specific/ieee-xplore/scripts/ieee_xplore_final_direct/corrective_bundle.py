#!/usr/bin/env python3
"""Complete the unresolved IEEE final partitions and assemble one source bundle."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
REPOSITORY_ROOT = SCRIPT_PATH.parents[6]
CORE_PATH = SCRIPT_DIR / "run.py"
CORRECTIVE_SHARED_PATH = SCRIPT_DIR / "corrective_shared.py"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/ieee-xplore/scripts/ieee_xplore_pilot005/queries.py"
SOURCE_GUIDELINE = REPOSITORY_ROOT / "SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md"
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-bundle-plan/v1"
RUN_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-bundle-run/v1"
ASSESSMENT_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-bundle-assessment/v1"

SOURCE = "IEEE Xplore"
SOURCE_ID = "ieee_xplore"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
REUSED_PARTITIONS = ("A1", "A3", "BG2", "BT2")
PENDING_PARTITIONS = ("A2", "B1", "B2", "BG1", "BC1")
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
SEQUENCE = 5
DEFAULT_SETTLE_SECONDS = 90.0

PREDECESSOR_ROOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/ieee-xplore/final-searches/corrective-004"
PREDECESSOR_PLAN = PREDECESSOR_ROOT / "final-event-plan.json"
PREDECESSOR_RECEIPT = PREDECESSOR_ROOT / "run-receipt.json"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module("ieee_final_core_bundle", CORE_PATH)
CORRECTIVE_SHARED = load_module("ieee_final_shared_bundle", CORRECTIVE_SHARED_PATH)
SUMMARY = CORRECTIVE_SHARED.CORRECTIVE2.compact_artifact_summary


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return CORE.digest(path)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def relative(path: Path) -> str:
    return CORE.relative(path)


def load(path: Path) -> dict[str, Any]:
    return CORE.load(path)


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise FileExistsError(f"Refusing to overwrite {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        CORE_PATH,
        CORRECTIVE_SHARED_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {relative(path): digest(path) for path in paths}


def predecessor() -> tuple[dict[str, Any], dict[str, Any]]:
    if not PREDECESSOR_PLAN.is_file() or PREDECESSOR_PLAN.is_symlink():
        raise RuntimeError("The card-hydration final plan is unavailable")
    if not PREDECESSOR_RECEIPT.is_file() or PREDECESSOR_RECEIPT.is_symlink():
        raise RuntimeError("The card-hydration final receipt is unavailable")
    plan = load(PREDECESSOR_PLAN)
    receipt = load(PREDECESSOR_RECEIPT)
    if (
        plan.get("schema_version") != "slr1-ieee-xplore-final-direct-corrective-hydration-plan/v1"
        or receipt.get("schema_version") != "slr1-ieee-xplore-final-direct-corrective-hydration-run/v1"
        or receipt.get("plan_sha256") != digest(PREDECESSOR_PLAN)
        or receipt.get("success") is not False
        or receipt.get("accepted_event_count") != len(REUSED_PARTITIONS)
        or receipt.get("all_partitions_attempted") is not True
    ):
        raise RuntimeError("The card-hydration campaign is not the expected partial final run")
    return plan, receipt


def reused_artifacts(plan: Mapping[str, Any], receipt: Mapping[str, Any]) -> list[dict[str, Any]]:
    outcomes = {
        outcome.get("partition_id"): outcome
        for outcome in receipt.get("outcomes", [])
        if isinstance(outcome, Mapping)
    }
    events = {
        event.get("partition_id"): event
        for event in plan.get("events", [])
        if isinstance(event, Mapping)
    }
    rows: list[dict[str, Any]] = []
    for partition in REUSED_PARTITIONS:
        event = events.get(partition)
        outcome = outcomes.get(partition)
        if not isinstance(event, Mapping) or not isinstance(outcome, Mapping):
            raise RuntimeError(f"The successful {partition} event is unavailable")
        output = PREDECESSOR_ROOT / str(event.get("output_filename"))
        summary = SUMMARY(output, event, plan)
        if (
            outcome.get("success") is not True
            or summary.get("valid") is not True
            or outcome.get("artifact_sha256") != summary.get("artifact_sha256")
            or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
        ):
            raise RuntimeError(f"The successful {partition} artifact no longer validates")
        rows.append(
            {
                "partition_id": partition,
                "event_id": event["event_id"],
                "artifact": relative(output),
                "artifact_sha256": summary["artifact_sha256"],
                "artifact_bytes": summary["artifact_bytes"],
                "source_total": summary["source_total"],
                "retained_record_count": summary["retained_record_count"],
                "full_abstract_count": summary["full_abstract_count"],
                "publication_type_counts": summary["publication_type_counts"],
            }
        )
    return rows


def build_plan() -> dict[str, Any]:
    prior_plan, prior_receipt = predecessor()
    reuse = reused_artifacts(prior_plan, prior_receipt)
    queries = CORE.load_queries()
    source_strategy_reference = prior_plan["strategy_reference"]
    source_strategy_version = prior_plan["repository_head_at_predeclaration"]
    events = []
    for partition in PENDING_PARTITIONS:
        event = CORE.plan_event(
            partition,
            queries.SCHEDULE[partition],
            SEQUENCE,
            source_strategy_version,
        )
        event["browser_execution"] = "attached_shared_cdp_owned_page"
        event["rendered_card_hydration"] = "content_visibility_and_aria_hidden_aware"
        events.append(event)
    base = CORE.build_plan()
    base.update(
        {
            "schema_version": PLAN_SCHEMA,
            "created_at_utc": now(),
            # The source union requires one scientific strategy linkage across
            # the reused and replacement final events.
            "repository_head_at_predeclaration": source_strategy_version,
            "execution_repository_head": CORE.repository_head(),
            "strategy_reference": source_strategy_reference,
            "events": events,
            "bindings": {"files": bindings()},
            "source_union_expected_partitions": list(PARTITIONS),
            "source_union_expected_sources": [SOURCE_ID],
            "execution_policy": {
                "one_source_execution_per_pending_partition": True,
                "reuse_only_valid_predeclared_prior_events": True,
                "continue_after_partition_failure": True,
                "attached_shared_cdp_owned_page_per_partition": True,
                "target_identifiers_retained": False,
                "inter_event_settle_seconds": DEFAULT_SETTLE_SECONDS,
                "retry_policy": "none_after_bundle_corrective_plan_execution_begins",
                "skip_full_abstracts": False,
                "publication_type_filter": None,
            },
            "corrective_bundle": {
                "sequence": SEQUENCE,
                "reason": (
                    "Four partitions completed under the prior v13 card-hydration plan. "
                    "This plan reruns only its five nonmergeable partitions. Adapter v14 "
                    "treats IEEE aria-hidden offscreen cards as source rows because the "
                    "prior screenshots showed those cards as visibly rendered."
                ),
                "superseded_plan": relative(PREDECESSOR_PLAN),
                "superseded_plan_sha256": digest(PREDECESSOR_PLAN),
                "superseded_run_receipt": relative(PREDECESSOR_RECEIPT),
                "superseded_run_receipt_sha256": digest(PREDECESSOR_RECEIPT),
                "scientific_query_changed": False,
                "reused_partitions": list(REUSED_PARTITIONS),
                "pending_partitions": list(PENDING_PARTITIONS),
                "reused_artifacts": reuse,
                "adapter_repair": {
                    "prior_adapter_version": prior_plan["adapter"]["version"],
                    "prior_adapter_sha256": prior_plan["adapter"]["sha256"],
                    "repaired_behavior": (
                        "A connected IEEE result card is retained even when aria-hidden "
                        "marks it as offscreen for assistive technology."
                    ),
                    "focused_tests": {"test_count": 35, "status": "passed", "lint": "passed"},
                },
            },
        }
    )
    return base


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    prior_plan, prior_receipt = predecessor()
    reuse = reused_artifacts(prior_plan, prior_receipt)
    queries = CORE.load_queries()
    source_strategy_reference = prior_plan["strategy_reference"]
    source_strategy_version = prior_plan["repository_head_at_predeclaration"]
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != source_strategy_reference
        or plan.get("repository_head_at_predeclaration") != source_strategy_version
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("source_union_expected_sources") != [SOURCE_ID]
    ):
        errors.append("identity")
    window = plan.get("date_window", {})
    if (
        window.get("publication_date_start") != DATE_START
        or window.get("publication_date_end") != DATE_END
        or window.get("source_year_envelope") != "2011_2026_Year"
        or window.get("inclusive") is not True
    ):
        errors.append("date_window")
    configuration = plan.get("source_configuration", {})
    if (
        configuration.get("full_abstracts") is not True
        or configuration.get("abstracts", {}).get("normalized_field") != "abstract"
        or configuration.get("publication_types", {}).get("normalized_field") != "documentType"
        or configuration.get("publication_type_filter") is not None
        or configuration.get("language_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
    ):
        errors.append("capture_configuration")
    execution = plan.get("execution_policy", {})
    if (
        execution.get("one_source_execution_per_pending_partition") is not True
        or execution.get("reuse_only_valid_predeclared_prior_events") is not True
        or execution.get("attached_shared_cdp_owned_page_per_partition") is not True
        or execution.get("target_identifiers_retained") is not False
        or execution.get("inter_event_settle_seconds") != DEFAULT_SETTLE_SECONDS
        or execution.get("retry_policy") != "none_after_bundle_corrective_plan_execution_begins"
        or execution.get("skip_full_abstracts") is not False
        or execution.get("publication_type_filter") is not None
    ):
        errors.append("execution_policy")
    bundle = plan.get("corrective_bundle", {})
    if (
        bundle.get("sequence") != SEQUENCE
        or bundle.get("superseded_plan") != relative(PREDECESSOR_PLAN)
        or bundle.get("superseded_plan_sha256") != digest(PREDECESSOR_PLAN)
        or bundle.get("superseded_run_receipt") != relative(PREDECESSOR_RECEIPT)
        or bundle.get("superseded_run_receipt_sha256") != digest(PREDECESSOR_RECEIPT)
        or bundle.get("scientific_query_changed") is not False
        or bundle.get("reused_partitions") != list(REUSED_PARTITIONS)
        or bundle.get("pending_partitions") != list(PENDING_PARTITIONS)
        or bundle.get("reused_artifacts") != reuse
        or bundle.get("adapter_repair", {}).get("prior_adapter_version") != prior_plan["adapter"]["version"]
        or bundle.get("adapter_repair", {}).get("prior_adapter_sha256") != prior_plan["adapter"]["sha256"]
        or bundle.get("adapter_repair", {}).get("focused_tests", {}).get("status") != "passed"
        or prior_receipt.get("success") is not False
    ):
        errors.append("corrective_provenance")
    events = plan.get("events")
    if not isinstance(events, list) or [
        event.get("partition_id") for event in events if isinstance(event, Mapping)
    ] != list(PENDING_PARTITIONS):
        return [*errors, "pending_partition_coverage"]
    for event in events:
        if not isinstance(event, Mapping):
            errors.append("malformed_event")
            continue
        partition = event.get("partition_id")
        if not isinstance(partition, str):
            errors.append("event_shape")
            continue
        expected = CORE.plan_event(partition, queries.SCHEDULE[partition], SEQUENCE, source_strategy_version)
        expected["browser_execution"] = "attached_shared_cdp_owned_page"
        expected["rendered_card_hydration"] = "content_visibility_and_aria_hidden_aware"
        if dict(event) != expected:
            errors.append(f"event_contract:{partition}")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        if (
            adapter.get("id") != "search_ieee_xplore"
            or adapter.get("version") != CORE.adapter_version()
            or adapter.get("sha256") != digest(ADAPTER)
        ):
            errors.append("adapter_changed")
        files = plan.get("bindings", {}).get("files")
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected in files.items():
                path = REPOSITORY_ROOT / str(name)
                if not path.is_file() or path.is_symlink() or digest(path) != expected:
                    errors.append(f"binding_changed:{name}")
    return errors


def final_command(event: Mapping[str, Any], output: Path, plan: Mapping[str, Any], cdp_url: str) -> list[str]:
    return [
        "uv", "run", str(ADAPTER), "--query", str(event["query"]),
        "--publication-date-start", DATE_START, "--publication-date-end", DATE_END,
        "--scope", "documents", "--access-scope", "all", "--sort", "Oldest",
        "--page-size", str(event["page_size"]), "--limit", str(event["limit"]),
        "--max-pages", str(event["max_pages"]), "--timeout", str(event["timeout_seconds"]),
        "--page-delay-seconds", str(event["page_delay_seconds"]),
        "--detail-delay-seconds", str(event["detail_delay_seconds"]),
        "--require-complete", "--cdp-url", cdp_url, "--output-path", str(output),
        "--prisma-run-id", str(event["event_id"]),
        "--prisma-review-id", str(plan["review_id"]),
        "--prisma-strategy-reference", str(plan["strategy_reference"]),
        "--prisma-strategy-version", str(event["strategy_version"]),
        "--prisma-phase", str(plan["phase"]), "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", str(event["partition_id"]),
        "--prisma-partition-label", str(event["partition_id"]),
        "--prisma-partition-description",
        f"IEEE Xplore bundle corrective final direct discovery partition {event['partition_id']}",
    ]


def output_paths_occupied(output: Path) -> bool:
    return any(path.exists() or path.is_symlink() for path in (output, CORE.marker_path(output), *CORE.screenshot_paths(output)))


def run_final(plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid IEEE bundle corrective plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The IEEE bundle output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("IEEE bundle execution requires a loopback CDP endpoint")
    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        if output_paths_occupied(output):
            raise FileExistsError(f"Refusing to overwrite {event['partition_id']}")
        stdout = stderr = ""
        exit_code: int | None = None
        try:
            completed = subprocess.run(final_command(event, output, plan, cdp_url), check=False, capture_output=True, text=True)
            stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
            summary = SUMMARY(output, event, plan)
        except Exception as error:
            summary = {"artifact_written": output.is_file() and not output.is_symlink(), "valid": False, "runner_failure": type(error).__name__}
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"], "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() and not output.is_symlink() else None,
            "exit_code": exit_code, "source_command_attempt_count": 1,
            "browser_execution": "attached_shared_cdp_owned_page", "target_identifier_retained": False,
            "stdout_sha256": digest_text(stdout), "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": digest_text(stderr), "stderr_bytes": len(stderr.encode("utf-8")),
            **summary,
        }
        outcomes.append(outcome)
        print(json.dumps({
            "partition": event["partition_id"], "success": success, "exit_code": exit_code,
            "source_total": outcome.get("source_total"), "retained_records": outcome.get("retained_record_count"),
            "full_abstracts": outcome.get("full_abstract_count"),
            "missing_publication_types": outcome.get("missing_publication_type_count"),
            "error_stage": outcome.get("error_stage"),
        }), flush=True)
    success = len(outcomes) == len(plan["events"]) and all(item.get("success") is True for item in outcomes)
    receipt = {
        "schema_version": RUN_SCHEMA, "source": SOURCE, "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE, "event_kind": "final_corrective_bundle",
        "plan": relative(plan_path), "plan_sha256": digest(plan_path), "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"], "target_identifier_retained": False,
        "started_at_utc": started, "completed_at_utc": now(),
        "planned_pending_partition_count": len(plan["events"]), "attempted_pending_partition_count": len(outcomes),
        "source_command_attempt_count": len(outcomes),
        "accepted_pending_event_count": sum(item.get("success") is True for item in outcomes),
        "all_pending_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success, "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def campaign_artifacts(plan: Mapping[str, Any], output_dir: Path) -> list[tuple[str, Path, Mapping[str, Any], Mapping[str, Any]]]:
    prior_plan, prior_receipt = predecessor()
    prior_events = {event["partition_id"]: event for event in prior_plan["events"]}
    result: list[tuple[str, Path, Mapping[str, Any], Mapping[str, Any]]] = []
    for partition in PARTITIONS:
        if partition in REUSED_PARTITIONS:
            event = prior_events[partition]
            path = PREDECESSOR_ROOT / str(event["output_filename"])
            result.append((partition, path, event, prior_plan))
        else:
            event = next(item for item in plan["events"] if item["partition_id"] == partition)
            result.append((partition, output_dir / str(event["output_filename"]), event, plan))
    return result


def assess(plan_path: Path, receipt_path: Path, output_dir: Path, union_path: Path, assessment_path: Path) -> int:
    if assessment_path.exists() or assessment_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {assessment_path}")
    plan, run = load(plan_path), load(receipt_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_pending_event_count") != len(PENDING_PARTITIONS)
    ):
        errors.append("run_receipt")
    outcomes = {row.get("partition_id"): row for row in run.get("outcomes", []) if isinstance(row, Mapping)}
    partitions: list[dict[str, Any]] = []
    source_total = retained = excluded = unresolved = full = unavailable = 0
    all_ids: set[str] = set()
    types: dict[str, int] = {}
    input_paths: list[Path] = []
    for partition, path, event, event_plan in campaign_artifacts(plan, output_dir):
        summary = SUMMARY(path, event, event_plan)
        if summary.get("valid") is not True:
            errors.append(f"artifact:{partition}")
        if partition in PENDING_PARTITIONS:
            outcome = outcomes.get(partition)
            if outcome is None or outcome.get("success") is not True:
                errors.append(f"event:{partition}")
            elif (
                outcome.get("artifact_sha256") != summary.get("artifact_sha256")
                or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
            ):
                errors.append(f"artifact_binding:{partition}")
        event_total, event_retained, event_excluded = summary.get("source_total"), summary.get("retained_record_count"), summary.get("client_date_excluded_count")
        if not all(isinstance(item, int) and item >= 0 for item in (event_total, event_retained, event_excluded)):
            errors.append(f"count_shape:{partition}")
        elif event_total != event_retained + event_excluded:
            errors.append(f"date_accounting:{partition}")
        source_total += event_total if isinstance(event_total, int) else 0
        retained += event_retained if isinstance(event_retained, int) else 0
        excluded += event_excluded if isinstance(event_excluded, int) else 0
        unresolved += summary.get("unresolved_exact_date_count", 0)
        full += summary.get("full_abstract_count", 0)
        unavailable += summary.get("source_abstract_not_available_count", 0)
        for publication_type, count in summary.get("publication_type_counts", {}).items():
            if isinstance(publication_type, str) and isinstance(count, int):
                types[publication_type] = types.get(publication_type, 0) + count
        if path.is_file() and not path.is_symlink():
            for row in load(path).get("results", []):
                if isinstance(row, Mapping) and isinstance(row.get("paperId"), str):
                    all_ids.add(row["paperId"])
        input_paths.append(path)
        partitions.append({"partition_id": partition, "artifact": relative(path), "reused": partition in REUSED_PARTITIONS, **summary})
    union_valid = False
    union_attempt: dict[str, Any] | None = None
    if not errors:
        if union_path.exists() or union_path.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {union_path}")
        command = [
            "uv", "run", str(CORE.SOURCE_UNION_TOOL), "--input", *[str(path) for path in input_paths],
            "--output-path", str(union_path), "--expected-partitions", *PARTITIONS,
            "--expected-source", SOURCE_ID, "--review-namespace", REVIEW_NAMESPACE,
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        union_valid = bool(completed.returncode == 0 and union_path.is_file() and not union_path.is_symlink())
        if union_valid:
            union = load(union_path)
            union_valid = bool(
                union.get("schema_version") == "academic-search-source-union-receipt/v1"
                and union.get("review_namespace") == REVIEW_NAMESPACE
                and union.get("expected_partitions") == list(PARTITIONS)
                and union.get("expected_sources") == [SOURCE_ID]
                and union.get("completeness_status") == "complete"
                and union.get("failure_status") == "none"
            )
        union_attempt = {
            "return_code": completed.returncode,
            "stdout_sha256": digest_text(completed.stdout),
            "stdout_bytes": len(completed.stdout.encode("utf-8")),
            "stderr_sha256": digest_text(completed.stderr),
            "stderr_bytes": len(completed.stderr.encode("utf-8")),
            "output_written": union_path.is_file() and not union_path.is_symlink(),
        }
        if not union_valid:
            errors.append("source_union_receipt")
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA, "status": "passed" if not errors else "failed",
        "source": SOURCE, "source_id": SOURCE_ID, "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(plan_path), "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path), "run_receipt_sha256": digest(receipt_path),
        "adapter": plan["adapter"], "date_window": plan["date_window"],
        "corrective_bundle": plan["corrective_bundle"], "partition_count": len(partitions),
        "accepted_partition_count": sum(row.get("valid") is True for row in partitions),
        "source_total_occurrence_count": source_total, "retained_record_occurrence_count": retained,
        "client_date_excluded_occurrence_count": excluded,
        "unresolved_exact_date_occurrence_count": unresolved,
        "unique_retained_source_record_count": len(all_ids),
        "unique_retained_source_record_id_set_sha256": CORE.digest_ids(all_ids),
        "full_abstract_occurrence_count": full,
        "source_abstract_not_available_occurrence_count": unavailable,
        "publication_type_occurrence_counts": dict(sorted(types.items())),
        "publication_type_field_complete": all(row.get("all_retained_rows_have_publication_type") is True for row in partitions),
        "detail_capture_complete": all(row.get("record_capture_valid") is True for row in partitions),
        "source_union_receipt": relative(union_path) if union_valid and union_path.is_file() else None,
        "source_union_receipt_sha256": digest(union_path) if union_valid and union_path.is_file() else None,
        "source_union_valid": union_valid, "source_union_attempt": union_attempt,
        "partitions": partitions, "validation_errors": errors, "completed_at_utc": now(),
    }
    write_new(assessment_path, assessment)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-plan")
    build.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--verify-bindings", action="store_true")
    run = commands.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)
    run.add_argument("--settle-seconds", type=float, default=DEFAULT_SETTLE_SECONDS)
    assess_parser = commands.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--source-union", type=Path, required=True)
    assess_parser.add_argument("--assessment", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan()
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError("Generated an invalid IEEE bundle plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"]), "reused": len(REUSED_PARTITIONS)}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        if args.settle_seconds < 0:
            raise ValueError("--settle-seconds cannot be negative")
        return run_final(args.plan, args.output_dir, args.receipt, args.settle_seconds)
    if args.command == "assess":
        return assess(args.plan, args.receipt, args.output_dir, args.source_union, args.assessment)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
