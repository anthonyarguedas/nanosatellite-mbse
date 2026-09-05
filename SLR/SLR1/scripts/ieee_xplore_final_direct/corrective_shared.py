#!/usr/bin/env python3
"""Run the shared-browser corrective IEEE Xplore final-search campaign."""

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
REPOSITORY_ROOT = SCRIPT_PATH.parents[4]
CORE_PATH = SCRIPT_DIR / "run.py"
CORRECTIVE2_PATH = SCRIPT_DIR / "corrective.py"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/ieee_xplore_pilot005/queries.py"
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-shared-plan/v1"
RUN_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-shared-run/v1"
ASSESSMENT_SCHEMA = "slr1-ieee-xplore-final-direct-corrective-shared-assessment/v1"

SOURCE = "IEEE Xplore"
SOURCE_ID = "ieee_xplore"
REVIEW_ID = "slr1-1.1-restart"
REVIEW_NAMESPACE = "main"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-ieee-xplore-main-direct-v3"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
SEQUENCE = 3

PREDECESSOR_ROOT = (
    REPOSITORY_ROOT / "SLR/SLR1/source-specific/ieee-xplore/final-searches/corrective-002"
)
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


CORE = load_module("ieee_final_direct_core_shared", CORE_PATH)
CORRECTIVE2 = load_module("ieee_final_direct_corrective_two", CORRECTIVE2_PATH)


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
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
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
        CORRECTIVE2_PATH,
        QUERY_SNAPSHOT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    return {relative(path): digest(path) for path in paths}


def predecessor() -> tuple[dict[str, Any], dict[str, Any]]:
    if not PREDECESSOR_PLAN.is_file() or PREDECESSOR_PLAN.is_symlink():
        raise RuntimeError("The fresh-browser corrective plan is unavailable")
    if not PREDECESSOR_RECEIPT.is_file() or PREDECESSOR_RECEIPT.is_symlink():
        raise RuntimeError("The fresh-browser corrective receipt is unavailable")
    plan = load(PREDECESSOR_PLAN)
    receipt = load(PREDECESSOR_RECEIPT)
    if (
        plan.get("schema_version") != CORRECTIVE2.PLAN_SCHEMA
        or receipt.get("schema_version") != CORRECTIVE2.RUN_SCHEMA
        or receipt.get("plan_sha256") != digest(PREDECESSOR_PLAN)
        or receipt.get("success") is not False
        or receipt.get("all_partitions_attempted") is not True
        or receipt.get("accepted_event_count") != 0
    ):
        raise RuntimeError("The fresh-browser corrective run is not the expected failure")
    return plan, receipt


