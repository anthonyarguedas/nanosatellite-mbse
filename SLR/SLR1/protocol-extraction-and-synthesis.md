# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction and synthesis

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · **3 — Extraction and synthesis** (this file) · [Supporting need assessment — Prior secondary reviews](protocol-prior-secondary-reviews.md)
>
> **Canonical definitions and rules:** Part 1 governs [report eligibility versus question contribution](protocol.md#report-eligibility-versus-question-contribution), [evidence statuses](protocol.md#evidence-statuses), [eligible EPS evidence routes](protocol.md#eligible-eps-evidence-routes), [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring), [RQ2 eligibility](protocol.md#mbse-enabled-outcomes-and-implementation-burdens-versus-eps-engineering-outputs), [direct RQ3 eligibility](protocol.md#direct-eps-linked-pre-physical-vv), and [units and counting](protocol.md#units-of-evidence-and-counting). Part 2 governs [finding-level evidence appraisal](protocol-discovery-and-appraisal.md#finding-level-evidence-appraisal). This part defines the report-level extraction fields, cross-report lineage resolution and separate lineage-level extraction, validation, synthesis, and reporting.

## Extraction design

Extraction is report-level by default. Create one extraction file for each included report. Use nested groups for EPS content, inputs, results, findings, and V&V activities. Create another EPS case section only when a report contains materially separate models, implementations, or evaluations that cannot be represented clearly together.

Keep report-family resolution and cross-report artifact identity pending during the first report pass. Record concise family leads. Fully extract every reusable artifact, reported lineage, reuse claim, and tailoring application described by each report, including a report-bounded reuse level. Resolve families and cross-report lineage identity after all report extractions are available, then create separate lineage-level and consolidated application records.

Report-level records remain fixed during the cross-report pass. That pass may update only `lineage_id` from its first-pass state to a stable resolved ID or `unresolved_after_review`. It does not backfill or overwrite any other report-level field.

Do not create separate analytic objects for individual measurements, comparators, rival explanations, appraisal domains, or claim-support judgments. Keep them as fields in the result, finding, activity, lineage, or tailoring row that uses them.

### Common field rules

Create a run-specific codebook and machine-readable schema from this protocol before full extraction. Every report and repeatable row must have a stable ID. Each repeatable row also records:

- `evidence_location`, including report ID, page or section, and figure or table when relevant.
- `coding_confidence`, using `high`, `moderate`, or `low` under Part 2.
- `provenance`, using `source_reported`, `author_claimed_or_planned`, `reviewer_inferred`, or `reviewer_derived`.
- `notes`, only when needed to explain ambiguity or a coding decision.

Apply the Part 1 statuses `not_reported`, `none`, `not_applicable`, and `uncertain` exactly. Do not use an empty value when one of these statuses applies. Keep source-observed results separate from author expectations and reviewer calculations.

A source location and coding confidence may cover a compact group of fields when they come from the same passage, figure, or table. Do not duplicate the same quotation for every field.

Discovery events, search ranks, raw-file provenance, and screening history remain in the search and screening data. Link them through `screening_record_id` rather than copying them into the extraction.

## Report-level extraction fields

### Identity, eligibility, and review management

Record:

- `report_id`.
- `screening_record_id`.
- full citation.
- title and authors.
- year and full publication date when available.
- venue or issuing organization.
- publication type and publication status.
- DOI, arXiv ID, or other stable URL.
- version used and its relationship to other known versions.
- possible companion reports or shared implementations.
- `family_lead`, using `yes`, `no`, or `uncertain`.
- concise report-family lead reason, or `not_reported`.
- source-file path.
- final full-text decision.
- Route A or Route B.
- concise eligibility and route reason with evidence location.
- extraction date and extractor.
- verification status.

For a thesis or dissertation, also record degree level and name, institution, country, department, completion status, persistent IDs, repository version, and access, embargo, and licence status.

For an arXiv preprint, record the identifier, subject category, version, and version date.

### Report and implementation context

Record:

- mission or platform.
- form factor or mass.
- mission purpose or domain.
- orbit and environment.
- organization type.
- development setting, such as academic, agency, industry, distributed, agile, concurrent, rapid, or resource constrained.
- lifecycle stage actually demonstrated.
- lifecycle stages only claimed or planned.
- project maturity, using `conceptual_framework`, `reference_or_template`, `prototype`, `executable`, `used_on_project`, `physically_checked`, `operational`, `flight`, or `not_reported`. More than one may apply.

### MBSE approach

Record:

- author objective.
- problem addressed.
- intended decision.
- reason for using MBSE.
- method or modeling language.
- tools and versions.
- toolchain and data flow.
- model artifacts.
- modeled systems-engineering concerns.
- explicit relationships among concerns.
- system boundary.
- artifact availability.
- licence when reported.

### EPS representation

For each report, record one EPS case section by default. Record:

- `eps_case_id` only when more than one case section is needed.
- EPS anchor.
- host-model anchor for Route B.
- EPS boundary.
- EPS elements.
- EPS architecture.
- EPS interfaces.
- EPS modes and operations.
- EPS model representations.
- each EPS-to-model bridge needed to establish qualification and Route B eligibility.
- abstraction or fidelity.
- purposes and supported decisions.
- scope deliberately omitted.
- EPS model maturity.
- availability of the EPS model, profile, script, data, or documentation.

EPS elements may include generation, storage, battery management, conversion, regulation, conditioning, distribution, protection, monitoring, control, bus, harness, loads, interfaces, modes, margins, degradation, faults, and another source-described element.

Purposes may include definition or sizing, requirements or traceability, trade study, interface management, executable analysis, V&V, communication, lifecycle continuity, and reuse or tailoring.

### General implementation footprint

Record the report's general MBSE implementation footprint:

- roles.
- skills and training.
- staffing.
- workflow.
- automation.
- tools, licences, and infrastructure.
- model preparation.
- data preparation.
- computing requirements.
- integration and interoperability.
- governance and configuration control.
- implementation effort.
- implementation duration.
- implementation cost.
- ongoing maintenance.
- reported burdens.
- burden mitigations.

Keep measured values, author estimates, and unsupported characterizations distinct. Extract tailoring-specific effort in each report-level tailoring application and independently in each consolidated application.

### Input and assumption groups

Group related inputs rather than creating an object for every value. Useful groups include mission requirements, base assumptions, scenario inputs, model formulation, V&V configuration, and tool prerequisites.

For each group, record:

- `input_group_id`.
- category.
- linked EPS case and scenario or configuration.
- parameters or constructs.
- source-reported values or descriptions.
- units and time basis.
- nominal, worst-case, range, or distribution status.
- source or provenance, such as requirement, standard, vendor data, test or flight data, heritage, literature, tool default, analyst assumption, or calculation.
- uncertainty, variability, margin, sensitivity, and degradation handling.
- rationale.
- model trace location.
- affected outputs or decisions.

An input group can contain a small value table. Preserve each original value and unit in that table.

### Evaluation and result sets

Keep outputs from one evaluation or scenario together. Create a new result set only when the design, scenario, inputs, or evidence basis differs materially.

For each result set, record:

- `result_set_id`.
- linked EPS case.
- evaluation design, using `model_or_simulation_evaluation`, `case_or_experience_report`, `comparative_observational`, `controlled_or_quasi_experimental`, `survey`, `interview_or_qualitative`, `mixed_methods`, `artifact_or_reuse_demonstration`, `other`, or `unclear`.
- scenario or configuration.
- linked input groups.
- cases, participants, or observational units.
- data sources.
- method.
- execution status.
- analysis method.
- missing data, failures, and exclusions.
- outputs as a nested table containing quantity or construct, source-reported value, unit, time basis, denominator when relevant, and observed or expected status.
- criteria and verdicts as a nested table containing target, criterion, result, and scope.
- uncertainty, sensitivity, central tendency, dispersion, effect estimate, confidence interval, exact p-value, and statistical method when reported.
- comparator summary when present.
- decision informed.
- physical or operational link.

An EPS engineering output is not an MBSE benefit by itself. Link it to RQ2 or RQ3 only when the Part 1 rules are met.

If the reviewer calculates or converts a value, keep it in a `reviewer_derived_values` table within the result set. Record the source values, formula or transformation, unit conversion, assumptions, missing-data handling, analysis script path and version, reviewer-derived result, and sensitivity to reasonable alternatives. Never overwrite a source-reported value.

### RQ1 evaluative characterizations

Create a short row only when a report uses an evaluative characterization such as *lightweight*, *scalable*, *comprehensive*, *easy to implement*, *resource intensive*, or an equivalent claim.

Record:

- `rq1_claim_id`.
- claim wording.
- claimed characteristic.
- claim scope and object.
- linked EPS case or result set.
- `evidence_basis`.
- `support`.
- `support_reason`.

Descriptive facts such as the tool used or diagrams present remain normal report fields and do not need a claim row.

### RQ2 outcome and burden findings

Create one row for each materially distinct EPS-attributed outcome, burden, or trade-off. Split a statement when direction, evidence, actor, scenario, or scope differs materially. Keep plausible near misses with `direct_synthesis = no` and one reason.

Record:

- `rq2_finding_id`.
- `direct_synthesis`, using `yes`, `no`, or `uncertain`.
- exclusion or uncertainty reason when not in direct synthesis.
- exact claim wording or cautious paraphrase.
- claim kind, using `descriptive_occurrence`, `feasibility_or_executed_result`, `technical_performance`, `comparative`, `causal_attribution`, `experiential_or_perceived`, `implementation_burden`, `transfer_or_generalization`, `other`, or `unclear`.
- role, using `outcome`, `implementation_burden`, or `mixed_trade_off`.
- target and scope.
- outcome category.
- author-claimed direction, using `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, `unclear`, or `not_reported`.
- evidence-supported direction, using `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, `unclear`, or `unsupported`.
- EPS attribution, using `explicit_eps_attribution`, `ambiguous_attribution`, or `generic_or_ineligible`.
- proposed MBSE mechanism.
- linked model, activity, input group, or result set.
- measure and value.
- unit, denominator, and time basis.
- central tendency, dispersion, absolute and relative differences, effect estimate, confidence interval, exact p-value, and statistical method when reported.
- missing observations or exclusions that affect the measure.
- measure directness, using `direct`, `surrogate`, `intermediate_or_process`, or `unclear`.
- lifecycle stage.
- applicability.
- `evidence_basis`.
- `support`.
- `support_reason`.

Outcome categories include EPS reliability, mission or system assurance, defect or error reduction, risk reduction, reproducibility, reuse, integration or interoperability, interface consistency, traceability or requirements quality, completeness, lifecycle continuity, decision support, cost, schedule, effort or automation, communication or knowledge, governance, value realization, and another source-described category. For a reliability finding, also record whether it concerns EPS reliability, system or mission reliability, process reliability, model consistency, mission assurance, defect or error reduction, a generic reliability claim, or is unclear.

For comparative or causal claims, also record:

- comparator description and type.
- whether the comparator is concurrent or historical and planned or retrospective.
- material differences in task, inputs, mission, lifecycle stage, team, experience, training, tools, automation, time, outcome definition, and data completeness.
- comparator adequacy, using `adequate`, `partial`, `inadequate`, or `unclear`.
- major author-identified or reviewer-noted rival explanations and how the source handled them.

Reviewer-noted rival explanations inform support. They are not primary-source findings.

For burdens, also record:

- burden category.
- affected role or team.
- whether the burden occurs during adoption or ongoing use.
- effort, time, schedule, cost, staffing, training, tool, infrastructure, preparation, computing, integration, governance, or maintenance amount when reported.
- measurement method.
- mitigation.
- linked benefit or trade-off.

A power or energy margin does not become a reliability finding without an explicit reliability or assurance link. Model availability does not establish reproducibility. Co-occurring diagrams do not establish interoperability.

### RQ3 V&V activities

Create one activity row for each materially distinct target–method–scenario combination. Keep several criteria and verdicts in one activity when the method, scenario, and timing are shared. Retain relevant near misses with `direct_synthesis = no`.

Record:

- `rq3_activity_id`.
- `direct_synthesis`, using `yes`, `no`, or `uncertain`.
- failed eligibility condition or uncertainty reason when applicable.
- EPS target.
- target type and requirement or criterion ID.
- model artifact.
- explicit model-to-V&V bridge.
- source terminology for verification, validation, V&V, checking, or analysis.
- linkage scope, using `eps_specific`, `system_wide_eps_linked`, `system_wide_cooccurrence`, or `unclear`.
- normalized V&V object, using `model_verification`, `model_validation`, `system_or_design_verification`, `system_or_design_validation`, `multiple`, or `unclear`.
- method.
- execution environment.
- hardware present.
- physicality relative to the target EPS.
- lifecycle stage.
- timing relative to physical realization, integration, and test.
- criteria or oracles as a nested table containing criterion ID, target, threshold or expected behavior, source, and applicability.
- criterion sources.
- status, using `proposed`, `prepared_or_generated`, `executed_virtual`, `result_reported`, `downstream_physical_link`, or `model_to_test_closure`.
- results or verdicts as a nested table containing target, result, value, unit, scope, and observed or expected status.
- measure directness, using `direct`, `surrogate`, `intermediate_or_process`, or `unclear`.
- discrepancies and resolution.
- later physical link.
- model-to-test closure.
- `evidence_basis`.
- `support`.
- `support_reason`.

Record a comparator and major rival explanations only when the report makes a comparative or causal V&V-effectiveness claim. For validation, state why the criterion or oracle is authoritative for the intended use.

### Reusable artifact and reported lineage

The first report pass creates a complete source-bounded extraction for every identifiable EPS-linked artifact assessed for reuse, reported artifact lineage, or method or workflow reuse case described in the report. Create more than one reuse record when the report describes materially distinct artifacts or lineages. Extract all evidence available in the report even when no companion report is known. Cross-report identity remains pending.

Record once for the report:

- `lineage_mentioned`, using `yes`, `no`, or `uncertain`.
- lineage-mention reason and evidence location.

Use `yes` when the report explicitly identifies or provides sufficient source evidence for continuity between a base artifact and a version, derived instance, or adoption. The report does not have to use the word *lineage*. Use `uncertain` when continuity is plausible but unresolved. Use `no` for a reuse claim or stand-alone artifact without a reported continuity relationship. Similar diagrams, authors, organizations, tools, topics, or terminology do not establish continuity.

For each report-level reuse record, record identity and provenance:

- `report_reuse_record_id`.
- `lineage_id`, using `pending_resolution` for a reported or uncertain lineage and `not_applicable` when no lineage relationship is reported.
- artifact names and versions.
- identity and derivation evidence contained in the report.
- base-to-derived relationships.
- repository or location.
- owner or developer.
- artifact type.
- EPS scope.
- availability and licence.
- exact reuse claim.
- claimed reuse object, such as artifact, method, workflow, toolchain, language, or unclear.
- stated parent or derived artifact.
- possible related reports or artifacts.
- whether reuse concerns the artifact or only a method or workflow.

Record the declared applicability envelope:

- target platforms and missions.
- lifecycle uses and decisions.
- EPS boundary.
- model boundary and abstraction.
- architecture and interfaces.
- environment, modes, and loads.
- required inputs.
- tools and versions.
- organizational prerequisites.
- exclusions and limits.

Record the reuse design:

- reusable core.
- variation points.
- allowed options, ranges, and defaults.
- dependencies.
- tailoring rules.
- tailoring operations.
- required roles and skills.
- required tools and data.
- automation.
- governance and configuration control.

Record the report-bounded reuse assessment:

- linked `report_application_id` values.
- `report_reuse_level`, using any level from `NA` through `R4_independent_reuse_demonstrated` under Part 1.
- report-reuse-level reason.
- demonstrated settings.
- demonstrated coverage.
- failed applications.
- applications outside the declared envelope.
- conflicting evidence within the report.
- `evidence_basis`.
- `support`.
- `support_reason`.

Assign `report_reuse_level` from evidence contained in this report only. A single report can support R3 or R4. Assign R3 or R4 only when the corresponding report-level application below is complete, includes post-tailoring assurance, and meets the required adopter condition.

#### Report-level tailoring application

Create one `report_application_id` row for each actual adoption or tailoring event described in the report. Merge repeated descriptions of the same event within the report. Keep an account of the same event in another report as a separate report-level row.

Record identity and setting:

- `report_application_id`.
- linked `report_reuse_record_id`.
- `lineage_id`, inherited from the linked reuse record until cross-report resolution.
- target model or configuration.
- adopting team.
- relationship to the originator.
- mission or platform.
- lifecycle purpose.
- EPS architecture and interfaces.
- orbit, environment, modes, and loads.
- model abstraction.
- tools and versions.
- organization and process.
- relationship to the declared applicability envelope, using `inside`, `boundary`, `outside`, `unclear`, or `not_reported`.
- material difference from other applications described in the report.

Record tailoring performed:

- base version.
- retained core.
- configured or changed content.
- variation points used.
- tailoring operations.
- before-and-after trace.
- reasons for changes or unchanged use.
- tailoring inputs and assumptions.

Record tailoring effort:

- effort basis, using `measured`, `author_estimated`, `asserted`, or `not_reported`.
- roles involved.
- number of people.
- skills and training.
- person-hours or person-days.
- elapsed duration.
- schedule effect.
- financial cost.
- tools, licences, and infrastructure.
- data preparation.
- model preparation.
- integration or migration work.
- manual work.
- automated work.
- governance and configuration work.
- review and assurance effort.
- rework.
- ongoing maintenance.
- reported burdens.
- mitigations.

Do not infer low effort from parameterization, automation, a small mission, or the absence of a reported burden.

Record result and assurance:

- resulting artifact.
- configuration identifier.
- availability.
- decisions or analyses supported.
- success, failure, or partial result.
- trade-offs.
- post-tailoring criterion.
- assurance method.
- assurance timing.
- assurance result.
- discrepancies and resolution.
- linked report-level result sets.
- linked RQ2 findings.
- linked RQ3 activities.

Record independence:

- adopter relationship, using `originating_team`, `same_organization_operationally_separate`, `outside_organization_or_team`, `independent_evaluation_of_originator_instance_only`, or `unclear`.
- personnel overlap.
- who controlled the implementation.
- adopter-attributable evidence for adoption.
- adopter-attributable evidence for assurance.

An outside team normally qualifies as independent when lineage, adoption, and assurance are established. A team in the same organization qualifies only when it controls the implementation, the originating team performs no substantive implementation work, and the assured application is distinct.

### Limitations and open extraction

Record:

- author-stated limitations.
- future work.
- source conflicts.
- reviewer uncertainties.
- missing information relevant for interpretation.

Derive simple synthesis flags from these fields during compilation. Do not duplicate every missing field in a manual limitation list.

## Cross-report resolution and lineage-level extraction

Begin this pass only after all first-pass report extractions are complete and validated. Resolve report families first. Reports with `lineage_mentioned = yes` seed lineage resolution, and reports with `lineage_mentioned = uncertain` receive resolution review. Follow source-supported relationships to include every report in each candidate lineage, including linked reports with `lineage_mentioned = no`. Preserve report provenance for every lineage-level field.

Report-level extractions remain fixed throughout this pass. Update only `lineage_id` on the relevant report reuse and application records. Assign a stable lineage ID to every matched record, including a record initially marked `not_applicable` that another report links to the lineage. Use `unresolved_after_review` when a candidate relationship cannot be resolved. A correction to any other report-level field follows the focused-audit and adjudication procedure outside this pass.

Create lineage-level extractions and consolidated tailoring applications as separate records. Treat all linked reports in a resolved lineage as one evidence bundle when completing those records. Do not copy lineage-level values into a report-level extraction.

### Study or implementation report family

Record:

- `family_id`.
- linked report IDs.
- shared investigation or implementation.
- relationship among reports.
- shared data, models, scenarios, or results.
- preferred or most complete version for overlapping content.
- dependence reason.
- family coding confidence.

A shared topic, institution, author, or tool is not enough. Keep unresolved relationships separate or uncertain.

### Lineage-level reusable artifact extraction

Create one separate record for each resolved lineage. Extract the fields below at lineage scope from the complete set of linked reports. Record every report and source location contributing to each combined field, including disagreements and missing information.

Record identity and provenance:

- `lineage_id`.
- linked `report_reuse_record_id` values.
- linked report and family IDs.
- artifact names and versions.
- identity and derivation evidence.
- base-to-derived relationships.
- owner or developer.
- artifact type.
- EPS scope.
- availability and licence.
- exact reuse claim.
- whether reuse concerns the artifact or only a method or workflow.

Record the declared applicability envelope:

- target platforms and missions.
- lifecycle uses and decisions.
- EPS boundary.
- model boundary and abstraction.
- architecture and interfaces.
- environment, modes, and loads.
- required inputs.
- tools and versions.
- organizational prerequisites.
- exclusions and limits.

Record the reuse design:

- reusable core.
- variation points.
- allowed options, ranges, and defaults.
- dependencies.
- tailoring rules.
- tailoring operations.
- required roles and skills.
- required tools and data.
- automation.
- governance and configuration control.

Record the reuse assessment:

- linked consolidated tailoring-application IDs.
- contributing `report_reuse_level` values.
- `lineage_reuse_level` under Part 1.
- lineage-reuse-level reason.
- demonstrated settings.
- demonstrated coverage.
- failed applications.
- applications outside the declared envelope.
- conflicting evidence.
- lineage coding confidence.
- `evidence_basis`.
- `support`.
- `support_reason`.

Assign `lineage_reuse_level` from the combined lineage evidence. Do not assign R3 or R4 until the corresponding consolidated tailoring application below is complete, includes post-tailoring assurance, and meets the required adopter condition.

After resolving the lineage, assign its `lineage_id` to each matching report-level reuse record and report-level application. This ID assignment is the only change made to those report-level records during the cross-report pass.

### Consolidated tailoring application

Create one separate row for each actual adoption or tailoring event represented across the lineage reports. Merge repeated reporting of the same event only in this consolidated row. Keep every contributing report-level application unchanged.

Record identity and setting:

- `tailoring_application_id`.
- lineage ID.
- linked `report_application_id` values.
- linked report and family IDs.
- target model or configuration.
- adopting team.
- relationship to the originator.
- mission or platform.
- lifecycle purpose.
- EPS architecture and interfaces.
- orbit, environment, modes, and loads.
- model abstraction.
- tools and versions.
- organization and process.
- relationship to the declared applicability envelope, using `inside`, `boundary`, `outside`, `unclear`, or `not_reported`.
- material difference from other applications.

Record tailoring performed:

- base version.
- retained core.
- configured or changed content.
- variation points used.
- tailoring operations.
- before-and-after trace.
- reasons for changes or unchanged use.
- tailoring inputs and assumptions.

Record tailoring effort:

- effort basis, using `measured`, `author_estimated`, `asserted`, or `not_reported`.
- roles involved.
- number of people.
- skills and training.
- person-hours or person-days.
- elapsed duration.
- schedule effect.
- financial cost.
- tools, licences, and infrastructure.
- data preparation.
- model preparation.
- integration or migration work.
- manual work.
- automated work.
- governance and configuration work.
- review and assurance effort.
- rework.
- ongoing maintenance.
- reported burdens.
- mitigations.

Do not infer low effort from parameterization, automation, a small mission, or the absence of a reported burden.

Record result and assurance:

- resulting artifact.
- configuration identifier.
- availability.
- decisions or analyses supported.
- success, failure, or partial result.
- trade-offs.
- post-tailoring criterion.
- assurance method.
- assurance timing.
- assurance result.
- discrepancies and resolution.
- linked report result sets.
- linked RQ2 findings.
- linked RQ3 activities.

Record independence:

- adopter relationship, using `originating_team`, `same_organization_operationally_separate`, `outside_organization_or_team`, `independent_evaluation_of_originator_instance_only`, or `unclear`.
- personnel overlap.
- who controlled the implementation.
- adopter-attributable evidence for adoption.
- adopter-attributable evidence for assurance.

An outside team normally qualifies as independent when lineage, adoption, and assurance are established. A team in the same organization qualifies only when it controls the implementation, the originating team performs no substantive implementation work, and the assured application is distinct.

## Simplified appraisal

Apply the inline appraisal defined in [Part 2](protocol-discovery-and-appraisal.md#finding-level-evidence-appraisal). Do not create a separate methodological-appraisal table or claim-support object.

Every evaluative RQ1 claim, direct RQ2 finding, direct RQ3 activity, report-level reuse conclusion, and lineage-level reuse conclusion receives:

- `evidence_basis`.
- `support`.
- `support_reason`.

The support reason states the strongest evidence and the main claim-relevant limitation. Keep it bounded to the claim. A narrow executed-result finding can be supported while a broad benefit or transfer claim from the same report is unsupported.

Record comparator adequacy only for comparative or causal claims. Record oracle adequacy only for validation claims. Record adopter independence and post-tailoring assurance only for reuse claims. These conditional fields provide the needed appraisal without a general domain matrix.

## Calibration, consistency, and validation

Before full extraction:

1. [ ] Test report-level eligibility and Route A or Route B coding on clear and borderline examples.
2. [ ] Test the complete report form on a varied sample containing Route A and Route B reports, grouped inputs, grouped outputs, RQ2 findings, RQ3 activities, figures or tables, complete reusable-artifact and report-level application fields, `lineage_mentioned`, and report-bounded reuse levels. Include a report that can reach R3 or R4 by itself when available.
3. [ ] Test cross-report family and lineage-identity resolution, immutable report-level records, separate lineage-level extraction, and separate consolidated application, effort, assurance, independence, and reuse-level fields on at least one multi-report example.
4. [ ] Calibrate the difference between assertion, worked example, execution, comparison, physical or operational checking, and independent transfer.
5. [ ] Calibrate `supported`, `limited`, `unsupported`, and `unclear` on narrow and broad claims from the same report.
6. Revise and freeze the codebook, schema, audit procedure, and calibration decisions before full extraction.

### Sole-reviewer extraction and verification

One human reviewer performs the primary extraction and every final decision. Verification uses one focused audit, deterministic validation, a delayed human test–retest sample, and an optional supervisor sample. It does not require two complete model extractions for every report.

Apply this sequence:

1. **Primary extraction.** The reviewer extracts the complete report into the frozen report-level form.
2. **Focused audit.** For every included report, an authorized LLM or a delayed human check reviews eligibility and route, Route B anchors and bridge, omitted or duplicated groups, direct RQ2 attribution, direct RQ3 linkage, `lineage_mentioned`, complete report-level reuse and application coding, every report-level R3 or R4 assignment, evidence locations, source-versus-inference distinctions, and reviewer-derived values. The audit may see the extraction because its purpose is error detection.
3. **Deterministic validation.** Validate schema, controlled values, IDs, required fields, links, units, and calculations that can be reproduced. Preserve source values and reviewer-derived values separately.
4. **Human adjudication.** The reviewer resolves every audit or deterministic issue against the full source. No automated process writes directly to the canonical extraction.
5. **Cross-report pass.** After report extraction, the reviewer resolves report families and artifact-lineage identity, updates only report-level `lineage_id` values, and creates separate lineage-level and consolidated tailoring-application records. Run one focused cross-report audit for every uncertain merge or split and every lineage-level R3 or R4 assignment.

A focused audit is complete only when the complete source sections, figures, and tables needed for its scope were available. Record the report or lineage, actor, date, scope, source and extraction hashes, completion status, issues raised, and human disposition. Record each accepted correction or unresolved ambiguity in a concise discrepancy log containing field, original value, proposed value, final value, evidence, impact, and reason.

Use an LLM only after recording that transmission, processing, retention, storage, and publication handling are permitted for the source and provider route. If no authorized route is available or document ingestion is incomplete, use the delayed human audit. Model output is an error-detection aid, not an independent reviewer or evidence source.

After all first-pass report extractions are complete, select a reproducible test–retest sample of `n = min(5, max(2, ceil(0.10 × N)))` when `N > 0`. Include Route A and Route B when both are present and at least one report with complex RQ2, RQ3, or artifact content when available. Freeze the sampling frame, sorted IDs, selection rule, seed, and selected IDs. The reviewer re-extracts each sampled report after at least seven days while the original extraction and audit output are hidden. Compare and adjudicate all differences. Report this as sole-reviewer consistency, not independent agreement.

Ask the supervisor to audit up to two reports from the test–retest sample when available. Preserve the requested and completed scope. Do not replace a missing supervisor check with an LLM label.

A discrepancy is impactful when it can change eligibility or route, a report family or lineage, a reuse level, a tailoring application, direct RQ2 or RQ3 status, outcome direction, support, a quantitative result, or a synthesis conclusion. An impactful issue that may recur triggers a targeted check of every report or lineage that could be affected. Record any codebook change, focused recalibration, and recheck scope.

Do not calculate inter-rater reliability between the reviewer and an LLM. Report audit coverage, issues raised, accepted corrections, rejected flags, unresolved ambiguities, and test–retest differences with their denominators.

Before synthesis, validate every report-level extraction and every separate family, lineage, and consolidated application table against the frozen schema. Confirm that every included report has a completed focused audit or human fallback, every discrepancy has a human disposition, every derived value is reproducible, every lineage-level field preserves report provenance, and cross-report processing changed only report-level `lineage_id` values.

## Planned synthesis

Use a structured evidence map and narrative synthesis. Do not pool effect estimates because the models, outcomes, and evidence designs are expected to differ too much.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 through 2023. It maps methods, languages, tools, five MBSE phases, and general challenges across many kinds of space work.

Use Buruso et al. only under the [Part 1 evidence restrictions](protocol.md#need-for-this-review), the [supporting prior-secondary-review protocol](protocol-prior-secondary-reviews.md), and the [Part 2 baseline and citation-search procedure](protocol-discovery-and-appraisal.md#completing-the-baseline-and-citation-searches).

This review is not an update or replication of Buruso et al. Do not compare the two reviews' counts as evidence of effectiveness.

For a descriptive view of currency and overlap, results may be split into 2011–2023, matching Buruso et al.'s evidence window, and 2024 through the common evidence cutoff. This split does not change eligibility or imply independence.

### RQ1

- Synthesize report context, EPS representation, grouped inputs and assumptions, grouped engineering results, implementation footprint, limitations, and evaluative RQ1 claims.
- Present Route A and Route B separately before combining them.
- Compare author labels such as *lightweight* or *scalable* with the extracted footprint and inline support.
- Present all `report_reuse_level` values as source-bounded report-level results. Synthesize resolved artifact lineages, applicability envelopes, reusable cores, variation points, tailoring methods, tailoring effort, assurance, independence, failures, demonstrated coverage, and `lineage_reuse_level` from the separate lineage-level records. Use lineage and consolidated-application denominators for deduplicated conclusions, and keep unresolved report-level cases visible.
- Keep method or workflow reuse separate from artifact reuse.

### RQ2

- Use only findings with `direct_synthesis = yes` for direct conclusions. Present near misses separately.
- Present claim kind and scope, role, category, author direction, evidence-supported direction, mechanism, measure directness, evidence basis, support, comparator adequacy and rival explanations when required, applicability, and lifecycle stage.
- Present assertion-only findings separately from executed, comparative, stakeholder, physical, operational, and independent-transfer evidence.
- Preserve source-reported values, units, denominators, uncertainty, and practical interpretation. Label reviewer-derived values.
- Keep benefits, null findings, adverse findings, and burdens visible without calculating a reviewer-defined net effect.

### RQ3

- Use only activities with `direct_synthesis = yes` for direct conclusions. Present system-wide co-occurrence and other near misses separately.
- Map target, bridge, V&V object, method, criterion, timing, execution, result, evidence basis, support, and later physical continuity.
- Keep EPS-specific and system-wide EPS-linked activities separate.
- Distinguish execution from validation and model-to-test closure.
- Record comparator adequacy and rival explanations only for comparative or causal V&V-effectiveness claims.

### Cross-cutting safeguards

- Apply the canonical units, denominator, and dependence rules in Part 1.
- Separate peer-reviewed reports from preprints, technical reports, and theses in descriptive or sensitivity views when useful.
- Apply the Part 2 [finding-support and conclusion-confidence framework](protocol-discovery-and-appraisal.md#finding-support-reporting-bias-assessment-and-conclusion-confidence).
- Use sensitivity views by route, evidence basis, support, measure directness, comparator adequacy when required, publication provenance, lineage confidence, reuse level, and artifact availability.
- Treat cross-tabulations as descriptive co-reporting unless extraction establishes a direct link.
- Treat sparse direct evidence as a result. Do not fill gaps with whole-spacecraft MBSE claims.

## Required new-run artifacts

Under the Part 1 restart policy, create these artifacts with provenance after task [`P-000`](TASKS.md) is complete. Track search infrastructure under [`S-001`](TASKS.md), extraction forms under `E-001`, and remaining artifacts under [`A-001`](TASKS.md):

- dated methods decision log.
- complete Part 2 discovery and screening artifact bundle.
- separate prior-secondary-review bundle.
- frozen report-level extraction codebook and schema.
- one extraction file per included report.
- report-family table.
- compiled report-level reuse-record and report-level application tables.
- separate artifact-lineage extraction table.
- separate consolidated tailoring-application table including effort and assurance.
- focused-audit log, discrepancy and adjudication log, deterministic-validation report, test–retest files, and supervisor-audit files when applicable.
- compiled report, report-level reuse, RQ2, RQ3, lineage-level reuse, and consolidated tailoring data.
- bibliography, analysis code, and derived-value scripts.
- machine-readable PRISMA count reconciliation, official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S and PRISMA 2020 checklists.

Do not publish licensed exports, copyrighted abstracts, or full texts when rights prevent it. Publish or archive the methods, dates, schemas, decisions, derived counts, code, and a clear materials-availability statement.

## Completed-review reporting

The final report will:

- name every source used, search date, and common evidence cutoff.
- distinguish failed or planned-but-unused sources.
- link to exact source-native searches and PRISMA-S logs.
- report focused-audit, deterministic-validation, test–retest, and supervisor coverage exactly as performed.
- report the prior-secondary-review assessment separately.
- explain why no pooled effect estimate was used.
- label every count with its analytic denominator.
- cite apparently eligible full-text exclusions with source-located reasons.
- present evidence basis, finding support, reporting-bias considerations, reuse levels, and conclusion confidence under Part 2.
- report all protocol changes and departures.
- state access to the protocol, data, code, and materials.

---

**Previous:** [Part 2 — Discovery and appraisal](protocol-discovery-and-appraisal.md)
