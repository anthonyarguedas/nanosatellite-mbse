#!/usr/bin/env python3

"""Build final language-count pairs for every IF-augmented ATAI partition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry3-plan", type=Path, required=True)
    parser.add_argument("--if-reconciliation", type=Path, required=True)
    parser.add_argument("--detail-harvest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    retry3 = json.loads(args.retry3_plan.read_text())
    if_reconciliation = json.loads(args.if_reconciliation.read_text())
    detail = json.loads(args.detail_harvest.read_text())
    if if_reconciliation.get("status") != "complete_two_pass_card_id_reconciliation":
        raise RuntimeError("IF stable-ID reconciliation is incomplete.")
    if detail.get("status") != "complete_two_pass_detail_readback":
        raise RuntimeError("Candidate detail harvest is incomplete.")
    by_id = {event["event_id"]: event for event in retry3["events"]}
    events = []
    for pass_number in (1, 2):
        for partition in PARTITIONS:
            source = by_id[f"if-{partition}-augmented-count-pass1"]
            for label, language in (("unfiltered", None), ("english", "English")):
                event_id = f"final-language-{partition}-{label}-count-pass{pass_number}"
                events.append({
                    "event_id": event_id,
                    "purpose": f"Exact count pass {pass_number} for IF-augmented {partition}, {label} language scope.",
                    "query": source["query"],
                    "query_sha256": source["query_sha256"],
                    "language": language,
                    "date_start": "2011-01-01",
                    "date_end": "2026-08-29",
                    "require_complete": False,
                    "count_only": True,
                    "do_not_merge": True,
                    "output": f"retry7/{event_id}.json",
                })
    plan = {
        "schema_version": "atai-pilot-006-final-language-plan/v1",
        "source": retry3["source"],
        "source_id": retry3["source_id"],
        "platform": retry3["platform"],
        "pilot": "006",
        "attempt": "retry7",
        "do_not_merge": True,
        "retry3_plan": str(args.retry3_plan),
        "if_reconciliation": str(args.if_reconciliation),
        "detail_harvest": str(args.detail_harvest),
        "prospective_translation": "Every ordinary literal atom is NOFT literal OR IF.EXACT literal; every pair remains NOFT NEAR/5.",
        "acceptance": "For every partition, LA(English) must be a stable subset. Every unfiltered-only source record must have its language metadata reconciled before retaining the filter.",
        "events": events,
    }
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
