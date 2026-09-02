#!/usr/bin/env python3
"""Run the isolated clean retry of all current-literal Scopus PSR events."""

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

SCHEMA = "scopus-current-literal-psr-isolated-retry-run/v1"
PLAN_SCHEMA = "scopus-current-literal-psr-isolated-retry-plan/v1"
PILOT = "015"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
SCOPUS_ADVANCED_URL = "https://www.scopus.com/search/form.uri?display=advanced"
EXPECTED_PARTITIONS = {"PSR1", "PSR2", "PSR3", "PSR4"}
STRICT_SCHEMA = "academic-search-scopus-strict-two-pass/v2"
SCREENSHOT_SCHEMA = "scopus-automatic-screenshots/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def screenshot_paths(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.stem}.search-page.png"),
        path.with_name(f"{path.stem}.results-page.png"),
    )


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


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
                "path": str(image),
                "sha256": digest(image) if image.is_file() else None,
                "valid": image_valid,
            }
        )
    return valid, rows


def controls_valid(value: dict[str, Any], event: dict[str, Any]) -> bool:
    metadata = value.get("output_metadata", {})
    strategy = metadata.get("prisma_search_run", {}).get("strategy", {})
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
        strategy.get("requested_query") == event.get("query")
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
        common_valid = bool(
            report.get("pass_number") == number
            and report.get("complete") is True
            and report.get("native_query_readback_observed") is True
            and report.get("source_reported_total") == total
            and report.get("source_entries_traversed") == total
            and report.get("normalized_records_retrieved") == total
            and report.get("stable_id_set_sha256")
            == receipt.get("stable_id_set_sha256")
        )
        if not common_valid:
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


def summarize(path: Path, event: dict[str, Any]) -> dict[str, Any]:
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
    controls_ok = controls_valid(value, event)
    strict_ok = strict_receipt_valid(value, event)
    marker_ok = committed_artifact_valid(path)
    screenshot_receipt_ok = bool(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA
        and screenshots.get("automatic") is True
        and screenshots.get("same_directory_as_json") is True
        and screenshot_valid
    )
    records = value.get("results", [])
    known_item = next(
        (
            record
            for record in records
            if isinstance(record, dict)
            and record.get("paperId") == "SCOPUS-PUBLICATION:105032155734"
        ),
        None,
    )
    return {
        "valid": bool(controls_ok and strict_ok and screenshot_receipt_ok and marker_ok),
        "artifact_written": True,
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
        "screenshots_valid": screenshot_receipt_ok,
        "terminal_marker_valid": marker_ok,
        "screenshots": image_rows,
        "known_item_retrieved": known_item is not None,
        "known_item_doi": known_item.get("doi") if known_item else None,
        "known_item_title": known_item.get("title") if known_item else None,
    }


def command(event: dict[str, Any], output: Path, cdp_url: str, target_id: str) -> list[str]:
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
        "180",
        "--page-delay-seconds",
        "0.75",
        "--skip-full-abstracts",
        "--require-complete",
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
        "--output-path",
        str(output),
        "--prisma-run-id",
        f"pilot-scopus-015-{event['partition_id']}",
        "--prisma-review-id",
        "slr1-pilot-015",
        "--prisma-strategy-reference",
        "slr1-scopus-current-literal-psr-isolated-retry-v1",
        "--prisma-strategy-version",
        event["protocol_commit"],
        "--prisma-phase",
        "pilot",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        event["partition_id"],
        "--prisma-partition-label",
        event["partition_id"],
        "--prisma-partition-description",
        f"Scopus Pilot 015 current literal isolated retry {event['partition_id']}",
    ]


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(
        f"{cdp_url.rstrip('/')}{path}",
        method=method,
    )
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
            f"{cdp_url.rstrip('/')}/json/close/{target_id}",
            timeout=10,
        ) as response:
            response.read()
    except Exception:
        return False
    return True


