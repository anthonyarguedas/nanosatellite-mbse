# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction

## Extraction design

Extraction is report-level by default. Create one extraction file for each included report. Use nested groups for EPS content, inputs, results, findings, and V&V activities. Create another EPS case section only when a report contains materially separate models, implementations, or evaluations that cannot be represented clearly together.

Keep report-family resolution and cross-report artifact identity pending during the first report pass. Record concise family leads. Fully extract every reusable artifact, reported lineage, reuse claim, and tailoring application described by each report, including a report-bounded reuse level. Resolve families and cross-report lineage identity after all report extractions are available, then create separate lineage-level and consolidated application records.

Report-level records remain fixed during the cross-report pass. That pass may update only `lineage_id` from its first-pass state to a stable resolved ID or `unresolved_after_review`. It does not backfill or overwrite any other report-level field.

Do not create separate analytic objects for individual measurements, comparators, rival explanations, appraisal domains, or claim-support judgments. Keep them as fields in the result, finding, activity, lineage, or tailoring row that uses them.

### Common field rules

Create a codebook and machine-readable schema from this protocol before full extraction. Every report and repeatable row must have a stable ID. Each repeatable row also records:

- `evidence_location`, including report ID, page, section, and figure or table when relevant.
- `coding_confidence`, using `high`, `moderate`, or `low`. Assign coding confidence as `high` for explicit and unambiguous source support, `moderate` when a bounded reconstruction is required, and `low` when material ambiguity remains.
- `provenance`, using `source_reported`, `author_claimed_or_planned`, `reviewer_inferred`, or `reviewer_derived`.
- `notes`, only when needed to explain ambiguity or a coding decision.

Apply the evidence statuses `not_reported`, `none`, `not_applicable`, and `uncertain` exactly. 

- **`not_reported`:** the available source does not provide the information needed for the field;
- **`none`:** the evidence establishes that the condition, item, result, or capability was absent or failed, rather than merely unreported;
- **`not_applicable`:** the field or rule does not logically apply to the evidence unit, with a narrow reason; and
- **`uncertain`:** relevant evidence exists, but it does not resolve the value or classification.

`unclear` is a field-specific classification used where a controlled vocabulary expressly provides it; it is not a substitute for one of the statuses above when that field distinguishes them. Missing reporting does not prove absence or poor conduct, and coding confidence does not replace a controlled status. Within source-reported information, distinguish author-declared or planned content from source-observed results; keep both separate from reviewer-inferred and reviewer-derived information.

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
- possible companion reports or shared implementations.
- `family_lead`, using `yes`, `no`, or `uncertain`.
- concise report-family lead reason, or `not_reported`.
- source-file path.

For a thesis or dissertation, also record degree level and name, institution, country, department, and completion status.

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

