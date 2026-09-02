#!/usr/bin/env python3
"""Assess NASA NTRS Pilot 006 maximal wildcard coverage."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import queries

SCHEMA = "ntrs-maximal-wildcard-pilot-assessment/v1"
PLAN_SCHEMA = "ntrs-maximal-wildcard-pilot-plan/v1"
RUN_SCHEMA = "ntrs-maximal-wildcard-pilot-run/v1"
HELPER_PATH = Path(__file__).resolve().parents[1] / "ntrs_pilot004" / "build_assessment.py"
_spec = importlib.util.spec_from_file_location("ntrs_pilot006_evidence_helper", HELPER_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {HELPER_PATH}")
_helper = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _helper
_spec.loader.exec_module(_helper)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sequence_hash(values: list[str]) -> str:
    result = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


def build(*, pilot_root: Path, plan_path: Path, run_path: Path) -> dict[str, Any]:
    plan = load(plan_path)
    run = load(run_path)
    validation_errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        validation_errors.append("plan schema mismatch")
    if run.get("schema_version") != RUN_SCHEMA or run.get("success") is not True:
        validation_errors.append("run receipt is not successful")
    if run.get("plan_sha256") != digest(plan_path):
        validation_errors.append("run plan binding mismatch")
    if plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        validation_errors.append("protocol commit mismatch")
    adapter_hash = plan.get("adapter", {}).get("sha256")
    if not isinstance(adapter_hash, str):
        adapter_hash = ""
        validation_errors.append("adapter hash missing")

    repository_root = Path(__file__).resolve().parents[4]
    baseline_sets: dict[str, set[str]] = {}
    baseline_rows: dict[str, dict[str, dict[str, Any]]] = {}
    for partition, receipt in plan.get("baseline", {}).get("partitions", {}).items():
        path = repository_root / receipt["path"]
        value = load(path)
        ids = [row["paperId"] for row in value.get("results", [])]
        if (
            digest(path) != receipt.get("sha256")
            or value.get("total") != receipt.get("source_total")
            or sequence_hash(ids) != receipt.get("ordered_stable_ids_sha256")
        ):
            validation_errors.append(f"baseline binding mismatch: {partition}")
        baseline_sets[partition] = set(ids)
        baseline_rows[partition] = {
            row["paperId"]: row for row in value.get("results", [])
        }

    planned = {event["event_id"]: event for event in plan.get("events", [])}
    run_events = {event["event_id"]: event for event in run.get("events", [])}
    if set(planned) != set(run_events):
        validation_errors.append("planned and completed event sets differ")
    evidence_rows: list[dict[str, Any]] = []
    wildcard_sets: dict[str, set[str]] = {}
    wildcard_rows: dict[str, dict[str, dict[str, Any]]] = {}
    retained_failures = []
    for event_id, event in planned.items():
        outcome = run_events.get(event_id, {})
        accepted = outcome.get("accepted_artifact")
        if outcome.get("success") is not True or not isinstance(accepted, str):
            validation_errors.append(f"{event_id}: no accepted artifact")
            continue
        if not accepted.startswith("searches/"):
            validation_errors.append(f"{event_id}: malformed accepted path")
            continue
        selected = dict(event)
        selected["output"] = accepted[len("searches/"):]
        evidence, _ordered, ids, rows = _helper.event_evidence(
            pilot_root=pilot_root,
            event=selected,
            adapter_hash=adapter_hash,
        )
        evidence_rows.append(evidence)
        partition = event["partition_id"]
        wildcard_sets[partition] = ids
        wildcard_rows[partition] = rows
        validation_errors.extend(
            f"{event_id}: {error}" for error in evidence["errors"]
        )
        for attempt in outcome.get("attempts", []):
            if attempt.get("artifact") == accepted:
                continue
            path = pilot_root / attempt.get("artifact", "")
            value = load(path) if path.is_file() else {}
            metadata = value.get("output_metadata", {})
            valid_failure = bool(
                attempt.get("exit_code") != 0
                and attempt.get("retryable") is True
                and value.get("total") is None
                and value.get("results") == []
                and metadata.get("status") == "error"
                and metadata.get("merge_eligible") is False
            )
            if not valid_failure:
                validation_errors.append(f"{event_id}: invalid failed attempt")
            retained_failures.append(
                {
                    "event_id": event_id,
                    "attempt": attempt.get("attempt"),
                    "path": attempt.get("artifact"),
                    "sha256": digest(path) if path.is_file() else None,
                    "error_stage": metadata.get("error_stage"),
                    "search_page_written": attempt.get("screenshot_files_written", {}).get("search_page"),
                    "results_page_written": attempt.get("screenshot_files_written", {}).get("results_page"),
                    "valid_null_failure": valid_failure,
                }
            )

    comparisons = []
    baseline_union: set[str] = set()
    wildcard_union: set[str] = set()
    for partition in queries.SCHEDULE_IDS:
        baseline = baseline_sets.get(partition, set())
        wildcard = wildcard_sets.get(partition, set())
        missing = sorted(baseline - wildcard)
        added = sorted(wildcard - baseline)
        baseline_union.update(baseline)
        wildcard_union.update(wildcard)
        comparisons.append(
            {
                "partition_id": partition,
                "literal_total": len(baseline),
                "maximal_wildcard_total": len(wildcard),
                "literal_query_characters": len(queries.LITERAL_SCHEDULE[partition]),
                "maximal_wildcard_query_characters": len(queries.WILDCARD_SCHEDULE[partition]),
                "character_reduction": (
                    len(queries.LITERAL_SCHEDULE[partition])
                    - len(queries.WILDCARD_SCHEDULE[partition])
                ),
                "wildcard_count": queries.WILDCARD_SCHEDULE[partition].count("*"),
                "missing_literal_ids": missing,
                "missing_literal_count": len(missing),
                "missing_literal_records": [
                    {
                        "paperId": stable_id,
                        "title": baseline_rows.get(partition, {}).get(stable_id, {}).get("title"),
                        "year": baseline_rows.get(partition, {}).get(stable_id, {}).get("year"),
                    }
                    for stable_id in missing
                ],
                "wildcard_only_ids": added,
                "wildcard_only_count": len(added),
                "wildcard_only_records": [
                    {
                        "paperId": stable_id,
                        "title": wildcard_rows.get(partition, {}).get(stable_id, {}).get("title"),
                        "year": wildcard_rows.get(partition, {}).get(stable_id, {}).get("year"),
                    }
                    for stable_id in added
                ],
                "set_relation": (
                    "equal"
                    if baseline == wildcard
                    else "maximal_wildcard_strict_subset"
                    if wildcard < baseline
                    else "maximal_wildcard_strict_superset"
                    if baseline < wildcard
                    else "overlapping_sets"
                ),
            }
        )

    screenshot_count = sum(
        image["valid"] for event in evidence_rows for image in event["screenshots"]
    )
    if len(evidence_rows) != 9:
        validation_errors.append("accepted event count is not nine")
    if screenshot_count != 18:
        validation_errors.append("accepted screenshot count is not 18")
    missing_count = sum(item["missing_literal_count"] for item in comparisons)
    exact = all(item["set_relation"] == "equal" for item in comparisons)
    candidate_decision = (
        "adopt_maximal_wildcard_translation"
        if exact
        else "reject_maximal_translation_retain_pilot005_standalone_wildcards"
    )
    status = "passed" if not validation_errors else "failed"
    return {
        "schema_version": SCHEMA,
        "status": status,
        "pilot": "006",
        "source": "NASA Technical Reports Server (NTRS)",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": {"path": str(plan_path), "sha256": digest(plan_path)},
        "run_receipt": {"path": str(run_path), "sha256": digest(run_path)},
        "adapter": dict(plan.get("adapter", {})),
        "accepted_source_event_count": len(evidence_rows),
        "source_attempt_count": run.get("source_attempt_count"),
        "retained_null_failure_count": len(retained_failures),
        "verified_screenshot_file_count": screenshot_count,
        "required_screenshot_file_count": 18,
        "events": evidence_rows,
        "retained_failures": retained_failures,
        "comparisons": comparisons,
        "schedule_union": {
            "literal_unique_ids": len(baseline_union),
            "maximal_wildcard_unique_ids": len(wildcard_union),
            "missing_literal_ids": sorted(baseline_union - wildcard_union),
            "missing_literal_count": len(baseline_union - wildcard_union),
            "wildcard_only_ids": sorted(wildcard_union - baseline_union),
            "wildcard_only_count": len(wildcard_union - baseline_union),
        },
        "wildcard": {
            "decision": candidate_decision,
            "candidate_count": queries.WILDCARD_ATOM_COUNT,
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "partition_level_exact_set_equality": exact,
            "partition_missing_occurrences": missing_count,
            "interpretation": (
                "The all-family candidate is not recall safe when any literal record "
                "is missing. The Pilot 005 standalone-token candidate remains the "
                "accepted wildcard boundary."
            ),
        },
        "validation_errors": validation_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    result = build(pilot_root=args.pilot_root, plan_path=args.plan, run_path=args.run_receipt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "events": result["accepted_source_event_count"],
                "screenshots": result["verified_screenshot_file_count"],
                "decision": result["wildcard"]["decision"],
                "missing_occurrences": result["wildcard"]["partition_missing_occurrences"],
                "validation_errors": len(result["validation_errors"]),
            }
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
