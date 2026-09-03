#!/usr/bin/env python3
"""Run the predeclared final Web of Science prior-secondary-review events once."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "slr1-wos-final-psr-run/v1"
PLAN_SCHEMA = "slr1-wos-final-psr-plan/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_web_of_science.py"
WOS_ADVANCED_URL = "https://www.webofscience.com/wos/woscc/advanced-search"
SCREENSHOT_SCHEMA = "web-of-science-automatic-screenshots/v1"
PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sequence_digest(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def screenshot_evidence(path: Path, screenshots: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    valid = True
    rows: list[dict[str, Any]] = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshots.get(key, {})
        image_valid = bool(
            image.is_file()
            and image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            and evidence.get("path") == image.name
            and evidence.get("sha256") == digest(image)
            and isinstance(evidence.get("width"), int)
            and evidence["width"] > 0
            and isinstance(evidence.get("height"), int)
            and evidence["height"] > 0
            and evidence.get("browser_chrome_captured") is False
            and evidence.get("complete_page_url_retained") is False
            and evidence.get("session_identifiers_retained") is False
        )
        valid = valid and image_valid
        rows.append(
            {
                "kind": key,
                "path": image.name,
                "sha256": digest(image) if image.is_file() else None,
                "valid": image_valid,
            }
        )
    return valid, rows


def controls_valid(value: dict[str, Any], event: dict[str, Any], plan: dict[str, Any]) -> bool:
    metadata = value.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {})
    strategy = run.get("strategy", {})
    limits = strategy.get("limits", {})
    scope = strategy.get("search_scope", {})
    scope_controls = scope.get("controls", {})
    database = scope_controls.get("database", {})
    editions = scope_controls.get("editions", {})
    sort = strategy.get("sort", {})
    total = value.get("total")
    positive_sort_valid = bool(
        sort.get("state") == "applied"
        and sort.get("value") == "Date: oldest first"
    )
    zero_sort_valid = bool(
        total == 0
        and sort.get("state") == "unknown"
        and sort.get("requested") == "Date: oldest first"
    )
    return bool(
        run.get("review_id") == plan.get("review_id")
        and run.get("strategy_reference") == plan.get("strategy_reference")
        and run.get("strategy_version") == event.get("strategy_version")
        and run.get("phase") == plan.get("phase")
        and run.get("coverage", {}).get("coverage_scope") == "partition"
        and run.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and value.get("executed_query") == event.get("query")
        and strategy.get("executed_query") == event.get("query")
        and strategy.get("query_fields") == ["TS", "PY"]
        and strategy.get("executed_query_provenance") == "source_observed"
        and scope.get("database") == "Web of Science Core Collection"
        and scope.get("editions_requested") == ["All"]
        and database.get("state") == "applied"
        and database.get("effective") == "Web of Science Core Collection"
        and editions.get("state") == "applied"
        and editions.get("requested") == ["All"]
        and isinstance(editions.get("effective"), list)
        and len(editions["effective"]) > 0
        and limits.get("language", {}).get("state") == "not_applied"
        and limits.get("publication_year", {}).get("state") == "not_applied"
        and limits.get("document_type", {}).get("state") == "not_applied"
        and limits.get("document_types", {}).get("state") == "not_applied"
        and (positive_sort_valid or zero_sort_valid)
    )


def native_ris_valid(path: Path, value: dict[str, Any], event: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    metadata = value.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {})
    native = run.get("native_artifact")
    total = value.get("total")
    ris_path = path.with_name(event["native_ris_filename"])
    if total == 0:
        return native is None and not ris_path.exists(), None
    if not isinstance(total, int) or total < 1 or not isinstance(native, dict):
        return False, None
    valid = bool(
        ris_path.is_file()
        and native.get("schema_version") == "academic-search-native-artifact/v1"
        and native.get("format") == "RIS"
        and native.get("digest_algorithm") == "sha256"
        and native.get("sha256") == digest(ris_path)
        and native.get("byte_count") == ris_path.stat().st_size
        and native.get("record_count") == total
        and native.get("record_count_provenance") == "framed_native_file_parse"
        and native.get("pages_exported") == math.ceil(total / 50)
        # The adapter deliberately keeps its normalized receipt path-free.
        # A verified caller-side RIS file proves this sidecar was retained.
        and native.get("local_path_persisted") is False
    )
    return valid, {
        "path": ris_path.name,
        "sha256": digest(ris_path) if ris_path.is_file() else None,
        "bytes": ris_path.stat().st_size if ris_path.is_file() else None,
        "record_count": native.get("record_count"),
        "valid": valid,
    }


def committed_artifact_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not marker.is_file():
        return False
    try:
        receipt = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    normalized = receipt.get("normalized_json", {})
    return bool(
        normalized.get("sha256") == digest(path)
        and normalized.get("bytes") == path.stat().st_size
    )


def summarize(path: Path, event: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        return {"valid": False, "artifact_written": False}
    try:
        value = load(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "valid": False,
            "artifact_written": True,
            "parse_error": type(error).__name__,
        }
    metadata = value.get("output_metadata", {})
    run = metadata.get("prisma_search_run", {})
    screenshots = metadata.get("screenshots", {})
    screenshot_valid, image_rows = screenshot_evidence(path, screenshots)
    controls_ok = controls_valid(value, event, plan)
    records = value.get("results", [])
    ids = [
        row.get("paperId")
        for row in records
        if isinstance(row, dict) and isinstance(row.get("paperId"), str)
    ]
    total = value.get("total")
    staging = run.get("staged_counts", {})
    completeness_ok = bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == "Web of Science Core Collection"
        and isinstance(total, int)
        and total >= 0
        and total == len(records) == len(ids) == len(set(ids))
        and all(identifier.startswith("WOS:") for identifier in ids)
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and run.get("completion_status") == "complete"
        and run.get("report_ready") is True
        and run.get("report_readiness_reasons") == []
        and staging.get("source_reported_total") == total
        and staging.get("source_reported_total_exact") is True
        and staging.get("raw_source_records") == total
        and staging.get("records_exported") == total
    )
    adapter = run.get("adapter", {})
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    native_ok, native_row = native_ris_valid(path, value, event)
    marker_ok = committed_artifact_valid(path)
    screenshot_receipt_ok = bool(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("no_opt_out") is True
        and screenshots.get("same_directory_as_json") is True
        and screenshots.get("complete") is True
        and screenshot_valid
    )
    return {
        "valid": bool(
            controls_ok
            and completeness_ok
            and adapter_ok
            and native_ok
            and screenshot_receipt_ok
            and marker_ok
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "total": total,
        "stable_id_count": len(set(ids)),
        "ordered_wos_ids_sha256": sequence_digest(ids),
        "controls_valid": controls_ok,
        "completion_valid": completeness_ok,
        "adapter_binding_valid": adapter_ok,
        "native_ris_valid": native_ok,
        "native_ris": native_row,
        "screenshots_valid": screenshot_receipt_ok,
        "terminal_marker_valid": marker_ok,
        "screenshots": image_rows,
    }


def command(event: dict[str, Any], output: Path, cdp_url: str, target_id: str, plan: dict[str, Any]) -> list[str]:
    ris_path = output.with_name(event["native_ris_filename"])
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--raw-query",
        event["query"],
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--require-complete",
        "--ris-output-path",
        str(ris_path),
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
        "--output-path",
        str(output),
        "--prisma-run-id",
        event["event_id"],
        "--prisma-review-id",
        plan["review_id"],
        "--prisma-strategy-reference",
        plan["strategy_reference"],
        "--prisma-strategy-version",
        event["strategy_version"],
        "--prisma-phase",
        plan["phase"],
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["partition_id"],
        "--prisma-partition-label",
        event["partition_id"],
        "--prisma-partition-description",
        f"Web of Science final prior-secondary-review {event['partition_id']} discovery partition",
    ]


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def create_ephemeral_wos_target(cdp_url: str, timeout_seconds: float = 45.0) -> str:
    encoded = urllib.parse.quote(WOS_ADVANCED_URL, safe="")
    created = cdp_json(cdp_url, f"/json/new?{encoded}", method="PUT")
    target_id = created.get("id") if isinstance(created, dict) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not return one explicit Web of Science target")
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        targets = cdp_json(cdp_url, "/json/list")
        target = next(
            (
                item
                for item in targets
                if isinstance(item, dict) and item.get("id") == target_id
            ),
            None,
        )
        if isinstance(target, dict):
            parsed = urllib.parse.urlparse(target.get("url", ""))
            if (
                target.get("type") == "page"
                and parsed.scheme == "https"
                and parsed.hostname in {"webofscience.com", "www.webofscience.com"}
            ):
                return target_id
        time.sleep(0.5)
    raise RuntimeError("The fresh Web of Science target did not become ready")


def close_ephemeral_target(cdp_url: str, target_id: str) -> bool:
    try:
        with urllib.request.urlopen(
            f"{cdp_url.rstrip('/')}/json/close/{target_id}", timeout=10
        ) as response:
            response.read()
    except Exception:
        return False
    return True


def verify_plan_bindings(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if digest(ADAPTER) != plan.get("adapter", {}).get("sha256"):
        errors.append("adapter_changed")
    bindings = plan.get("bindings", {})
    query = bindings.get("query_snapshot", {})
    query_path = REPOSITORY_ROOT / query.get("path", "")
    if not query_path.is_file() or digest(query_path) != query.get("sha256"):
        errors.append("query_snapshot_changed")
    for relative, expected in bindings.get("source_affecting_scripts", {}).items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest(path) != expected:
            errors.append(f"source_script_changed:{relative}")
    for relative, expected in bindings.get("protocols", {}).items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest(path) != expected:
            errors.append(f"protocol_changed:{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--settle-seconds", type=float, default=5.0)
    args = parser.parse_args()
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise SystemExit("Final Web of Science PSR execution requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected final WoS PSR plan schema")
    events = plan.get("events")
    if (
        not isinstance(events, list)
        or [event.get("partition_id") for event in events] != list(PARTITIONS)
    ):
        raise SystemExit("Final WoS PSR plan must contain PSR1 through PSR4 once")
    binding_errors = verify_plan_bindings(plan)
    if binding_errors:
        raise SystemExit("Plan binding failure: " + ", ".join(binding_errors))
    if args.output_dir.is_symlink():
        raise SystemExit("The final WoS PSR output directory may not be a symlink")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(events):
        if index and args.settle_seconds:
            time.sleep(args.settle_seconds)
        output = args.output_dir / event["output_filename"]
        ris_path = args.output_dir / event["native_ris_filename"]
        occupied = (output, ris_path, *screenshot_paths(output), marker_path(output))
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise SystemExit(
                f"Refusing to overwrite final {event['partition_id']} artifact"
            )
        try:
            target_id = create_ephemeral_wos_target(cdp_url)
        except Exception as error:
            outcome = {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "success": False,
                "artifact": None,
                "exit_code": None,
                "attempt_count": 0,
                "runner_failure": "ephemeral_target_creation_failed",
                "runner_failure_class": type(error).__name__,
                "source_execution_not_started": True,
                "target_identifier_retained": False,
            }
            outcomes.append(outcome)
            print(json.dumps({"partition": event["partition_id"], "success": False, "runner_failure": outcome["runner_failure"]}), flush=True)
            continue
        time.sleep(3)
        try:
            completed = subprocess.run(
                command(event, output, cdp_url, target_id, plan),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            summary = summarize(output, event, plan)
            exit_code: int | None = completed.returncode
        except Exception as error:
            summary = {
                "valid": False,
                "artifact_written": output.is_file(),
                "runner_failure": "subprocess_or_summary_failed",
                "runner_failure_class": type(error).__name__,
            }
            exit_code = None
        finally:
            target_close_requested = close_ephemeral_target(cdp_url, target_id)
        success = bool(exit_code == 0 and summary.get("valid") is True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": success,
            "artifact": output.name if output.is_file() else None,
            "native_ris_artifact": ris_path.name if ris_path.is_file() else None,
            "exit_code": exit_code,
            "attempt_count": 1,
            "ephemeral_target_created": True,
            "ephemeral_target_close_requested": target_close_requested,
            "target_identifier_retained": False,
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "success": success,
                    "exit_code": exit_code,
                    "total": outcome.get("total"),
                    "native_ris_valid": outcome.get("native_ris_valid"),
                }
            ),
            flush=True,
        )

    success = bool(
        len(outcomes) == len(events)
        and all(outcome.get("success") is True for outcome in outcomes)
    )
    receipt = {
        "schema_version": SCHEMA,
        "source": "Web of Science Core Collection",
        "source_id": "web_of_science_core_collection",
        "review_namespace": "prior_secondary_reviews",
        "event_kind": "final",
        "plan": args.plan.name,
        "plan_sha256": digest(args.plan),
        "adapter": plan["adapter"],
        "target_identifier_retained": False,
        "execution_policy": plan["execution_policy"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(events),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": sum(
            outcome.get("attempt_count", 0) for outcome in outcomes
        ),
        "accepted_event_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "all_partitions_attempted": len(outcomes) == len(events),
        "success": success,
        "outcomes": outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
