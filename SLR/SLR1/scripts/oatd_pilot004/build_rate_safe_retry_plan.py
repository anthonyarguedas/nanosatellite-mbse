#!/usr/bin/env python3
"""Predeclare slower pacing for the OATD Pilot 004 shared harvest."""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-004-rate-safe-retry-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific" / "oatd" / "pilots" / "004"
DEFAULT_PRIOR_PLAN = PILOT_ROOT / "searches/event-plan.checkpoint-repair.json"
DEFAULT_CHECKPOINT = PILOT_ROOT / "searches/checkpoint/P-shared.checkpoint.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches/event-plan.rate-safe.json"
SOURCE_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "run_pilot.py",
    SCRIPT_DIR / "run_page_size_retry.py",
    SCRIPT_DIR / "build_rate_safe_retry_plan.py",
    SCRIPT_DIR / "run_rate_safe_retry.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def build(prior_plan_path: Path, checkpoint_path: Path) -> dict[str, Any]:
    prior = load(prior_plan_path)
    checkpoint = load(checkpoint_path)
    event = deepcopy(prior["events"][0])
    if (
        event.get("page_size") != 30
        or event.get("page_delay_seconds") != 0.75
        or event.get("detail_delay_seconds") != 0.5
    ):
        raise RuntimeError("The prior event lacks the expected initial pacing")
    event["page_delay_seconds"] = 6.0
    event["detail_delay_seconds"] = 6.0
    completed = checkpoint.get("completed_ids")
    source = checkpoint.get("source_population")
    if not isinstance(completed, list) or not isinstance(source, dict) or not completed:
        raise RuntimeError("The checkpoint lacks resumable source evidence")
    return {
        "schema_version": SCHEMA,
        "source": prior["source"],
        "source_id": prior["source_id"],
        "platform": prior["platform"],
        "pilot": "004",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Resume the unchanged P-only page-size-30 harvest with source-safe pacing."
        ),
        "checkpoint_repair_plan": {
            "path": str(prior_plan_path.relative_to(PILOT_ROOT)),
            "sha256": base.file_sha256(prior_plan_path),
        },
        "rate_safe_pacing": {
            "failure_basis": (
                "The dense 42-page identity pass succeeded, then the source presented "
                "an access challenge after one new detail record."
            ),
            "page_delay_seconds": {"initial": 0.75, "retry": 6.0},
            "detail_delay_seconds": {"initial": 0.5, "retry": 6.0},
            "source_query_changed": False,
            "source_controls_changed": False,
            "local_plan_changed": False,
            "page_size_changed": False,
            "record_limit_changed": False,
            "ordering_changed": False,
            "minimum_completed_ids": len(completed),
            "source_reported_total": source.get("source_reported_total"),
            "stable_record_ids_sha256": source.get("stable_record_ids_sha256"),
            "page_size": source.get("page_size"),
            "failure_checkpoint_snapshot": {
                "path": "searches/checkpoint/P-shared.attempt-04.checkpoint.json",
                "sha256": base.file_sha256(
                    checkpoint_path.with_name("P-shared.attempt-04.checkpoint.json")
                ),
            },
        },
        "adapter": prior["adapter"],
        "source_affecting_scripts": {
            str(path.relative_to(base.REPOSITORY_ROOT)): base.file_sha256(path)
            for path in SOURCE_SCRIPTS
        },
        "acceptance_checks": prior["acceptance_checks"],
        "event_count": 1,
        "events": [event],
    }


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-plan", type=Path, default=DEFAULT_PRIOR_PLAN)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    plan = build(args.prior_plan, args.checkpoint)
    write_new(args.output, plan)
    print(
        json.dumps(
            {
                "saved": str(args.output),
                "page_delay_seconds": plan["events"][0]["page_delay_seconds"],
                "detail_delay_seconds": plan["events"][0]["detail_delay_seconds"],
                "checkpoint_completed_ids": plan["rate_safe_pacing"][
                    "minimum_completed_ids"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
