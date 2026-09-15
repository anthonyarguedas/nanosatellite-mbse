#!/usr/bin/env python3
"""Predeclare an A2 branch split after the broad direct query timed out."""

from __future__ import annotations

import hashlib
import json
import os

from build_plan import ADAPTER, DEFAULT_OUTPUT, PILOT_ROOT, load, sha256_file
import queries

SCHEMA = "wos-broad-wildcard-pilot-recovery-plan/v1"
RUN_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
OUTPUT = PILOT_ROOT / "searches" / "recovery-plan.json"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def a2_cells() -> list[dict[str, object]]:
    ordinary = queries.WILDCARD_ORDINARY_BLOCKS
    cells = []
    for cell_id, model_block in (
        ("mh", ordinary["M_H"]),
        ("mb", ordinary["M_B"]),
    ):
        query = queries._baseline.with_main_controls(
            queries._baseline.all_of(
                ordinary["P"], ordinary["E_F"], model_block
            )
        )
        cells.append(
            {
                "cell_id": cell_id,
                "query": query,
                "query_sha256": sha256_text(query),
                "query_characters": len(query),
                "wildcard_operator_count": query.count("*") + query.count("$"),
                "attempt_outputs": [
                    f"recovery/A2-{cell_id}.attempt-{attempt:02d}.json"
                    for attempt in range(1, 4)
                ],
            }
        )
    return cells


def main() -> int:
    if os.path.lexists(OUTPUT):
        raise SystemExit(f"Refusing to overwrite {OUTPUT}")
    plan = load(DEFAULT_OUTPUT)
    receipt = load(RUN_RECEIPT)
    a2_event = next(item for item in plan["events"] if item["partition_id"] == "A2")
    failures = []
    for outcome in receipt.get("outcomes", []):
        if outcome.get("partition_id") != "A2":
            continue
        path = PILOT_ROOT / outcome["artifact"]
        artifact = load(path)
        if (
            artifact.get("total") is not None
            or artifact.get("output_metadata", {}).get("status") != "error"
            or artifact.get("output_metadata", {}).get("error_stage") != "submit"
            or artifact.get("output_metadata", {}).get("screenshots", {}).get("search_page") is None
        ):
            raise SystemExit("The A2 failure history does not permit a branch split")
        failures.append(
            {
                "attempt": outcome["attempt"],
                "artifact": outcome["artifact"],
                "sha256": sha256_file(path),
                "total": None,
                "error_stage": "submit",
                "configured_search_screenshot_retained": True,
                "results_screenshot_retained": False,
            }
        )
    if len(failures) != 3 or receipt.get("success") is not False:
        raise SystemExit("Expected three retained direct A2 submit failures")
    remaining = [
        item["event_id"]
        for item in plan["events"]
        if queries.SCHEDULE_IDS.index(item["partition_id"])
        > queries.SCHEDULE_IDS.index("A2")
    ]
    payload = {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "Web of Science Core Collection",
        "diagnostic_only": True,
        "do_not_merge": True,
        "reason": (
            "The 2,743-character direct broad A2 query retained three configured-search "
            "screenshots, then timed out at submit with total null. Split only the "
            "predeclared M_H OR M_B factor into a lossless two-cell union."
        ),
        "original_event": {
            "event_id": a2_event["event_id"],
            "query": a2_event["query"],
            "query_sha256": a2_event["query_sha256"],
        },
        "retained_failures": failures,
        "repair": {
            "partition_id": "A2",
            "identity": "(P AND E_F AND M_H) OR (P AND E_F AND M_B)",
            "result_driven": False,
            "cells": a2_cells(),
            "union_identity": "ordered WOS-ID union with deduplication",
        },
        "remaining_original_events": remaining,
        "retry_policy": plan["retry_policy"],
        "adapter": {
            "version": plan["adapter"]["version"],
            "sha256": sha256_file(ADAPTER),
        },
        "original_plan": str(DEFAULT_OUTPUT.relative_to(PILOT_ROOT)),
        "original_plan_sha256": sha256_file(DEFAULT_OUTPUT),
        "initial_run_receipt": str(RUN_RECEIPT.relative_to(PILOT_ROOT)),
        "initial_run_receipt_sha256": sha256_file(RUN_RECEIPT),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(OUTPUT), "cells": 2, "remaining": len(remaining)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
