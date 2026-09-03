# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction

## Extraction design

Extraction is report-level by default. Create one extraction file for each included report. Use nested groups for EPS content, inputs, results, findings, and V&V activities. Create another EPS case section only when a report contains materially separate models, implementations, or evaluations that cannot be represented clearly together.

Keep report-family resolution and cross-report artifact identity pending during the first report pass. Record concise family leads. Fully extract every model generation method, reusable artifact, reported lineage, reuse claim, and reuse or tailoring application described by each report, including report-bounded artifact and method reuse levels. Resolve families and cross-report artifact-lineage identity after all report extractions are available, then create separate lineage-level and consolidated artifact application records.

Report-level records remain fixed during the cross-report pass. That pass may update only `lineage_id` from its first-pass state to a stable resolved ID or `unresolved_after_review`. It does not backfill or overwrite any other report-level field.

Record each source fact once at its most detailed applicable location. Store measurements, criteria and verdicts, comparators and rival explanations in the result set that reports them. Store implementation effort and burdens in implementation records. Store reuse and tailoring evidence in report-level applications. Give each nested row a stable ID, then link later findings, activities, reuse assessments, and consolidated records to those IDs instead of copying the content. Do not create separate top-level analytic objects for individual measurements, comparators, rival explanations, appraisal domains, or claim-support judgments.

### Common field rules

Create a codebook and machine-readable schema from this protocol before full extraction. Every report, repeatable coded record, and nested coded row must have a stable ID.

Each report extraction contains a `citations` table. Each citation row records:

- `citation_id`, unique across the review.
- `report_id`.
- `page`, using the one-based physical page in the stored source file.
- `quote`, copied verbatim from that page.
- optional `graphic`, identifying a figure, table, diagram, or other graphic containing the quote.
- optional `graphic_quote_description`, briefly describing where the quote appears in the graphic and how it supports the coding.

A citation containing `graphic` or `graphic_quote_description` is excluded from deterministic quote matching. The human auditor verifies its quote, graphic reference, and description against the cited page. Store each citation once and reuse its ID. Split a quotation that crosses pages into one citation per page. Every source-backed field or compact group of fields records the applicable `citation_ids`. Each repeatable coded record and nested coded row also records:

- `coding_confidence`, using `high`, `moderate`, or `low`. Assign coding confidence as `high` for explicit and unambiguous source support, `moderate` when a bounded reconstruction is required, and `low` when material ambiguity remains.
- `provenance`, using `source_reported`, `author_claimed_or_planned`, `reviewer_inferred`, or `reviewer_derived`.
- `notes`, only when needed to explain ambiguity or a coding decision.

Use the provenance codes as follows:

- **`source_reported`:** the source explicitly documents the fact, method, artifact, action, datum, or observed result.
- **`author_claimed_or_planned`:** the source presents an interpretation, estimate, expected result, intention, or future action.
- **`reviewer_inferred`:** the reviewer reconstructs a nonnumeric value from cited evidence.
- **`reviewer_derived`:** the reviewer calculates, converts, or transforms cited source values using a recorded method.

Every field that records source evidence accepts the evidence statuses `not_reported`, `none`, `not_applicable`, and `uncertain` in place of an ordinary value. A status applies to the whole field and cannot coexist with an ordinary value. For a repeatable field, use the status in place of the array. An empty array does not mean `none`. Stable IDs, links, and reviewer-derived or schema-derived fields follow their own required-value rules.

- **`not_reported`:** the available source does not provide the information needed for the field;
- **`none`:** the evidence establishes that the condition, item, result, or capability was absent or failed, rather than merely unreported;
- **`not_applicable`:** the field or rule does not logically apply to the evidence unit, with a narrow reason; and
- **`uncertain`:** relevant evidence exists, but it does not resolve the value or classification.

Citations are required for source-reported, author-claimed or planned, and reviewer-inferred coding, and for `none` and `uncertain`. Reviewer-derived values link to their cited source values. `not_reported` and `not_applicable` do not require a citation, but each requires a concise reason.

`unclear` is a field-specific classification used where a controlled vocabulary expressly provides it. It does not replace one of the statuses above when that field distinguishes them. Missing reporting does not prove absence or poor conduct, and coding confidence does not replace a controlled status. Within source-reported information, distinguish author-declared or planned content from source-observed results. Keep both separate from reviewer-inferred and reviewer-derived information.

A citation and coding confidence may cover a compact group of fields supported by the same quotation. Do not duplicate a citation for every field. For every controlled field, `other` requires the source term and a note.

Discovery events, search ranks, raw-file provenance, and screening history remain in the search and screening data. Link them through `screening_record_id` rather than copying them into the extraction.

## Report-level extraction fields

### Identity, eligibility, and review management

Record:

- `report_id`.
- `screening_record_id`.
- title and authors.
- year and full publication date when available.
- venue or issuing organization.
- DOI, arXiv ID, or other stable URL.
- possible companion reports or shared implementations, derived as the union of possible related reports or artifacts in the report-level reuse records.
- `family_lead`, using `yes`, `no`, or `uncertain`.
- concise report-family lead reason, or `not_reported`.
- source-file path.

Read publication type, publication status, and degree metadata through `screening_record_id`. Do not copy them into the extraction.

Use `family_lead` as follows:

- **`yes`:** at least one candidate companion report or shared implementation was identified.
- **`no`:** no candidate lead was found during complete source review. This does not prove that no companion exists.
- **`uncertain`:** a possible relationship exists, but the candidate cannot be identified or bounded reliably.

For an arXiv preprint, also record the version and version date. Use the arXiv ID recorded with the other stable identifiers.

### Report and implementation context

Record:

- mission or platform.
- form factor or mass.
- mission purpose or domain.
- orbit and environment.
- `organization_type`, using one or more of `academic`, `civil_space_agency`, `other_government_or_defence`, `industry`, `nonprofit_or_independent_research`, `other`, or `unclear`.
- `development_setting`, using one or more of `academic_project`, `agency_program`, `industrial_project`, `distributed`, `agile_or_iterative`, `concurrent_engineering`, `rapid_development`, `resource_constrained`, `other`, or `unclear`.
- lifecycle stages actually demonstrated, using the lifecycle-stage codes below.
- lifecycle stages only claimed or planned, using the same lifecycle-stage codes.
- `project_maturity`, using one or more of `conceptual_framework`, `reference_or_template`, `prototype`, `executable`, `used_on_project`, `physically_checked`, `operational`, or `flight`.

Use organization type as follows:

- **`academic`:** a university, college, or academic research organization.
- **`civil_space_agency`:** a civil government space agency or its center.
- **`other_government_or_defence`:** another government, public-sector, military, or defence organization.
- **`industry`:** a commercial company or industrial organization.
- **`nonprofit_or_independent_research`:** a nonprofit or independent research organization.
- **`other`:** another identified organization type.
- **`unclear`:** the organization type cannot be classified.

Use development setting as follows:

- **`academic_project`:** conducted as university research or student development.
- **`agency_program`:** conducted within an agency-led program.
- **`industrial_project`:** conducted within commercial development.
- **`distributed`:** work is divided across locations or organizations.
- **`agile_or_iterative`:** short or iterative development cycles are used.
- **`concurrent_engineering`:** disciplines work together through an explicit concurrent process.
- **`rapid_development`:** schedule compression is an explicit approach.
- **`resource_constrained`:** limited staffing, funding, tools, or time materially shapes development.
- **`other`:** another identified development setting.
- **`unclear`:** the development setting cannot be classified.

Use these lifecycle-stage codes:

- **`concept_and_feasibility`:** mission concept or feasibility work.
- **`requirements`:** needs and system requirements development.
- **`architecture_and_design`:** functional, logical, or physical design.
- **`implementation`:** hardware, software, or model realization.
- **`integration`:** assembly or integration across elements.
- **`verification`:** checking requirements or specifications.
- **`validation`:** checking stakeholder, mission, or intended-use needs.
- **`deployment_and_commissioning`:** launch preparation, deployment, or commissioning.
- **`operations`:** active mission operations.
- **`maintenance_and_sustainment`:** ongoing support or change during use.
- **`retirement_or_disposal`:** end-of-life work.
- **`cross_lifecycle`:** explicit continuity across several stages.
- **`other`:** another identified lifecycle stage.
- **`unclear`:** the lifecycle stage cannot be classified.

Use project maturity as follows:

- **`conceptual_framework`:** concepts or a method are defined without a target-specific implementation.
- **`reference_or_template`:** a generic artifact is intended for repeated configuration or instantiation.
- **`prototype`:** a target-specific proof of concept exists without established project use.
- **`executable`:** the model or toolchain runs and produces an output or artifact.
- **`used_on_project`:** it supports actual mission or project engineering work.
- **`physically_checked`:** it is compared or connected with hardware, test data, or other physical evidence.
- **`operational`:** it supports a deployed operational process or spacecraft.
- **`flight`:** the represented spacecraft or EPS has flown.

