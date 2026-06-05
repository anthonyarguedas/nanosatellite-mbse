# E0 data audit — SLR1 extraction flattening

Source generated_at: `2026-05-28T15:59:44-06:00`
Source codebook_version: `1.1`

## Study preservation

Flattening preserved all studies: **yes**. The source reports `40` studies, contains `40` study objects, and `data/studies.jsonl` contains `40` records.

## Generated row counts

| Artifact | Rows |
| --- | --- |
| studies.jsonl | 40 |
| study_codes.jsonl | 7370 |
| claims.jsonl | 270 |
| limitations.jsonl | 602 |
| emergent_codes.jsonl | 345 |
| evidence_quotes.jsonl | 15937 |
| gap_mappings.jsonl | 200 |

## Source statistics comparison

Counts are regenerated from normalized per-study fields. Empty `values: []` records are retained in JSONL for provenance but excluded from controlled-value count comparisons.

| Statistic | Matches | Source | Generated | Notes |
| --- | --- | --- | --- | --- |
| tier_counts | yes | core: 21, supporting: 19 | core: 21, supporting: 19 |  |
| quality_score_total.counts | no | 0.0: 15, 5.0: 2, 5.5: 3, 6.0: 8, 6.5: 7, 7.0: 3, 7.5: 2 | 5.0: 3, 5.5: 6, 6.0: 13, 6.5: 9, 7.0: 7, 7.5: 2 | Computed from per-study quality_checklist/structured quality fields. Source statistics quality aggregate differs from per-study extraction fields (source min/mean/max=0.0/3.9/7.5; generated min/mean/max=5.0/6.2125/7.5). |
| rq_relevance_counts.RQ1 | yes | high: 24, partial: 16 | high: 24, partial: 16 |  |
| rq_relevance_counts.RQ2 | yes | high: 3, partial: 37 | high: 3, partial: 37 |  |
| rq_relevance_counts.RQ3 | yes | high: 2, none: 9, partial: 29 | high: 2, none: 9, partial: 29 |  |
| eps_relevance_counts | yes | EPS-adjacent: 13, EPS-specific: 2, not EPS-relevant: 2, power-budget/electrical-architecture: 19, system-level only: 4 | EPS-adjacent: 13, EPS-specific: 2, not EPS-relevant: 2, power-budget/electrical-architecture: 19, system-level only: 4 |  |
| approach_classification_counts | yes | Enhanced MBSE: 11, Extended MBSE: 17, Integrated MBSE/digital engineering: 6, Pure MBSE: 6 | Enhanced MBSE: 11, Extended MBSE: 17, Integrated MBSE/digital engineering: 6, Pure MBSE: 6 |  |
| extraction_confidence_counts | yes | high: 29, medium: 11 | high: 29, medium: 11 |  |
| ivv_integration_level_counts | yes | executable/model-based checks: 6, model-contained verification artifacts: 2, none/not reported: 10, separate document only: 1, simulation-in-the-loop: 12, software/hardware-in-the-loop: 1, trace-linked verification artifacts: 5 | executable/model-based checks: 6, model-contained verification artifacts: 2, none/not reported: 10, separate document only: 1, simulation-in-the-loop: 12, software/hardware-in-the-loop: 1, trace-linked verification artifacts: 5 |  |
| reliability_subtype_counts | yes | EPS reliability: 2, defect/error reduction: 11, generic reliability claim: 2, mission assurance: 29, model consistency/reliability: 34, process reliability: 8, system/mission reliability: 10 | EPS reliability: 2, defect/error reduction: 11, generic reliability claim: 2, mission assurance: 29, model consistency/reliability: 34, process reliability: 8, system/mission reliability: 10 |  |
| generality_reuse_mechanism_counts | yes | high-level abstraction: 33, interface-focused model: 12, library: 11, low-dynamics / non-detailed-behavior model: 10, method guidance: 39, mission-agnostic architecture: 22, open package: 6, pattern: 3, profile: 6, reference model: 21, reusable workflow: 34, specific-mission model with reusable method only: 14, template: 24, transformation: 6 | high-level abstraction: 33, interface-focused model: 12, library: 11, low-dynamics / non-detailed-behavior model: 10, method guidance: 39, mission-agnostic architecture: 22, open package: 6, pattern: 3, profile: 6, reference model: 21, reusable workflow: 34, specific-mission model with reusable method only: 14, template: 24, transformation: 6 |  |
| limitation_flag_counts | yes | assumptions_or_data_quality_limits: 17, incomplete_lifecycle_coverage: 40, interoperability_limitations: 29, learning_curve_or_training_burden: 11, lineage_or_duplicate_reference_model_overlap: 19, model_not_available: 34, no_baseline_or_comparator: 38, no_eps_specific_evidence: 33, no_independent_validation: 40, no_physical_test_or_flight_evidence: 39, no_pre_physical_verification_model: 20, no_quantitative_evaluation: 35, prototype_or_future_work: 40, single_case_or_limited_scope: 40, tool_dependency_or_vendor_lockin: 14, weak_claim_evidence_linkage: 40 | assumptions_or_data_quality_limits: 17, incomplete_lifecycle_coverage: 40, interoperability_limitations: 29, learning_curve_or_training_burden: 11, lineage_or_duplicate_reference_model_overlap: 19, model_not_available: 34, no_baseline_or_comparator: 38, no_eps_specific_evidence: 33, no_independent_validation: 40, no_physical_test_or_flight_evidence: 39, no_pre_physical_verification_model: 20, no_quantitative_evaluation: 35, prototype_or_future_work: 40, single_case_or_limited_scope: 40, tool_dependency_or_vendor_lockin: 14, weak_claim_evidence_linkage: 40 |  |
| gap_mapping.practical_implementation_pathway | yes | addressed conceptually: 11, addressed with evidence: 29 | addressed conceptually: 11, addressed with evidence: 29 |  |
| gap_mapping.toolchain_fragmentation_interoperability | yes | addressed conceptually: 13, addressed with evidence: 19, mentioned only: 6, not addressed: 2 | addressed conceptually: 13, addressed with evidence: 19, mentioned only: 6, not addressed: 2 |  |
| gap_mapping.lightweight_resource_constrained_tailoring | yes | addressed conceptually: 21, addressed with evidence: 15, mentioned only: 3, not addressed: 1 | addressed conceptually: 21, addressed with evidence: 15, mentioned only: 3, not addressed: 1 |  |
| gap_mapping.governance_project_deliverables_roi | yes | addressed conceptually: 20, addressed with evidence: 7, mentioned only: 13 | addressed conceptually: 20, addressed with evidence: 7, mentioned only: 13 |  |
| gap_mapping.newspace_agile_distributed_rapid_iteration_alignment | yes | addressed conceptually: 11, addressed with evidence: 6, mentioned only: 15, not addressed: 8 | addressed conceptually: 11, addressed with evidence: 6, mentioned only: 15, not addressed: 8 |  |

