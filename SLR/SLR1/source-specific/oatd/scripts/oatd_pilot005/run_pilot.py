#!/usr/bin/env python3
"""Run the predeclared OATD Pilot 005 gate counts conservatively."""

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import queries

SCHEMA = "oatd-pilot-005-gate-count-run/v1"
PLAN_SCHEMA = "oatd-pilot-005-gate-count-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
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


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError as error:
            raise RuntimeError(f"Refusing to overwrite {path}") from error
    finally:
        temporary_path.unlink(missing_ok=True)


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "oatd_pilot005_execution_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expected_screenshots(output: Path) -> dict[str, Path]:
    return {
        "search_page": output.with_name(f"{output.stem}.search-page.png"),
        "results_page": output.with_name(f"{output.stem}.results-page.png"),
    }


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[Any, list[dict[str, Any]]]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != "005"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or len(events) != 5
        or [event.get("event_id") for event in events] != list(queries.GATE_IDS)
    ):
        raise RuntimeError("Unexpected OATD Pilot 005 count plan")
    safety = plan.get("source_safety")
    if (
        not isinstance(safety, dict)
        or safety.get("stop_after_first_failed_event") is not True
        or safety.get("runner_level_retries") != 0
        or safety.get("inter_event_delay_seconds") != 120.0
    ):
        raise RuntimeError("The OATD Pilot 005 source safety policy changed")
    adapter = load_adapter()
    adapter_plan = plan.get("adapter")
    if (
        not isinstance(adapter_plan, dict)
        or adapter_plan.get("id") != adapter.ADAPTER_ID
        or adapter_plan.get("version") != adapter.ADAPTER_VERSION
        or adapter.ADAPTER_VERSION != "10"
    ):
        raise RuntimeError("The OATD Pilot 005 adapter identity changed")
    files = adapter_plan.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("The OATD Pilot 005 adapter bindings are missing")
    for name, path in ADAPTER_FILES.items():
        descriptor = files.get(name)
        if not isinstance(descriptor, dict) or descriptor.get("sha256") != digest(path):
            raise RuntimeError(f"The OATD adapter changed after planning: {name}")
    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("The OATD Pilot 005 script bindings are missing")
    for relative, expected in scripts.items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"An OATD Pilot 005 source script changed: {relative}")
    baseline = plan.get("pilot004_baseline")
    if not isinstance(baseline, dict) or baseline.get("source_reported_total") != 1249:
        raise RuntimeError("The OATD Pilot 004 baseline is invalid")
    for key in ("failure_receipt", "checkpoint"):
        descriptor = baseline.get(key)
        if not isinstance(descriptor, dict):
            raise RuntimeError(f"The OATD baseline {key} binding is missing")
        path = REPOSITORY_ROOT / descriptor.get("path", "")
        if not path.is_file() or digest(path) != descriptor.get("sha256"):
            raise RuntimeError(f"The OATD baseline {key} changed")
    resolved = {plan_path.resolve()}
    for event in events:
        gate_id = event["event_id"]
        query = queries.GATE_QUERIES[gate_id]
        output = pilot_root / event.get("output", "")
        screenshots = expected_screenshots(output)
        declared_screenshots = {
            key: str(path.relative_to(pilot_root)) for key, path in screenshots.items()
        }
        if (
            event.get("query") != query
            or event.get("query_sha256") != text_digest(query)
            or event.get("count_only") is not True
            or event.get("language") != "English"
            or event.get("year_start") != 2011
            or event.get("year_end") != 2026
            or event.get("page_size") != 30
            or event.get("limit") != 1
            or event.get("max_pages") != 1
            or event.get("screenshots") != declared_screenshots
            or output.parent != pilot_root / "searches"
        ):
            raise RuntimeError(f"The OATD gate event changed: {gate_id}")
        configuration = adapter.build_oatd_search_configuration(
            query,
            language="English",
            year_start=2011,
            year_end=2026,
            page_size=30,
        )
        route = adapter.build_search_url(query, configuration=configuration)
        if (
            configuration.effective_query != event.get("effective_query")
            or text_digest(configuration.effective_query)
            != event.get("effective_query_sha256")
            or len(route) != event.get("navigation_route_characters")
            or len(route) > adapter.MAX_OATD_SEARCH_ROUTE_CHARACTERS
        ):
            raise RuntimeError(f"The OATD gate route changed: {gate_id}")
        for path in (
            output,
            adapter.oatd_output_commit_marker_path(output),
            *screenshots.values(),
        ):
            if os.path.lexists(path):
                raise RuntimeError(
                    f"Refusing to overwrite OATD gate output: {path.name}"
                )
            if path.resolve() in resolved:
                raise RuntimeError("An OATD Pilot 005 path collision was found")
            resolved.add(path.resolve())
    return adapter, events


def command(event: dict[str, Any], output: Path) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER_PATH),
        "--query",
        event["query"],
        "--language",
        event["language"],
        "--year-start",
        str(event["year_start"]),
        "--year-end",
        str(event["year_end"]),
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
        "--busy-retries",
        str(event["busy_retries"]),
        "--busy-retry-delay-seconds",
        str(event["busy_retry_delay_seconds"]),
        "--count-only",
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"slr1-oatd-p005-{event['event_id']}",
        "--prisma-review-id",
        "slr1",
        "--prisma-strategy-reference",
        "slr1-oatd-five-gate-count-pilot-v1",
        "--prisma-strategy-version",
        event["query_sha256"],
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["event_id"],
        "--prisma-partition-label",
        f"OATD Pilot 005 {event['event_id']} count gate",
        "--prisma-partition-description",
        event["purpose"],
    ]


