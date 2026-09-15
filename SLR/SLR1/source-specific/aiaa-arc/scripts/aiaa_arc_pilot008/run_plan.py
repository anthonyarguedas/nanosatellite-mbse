#!/usr/bin/env python3
"""Run resumable AIAA ARC Pilot 008 Topic events."""

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

ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOT = ROOT.parents[1]
PILOT_ROOT = ROOT / "source-specific" / "aiaa-arc" / "pilots" / "008"
SEARCH_ROOT = PILOT_ROOT / "searches"
DEFAULT_PLAN = SEARCH_ROOT / "discovery-plan.json"
DEFAULT_ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py"


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
    return [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 20))]


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


def strategy_for(data: dict[str, Any]) -> dict[str, Any]:
    return (
        data.get("output_metadata", {})
        .get("prisma_search_run", {})
        .get("strategy", {})
    )


def topic_evidence(strategy: dict[str, Any]) -> tuple[str | None, str | None]:
    limits = strategy.get("limits", {})
    topic = limits.get("topic", {}) if isinstance(limits, dict) else {}
    effective = topic.get("effective") if isinstance(topic, dict) else None
    native_id = None
    if isinstance(effective, list) and len(effective) == 1 and isinstance(effective[0], str):
        native_id = effective[0]
    return topic.get("state") if isinstance(topic, dict) else None, native_id


def requested_topic(event: dict[str, Any]) -> tuple[str | None, str | None]:
    selection = event.get("topic_selection")
    if isinstance(selection, dict):
        return selection.get("label"), selection.get("concept_id")
    return event.get("topic_label"), None


def validate_success(path: Path, event: dict[str, Any]) -> list[str]:
    data = load(path)
    errors: list[str] = []
    total = data.get("total")
    results = data.get("results")
    metadata = data.get("output_metadata", {})
    strategy = strategy_for(data)
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
    elif total > 100:
        errors.append("event exceeds the 100-record complete-preview bound")
    if not isinstance(results, list):
        errors.append("results are unavailable")
    elif isinstance(total, int) and len(results) != total:
        errors.append("preview did not retain every source result")
    if metadata.get("status") != "preview" or metadata.get("retrieval_complete") is not True:
        errors.append("artifact is not a complete preview receipt")

    limits = strategy.get("limits", {})
    topic = limits.get("topic", {}) if isinstance(limits, dict) else {}
    expected_topic, expected_topic_id = requested_topic(event)
    if expected_topic is None:
        if topic.get("state") != "not_applied":
            errors.append("unexpected Topic restriction")
        if strategy.get("topic_selections") not in (None, []):
            errors.append("unexpected Topic selection")
    else:
        if topic.get("state") != "applied":
            errors.append("Topic was not marked applied")
        if topic.get("requested") != [expected_topic]:
            errors.append("Topic requested-label readback mismatch")
        if limits.get("topic_selections") != [expected_topic]:
            errors.append("Topic strategy-label readback mismatch")
        selection_state, native_id = topic_evidence(strategy)
        if selection_state != "applied" or topic.get("provenance") != "source_echo":
            errors.append("Topic selection lacks applied source readback")
        if not isinstance(native_id, str) or not native_id.isdecimal():
            errors.append("Topic selection lacks one numeric ConceptID")
        elif expected_topic_id is not None and native_id != expected_topic_id:
            errors.append("Topic ConceptID changed from the predeclared typed selection")

    screenshots = metadata.get("screenshots", {})
    for key, expected_path in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        if not expected_path.is_file():
            errors.append(f"missing {key} screenshot")
            continue
        if evidence.get("path") != expected_path.name:
            errors.append(f"{key} screenshot path evidence mismatch")
        if evidence.get("sha256") != digest(expected_path):
            errors.append(f"{key} screenshot hash mismatch")
    return errors


def command_for(adapter: Path, target: Path, event: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required")
    command = [uv, "run", str(adapter)]
    for row in event["field_rows"]:
        command.extend(("--field-row", f"{row['field']}={row['text']}"))
    topic_label, topic_id = requested_topic(event)
    if topic_id is not None:
        command.extend(("--topic-selection", f"{topic_id}={topic_label}"))
    elif topic_label is not None:
        command.extend(("--topic", topic_label))
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
        "120",
        "--preview-cards-only",
        "--output-path",
        str(target),
    ))
    return command