Differences are limited to the following aggregate(s): quality_score_total.counts. See notes above for the explanation.

## Multi-valued fields requiring many-to-many graph edges

### Study-level code fields

| Source | Field path | Studies with >1 value | Max values/study | Total values | Examples |
| --- | --- | --- | --- | --- | --- |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].baseline_comparator | 23 | 3 | 62 | paper-0001;paper-0002;paper-0003;paper-0011;paper-0012;paper-0013;paper-0015;paper-0016 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].evidence_confidence_rating | 39 | 4 | 109 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].evidence_type | 40 | 6 | 169 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].lifecycle_stage | 35 | 7 | 125 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].mbse_mechanism | 40 | 10 | 278 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].metric_or_value_indicator | 34 | 9 | 151 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0011 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].outcome_category | 40 | 17 | 464 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].reliability_subtype | 29 | 5 | 96 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | claimed_outcomes_value_mechanisms_evidence[].specificity_of_claim | 37 | 4 | 97 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | eps_verification_specific.eps_elements_modeled | 31 | 11 | 175 | paper-0001;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0011;paper-0012 |
| structured_code_summary | eps_verification_specific.integration_test_readiness | 7 | 3 | 18 | paper-0003;paper-0023;paper-0037;paper-0054;paper-0063;paper-0078;paper-0079 |
| structured_code_summary | eps_verification_specific.pre_physical_development_verification_mechanism | 24 | 5 | 76 | paper-0001;paper-0003;paper-0005;paper-0007;paper-0008;paper-0010;paper-0011;paper-0012 |
| structured_code_summary | eps_verification_specific.verification_validation_artifacts | 17 | 5 | 57 | paper-0001;paper-0003;paper-0008;paper-0012;paper-0023;paper-0026;paper-0027;paper-0034 |
| structured_code_summary | governance_roi_project_decision_linkage.model_governance_strategy | 14 | 4 | 42 | paper-0004;paper-0005;paper-0011;paper-0013;paper-0014;paper-0015;paper-0016;paper-0022 |
| structured_code_summary | governance_roi_project_decision_linkage.roi_value_realization_evidence | 2 | 4 | 9 | paper-0061;paper-0078 |
| structured_code_summary | implementation_pathway_tailoring.tailoring_rationale | 36 | 7 | 154 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | mbse_objective_scope_artifacts.generality_reuse_mechanism | 40 | 10 | 241 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | mbse_objective_scope_artifacts.model_artifacts_used | 39 | 11 | 245 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | mbse_objective_scope_artifacts.modeling_scope | 40 | 14 | 409 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| structured_code_summary | study_context_population.development_context | 31 | 6 | 107 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0008;paper-0010;paper-0012 |
| structured_code_summary | study_context_population.lifecycle_stage_addressed | 31 | 7 | 106 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0008;paper-0010;paper-0011 |
| structured_code_summary | study_context_population.model_maturity | 37 | 5 | 110 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0011 |
| structured_code_summary | toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms | 27 | 5 | 76 | paper-0001;paper-0003;paper-0008;paper-0011;paper-0013;paper-0014;paper-0016;paper-0022 |
| structured_code_summary | toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool | 38 | 8 | 153 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0008;paper-0010;paper-0011 |
| structured_code_summary | toolchain_interoperability_lifecycle_continuity.toolchain_limitations | 12 | 3 | 41 | paper-0003;paper-0010;paper-0014;paper-0023;paper-0026;paper-0027;paper-0046;paper-0059 |
| extraction | eps_verification_specific.eps_elements_modeled | 31 | 11 | 175 | paper-0001;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0011;paper-0012 |
| extraction | eps_verification_specific.integration_test_readiness | 6 | 3 | 40 | paper-0023;paper-0037;paper-0054;paper-0063;paper-0078;paper-0079 |
| extraction | eps_verification_specific.pre_physical_development_verification_mechanism | 23 | 5 | 81 | paper-0001;paper-0003;paper-0005;paper-0007;paper-0008;paper-0010;paper-0011;paper-0012 |
| extraction | eps_verification_specific.verification_validation_artifacts | 19 | 7 | 74 | paper-0001;paper-0003;paper-0005;paper-0008;paper-0010;paper-0011;paper-0012;paper-0023 |
| extraction | governance_roi_project_decision_linkage.model_governance_strategy | 13 | 4 | 54 | paper-0004;paper-0005;paper-0011;paper-0014;paper-0015;paper-0016;paper-0022;paper-0023 |
| extraction | governance_roi_project_decision_linkage.roi_value_realization_evidence | 2 | 4 | 38 | paper-0061;paper-0078 |
| extraction | implementation_pathway_tailoring.tailoring_rationale | 36 | 7 | 155 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| extraction | mbse_objective_scope_artifacts.generality_reuse_mechanism | 40 | 10 | 241 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| extraction | mbse_objective_scope_artifacts.model_artifacts_used | 40 | 12 | 301 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| extraction | mbse_objective_scope_artifacts.modeling_scope | 39 | 14 | 403 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| extraction | study_context_population.development_context | 31 | 6 | 109 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0008;paper-0010;paper-0012 |
| extraction | study_context_population.lifecycle_stage_addressed | 31 | 7 | 106 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0008;paper-0010;paper-0011 |
| extraction | study_context_population.model_maturity | 37 | 5 | 110 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0011 |
| extraction | toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms | 27 | 9 | 100 | paper-0001;paper-0003;paper-0008;paper-0011;paper-0013;paper-0014;paper-0016;paper-0022 |
| extraction | toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool | 38 | 18 | 203 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0008;paper-0010;paper-0011 |
| extraction | toolchain_interoperability_lifecycle_continuity.toolchain_limitations | 17 | 6 | 74 | paper-0003;paper-0008;paper-0010;paper-0012;paper-0013;paper-0014;paper-0023;paper-0024 |

