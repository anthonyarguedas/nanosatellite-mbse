# E13 — Research agenda prioritization

**Exploratory notice:** scores rank research-agenda needs over the SLR1 40-study extraction. They are deterministic and transparent, but they are not statistical significance estimates.

## Formula

```text
gap_priority = frequency + weak_evidence_weight + eps_specificity_weight + lifecycle_undercoverage_weight + model_unavailability_weight + no_independent_validation_weight
```

Formula version: `e13_gap_priority_v1`.

Component definitions used in this implementation:

- `frequency`: number of unique studies where the gap is **not** coded `addressed with evidence`.
- `weak_evidence_weight`: sum of gap-level severity (`addressed conceptually` = 1, `mentioned only` = 2, `not addressed` = 3) plus `0.10 ×` capped weak/unsupported claim counts in those contributing studies.
- `eps_specificity_weight`: `0.50 ×` under-addressed studies that are EPS-relevant/EPS-element-bearing and have EPS evidence needs or no physical/pre-physical evidence signals.
- `lifecycle_undercoverage_weight`: `0.50 ×` under-addressed studies with `incomplete_lifecycle_coverage` or no later lifecycle markers.
- `model_unavailability_weight`: `0.50 ×` under-addressed studies with `model_not_available`.
- `no_independent_validation_weight`: `0.50 ×` under-addressed studies with `no_independent_validation` or `no_physical_test_or_flight_evidence`.

Inputs: `data/gap_mappings.jsonl`, `data/claims.jsonl`, `data/limitations.jsonl`, `data/study_codes.jsonl`; E6 lifecycle table status: **available**; E5 gap-limitation heatmap status: **available**.

## Ranked gap priorities

| rank | gap | gap_priority_score | frequency | weak_evidence_weight | eps_specificity_weight | lifecycle_undercoverage_weight | model_unavailability_weight | no_independent_validation_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | newspace_agile_distributed_rapid_iteration_alignment | 175.30 | 34 | 79.30 | 14.00 | 17.00 | 14.00 | 17.00 |
| 2 | governance_project_deliverables_roi | 154.50 | 33 | 59.50 | 14.00 | 16.50 | 15.00 | 16.50 |
| 3 | lightweight_resource_constrained_tailoring | 111.40 | 25 | 40.90 | 9.50 | 12.50 | 11.00 | 12.50 |
| 4 | toolchain_fragmentation_interoperability | 101.10 | 21 | 40.60 | 8.50 | 10.50 | 10.00 | 10.50 |
| 5 | practical_implementation_pathway | 47.20 | 11 | 16.20 | 4.00 | 5.50 | 5.00 | 5.50 |


## Gap mapping level counts

| gap | addressed_with_evidence | addressed_conceptually | mentioned_only | not_addressed | underaddressed_study_count |
| --- | --- | --- | --- | --- | --- |
| newspace_agile_distributed_rapid_iteration_alignment | 6 | 11 | 15 | 8 | 34 |
| governance_project_deliverables_roi | 7 | 20 | 13 | 0 | 33 |
| lightweight_resource_constrained_tailoring | 15 | 21 | 3 | 1 | 25 |
| toolchain_fragmentation_interoperability | 19 | 13 | 6 | 2 | 21 |
| practical_implementation_pathway | 29 | 11 | 0 | 0 | 11 |


## Interpretation

The top priorities are the gaps with many under-addressed mappings and many co-occurring evidence-quality bottlenecks. Because all five planned gap dimensions are represented across the corpus, raw frequency alone is not very discriminating; the level/severity and limitation components provide the useful ordering.

## Outputs

- `outputs/tables/research_gap_priorities.csv`
- `outputs/reports/future_research_agenda.md`
- `outputs/reports/e13_research_agenda_prioritization.md`
