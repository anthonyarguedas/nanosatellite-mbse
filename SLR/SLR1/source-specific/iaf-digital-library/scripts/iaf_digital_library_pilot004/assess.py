#!/usr/bin/env python3
"""Assess the complete IAF Pilot 004 changed-partition cell run."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from plan import (
    CHANGED_IDS,
    DATE_END,
    DATE_START,
    DEFAULT_PLAN_PATH,
    PILOT003_ASSESSMENT,
    PILOT_DIR,
    validate_plan_payload,
)

THRESHOLD = 100


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def artifact_path(root: Path, partition_id: str, cell_id: str) -> Path:
    return root / "searches" / "cells" / partition_id / f"{cell_id}.json"


def ledger_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.identity-ledger.json")


def marker_errors(output: Path) -> list[str]:
    errors = []
    try:
        marker = load(marker_path(output))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"Commit marker is unreadable for {output}: {error}"]
    normalized = marker.get("normalized_json")
    if (
        marker.get("schema") != "academic_search_output_commit_marker_v1"
        or not isinstance(normalized, Mapping)
        or normalized.get("sha256") != file_sha256(output)
        or normalized.get("bytes") != output.stat().st_size
    ):
        errors.append(f"Commit marker differs for {output}")
    return errors


def source_cell_errors(
    artifact: Mapping[str, Any],
    ledger: Mapping[str, Any],
    *,
    query: str,
    output: Path,
    partition_id: str,
) -> list[str]:
    errors = []
    metadata = artifact.get("output_metadata")
    receipt = (
        metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    )
    strategy = receipt.get("strategy") if isinstance(receipt, Mapping) else None
    limits = strategy.get("limits") if isinstance(strategy, Mapping) else None
    publication_date = (
        limits.get("publication_date") if isinstance(limits, Mapping) else None
    )
    effective_date = (
        publication_date.get("effective")
        if isinstance(publication_date, Mapping)
        else None
    )
    compact = ledger.get("compact_artifact")
    raw_ids = ledger.get("raw_ordered_paper_ids")
    retained_ids = ledger.get("diagnostic_window_ordered_paper_ids")
    records = artifact.get("results")
    if artifact.get("schema_version") != "academic-search-result/v1":
        errors.append(f"Unexpected source schema: {output}")
    if artifact.get("executed_query") != query or ledger.get("query") != query:
        errors.append(f"Query readback differs: {output}")
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("count_only") is not False
        or metadata.get("merge_eligible") is not False
        or artifact.get("do_not_merge") is not True
    ):
        errors.append(f"Completion or diagnostic status differs: {output}")
    if (
        not isinstance(receipt, Mapping)
        or receipt.get("completion_status") != "complete"
        or receipt.get("coverage", {}).get("partition_id") != partition_id
        or receipt.get("strategy_reference")
        != "slr1-direct-query-schedule-post-proximity-v1"
        or receipt.get("strategy_version") != "3194156e90497186664260a8e86435e78d2e2aa1"
    ):
        errors.append(f"PRISMA run receipt differs: {output}")
    source_scope = (
        strategy.get("search_scope") if isinstance(strategy, Mapping) else None
    )
    if (
        not isinstance(strategy, Mapping)
        or strategy.get("executed_query") != query
        or source_scope.get("library", {}).get("effective")
        != "full_iaf_digital_library"
        or effective_date.get("mode") != "local_post_filter"
        or effective_date.get("start") != DATE_START
        or effective_date.get("end") != DATE_END
        or effective_date.get("inclusive") is not True
    ):
        errors.append(f"Source controls differ: {output}")
    if (
        ledger.get("schema_version")
        != "iaf-digital-library-pilot004-complete-identity-ledger/v1"
        or ledger.get("diagnostic_only") is not True
        or ledger.get("do_not_merge") is not True
        or not isinstance(raw_ids, list)
        or not isinstance(retained_ids, list)
        or len(raw_ids) != len(set(raw_ids))
        or len(retained_ids) != len(set(retained_ids))
        or ledger.get("raw_ordered_paper_ids_sha256") != sequence_sha256(raw_ids)
        or ledger.get("diagnostic_window_ordered_paper_ids_sha256")
        != sequence_sha256(retained_ids)
    ):
        errors.append(f"Identity ledger differs: {output}")
    if (
        not isinstance(records, list)
        or not isinstance(raw_ids, list)
        or not isinstance(retained_ids, list)
        or artifact.get("total") != len(raw_ids)
        or [record.get("paperId") for record in records] != retained_ids
        or not set(retained_ids).issubset(raw_ids)
    ):
        errors.append(f"Source total or retained records do not reconcile: {output}")
    accounting = ledger.get("date_filter_accounting")
    if (
        not isinstance(accounting, Mapping)
        or accounting.get("raw_total") != len(raw_ids or [])
        or accounting.get("retained") != len(retained_ids or [])
        or accounting.get("included", 0)
        + accounting.get("excluded", 0)
        + accounting.get("unresolved", 0)
        != len(raw_ids or [])
        or accounting.get("complete") is not True
    ):
        errors.append(f"Date accounting differs: {output}")
    if (
        not isinstance(compact, Mapping)
        or compact.get("file_name") != output.name
        or compact.get("sha256") != file_sha256(output)
        or compact.get("bytes") != output.stat().st_size
        or compact.get("commit_marker") != marker_path(output).name
    ):
        errors.append(f"Compact artifact binding differs: {output}")
    errors.extend(marker_errors(output))
    return errors


def build(root: Path, plan_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = load(plan_path)
    errors = validate_plan_payload(plan)
    receipt = load(root / "searches" / "run-receipt.json")
    old = load(PILOT003_ASSESSMENT)
    if (
        receipt.get("status") != "complete"
        or receipt.get("selected_partitions") != list(CHANGED_IDS)
        or receipt.get("predeclared_cell_count") != plan["packing"]["live_pilot_cells"]
        or receipt.get("completed_cell_count") != plan["packing"]["live_pilot_cells"]
    ):
        errors.append("The live run receipt is incomplete")

    entries: dict[str, Any] = {}
    partition_sets: dict[str, set[str]] = {}
    partition_records: dict[str, dict[str, dict[str, Any]]] = {}
    source_artifact_count = 0
    for partition_id in CHANGED_IDS:
        raw_occurrences: list[str] = []
        retained_occurrences: list[str] = []
        membership: defaultdict[str, dict[str, list[str]]] = defaultdict(
            lambda: {"raw_cells": [], "retained_cells": []}
        )
        records: dict[str, dict[str, Any]] = {}
        branch_occurrences: defaultdict[str, dict[str, list[str]]] = defaultdict(
            lambda: {"raw": [], "retained": []}
        )
        branch_cell_counts: defaultdict[str, int] = defaultdict(int)
        date_counts = {"included": 0, "excluded": 0, "unresolved": 0, "retained": 0}

        for cell in plan["partitions"][partition_id]["cells"]:
            output = artifact_path(root, partition_id, cell["cell_id"])
            identity_path = ledger_path(output)
            try:
                artifact = load(output)
                identity = load(identity_path)
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
                errors.append(
                    f"Could not load {partition_id}/{cell['cell_id']}: {error}"
                )
                continue
            source_artifact_count += 1
            errors.extend(
                source_cell_errors(
                    artifact,
                    identity,
                    query=cell["query"],
                    output=output,
                    partition_id=partition_id,
                )
            )
            raw_ids = list(identity["raw_ordered_paper_ids"])
            retained_ids = list(identity["diagnostic_window_ordered_paper_ids"])
            raw_occurrences.extend(raw_ids)
            retained_occurrences.extend(retained_ids)
            branch = cell["branch_id"]
            branch_cell_counts[branch] += 1
            branch_occurrences[branch]["raw"].extend(raw_ids)
            branch_occurrences[branch]["retained"].extend(retained_ids)
            accounting = identity["date_filter_accounting"]
            for key in date_counts:
                date_counts[key] += accounting[key]
            for paper_id in raw_ids:
                membership[paper_id]["raw_cells"].append(cell["cell_id"])
            for paper_id in retained_ids:
                membership[paper_id]["retained_cells"].append(cell["cell_id"])
            for record in artifact.get("results", []):
                paper_id = str(record["paperId"])
                current = {
                    "paper_id": paper_id,
                    "title": record.get("title"),
                    "year": record.get("year"),
                    "event_code": record.get("eventCode"),
                    "paper_number": record.get("paperNumber"),
                }
                if paper_id in records and records[paper_id] != current:
                    errors.append(f"Metadata differs across cells for {paper_id}")
                records[paper_id] = current

        raw_union = sorted(set(raw_occurrences))
        retained_union = sorted(set(retained_occurrences))
        partition_sets[partition_id] = set(retained_union)
        partition_records[partition_id] = records
        branches = {}
        for branch_id, values in branch_occurrences.items():
            raw = values["raw"]
            retained = values["retained"]
            branches[branch_id] = {
                "complete_cells": branch_cell_counts[branch_id],
                "raw_source_event_total": len(raw),
                "raw_paper_id_union": len(set(raw)),
                "diagnostic_window_event_total": len(retained),
                "diagnostic_window_paper_id_union": len(set(retained)),
                "diagnostic_window_paper_ids": sorted(set(retained)),
            }
        entries[partition_id] = {
            "status": "complete",
            "complete_cells": plan["partitions"][partition_id]["packed_cell_count"],
            "branches": branches,
            "source_event_counts": {
                "raw_source_total_sum": len(raw_occurrences),
                "raw_paper_id_occurrences": len(raw_occurrences),
                "diagnostic_window_paper_id_occurrences": len(retained_occurrences),
                "date_filter_event_counts": date_counts,
            },
            "raw_paper_id_union": {
                "deduplicated_count": len(raw_union),
                "paper_ids": raw_union,
                "paper_ids_sha256": sequence_sha256(raw_union),
            },
            "diagnostic_window_paper_id_union": {
                "deduplicated_count": len(retained_union),
                "paper_ids": retained_union,
                "paper_ids_sha256": sequence_sha256(retained_union),
            },
            "paper_id_membership": [
                {"paper_id": paper_id, **membership[paper_id]} for paper_id in raw_union
            ],
            "record_catalog": [records[paper_id] for paper_id in retained_union],
            "investigation_required": {
                "threshold": THRESHOLD,
                "raw_paper_id_union": len(raw_union) > THRESHOLD,
                "diagnostic_window_paper_id_union": len(retained_union) > THRESHOLD,
            },
        }

    intersections = {}
    for index, left in enumerate(CHANGED_IDS):
        for right in CHANGED_IDS[index + 1 :]:
            overlap = sorted(partition_sets[left] & partition_sets[right])
            if overlap:
                intersections[f"{left}_and_{right}"] = overlap
    changed_union = sorted(set().union(*partition_sets.values()))

    superseded = {}
    for partition_id in CHANGED_IDS:
        old_ids = old["entries"][partition_id]["diagnostic_window_paper_id_union"][
            "paper_ids"
        ]
        current_ids = entries[partition_id]["diagnostic_window_paper_id_union"][
            "paper_ids"
        ]
        old_set = set(old_ids)
        current_set = set(current_ids)
        superseded[partition_id] = {
            "superseded_pair_schedule_count": len(old_ids),
            "current_count": len(current_ids),
            "retained_ids": sorted(old_set & current_set),
            "current_only_ids": sorted(current_set - old_set),
            "superseded_only_ids": sorted(old_set - current_set),
        }

    failures = sorted((root / "searches" / "failures").rglob("*.json"))
    threshold_entries = {
        partition_id: {
            "raw_union": entry["raw_paper_id_union"]["deduplicated_count"],
            "diagnostic_window_union": entry["diagnostic_window_paper_id_union"][
                "deduplicated_count"
            ],
            "triggered": (
                entry["raw_paper_id_union"]["deduplicated_count"] > THRESHOLD
                or entry["diagnostic_window_paper_id_union"]["deduplicated_count"]
                > THRESHOLD
            ),
        }
        for partition_id, entry in entries.items()
    }
    threshold_payload = {
        "schema_version": "iaf-digital-library-pilot004-threshold-investigations/v1",
        "pilot": "004",
        "threshold": THRESHOLD,
        "rule": "Investigate any deduplicated raw or diagnostic-window partition union over 100 records.",
        "entries": threshold_entries,
        "triggered_partitions": [
            partition_id
            for partition_id, entry in threshold_entries.items()
            if entry["triggered"]
        ],
        "status": "not_triggered"
        if not any(entry["triggered"] for entry in threshold_entries.values())
        else "investigation_required",
    }
    if threshold_payload["status"] != "not_triggered":
        errors.append("A threshold investigation remains required")

    assessment = {
        "schema_version": "iaf-digital-library-pilot004-assessment/v1",
        "pilot": "004",
        "source": {"id": "iaf_digital_library", "label": "IAF Digital Library"},
        "protocol_commit": plan.get("protocol_commit"),
        "status": "complete" if not errors else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": "accept_lossless_no_proximity_branch_cell_translation"
        if not errors
        else "unresolved",
        "decision_basis": (
            "The five unchanged partitions reproduce every Pilot 003 cell byte for byte. "
            "All 86 cells for the four changed partitions completed strict two-pass traversal "
            "with exact query readback, marker-bound artifacts, and reconciled stable-ID ledgers."
        ),
        "date_window": plan.get("requested_window"),
        "plan": {
            "artifact": str(plan_path.relative_to(root)),
            "sha256": file_sha256(plan_path),
            "complete_schedule_cells": plan["packing"]["complete_schedule_cells"],
            "carried_forward_cells": plan["packing"]["complete_schedule_cells"]
            - plan["packing"]["live_pilot_cells"],
            "live_cells": plan["packing"]["live_pilot_cells"],
        },
        "carry_forward": plan.get("carry_forward"),
        "entries": entries,
        "changed_partition_union": {
            "partition_record_occurrences": sum(
                len(values) for values in partition_sets.values()
            ),
            "deduplicated_stable_ids": len(changed_union),
            "paper_ids": changed_union,
            "cross_partition_intersections": intersections,
        },
        "superseded_schedule_comparison": {
            "scope_warning": (
                "Pilot 003 implemented superseded pair-based concepts. Set differences describe "
                "the protocol change and do not form a recall benchmark."
            ),
            "partitions": superseded,
        },
        "threshold_investigations": threshold_payload,
        "source_artifact_count": source_artifact_count,
        "retained_failure_artifacts": [
            str(path.relative_to(root)) for path in failures
        ],
        "controls": plan.get("controls"),
        "errors": errors,
    }
    return assessment, threshold_payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_DIR)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold-output", type=Path, required=True)
    args = parser.parse_args()
    assessment, threshold = build(args.pilot_root, args.plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.threshold_output.write_text(
        json.dumps(threshold, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