### Claim-level fields

| Field path | Claims with >1 value | Studies represented | Max values/claim | Total values | Examples |
| --- | --- | --- | --- | --- | --- |
| claimed_outcomes_value_mechanisms_evidence[].evidence_type | 155 | 36 | 3 | 450 | paper-0001;paper-0003;paper-0004;paper-0007;paper-0008;paper-0011;paper-0012;paper-0013 |
| claimed_outcomes_value_mechanisms_evidence[].lifecycle_stage | 172 | 34 | 4 | 497 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| claimed_outcomes_value_mechanisms_evidence[].mbse_mechanism | 249 | 40 | 5 | 738 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| claimed_outcomes_value_mechanisms_evidence[].metric | 73 | 29 | 5 | 289 | paper-0001;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0011;paper-0012 |
| claimed_outcomes_value_mechanisms_evidence[].outcome_category | 263 | 40 | 7 | 840 | paper-0001;paper-0002;paper-0003;paper-0004;paper-0005;paper-0007;paper-0008;paper-0010 |
| claimed_outcomes_value_mechanisms_evidence[].reliability_subtype | 29 | 18 | 3 | 305 | paper-0002;paper-0007;paper-0010;paper-0013;paper-0023;paper-0026;paper-0027;paper-0034 |

## Missing and unexpected sections