### MBSE approach

Record:

- problem addressed.
- intended decision.
- reason for using MBSE.
- `model_generation_methods` as nested rows containing `model_generation_method_id`, linked `eps_case_id` values, the source method name or description, and `generation_method_types`, using one or more of `named_mbse_method`, `author_defined_process`, `manual_model_construction`, `reference_or_template_instantiation`, `configuration_or_parameterization`, `model_transformation`, `automated_generation`, `import_or_reverse_engineering`, `other`, or `unclear`.
- `modeling_languages`, preserving source-reported names and versions.
- tools and versions.
- toolchain and data flow.
- model artifacts.
- modeled systems-engineering concerns.
- explicit relationships among concerns.
- system boundary.
- artifact availability, using the shared availability codes below.

Use these availability codes for report artifacts, EPS assets, reusable artifacts, and resulting tailored artifacts:

- **`public_complete`:** the source identifies public access to the complete asset.
- **`public_partial`:** only extracts, documentation, or part of the asset are public.
- **`available_on_request`:** access requires a request to an author or owner.
- **`restricted`:** access is proprietary, internal, controlled, or otherwise limited.
- **`described_only`:** the asset is described without an identified distribution route.
- **`unavailable`:** the source states that it is unavailable.
- **`unclear`:** the reported access condition cannot be classified.

A model generation method is a reported procedure used to construct, populate, configure, transform, or generate the EPS MBSE model. A modeling language or tool alone is not a generation method. The common evidence fields apply to every method row.

Use generation method types as follows:

- **`named_mbse_method`:** the source applies an identified MBSE method or process.
- **`author_defined_process`:** the source defines its own model creation process.
- **`manual_model_construction`:** people construct or populate the model directly.
- **`reference_or_template_instantiation`:** a reference model or template is instantiated for the target.
- **`configuration_or_parameterization`:** an existing model is configured or parameterized.
- **`model_transformation`:** a source model or representation is transformed into the EPS model or part of it.
- **`automated_generation`:** software generates the EPS model or a persistent part of it.
- **`import_or_reverse_engineering`:** existing data, documents, software, or hardware descriptions are imported or reconstructed into the model.
- **`other`:** another identified generation method.
- **`unclear`:** the generation method cannot be classified.

### EPS representation

For each report, record one EPS case section by default. Record:

- `eps_case_id`, including for the single default case.
- EPS anchor.
- model anchor for Route B.
- EPS boundary.
- EPS elements.
- EPS architecture.
- `eps_exchanges` as nested rows containing `eps_exchange_id`, source endpoint, destination endpoint, named EPS interface when present, exchanged item, direction, `exchange_type` using `energy`, `information_or_control`, `material_or_other_resource`, `mixed`, `other`, or `unclear`, and `exchange_scope` using `within_eps`, `cross_subsystem`, `spacecraft_environment`, `external_system`, or `unclear`.
- `eps_dependencies` as nested rows containing `eps_dependency_id`, dependent endpoint, provider or driver endpoint, description, linked `eps_exchange_id` values when applicable, `dependency_type` using `electrical_power`, `information_or_control`, `thermal_or_environmental`, `mechanical_or_structural`, `functional_or_behavioral`, `operational_or_mode`, `requirement_or_constraint`, `shared_resource`, `other`, or `unclear`, and `dependency_scope` using `within_eps`, `cross_subsystem`, `spacecraft_environment`, `external_system`, or `unclear`.
- EPS modes and operations.
- EPS model representations.
- `modeled_disciplinary_viewpoints`, using one or more of `electrical_or_electronic`, `thermal`, `software_or_algorithmic`, `mechanical_or_structural`, `operational`, `other`, or `unclear`.
- EPS-to-model bridges as nested rows containing `eps_model_bridge_id`, the EPS anchor endpoint, the model or second-concern endpoint, relationship or mapping, and reconstructed meaning. Record every bridge needed to establish qualification and Route B eligibility.
- `eps_abstraction`, using `conceptual`, `logical`, `physical_design`, `implementation`, `mixed`, or `unclear`.
- `eps_decomposition_visibility`, using `black_box`, `white_box`, `mixed`, or `unclear`.
- `eps_fidelity`, using `qualitative`, `idealized_quantitative`, `engineering_representative`, `implementation_representative`, `as_built_or_calibrated`, `mixed`, or `unclear`.
- purposes, using one or more of `definition_or_sizing`, `requirements_or_traceability`, `trade_study`, `interface_management`, `executable_analysis`, `verification_and_validation`, `communication`, `lifecycle_continuity`, `reuse_or_tailoring`, or `other`, and the supported decisions.
- scope deliberately omitted.
- EPS model maturity, using the project-maturity codes at EPS-model scope.
- availability of the EPS model, profile, script, data, or documentation, using the shared availability codes.

