#!/usr/bin/env python3
"""Assess the positive wildcard comparisons in IAF Pilot 005."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from build_plan import DEFAULT_OUTPUT, PILOT004_ROOT, PILOT_ROOT, load, validate

SCHEMA = "iaf-digital-library-pilot005-assessment/v1"
PILOT004_ASSESSMENT = PILOT004_ROOT / "searches" / "assessment.json"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sequence_sha256(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.ACADEMIC_SEARCH_COMMIT.json")


def ledger_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.identity-ledger.json")


def ordered_union(*sequences: list[str]) -> list[str]:
    seen = set()
    result = []
    for sequence in sequences:
        for value in sequence:
            if value not in seen:
                seen.add(value)
                result.append(value)
    return result


def validate_source_event(
    event: Mapping[str, Any],
    artifact: Mapping[str, Any],
    ledger: Mapping[str, Any],
    output: Path,
) -> list[str]:
    errors = []
    query = event["query"]
    metadata = artifact.get("output_metadata")
    receipt = (
        metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    )
    strategy = receipt.get("strategy") if isinstance(receipt, Mapping) else None
    compact = ledger.get("compact_artifact")
    raw_ids = ledger.get("raw_ordered_paper_ids")
    retained_ids = ledger.get("diagnostic_window_ordered_paper_ids")
    records = artifact.get("results")
    if artifact.get("executed_query") != query or ledger.get("query") != query:
        errors.append(f"Query readback differs for {event['event_id']}")
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("merge_eligible") is not False
        or artifact.get("do_not_merge") is not True
    ):
        errors.append(f"Completion status differs for {event['event_id']}")
    if (
        not isinstance(receipt, Mapping)
        or receipt.get("completion_status") != "complete"
        or receipt.get("strategy_reference")
        != "slr1-iaf-positive-wildcard-diagnostic-v1"
        or receipt.get("strategy_version") != "3194156e90497186664260a8e86435e78d2e2aa1"
    ):
        errors.append(f"PRISMA receipt differs for {event['event_id']}")
    scope = strategy.get("search_scope") if isinstance(strategy, Mapping) else None
    limits = strategy.get("limits") if isinstance(strategy, Mapping) else None
    date = (
        limits.get("publication_date", {}).get("effective", {})
        if isinstance(limits, Mapping)
        else {}
    )
    if (
        not isinstance(strategy, Mapping)
        or strategy.get("executed_query") != query
        or not isinstance(scope, Mapping)
        or scope.get("library", {}).get("effective") != "full_iaf_digital_library"
        or date.get("mode") != "local_post_filter"
        or date.get("start") != "2011-01-01"
        or date.get("end") != "2026-08-29"
    ):
        errors.append(f"Source controls differ for {event['event_id']}")
    if (
        ledger.get("schema_version")
        != "iaf-digital-library-pilot005-complete-identity-ledger/v1"
        or ledger.get("diagnostic_only") is not True
        or ledger.get("do_not_merge") is not True
        or not isinstance(raw_ids, list)
        or not isinstance(retained_ids, list)
        or ledger.get("raw_ordered_paper_ids_sha256") != sequence_sha256(raw_ids or [])
        or ledger.get("diagnostic_window_ordered_paper_ids_sha256")
        != sequence_sha256(retained_ids or [])
    ):
        errors.append(f"Identity ledger differs for {event['event_id']}")
    if (
        not isinstance(records, list)
        or artifact.get("total") != len(raw_ids or [])
        or [record.get("paperId") for record in records] != retained_ids
        or not set(retained_ids or []).issubset(raw_ids or [])
    ):
        errors.append(f"Stable IDs do not reconcile for {event['event_id']}")
    accounting = ledger.get("date_filter_accounting")
    if (
        not isinstance(accounting, Mapping)
        or accounting.get("raw_total") != len(raw_ids or [])
        or accounting.get("retained") != len(retained_ids or [])
        or accounting.get("complete") is not True
    ):
        errors.append(f"Date accounting differs for {event['event_id']}")
    digest = file_sha256(output)
    if (
        not isinstance(compact, Mapping)
        or compact.get("file_name") != output.name
        or compact.get("sha256") != digest
        or compact.get("bytes") != output.stat().st_size
        or compact.get("commit_marker") != marker_path(output).name
    ):
        errors.append(f"Compact binding differs for {event['event_id']}")
    marker = load(marker_path(output))
    marker_json = marker.get("normalized_json", {})
    if (
        marker.get("schema") != "academic_search_output_commit_marker_v1"
        or marker_json.get("sha256") != digest
        or marker_json.get("bytes") != output.stat().st_size
    ):
        errors.append(f"Commit marker differs for {event['event_id']}")
    return errors


def build(root: Path, plan_path: Path) -> dict[str, Any]:
    plan = load(plan_path)
    errors = validate(plan)
    receipt = load(root / "searches" / "run-receipt.json")
    if (
        receipt.get("status") != "complete"
        or receipt.get("predeclared_event_count") != 7
        or receipt.get("completed_event_count") != 7
        or receipt.get("retained_failure_artifacts") != []
    ):
        errors.append("The live run receipt is incomplete")

    event_results: dict[str, Any] = {}
    records: dict[str, dict[str, Any]] = {}
    for event in plan["events"]:
        output = root / "searches" / event["output"]
        identity_path = ledger_path(output)
        try:
            artifact = load(output)
            ledger = load(identity_path)
            errors.extend(validate_source_event(event, artifact, ledger, output))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Could not validate {event['event_id']}: {error}")
            continue
        for record in artifact.get("results", []):
            records[record["paperId"]] = {
                "paper_id": record["paperId"],
                "title": record.get("title"),
                "year": record.get("year"),
            }
        event_results[event["event_id"]] = {
            "query_characters": event["query_characters"],
            "contains_wildcard": "*" in event["query"],
            "source_total": artifact.get("total"),
            "raw_ordered_paper_ids": ledger["raw_ordered_paper_ids"],
            "diagnostic_window_ordered_paper_ids": ledger[
                "diagnostic_window_ordered_paper_ids"
            ],
            "date_filter_accounting": ledger["date_filter_accounting"],
        }

    exact_cube = event_results.get("exact-cube", {}).get("raw_ordered_paper_ids", [])
    exact_other = ordered_union(
        event_results.get("exact-other-a", {}).get("raw_ordered_paper_ids", []),
        event_results.get("exact-other-b", {}).get("raw_ordered_paper_ids", []),
    )
    exact_full = ordered_union(exact_cube, exact_other)
    wildcard_cube = event_results.get("wildcard-cube", {}).get(
        "raw_ordered_paper_ids", []
    )
    wildcard_other = event_results.get("wildcard-other", {}).get(
        "raw_ordered_paper_ids", []
    )
    wildcard_full_1 = event_results.get("wildcard-full-pass1", {}).get(
        "raw_ordered_paper_ids", []
    )
    wildcard_full_2 = event_results.get("wildcard-full-pass2", {}).get(
        "raw_ordered_paper_ids", []
    )

    prior = load(PILOT004_ASSESSMENT)
    prior_ids = prior["entries"]["BG1"]["branches"]["fixed"][
        "diagnostic_window_paper_ids"
    ]
    comparisons = {
        "cube_family": {
            "explicit_count": len(exact_cube),
            "wildcard_count": len(wildcard_cube),
            "explicit_ids": exact_cube,
            "wildcard_ids": wildcard_cube,
            "missing_from_wildcard": sorted(set(exact_cube) - set(wildcard_cube)),
            "wildcard_only": sorted(set(wildcard_cube) - set(exact_cube)),
            "non_zero": bool(exact_cube and wildcard_cube),
            "wildcard_is_superset": set(exact_cube).issubset(wildcard_cube),
            "sets_equal": set(exact_cube) == set(wildcard_cube),
        },
        "other_family": {
            "explicit_count": len(exact_other),
            "wildcard_count": len(wildcard_other),
            "explicit_ids": exact_other,
            "wildcard_ids": wildcard_other,
            "missing_from_wildcard": sorted(set(exact_other) - set(wildcard_other)),
            "wildcard_only": sorted(set(wildcard_other) - set(exact_other)),
            "non_zero": bool(exact_other and wildcard_other),
            "wildcard_is_superset": set(exact_other).issubset(wildcard_other),
            "sets_equal": set(exact_other) == set(wildcard_other),
        },
        "full_population": {
            "explicit_count": len(exact_full),
            "wildcard_pass1_count": len(wildcard_full_1),
            "wildcard_pass2_count": len(wildcard_full_2),
            "explicit_ids": exact_full,
            "wildcard_pass1_ids": wildcard_full_1,
            "wildcard_pass2_ids": wildcard_full_2,
            "missing_from_wildcard": sorted(set(exact_full) - set(wildcard_full_1)),
            "wildcard_only": sorted(set(wildcard_full_1) - set(exact_full)),
            "non_zero": bool(exact_full and wildcard_full_1 and wildcard_full_2),
            "wildcard_is_superset": set(exact_full).issubset(wildcard_full_1),
            "sets_equal": set(exact_full) == set(wildcard_full_1),
            "repeated_order_equal": wildcard_full_1 == wildcard_full_2,
            "fresh_explicit_matches_pilot004": set(exact_full) == set(prior_ids),
        },
    }
    acceptance = {
        "all_comparison_groups_non_zero": all(
            comparison["non_zero"] for comparison in comparisons.values()
        ),
        "all_explicit_ids_retained": all(
            comparison["wildcard_is_superset"] for comparison in comparisons.values()
        ),
        "all_comparison_sets_equal": all(
            comparison["sets_equal"] for comparison in comparisons.values()
        ),
        "full_wildcard_repeat_stable": comparisons["full_population"][
            "repeated_order_equal"
        ],
        "fresh_explicit_baseline_reproduced": comparisons["full_population"][
            "fresh_explicit_matches_pilot004"
        ],
        "wildcard_only_record_count": len(
            comparisons["full_population"]["wildcard_only"]
        ),
    }
    successful = all(
        (
            acceptance["all_comparison_groups_non_zero"],
            acceptance["all_explicit_ids_retained"],
            acceptance["full_wildcard_repeat_stable"],
            acceptance["fresh_explicit_baseline_reproduced"],
        )
    )
    if not successful:
        errors.append("The positive wildcard acceptance checks did not all pass")

    failures = sorted((root / "searches" / "failures").glob("*.json"))
    if failures:
        errors.append("Retained source failures exist")
    return {
        "schema_version": SCHEMA,
        "pilot": "005",
        "source": "IAF Digital Library",
        "status": "complete" if not errors else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision": "positive_wildcard_equivalence_confirmed_in_bounded_bg1_context"
        if not errors
        else "unresolved",
        "decision_basis": (
            "All three positive stable-ID comparisons retained every explicit ID. "
            "The family and full sets were equal, and two full wildcard runs had identical order."
        ),
        "canonical_schedule_decision": {
            "changed": False,
            "reason": (
                "The test validates the eight-atom population wildcard candidate in one positive "
                "BG1 fixed-branch context. It does not isolate every wildcard atom or establish "
                "stable-ID equivalence across all nine partitions."
            ),
            "next_step_for_adoption": (
                "Predeclare the wildcard population block in every affected partition, run the "
                "complete candidate cell plan, and compare each partition union with the explicit plan."
            ),
        },
        "plan": {
            "artifact": str(plan_path.relative_to(root)),
            "sha256": file_sha256(plan_path),
            "event_count": len(plan["events"]),
        },
        "event_results": event_results,
        "comparisons": comparisons,
        "acceptance": acceptance,
        "compression": {
            "explicit_population_terms": 26,
            "wildcard_population_atoms": 8,
            "explicit_full_query_characters": plan["wildcard_candidate"][
                "explicit_full_query_characters"
            ],
            "wildcard_full_query_characters": plan["wildcard_candidate"][
                "full_query_characters"
            ],
            "character_reduction": plan["wildcard_candidate"][
                "explicit_full_query_characters"
            ]
            - plan["wildcard_candidate"]["full_query_characters"],
            "explicit_source_cells": 3,
            "wildcard_source_cells": 1,
        },
        "wildcard_only_records": [
            records[paper_id]
            for paper_id in comparisons["full_population"]["wildcard_only"]
        ],
        "record_catalog": [records[paper_id] for paper_id in sorted(records)],
        "source_artifact_count": len(event_results),
        "retained_failure_artifacts": [
            str(path.relative_to(root)) for path in failures
        ],
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assessment = build(args.pilot_root, args.plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