def build_plan() -> dict[str, Any]:
    prior_plan, _ = predecessor()
    queries = CORE.load_queries()
    strategy_version = CORE.repository_head()
    events = []
    for partition in PARTITIONS:
        event = CORE.plan_event(
            partition, queries.SCHEDULE[partition], SEQUENCE, strategy_version
        )
        event["browser_execution"] = "attached_shared_cdp_owned_page"
        events.append(event)
    base = CORE.build_plan()
    base.update(
        {
            "schema_version": PLAN_SCHEMA,
            "created_at_utc": now(),
            "repository_head_at_predeclaration": strategy_version,
            "strategy_reference": STRATEGY_REFERENCE,
            "events": events,
            "bindings": {"files": bindings()},
            "execution_policy": {
                "one_source_execution_per_partition": True,
                "continue_after_partition_failure": True,
                "attached_shared_cdp_owned_page_per_partition": True,
                "target_identifiers_retained": False,
                "retry_policy": "none_after_shared_browser_corrective_plan_execution_begins",
                "skip_full_abstracts": False,
                "publication_type_filter": None,
            },
            "corrective_run": {
                "sequence": SEQUENCE,
                "reason": (
                    "The repaired v12 adapter was exercised in nine fresh visible "
                    "browser processes. Every process reached query submission but "
                    "none observed a rendered source query echo. The shared browser "
                    "profile had completed the prior A1 source event, so this campaign "
                    "uses an adapter-owned page in that profile without a retained target ID."
                ),
                "superseded_plan": relative(PREDECESSOR_PLAN),
                "superseded_plan_sha256": digest(PREDECESSOR_PLAN),
                "superseded_run_receipt": relative(PREDECESSOR_RECEIPT),
                "superseded_run_receipt_sha256": digest(PREDECESSOR_RECEIPT),
                "scientific_query_changed": False,
                "adapter_changed": False,
                "browser_execution_changed": {
                    "from": "fresh_visible_browser",
                    "to": "attached_shared_cdp_owned_page",
                    "target_identifier_retained": False,
                },
                "retained_adapter": {
                    "version": prior_plan["adapter"]["version"],
                    "sha256": prior_plan["adapter"]["sha256"],
                },
            },
        }
    )
    return base


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    prior_plan, prior_receipt = predecessor()
    queries = CORE.load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
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
        or configuration.get("publication_types", {}).get("normalized_field")
        != "documentType"
        or configuration.get("publication_type_filter") is not None
        or configuration.get("language_filter") is not None
        or configuration.get("controlled_vocabulary_supplement") is not None
    ):
        errors.append("capture_configuration")
    execution = plan.get("execution_policy", {})
    if (
        execution.get("attached_shared_cdp_owned_page_per_partition") is not True
        or execution.get("target_identifiers_retained") is not False
        or execution.get("retry_policy")
        != "none_after_shared_browser_corrective_plan_execution_begins"
        or execution.get("skip_full_abstracts") is not False
        or execution.get("publication_type_filter") is not None
    ):
        errors.append("execution_policy")
    corrective = plan.get("corrective_run", {})
    if (
        corrective.get("sequence") != SEQUENCE
        or corrective.get("superseded_plan") != relative(PREDECESSOR_PLAN)
        or corrective.get("superseded_plan_sha256") != digest(PREDECESSOR_PLAN)
        or corrective.get("superseded_run_receipt") != relative(PREDECESSOR_RECEIPT)
        or corrective.get("superseded_run_receipt_sha256") != digest(PREDECESSOR_RECEIPT)
        or corrective.get("scientific_query_changed") is not False
        or corrective.get("adapter_changed") is not False
        or corrective.get("retained_adapter", {}).get("version")
        != prior_plan["adapter"]["version"]
        or corrective.get("retained_adapter", {}).get("sha256")
        != prior_plan["adapter"]["sha256"]
        or prior_receipt.get("success") is not False
    ):
        errors.append("corrective_provenance")
    strategy_version = plan.get("repository_head_at_predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or [
        event.get("partition_id") for event in events if isinstance(event, Mapping)
    ] != list(PARTITIONS):
        return [*errors, "partition_coverage"]
    for event in events:
        if not isinstance(event, Mapping):
            errors.append("malformed_event")
            continue
        partition = event.get("partition_id")
        if not isinstance(partition, str):
            errors.append("event_shape")
            continue
        expected = CORE.plan_event(
            partition, queries.SCHEDULE[partition], SEQUENCE, strategy_version
        )
        expected["browser_execution"] = "attached_shared_cdp_owned_page"
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
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
        "--publication-date-start",
        DATE_START,
        "--publication-date-end",
        DATE_END,
        "--scope",
        "documents",
        "--access-scope",
        "all",
        "--sort",
        "Oldest",
        "--page-size",
        str(event["page_size"]),
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--detail-delay-seconds",
        str(event["detail_delay_seconds"]),
        "--require-complete",
        "--cdp-url",
        cdp_url,
        "--output-path",
        str(output),
        "--prisma-run-id",
        str(event["event_id"]),
        "--prisma-review-id",
        str(plan["review_id"]),
        "--prisma-strategy-reference",
        str(plan["strategy_reference"]),
        "--prisma-strategy-version",
        str(event["strategy_version"]),
        "--prisma-phase",
        str(plan["phase"]),
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        str(event["partition_id"]),
        "--prisma-partition-label",
        str(event["partition_id"]),
        "--prisma-partition-description",
        f"IEEE Xplore shared-browser corrective final direct discovery partition {event['partition_id']}",
    ]


def output_paths_occupied(output: Path) -> bool:
    return any(
        path.exists() or path.is_symlink()
        for path in (output, CORE.marker_path(output), *CORE.screenshot_paths(output))
    )


