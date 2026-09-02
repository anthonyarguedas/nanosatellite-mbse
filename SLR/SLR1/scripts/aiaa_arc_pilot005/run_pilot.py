#!/usr/bin/env python3
"""Execute immutable AIAA ARC Pilot 005 diagnostic events."""

from __future__ import annotations

import argparse
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
PILOT_ROOT = ROOT / "source-specific" / "aiaa-arc" / "pilots" / "005"
SEARCH_ROOT = PILOT_ROOT / "searches"
DEFAULT_PLAN = SEARCH_ROOT / "event-plan.json"
DEFAULT_ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py"
DEFAULT_DATE_START = "2011-01-01"
DEFAULT_DATE_END = "2026-08-29"


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


def successful_attempt(base: Path) -> Path | None:
    candidates = [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 8))]
    for candidate in candidates:
        if candidate.exists():
            try:
                data = load(candidate)
            except Exception:
                continue
            if isinstance(data.get("total"), int):
                return candidate
    return None


def next_attempt(base: Path) -> Path:
    candidates = [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 8))]
    for candidate in candidates:
        if not candidate.exists() and not failure_path(candidate).exists():
            return candidate
    raise RuntimeError(f"All attempt paths are occupied for {base}")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PILOT_ROOT))
    except ValueError:
        return str(path)


def phase_for(event: dict[str, Any]) -> str:
    event_id = str(event["event_id"])
    if event_id.startswith("count-"):
        return "counts"
    if event_id.startswith("repeat-count-"):
        return "repeats"
    if event_id.startswith("preview-"):
        return "previews"
    if event_id.startswith("known-item-"):
        return "known"
    if event_id.startswith(("branch-", "phrase-")):
        return "followup"
    raise RuntimeError(f"Unknown event phase: {event_id}")


def command_for(adapter: Path, event: dict[str, Any], output: Path, plan: dict[str, Any]) -> list[str]:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required")
    date_window = plan["date_window"]
    mode = event["mode"]
    command = [
        uv,
        "run",
        str(adapter),
    ]
    for row in event.get("field_rows", []):
        command.extend(("--field-row", f"{row['field']}={row['text']}"))
    command.extend((
        "--access",
        "all",
        "--date-start",
        str(date_window.get("requested_start", DEFAULT_DATE_START)),
        "--date-end",
        str(date_window.get("requested_end", DEFAULT_DATE_END)),
        "--timeout",
        "90",
        "--page-delay-seconds",
        "1",
    ))
    if mode == "count":
        command.extend(("--limit", "20", "--max-pages", "1", "--count-only"))
    elif mode == "preview":
        command.extend(("--limit", "100", "--max-pages", "5", "--preview-results"))
    else:
        raise RuntimeError(f"Unknown event mode: {mode}")
    command.extend(("--output-path", str(output)))
    return command


def compact_output(completed: subprocess.CompletedProcess[str] | None, error: str | None = None) -> str:
    if error is not None:
        return error[-2000:]
    assert completed is not None
    value = ((completed.stdout or "") + (completed.stderr or "")).strip()
    value = value.replace(str(PROJECT_ROOT), ".")
    return value[-2000:] if value else "(no adapter output)"


def run_event(adapter: Path, event: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    base = PILOT_ROOT / str(event["output"])
    existing = successful_attempt(base)
    if existing is not None:
        data = load(existing)
        return {
            "event_id": event["event_id"],
            "status": "existing",
            "artifact": relative(existing),
            "source_total": data.get("total"),
        }
    target = next_attempt(base)
    target.parent.mkdir(parents=True, exist_ok=True)
    command = command_for(adapter, event, target, plan)
    completed: subprocess.CompletedProcess[str] | None = None
    timeout_error: str | None = None
    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False, timeout=240)
    except subprocess.TimeoutExpired as exc:
        timeout_error = f"Runner timeout after {exc.timeout} seconds"
    if target.exists():
        data = load(target)
        return {
            "event_id": event["event_id"],
            "status": "ran" if completed is not None and completed.returncode == 0 else "artifact_after_nonzero",
            "artifact": relative(target),
            "source_total": data.get("total"),
            "adapter_returncode": completed.returncode if completed is not None else None,
        }
    sidecar = failure_path(target)
    if not sidecar.exists():
        atomic_write(
            sidecar,
            {
                "schema_version": "aiaa-arc-pilot005-runner-failure/v1",
                "source": plan["source"],
                "pilot": plan["pilot"],
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
        "artifact": relative(sidecar),
        "source_total": None,
        "adapter_returncode": completed.returncode if completed is not None else None,
    }


def receipt_path(phase: str) -> Path:
    base = SEARCH_ROOT / f"run-receipt-{phase}.json"
    if not base.exists():
        return base
    for index in range(1, 8):
        candidate = SEARCH_ROOT / f"run-receipt-{phase}-retry{index}.json"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"All receipt paths are occupied for phase {phase}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument(
        "--phase",
        choices=("counts", "repeats", "previews", "known", "followup", "all"),
        default="all",
    )
    args = parser.parse_args()
    if not os.environ.get("BH_CDP_URL"):
        raise RuntimeError("Run through run_with_browser.py. BH_CDP_URL is absent.")
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise RuntimeError("The shared-browser-owned-tabs-v1 contract is required.")
    adapter = args.adapter.expanduser().resolve()
    if not adapter.is_file():
        raise FileNotFoundError(adapter)
    plan = load(args.plan)
    phases = {"counts", "repeats", "previews", "known", "followup"} if args.phase == "all" else {args.phase}
    events = [event for event in plan["events"] if phase_for(event) in phases]
    reports = [run_event(adapter, event, plan) for event in events]
    receipt = {
        "schema_version": "aiaa-arc-pilot005-run-receipt/v1",
        "source": plan["source"],
        "pilot": plan["pilot"],
        "phase": args.phase,
        "do_not_merge": True,
        "completed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "events": reports,
        "successful": sum(report["source_total"] is not None for report in reports),
        "failed": sum(report["source_total"] is None for report in reports),
    }
    target = receipt_path(args.phase)
    atomic_write(target, receipt)
    print(json.dumps({"receipt": relative(target), "successful": receipt["successful"], "failed": receipt["failed"]}))
    return 0 if receipt["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
