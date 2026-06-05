#!/usr/bin/env python3
"""Prioritize future-research gaps for E13 over the SLR1 evidence base.

The scoring is transparent and intentionally exploratory. It combines gap
mapping levels with weak evidence, EPS-specific evidence needs, lifecycle
undercoverage, model unavailability, and missing independent/physical
validation signals from the flattened extraction and controlled analyses.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from kg_common import (
    DATA_DIR,
    REPORTS_DIR,
    TABLES_DIR,
    clean_text,
    dedupe_study_codes,
    ensure_dirs,
    ensure_issue001_outputs,
    is_none_like,
    join_values,
    load_jsonl,
    markdown_table,
    unique_preserve,
    values,
    write_csv,
    write_text,
)


EPS_RELEVANCE_FIELD = "study_context_population.eps_relevance"
EPS_ELEMENTS_FIELD = "eps_verification_specific.eps_elements_modeled"
VERIFICATION_MECHANISM_FIELD = "eps_verification_specific.pre_physical_development_verification_mechanism"
LIFECYCLE_FIELD = "study_context_population.lifecycle_stage_addressed"
REUSE_FIELD = "mbse_objective_scope_artifacts.generality_reuse_mechanism"
MODEL_ARTIFACT_FIELD = "mbse_objective_scope_artifacts.model_artifacts_used"
MODEL_MATURITY_FIELD = "study_context_population.model_maturity"

FORMULA_VERSION = "e13_gap_priority_v1"
WEAK_OR_UNSUPPORTED = {"Weak", "Unsupported"}
LATE_LIFECYCLE_MARKERS = ["pdr", "cdr", "integration", "test", "implementation", "operations", "flight"]

LEVEL_NEED_WEIGHTS = {
    "addressed with evidence": 0.0,
    "addressed conceptually": 1.0,
    "mentioned only": 2.0,
    "not addressed": 3.0,
}

RECOMMENDATIONS = {
    "newspace_agile_distributed_rapid_iteration_alignment": "Design and evaluate MBSE workflows for rapid, distributed NewSpace iteration, including evidence from multi-team use, versioned model repositories, and independent validation beyond concept demonstrations.",
    "governance_project_deliverables_roi": "Connect models to project deliverables, governance gates, cost/schedule baselines, and ROI evidence; prioritize studies with explicit comparators and decision records.",
    "lightweight_resource_constrained_tailoring": "Develop lightweight EPS/nanosatellite-specific tailoring patterns that preserve verification rigor while reducing modeling burden for resource-constrained teams.",
    "toolchain_fragmentation_interoperability": "Evaluate open, interoperable toolchains with reproducible transformations, APIs/co-simulation links, and traceable data handoffs across SysML, analysis, simulation, and requirements tools.",
    "practical_implementation_pathway": "Publish implementation playbooks, reference workflows, and reusable artifacts with evidence from project application and independent replication.",
}

CSV_COLUMNS = [
    "rank",
    "gap",
    "gap_priority_score",
    "frequency",
    "raw_frequency_studies",
    "weak_evidence_weight",
    "eps_specificity_weight",
    "lifecycle_undercoverage_weight",
    "model_unavailability_weight",
    "no_independent_validation_weight",
    "level_addressed_with_evidence",
    "level_addressed_conceptually",
    "level_mentioned_only",
    "level_not_addressed",
    "underaddressed_study_count",
    "weak_unsupported_claims_in_contributing_studies",
    "eps_need_study_count",
    "lifecycle_undercovered_study_count",
    "model_unavailable_study_count",
    "no_independent_validation_study_count",
    "no_physical_test_or_flight_evidence_study_count",
    "top_limitation_flags",
    "example_studies",
    "example_rationales",
    "recommendation",
    "formula_version",
    "exploratory",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_field_index(study_codes: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in study_codes:
        study_id = clean_text(record.get("study_id"))
        field_path = clean_text(record.get("field_path"))
        value = clean_text(record.get("value"))
        if study_id and field_path and value is not None:
            out[study_id][field_path].append(record)
    return {study_id: dict(fields) for study_id, fields in out.items()}


def field_values(field_index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_path: str) -> list[str]:
    return unique_preserve(
        value
        for value in (clean_text(record.get("value")) for record in field_index.get(study_id, {}).get(field_path, []))
        if value
    )


def meaningful_values(field_index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_path: str) -> list[str]:
    return [value for value in field_values(field_index, study_id, field_path) if not is_none_like(value)]


def limitations_by_study(limitations: Iterable[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for limitation in limitations:
        flag = clean_text(limitation.get("flag"))
        if flag:
            out[str(limitation["study_id"])].add(flag)
    return dict(out)


def claims_by_study(claims: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        out[str(claim["study_id"])].append(claim)
    return dict(out)


def level_key(level: Any) -> str:
    return (clean_text(level) or "not reported").strip().lower()


def is_underaddressed(level: Any) -> bool:
    return level_key(level) != "addressed with evidence"


def level_need_weight(level: Any) -> float:
    return LEVEL_NEED_WEIGHTS.get(level_key(level), 1.0)


def is_eps_relevant(field_index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str) -> bool:
    values_out = [
        *meaningful_values(field_index, study_id, EPS_RELEVANCE_FIELD),
        *meaningful_values(field_index, study_id, EPS_ELEMENTS_FIELD),
    ]
    if not values_out:
        return False
    for value in values_out:
        lower = value.lower()
        if "not eps" in lower or "system-level only" in lower:
            continue
        return True
    return False


def has_late_lifecycle(field_index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str) -> bool:
    stages = " | ".join(meaningful_values(field_index, study_id, LIFECYCLE_FIELD)).lower()
    return any(marker in stages for marker in LATE_LIFECYCLE_MARKERS)


def lifecycle_undercovered(field_index: dict[str, dict[str, list[dict[str, Any]]]], limitation_flags: set[str], study_id: str) -> bool:
    return "incomplete_lifecycle_coverage" in limitation_flags or not has_late_lifecycle(field_index, study_id)


def weak_unsupported_claim_count(claims: Iterable[dict[str, Any]]) -> int:
    return sum(1 for claim in claims if (clean_text(claim.get("evidence_confidence")) or "") in WEAK_OR_UNSUPPORTED)


def top_flags(flags_by_study: dict[str, set[str]], study_ids: Iterable[str], max_items: int = 8) -> str:
    counter: Counter[str] = Counter()
    for study_id in study_ids:
        counter.update(flags_by_study.get(study_id, set()))
    return "; ".join(f"{flag} ({count})" for flag, count in counter.most_common(max_items))


def snippet(value: Any, max_chars: int = 300) -> str:
    text = clean_text(value) or ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def example_rationales(records: list[dict[str, Any]], max_items: int = 4) -> str:
    sorted_records = sorted(
        records,
        key=lambda row: (-level_need_weight(row.get("level")), str(row.get("study_id")), str(row.get("gap_mapping_id"))),
    )
    examples = []
    for record in sorted_records:
        text = clean_text(record.get("evidence_quote")) or clean_text(record.get("rationale"))
        if text:
            examples.append(f"{record.get('study_id')}[{record.get('level')}]: {snippet(text, 220)}")
        if len(examples) >= max_items:
            break
    return " | ".join(examples)


def load_inputs() -> dict[str, Any]:
    ensure_issue001_outputs()
    ensure_dirs(TABLES_DIR, REPORTS_DIR)
    studies = load_jsonl(DATA_DIR / "studies.jsonl")
    study_codes = dedupe_study_codes(load_jsonl(DATA_DIR / "study_codes.jsonl"))
    claims = load_jsonl(DATA_DIR / "claims.jsonl")
    limitations = load_jsonl(DATA_DIR / "limitations.jsonl")
    gap_mappings = load_jsonl(DATA_DIR / "gap_mappings.jsonl")
    field_index = build_field_index(study_codes)
    return {
        "studies": studies,
        "studies_by_id": {str(study["study_id"]): study for study in studies},
        "study_codes": study_codes,
        "field_index": field_index,
        "claims": claims,
        "claims_by_study": claims_by_study(claims),
        "limitations": limitations,
        "limitations_by_study": limitations_by_study(limitations),
        "gap_mappings": gap_mappings,
        "lifecycle_coverage_rows": read_csv_rows(TABLES_DIR / "lifecycle_coverage.csv"),
        "gap_limitation_heatmap_rows": read_csv_rows(TABLES_DIR / "gap_limitation_heatmap.csv"),
    }


def score_gap(gap: str, records: list[dict[str, Any]], data: dict[str, Any]) -> dict[str, Any]:
    field_index = data["field_index"]
    limitations = data["limitations_by_study"]
    claims_index = data["claims_by_study"]
    level_counts = Counter(level_key(record.get("level")) for record in records)
    raw_studies = sorted({str(record["study_id"]) for record in records})
    under_records = [record for record in records if is_underaddressed(record.get("level"))]
    under_studies = sorted({str(record["study_id"]) for record in under_records})

    frequency = len(under_studies)
    weak_claims = sum(min(5, weak_unsupported_claim_count(claims_index.get(study_id, []))) for study_id in under_studies)
    # Weak evidence combines gap-addressing level severity with capped weak/unsupported claim counts.
    weak_evidence_weight = sum(level_need_weight(record.get("level")) for record in under_records) + 0.10 * weak_claims

    eps_need_studies = []
    lifecycle_studies = []
    model_unavailable_studies = []
    no_independent_validation_studies = []
    no_physical_studies = []
    for study_id in under_studies:
        flags = limitations.get(study_id, set())
        if is_eps_relevant(field_index, study_id) and (
            "no_eps_specific_evidence" in flags
            or "no_pre_physical_verification_model" in flags
            or "no_physical_test_or_flight_evidence" in flags
            or meaningful_values(field_index, study_id, EPS_ELEMENTS_FIELD)
        ):
            eps_need_studies.append(study_id)
        if lifecycle_undercovered(field_index, flags, study_id):
            lifecycle_studies.append(study_id)
        if "model_not_available" in flags:
            model_unavailable_studies.append(study_id)
        if "no_independent_validation" in flags:
            no_independent_validation_studies.append(study_id)
        if "no_physical_test_or_flight_evidence" in flags:
            no_physical_studies.append(study_id)

    eps_specificity_weight = 0.50 * len(eps_need_studies)
    lifecycle_undercoverage_weight = 0.50 * len(lifecycle_studies)
    model_unavailability_weight = 0.50 * len(model_unavailable_studies)
    no_independent_validation_weight = 0.50 * len(set(no_independent_validation_studies) | set(no_physical_studies))

    score = (
        frequency
        + weak_evidence_weight
        + eps_specificity_weight
        + lifecycle_undercoverage_weight
        + model_unavailability_weight
        + no_independent_validation_weight
    )

    example_studies = sorted(
        under_studies,
        key=lambda sid: (
            -int(sid in eps_need_studies),
            -int(sid in model_unavailable_studies),
            -weak_unsupported_claim_count(claims_index.get(sid, [])),
            sid,
        ),
    )[:10]

    return {
        "rank": 0,
        "gap": gap,
        "gap_priority_score": f"{score:.2f}",
        "frequency": frequency,
        "raw_frequency_studies": len(raw_studies),
        "weak_evidence_weight": f"{weak_evidence_weight:.2f}",
        "eps_specificity_weight": f"{eps_specificity_weight:.2f}",
        "lifecycle_undercoverage_weight": f"{lifecycle_undercoverage_weight:.2f}",
        "model_unavailability_weight": f"{model_unavailability_weight:.2f}",
        "no_independent_validation_weight": f"{no_independent_validation_weight:.2f}",
        "level_addressed_with_evidence": level_counts.get("addressed with evidence", 0),
        "level_addressed_conceptually": level_counts.get("addressed conceptually", 0),
        "level_mentioned_only": level_counts.get("mentioned only", 0),
        "level_not_addressed": level_counts.get("not addressed", 0),
        "underaddressed_study_count": len(under_studies),
        "weak_unsupported_claims_in_contributing_studies": weak_claims,
        "eps_need_study_count": len(eps_need_studies),
        "lifecycle_undercovered_study_count": len(lifecycle_studies),
        "model_unavailable_study_count": len(model_unavailable_studies),
        "no_independent_validation_study_count": len(no_independent_validation_studies),
        "no_physical_test_or_flight_evidence_study_count": len(no_physical_studies),
        "top_limitation_flags": top_flags(limitations, under_studies),
        "example_studies": "; ".join(example_studies),
        "example_rationales": example_rationales(under_records),
        "recommendation": RECOMMENDATIONS.get(gap, "Prioritize studies that convert conceptual coverage into reusable artifacts with independent validation and explicit evidence comparators."),
        "formula_version": FORMULA_VERSION,
        "exploratory": True,
    }


def score_all_gaps(data: dict[str, Any]) -> list[dict[str, Any]]:
    by_gap: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in data["gap_mappings"]:
        gap = clean_text(record.get("gap"))
        if gap:
            by_gap[gap].append(record)
    rows = [score_gap(gap, records, data) for gap, records in sorted(by_gap.items())]
    rows.sort(
        key=lambda row: (
            -float(row["gap_priority_score"]),
            -int(row["frequency"]),
            -int(row["level_not_addressed"]),
            row["gap"],
        )
    )
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def lifecycle_summary_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("lifecycle_coverage_rows") or []
    if not rows:
        return []
    out = []
    for row in rows:
        weak = int(row.get("weak_claims") or 0) + int(row.get("unsupported_claims") or 0)
        strong = int(row.get("strong_claims") or 0) + int(row.get("moderate_claims") or 0)
        out.append(
            {
                "lifecycle_stage": row.get("lifecycle_stage", ""),
                "study_count": row.get("study_count", ""),
                "claim_count": row.get("claim_count", ""),
                "weak_or_unsupported_claims": weak,
                "moderate_or_strong_claims": strong,
                "verification_artifact_count": row.get("verification_artifact_count", ""),
            }
        )
    out.sort(key=lambda row: (-int(row.get("weak_or_unsupported_claims") or 0), -int(row.get("study_count") or 0), str(row.get("lifecycle_stage"))))
    return out[:10]


def write_future_agenda(rows: list[dict[str, Any]], data: dict[str, Any]) -> None:
    top_rows = rows[:5]
    lines = [
        "# Future research agenda from E13 gap prioritization",
        "",
        "**Exploratory notice:** this agenda ranks research needs over the 40-study SLR1 extraction. It is a transparent prioritization aid, not a statistical significance test.",
        "",
        "## Ranked priorities",
        "",
        markdown_table(
            top_rows,
            ["rank", "gap", "gap_priority_score", "frequency", "weak_evidence_weight", "eps_specificity_weight", "model_unavailable_study_count", "recommendation"],
            max_rows=10,
        ),
        "",
        "## Recommended agenda items",
        "",
    ]
    for row in top_rows:
        lines.extend(
            [
                f"### {row['rank']}. `{row['gap']}`",
                "",
                f"- Priority score: **{row['gap_priority_score']}** using `{FORMULA_VERSION}`.",
                f"- Evidence need: {row['frequency']} under-addressed studies out of {row['raw_frequency_studies']} mapped studies; levels = addressed with evidence {row['level_addressed_with_evidence']}, conceptual {row['level_addressed_conceptually']}, mentioned only {row['level_mentioned_only']}, not addressed {row['level_not_addressed']}.",
                f"- Main signals: weak evidence weight {row['weak_evidence_weight']}; EPS-specific need {row['eps_specificity_weight']}; lifecycle undercoverage {row['lifecycle_undercoverage_weight']}; model unavailability {row['model_unavailability_weight']}; independent/physical validation gap {row['no_independent_validation_weight']}.",
                f"- Proposed focus: {row['recommendation']}",
                f"- Example contributing studies: {row['example_studies']}",
                "",
            ]
        )
    lifecycle_rows = lifecycle_summary_rows(data)
    if lifecycle_rows:
        lines.extend(
            [
                "## Lifecycle evidence context from E6",
                "",
                "Lifecycle coverage is used as a quality-control context for the lifecycle-undercoverage component; it is not a separate statistical model.",
                "",
                markdown_table(
                    lifecycle_rows,
                    ["lifecycle_stage", "study_count", "claim_count", "weak_or_unsupported_claims", "moderate_or_strong_claims", "verification_artifact_count"],
                    max_rows=10,
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Caveats",
            "",
            "- Gap mappings appear for every study; the ranking therefore emphasizes under-addressed mappings (`addressed conceptually`, `mentioned only`, `not addressed`) rather than raw mapping presence alone.",
            "- Limitation flags such as `no_independent_validation` and `incomplete_lifecycle_coverage` are frequent across this corpus, so they should be interpreted as systematic bottleneck signals, not study-level blame.",
            "- Model availability is inferred from extracted limitation/reproducibility fields and was not rechecked online.",
        ]
    )
    write_text(REPORTS_DIR / "future_research_agenda.md", "\n".join(lines))


def write_method_report(rows: list[dict[str, Any]], data: dict[str, Any]) -> None:
    formula = "gap_priority = frequency + weak_evidence_weight + eps_specificity_weight + lifecycle_undercoverage_weight + model_unavailability_weight + no_independent_validation_weight"
    top_rows = rows[:5]
    level_rows = []
    for row in rows:
        level_rows.append(
            {
                "gap": row["gap"],
                "addressed_with_evidence": row["level_addressed_with_evidence"],
                "addressed_conceptually": row["level_addressed_conceptually"],
                "mentioned_only": row["level_mentioned_only"],
                "not_addressed": row["level_not_addressed"],
                "underaddressed_study_count": row["underaddressed_study_count"],
            }
        )
    heatmap_note = "available" if data.get("gap_limitation_heatmap_rows") else "not available"
    lifecycle_note = "available" if data.get("lifecycle_coverage_rows") else "not available"
    text = f"""# E13 — Research agenda prioritization

