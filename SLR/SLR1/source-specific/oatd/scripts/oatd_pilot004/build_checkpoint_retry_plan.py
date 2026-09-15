#!/usr/bin/env python3
"""Predeclare the OATD Pilot 004 checkpoint false-positive repair retry."""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-004-checkpoint-repair-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_ROOT / "source-specific" / "oatd" / "pilots" / "004"
DEFAULT_PRIOR_PLAN = PILOT_ROOT / "searches" / "event-plan.page-size-30.json"
DEFAULT_CHECKPOINT = PILOT_ROOT / "searches" / "checkpoint/P-shared.checkpoint.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.checkpoint-repair.json"
SOURCE_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "run_pilot.py",
    SCRIPT_DIR / "run_page_size_retry.py",
    SCRIPT_DIR / "build_checkpoint_retry_plan.py",
    SCRIPT_DIR / "run_checkpoint_retry.py",
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
    if event.get("page_size") != 30 or event.get("max_pages") != 100:
        raise RuntimeError("The prior event does not contain the page-size refinement")
    if checkpoint.get("adapter", {}).get("adapter_version") != "10":
        raise RuntimeError("The checkpoint does not bind OATD adapter v10")
    completed = checkpoint.get("completed_ids")
    source = checkpoint.get("source_population")
    if not isinstance(completed, list) or not isinstance(source, dict) or not completed:
        raise RuntimeError("The checkpoint lacks resumable source evidence")

    adapter_files = {
        name: {
            "path": f"~/agent-tools/{path.relative_to(base.ADAPTER_ROOT)}",
            "sha256": base.file_sha256(path),
        }
        for name, path in base.ADAPTER_FILES.items()
    }
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
            "Resume the unchanged page-size-30 P-only harvest after repairing a "
            "checkpoint false positive for public thesis text."
        ),
        "page_size_retry_plan": {
            "path": str(prior_plan_path.relative_to(PILOT_ROOT)),
            "sha256": base.file_sha256(prior_plan_path),
        },
        "adapter": {
            "id": "search_oatd",
            "version": "10",
            "files": adapter_files,
            "mandatory_automatic_screenshots": True,
            "screenshot_opt_out": False,
        },
        "checkpoint_repair": {
            "failure": (
                "A public thesis metadata field mentioned local computing. The broad "
                "checkpoint scan misclassified that public text as private runtime context."
            ),
            "repair": (
                "Apply local-context value checks only to operational query and URL "
                "locations. Preserve public bibliographic text verbatim."
            ),
            "forbidden_checkpoint_keys_unchanged": True,
            "query_location_checks_retained": True,
            "url_location_checks_retained": True,
            "checkpoint_schema_changed": False,
            "source_query_changed": False,
            "source_controls_changed": False,
            "local_plan_changed": False,
            "minimum_completed_ids": len(completed),
            "source_reported_total": source.get("source_reported_total"),
            "stable_record_ids_sha256": source.get("stable_record_ids_sha256"),
            "page_size": source.get("page_size"),
            "failed_checkpoint_snapshot": {
                "path": "searches/checkpoint/P-shared.attempt-03.checkpoint.json",
                "sha256": base.file_sha256(
                    checkpoint_path.with_name("P-shared.attempt-03.checkpoint.json")
                ),
            },
        },
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
                "checkpoint_completed_ids": plan["checkpoint_repair"][
                    "minimum_completed_ids"
                ],
                "source_reported_total": plan["checkpoint_repair"][
                    "source_reported_total"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
