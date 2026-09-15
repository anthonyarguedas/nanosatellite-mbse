#!/usr/bin/env python3
"""Predeclare recovery from Pilot 004's connection-stage source attempt."""

from __future__ import annotations

import json
import os

from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, file_sha256, load

SCHEMA = "wos-current-schedule-wildcard-pilot-recovery-plan/v1"
FAILED_EVENT_ID = "wildcard-BG1"
FAILED_ARTIFACT = PILOT_ROOT / "searches" / "events" / f"{FAILED_EVENT_ID}.json"
FAILED_RUN_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
OUTPUT = PILOT_ROOT / "searches" / "recovery-plan.json"


def main() -> int:
    if os.path.lexists(OUTPUT):
        raise SystemExit(f"Refusing to overwrite {OUTPUT}")
    plan = load(DEFAULT_OUTPUT)
    event = next(item for item in plan["events"] if item["event_id"] == FAILED_EVENT_ID)
    failure = load(FAILED_ARTIFACT)
    receipt = load(FAILED_RUN_RECEIPT)
    if (
        failure.get("total") is not None
        or failure.get("output_metadata", {}).get("status") != "error"
        or failure.get("output_metadata", {}).get("error_stage") != "connection"
        or receipt.get("stopped_after_failure") is not True
        or receipt.get("outcomes", [])[-1].get("event_id") != FAILED_EVENT_ID
    ):
        raise SystemExit("The retained failure does not permit this exact recovery")
    failed_index = [item["event_id"] for item in plan["events"]].index(FAILED_EVENT_ID)
    payload = {
        "schema_version": SCHEMA,
        "pilot": "004",
        "source": "Web of Science Core Collection",
        "diagnostic_only": True,
        "do_not_merge": True,
        "reason": "The first wildcard-BG1 attempt failed at browser connection before query execution and retained total null with no screenshots.",
        "unchanged_event": {
            "event_id": FAILED_EVENT_ID,
            "partition_id": event["partition_id"],
            "variant": event["variant"],
            "query": event["query"],
            "query_sha256": event["query_sha256"],
        },
        "retained_failure": {
            "artifact": str(FAILED_ARTIFACT.relative_to(PILOT_ROOT)),
            "artifact_sha256": file_sha256(FAILED_ARTIFACT),
            "run_receipt": str(FAILED_RUN_RECEIPT.relative_to(PILOT_ROOT)),
            "run_receipt_sha256": file_sha256(FAILED_RUN_RECEIPT),
            "error_stage": "connection",
            "total": None,
            "screenshots_complete": False,
        },
        "adapter": {
            "version": plan["adapter"]["version"],
            "sha256": file_sha256(ADAPTER),
        },
        "retry_policy": {
            "exact_query_only": True,
            "maximum_additional_attempts": 2,
            "stop_after_first_success": True,
            "outputs": [
                "retries/wildcard-BG1-attempt2.json",
                "retries/wildcard-BG1-attempt3.json",
            ],
            "no_reuse_of_failed_page_or_state": True,
        },
        "remaining_original_events": [
            item["event_id"] for item in plan["events"][failed_index + 1 :]
        ],
        "original_plan": str(DEFAULT_OUTPUT.relative_to(PILOT_ROOT)),
        "original_plan_sha256": file_sha256(DEFAULT_OUTPUT),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(OUTPUT), "remaining": len(payload["remaining_original_events"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
