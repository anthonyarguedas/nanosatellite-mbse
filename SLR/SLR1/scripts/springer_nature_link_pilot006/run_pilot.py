#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "cdp-use==1.4.5",
#     "pillow==12.2.0",
#     "playwright>=1.48",
#     "websockets==15.0.1",
# ]
# ///

"""Run Springer Pilot 006 strict complete readiness events."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PILOT_ROOT = SLR1_DIR / "source-specific" / "springer-nature-link" / "pilots" / "006"
DEFAULT_PLAN = PILOT_ROOT / "searches" / "event-plan-v4.json"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
DEFAULT_ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_springer_link.py"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


def write_json_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_adapter(path: Path, minimum_version: int) -> Any:
    spec = importlib.util.spec_from_file_location("springer_p006_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Springer adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if int(module.ADAPTER_VERSION) < minimum_version:
        raise RuntimeError(f"Springer adapter version {minimum_version}+ is required")
    return module


def validate_plan(plan: dict[str, Any]) -> None:
    controls = plan.get("shared_controls")
    events = plan.get("events")
    if (
        plan.get("schema_version")
        not in {
            "springer-nature-link-pilot006-event-plan/v1",
            "springer-nature-link-pilot006-event-plan/v2",
            "springer-nature-link-pilot006-event-plan/v3",
            "springer-nature-link-pilot006-event-plan/v4",
        }
        or plan.get("adapter_minimum_version") not in {11, 12}
        or not isinstance(controls, dict)
        or controls.get("require_complete") is not True
        or controls.get("passes") != 2
        or controls.get("browser_mode", "attached")
        not in {
            "attached",
            "fresh_visible",
            "attached_in_process",
            "target_scoped_shared_cdp",
        }
        or not isinstance(events, list)
        or len(events) != 3
    ):
        raise RuntimeError("Springer Pilot 006 plan is invalid")
    for event in events:
        if (
            not isinstance(event.get("event_id"), str)
            or not isinstance(event.get("query"), str)
            or not isinstance(event.get("title"), str)
            or not isinstance(event.get("output"), str)
            or not isinstance(event.get("expected_source_total"), int)
            or not isinstance(event.get("expected_results_retrieved"), int)
        ):
            raise RuntimeError("Springer Pilot 006 event is invalid")


def command_for_event(
    adapter_path: Path,
    plan: dict[str, Any],
    event: dict[str, Any],
    output: Path,
    cdp_url: str,
) -> list[str]:
    controls = plan["shared_controls"]
    browser_args = (
        ["--fresh-browser"]
        if controls.get("browser_mode") == "fresh_visible"
        else ["--cdp-url", cdp_url]
    )
    return [
        "--query",
        event["query"],
        "--title",
        event["title"],
        "--date-start",
        controls["date_start"],
        "--date-end",
        controls["date_end"],
        "--language",
        controls["language"],
        "--sort",
        controls["sort"],
        "--passes",
        str(controls["passes"]),
        "--limit",
        str(controls["limit"]),
        "--max-pages",
        str(controls["max_pages"]),
        "--timeout",
        "60",
        "--require-complete",
        *browser_args,
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"springer-p006-{event['event_id']}",
        "--prisma-review-id",
        "nanosatellite-mbse-slr1",
        "--prisma-strategy-reference",
        f"SLR1-Springer-Pilot-006-{event['event_id']}",
        "--prisma-strategy-version",
        "3194156e90497186664260a8e86435e78d2e2aa1",
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        f"springer-p006-{event['event_id']}",
        "--prisma-partition-label",
        event["event_id"],
    ]


def run(args: argparse.Namespace) -> dict[str, Any]:
    plan = load_json(args.plan)
    validate_plan(plan)
    adapter = load_adapter(args.adapter, plan["adapter_minimum_version"])
    started_at = now()
    results = []
    for event in plan["events"]:
        output = args.pilot_root / "searches" / event["output"]
        screenshot_paths = adapter.screenshot_paths_for_output(output)
        commit_path = adapter.normal_output_commit_path(output)
        reserved = [
            output,
            commit_path,
            screenshot_paths.search_page,
            screenshot_paths.results_page,
        ]
        if (
            adapter.is_complete_output_publication(output, None)
            and screenshot_paths.search_page.is_file()
            and screenshot_paths.results_page.is_file()
        ):
            results.append(
                {
                    "event_id": event["event_id"],
                    "execution": "existing_valid",
                    "output": event["output"],
                    "output_sha256": file_sha256(output),
                    "commit_marker": commit_path.name,
                    "commit_marker_sha256": file_sha256(commit_path),
                    "search_page": screenshot_paths.search_page.name,
                    "search_page_sha256": file_sha256(screenshot_paths.search_page),
                    "results_page": screenshot_paths.results_page.name,
                    "results_page_sha256": file_sha256(screenshot_paths.results_page),
                    "stdout_sha256": None,
                    "stderr_sha256": None,
                    "started_at": None,
                    "completed_at": now(),
                }
            )
            continue
        if any(os.path.lexists(path) for path in reserved):
            raise FileExistsError(
                f"Refusing to reuse incomplete output paths for {event['event_id']}"
            )
        command = command_for_event(args.adapter, plan, event, output, args.cdp_url)
        event_started_at = now()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            returncode = adapter.main(command)
        stdout_value = stdout.getvalue()
        stderr_value = stderr.getvalue()
        if returncode != 0:
            failure = {
                "schema_version": "springer-nature-link-pilot006-run-failure/v1",
                "pilot": "006",
                "event_id": event["event_id"],
                "status": "failure",
                "diagnostic_only": True,
                "do_not_merge": True,
                "returncode": returncode,
                "stderr": adapter.clean_text(stderr_value)[-2000:],
                "recorded_at": now(),
            }
            failure_root = args.pilot_root / "searches" / "failures"
            failure_path = failure_root / f"{event['event_id']}.json"
            attempt = 2
            while failure_path.exists() or failure_path.is_symlink():
                failure_path = (
                    failure_root / f"{event['event_id']}.attempt-{attempt:02d}.json"
                )
                attempt += 1
            write_json_create_only(failure_path, failure)
            raise RuntimeError(f"Springer Pilot 006 event failed: {event['event_id']}")
        if (
            not adapter.is_complete_output_publication(output, None)
            or not screenshot_paths.search_page.is_file()
            or not screenshot_paths.results_page.is_file()
        ):
            raise RuntimeError(
                f"Springer Pilot 006 publication is incomplete: {event['event_id']}"
            )
        results.append(
            {
                "event_id": event["event_id"],
                "execution": "success",
                "output": event["output"],
                "output_sha256": file_sha256(output),
                "commit_marker": commit_path.name,
                "commit_marker_sha256": file_sha256(commit_path),
                "search_page": screenshot_paths.search_page.name,
                "search_page_sha256": file_sha256(screenshot_paths.search_page),
                "results_page": screenshot_paths.results_page.name,
                "results_page_sha256": file_sha256(screenshot_paths.results_page),
                "stdout_sha256": hashlib.sha256(
                    stdout_value.encode("utf-8")
                ).hexdigest(),
                "stderr_sha256": hashlib.sha256(
                    stderr_value.encode("utf-8")
                ).hexdigest(),
                "started_at": event_started_at,
                "completed_at": now(),
            }
        )
    return {
        "schema_version": "springer-nature-link-pilot006-run-receipt/v1",
        "pilot": "006",
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan.relative_to(args.pilot_root)),
        "plan_sha256": file_sha256(args.plan),
        "adapter": {
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": file_sha256(args.adapter),
        },
        "event_count": len(results),
        "events": results,
        "started_at": started_at,
        "completed_at": now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    args = parser.parse_args()
    if args.receipt.exists() or args.receipt.is_symlink():
        parser.error(f"Refusing to overwrite {args.receipt}")
    receipt = run(args)
    write_json_create_only(args.receipt, receipt)
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