All expected top-level `extraction.*` sections were present, and no unexpected top-level sections were encountered.

Structured controlled-field keys observed: `47` (source controlled_field_count: `47`).

Some exact controlled field paths were absent from nested `extraction.*` sections even though the normalized `structured_code_summary` contained them. Top missing exact paths:
- `bibliographic_review_management.rq1_relevance` missing in 40 studies
- `bibliographic_review_management.rq2_relevance` missing in 40 studies
- `bibliographic_review_management.rq3_relevance` missing in 40 studies
- `implementation_pathway_tailoring.adoption_guidance` missing in 6 studies
- `bibliographic_review_management.tier_status` missing in 2 studies
- `toolchain_interoperability_lifecycle_continuity.toolchain_limitations` missing in 1 studies
- `mbse_objective_scope_artifacts.modeling_scope` missing in 1 studies

Controlled fields with explicit empty values/statuses were retained as provenance rows. Top empty-value paths:
- `governance_roi_project_decision_linkage.roi_value_realization_evidence` empty in 35 records
- `eps_verification_specific.integration_test_readiness` empty in 30 records
- `governance_roi_project_decision_linkage.model_governance_strategy` empty in 23 records
- `eps_verification_specific.verification_validation_artifacts` empty in 16 records
- `toolchain_interoperability_lifecycle_continuity.toolchain_limitations` empty in 15 records
- `eps_verification_specific.pre_physical_development_verification_mechanism` empty in 14 records
- `extraction.eps_verification_specific.verification_validation_artifacts` empty in 13 records
- `claimed_outcomes_value_mechanisms_evidence[].baseline_comparator` empty in 12 records
- `toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms` empty in 11 records
- `extraction.eps_verification_specific.pre_physical_development_verification_mechanism` empty in 9 records
- `extraction.governance_roi_project_decision_linkage.model_governance_strategy` empty in 8 records
- `eps_verification_specific.eps_elements_modeled` empty in 7 records

## Caveats for downstream KG work

- `study_codes.jsonl` includes both canonical `structured_code_summary` records and exact-path `extraction` records; use `source_section` to avoid double-counting.
- Claim fields remain arrays where the extraction is multi-valued, so KG builders should explode those arrays into many-to-many edges.
- The source `statistics.quality_score_total` aggregate does not match the per-study quality fields; this audit preserves the per-study judgments and reports the mismatch rather than editing the source extraction.
