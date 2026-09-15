#!/usr/bin/env python3
"""Validate and publish the terminal OATD final-search failure assessment."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCRIPT_PATH = Path(__file__).resolve()
SLR1_ROOT = SCRIPT_PATH.parents[4]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
FINAL_ROOT = SLR1_ROOT / "source-specific/oatd/final-searches"
OUTPUT = FINAL_ROOT / "final-failure-assessment.json"
VALIDATION = FINAL_ROOT / "final-failure-validation.json"

ASSESSMENT_SCHEMA = "slr1-oatd-final-failure-assessment/v1"
VALIDATION_SCHEMA = "slr1-oatd-final-failure-validation/v1"
SOURCE = "Open Access Theses and Dissertations (OATD)"
CUTOFF = "2026-08-24"

ENDPOINT_FAILURES = (
    (
        "corrective-005/final-event-plan.json",
        "corrective-005/failure-receipt-20260904T185241Z.json",
        "OATD route returned HTTP 504 without a ready source state.",
    ),
    (
        "corrective-006/final-event-plan.json",
        "corrective-006/failure-receipt-20260904T192350Z.json",
        "OATD route returned HTTP 504 without a ready source state.",
    ),
    (
        "corrective-007/final-event-plan.json",
        "corrective-007/failure-receipt-20260905T030612Z.json",
        "OATD route returned HTTP 500 without a ready source state.",
    ),
)
DIAGNOSTIC_PLAN = FINAL_ROOT / "search-endpoint-diagnostic/plan.json"
DIAGNOSTIC_RESULT = FINAL_ROOT / "search-endpoint-diagnostic/CubeSat-count.json"
LOCAL_HISTORY = (
    "final-event-plan.json",
    "failure-receipt-20260904T155704Z.json",
    "corrective-002/final-event-plan.json",
    "corrective-002/failure-receipt-20260904T162705Z.json",
    "corrective-003/final-event-plan.json",
    "corrective-003/failure-receipt-20260904T163422Z.json",
    "corrective-004/final-event-plan.json",
    "corrective-004/failure-receipt-20260904T184820Z.json",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(REPOSITORY_ROOT))


def load(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Expected a regular evidence file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object: {path}")
    return value


def descriptor(path: Path) -> dict[str, Any]:
    return {
        "path": relative(path),
        "sha256": digest(path),
        "bytes": path.stat().st_size,
    }


def require_null_union() -> None:
    forbidden = [FINAL_ROOT / "hydrated-union.json"]
    forbidden.extend(FINAL_ROOT.glob("corrective-*/hydrated-union.json"))
    forbidden.extend(FINAL_ROOT.glob("**/gates/*.json"))
    forbidden.extend(FINAL_ROOT.glob("**/checkpoint/*.json"))
    occupied = [path for path in forbidden if os.path.lexists(path)]
    if occupied:
        raise RuntimeError("OATD failure finalization found a purported complete source artifact")


def build() -> dict[str, Any]:
    require_null_union()
    attempts: list[dict[str, Any]] = []
    for plan_name, receipt_name, expected_error in ENDPOINT_FAILURES:
        plan_path = FINAL_ROOT / plan_name
        receipt_path = FINAL_ROOT / receipt_name
        plan = load(plan_path)
        receipt = load(receipt_path)
        policy = plan.get("execution_policy")
        cutoff = plan.get("cutoff")
        if (
            plan.get("source_id") != "oatd"
            or not isinstance(policy, Mapping)
            or policy.get("fresh_browser") is not False
            or policy.get("browser_profile") != "shared_chrome_automation_cdp_9222"
            or not isinstance(cutoff, Mapping)
            or cutoff.get("exact_common_cutoff") != CUTOFF
            or len(plan.get("events", [])) != 8
            or receipt.get("success") is not False
            or receipt.get("error") != expected_error
            or receipt.get("checkpoint_completed_ids_after") != 0
            or receipt.get("hydrated_union_created") is not False
        ):
            raise RuntimeError(f"Invalid OATD endpoint-failure evidence: {receipt_path}")
        attempts.append(
            {
                "run_id": plan["run_id"],
                "started_at_utc": receipt["started_at_utc"],
                "completed_at_utc": receipt["completed_at_utc"],
                "error_type": receipt["error_type"],
                "error": receipt["error"],
                "failed_stage": "first_exact_gate_before_query_readback_or_total",
                "automatic_http_retry": False,
                "plan": descriptor(plan_path),
                "failure_receipt": descriptor(receipt_path),
            }
        )

    diagnostic_plan = load(DIAGNOSTIC_PLAN)
    diagnostic = load(DIAGNOSTIC_RESULT)
    metadata = diagnostic.get("output_metadata")
    if (
        diagnostic_plan.get("query") != '"CubeSat"'
        or diagnostic_plan.get("fresh_browser") is not False
        or diagnostic_plan.get("browser_profile") != "shared_chrome_automation_cdp_9222"
        or diagnostic.get("query") != '"CubeSat"'
        or diagnostic.get("executed_query") != ""
        or diagnostic.get("total") is not None
        or diagnostic.get("results") != []
        or not isinstance(metadata, Mapping)
        or metadata.get("status") != "error"
        or metadata.get("observed_exact_query_echo") is not False
        or metadata.get("error")
        != "OATD route returned HTTP 504 without a ready source state."
        or metadata.get("merge_eligible") is not False
    ):
        raise RuntimeError("The OATD one-literal search-endpoint diagnostic is invalid")

    local_history = [descriptor(FINAL_ROOT / name) for name in LOCAL_HISTORY]
    return {
        "schema_version": ASSESSMENT_SCHEMA,
        "generated_at_utc": now(),
        "source": SOURCE,
        "source_id": "oatd",
        "review_id": "slr1-1.1-restart",
        "common_evidence_cutoff": CUTOFF,
        "status": "terminal_search_failure",
        "source_disposition": "exclude_source_due_to_search_failure",
        "failure_scope": (
            "The OATD home page remained reachable, but the required rendered search "
            "route failed before exact query readback or a source total."
        ),
        "accepted_route": {
            "gate_count": 8,
            "all_gates_required": True,
            "endpoint_failure_attempts_reached_first_gate_readback": False,
            "complete_confirmed_gate_artifact_count": 0,
        },
        "endpoint_failure_attempts": attempts,
        "minimal_route_diagnostic": {
            "query": '"CubeSat"',
            "controls": diagnostic_plan["controls"],
            "status": "http_504_before_query_readback_or_total",
            "plan": descriptor(DIAGNOSTIC_PLAN),
            "artifact": descriptor(DIAGNOSTIC_RESULT),
            "screenshots": None,
            "reason_screenshots_absent": "The CLI event failed before a validated results page existed.",
        },
        "superseded_local_execution_history": local_history,
        "source_union": None,
        "source_union_total": None,
        "merge_eligible_artifact": None,
        "record_metadata_capture": {
            "records_hydrated": 0,
            "full_abstracts": None,
            "source_publication_types": None,
            "reason": (
                "The workflow never completed all initial gate snapshots, so the "
                "deduplicated stable-ID union and Record Details hydration never began."
            ),
            "pilot_records_reused": 0,
            "empty_result_inferred": False,
        },
        "accounting": {
            "identified_records_from_oatd": None,
            "oatd_count_treatment": "source_failure_not_zero_results",
            "failed_source_count": 1,
        },
        "conclusion": (
            "Repeated exact-gate failures and a one-literal controlled diagnostic show "
            "that OATD's search endpoint was unavailable for final execution. The "
            "complete source union remains null and OATD contributes no records."
        ),
    }


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor_fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor_fd, "wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def validate_assessment(value: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (
        value.get("schema_version") != ASSESSMENT_SCHEMA
        or value.get("status") != "terminal_search_failure"
        or value.get("source_disposition") != "exclude_source_due_to_search_failure"
        or value.get("source_union") is not None
        or value.get("source_union_total") is not None
        or value.get("merge_eligible_artifact") is not None
    ):
        errors.append("terminal_state")
    attempts = value.get("endpoint_failure_attempts")
    if not isinstance(attempts, list) or len(attempts) != 3:
        errors.append("endpoint_attempts")
    elif [attempt.get("error") for attempt in attempts] != [
        "OATD route returned HTTP 504 without a ready source state.",
        "OATD route returned HTTP 504 without a ready source state.",
        "OATD route returned HTTP 500 without a ready source state.",
    ]:
        errors.append("endpoint_error_sequence")
    capture = value.get("record_metadata_capture")
    if (
        not isinstance(capture, Mapping)
        or capture.get("records_hydrated") != 0
        or capture.get("full_abstracts") is not None
        or capture.get("source_publication_types") is not None
        or capture.get("pilot_records_reused") != 0
        or capture.get("empty_result_inferred") is not False
    ):
        errors.append("record_metadata_capture")
    try:
        require_null_union()
    except RuntimeError:
        errors.append("unexpected_complete_artifact")
    return errors


def main() -> int:
    assessment = build()
    errors = validate_assessment(assessment)
    if errors:
        raise SystemExit("Invalid OATD final failure assessment: " + ", ".join(errors))
    write_new(OUTPUT, assessment)
    persisted = load(OUTPUT)
    persisted_errors = validate_assessment(persisted)
    report = {
        "schema_version": VALIDATION_SCHEMA,
        "generated_at_utc": now(),
        "source": SOURCE,
        "status": "valid" if not persisted_errors else "invalid",
        "errors": persisted_errors,
        "assessment": descriptor(OUTPUT),
        "endpoint_failure_attempts_validated": 3,
        "minimal_route_diagnostic_validated": True,
        "source_union_is_null": True,
        "empty_result_inferred": False,
    }
    write_new(VALIDATION, report)
    print(json.dumps({"status": report["status"], "assessment": str(OUTPUT)}))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
