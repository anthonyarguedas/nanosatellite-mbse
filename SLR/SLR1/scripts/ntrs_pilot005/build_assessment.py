#!/usr/bin/env python3
"""Assess NASA NTRS Pilot 005 strict events and wildcard set equality."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import queries

SCHEMA = "ntrs-repaired-post-proximity-wildcard-pilot-assessment/v1"
PLAN_SCHEMA = "ntrs-repaired-post-proximity-wildcard-pilot-plan/v1"
RUN_SCHEMA = "ntrs-repaired-post-proximity-wildcard-pilot-run/v1"
HELPER_PATH = Path(__file__).resolve().parents[1] / "ntrs_pilot004" / "build_assessment.py"
_spec = importlib.util.spec_from_file_location("ntrs_pilot005_evidence_helper", HELPER_PATH)
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


def build(
    *, pilot_root: Path, plan_path: Path, run_receipt_path: Path
) -> dict[str, Any]:
    plan = load(plan_path)
    run = load(run_receipt_path)
    errors: list[str] = []
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("plan schema mismatch")
    if run.get("schema_version") != RUN_SCHEMA or run.get("success") is not True:
        errors.append("run receipt is not successful")
    if run.get("plan_sha256") != digest(plan_path):
        errors.append("run plan binding mismatch")
    if plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        errors.append("protocol commit mismatch")
    adapter_hash = plan.get("adapter", {}).get("sha256")
    if not isinstance(adapter_hash, str):
        adapter_hash = ""
        errors.append("adapter hash missing")

    planned = {event["event_id"]: event for event in plan.get("events", [])}
    run_events = {event["event_id"]: event for event in run.get("events", [])}
    if set(planned) != set(run_events):
        errors.append("planned and completed event sets differ")

    evidence_rows: list[dict[str, Any]] = []
    sets: dict[tuple[str, str], set[str]] = {}
    records: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    failed_attempts: list[dict[str, Any]] = []
    for event_id, event in planned.items():
        outcome = run_events.get(event_id, {})
        accepted = outcome.get("accepted_artifact")
        if outcome.get("success") is not True or not isinstance(accepted, str):
            errors.append(f"{event_id}: no accepted strict artifact")
            continue
        prefix = "searches/"
        if not accepted.startswith(prefix):
            errors.append(f"{event_id}: malformed accepted path")
            continue
        selected = dict(event)
        selected["output"] = accepted[len(prefix):]
        evidence, _ordered, stable_ids, rows = _helper.event_evidence(
            pilot_root=pilot_root,
            event=selected,
            adapter_hash=adapter_hash,
        )
        evidence_rows.append(evidence)
        key = (event["partition_id"], event["variant"])
        sets[key] = stable_ids
        records[key] = rows
        errors.extend(f"{event_id}: {error}" for error in evidence["errors"])

        for attempt in outcome.get("attempts", []):
            if attempt.get("artifact") == accepted:
                continue
            artifact = pilot_root / attempt.get("artifact", "")
            value = load(artifact) if artifact.is_file() else {}
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
                errors.append(f"{event_id}: invalid retained failed attempt")
            failed_attempts.append(
                {
                    "event_id": event_id,
                    "attempt": attempt.get("attempt"),
                    "path": attempt.get("artifact"),
                    "sha256": digest(artifact) if artifact.is_file() else None,
                    "error_stage": metadata.get("error_stage"),
                    "search_page_written": attempt.get("screenshot_files_written", {}).get("search_page"),
                    "results_page_written": attempt.get("screenshot_files_written", {}).get("results_page"),
                    "valid_null_failure": valid_failure,
                }
            )

    comparisons = []
    literal_union: set[str] = set()
    wildcard_union: set[str] = set()
    for partition in queries.SCHEDULE_IDS:
        literal = sets.get((partition, "literal"), set())
        wildcard = sets.get((partition, "wildcard"), set())
        missing = sorted(literal - wildcard)
        added = sorted(wildcard - literal)
        literal_union.update(literal)
        wildcard_union.update(wildcard)
        wildcard_rows = records.get((partition, "wildcard"), {})
        comparisons.append(
            {
                "partition_id": partition,
                "literal_total": len(literal),
                "wildcard_total": len(wildcard),
                "literal_query_characters": len(queries.LITERAL_SCHEDULE[partition]),
                "wildcard_query_characters": len(queries.WILDCARD_SCHEDULE[partition]),
                "character_reduction": (
                    len(queries.LITERAL_SCHEDULE[partition])
                    - len(queries.WILDCARD_SCHEDULE[partition])
                ),
                "wildcard_count": queries.WILDCARD_SCHEDULE[partition].count("*"),
                "missing_literal_ids": missing,
                "missing_literal_count": len(missing),
                "wildcard_only_ids": added,
                "wildcard_only_count": len(added),
                "wildcard_only_records": [
                    {
                        "paperId": stable_id,
                        "title": wildcard_rows.get(stable_id, {}).get("title"),
                        "year": wildcard_rows.get(stable_id, {}).get("year"),
                    }
                    for stable_id in added
                ],
                "set_relation": (
                    "equal"
                    if literal == wildcard
                    else "wildcard_strict_superset"
                    if literal < wildcard
                    else "missing_literal_records"
                ),
            }
        )

    exact = all(item["set_relation"] == "equal" for item in comparisons)
    missing_union = sorted(literal_union - wildcard_union)
    added_union = sorted(wildcard_union - literal_union)
    if not exact:
        errors.append("partition-level literal-wildcard equality failed")
    accepted_screenshots = sum(
        image["valid"] for event in evidence_rows for image in event["screenshots"]
    )
    if len(evidence_rows) != 18:
        errors.append("accepted source event count is not 18")
    if accepted_screenshots != 36:
        errors.append("accepted screenshot count is not 36")
    status = "passed" if not errors else "failed"
    decision = (
        "adopt_standalone_wildcards_for_all_main_partitions"
        if status == "passed"
        else "retain_literal_translation_pending_follow_up"
    )
    return {
        "schema_version": SCHEMA,
        "status": status,
        "pilot": "005",
        "source": "NASA Technical Reports Server (NTRS)",
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": {"path": str(plan_path), "sha256": digest(plan_path)},
        "run_receipt": {
            "path": str(run_receipt_path),
            "sha256": digest(run_receipt_path),
        },
        "adapter": dict(plan.get("adapter", {})),
        "accepted_source_event_count": len(evidence_rows),
        "source_attempt_count": run.get("source_attempt_count"),
        "retained_null_failure_count": len(failed_attempts),
        "verified_accepted_screenshot_file_count": accepted_screenshots,
        "required_accepted_screenshot_file_count": 36,
        "events": evidence_rows,
        "retained_failures": failed_attempts,
        "comparisons": comparisons,
        "schedule_union": {
            "literal_unique_ids": len(literal_union),
            "wildcard_unique_ids": len(wildcard_union),
            "missing_literal_ids": missing_union,
            "missing_literal_count": len(missing_union),
            "wildcard_only_ids": added_union,
            "wildcard_only_count": len(added_union),
            "set_relation": "equal" if literal_union == wildcard_union else "different",
        },
        "wildcard": {
            "decision": decision,
            "candidate_count": queries.WILDCARD_ATOM_COUNT,
            "replaced_literal_count": queries.REPLACED_LITERAL_COUNT,
            "phrase_wildcards_used": False,
            "acronym_wildcards_used": False,
            "partition_level_exact_set_equality": exact,
        },
        "errors": errors,
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
    result = build(
        pilot_root=args.pilot_root,
        plan_path=args.plan,
        run_receipt_path=args.run_receipt,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "events": result["accepted_source_event_count"],
                "attempts": result["source_attempt_count"],
                "screenshots": result["verified_accepted_screenshot_file_count"],
                "decision": result["wildcard"]["decision"],
                "errors": len(result["errors"]),
            }
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
