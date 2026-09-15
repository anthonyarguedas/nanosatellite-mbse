#!/usr/bin/env python3
"""Assess all-partition wildcard population evidence for IAF Pilot 006."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from build_plan import DEFAULT_OUTPUT, PILOT_ROOT, load, queries, validate

SCHEMA = "iaf-digital-library-pilot006-assessment/v1"
THRESHOLD = 100


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


def ledger_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.identity-ledger.json")


def artifact_path(root: Path, partition_id: str, cell_id: str) -> Path:
    return root / "searches" / "cells" / partition_id / f"{cell_id}.json"


def marker_errors(path: Path) -> list[str]:
    marker = load(marker_path(path))
    evidence = marker.get("normalized_json", {})
    digest = file_sha256(path)
    if (
        marker.get("schema") != "academic_search_output_commit_marker_v1"
        or evidence.get("sha256") != digest
        or evidence.get("bytes") != path.stat().st_size
    ):
        return [f"Commit marker differs for {path}"]
    return []


def source_cell_errors(
    cell: Mapping[str, Any],
    artifact: Mapping[str, Any],
    ledger: Mapping[str, Any],
    path: Path,
    partition_id: str,
) -> list[str]:
    errors = []
    query = cell["query"]
    metadata = artifact.get("output_metadata")
    receipt = (
        metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    )
    strategy = receipt.get("strategy") if isinstance(receipt, Mapping) else None
    scope = strategy.get("search_scope") if isinstance(strategy, Mapping) else None
    limits = strategy.get("limits") if isinstance(strategy, Mapping) else None
    date = (
        limits.get("publication_date", {}).get("effective", {})
        if isinstance(limits, Mapping)
        else {}
    )
    compact = ledger.get("compact_artifact")
    raw_ids = ledger.get("raw_ordered_paper_ids")
    retained_ids = ledger.get("diagnostic_window_ordered_paper_ids")
    results = artifact.get("results")
    if artifact.get("executed_query") != query or ledger.get("query") != query:
        errors.append(f"Query readback differs for {partition_id}/{cell['cell_id']}")
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("count_only") is not False
        or metadata.get("merge_eligible") is not False
        or artifact.get("do_not_merge") is not True
    ):
        errors.append(f"Completion status differs for {partition_id}/{cell['cell_id']}")
    if (
        not isinstance(receipt, Mapping)
        or receipt.get("completion_status") != "complete"
        or receipt.get("strategy_reference")
        != "slr1-iaf-all-partition-wildcard-population-v1"
        or receipt.get("strategy_version") != "3194156e90497186664260a8e86435e78d2e2aa1"
        or receipt.get("coverage", {}).get("partition_id") != partition_id
    ):
        errors.append(f"PRISMA receipt differs for {partition_id}/{cell['cell_id']}")
    if (
        not isinstance(strategy, Mapping)
        or strategy.get("executed_query") != query
        or not isinstance(scope, Mapping)
        or scope.get("library", {}).get("effective") != "full_iaf_digital_library"
        or date.get("mode") != "local_post_filter"
        or date.get("start") != "2011-01-01"
        or date.get("end") != "2026-08-29"
        or date.get("inclusive") is not True
    ):
        errors.append(f"Source controls differ for {partition_id}/{cell['cell_id']}")
    if (
        ledger.get("schema_version")
        != "iaf-digital-library-pilot006-complete-identity-ledger/v1"
        or ledger.get("diagnostic_only") is not True
        or ledger.get("do_not_merge") is not True
        or not isinstance(raw_ids, list)
        or not isinstance(retained_ids, list)
        or len(raw_ids or []) != len(set(raw_ids or []))
        or len(retained_ids or []) != len(set(retained_ids or []))
        or ledger.get("raw_ordered_paper_ids_sha256") != sequence_sha256(raw_ids or [])
        or ledger.get("diagnostic_window_ordered_paper_ids_sha256")
        != sequence_sha256(retained_ids or [])
    ):
        errors.append(f"Identity ledger differs for {partition_id}/{cell['cell_id']}")
    if (
        not isinstance(results, list)
        or artifact.get("total") != len(raw_ids or [])
        or [record.get("paperId") for record in results] != retained_ids
        or not set(retained_ids or []).issubset(raw_ids or [])
    ):
        errors.append(
            f"Stable IDs do not reconcile for {partition_id}/{cell['cell_id']}"
        )
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
        errors.append(f"Date accounting differs for {partition_id}/{cell['cell_id']}")
    digest = file_sha256(path)
    if (
        not isinstance(compact, Mapping)
        or compact.get("file_name") != path.name
        or compact.get("sha256") != digest
        or compact.get("bytes") != path.stat().st_size
        or compact.get("commit_marker") != marker_path(path).name
    ):
        errors.append(f"Compact binding differs for {partition_id}/{cell['cell_id']}")
    errors.extend(marker_errors(path))
    return errors


def validate_failure(path: Path, planned_queries: set[str]) -> list[str]:
    errors = []
    artifact = load(path)
    metadata = artifact.get("output_metadata", {})
    receipt = metadata.get("prisma_search_run", {})
    strategy = receipt.get("strategy", {})
    requested = artifact.get("requested_query") or strategy.get("requested_query")
    if (
        metadata.get("status") != "error"
        or metadata.get("merge_eligible") is not False
        or artifact.get("do_not_merge") is not True
        or receipt.get("completion_status") != "error"
        or requested not in planned_queries
    ):
        errors.append(f"Retained failure differs for {path}")
    errors.extend(marker_errors(path))
    return errors


def build(root: Path, plan_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = load(plan_path)
    errors = validate(plan)
    receipt = load(root / "searches" / "run-receipt.json")
    if (
        receipt.get("status") != "complete"
        or receipt.get("selected_partitions") != list(queries.SCHEDULE_IDS)
        or receipt.get("predeclared_cell_count") != 158
        or receipt.get("completed_cell_count") != 158
        or receipt.get("outcome_count") != 161
        or receipt.get("source_attempt_count") != 161
        or receipt.get("reused_existing_cell_count") != 0
    ):
        errors.append("The run receipt is incomplete")

    entries: dict[str, Any] = {}
    records: dict[str, dict[str, Any]] = {}
    source_artifact_count = 0
    planned_queries = set()
    for partition_id in queries.SCHEDULE_IDS:
        raw_occurrences: list[str] = []
        retained_occurrences: list[str] = []
        branch_values: defaultdict[str, dict[str, list[str] | int]] = defaultdict(
            lambda: {"cells": 0, "raw": [], "retained": []}
        )
        date_counts = {"included": 0, "excluded": 0, "unresolved": 0, "retained": 0}
        for cell in plan["partitions"][partition_id]["cells"]:
            planned_queries.add(cell["query"])
            path = artifact_path(root, partition_id, cell["cell_id"])
            try:
                artifact = load(path)
                ledger = load(ledger_path(path))
                errors.extend(
                    source_cell_errors(cell, artifact, ledger, path, partition_id)
                )
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
                errors.append(
                    f"Could not validate {partition_id}/{cell['cell_id']}: {error}"
                )
                continue
            source_artifact_count += 1
            raw_ids = list(ledger["raw_ordered_paper_ids"])
            retained_ids = list(ledger["diagnostic_window_ordered_paper_ids"])
            raw_occurrences.extend(raw_ids)
            retained_occurrences.extend(retained_ids)
            branch = branch_values[cell["branch_id"]]
            branch["cells"] = int(branch["cells"]) + 1
            branch["raw"].extend(raw_ids)  # type: ignore[union-attr]
            branch["retained"].extend(retained_ids)  # type: ignore[union-attr]
            accounting = ledger["date_filter_accounting"]
            for key in date_counts:
                date_counts[key] += accounting[key]
            for record in artifact.get("results", []):
                records[record["paperId"]] = {
                    "paper_id": record["paperId"],
                    "title": record.get("title"),
                    "year": record.get("year"),
                }

        raw_union = sorted(set(raw_occurrences))
        retained_union = sorted(set(retained_occurrences))
        baseline = plan["explicit_baseline"]["entries"][partition_id]
        baseline_raw = baseline["raw_ids"]
        baseline_retained = baseline["diagnostic_window_ids"]
        branches = {}
        for branch_id, values in branch_values.items():
            raw = values["raw"]
            retained = values["retained"]
            branches[branch_id] = {
                "complete_cells": values["cells"],
                "raw_source_event_total": len(raw),
                "raw_union": len(set(raw)),
                "diagnostic_window_event_total": len(retained),
                "diagnostic_window_union": len(set(retained)),
            }
        entries[partition_id] = {
            "status": "complete",
            "complete_cells": plan["partitions"][partition_id]["packed_cell_count"],
            "raw_source_event_total_sum": len(raw_occurrences),
            "raw_union": {
                "count": len(raw_union),
                "ids": raw_union,
                "explicit_baseline_count": len(baseline_raw),
                "missing_explicit_ids": sorted(set(baseline_raw) - set(raw_union)),
                "wildcard_only_ids": sorted(set(raw_union) - set(baseline_raw)),
                "sets_equal": set(raw_union) == set(baseline_raw),
            },
            "diagnostic_window_union": {
                "count": len(retained_union),
                "ids": retained_union,
                "explicit_baseline_count": len(baseline_retained),
                "missing_explicit_ids": sorted(
                    set(baseline_retained) - set(retained_union)
                ),
                "wildcard_only_ids": sorted(
                    set(retained_union) - set(baseline_retained)
                ),
                "sets_equal": set(retained_union) == set(baseline_retained),
            },
            "date_filter_event_counts": date_counts,
            "branches": branches,
            "investigation_required": {
                "threshold": THRESHOLD,
                "raw_union_over_threshold": len(raw_union) > THRESHOLD,
                "diagnostic_window_union_over_threshold": len(retained_union)
                > THRESHOLD,
            },
        }

    failure_paths = sorted(
        path
        for path in (root / "searches" / "failures").rglob(
            "*.NON_MERGEABLE_FAILURE.json"
        )
        if not path.name.startswith(".")
    )
    for path in failure_paths:
        errors.extend(validate_failure(path, planned_queries))
    failed_outcomes = [
        outcome
        for outcome in receipt.get("outcomes", [])
        if outcome.get("status") == "failed"
    ]
    if len(failure_paths) != 3 or len(failed_outcomes) != 3:
        errors.append("The retained failure count changed")
    for outcome in failed_outcomes:
        later_success = any(
            candidate.get("partition_id") == outcome.get("partition_id")
            and candidate.get("cell_id") == outcome.get("cell_id")
            and candidate.get("status") == "complete"
            and candidate.get("attempt", 0) > outcome.get("attempt", 0)
            for candidate in receipt.get("outcomes", [])
        )
        if not later_success:
            errors.append(
                f"Failed attempt lacks successful retry for {outcome.get('partition_id')}/{outcome.get('cell_id')}"
            )

    all_raw_equal = all(entry["raw_union"]["sets_equal"] for entry in entries.values())
    all_window_equal = all(
        entry["diagnostic_window_union"]["sets_equal"] for entry in entries.values()
    )
    wildcard_only = sorted(
        {
            paper_id
            for entry in entries.values()
            for paper_id in entry["diagnostic_window_union"]["wildcard_only_ids"]
        }
    )
    missing = sorted(
        {
            paper_id
            for entry in entries.values()
            for paper_id in entry["diagnostic_window_union"]["missing_explicit_ids"]
        }
    )
    threshold_entries = {
        partition_id: {
            "raw_union": entry["raw_union"]["count"],
            "diagnostic_window_union": entry["diagnostic_window_union"]["count"],
            "triggered": (
                entry["investigation_required"]["raw_union_over_threshold"]
                or entry["investigation_required"][
                    "diagnostic_window_union_over_threshold"
                ]
            ),
        }
        for partition_id, entry in entries.items()
    }
    threshold = {
        "schema_version": "iaf-digital-library-pilot006-threshold-investigations/v1",
        "pilot": "006",
        "threshold": THRESHOLD,
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
    if not all_raw_equal or not all_window_equal or missing or wildcard_only:
        errors.append("Wildcard and explicit partition unions differ")
    if threshold["status"] != "not_triggered":
        errors.append("A threshold investigation remains required")

    assessment = {
        "schema_version": SCHEMA,
        "pilot": "006",
        "source": "IAF Digital Library",
        "status": "complete" if not errors else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": "approve_eight_atom_population_wildcard_for_all_partitions"
        if not errors
        else "unresolved",
        "decision_basis": (
            "All 158 wildcard cells completed. Every raw and diagnostic-window partition "
            "union exactly equaled its explicit baseline, with no missing or wildcard-only ID."
        ),
        "canonical_schedule_decision": {
            "changed": not errors,
            "population_translation": list(plan["wildcard_population"]["atoms"]),
            "wildcard_scope": "IAF population block P only",
            "other_blocks": "retain explicit ordinary terms",
            "schedule_cells_before": 551,
            "schedule_cells_after": 158,
            "cell_reduction": 393,
            "cell_reduction_percent": 71.32,
        },
        "plan": {
            "artifact": str(plan_path.relative_to(root)),
            "sha256": file_sha256(plan_path),
            "cells": 158,
        },
        "entries": entries,
        "acceptance": {
            "all_nine_partitions_complete": source_artifact_count == 158,
            "all_raw_unions_equal": all_raw_equal,
            "all_diagnostic_window_unions_equal": all_window_equal,
            "missing_explicit_id_count": len(missing),
            "wildcard_only_id_count": len(wildcard_only),
            "result_driven_filters_added": False,
        },
        "threshold_investigations": threshold,
        "record_catalog": [records[paper_id] for paper_id in sorted(records)],
        "source_artifact_count": source_artifact_count,
        "retained_failure_artifacts": [
            str(path.relative_to(root)) for path in failure_paths
        ],
        "retained_failure_summary": {
            "count": len(failure_paths),
            "failed_cells": [
                f"{outcome['partition_id']}/{outcome['cell_id']}"
                for outcome in failed_outcomes
            ],
            "all_recovered_by_unchanged_query_retry": all(
                any(
                    candidate.get("partition_id") == outcome.get("partition_id")
                    and candidate.get("cell_id") == outcome.get("cell_id")
                    and candidate.get("status") == "complete"
                    and candidate.get("attempt", 0) > outcome.get("attempt", 0)
                    for candidate in receipt.get("outcomes", [])
                )
                for outcome in failed_outcomes
            ),
            "failure_stage": "before exact executed-query observation",
        },
        "errors": errors,
    }
    return assessment, threshold


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold-output", type=Path, required=True)
    args = parser.parse_args()
    assessment, threshold = build(args.pilot_root, args.plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    args.threshold_output.write_text(
        json.dumps(threshold, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