def validate_success(
    adapter: Any, artifact: dict[str, Any], event: dict[str, Any], output: Path
) -> int:
    total = artifact.get("total")
    metadata = artifact.get("output_metadata")
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("requested_query") != event["query"]
        or artifact.get("executed_query") != event["effective_query"]
        or not isinstance(total, int)
        or isinstance(total, bool)
        or total < 0
        or total >= 1249
        or artifact.get("results") != []
        or artifact.get("do_not_merge") is not True
        or not isinstance(metadata, dict)
        or metadata.get("status") != "count_only"
        or metadata.get("count_only") is not True
        or metadata.get("observed_exact_query_echo") is not True
        or metadata.get("merge_eligible") is not False
        or metadata.get("normalized_merge_eligible") is not False
        or metadata.get("page_size") != 30
        or metadata.get("earliest_year_filter") != 2011
        or metadata.get("latest_year_filter") != 2026
    ):
        raise RuntimeError(f"The OATD {event['event_id']} count artifact is invalid")
    receipt = metadata.get("screenshots")
    screenshots = expected_screenshots(output)
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema_version") != "oatd-automatic-screenshots/v1"
        or receipt.get("automatic") is not True
        or receipt.get("opt_out_available") is not False
    ):
        raise RuntimeError(f"The OATD {event['event_id']} screenshots are invalid")
    for key, path in screenshots.items():
        evidence = receipt.get(key)
        if (
            not path.is_file()
            or not isinstance(evidence, dict)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != digest(path)
            or evidence.get("full_page") is not True
        ):
            raise RuntimeError(f"The OATD {event['event_id']} {key} is invalid")
    if not adapter.verify_commit_gated_publication(output, artifact):
        raise RuntimeError(f"The OATD {event['event_id']} marker is invalid")
    return total


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> int:
    if os.path.lexists(receipt_path):
        raise RuntimeError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    adapter, events = validate_plan(plan, plan_path, pilot_root)
    safety = plan["source_safety"]
    not_before = parse_utc(safety["first_source_request_not_before_utc"])
    wait_seconds = max(0.0, (not_before - datetime.now(timezone.utc)).total_seconds())
    if wait_seconds:
        print(f"Waiting {wait_seconds:.1f} seconds for the OATD cooldown.", flush=True)
        time.sleep(wait_seconds)

    started = now()
    outcomes: list[dict[str, Any]] = []
    stopped = False
    for index, event in enumerate(events):
        if index:
            time.sleep(float(safety["inter_event_delay_seconds"]))
        output = pilot_root / event["output"]
        event_started = now()
        timed_out = False
        try:
            completed = subprocess.run(
                command(event, output),
                check=False,
                capture_output=True,
                text=True,
                timeout=600,
            )
            return_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            timed_out = True
            return_code = 124
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
        artifact_exists = output.is_file()
        total: int | None = None
        valid = False
        validation_error: str | None = None
        if return_code == 0 and artifact_exists:
            try:
                total = validate_success(adapter, load(output), event, output)
                valid = True
            except Exception as error:
                validation_error = " ".join(str(error).split())[:500]
        elif artifact_exists:
            observed = load(output)
            candidate = observed.get("total")
            total = (
                candidate
                if isinstance(candidate, int) and not isinstance(candidate, bool)
                else None
            )
        screenshots = expected_screenshots(output)
        marker = adapter.oatd_output_commit_marker_path(output)
        outcome = {
            "event_id": event["event_id"],
            "started_at_utc": event_started,
            "completed_at_utc": now(),
            "return_code": return_code,
            "timed_out": timed_out,
            "valid_count_artifact": valid,
            "total": total,
            "strictly_below_p_baseline": isinstance(total, int) and total < 1249,
            "output": str(output.relative_to(pilot_root)),
            "output_exists": artifact_exists,
            "output_sha256": digest(output) if artifact_exists else None,
            "marker_exists": marker.is_file(),
            "screenshots_exist": {
                key: path.is_file() for key, path in screenshots.items()
            },
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stdout_sha256": text_digest(stdout),
            "stderr_bytes": len(stderr.encode("utf-8")),
            "stderr_sha256": text_digest(stderr),
            "validation_error": validation_error,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "event": event["event_id"],
                    "return_code": return_code,
                    "total": total,
                    "valid": valid,
                }
            ),
            flush=True,
        )
        if not valid:
            stopped = True
            break

    success = not stopped and len(outcomes) == len(events)
    receipt = {
        "schema_version": SCHEMA,
        "source": plan["source"],
        "pilot": "005",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(plan_path.relative_to(pilot_root)),
        "plan_sha256": digest(plan_path),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "completed_event_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": success,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0 if success else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args.plan, args.pilot_root, args.receipt)
    except Exception as error:
        print(" ".join(str(error).split())[:1000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
