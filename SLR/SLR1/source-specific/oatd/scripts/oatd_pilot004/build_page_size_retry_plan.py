#!/usr/bin/env python3
"""Predeclare the OATD Pilot 004 native-page-size retry."""

from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import queries
import run_pilot as base

SCHEMA = "oatd-pilot-004-page-size-retry-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_ROOT / "source-specific" / "oatd" / "pilots" / "004"
DEFAULT_INITIAL_PLAN = PILOT_ROOT / "searches" / "event-plan.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.page-size-30.json"
RETRY_SCRIPTS = (
    SCRIPT_DIR / "build_page_size_retry_plan.py",
    SCRIPT_DIR / "run_page_size_retry.py",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def build(initial_path: Path) -> dict[str, Any]:
    initial = load(initial_path)
    event = deepcopy(initial["events"][0])
    if event.get("page_size") != 100 or event.get("max_pages") != 30:
        raise RuntimeError("The initial OATD event does not have the expected bounds")
    event["page_size"] = 30
    event["max_pages"] = 100
    scripts = dict(initial["source_affecting_scripts"])
    scripts.update(
        {
            str(path.relative_to(base.REPOSITORY_ROOT)): base.file_sha256(path)
            for path in RETRY_SCRIPTS
        }
    )
    return {
        "schema_version": SCHEMA,
        "source": initial["source"],
        "source_id": initial["source_id"],
        "platform": initial["platform"],
        "pilot": "004",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Retry the unchanged P-only shared harvest with native page size 30."
        ),
        "initial_plan": {
            "path": str(initial_path.relative_to(PILOT_ROOT)),
            "sha256": base.file_sha256(initial_path),
        },
        "failure_basis": {
            "page_size_100_attempts": 2,
            "result": "explicit source busy or cleanup failure with no source total",
            "checkpoint_created": False,
            "source_query_rejected": False,
        },
        "operational_refinement": {
            "page_size": {"initial": 100, "retry": 30},
            "max_pages": {"initial": 30, "retry": 100},
            "reason": (
                "The P route remained busy with the explicit pagesize=100 parameter. "
                "The source default of 30 removes that parameter and reduces rendered "
                "first-page work. The larger max-pages bound preserves complete coverage."
            ),
            "source_semantics_changed": False,
            "query_changed": False,
            "language_changed": False,
            "year_window_changed": False,
            "local_matching_plan_changed": False,
            "record_limit_changed": False,
            "ordering_changed": False,
        },
        "adapter": initial["adapter"],
        "source_affecting_scripts": scripts,
        "acceptance_checks": initial["acceptance_checks"],
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
    parser.add_argument("--initial-plan", type=Path, default=DEFAULT_INITIAL_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    plan = build(args.initial_plan)
    write_new(args.output, plan)
    print(
        json.dumps(
            {
                "saved": str(args.output),
                "page_size": plan["events"][0]["page_size"],
                "max_pages": plan["events"][0]["max_pages"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
