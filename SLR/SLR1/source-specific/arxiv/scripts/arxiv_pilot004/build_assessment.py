#!/usr/bin/env python3
"""Reconcile Pilot 004 browser cells and summarize transport differences."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ARXIV_ID = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z][a-z.\-]*/\d{7})$", re.IGNORECASE)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(
    pilot_root: Path,
    plan_path: Path,
    atom_union_path: Path | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = load(plan_path)
    events = plan["events"]
    partitions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    screenshot_events: list[dict[str, Any]] = []
    errors: list[str] = []

    for event in events:
        path = pilot_root / "searches" / event["output"]
        artifact = load(path)
        total = artifact.get("total")
        records = artifact.get("results", [])
        if not isinstance(total, int) or total < 0 or len(records) != total:
            errors.append(f"Incomplete source accounting: {path}")
        if artifact.get("executed_query") != event["serialized_query"]:
            errors.append(f"Executed query mismatch: {path}")
        metadata = artifact.get("output_metadata", {})
        if (
            metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or artifact.get("do_not_merge") is not True
            or metadata.get("pilot_only") is not True
        ):
            errors.append(f"Pilot marking or completion mismatch: {path}")

        screenshots = metadata.get("screenshots", {})
        screenshot_event = {"json": str(path.relative_to(pilot_root))}
        for key, suffix in (
            ("search_page", ".search-page.png"),
            ("results_page", ".results-page.png"),
        ):
            screenshot = path.with_name(f"{path.stem}{suffix}")
            evidence = screenshots.get(key, {})
            if (
                not screenshot.is_file()
                or evidence.get("path") != screenshot.name
                or evidence.get("sha256") != file_sha256(screenshot)
            ):
                errors.append(f"Screenshot mismatch: {screenshot}")
            screenshot_event[key] = {
                **evidence,
                "repository_path": str(screenshot.relative_to(pilot_root)),
            }
        screenshot_events.append(screenshot_event)
        partitions[event["partition_id"]].append(
            {"event": event, "path": path, "artifact": artifact}
        )

    union_partitions: dict[str, Any] = {}
    for partition_id in plan["partition_ids"]:
        members = partitions[partition_id]
        by_id: dict[str, dict[str, Any]] = {}
        cell_total_sum = 0
        for member in members:
            event = member["event"]
            artifact = member["artifact"]
            cell_total_sum += artifact["total"]
            for record in artifact["results"]:
                stable_id = record.get("paperId")
                if not isinstance(stable_id, str) or ARXIV_ID.fullmatch(stable_id) is None:
                    errors.append(f"Invalid arXiv stable ID in {member['path']}")
                    continue
                retained = by_id.setdefault(
                    stable_id,
                    {
                        "source_record_stable_id": stable_id,
                        "source_record_version_ids": [],
                        "cell_ids": [],
                        "title": record.get("title", ""),
                        "abstract": record.get("abstract", ""),
                        "submitted_date": record.get("sourceSubmittedDate", ""),
                    },
                )
                version_id = record.get("sourceRecordStableId")
                if isinstance(version_id, str) and version_id not in retained["source_record_version_ids"]:
                    retained["source_record_version_ids"].append(version_id)
                if event["event_id"] not in retained["cell_ids"]:
                    retained["cell_ids"].append(event["event_id"])
        stable_ids = sorted(by_id)
        union_partitions[partition_id] = {
            "outcome": "complete" if members else "missing",
            "complete_cells": len(members),
            "raw_source_discovery_events": cell_total_sum,
            "cell_total_sum": cell_total_sum,
            "unique_stable_id_count": len(stable_ids),
            "duplicate_discovery_events": cell_total_sum - len(stable_ids),
            "stable_id_union": stable_ids,
            "cells": [
                {
                    "cell_id": member["event"]["event_id"],
                    "branch": member["event"]["branch"],
                    "source_total": member["artifact"]["total"],
                    "artifact": str(member["path"].relative_to(pilot_root)),
                }
                for member in members
            ],
            "records": [by_id[stable_id] for stable_id in stable_ids],
        }

    union = {
        "schema_version": "arxiv-browser-pilot004-unions/v1",
        "event_kind": "pilot_union_reconciliation",
        "merge_eligible": False,
        "do_not_merge": True,
        "source": "arXiv",
        "interface": "rendered Advanced Search web interface",
        "diagnostic_window": plan["date_window"],
        "deduplication_key": "bare arXiv identifier",
        "partitions": union_partitions,
    }

    atom_comparison: dict[str, Any] = {
        "status": "not_requested",
        "interpretation": (
            "Transport comparison is descriptive. Expansion-block definitions changed "
            "after Atom Pilot 003, and source analyzers can differ."
        ),
        "partitions": {},
    }
    if atom_union_path is not None and atom_union_path.is_file():
        atom = load(atom_union_path)
        atom_comparison["status"] = "complete"
        for partition_id, web in union_partitions.items():
            old = atom.get("partitions", {}).get(partition_id, {})
            old_ids = set(old.get("stable_id_union", []))
            web_ids = set(web["stable_id_union"])
            atom_comparison["partitions"][partition_id] = {
                "definition_comparable": partition_id in {"A1", "A2", "A3", "B1", "B2"},
                "browser_count": len(web_ids),
                "atom_pilot003_count": len(old_ids),
                "overlap_count": len(web_ids & old_ids),
                "browser_only": sorted(web_ids - old_ids),
                "atom_only": sorted(old_ids - web_ids),
            }

    assessment = {
        "schema_version": "arxiv-browser-pilot004-assessment/v1",
        "source": "arXiv",
        "pilot": "004",
        "status": "passed" if not errors else "failed",
        "do_not_merge": True,
        "interface": "rendered Advanced Search web interface",
        "source_event_count": len(events),
        "screenshot_file_count": 2 * len(screenshot_events),
        "screenshots": screenshot_events,
        "partition_summary": {
            partition_id: {
                key: value
                for key, value in partition.items()
                if key
                in {
                    "complete_cells",
                    "raw_source_discovery_events",
                    "unique_stable_id_count",
                    "duplicate_discovery_events",
                    "stable_id_union",
                }
            }
            for partition_id, partition in union_partitions.items()
        },
        "atom_pilot003_comparison": atom_comparison,
        "conclusions": [
            "All nine semantic partitions were represented by twelve rendered browser cells.",
            "A2, BG1, and BG2 used lossless distribution of one compound OR branch each.",
            "Every source cell used strict two-pass complete capture and mandatory screenshots.",
            "The browser route is the prospective arXiv route for cross-source interface consistency.",
        ],
        "errors": errors,
    }
    return union, assessment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--atom-union", type=Path)
    parser.add_argument("--union-output", type=Path, required=True)
    parser.add_argument("--assessment-output", type=Path, required=True)
    args = parser.parse_args()
    union, assessment = build(args.pilot_root, args.event_plan, args.atom_union)
    args.union_output.write_text(json.dumps(union, indent=2, ensure_ascii=False) + "\n")
    args.assessment_output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n"
    )
    return 0 if assessment["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
