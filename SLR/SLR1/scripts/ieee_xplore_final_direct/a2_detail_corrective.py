#!/usr/bin/env python3
"""Run one predeclared A2 final correction with controlled detail evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
ROOT = SCRIPT_PATH.parents[4]
CORE_PATH = SCRIPT_DIR / "run.py"
BUNDLE_PATH = SCRIPT_DIR / "corrective_bundle.py"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
PREVIOUS_ROOT = ROOT / "SLR/SLR1/source-specific/ieee-xplore/final-searches/corrective-007"
PREVIOUS_PLAN = PREVIOUS_ROOT / "final-event-plan.json"
PREVIOUS_RECEIPT = PREVIOUS_ROOT / "run-receipt.json"
QUERY_SNAPSHOT = ROOT / "SLR/SLR1/scripts/ieee_xplore_pilot005/queries.py"
GUIDELINE = ROOT / "SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md"
PROTOCOL = ROOT / "SLR/SLR1/protocol.md"
DISCOVERY = ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
PLAN_SCHEMA = "slr1-ieee-xplore-a2-detail-corrective-plan/v1"
RUN_SCHEMA = "slr1-ieee-xplore-a2-detail-corrective-run/v1"
PARTITION = "A2"
SEQUENCE = 8
DETAIL_DELAY_SECONDS = 5.0
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"


def module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CORE = module("ieee_a2_core", CORE_PATH)
BUNDLE = module("ieee_a2_bundle", BUNDLE_PATH)
SUMMARY = BUNDLE.SUMMARY


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return CORE.digest(path)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def relative(path: Path) -> str:
    return CORE.relative(path)


def load(path: Path) -> dict[str, Any]:
    return CORE.load(path)


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def prior() -> tuple[dict[str, Any], dict[str, Any]]:
    plan, run = load(PREVIOUS_PLAN), load(PREVIOUS_RECEIPT)
    if (
        run.get("plan_sha256") != digest(PREVIOUS_PLAN)
        or run.get("success") is not False
        or run.get("accepted_pending_event_count") != 0
        or not all(
            outcome.get("error_stage") in {"detail", "browser_open"}
            for outcome in run.get("outcomes", [])
            if isinstance(outcome, Mapping)
        )
    ):
        raise RuntimeError("The prior paced correction is not the expected failure")
    return plan, run


def bindings() -> dict[str, str]:
    paths = (SCRIPT_PATH, CORE_PATH, BUNDLE_PATH, QUERY_SNAPSHOT, GUIDELINE, PROTOCOL, DISCOVERY)
    return {relative(path): digest(path) for path in paths}


def build_plan() -> dict[str, Any]:
    previous, _ = prior()
    queries = CORE.load_queries()
    event = CORE.plan_event(
        PARTITION,
        queries.SCHEDULE[PARTITION],
        SEQUENCE,
        previous["repository_head_at_predeclaration"],
    )
    event["detail_delay_seconds"] = DETAIL_DELAY_SECONDS
    event["browser_execution"] = "attached_shared_cdp_owned_page"
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": "IEEE Xplore",
        "source_id": "ieee_xplore",
        "review_namespace": "main",
        "review_id": previous["review_id"],
        "phase": previous["phase"],
        "strategy_reference": previous["strategy_reference"],
        "strategy_version": previous["repository_head_at_predeclaration"],
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "date_window": previous["date_window"],
        "source_configuration": previous["source_configuration"],
        "execution_policy": {
            "one_source_execution": True,
            "retry_policy": "none_after_a2_detail_corrective_plan_begins",
            "detail_delay_seconds": DETAIL_DELAY_SECONDS,
            "skip_full_abstracts": False,
            "publication_type_filter": None,
            "target_identifiers_retained": False,
        },
        "corrective": {
            "superseded_plan": relative(PREVIOUS_PLAN),
            "superseded_plan_sha256": digest(PREVIOUS_PLAN),
            "superseded_run_receipt": relative(PREVIOUS_RECEIPT),
            "superseded_run_receipt_sha256": digest(PREVIOUS_RECEIPT),
            "scientific_query_changed": False,
            "reason": (
                "The paced A2 event reached strict detail capture and failed. Adapter v18 "
                "publishes one fixed detail error reason if this event fails again. The "
                "five-second interval also tests a stronger source-safe detail cadence."
            ),
            "prior_adapter_version": previous["adapter"]["version"],
            "prior_adapter_sha256": previous["adapter"]["sha256"],
        },
        "adapter": {
            "id": "search_ieee_xplore",
            "version": CORE.adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "bindings": {"files": bindings()},
        "event": event,
    }


def validate(plan: Mapping[str, Any], verify: bool) -> list[str]:
    errors: list[str] = []
    previous, _ = prior()
    queries = CORE.load_queries()
    event = plan.get("event", {})
    expected = CORE.plan_event(
        PARTITION,
        queries.SCHEDULE[PARTITION],
        SEQUENCE,
        previous["repository_head_at_predeclaration"],
    )
    expected["detail_delay_seconds"] = DETAIL_DELAY_SECONDS
    expected["browser_execution"] = "attached_shared_cdp_owned_page"
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    if (
        plan.get("source_id") != "ieee_xplore"
        or plan.get("review_namespace") != "main"
        or plan.get("review_id") != previous["review_id"]
        or plan.get("strategy_reference") != previous["strategy_reference"]
        or plan.get("strategy_version") != previous["repository_head_at_predeclaration"]
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or event != expected
    ):
        errors.append("identity")
    if (
        plan.get("date_window") != previous["date_window"]
        or plan.get("source_configuration") != previous["source_configuration"]
        or plan.get("execution_policy", {}).get("detail_delay_seconds") != DETAIL_DELAY_SECONDS
        or plan.get("execution_policy", {}).get("skip_full_abstracts") is not False
        or plan.get("execution_policy", {}).get("publication_type_filter") is not None
        or plan.get("corrective", {}).get("scientific_query_changed") is not False
        or plan.get("corrective", {}).get("superseded_plan_sha256") != digest(PREVIOUS_PLAN)
        or plan.get("corrective", {}).get("superseded_run_receipt_sha256") != digest(PREVIOUS_RECEIPT)
    ):
        errors.append("contract")
    if verify:
        adapter = plan.get("adapter", {})
        if adapter.get("version") != CORE.adapter_version() or adapter.get("sha256") != digest(ADAPTER):
            errors.append("adapter_changed")
        for name, expected_hash in plan.get("bindings", {}).get("files", {}).items():
            path = ROOT / name
            if not path.is_file() or path.is_symlink() or digest(path) != expected_hash:
                errors.append(f"binding:{name}")
    return errors


def command(plan: Mapping[str, Any], output: Path) -> list[str]:
    event = plan["event"]
    cdp = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    return [
        "uv", "run", str(ADAPTER), "--query", event["query"],
        "--publication-date-start", DATE_START, "--publication-date-end", DATE_END,
        "--scope", "documents", "--access-scope", "all", "--sort", "Oldest",
        "--page-size", str(event["page_size"]), "--limit", str(event["limit"]),
        "--max-pages", str(event["max_pages"]), "--timeout", str(event["timeout_seconds"]),
        "--page-delay-seconds", str(event["page_delay_seconds"]),
        "--detail-delay-seconds", str(event["detail_delay_seconds"]), "--require-complete",
        "--cdp-url", cdp, "--output-path", str(output),
        "--prisma-run-id", event["event_id"], "--prisma-review-id", plan["review_id"],
        "--prisma-strategy-reference", plan["strategy_reference"],
        "--prisma-strategy-version", plan["strategy_version"], "--prisma-phase", plan["phase"],
        "--prisma-coverage-scope", "partition", "--prisma-partition-id", PARTITION,
        "--prisma-partition-label", PARTITION,
        "--prisma-partition-description", "IEEE Xplore A2 detail corrective final discovery event",
    ]


def run(plan_path: Path, output: Path, receipt: Path) -> int:
    plan = load(plan_path)
    errors = validate(plan, True)
    if errors:
        raise ValueError("Invalid A2 corrective plan: " + ", ".join(errors))
    if any(path.exists() or path.is_symlink() for path in (output, CORE.marker_path(output), *CORE.screenshot_paths(output), receipt)):
        raise FileExistsError("Refusing to overwrite A2 corrective artifacts")
    started = now()
    completed = subprocess.run(command(plan, output), check=False, capture_output=True, text=True)
    summary = SUMMARY(output, plan["event"], {
        "review_id": plan["review_id"], "strategy_reference": plan["strategy_reference"],
        "phase": plan["phase"], "adapter": plan["adapter"],
    })
    success = completed.returncode == 0 and summary.get("valid") is True
    value = {
        "schema_version": RUN_SCHEMA,
        "source": "IEEE Xplore",
        "partition_id": PARTITION,
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "source_command_attempt_count": 1,
        "target_identifier_retained": False,
        "success": success,
        "exit_code": completed.returncode,
        "stdout_sha256": digest_text(completed.stdout),
        "stdout_bytes": len(completed.stdout.encode()),
        "stderr_sha256": digest_text(completed.stderr),
        "stderr_bytes": len(completed.stderr.encode()),
        **summary,
    }
    write_new(receipt, value)
    print(json.dumps({
        "partition": PARTITION,
        "success": success,
        "source_total": summary.get("source_total"),
        "retained_records": summary.get("retained_record_count"),
        "full_abstracts": summary.get("full_abstract_count"),
        "error_stage": summary.get("error_stage"),
        "error_reason": summary.get("error_reason"),
    }))
    return 0 if success else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-plan")
    build.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("check-plan")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--verify-bindings", action="store_true")
    execute = commands.add_parser("run")
    execute.add_argument("--plan", type=Path, required=True)
    execute.add_argument("--output", type=Path, required=True)
    execute.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan()
        errors = validate(plan, False)
        if errors:
            raise ValueError("Generated invalid A2 plan: " + ", ".join(errors))
        write_new(args.output, plan)
        return 0
    if args.command == "check-plan":
        errors = validate(load(args.plan), args.verify_bindings)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 1 if errors else 0
    if args.command == "run":
        return run(args.plan, args.output, args.receipt)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