def verify_plan_bindings(plan: dict[str, Any], repository_root: Path) -> list[str]:
    errors: list[str] = []
    if digest(ADAPTER) != plan.get("adapter", {}).get("sha256"):
        errors.append("adapter_changed")
    query_snapshot = repository_root / plan.get("query_snapshot", {}).get("path", "")
    if not query_snapshot.is_file() or digest(query_snapshot) != plan.get("query_snapshot", {}).get("sha256"):
        errors.append("query_snapshot_changed")
    for relative, expected in plan.get("source_affecting_scripts", {}).items():
        path = repository_root / relative
        if not path.is_file() or digest(path) != expected:
            errors.append(f"source_script_changed:{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--settle-seconds", type=float, default=5.0)
    args = parser.parse_args()
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    if not cdp_url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise SystemExit("Pilot 015 requires a loopback browser endpoint")
    plan = load(args.plan)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise SystemExit("Unexpected plan schema")
    events = plan.get("events")
    if (
        not isinstance(events, list)
        or len(events) != 4
        or {event.get("partition_id") for event in events} != EXPECTED_PARTITIONS
    ):
        raise SystemExit("Pilot 015 requires all four PSR events")
    repository_root = Path(__file__).resolve().parents[4]
    binding_errors = verify_plan_bindings(plan, repository_root)
    if binding_errors:
        raise SystemExit("Plan binding failure: " + ", ".join(binding_errors))

    outcomes: list[dict[str, Any]] = []
    started = now()
    for index, event in enumerate(events):
        if index and args.settle_seconds:
            time.sleep(args.settle_seconds)
        output = args.pilot_root / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        occupied = (output, *screenshot_paths(output), marker_path(output))
        if any(path.exists() or path.is_symlink() for path in occupied):
            raise SystemExit(f"Refusing to overwrite {event['partition_id']}")
        try:
            target_id = create_ephemeral_scopus_target(cdp_url)
        except Exception as error:
            outcome = {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "exit_code": None,
                "artifact": str(output.relative_to(args.pilot_root)),
                "stderr_tail": "",
                "valid": False,
                "artifact_written": False,
                "runner_error": "ephemeral_target_creation_failed",
                "runner_error_class": type(error).__name__,
                "ephemeral_target_created": False,
                "ephemeral_target_close_requested": False,
            }
            outcomes.append(outcome)
            print(
                json.dumps(
                    {
                        "partition": event["partition_id"],
                        "exit_code": None,
                        "valid": False,
                        "runner_error": "ephemeral_target_creation_failed",
                    }
                ),
                flush=True,
            )
            continue
        try:
            result = subprocess.run(
                command(event, output, cdp_url, target_id),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            summary = summarize(output, event)
            exit_code: int | None = result.returncode
            stderr_tail = result.stderr[-4000:] if result.stderr else ""
        except Exception as error:
            summary = {
                "valid": False,
                "artifact_written": output.is_file(),
                "runner_error": "subprocess_or_summary_failed",
                "runner_error_class": type(error).__name__,
            }
            exit_code = None
            stderr_tail = ""
        finally:
            target_close_requested = close_ephemeral_target(cdp_url, target_id)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "exit_code": exit_code,
            "artifact": str(output.relative_to(args.pilot_root)),
            "stderr_tail": stderr_tail,
            "ephemeral_target_created": True,
            "ephemeral_target_close_requested": target_close_requested,
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "exit_code": exit_code,
                    **{
                        key: summary.get(key)
                        for key in (
                            "valid",
                            "total",
                            "strict_v2_valid",
                            "two_pass_order_verified",
                            "order_difference_count",
                            "known_item_retrieved",
                            "runner_error",
                        )
                    },
                }
            ),
            flush=True,
        )

    success = bool(
        len(outcomes) == len(events)
        and all(
            outcome.get("exit_code") == 0 and outcome.get("valid") is True
            for outcome in outcomes
        )
    )
    receipt = {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "target_identifier_retained": False,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "adapter": plan["adapter"],
        "command_contract": {
            "year_start_option_omitted": True,
            "year_end": 2026,
            "language_option_omitted": True,
            "document_type_option_omitted": True,
            "subject_area_options_omitted": True,
            "open_access_option_omitted": True,
            "search_within_option_omitted": True,
            "page_size": 200,
            "fresh_authorized_target_per_event": True,
            "ephemeral_target_ids_retained": False,
            "require_complete": True,
            "skip_full_abstracts": True,
        },
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_event_count": len(events),
        "attempted_event_count": len(outcomes),
        "all_partitions_attempted": len(outcomes) == len(events),
        "continue_after_failure_policy_applied": True,
        "success": success,
        "outcomes": outcomes,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