**Exploratory notice:** scores rank research-agenda needs over the SLR1 40-study extraction. They are deterministic and transparent, but they are not statistical significance estimates.

## Formula

```text
{formula}
```

Formula version: `{FORMULA_VERSION}`.

Component definitions used in this implementation:

- `frequency`: number of unique studies where the gap is **not** coded `addressed with evidence`.
- `weak_evidence_weight`: sum of gap-level severity (`addressed conceptually` = 1, `mentioned only` = 2, `not addressed` = 3) plus `0.10 ×` capped weak/unsupported claim counts in those contributing studies.
- `eps_specificity_weight`: `0.50 ×` under-addressed studies that are EPS-relevant/EPS-element-bearing and have EPS evidence needs or no physical/pre-physical evidence signals.
- `lifecycle_undercoverage_weight`: `0.50 ×` under-addressed studies with `incomplete_lifecycle_coverage` or no later lifecycle markers.
- `model_unavailability_weight`: `0.50 ×` under-addressed studies with `model_not_available`.
- `no_independent_validation_weight`: `0.50 ×` under-addressed studies with `no_independent_validation` or `no_physical_test_or_flight_evidence`.

Inputs: `data/gap_mappings.jsonl`, `data/claims.jsonl`, `data/limitations.jsonl`, `data/study_codes.jsonl`; E6 lifecycle table status: **{lifecycle_note}**; E5 gap-limitation heatmap status: **{heatmap_note}**.

