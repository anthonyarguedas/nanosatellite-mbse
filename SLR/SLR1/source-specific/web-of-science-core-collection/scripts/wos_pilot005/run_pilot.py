#!/usr/bin/env python3
"""Run the predeclared Web of Science Pilot 005 wildcard events."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping

from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, load, sha256_file, validate

SCHEMA = "wos-broad-wildcard-pilot-run/v1"
SCREENSHOT_SCHEMA = "web-of-science-automatic-screenshots/v1"
OUTPUT = PILOT_ROOT / "searches" / "run-receipt.json"


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    stem = output.name[:-5] if output.name.lower().endswith(".json") else output.name
    return (
        output.with_name(f"{stem}.search-page.png"),
        output.with_name(f"{stem}.results-page.png"),
    )


def artifact_summary(output: Path, event: Mapping[str, Any]) -> dict[str, Any]:
    if not output.is_file():
        return {"valid": False, "artifact_written": False}
    artifact = load(output)
    metadata = artifact.get("output_metadata")
    rows = artifact.get("results")
    if not isinstance(metadata, Mapping) or not isinstance(rows, list):
        return {"valid": False, "artifact_written": True}
    ids = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ]
    prisma = metadata.get("prisma_search_run")
    staged = prisma.get("staged_counts", {}) if isinstance(prisma, Mapping) else {}
    native = prisma.get("native_artifact", {}) if isinstance(prisma, Mapping) else {}
    screenshots = metadata.get("screenshots")
    shot_checks = []
    for key, path in zip(("search_page", "results_page"), screenshot_paths(output)):
        evidence = screenshots.get(key, {}) if isinstance(screenshots, Mapping) else {}
        shot_checks.append(
            path.is_file()
            and evidence.get("path") == path.name
            and evidence.get("sha256") == hashlib.sha256(path.read_bytes()).hexdigest()
            and isinstance(evidence.get("width"), int)
            and evidence.get("width") > 0
            and isinstance(evidence.get("height"), int)
            and evidence.get("height") > 0
        )
    valid = bool(
        artifact.get("schema_version") == "academic-search-result/v1"
        and artifact.get("executed_query") == event.get("query")
        and isinstance(artifact.get("total"), int)
        and artifact.get("total") == len(rows) == len(ids) == len(set(ids))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and isinstance(prisma, Mapping)
        and prisma.get("completion_status") == "complete"
        and prisma.get("report_ready") is True
        and prisma.get("phase") == "pilot"
        and prisma.get("adapter", {}).get("adapter_version") == "2"
        and prisma.get("strategy", {}).get("executed_query") == event.get("query")
        and staged.get("source_reported_total") == artifact.get("total")
        and staged.get("raw_source_records") == len(ids)
        and staged.get("records_exported") == len(ids)
        and native.get("format") == "RIS"
        and native.get("record_count") == len(ids)
        and isinstance(screenshots, Mapping)
        and screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
        and screenshots.get("complete") is True
        and all(shot_checks)
    )
    return {
        "artifact_written": True,
        "valid": valid,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "total": artifact.get("total"),
        "stable_id_count": len(ids),
        "ordered_wos_ids_sha256": hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest(),
        "screenshot_count": sum(shot_checks),
    }


def command(event: Mapping[str, Any], output: Path, cdp_url: str, attempt: int) -> list[str]:
    partition_id = str(event["partition_id"])
    return [
        "uv", "run", str(ADAPTER),
        "--raw-query", str(event["query"]),
        "--limit", "2000",
        "--max-pages", "40",
        "--timeout", "120",
        "--page-delay-seconds", "0.25",
        "--require-complete",
        "--cdp-url", cdp_url,
        "--output-path", str(output),
        "--prisma-run-id", f"pilot-wos-005-{partition_id}-attempt-{attempt:02d}",
        "--prisma-review-id", "slr1-pilot-005",
        "--prisma-strategy-reference", "slr1-wos-broad-wildcard-v1",
        "--prisma-strategy-version", str(event.get("protocol_commit", "3194156e90497186664260a8e86435e78d2e2aa1")),
        "--prisma-phase", "pilot",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", partition_id,
        "--prisma-partition-label", partition_id,
        "--prisma-partition-description", f"Web of Science Pilot 005 broad wildcard {partition_id}",
    ]


def safe_tail(value: str) -> str:
    return value.replace(str(Path.home()), "~")[-3000:] or "(no adapter output)"


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if os.path.lexists(OUTPUT):
        raise SystemExit(f"Refusing to overwrite {OUTPUT}")
    plan = load(DEFAULT_OUTPUT)
    errors = validate(plan)
    if errors or plan.get("adapter", {}).get("sha256") != sha256_file(ADAPTER):
        raise SystemExit("Plan or adapter binding changed: " + "; ".join(errors))
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise SystemExit("Pilot 005 requires a loopback browser endpoint")

    outcomes: list[dict[str, Any]] = []
    selected: dict[str, str] = {}
    stopped = False
    for event_index, event in enumerate(plan["events"]):
        if event_index:
            time.sleep(2)
        succeeded = False
        for attempt, relative in enumerate(event["attempt_outputs"], start=1):
            output = PILOT_ROOT / "searches" / relative
            occupied = (output, *screenshot_paths(output))
            if any(os.path.lexists(path) for path in occupied):
                raise SystemExit(f"Refusing to overwrite {output}")
            completed = subprocess.run(
                command(event, output, cdp_url, attempt),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            summary = artifact_summary(output, event)
            outcome = {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "attempt": attempt,
                "artifact": str(output.relative_to(PILOT_ROOT)),
                "exit_code": completed.returncode,
                **summary,
            }
            if completed.returncode != 0 or summary.get("valid") is not True:
                outcome["adapter_stderr_tail"] = safe_tail(completed.stderr)
            outcomes.append(outcome)
            print(json.dumps({"event": event["event_id"], "attempt": attempt, "exit_code": completed.returncode, "total": summary.get("total"), "valid": summary.get("valid")}), flush=True)
            if completed.returncode == 0 and summary.get("valid") is True:
                selected[event["partition_id"]] = outcome["artifact"]
                succeeded = True
                break
            # Retry only explicit record-free failures.
            try:
                failed = load(output)
            except (OSError, TypeError, ValueError, json.JSONDecodeError):
                failed = {}
            if failed.get("total") is not None:
                break
            time.sleep(10)
        if not succeeded:
            stopped = True
            break

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "Web of Science Core Collection",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(DEFAULT_OUTPUT.relative_to(PILOT_ROOT)),
        "plan_sha256": sha256_file(DEFAULT_OUTPUT),
        "adapter": {"id": "search_web_of_science", "version": "2", "sha256": sha256_file(ADAPTER)},
        "planned_event_count": 9,
        "successful_event_count": len(selected),
        "attempt_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": not stopped and len(selected) == 9,
        "selected_artifacts": selected,
        "outcomes": outcomes,
    }
    write_create_only(OUTPUT, receipt)
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
