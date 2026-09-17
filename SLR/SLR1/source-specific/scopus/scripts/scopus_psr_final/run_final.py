#!/usr/bin/env python3
"""Run the predeclared corrective Scopus prior-secondary-review events once."""

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

SCHEMA = "slr1-scopus-final-psr-run/v2"
PLAN_SCHEMA = "slr1-scopus-final-psr-plan/v2"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
SCOPUS_ADVANCED_URL = "https://www.scopus.com/pages/search/publications?type=advanced"
STRICT_SCHEMA = "academic-search-scopus-strict-two-pass/v2"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"
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


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def expected_executed_query(query: str) -> str:
    return f"({query}) AND PUBYEAR < 2027"


def screenshot_evidence(path: Path, screenshots: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    valid = True
    rows: list[dict[str, Any]] = []
    for key, image in zip(("search_page", "results_page"), screenshot_paths(path)):
        evidence = screenshots.get(key, {})
        image_valid = bool(
            image.is_file()
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
    year = limits.get("year_interval", {})
    facets = limits.get("result_facets", {})
    search_within = limits.get("search_within", {})
    scope = strategy.get("search_scope", {})
    sort = strategy.get("sort", {})
    total = value.get("total")
    positive_sort_valid = bool(
        sort.get("state") == "applied"
        and sort.get("value", {}).get("value") == "plf-t"
        and sort.get("value", {}).get("label") == "Date (oldest)"
    )
    zero_sort_valid = bool(total == 0 and sort.get("state") == "not_applicable")
    return bool(
        run.get("review_id") == plan.get("review_id")
        and run.get("strategy_reference") == plan.get("strategy_reference")
        and run.get("strategy_version") == event.get("strategy_version")
        and run.get("phase") == plan.get("phase")
        and run.get("coverage", {}).get("coverage_scope") == "partition"
        and run.get("coverage", {}).get("partition_id") == event.get("partition_id")
        and strategy.get("requested_query") == event.get("query")
        and value.get("requested_query") == event.get("query")
        and value.get("executed_query") == expected_executed_query(event.get("query", ""))
        and strategy.get("executed_query") == value.get("executed_query")
        and "PUBYEAR >" not in value.get("executed_query", "").upper()
        and year.get("state") == "applied"
        and year.get("value", {}).get("start") is None
        and year.get("value", {}).get("end") == 2026
        and year.get("value", {}).get("inclusive") is True
        and search_within.get("state") == "not_applied"
        and facets.get("state") == "not_applied"
        and facets.get("requested") in (None, [])
        and facets.get("effective") in (None, [])
        and scope.get("tab_id") == "s"
        and scope.get("label") == "Documents"
        and (positive_sort_valid or zero_sort_valid)
    )


def strict_receipt_valid(value: dict[str, Any], event: dict[str, Any]) -> bool:
    metadata = value.get("output_metadata", {})
    receipt = metadata.get("strict_two_pass_receipt", {})
    records = value.get("results", [])
    total = value.get("total")
    ids = [
        record.get("paperId")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("paperId"), str)
    ]
    reports = receipt.get("pass_reports", [])
    if not isinstance(total, int) or total < 0:
        return False
    if not isinstance(reports, list) or len(reports) != 2:
        return False
    expected_pages = math.ceil(total / event["page_size"]) if total else 0
    for number, report in enumerate(reports, 1):
        if not isinstance(report, dict):
            return False
        if not bool(
            report.get("pass_number") == number
            and report.get("complete") is True
            and report.get("native_query_readback_observed") is True
            and report.get("source_reported_total") == total
            and report.get("source_entries_traversed") == total
            and report.get("normalized_records_retrieved") == total
            and report.get("stable_id_set_sha256")
            == receipt.get("stable_id_set_sha256")
        ):
            return False
        if total > 0 and (
            report.get("pages_retrieved") != expected_pages
            or report.get("expected_page_count") != expected_pages
            or report.get("page_size") != event["page_size"]
            or report.get("scope_id") != "s"
            or report.get("sort_value") != "plf-t"
        ):
            return False
        if total == 0 and report.get("pages_retrieved") not in (0, None):
            return False
    return bool(
        value.get("schema_version") == "academic-search-result/v1"
        and value.get("source") == "Scopus"
        and value.get("requested_query") == event.get("query")
        and total == len(records) == len(ids) == len(set(ids))
        and metadata.get("status") == "success"
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and receipt.get("schema_version") == STRICT_SCHEMA
        and receipt.get("status") == "success"
        and receipt.get("strict_completion") is True
        and receipt.get("strict_stable_id_sets_reconciled") is True
        and receipt.get("strict_record_id_sets_reconciled") is True
        and receipt.get("strict_publication_id_sets_reconciled") is True
        and receipt.get("strict_total_reconciled") is True
        and receipt.get("two_pass_set_verified") is True
        and receipt.get("two_pass_total_verified") is True
        and isinstance(receipt.get("two_pass_order_verified"), bool)
        and isinstance(receipt.get("order_difference_count"), int)
        and receipt.get("order_difference_count") >= 0
        and receipt.get("source_reported_total") == total
        and receipt.get("source_entries_retrieved") == total
        and receipt.get("records_exported") == total
        and receipt.get("stable_id_set_sha256")
        == receipt.get("record_id_set_sha256")
        == receipt.get("publication_id_set_sha256")
    )


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
    receipt = metadata.get("strict_two_pass_receipt", {})
    screenshots = metadata.get("screenshots", {})
    screenshot_valid, image_rows = screenshot_evidence(path, screenshots)
    controls_ok = controls_valid(value, event, plan)
    strict_ok = strict_receipt_valid(value, event)
    marker_ok = committed_artifact_valid(path)
    adapter = metadata.get("prisma_search_run", {}).get("adapter", {})
    adapter_ok = bool(
        adapter.get("adapter_id") == plan.get("adapter", {}).get("id")
        and adapter.get("adapter_version") == plan.get("adapter", {}).get("version")
        and adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256")
    )
    screenshot_receipt_ok = bool(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
        and screenshot_valid
    )
    records = value.get("results", [])
    abstract_capture_observed = bool(
        isinstance(records, list)
        and all(
            isinstance(row, dict)
            and (
                (
                    bool(row.get("abstract"))
                    and row.get("abstract_source") == "native_scopus_result_page"
                    and row.get("abstract_not_available") is False
                    and row.get("abstract_detail_verified") is True
                )
                or (
                    row.get("abstract") in ("", None)
                    and row.get("abstract_source") == "not_rendered"
                    and row.get("abstract_not_available") is True
                )
            )
            for row in records
        )
    )
    return {
        "valid": bool(
            controls_ok
            and strict_ok
            and adapter_ok
            and screenshot_receipt_ok
            and marker_ok
            and abstract_capture_observed
        ),
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
        "total": value.get("total"),
        "stable_id_count": len(
            {
                record.get("paperId")
                for record in records
                if isinstance(record, dict) and isinstance(record.get("paperId"), str)
            }
        ),
        "stable_id_set_sha256": receipt.get("stable_id_set_sha256"),
        "two_pass_order_verified": receipt.get("two_pass_order_verified"),
        "order_difference_count": receipt.get("order_difference_count"),
        "pass_order_hashes": [
            report.get("ordered_stable_ids_sha256")
            for report in receipt.get("pass_reports", [])
            if isinstance(report, dict)
        ],
        "controls_valid": controls_ok,
        "strict_v2_valid": strict_ok,
        "adapter_binding_valid": adapter_ok,
        "screenshots_valid": screenshot_receipt_ok,
        "terminal_marker_valid": marker_ok,
        "abstract_capture_observed": abstract_capture_observed,
        "full_abstract_count": sum(
            bool(record.get("abstract"))
            for record in records
            if isinstance(record, dict)
        ),
        "verified_missing_abstract_count": sum(
            record.get("abstract") in ("", None)
            for record in records
            if isinstance(record, dict)
        ),
        "screenshots": image_rows,
    }


def command(event: dict[str, Any], output: Path, cdp_url: str, target_id: str, plan: dict[str, Any]) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        event["query"],
        "--year-end",
        "2026",
        "--result-scope",
        "documents",
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
        "--require-complete",
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
        f"Scopus final prior-secondary-review {event['partition_id']} discovery partition",
    ]


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def create_ephemeral_scopus_target(cdp_url: str, timeout_seconds: float = 45.0) -> str:
    encoded = urllib.parse.quote(SCOPUS_ADVANCED_URL, safe="")
    created = cdp_json(cdp_url, f"/json/new?{encoded}", method="PUT")
    target_id = created.get("id") if isinstance(created, dict) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not return one explicit Scopus target")
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
            url = target.get("url", "")
            title = target.get("title", "")
            parsed = urllib.parse.urlparse(url)
            if (
                target.get("type") == "page"
                and parsed.scheme == "https"
                and parsed.hostname in {"scopus.com", "www.scopus.com"}
                and isinstance(title, str)
                and "Scopus" in title
            ):
                return target_id
        time.sleep(0.5)
    raise RuntimeError("The fresh Scopus target did not become ready")


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
        raise SystemExit("Final Scopus PSR execution requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected final PSR plan schema")
    events = plan.get("events")
    if (
        not isinstance(events, list)
        or [event.get("partition_id") for event in events] != list(PARTITIONS)
    ):
        raise SystemExit("Final Scopus PSR plan must contain PSR1 through PSR4 once")
    binding_errors = verify_plan_bindings(plan)
    if binding_errors:
        raise SystemExit("Plan binding failure: " + ", ".join(binding_errors))
    if args.output_dir.is_symlink():
        raise SystemExit("The final PSR output directory may not be a symlink")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(events):
        if index and args.settle_seconds:
            time.sleep(args.settle_seconds)
        output = args.output_dir / event["output_filename"]
        occupied = (output, *screenshot_paths(output), marker_path(output))
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise SystemExit(
                f"Refusing to overwrite final {event['partition_id']} artifact"
            )
        try:
            target_id = create_ephemeral_scopus_target(cdp_url)
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
                    "strict_v2_valid": outcome.get("strict_v2_valid"),
                    "order_difference_count": outcome.get("order_difference_count"),
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
        "source": "Scopus",
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
