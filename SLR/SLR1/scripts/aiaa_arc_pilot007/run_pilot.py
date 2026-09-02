#!/usr/bin/env python3
"""Run resumable AIAA ARC Pilot 007 hybrid metadata cells."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ROOT.parents[1]
PILOT_ROOT = ROOT / "source-specific" / "aiaa-arc" / "pilots" / "007"
SEARCH_ROOT = PILOT_ROOT / "searches"
DEFAULT_PLAN = SEARCH_ROOT / "event-plan.json"
DEFAULT_ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def failure_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.NON_MERGEABLE_FAILURE{path.suffix}")


def attempts(base: Path) -> list[Path]:
    return [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 10))]


def successful_attempt(base: Path) -> Path | None:
    for candidate in attempts(base):
        if not candidate.exists():
            continue
        try:
            data = load(candidate)
        except Exception:
            continue
        if isinstance(data.get("total"), int):
            return candidate
    return None


def next_attempt(base: Path) -> Path:
    for candidate in attempts(base):
        if not candidate.exists() and not failure_path(candidate).exists():
            return candidate
    raise RuntimeError(f"All output attempts are occupied for {base}")


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    base = output.name[:-5] if output.name.casefold().endswith(".json") else output.name
    return (
        output.with_name(f"{base}.search-page.png"),
        output.with_name(f"{base}.results-page.png"),
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_success(path: Path, event: dict[str, Any]) -> list[str]:
    data = load(path)
    errors = []
    total = data.get("total")
    results = data.get("results")
    metadata = data.get("output_metadata", {})
    strategy = metadata.get("prisma_search_run", {}).get("strategy", {})
    expected_rows = event["field_rows"]
    observed_rows = strategy.get("field_rows", [])
    if strategy.get("executed_query_provenance") != "source_observed":
        errors.append("query was not source-observed")
    if len(observed_rows) != len(expected_rows):
        errors.append("field-row count mismatch")
    else:
        for observed, expected in zip(observed_rows, expected_rows):
            if (
                observed.get("field") != expected["source_field"]
                or observed.get("text") != expected["text"]
            ):
                errors.append("field-row readback mismatch")
    if not isinstance(total, int) or total < 0:
        errors.append("source total is unavailable")
    if not isinstance(results, list):
        errors.append("results are unavailable")
    elif isinstance(total, int) and total <= 100 and len(results) != total:
        errors.append("cell preview did not retain every source result")
    if isinstance(total, int) and total > 100:
        errors.append("cell exceeds the 100-record complete-preview bound")
    if metadata.get("status") != "preview":
        errors.append("artifact is not a preview receipt")
    if isinstance(total, int) and total <= 100 and metadata.get("retrieval_complete") is not True:
        errors.append("cell preview is not marked complete")
    screenshots = metadata.get("screenshots", {})
    expected_screenshots = screenshot_paths(path)
    for key, expected_path in zip(("search_page", "results_page"), expected_screenshots):
        evidence = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        if not expected_path.is_file():
            errors.append(f"missing {key} screenshot")
            continue
        if evidence.get("path") != expected_path.name:
            errors.append(f"{key} screenshot path evidence mismatch")
        if evidence.get("sha256") != digest(expected_path):
            errors.append(f"{key} screenshot hash mismatch")
        if not isinstance(evidence.get("width"), int) or not isinstance(evidence.get("height"), int):
            errors.append(f"{key} screenshot dimensions missing")
    return errors


def command_for(adapter: Path, target: Path, event: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required")
    command = [uv, "run", str(adapter)]
    for row in event["field_rows"]:
        command.extend(("--field-row", f"{row['field']}={row['text']}"))
    command.extend((
        "--access",
        "all",
        "--date-start",
        plan["date_window"]["requested_start"],
        "--date-end",
        plan["date_window"]["requested_end"],
        "--limit",
        "100",
        "--max-pages",
        "5",
        "--timeout",
        "90",
        "--preview-cards-only",
        "--output-path",
        str(target),
    ))
    return command


def compact_output(completed: subprocess.CompletedProcess[str] | None, error: str | None) -> str:
    if error is not None:
        return error[-2000:]
    assert completed is not None
    value = ((completed.stdout or "") + (completed.stderr or "")).strip()
    return value.replace(str(PROJECT_ROOT), ".")[-2000:] or "(no adapter output)"


def run_event(adapter: Path, event: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    base = PILOT_ROOT / event["output"]
    existing = successful_attempt(base)
    if existing is not None:
        errors = validate_success(existing, event)
        data = load(existing)
        return {
            "event_id": event["event_id"],
            "status": "existing" if not errors else "existing_incomplete",
            "artifact": str(existing.relative_to(PILOT_ROOT)),
            "source_total": data.get("total"),
            "errors": errors,
        }
    target = next_attempt(base)
    target.parent.mkdir(parents=True, exist_ok=True)
    completed: subprocess.CompletedProcess[str] | None = None
    timeout_error: str | None = None
    try:
        completed = subprocess.run(
            command_for(adapter, target, event, plan),
            text=True,
            capture_output=True,
            check=False,
            timeout=300,
        )
    except subprocess.TimeoutExpired as error:
        timeout_error = f"Runner timeout after {error.timeout} seconds"
    if target.exists():
        errors = validate_success(target, event)
        data = load(target)
        return {
            "event_id": event["event_id"],
            "status": "ran" if not errors else "ran_incomplete",
            "artifact": str(target.relative_to(PILOT_ROOT)),
            "source_total": data.get("total"),
            "adapter_returncode": completed.returncode if completed is not None else None,
            "errors": errors,
        }
    sidecar = failure_path(target)
    if not sidecar.exists():
        atomic_write(
            sidecar,
            {
                "schema_version": "aiaa-arc-pilot007-runner-failure/v1",
                "source": plan["source"],
                "pilot": "007",
                "event_id": event["event_id"],
                "do_not_merge": True,
                "status": "source_or_adapter_failure",
                "attempted_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "adapter_returncode": completed.returncode if completed is not None else None,
                "output": compact_output(completed, timeout_error),
            },
        )
    return {
        "event_id": event["event_id"],
        "status": "source_or_adapter_failure",
        "artifact": str(sidecar.relative_to(PILOT_ROOT)),
        "source_total": None,
        "adapter_returncode": completed.returncode if completed is not None else None,
        "errors": [compact_output(completed, timeout_error)],
    }


def receipt_path(partition: str) -> Path:
    base = SEARCH_ROOT / f"run-receipt-{partition}.json"
    if not base.exists():
        return base
    for index in range(1, 10):
        candidate = SEARCH_ROOT / f"run-receipt-{partition}-retry{index}.json"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"All receipt paths are occupied for {partition}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--partition", choices=PARTITIONS, required=True)
    args = parser.parse_args()
    if not os.environ.get("BH_CDP_URL"):
        raise RuntimeError("Run through run_with_browser.py. BH_CDP_URL is absent.")
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise RuntimeError("The shared-browser-owned-tabs-v1 contract is required.")
    adapter = args.adapter.expanduser().resolve()
    if not adapter.is_file():
        raise FileNotFoundError(adapter)
    plan = load(args.plan)
    events = [event for event in plan["events"] if event["partition"] == args.partition]
    reports = [run_event(adapter, event, plan) for event in events]
    receipt = {
        "schema_version": "aiaa-arc-pilot007-run-receipt/v1",
        "source": plan["source"],
        "pilot": "007",
        "partition": args.partition,
        "do_not_merge": True,
        "completed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "events": reports,
        "successful": sum(not report["errors"] for report in reports),
        "failed_or_incomplete": sum(bool(report["errors"]) for report in reports),
    }
    target = receipt_path(args.partition)
    atomic_write(target, receipt)
    print(json.dumps({
        "receipt": str(target.relative_to(PILOT_ROOT)),
        "successful": receipt["successful"],
        "failed_or_incomplete": receipt["failed_or_incomplete"],
    }))
    return 0 if receipt["failed_or_incomplete"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