def run_final(plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid shared-browser corrective IEEE plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The shared-browser corrective output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise ValueError("Shared-browser IEEE execution requires a loopback CDP endpoint")
    outcomes: list[dict[str, Any]] = []
    started = now()
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / str(event["output_filename"])
        if output_paths_occupied(output):
            raise FileExistsError(f"Refusing to overwrite {event['partition_id']}")
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                final_command(event, output, plan, cdp_url),
                check=False,
                capture_output=True,
                text=True,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            summary = CORRECTIVE2.compact_artifact_summary(output, event, plan)
        except Exception as error:
            summary = {
                "artifact_written": output.is_file() and not output.is_symlink(),
                "valid": False,
                "runner_failure": type(error).__name__,
            }
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() and not output.is_symlink() else None,
            "exit_code": exit_code,
            "source_command_attempt_count": 1,
            "browser_execution": "attached_shared_cdp_owned_page",
            "target_identifier_retained": False,
            "stdout_sha256": digest_text(stdout),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": digest_text(stderr),
            "stderr_bytes": len(stderr.encode("utf-8")),
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "source_total": outcome.get("source_total"),
                    "retained_records": outcome.get("retained_record_count"),
                    "full_abstracts": outcome.get("full_abstract_count"),
                    "missing_publication_types": outcome.get("missing_publication_type_count"),
                    "error_stage": outcome.get("error_stage"),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == len(plan["events"]) and all(
        outcome.get("success") is True for outcome in outcomes
    )
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final_corrective",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"],
        "target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": len(outcomes),
        "accepted_event_count": sum(outcome.get("success") is True for outcome in outcomes),
        "all_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def assess(plan_path: Path, receipt_path: Path, output_dir: Path, union_path: Path, assessment_path: Path) -> int:
    if assessment_path.exists() or assessment_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {assessment_path}")
    plan = load(plan_path)
    run = load(receipt_path)
    errors = validate_plan(plan, verify_bindings=True)
    if (
        run.get("schema_version") != RUN_SCHEMA
        or run.get("plan_sha256") != digest(plan_path)
        or run.get("success") is not True
        or run.get("accepted_event_count") != len(plan["events"])
    ):
        errors.append("run_receipt")
    outcomes = {
        row.get("event_id"): row
        for row in run.get("outcomes", [])
        if isinstance(row, Mapping)
    }
    partitions: list[dict[str, Any]] = []
    all_ids: set[str] = set()
    source_total = retained = excluded = unresolved = full_abstracts = unavailable = 0
    publication_types: dict[str, int] = {}
    for event in plan["events"]:
        output = output_dir / str(event["output_filename"])
        summary = CORRECTIVE2.compact_artifact_summary(output, event, plan)
        outcome = outcomes.get(event["event_id"])
        if outcome is None or outcome.get("success") is not True or summary.get("valid") is not True:
            errors.append(f"event:{event['partition_id']}")
        if outcome is not None and (
            outcome.get("artifact_sha256") != summary.get("artifact_sha256")
            or outcome.get("artifact_bytes") != summary.get("artifact_bytes")
        ):
            errors.append(f"artifact_binding:{event['partition_id']}")
        event_total = summary.get("source_total")
        event_retained = summary.get("retained_record_count")
        event_excluded = summary.get("client_date_excluded_count")
        if not all(isinstance(item, int) and item >= 0 for item in (event_total, event_retained, event_excluded)):
            errors.append(f"count_shape:{event['partition_id']}")
        elif event_total != event_retained + event_excluded:
            errors.append(f"date_accounting:{event['partition_id']}")
        source_total += event_total if isinstance(event_total, int) else 0
        retained += event_retained if isinstance(event_retained, int) else 0
        excluded += event_excluded if isinstance(event_excluded, int) else 0
        unresolved += summary.get("unresolved_exact_date_count", 0)
        full_abstracts += summary.get("full_abstract_count", 0)
        unavailable += summary.get("source_abstract_not_available_count", 0)
        for publication_type, count in summary.get("publication_type_counts", {}).items():
            if isinstance(publication_type, str) and isinstance(count, int):
                publication_types[publication_type] = publication_types.get(publication_type, 0) + count
        if output.is_file() and not output.is_symlink():
            for row in load(output).get("results", []):
                if isinstance(row, Mapping) and isinstance(row.get("paperId"), str):
                    all_ids.add(row["paperId"])
        partitions.append({"event_id": event["event_id"], "partition_id": event["partition_id"], "artifact": output.name, **summary})
    union_valid = False
    union_attempt: dict[str, Any] | None = None
    if not errors:
        union_valid, union_attempt = CORE.create_source_union(plan_path, output_dir, union_path)
        if not union_valid:
            errors.append("source_union_receipt")
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "adapter": plan["adapter"],
        "date_window": plan["date_window"],
        "corrective_run": plan["corrective_run"],
        "partition_count": len(partitions),
        "accepted_partition_count": sum(row.get("valid") is True for row in partitions),
        "source_total_occurrence_count": source_total,
        "retained_record_occurrence_count": retained,
        "client_date_excluded_occurrence_count": excluded,
        "unresolved_exact_date_occurrence_count": unresolved,
        "unique_retained_source_record_count": len(all_ids),
        "unique_retained_source_record_id_set_sha256": CORE.digest_ids(all_ids),
        "full_abstract_occurrence_count": full_abstracts,
        "source_abstract_not_available_occurrence_count": unavailable,
        "publication_type_occurrence_counts": dict(sorted(publication_types.items())),
        "publication_type_field_complete": all(row.get("all_retained_rows_have_publication_type") is True for row in partitions),
        "detail_capture_complete": all(row.get("record_capture_valid") is True for row in partitions),
        "source_union_receipt": relative(union_path) if union_valid and union_path.is_file() else None,
        "source_union_receipt_sha256": digest(union_path) if union_valid and union_path.is_file() else None,
        "source_union_valid": union_valid,
        "source_union_attempt": union_attempt,
        "partitions": partitions,
        "validation_errors": errors,
        "completed_at_utc": now(),
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
    run.add_argument("--settle-seconds", type=float, default=10.0)
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
            raise ValueError("Generated an invalid shared-browser corrective IEEE plan: " + ", ".join(errors))
        write_new(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
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
