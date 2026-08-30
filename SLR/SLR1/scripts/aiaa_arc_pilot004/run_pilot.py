#!/usr/bin/env python3
"""Run the gated, non-final AIAA ARC Pilot 004 source events.

Run this program *inside* the shared-browser runner.  Unlike Pilot 003's old
count-only workaround, every source event invokes the repaired ARC normal CLI
with repeatable ``--field-row`` arguments.  The adapter writes immutable,
non-mergeable source receipts; this runner only coordinates cells and gates
schedule execution on the known-item recall result.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import (
    DATE_END,
    DATE_START,
    KNOWN_DOI,
    KNOWN_TITLE,
    PRIMARY_DIR,
    RECALL_DIR,
    SEARCH_DIR,
    UNION_DIR,
    Cell,
    artifact_path,
    artifact_total,
    atomic_write_json,
    ensure_directories,
    final_cells_by_schedule,
    load_json,
    next_attempt,
    primary_cells,
    recall_cells,
    successful_attempt,
    validate_artifact_common,
    validate_preview_artifact,
    validate_zero_count_artifact,
)
from queries import SCHEDULE_IDS

DEFAULT_ADAPTER = (
    Path.home()
    / "agent-tools-worktrees"
    / "slr-integration"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_aiaa_arc.py"
)


def adapter_path(value: str | None) -> Path:
    candidate = Path(value or os.environ.get("AIAA_ARC_ADAPTER", DEFAULT_ADAPTER)).expanduser()
    if not candidate.is_file():
        raise RuntimeError(
            "The repaired read-only ARC adapter is unavailable at "
            f"{candidate}. Set AIAA_ARC_ADAPTER to search_aiaa_arc.py."
        )
    return candidate.resolve()


def require_shared_browser() -> None:
    if not os.environ.get("BH_CDP_URL"):
        raise RuntimeError("Run Pilot 004 through run_with_browser.py; BH_CDP_URL is absent.")
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise RuntimeError(
            "Pilot 004 requires the shared-browser-owned-tabs-v1 contract; "
            "do not attach a separate browser/profile."
        )


def short_output(completed: subprocess.CompletedProcess[str]) -> str:
    value = (completed.stdout or "") + (completed.stderr or "")
    value = value.strip()
    return value[-1600:] if value else "(no adapter output)"


def command_for(adapter: Path, output_path: Path, cell: Cell, mode: str) -> list[str]:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required to run the ARC adapter CLI")
    command = [
        uv,
        "run",
        str(adapter),
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--limit",
        "100",
        "--max-pages",
        "5",
        "--timeout",
        "60",
        "--page-delay-seconds",
        "1",
    ]
    for field, text in cell.rows:
        command.extend(("--field-row", f"{field}={text}"))
    if mode == "preview":
        command.append("--preview-results")
    elif mode == "count":
        command.append("--count-only")
    else:  # pragma: no cover - internal caller invariant
        raise ValueError(f"Unknown ARC mode: {mode}")
    command.extend(("--output-path", str(output_path)))
    return command


def run_one(adapter: Path, output_base: Path, cell: Cell, mode: str) -> dict[str, Any]:
    """Run/resume one normal-CLI event and return its immutable receipt status."""
    existing = successful_attempt(output_base)
    if existing is not None:
        data = load_json(existing)
        return {
            "cell_id": cell.cell_id,
            "status": "existing",
            "mode": mode,
            "artifact": str(existing.relative_to(SEARCH_DIR.parent)),
            "total": data.get("total"),
            "errors": (
                validate_preview_artifact(data, cell)
                if mode == "preview"
                else validate_zero_count_artifact(data, cell)
                if mode == "count" and data.get("total") == 0
                else validate_artifact_common(data, cell)
            ),
        }
    target = next_attempt(output_base)
    if target is None:
        return {
            "cell_id": cell.cell_id,
            "status": "retry_limit_reached",
            "mode": mode,
            "artifact": None,
            "total": None,
            "errors": ["all normal/retry output paths are occupied by source failures"],
        }
    completed = subprocess.run(
        command_for(adapter, target, cell, mode),
        text=True,
        capture_output=True,
        check=False,
    )
    if target.exists():
        data = load_json(target)
        if mode == "preview":
            errors = validate_preview_artifact(data, cell)
        elif data.get("total") == 0:
            errors = validate_zero_count_artifact(data, cell)
        else:
            errors = validate_artifact_common(data, cell)
        return {
            "cell_id": cell.cell_id,
            "status": "ran" if completed.returncode == 0 else "adapter_nonzero_with_artifact",
            "mode": mode,
            "artifact": str(target.relative_to(SEARCH_DIR.parent)),
            "total": data.get("total"),
            "errors": errors,
            "adapter_returncode": completed.returncode,
        }
    failure = target.with_name(f"{target.stem}.NON_MERGEABLE_FAILURE{target.suffix}")
    return {
        "cell_id": cell.cell_id,
        "status": "source_or_adapter_failure",
        "mode": mode,
        "artifact": str(failure.relative_to(SEARCH_DIR.parent)) if failure.exists() else None,
        "total": None,
        "errors": [short_output(completed)],
        "adapter_returncode": completed.returncode,
    }


def source_index_cell() -> Cell:
    return Cell(
        schedule_id="known_item_source_indexing",
        cell_id="known-item-source-indexing-doi",
        rows=(("Anywhere", f'"{KNOWN_DOI}"'),),
        stage="known_item_source_indexing",
    )


def source_index_base() -> Path:
    return SEARCH_DIR / "known-item-source-indexing-doi.json"


def valid_result(report: dict[str, Any]) -> bool:
    return report.get("status") in {"ran", "existing"} and not report.get("errors")


def run_index(adapter: Path) -> tuple[dict[str, Any], Path | None]:
    cell = source_index_cell()
    report = run_one(adapter, source_index_base(), cell, "preview")
    result_path = successful_attempt(source_index_base())
    if valid_result(report) and result_path is not None:
        data = load_json(result_path)
        returned = [row.get("doi", "") for row in data.get("results", []) if isinstance(row, dict)]
        if KNOWN_DOI not in {str(value).casefold() for value in returned}:
            report["errors"].append("the DOI source-indexing result did not contain the required stable DOI")
        titles = [row.get("title") for row in data.get("results", []) if isinstance(row, dict)]
        if KNOWN_TITLE not in titles:
            report["errors"].append("the DOI source-indexing result did not retain the expected title")
    return report, result_path


def run_recall(adapter: Path) -> int:
    index_report, index_path = run_index(adapter)
    output: dict[str, Any] = {
        "schema_version": "aiaa-arc-pilot004-known-item-recall/v1",
        "pilot": "004",
        "source": "AIAA Aerospace Research Central (ARC)",
        "diagnostic_only": True,
        "date_window": {"start": DATE_START, "end": DATE_END},
        "normal_field_row_cli": True,
        "known_item": {"doi": KNOWN_DOI, "title": KNOWN_TITLE},
        "source_indexing": index_report,
        "applicable_partitions": {},
        "nonapplicable_partitions": {
            "A1": "No E_H literal was found in the source-located metadata/full text evidence register.",
            "A3": "No E_H literal was found in the source-located metadata/full text evidence register.",
            "BG1": "No G_model fixed literal or declared pair was found in the source-located metadata/full text evidence register.",
            "BG2": "No G_structure fixed literal or declared pair was found in the source-located metadata/full text evidence register.",
        },
    }
    okay = valid_result(index_report) and index_path is not None
    for schedule_id, cells in recall_cells().items():
        reports = []
        source_events = []
        for cell in cells:
            report = run_one(adapter, artifact_path(RECALL_DIR, cell), cell, "preview")
            reports.append(report)
            candidate = successful_attempt(artifact_path(RECALL_DIR, cell))
            if valid_result(report) and candidate is not None:
                data = load_json(candidate)
                for row in data.get("results", []):
                    if isinstance(row, dict):
                        source_events.append(
                            {
                                "cell_id": cell.cell_id,
                                "doi": row.get("doi"),
                                "title": row.get("title"),
                            }
                        )
        returned = {
            str(event["doi"]).casefold()
            for event in source_events
            if isinstance(event.get("doi"), str)
        }
        target_cells = [event["cell_id"] for event in source_events if str(event.get("doi", "")).casefold() == KNOWN_DOI]
        cells_complete = all(valid_result(report) for report in reports)
        partition_ok = cells_complete and KNOWN_DOI in returned
        output["applicable_partitions"][schedule_id] = {
            "cells": reports,
            "source_event_count": len(source_events),
            "stable_doi_union": sorted(returned),
            "known_doi_retrieved": KNOWN_DOI in returned,
            "known_doi_cells": target_cells,
            "all_lossless_subcells_executed": (
                len(cells) == 4 if schedule_id == "BT2" else True
            ),
            "status": (
                "retrieved"
                if partition_ok
                else "missed_after_complete_union"
                if cells_complete
                else "source_failure_unresolved"
            ),
        }
        okay = okay and partition_ok
    statuses = [entry["status"] for entry in output["applicable_partitions"].values()]
    if any(status == "source_failure_unresolved" for status in statuses):
        decision_status = "unresolved_source_failure"
    elif any(status == "missed_after_complete_union" for status in statuses):
        decision_status = "rejected_known_item_missed"
    else:
        decision_status = "accepted_observed_known_item_recall"
    output["decision"] = {
        "status": decision_status,
        "scope": (
            "Observed recall only for the source-located eligible sentinel. It does not prove "
            "recall for unknown records or turn hidden Anywhere/full-text matches into visible metadata matches."
        ),
        "gate": (
            "The normal schedule may use the prospective field union only when this status is accepted; "
            "this remains a pilot and is not a final search."
        ),
    }
    final_assessment = SEARCH_DIR / "known-item-recall.json"
    if decision_status == "unresolved_source_failure":
        attempt = 1
        while True:
            assessment = SEARCH_DIR / f"known-item-recall-attempt{attempt}-unresolved.json"
            if not assessment.exists():
                atomic_write_json(assessment, output)
                break
            attempt += 1
    elif not final_assessment.exists():
        atomic_write_json(final_assessment, output)
    else:
        prior = load_json(final_assessment)
        if prior.get("decision", {}).get("status") != decision_status:
            raise RuntimeError("existing final known-item recall decision conflicts with a later rerun")
    print(json.dumps({"phase": "recall", "decision": decision_status}, indent=2))
    return 0 if decision_status == "accepted_observed_known_item_recall" else 1


def load_accepted_recall() -> None:
    path = SEARCH_DIR / "known-item-recall.json"
    if not path.exists():
        raise RuntimeError("Known-item recall has not been recorded; run --phase recall first.")
    decision = load_json(path).get("decision", {}).get("status")
    if decision != "accepted_observed_known_item_recall":
        raise RuntimeError(f"Known-item recall gate is not accepted: {decision!r}")


def run_primary(adapter: Path) -> int:
    load_accepted_recall()
    reports = []
    okay = True
    for schedule_id in SCHEDULE_IDS:
        for cell in primary_cells(schedule_id):
            report = run_one(adapter, artifact_path(PRIMARY_DIR, cell), cell, "count")
            reports.append(report)
            okay = okay and valid_result(report)
    if okay:
        sums: dict[str, int] = {}
        for schedule_id in SCHEDULE_IDS:
            total = 0
            for cell in primary_cells(schedule_id):
                path = successful_attempt(artifact_path(PRIMARY_DIR, cell))
                assert path is not None
                total += artifact_total(load_json(path))
            sums[schedule_id] = total
        payload = {
            "schema_version": "aiaa-arc-pilot004-primary-field-union/v1",
            "pilot": "004",
            "source": "AIAA Aerospace Research Central (ARC)",
            "diagnostic_only": True,
            "date_window": {"start": DATE_START, "end": DATE_END},
            "normal_field_row_cli": True,
            "cells": reports,
            "conservative_primary_cell_sums": sums,
            "threshold": 100,
            "refinement_rule": "Use the 3-by-3 P/defining-block union when a P-field cell sum exceeds 100; retain all four disjoint T2 subcells.",
        }
        path = SEARCH_DIR / "primary-field-union.json"
        if not path.exists():
            atomic_write_json(path, payload)
    print(json.dumps({"phase": "primary", "status": "ok" if okay else "failure", "cells": len(reports)}, indent=2))
    return 0 if okay else 1


def primary_sums() -> dict[str, int]:
    path = SEARCH_DIR / "primary-field-union.json"
    if not path.exists():
        raise RuntimeError("Primary cells have not been reconciled; run --phase primary first.")
    values = load_json(path).get("conservative_primary_cell_sums")
    if not isinstance(values, dict) or set(values) != set(SCHEDULE_IDS):
        raise RuntimeError("Primary field-union totals are incomplete")
    if not all(isinstance(values[item], int) and values[item] >= 0 for item in SCHEDULE_IDS):
        raise RuntimeError("Primary field-union totals are invalid")
    return {item: values[item] for item in SCHEDULE_IDS}


def run_final_cell(adapter: Path, cell: Cell) -> dict[str, Any]:
    preview_base = artifact_path(UNION_DIR, cell)
    zero_base = artifact_path(UNION_DIR, cell, ".zero-count")
    zero_existing = successful_attempt(zero_base)
    if zero_existing is not None:
        data = load_json(zero_existing)
        # A count probe after a transient preview/export failure can be
        # positive. Keep that probe as evidence, but retry preview rather than
        # mislabelling it as a zero-result cell.
        if data.get("total") == 0:
            errors = validate_zero_count_artifact(data, cell)
            return {
                "cell_id": cell.cell_id,
                "status": "existing_zero_count",
                "mode": "count",
                "artifact": str(zero_existing.relative_to(SEARCH_DIR.parent)),
                "total": data.get("total"),
                "errors": errors,
            }
    preview = run_one(adapter, preview_base, cell, "preview")
    if valid_result(preview):
        return preview
    # ARC's preview writer intentionally has no zero-record output form.  A
    # fresh normal-CLI count-only run distinguishes its exact zero from a
    # source/browser error without treating either as a false match.
    count = run_one(adapter, zero_base, cell, "count")
    if valid_result(count):
        count_path = successful_attempt(zero_base)
        assert count_path is not None
        count_data = load_json(count_path)
        if count_data.get("total") == 0:
            count["status"] = "zero_count_fallback"
            count["preview_attempt"] = preview
            return count
    return {
        "cell_id": cell.cell_id,
        "status": "preview_or_zero_count_unresolved",
        "mode": "preview_then_count",
        "artifact": preview.get("artifact"),
        "total": None,
        "errors": [*preview.get("errors", []), *count.get("errors", [])],
        "preview_attempt": preview,
        "count_attempt": count,
    }


def run_final(adapter: Path) -> int:
    load_accepted_recall()
    sums = primary_sums()
    selected = final_cells_by_schedule(sums)
    reports = []
    okay = True
    for schedule_id in SCHEDULE_IDS:
        for cell in selected[schedule_id]:
            report = run_final_cell(adapter, cell)
            reports.append(report)
            okay = okay and report.get("status") in {
                "ran",
                "existing",
                "existing_zero_count",
                "zero_count_fallback",
            } and not report.get("errors")
    if okay:
        payload = {
            "schema_version": "aiaa-arc-pilot004-final-cell-capture/v1",
            "pilot": "004",
            "source": "AIAA Aerospace Research Central (ARC)",
            "diagnostic_only": True,
            "date_window": {"start": DATE_START, "end": DATE_END},
            "normal_field_row_cli": True,
            "preview_contract": "Positive cells are full non-mergeable rendered-card previews with stable DOIs. Exact zeros use a separate normal-CLI count-only fallback because preview output has no zero-record form.",
            "primary_conservative_cell_sums": sums,
            "selected_cell_counts": {key: len(value) for key, value in selected.items()},
            "cells": reports,
        }
        path = SEARCH_DIR / "final-cell-capture.json"
        if not path.exists():
            atomic_write_json(path, payload)
    print(json.dumps({"phase": "final", "status": "ok" if okay else "failure", "cells": len(reports)}, indent=2))
    return 0 if okay else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("index", "recall", "primary", "final", "all"), required=True)
    parser.add_argument("--adapter", help="Read-only repaired search_aiaa_arc.py path; defaults to AIAA_ARC_ADAPTER or the integration worktree")
    args = parser.parse_args()
    ensure_directories()
    require_shared_browser()
    adapter = adapter_path(args.adapter)
    if args.phase == "index":
        report, _ = run_index(adapter)
        print(json.dumps({"phase": "index", "report": report}, indent=2))
        return 0 if valid_result(report) else 1
    if args.phase == "recall":
        return run_recall(adapter)
    if args.phase == "primary":
        return run_primary(adapter)
    if args.phase == "final":
        return run_final(adapter)
    for phase in (run_recall, run_primary, run_final):
        status = phase(adapter)
        if status:
            return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