For a list of EPS elements see [Part 1 - EPS boundary and elements](protocol.md#EPS boundary and elements)

Purposes may include definition or sizing, requirements or traceability, trade study, interface management, executable analysis, V&V, communication, lifecycle continuity, and reuse or tailoring.

- **EPS anchor**: a named EPS requirement, function, behavior, component, interface, mode, load or profile, budget, parameter, constraint, or hazard;
- **model anchor**: an identifiable representation of that EPS content in a structured system-model artifact or a clearly connected analysis model; and
- **EPS-to-model bridge**: a locatable relationship between the EPS anchor and a second concern, such as a requirement, behavior, architecture or interface, analysis, decision, output, or V&V artifact. Examples include allocation, trace, satisfy/refine/verify relations, interfaces or flows, parametric bindings, transformations, and data mappings.

An EPS label, equipment-list entry, or place in a general spacecraft breakdown can show where an anchor appears, but it is not a bridge by itself. The source does not have to name a formal relationship type. Its endpoints and meaning must still be clear enough to reconstruct.

Support the anchors and bridge with text, a figure or table, a model extract, a trace record, or another identifiable location in the source. Keywords, reviewer inference, or items that merely appear in the same report are not enough.

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

- **`evidence_basis`**, using one or more of `assertion_only`, `worked_example`, `executed_result`, `comparison`, `stakeholder_evidence`, `physical_or_operational_check`, and `independent_transfer`;
- **`support`**, using `supported`, `limited`, `unsupported`, or `unclear`; and
- **`support_reason`**, one concise source-located sentence naming the strongest evidence and the main limitation.

Use the support codes as follows:

- **`supported`:** direct or credibly justified evidence from a method fit for the bounded claim supports it, with no major unresolved limitation relevant to that claim.
- **`limited`:** relevant evidence exists, but an important limitation in method, directness, comparison, precision, independence, or applicability remains.
- **`unsupported`:** the source provides assertion only, no observation bearing on the claim, or a result that does not measure the claimed construct.
- **`unclear`:** relevant evidence is reported, but ambiguity prevents a support judgment.

### RQ2 outcome and burden findings

Create one row for each materially distinct EPS-attributed outcome, burden, or trade-off. Split a statement when direction, evidence, actor, scenario, or scope differs materially. Keep plausible near misses with `direct_synthesis = no` and one reason.

Record:

- `rq2_finding_id`.
- `direct_synthesis`, using `yes`, `no`, or `uncertain`.
- exclusion or uncertainty reason when not in direct synthesis.
- exact claim wording.
- claim kind, using `descriptive_occurrence`, `feasibility_or_executed_result`, `technical_performance`, `comparative`, `causal_attribution`, `experiential_or_perceived`, `implementation_burden`, `transfer_or_generalization`, `other`, or `unclear`.
- role, using `outcome`, `implementation_burden`, or `mixed_trade_off`.
- target and scope.
- outcome category.
- author-claimed direction, using `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, `unclear`, or `not_reported`.
- evidence-supported direction, using `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, `unclear`, or `unsupported`.
- EPS attribution, using `explicit_eps_attribution`, `ambiguous_attribution`, or `generic_or_ineligible`.
- mechanism, which is the explanation given by the source of how an EPS-linked model artifact or activity led to a claimed outcome or burden. Do not infer a mechanism. Use `not_reported` when the source provides no explanation. A missing mechanism makes the claim harder to interpret but does not remove an otherwise clear EPS-attributed finding.
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
- criteria or pass/fail criteria as a nested table containing criterion ID, target, threshold or expected behavior, source, and applicability.
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

- **EPS target**: a named EPS requirement, model element, parameter, mode, interface, behavior, function, or hazard; or a wider system target that is clearly decomposed, allocated, or traced to named EPS content;
- **model-to-V&V bridge**: a reported trace, shared ID, binding, port or data mapping, transformation, generated artifact, allocation, or another clear link; and
- **V&V method, intent, or artifact**: the source presents the work as verification, validation, compliance or requirement checking, virtual integration, a model-derived test activity, or another V&V function.

- **`eps_specific`:** both the target and the V&V activity are clearly about the EPS;
- **`system_wide_eps_linked`:** a wider system activity includes a named EPS target and a bridge that can be reconstructed;
- **`system_wide_cooccurrence`:** system-wide V&V and EPS content appear in the same report without the required direct link; or
- **`unclear`:** the report does not make the scope clear.

- **model verification:** checking whether a model, transformation, or executable representation was implemented correctly against its specification or formulation;
- **model validation:** checking whether a model is adequate or credible for its intended use against an authoritative reference, data, or expected behavior;
- **system/design verification:** checking whether the EPS or wider design meets stated requirements or criteria;
- **system/design validation:** checking whether the design meets stakeholder, operational, or mission needs;
- **multiple:** the source clearly demonstrates more than one of these objects; or
- **unclear.**

Keep the source's own term as well as the reviewer's normalized code and reason. Running a method in a model does not automatically make it model verification or model validation. For example, a virtual requirement check can be system or design verification. Code execution settings such as MIL, SIL, PIL, HIL, and virtual testbeds separately from the V&V object.

Classify status in stages.

- `proposed`: target, bridge, and V&V method, intent, or artifact are reported.
- `prepared_or_generated`: the activity also gives a requirement, threshold, expected behavior, formal property, or pass/fail criterion.
- `executed_virtual`: the linked method was run before physical integration or testing of the target EPS, and the source reports a result or verdict (`result_reported`).
- `model_to_test_closure`: the source links a later physical artifact or activity (`downstream_physical_link`). Reserve `model_to_test_closure` for cases that compare results and report how differences were handled.

### Reusable artifact and reported lineage

A **reusable EPS MBSE artifact** is a source-identifiable structured-model asset, or documented package of assets, that contains a qualifying EPS thread or is explicitly connected to one. It can be:

- a reference or template model;
- a metamodel or profile that carries EPS meaning;
- a model library or pattern;
- an interface contract;
- a parametric-model package;
- a transformation or generator with persistent model content; or
- a larger reusable spacecraft model whose EPS part can be reconstructed separately.

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
- `report_reuse_level`, using any level from `NA` through `R4_independent_reuse_demonstrated`
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

A **reusable core** is the set of model elements, relationships, constraints, interfaces, meanings, or packaged assets that the source states or clearly shows remain across uses.

A **variation point** is a source-described place, option, range, rule, or dependency through which that core can vary.

**Tailoring** means using a source-described process to create or select a target-specific instance. It can involve configuration, parameterization, selection, specialization, extension, deletion or substitution, interface mapping, transformation or generation, or a clearly justified decision to use the artifact unchanged.

A parameter sweep or scenario run in one unchanged mission model is analysis, not tailoring across settings. Rebuilding a model without structure may show reuse of a method. It shows reuse of an artifact only when the source establishes the artifact lineage and the retained core.

Table of reuse level codes.
| Level | Minimum evidence | Meaning |
|---|---|---|
| **`NA`** | No identifiable reusable EPS model artifact, or only a method or workflow is reused | Keep the reuse description under report-level RQ1. |
| **`R0_artifact_only`** | An EPS-linked artifact is identifiable, with no reuse claim or application reported | An artifact exists. Reuse has not been claimed or shown. |
| **`R1_reuse_claimed`** | The source claims or suggests reuse for the identifiable artifact | Reuse is asserted. Its range and method are not sufficiently specified. |
| **`R2_reuse_specified`** | The declared applicability envelope, reusable core, variation points or unchanged-use rule, tailoring process, and prerequisites are reported | Bounded reuse is specified. Transfer does not have to be demonstrated. |
| **`R3_reuse_demonstrated`** | R2 is met, and at least one materially distinct target setting uses the identified core, reports what stayed the same and what changed, and reports a relevant post-tailoring check and result | Transfer is demonstrated in the reported setting. |
| **`R4_independent_reuse_demonstrated`** | R3 is met by at least one adopter operationally independent of the originating implementation team | Independent transfer is demonstrated in the reported setting. |

#### Report-level tailoring application

A **tailoring application** is one use of an artifact lineage in one target setting. The original development mission counts only if the source identifies it as an adoption or configuration of the same reusable core and reports what was kept and changed, or why it was used unchanged. The mission where an artifact happened to be created does not by itself show transfer.

Two applications are **materially distinct** only if they differ on at least one DAE dimension in a way that exercises or tests the reuse claim. Two papers, scenarios, revisions, or names for the same implementation do not count as two applications.

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

One LLM reviewer reviews the primary extraction and every final decision. Verification uses one focused audit, deterministic validation, a delayed LLM test–retest sample.

Apply this sequence:

1. **Primary extraction.** An LLM extracts the complete report into the frozen report-level form.
2. **Focused audit.** For every included report, a human check reviews eligibility and route, Route B anchors and bridge, omitted or duplicated groups, direct RQ2 attribution, direct RQ3 linkage, `lineage_mentioned`, complete report-level reuse and application coding, every report-level R3 or R4 assignment, evidence locations, source-versus-inference distinctions, and reviewer-derived values. The audit may see the extraction because its purpose is error detection.
3. **Deterministic validation.** Validate schema, controlled values, IDs, required fields, links, units, and calculations that can be reproduced. Preserve source values and reviewer-derived values separately.
4. **Human adjudication.** The reviewer resolves every audit or deterministic issue against the full source. No automated process writes directly to the canonical extraction.
5. **Cross-report pass.** After report extraction, an LLM resolves report families and artifact-lineage identity, updates only report-level `lineage_id` values, and creates separate lineage-level and consolidated tailoring-application records. Run one focused cross-report audit for every uncertain merge or split and every lineage-level R3 or R4 assignment.

A focused audit is complete only when the complete source sections, figures, and tables needed for its scope were available. Record the report or lineage, actor, date, scope, source and extraction hashes, completion status, issues raised, and human disposition. Record each accepted correction or unresolved ambiguity in a concise discrepancy log containing field, original value, proposed value, final value, evidence, impact, and reason.

After all first-pass report extractions are complete, select a reproducible test–retest sample of `n = min(5, max(2, ceil(0.10 × N)))` when `N > 0`. Include Route A and Route B when both are present and at least one report with complex RQ2, RQ3, or artifact content when available. Freeze the sampling frame, sorted IDs, selection rule, seed, and selected IDs. The LLM re-extracts each sampled report while the original extraction and audit output are hidden. Compare and adjudicate all differences. Report this as sole-reviewer consistency, not independent agreement.

A discrepancy is impactful when it can change eligibility or route, a report family or lineage, a reuse level, a tailoring application, direct RQ2 or RQ3 status, outcome direction, support, a quantitative result, or a synthesis conclusion. An impactful issue that may recur triggers a targeted check of every report or lineage that could be affected. Record any codebook change, focused recalibration, and recheck scope.

Do not calculate inter-rater reliability between the reviewer and an LLM. Report audit coverage, issues raised, accepted corrections, rejected flags, unresolved ambiguities, and test–retest differences with their denominators.

Before synthesis, validate every report-level extraction and every separate family, lineage, and consolidated application table against the frozen schema. Confirm that every included report has a completed focused audit, every discrepancy has a human disposition, every derived value is reproducible, every lineage-level field preserves report provenance, and cross-report processing changed only report-level `lineage_id` values.