For a list of EPS elements see [Part 1 - EPS boundary and elements](protocol.md#EPS boundary and elements)

Use exchange type as follows:

- **`energy`:** electrical or other energy crosses the identified interface.
- **`information_or_control`:** data, status, commands, or control signals cross the identified interface.
- **`material_or_other_resource`:** matter or another nonenergy resource crosses the identified interface.
- **`mixed`:** inseparable exchanges of more than one type are represented.
- **`other`:** another identified exchange type.
- **`unclear`:** the exchange type cannot be classified.

Use exchange scope as follows:

- **`within_eps`:** both exchange endpoints are inside the EPS boundary.
- **`cross_subsystem`:** the exchange crosses between the EPS and another nanosatellite subsystem.
- **`spacecraft_environment`:** the exchange crosses between the EPS and the spacecraft's physical or orbital environment.
- **`external_system`:** the exchange involves a ground, launch, test, or other external system.
- **`unclear`:** the exchange scope cannot be classified.

Use dependency type as follows:

- **`electrical_power`:** an element depends on electrical power, energy, voltage, current, capacity, or another electrical condition.
- **`information_or_control`:** an element depends on data, status, commands, control, or communication.
- **`thermal_or_environmental`:** an element depends on temperature, illumination, radiation, orbit, or another environmental condition.
- **`mechanical_or_structural`:** an element depends on physical placement, structure, mass, geometry, or a mechanical connection.
- **`functional_or_behavioral`:** an element depends on another function, behavior, or state transition.
- **`operational_or_mode`:** an element depends on mission operations, schedules, spacecraft modes, or load profiles.
- **`requirement_or_constraint`:** an element depends on a requirement, limit, rule, or design constraint.
- **`shared_resource`:** an element depends on another shared resource that is not classified above.
- **`other`:** another identified dependency type.
- **`unclear`:** the dependency type cannot be classified.

Use dependency scope as follows:

- **`within_eps`:** both dependency endpoints are inside the EPS boundary.
- **`cross_subsystem`:** the dependency crosses between the EPS and another nanosatellite subsystem.
- **`spacecraft_environment`:** the dependency connects the EPS to the spacecraft's physical or orbital environment.
- **`external_system`:** the dependency involves a ground, launch, test, or other external system.
- **`unclear`:** the dependency scope cannot be classified.

Use modeled disciplinary viewpoints as follows:

- **`electrical_or_electronic`:** electrical power, electronics, circuits, or electrical interfaces are represented.
- **`thermal`:** temperatures, heat transfer, or thermal constraints are represented.
- **`software_or_algorithmic`:** software, firmware, control logic, or algorithms are represented.
- **`mechanical_or_structural`:** mechanical configuration, packaging, geometry, mass, or structure is represented.
- **`operational`:** mission operations, spacecraft modes, schedules, or operational scenarios are represented.
- **`other`:** another identified disciplinary viewpoint is represented.
- **`unclear`:** the modeled disciplinary viewpoint cannot be classified.

Use EPS abstraction as follows:

- **`conceptual`:** high-level concepts and relationships without a complete logical architecture.
- **`logical`:** technology-independent functions, behaviors, or logical elements.
- **`physical_design`:** component-level architecture, technology choices, or design parameters.
- **`implementation`:** realized software, hardware, interface, or configuration detail.
- **`mixed`:** the representation explicitly integrates several abstraction levels.
- **`unclear`:** the abstraction level cannot be classified.

Use EPS decomposition visibility as follows:

- **`black_box`:** the representation shows externally visible EPS behavior, exchanges, or interfaces without internal decomposition.
- **`white_box`:** the representation shows internal EPS elements and their relationships.
- **`mixed`:** both black-box and white-box representations are used.
- **`unclear`:** decomposition visibility cannot be classified.

Use EPS fidelity as follows:

- **`qualitative`:** the representation contains no quantitative behavior.
- **`idealized_quantitative`:** simplified quantitative relations support bounded analysis.
- **`engineering_representative`:** mission-relevant parameters and constraints support engineering decisions.
- **`implementation_representative`:** the representation reflects implementation interfaces, timing, or configuration.
- **`as_built_or_calibrated`:** the representation is calibrated or parameterized against a physical instance.
- **`mixed`:** materially different fidelity levels are integrated.
- **`unclear`:** fidelity cannot be classified.

Use EPS purposes as follows:

- **`definition_or_sizing`:** defines architecture, components, capacity, or dimensions.
- **`requirements_or_traceability`:** develops, manages, or links requirements.
- **`trade_study`:** compares design alternatives.
- **`interface_management`:** defines or checks interfaces and flows.
- **`executable_analysis`:** produces quantitative or behavioral analysis.
- **`verification_and_validation`:** defines or performs V&V.
- **`communication`:** supports review or shared understanding.
- **`lifecycle_continuity`:** carries model information across stages or tools.
- **`reuse_or_tailoring`:** supports repeated use or target-specific configuration.
- **`other`:** another source-described purpose.

Apply each project-maturity code to the EPS model itself when recording EPS model maturity.

- **EPS anchor**: a named EPS requirement, function, behavior, component, interface, mode, load or profile, budget, parameter, constraint, or hazard;
- **model anchor**: an identifiable representation of that EPS content in a structured system-model artifact or a clearly connected analysis model; and
- **EPS-to-model bridge**: a locatable relationship between the EPS anchor and a second concern, such as a requirement, behavior, architecture or interface, analysis, decision, output, or V&V artifact. Examples include allocation, trace, satisfy/refine/verify relations, interfaces or flows, parametric bindings, transformations, and data mappings.

An EPS label, equipment-list entry, or place in a general spacecraft breakdown can show where an anchor appears, but it is not a bridge by itself. The source does not have to name a formal relationship type. Its endpoints and meaning must still be clear enough to reconstruct.

Support the anchors and bridge with text, a figure or table, a model extract, a trace record, or another identifiable location in the source. Keywords, reviewer inference, or items that merely appear in the same report are not enough.

The common evidence fields apply to every exchange and dependency row. An exchange or dependency is modeled EPS content. It counts as an EPS-to-model bridge only when it also meets the bridge definition above.

### Implementation footprint and effort records

Group related implementation facts by scope. Create one general implementation record by default. Create another record when a reuse or tailoring application or another bounded implementation has materially different roles, resources, effort, or burdens.

For each implementation record, record:

- `implementation_record_id`.
- scope.
- roles and affected teams.
- skills and training.
- staffing and number of people.
- workflow.
- automation.
- tools, licences, and infrastructure.
- model preparation.
- data preparation.
- computing requirements.
- integration or migration work and interoperability.
- governance and configuration control.
- `effort_basis`, using `measured`, `author_estimated`, or `asserted`.
- person-hours or person-days.
- elapsed duration.
- schedule effect.
- financial cost.
- manual and automated work.
- review and assurance effort.
- rework.
- ongoing maintenance.
- `burden_categories`, using one or more of `effort`, `schedule_or_time`, `financial_cost`, `staffing`, `skills_or_training`, `tools_or_licensing`, `infrastructure`, `model_preparation`, `data_preparation`, `computing`, `integration_or_migration`, `governance_or_configuration`, `maintenance`, `rework`, `other`, or `unclear`.
- `burden_phase`, using `adoption`, `ongoing_use`, `both`, or `unclear`.
- reported burden.
- measurement method.
- mitigation.
- linked benefit or trade-off.

Use effort basis as follows:

- **`measured`:** effort was tracked or measured using a reported basis.
- **`author_estimated`:** the source provides a quantified estimate without direct tracking.
- **`asserted`:** the source characterizes effort without a reported measurement or estimation method.

Use burden phase as follows:

- **`adoption`:** the burden occurs during initial introduction, setup, migration, or training.
- **`ongoing_use`:** the burden occurs during routine operation, update, or maintenance.
- **`both`:** material burden occurs in both phases.
- **`unclear`:** timing cannot be separated.

The burden-category codes identify labor, elapsed time, money, people, competence, tools, infrastructure, preparation, computing, integration, governance, maintenance, or rework burdens according to their labels.

Keep measured values, author estimates, and unsupported characterizations distinct. Link RQ2 burden findings and reuse or tailoring applications to these records instead of copying the implementation details.

### Input and assumption groups

Extract inputs and assumptions that define the EPS representation, materially shape an evaluation or result, establish a V&V configuration or criterion, inform a decision, or bound reuse or tailoring. Group related items as mission requirements, base assumptions, scenario inputs, model formulation, V&V configuration, or tool prerequisites. Do not inventory every model parameter.

For each group, record:

- `input_group_id`.
- `category`, using `mission_requirements`, `base_assumptions`, `scenario_inputs`, `model_formulation`, `vv_configuration`, `tool_prerequisites`, or `other`.
- linked EPS case and scenario or configuration.
- linked `model_generation_method_id` values when the input or assumption applies to a generation method.
- linked `report_reuse_record_id` values when the input or assumption applies to reuse of a method or artifact.
- parameters or constructs.
- material source-reported values or descriptions, with units and time basis when needed for interpretation. State whether a material value is nominal, worst case, a range, or a distribution when the source provides that basis.
- `input_source_types`, using one or more of `requirement`, `standard`, `vendor_data`, `test_data`, `flight_data`, `heritage`, `literature`, `tool_default`, `analyst_assumption`, `calculation`, `other`, or `unclear`.
- material uncertainty, variability, margin, sensitivity, or degradation handling.
- rationale when it affects interpretation.
- linked `result_output_id`, `result_criterion_id`, `rq3_activity_id`, or `report_application_id` values, and decisions, when applicable.

Use input categories as follows:

- **`mission_requirements`:** mission, system, or EPS requirements.
- **`base_assumptions`:** fixed premises shared across evaluations.
- **`scenario_inputs`:** values specific to an operating case or scenario.
- **`model_formulation`:** equations, constraints, structures, or model parameters.
- **`vv_configuration`:** V&V targets, criteria, setup, or configuration.
- **`tool_prerequisites`:** required software, settings, formats, or supporting data.
- **`other`:** another source-described input category.

Use input source types as follows:

- **`requirement`:** an authoritative or project requirement.
- **`standard`:** an external standard or specification.
- **`vendor_data`:** data supplied by a vendor or manufacturer.
- **`test_data`:** data produced by physical or software testing.
- **`flight_data`:** data observed in flight or mission operations.
- **`heritage`:** a prior mission, design, model, or implementation.
- **`literature`:** an external publication or documented study.
- **`tool_default`:** a value supplied by a tool without source-specific replacement.
- **`analyst_assumption`:** a value selected by an analyst without another stated source.
- **`calculation`:** a value calculated by the report authors from other inputs.
- **`other`:** another identified source type.
- **`unclear`:** the input source type cannot be classified.

### Evaluation and result sets

Keep outputs from one evaluation or scenario together. Create a new result set only when the design, scenario, inputs, or evidence basis differs materially.

For each result set, record:

- `result_set_id`.
- linked EPS case.
- `evaluation_design`, using `model_or_simulation_evaluation`, `case_or_experience_report`, `comparative_observational`, `controlled_or_quasi_experimental`, `survey`, `interview_or_qualitative`, `mixed_methods`, `artifact_or_reuse_demonstration`, `other`, or `unclear`.
- scenario or configuration.
- linked input groups.
- cases, participants, or observational units.
- data sources.
- method.
- `execution_status`, using `planned`, `prepared`, `executed_complete`, `executed_partial`, `attempted_failed`, or `unclear`.
- analysis method.
- evaluation-level missing data, failures, exclusions, uncertainty, and sensitivity.
- outputs as a nested table containing `result_output_id`, quantity or construct, source-reported value, unit, time basis, denominator when relevant, observed or expected status, and output-specific missing observations or exclusions. When the source reports a statistical evaluation, also record the applicable central tendency, dispersion, absolute or relative difference, effect estimate, confidence interval, exact p-value, and statistical method. Omit this conditional statistical group for deterministic engineering outputs.
- `criteria` as a nested table containing `result_criterion_id`, source criterion or requirement ID, target, threshold or expected behavior, `source`, `criterion_applicability` using `applicable_as_stated`, `applicable_with_conditions`, `partially_applicable`, `superseded_or_inactive`, or `unclear`, result or verdict, linked `result_output_id` values, scope, observed or expected status, and why the criterion or oracle is authoritative for the intended use when validation is claimed.
- comparators as a nested table containing `comparator_id`, description, `comparator_type` using `usual_or_existing_practice`, `document_based_practice`, `manual_analysis_or_check`, `alternative_model_or_method`, `alternative_toolchain`, `alternative_design_or_configuration`, `prior_mission_or_model`, `no_intervention_or_unassisted`, `external_benchmark_or_reference`, `other`, or `unclear`, `material_differences`, giving a concise account of only the differences that affect interpretation, and `comparator_adequacy` using `adequate`, `partial`, `inadequate`, or `unclear`.
- decision informed.
- physical or operational link.

Use evaluation design as follows:

- **`model_or_simulation_evaluation`:** a model or simulation is analyzed or executed to evaluate behavior or performance.
- **`case_or_experience_report`:** one or more implementations are described without a designed comparison.
- **`comparative_observational`:** existing cases or practices are compared without controlled assignment.
- **`controlled_or_quasi_experimental`:** a designed comparison uses controlled or nonrandom assignment.
- **`survey`:** data come primarily from a structured questionnaire.
- **`interview_or_qualitative`:** data come primarily from interviews, observations, or qualitative analysis.
- **`mixed_methods`:** quantitative and qualitative methods are deliberately integrated.
- **`artifact_or_reuse_demonstration`:** the main evaluation is an artifact instantiation, transfer, or reuse demonstration.
- **`other`:** another identifiable evaluation design.
- **`unclear`:** the reported method cannot be classified.

Use execution status as follows:

- **`planned`:** the evaluation is described but not prepared or run.
- **`prepared`:** inputs or execution artifacts are prepared without a reported run.
- **`executed_complete`:** the intended evaluation scope was completed.
- **`executed_partial`:** only part of the intended scope was completed.
- **`attempted_failed`:** execution was attempted without a usable result.
- **`unclear`:** execution state cannot be established.

Use criterion applicability as follows:

- **`applicable_as_stated`:** the criterion applies to the complete linked target and scenario.
- **`applicable_with_conditions`:** it applies only under stated modes, configurations, or conditions.
- **`partially_applicable`:** it applies to only part of the linked target or scope.
- **`superseded_or_inactive`:** the criterion is identified but was not active for this evaluation.
- **`unclear`:** applicability cannot be established.

Use comparator type as follows:

- **`usual_or_existing_practice`:** the existing practice or baseline process.
- **`document_based_practice`:** document-centered systems engineering.
- **`manual_analysis_or_check`:** a manual calculation, analysis, or check.
- **`alternative_model_or_method`:** another modeling or engineering method.
- **`alternative_toolchain`:** another tool or connected toolchain.
- **`alternative_design_or_configuration`:** another technical design or scenario.
- **`prior_mission_or_model`:** an earlier mission, project, model, or version.
- **`no_intervention_or_unassisted`:** no MBSE intervention or assistance.
- **`external_benchmark_or_reference`:** external benchmark or reference data.
- **`other`:** another identified comparator type.
- **`unclear`:** comparator type cannot be classified.

Use comparator adequacy as follows:

- **`adequate`:** the comparator is sufficiently similar, or material differences are handled, for the bounded claim.
- **`partial`:** the comparator is relevant, but material residual differences limit interpretation.
- **`inadequate`:** major noncomparability or missing information prevents the comparator from supporting the claim.
- **`unclear`:** available reporting does not permit an adequacy judgment.

Each comparator can contain nested rows for material rival explanations that bear on the claim. Each row records `rival_explanation_id`, whether the explanation is author-identified or reviewer-noted, the explanation, and how the source handled it. Reviewer-noted rival explanations inform support. They are not primary-source findings.

The common evidence fields apply to every output, criterion, comparator, and rival-explanation row. An EPS engineering output is not an MBSE benefit by itself. Link it to RQ2 or RQ3 only when the Part 1 rules are met.

If the reviewer calculates or converts a value, keep it in a `reviewer_derived_values` table within the result set. Record `reviewer_derived_value_id`, linked `input_group_id` or `result_output_id` values, the source values used, formula or transformation, unit conversion, assumptions, missing-data handling, analysis script path and version, reviewer-derived result, and sensitivity to reasonable alternatives. Never overwrite or copy a source-reported value.

### RQ1 evaluative characterizations

Create a short row only when a report uses an evaluative characterization such as *lightweight*, *scalable*, *comprehensive*, *easy to implement*, *resource intensive*, or an equivalent claim.

Record:

- `rq1_claim_id`.
- claim wording.
- claimed characteristic.
- claim scope and object.
- linked model generation method, EPS case, report reuse record, result set, result output, result criterion, comparator, or implementation record when relevant.
- `evidence_basis`.
- `support`.
- `support_reason`.

Descriptive facts such as the tool used or diagrams present remain normal report fields and do not need a claim row.

- **`evidence_basis`**, using one or more of `assertion_only`, `worked_example`, `executed_result`, `comparison`, `stakeholder_evidence`, `physical_or_operational_check`, and `independent_transfer`;
- **`support`**, using `supported`, `limited`, `unsupported`, or `unclear`; and
- **`support_reason`**, one concise sentence naming the strongest evidence and the main limitation, with links to the applicable citations.

Use evidence-basis codes as follows:

- **`assertion_only`:** the claim has no worked, executed, comparative, stakeholder, physical, or transfer evidence.
- **`worked_example`:** a populated or applied example is shown without a reported execution result.
- **`executed_result`:** an actual execution produces a reported output or verdict.
- **`comparison`:** alternatives, groups, baselines, or time periods are explicitly compared.
- **`stakeholder_evidence`:** evidence comes from users, developers, participants, surveys, or interviews.
- **`physical_or_operational_check`:** evidence comes from hardware, physical tests, flight, or operations.
- **`independent_transfer`:** an operationally independent adopter applies and assures the transferred work.

`assertion_only` is exclusive of all other evidence-basis values.

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
- `claim_kind`, using `descriptive_occurrence`, `feasibility_or_executed_result`, `technical_performance`, `comparative`, `causal_attribution`, `experiential_or_perceived`, `implementation_burden`, `transfer_or_generalization`, `other`, or `unclear`.
- `role`, using `outcome`, `implementation_burden`, or `mixed_trade_off`.
- target and scope.
- `outcome_category`, using `eps_reliability`, `mission_or_system_assurance`, `defect_or_error_reduction`, `risk_reduction`, `reproducibility`, `reuse`, `integration_or_interoperability`, `interface_consistency`, `traceability_or_requirements_quality`, `completeness`, `lifecycle_continuity`, `decision_support`, `cost`, `schedule`, `effort_or_automation`, `communication_or_knowledge`, `governance`, `value_realization`, or `other`.
- `reliability_subtype` for a reliability finding, using `eps_reliability`, `system_or_mission_reliability`, `process_reliability`, `model_consistency`, `mission_assurance`, `defect_or_error_reduction`, `generic_reliability_claim`, or `unclear`.
- `author_claimed_direction`, using `beneficial`, `null_or_no_observed_effect`, `mixed_or_conditional`, `adverse`, or `unclear`.
- `evidence_supported_direction`, using `beneficial`, `null_or_no_observed_effect`, `mixed_or_conditional`, `adverse`, `unclear`, or `unsupported`.
- `eps_attribution`, using `explicit_eps_attribution`, `ambiguous_attribution`, or `generic_or_ineligible`.
- mechanism, which is the explanation given by the source of how an EPS-linked model artifact or activity led to a claimed outcome or burden. Do not infer a mechanism. Use `not_reported` when the source provides no explanation. A missing mechanism makes the claim harder to interpret but does not remove an otherwise clear EPS-attributed finding.
- linked model, model generation method, RQ3 activity, input group, result set, result output, result criterion, comparator, report reuse record, or implementation record IDs.
- `measure_directness`, using `direct`, `surrogate`, `intermediate_or_process`, or `unclear`.
- lifecycle stage, using the shared lifecycle-stage codes.
- `applicability`, using `reported_case_only`, `bounded_conditions`, `declared_envelope`, `broader_claim`, or `unclear`.
- `evidence_basis`.
- `support`.
- `support_reason`.

Use `direct_synthesis` for RQ2 findings and RQ3 activities as follows:

- **`yes`:** every RQ-specific condition for direct inclusion is met.
- **`no`:** at least one required condition fails.
- **`uncertain`:** relevant evidence exists, but at least one required condition cannot be resolved.

Use claim kind as follows:

- **`descriptive_occurrence`:** reports that something occurred or existed without evaluating its effect.
- **`feasibility_or_executed_result`:** shows that an activity could be or was completed without establishing performance.
- **`technical_performance`:** reports an EPS or system performance result.
- **`comparative`:** reports a difference without claiming that the intervention caused it.
- **`causal_attribution`:** claims that an artifact or activity caused an outcome.
- **`experiential_or_perceived`:** reports stakeholder experience, opinion, or perceived effect.
- **`implementation_burden`:** reports resources, cost, delay, difficulty, or another implementation burden.
- **`transfer_or_generalization`:** claims applicability, reuse, or performance across settings.
- **`other`:** another identifiable claim kind.
- **`unclear`:** the inferential form cannot be classified.

Use role as follows:

- **`outcome`:** the finding reports an outcome without an inseparable burden.
- **`implementation_burden`:** the finding reports a burden without an inseparable benefit.
- **`mixed_trade_off`:** the finding combines a linked benefit and burden that cannot be represented clearly as separate findings.

Use outcome direction as follows:

- **`beneficial`:** movement toward the stated objective, target, or desired condition.
- **`null_or_no_observed_effect`:** no meaningful or observed change is reported.
- **`mixed_or_conditional`:** direction differs by measure, actor, scenario, or condition.
- **`adverse`:** movement away from the objective or an increase in burden, harm, or failure.
- **`unclear`:** the statement is directional, but its direction cannot be classified.
- **`unsupported`:** no direction is warranted by the evidence. Use this only for evidence-supported direction.

Use EPS attribution as follows:

- **`explicit_eps_attribution`:** the source directly links the outcome or burden to a named EPS artifact or activity.
- **`ambiguous_attribution`:** EPS relevance is clear, but the attributed EPS contribution cannot be separated reliably.
- **`generic_or_ineligible`:** the claim concerns generic or whole-system MBSE without a qualifying EPS attribution.

Use measure directness as follows:

- **`direct`:** the measure directly represents the claimed construct or outcome.
- **`surrogate`:** a substitute measure is used to stand for the claimed outcome.
- **`intermediate_or_process`:** the measure represents a step, mechanism, or process output before the claimed outcome.
- **`unclear`:** the relationship between measure and claim cannot be determined.

Use outcome category as follows:

- **`eps_reliability`:** ability or probability that the EPS performs its required functions.
- **`mission_or_system_assurance`:** confidence that mission or system objectives will be met.
- **`defect_or_error_reduction`:** reduction in faults, defects, inconsistencies, or errors.
- **`risk_reduction`:** reduction in identified likelihood, consequence, or uncertainty.
- **`reproducibility`:** ability to reproduce a model, process, analysis, or result.
- **`reuse`:** repeated use of an artifact or method across settings.
- **`integration_or_interoperability`:** ability to combine systems, models, tools, or data.
- **`interface_consistency`:** agreement and compatibility across interfaces.
- **`traceability_or_requirements_quality`:** trace coverage or improved requirement quality.
- **`completeness`:** coverage of required elements, concerns, or cases.
- **`lifecycle_continuity`:** continuity of information across lifecycle stages.
- **`decision_support`:** support for selecting, justifying, or revising decisions.
- **`cost`:** a financial effect.
- **`schedule`:** an elapsed-time or deadline effect.
- **`effort_or_automation`:** a labor, manual-work, or automation effect.
- **`communication_or_knowledge`:** shared understanding, communication, or knowledge retention.
- **`governance`:** a configuration, ownership, review, or control effect.
- **`value_realization`:** delivered utility or value relative to objectives or investment.
- **`other`:** another source-described outcome category.

Use reliability subtype as follows:

- **`eps_reliability`:** reliability of EPS functions or hardware.
- **`system_or_mission_reliability`:** reliability of the wider spacecraft or mission.
- **`process_reliability`:** consistency or dependability of an engineering process.
- **`model_consistency`:** internal consistency of model content.
- **`mission_assurance`:** confidence in mission success without a direct reliability measure.
- **`defect_or_error_reduction`:** reliability framed through detected or prevented defects.
- **`generic_reliability_claim`:** reliability is claimed without a defined object.
- **`unclear`:** the reliability object cannot be classified.

Use applicability as follows:

- **`reported_case_only`:** applies only to the observed case or scenario.
- **`bounded_conditions`:** applies to explicitly stated conditions or settings.
- **`declared_envelope`:** applies across a declared applicability envelope.
- **`broader_claim`:** the source claims applicability beyond demonstrated or bounded settings.
- **`unclear`:** the applicability scope cannot be established.

For comparative or causal claims, link every applicable `comparator_id`. Keep all comparator details and rival explanations in the linked result set.

For burdens, link every applicable `implementation_record_id`. Keep all roles, amounts, measurement details, mitigations, and linked trade-offs in the implementation record.

A power or energy margin does not become a reliability finding without an explicit reliability or assurance link. Model availability does not establish reproducibility. Co-occurring diagrams do not establish interoperability.

### RQ3 V&V activities

Create one activity row for each materially distinct target–method–scenario combination. Keep several criteria and verdicts in one activity when the method and scenario are shared. Retain relevant near misses with `direct_synthesis = no`.

Record:

- `rq3_activity_id`.
- `direct_synthesis`, using `yes`, `no`, or `uncertain` and the definitions under RQ2.
- failed eligibility condition or uncertainty reason when applicable.
- EPS target.
- `target_type`, using `eps_requirement_or_criterion`, `eps_model_element`, `eps_parameter_or_constraint`, `eps_mode_or_scenario`, `eps_interface_or_flow`, `eps_behavior_or_function`, `eps_component_or_architecture`, `eps_hazard_or_risk_control`, `system_target_traced_to_eps`, `multiple`, `other`, or `unclear`.
- requirement or criterion ID when present.
- model artifact.
- explicit model-to-V&V bridge.
- source terminology for verification, validation, V&V, checking, or analysis.
- linkage scope, using `eps_specific`, `system_wide_eps_linked`, `system_wide_cooccurrence`, or `unclear`.
- normalized V&V object, using `model_verification`, `model_validation`, `system_or_design_verification`, `system_or_design_validation`, `multiple`, or `unclear`.
- normalized V&V object reason.
- method.
- `execution_settings`, using one or more of `mil`, `sil`, `pil`, `hil`, `virtual_testbed`, `other`, or `unclear`.
- `hardware_present`, using `no_hardware`, `support_hardware_only`, `representative_target_hardware`, `actual_target_component`, `actual_target_eps`, `integrated_spacecraft_hardware`, or `unclear`.
- lifecycle stage, using the shared lifecycle-stage codes.
- linked `result_set_id`, `result_criterion_id`, and `result_output_id` values.
- linked `comparator_id` values when the report makes a comparative or causal V&V-effectiveness claim.
- `status`, a derived cumulative set using one or more of `proposed`, `prepared_or_generated`, `result_reported`, `executed_virtual`, `downstream_physical_link`, and `model_to_test_closure`.
- measure directness, using `direct`, `surrogate`, `intermediate_or_process`, or `unclear` and the definitions under RQ2.
- discrepancies and resolution.
- `later_physical_link`.
- `model_to_test_closure`.
- `evidence_basis`.
- `support`.
- `support_reason`.

For validation, link the criterion row that states why the criterion or oracle is authoritative for the intended use. Do not create a separate `oracle_adequacy` field. Record the authority reason in the criterion and reflect any limitation in support.

Use target type to identify the primary object being checked. Use `multiple` only when the activity has inseparable target types.

Use execution settings as follows:

- **`mil`:** the model under test and its environment are represented at model level.
- **`sil`:** executable software runs against a simulated environment on a host platform.
- **`pil`:** software runs on a target or representative processor against a simulated environment.
- **`hil`:** physical target or representative hardware interacts with a simulated environment.
- **`virtual_testbed`:** an integrated virtual environment is not classified as MIL, SIL, PIL, or HIL.
- **`other`:** another source-reported execution setting.
- **`unclear`:** the execution setting cannot be classified.

Use hardware presence as follows:

- **`no_hardware`:** no physical hardware participates.
- **`support_hardware_only`:** computers or instruments participate without representing the target EPS.
- **`representative_target_hardware`:** surrogate or representative EPS hardware participates.
- **`actual_target_component`:** a physical component from the target EPS participates.
- **`actual_target_eps`:** the target EPS participates as a subsystem.
- **`integrated_spacecraft_hardware`:** the target EPS participates within integrated spacecraft hardware.
- **`unclear`:** hardware presence cannot be classified.

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

Keep the source's own term as well as the reviewer's normalized code and reason. Running a method in a model does not automatically make it model verification or model validation. For example, a virtual requirement check can be system or design verification. Keep execution settings separate from the V&V object.

Keep `later_physical_link` and `model_to_test_closure` as required source-evidence fields in every activity. Derive and store every attained status milestone. Do not code status independently from its supporting activity evidence and linked criteria or results. Every milestone after `proposed` requires `proposed`, and each attained prerequisite remains in the cumulative set. A retained near miss can have an empty status set when it attains no milestone.

- `proposed`: the target, bridge, and V&V method, intent, or artifact are reported.
- `prepared_or_generated`: a linked criterion row gives a requirement, threshold, expected behavior, formal property, or pass/fail criterion.
- `result_reported`: a linked output or criterion row reports a result or verdict.
- `executed_virtual`: cited activity evidence establishes that the linked method was run before physical integration or testing of the target EPS, and `result_reported` is attained.
- `downstream_physical_link`: the later-physical-link field connects the activity to a later physical artifact or activity.
- `model_to_test_closure`: the model-to-test-closure field compares model and physical results and reports how differences were handled. This milestone also requires `downstream_physical_link`.

### Artifact and method reuse

A **reusable EPS MBSE artifact** is a source-identifiable structured-model asset, or documented package of assets, that contains a qualifying EPS thread or is explicitly connected to one. It can be:

- a reference or template model;
- a metamodel or profile that carries EPS meaning;
- a model library or pattern;
- an interface contract;
- a parametric-model package;
- a transformation or generator with persistent model content; or
- a larger reusable spacecraft model whose EPS part can be reconstructed separately.

The first report pass creates a complete source-bounded extraction for every identifiable EPS-linked artifact assessed for reuse and every model generation method. Create a reuse record for each generation method even when the source makes no reuse claim. Also capture every reported artifact lineage and each workflow, toolchain, or language reuse case. Create more than one reuse record when the report describes materially distinct artifacts, methods, or lineages. Create separate artifact and method records when their reuse evidence or levels differ. Extract all evidence available in the report even when no companion report is known. Cross-report artifact identity remains pending.

An artifact relationship is one source-supported parent-to-derived connection. Store it as a nested row containing `artifact_relationship_id`, parent artifact name and version, derived artifact name and version, relationship or derivation, and identity and derivation evidence. The common evidence fields apply to every relationship row.

Record once for the report:

- `lineage_mentioned`, using `yes`, `no`, or `uncertain`.
- lineage-mention reason and citation IDs.

Use `yes` when the report explicitly identifies or provides sufficient source evidence for continuity between a base artifact and a version, derived instance, or adoption. The report does not have to use the word *lineage*. Use `uncertain` when continuity is plausible but unresolved. Use `no` for a reuse claim or stand-alone artifact without a reported continuity relationship. Similar diagrams, authors, organizations, tools, topics, or terminology do not establish continuity.

For each report-level reuse record, record identity and provenance:

- `report_reuse_record_id`.
- `lineage_id`, using `pending_resolution` for a reported or uncertain artifact lineage and `not_applicable` when no artifact-lineage relationship is reported.
- linked `model_generation_method_id` values when the record assesses a generation method.
- artifact names and versions.
- artifact relationships using the structured rows defined above.
- repository or location.
- owner or developer.
- `artifact_type`, using `reference_or_template_model`, `metamodel_or_profile`, `model_library_or_pattern`, `interface_contract`, `parametric_model_package`, `transformation_or_generator`, `spacecraft_model_with_separable_eps_thread`, `other`, or `unclear`.
- EPS scope.
- availability, using the shared availability codes.
- `license_category`, using `open_permissive`, `open_copyleft`, `public_domain`, `research_or_noncommercial`, `proprietary_or_commercial`, `custom_other`, `no_license_declared`, or `unclear`.
- exact reuse claim.
- `claimed_reuse_object`, using one or more of `artifact`, `method`, `workflow`, `toolchain`, `language`, `other`, or `unclear`.
- possible related reports or artifacts.

Use artifact type as follows:

- **`reference_or_template_model`:** a generic model intended for configuration or instantiation.
- **`metamodel_or_profile`:** a metamodel, profile, or domain extension that carries EPS meaning.
- **`model_library_or_pattern`:** a reusable collection, pattern, or packaged model element.
- **`interface_contract`:** a reusable specification of interfaces, ports, flows, or obligations.
- **`parametric_model_package`:** a reusable package of equations, constraints, parameters, or analyses.
- **`transformation_or_generator`:** a transformation or generator with persistent model content.
- **`spacecraft_model_with_separable_eps_thread`:** a larger spacecraft model whose EPS part can be reconstructed separately.
- **`other`:** another qualifying reusable artifact type.
- **`unclear`:** artifact type cannot be classified.

Use licence category as follows:

- **`open_permissive`:** open reuse is allowed with permissive conditions.
- **`open_copyleft`:** open reuse requires specified sharing conditions.
- **`public_domain`:** no applicable copyright restriction is claimed.
- **`research_or_noncommercial`:** reuse is limited to research or noncommercial purposes.
- **`proprietary_or_commercial`:** owner permission or commercial terms govern reuse.
- **`custom_other`:** another explicit licence applies.
- **`no_license_declared`:** the source explicitly states that no licence is declared.
- **`unclear`:** reported licence terms cannot be classified.

Use claimed reuse object as follows:

- **`artifact`:** a persistent structured-model asset is reused.
- **`method`:** a defined modeling or engineering method is reused.
- **`workflow`:** a sequence of activities or process steps is reused.
- **`toolchain`:** a connected set of tools or integrations is reused.
- **`language`:** a modeling language, profile syntax, or notation is reused.
- **`other`:** another identifiable reuse object.
- **`unclear`:** the claimed reuse object cannot be identified.

Record the declared applicability envelope (DAE). Its dimensions are:

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
- `report_reuse_level`, using `NA` or one level from `R0_artifact_only` through `R4_independent_reuse_demonstrated`.
- report-reuse-level reason.
- `method_reuse_level`, using `NA` or one level from `M0_method_identified` through `M4_independent_method_reuse_demonstrated`.
- method-reuse-level reason.
- conflicting evidence within the report.
- `evidence_basis`.
- `support`.
- `support_reason`.

Use `report_reuse_level` only for artifact reuse and `method_reuse_level` only for a model generation method or a workflow that defines how the model is generated. Toolchain or language reuse alone remains described through `claimed_reuse_object` and receives `method_reuse_level = NA`. Create separate reuse records when artifact and method conclusions require different evidence-basis or support judgments.

Derive artifact demonstrated settings, coverage, failed applications, and applications outside the declared envelope from linked applications whose `application_object` is `artifact` or `artifact_and_method`. Derive the corresponding method results from applications whose object is `method` or `artifact_and_method`. Do not copy these details into the reuse assessment.

Assign both reuse levels from evidence contained in this report only. A single report can support R3 or R4 and can support M3 or M4. Assign R3 or R4 only when the corresponding artifact application below is complete, includes post-tailoring assurance, and meets the required adopter condition. Assign M3 or M4 only when the corresponding method application is complete, identifies what stayed the same and what changed, reports a relevant post-application check and result, and meets the required adopter condition. A companion report is not required for any report-bounded level.

A **reusable core** is the content that the source states or clearly shows remains across uses. For an artifact, it can include model elements, relationships, constraints, interfaces, meanings, or packaged assets. For a method, it can include stable steps, decision rules, roles, inputs, outputs, or assurance activities.

A **variation point** is a source-described place, option, range, rule, dependency, or method step through which that core can vary.

**Tailoring** means using a source-described process to create or select a target-specific artifact instance or to adapt a generation method to a target setting. It can involve configuration, parameterization, selection, specialization, extension, deletion or substitution, interface mapping, transformation or generation, adding, removing, or reordering method steps, or a clearly justified decision to use the artifact or method unchanged.

A parameter sweep or scenario run in one unchanged mission model is analysis, not tailoring across settings. Rebuilding a model without structure may show reuse of a method. It shows reuse of an artifact only when the source establishes the artifact lineage and the retained core.

Table of artifact reuse level codes.
| Level | Minimum evidence | Meaning |
|---|---|---|
| **`NA`** | The record does not establish an identifiable reusable EPS model artifact | Artifact reuse does not apply to this record. |
| **`R0_artifact_only`** | An EPS-linked artifact is identifiable, with no reuse claim or application reported | An artifact exists. Reuse has not been claimed or shown. |
| **`R1_reuse_claimed`** | The source claims or suggests reuse for the identifiable artifact | Reuse is asserted. Its range and method are not sufficiently specified. |
| **`R2_reuse_specified`** | The declared applicability envelope, reusable core, variation points or unchanged-use rule, tailoring process, and prerequisites are reported | Bounded reuse is specified. Transfer does not have to be demonstrated. |
| **`R3_reuse_demonstrated`** | R2 is met, and at least one materially distinct target setting uses the identified core, reports what stayed the same and what changed, and reports a relevant post-tailoring check and result | Transfer is demonstrated in the reported setting. |
| **`R4_independent_reuse_demonstrated`** | R3 is met by at least one adopter operationally independent of the originating implementation team | Independent transfer is demonstrated in the reported setting. |

Table of method reuse level codes.
| Level | Minimum evidence | Meaning |
|---|---|---|
| **`NA`** | The record does not identify a model generation method | Method reuse does not apply to this record. |
| **`M0_method_identified`** | A model generation method is identified, with no reuse claim or materially distinct application reported | A method exists. Reuse has not been claimed or shown. |
| **`M1_method_reuse_claimed`** | The source claims or suggests that the identified method is reusable | Method reuse is asserted. Its range and adaptation process are not sufficiently specified. |
| **`M2_method_reuse_specified`** | The declared applicability envelope, stable method core, variation points or unchanged-use rule, adaptation process, and prerequisites are reported | Bounded method reuse is specified. Transfer does not have to be demonstrated. |
| **`M3_method_reuse_demonstrated`** | M2 is met, and at least one materially distinct target setting applies the identified method, reports what stayed the same and what changed, and reports a relevant post-application check and result | Method transfer is demonstrated in the reported setting. |
| **`M4_independent_method_reuse_demonstrated`** | M3 is met by at least one adopter operationally independent of the originating method team | Independent method transfer is demonstrated in the reported setting. |

Method levels are cumulative. A report can establish M4 entirely with evidence reported in that single report when it documents the method, specification, materially distinct application, post-application check and result, and operationally independent adopter.

#### Report-level reuse or tailoring application

A **report-level application** is one use of an artifact lineage, model generation method, or both in one target setting. For an artifact, the original development mission counts only if the source identifies it as an adoption or configuration of the same reusable core and reports what was kept and changed, or why it was used unchanged. For a method, the originating use counts only if the source identifies it as an application of an already defined method and reports what was retained and adapted, or why it was used unchanged. Initial creation of an artifact or formulation of a method does not by itself show transfer.

Two applications are **materially distinct** only if they differ on at least one DAE dimension in a way that exercises or tests the reuse claim. Two papers, scenarios, revisions, or names for the same implementation do not count as two applications.

Create one `report_application_id` row for each actual reuse, adoption, or tailoring event described in the report. Merge repeated descriptions of the same event within the report. Keep an account of the same event in another report as a separate report-level row.

Record identity and setting:

- `report_application_id`.
- linked `report_reuse_record_id` values.
- `application_object`, using `artifact`, `method`, `artifact_and_method`, or `unclear`.
- `lineage_id`, inherited from the linked artifact reuse record until cross-report resolution, or `not_applicable` for a method-only application.
- linked `model_generation_method_id` values when applicable.
- linked `eps_case_id` values.
- target model or configuration.
- adopting team.
- relationship to the originator, using `originating_team`, `same_organization_operationally_separate`, `outside_originating_organization`, `independent_evaluation_only`, or `unclear`.
- lifecycle purpose.
- relationship to the declared applicability envelope, using `inside`, `boundary`, `outside`, or `unclear`.
- `material_setting_differences`, recording only differences from the linked report context, EPS case, or other applications that identify a distinct application or affect the envelope classification.

Read shared mission or platform, EPS architecture and interfaces, orbit, environment, modes and loads, model abstraction, tools and versions, and organization and process from the linked report, EPS case, MBSE approach, and implementation records. Do not copy them into the application.

Use application object as follows:

- **`artifact`:** the application reuses or tailors an identifiable artifact.
- **`method`:** the application reuses or adapts an identifiable model generation method.
- **`artifact_and_method`:** the application inseparably reuses both an artifact and its generation method.
- **`unclear`:** the application object cannot be classified.

Each `artifact` or `artifact_and_method` application links an artifact reuse record. Each `method` or `artifact_and_method` application links at least one `model_generation_method_id` and its method reuse record.

Use relationship to the originator as follows:

- **`originating_team`:** the team that originated the artifact or method controls the application.
- **`same_organization_operationally_separate`:** a separate team in the same organization controls the application without substantive implementation or adaptation work by the originating team.
- **`outside_originating_organization`:** a team outside the originating organization controls the application.
- **`independent_evaluation_only`:** an independent party evaluates an originator-built artifact or originator-applied method without adopting or implementing it.
- **`unclear`:** control or team separation cannot be established.

`independent_evaluation_only` does not satisfy R4 or M4 because the independent party does not control the adoption or implementation.

Use relationship to the DAE as follows:

- **`inside`:** every known relevant dimension lies within declared limits.
- **`boundary`:** at least one dimension lies at an explicit limit or tests a stated boundary.
- **`outside`:** at least one dimension exceeds an explicit limit.
- **`unclear`:** the envelope or application information does not support classification.

Record tailoring or adaptation performed:

- base artifact or method and version.
- retained artifact core or method steps and rules.
- configured or changed artifact content or method steps.
- variation points used.
- tailoring or adaptation operations.
- before-and-after trace.
- reasons for changes or unchanged use.
- tailoring or adaptation inputs and assumptions.

Record tailoring or adaptation effort through linked `implementation_record_id` values. Keep the complete effort and burden details in those implementation records. Do not infer low effort from parameterization, automation, a small mission, or the absence of a reported burden.

Record result and assurance:

- resulting artifact.
- configuration identifier.
- availability, using the shared availability codes.
- decisions or analyses supported.
- `application_result`, using `success`, `partial`, `failure`, or `unclear`.
- trade-offs.
- post-tailoring criterion.
- assurance method.
- assurance timing.
- assurance result.
- discrepancies and resolution.
- linked report-level result sets.
- linked RQ2 findings.
- linked RQ3 activities.

For a method-only application, use `not_applicable` for resulting-artifact and configuration fields unless the method application produces an identifiable artifact. The post-tailoring criterion, assurance, and discrepancy fields then refer to the check performed after applying the method.

Use application result as follows:

- **`success`:** the application meets its stated purpose and applicable post-tailoring or post-application criterion.
- **`partial`:** it meets only part of its purpose or criterion.
- **`failure`:** it does not meet its stated purpose or criterion.
- **`unclear`:** the reported evidence does not establish the result.

Record independence:

- personnel overlap.
- who controlled the implementation.
- adopter-attributable evidence for adoption.
- adopter-attributable evidence for assurance.

An outside team normally qualifies as independent when the artifact lineage or method identity, adoption, and assurance are established. A team in the same organization qualifies only when it controls the implementation or adaptation, the originating team performs no substantive implementation or adaptation work, and the assured application is distinct.

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

Report-level extractions remain fixed throughout this pass. Update only `lineage_id` on the relevant artifact reuse records and artifact-containing application records. Assign a stable lineage ID to every matched artifact record, including a record initially marked `not_applicable` that another report links to the lineage. Keep `lineage_id = not_applicable` for method-only records and applications. Use `unresolved_after_review` when a candidate artifact relationship cannot be resolved. A correction to any other report-level field follows the focused-audit and adjudication procedure outside this pass.

Create lineage-level extractions and consolidated artifact application records. Treat all linked reports in a resolved artifact lineage as one evidence bundle when completing those records. Method reuse levels and method-only applications remain fixed, source-bounded report-level results. Do not merge method identities or method-only applications during the artifact-lineage pass. Do not copy lineage-level values into a report-level extraction.

### Study or implementation report family

Record:

- `family_id`.
- linked report IDs.
- shared investigation or implementation.
- relationship among reports.
- shared data, models, methods, scenarios, or results.
- preferred or most complete version for overlapping content.
- dependence reason.

A shared topic, institution, author, or tool is not enough. Keep unresolved relationships separate or uncertain.

### Lineage-level reusable artifact extraction

Create one separate record for each resolved lineage. Extract the fields below at lineage scope from the complete set of linked reports. Record every report and citation ID contributing to each combined field, including disagreements and missing information.

Record identity and provenance:

- `lineage_id`.
- linked `report_reuse_record_id` values.
- linked report and family IDs.
- artifact names and versions.
- artifact relationships using the structured rows defined above.
- owner or developer.
- artifact type, using the artifact-type codes defined above.
- EPS scope.
- availability, using the shared availability codes.
- `license_category`, using the licence-category codes defined above.
- exact reuse claim.
- claimed reuse object, using the claimed-reuse-object codes defined above.

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
- `lineage_reuse_level`, using the R0 through R4 reuse level codes defined above.
- lineage-reuse-level reason.
- conflicting evidence.
- `evidence_basis`.
- `support`.
- `support_reason`.

Read contributing report artifact reuse levels from the linked report-level reuse records. Derive demonstrated settings, demonstrated coverage, failed applications, and applications outside the declared envelope from the linked consolidated tailoring applications. Do not copy these details into the lineage assessment.

Assign `lineage_reuse_level` from the combined lineage evidence. Do not assign R3 or R4 until the corresponding consolidated tailoring application below is complete, includes post-tailoring assurance, and meets the required adopter condition.

After resolving the lineage, assign its `lineage_id` to each matching report-level artifact reuse record and artifact-containing report-level application. This ID assignment is the only change made to those report-level records during the cross-report pass.

### Consolidated tailoring application

Create one separate row for each actual artifact adoption or tailoring event represented across the lineage reports. Include report-level applications whose `application_object` is `artifact` or `artifact_and_method`. Method-only applications are not consolidated in the artifact-lineage pass. Merge repeated reporting of the same event only in this consolidated row. Keep every contributing report-level application unchanged.

Record identity and setting:

- `tailoring_application_id`.
- `lineage_id`.
- linked `report_application_id` values.
- `application_object`, using `artifact` or `artifact_and_method`.
- linked `model_generation_method_id` values when applicable.
- linked report IDs, family IDs, and `eps_case_id` values.
- target model or configuration.
- adopting team.
- relationship to the originator, using `originating_team`, `same_organization_operationally_separate`, `outside_originating_organization`, `independent_evaluation_only`, or `unclear`.
- lifecycle purpose.
- relationship to the declared applicability envelope, using `inside`, `boundary`, `outside`, or `unclear`.
- `material_setting_differences`, recording only differences from the linked records or other applications that identify a distinct application or affect the envelope classification.

Read shared setting details through the linked report applications and their source records. Do not copy mission or platform, EPS architecture and interfaces, orbit, environment, modes and loads, model abstraction, tools and versions, or organization and process into the consolidated application.

Use the relationship-to-originator and relationship-to-DAE codes defined for report-level applications.

Record tailoring or adaptation performed:

- base artifact or method and version.
- retained artifact core or method steps and rules.
- configured or changed artifact content or method steps.
- variation points used.
- tailoring or adaptation operations.
- before-and-after trace.
- reasons for changes or unchanged use.
- tailoring or adaptation inputs and assumptions.

Record tailoring or adaptation effort through the `implementation_record_id` values linked by the contributing report-level applications. Keep the complete effort and burden details in those implementation records. Do not infer low effort from parameterization, automation, a small mission, or the absence of a reported burden.

Record result and assurance:

- resulting artifact.
- configuration identifier.
- availability, using the shared availability codes.
- decisions or analyses supported.
- application result, using the application-result codes defined above.
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

- personnel overlap.
- who controlled the implementation.
- adopter-attributable evidence for adoption.
- adopter-attributable evidence for assurance.

An outside team normally qualifies as independent when the artifact lineage or method identity, adoption, and assurance are established. A team in the same organization qualifies only when it controls the implementation or adaptation, the originating team performs no substantive implementation or adaptation work, and the assured application is distinct.

## Simplified appraisal

Apply the inline appraisal defined in this section. Do not create a separate methodological-appraisal table or claim-support object.

Every evaluative RQ1 claim, every RQ2 finding, every RQ3 activity, every report-level artifact or method reuse conclusion, and every lineage-level artifact reuse conclusion receives:

- `evidence_basis`.
- `support`.
- `support_reason`.

The support reason states the strongest evidence and the main claim-relevant limitation. Keep it bounded to the claim. A narrow executed-result finding can be supported while a broad benefit or transfer claim from the same report is unsupported.

Record comparator adequacy only for comparative or causal claims. Record relationship to the originator and post-tailoring or post-application assurance only for reuse claims. These conditional fields provide the needed appraisal without a general domain matrix.

## Calibration, consistency, and validation

Before full extraction:

1. [ ] Test report-level eligibility and Route A or Route B coding on clear and borderline examples.
2. [ ] Test the complete report form on a varied sample containing Route A and Route B reports, model generation methods, EPS exchanges, dependencies, disciplinary viewpoints, decomposition visibility, grouped inputs, grouped outputs, RQ2 findings, RQ3 activities, figures or tables, complete reusable-artifact and report-level application fields, `lineage_mentioned`, and report-bounded artifact and method reuse levels. Include a report that can reach R3 or R4 by itself and a report that can reach M3 or M4 by itself when available.
3. [ ] Test cross-report family and lineage-identity resolution, immutable report-level records, separate lineage-level extraction, and separate consolidated application, effort, assurance, independence, and reuse-level fields on at least one multi-report example.
4. [ ] Calibrate the difference between assertion, worked example, execution, comparison, physical or operational checking, and independent transfer.
5. [ ] Calibrate `supported`, `limited`, `unsupported`, and `unclear` on narrow and broad claims from the same report.
6. Revise and freeze the codebook, schema, audit procedure, and calibration decisions before full extraction.

### Sole-reviewer extraction and verification

One LLM reviewer performs the primary extraction, cross-report extraction, test–retest extraction, and final review judgments. One human auditor performs the focused audits and controls every write to the canonical extraction. Verification uses one focused audit, deterministic validation, and a delayed LLM test–retest sample.

Apply this sequence:

1. **Primary extraction.** The LLM reviewer extracts the complete report into the frozen report-level form.
2. **Focused audit.** For every included report, the human auditor checks eligibility and route, Route B anchors and bridge, omitted or duplicated groups, direct RQ2 attribution, direct RQ3 linkage, `lineage_mentioned`, complete report-level reuse and application coding, every report-level R3/R4 or M3/M4 assignment, citations, source-versus-inference distinctions, and reviewer-derived values. The auditor may see the extraction because the audit's purpose is error detection.
3. **Deterministic validation.** Validate schema, controlled values, IDs, required fields, links, units, and calculations that can be reproduced. Confirm each citation's report and page range. For citations without `graphic` or `graphic_quote_description`, confirm the verbatim quotation against the stored source using the frozen page-text extraction and normalization rule. Preserve source values and reviewer-derived values separately.
4. **Adjudication.** The LLM reviewer resolves every audit or deterministic issue against the full source and gives the final review judgment. The human auditor records the disposition in the relevant Git commit and applies accepted changes. No automated process writes directly to the canonical extraction.
5. **Cross-report pass.** After report extraction, the LLM reviewer resolves report families and artifact-lineage identity, updates only report-level `lineage_id` values, and creates separate lineage-level and consolidated tailoring-application records. The human auditor performs one focused cross-report audit for every uncertain merge or split and every lineage-level R3 or R4 assignment.

A focused audit is complete only when the complete source sections, figures, and tables needed for its scope were available. Record `audit_id`, the report or lineage, actor, date, scope, `audit_completion_status` using `not_started`, `in_progress`, `complete`, `incomplete_missing_source`, or `incomplete_other`, and counts of issues raised, corrections accepted, flags rejected, and unresolved ambiguities. Add a concise note for any unresolved ambiguity. Record issue resolutions and accepted extraction changes in Git commits rather than separate discrepancy rows.

Use audit completion status as follows:

- **`not_started`:** the audit has not begun.
- **`in_progress`:** the audit has begun but required checks remain.
- **`complete`:** every required check was performed with the necessary source material.
- **`incomplete_missing_source`:** required source material was unavailable.
- **`incomplete_other`:** another condition prevented completion.

After all first-pass report extractions are complete, select a reproducible test–retest sample of `n = min(5, max(2, ceil(0.10 × N)))` when `N > 0`. Include Route A and Route B when both are present and at least one report with complex RQ2, RQ3, or artifact content when available. Freeze the sampling frame, sorted IDs, selection rule, seed, and selected IDs. The LLM reviewer re-extracts each sampled report while the original extraction and audit output are hidden, then compares and adjudicates all differences. The human auditor records dispositions in the relevant Git commits and applies accepted changes. Report this as sole-reviewer consistency, not independent agreement.

An issue is impactful when it can change eligibility or route, a report family or lineage, an artifact or method reuse level, a reuse or tailoring application, direct RQ2 or RQ3 status, outcome direction, support, a quantitative result, or a synthesis conclusion. An impactful issue that may recur triggers a targeted check of every report or lineage that could be affected. Record any codebook change, focused recalibration, and recheck scope.

Do not calculate inter-rater reliability between the reviewer and an LLM. Report audit coverage, issues raised, accepted corrections, rejected flags, unresolved ambiguities, and test–retest differences with their denominators.

Before synthesis, validate every report-level extraction and every separate family, lineage, and consolidated application table against the frozen schema. Confirm that every included report has a completed focused audit, every raised issue has a recorded resolution or unresolved status in the audit summary and Git history, every derived value is reproducible, every lineage-level field preserves report provenance, and cross-report processing changed only report-level `lineage_id` values.
