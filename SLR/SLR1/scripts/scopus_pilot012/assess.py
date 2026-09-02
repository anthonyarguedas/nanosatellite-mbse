#!/usr/bin/env python3
"""Assess the relaxed Scopus strict validation events."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "scopus-set-reconciled-strict-validation-assessment/v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    plan = load(args.plan)
    events = []
    errors = []
    screenshot_count = 0
    for event in plan["events"]:
        path = args.pilot_root / "searches" / event["output"]
        try:
            value = load(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{event['event_id']}:{type(error).__name__}")
            continue
        metadata = value.get("output_metadata", {})
        receipt = metadata.get("strict_two_pass_receipt", {})
        screenshots = metadata.get("screenshots", {})
        valid = bool(
            value.get("requested_query") == event["query"]
            and isinstance(value.get("total"), int)
            and value["total"] == len(value.get("results", []))
            and metadata.get("status") == "success"
            and metadata.get("retrieval_complete") is True
            and metadata.get("merge_eligible") is True
            and receipt.get("schema_version")
            == "academic-search-scopus-strict-two-pass/v2"
            and receipt.get("strict_stable_id_sets_reconciled") is True
            and receipt.get("two_pass_set_verified") is True
            and isinstance(receipt.get("two_pass_order_verified"), bool)
            and isinstance(receipt.get("order_difference_count"), int)
            and receipt.get("stable_id_set_sha256")
            == receipt.get("record_id_set_sha256")
            and len(receipt.get("pass_reports", [])) == 2
        )
        for key, suffix in (
            ("search_page", ".search-page.png"),
            ("results_page", ".results-page.png"),
        ):
            image = path.with_name(f"{path.stem}{suffix}")
            evidence = screenshots.get(key, {})
            if (
                not image.is_file()
                or evidence.get("path") != image.name
                or evidence.get("sha256") != digest(image)
            ):
                valid = False
            screenshot_count += 1
        if not valid:
            errors.append(f"invalid:{event['event_id']}")
        events.append(
            {
                "event_id": event["event_id"],
                "artifact": str(path),
                "sha256": digest(path),
                "valid": valid,
                "total": value.get("total"),
                "stable_id_set_sha256": receipt.get("stable_id_set_sha256"),
                "two_pass_order_verified": receipt.get("two_pass_order_verified"),
                "order_difference_count": receipt.get("order_difference_count"),
                "pass_order_hashes": [
                    report.get("ordered_stable_ids_sha256")
                    for report in receipt.get("pass_reports", [])
                    if isinstance(report, dict)
                ],
            }
        )
    complete = len(events) == 2 and not errors
    b1 = next((event for event in events if event["event_id"] == "B1-wildcard-strict"), None)
    assessment = {
        "schema_version": SCHEMA,
        "pilot": "012",
        "source": "Scopus",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "event_count": len(events),
        "verified_screenshot_file_count": screenshot_count,
        "receipt_schema": "academic-search-scopus-strict-two-pass/v2",
        "complete_stable_id_set_reconciliation_validated": complete,
        "source_order_retained_as_audit_evidence": complete,
        "order_equality_required_for_completion": False,
        "b1_final_search_readiness": bool(
            complete and b1 is not None and b1.get("valid") is True
        ),
        "events": events,
        "decision": (
            "accept_set_reconciled_strict_contract"
            if complete
            else "retain_prior_strict_contract_pending_validation"
        ),
        "errors": errors,
        "status": "passed" if complete else "failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "b1_ready": assessment["b1_final_search_readiness"],
                "events": [
                    {
                        "id": event["event_id"],
                        "total": event["total"],
                        "order_match": event["two_pass_order_verified"],
                        "order_differences": event["order_difference_count"],
                    }
                    for event in events
                ],
            }
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
