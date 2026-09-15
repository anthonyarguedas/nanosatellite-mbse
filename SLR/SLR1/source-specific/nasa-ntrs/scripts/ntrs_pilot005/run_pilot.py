#!/usr/bin/env python3
"""Execute the predeclared NASA NTRS Pilot 005 with null-only retries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ntrs-repaired-post-proximity-wildcard-pilot-run/v1"
PLAN_SCHEMA = "ntrs-repaired-post-proximity-wildcard-pilot-plan/v1"
SCREENSHOT_SCHEMA = "ntrs-automatic-screenshots/v1"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ntrs.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.NTRS_COMMIT.json")


def screenshot_paths(path: Path) -> dict[str, Path]:
    return {
        "search_page": path.with_name(f"{path.stem}.search-page.png"),
        "results_page": path.with_name(f"{path.stem}.results-page.png"),
    }


def ordered_id_hash(ids: list[str]) -> str:
    result = hashlib.sha256()
    for stable_id in ids:
        encoded = stable_id.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


def artifact_summary(path: Path, event: dict[str, Any], adapter_hash: str) -> dict[str, Any]:
    if not path.is_file():
        return {"artifact_written": False, "valid": False, "retryable": False}
    value = load(path)
    metadata = value.get("output_metadata", {})
    records = value.get("results", [])
    ids = [
        row.get("paperId")
        for row in records
        if isinstance(row, dict) and isinstance(row.get("paperId"), str)
    ]
    prisma = metadata.get("prisma_search_run", {}) if isinstance(metadata, dict) else {}
    strategy = prisma.get("strategy", {}) if isinstance(prisma, dict) else {}
    limits = strategy.get("limits", {}) if isinstance(strategy, dict) else {}
    publication = limits.get("publication_date", {}) if isinstance(limits, dict) else {}
    screenshots = metadata.get("screenshots", {}) if isinstance(metadata, dict) else {}
    screenshot_checks = {}
    for key, image in screenshot_paths(path).items():
        receipt = screenshots.get(key, {}) if isinstance(screenshots, dict) else {}
        exists = image.is_file()
        screenshot_checks[key] = {
            "path": str(image),
            "exists": exists,
            "receipt_path_matches": receipt.get("path") == image.name,
            "receipt_hash_matches": exists and receipt.get("sha256") == digest(image),
            "width": receipt.get("width"),
            "height": receipt.get("height"),
        }
    marker_file = marker_path(path)
    marker = load(marker_file) if marker_file.is_file() else {}
    success_valid = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == "NASA Technical Reports Server (NTRS)"
        and value.get("executed_query") == event["query"]
        and isinstance(value.get("total"), int)
        and value.get("total") == len(records) == len(ids) == len(set(ids))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and prisma.get("completion_status") == "complete"
        and prisma.get("adapter", {}).get("script_sha256") == adapter_hash
        and strategy.get("sort", {}).get("value") == "Publication Date (Oldest)"
        and publication.get("state") == "applied"
        and publication.get("value", {}).get("gte") == "2011-01-01"
        and publication.get("value", {}).get("lte") == "2026-08-29"
        and screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
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
        and marker.get("schema") == "ntrs_output_commit_marker_v1"
        and marker.get("normalized_json", {}).get("sha256") == digest(path)
        and marker.get("normalized_json", {}).get("bytes") == path.stat().st_size
    )
    retryable = bool(
        value.get("total") is None
        and records == []
        and metadata.get("status") == "error"
        and metadata.get("merge_eligible") is False
    )
    return {
        "artifact_written": True,
        "valid": success_valid,
        "retryable": retryable,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "total": value.get("total"),
        "stable_id_count": len(ids),
        "ordered_stable_ids_sha256": ordered_id_hash(ids),
        "marker": str(marker_file),
        "screenshots": screenshot_checks,
    }


def command_for(
    event: dict[str, Any], *, attempt: int, output: Path, cdp_url: str
) -> list[str]:
    event_id = event["event_id"]
    partition = event["partition_id"]
    return [
        "uv", "run", str(ADAPTER),
        "--query", event["query"],
        "--date-start", "2011-01-01",
        "--date-end", "2026-08-29",
        "--page-size", "100",
        "--limit", "10000",
        "--max-pages", "100",
        "--timeout", "240",
        "--page-delay-seconds", "0",
        "--detail-delay-seconds", "0",
        "--skip-full-abstracts",
        "--require-complete",
        "--cdp-url", cdp_url,
        "--output-path", str(output),
        "--prisma-run-id", f"pilot-ntrs-005-{event_id}-attempt{attempt}",
        "--prisma-review-id", "slr1-ntrs-pilot005",
        "--prisma-strategy-reference", "slr1-ntrs-post-proximity-wildcard-v1",
        "--prisma-strategy-version", event["protocol_commit"],
        "--prisma-phase", "pilot",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", partition,
        "--prisma-partition-label", partition,
        "--prisma-partition-description",
        f"NASA NTRS Pilot 005 {event_id} attempt {attempt}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--settle-seconds", type=float, default=3.0)
    args = parser.parse_args()
    if args.settle_seconds < 0:
        raise SystemExit("--settle-seconds cannot be negative")
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", cdp_url):
        raise SystemExit("Pilot 005 requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected Pilot 005 plan schema")
    adapter_hash = digest(ADAPTER)
    if adapter_hash != plan.get("adapter", {}).get("sha256"):
        raise SystemExit("The NTRS adapter changed after predeclaration")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != 18:
        raise SystemExit("Pilot 005 requires exactly 18 semantic events")

    started = now()
    event_outcomes: list[dict[str, Any]] = []
    source_attempt_count = 0
    stopped = False
    for event in events:
        attempts = []
        accepted_artifact: str | None = None
        for attempt, output_name in enumerate(event["attempt_outputs"], start=1):
            if source_attempt_count:
                time.sleep(args.settle_seconds)
            output = args.pilot_root / "searches" / output_name
            output.parent.mkdir(parents=True, exist_ok=True)
            occupied = [output, marker_path(output), *screenshot_paths(output).values()]
            if any(path.exists() or path.is_symlink() for path in occupied):
                raise SystemExit(
                    f"Refusing to overwrite attempt {attempt} for {event['event_id']}"
                )
            completed = subprocess.run(
                command_for(event, attempt=attempt, output=output, cdp_url=cdp_url),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=360,
            )
            source_attempt_count += 1
            summary = artifact_summary(output, event, adapter_hash)
            row = {
                "attempt": attempt,
                "exit_code": completed.returncode,
                "artifact": str(output.relative_to(args.pilot_root)),
                "stderr_sha256": hashlib.sha256(
                    completed.stderr.encode("utf-8")
                ).hexdigest(),
                "stderr_bytes": len(completed.stderr.encode("utf-8")),
                "screenshot_files_written": {
                    key: path.is_file() for key, path in screenshot_paths(output).items()
                },
                **summary,
            }
            attempts.append(row)
            print(
                json.dumps(
                    {
                        "event": event["event_id"],
                        "attempt": attempt,
                        "exit_code": completed.returncode,
                        "total": summary.get("total"),
                        "valid": summary.get("valid"),
                        "retryable": summary.get("retryable"),
                    }
                ),
                flush=True,
            )
            if completed.returncode == 0 and summary["valid"]:
                accepted_artifact = row["artifact"]
                break
            if not summary["retryable"]:
                break
        success = accepted_artifact is not None
        event_outcomes.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "variant": event["variant"],
                "success": success,
                "accepted_artifact": accepted_artifact,
                "attempt_count": len(attempts),
                "attempts": attempts,
            }
        )
        if not success:
            stopped = True
            break

    receipt = {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "NASA Technical Reports Server (NTRS)",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "adapter": {
            "id": "search_ntrs",
            "version": plan.get("adapter", {}).get("version"),
            "sha256": adapter_hash,
        },
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "completed_event_count": len(event_outcomes),
        "source_attempt_count": source_attempt_count,
        "stopped_after_failure": stopped,
        "success": not stopped and len(event_outcomes) == len(events),
        "events": event_outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
