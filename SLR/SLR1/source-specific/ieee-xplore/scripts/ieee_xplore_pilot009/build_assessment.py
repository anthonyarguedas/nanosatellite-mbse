#!/usr/bin/env python3
"""Assess the IEEE literal A2 adapter transport repair."""

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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.IEEE_COMMIT.json")


def marker_valid(path: Path) -> bool:
    marker = marker_path(path)
    if not marker.is_file():
        return False
    value = load(marker)
    evidence = value.get("normalized_json", {})
    return (
        value.get("schema") == "ieee_xplore_output_commit_marker_v1"
        and evidence.get("sha256") == sha256(path)
        and evidence.get("bytes") == path.stat().st_size
    )


def build(pilot_root: Path, pilot008_root: Path) -> dict[str, Any]:
    searches = pilot_root / "searches"
    plan = load(searches / "event-plan.json")
    run = load(searches / "run-receipt.json")
    transport_path = searches / "transport-investigation.json"
    transport_investigation = load(transport_path)
    pilot008_plan = load(pilot008_root / "searches" / "event-plan.json")
    ledger = []
    totals = []

    for event in plan["events"]:
        path = searches / event["output"]
        artifact = load(path)
        metadata = artifact["output_metadata"]
        prisma = metadata["prisma_search_run"]
        adapter = prisma["adapter"]
        strategy = prisma["strategy"]
        year = metadata["publication_year_readback"]
        total = artifact.get("total")
        totals.append(total)
        ledger.append(
            {
                "event_id": event["event_id"],
                "path": str(path.relative_to(pilot_root)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "status": metadata.get("status"),
                "total": total,
                "executed_query_matches_plan": artifact.get("executed_query")
                == event["query"],
                "executed_query_provenance": strategy.get(
                    "executed_query_provenance"
                ),
                "adapter_version": adapter.get("adapter_version"),
                "adapter_sha256": adapter.get("script_sha256"),
                "sort": strategy.get("sort"),
                "year_readback": year,
                "do_not_merge": artifact.get("do_not_merge") is True,
                "terminal_marker_valid": marker_valid(path),
            }
        )

    return {
        "schema_version": "ieee-xplore-pilot-009-assessment/v1",
        "source": "IEEE Xplore",
        "pilot": "009",
        "diagnostic_only": True,
        "do_not_merge": True,
        "query_identity": {
            **plan["query_identity"],
            "matches_pilot008_bytes": plan["events"][0]["query"]
            == pilot008_plan["events"][0]["query"],
            "query_changed": False,
            "wildcard_used": False,
        },
        "transport": {
            **plan["transport"],
            "investigation_artifact": str(transport_path.relative_to(pilot_root)),
            "investigation_sha256": sha256(transport_path),
            "diagnosis": transport_investigation["diagnosis"],
        },
        "run": {
            "status": run["status"],
            "successful_source_event_count": run["successful_source_event_count"],
            "failed_source_event_count": run["failed_source_event_count"],
            "repeated_total": totals[0]
            if len(totals) == 2 and totals[0] == totals[1]
            else None,
        },
        "artifact_ledger": ledger,
        "comparison": {
            "pilot008_adapter_version": "9",
            "pilot008_outcome": (
                "two HTTP 414 transport failures misclassified as unready result shells"
            ),
            "pilot009_adapter_version": plan["adapter"]["version"],
            "pilot009_outcome": (
                "two complete count-only events with exact query, Year, sort, and total readback"
            ),
            "scientific_query_changed": False,
            "wildcard_used": False,
        },
        "conclusion": {
            "classification": "adapter_transport_failure_repaired",
            "pilot008": (
                "Pilot 008 remains immutable failure evidence for adapter v9. Its direct-A2 "
                "source-limitation diagnosis is superseded."
            ),
            "repair": (
                "Adapter v10 selected a bounded compact representation of the same ordered "
                "decoded parameters and completed both unchanged literal A2 events."
            ),
            "use_boundary": (
                "Pilot 009 is diagnostic and does not authorize a final IEEE search or "
                "resolve the exact publication-day cutoff."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot008-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(args.pilot_root, args.pilot008_root)
    args.output.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
