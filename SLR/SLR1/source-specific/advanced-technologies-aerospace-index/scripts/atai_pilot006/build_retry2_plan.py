#!/usr/bin/env python3

"""Build Pilot 006 retry 2 using repeated exact source totals only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry1-plan", type=Path, required=True)
    parser.add_argument("--retry1-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    retry1 = json.loads(args.retry1_plan.read_text())
    receipt = json.loads(args.retry1_receipt.read_text())
    if receipt.get("status") != "stopped_on_source_or_adapter_failure":
        raise RuntimeError("Retry 1 does not preserve a stopped run.")
    if receipt.get("outcomes", [{}])[-1].get("event_id") != "field-index-explicit-no-date":
        raise RuntimeError("Retry 1 did not stop on the non-exportable indexed-keyword row.")
    by_id = {event["event_id"]: event for event in retry1["events"]}
    index_explicit = by_id["field-index-explicit-no-date"]
    index_noft = by_id["field-index-noft-no-date"]
    language = [event for event in retry1["events"] if event["event_id"].startswith("language-")]

    events = []
    for pass_number in (1, 2):
        for base in (index_explicit, index_noft):
            value = dict(base)
            value["event_id"] = f"{base['event_id']}-count-pass{pass_number}"
            value["purpose"] = f"Exact count-only pass {pass_number}: {base['purpose']}"
            value["require_complete"] = False
            value["count_only"] = True
            value["output"] = f"retry2/{value['event_id']}.json"
            events.append(value)
    for base in language:
        value = dict(base)
        value["output"] = f"retry2/{base['event_id']}.json"
        events.append(value)

    result = {
        "schema_version": "atai-pilot-006-retry2-plan/v1",
        "source": retry1["source"],
        "source_id": retry1["source_id"],
        "platform": retry1["platform"],
        "pilot": "006",
        "attempt": "retry2",
        "do_not_merge": True,
        "retry1_plan": str(args.retry1_plan),
        "retained_retry1_receipt": str(args.retry1_receipt),
        "repair_boundaries": [
            "The indexed-keyword row is source-positive but lacks the adapter's required Abstract/Details link. Two exact count-only passes replace full-record capture for this AN-bounded field contrast.",
            "The NOFT counterpart uses the same AN-bounded repeated-count method.",
            "The four predeclared complete-schedule language count cells are retained unchanged from retry 1.",
            "No stable-ID or full-record claim is made from count-only artifacts.",
        ],
        "events": events,
    }
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