## Ranked gap priorities

{markdown_table(top_rows, ["rank", "gap", "gap_priority_score", "frequency", "weak_evidence_weight", "eps_specificity_weight", "lifecycle_undercoverage_weight", "model_unavailability_weight", "no_independent_validation_weight"], max_rows=10)}

## Gap mapping level counts

{markdown_table(level_rows, ["gap", "addressed_with_evidence", "addressed_conceptually", "mentioned_only", "not_addressed", "underaddressed_study_count"], max_rows=10)}

## Interpretation

The top priorities are the gaps with many under-addressed mappings and many co-occurring evidence-quality bottlenecks. Because all five planned gap dimensions are represented across the corpus, raw frequency alone is not very discriminating; the level/severity and limitation components provide the useful ordering.

## Outputs

- `outputs/tables/research_gap_priorities.csv`
- `outputs/reports/future_research_agenda.md`
- `outputs/reports/e13_research_agenda_prioritization.md`
"""
    write_text(REPORTS_DIR / "e13_research_agenda_prioritization.md", text)


def main() -> None:
    data = load_inputs()
    rows = score_all_gaps(data)
    write_csv(TABLES_DIR / "research_gap_priorities.csv", rows, CSV_COLUMNS)
    write_future_agenda(rows, data)
    write_method_report(rows, data)
    print("Research agenda prioritization complete (exploratory):")
    for row in rows[:5]:
        print(f"  {row['rank']}. {row['gap']}: {row['gap_priority_score']}")


if __name__ == "__main__":
    main()
