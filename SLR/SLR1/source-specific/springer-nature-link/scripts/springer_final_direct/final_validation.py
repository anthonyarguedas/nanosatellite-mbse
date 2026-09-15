#!/usr/bin/env python3
"""Validate the reconciled final Springer search corpus."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
SCRIPT_PATH = Path(__file__).resolve()
RUNNER_PATH = SCRIPT_PATH.with_name("run.py")
REPLACEMENT_PATH = SCRIPT_PATH.with_name("replacement.py")
SCHEMA = "slr1-springer-nature-link-final-assessment/v2"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("slr1_springer_final_validation_runner", RUNNER_PATH)
replacement = load_module(
    "slr1_springer_final_validation_replacement", REPLACEMENT_PATH
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    return runner.load(path)


def digest(path: Path) -> str:
    return runner.digest(path)


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    runner.write_new(path, value)


def relative(path: Path) -> str:
    return runner.relative(path)


def assess(
    plan_path: Path,
    reconciled_run_path: Path,
    reconciliation_path: Path,
    declarations_path: Path,
    source_union_path: Path,
    record_union_path: Path,
    superseded_assessment_path: Path,
    output_path: Path,
) -> int:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    plan = load(plan_path)
    reconciled_run = load(reconciled_run_path)
    reconciliation = load(reconciliation_path)
    declarations = load(declarations_path)
    source_union = load(source_union_path)
    record_union = load(record_union_path)
    superseded = load(superseded_assessment_path)
    errors = replacement.validate_plan(plan, verify_bindings=True)
    if (
        reconciled_run.get("schema_version") != replacement.RUN_SCHEMA
        or reconciled_run.get("plan_sha256") != digest(plan_path)
        or reconciled_run.get("success") is not True
        or reconciled_run.get("accepted_source_cell_count") != 57
    ):
        errors.append("reconciled_replacement_run")
    if (
        reconciliation.get("schema_version") != replacement.RECONCILIATION_SCHEMA
        or reconciliation.get("replacement_plan_sha256") != digest(plan_path)
        or reconciliation.get("replacement_receipt_sha256")
        != digest(reconciled_run_path)
        or reconciliation.get("success") is not True
        or reconciliation.get("selected_source_cell_count") != 67
    ):
        errors.append("final_reconciliation")
    if (
        declarations.get("schema_version") != replacement.DECLARATIONS_SCHEMA
        or declarations.get("reconciliation_sha256") != digest(reconciliation_path)
        or len(declarations.get("expected_cells", [])) != 67
    ):
        errors.append("source_cell_declarations")
    if (
        superseded.get("schema_version") != replacement.ASSESSMENT_SCHEMA
        or superseded.get("status") != "failed"
        or superseded.get("validation_errors") != ["source_union"]
    ):
        errors.append("superseded_assessment")

    try:
        selected = replacement.validated_reconciled_cells(reconciliation)
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"source_cells:{type(error).__name__}")
        selected = []

    raw_source_occurrences = 0
    retained_occurrences = 0
    client_exclusions = 0
    full_abstract_occurrences = 0
    source_abstract_absences = 0
    publication_types: Counter[str] = Counter()
    stable_ids: set[str] = set()
    source_years: dict[str, set[int]] = {
        "B2": set(),
        "BC1": set(),
        "BT2": set(),
    }
    source_cells_by_partition: Counter[str] = Counter()
    target_recoveries = 0
    for item in selected:
        event = item["event"]
        summary = item["summary"]
        data = item["data"]
        total = summary.get("source_total")
        retained = summary.get("retained_record_count")
        excluded = summary.get("client_date_excluded_count")
        if not all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in (total, retained, excluded)
        ) or total != retained + excluded:
            errors.append(f"date_accounting:{event.get('event_id')}")
            continue
        raw_source_occurrences += total
        retained_occurrences += retained
        client_exclusions += excluded
        full_abstract_occurrences += summary["full_abstract_count"]
        source_abstract_absences += summary[
            "source_abstract_not_available_count"
        ]
        publication_types.update(summary["publication_type_counts"])
        stable_ids.update(summary["record_paper_ids"])
        target_recoveries += summary.get("detail_target_recovery_count") or 0
        partition = event["partition_id"]
        source_cells_by_partition[partition] += 1
        if partition in source_years:
            year = event.get("source_year_partition")
            if not isinstance(year, int):
                errors.append(f"source_year:{event.get('event_id')}")
            else:
                source_years[partition].add(year)
            if (
                event.get("date_start") != runner.DATE_START
                or event.get("date_end") != runner.DATE_END
                or summary.get("source_year_partition") != year
                or summary.get("source_year_partition_valid") is not True
            ):
                errors.append(f"global_date_window:{event.get('event_id')}")
        for record in data.get("results", []):
            if (
                not isinstance(record.get("abstract"), str)
                or record.get("abstract_not_available")
                != (not bool(record.get("abstract")))
                or not isinstance(record.get("documentType"), str)
                or not record["documentType"].strip()
                or record.get("exactDateFilterStatus")
                not in {"included", "unresolved"}
            ):
                errors.append(f"record_capture:{event.get('event_id')}")
                break

    expected_cell_counts = {
        "A1": 1,
        "A2": 5,
        "A3": 1,
        "B1": 1,
        "B2": 25,
        "BG1": 1,
        "BG2": 1,
        "BC1": 16,
        "BT2": 16,
    }
    if dict(source_cells_by_partition) != expected_cell_counts:
        errors.append("partition_cell_counts")
    expected_years = set(range(2011, 2027))
    if any(years != expected_years for years in source_years.values()):
        errors.append("source_year_coverage")
    if (
        full_abstract_occurrences + source_abstract_absences
        != retained_occurrences
        or sum(publication_types.values()) != retained_occurrences
    ):
        errors.append("capture_accounting")

    union_source = source_union.get("source_unions", {}).get(runner.SOURCE_ID, {})
    source_union_valid = bool(
        source_union.get("schema_version")
        == "academic-search-source-union-receipt/v1"
        and source_union.get("review_namespace") == runner.REVIEW_NAMESPACE
        and source_union.get("review_id") == runner.REVIEW_ID
        and source_union.get("strategy_reference") == runner.STRATEGY_REFERENCE
        and source_union.get("strategy_version") == plan["strategy_version"]
        and source_union.get("expected_partitions") == list(runner.PARTITIONS)
        and source_union.get("expected_sources") == [runner.SOURCE_ID]
        and source_union.get("event_count") == 67
        and source_union.get("artifact_count") == 67
        and union_source.get("event_total_sum") == retained_occurrences
        and union_source.get("raw_record_count") == retained_occurrences
        and union_source.get("unique_union_count") == len(stable_ids)
        and set(union_source.get("stable_record_ids", [])) == stable_ids
        and union_source.get("completeness_status") == "complete"
        and union_source.get("failure_status") == "none"
    )
    if not source_union_valid:
        errors.append("source_union")
    cell_unions = union_source.get("cell_unions", {})
    for partition, count in expected_cell_counts.items():
        if cell_unions.get(partition, {}).get("cell_count") != count:
            errors.append(f"source_union_cell:{partition}")

    records = record_union.get("records")
    record_union_valid = bool(
        record_union.get("schema_version") == replacement.RECORD_UNION_SCHEMA
        and record_union.get("reconciliation_sha256") == digest(reconciliation_path)
        and record_union.get("source_event_record_count") == retained_occurrences
        and record_union.get("unique_source_card_path_count") == len(stable_ids)
        and record_union.get("records_with_full_abstract") == 753
        and record_union.get("records_with_source_abstract_absence") == 19
        and record_union.get("records_missing_abstract_state") == 0
        and record_union.get("records_with_source_publication_type")
        == len(stable_ids)
        and record_union.get("records_missing_source_publication_type") == 0
        and record_union.get("metadata_conflicts") == []
        and record_union.get("complete") is True
        and isinstance(records, list)
        and len(records) == len(stable_ids)
    )
    if not record_union_valid:
        errors.append("record_union")

    value = {
        "schema_version": SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": runner.SOURCE,
        "source_id": runner.SOURCE_ID,
        "review_namespace": runner.REVIEW_NAMESPACE,
        "replacement_plan": relative(plan_path),
        "replacement_plan_sha256": digest(plan_path),
        "reconciled_replacement_run": relative(reconciled_run_path),
        "reconciled_replacement_run_sha256": digest(reconciled_run_path),
        "final_reconciliation": relative(reconciliation_path),
        "final_reconciliation_sha256": digest(reconciliation_path),
        "source_cell_declarations": relative(declarations_path),
        "source_cell_declarations_sha256": digest(declarations_path),
        "source_union_receipt": relative(source_union_path),
        "source_union_receipt_sha256": digest(source_union_path),
        "record_union": relative(record_union_path),
        "record_union_sha256": digest(record_union_path),
        "superseded_assessment": relative(superseded_assessment_path),
        "superseded_assessment_sha256": digest(superseded_assessment_path),
        "supersession_reason": (
            "The v1 assessment compared the retained source-union event total "
            "against the raw prefilter total. This assessment validates raw source "
            "occurrences and retained union occurrences separately."
        ),
        "validation_script": relative(SCRIPT_PATH),
        "validation_script_sha256": digest(SCRIPT_PATH),
        "adapter": plan["adapter"],
        "date_contract": plan["date_contract"],
        "source_cell_count": len(selected),
        "source_cell_counts_by_partition": expected_cell_counts,
        "source_year_coverage": {
            partition: sorted(years) for partition, years in source_years.items()
        },
        "raw_source_record_occurrence_count": raw_source_occurrences,
        "client_date_excluded_occurrence_count": client_exclusions,
        "retained_record_occurrence_count": retained_occurrences,
        "unique_retained_source_card_path_count": len(stable_ids),
        "unique_retained_source_card_path_set_sha256": runner.digest_set(stable_ids),
        "full_abstract_occurrence_count": full_abstract_occurrences,
        "source_abstract_not_available_occurrence_count": source_abstract_absences,
        "publication_type_occurrence_count": sum(publication_types.values()),
        "publication_type_counts": dict(sorted(publication_types.items())),
        "unique_records_with_full_abstract": record_union.get(
            "records_with_full_abstract"
        ),
        "unique_records_with_source_abstract_absence": record_union.get(
            "records_with_source_abstract_absence"
        ),
        "unique_records_with_source_publication_type": record_union.get(
            "records_with_source_publication_type"
        ),
        "detail_owned_target_recovery_count": target_recoveries,
        "full_abstract_and_publication_type_capture_complete": bool(not errors),
        "source_union_valid": source_union_valid,
        "record_union_valid": record_union_valid,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new(output_path, value)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--reconciled-run", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--cell-declarations", type=Path, required=True)
    parser.add_argument("--source-union", type=Path, required=True)
    parser.add_argument("--record-union", type=Path, required=True)
    parser.add_argument("--superseded-assessment", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return assess(
        args.plan,
        args.reconciled_run,
        args.reconciliation,
        args.cell_declarations,
        args.source_union,
        args.record_union,
        args.superseded_assessment,
        args.output,
    )


if __name__ == "__main__":
    raise SystemExit(main())
