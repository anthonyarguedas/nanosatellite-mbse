#!/usr/bin/env python3
"""Run the predeclared Web of Science Pilot 004 source events."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Mapping

from build_plan import (
    ADAPTER,
    DEFAULT_OUTPUT,
    PILOT_ROOT,
    SCHEMA as PLAN_SCHEMA,
    file_sha256,
    load,
    validate,
)

SCHEMA = "wos-current-schedule-wildcard-pilot-run/v1"
SCREENSHOT_SCHEMA = "web-of-science-automatic-screenshots/v1"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_tail(value: str) -> str:
    cleaned = value.replace(str(Path.home()), "~")
    return cleaned[-3000:] or "(no adapter output)"


def screenshot_paths(output: Path) -> dict[str, Path]:
    stem = output.name[:-5] if output.name.lower().endswith(".json") else output.name
    return {
        "search_page": output.with_name(f"{stem}.search-page.png"),
        "results_page": output.with_name(f"{stem}.results-page.png"),
    }


def artifact_summary(path: Path, event: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact_written": False, "valid": False}
    artifact = load(path)
    metadata = artifact.get("output_metadata")
    rows = artifact.get("results")
    if not isinstance(metadata, Mapping) or not isinstance(rows, list):
        return {"artifact_written": True, "valid": False}
    ids = [
        row.get("paperId")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("paperId"), str)
    ]
    screenshots = metadata.get("screenshots")
    screenshot_checks: dict[str, Any] = {}
    for key, image in screenshot_paths(path).items():
        evidence = screenshots.get(key, {}) if isinstance(screenshots, Mapping) else {}
        exists = image.is_file()
        digest = hashlib.sha256(image.read_bytes()).hexdigest() if exists else None
        screenshot_checks[key] = {
            "path": str(image),
            "exists": exists,
            "receipt_path_matches": evidence.get("path") == image.name,
            "receipt_hash_matches": exists and evidence.get("sha256") == digest,
            "width": evidence.get("width"),
            "height": evidence.get("height"),
        }
    prisma = metadata.get("prisma_search_run")
    staged = prisma.get("staged_counts", {}) if isinstance(prisma, Mapping) else {}
    strategy = prisma.get("strategy", {}) if isinstance(prisma, Mapping) else {}
    native = prisma.get("native_artifact", {}) if isinstance(prisma, Mapping) else {}
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
        and prisma.get("report_readiness_reasons") == []
        and prisma.get("phase") == "pilot"
        and prisma.get("adapter", {}).get("adapter_id") == "search_web_of_science"
        and prisma.get("adapter", {}).get("adapter_version") == "2"
        and strategy.get("executed_query") == event.get("query")
        and staged.get("source_reported_total") == artifact.get("total")
        and staged.get("source_reported_total_exact") is True
        and staged.get("raw_source_records") == len(ids)
        and staged.get("records_exported") == len(ids)
        and native.get("format") == "RIS"
        and native.get("record_count") == len(ids)
        and screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
        and screenshots.get("same_directory_as_json") is True
        and screenshots.get("complete") is True
        and all(
            check["exists"]
            and check["receipt_path_matches"]
            and check["receipt_hash_matches"]
            and isinstance(check["width"], int)
            and check["width"] > 0
            and isinstance(check["height"], int)
            and check["height"] > 0
            for check in screenshot_checks.values()
        )
    )
    return {
        "artifact_written": True,
        "valid": valid,
        "status": metadata.get("status"),
        "total": artifact.get("total"),
        "stable_id_count": len(ids),
        "ordered_wos_ids_sha256": hashlib.sha256(
            "\n".join(ids).encode("utf-8")
        ).hexdigest(),
        "screenshots": screenshot_checks,
    }


def command_for(
    event: Mapping[str, Any], *, output: Path, cdp_url: str
) -> list[str]:
    event_id = str(event["event_id"])
    partition_id = str(event["partition_id"])
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--raw-query",
        str(event["query"]),
        "--limit",
        "2000",
        "--max-pages",
        "40",
        "--timeout",
        "120",
        "--page-delay-seconds",
        "0.25",
        "--require-complete",
        "--cdp-url",
        cdp_url,
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"pilot-wos-004-{event_id}",
        "--prisma-review-id",
        "slr1-pilot-004",
        "--prisma-strategy-reference",
        "slr1-wos-current-schedule-wildcard-v1",
        "--prisma-strategy-version",
        str(event.get("protocol_commit", "3194156e90497186664260a8e86435e78d2e2aa1")),
        "--prisma-phase",
        "pilot",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition_id,
        "--prisma-partition-label",
        partition_id,
        "--prisma-partition-description",
        f"Web of Science Pilot 004 {partition_id} {event['variant']}",
    ]


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--settle-seconds", type=float, default=1.0)
    args = parser.parse_args()

    if args.settle_seconds < 0:
        raise SystemExit("--settle-seconds cannot be negative")
    if not ADAPTER.is_file():
        raise SystemExit(f"Web of Science adapter is missing: {ADAPTER}")
    if os.path.lexists(args.receipt):
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise SystemExit("Pilot 004 requires a loopback browser endpoint")

    plan = load(args.plan)
    errors = validate(plan)
    if plan.get("schema_version") != PLAN_SCHEMA or errors:
        raise SystemExit("Invalid predeclared plan: " + "; ".join(errors))
    if file_sha256(ADAPTER) != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The Web of Science adapter changed after predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 18:
        raise SystemExit("Pilot 004 requires exactly 18 predeclared events")

    started = now()
    outcomes: list[dict[str, Any]] = []
    stopped = False
    for index, event in enumerate(events):
        if index and args.settle_seconds:
            import time

            time.sleep(args.settle_seconds)
        output = args.pilot_root / "searches" / str(event["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        occupied = [output, *screenshot_paths(output).values()]
        resumed = any(os.path.lexists(path) for path in occupied)
        if resumed:
            summary = artifact_summary(output, event)
            if summary.get("valid") is not True:
                raise SystemExit(
                    f"Refusing to overwrite an incomplete event artifact for {event['event_id']}"
                )
            return_code = 0
            stderr = ""
        else:
            completed = subprocess.run(
                command_for(event, output=output, cdp_url=cdp_url),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            return_code = completed.returncode
            stderr = completed.stderr
            summary = artifact_summary(output, event)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "variant": event["variant"],
            "exit_code": return_code,
            "resumed_preexisting_valid_event": resumed,
            "artifact": str(output.relative_to(args.pilot_root)),
            **summary,
        }
        if return_code != 0 or summary.get("valid") is not True:
            outcome["adapter_stderr_tail"] = safe_tail(stderr)
            stopped = True
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "event": event["event_id"],
                    "exit_code": return_code,
                    "total": summary.get("total"),
                    "valid": summary.get("valid"),
                }
            ),
            flush=True,
        )
        if stopped:
            break

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Web of Science Core Collection",
        "protocol_commit": plan.get("protocol_commit"),
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": file_sha256(args.plan),
        "adapter": {
            "id": "search_web_of_science",
            "version": plan.get("adapter", {}).get("version"),
            "sha256": file_sha256(ADAPTER),
        },
        "browser_target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "completed_event_count": len(outcomes),
        "stopped_after_failure": stopped,
        "success": not stopped and len(outcomes) == len(events),
        "outcomes": outcomes,
    }
    write_create_only(args.receipt, receipt)
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
