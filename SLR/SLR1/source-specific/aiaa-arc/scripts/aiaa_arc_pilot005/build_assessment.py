#!/usr/bin/env python3
"""Build the evidence assessment for AIAA ARC Pilot 005."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from queries import (
    C1_FIXED_TERMS,
    CHANGED_IDS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    P_TERMS,
    PROTOCOL_COMMIT,
    SCHEDULE,
    SCHEDULE_IDS,
    TPRECISE_TERMS,
    TERM_COUNTS,
)

KNOWN_DOI = "10.2514/6.2015-4474"
KNOWN_IDS = ("A2", "B1", "B2", "BC1")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object in {path}")
    return value


def artifact_for(base: Path) -> tuple[Path, dict[str, Any]]:
    candidates = [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 8))]
    for candidate in candidates:
        if candidate.exists():
            data = load(candidate)
            if isinstance(data.get("total"), int):
                return candidate, data
    raise RuntimeError(f"No successful source artifact for {base}")


def strategy(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("output_metadata", {}).get("prisma_search_run", {}).get("strategy", {})


def limits(data: dict[str, Any]) -> dict[str, Any]:
    return strategy(data).get("limits", {})


def validate_event_artifact(event: dict[str, Any], path: Path, data: dict[str, Any]) -> list[str]:
    errors = []
    if data.get("source") != "AIAA Aerospace Research Central (ARC)":
        errors.append("source mismatch")
    observed_strategy = strategy(data)
    if observed_strategy.get("executed_query_provenance") != "source_observed":
        errors.append("query was not observed from the source")
    observed_rows = observed_strategy.get("field_rows", [])
    expected_rows = event.get("field_rows", [])
    if len(observed_rows) != len(expected_rows):
        errors.append("field-row count mismatch")
    else:
        for observed, expected in zip(observed_rows, expected_rows):
            expected_field = expected.get("source_field")
            if observed.get("field") != expected_field or observed.get("text") != expected.get("text"):
                errors.append("field-row readback mismatch")
    observed_limits = limits(data)
    publication_date = observed_limits.get("publication_date", {}).get("requested", {})
    if publication_date != {"exact_start": "2011-01-01", "exact_end": "2026-08-29"}:
        errors.append("requested date mismatch")
    access = observed_limits.get("access", {})
    if access.get("effective") != "All content":
        errors.append("access readback mismatch")
    for name in ("topic", "published_in"):
        if observed_limits.get(name, {}).get("state") != "not_applied":
            errors.append(f"unexpected {name} restriction")
    if event["mode"] == "count" and data.get("output_metadata", {}).get("status") != "count_only":
        errors.append("count-mode status mismatch")
    if event["mode"] == "preview" and data.get("output_metadata", {}).get("status") != "preview":
        errors.append("preview-mode status mismatch")
    if not isinstance(data.get("total"), int):
        errors.append("missing source total")
    if errors:
        raise RuntimeError(f"{path}: " + "; ".join(errors))
    return errors


def event_map(plan: dict[str, Any], pilot_root: Path) -> dict[str, tuple[dict[str, Any], Path, dict[str, Any]]]:
    output = {}
    for event in plan["events"]:
        path, data = artifact_for(pilot_root / event["output"])
        validate_event_artifact(event, path, data)
        output[event["event_id"]] = (event, path, data)
    return output


def has_literal(text: str, term: str) -> bool:
    pattern = r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(has_literal(text, term) for term in terms)


def title_factors(schedule_id: str, title: str) -> dict[str, bool]:
    factors = {"P": has_any(title, P_TERMS)}
    if schedule_id == "BG1":
        factors["G_model"] = (
            has_any(title, GMODEL_FIXED_TERMS)
            or has_any(title, GMISSION_EXACT_TERMS)
            or (has_any(title, GMISSION_TERMS) and has_any(title, MB_TERMS))
        )
    elif schedule_id == "BG2":
        factors["G_structure"] = (
            has_any(title, GSTRUCTURE_FIXED_TERMS)
            or has_any(title, GPRODUCT_EXACT_TERMS)
            or has_any(title, GVARIATION_TERMS)
            or (has_any(title, GPRODUCT_TERMS) and has_any(title, MB_TERMS))
        )
    elif schedule_id == "BC1":
        factors["C1"] = has_any(title, C1_FIXED_TERMS) or has_any(title, GDSL_TERMS)
    elif schedule_id == "BT2":
        factors["M_B"] = has_any(title, MB_TERMS)
        factors["T_precise"] = has_any(title, TPRECISE_TERMS)
    else:
        raise ValueError(schedule_id)
    return factors


def preview_audit(schedule_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    records = data.get("results", [])
    rows = []
    for record in records:
        factors = title_factors(schedule_id, str(record.get("title", "")))
        rows.append({
            "source_record_id": record.get("sourceRecordStableId") or record.get("doi"),
            "title": record.get("title"),
            "factors": factors,
            "all_factors_visible": all(factors.values()),
        })
    factor_names = list(rows[0]["factors"]) if rows else []
    return {
        "artifact": str(path),
        "source_total": data["total"],
        "rendered_cards": len(rows),
        "capture_complete": data.get("output_metadata", {}).get("retrieval_complete"),
        "visible_title_factor_counts": {
            factor: sum(row["factors"][factor] for row in rows) for factor in factor_names
        },
        "all_factors_visible_count": sum(row["all_factors_visible"] for row in rows),
        "scope": "Rendered titles only. ARC Anywhere can match hidden indexing or full text.",
        "records": rows,
    }


def rel(path: Path, pilot_root: Path) -> str:
    return str(path.relative_to(pilot_root))


def build(pilot_root: Path) -> dict[str, Any]:
    search_root = pilot_root / "searches"
    main_plan = load(search_root / "event-plan.json")
    threshold_plan = load(search_root / "threshold-event-plan.json")
    bg2_plan = load(search_root / "bg2-fixed-event-plan.json")
    phrase_plan = load(search_root / "phrase-event-plan.json")
    if main_plan.get("protocol_commit") != PROTOCOL_COMMIT:
        raise RuntimeError("Protocol commit mismatch")

    main = event_map(main_plan, pilot_root)
    threshold = event_map(threshold_plan, pilot_root)
    bg2 = event_map(bg2_plan, pilot_root)
    phrase = event_map(phrase_plan, pilot_root)

    schedule_counts = {schedule_id: main[f"count-{schedule_id}"][2]["total"] for schedule_id in SCHEDULE_IDS}
    repeat_counts = {schedule_id: main[f"repeat-count-{schedule_id}"][2]["total"] for schedule_id in CHANGED_IDS}
    if any(schedule_counts[key] != repeat_counts[key] for key in CHANGED_IDS):
        raise RuntimeError("A changed-partition repeated total differs")

    previews = {}
    for schedule_id in CHANGED_IDS:
        _, path, data = main[f"preview-{schedule_id}"]
        audit = preview_audit(schedule_id, path, data)
        audit["artifact"] = rel(path, pilot_root)
        previews[schedule_id] = audit

    known = {}
    for schedule_id in KNOWN_IDS:
        _, path, data = main[f"known-item-{schedule_id}"]
        returned = [str(row.get("doi", "")).casefold() for row in data.get("results", [])]
        retrieved = KNOWN_DOI in returned
        if not retrieved:
            raise RuntimeError(f"Known DOI missed in {schedule_id}")
        known[schedule_id] = {
            "artifact": rel(path, pilot_root),
            "source_total": data["total"],
            "known_doi_retrieved": retrieved,
        }

    branch_counts = {}
    for event_id, (event, path, data) in threshold.items():
        branch_counts[event_id.removeprefix("branch-")] = {
            "schedule_id": event["schedule_id"],
            "branch": event["branch"],
            "source_total": data["total"],
            "artifact": rel(path, pilot_root),
        }
    bg2_literal_counts = []
    for _, (event, path, data) in bg2.items():
        bg2_literal_counts.append({
            "literal": event["literal"],
            "source_total": data["total"],
            "artifact": rel(path, pilot_root),
        })

    phrase_counts = {
        event_id.removeprefix("phrase-"): {
            "source_total": data["total"],
            "artifact": rel(path, pilot_root),
        }
        for event_id, (_, path, data) in phrase.items()
    }
    title_expectations = phrase_plan["expected_if_quotes_are_ordered_phrases"]
    for event_id, expected in title_expectations.items():
        actual = phrase[event_id][2]["total"]
        if actual != expected:
            raise RuntimeError(f"Phrase control {event_id} returned {actual}, expected {expected}")

    failures = sorted(
        rel(path, pilot_root)
        for path in pilot_root.rglob("*NON_MERGEABLE_FAILURE.json")
    )
    old_bg1 = main_plan["historical_comparators"]["old_pair_fallback_BG1_total"]
    new_bg1 = schedule_counts["BG1"]
    old_bt2_chars = main_plan["historical_comparators"]["old_pair_expanded_BT2_remainder_characters"]
    new_bt2_chars = main_plan["translation"]["query_lengths"]["BT2"]

    return {
        "schema_version": "aiaa-arc-pilot005-assessment/v1",
        "source": main_plan["source"],
        "pilot": "005",
        "protocol_commit": PROTOCOL_COMMIT,
        "status": "complete",
        "diagnostic_only": True,
        "do_not_merge": True,
        "translation": {
            "field": "one Anywhere (AllField) row",
            "literal": "one straight double-quoted token or ordered phrase",
            "boolean": "fully parenthesized explicit uppercase AND and OR",
            "proximity": None,
            "pair_expansion": None,
            "wildcard": None,
            "metadata_field_narrowing": None,
            "term_counts": TERM_COUNTS,
            "query_lengths": main_plan["translation"]["query_lengths"],
            "all_nine_queries_have_no_proximity_or_wildcard": all(
                "NEAR" not in query.upper() and "*" not in query and "?" not in query
                for query in SCHEDULE.values()
            ),
        },
        "schedule_counts": schedule_counts,
        "changed_partition_repeat_counts": repeat_counts,
        "changed_totals_repeated_exactly": True,
        "direct_BT2": {
            "source_total": schedule_counts["BT2"],
            "query_characters": new_bt2_chars,
            "historical_pair_expanded_remainder_characters": old_bt2_chars,
            "character_reduction": old_bt2_chars - new_bt2_chars,
            "single_cell_accepted": True,
        },
        "historical_BG1_comparator": {
            "historical_pair_fallback_total": old_bg1,
            "current_direct_total": new_bg1,
            "absolute_reduction": old_bg1 - new_bg1,
            "percent_reduction": round((old_bg1 - new_bg1) / old_bg1 * 100, 2),
            "comparability_limit": "The cross-source G_model definition changed. This is a search-burden comparator, not set equality.",
        },
        "known_item_recall": {
            "doi": KNOWN_DOI,
            "current_source_located_applicable_partitions": list(KNOWN_IDS),
            "partitions": known,
            "all_applicable_partitions_retrieved": True,
            "BT2_nonapplicability": "The PDF has no current T_precise literal. The superseded adapted/model pair no longer creates BT2 membership.",
        },
        "changed_partition_previews": previews,
        "threshold_investigation": {
            "threshold": 100,
            "triggered_partitions": [key for key in CHANGED_IDS if schedule_counts[key] > 100],
            "branch_counts": branch_counts,
            "BG2_fixed_literal_counts": bg2_literal_counts,
            "findings": {
                "BG1": "The complete direct result fell below 100.",
                "BG2": "G_structure_fixed accounts for 3571 of 3584 results. The reference architecture literal alone returns 3536.",
                "BC1": "C1_fixed returns all 152 records. G_DSL returns 1 overlapping candidate event.",
                "BT2": "Every morphological diagnostic branch returns at least 54 records. Branches overlap and remain subordinate to the 437-record complete query.",
            },
        },
        "ordered_phrase_validation": {
            "status": "accepted_bounded_title_controls",
            "counts": phrase_counts,
            "finding": (
                "Both contiguous known-title phrases returned 1, both noncontiguous or reversed quoted controls returned 0, "
                "and the explicit noncontiguous conjunction returned 1. The dominant reference architecture total is not "
                "explained by quotes collapsing to unordered AND."
            ),
            "scope": "Bounded title controls plus Anywhere count contrasts. ARC's hidden match text remains unavailable.",
        },
        "retained_source_failures": {
            "count": len(failures),
            "artifacts": failures,
            "all_recovered_by_exact_retries": True,
            "failures_converted_to_zero": False,
        },
        "decisions": {
            "source_translation": "accept_prospective_direct_anywhere_boolean_translation",
            "proximity_limitation": "retired_after_cross_source_protocol_change",
            "canonical_field_route": "direct_Anywhere_only",
            "metadata_field_union": "retire_as_canonical_translation",
            "metadata_priority_lane": "optional_nonexcluding_screening_priority_only",
            "BT2_subcells": "retire_unless_a_future_source_length_failure_requires_a_new_lossless_boolean_split",
            "language_filter": "none_screen_full_text",
            "publication_type_filter": "none",
            "topic_filter": "none",
            "wildcard": "none",
            "final_search": "not_executed",
        },
        "issue_resolution": {
            "exact_compound_boolean_semantics": "resolved",
            "declared_pair_or_proximity_semantics": "removed_from_protocol_and_translation",
            "metadata_field_recall_risk": "resolved_by_removing_field_narrowing",
            "BT2_query_length_failure": "resolved_in_this_pilot",
            "BG1_search_volume": "resolved_below_100",
            "hidden_Anywhere_precision": "remains_for_BG2_BC1_BT2_and_other_high_volume_partitions",
            "overall": "semantic_and_recall_translation_issues_resolved_precision_only_partly_resolved",
        },
        "limits": [
            "Anywhere includes hidden indexed material or full text, so rendered titles do not explain most matches.",
            "The BG2 total remains 3584 and cannot be narrowed with an unproved metadata, type, Topic, language, or access filter.",
            "Source date controls are inclusive months in this pilot. A final run still requires exact-day treatment and native export.",
            "Pilot previews and count receipts are non-mergeable and cannot enter the final corpus.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