def compact_output(completed: subprocess.CompletedProcess[str] | None, error: str | None) -> str:
    if error is not None:
        return error[-3000:]
    assert completed is not None
    value = ((completed.stdout or "") + (completed.stderr or "")).strip()
    return value.replace(str(PROJECT_ROOT), ".")[-3000:] or "(no adapter output)"


def run_event(adapter: Path, event: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    base = PILOT_ROOT / event["output"]
    existing = successful_attempt(base)
    if existing is not None:
        errors = validate_success(existing, event)
        data = load(existing)
        state, native_id = topic_evidence(strategy_for(data))
        return {
            "event_id": event["event_id"],
            "status": "existing" if not errors else "existing_incomplete",
            "artifact": str(existing.relative_to(PILOT_ROOT)),
            "source_total": data.get("total"),
            "topic_label": requested_topic(event)[0],
            "topic_concept_id": native_id,
            "topic_state": state,
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
            timeout=420,
        )
    except subprocess.TimeoutExpired as error:
        timeout_error = f"Runner timeout after {error.timeout} seconds"
    if target.exists():
        errors = validate_success(target, event)
        data = load(target)
        state, native_id = topic_evidence(strategy_for(data))
        return {
            "event_id": event["event_id"],
            "status": "ran" if not errors else "ran_incomplete",
            "artifact": str(target.relative_to(PILOT_ROOT)),
            "source_total": data.get("total"),
            "topic_label": requested_topic(event)[0],
            "topic_concept_id": native_id,
            "topic_state": state,
            "adapter_returncode": completed.returncode if completed is not None else None,
            "errors": errors,
        }
    sidecar = failure_path(target)
    if not sidecar.exists():
        atomic_write(
            sidecar,
            {
                "schema_version": "aiaa-arc-pilot008-runner-failure/v1",
                "source": plan["source"],
                "pilot": "008",
                "event_id": event["event_id"],
                "topic_label": requested_topic(event)[0],
                "topic_selection": event.get("topic_selection"),
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
        "topic_label": requested_topic(event)[0],
        "topic_concept_id": None,
        "topic_state": None,
        "adapter_returncode": completed.returncode if completed is not None else None,
        "errors": [compact_output(completed, timeout_error)],
    }


def receipt_path(plan: Path) -> Path:
    stem = plan.stem.removesuffix("-plan")
    base = SEARCH_ROOT / f"run-receipt-{stem}.json"
    if not base.exists():
        return base
    for index in range(1, 20):
        candidate = SEARCH_ROOT / f"run-receipt-{stem}-retry{index}.json"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"All receipt paths are occupied for {plan}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--event-id", action="append", default=[])
    args = parser.parse_args()
    if not os.environ.get("BH_CDP_URL"):
        raise RuntimeError("Run through run_with_browser.py. BH_CDP_URL is absent.")
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise RuntimeError("The shared-browser-owned-tabs-v1 contract is required.")
    adapter = args.adapter.expanduser().resolve()
    if not adapter.is_file():
        raise FileNotFoundError(adapter)
    plan_path = args.plan.resolve()
    plan = load(plan_path)
    selected = set(args.event_id)
    events = [event for event in plan["events"] if not selected or event["event_id"] in selected]
    if selected - {event["event_id"] for event in events}:
        raise RuntimeError(f"Unknown event IDs: {sorted(selected - {event['event_id'] for event in events})}")
    reports = [run_event(adapter, event, plan) for event in events]
    receipt = {
        "schema_version": "aiaa-arc-pilot008-run-receipt/v1",
        "source": plan["source"],
        "pilot": "008",
        "plan": str(plan_path.relative_to(PILOT_ROOT)),
        "do_not_merge": True,
        "completed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "events": reports,
        "successful": sum(not report["errors"] for report in reports),
        "failed_or_incomplete": sum(bool(report["errors"]) for report in reports),
    }
    target = receipt_path(plan_path)
    atomic_write(target, receipt)
    print(json.dumps({
        "receipt": str(target.relative_to(PILOT_ROOT)),
        "successful": receipt["successful"],
        "failed_or_incomplete": receipt["failed_or_incomplete"],
    }))
    return 0 if receipt["failed_or_incomplete"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
