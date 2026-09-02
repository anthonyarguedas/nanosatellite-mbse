#!/usr/bin/env python3
"""Assess the unchanged IEEE A2 readiness retest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected an object in {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(pilot_root: Path, pilot005_root: Path) -> dict[str, Any]:
    searches = pilot_root / "searches"
    plan = load(searches / "event-plan.json")
    run = load(searches / "run-receipt.json")
    p005_plan = load(pilot005_root / "searches" / "event-plan.json")
    p005_a2 = next(
        event for event in p005_plan["events"] if event["event_id"] == "count-A2-pass1"
    )
    ledger = []
    signatures = []

    for event in plan["events"]:
        path = searches / event["output"]
        artifact = load(path)
        metadata = artifact["output_metadata"]
        receipt = metadata["ieee_observation_receipt"]
        rendered = receipt["rendered_state"]
        signature = {
            "error_stage": metadata.get("error_stage"),
            "initial_form_state": receipt["initial_form_readiness"]["state"],
            "query_echo": rendered["query_echo"],
            "summary": rendered["summary"],
            "loading": rendered["loading"],
            "card_count": rendered["card_count"],
            "sort": rendered["sort"],
            "route": receipt["syntax_access_state"]["route"],
            "access": receipt["syntax_access_state"]["access"],
            "ready": receipt["syntax_access_state"]["ready"],
            "year_attempt_count": receipt["year_control"]["attempt_count"],
        }
        signatures.append(signature)
        ledger.append(
            {
                "event_id": event["event_id"],
                "path": str(path.relative_to(pilot_root)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "status": metadata["status"],
                "total": artifact["total"],
                "executed_query_matches_plan": artifact.get("executed_query")
                == event["query"],
                "do_not_merge": artifact.get("do_not_merge") is True,
                "terminal_marker_present": path.with_name(
                    f".{path.name}.IEEE_COMMIT.json"
                ).exists(),
                "readiness_signature": signature,
            }
        )

    return {
        "schema_version": "ieee-xplore-pilot-008-assessment/v1",
        "source": "IEEE Xplore",
        "pilot": "008",
        "diagnostic_only": True,
        "do_not_merge": True,
        "query_identity": {
            "characters": plan["query_identity"]["characters"],
            "sha256": plan["query_identity"]["sha256"],
            "matches_pilot005": plan["events"][0]["query"] == p005_a2["query"],
            "pilot005_sha256": p005_a2["query_sha256"],
            "source_cells": 1,
            "query_changed": False,
        },
        "run": {
            "status": run["status"],
            "successful_source_event_count": run["successful_source_event_count"],
            "failed_source_event_count": run["failed_source_event_count"],
            "source_total": None,
        },
        "artifact_ledger": ledger,
        "repeated_failure_signature": signatures[0]
        if len(signatures) == 2 and signatures[0] == signatures[1]
        else None,
        "comparison": {
            "pilot005_attempt_count": 2,
            "pilot005_outcome": "two initial_form_readiness failures with exact query echo and total null",
            "pilot008_attempt_count": 2,
            "pilot008_outcome": "two initial_form_readiness failures with exact query echo and total null",
            "combined_unchanged_attempt_count": 4,
        },
        "conclusion": {
            "direct_a2": (
                "The unchanged direct A2 expression is not currently executable through a stable "
                "rendered result page. Four independent attempts have the same failure state."
            ),
            "source_observation": (
                "IEEE echoes the exact query on the expected public route with no access or syntax "
                "state, then leaves the result shell unready with no summary, cards, sort, or total."
            ),
            "controls": "The failure occurs before Publication Year handling.",
            "next_boundary": (
                "Any future lossless source-cell distribution requires a separately predeclared pilot."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot005-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(args.pilot_root, args.pilot005_root)
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
